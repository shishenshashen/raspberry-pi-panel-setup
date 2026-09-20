"""Verify candidate ways to drop back to the default green after a bright
white label: the console keeps the intensity bit, so plain 37/39 stay white."""
import collections
import os
import struct
import time

W, H = 480, 320
PAL = ["ffffff", "55ffff", "ff55ff", "55aaff", "ffff55", "55ff55", "ff5555", "ff00ff",
       "aaaaaa", "00aaaa", "aa00aa", "0000aa", "aaaa00", "00aa00", "aa0000", "000000"]


def to565(h):
    return ((int(h[0:2], 16) >> 3) << 11) | ((int(h[2:4], 16) >> 2) << 5) | (int(h[4:6], 16) >> 3)


fb2pal = {}
for i, v in enumerate(PAL):
    fb2pal.setdefault(to565(v), []).append(i)

tests = [
    ("white", "\033[97m AAAA"),
    ("plain37", "\033[97mAAAA\033[37mBBBB"),
    ("zero37", "\033[97mAAAA\033[0;37mBBBB"),
    ("zero37-then-white", "\033[0;37mAAAA\033[97mBBBB"),
    ("dim-then-green", "\033[90mAAAA\033[0;37mBBBB"),
]

seq = "".join("\033]P%x%s" % (i, v) for i, v in enumerate(PAL)) + "\033[2J\033[H"
for name, body in tests:
    seq += body + "\033[0m" + "\r\n"
seq += "\033[22;1H"
with open("/dev/tty1", "wb") as f:
    f.write(seq.encode())
time.sleep(0.6)

px = struct.unpack("<%dH" % (W * H), open("/dev/fb0", "rb").read(W * H * 2))
for idx, (name, _) in enumerate(tests):
    band = px[idx * 14 * W:(idx + 1) * 14 * W]
    c = collections.Counter(p for p in band if p != 0xFFFF)   # keep white (fb 0x0000)
    print("%-18s %s" % (name, ", ".join("fb=%04x pal=%s n=%d" % (v, fb2pal.get(v, "?"), n)
                                        for v, n in c.most_common(4))))
