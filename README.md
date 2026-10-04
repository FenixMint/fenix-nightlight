# Fenix Night Light

**Fenix Night Light** is a privacy-first adaptive color-temperature manager for Linux.

It is being developed as a component of the upcoming **FX Linux** system, while remaining an independent project that can be used on other Linux distributions and desktop environments.

> Status: **0.2 development** — architecture is under active refinement. Fedora COSMIC deployment is intentionally deferred until the COSMIC backend is mature enough for safe daily use.

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

### COSMIC DRM fallback

Current COSMIC support uses the external `cosmic-nightlight-helper` as a DRM/KMS fallback.

Important limitations discovered during Fedora COSMIC validation:

- the helper requires elevated privileges,
- it may briefly flicker while acquiring DRM master,
- therefore the backend is classified as **discrete**, not smooth,
- Fenix Night Light will apply only the day/night boundary change on this backend rather than stepping every few minutes.

The backend capability model is designed so future COSMIC-native, wlroots, GNOME, KDE, or X11 adapters can expose their own transition behavior without changing solar policy.

When Fenix Night Light eventually owns scheduling on a COSMIC workstation, the existing COSMIC Night Light app must not simultaneously control the display.

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
