#!/usr/bin/env bash
# Install pi-panel-info dashboard + custom 6x14 console font.
# Run as root (or with sudo) on the Pi.  Idempotent.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
FONT_SRC="$SCRIPT_DIR/wdf-panel-6x14.psf.gz"
FONT_DST="/usr/local/share/consolefonts/wdf-panel-6x14.psf.gz"
CONSOLE_DEFAULTS="/etc/default/console-setup"

echo "==> installing custom 6x14 font"
install -m 0644 "$FONT_SRC" "$FONT_DST"

if [ -f "$CONSOLE_DEFAULTS" ]; then
    cp "$CONSOLE_DEFAULTS" "${CONSOLE_DEFAULTS}.bak-$(date +%Y%m%d-%H%M%S)"
fi
cat > "$CONSOLE_DEFAULTS" <<'CONF'
# Configured for wdf-panel 6x14 custom font
FONT=/usr/local/share/consolefonts/wdf-panel-6x14.psf.gz
FONTFACE=
FONTSIZE=
CHARMAP=UTF-8
CONF
setupcon
echo "    grid: $(stty -F /dev/tty1 size)"

echo "==> installing pi-panel-info"
install -m 0755 "$SCRIPT_DIR/pi-panel-info" /usr/local/bin/pi-panel-info
python3 -m py_compile /usr/local/bin/pi-panel-info && echo "    py_compile OK"

echo "==> installing systemd service"
install -m 0644 "$SCRIPT_DIR/pi-panel-info.service" /etc/systemd/system/pi-panel-info.service
systemctl daemon-reload
systemctl enable pi-panel-info.service
systemctl restart pi-panel-info.service
sleep 1

echo "==> status"
systemctl is-active pi-panel-info.service || true
systemctl show -p SubState,ExecMainStatus pi-panel-info.service
echo "    journal (last 5):"
journalctl -u pi-panel-info.service -b --no-pager | tail -5
echo "==> done"
