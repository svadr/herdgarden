"""Top-down yard for the selected agent's plot: the space's house at the top, a fence, a tilled bed for the agent's
crops, a flower bed, a stone path, trees and a pond. One picture per kind of house. 212 x 176, one art pixel per
CSS pixel, so it matches the 16 x 32 villagers that walk on it. Original art."""
import os, sys, math, random
sys.path.insert(0, os.path.dirname(__file__))
from px import C, hexc, mix

W, H = 212, 176
K = hexc
DARK = K('#3a2414')


def outline_obj(o, color=DARK):
    todo = []
    for y in range(o.h):
        for x in range(o.w):
            if o.p[y][x] is None:
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    xx, yy = x + dx, y + dy
                    if 0 <= xx < o.w and 0 <= yy < o.h and o.p[yy][xx] is not None:
                        todo.append((x, y)); break
    for x, y in todo:
        o.p[y][x] = color
    return o


def trap(o, y0, y1, xl0, xr0, xl1, xr1, fn):
    for y in range(y0, y1 + 1):
        t = (y - y0) / max(1, (y1 - y0))
        xl = int(round(xl0 + (xl1 - xl0) * t)); xr = int(round(xr0 + (xr1 - xr0) * t))
        for x in range(xl, xr + 1):
            o.set(x, y, fn(x, y, xl, xr))


def shingles(base, dark, light, y0, step=4, tick=7):
    base, dark, light = K(base), K(dark), K(light)

    def fn(x, y, xl, xr):
        band = (y - y0) // step
        if y - y0 < 2:
            return light
        if x - xl < 2:
            return light
        if xr - x < 2:
            return dark
        if (y - y0) % step == step - 1:
            return dark
        if (x + band * 3) % tick == 0:
            return dark
        return base
    return fn


def planks(o, x0, y0, x1, y1, base, dark, light, vertical=True, step=4):
    base, dark, light = K(base), K(dark), K(light)
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            k = (x - x0) if vertical else (y - y0)
            c = dark if k % step == step - 1 else (light if k % step == 0 else base)
            o.set(x, y, c)


def window(o, x, y, w=10, h=10, glass='#8fd0ea', shutters='#4f9a5a', lit=None):
    o.rect(x, y, x + w - 1, y + h - 1, K('#fbf6ea'))
    g = K(lit or glass)
    o.rect(x + 1, y + 1, x + w - 2, y + h - 2, g)
    o.rect(x + 1, y + 1, x + 2, y + 2, mix(g, (255, 255, 255), 0.6))
    o.rect(x + w // 2 - 1, y + 1, x + w // 2 - 1, y + h - 2, K('#fbf6ea'))
    o.rect(x + 1, y + h // 2 - 1, x + w - 2, y + h // 2 - 1, K('#fbf6ea'))
    if shutters:
        s, sd = K(shutters), mix(K(shutters), (0, 0, 0), 0.3)
        o.rect(x - 3, y, x - 1, y + h - 1, s); o.rect(x + w, y, x + w + 2, y + h - 1, s)
        for yy in range(y + 2, y + h - 1, 3):
            o.rect(x - 3, yy, x - 1, yy, sd); o.rect(x + w, yy, x + w + 2, yy, sd)


def door(o, x, y, w=10, h=18, wood='#b9773f', dark='#8a5328', frame='#f1d9a8'):
    o.rect(x - 1, y - 1, x + w, y + h - 1, K(frame))
    o.rect(x, y, x + w - 1, y + h - 1, K(wood))
    o.rect(x + 1, y + 1, x + w - 2, y + 7, K(dark)); o.rect(x + 2, y + 2, x + w - 3, y + 6, K(wood))
    o.rect(x + 1, y + 10, x + w - 2, y + h - 2, K(dark)); o.rect(x + 2, y + 11, x + w - 3, y + h - 3, K(wood))
    o.set(x + w - 3, y + 9, K('#f6d04a'))


def foundation(o, x0, x1, y):
    for x in range(x0, x1 + 1):
        for yy in (y, y + 1, y + 2):
            o.set(x, yy, K('#9a9288') if (x + yy * 3) % 6 else K('#6f675f'))
        o.set(x, y, K('#b9b1a6') if x % 6 else K('#6f675f'))


def house(kind):
    o = C(70, 66)
    ox = 3
    if kind == 'farmhouse':
        planks(o, ox + 6, 32, ox + 57, 58, '#e2b274', '#b98850', '#f0c98f')
        o.rect(ox + 6, 32, ox + 57, 33, K('#a97a46'))                               # eave shadow
        foundation(o, ox + 6, ox + 57, 59)
        # chimney
        for y in range(1, 16):
            for x in range(ox + 43, ox + 50):
                o.set(x, y, K('#b0705a') if (x + (y // 3) * 2) % 4 and y % 3 else K('#7d4a3a'))
        o.rect(ox + 42, 1, ox + 51, 2, K('#8a8078'))
        trap(o, 9, 31, ox + 13, ox + 50, ox + 1, ox + 62, shingles('#cf4a32', '#9a3020', '#e8755a', 9))
        door(o, ox + 27, 41)
        window(o, ox + 11, 40); window(o, ox + 44, 40)
        o.rect(ox + 8, 51, ox + 23, 52, K('#8a5a36'))                               # flower box
        for i, cc in enumerate(('#f28fb1', '#f6d04a', '#f28fb1', '#ffffff', '#f6d04a', '#f28fb1')):
            o.set(ox + 9 + i * 2 + (i % 2), 50, K(cc)); o.set(ox + 10 + i * 2, 49, K('#4f9a5a'))
        o.rect(ox + 25, 60, ox + 38, 62, K('#c9bfa8')); o.rect(ox + 25, 60, ox + 38, 60, K('#e6ddc8'))   # step
    elif kind == 'cabin':
        planks(o, ox + 8, 32, ox + 55, 58, '#b47a48', '#8a5730', '#cf9763', vertical=False, step=4)
        o.rect(ox + 8, 32, ox + 55, 33, K('#6e4324'))
        for y in range(34, 59, 4):                                                    # log ends
            for x in (ox + 6, ox + 56):
                o.rect(x, y, x + 1, y + 2, K('#d9b07a')); o.set(x + 1, y + 1, K('#8a5730'))
        foundation(o, ox + 8, ox + 55, 59)
        trap(o, 8, 31, ox + 16, ox + 47, ox + 2, ox + 61, shingles('#dba844', '#a87724', '#f3d37a', 8, step=3, tick=4))
        door(o, ox + 14, 41, wood='#7a4a26', dark='#553018', frame='#cf9763')
        window(o, ox + 38, 40, w=12, shutters=None, lit='#ffd978')
        o.rect(ox + 12, 60, ox + 25, 62, K('#c9bfa8')); o.rect(ox + 12, 60, ox + 25, 60, K('#e6ddc8'))
    elif kind == 'barn':
        planks(o, ox + 6, 30, ox + 57, 60, '#c4543e', '#96392a', '#dc7059')
        o.rect(ox + 6, 30, ox + 57, 31, K('#7e2c20'))
        for x in (ox + 6, ox + 57):
            o.rect(x, 30, x, 60, K('#fbf3e4'))
        trap(o, 4, 15, ox + 22, ox + 41, ox + 10, ox + 53, shingles('#8f7d70', '#6a5a4f', '#b0a294', 4))
        trap(o, 16, 29, ox + 9, ox + 54, ox + 2, ox + 61, shingles('#8f7d70', '#6a5a4f', '#a09285', 16))
        o.rect(ox + 27, 20, ox + 36, 27, K('#fbf3e4')); o.rect(ox + 28, 21, ox + 35, 26, K('#3d2a22'))
        o.rect(ox + 28, 24, ox + 35, 26, K('#e9c46a')); o.rect(ox + 30, 23, ox + 33, 23, K('#e9c46a'))   # hay loft
        dx0, dx1, dy0, dy1 = ox + 20, ox + 43, 36, 60
        o.rect(dx0, dy0, dx1, dy1, K('#fbf3e4')); o.rect(dx0 + 2, dy0 + 2, dx1 - 2, dy1, K('#b4483a'))
        o.rect(ox + 31, dy0 + 2, ox + 32, dy1, K('#3d2a22'))
        for i in range(0, 10):                                                        # X braces
            for (a, b) in ((dx0 + 2 + i, dy0 + 2 + i * 2), (dx0 + 11 - i, dy0 + 2 + i * 2), (ox + 33 + i, dy0 + 2 + i * 2), (dx1 - 2 - i, dy0 + 2 + i * 2)):
                o.set(a, b, K('#fbf3e4')); o.set(a, b + 1, K('#fbf3e4'))
        o.rect(dx0 + 2, dy0 + 12, dx1 - 2, dy0 + 13, K('#fbf3e4')); o.rect(ox + 31, dy0 + 2, ox + 32, dy1, K('#3d2a22'))
    else:                                                                             # greenhouse
        F, FD, G, GL, GD = K('#f7f2e8'), K('#cfc7b8'), K('#a9dcd3'), K('#dcf4ef'), K('#7fbfb5')

        def glass(x, y, xl, xr):
            if x - xl < 2 or xr - x < 2 or y < 10:
                return F
            if (x - (ox + 31)) % 10 in (0, 1) or (y - 9) % 9 == 0:
                return F
            return GL if (x + y) % 11 < 2 else G
        trap(o, 8, 30, ox + 22, ox + 41, ox + 3, ox + 60, glass)
        o.rect(ox + 5, 31, ox + 58, 60, F); o.rect(ox + 5, 31, ox + 58, 32, FD)
        for px0 in range(ox + 8, ox + 56, 10):
            o.rect(px0, 34, px0 + 7, 58, G)
            o.rect(px0, 34, px0 + 1, 40, GL); o.rect(px0, 46, px0 + 7, 46, F)
            for (dx, dy, cc) in ((1, 55, '#4f9a5a'), (3, 53, '#4f9a5a'), (5, 56, '#3f7a3a'), (2, 51, '#e8736a'), (5, 52, '#f6d04a'), (4, 57, '#4f9a5a')):
                o.set(px0 + dx, dy, K(cc)); o.set(px0 + dx, dy + 1, K('#3f7a3a'))
        o.rect(ox + 27, 38, ox + 36, 60, F); o.rect(ox + 28, 39, ox + 35, 60, GD); o.rect(ox + 28, 39, ox + 29, 44, GL)
        o.rect(ox + 31, 39, ox + 32, 60, F); o.rect(ox + 5, 59, ox + 58, 60, FD)
    return outline_obj(o, K('#4a3020') if kind != 'greenhouse' else K('#5f6d67'))


def tree(rnd, r=13, pine=False):
    o = C(r * 2 + 8, r * 2 + 18)
    cx = o.w // 2
    base, light, dark = (K('#2f7f5c'), K('#4fa477'), K('#1e5a44')) if pine else (K('#3f9a4c'), K('#6cc060'), K('#2a6e3c'))
    ty = o.h - 2
    o.rect(cx - 2, ty - 9, cx + 1, ty, K('#7a4e2a')); o.rect(cx + 1, ty - 9, cx + 1, ty, K('#553318')); o.rect(cx - 2, ty - 9, cx - 2, ty, K('#9a6a3c'))
    if pine:
        top = 2
        for tier, (w, y0, y1) in enumerate(((5, top, top + 10), (9, top + 7, top + 19), (12, top + 15, top + 29))):
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
    return outline_obj(o, K('#1c4630'))


def bush(rnd, flowers=None, r=6):
    o = C(r * 2 + 6, r * 2 + 4)
    base, light, dark = K('#4a9a4c'), K('#72c062'), K('#2f743c')
    o.disc(o.w / 2 - 0.5, r + 2, r, base); o.disc(o.w / 2 + 2, r + 3, r - 2, dark); o.disc(o.w / 2 - 2.5, r, r - 3, light)
    if flowers:
        for _ in range(7):
            x, y = rnd.randrange(2, o.w - 2), rnd.randrange(2, o.h - 2)
            if o.get(x, y) is not None:
                o.set(x, y, K(flowers)); o.set(x + 1, y, mix(K(flowers), (255, 255, 255), 0.4))
    return outline_obj(o, K('#1c4630'))


def scene(kind, seed=11):
    rnd = random.Random(seed)
    c = C(W, H)
    G, GL, GD = K('#86c05a'), K('#a8d870'), K('#63a246')
    c.rect(0, 0, W - 1, H - 1, G)
    for _ in range(1100):
        c.set(rnd.randrange(W), rnd.randrange(H), GL if rnd.random() < 0.55 else GD)
    for _ in range(80):
        x, y = rnd.randrange(2, W - 2), rnd.randrange(2, H - 2)
        c.set(x, y, GD); c.set(x - 1, y - 1, GD); c.set(x + 1, y - 1, GD)
    # dirt yard
    D, DL, DD = K('#e4b474'), K('#f1cd92'), K('#c9975c')
    for y in range(74, 174):
        for x in range(4, 208):
            edge = min(x - 4, 207 - x, y - 74, 173 - y)
            if edge + rnd.choice((0, 0, 1, 1, 2, 3)) >= 3:
                c.set(x, y, D)
    for _ in range(420):
        x, y = rnd.randrange(8, 204), rnd.randrange(78, 170)
        if c.get(x, y) == D:
            c.set(x, y, DL if rnd.random() < 0.6 else DD)
    # tilled bed for the agent's crops, and a flower bed
    S, SD, SL = K('#7b4b2b'), K('#5a341d'), K('#986540')

    def bed(x0, y0, x1, y1):
        c.rect(x0, y0, x1, y1, S)
        for y in range(y0 + 3, y1, 5):
            c.rect(x0 + 1, y, x1 - 1, y, SD)
        for _ in range((x1 - x0) * (y1 - y0) // 14):
            c.set(rnd.randrange(x0 + 1, x1), rnd.randrange(y0 + 1, y1), SL)
        for x in range(x0, x1 + 1):
            c.set(x, y0, SD); c.set(x, y1, SD)
        for y in range(y0, y1 + 1):
            c.set(x0, y, SD); c.set(x1, y, SD)
    bed(12, 88, 92, 134)
    bed(118, 84, 200, 112)
    for i in range(6):                                                               # sunflowers and marigolds
        for j, yy in enumerate((90, 102)):
            x = 124 + i * 13 + (j * 4)
            c.rect(x, yy, x + 1, yy + 6, K('#3f8a3a')); c.set(x - 1, yy + 4, K('#5fae4a')); c.set(x + 2, yy + 3, K('#5fae4a'))
            cc = K('#f6c832') if (i + j) % 2 == 0 else K('#f08a3a')
            c.rect(x - 1, yy - 3, x + 2, yy, cc); c.rect(x, yy - 4, x + 1, yy + 1, cc); c.rect(x, yy - 2, x + 1, yy - 1, K('#7a4a1c'))
    # stone path from the door
    for y in range(72, 176, 7):
        x = 101 + ((y // 7) % 2)
        c.rect(x, y, x + 8, y + 3, K('#cfc5ad')); c.rect(x + 1, y - 1, x + 7, y + 4, K('#cfc5ad'))
        c.rect(x + 1, y - 1, x + 6, y, K('#e7dfca')); c.rect(x + 2, y + 4, x + 7, y + 4, K('#a59a82'))
    # pond
    cx, cy, rx, ry = 164, 146, 30, 16
    for y in range(cy - ry - 3, cy + ry + 4):
        for x in range(cx - rx - 3, cx + rx + 4):
            d = ((x - cx) / (rx + 3)) ** 2 + ((y - cy) / (ry + 3)) ** 2 + math.sin(x * 0.7) * 0.03
            if d <= 1:
                c.set(x, y, K('#8a8076') if (x * 7 + y * 3) % 5 else K('#6a6058'))
    for y in range(cy - ry, cy + ry + 1):
        for x in range(cx - rx, cx + rx + 1):
            d = ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2
            if d <= 1:
                c.set(x, y, K('#3f8fb0') if d > 0.82 else K('#55aecb'))
    for (x, y, w) in ((150, 140, 7), (166, 150, 9), (172, 138, 5), (146, 152, 4)):
        c.rect(x, y, x + w, y, K('#a8dcea'))
    c.rect(178, 148, 181, 149, K('#4f9a5a')); c.set(180, 147, K('#f28fb1'))        # lily pad
    for (x, y) in ((134, 132), (192, 134), (140, 160), (186, 160), (160, 128)):
        c.rect(x, y, x + 4, y + 2, K('#b0a79b')); c.rect(x, y, x + 3, y, K('#d6cfc4')); c.rect(x + 1, y + 3, x + 4, y + 3, K('#6a6058'))
    # fence with a gap at the path
    def fence(x0, x1, y):
        for x in range(x0, x1, 2):
            c.rect(x, y + 3, x + 1, y + 4, K('#b98250')); c.rect(x, y + 7, x + 1, y + 8, K('#b98250'))
            c.set(x, y + 5, K('#6e4624')); c.set(x, y + 9, K('#6e4624'))
        for x in range(x0, x1 + 1, 11):
            c.rect(x, y, x + 3, y + 11, K('#a8703c')); c.rect(x, y, x, y + 11, K('#d09a62')); c.rect(x + 3, y, x + 3, y + 11, K('#6e4624'))
            c.rect(x, y, x + 3, y, K('#d09a62')); c.rect(x, y + 12, x + 3, y + 12, K('#4a3020'))
    fence(6, 86, 62); fence(122, 204, 62)
    # trees and bushes behind and beside the house
    def place(o, x, y):
        for yy in range(3):                                                           # ground shadow
            for xx in range(4, o.w - 4):
                if c.get(x + xx, y + o.h - 2 + yy) in (G, GL, GD):
                    c.set(x + xx, y + o.h - 2 + yy, K('#5a9440'))
        c.blit(o, x, y)
    place(tree(rnd, 14), -6, 2)
    place(tree(rnd, 11, pine=True), 22, -4)
    place(tree(rnd, 12, pine=True), 150, -2)
    place(tree(rnd, 15), 176, 6)
    place(bush(rnd, '#f28fb1'), 140, 44)
    place(bush(rnd), 48, 46)
    # the house of this space
    h = house(kind)
    for yy in range(4):
        for xx in range(4, h.w - 4):
            if c.get(72 + xx - 1, 64 + yy) in (G, GL, GD):
                c.set(72 + xx - 1, 64 + yy, K('#5a9440'))
    c.blit(h, 71, 2)
    # yard dressing
    place(bush(rnd, '#c77adf', r=7), 108, 150)
    c.blit(outline_obj(barrel()), 16, 146)
    c.blit(tree(rnd, 9), 40, 132)
    return c


def barrel():
    o = C(14, 18)
    o.rect(2, 2, 11, 15, K('#a8703c')); o.rect(2, 2, 3, 15, K('#d09a62')); o.rect(10, 2, 11, 15, K('#6e4624'))
    o.rect(2, 5, 11, 5, K('#8a8078')); o.rect(2, 12, 11, 12, K('#8a8078')); o.rect(3, 2, 10, 3, K('#4fa0c0')); o.rect(4, 2, 6, 2, K('#a8dcea'))
    return o


if __name__ == '__main__':
    here = os.path.dirname(__file__)
    os.makedirs(os.path.join(here, 'art'), exist_ok=True)
    for kind in ('farmhouse', 'cabin', 'barn', 'greenhouse'):
        s = scene(kind)
        s.png(os.path.join(here, 'art', f'garden-{kind}.png'))
        s.png(os.path.join(here, f'gview-{kind}.png'), scale=4)
    print('ok')
