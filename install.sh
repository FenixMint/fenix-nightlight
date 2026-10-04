#!/bin/sh
set -eu

ROOT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
DATA_HOME=${XDG_DATA_HOME:-"$HOME/.local/share"}
CONFIG_HOME=${XDG_CONFIG_HOME:-"$HOME/.config"}
BIN_DIR="$HOME/.local/bin"
APP_DIR="$DATA_HOME/fenix-nightlight"
SYSTEMD_DIR="$CONFIG_HOME/systemd/user"
AUTOSTART_DIR="$CONFIG_HOME/autostart"

command -v python3 >/dev/null 2>&1 || {
    echo "python3 is required" >&2
    exit 1
}

mkdir -p "$APP_DIR" "$BIN_DIR" "$SYSTEMD_DIR" "$AUTOSTART_DIR"
rm -rf "$APP_DIR/fenix_nightlight"
cp -R "$ROOT_DIR/src/fenix_nightlight" "$APP_DIR/fenix_nightlight"

cat >"$BIN_DIR/fenix-nightlight" <<EOF
#!/bin/sh
PYTHONPATH="$APP_DIR${PYTHONPATH:+:$PYTHONPATH}" exec python3 -m fenix_nightlight "$@"
EOF
chmod 0755 "$BIN_DIR/fenix-nightlight"

cp "$ROOT_DIR/systemd/fenix-nightlight-refresh.service" "$SYSTEMD_DIR/"
cp "$ROOT_DIR/systemd/fenix-nightlight-refresh.timer" "$SYSTEMD_DIR/"

cat >"$AUTOSTART_DIR/fenix-nightlight.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=Fenix Night Light
Comment=Apply local adaptive color temperature settings
Exec=$BIN_DIR/fenix-nightlight bootstrap
Terminal=false
X-GNOME-Autostart-enabled=true
EOF

if command -v systemctl >/dev/null 2>&1; then
    systemctl --user daemon-reload || true
    systemctl --user enable --now fenix-nightlight-refresh.timer || true
fi

echo
echo "Fenix Night Light installed."
echo "Next: $BIN_DIR/fenix-nightlight setup"
echo "Then: $BIN_DIR/fenix-nightlight bootstrap"
