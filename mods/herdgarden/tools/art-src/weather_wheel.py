"""What falls in the yard, as wheels. Herdr's only one-way animation is `spin`, which turns a one-color
SVG. Each wheel is a big ring of small flakes whose centre sits to the left of the yard; turning clockwise,
the part of the ring that crosses the yard moves downward, so the flakes fall and never come back up.

  python3 weather_wheel.py <art folder>     writes weather/<season>-<n>.svg

The mod draws each SVG at left = -(D + R), top = 66 - R, size 2R (art pixels) and spins it.
"""
import math, os, random, sys

W, H = 212, 132
D = 250                 # from the wheel's centre to the yard's left edge
R = D + W + 6           # the wheel's radius
# season: one wheel per color; each (name, flakes in view, flake w, flake h)
WHEELS = {
    'spring': (('a', 6, 2, 1.2), ('b', 4, 2, 1.2)),
    'autumn': (('a', 5, 2.4, 1.3), ('b', 4, 2.4, 1.3), ('c', 3, 2.4, 1.3)),
    'winter': (('a', 12, 1.3, 1.3), ('b', 7, 2, 2)),
}


def wheel(seed, in_view, w, h):
    rnd = random.Random(seed)
    area = math.pi * (R * R - D * D)
    n = round(in_view * area / (W * H))
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{2 * R}" height="{2 * R}" viewBox="0 0 {2 * R} {2 * R}" fill="#000000">']
    for _ in range(n):
        r = math.sqrt(rnd.uniform(D * D, R * R))        # even over the ring's area
        a = rnd.uniform(0, 2 * math.pi)
        x, y = R + r * math.cos(a), R + r * math.sin(a)
        # each flake is turned to its place on the wheel, so it is upright as it crosses the yard
        out.append(f'<rect x="{x - w / 2:.1f}" y="{y - h / 2:.1f}" width="{w}" height="{h}" transform="rotate({math.degrees(a):.1f} {x:.1f} {y:.1f})"/>')
    out.append('</svg>')
    return '\n'.join(out)


if __name__ == '__main__':
    out = os.path.join(os.path.abspath(os.path.expanduser(sys.argv[1])), 'weather')
    os.makedirs(out, exist_ok=True)
    for season, wheels in WHEELS.items():
        for i, (name, in_view, w, h) in enumerate(wheels):
            with open(os.path.join(out, f'{season}-{name}.svg'), 'w') as f:
                f.write(wheel(f'{season}{i}', in_view, w, h))
    print('ok', D, R)
