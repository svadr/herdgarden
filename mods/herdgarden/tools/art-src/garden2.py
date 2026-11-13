"""Four yard layouts for the selected agent's plot, each 212 x 132 and each drawn once per kind of house.
homestead: house in the middle, crop bed and flower bed below, small pond.
orchard:   house on the left, a row of apple trees, crop bed on the right, a well and beehives.
pond:      house on the right, a large pond with a dock and ducks, crop bed beside the house.
zen:       house on the left, a raked-sand rock garden with a maple, crop bed and a koi pond below."""
import os, sys, math, random
sys.path.insert(0, os.path.dirname(__file__))
from px import C, hexc, mix
from garden import house, bush, barrel, outline_obj

W, H = 212, 132
K = hexc
G, GL, GD = K('#86c05a'), K('#a8d870'), K('#63a246')


def ground(c, rnd):
    c.rect(0, 0, W - 1, H - 1, G)
    for _ in range(820):
        c.set(rnd.randrange(W), rnd.randrange(H), GL if rnd.random() < 0.55 else GD)
    for _ in range(60):
        x, y = rnd.randrange(2, W - 2), rnd.randrange(2, H - 2)
        c.set(x, y, GD); c.set(x - 1, y - 1, GD); c.set(x + 1, y - 1, GD)


def dirt(c, rnd, x0, y0, x1, y1, base='#e4b474', light='#f1cd92', dark='#c9975c'):
    D, DL, DD = K(base), K(light), K(dark)
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            edge = min(x - x0, x1 - x, y - y0, y1 - y)
            if edge + rnd.choice((0, 0, 1, 1, 2, 3)) >= 3:
                c.set(x, y, D)
    for _ in range((x1 - x0) * (y1 - y0) // 40):
        x, y = rnd.randrange(x0 + 3, x1 - 2), rnd.randrange(y0 + 3, y1 - 2)
        if c.get(x, y) == D:
            c.set(x, y, DL if rnd.random() < 0.6 else DD)


def bed(c, rnd, x0, y0, x1, y1):
    S, SD, SL = K('#7b4b2b'), K('#5a341d'), K('#986540')
    c.rect(x0, y0, x1, y1, S)
    for y in range(y0 + 3, y1, 5):
        c.rect(x0 + 1, y, x1 - 1, y, SD)
    for _ in range((x1 - x0) * (y1 - y0) // 14):
        c.set(rnd.randrange(x0 + 1, x1), rnd.randrange(y0 + 1, y1), SL)
    for x in range(x0, x1 + 1):
        c.set(x, y0, SD); c.set(x, y1, SD)
    for y in range(y0, y1 + 1):
        c.set(x0, y, SD); c.set(x1, y, SD)


def flowers(c, x0, y0, n, rows=(0, 11)):
    for i in range(n):
        for j, dy in enumerate(rows):
            x, yy = x0 + i * 13 + j * 4, y0 + dy
            c.rect(x, yy, x + 1, yy + 6, K('#3f8a3a')); c.set(x - 1, yy + 4, K('#5fae4a')); c.set(x + 2, yy + 3, K('#5fae4a'))
            cc = K('#f6c832') if (i + j) % 2 == 0 else K('#f08a3a')
            c.rect(x - 1, yy - 3, x + 2, yy, cc); c.rect(x, yy - 4, x + 1, yy + 1, cc); c.rect(x, yy - 2, x + 1, yy - 1, K('#7a4a1c'))


def stones(c, pts):
    for (x, y) in pts:
        c.rect(x, y, x + 8, y + 3, K('#cfc5ad')); c.rect(x + 1, y - 1, x + 7, y + 4, K('#cfc5ad'))
        c.rect(x + 1, y - 1, x + 6, y, K('#e7dfca')); c.rect(x + 2, y + 4, x + 7, y + 4, K('#a59a82'))


def pond(c, cx, cy, rx, ry, lily=True, koi=False):
    for y in range(cy - ry - 3, cy + ry + 4):
        for x in range(cx - rx - 3, cx + rx + 4):
            d = ((x - cx) / (rx + 3)) ** 2 + ((y - cy) / (ry + 3)) ** 2 + math.sin(x * 0.7) * 0.03
            if d <= 1:
                c.set(x, y, K('#8a8076') if (x * 7 + y * 3) % 5 else K('#6a6058'))
    for y in range(cy - ry, cy + ry + 1):
        for x in range(cx - rx, cx + rx + 1):
            d = ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2
            if d <= 1:
                c.set(x, y, K('#3f8fb0') if d > 0.8 else K('#55aecb'))
    for i, (fx, fy, w) in enumerate(((-0.45, -0.35, 7), (0.1, 0.3, 9), (0.3, -0.45, 5), (-0.6, 0.35, 4))):
        x, y = int(cx + fx * rx), int(cy + fy * ry)
        c.rect(x, y, x + w, y, K('#a8dcea'))
    if lily:
        x, y = int(cx + rx * 0.5), int(cy + ry * 0.15)
        c.rect(x, y, x + 3, y + 1, K('#4f9a5a')); c.set(x + 2, y - 1, K('#f28fb1'))
    if koi:
        for (fx, fy, cc) in ((-0.2, 0.1, '#f08a3a'), (0.25, -0.2, '#fbf6ea')):
            x, y = int(cx + fx * rx), int(cy + fy * ry)
            c.rect(x, y, x + 3, y, K(cc)); c.set(x + 4, y - 1, K(cc)); c.set(x + 4, y + 1, K(cc))


def fence(c, x0, x1, y):
    for x in range(x0, x1, 2):
        c.rect(x, y + 3, x + 1, y + 4, K('#b98250')); c.rect(x, y + 7, x + 1, y + 8, K('#b98250'))
        c.set(x, y + 5, K('#6e4624')); c.set(x, y + 9, K('#6e4624'))
    for x in range(x0, x1 + 1, 11):
        c.rect(x, y, x + 3, y + 11, K('#a8703c')); c.rect(x, y, x, y + 11, K('#d09a62')); c.rect(x + 3, y, x + 3, y + 11, K('#6e4624'))
        c.rect(x, y, x + 3, y, K('#d09a62')); c.rect(x, y + 12, x + 3, y + 12, K('#4a3020'))


LEAFY = ('#3f9a4c', '#6cc060', '#2a6e3c', '#1c4630')
MAPLE = ('#d9632c', '#f29a44', '#a8431c', '#5e2410')
PINE = ('#2f7f5c', '#4fa477', '#1e5a44', '#143c30')


def tree(rnd, r=13, pal=LEAFY, pine=False, fruit=None):
    o = C(r * 2 + 8, r * 2 + 18)
    cx = o.w // 2
    base, light, dark, line = (K(v) for v in (PINE if pine else pal))
    ty = o.h - 2
    o.rect(cx - 2, ty - 9, cx + 1, ty, K('#7a4e2a')); o.rect(cx + 1, ty - 9, cx + 1, ty, K('#553318')); o.rect(cx - 2, ty - 9, cx - 2, ty, K('#9a6a3c'))
    if pine:
        for (w, y0, y1) in ((5, 2, 12), (9, 9, 21), (12, 17, 31)):
            for y in range(y0, y1 + 1):
                half = int(1 + (w - 1) * (y - y0) / (y1 - y0))
                for x in range(cx - half, cx + half):
                    o.set(x, y, light if x < cx - half + 2 else (dark if x > cx + half - 4 or y > y1 - 2 else base))
    else:
        cy = r + 3
        for (dx, dy, rr, cc) in ((0, 0, r, base), (-r * 0.5, r * 0.35, r * 0.7, base), (r * 0.5, r * 0.4, r * 0.7, dark), (r * 0.25, r * 0.55, r * 0.6, dark),
                                 (-r * 0.3, -r * 0.3, r * 0.55, light), (-r * 0.1, -r * 0.55, r * 0.35, light)):
            o.disc(cx + dx, cy + dy, rr, cc)
        for _ in range(r * 5):
            x, y = rnd.randrange(o.w), rnd.randrange(o.h - 10)
            if o.get(x, y) in (base, dark, light):
                o.set(x, y, rnd.choice((light, dark, base)))
        if fruit:
            n = 0
            while n < 7:
                x, y = rnd.randrange(2, o.w - 3), rnd.randrange(3, r * 2)
                if o.get(x, y) in (base, dark, light) and o.get(x + 1, y + 1) in (base, dark, light):
                    o.rect(x, y, x + 1, y + 1, K(fruit)); o.set(x, y, mix(K(fruit), (255, 255, 255), 0.45)); n += 1
    return outline_obj(o, line)


def well():
    o = C(18, 22)
    for y in range(2, 8):
        half = 2 + (y - 2)
        o.rect(9 - half, y, 8 + half, y, K('#a8553a') if y % 2 else K('#8a3f28'))
    o.rect(3, 8, 4, 15, K('#8a5a36')); o.rect(13, 8, 14, 15, K('#6e4624')); o.rect(5, 9, 12, 9, K('#6e4624')); o.rect(8, 10, 9, 12, K('#c9bfa8'))
    for y in range(14, 20):
        for x in range(2, 16):
            o.set(x, y, K('#a39a8e') if (x + (y % 2) * 3) % 5 else K('#6f675f'))
    o.rect(4, 14, 13, 15, K('#2f6f8c')); o.rect(5, 14, 7, 14, K('#7fc4dc')); o.rect(2, 14, 15, 14, K('#c2bab0')); o.rect(4, 14, 13, 14, K('#2f6f8c'))
    return outline_obj(o)


def hive():
    o = C(12, 15)
    o.rect(1, 2, 10, 3, K('#8a5a36')); o.rect(2, 4, 9, 12, K('#f6efdc')); o.rect(9, 4, 9, 12, K('#cfc4a8'))
    o.rect(2, 7, 9, 7, K('#cfc4a8')); o.rect(2, 10, 9, 10, K('#cfc4a8')); o.rect(4, 11, 7, 11, K('#3a2414')); o.rect(1, 13, 10, 13, K('#8a5a36'))
    return outline_obj(o)


def lantern():
    o = C(11, 18)
    o.rect(2, 2, 8, 3, K('#8a8580')); o.rect(1, 4, 9, 5, K('#a8a39c')); o.rect(3, 6, 7, 10, K('#b9b4ac')); o.rect(4, 7, 6, 9, K('#ffd978'))
    o.rect(2, 11, 8, 11, K('#8a8580')); o.rect(4, 12, 6, 14, K('#a8a39c')); o.rect(2, 15, 8, 16, K('#8a8580')); o.rect(3, 6, 3, 10, K('#d2cdc5'))
    return outline_obj(o, K('#4a4744'))


def rock(w, h):
    o = C(w + 2, h + 2)
    o.ellipse(w / 2 + 0.5, h / 2 + 0.5, w / 2, h / 2, K('#8f887e'))
    o.ellipse(w / 2 - 0.5, h / 2 - 0.5, w / 2 - 1.5, h / 2 - 1.5, K('#b3aca1'))
    o.ellipse(w / 2 + 1.5, h / 2 + 1.5, w / 2 - 2.5, max(1, h / 2 - 2.5), K('#8f887e'))
    return outline_obj(o, K('#4a4744'))


def sand_garden(c, x0, y0, x1, y1, rocks):
    S, SL = K('#eee2c6'), K('#d5c5a0')
    c.rect(x0, y0, x1, y1, S)
    for y in range(y0 + 2, y1, 3):
        c.rect(x0 + 2, y, x1 - 2, y, SL)
    for (rx0, ry0, w, h) in rocks:
        cx, cy = rx0 + w / 2 + 1, ry0 + h / 2 + 1
        for y in range(y0 + 1, y1):
            for x in range(x0 + 1, x1):
                d = math.hypot((x - cx) / (w / 2 + 1), (y - cy) / (h / 2 + 1))
                if d < 2.6:
                    c.set(x, y, SL if int(d * 2.4) % 2 == 0 else S)
    for x in range(x0, x1 + 1):
        for y in (y0, y1):
            c.set(x, y, K('#a8a096') if x % 5 else K('#7a736a'))
    for y in range(y0, y1 + 1):
        for x in (x0, x1):
            c.set(x, y, K('#a8a096') if y % 5 else K('#7a736a'))
    for (rx0, ry0, w, h) in rocks:
        c.blit(rock(w, h), rx0, ry0)


def dock(c, x0, y0, w=22, h=8):
    for y in range(y0, y0 + h):
        for x in range(x0, x0 + w):
            c.set(x, y, K('#b98250') if (x - x0) % 5 else K('#7e5230'))
    c.rect(x0, y0, x0 + w - 1, y0, K('#d6a26e')); c.rect(x0, y0 + h, x0 + w - 1, y0 + h, K('#4a3020'))
    for x in (x0 + 1, x0 + w - 3):
        c.rect(x, y0 + h, x + 1, y0 + h + 3, K('#6e4624'))


def duck(c, x, y):
    W_, O_ = K('#fbf8f0'), K('#f08a3a')
    c.rect(x + 1, y, x + 2, y, W_); c.rect(x, y + 1, x + 4, y + 2, W_); c.set(x + 3, y, W_); c.set(x + 4, y, O_); c.rect(x + 1, y + 3, x + 3, y + 3, K('#cfc8ba'))
    c.set(x + 3, y - 1, W_); c.set(x + 3, y, K('#2b1810'))


LAMPS = ((88, 48), (112, 48), (3, 66), (194, 92))          # top-left corner of each lamp post in the homestead yard
LAMP = [".........", "...ooo...", "..ooooo..", ".ogggggo.", ".ogGGGgo.", ".ogGGGgo.", ".ogggggo.", "..ooooo..",
        "....pP...", "....pP...", "....pP...", "....pP...", "....pP...", "....pP...", "....pP...", "....pP...",
        "....pP...", "....pP...", "...oooo..", "..oooooo."]


def lamp(lit=False):
    o = C(9, 20)
    pal = {'o': K('#34343e'), 'p': K('#5c5c6a'), 'P': K('#3e3e4a'),
           'g': K('#ffd978') if lit else K('#aebbc0'), 'G': K('#fff6c8') if lit else K('#d2dcdf')}
    o.stamp(0, 0, LAMP, pal)
    return o


def lit_layer(kind):
    """Only what glows: lamp glass and the house's windows. Shown over the darkened yard at dawn and night."""
    c = C(W, H)
    warm, hot, frame = K('#ffd978'), K('#fff3c0'), K('#fbf6ea')
    for (x, y) in LAMPS:
        l = lamp(True)
        for yy in range(3, 7):
            for xx in range(2, 7):
                c.set(x + xx, y + yy, l.p[yy][xx])
    hx, hy = 71 + 3, -2

    def pane(x, y, w=10, h=10):
        c.rect(hx + x + 1, hy + y + 1, hx + x + w - 2, hy + y + h - 2, warm)
        c.rect(hx + x + 1, hy + y + 1, hx + x + 2, hy + y + 2, hot)
        c.rect(hx + x + w // 2 - 1, hy + y + 1, hx + x + w // 2 - 1, hy + y + h - 2, frame)
        c.rect(hx + x + 1, hy + y + h // 2 - 1, hx + x + w - 2, hy + y + h // 2 - 1, frame)
    if kind == 'farmhouse':
        pane(11, 40); pane(44, 40)
    elif kind == 'cabin':
        pane(38, 40, w=12)
    elif kind == 'barn':
        c.rect(hx + 28, hy + 21, hx + 35, hy + 23, warm); c.rect(hx + 31, hy + 38, hx + 32, hy + 58, warm)
    else:
        for px0 in range(8, 56, 10):
            c.rect(hx + px0, hy + 34, hx + px0 + 7, hy + 45, (255, 226, 150, 150)); c.rect(hx + px0, hy + 47, hx + px0 + 7, hy + 50, (255, 226, 150, 110))
        c.rect(hx + 28, hy + 39, hx + 35, hy + 58, (255, 236, 180, 170))
    return c


def scene(variant, kind, seed=11):
    rnd = random.Random(seed + {'homestead': 0, 'orchard': 7, 'pond': 13, 'zen': 21}[variant])
    c = C(W, H)
    ground(c, rnd)

    def place(o, x, y):
        for yy in range(3):
            for xx in range(4, o.w - 4):
                if c.get(x + xx, y + o.h - 2 + yy) in (G, GL, GD):
                    c.set(x + xx, y + o.h - 2 + yy, K('#5a9440'))
        c.blit(o, x, y)

    h = house(kind)
    if variant == 'homestead':
        dirt(c, rnd, 4, 70, 207, 130)
        bed(c, rnd, 12, 80, 92, 126)
        bed(c, rnd, 118, 78, 200, 102); flowers(c, 124, 84, 6, rows=(0, 9))
        stones(c, [(101 + (i % 2), 68 + i * 7) for i in range(10)])
        pond(c, 162, 117, 26, 8)
        fence(c, 6, 86, 57); fence(c, 122, 204, 57)
        place(tree(rnd, 13), -6, 0); place(tree(rnd, 11, pine=True), 24, -8); place(tree(rnd, 12, pine=True), 150, -6); place(tree(rnd, 14), 178, 0)
        place(bush(rnd, '#f28fb1'), 140, 40); place(bush(rnd), 50, 42)
        place(h, 71, -2)
        for (lx, ly) in LAMPS:
            c.blit(outline_obj(lamp(), K('#22222a')), lx, ly)
    elif variant == 'orchard':
        dirt(c, rnd, 4, 72, 207, 130)
        fence(c, 80, 206, 57)
        for i, x in enumerate((76, 110, 144, 178)):
            place(tree(rnd, 11, fruit='#e2432f'), x, 2 + (i % 2) * 3)
        bed(c, rnd, 112, 80, 192, 126)
        stones(c, [(33 + (i % 2), 70 + i * 7) for i in range(9)])
        stones(c, [(46 + i * 11, 100 + (i % 2)) for i in range(5)])
        place(h, 2, 0)
        c.blit(well(), 62, 76); c.blit(hive(), 10, 84); c.blit(hive(), 10, 104); c.blit(outline_obj(barrel()), 196, 84)
        place(bush(rnd, '#f6c832'), 66, 108); place(bush(rnd, '#f28fb1', r=5), 196, 108)
    elif variant == 'pond':
        dirt(c, rnd, 4, 14, 134, 76)
        dirt(c, rnd, 150, 64, 207, 130)
        bed(c, rnd, 12, 22, 92, 68)
        pond(c, 62, 104, 46, 18)
        dock(c, 96, 98, w=26)
        duck(c, 40, 98); duck(c, 58, 108); c.rect(84, 112, 87, 113, K('#4f9a5a')); c.set(86, 111, K('#f28fb1'))
        for x in (14, 18, 22, 104, 108):
            c.rect(x, 84 if x < 50 else 112, x, 92 if x < 50 else 120, K('#3f8a3a')); c.rect(x, 82 if x < 50 else 110, x, 84 if x < 50 else 112, K('#8a5a36'))
        stones(c, [(170 + (i % 2), 68 + i * 7) for i in range(9)])
        stones(c, [(128 + i * 11, 100 + (i % 2)) for i in range(4)])
        place(tree(rnd, 12), 100, 2); place(tree(rnd, 11, pine=True), -4, -14)
        place(bush(rnd, '#c77adf'), 188, 100); place(bush(rnd), 154, 108)
        place(h, 140, -2)
    else:                                                                             # zen
        dirt(c, rnd, 4, 70, 207, 130, base='#e8d6ae', light='#f3e6c6', dark='#cdb98c')
        sand_garden(c, 104, 6, 204, 60, ((120, 24, 16, 9), (160, 36, 10, 6), (176, 14, 12, 8)))
        c.blit(lantern(), 190, 40)
        place(tree(rnd, 12, pal=MAPLE), 86, -8)
        bed(c, rnd, 112, 80, 192, 126)
        pond(c, 46, 108, 26, 11, koi=True)
        stones(c, [(50 + (i % 2), 68 + i * 7) for i in range(4)])
        stones(c, [(80 + i * 11, 98 + (i % 2)) for i in range(3)])
        place(tree(rnd, 10, pal=MAPLE), -6, 60); place(bush(rnd), 84, 112); place(bush(rnd, '#f28fb1', r=5), 196, 100)
        c.blit(rock(9, 6), 14, 112); c.blit(rock(6, 4), 76, 120)
        place(h, 20, -2)
    return c


if __name__ == '__main__':
    here = os.path.dirname(__file__)
    sheet = C(W * 2 + 6, H * 2 + 6)
    for i, variant in enumerate(('homestead', 'orchard', 'pond', 'zen')):
        for kind in ('farmhouse', 'cabin', 'barn', 'greenhouse'):
            s = scene(variant, kind)
            s.png(os.path.join(here, 'art', f'yard-{variant}-{kind}.png'))
            if variant == 'homestead':
                lit_layer(kind).png(os.path.join(here, 'art', f'yard-homestead-{kind}-lit.png'))
            if kind == 'farmhouse':
                sheet.blit(s, 2 + (i % 2) * (W + 2), 2 + (i // 2) * (H + 2))
    sheet.png(os.path.join(here, 'yards.png'), scale=3, bg=hexc('#1a1612'))
    print('ok')
