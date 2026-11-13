"""The homestead yard before anything is built: the same ground, path, pond, fences and lamps,
with a staked-out lot, a signpost and a lumber pile where the house will go, and two bare beds.
Also the 24 x 24 sidebar icon for the lot."""
import os, sys, random
sys.path.insert(0, os.path.dirname(__file__))
from px import C, hexc
from garden import bush, outline_obj
import garden2 as g2
from garden2 import W, H, K, G, GL, GD, ground, dirt, bed, stones, pond, fence, tree, lamp, LAMPS

DARK = K('#3a2416')
WOOD = {'o': DARK, 'L': K('#e9c48a'), 'B': K('#d3a468'), 'D': K('#a9793f'), 'P': K('#b9773f'), 'p': K('#8a5328'),
        'g': K('#2f6e2a'), 'G': K('#3f8a3a'), 'E': K('#f3dcae'), 'r': K('#e2432f'), 'R': K('#f47a5a'),
        's': K('#d9c7a0'), 'S': K('#efe2c2'), 't': K('#b09a70'), 'k': K('#8a5a36')}

SIGN = [".ooooooooooooo.",
        "oLLLLLLLLLLLLLo",
        "oLBBBGBBBGBBBDo",
        "oLBBBBGBGBBBBDo",
        "oLBBBBBgBBBBBDo",
        "oLBBBBBgBBBBBDo",
        "oBDDDDDDDDDDDDo",
        ".ooooooooooooo.",
        "......oPpo.....",
        "......oPpo.....",
        "......oPpo.....",
        "......oPpo.....",
        "......oPpo.....",
        "......oPpo.....",
        "......oPpo.....",
        "......oooo....."]

LUMBER = ["....oooooooooooooo..",
          "...oLLLLLLLLLLLLLEo.",
          "...oDDDDDDDDDDDDDEo.",
          ".oooooooooooooooooo.",
          "oLLLLLLLLLLLLLEoLLEo",
          "oDDDDDDDDDDDDDEoDDEo",
          "oooooooooooooooooooo"]

STAKE = ["oRro",
         "oPpo",
         "oPpo",
         "oPpo",
         "oPpo",
         "oooo"]

SACK = ["..okko...",
        ".oSSSSo..",
        "oSSSSSSo.",
        "oSsGsSSso",
        "oSsgsSsso",
        "oSssssSso",
        "ostttttto",
        ".ooooooo."]

LOT = (82, 24, 128, 58)                                        # the cleared ground the house will stand on
STAKES = ((82, 22), (125, 22), (82, 52), (125, 52))


def obj(rows):
    o = C(len(rows[0]), len(rows))
    o.stamp(0, 0, rows, WOOD)
    return o


def shade(c, o, x, y):
    for xx in range(1, o.w - 1):
        if c.get(x + xx, y + o.h) in (G, GL, GD):
            c.set(x + xx, y + o.h, K('#5a9440'))
        elif c.get(x + xx, y + o.h) is not None:
            c.set(x + xx, y + o.h, K('#c9975c'))
    c.blit(o, x, y)


def scene(seed=11):
    rnd = random.Random(seed)
    c = C(W, H)
    ground(c, rnd)

    def place(o, x, y):
        for yy in range(3):
            for xx in range(4, o.w - 4):
                if c.get(x + xx, y + o.h - 2 + yy) in (G, GL, GD):
                    c.set(x + xx, y + o.h - 2 + yy, K('#5a9440'))
        c.blit(o, x, y)

    dirt(c, rnd, 4, 70, 207, 130)
    bed(c, rnd, 12, 80, 92, 126)
    bed(c, rnd, 118, 78, 200, 102)
    stones(c, [(101 + (i % 2), 68 + i * 7) for i in range(10)])
    pond(c, 162, 117, 26, 8)
    dirt(c, rnd, *LOT)
    fence(c, 6, 78, 57); fence(c, 134, 204, 57)
    place(tree(rnd, 13), -6, 0); place(tree(rnd, 11, pine=True), 24, -8); place(tree(rnd, 12, pine=True), 150, -6); place(tree(rnd, 14), 178, 0)
    place(bush(rnd, '#f28fb1'), 140, 40); place(bush(rnd), 50, 42)
    # the string between the stakes, then the stakes over it
    x0, y0, x1, y1 = STAKES[0][0] + 2, STAKES[0][1] + 3, STAKES[3][0] + 1, STAKES[3][1] + 3
    for x in range(x0, x1 + 1):
        if (x // 2) % 2 == 0:
            c.set(x, y0, K('#fbf3dc')); c.set(x, y1, K('#fbf3dc'))
    for y in range(y0, y1 + 1):
        if (y // 2) % 2 == 0:
            c.set(x0, y, K('#fbf3dc')); c.set(x1, y, K('#fbf3dc'))
    for (x, y) in STAKES:
        shade(c, obj(STAKE), x, y)
    shade(c, obj(LUMBER), 83, 37)
    shade(c, obj(SACK), 115, 35)
    shade(c, obj(SIGN), 98, 26)
    for (lx, ly) in LAMPS:
        c.blit(outline_obj(lamp(), K('#22222a')), lx, ly)
    return c


def lit():
    c = C(W, H)
    for (x, y) in LAMPS:
        l = lamp(True)
        for yy in range(3, 7):
            for xx in range(2, 7):
                c.set(x + xx, y + yy, l.p[yy][xx])
    return c


def icon():
    """24 x 24: the signpost on a tuft of grass."""
    c = C(24, 24)
    for x in range(3, 21):
        c.set(x, 21, K('#63a246'))
    for x in range(5, 19):
        c.set(x, 22, K('#4f8a3a'))
    for x in (4, 8, 15, 19):
        c.set(x, 20, K('#86c05a'))
    c.blit(obj(SIGN), 4, 5)
    return c


if __name__ == '__main__':
    here = os.path.dirname(__file__)
    s = scene()
    s.png(os.path.join(here, 'art', 'yard-homestead-empty.png'))
    lit().png(os.path.join(here, 'art', 'yard-homestead-empty-lit.png'))
    icon().png(os.path.join(here, 'art', 'h-lot.png'))
    s.png(os.path.join(here, 'empty-big.png'), scale=5)
    icon().png(os.path.join(here, 'lot-big.png'), scale=10, bg=hexc('#f4ecdf'))
    print('ok')
