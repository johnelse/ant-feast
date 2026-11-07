"""Apple: a ripe apple hanging from a leafy branch over an orchard fence (40x40)."""
import math
from shapes import *

PAL = {
    'c': '#a7d8f0', 'w': '#fff7f0', 'r': '#e53935', 'd': '#8e1b26',
    't': '#e8b86d', 'b': '#6d4c2f', 'G': '#2e7d32', 'g': '#9ccc65',
}


def draw(S):
    P = new(S, 'G', PAL)
    # inside the tree: sky glimpsed between leaves, branches, other apples
    for cx, cy, r in ((5, 4, 3.2), (16, 2, 2.6), (34, 3.5, 3.4), (37, 16, 2.4), (3, 19, 2.6), (29, 13, 1.8),
                      (10, 12, 1.6), (35, 27, 2.2), (6, 31, 2.0)):
        fill(P, circle(cx, cy, r), 'c')
    cloud(P, 34, 4, 5, 'w')
    for x0, y0, x1, y1 in ((-1, 9, 14, 13), (41, 22, 27, 18), (-1, 26, 10, 24)):
        for d in (0, 1):
            line(P, x0, y0 + d, x1, y1 + d, 'b')
    # big leaves all over: light ones with dark veins, some dark ones with light veins
    for row in range(4):
        for col in range(4):
            x0 = col * 10.5 - 2 + (5 if row % 2 else 0) + 1.2 * math.sin(row * 2.1 + col)
            y0 = row * 10 - 1 + 1.2 * math.sin(col * 1.7 + row)
            d = 30 + 55 * ((row + col) % 3) + 25 * math.sin(row + col * 1.9)
            k, v = ('g', 'G') if (row * 5 + col) % 3 else ('G', 'g')
            leaf(P, x0, y0, 11, 3.6, d, k, v, side_veins=False)
    for ax, ay in ((5.5, 15.5), (34, 24), (31, 6.5), (9, 35)):
        ap = circle(ax, ay, 2.2)
        fill(P, ap, 'r')
        fill(P, minus(ap, circle(ax - 0.7, ay - 0.6, 2.2)), 'd')
        put(P, ax - 0.8, ay - 0.9, 'w')
        line(P, ax, ay - 2.2, ax + 0.4, ay - 3.4, 'b')
    # the branch our apple hangs from
    br = lambda t: (t, 4.5 + 1.6 * math.sin(t * 0.18 + 0.4))
    for dy in (0, 1):
        curve(P, lambda t, dy=dy: (br(t)[0], br(t)[1] + dy), 8, 32, 'b')
    # grass and fence glimpsed at the bottom
    fill(P, lambda x, y: y > 37.5 + 0.6 * math.sin(x * 0.7), 'g')
    grass(P, 38.5, 'G', x0=1, step=2.0, height=2.5, seed=2.0)
    for fx, fy in ((4, 38.5), (31, 38.8), (36.5, 39)):
        flower(P, fx, fy, 'w', 't')

    # apple: two lobes and a rounder bottom, dipped at the stem
    apple = minus(union(circle(15.8, 21.5, 8.6), circle(24.2, 21.5, 8.6), circle(20, 24.5, 9.8)),
                  circle(20, 11.2, 2.6))
    fill(P, apple, 'r')
    # shadow on the right and underneath
    fill(P, minus(apple, circle(18.3, 21.8, 10.8)), 'd')
    # streaks running down from the stem, curving with the apple
    for off, ln in ((-6.5, 4), (-3.5, 5.5), (3.5, 5.5), (6.5, 4), (9, 3.5)):
        curve(P, lambda t, off=off: (20 + off * (0.55 + 0.45 * math.sin(math.pi * min(t, 14) / 14 * 0.9)),
                                     14 + t), 0.5, ln, 'd')
    # a few pale flecks
    for fx, fy in ((16, 27), (22, 29.5), (26, 25), (13, 23.5), (24, 20)):
        put(P, fx, fy, 't')
    # highlight: an arc and a glint, upper left
    curve(P, lambda a: (19 + 7.5 * math.cos(math.radians(a)), 22 + 7.5 * math.sin(math.radians(a))),
          200, 245, 'w')
    fill(P, circle(14.3, 17.2, 0.9), 'w')
    outline(P, apple, 'd')
    # stem up to the branch, and a leaf on it
    curve(P, lambda t: (20 + 0.6 * math.sin(t * 0.4), 13 - t), 0, 7, 'b')
    leaf(P, 20.5, 10.5, 7, 2.3, -20, 'g', 'G')
    return P


if __name__ == '__main__':
    import sys
    P = draw(40)
    P.png(sys.argv[1], cell=12)
    print(P.counts())
