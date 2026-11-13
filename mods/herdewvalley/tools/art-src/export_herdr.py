"""Exports the Herdewvalley art for the Herdr mod. Everything is drawn by the scripts next to this one;
this file only scales it up (so Herdr's smooth image scaling still shows hard pixels), bakes the dawn and
night light into the yard pictures (Herdr has no blend modes), and packs the valley scenes as small
palette files the mod can read without a PNG decoder.

  python3 export_herdr.py <out folder>      e.g. ~/.config/herdr-app/mods/herdewvalley/art
"""
import os, sys, math, struct, zlib, subprocess, tempfile, shutil
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from px import C, hexc
import scene as valley
import garden2 as g2
import garden_empty as ge
import garden_seasons as gs
import sprites24
import villagers3 as v3
import villagers_side as vside
import villagers_seasons as vsn

OUT = os.path.abspath(os.path.expanduser(sys.argv[1]))
SEASONS = ('spring', 'summer', 'autumn', 'winter')
TODS = ('dawn', 'day', 'night')
KINDS = ('farmhouse', 'cabin', 'barn', 'greenhouse', None)


def rgba(p):
    if p is None:
        return b'\0\0\0\0'
    return bytes(p) if len(p) == 4 else bytes((*p, 255))


def save(c, path, scale=1):
    """PNG at an integer scale, nearest neighbour. Rows are built as bytes, so large pictures stay quick."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    raw = bytearray()
    for row in c.p:
        line = b'\0' + b''.join(rgba(p) * scale for p in row)
        raw += line * scale

    def chunk(t, d):
        return struct.pack('>I', len(d)) + t + d + struct.pack('>I', zlib.crc32(t + d) & 0xffffffff)
    with open(path, 'wb') as f:
        f.write(b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', c.w * scale, c.h * scale, 8, 6, 0, 0, 0))
                + chunk(b'IDAT', zlib.compress(bytes(raw), 9)) + chunk(b'IEND', b''))


def flip(c):
    o = C(c.w, c.h)
    o.p = [list(reversed(r)) for r in c.p]
    return o


def crop(c, x0, y0, w, h):
    o = C(w, h)
    for y in range(h):
        o.p[y] = c.p[y0 + y][x0:x0 + w]
    return o


def mul(p, t, k=1.0):
    if p is None:
        return None
    out = tuple(round(p[i] * (1 - k) + p[i] * t[i] / 255 * k) for i in range(3))
    return out if len(p) == 3 else (*out, p[3])


def webp(frames, path, ms, scale=1):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = tempfile.mkdtemp()
    names = []
    for i, f in enumerate(frames):
        n = os.path.join(tmp, f'f{i:03d}.png'); save(f, n, scale); names.append(n)
    args = ['img2webp', '-loop', '0', '-lossless']
    for n in names:
        args += ['-d', str(ms), n]
    subprocess.run(args + ['-o', path], check=True, capture_output=True)
    shutil.rmtree(tmp)


# ---------- yard: light baked in for dawn and night ----------
POOLS = (((104, 52), (24, 36, 48)), ((7, 72), (18, 32, 46)), ((198, 97), (16, 26, 36)))
TINT = {'night': (74, 84, 152), 'dawn': (176, 150, 186)}
EXTRA = {('winter', 'night'): (142, 150, 200), ('winter', 'dawn'): (226, 214, 228), ('autumn', 'night'): (196, 192, 214)}
GLOW = {'night': 1.0, 'dawn': 0.6}
GLOW_K = {('winter', 'night'): 0.55, ('autumn', 'night'): 0.7}


def step(d, radii, vals):
    for r, v in zip(radii, vals):
        if d <= r:
            return v
    return vals[-1]


def lit(c, season, tod, kind):
    if tod == 'day':
        return c
    o = C(c.w, c.h)
    layer = g2.lit_layer(kind) if kind else ge.lit()
    for y in range(c.h):
        for x in range(c.w):
            p = c.p[y][x]
            m, glows = 1.0, []
            for (cx, cy), radii in POOLS:
                d = math.hypot(x + 0.5 - cx, y + 0.5 - cy)
                m *= step(d, radii, (0.30, 0.55, 0.8, 1.0))
                glows.append(step(d, radii, (0.34, 0.17, 0.07, 0.0)))
            p = mul(p, TINT[tod], m)
            e = EXTRA.get((season, tod))
            if e:
                p = mul(p, e)
            k = GLOW[tod] * GLOW_K.get((season, tod), 1.0)
            for g in glows:
                a = g * k
                p = tuple(round(p[i] * (1 - a) + (255, 186, 90)[i] * a) for i in range(3))
            q = layer.p[y][x]
            if q is not None:
                a = q[3] / 255 if len(q) == 4 else 1.0
                p = tuple(round(p[i] * (1 - a) + q[i] * a) for i in range(3))
            o.p[y][x] = p
    return o


def yards():
    for season in SEASONS:
        for kind in KINDS:
            base = gs.yard(kind, season)
            for tod in TODS:
                save(lit(base, season, tod, kind), os.path.join(OUT, 'yard', f'{kind or "empty"}-{season}-{tod}.png'), 4)


# ---------- small sprites ----------
def load_png(path):
    d = open(path, 'rb').read(); w, h = struct.unpack('>II', d[16:24]); i = 8; idat = b''
    while i < len(d):
        n = struct.unpack('>I', d[i:i + 4])[0]; t = d[i + 4:i + 8]
        if t == b'IDAT':
            idat += d[i + 8:i + 8 + n]
        i += 12 + n
    raw = zlib.decompress(idat); st = w * 4 + 1
    c = C(w, h)
    for y in range(h):
        assert raw[y * st] == 0
        for x in range(w):
            q = raw[y * st + 1 + x * 4:y * st + 5 + x * 4]
            c.p[y][x] = None if q[3] == 0 else (tuple(q) if q[3] < 255 else tuple(q[:3]))
    return c


def sprites():
    art = os.path.join(HERE, 'art')
    for n in ('h-farmhouse', 'h-cabin', 'h-barn', 'h-greenhouse', 'h-lot'):
        save(load_png(os.path.join(art, n + '.png')), os.path.join(OUT, 'home', n[2:] + '.png'), 6)
    for n in ('g-can', 'g-basket', 'g-bang', 'g-shovel'):
        save(load_png(os.path.join(art, n + '.png')), os.path.join(OUT, 'tool', n[2:] + '.png'), 6)
    for n in ('p-1', 'p-2', 'p-3', 'p-4', 'p-wilt'):
        for cover in ('', '-winter'):
            c = load_png(os.path.join(art, n + cover + '.png'))
            for tod in TODS:
                t = C(c.w, c.h)
                t.p = [[(mul(p, TINT[tod], 0.85) if tod != 'day' else p) for p in row] for row in c.p]
                save(t, os.path.join(OUT, 'crop', f'{n[2:]}{cover}-{tod}.png'), 6)
    halo = C(56, 56)
    for y in range(56):
        for x in range(56):
            d = math.hypot(x + 0.5 - 28, y + 0.5 - 28)
            a = step(d, (10, 18, 27), (0.46, 0.26, 0.12, 0))
            if a:
                halo.p[y][x] = ((255, 216, 142) if d <= 10 else (255, 202, 122)) + (round(a * 255),)
    save(halo, os.path.join(OUT, 'tool', 'halo.png'), 4)


def villagers():
    for season in SEASONS:
        for name in vsn.NAMES:
            vsn.now['name'], vsn.now['o'] = name, vsn.OUTFIT[name].get(season, {})
            pal = vsn.palette(name, season)
            rows = [''.join(r) for r in getattr(v3, name)()[0]]
            base = os.path.join(OUT, 'villager', f'{name}-{season}')
            c = C(16, 32); c.stamp(0, 0, rows, pal); save(c, base + '.png', 6)
            b = C(16, 20); b.stamp(0, 0, rows[1:21], pal); save(b, base + '-bust.png', 6)
            f = C(16, 16); f.stamp(0, 0, rows[0:16], pal); save(f, base + '-face.png', 6)
            # a step: the body rises one pixel while the feet stay on the ground
            st = C(16, 32); st.stamp(0, 0, rows[1:28] + [rows[27]] + rows[28:], pal); save(st, base + '-step.png', 6)
            frames = []
            for (pose, swing, dy) in vside.FRAMES:
                fr = C(16, 32); fr.stamp(0, 0, [''.join(r) for r in getattr(vside, name)(pose, swing, dy)], pal); frames.append(fr)
            webp(frames, base + '-walk-r.webp', 215, 4)
            webp([flip(x) for x in frames], base + '-walk-l.webp', 215, 4)
            save(frames[1], base + '-stand-r.png', 6); save(flip(frames[1]), base + '-stand-l.png', 6)
    vsn.now['o'] = {}


# ---------- what falls in the yard: one seamless loop per season ----------
def weather():
    W, H, T = 212, 132, 48
    looks = {'spring': ((251, 208, 221), (255, 255, 255)), 'autumn': ((232, 134, 46), (241, 192, 64), (201, 71, 43)), 'winter': ((255, 255, 255),)}
    count = {'spring': 9, 'autumn': 10, 'winter': 18}
    for season, cols in looks.items():
        r = 3
        parts = []
        for i in range(count[season]):
            r = (r * 9301 + 49297) % 233280; x0 = r % (W - 6) + 3
            r = (r * 9301 + 49297) % 233280; y0 = r % H
            r = (r * 9301 + 49297) % 233280; sw = 2 + r % 5
            parts.append((x0, y0, 1 + (i % 3 == 0), sw, cols[i % len(cols)], i))
        frames = []
        for t in range(T):
            c = C(W, H)
            for (x0, y0, k, sw, col, i) in parts:
                y = (y0 + k * H * t // T) % H
                x = x0 + round(sw * math.sin(2 * math.pi * (t / T) * (1 + i % 2) + i))
                c.set(x, y, col)
                if season != 'winter' or i % 3 == 0:
                    c.set(x + 1, y, col)
                if season == 'winter' and i % 3 == 0:
                    c.set(x, y + 1, col); c.set(x + 1, y + 1, col)
            frames.append(c)
        webp(frames, os.path.join(OUT, 'weather', f'{season}.webp'), 110, 2)
        save(frames[0], os.path.join(OUT, 'weather', f'{season}.png'), 2)


# ---------- valley scenes as palette files ----------
def scenes():
    os.makedirs(os.path.join(OUT, 'scene'), exist_ok=True)
    for name, (paper, ink, roof, leaf, glow, blossom, sky) in valley.VARIANTS.items():
        for season in SEASONS:
            c = valley.scene(paper, ink, roof, leaf, glow, name.split('-')[1], blossom, sky, season)
            pal, idx = {}, bytearray()
            for row in c.p:
                for p in row:
                    idx.append(0 if p is None else pal.setdefault(p, len(pal) + 1))
            assert len(pal) < 255, (name, season, len(pal))
            head = b'HVS1' + struct.pack('<HHH', c.w, c.h, len(pal))
            with open(os.path.join(OUT, 'scene', f'{name}-{season}.bin'), 'wb') as f:
                f.write(head + b''.join(bytes(p) for p in pal) + bytes(idx))


if __name__ == '__main__':
    what = sys.argv[2:] or ['sprites', 'villagers', 'weather', 'scenes', 'yards']
    for w in what:
        globals()[w]()
        print('done', w)
