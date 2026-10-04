# Fenix Night Light

**Fenix Night Light** is a privacy-first adaptive color-temperature manager for Linux.

It is being developed as a component of the upcoming **FX Linux** system, while remaining an independent project that can be used on other Linux distributions and desktop environments.

> Status: **0.1 alpha** — usable for testing, API and integration details may still change.

## Design goals

- no automatic geolocation,
- no telemetry,
- no network connection required,
- sunrise/sunset calculated locally,
- user-entered location stays on the computer,
- smooth day/night transitions,
- distribution-agnostic core,
- pluggable desktop/compositor backends,
- event-driven scheduling instead of frequent polling.

## Default policy

The current defaults are:

- day: **4500 K**
- night: **4000 K**
- brightness: **100%**
- transition: **30 minutes**
- transition step: **5 minutes**

There is **no default city or coordinate**. On first setup the user enters a location manually. Later runs show the last saved location and offer **confirm or change**.

## Current backend

### COSMIC

Version 0.1 supports COSMIC through:

```text
cosmic-nightlight-helper
```

The backend is detected automatically when the helper is available.

Additional backends are planned.

When Fenix Night Light owns scheduling, disable the COSMIC Night Light app's own schedule/background automation to avoid two controllers competing for the same display state.

## Install from a clone

```bash
git clone https://github.com/FenixMint/fenix-nightlight.git
cd fenix-nightlight
./install.sh
fenix-nightlight setup
fenix-nightlight bootstrap
```

The installer uses only the current user's home directory. It does not require `sudo`.

## Configuration

Configuration follows XDG conventions:

```text
~/.config/fenix-nightlight/config.ini
```

Example:

```ini
[fenix-nightlight]
location_name = Example City
latitude = 52.0000
longitude = 17.0000
timezone = Europe/Warsaw
day_temp = 4500
night_temp = 4000
brightness = 1.0
transition_minutes = 30
transition_step_minutes = 5
backend = auto
```

The location label is for the human. Sunrise/sunset calculations use the coordinates and IANA time zone.

## CLI

```bash
fenix-nightlight setup
fenix-nightlight location
fenix-nightlight status
fenix-nightlight apply
fenix-nightlight test 4000
fenix-nightlight off
fenix-nightlight schedule
fenix-nightlight bootstrap
```

`setup` shows the previously saved location, when present, and lets the user confirm it or change it.

## Scheduling

The optional installer adds:

- desktop autostart → `bootstrap` after login,
- a daily `systemd --user` timer to refresh solar event times,
- transient persistent timers for the next sunrise and sunset.

The program does **not** need a five-minute polling loop.

If the machine starts several times in one day, each login corrects the current state. If it stays running for days, the daily timer refreshes the next solar events.

## Privacy

See [docs/PRIVACY.md](docs/PRIVACY.md).

Short version: location is manual and local-only. Fenix Night Light performs no IP geolocation, GPS lookup or telemetry.

## Development

Run the test suite with:

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

## License

Mozilla Public License 2.0 (MPL-2.0).
