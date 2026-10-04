from __future__ import annotations

import argparse
import sys
import time
from datetime import datetime
from zoneinfo import ZoneInfo

from . import __version__
from .backends import BackendError, get_backend
from .config import load_settings, setup_interactive
from .scheduler import schedule_systemd_user_events
from .solar import solar_times
from .transition import TargetState, target_state


def _settings_or_help():
    try:
        return load_settings()
    except FileNotFoundError:
        print("No configuration found. Run: fenix-nightlight setup", file=sys.stderr)
        raise SystemExit(2)


def _current(settings, backend) -> tuple[datetime, object, TargetState]:
    tz = ZoneInfo(settings.timezone)
    now = datetime.now(tz)
    solar = solar_times(now.date(), settings.latitude, settings.longitude, settings.timezone)
    state = target_state(
        now,
        settings,
        solar,
        smooth=backend.capabilities.smooth_transitions,
    )
    return now, solar, state


def _apply(settings, backend, state: TargetState, announce: bool = True) -> None:
    backend.apply(state.temperature, settings.brightness)
    if announce:
        print(
            f"Applied {state.temperature} K @ {settings.brightness:.0%} "
            f"({state.phase}, backend={backend.name})"
        )


def cmd_setup(_args) -> int:
    settings = setup_interactive()
    print()
    print(f"Saved local configuration for: {settings.location_name}")
    return 0


def cmd_status(_args) -> int:
    settings = _settings_or_help()
    backend = get_backend(settings)
    now, solar, state = _current(settings, backend)

    print("Fenix Night Light")
    print(f"Location: {settings.location_name}")
    print("Location source: user configured / local only")
    print(f"Timezone: {settings.timezone}")
    print(f"Sunrise: {solar.sunrise:%H:%M}")
    print(f"Sunset:  {solar.sunset:%H:%M}")
    print(f"Current time: {now:%Y-%m-%d %H:%M:%S %Z}")
    print(f"Phase: {state.phase}")
    print(f"Target: {state.temperature} K")
    print(f"Day / night: {settings.day_temp} K / {settings.night_temp} K")
    print(f"Backend: {backend.name}")
    print("Transition mode: " + ("smooth" if backend.capabilities.smooth_transitions else "discrete"))
    print("Requires privilege: " + ("yes" if backend.capabilities.requires_privilege else "no"))
    print("May flicker: " + ("yes" if backend.capabilities.may_flicker else "no"))
    return 0


def cmd_apply(_args) -> int:
    settings = _settings_or_help()
    backend = get_backend(settings)
    _now, _solar, state = _current(settings, backend)
    _apply(settings, backend, state)
    return 0


def cmd_test(args) -> int:
    settings = _settings_or_help()
    temperature = int(args.temperature)
    if not 1000 <= temperature <= 10000:
        raise SystemExit("temperature must be between 1000 and 10000 K")
    backend = get_backend(settings)
    backend.apply(temperature, settings.brightness)
    print(f"Applied test value: {temperature} K via {backend.name}")
    return 0


def cmd_off(_args) -> int:
    settings = _settings_or_help()
    backend = get_backend(settings)
    backend.off()
    print("Night-light correction disabled by backend.")
    return 0


def cmd_transition(_args) -> int:
    settings = _settings_or_help()
    backend = get_backend(settings)

    if not backend.capabilities.smooth_transitions:
        _now, _solar, state = _current(settings, backend)
        _apply(settings, backend, state)
        return 0

    while True:
        _now, _solar, state = _current(settings, backend)
        _apply(settings, backend, state)
        if state.phase not in {"morning-transition", "evening-transition"}:
            return 0
        time.sleep(settings.transition_step_minutes * 60)


def cmd_schedule(_args) -> int:
    settings = _settings_or_help()
    events = schedule_systemd_user_events(settings)
    for event in events:
        print(f"Scheduled {event.name}: {event.when:%Y-%m-%d %H:%M:%S %Z}")
    return 0


def cmd_bootstrap(_args) -> int:
    settings = _settings_or_help()
    backend = get_backend(settings)
    _now, _solar, state = _current(settings, backend)
    _apply(settings, backend, state)

    try:
        events = schedule_systemd_user_events(settings)
        for event in events:
            print(f"Scheduled {event.name}: {event.when:%Y-%m-%d %H:%M:%S %Z}")
    except RuntimeError as exc:
        print(f"Scheduler unavailable: {exc}", file=sys.stderr)

    if backend.capabilities.smooth_transitions and state.phase in {
        "morning-transition",
        "evening-transition",
    }:
        return cmd_transition(_args)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="fenix-nightlight",
        description="Privacy-first adaptive color temperature manager for Linux.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("setup", help="confirm or change the local location/configuration").set_defaults(func=cmd_setup)
    sub.add_parser("location", help="alias for setup").set_defaults(func=cmd_setup)
    sub.add_parser("status", help="show solar times and current target").set_defaults(func=cmd_status)
    sub.add_parser("apply", help="apply the correct temperature for the current time").set_defaults(func=cmd_apply)
    sub.add_parser("off", help="ask the active backend to disable correction").set_defaults(func=cmd_off)
    sub.add_parser("transition", help="apply the backend-appropriate solar transition").set_defaults(func=cmd_transition)
    sub.add_parser("schedule", help="schedule the next sunrise and sunset with systemd --user").set_defaults(func=cmd_schedule)
    sub.add_parser("bootstrap", help="apply current state and schedule upcoming events").set_defaults(func=cmd_bootstrap)

    test_parser = sub.add_parser("test", help="apply a temporary temperature value")
    test_parser.add_argument("temperature", type=int)
    test_parser.set_defaults(func=cmd_test)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.func(args) or 0)
    except (BackendError, ValueError, RuntimeError) as exc:
        print(f"fenix-nightlight: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
