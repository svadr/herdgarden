"""Side-on walking frames for the four villagers, facing right. Four frames each, laid out in a strip:
stride (arm back), passing (body one pixel up), stride (arm forward), passing. Same drawing rules as the front views."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from px import C, hexc
from villagers3 import grid, span, put, outline, SKIN, W, H, farmer as _f, tinker as _t, gardener as _g, elder as _e

FRAMES = ((0, -1, 0), (1, 0, -1), (0, 1, 0), (1, 0, -1))        # leg pose, arm swing, body lift


def head(g, dy, bald=False):
    for y in range(9, 14):
        span(g, y + dy, 7, 11, 'S')
    span(g, 14 + dy, 7, 10, 'S')
    g[12 + dy][12] = 'S'                                           # nose
    if not bald:
        span(g, 9 + dy, 7, 11, 's')
    g[11 + dy][7] = 's'; g[12 + dy][7] = 's'                       # ear
    g[14 + dy][7] = 's'; g[14 + dy][8] = 's'
    g[11 + dy][10] = 'E'; g[12 + dy][10] = 'E'
    put(g, 15 + dy, 7, 'ss')


def torso(g, dy):
    for y in range(16, 23):
        span(g, y + dy, 5, 10, 'C'); g[y + dy][5] = 'c'
    g[16 + dy][5] = '.'; g[16 + dy][10] = '.'
    if dy:
        span(g, 22, 6, 9, 'N')                                     # legs reach up when the body lifts


def arm(g, dy, swing, sleeve_to=20):
    x = 7 + swing
    for y in range(17, 23):
        hand = y > sleeve_to
        g[y + dy][x] = 's' if hand else 'c'
        g[y + dy][x + 1] = 'S' if hand else 'L'


def legs(g, pose):
    if pose == 0:
        for y in range(23, 28):
            a = 5 if y < 25 else 4
            b = 8 if y < 25 else 9
            span(g, y, a, a + 2, 'n'); span(g, y, b, b + 2, 'N')
        for y in (28, 29):
            span(g, y, 3, 6, 'b'); span(g, y, 9, 12, 'B')
    else:
        for y in range(23, 28):
            span(g, y, 6, 7, 'n'); span(g, y, 8, 9, 'N')
        for y in (28, 29):
            span(g, y, 6, 10, 'B'); g[y][6] = 'b'


def finish(g, hair, extra=()):
    outline(g, set(hair), 'O')
    outline(g, set('Sls'), 'k')
    for chars, och in extra:
        outline(g, set(chars), och)
    outline(g, set('CLcUuWwVvJm'), 'Q')
    outline(g, set('Nn'), 'q')
    outline(g, set('Bb'), 'o')
    return g


def farmer(pose, swing, dy):
    g = grid(); head(g, dy); torso(g, dy); legs(g, pose)
    for y in range(18, 23):
        span(g, y + dy, 6, 10, 'U'); g[y + dy][6] = 'u'
    g[16 + dy][8] = 'U'; g[17 + dy][8] = 'U'
    arm(g, dy, swing)
    span(g, 2 + dy, 5, 10, 'Y'); span(g, 3 + dy, 4, 11, 'Y'); span(g, 4 + dy, 4, 11, 'Y'); span(g, 5 + dy, 4, 11, 'R')
    span(g, 6 + dy, 2, 13, 'Y'); span(g, 7 + dy, 1, 14, 'Y'); span(g, 8 + dy, 3, 12, 'w')
    put(g, 2 + dy, 6, 'yy'); g[3 + dy][5] = 'y'; span(g, 6 + dy, 3, 6, 'y'); g[3 + dy][11] = 'w'; g[4 + dy][11] = 'w'; span(g, 7 + dy, 10, 14, 'w'); put(g, 5 + dy, 4, 'rr')
    for y in range(9, 13):
        span(g, y + dy, 4, 6, 'H')
    g[13 + dy][5] = 'H'; g[13 + dy][6] = 'H'
    return finish(g, 'YywRrH')


def tinker(pose, swing, dy):
    g = grid(); head(g, dy); torso(g, dy); legs(g, pose)
    span(g, 22 + dy, 5, 10, 'J'); g[22 + dy][9] = 'm'
    arm(g, dy, swing)
    span(g, 4 + dy, 5, 10, 'H'); span(g, 5 + dy, 3, 11, 'H')
    for y in (6, 7, 8):
        span(g, y + dy, 3, 11, 'H')
    g[3 + dy][5] = 'H'; g[3 + dy][8] = 'H'; g[4 + dy][3] = 'H'; g[3 + dy][10] = 'H'
    put(g, 5 + dy, 5, 'ii'); g[6 + dy][4] = 'i'; g[6 + dy][3] = 'h'; g[7 + dy][3] = 'h'
    span(g, 7 + dy, 3, 11, 'J')
    put(g, 6 + dy, 9, 'ggg'); put(g, 7 + dy, 9, 'gGg'); put(g, 8 + dy, 9, 'ggg')
    for y in range(9, 13):
        span(g, y + dy, 3, 6, 'H'); g[y + dy][3] = 'h'
    g[13 + dy][5] = 'H'; g[13 + dy][6] = 'H'
    return finish(g, 'HhiJgG')


def gardener(pose, swing, dy):
    g = grid(); head(g, dy); torso(g, dy)
    span(g, 22, 5, 10, 'C'); g[22][5] = 'c'
    span(g, 23, 5, 10, 'C')
    for y in (24, 25, 26):
        span(g, y, 4, 11, 'C'); g[y][4] = 'c'
    span(g, 27, 4, 11, 'c')
    for y in range(18, 27):
        span(g, y + (dy if y < 23 else 0), 9, 10, 'W')
    put(g, 26, 9, 'ww')
    for y in (28, 29):
        if pose == 0:
            span(g, y, 4, 6, 'b'); span(g, y, 9, 11, 'B')
        else:
            span(g, y, 6, 9, 'B'); g[y][6] = 'b'
    arm(g, dy, swing, sleeve_to=18)
    span(g, 4 + dy, 5, 10, 'H'); span(g, 5 + dy, 3, 11, 'H')
    for y in (6, 7, 8):
        span(g, y + dy, 2, 11, 'H')
    for y in range(9, 16):
        span(g, y + dy, 2, 6, 'H'); g[y + dy][2] = 'h'
    for y in (16, 17, 18):
        span(g, y + dy, 2, 4, 'H'); g[y + dy][2] = 'h'
    g[9 + dy][10] = 'H'; g[9 + dy][11] = 'H'; g[10 + dy][11] = 'H'
    put(g, 5 + dy, 6, 'iii'); put(g, 6 + dy, 4, 'ii'); g[7 + dy][3] = 'i'
    g[5 + dy][5] = 'F'; put(g, 6 + dy, 4, 'FfF'); g[7 + dy][5] = 'F'
    return finish(g, 'HhiFf')


def elder(pose, swing, dy):
    g = grid(); head(g, dy, bald=True); torso(g, dy); legs(g, pose)
    for y in range(16, 23):
        for x in range(5, 11):
            if g[y + dy][x] in 'Cc':
                g[y + dy][x] = 'V' if x > 5 else 'v'
    arm(g, dy, swing)
    span(g, 5 + dy, 6, 10, 'S'); span(g, 6 + dy, 4, 11, 'S'); span(g, 7 + dy, 4, 11, 'S'); span(g, 8 + dy, 4, 11, 'S')
    for y in range(9, 14):
        span(g, y + dy, 4, 6, 'S')
    put(g, 6 + dy, 7, 'll'); g[7 + dy][8] = 'l'
    for y in range(8, 14):
        span(g, y + dy, 3, 5, 'W'); g[y + dy][3] = 'w'
    put(g, 10 + dy, 9, 'WW')
    span(g, 13 + dy, 8, 12, 'W'); span(g, 14 + dy, 7, 12, 'W'); span(g, 15 + dy, 7, 12, 'W'); span(g, 16 + dy, 8, 11, 'W'); span(g, 17 + dy, 9, 10, 'W')
    g[15 + dy][7] = 'w'; g[16 + dy][8] = 'w'; g[17 + dy][9] = 'w'; g[14 + dy][7] = 'w'
    put(g, 17 + dy, 12, 'KK')
    for y in range(18 + dy, 30):
        g[y][13] = 'K'
    return finish(g, 'Ww', extra=(('K', 'o'),))


def build(outdir):
    out = {}
    for name, fn, front in (('farmer', farmer, _f), ('tinker', tinker, _t), ('gardener', gardener, _g), ('elder', elder, _e)):
        pal = {k: hexc(v) for k, v in front()[1].items()}
        strip = C(W * 4, H)
        for i, (pose, swing, dy) in enumerate(FRAMES):
            g = fn(pose, swing, dy)
            strip.stamp(i * W, 0, [''.join(r) for r in g], pal)
        strip.png(os.path.join(outdir, f'v-{name}-walk.png'))
        out[name] = strip
    return out


if __name__ == '__main__':
    here = os.path.dirname(__file__)
    sp = build(os.path.join(here, 'art'))
    big = C(W * 4 + 4, (H + 2) * 4 + 2)
    for i, n in enumerate(sp):
        big.blit(sp[n], 2, 2 + i * (H + 2))
    big.png(os.path.join(here, 'walksheet.png'), scale=8, bg=hexc('#e4b474'))
    print(list(sp))
