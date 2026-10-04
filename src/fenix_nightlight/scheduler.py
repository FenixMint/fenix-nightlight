from __future__ import annotations

import shutil
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from .config import Settings
from .solar import solar_times


@dataclass(frozen=True)
class ScheduledEvent:
    name: str
    when: datetime


def next_solar_events(now: datetime, settings: Settings) -> list[ScheduledEvent]:
    candidates: list[ScheduledEvent] = []
    for offset in range(0, 3):
        day = (now + timedelta(days=offset)).date()
        solar = solar_times(day, settings.latitude, settings.longitude, settings.timezone)
        candidates.extend([
            ScheduledEvent("sunrise", solar.sunrise),
            ScheduledEvent("sunset", solar.sunset),
        ])

    future = [event for event in candidates if event.when > now]
    result: list[ScheduledEvent] = []
    for name in ("sunrise", "sunset"):
        matches = [event for event in future if event.name == name]
        if matches:
            result.append(min(matches, key=lambda event: event.when))
    return sorted(result, key=lambda event: event.when)


def _systemd_timestamp(value: datetime, timezone_name: str) -> str:
    return f"{value:%Y-%m-%d %H:%M:%S} {timezone_name}"


def _program_command() -> list[str]:
    installed = Path.home() / ".local" / "bin" / "fenix-nightlight"
    if installed.is_file():
        return [str(installed)]
    discovered = shutil.which("fenix-nightlight")
    if discovered:
        return [discovered]
    return [sys.executable, "-m", "fenix_nightlight"]


def schedule_systemd_user_events(settings: Settings, now: datetime | None = None) -> list[ScheduledEvent]:
    if not shutil.which("systemd-run") or not shutil.which("systemctl"):
        raise RuntimeError("systemd user scheduling is unavailable on this system")

    tz = ZoneInfo(settings.timezone)
    now = now or datetime.now(tz)
    events = next_solar_events(now, settings)

    for event in events:
        unit = f"fenix-nightlight-{event.name}"
        subprocess.run(
            ["systemctl", "--user", "stop", f"{unit}.timer", f"{unit}.service"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )
        subprocess.run(
            ["systemctl", "--user", "reset-failed", f"{unit}.timer", f"{unit}.service"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )
        command = [
            "systemd-run",
            "--user",
            f"--unit={unit}",
            "--collect",
            f"--on-calendar={_systemd_timestamp(event.when, settings.timezone)}",
            "--timer-property=Persistent=true",
            *_program_command(),
            "transition",
        ]
        result = subprocess.run(command, text=True, capture_output=True, check=False)
        if result.returncode != 0:
            detail = (result.stderr or result.stdout).strip()
            raise RuntimeError(detail or f"failed to schedule {event.name}")

    return events
