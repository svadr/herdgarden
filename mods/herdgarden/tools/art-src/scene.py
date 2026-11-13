"""Quiet valley scene for the bottom-right of the work area. Flat tints of one ink colour on the paper colour.
Three times of day: dawn (sun rising between the peaks, dithered sky glow, valley mist), day, night."""
import os, sys, math, random
sys.path.insert(0, os.path.dirname(__file__))
from px import C, hexc, mix

W, H = 340, 170
BAYER = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]


def bayer(x, y):
    return (BAYER[y % 4][x % 4] + 0.5) / 16.0


def sm(x, x0, x1):
    t = min(1.0, max(0.0, (x - x0) / (x1 - x0)))
    return t * t * (3 - 2 * t)


AUTUMN = ('#d9822b', '#c4532a', '#e0aa3a')                    # amber, rust, gold
PETAL, PUMPKIN, WHEAT = '#e58aa6', '#e08a2e', '#d9a83c'


def scene(paper, ink, roof, leaf, glow, mode, blossom=None, sky=None, season='summer'):
    """season: summer is the original picture. Spring, autumn and winter change only the trees, the field,
    small things on the hills and what is in the sky; the hills, the house and the layout never move."""
    night, dawn = mode == 'night', mode == 'dawn'
    spring, autumn, winter = season == 'spring', season == 'autumn', season == 'winter'
    paper, ink, roof, leaf, glow = map(hexc, (paper, ink, roof, leaf, glow))
    dark = sum(paper) < 384
    snow = mix(paper, (214, 226, 244), 0.58) if dark else (255, 255, 255)
    c = C(W, H)
    T = lambda t: mix(paper, ink, t)
    count = [0]

    def far(x):
        peak1 = 96 - abs(x - 262) * 0.95
        peak2 = 74 - abs(x - 205) * 0.80
        roll = 52 + 9 * math.sin(x / 31 + 1.1)
        return H - sm(x, 70, 250) * max(roll, peak1, peak2)

    def mid(x):
        return H - sm(x, 96, 300) * (50 + 9 * math.sin(x / 34 + 0.2) + 4 * math.sin(x / 13 + 2))

    def near(x):
        return H - sm(x, 128, 320) * (33 + 6 * math.sin(x / 47 + 2.4) + 2 * math.sin(x / 15))

    def front(x):
        return H - sm(x, 150, 330) * (15 + 2 * math.sin(x / 23 + 1))

    layers = [(far, 0.055), (mid, 0.10), (near, 0.155), (front, 0.215)]
    tops = [[int(round(fn(x))) for x in range(W)] for fn, _ in layers]
    FAR, MID, NEAR, FRONT = tops

    # ---- sky, behind the hills ----
    rnd = random.Random(7)
    if dawn:
        skyc = hexc(sky)
        for x in range(W):
            fade = sm(x, 90, 250)
            for y in range(34, FAR[x]):
                s = min(1.0, (y - 34) / 84.0) ** 1.7 * 0.55 * fade
                steps = s / 0.07
                lvl = int(steps) + (1 if bayer(x, y) < steps - int(steps) else 0)
                if lvl > 0:
                    c.set(x, y, mix(paper, skyc, min(0.62, lvl * 0.07)))
        sx, sy = 228, 106                                   # sun rising between the two peaks
        c.disc(sx, sy, 21, mix(paper, glow, 0.42))
        c.disc(sx, sy, 16, mix(paper, glow, 0.72))
        c.disc(sx, sy, 12, mix(paper, glow, 0.96))
        for (bx, by) in ((176, 58), (190, 50), (150, 70)):
            col = T(0.40)
            for dx, dy in ((0, 0), (1, 1), (2, 0), (-1, -1), (3, -1)):
                c.set(bx + dx, by + dy, col)
    elif night:
        for _ in range(46):
            x = rnd.randrange(120, W - 4)
            y = rnd.randrange(4, 96)
            if y < FAR[x] - 3:
                c.set(x, y, mix(paper, glow, rnd.choice((0.35, 0.5, 0.7, 0.9))))
        for (x, y) in ((182, 22), (236, 12), (300, 40), (150, 52)):
            col = mix(paper, glow, 0.95)
            for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)):
                if y + dy < FAR[x] - 3:
                    c.set(x + dx, y + dy, col)
        mx, my = 296, 26                                    # crescent moon; a full harvest moon in autumn
        c.disc(mx, my, 9, mix(paper, glow, 0.92))
        if autumn:
            for (dx, dy) in ((-3, -2), (-2, -2), (2, 3), (3, 1), (-1, 4)):
                c.set(mx + dx, my + dy, mix(paper, glow, 0.74))
        else:
            for y in range(my - 11, my + 11):
                for x in range(mx - 11, mx + 11):
                    if (x - (mx - 4)) ** 2 + (y - (my - 3)) ** 2 <= 8.2 * 8.2:
                        c.p[y][x] = None
    else:
        for (cx, cy, cw) in ((150, 44, 30), (232, 62, 22), (196, 22, 18)):   # flat clouds
            col = T(0.05)
            c.rect(cx + 2, cy, cx + cw - 3, cy, col)
            c.rect(cx, cy + 1, cx + cw - 1, cy + 3, col)
            c.rect(cx + 3, cy - 2, cx + cw // 2, cy - 1, col)
            c.rect(cx + 1, cy + 4, cx + cw - 4, cy + 4, col)
        sx, sy = 292, 30
        c.disc(sx, sy, 10, mix(paper, glow, 0.24 if winter else 0.38))
        c.disc(sx, sy, 7, mix(paper, glow, 0.42 if winter else 0.62))
        birds = ((214, 34), (228, 26), (176, 48))
        if autumn:                                          # flying south in a V
            birds = ((236, 32), (228, 28), (220, 24), (229, 37), (222, 42))
        elif winter:
            birds = ()
        for (bx, by) in birds:
            col = T(0.34)
            for dx, dy in ((0, 0), (1, 1), (2, 0), (-1, -1), (3, -1)):
                c.set(bx + dx, by + dy, col)

    # ---- hills ----
    def hill(i):
        t = layers[i][1]
        if winter and dark:                                 # snow under the moon: a little lighter and bluer
            return mix(paper, (176, 194, 224), t * 1.25)
        if winter:
            return mix(paper, mix(ink, (104, 132, 176), 0.35), t)
        return T(t)

    def fill(i):
        col = hill(i)
        for x in range(W):
            for y in range(tops[i][x], H):
                c.set(x, y, col)

    def crest(i, thick):
        col = mix(hill(i), snow, 0.55 if dark else 1.0)
        for x in range(W):
            if tops[i][x] < H - 1:
                c.set(x, tops[i][x], col)

    fill(0)
    fill(1)

    def bare(x, base, r, t):
        tr = T(t + 0.16)
        top = base - 3 - int(r * 1.9)
        fork = base - 3 - int(r * 0.7)
        c.rect(x, fork, x + 1, base, tr)
        for y in range(top, fork):
            c.set(x + (1 if (fork - y) > r * 0.6 else 0), y, tr)
        ends = [(x + 1, top)]
        for side, start, n in ((-1, fork, int(r * 0.95)), (1, fork - max(1, r // 4), int(r * 0.8))):
            px, py = (x if side < 0 else x + 1), start
            for i in range(1, n + 1):
                px += side; py -= 1 if (i % 3) else 0
                c.set(px, py, tr)
                if i == n // 2 and r >= 5:                  # a twig going straight up from the middle of the limb
                    for k in range(1, max(2, r // 2) + 1):
                        c.set(px, py - k, tr)
                    ends.append((px, py - max(2, r // 2)))
            ends.append((px, py))
        if r >= 6:
            for side in (-1, 1):
                for i in range(1, r // 2 + 1):
                    c.set(x + 1 + side * i, top + r // 2 - i + 1, tr)
                ends.append((x + 1 + side * (r // 2), top + 1))
        for (ex, ey) in ends:
            c.set(ex, ey - 1, snow)

    def tree(x, base, r, t=0.30):
        k = count[0]; count[0] += 1
        if winter:
            return bare(x, base, r, t)
        col, hi, tr = T(t), T(t - 0.07), T(t + 0.14)
        lo = T(t + 0.06)
        if blossom:
            col, hi = mix(paper, hexc(blossom), 0.62), mix(paper, hexc(blossom), 0.40)
            lo = mix(paper, hexc(blossom), 0.80)
        if spring and not blossom and k in (1, 4, 5, 6):
            s = 0.56 if t >= 0.3 else 0.40
            col, hi, lo = (mix(paper, hexc(PETAL), v) for v in (s, s - 0.22, s + 0.16))
        if autumn:
            a, s = hexc(AUTUMN[k % 3]), (0.60 if t >= 0.3 else 0.40)
            col, hi, lo = mix(paper, a, s), mix(paper, a, s - 0.20), mix(paper, a, s + 0.18)
        c.rect(x, base - 3, x + 1, base, tr)
        c.disc(x + 0.5, base - 3 - r, r, col)
        c.disc(x - r * 0.55, base - 3 - r * 0.55, r * 0.62, col)
        c.disc(x + 1 + r * 0.55, base - 3 - r * 0.6, r * 0.62, col)
        if r >= 5:
            c.disc(x + 1 + r * 0.50, base - 3 - r * 0.45, r * 0.50, lo)
        c.disc(x - 1, base - 4 - r * 1.15, r * 0.5, hi)

    def pine(x, base, h, t=0.32):
        col, tr = T(t), T(t + 0.12)
        c.rect(x, base - 2, x, base, tr)
        prev = -1
        for i in range(h):
            half = (i * 0.42) % 3 + i * 0.22
            for dx in range(-int(half), int(half) + 1):
                c.set(x + dx, base - 2 - h + i, snow if winter and (dx < -prev or i == 0 or (dx == -int(half) and i % 2)) else col)
            prev = int(half)

    for x, r in ((150, 4), (166, 5), (178, 3), (226, 5), (322, 5)):
        tree(x, MID[x] + 1, r, 0.20)
    for x, h in ((196, 11), (203, 14), (210, 10), (300, 12), (307, 15)):
        pine(x, MID[x] + 1, h, 0.22)

    if dawn:                                                # mist lying in the valley
        for y in range(H - 50, H - 34):
            dens = max(0.0, 1 - abs(y - (H - 41)) / 8.0) * 0.85
            for x in range(110, W):
                if y >= FAR[x] and bayer(x, y) < dens * sm(x, 130, 200):
                    c.set(x, y, T(0.02))

    fill(2)
    if winter:
        crest(2, 2)
    fill(3)
    if winter:
        crest(3, 2)
    if spring:                                              # small flowers in the grass
        r2 = random.Random(21)
        tints = (mix(paper, hexc(blossom or PETAL), 0.78), mix(paper, glow, 0.85), mix(paper, hexc(blossom or PETAL), 0.45))
        n = 0
        while n < 30:
            x = r2.randrange(146, W - 3)
            y = r2.randrange(NEAR[x] + 4, H - 2) if NEAR[x] + 4 < H - 2 else 0
            if y and not (x > 196 and y > H - 22):
                c.set(x, y, r2.choice(tints)); n += 1
    if autumn:                                              # leaves on the ground under the trees
        r2 = random.Random(5)
        for (tx, tr_) in ((246 - 16, 7), (246 + 38, 6), (246 + 52, 8)):
            for _ in range(7):
                x = tx + r2.randrange(-tr_ - 4, tr_ + 6)
                y = NEAR[tx] + r2.randrange(3, 9)
                c.set(x, y, mix(paper, hexc(r2.choice(AUTUMN)), 0.62))

    # farmhouse on the near hill
    hx = 246
    by = NEAR[hx + 10] + 1
    wall, wall_sh, line = mix(paper, ink, 0.03), T(0.12), T(0.46)
    rf, rf_d = mix(paper, roof, 0.78), mix(paper, roof, 0.95)
    c.rect(hx, by - 12, hx + 21, by, wall)
    c.rect(hx, by - 12, hx + 21, by - 11, wall_sh)
    for x in (hx, hx + 21):
        c.rect(x, by - 12, x, by, line)
    for i in range(9):
        c.rect(hx - 3 + i, by - 13 - i, hx + 24 - i, by - 13 - i, rf)
    c.rect(hx - 3, by - 13, hx + 24, by - 13, rf_d)
    for i in range(1, 9):                                   # light catches the left roof edge
        c.set(hx - 3 + i, by - 13 - i, mix(paper, roof, 0.50))
        c.set(hx - 2 + i, by - 13 - i, mix(paper, roof, 0.62))
    c.rect(hx + 16, by - 25, hx + 18, by - 19, T(0.40))
    c.rect(hx + 9, by - 7, hx + 12, by, T(0.50))
    win = mix(paper, glow, 0.95) if (night or dawn) else T(0.26)
    c.rect(hx + 3, by - 8, hx + 6, by - 5, win)
    c.rect(hx + 15, by - 8, hx + 18, by - 5, win)
    if winter:
        edge = T(0.20)
        for i in range(5, 9):
            for x in range(hx - 3 + i, hx + 25 - i):
                if i > 5 or (x + i) % 3:
                    c.set(x, by - 13 - i, snow)
            if i > 5:
                c.set(hx - 4 + i, by - 13 - i, edge); c.set(hx + 25 - i, by - 13 - i, edge)
        c.rect(hx + 6, by - 22, hx + 15, by - 22, edge)
        c.rect(hx + 16, by - 26, hx + 18, by - 26, snow)
        c.rect(hx + 16, by - 25, hx + 18, by - 22, T(0.40))
    if not night:
        puffs = ((17, -28), (18, -31), (20, -34), (21, -38)) + (((23, -42), (24, -46)) if winter else ())
        for (dx, dy) in puffs:
            c.set(hx + dx, by + dy, T(0.16)); c.set(hx + dx + 1, by + dy, T(0.16))
    tree(hx - 16, NEAR[hx - 16] + 1, 7, 0.31)
    tree(hx + 38, NEAR[hx + 38] + 1, 6, 0.31)
    tree(hx + 52, NEAR[hx + 52] + 1, 8, 0.33)
    pine(hx - 30, NEAR[hx - 30] + 1, 15, 0.30)

    # fence along the near hill
    for x in range(176, 226):
        y = NEAR[x] - 2
        c.set(x, y, T(0.40))
        if x % 6 == 0:
            c.rect(x, y - 2, x, y + 2, T(0.46))
            if winter:
                c.set(x, y - 3, snow)
    if dawn:                                                # a rooster on a fence post greets the sun
        rx, ry = 198, NEAR[198] - 5
        body, comb = T(0.55), mix(paper, roof, 0.95)
        for dx, dy in ((0, 0), (1, 0), (2, 0), (0, -1), (1, -1), (-1, -1), (-2, -2), (-1, -2), (2, -1), (2, -2), (2, -3)):
            c.set(rx + dx, ry + dy, body)
        c.set(rx + 2, ry - 4, comb); c.set(rx + 3, ry - 2, mix(paper, glow, 0.9))

    # crop rows in the foreground
    for row in range(4):
        y = H - 4 - row * 4
        for x in range(214 - row * 3, W - 8, 5):
            if y > FRONT[x] + 2:
                j = (x - (214 - row * 3)) // 5
                if winter:                                  # stubble under the snow
                    c.set(x, y, T(0.34)); c.set(x, y - 1, snow)
                elif spring:                                # seedlings
                    c.set(x, y, T(0.50)); c.set(x, y - 1, mix(paper, leaf, 0.85))
                    if (j + row) % 2:
                        c.set(x + 1, y - 2, mix(paper, leaf, 0.60))
                elif autumn and (j + row * 2) % 3 == 0:     # pumpkins between the ripe rows
                    pk = hexc(PUMPKIN)
                    c.rect(x - 1, y - 1, x + 1, y, mix(paper, pk, 0.92)); c.set(x - 1, y - 1, mix(paper, pk, 0.60))
                    c.set(x, y - 2, mix(paper, leaf, 0.85))
                else:
                    top = hexc(WHEAT) if autumn else leaf
                    c.set(x, y, T(0.50))
                    c.set(x, y - 1, mix(paper, top, 0.85))
                    c.set(x + 1, y - 2, mix(paper, top, 0.85))
                    c.set(x - 1, y - 2, mix(paper, top, 0.60))
    # scarecrow
    sx = 318
    sy = FRONT[sx] + 1
    c.rect(sx, sy - 12, sx, sy, T(0.50))
    c.rect(sx - 4, sy - 9, sx + 4, sy - 9, T(0.50))
    c.rect(sx - 1, sy - 15, sx + 1, sy - 13, mix(paper, glow, 0.75))
    c.rect(sx - 3, sy - 16, sx + 3, sy - 16, T(0.50))
    if winter:                                              # snow on the hat, and a scarf
        c.rect(sx - 2, sy - 17, sx + 2, sy - 17, snow)
        c.rect(sx - 1, sy - 12, sx + 1, sy - 12, mix(paper, roof, 0.90)); c.set(sx + 2, sy - 11, mix(paper, roof, 0.90))
    if autumn:                                              # a crow on the scarecrow's arm
        for (dx, dy) in ((-4, -10), (-3, -10), (-3, -11), (-2, -10)):
            c.set(sx + dx, sy + dy, T(0.74))
        c.set(sx - 5, sy - 10, mix(paper, glow, 0.9))

    if night and not (autumn or winter):  # fireflies
        flies = ((228, 104), (236, 118), (289, 112), (268, 92), (205, 128), (310, 126), (186, 138))
        for (x, y) in (flies[:4] if spring else flies):
            c.set(x, y, mix(paper, glow, 1.0))
            c.set(x + 1, y, mix(paper, glow, 0.45)); c.set(x - 1, y, mix(paper, glow, 0.45))
            c.set(x, y + 1, mix(paper, glow, 0.45)); c.set(x, y - 1, mix(paper, glow, 0.45))
    return c


VARIANTS = {
    # name: paper, ink, roof, leaf, glow, blossom, sky
    'paper-dawn': ('#fbf8f4', '#5a5a66', '#bc4e34', '#467552', '#f4b06a', None, '#f2b3a0'),
    'paper-day': ('#fbfbf7', '#3d4f47', '#bc4e34', '#467552', '#e8b64a', None, None),
    'paper-night': ('#121816', '#a9c2b6', '#e8866a', '#8cc29a', '#f4d98a', None, None),
    'sand-dawn': ('#fcf2e8', '#7a5a55', '#b34a30', '#4f7538', '#f2a65a', None, '#f5a88e'),
    'sand-day': ('#fbf6ee', '#6b5540', '#ad5028', '#4f7538', '#e3a63a', None, None),
    'sand-night': ('#1a1612', '#c9b49a', '#ea9a6e', '#a9c785', '#f6d58a', None, None),
    'blossom-dawn': ('#fef3f1', '#86586a', '#b8445d', '#3f775a', '#f6b36e', '#d9788f', '#f7a3b0'),
    'blossom-day': ('#fdf7f4', '#7a5560', '#b8445d', '#3f775a', '#e9a94e', '#d9788f', None),
    'blossom-night': ('#18131a', '#c7aebd', '#f08fa4', '#9fd3b0', '#f6d590', '#e58aa3', None),
}

if __name__ == '__main__':
    here = os.path.dirname(__file__)
    os.makedirs(os.path.join(here, 'art'), exist_ok=True)
    for name, (paper, ink, roof, leaf, glow, blossom, sky) in VARIANTS.items():
        for season in ('spring', 'summer', 'autumn', 'winter'):
            s = scene(paper, ink, roof, leaf, glow, name.split('-')[1], blossom, sky, season)
            s.png(os.path.join(here, 'art', f'scene-{name}-{season}.png'))
            s.png(os.path.join(here, 'seasons', f'view-{name}-{season}.png'), scale=3, bg=hexc(paper))
    print('ok')
