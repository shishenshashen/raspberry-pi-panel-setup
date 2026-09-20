import os

# 演示调色板: 0=背景  7=默认文字  1=候选绿B  2=候选绿C
pal = {0: "ffffff", 7: "000000", 1: "ff00ff", 2: "00ffff"}
seq = "".join("\033]P%x%s" % (i, v) for i, v in sorted(pal.items()))


def row(txt, esc=""):
    return (esc + txt + "\033[0m\r\n") if esc else (txt + "\r\n")


seq += "\033[2J\033[H"
seq += row("=" * 60)
seq += row(" wdf-pai console check                         2026-09-20")
seq += row("-" * 60)
seq += row(" Q:  which line below looks GREEN ?   answer B or C")
seq += row("")
seq += row(" B)  ##################################################", "\033[31m")
seq += row(" C)  ##################################################", "\033[32m")
seq += row("")
seq += row(" A)  this line is WHITE   (option A = white text)")
seq += row("")
seq += row("-" * 60)
seq += row(" normal text color:  A = white    B/C = the green one")
seq += row("=" * 60)

fd = os.open("/dev/tty1", os.O_WRONLY | os.O_NOCTTY)
try:
    os.write(fd, seq.encode())
finally:
    os.close(fd)
print("demo drawn on tty1")
