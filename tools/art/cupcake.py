"""Cupcake: a frosted cupcake with a cherry, on a plate at a party (40x40)."""
import math
from shapes import *

PAL = {
    'c': '#ffe0ec', 'w': '#ffffff', 'p': '#f48fb1', 'P': '#ad1457',
    'f': '#fff3d0', 'y': '#fbc02d', 'B': '#42a5f5', 'r': '#d32f2f',
}


def draw(S):
    P = new(S, 'c', PAL)
    # wallpaper: soft wavy stripes
    for x0 in range(2, 40, 6):
        curve(P, lambda t, x0=x0: (x0 + 0.9 * math.sin(t * 0.4), t), -1, 41, 'w')
    # bunting: a sagging string with little flags
    string = lambda t: (t, 0.8 + 1.4 * math.sin(math.pi * t / 40))
    curve(P, string, -1, 41, 'P')
    for i, x in enumerate(range(1, 40, 5)):
        _, y = string(x + 1.5)
        k = 'Bpy'[i % 3]
        fill(P, poly([(x, y), (x + 3.2, y), (x + 1.6, y + 3.6)]), k)
    # table and plate
    fill(P, lambda x, y: y > 34, 'f')
    line(P, 0, 34.5, 40, 34.5, 'y')
    plate = ellipse(20, 34.5, 15, 2.6)
    fill(P, plate, 'w')
    outline(P, plate, 'B')
    # wrapper: tapered cup with pleats
    cup = poly([(9.5, 23), (30.5, 23), (27.5, 34.5), (12.5, 34.5)])
    fill(P, cup, 'B')
    for i, x in enumerate(range(10, 31, 2)):
        xb = 12.5 + (x - 9.5) * (15 / 21)
        line(P, x + 0.5, 23, xb + 0.5, 34.5, 'w' if i % 2 else 'B')
    outline(P, cup, 'P')
    # frosting: three stacked swirls narrowing upward
    tiers = (ellipse(20, 22, 12.5, 4.0), ellipse(20, 18, 9.8, 3.6), ellipse(20, 14.4, 6.8, 3.1), ellipse(20, 11.4, 3.6, 2.4))
    frost = union(*tiers)
    fill(P, frost, 'p')
    # swirl lines: the lower edge of each tier, darker
    for t in tiers[1:]:
        outline(P, both(t, lambda x, y: True), 'P', where=lambda x, y, dx, dy: dy == 1)
    outline(P, frost, 'P')
    # highlights on the left of each tier
    for cx, cy, rx, ry in ((20, 22, 12.5, 4.0), (20, 18, 9.8, 3.6), (20, 14.4, 6.8, 3.1)):
        curve(P, lambda a, cx=cx, cy=cy, rx=rx, ry=ry: (cx + rx * 0.72 * math.cos(a), cy + ry * 0.55 * math.sin(a)),
              3.4, 4.1, 'w')
    # sprinkles: short dashes in three colours, angled
    for i, (sx, sy) in enumerate(((13, 21), (17, 23.5), (24, 22), (27.5, 20.5), (15, 18), (22.5, 17),
                                  (25.5, 19), (18, 14), (22, 13.5), (11, 23.5), (29, 23.3), (19.5, 20))):
        k = 'Byw'[i % 3]
        d = math.radians(40 + 50 * (i % 3))
        line(P, sx, sy, sx + 1.2 * math.cos(d), sy + 1.2 * math.sin(d), k)
    # cherry with a glint and a stem
    cherry = circle(20, 7.6, 3.1)
    fill(P, cherry, 'r')
    outline(P, cherry, 'P', where=lambda x, y, dx, dy: dy == 1)
    put(P, 19.0, 6.4, 'w')
    curve(P, lambda t: (20.5 + t * 0.9, 5 - t + 0.12 * t * t), 0, 3.2, 'P')
    return P


if __name__ == '__main__':
    import sys
    P = draw(40)
    P.png(sys.argv[1], cell=12)
    print(P.counts())
