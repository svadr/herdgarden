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
SPEED = 8.6 / 1000
ROUTE = [
    ("walk", 30, -2, 1), ("stop", 3000, 1), ("walk", 62, -2, 1), ("walk", 76, -2, 1),
    ("walk", 76, 14, 0),
    ("walk", 40, 14, 1), ("stop", 3000, 1), ("walk", 6, 14, 1), ("stop", 1600, 1),
    ("walk", 76, 14, 0), ("walk", 76, -2, 0),
    ("walk", 96, -7, 0), ("walk", 136, -7, 1), ("stop", 3000, 1), ("walk", 174, -7, 1),
    ("walk", 104, -7, 1), ("walk", 104, 12, 0), ("stop", 4000, 0), ("walk", 104, -2, 0),
    ("walk", 62, -2, 0), ("walk", -2, -2, 1), ("stop", 1200, 1),
]


def build_legs():
    x, y, d, out = -2, -2, 1, []
    for kind, a, b, *rest in ROUTE:
        if kind == "stop":
            out.append((x, y, x, y, a, 0, d, b)); continue
        dx, dy = a - x, b - y
        if dx:
            d = 1 if dx > 0 else -1
        face = ('down' if dy > 0 else 'up') if abs(dy) > abs(dx) else d
        out.append((x, y, a, b, round(math.hypot(dx, dy) / SPEED), 1, face, rest[0]))
        x, y = a, b
    return out


LEGS = build_legs()
ROUND = sum(l[4] for l in LEGS)
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
    """Position, facing, walking, tool in use, and whether in the lower aisle, at t (0..1 of the round)."""
    ms = (t % 1) * ROUND
    for (x0, y0, x1, y1, d, walk, face, work) in LEGS:
        if ms <= d:
            k = ms / d if d else 1
            return x0 + (x1 - x0) * k, y0 + (y1 - y0) * k, face, walk, work, max(y0, y1) >= 10
        ms -= d
    return -2, -2, 1, 0, 1, False


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
    low = status == 'working' and where(walk_t if walk_t is not None else t)[5]
    if low:
        for i in range(5, 10):
            blit(c, crop(i), BX + 5 + (i % 5) * 15, BY + 30)
    walk, front, turn = villager_frames[(who, season)]
    if status == 'working':
        x, y, d, walking, work, low = where(walk_t if walk_t is not None else t)
        x, y = int(BX + x), int(BY + y)
        if d in ('down', 'up'):
            blit(c, turn[d][int(t * 200) % 4], x, y)
            if d == 'down':
                blit(c, sprite(os.path.join(ART, 'g-can.png' if not winter else 'g-shovel.png')), x + 11, y + 20)
            if not low:
                for i in range(5, 10):
                    blit(c, crop(i), BX + 5 + (i % 5) * 15, BY + 30)
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
    if not low:
        for i in range(5, 10):
            blit(c, crop(i), BX + 5 + (i % 5) * 15, BY + 30)
    for (x, y, col, sz) in particles(season, t):
        for dx in range(sz):
            c.set(x + dx, y, col)
    return c


# Labels are drawn smooth onto the enlarged frames, in the system UI font, so they read at any size.
UI_FONT = '/System/Library/Fonts/SFNS.ttf' if os.path.exists('/System/Library/Fonts/SFNS.ttf') else 'Helvetica'
badge_cache = {}


def badge_png(text, size):
    """A rounded dark badge with white text, as a PNG path and its size in pixels."""
    if (text, size) not in badge_cache:
        d = tempfile.mkdtemp()
        t, b = os.path.join(d, 't.png'), os.path.join(d, 'b.png')
        subprocess.run(['magick', '-background', 'none', '-fill', 'white', '-font', UI_FONT, '-pointsize', str(size), f'label:{text}', t], check=True)
        w, h = map(int, subprocess.run(['magick', 'identify', '-format', '%w %h', t], capture_output=True, text=True, check=True).stdout.split())
        bw, bh, r = w + round(size * 1.1), h + round(size * 0.5), round(size * 0.45)
        subprocess.run(['magick', '-size', f'{bw}x{bh}', 'xc:none', '-fill', 'rgba(26,32,30,0.78)', '-draw', f'roundrectangle 0,0,{bw - 1},{bh - 1},{r},{r}',
                        t, '-gravity', 'center', '-composite', b], check=True)
        badge_cache[(text, size)] = (b, bw, bh)
    return badge_cache[(text, size)]


# Mod time per GIF frame, as a share of the 52-second working round. Frames show for 0.1 s, so
# 0.16 s of mod time per frame plays the yard 1.6 times faster than it runs in Herdr.
STEP = 0.16 / 52


def gif(frames, path, delay, scale=3, labels=None):
    """labels: for each frame, a list of (text, x, y) in frame pixels before scaling."""
    tmp = tempfile.mkdtemp()
    names = []
    for i, f in enumerate(frames):
        n = os.path.join(tmp, f'{i:04d}.png'); ex.save(f, n, scale); names.append(n)
        if labels and labels[i]:
            cmd = ['magick', n]
            for (text, x, y) in labels[i]:
                b, _, _ = badge_png(text, round(7.5 * scale))
                cmd += [b, '-geometry', f'+{x * scale}+{y * scale}', '-composite']
            subprocess.run(cmd + [n], check=True)
    subprocess.run(['magick', '-delay', str(delay), '-loop', '0', *names, '-layers', 'Optimize', path], check=True)
    shutil.rmtree(tmp)
    print(path, os.path.getsize(path) // 1024, 'KB')


if __name__ == '__main__':
    os.makedirs(DOCS, exist_ok=True)
    bases, villager_frames = {}, {}
    need = [('farmhouse', s, 'day') for s in ex.SEASONS] + [('farmhouse', 'summer', 'night'), ('farmhouse', 'summer', 'dawn'), ('farmhouse', 'winter', 'night'), ('farmhouse', 'autumn', 'dawn')]
    for (kind, season, tod) in need:
        bases[(kind, season, tod)] = ex.lit(gs.yard(kind, season), season, tod, kind)
    for who in ('farmer', 'tinker', 'gardener', 'elder'):
        for season in ex.SEASONS:
            villager_frames[(who, season)] = frames_of(who, season)
    # Every yard GIF steps the same small slice of mod time per frame (STEP), so the villager walks,
    # the water drips and the "!" blinks at one steady pace, a little faster than in Herdr.
    # 1. a whole working round: watering both beds, the flower bed, the pond, and home again
    n = round(1 / STEP)
    gif([yard_frame('summer', 'day', 'working', i * STEP, walk_t=i * STEP) for i in range(n)],
        os.path.join(DOCS, 'yard-round.gif'), 10, labels=[[('Working', 4, 4)]] * n)
    # 2. the four states, side by side, each named
    states = ('working', 'blocked', 'done', 'idle')
    fr = []
    for i in range(80):
        tiles = [yard_frame('summer', 'day', st, i * STEP, walk_t=0.0 + i * STEP) for st in states]
        sheet = C(212 * 4 + 6, 132)
        for k, tile in enumerate(tiles):
            for y in range(132):
                sheet.p[y][k * 214:k * 214 + 212] = tile.p[y]
        fr.append(sheet)
    gif(fr, os.path.join(DOCS, 'yard-states.gif'), 10, scale=2,
        labels=[[(st.capitalize(), k * 214 + 4, 4) for k, st in enumerate(states)]] * len(fr))
    # 3. the four seasons, 5 s each, villager at work, the season named
    start = {'spring': 0.02, 'summer': 0.02, 'autumn': 0.02, 'winter': 0.07}
    fr, lb = [], []
    for season in ex.SEASONS:
        for i in range(50):
            t = start[season] + i * STEP
            fr.append(yard_frame(season, 'day', 'working', t, walk_t=t)); lb.append([(season.capitalize(), 4, 4)])
    gif(fr, os.path.join(DOCS, 'yard-seasons.gif'), 10, labels=lb)
    # 4. dawn, day and night in the same summer yard: lamps and windows light up after dark
    fr, lb = [], []
    for tod in ('dawn', 'day', 'night'):
        for i in range(50):
            t = 0.02 + i * STEP
            fr.append(yard_frame('summer', tod, 'working', t, walk_t=t)); lb.append([(tod.capitalize(), 4, 4)])
    gif(fr, os.path.join(DOCS, 'yard-times.gif'), 10, labels=lb)
    # 5. the villagers walking, every season: one column per agent, one row per season, rows named
    LEFT, TOP, SCALE = 30, 1, 5
    fr = []
    for i in range(8):
        sheet = C(LEFT + 4 * 20 + 4, TOP + 4 * 34 + 2)
        for col, who in enumerate(('farmer', 'tinker', 'gardener', 'elder')):
            for row, season in enumerate(ex.SEASONS):
                blit(sheet, villager_frames[(who, season)][0][i % 4], LEFT + 4 + col * 20, TOP + 1 + row * 34)
        fr.append(sheet)
    tmp = tempfile.mkdtemp(); names = []
    for i, f in enumerate(fr):
        nm = os.path.join(tmp, f'{i}.png'); ex.save(f, nm, SCALE)
        cmd = ['magick', nm, '-background', '#f4f5ef', '-alpha', 'remove', '-font', UI_FONT, '-pointsize', '28', '-fill', '#66726b', '-gravity', 'NorthEast']
        for row, season in enumerate(ex.SEASONS):
            cmd += ['-annotate', f'+{(4 * 20 + 4 + 4) * SCALE}+{(TOP + 1 + row * 34 + 16) * SCALE - 18}', season.capitalize()]
        subprocess.run(cmd + [nm], check=True); names.append(nm)
    out = os.path.join(DOCS, 'villagers.gif')
    subprocess.run(['magick', '-delay', '24', '-loop', '0', *names, '-layers', 'Optimize', out], check=True)
    print(out)
