"""The homestead yard in four seasons. Summer is the original yard, drawn by garden2 and garden_empty unchanged.
Spring: fresh grass with wildflowers, a cherry tree in blossom, tulips in the flower bed.
Autumn: golden grass, orange and gold trees, fallen leaves, pumpkins in the flower bed.
Winter: snow on the ground, the roof, the fences and the lamps, bare trees, a frozen pond and a snowman.
The layout never changes, so the villager's route, the crops and the lit layers are the same in every season."""
import os, sys, math, random
sys.path.insert(0, os.path.dirname(__file__))
from px import C, hexc, mix
import garden as g1
import garden2 as g2
import garden_empty as ge
from garden2 import W, H, K, LAMPS

SEASONS = ('spring', 'summer', 'autumn', 'winter')
#          grass,     light,     dark,      shadow under things
GROUND = {'spring': ('#93cd62', '#b9e482', '#6fb04c', '#62a046'),
          'autumn': ('#c9b257', '#dfca73', '#aa933f', '#94802f'),
          'winter': ('#e3ecf5', '#f9fcff', '#cbd8e7', '#b3c3d7')}
CHERRY = ('#f4a6c0', '#fcd3df', '#dc7d9e', '#8a3b58')
FRESH = ('#57b356', '#8ad672', '#35874a', '#1c4630')
GOLD = ('#e3a92f', '#f7d264', '#b57d1c', '#5e3e10')
WHITE, SHADE, SLATE = K('#ffffff'), K('#cfdbea'), K('#4a5a70')


def ground(c, rnd, pal, specks=820, tufts=60):
    g, gl, gd = pal
    c.rect(0, 0, W - 1, H - 1, g)
    for _ in range(specks):
        c.set(rnd.randrange(W), rnd.randrange(H), gl if rnd.random() < 0.55 else gd)
    for _ in range(tufts):
        x, y = rnd.randrange(2, W - 2), rnd.randrange(2, H - 2)
        c.set(x, y, gd); c.set(x - 1, y - 1, gd); c.set(x + 1, y - 1, gd)


def wildflowers(c, rnd, grass, n=46):
    cols = [K(v) for v in ('#ffffff', '#f7a8c4', '#ffe26a', '#c9a2f0')]
    done = 0
    while done < n:
        x, y = rnd.randrange(3, W - 3), rnd.randrange(3, H - 3)
        if all(c.get(x + dx, y + dy) in grass for dx in (-1, 0, 1) for dy in (-1, 0, 1)):
            col = rnd.choice(cols)
            if done % 3 == 0:                                                        # four petals round a centre
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    c.set(x + dx, y + dy, col)
                c.set(x, y, K('#f6c832') if col != cols[2] else K('#f08a3a'))
            else:
                c.set(x, y, col); c.set(x, y + 1, K('#3f8a3a'))
            done += 1


def leaves(c, rnd, n, box, keep=None):
    cols = [K(v) for v in ('#d9632c', '#f29a44', '#e8b23a', '#a8431c')]
    x0, y0, x1, y1 = box
    for _ in range(n):
        x, y = rnd.randrange(x0, x1), rnd.randrange(y0, y1)
        if keep is not None and c.get(x, y) not in keep:
            continue
        col = rnd.choice(cols)
        c.set(x, y, col); c.set(x + 1, y + rnd.choice((0, 0, 1)), col)


def tulips(c, x0, y0, n, rows):
    cols = (('#f27fa5', '#fbb6cd'), ('#fdf3f5', '#ffffff'), ('#b98ae0', '#d9bdf2'), ('#f6c832', '#fde48a'))
    for i in range(n):
        for j, dy in enumerate(rows):
            x, yy = x0 + i * 13 + j * 4, y0 + dy
            c.rect(x, yy, x + 1, yy + 6, K('#3f8a3a')); c.set(x - 1, yy + 4, K('#5fae4a')); c.set(x + 2, yy + 3, K('#5fae4a'))
            c.set(x - 1, yy + 5, K('#5fae4a')); c.set(x + 2, yy + 4, K('#5fae4a'))
            base, light = (K(v) for v in cols[(i + j * 2) % 4])
            c.rect(x - 1, yy - 3, x + 2, yy - 1, base); c.rect(x, yy, x + 1, yy, base)
            c.set(x - 1, yy - 4, base); c.set(x + 2, yy - 4, base); c.set(x, yy - 4, light)
            c.rect(x - 1, yy - 3, x - 1, yy - 2, light)


def pumpkins(c, x0, y0, n, rows):
    O, OD, OL, GR = K('#e8862e'), K('#bd5f1c'), K('#f7b25c'), K('#3f8a3a')
    for i in range(n):
        for j, dy in enumerate(rows):
            x, yy = x0 + i * 13 + j * 4, y0 + dy + 1
            big = (i + j) % 2 == 0
            w = 3 if big else 2
            c.rect(x - w + 1, yy, x + w, yy + (4 if big else 3), O)
            c.rect(x - w, yy + 1, x + w + 1, yy + (3 if big else 2), O)
            for xx in (x - 1, x + 2):
                c.rect(xx, yy, xx, yy + (4 if big else 3), OD)
            c.rect(x - w + 1, yy + 1, x - w + 1, yy + 2, OL)
            c.rect(x - w + 1, yy + (5 if big else 4), x + w, yy + (5 if big else 4), K('#5a341d'))
            c.rect(x, yy - 2, x + 1, yy - 1, GR); c.set(x + 2, yy - 2, K('#5fae4a'))
            c.set(x + w + 2, yy + 3, GR); c.set(x + w + 3, yy + 2, K('#5fae4a')); c.set(x + w + 3, yy + 3, GR)   # a bit of vine


def snow_rows(c, rnd, x0, y0, x1, y1):
    """Snow lying on the ridges between the furrows, with soil showing through."""
    for y in range(y0 + 4, y1 - 1, 5):
        for yy in (y, y + 1):
            x = x0 + 2 + rnd.randrange(3)
            while x < x1 - 2:
                run = rnd.randrange(3, 9)
                for xx in range(x, min(x + run, x1 - 1)):
                    if yy == y or xx % 3:
                        c.set(xx, yy, WHITE if yy == y else SHADE)
                x += run + rnd.randrange(3, 9)


def sprigs(c, x0, y0, n, rows):
    """Winter greens with red berries, where the flowers were."""
    for i in range(n):
        for j, dy in enumerate(rows):
            if (i + j) % 2:
                continue
            x, yy = x0 + i * 13 + j * 4, y0 + dy
            c.rect(x, yy + 1, x + 1, yy + 6, K('#2f6e4a'))
            for dx, ddy in ((-1, 3), (2, 2), (-2, 2), (3, 1), (-1, 0), (2, -1)):
                c.set(x + dx, yy + ddy, K('#3f8a5a'))
            c.rect(x, yy - 1, x + 1, yy, K('#3f8a5a'))
            for dx, ddy in ((-1, 1), (2, 0), (0, -2)):
                c.set(x + dx, yy + ddy, K('#d8352f'))
            c.set(x, yy - 3, WHITE); c.set(x + 1, yy - 2, WHITE)


def wraps(c, x0, y0, n, rows):
    """Shrubs wrapped in burlap for the winter, tied at the top, with snow on them."""
    T, TD, TL, ST = K('#c9a56a'), K('#9c7a42'), K('#e0c48e'), K('#6e4c22')
    for i in range(n):
        for j, dy in enumerate(rows):
            x, yy = x0 + i * 13 + j * 4, y0 + dy - 3
            c.rect(x - 1, yy + 3, x + 3, yy + 8, T); c.rect(x - 2, yy + 5, x + 4, yy + 8, T)
            c.rect(x + 3, yy + 3, x + 3, yy + 8, TD); c.rect(x + 4, yy + 5, x + 4, yy + 8, TD); c.rect(x - 2, yy + 5, x - 2, yy + 7, TL)
            for (dx, ddy) in ((0, 5), (2, 6), (0, 7), (-1, 6), (1, 4)):
                c.set(x + dx, yy + ddy, TD)
            c.rect(x - 1, yy + 2, x + 3, yy + 2, ST)                                    # the tie
            c.rect(x, yy, x + 2, yy + 1, T); c.set(x + 2, yy + 1, TD)
            c.rect(x, yy - 1, x + 2, yy - 1, WHITE); c.set(x - 1, yy + 3, WHITE); c.set(x - 2, yy + 5, WHITE); c.set(x + 3, yy + 3, SHADE)
            c.rect(x - 2, yy + 9, x + 4, yy + 9, K('#5a341d'))


def ice(c, cx, cy, rx, ry):
    g2.pond(c, cx, cy, rx, ry, lily=False)
    swap = {K('#55aecb'): K('#cfe7f3'), K('#3f8fb0'): K('#a8cfe4'), K('#a8dcea'): WHITE}
    for y in range(cy - ry - 4, cy + ry + 5):
        for x in range(cx - rx - 4, cx + rx + 5):
            p = c.get(x, y)
            if p in swap:
                c.set(x, y, swap[p])
            elif p in (K('#8a8076'), K('#6a6058')) and y < cy - ry + 1 and (x + y) % 3:
                c.set(x, y, WHITE if (x * 5 + y) % 4 else SHADE)                   # snow on the far stones
    for (dx, dy, n) in ((-12, 2, 6), (4, -3, 5)):                                    # skate marks
        for i in range(n):
            c.set(cx + dx + i, cy + dy - i // 3, WHITE)


def snowy_fence(c, x0, x1, y):
    g2.fence(c, x0, x1, y)
    for x in range(x0, x1, 2):
        if (x - x0) % 11 >= 4 and (x // 2) % 5 != 4:
            c.rect(x, y + 2, x + 1, y + 2, WHITE)
    for x in range(x0, x1 + 1, 11):
        c.rect(x, y - 1, x + 3, y - 1, WHITE); c.rect(x + 1, y - 2, x + 2, y - 2, WHITE); c.set(x + 3, y - 1, SHADE)


def bare_tree(rnd, r):
    o = C(r * 2 + 8, r * 2 + 18)
    cx, ty = o.w // 2, o.h - 2
    WD, WL, WK = K('#8a6a55'), K('#a98a72'), K('#5e4536')
    top = ty - 9 - r // 2
    o.rect(cx - 2, top, cx + 1, ty, WD); o.rect(cx + 1, top, cx + 1, ty, WK); o.rect(cx - 2, top, cx - 2, ty, WL)
    twigs = []

    def limb(x, y, ang, length, thick, depth):
        col = WD if thick > 1 else WK
        for i in range(int(length) + 1):
            px, py = x + math.sin(ang) * i, y - math.cos(ang) * i
            for t in range(thick):
                o.set(px + t, py, col)
            twigs.append((int(px), int(py), thick))
        ex, ey = x + math.sin(ang) * length, y - math.cos(ang) * length
        if depth:
            spread = 0.62 + rnd.random() * 0.2
            limb(ex, ey, ang - spread, length * 0.66, max(1, thick - 1), depth - 1)
            limb(ex, ey, ang + spread * 0.9, length * 0.66, max(1, thick - 1), depth - 1)
            if depth > 1:
                limb(ex, ey, ang + rnd.uniform(-0.15, 0.15), length * 0.55, 1, depth - 2)

    limb(cx - 1, top, -0.75, r * 0.62, 2, 2)
    limb(cx, top, 0.70, r * 0.62, 2, 2)
    limb(cx - 1, top, 0.02, r * 0.70, 2, 2)
    for (x, y, thick) in twigs:                                                      # snow on top of the branches
        if o.get(x, y - 1) is None and rnd.random() < 0.62:
            o.set(x, y - 1, WHITE)
            if thick > 1:
                o.set(x + 1, y - 1, WHITE)
    for x in range(cx - 4, cx + 4):                                                  # a little drift at the foot
        o.set(x, ty, WHITE if abs(x - cx) < 3 else SHADE)
    return o


def snowy_pine(rnd, r):
    o = C(r * 2 + 8, r * 2 + 18)
    cx, ty = o.w // 2, o.h - 2
    base, light, dark, line = (K(v) for v in g2.PINE)
    o.rect(cx - 2, ty - 9, cx + 1, ty, K('#7a4e2a')); o.rect(cx + 1, ty - 9, cx + 1, ty, K('#553318')); o.rect(cx - 2, ty - 9, cx - 2, ty, K('#9a6a3c'))
    for (w, y0, y1) in ((5, 2, 12), (9, 9, 21), (12, 17, 31)):
        for y in range(y0, y1 + 1):
            half = int(1 + (w - 1) * (y - y0) / (y1 - y0))
            for x in range(cx - half, cx + half):
                col = light if x < cx - half + 2 else (dark if x > cx + half - 4 or y > y1 - 2 else base)
                k = y - y0
                if k < 2 or x < cx - half + 3 + (k % 3 == 0) or (x < cx + 1 and (x + y * 2) % 7 == 0):
                    col = WHITE
                elif k < 3 or (x == cx - half + 4 and k % 2):
                    col = SHADE if x > cx else WHITE
                o.set(x, y, col)
    return g1.outline_obj(o, line)


def snowy_bush(rnd, r=6):
    o = g1.bush(rnd, None, r)
    line = K('#1c4630')
    for x in range(o.w):
        top = next((y for y in range(o.h) if o.p[y][x] is not None), None)
        if top is None:
            continue
        depth = max(1, int((r - abs(x - o.w / 2 + 0.5)) * 0.75) + (x % 2))
        for y in range(top + 1, min(o.h - 2, top + 1 + depth)):
            if o.p[y][x] is not None and o.p[y][x] != line:
                o.p[y][x] = WHITE if y < top + depth else SHADE
    return o


def snowy_roof(o):
    """Snow on whatever faces the sky: a band under the top outline of every column."""
    for x in range(o.w):
        top = next((y for y in range(o.h) if o.p[y][x] is not None), None)
        if top is None or top > 40:
            continue
        depth = 2 if top == 0 else 4 + (x % 3 == 0) + (x % 7 == 0)
        for y in range(top + 1, top + 1 + depth):
            if o.p[y][x] is not None:
                o.p[y][x] = WHITE if y < top + depth else SHADE
    return o


def snowman():
    o = C(18, 24)
    o.ellipse(8.5, 16.5, 6.4, 5.6, WHITE); o.ellipse(8.5, 8, 4.4, 4.2, WHITE)
    for y in range(o.h):                                                             # shade on the right and underneath
        xs = [x for x in range(o.w) if o.p[y][x] is not None]
        if xs:
            o.p[y][xs[-1]] = SHADE
            if len(xs) > 6:
                o.p[y][xs[-2]] = SHADE
    for x in range(4, 14):
        if o.p[21][x] is not None:
            o.p[21][x] = SHADE
    o.rect(5, 1, 11, 3, K('#4f6d94')); o.rect(5, 1, 6, 3, K('#6f8db4')); o.rect(4, 4, 12, 4, K('#3a5478'))      # hat
    o.set(7, 7, K('#2b2420')); o.set(10, 7, K('#2b2420'))
    o.rect(9, 9, 11, 9, K('#f08a3a')); o.set(12, 9, K('#c9661f'))                                               # carrot
    o.rect(4, 11, 12, 12, K('#d8352f')); o.rect(11, 13, 12, 15, K('#d8352f')); o.rect(4, 12, 12, 12, K('#a8241f'))  # scarf
    o.set(8, 15, K('#2b2420')); o.set(8, 18, K('#2b2420'))
    o = g1.outline_obj(o, SLATE)
    for (x, y) in ((1, 14), (0, 13), (0, 15), (16, 14), (17, 13), (17, 12)):                                     # twig arms
        o.set(x, y, K('#5e4536'))
    return o


def yard(kind, season, seed=11):
    """kind is a house ('farmhouse', 'cabin', 'barn', 'greenhouse') or None for the empty lot."""
    if season == 'summer':
        return g2.scene('homestead', kind) if kind else ge.scene()
    spring, autumn, winter = season == 'spring', season == 'autumn', season == 'winter'
    rnd = random.Random(seed + SEASONS.index(season) * 3)
    g, gl, gd, sh = (K(v) for v in GROUND[season])
    grass = (g, gl, gd)
    c = C(W, H)
    ground(c, rnd, grass, specks=420 if winter else 820, tufts=24 if winter else 60)
    if spring:
        wildflowers(c, rnd, grass)

    def place(o, x, y):
        inset = min(11, o.w // 2 - 3) if winter else 4                              # a small shadow on snow
        for yy in range(2 if winter else 3):
            for xx in range(inset, o.w - inset):
                if c.get(x + xx, y + o.h - 2 + yy) in grass:
                    c.set(x + xx, y + o.h - 2 + yy, sh)
        c.blit(o, x, y)

    if winter:                                                                       # trodden snow where the dirt was
        g2.dirt(c, rnd, 4, 70, 207, 130, base='#d2dce8', light='#e6edf5', dark='#bccadb')
    else:
        g2.dirt(c, rnd, 4, 70, 207, 130)
    if autumn:
        leaves(c, rnd, 70, (2, 2, W - 3, H - 3))
        leaves(c, rnd, 46, (2, 34, 60, 70)); leaves(c, rnd, 46, (150, 40, W - 3, 76))
    g2.bed(c, rnd, 12, 80, 92, 126)
    g2.bed(c, rnd, 118, 78, 200, 102)
    if winter:
        snow_rows(c, rnd, 12, 80, 92, 126); snow_rows(c, rnd, 118, 78, 200, 102)
    if kind:
        if spring:
            tulips(c, 124, 84, 6, rows=(0, 9))
        elif autumn:
            pumpkins(c, 124, 84, 6, rows=(0, 10))
        else:
            wraps(c, 124, 84, 6, rows=(0, 9))
    g2.stones(c, [(101 + (i % 2), 68 + i * 7) for i in range(10)])
    if winter:
        ice(c, 162, 117, 26, 8)
    else:
        g2.pond(c, 162, 117, 26, 8, lily=not autumn)
        if autumn:                                                                   # leaves on the water
            for (x, y, col) in ((150, 114, '#f29a44'), (171, 120, '#d9632c'), (176, 113, '#e8b23a')):
                c.rect(x, y, x + 1, y, K(col))
    if not kind:
        g2.dirt(c, rnd, *ge.LOT)
    fence = snowy_fence if winter else g2.fence
    if kind:
        fence(c, 6, 86, 57); fence(c, 122, 204, 57)
    else:
        fence(c, 6, 78, 57); fence(c, 134, 204, 57)

    if winter:
        place(bare_tree(rnd, 13), -6, 0); place(snowy_pine(rnd, 11), 24, -8); place(snowy_pine(rnd, 12), 150, -6); place(bare_tree(rnd, 14), 178, 0)
        place(snowy_bush(rnd), 140, 40)
        if kind:
            place(snowman(), 51, 33)
        else:
            place(snowy_bush(rnd), 50, 42)
    else:
        a, b = (CHERRY, FRESH) if spring else (GOLD, g2.MAPLE)
        place(g2.tree(rnd, 13, pal=a), -6, 0); place(g2.tree(rnd, 11, pine=True), 24, -8); place(g2.tree(rnd, 12, pine=True), 150, -6)
        place(g2.tree(rnd, 14, pal=b, fruit='#fff1f5' if spring else None), 178, 0)
        place(g1.bush(rnd, '#f28fb1' if spring else '#c2342f'), 140, 40); place(g1.bush(rnd, '#ffffff' if spring else None), 50, 42)

    if kind:
        h = g1.house(kind)
        place(snowy_roof(h) if winter else h, 71, -2)
    else:
        x0, y0, x1, y1 = ge.STAKES[0][0] + 2, ge.STAKES[0][1] + 3, ge.STAKES[3][0] + 1, ge.STAKES[3][1] + 3
        for x in range(x0, x1 + 1):
            if (x // 2) % 2 == 0:
                c.set(x, y0, K('#fbf3dc')); c.set(x, y1, K('#fbf3dc'))
        for y in range(y0, y1 + 1):
            if (y // 2) % 2 == 0:
                c.set(x0, y, K('#fbf3dc')); c.set(x1, y, K('#fbf3dc'))
        for (x, y) in ge.STAKES:
            c.blit(ge.obj(ge.STAKE), x, y)
        for rows, x, y in ((ge.LUMBER, 83, 37), (ge.SACK, 115, 35), (ge.SIGN, 98, 26)):
            o = ge.obj(rows)
            c.blit(o, x, y)
            if winter:
                for xx in range(1, o.w - 1):
                    top = next((yy for yy in range(o.h) if o.p[yy][xx] is not None), None)
                    if top is not None and (xx + x) % 6:
                        c.set(x + xx, y + top, WHITE)
    for (lx, ly) in LAMPS:
        c.blit(g1.outline_obj(g2.lamp(), K('#22222a')), lx, ly)
        if winter:
            c.rect(lx + 2, ly, lx + 6, ly, WHITE); c.rect(lx + 3, ly - 1, lx + 5, ly - 1, WHITE)
    return c


if __name__ == '__main__':
    here = os.path.dirname(__file__)
    os.makedirs(os.path.join(here, 'seasons'), exist_ok=True)
    sheet = C(W * 2 + 6, H * 2 + 6)
    sheet2 = C(W * 2 + 6, H * 2 + 6)
    for i, season in enumerate(SEASONS):
        for kind in ('farmhouse', 'cabin', 'barn', 'greenhouse', None):
            s = yard(kind, season)
            s.png(os.path.join(here, 'art', f'yard-homestead-{kind or "empty"}-{season}.png'))
            if kind == 'farmhouse':
                sheet.blit(s, 2 + (i % 2) * (W + 2), 2 + (i // 2) * (H + 2))
            if kind is None:
                sheet2.blit(s, 2 + (i % 2) * (W + 2), 2 + (i // 2) * (H + 2))
    sheet.png(os.path.join(here, 'seasons', 'yards.png'), scale=3, bg=hexc('#1a1612'))
    sheet2.png(os.path.join(here, 'seasons', 'yards-empty.png'), scale=3, bg=hexc('#1a1612'))
    w = C(W * 2 + 6, H * 2 + 6)
    for i, kind in enumerate(('farmhouse', 'cabin', 'barn', 'greenhouse')):
        w.blit(yard(kind, 'winter'), 2 + (i % 2) * (W + 2), 2 + (i // 2) * (H + 2))
    w.png(os.path.join(here, 'seasons', 'yards-winter.png'), scale=3, bg=hexc('#1a1612'))
    print('ok')
