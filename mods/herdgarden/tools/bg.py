#!/usr/bin/env python3
"""Draws the valley picture that sits behind the panes, at exactly the size of the panes' area.

  bg.py <scene.bin> <out.png> <width> <height> <canvas #rrggbb> <strength 0-100> <blur px>

The scene (a small palette file, 2 picture pixels per art pixel) goes in the bottom-right corner on the
canvas color, faded toward its left and top edges, at the given strength, blurred by the given amount.
Herdr can only stretch a background to cover its node, so the picture must match the node's size.
Standard library only. The mod runs this; it reads one file and writes one file.
"""
import math, struct, sys, zlib, os

SCALE = 2


def main(src, out, w, h, canvas, strength, blur):
    w, h, k, blur = int(w), int(h), max(0.0, min(100.0, float(strength))) / 100, float(blur)
    c = tuple(int(canvas.lstrip('#')[i:i + 2], 16) for i in (0, 2, 4))
    b = open(src, 'rb').read()
    assert b[:4] == b'HVS1'
    sw, sh, n = struct.unpack('<HHH', b[4:10])
    pal = [tuple(b[10 + i * 3:13 + i * 3]) for i in range(n)]
    idx = b[10 + n * 3:]
    # one list per channel, each a list of rows
    art = [[[float(c[ch])] * sw for _ in range(sh)] for ch in range(3)]
    for y in range(sh):
        fy = min(1.0, y / sh / 0.2)
        row = idx[y * sw:(y + 1) * sw]
        for x, i in enumerate(row):
            if i:
                a = k * fy * min(1.0, x / sw / 0.24)
                p = pal[i - 1]
                for ch in range(3):
                    art[ch][y][x] = c[ch] + (p[ch] - c[ch]) * a
    sigma = blur / SCALE
    if sigma > 0.1:
        r = max(1, math.ceil(sigma * 2.5))
        ker = [math.exp(-(i * i) / (2 * sigma * sigma)) for i in range(-r, r + 1)]
        tot = sum(ker)
        ker = [v / tot for v in ker]
        for ch in range(3):
            rows = art[ch]
            # across, then down; edges repeat
            rows = [[sum(kv * row[min(sw - 1, max(0, x + i - r))] for i, kv in enumerate(ker)) for x in range(sw)] for row in rows]
            rows = [[sum(kv * rows[min(sh - 1, max(0, y + i - r))][x] for i, kv in enumerate(ker)) for x in range(sw)] for y in range(sh)]
            art[ch] = rows
    smooth = sigma > 0.1
    pw, ph = sw * SCALE, sh * SCALE
    x0, y0 = w - pw, h - ph
    blank = b'\0' + bytes(c) * w
    left = bytes(c) * max(0, x0)
    skip = max(0, -x0)
    raw = bytearray()
    for y in range(h):
        py = y - y0
        if py < 0:
            raw += blank
            continue
        ay = py >> 1
        ay2 = min(sh - 1, ay + 1) if (smooth and py & 1) else ay
        line = bytearray()
        r0, g0, b0 = art[0][ay], art[1][ay], art[2][ay]
        r1, g1, b1 = art[0][ay2], art[1][ay2], art[2][ay2]
        for ax in range(sw):
            ax2 = min(sw - 1, ax + 1) if smooth else ax
            p = (int((r0[ax] + r1[ax]) / 2 + 0.5), int((g0[ax] + g1[ax]) / 2 + 0.5), int((b0[ax] + b1[ax]) / 2 + 0.5))
            q = (int((r0[ax] + r0[ax2] + r1[ax] + r1[ax2]) / 4 + 0.5), int((g0[ax] + g0[ax2] + g1[ax] + g1[ax2]) / 4 + 0.5), int((b0[ax] + b0[ax2] + b1[ax] + b1[ax2]) / 4 + 0.5))
            line += bytes(p) + bytes(q)
        raw += b'\0' + left + bytes(line[skip * 3:])

    def chunk(t, d):
        return struct.pack('>I', len(d)) + t + d + struct.pack('>I', zlib.crc32(t + d) & 0xffffffff)
    tmp = out + '.part'
    with open(tmp, 'wb') as f:
        f.write(b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 2, 0, 0, 0)) + chunk(b'IDAT', zlib.compress(bytes(raw), 6)) + chunk(b'IEND', b''))
    os.replace(tmp, out)


if __name__ == '__main__':
    main(*sys.argv[1:8])
