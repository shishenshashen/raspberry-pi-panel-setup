#!/usr/bin/env bash
# One-command full restore: boot config + dtbo + console dashboard + font.
# Run as root (or with sudo) on a fresh Pi with the same SD card.
# Usage: sudo bash restore-all.sh [--skip-boot]
set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
SKIP_BOOT=false
[[ "${1:-}" == "--skip-boot" ]] && SKIP_BOOT=true

RED="\033[0;31m"; GREEN="\033[0;32m"; YELLOW="\033[1;33m"; NC="\033[0m"
ok()   { echo -e "  ${GREEN}✓${NC} $1"; }
warn() { echo -e "  ${YELLOW}⚠${NC} $1"; }
fail() { echo -e "  ${RED}✗${NC} $1"; exit 1; }

echo "========================================"
echo "  pi-config full restore"
echo "========================================"
echo

# --- PARTUUID check ---
CURRENT_UUID=$(grep -o "PARTUUID=[^ ]*" /boot/firmware/cmdline.txt 2>/dev/null | head -1 | cut -d= -f2 || echo "")
REPO_UUID=$(grep -o "PARTUUID=[^ ]*" "$REPO_DIR/boot/running/cmdline.txt" | head -1 | cut -d= -f2 || echo "")
if [ -n "$CURRENT_UUID" ] && [ -n "$REPO_UUID" ] && [ "$CURRENT_UUID" != "$REPO_UUID" ]; then
    warn "PARTUUID mismatch: this card=$CURRENT_UUID, repo=$REPO_UUID"
    warn "cmdline.txt will be patched with the correct PARTUUID before install."
    sed -i "s|PARTUUID=$REPO_UUID|PARTUUID=$CURRENT_UUID|g" "$REPO_DIR/boot/running/cmdline.txt"
    ok "cmdline.txt PARTUUID patched → $CURRENT_UUID"
fi

# --- Boot config ---
if [ "$SKIP_BOOT" = true ]; then
    warn "skipping boot config (--skip-boot)"
else
    echo "[1/4] boot config"
    cp /boot/firmware/config.txt /boot/firmware/config.txt.bak-$(date +%Y%m%d-%H%M%S) 2>/dev/null || true
    cp /boot/firmware/cmdline.txt /boot/firmware/cmdline.txt.bak-$(date +%Y%m%d-%H%M%S) 2>/dev/null || true
    cp "$REPO_DIR/boot/running/config.txt" /boot/firmware/config.txt
    cp "$REPO_DIR/boot/running/cmdline.txt" /boot/firmware/cmdline.txt
    ok "config.txt + cmdline.txt → /boot/firmware/"
fi

# --- DTBO ---
echo "[2/4] device-tree overlay"
if [ "$SKIP_BOOT" = false ]; then
    cp "$REPO_DIR/overlays/waveshare35b-v2.dtbo" /boot/firmware/overlays/waveshare35b-v2.dtbo
    ok "waveshare35b-v2.dtbo → /boot/firmware/overlays/"
else
    if [ -f /boot/firmware/overlays/waveshare35b-v2.dtbo ]; then
        ok "dtbo already present"
    else
        cp "$REPO_DIR/overlays/waveshare35b-v2.dtbo" /boot/firmware/overlays/waveshare35b-v2.dtbo
        ok "waveshare35b-v2.dtbo → /boot/firmware/overlays/"
    fi
fi

# --- Console dashboard + font ---
echo "[3/4] console dashboard + custom font"
bash "$REPO_DIR/panel/pi-panel-info-install.sh"

# --- Console-setup ---
echo "[4/4] console-setup"
if [ -f /etc/default/console-setup ]; then
    cp /etc/default/console-setup /etc/default/console-setup.bak-$(date +%Y%m%d-%H%M%S)
fi
cp "$REPO_DIR/etc/console-setup" /etc/default/console-setup
setupcon 2>/dev/null || true
ok "console-setup → /etc/default/console-setup"

echo
echo "========================================"
echo -e "  ${GREEN}Restore complete.${NC}"
echo "  Reboot required for boot config changes."
echo "  (or run: sudo dtoverlay waveshare35b-v2 rotate=270)"
echo "========================================"
