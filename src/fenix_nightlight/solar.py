from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo

ZENITH_DEGREES = 90.833


@dataclass(frozen=True)
class SolarTimes:
    sunrise: datetime
    sunset: datetime


def _fractional_year(day: date, hour: float = 12.0) -> float:
    days = 366 if _is_leap(day.year) else 365
    return (2.0 * math.pi / days) * (day.timetuple().tm_yday - 1 + (hour - 12.0) / 24.0)


def _is_leap(year: int) -> bool:
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)


def _equation_of_time_and_declination(day: date) -> tuple[float, float]:
    gamma = _fractional_year(day)
    equation = 229.18 * (
        0.000075
        + 0.001868 * math.cos(gamma)
        - 0.032077 * math.sin(gamma)
        - 0.014615 * math.cos(2 * gamma)
        - 0.040849 * math.sin(2 * gamma)
    )
    declination = (
        0.006918
        - 0.399912 * math.cos(gamma)
        + 0.070257 * math.sin(gamma)
        - 0.006758 * math.cos(2 * gamma)
        + 0.000907 * math.sin(2 * gamma)
        - 0.002697 * math.cos(3 * gamma)
        + 0.00148 * math.sin(3 * gamma)
    )
    return equation, declination


def solar_times(day: date, latitude: float, longitude: float, timezone_name: str) -> SolarTimes:
    """Return approximate civil sunrise and sunset for a local calendar date."""
    if not -90.0 <= latitude <= 90.0:
        raise ValueError("latitude must be between -90 and 90")
    if not -180.0 <= longitude <= 180.0:
        raise ValueError("longitude must be between -180 and 180")

    equation, declination = _equation_of_time_and_declination(day)
    lat = math.radians(latitude)
    zenith = math.radians(ZENITH_DEGREES)
    denominator = math.cos(lat) * math.cos(declination)
    if abs(denominator) < 1e-12:
        raise ValueError("sunrise/sunset cannot be calculated at this latitude/date")

    cos_hour_angle = math.cos(zenith) / denominator - math.tan(lat) * math.tan(declination)
    if cos_hour_angle > 1.0:
        raise ValueError("sun does not rise on this date at this latitude")
    if cos_hour_angle < -1.0:
        raise ValueError("sun does not set on this date at this latitude")

    hour_angle_degrees = math.degrees(math.acos(cos_hour_angle))
    solar_noon_utc_minutes = 720.0 - (4.0 * longitude) - equation
    sunrise_utc_minutes = solar_noon_utc_minutes - 4.0 * hour_angle_degrees
    sunset_utc_minutes = solar_noon_utc_minutes + 4.0 * hour_angle_degrees

    utc_midnight = datetime.combine(day, time.min, tzinfo=timezone.utc)
    tz = ZoneInfo(timezone_name)
    return SolarTimes(
        sunrise=(utc_midnight + timedelta(minutes=sunrise_utc_minutes)).astimezone(tz),
        sunset=(utc_midnight + timedelta(minutes=sunset_utc_minutes)).astimezone(tz),
    )
