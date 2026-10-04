from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

from .config import Settings
from .solar import SolarTimes


@dataclass(frozen=True)
class TargetState:
    temperature: int
    phase: str


def _interpolate(start: int, end: int, fraction: float) -> int:
    fraction = min(1.0, max(0.0, fraction))
    value = start + ((end - start) * fraction)
    return int(round(value / 10.0) * 10)


def target_state(
    now: datetime,
    settings: Settings,
    solar: SolarTimes,
    *,
    smooth: bool = True,
) -> TargetState:
    if not smooth:
        if solar.sunrise <= now < solar.sunset:
            return TargetState(settings.day_temp, "day")
        return TargetState(settings.night_temp, "night")

    duration = timedelta(minutes=settings.transition_minutes)
    sunrise_end = solar.sunrise + duration
    sunset_end = solar.sunset + duration

    if solar.sunrise <= now < sunrise_end:
        fraction = (now - solar.sunrise) / duration
        return TargetState(
            _interpolate(settings.night_temp, settings.day_temp, fraction),
            "morning-transition",
        )

    if sunrise_end <= now < solar.sunset:
        return TargetState(settings.day_temp, "day")

    if solar.sunset <= now < sunset_end:
        fraction = (now - solar.sunset) / duration
        return TargetState(
            _interpolate(settings.day_temp, settings.night_temp, fraction),
            "evening-transition",
        )

    return TargetState(settings.night_temp, "night")
