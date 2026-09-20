"""Rebuild Lat15-Terminus12x6 (PSF2 6x12) with 1 blank pixel above and below,
so the console keeps the same glyphs but gets ~17% more leading (6x14)."""
import gzip
import struct

SRC = "/usr/share/consolefonts/Lat15-Terminus12x6.psf.gz"
DST = "/usr/local/share/consolefonts/wdf-panel-6x14.psf.gz"
PAD_TOP = 1
NEW_H = 14

data = gzip.open(SRC, "rb").read()
magic, ver, hsize, flags, length, charsize, h, w = struct.unpack("<8I", data[:32])
assert magic == 0x864ab572, "not PSF2"
row_bytes = (w + 7) // 8
assert charsize == h * row_bytes, "charsize mismatch"

glyphs = data[hsize:hsize + length * charsize]
rest = data[hsize + length * charsize:]
blank = b"\x00" * row_bytes
new_cs = NEW_H * row_bytes

out = bytearray()
for i in range(length):
    out += blank * PAD_TOP + glyphs[i * charsize:(i + 1) * charsize] + blank * (NEW_H - h - PAD_TOP)

psf = struct.pack("<8I", magic, ver, 32, flags, length, new_cs, NEW_H, w) + bytes(out) + rest
with gzip.open(DST, "wb") as f:
    f.write(psf)

print("source %dx%d charsize=%d flags=%#x glyphs=%d" % (w, h, charsize, flags, length))
print("wrote %s -> %dx%d charsize=%d" % (DST, w, NEW_H, new_cs))
