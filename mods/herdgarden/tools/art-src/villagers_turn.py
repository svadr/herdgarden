"""Front and back walking frames for the four villagers, for when they walk down (toward you) or up
(away from you). Built from the front drawing in villagers3: the back view turns the face into the back
of the head, and the walk lifts one foot, then the other.

Use with villagers_seasons, which dresses them for the season:
    grids = turned(name, back=True)    -> the finished 16 x 32 grid, before the walk
    walk(grid)                          -> four grids: left foot up, passing, right foot up, passing
"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
import villagers3 as v3
from villagers3 import W, H

BACK = {'on': False}
_inner = None


def backify(g, name):
    """The back of the head, and no beard or front details on the body."""
    if name in ('farmer', 'tinker', 'gardener'):
        for y in range(9, 15):
            for x in range(2, 14):
                if g[y][x] in 'SsEl':
                    g[y][x] = 'H'
        for y in range(4, 9):                                   # goggles: only the strap shows from behind
            for x in range(W):
                if g[y][x] in 'gG':
                    g[y][x] = 'J' if name == 'tinker' else g[y][x]
        if name == 'gardener':                                  # the flower sits on the other side
            for y in range(4, 9):
                for x in range(W):
                    if g[y][x] in 'Ff':
                        g[y][x] = 'H'
        g[15][7] = 's'; g[15][8] = 's'                          # the neck
    else:                                                       # elder: bald crown, a ring of white hair low at the back
        for y in range(9, 13):
            for x in range(4, 12):
                if g[y][x] in 'sEW':
                    g[y][x] = 'S'
        for y in (11, 12):
            for x in range(3, 13):
                if g[y][x] != '.':
                    g[y][x] = 'W' if x < 12 else 'w'
        for x in range(4, 12):
            g[13][x] = 'S' if x < 11 else 's'
        for x in range(3, 13):                                  # no beard from behind
            g[14][x] = 's' if 6 <= x <= 9 else '.'
            g[15][x] = 's' if 7 <= x <= 8 else '.'
        for y in range(16, 19):
            for x in range(4, 12):
                if g[y][x] in 'Ww':
                    g[y][x] = 'V' if x < 10 else 'v'
    if name == 'elder':                                         # the shirt shows only at the front
        for y in range(16, 23):
            for x in (7, 8):
                if g[y][x] in 'Cc':
                    g[y][x] = 'V'
    # front details of the clothes: buttons and openings are not on the back
    for y in range(16, 23):
        for x in range(W):
            if g[y][x] == 'm':
                g[y][x] = 'U' if name == 'farmer' else ('V' if name == 'elder' else 'J')


def install():
    """Wrap villagers3.finish (already wrapped by villagers_seasons) so a back view can be asked for."""
    global _inner
    if _inner is not None:
        return
    _inner = v3.finish

    def finish(g, hair, extra=()):
        if BACK['on']:
            backify(g, BACK['name'])
        return _inner(g, hair, extra)
    v3.finish = finish


def turned(name, back):
    install()
    BACK['on'], BACK['name'] = back, name
    try:
        g, _ = getattr(v3, name)()
    finally:
        BACK['on'] = False
    return [list(r) for r in g]


FEET = set('NnBbqo')


def lift(g, x0, x1):
    out = [r[:] for r in g]
    for y in range(22, 30):
        for x in range(x0, x1 + 1):
            if y < 29 and g[y + 1][x] in FEET:
                out[y][x] = g[y + 1][x]
            elif g[y][x] in FEET:
                out[y][x] = '.' if y == 29 or g[y + 1][x] not in FEET else g[y + 1][x]
    for x in range(x0, x1 + 1):
        if out[29][x] in FEET:
            out[29][x] = '.'
    return out


def walk(g):
    return [lift(g, 2, 7), [r[:] for r in g], lift(g, 8, 13), [r[:] for r in g]]
