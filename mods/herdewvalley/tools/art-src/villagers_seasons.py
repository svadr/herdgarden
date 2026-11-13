"""The four villagers dressed for each season. Summer is the original drawing, unchanged.
Spring and autumn change the colours of their clothes; autumn adds long sleeves and a scarf where it suits.
Winter gives each a coat, a scarf, mittens, and for the elder a wool hat. Faces, hair and hats that identify them stay.
Also draws the winter covers for the crops and the snow shovel."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from px import C, hexc
import villagers3 as v3
import villagers_side as vs
from villagers3 import span, put, outline, W, H

SEASONS = ('spring', 'summer', 'autumn', 'winter')
NAMES = ('farmer', 'tinker', 'gardener', 'elder')
OUTFIT = {
    'farmer': {
        'spring': {'pal': {'C': '#bfe6c0', 'L': '#e0f6df', 'c': '#8fc596'}},
        'autumn': {'pal': {'C': '#c9472b', 'L': '#e06a4a', 'c': '#96301c', 'Q': '#3c1408', 'U': '#8a5a36', 'u': '#684224',
                           'N': '#8a5a36', 'n': '#684224', 'q': '#2e1c0c'}},
        'winter': {'pal': {'C': '#3f5f8f', 'L': '#5a7db0', 'c': '#2c4670', 'U': '#48699a', 'u': '#2c4670', 'Q': '#16233c',
                           'N': '#5a4a3c', 'n': '#40332a', 'q': '#221a14'},
                   'scarf': ('#d8352f', '#a8241f'), 'mitt': ('#d9a25a', '#a8742f')},
    },
    'tinker': {
        'spring': {'pal': {'C': '#3fa39a', 'L': '#6fc9be', 'c': '#2a7a72', 'Q': '#12403c'}},
        'autumn': {'pal': {'C': '#4f7a4a', 'L': '#6f9a62', 'c': '#365a34', 'Q': '#1c3a1c'}, 'scarf': ('#e3a92f', '#b57d1c')},
        'winter': {'pal': {'C': '#a83a2c', 'L': '#c9553f', 'c': '#7c2418', 'Q': '#3c0c08', 'N': '#4a4a56', 'n': '#33333c', 'q': '#1a1a20'},
                   'scarf': ('#f3ead8', '#cfc3a8'), 'mitt': ('#4a4a56', '#33333c')},
    },
    'gardener': {
        'spring': {'pal': {'C': '#f08fb0', 'L': '#fbb8cf', 'c': '#cf6a8f', 'Q': '#6a2a44'}},
        'autumn': {'pal': {'C': '#c9632c', 'L': '#e58a4a', 'c': '#9a431c', 'Q': '#4a1c08'}, 'sleeves': True},
        'winter': {'pal': {'C': '#8a4f96', 'L': '#a970b4', 'c': '#673672', 'Q': '#33143c', 'W': '#9c5fa8', 'w': '#7a4186'},
                   'scarf': ('#fdf3f5', '#e3cdd6'), 'mitt': ('#f08fb0', '#c96a8c'), 'sleeves': True, 'muffs': True, 'tail': False},
    },
    'elder': {
        'spring': {'pal': {'V': '#5f9fd9', 'v': '#3f78b0'}},
        'autumn': {'pal': {'V': '#8f2f3f', 'v': '#6a1f2c'}},
        'winter': {'pal': {'C': '#6f7f96', 'L': '#8a9ab0', 'c': '#536178', 'V': '#5f6f88', 'v': '#465468', 'Q': '#222a38',
                           'N': '#4a4036', 'n': '#362e26', 'q': '#1c1610'},
                   'mitt': ('#3f5f8f', '#2c4670'), 'hat': True},
    },
}
EXTRA = {'T': '#c9472b', 't': '#96301c', 'P': '#fbf6ea', 'd': '#3c1408', 'A': '#f7b6cc'}
now = {'name': None, 'o': {}}


def arms(g, o, top, sleeve):
    """Long sleeves and mittens: the bare skin of each arm, from the top down, becomes sleeve and then mitten."""
    for x in range(W):
        rows = [y for y in range(top, 24) if g[y][x] in 'Ss']
        if o.get('sleeves'):
            for y in rows[:-2]:
                g[y][x] = sleeve(x)
        if o.get('mitt'):
            for y in rows[-2:]:
                g[y][x] = 'M' if g[y][x] == 'S' else 'z'


def dress_front(g):
    o, name = now['o'], now['name']
    arms(g, o, 17, lambda x: {3: 'L', 4: 'C', 11: 'C', 12: 'c'}.get(x, 'C'))
    if o.get('scarf'):
        span(g, 15, 5, 10, 'X'); span(g, 16, 5, 10, 'X'); g[15][10] = 'x'; g[16][10] = 'x'
        if o.get('tail', True):
            g[17][9] = 'X'; g[18][9] = 'X'; g[19][9] = 'x'
    if o.get('muffs'):
        for y in (10, 11, 12):
            g[y][3] = 'A'; g[y][12] = 'A'
    if o.get('hat'):
        span(g, 4, 5, 10, 'T')
        for y in (5, 6, 7):
            span(g, y, 4, 11, 'T'); g[y][11] = 't'
        span(g, 8, 3, 12, 't'); put(g, 2, 7, 'PP'); put(g, 3, 7, 'PP'); g[5][5] = 'P'
    outline(g, set('TtP'), 'd'); outline(g, set('XxMzA'), 'Q')


def dress_side(g):
    o, name = now['o'], now['name']
    dy = next(y for y in range(H) if 'E' in g[y]) - 11
    arms(g, o, 17 + dy, lambda x: 'C')
    if o.get('scarf'):
        span(g, 15 + dy, 7 if not o.get('tail', True) else 6, 10, 'X'); span(g, 16 + dy, 7, 10, 'X'); g[16 + dy][10] = 'x'
        if o.get('tail', True):
            g[16 + dy][5] = 'X'; g[17 + dy][5] = 'X'; g[18 + dy][5] = 'x'
    if o.get('muffs'):
        for y in (11, 12):
            g[y + dy][6] = 'A'; g[y + dy][7] = 'A'
    if o.get('hat'):
        span(g, 4 + dy, 6, 10, 'T')
        for y in (5, 6, 7):
            span(g, y + dy, 4, 11, 'T'); g[y + dy][4] = 't'
        span(g, 8 + dy, 3, 12, 't'); put(g, 2 + dy, 7, 'PP'); put(g, 3 + dy, 7, 'PP')
    outline(g, set('TtP'), 'd'); outline(g, set('XxMzA'), 'Q')


_f3, _fs = v3.finish, vs.finish
v3.finish = lambda g, hair, extra=(): (dress_front(g), _f3(g, hair, extra))[1]
vs.finish = lambda g, hair, extra=(): (dress_side(g), _fs(g, hair, extra))[1]


def palette(name, season):
    o = OUTFIT[name].get(season, {})
    pal = {**getattr(v3, name)()[1], **EXTRA, **o.get('pal', {})}
    if o.get('scarf'):
        pal['X'], pal['x'] = o['scarf']
    if o.get('mitt'):
        pal['M'], pal['z'] = o['mitt']
    return {k: hexc(v) for k, v in pal.items()}


def build(outdir, season):
    out = {}
    for name in NAMES:
        now['name'], now['o'] = name, OUTFIT[name].get(season, {})
        pal = palette(name, season)
        rows = [''.join(r) for r in getattr(v3, name)()[0]]
        base = os.path.join(outdir, f'v-{name}-{season}')
        c = C(W, H); c.stamp(0, 0, rows, pal); c.png(base + '.png')
        b = C(W, 20); b.stamp(0, 0, rows[1:21], pal); b.png(base + '-bust.png')
        f = C(W, 16); f.stamp(0, 0, rows[0:16], pal); f.png(base + '-face.png')
        strip = C(W * 4, H)
        for i, (pose, swing, dy) in enumerate(vs.FRAMES):
            strip.stamp(i * W, 0, [''.join(r) for r in getattr(vs, name)(pose, swing, dy)], pal)
        strip.png(base + '-walk.png')
        out[name] = (c, strip)
    now['o'] = {}
    return out


# ---- winter covers for the crops: a glass cloche over each plant, snow on top, the plant still showing ----
CROPS = {
    'p-1': ["..........", "..........", "..........", "..........", "..........", "..........", "..........", "..........",
            "....dc....", "...dcca...", "....ba....", "....b....."],
    'p-2': ["..........", "..........", "..........", "..........", "..........", "....d.....", "...dcc.d..", "..dccacca.",
            "...acbca..", "....cba...", "....b.....", "....b....."],
    'p-3': ["..........", "..........", "....dc....", "...dcca...", "..dcccca..", ".dccaccca.", "..accbca..", ".dccbcca..",
            "..acbaa...", "....b.....", "....b.....", "....b....."],
    'p-4': ["..........", "..........", "....dc....", "...dcca...", "..dcfeca..", ".dcceecca.", "..accbcfe.", ".fecbccee.",
            ".eeabaa...", "....b.....", "....b.....", "....b....."],
    'p-wilt': ["..........", "..........", "..........", "..........", "..........", "..........", "....gg....", "...g.bg...",
               "..gh.b.gh.", "..h..b..h.", "....b.....", "....b....."],
}
CROP_PAL = {'a': '#3f7a30', 'b': '#4a8a3a', 'c': '#6fae4a', 'd': '#9bd06a', 'e': '#e2532f', 'f': '#f58a5a', 'g': '#b8b05a', 'h': '#8a7a3a'}
CLOCHE = ["....kk....",
          "...ssss...",
          "..ssssss..",
          ".osssssso.",
          "o........o",
          "o.h......o",
          "o.h......o",
          "o.h......o",
          "o........o",
          "o........o",
          "o........o",
          "oooooooooo"]


def covered(rows):
    c = C(10, 12)
    c.stamp(0, 0, rows, {k: hexc(v) for k, v in CROP_PAL.items()})
    glass, rim = (232, 244, 252), hexc('#8fb4cc')
    for y, r in enumerate(CLOCHE):
        inside = [x for x, ch in enumerate(r) if ch != '.']
        for x, ch in enumerate(r):
            if ch == 'o':
                c.set(x, y, rim)
            elif ch == 's':
                c.set(x, y, (255, 255, 255))
            elif ch == 'k':
                c.set(x, y, hexc('#6f94ad'))
            elif ch == 'h':
                c.set(x, y, (255, 255, 255, 215))
            elif y >= 4 and inside and inside[0] < x < inside[-1]:
                p = c.get(x, y)
                c.set(x, y, tuple(round(p[i] * 0.72 + glass[i] * 0.28) for i in range(3)) if p else (*glass, 96))
    return c


SHOVEL = ["HH............",
          ".Hh...........",
          "..Hh..........",
          "...Hh.........",
          "....Hh........",
          ".....Hh.......",
          "......Hh..WW..",
          ".......HhWWWW.",
          "........bBWWWW",
          "........bBBWWw",
          ".........bBBww",
          "..........bbb."]


if __name__ == '__main__':
    here = os.path.dirname(__file__)
    art = os.path.join(here, 'art')
    os.makedirs(os.path.join(here, 'seasons'), exist_ok=True)
    sheet = C(4 * 20 + 4 + 4 * 68, 4 * 34 + 2)
    for j, season in enumerate(SEASONS):
        sp = build(art, season)
        for i, name in enumerate(NAMES):
            sheet.blit(sp[name][0], 4 + i * 20, 1 + j * 34)
            sheet.blit(sp[name][1], 88 + i * 68, 1 + j * 34)
    sheet.png(os.path.join(here, 'seasons', 'villagers-light.png'), scale=6, bg=hexc('#e4b474'))
    sheet.png(os.path.join(here, 'seasons', 'villagers-snow.png'), scale=6, bg=hexc('#e3ecf5'))
    crops = C(5 * 12 + 2, 14)
    for i, (n, rows) in enumerate(CROPS.items()):
        cv = covered(rows); cv.png(os.path.join(art, n + '-winter.png')); crops.blit(cv, 2 + i * 12, 1)
    sh = C(14, 12)
    sh.stamp(0, 0, SHOVEL, {k: hexc(v) for k, v in {'H': '#a8703c', 'h': '#6e4624', 'B': '#9fb3c8', 'b': '#62768c', 'W': '#ffffff', 'w': '#cfdbea'}.items()})
    sh.png(os.path.join(art, 'g-shovel.png'))
    crops.blit(sh, 0, 0) if False else None
    crops.png(os.path.join(here, 'seasons', 'covers.png'), scale=10, bg=hexc('#7b4b2b'))
    sh.png(os.path.join(here, 'seasons', 'shovel.png'), scale=10, bg=hexc('#e3ecf5'))
    print('ok')
