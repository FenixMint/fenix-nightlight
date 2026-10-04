# Architecture

Fenix Night Light separates portable policy from desktop-specific display control.

## Core

The Python core uses only the standard library and owns:

- XDG-local configuration,
- solar calculations,
- day/night policy,
- transition policy selected from backend capabilities,
- CLI behavior,
- event planning.

It does not depend on Fedora, Debian, openSUSE, Arch or another distribution.

## Backends

Backends translate a requested color temperature into a desktop/compositor-specific action.

Backends expose capabilities in addition to apply/off operations:

- whether smooth transitions are safe,
- whether privileged execution is required,
- whether applying a value may visibly flicker.

The first implementation is `cosmic-drm`, currently using the external `cosmic-nightlight-helper`.
Because this path requires elevated DRM/KMS access and can visibly flicker, it is a **discrete backend**: sunrise and sunset apply one boundary change rather than a multi-step transition.

Future backends can be added without changing the solar or privacy logic. A native COSMIC backend can later replace `cosmic-drm` automatically once a suitable compositor API exists.

## Scheduling

The core works manually on any supported Linux system:

- `fenix-nightlight apply`
- `fenix-nightlight status`

The provided systemd user integration is optional. It schedules the next sunrise and sunset rather than polling every few minutes. A daily timer refreshes event times, and desktop autostart corrects the state after login.

If an event was missed while the computer was off or suspended, the next bootstrap or a persistent systemd timer applies the state appropriate for the current wall-clock time.
