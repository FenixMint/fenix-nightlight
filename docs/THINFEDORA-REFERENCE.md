# ThinFedora reference profile

Status: working reference for the Fedora COSMIC development machine used while building Fenix Night Light and future FX Linux components.

Last reconstructed from project conversations: 2026-10-04.

This document intentionally separates confirmed state from experiments. Do not turn every item into an FX Linux default without hardware/session detection.

## Reference machine

- Hostname: `ThinFedora`
- User home: `/home/fenix`
- Fedora Linux 44
- COSMIC 1.8.0 generation used during the tuning work
- Lenovo ThinkPad L13 Gen 2
- AMD Ryzen 5 PRO 5650U, 6C/12T
- 16 GB RAM

## Confirmed base state

These were verified on the machine and are good candidates for an FX Linux audit/profile layer.

| Area | Confirmed state | FX Linux treatment |
| --- | --- | --- |
| AMD CPU scaling | `amd_pstate=active` | audit first; preserve when supported |
| Power profile | `balanced-battery` | laptop profile candidate, not universal desktop default |
| Compressed swap | 8 GB ZRAM | keep/audit; Fedora already provides ZRAM |
| SSD maintenance | `fstrim.timer` enabled | keep/audit |
| Root filesystem | Btrfs | informational; do not convert existing systems automatically |
| ABRT/problem infrastructure | ABRT was intentionally left installed | do not mass-remove |

## Service pruning: final remembered state

The service pass reduced the active service set from roughly 42 to roughly 35 on this laptop.

Confirmed inactive/disabled in the final remembered state:

- `ModemManager`
- `pcscd`
- `atd`
- `qemu-guest-agent`
- `vboxservice`
- `vgauthd`
- `vmtoolsd`
- `iscsi-onboot`
- `iscsi-starter`
- `switcheroo-control`
- `systemd-homed`
- `geoclue`

Important exceptions and history:

- `gssproxy` was disabled during an early pass but was later restored. Final remembered state: **active**.
- `ABRT` was deliberately retained.
- `switcheroo-control` and `systemd-homed` were discussed/rolled back during tuning and later remembered as disabled on this specific laptop. Treat them as **hardware/session-conditional**, not universal FX Linux defaults.
- GeoClue was at one point masked with `sudo systemctl mask geoclue.service`. Privacy GUI settings for camera/microphone/location were not adopted as a blanket hardening policy after rollback/testing.

### Reproduction rule for FX Linux

Do not blindly disable the above list. First detect whether the machine actually has or uses:

- WWAN/modem hardware,
- smart-card hardware,
- virtualization guest services,
- iSCSI,
- hybrid/multi-GPU switching,
- systemd-homed accounts,
- location-dependent desktop features.

Only disable a service when the corresponding capability is absent or explicitly rejected by the user profile.

## Autostart/privacy experiments that are NOT baseline

An experiment hid some desktop autostart entries using files under `~/.config/autostart/`, including GeoClue-related startup, Problem Reporting and SELinux Troubleshooter.

That experiment was associated with a black-screen/rollback episode. Therefore:

- do not reproduce those autostart overrides as a default,
- do not hide SELinux/problem-reporting components merely to reduce process count,
- keep this class of change in an optional/test-only profile until independently revalidated.

## FenixSystem / Conky

Conky was installed as an RPM rather than Flatpak.

Known working layout:

- config: `~/.config/conky/conky.conf`
- Wayland output enabled: `out_to_wayland=true`
- alignment: `top_right`
- `gap_x=30`
- `gap_y=90`
- sensors helper: `~/.local/bin/fenix-sensors.sh`
- autostart: `~/.config/autostart/fenix-conky.desktop`

The FenixSystem panel evolved to show:

- CPU load
- 6 cores / 12 threads
- RAM
- SSD/storage
- CPU/APU thermal data
- fan speed
- APU PPT/power data
- battery
- network traffic

Relevant hwmon mapping observed during development:

- ThinkPad sensors/fan: hwmon6 `thinkpad`
- NVMe: hwmon3
- AMD GPU: hwmon4 `amdgpu`
- CPU temperature: hwmon5 `k10temp`

This should become an optional FX Linux monitor module, not a mandatory base component.

## Signal

Official Signal AppImage was used at:

`~/Applications/Signal-official.AppImage`

Its signature was verified with key:

`4B16 B723 2DFA A439 AD79 1002 EF9F 501F 13EE D94C`

This is application setup rather than an operating-system optimization, but it is part of the known ThinFedora reference environment.

## Flatpak policy

User preference is to avoid Flatpak where a good RPM/native/local option exists, partly because of SSD space use and duplicated runtimes.

The current COSMIC Night Light is an exception during development:

- Flatpak app ID: `io.github.cosmic_nightlight`
- version observed: 0.5.1
- it stores configuration under:
  `~/.config/cosmic/io.github.cosmic_nightlight/v1/`

Do not generalize that exception into an FX Linux preference for Flatpak.

## GRUB / boot visuals

A Breeze GRUB theme was present at:

`/boot/grub2/themes/breeze/theme.txt`

The theme was tested with graphical terminal output, but it rendered too small on the Full HD panel and the custom boot-screen work was postponed.

Treat the GRUB theme work as **experimental/not final**. Do not include it in the reproducible baseline yet.

## COSMIC desktop

The COSMIC dock and top bar were customized during setup.

The exact complete settings were not recovered from conversation memory, so they are intentionally not declared reproducible here. Before turning them into an FX Linux profile, export the actual COSMIC config and compare it with defaults.

## Development environment added after install

The Fedora machine was also prepared as an FX development host.

Packages explicitly installed for development included:

`git openssh-clients python3-devel python3-pip`

Known FX NEXUS layout on ThinFedora:

- repo: `~/src/fx-nexus`
- venv: `~/src/fx-nexus/.venv`
- launcher: `~/.local/bin/fx`
- data: `~/.local/share/fxnexus/`
- config: `~/.config/fxnexus/`
- cache: `~/.cache/fxnexus/`

This layout follows XDG separation and is a useful model for future FX Linux applications.

## Current Night Light implementation on ThinFedora

The Night Light currently installed on the workstation is **not a native COSMIC compositor feature**.

Observed components:

- Flatpak: `Night Light for COSMIC`
- app ID: `io.github.cosmic_nightlight`
- daemon form: `cosmic-nightlight --daemon --managed`
- settings form: `cosmic-nightlight --settings`
- external helper: `/usr/local/bin/cosmic-nightlight-helper`

The helper requires root privileges and was confirmed to work through:

`pkexec /usr/local/bin/cosmic-nightlight-helper --temp 4500 --brightness 1.0`

The helper reports that it switches VTs and grabs DRM master. The visible short flicker during temperature changes is therefore expected with this implementation.

Observed COSMIC Night Light config files:

- `temperature`
- `brightness`
- `schedule`
- `override`

under:

`~/.config/cosmic/io.github.cosmic_nightlight/v1/`

Observed values during investigation:

- temperature: 4000
- brightness: 1.0
- schedule: `"custom"`
- override: `"off"`

This current implementation is useful as a Fedora COSMIC reference/fallback, but it is not the final Fenix Night Light architecture.

## FX Linux lessons from ThinFedora

Candidate baseline policies:

1. audit first, never mass-disable services,
2. preserve Fedora-native ZRAM and trim behavior when already correct,
3. prefer `amd_pstate=active` on supported AMD hardware,
4. select a laptop-aware power profile,
5. use XDG paths consistently,
6. prefer native/RPM/local packages where practical,
7. classify changes as core, hardware-conditional, optional or experimental,
8. keep privacy hardening reversible,
9. do not confuse a lower process count with a healthier system,
10. keep desktop visuals/monitoring separate from the operating-system core.

## Items still worth capturing directly from the machine

Before calling this profile fully reproducible, export and version:

- exact enabled/disabled systemd units,
- exact COSMIC dock/top-panel config,
- installed RPM package delta versus clean Fedora COSMIC,
- user autostart files,
- power-profile configuration,
- current Conky config and sensor helper,
- GRUB defaults and theme state,
- any sysctl, udev, modprobe or kernel-command-line changes, if present.

Those exports should become machine-readable manifests for the future FX Linux profile instead of relying on conversation memory.
