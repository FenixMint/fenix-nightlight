#!/bin/sh
set -eu

DATA_HOME=${XDG_DATA_HOME:-"$HOME/.local/share"}
CONFIG_HOME=${XDG_CONFIG_HOME:-"$HOME/.config"}
BIN_DIR="$HOME/.local/bin"

if command -v systemctl >/dev/null 2>&1; then
    systemctl --user disable --now fenix-nightlight-refresh.timer >/dev/null 2>&1 || true
    systemctl --user stop fenix-nightlight-sunrise.timer fenix-nightlight-sunset.timer >/dev/null 2>&1 || true
fi

rm -f "$BIN_DIR/fenix-nightlight"
rm -rf "$DATA_HOME/fenix-nightlight"
rm -f "$CONFIG_HOME/systemd/user/fenix-nightlight-refresh.service"
rm -f "$CONFIG_HOME/systemd/user/fenix-nightlight-refresh.timer"
rm -f "$CONFIG_HOME/autostart/fenix-nightlight.desktop"

if command -v systemctl >/dev/null 2>&1; then
    systemctl --user daemon-reload || true
fi

echo "Program files removed."
echo "Local user configuration was intentionally kept in:"
echo "  $CONFIG_HOME/fenix-nightlight/"
