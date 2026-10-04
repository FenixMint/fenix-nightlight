# Privacy

Fenix Night Light is designed to work without learning where the user is automatically.

## Location

Location is:

- entered manually by the user,
- stored locally in the user's XDG configuration directory,
- used only to calculate sunrise and sunset,
- never inferred from GPS, Wi-Fi, IP address, browser data or account data,
- never sent to FenixMint or any external service.

The application requires no network connection for normal operation.

The configuration file is written with user-only permissions (`0600`) where supported.

## Telemetry

Fenix Night Light contains no telemetry, analytics, advertising identifiers or crash-report uploads.

## Philosophy

Location is user-provided, local-only and changeable at any time. The program should never silently infer it.
