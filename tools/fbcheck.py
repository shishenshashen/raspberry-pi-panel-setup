import collections, struct, zlib, sys

W, H = 480, 320
raw = open('/dev/fb0', 'rb').read(W * H * 2)
px = struct.unpack('<%dH' % (W * H), raw)

cnt = collections.Counter(px)
print("distinct colors: %d, nonzero px: %d" % (len(cnt), sum(n for c, n in cnt.items() if c)))
for c, n in cnt.most_common(8):
    r = ((c >> 11) & 0x1f) * 255 // 31
    g = ((c >> 5) & 0x3f) * 255 // 63
    b = (c & 0x1f) * 255 // 31
    print("  %04x  fb(%3d,%3d,%3d)  n=%d" % (c, r, g, b, n))


def chunk(t, d):
    return struct.pack('>I', len(d)) + t + d + struct.pack('>I', zlib.crc32(t + d) & 0xffffffff)


def write_png(path, panel):
    rows = []
    for y in range(H):
        row = bytearray([0])
        for x in range(W):
            c = px[y * W + x]
            r = ((c >> 11) & 0x1f) * 255 // 31
            g = ((c >> 5) & 0x3f) * 255 // 63
            b = (c & 0x1f) * 255 // 31
            if panel:
                r, g, b = 255 - r, 255 - g, 255 - b  # 实测映射: 纯反相
            row += bytes((r, g, b))
        rows.append(bytes(row))
    png = b'\x89PNG\r\n\x1a\n'
    png += chunk(b'IHDR', struct.pack('>IIBBBBB', W, H, 8, 2, 0, 0, 0))
    png += chunk(b'IDAT', zlib.compress(b''.join(rows), 6))
    png += chunk(b'IEND', b'')
    open(path, 'wb').write(png)


suffix = sys.argv[1] if len(sys.argv) > 1 else 'snap'
write_png('/tmp/fb-%s-raw.png' % suffix, False)
write_png('/tmp/fb-%s-panel.png' % suffix, True)
print("wrote /tmp/fb-%s-raw.png /tmp/fb-%s-panel.png" % (suffix, suffix))
