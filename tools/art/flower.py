"""Flower: a big pink bloom with a spiral seed head, in a garden (40x40)."""
import math
from shapes import *

PAL = {
    'c': '#b3e5fc', 'p': '#f48fb1', 'P': '#c2185b', 'y': '#ffeb3b',
    'Y': '#fb8c00', 'g': '#2e7d32', 'G': '#8bc34a', 's': '#8d6e63',
}


def petal(cx, cy, ang, length, width, inner=1.5):
    a = math.radians(ang)
    def inside(x, y):
        dx, dy = x - cx, y - cy
        u = dx * math.cos(a) + dy * math.sin(a)
        v = -dx * math.sin(a) + dy * math.cos(a)
        if u < inner or u > length:
            return False
        t = (u - inner) / (length - inner)
        return abs(v) <= width * math.sin(math.pi * (0.15 + 0.85 * t)) ** 0.7
    return inside


def draw(S):
    P = new(S, 'c', PAL)
    # rolling hills behind
    fill(P, lambda x, y: y > 27 + 2.5 * math.sin(x * 0.16 + 1.0), 'G')
    fill(P, lambda x, y: y > 30 + 1.8 * math.sin(x * 0.23 + 3.0), 'g')
    # blossom branches reaching in from the top corners
    for x0, y0, x1, y1 in ((-1, 2, 15, 7.5), (41, 4, 26, 6.5)):
        L = math.hypot(x1 - x0, y1 - y0)
        br = lambda t, x0=x0, y0=y0, x1=x1, y1=y1, L=L: (x0 + (x1 - x0) * t / L,
                                                          y0 + (y1 - y0) * t / L + 1.2 * math.sin(math.pi * t / L))
        curve(P, br, 0, L, 's')
        curve(P, lambda t, br=br: (br(t)[0], br(t)[1] + 0.9), 0, L * 0.6, 's')
        for i, t in enumerate((2.5, 6, 9.5, 13, L - 0.5)):
            if t > L:
                continue
            x, y = br(t)
            up = -1 if i % 2 else 1
            tx, ty = x + 0.6, y + up * 2.4
            line(P, x, y, tx, ty, 's')
            for a in range(0, 360, 72):
                r = math.radians(a + i * 25)
                fill(P, circle(tx + 1.1 * math.cos(r), ty + 1.1 * math.sin(r), 0.7), 'p')
            put(P, tx, ty, 'P')
            if i % 2 == 0:
                leaf(P, x, y, 3.2, 1.0, 60 + i * 30, 'G')
    # tall tulips at the sides
    for tx, top, k, k2 in ((4.5, 12, 'P', 'p'), (8.5, 17, 'Y', 'y'), (31.5, 16, 'p', 'P'), (36, 11.5, 'Y', 'y')):
        curve(P, lambda t, tx=tx: (tx + 0.5 * math.sin(t * 0.3), top + 2 + t), 0, 38 - top, 'g')
        cup = union(ellipse(tx, top + 1.5, 1.9, 2.2), rect(tx - 1.9, top - 1, tx + 1.9, top + 1))
        fill(P, cup, k)
        put(P, tx, top - 1, 'c')
        line(P, tx, top - 0.5, tx, top + 2.5, k2)
        leaf(P, tx + 0.3, 33, 6, 1.4, -70 if tx < 20 else -110, 'G', 'g', side_veins=False)
    # ground: soil with pebbles, grass blades in two greens
    fill(P, lambda x, y: y > 36 + 0.6 * math.sin(x * 0.5), 's')
    for px, py in ((3, 38.5), (11, 39), (27, 38.4), (35, 39.2)):
        fill(P, ellipse(px, py, 1.2, 0.6), 'Y')
    grass(P, 37, 'g', step=1.6, height=5.5, seed=0.3)
    grass(P, 37.5, 'G', x0=0.8, step=1.6, height=4.0, seed=1.9)
    # small flowers in the grass, on stems
    for fx, fy, k, kc in ((5, 28, 'P', 'y'), (34.5, 26, 'p', 'Y'), (30, 31, 'Y', 'P'), (9.5, 31.5, 'y', 'Y')):
        line(P, fx, fy, fx + 0.5, 37, 'g')
        for a in range(0, 360, 60):
            r = math.radians(a)
            put(P, fx + 1.2 * math.cos(r), fy + 1.2 * math.sin(r), k)
        put(P, fx, fy, kc)

    # stem with two veined leaves
    curve(P, lambda t: (20 + 1.2 * math.sin(t * 0.25), 18 + t), 0, 21, 'g')
    curve(P, lambda t: (21 + 1.2 * math.sin(t * 0.25), 18 + t), 0, 21, 'g')
    leaf(P, 21, 30, 10, 2.6, -35, 'G', 'g', side_veins=False)
    leaf(P, 20, 33, 9, 2.4, 205, 'G', 'g', side_veins=False)

    cx, cy = 20, 14
    # petals: pink, one magenta outline round the bloom, a magenta midline each
    outer = union(*[petal(cx, cy, a, 11.5, 3.3) for a in range(0, 360, 45)])
    fill(P, outer, 'p')
    outline(P, outer, 'P')
    for a in range(0, 360, 45):
        r = math.radians(a)
        line(P, cx + 5 * math.cos(r), cy + 5 * math.sin(r), cx + 9.5 * math.cos(r), cy + 9.5 * math.sin(r), 'P')
    fill(P, circle(cx, cy, 5.6), 'P')
    # seed head: yellow disc, orange ring, seeds in a sunflower spiral
    fill(P, circle(cx, cy, 4.3), 'Y')
    fill(P, circle(cx, cy, 3.6), 'y')
    for n in range(1, 40):
        r = 0.55 * math.sqrt(n)
        if r > 3.2:
            break
        a = n * math.radians(137.5)
        if n % 2:
            put(P, cx + r * math.cos(a), cy + r * math.sin(a), 'Y')
    # butterfly: orange wings with magenta spots, dark body
    bx, by = 13.5, 24
    for side in (-1, 1):
        up = ellipse(bx + side * 1.6, by - 0.8, 1.5, 1.6)
        lo = ellipse(bx + side * 1.2, by + 1.4, 1.0, 1.0)
        fill(P, union(up, lo), 'Y')
        put(P, bx + side * 1.7, by - 1.0, 'P')
    line(P, bx, by - 2, bx, by + 2.2, 's')
    line(P, bx, by - 2, bx - 1, by - 3.2, 's')
    line(P, bx, by - 2, bx + 1, by - 3.2, 's')
    return P


if __name__ == '__main__':
    import sys
    P = draw(40)
    P.png(sys.argv[1], cell=12)
    print(P.counts())
