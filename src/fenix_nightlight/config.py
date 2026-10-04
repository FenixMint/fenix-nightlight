from __future__ import annotations

import configparser
import os
from dataclasses import dataclass, replace
from datetime import date
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

APP_NAME = "fenix-nightlight"


def _xdg_dir(env_name: str, fallback: Path) -> Path:
    value = os.environ.get(env_name)
    return Path(value).expanduser() if value else fallback


def config_path() -> Path:
    return _xdg_dir("XDG_CONFIG_HOME", Path.home() / ".config") / APP_NAME / "config.ini"


@dataclass(frozen=True)
class Settings:
    location_name: str
    latitude: float
    longitude: float
    timezone: str
    day_temp: int = 4500
    night_temp: int = 4000
    brightness: float = 1.0
    transition_minutes: int = 30
    transition_step_minutes: int = 5
    backend: str = "auto"
    cosmic_helper: str = "/usr/local/bin/cosmic-nightlight-helper"
    location_confirmed: str = ""

    def validate(self) -> "Settings":
        if not self.location_name.strip():
            raise ValueError("location_name cannot be empty")
        if not -90.0 <= self.latitude <= 90.0:
            raise ValueError("latitude must be between -90 and 90")
        if not -180.0 <= self.longitude <= 180.0:
            raise ValueError("longitude must be between -180 and 180")
        try:
            ZoneInfo(self.timezone)
        except ZoneInfoNotFoundError as exc:
            raise ValueError(f"unknown timezone: {self.timezone}") from exc
        if not 1000 <= self.day_temp <= 10000:
            raise ValueError("day_temp must be between 1000 and 10000 K")
        if not 1000 <= self.night_temp <= 10000:
            raise ValueError("night_temp must be between 1000 and 10000 K")
        if not 0.1 <= self.brightness <= 1.0:
            raise ValueError("brightness must be between 0.1 and 1.0")
        if not 1 <= self.transition_minutes <= 180:
            raise ValueError("transition_minutes must be between 1 and 180")
        if not 1 <= self.transition_step_minutes <= self.transition_minutes:
            raise ValueError("transition_step_minutes must be between 1 and transition_minutes")
        return self


def detect_timezone_name() -> str:
    timezone_file = Path("/etc/timezone")
    if timezone_file.is_file():
        value = timezone_file.read_text(encoding="utf-8").strip()
        if value:
            try:
                ZoneInfo(value)
                return value
            except ZoneInfoNotFoundError:
                pass

    localtime = Path("/etc/localtime")
    try:
        resolved = localtime.resolve()
        marker = "/zoneinfo/"
        text = str(resolved)
        if marker in text:
            value = text.split(marker, 1)[1]
            ZoneInfo(value)
            return value
    except (OSError, ZoneInfoNotFoundError):
        pass
    return "UTC"


def load_settings(path: Path | None = None) -> Settings:
    path = path or config_path()
    parser = configparser.ConfigParser()
    if not path.is_file():
        raise FileNotFoundError(path)
    parser.read(path, encoding="utf-8")
    section = parser["fenix-nightlight"]
    return Settings(
        location_name=section["location_name"],
        latitude=section.getfloat("latitude"),
        longitude=section.getfloat("longitude"),
        timezone=section["timezone"],
        day_temp=section.getint("day_temp", fallback=4500),
        night_temp=section.getint("night_temp", fallback=4000),
        brightness=section.getfloat("brightness", fallback=1.0),
        transition_minutes=section.getint("transition_minutes", fallback=30),
        transition_step_minutes=section.getint("transition_step_minutes", fallback=5),
        backend=section.get("backend", fallback="auto"),
        cosmic_helper=section.get("cosmic_helper", fallback="/usr/local/bin/cosmic-nightlight-helper"),
        location_confirmed=section.get("location_confirmed", fallback=""),
    ).validate()


def save_settings(settings: Settings, path: Path | None = None) -> Path:
    settings = settings.validate()
    path = path or config_path()
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)

    parser = configparser.ConfigParser()
    parser["fenix-nightlight"] = {
        "location_name": settings.location_name,
        "latitude": str(settings.latitude),
        "longitude": str(settings.longitude),
        "timezone": settings.timezone,
        "day_temp": str(settings.day_temp),
        "night_temp": str(settings.night_temp),
        "brightness": str(settings.brightness),
        "transition_minutes": str(settings.transition_minutes),
        "transition_step_minutes": str(settings.transition_step_minutes),
        "backend": settings.backend,
        "cosmic_helper": settings.cosmic_helper,
        "location_confirmed": settings.location_confirmed or date.today().isoformat(),
    }

    temp = path.with_suffix(path.suffix + ".tmp")
    with temp.open("w", encoding="utf-8") as handle:
        parser.write(handle)
    os.chmod(temp, 0o600)
    temp.replace(path)
    os.chmod(path, 0o600)
    return path


def _prompt(prompt: str, default: str | None = None) -> str:
    suffix = f" [{default}]" if default not in (None, "") else ""
    value = input(f"{prompt}{suffix}: ").strip()
    return value if value else (default or "")


def setup_interactive() -> Settings:
    current: Settings | None = None
    try:
        current = load_settings()
    except FileNotFoundError:
        pass

    print("Fenix Night Light")
    print("Location is entered manually and remains on this computer only.")
    print("No GPS, IP geolocation, network lookup or telemetry is used.")
    print()

    if current:
        print("Last location:")
        print(f"  {current.location_name}")
        print(f"  {current.latitude:.5f}, {current.longitude:.5f}")
        print(f"  {current.timezone}")
        answer = input("Press Enter to confirm, or type C to change: ").strip().lower()
        if answer not in {"c", "change"}:
            confirmed = replace(current, location_confirmed=date.today().isoformat())
            save_settings(confirmed)
            return confirmed

    default_name = current.location_name if current else None
    default_lat = str(current.latitude) if current else None
    default_lon = str(current.longitude) if current else None
    default_tz = current.timezone if current else detect_timezone_name()

    name = _prompt("Location label", default_name)
    latitude = float(_prompt("Latitude", default_lat))
    longitude = float(_prompt("Longitude", default_lon))
    timezone = _prompt("IANA timezone", default_tz)

    base = current or Settings(
        location_name=name,
        latitude=latitude,
        longitude=longitude,
        timezone=timezone,
    )
    updated = replace(
        base,
        location_name=name,
        latitude=latitude,
        longitude=longitude,
        timezone=timezone,
        location_confirmed=date.today().isoformat(),
    ).validate()
    save_settings(updated)
    return updated
