"""Tiny pixel-art toolkit: RGBA canvas, shapes, ASCII stamps, PNG writer (no deps)."""
import zlib, struct


def hexc(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def mix(a, b, t):
    return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))


class C:
    def __init__(s, w, h):
        s.w, s.h = w, h
        s.p = [[None] * w for _ in range(h)]

    def set(s, x, y, c):
        x, y = int(x), int(y)
        if 0 <= x < s.w and 0 <= y < s.h:
            s.p[y][x] = c

    def get(s, x, y):
        return s.p[y][x] if 0 <= x < s.w and 0 <= y < s.h else None

    def rect(s, x0, y0, x1, y1, c):
        for y in range(int(y0), int(y1) + 1):
            for x in range(int(x0), int(x1) + 1):
                s.set(x, y, c)

    def disc(s, cx, cy, r, c):
        for y in range(int(cy - r - 1), int(cy + r + 2)):
            for x in range(int(cx - r - 1), int(cx + r + 2)):
                if (x - cx) ** 2 + (y - cy) ** 2 <= r * r + 0.5:
                    s.set(x, y, c)

    def ellipse(s, cx, cy, rx, ry, c):
        for y in range(int(cy - ry - 1), int(cy + ry + 2)):
            for x in range(int(cx - rx - 1), int(cx + rx + 2)):
                if ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1.0:
                    s.set(x, y, c)

    def stamp(s, ox, oy, rows, pal):
        for y, r in enumerate(rows):
            for x, ch in enumerate(r):
                if ch != '.':
                    s.set(ox + x, oy + y, pal[ch])

    def blit(s, o, ox, oy, scale=1):
        for y in range(o.h):
            for x in range(o.w):
                c = o.p[y][x]
                if c is not None:
                    s.rect(ox + x * scale, oy + y * scale, ox + x * scale + scale - 1, oy + y * scale + scale - 1, c)

    def png(s, path, scale=1, bg=None):
        W, H = s.w * scale, s.h * scale
        raw = bytearray()
        for y in range(H):
            raw.append(0)
            row = s.p[y // scale]
            for x in range(W):
                c = row[x // scale]
                if c is None:
                    raw += bytes((*bg, 255)) if bg else b'\0\0\0\0'
                elif len(c) == 4:
                    raw += bytes(c)
                else:
                    raw += bytes((*c, 255))

        def chunk(t, d):
            return struct.pack('>I', len(d)) + t + d + struct.pack('>I', zlib.crc32(t + d) & 0xffffffff)

        with open(path, 'wb') as f:
            f.write(b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', W, H, 8, 6, 0, 0, 0))
                    + chunk(b'IDAT', zlib.compress(bytes(raw), 9)) + chunk(b'IEND', b''))


def sprite(art, pal):
    rows = art.strip('\n').split('\n')
    w = len(rows[0])
    assert all(len(r) == w for r in rows), [len(r) for r in rows]
    c = C(w, len(rows))
    c.stamp(0, 0, rows, {k: hexc(v) for k, v in pal.items()})
    return c
