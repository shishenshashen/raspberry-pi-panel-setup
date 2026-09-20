import os, time

# 面板实测映射 = 纯反相: 显示色 = 255 - framebuffer 值
# （2026-09-20 用 B/C 双候选色测试确认: B 行 fb=ff00ff 显示为绿）
# 因此 framebuffer 调色板 = 目标显示色的反相，目标 = 标准 VGA 色 + 正文亮绿:
palette = ["ffffff",  # 0  bg      -> 000000 黑
           "55ffff",  # 1  red     -> aa0000
           "ff55ff",  # 2  green   -> 00aa00
           "55aaff",  # 3  brown   -> aa5500
           "ffff55",  # 4  blue    -> 0000aa
           "55ff55",  # 5  magenta -> aa00aa
           "ff5555",  # 6  cyan    -> 00aaaa
           "ff00ff",  # 7  text    -> 00ff00 亮绿
           "aaaaaa",  # 8  gray    -> 555555
           "00aaaa",  # 9  b-red   -> ff5555
           "aa00aa",  # 10 b-green -> 55ff55
           "0000aa",  # 11 yellow  -> ffff55
           "aaaa00",  # 12 b-blue  -> 5555ff
           "00aa00",  # 13 b-mag   -> ff55ff
           "aa0000",  # 14 b-cyan  -> 55ffff
           "000000"]  # 15 white   -> ffffff

seq = "".join("\033]P%x%s" % (i, v) for i, v in enumerate(palette))
seq += "\033[2J\033[H"


def row(txt):
    return txt + "\r\n"


seq += row("=" * 60)
seq += row(" wdf-pai display OK                  %s" % time.strftime("%Y-%m-%d %H:%M"))
seq += row("-" * 60)
seq += row(" panel : ILI9486 SPI 480x320  rotate=270   (no reboot)")
seq += row(" font  : VGA 8x16   60x20 chars")
seq += row(" color : black bg + green text")
seq += row("")
seq += row(" palette written at runtime via console OSC; the boot")
seq += row(" cmdline vt.default_* now carries the same values.")
seq += row("")
seq += row(" login on the panel will show here.")
seq += row("=" * 60)

fd = os.open("/dev/tty1", os.O_WRONLY | os.O_NOCTTY)
try:
    os.write(fd, seq.encode())
finally:
    os.close(fd)
print("palette entries written: %d, screen refreshed" % len(palette))
