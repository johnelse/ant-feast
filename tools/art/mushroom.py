"""Mushroom: a fly agaric at the edge of a wood, with ferns and small mushrooms (40x40)."""
import math
from shapes import *

PAL = {
    'c': '#9ad0ec', 'w': '#ffffff', 'g': '#43a047', 'y': '#fdd835',
    'R': '#d32f2f', 'k': '#3e2723', 's': '#ecd9b0', 'S': '#b8955f',
}


def draw(S):
    P = new(S, 'c', PAL)
    # wood behind: trunks and leafy crowns along the top
    for tx, w in ((3, 2.2), (35.5, 2.6), (28, 1.6)):
        fill(P, rect(tx - w / 2, 0, tx + w / 2, 30), 'S')
        line(P, tx - w / 2 + 0.5, 0, tx - w / 2 + 0.5, 30, 'k')
    for cx, cy, r in ((3, 3, 6), (12, 0, 5), (36, 4, 6.5), (27.5, 1, 4.5), (20, -2, 4)):
        fill(P, circle(cx, cy, r), 'g')
    # ground: grass with a mossy edge, fallen leaves
    fill(P, lambda x, y: y > 30 + 1.0 * math.sin(x * 0.35), 'g')
    grass(P, 31, 'g', step=1.3, height=3.2, seed=0.7)
    # ferns at the left, against the sky
    for x0, y0, ln, d, bend in ((0, 31, 14, -50, 45), (8, 31, 11, -100, -40)):
        fern(P, x0, y0, ln, d, bend, 'g')
    for lx, ly, d in ((3, 36, 20), (11, 38, 150), (27, 38.5, -30), (37, 37.5, 200), (23, 35.5, 60)):
        leaf(P, lx, ly, 4.5, 1.6, d, 'y', 'S', side_veins=False)

    # small mushrooms to the right
    for mx, my, r in ((31, 33.5, 2.4), (35.5, 35, 1.8)):
        fill(P, rect(mx - 0.6, my, mx + 0.6, my + 2.8), 's')
        cap = both(circle(mx, my + 0.6, r), lambda x, y, my=my: y <= my + 0.6)
        fill(P, cap, 'S')
        outline(P, cap, 'k', where=lambda x, y, dx, dy: dy != 1)
        put(P, mx - 0.6, my - 0.6, 's')

    # big fly agaric
    cx = 19
    # stem: cream with tan shading on the right, a frilly skirt
    stem = union(rect(cx - 3, 18, cx + 3, 33), ellipse(cx, 33, 4.2, 2.2))
    fill(P, stem, 's')
    fill(P, both(stem, lambda x, y: x > cx + 1.4), 'S')
    for yy in (27, 30):  # growth rings
        curve_in(P, lambda t, yy=yy: (t, yy + 0.4 * math.sin(t * 0.8)), cx - 3, cx + 1.4, 'S', stem)
    outline(P, stem, 'k')
    skirt = poly([(cx - 3.8, 22), (cx + 3.8, 22), (cx + 4.6, 25), (cx - 4.6, 25)])
    fill(P, skirt, 'w')
    for x in range(int(cx - 4), int(cx + 5), 2):
        put(P, x + 0.5, 24.6, 'S')
    outline(P, skirt, 'k', where=lambda x, y, dx, dy: dy == 1)
    # cap: dome with gills underneath
    cap = both(ellipse(cx, 18, 15, 13), lambda x, y: y <= 18)
    gills = both(ellipse(cx, 18, 14, 2.4), lambda x, y: y > 17.5)
    fill(P, gills, 's')
    for a in range(-60, 61, 12):
        for i in range(30):
            t = i / 29
            x, y = cx + 13 * math.sin(math.radians(a)) * t, 17.5 + 2.5 * t
            if gills(math.floor(x) + 0.5, math.floor(y) + 0.5):
                put(P, x, y, 'S')
    fill(P, cap, 'R')
    # spots: round, varied, fewer towards the rim; highlight on the upper left
    for sx, sy, sr in ((13, 9, 1.8), (19.5, 7, 2.1), (26, 9.5, 1.8), (9, 14.5, 1.5), (16, 12.8, 1.5),
                       (23, 13.5, 1.8), (29.5, 14.5, 1.5), (12, 5.5, 1.1), (25.5, 5, 1.1), (19.5, 16.3, 1.0),
                       (6, 17, 0.9), (32.5, 17, 0.9), (19.5, 3.2, 0.9), (16, 16.5, 0.8), (23.5, 16.6, 0.8),
                       (8.5, 10.5, 0.8), (30, 10.5, 0.8)):
        fill(P, both(circle(sx, sy, sr), cap), 'w')
    curve(P, lambda a: (cx + 11 * math.cos(a), 18 + 9.5 * math.sin(a)), 3.55, 4.0, 'w')
    outline(P, cap, 'k')
    outline(P, gills, 'k', where=lambda x, y, dx, dy: dy == 1)
    return P


if __name__ == '__main__':
    import sys
    P = draw(40)
    P.png(sys.argv[1], cell=12)
    print(P.counts())
