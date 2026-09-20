# pi-config

Raspberry Pi 4B (8 GB, Debian 13 trixie) configuration backup for a headless
setup with a **Waveshare 3.5" SPI LCD (ILI9486, waveshare35b-v2)** and a
live-refresh console dashboard.

Tested on kernel `6.18.50+rpt-rpi-v8` (2026-09-20).

---

## Repository layout

```
boot/
  config.txt          kernel/firmware config (SPI + overlay)
  cmdline.txt         boot command line (palette + fbcon font)
dotfiles/             bash_profile / bashrc session mirror (optional)
panel/                console dashboard + custom font
  pi-panel-info           dashboard renderer (Python 3)
  pi-panel-info.service   systemd unit
  pi-panel-info-install.sh one-command installer
  mkfont614.py            rebuilds 6x12 → 6x14 PSF2 font
  wdf-panel-6x14.psf.gz  the custom 6x14 console font
tools/                diagnostic utilities
  fbcheck.py              read /dev/fb0 → histogram + PNG
  sgrprobe*.py            probe Linux console SGR intensity bit
  console-palette.py      write 16-colour palette via OSC
  console-demo.py         colour demo page
screenshots/          what the panel looks like
```

---

## Display: Waveshare 3.5" SPI LCD

### Hardware

- ILI9486 controller on SPI0, 480×320 pixels
- RST = GPIO 25, DC = GPIO 24, CS1 carries ADS7846 touch
- Panel colour mapping (measured): **displayed = 255 − framebuffer** (plain
  per-channel inversion, no channel swap).  fb `000000` → white screen;
  fb `ffffff` → black screen.

### Device-tree overlay

The official Raspberry Pi firmware (as of 2026-09) does **not** ship a
`waveshare35b-v2.dtbo`.  Build it from the public source:

```bash
# on the Pi
git clone https://github.com/swkim01/waveshare-dtoverlays.git
cd waveshare-dtoverlays
dtc -@ -I dts -O dtb -o waveshare35b-v2.dtbo waveshare35b-v2.dts
sudo cp waveshare35b-v2.dtbo /boot/firmware/overlays/
```

### config.txt additions

```ini
[all]
dtparam=spi=on
dtoverlay=waveshare35b-v2,rotate=270
```

### cmdline.txt additions

```
fbcon=font:VGA8x16
vt.default_red=0xFF,0x55,0xFF,0x55,0xFF,0x55,0xFF,0xFF,0xAA,0x00,0xAA,0x00,0xAA,0x00,0xAA,0x00
vt.default_grn=0xFF,0xFF,0x55,0xAA,0xFF,0xFF,0x55,0x00,0xAA,0xAA,0x00,0x00,0xAA,0xAA,0x00,0x00
vt.default_blu=0xFF,0xFF,0xFF,0xFF,0x55,0x55,0x55,0xFF,0xAA,0xAA,0xAA,0xAA,0x00,0x00,0x00,0x00
```

Remove `quiet splash` if present.  The `vt.default_*` values are the
**inverted** standard VGA palette (because the panel inverts the framebuffer).

### Runtime hot-load (no reboot)

```bash
sudo dtoverlay waveshare35b-v2 rotate=270
# verify: configfs status = applied
cat /sys/kernel/config/device-tree/overlays/0_waveshare35b-v2/status
```

---

## Console dashboard (pi-panel-info)

A two-line status screen that lives on `/dev/tty1`:

```
2026-09-20 16:43:04  up 1h46m  temp 58.9C  mem 0.9G/7.6G
ip 172.12.0.1/24 eth0 (default)  wlan0 -  disk 20%/58G free 44G
======================================================================
services  dsh ok   cable-proxy ok   docker ok
docker    0 running / 0 total containers  load      0.38 0.62 2.64
```

- **Refresh**: 1-second clock tick, 10-second slow-metric refresh
  (configurable via `--interval N`).  Flicker-free per-row repaint.
- **Font**: custom 6×14 PSF2 (built from Lat15-Terminus12x6 with 1 px
  padding top/bottom → 80×22 grid on the 480×320 panel).
- **Colours**: white labels, bright-green body, grey separator, red alerts.
- **Services monitored**: dsh, dsh-cable-proxy.socket, docker (edit the
  `SERVICES` tuple in the script to change).

### Install

```bash
# copy the panel/ directory to the Pi, then:
cd panel
sudo bash pi-panel-info-install.sh
```

The installer:
1. Copies the 6×14 font to `/usr/local/share/consolefonts/`
2. Writes `/etc/default/console-setup` (backs up the old one)
3. Installs `pi-panel-info` to `/usr/local/bin/`
4. Installs and enables the systemd service

### Uninstall

```bash
sudo systemctl disable --now pi-panel-info.service
sudo rm /etc/systemd/system/pi-panel-info.service /usr/local/bin/pi-panel-info
sudo cp /etc/default/console-setup.bak-* /etc/default/console-setup
sudo setupcon
```

---

## Linux console colour gotchas

### SGR intensity bit

The Linux console stores 90–97 (bright colours) as a separate intensity bit,
independent of the base colour set by 30–37.  A sequence like `\033[97m`
followed by `\033[37m` changes only the base colour — the intensity bit
stays set, so text renders bright white instead of the intended colour.

**Fix**: always reset before setting body text colour:
```python
BODY = "\033[0;37m"   # reset first, then set colour
```

### Framebuffer inversion

Because the panel displays `255 − fb`, any screenshot tool that reads
`/dev/fb0` directly (like `tools/fbcheck.py`) must invert the pixels to
produce a PNG that matches what you see on screen.  The script writes two
files: `-raw.png` (framebuffer as-is) and `-panel.png` (inverted, matches
the physical display).

---

## Diagnostic tools

| Script | Purpose |
|---|---|
| `fbcheck.py <tag>` | Read `/dev/fb0`, print colour histogram, write raw + panel PNGs |
| `sgrprobe.py` | Demonstrate the 90–97 intensity bit persistence bug |
| `sgrprobe2.py` | Variant with explicit reset sequences |
| `sgrprobe3.py` | Pixel-counting probe (reads fb after writing SGR) |
| `console-palette.py` | Write the 16-colour inverted palette via OSC to `/dev/tty1` |
| `console-demo.py` | Render a colour demo page for visual calibration |

---

## Rollback reference

All changes made on 2026-09-20 are reversible without a reboot:

| What | Undo |
|---|---|
| Overlay loaded | `sudo dtoverlay -r waveshare35b-v2` |
| config.txt | `sudo cp /boot/firmware/config.txt.bak-20260920-display /boot/firmware/config.txt` |
| cmdline.txt (overlay) | `sudo cp /boot/firmware/cmdline.txt.bak-20260920-display /boot/firmware/cmdline.txt` |
| cmdline.txt (palette) | `sudo cp /boot/firmware/cmdline.txt.bak-20260920-palette /boot/firmware/cmdline.txt` |
| Console font | `sudo cp /etc/default/console-setup.bak-20260920-selfont /etc/default/console-setup && sudo setupcon` |
| Dashboard service | `sudo systemctl disable --now pi-panel-info.service && sudo rm /etc/systemd/system/pi-panel-info.service /usr/local/bin/pi-panel-info` |
| DTBO file | `sudo rm /boot/firmware/overlays/waveshare35b-v2.dtbo` |

---

## Notes

- `fb_ili9486` does not implement `.blank` — `/sys/class/graphics/fb0/blank`
  reads 4 and writing 0 returns I/O error.  This is normal, not a fault.
- SPI DMA means `/proc/interrupts` shows 0 for SPI; use
  `/sys/bus/spi/devices/spi0.0/statistics/bytes` to verify data flow
  (one frame ≈ 307 KB for 480×320×2).
- `card1-HDMI-A-1` / `card1-HDMI-A-2` showing disconnected is expected —
  they are HDMI outputs, unrelated to the SPI panel.
