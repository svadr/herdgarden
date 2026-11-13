"""Animated GIFs for the README, drawn from the same art as the mod.
  python3 gifs.py <docs folder>
"""
import os, sys, math, subprocess, tempfile, shutil, random
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.argv = [sys.argv[0], tempfile.mkdtemp()] + sys.argv[1:]
import export_herdr as ex
from px import C
import garden_seasons as gs
import villagers3 as v3, villagers_side as vside, villagers_seasons as vsn, villagers_turn as vturn

DOCS = os.path.abspath(os.path.expanduser(sys.argv[2]))
ART = os.path.join(HERE, 'art')
BX, BY = 12, 80
CROPS = {'working': '2 3 3 2 3 1 2 3 2 1', 'blocked': '3 2 3 wilt 2 2 3 wilt 2 3', 'done': '4 4 4 4 4 4 4 4 4 4', 'idle': '1 1 2 1 1 1 2 1 1 1'}
LEGS = [(6.76, 30, -2, 1, 1, 1), (12.52, 30, -2, 0, 1, 1), (19.27, 62, -2, 1, 1, 1), (26.53, 96, -7, 1, 1, 0), (34.97, 136, -7, 1, 1, 1),
        (40.73, 136, -7, 0, 1, 1), (48.75, 174, -7, 1, 1, 1), (63.53, 104, -7, 1, -1, 1), (67.54, 104, 12, 1, 'down', 0), (75.22, 104, 12, 0, 1, 0),
        (78.0, 104, -2, 1, 'up', 0), (84.57, 62, -2, 1, -1, 0), (98.08, -2, -2, 1, -1, 1), (100, -2, -2, 0, 1, 1)]
sprite_cache = {}


def sprite(path):
    if path not in sprite_cache:
        sprite_cache[path] = ex.load_png(path)
    return sprite_cache[path]


def blit(c, o, x, y):
    for yy in range(o.h):
        for xx in range(o.w):
            p = o.p[yy][xx]
            if p is not None and (len(p) == 3 or p[3] > 0):
                c.set(x + xx, y + yy, p[:3])


def frames_of(name, season):
    vsn.now['name'], vsn.now['o'] = name, vsn.OUTFIT[name].get(season, {})
    pal = vsn.palette(name, season)
    walk = []
    for (pose, swing, dy) in vside.FRAMES:
        f = C(16, 32); f.stamp(0, 0, [''.join(r) for r in getattr(vside, name)(pose, swing, dy)], pal); walk.append(f)
    front = C(16, 32); front.stamp(0, 0, [''.join(r) for r in getattr(v3, name)()[0]], pal)
    turn = {}
    for view, back in (('down', False), ('up', True)):
        fr = []
        for g in vturn.walk(vturn.turned(name, back)):
            f = C(16, 32); f.stamp(0, 0, [''.join(r) for r in g], pal); fr.append(f)
        turn[view] = fr
    vsn.now['o'] = {}
    return walk, front, turn


def where(t):
    """Position, facing, walking, tool in use at t (0..1 of the round)."""
    pct, prev, px, py = t * 100, 0, -2, -2
    for (until, x, y, walk, d, work) in LEGS:
        if pct <= until:
            k = (pct - prev) / (until - prev)
            return px + (x - px) * k, py + (y - py) * k, d, walk, work
        prev, px, py = until, x, y
    return -2, -2, 1, 0, 1


def particles(season, t, rnd_seed=4):
    if season == 'summer':
        return []
    cols = {'spring': [(251, 208, 221), (255, 255, 255)], 'autumn': [(232, 134, 46), (241, 192, 64), (201, 71, 43)], 'winter': [(255, 255, 255)]}[season]
    n = {'spring': 10, 'autumn': 12, 'winter': 22}[season]
    rnd = random.Random(rnd_seed)
    out = []
    for i in range(n):
        x0, y0, sp, sw = rnd.uniform(0, 212), rnd.uniform(0, 132), rnd.uniform(0.6, 1.2), rnd.uniform(2, 6)
        y = (y0 + t * 132 * 2 * sp) % 132
        x = x0 + sw * math.sin(t * 2 * math.pi * 3 * sp + i)
        out.append((int(x), int(y), cols[i % len(cols)], 2 if season != 'winter' or i % 3 == 0 else 1))
    return out


def yard_frame(season, tod, status, t, who='farmer', kind='farmhouse', walk_t=None):
    base = bases[(kind, season, tod)]
    c = C(base.w, base.h); c.p = [row[:] for row in base.p]
    crops = CROPS[status].split()
    winter = season == 'winter'
    crop = lambda i: sprite(os.path.join(ART, f'p-{crops[i]}{"-winter" if winter else ""}.png'))
    for i in range(5):
        blit(c, crop(i), BX + 5 + i * 15, BY + 6)
    walk, front, turn = villager_frames[(who, season)]
    if status == 'working':
        x, y, d, walking, work = where(walk_t if walk_t is not None else t)
        x, y = int(BX + x), int(BY + y)
        if d in ('down', 'up'):
            blit(c, turn[d][int(t * 200) % 4], x, y)
            if d == 'down':
                blit(c, sprite(os.path.join(ART, 'g-can.png' if not winter else 'g-shovel.png')), x + 11, y + 20)
            for (xx, yy, col, sz) in particles(season, t):
                for dx in range(sz):
                    c.set(xx + dx, yy, col)
            return c
        f = walk[int(t * 200) % 4] if walking else walk[1]
        if d < 0:
            f = ex.flip(f)
        blit(c, f, x, y)
        right = d > 0
        mx = lambda px, w: px if right else 16 - px - w
        if not winter:
            can = sprite(os.path.join(ART, 'g-can.png'))
            blit(c, can if right else ex.flip(can), x + mx(11, 9), y + 19)
            if work:
                for k, (dx, dy) in enumerate(((21, 22), (20, 25), (22, 27))):
                    if (int(t * 120) + k) % 3:
                        c.set(x + mx(dx, 1), y + dy + (int(t * 240) + k) % 4, (191, 230, 245))
        else:
            sh = sprite(os.path.join(ART, 'g-shovel.png'))
            lift = 5 if (not walking and int(t * 70) % 2) else 0
            blit(c, sh if right else ex.flip(sh), x + mx(8, 14), y + 18 - lift)
            if lift:
                for (dx, dy) in ((21, 14), (23, 11), (19, 12)):
                    c.set(x + mx(dx, 2), y + dy, (255, 255, 255)); c.set(x + mx(dx, 2) + 1, y + dy, (255, 255, 255))
    else:
        spot = {'blocked': (97, 62), 'done': (BX + 32, BY - 2), 'idle': (118, 90)}[status]
        blit(c, front, *spot)
        if status == 'done':
            blit(c, sprite(os.path.join(ART, 'g-basket.png')), spot[0] + 10, spot[1] + 21)
        if status == 'blocked' and int(t * 40) % 2 == 0:
            blit(c, sprite(os.path.join(ART, 'g-bang.png')), spot[0] + 5, spot[1] - 10)
    for i in range(5, 10):
        blit(c, crop(i), BX + 5 + (i % 5) * 15, BY + 30)
    for (x, y, col, sz) in particles(season, t):
        for dx in range(sz):
            c.set(x + dx, y, col)
    return c


def gif(frames, path, delay, scale=3):
    tmp = tempfile.mkdtemp()
    names = []
    for i, f in enumerate(frames):
        n = os.path.join(tmp, f'{i:04d}.png'); ex.save(f, n, scale); names.append(n)
    subprocess.run(['magick', '-delay', str(delay), '-loop', '0', *names, '-layers', 'Optimize', path], check=True)
    shutil.rmtree(tmp)
    print(path, os.path.getsize(path) // 1024, 'KB')


if __name__ == '__main__':
    os.makedirs(DOCS, exist_ok=True)
    bases, villager_frames = {}, {}
    need = [('farmhouse', s, 'day') for s in ex.SEASONS] + [('farmhouse', 'summer', 'night'), ('farmhouse', 'winter', 'night'), ('farmhouse', 'autumn', 'dawn')]
    for (kind, season, tod) in need:
        bases[(kind, season, tod)] = ex.lit(gs.yard(kind, season), season, tod, kind)
    for who in ('farmer', 'tinker', 'gardener', 'elder'):
        for season in ex.SEASONS:
            villager_frames[(who, season)] = frames_of(who, season)
    # 1. a whole round of watering, compressed: 52 s in 10 s
    n = 100
    gif([yard_frame('summer', 'day', 'working', i / n, walk_t=i / n) for i in range(n)], os.path.join(DOCS, 'yard-round.gif'), 10)
    # 2. the four seasons, 3 s each, villager working
    fr = []
    for k, season in enumerate(ex.SEASONS):
        for i in range(30):
            t = i / 30
            fr.append(yard_frame(season, 'day', 'working', t * 0.4 + k * 0.1, walk_t=0.02 + t * 0.10 if season != 'winter' else 0.07 + t * 0.05))
    gif(fr, os.path.join(DOCS, 'yard-seasons.gif'), 10)
    # 3. the four states, side by side
    states = ('working', 'blocked', 'done', 'idle')
    fr = []
    for i in range(40):
        t = i / 40
        tiles = [yard_frame('summer', 'day', st, t, walk_t=0.0 + t * 0.12) for st in states]
        sheet = C(212 * 4 + 6, 132)
        for k, tile in enumerate(tiles):
            for y in range(132):
                sheet.p[y][k * 214:k * 214 + 212] = tile.p[y]
        fr.append(sheet)
    gif(fr, os.path.join(DOCS, 'yard-states.gif'), 10, scale=2)
    # 4. the yard after dark, in winter: lamps lit, snow, shovel
    gif([yard_frame('winter', 'night', 'working', i / 40, walk_t=0.07 + (i / 40) * 0.05) for i in range(40)], os.path.join(DOCS, 'yard-winter-night.gif'), 10)
    # 5. the villagers walking, every season
    fr = []
    for i in range(8):
        sheet = C(4 * 20 + 4, 4 * 34 + 2)
        for col, who in enumerate(('farmer', 'tinker', 'gardener', 'elder')):
            for row, season in enumerate(ex.SEASONS):
                blit(sheet, villager_frames[(who, season)][0][i % 4], 4 + col * 20, 1 + row * 34)
        fr.append(sheet)
    tmp = tempfile.mkdtemp(); names = []
    for i, f in enumerate(fr):
        nm = os.path.join(tmp, f'{i}.png'); ex.save(f, nm, 5); names.append(nm)
    out = os.path.join(DOCS, 'villagers.gif')
    subprocess.run(['magick', '-delay', '22', '-loop', '0', *names, '-background', '#f4f5ef', '-alpha', 'remove', '-layers', 'Optimize', out], check=True)
    print(out)
