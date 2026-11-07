"""Owl: an owl on a branch under the moon (40x40)."""
import math
from shapes import *

PAL = {
    'n': '#14213d', 'y': '#ffd60a', 'w': '#f1f1e6', 'b': '#8d6e63',
    'k': '#3e2723', 'f': '#efdcc0', 'o': '#f57c00', 'g': '#558b2f',
}


def star(P, x, y, big=False):
    put(P, x, y, 'y')
    if big:
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            put(P, x + dx, y + dy, 'y')


def draw(S):
    P = new(S, 'n', PAL)
    # night sky: moonlit cloud wisps, moon, stars
    streaks(P, [(5.5, 0.4, 0.6, 9, 6), (11, 2.2, 0.7, 8, 27), (20, 3.6, 0.6, 7, 4), (28.5, 1.3, 0.6, 7, 27),
                (16, 4.8, 0.5, 6, 29), (25, 0.9, 0.5, 6, 3)], 'w')
    moon = minus(circle(31.5, 23, 3.4), circle(33.2, 21.8, 3.0))
    fill(P, moon, 'w')
    # tree trunks either side, with wavy bark grain
    left = lambda x, y: x < 5 + 1.0 * math.sin(y * 0.2) + (0.05 * (y - 26) ** 2 / 10 if y > 26 else 0)
    right = lambda x, y: x > 36 + 0.8 * math.sin(y * 0.25 + 1) - (0.05 * (y - 26) ** 2 / 10 if y > 26 else 0)
    trunks = union(left, right)
    fill(P, trunks, 'b')
    for x0 in (2.0, 38.3):
        curve_in(P, lambda t, x0=x0: (x0 + 0.8 * math.sin(t * 0.45 + x0), t), -1, 41, 'k', trunks)
    for kx, ky in ((2.5, 18), (38, 9)):
        fill(P, ellipse(kx, ky, 1.2, 1.8), 'k')
    outline(P, trunks, 'k', where=lambda x, y, dx, dy: dx != 0)
    for sx, sy, big in ((8, 9, True), (13, 3, False), (31, 4, True), (7.5, 18, False), (32.5, 15, False),
                        (28, 9, False), (8.5, 27, True), (33, 30, False), (16, 1.5, False), (25, 2, False)):
        star(P, sx, sy, big)
    # leafy twigs reaching in from the trunks
    for x0, y0, x1, y1, side in ((5, 9, 12, 6, 1), (36, 15, 29, 12, -1), (5.5, 22, 11, 21, 1)):
        line(P, x0, y0, x1, y1, 'b')
        for t in (0.45, 0.8, 1.0):
            x, y = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
            leaf(P, x, y, 3.2, 1.0, -60 if t < 0.9 else (0 if side > 0 else 180), 'g', 'k', side_veins=False)
    # branch with leaves
    br = lambda t: (t, 33 + 0.08 * (t - 20) + 0.6 * math.sin(t * 0.3))
    for dy in (0, 1, 2):
        curve(P, lambda t, dy=dy: (t, br(t)[1] + dy), -1, 41, 'k' if dy == 2 else 'b')
    for x0, d, k in ((3, 120, 'g'), (8, 60, 'g'), (31, 110, 'g'), (36, 55, 'g'), (14, 100, 'g'), (26, 80, 'g')):
        leaf(P, x0, br(x0)[1] + 1, 5.5, 1.8, d, k, 'k', side_veins=False)
    curve(P, lambda t: (36 + t, br(36)[1] - t * 0.8), 0, 5, 'b')

    # --- owl
    cx = 20
    body = ellipse(cx, 23, 9.5, 11)
    head = ellipse(cx, 12.5, 9, 7.5)
    tufts = union(poly([(cx - 8.5, 9), (cx - 9, 3.5), (cx - 4.5, 7)]), poly([(cx + 8.5, 9), (cx + 9, 3.5), (cx + 4.5, 7)]))
    owl = union(body, head, tufts)
    fill(P, owl, 'b')
    # chest: pale with rows of brown chevrons
    chest = ellipse(cx, 25, 6, 8)
    fill(P, chest, 'f')
    for j, yy in enumerate(range(20, 33, 3)):
        for xx in range(int(cx - 6) + (j % 2) * 2, int(cx + 6), 4):
            if chest(xx, yy):
                put(P, xx - 0.5, yy - 0.5, 'b')
                put(P, xx + 0.5, yy + 0.5, 'b')
                put(P, xx + 1.5, yy - 0.5, 'b')
    # wings: scalloped feather edges
    for side in (-1, 1):
        wing = both(ellipse(cx + side * 8, 24, 3.6, 9, side * -12), body)
        fill(P, wing, 'k')
        for yy in range(17, 33, 3):
            curve_in(P, lambda a, yy=yy: (cx + side * 8 + 2.2 * math.cos(a), yy + 1.2 * math.sin(a)), 0, math.pi,
                     'b', owl)
    # face: pale disc, big eyes
    face = union(circle(cx - 3.8, 12.5, 4.2), circle(cx + 3.8, 12.5, 4.2))
    fill(P, face, 'f')
    for ex in (cx - 3.8, cx + 3.8):
        fill(P, circle(ex, 12.5, 3.0), 'o')
        fill(P, circle(ex, 12.5, 2.3), 'y')
        fill(P, circle(ex, 12.5, 1.2), 'k')
        put(P, ex - 0.8, 11.6, 'w')
    # brow and beak
    line(P, cx - 7, 8.5, cx - 1, 10.3, 'k')
    line(P, cx + 7, 8.5, cx + 1, 10.3, 'k')
    fill(P, poly([(cx - 1.3, 14.5), (cx + 1.3, 14.5), (cx, 18)]), 'o')
    outline(P, owl, 'k')
    # feet gripping the branch
    for fx in (cx - 3, cx + 3):
        for dx in (-1, 0, 1):
            put(P, fx + dx, br(fx)[1] - 0.3, 'o')
    return P


if __name__ == '__main__':
    import sys
    P = draw(40)
    P.png(sys.argv[1], cell=12)
    print(P.counts())
