"""Villagers, fifth pass: drawn the way farm-game villagers are. 16 wide by 32 tall, a big head on a small body,
two-pixel dot eyes and no mouth, saturated colours, and a dark one-pixel outline in a deep shade of each material.
Original characters; the conventions are the genre's, the people are ours."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from px import C, hexc

W, H = 16, 32
SKIN = {'S': '#f8c79c', 's': '#e2a070', 'l': '#fddcb8', 'k': '#7c3c22', 'E': '#2b1810'}


def grid():
    return [['.'] * W for _ in range(H)]


def span(g, y, x0, x1, ch):
    for x in range(x0, x1 + 1):
        if 0 <= x < W and 0 <= y < H:
            g[y][x] = ch


def put(g, y, x, s):
    for i, ch in enumerate(s):
        if ch != ' ' and 0 <= x + i < W:
            g[y][x + i] = ch


def outline(g, chars, och):
    todo = []
    for y in range(H):
        for x in range(W):
            if g[y][x] in chars:
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    xx, yy = x + dx, y + dy
                    if 0 <= xx < W and 0 <= yy < H and g[yy][xx] == '.':
                        todo.append((xx, yy))
    for x, y in todo:
        g[y][x] = och


def face(g, fringe_shadow=True):
    for y in range(9, 14):
        span(g, y, 4, 11, 'S')
    span(g, 14, 5, 10, 'S')
    if fringe_shadow:
        span(g, 9, 4, 11, 's')
    for y in range(10, 14):
        g[y][11] = 's'
    g[14][10] = 's'; g[14][9] = 's'
    for x in (5, 10):
        g[11][x] = 'E'; g[12][x] = 'E'
    put(g, 15, 7, 'ss')


def body(g, sleeve_to=20):
    span(g, 16, 4, 11, 'C'); g[16][4] = 'L'; put(g, 16, 7, 'ss')
    for y in range(17, 23):
        span(g, y, 5, 10, 'C')
        hand = y > sleeve_to
        g[y][3] = 'S' if hand else 'L'; g[y][4] = 'S' if hand else 'C'
        g[y][11] = 'S' if hand else 'C'; g[y][12] = 's' if hand else 'c'
    for y in range(18, 23):
        g[y][5] = 'c'; g[y][10] = 'c'
    g[17][6] = 'L'


def legs(g):
    for y in range(23, 28):
        span(g, y, 5, 7, 'N'); span(g, y, 8, 10, 'N'); g[y][7] = 'n'; g[y][10] = 'n'
    shoes(g)


def shoes(g, y0=28):
    for y in (y0, y0 + 1):
        span(g, y, 4, 7, 'B'); span(g, y, 8, 11, 'B'); g[y][7] = 'b'; g[y][11] = 'b'


def finish(g, hair, extra=()):
    outline(g, set(hair), 'O')
    outline(g, set('Sls'), 'k')
    for chars, och in extra:
        outline(g, set(chars), och)
    outline(g, set('CLcUuWwVvJm'), 'Q')
    outline(g, set('Nn'), 'q')
    outline(g, set('Bb'), 'o')
    return g


def farmer():
    g = grid(); face(g); body(g); legs(g)
    # blue overalls over a white shirt
    for y in range(18, 23):
        span(g, y, 6, 9, 'U')
    for y in range(20, 23):
        span(g, y, 5, 10, 'U'); g[y][10] = 'u'
    g[16][6] = 'U'; g[17][6] = 'U'; g[16][9] = 'U'; g[17][9] = 'U'; g[18][6] = 'm'; g[18][9] = 'm'
    for y in range(18, 23):
        g[y][9] = 'u' if y < 20 else g[y][9]
    # straw hat with a red band
    span(g, 2, 5, 10, 'Y'); span(g, 3, 4, 11, 'Y'); span(g, 4, 4, 11, 'Y'); span(g, 5, 4, 11, 'R')
    span(g, 6, 2, 13, 'Y'); span(g, 7, 1, 14, 'Y'); span(g, 8, 3, 12, 'w')
    put(g, 2, 6, 'yy'); g[3][5] = 'y'; span(g, 6, 3, 6, 'y'); g[3][11] = 'w'; g[4][11] = 'w'; span(g, 7, 10, 14, 'w'); g[5][11] = 'r'; g[5][10] = 'r'
    g[8][3] = 'H'; g[8][12] = 'H'; g[9][3] = 'H'; g[9][12] = 'H'; g[10][3] = 'H'; g[9][4] = 'H'; g[9][11] = 'H'
    finish(g, 'YywRrH')
    return g, {**SKIN, 'Y': '#f4d77a', 'y': '#fceca8', 'w': '#d2a747', 'O': '#6e4c14', 'R': '#d2432f', 'r': '#a52f20',
               'H': '#8b4a2b', 'C': '#f6f1e6', 'L': '#ffffff', 'c': '#cdc5b4', 'Q': '#3a3a5c', 'U': '#4f80c2',
               'u': '#365e98', 'm': '#f6d04a', 'N': '#4f80c2', 'n': '#365e98', 'q': '#1f3560', 'B': '#7a4424',
               'b': '#5a2f16', 'o': '#2e1408'}


def tinker():
    g = grid(); face(g); body(g); legs(g)
    span(g, 22, 5, 10, 'J'); put(g, 22, 7, 'mm')
    put(g, 17, 7, 'cc'); g[18][8] = 'c'; g[19][8] = 'c'; g[20][8] = 'c'; g[21][8] = 'c'      # jacket opening
    # dark tousled hair, goggles up on the forehead
    span(g, 4, 5, 10, 'H'); span(g, 5, 3, 12, 'H')
    for y in (6, 7, 8):
        span(g, y, 3, 12, 'H')
    g[3][6] = 'H'; g[3][9] = 'H'; g[4][4] = 'H'; g[4][11] = 'H'; g[3][11] = 'H'
    put(g, 5, 5, 'ii'); g[6][4] = 'i'; g[5][11] = 'h'; g[6][12] = 'h'; g[7][12] = 'h'
    span(g, 7, 3, 12, 'J')
    for x in (4, 9):
        put(g, 6, x, 'ggg'); put(g, 7, x, 'gGg'); put(g, 8, x, 'ggg')
    for y in (9, 10):
        g[y][3] = 'H'; g[y][12] = 'h'
    finish(g, 'HhiJgG', extra=())
    return g, {**SKIN, 'H': '#4a2f2a', 'h': '#33201c', 'i': '#6e4a40', 'O': '#1c0f0c', 'J': '#7a4a22', 'g': '#c9ccd4',
               'G': '#7fd6ea', 'C': '#e6892c', 'L': '#f6ac56', 'c': '#b4621a', 'Q': '#6a3408', 'm': '#f6d04a',
               'N': '#5c6e3c', 'n': '#445428', 'q': '#232e12', 'B': '#4a3024', 'b': '#33201a', 'o': '#1c0f0c'}


def gardener():
    g = grid(); face(g); body(g, sleeve_to=18)
    # green dress, full skirt, white apron
    span(g, 23, 4, 11, 'C'); g[23][11] = 'c'
    for y in (24, 25, 26):
        span(g, y, 3, 12, 'C'); g[y][12] = 'c'; g[y][11] = 'c'
    span(g, 27, 3, 12, 'c')
    for y in range(18, 27):
        span(g, y, 6, 9, 'W'); g[y][9] = 'w'
    put(g, 26, 6, 'wwww'); g[16][6] = 'W'; g[17][6] = 'W'; g[16][9] = 'W'; g[17][9] = 'w'
    shoes(g, 28)
    for y in (28, 29):
        g[y][4] = '.'; g[y][11] = '.'
    # long auburn hair with a flower
    span(g, 4, 5, 10, 'H'); span(g, 5, 3, 12, 'H')
    for y in (6, 7, 8):
        span(g, y, 2, 13, 'H')
    for y in range(9, 16):
        g[y][2] = 'H'; g[y][3] = 'H'; g[y][12] = 'H'; g[y][13] = 'h'
    g[16][2] = 'H'; g[17][2] = 'H'; g[16][13] = 'h'; g[17][13] = 'h'; g[16][3] = 'H'; g[16][12] = 'h'
    g[9][4] = 'H'; g[9][5] = 'H'; g[9][8] = 'H'; g[9][11] = 'H'
    put(g, 5, 5, 'iii'); put(g, 6, 4, 'ii'); g[7][3] = 'i'; g[8][3] = 'i'; g[6][13] = 'h'; g[7][13] = 'h'; g[8][13] = 'h'; span(g, 8, 9, 12, 'h')
    g[5][10] = 'F'; put(g, 6, 9, 'FfF'); g[7][10] = 'F'
    finish(g, 'HhiFf')
    return g, {**SKIN, 'H': '#c8562a', 'h': '#96391a', 'i': '#ee8448', 'O': '#521a08', 'F': '#fff2f7', 'f': '#f6c544',
               'C': '#56a86e', 'L': '#7cc890', 'c': '#3c8052', 'Q': '#1c4a2c', 'W': '#faf6ec', 'w': '#d6cebd',
               'B': '#7a4424', 'b': '#5a2f16', 'o': '#2e1408'}


def elder():
    g = grid(); face(g, fringe_shadow=False); body(g); legs(g)
    # bald crown
    span(g, 5, 5, 10, 'S'); span(g, 6, 4, 11, 'S'); span(g, 7, 4, 11, 'S'); span(g, 8, 4, 11, 'S')
    put(g, 6, 5, 'll'); g[7][5] = 'l'; g[6][11] = 's'; g[7][11] = 's'; g[8][11] = 's'
    # white hair at the sides, brows, and a full beard
    for y in (8, 9, 10, 11):
        g[y][3] = 'W'; g[y][12] = 'w'
    put(g, 10, 4, 'WW'); put(g, 10, 9, 'WW')
    span(g, 13, 4, 11, 'W'); span(g, 14, 4, 11, 'W'); span(g, 15, 5, 10, 'W'); span(g, 16, 5, 10, 'W'); span(g, 17, 6, 9, 'W'); span(g, 18, 7, 8, 'W')
    g[13][11] = 'w'; g[14][11] = 'w'; g[15][10] = 'w'; g[16][10] = 'w'; g[17][9] = 'w'; g[18][8] = 'w'; put(g, 13, 7, 'ww')
    g[12][3] = 'W'; g[12][12] = 'w'; g[13][3] = 'W'; g[13][12] = 'w'
    # teal waistcoat over a cream shirt, brown trousers
    for y in range(16, 23):
        for x in range(5, 11):
            if g[y][x] in 'Cc':
                g[y][x] = 'V' if x < 10 else 'v'
    for y in range(19, 23):
        g[y][7] = 'C'; g[y][8] = 'c'
    g[20][7] = 'm'; g[22][7] = 'm'
    # walking stick
    put(g, 17, 13, 'KK')
    for y in range(18, 30):
        g[y][14] = 'K'
    finish(g, 'Ww', extra=(('K', 'o'),))
    return g, {**SKIN, 'W': '#f4f1ea', 'w': '#c9c4b8', 'O': '#8f8a7e', 'C': '#f3ecd9', 'L': '#fffaf0', 'c': '#cfc6ae',
               'Q': '#4a4436', 'V': '#2f948c', 'v': '#1f6c66', 'm': '#f6d04a', 'N': '#8a6238', 'n': '#684624',
               'q': '#2e1c0c', 'B': '#5a3a24', 'b': '#402818', 'o': '#2e1408', 'K': '#a06a30'}


def build(outdir):
    out = {}
    for name, fn in (('v-farmer', farmer), ('v-tinker', tinker), ('v-gardener', gardener), ('v-elder', elder)):
        g, pal = fn()
        rows = [''.join(r) for r in g]
        pal = {k: hexc(v) for k, v in pal.items()}
        c = C(W, H); c.stamp(0, 0, rows, pal); c.png(os.path.join(outdir, name + '.png'))
        b = C(W, 20); b.stamp(0, 0, rows[1:21], pal); b.png(os.path.join(outdir, name + '-bust.png'))
        out[name] = c
    return out


if __name__ == '__main__':
    here = os.path.dirname(__file__)
    sp = build(os.path.join(here, 'art'))
    for label, bg in (('light', hexc('#fbf6ee')), ('dark', hexc('#1a1612'))):
        big = C(len(sp) * 20 + 4, 34)
        for i, n in enumerate(sp):
            big.blit(sp[n], 4 + i * 20, 1)
        big.png(os.path.join(here, f'v3sheet-{label}.png'), scale=12, bg=bg)
    print(list(sp))
