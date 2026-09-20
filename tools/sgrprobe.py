"""Draw one line per SGR code on tty1, then read /dev/fb0 and report which
palette index each line actually rendered with."""
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

tests = [("default", ""), ("sgr30", "\033[30m"), ("sgr37", "\033[37m"), ("sgr39", "\033[39m"),
         ("sgr97", "\033[97m"), ("sgr92", "\033[92m"), ("sgr90", "\033[90m"), ("sgr7", "\033[7m")]

seq = "".join("\033]P%x%s" % (i, v) for i, v in enumerate(PAL)) + "\033[2J\033[H"
for name, esc in tests:
    seq += esc + name.ljust(8) + "ABCdef 0123" + "\033[0m" + "\r\n"
seq += "\033[22;1H"
with open("/dev/tty1", "wb") as f:
    f.write(seq.encode())
time.sleep(0.6)

px = struct.unpack("<%dH" % (W * H), open("/dev/fb0", "rb").read(W * H * 2))
for idx, (name, esc) in enumerate(tests):
    band = px[idx * 14 * W:(idx + 1) * 14 * W]
    c = collections.Counter(p for p in band if p)
    print("%-8s %s" % (name, ", ".join("fb=%04x pal=%s n=%d" % (v, fb2pal.get(v, "?"), n)
                                       for v, n in c.most_common(3))))
