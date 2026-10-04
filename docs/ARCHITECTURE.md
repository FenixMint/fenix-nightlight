# Architecture

Fenix Night Light separates portable policy from desktop-specific display control.

## Core

The Python core uses only the standard library and owns:

- XDG-local configuration,
- solar calculations,
- day/night policy,
- smooth transitions,
- CLI behavior,
- event planning.

It does not depend on Fedora, Debian, openSUSE, Arch or another distribution.

## Backends

Backends translate a requested color temperature into a desktop/compositor-specific action.

Version 0.1 ships with the `cosmic` backend, using `cosmic-nightlight-helper`.

Future backends can be added without changing the solar or privacy logic.

## Scheduling

The core works manually on any supported Linux system:

- `fenix-nightlight apply`
- `fenix-nightlight status`

The provided systemd user integration is optional. It schedules the next sunrise and sunset rather than polling every few minutes. A daily timer refreshes event times, and desktop autostart corrects the state after login.

If an event was missed while the computer was off or suspended, the next bootstrap or a persistent systemd timer applies the state appropriate for the current wall-clock time.
