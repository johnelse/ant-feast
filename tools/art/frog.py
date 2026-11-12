"""Frog: a frog sitting on a lily pad in a pond (40x40)."""
import math
from shapes import *

PAL = {
    'b': '#1e6fa8', 'l': '#8fd3f4', 'g': '#7cc242', 'G': '#2e6b1f',
    'y': '#fff176', 'k': '#1b1b1b', 'p': '#f48fb1', 'w': '#ffffff',
}


def pad(P, cx, cy, rx, ry, notch_deg, veins=7):
    """A round lily pad with a notch cut to its centre, an outline and radial veins."""
    n = math.radians(notch_deg)
    def inside(x, y):
        if ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 > 1:
            return False
        a = math.atan2((y - cy) / ry, (x - cx) / rx)
        d = (a - n + math.pi) % (2 * math.pi) - math.pi
        return abs(d) > 0.28
    fill(P, inside, 'g')
    outline(P, inside, 'G')
    for i in range(veins):
        a = n + 2 * math.pi * (i + 0.5) / veins
        curve_in(P, lambda t, a=a: (cx + math.cos(a) * rx * t, cy + math.sin(a) * ry * t), 0.15, 1.0, 'G', inside)
    return inside


def lily(P, cx, cy, r):
    """A pink water lily: pointed petals around a yellow centre."""
    for a in range(-90, 270, 45):
        rr = math.radians(a)
        fill(P, ellipse(cx + r * 0.7 * math.cos(rr), cy + r * 0.7 * math.sin(rr), r * 0.75, r * 0.32, a), 'p')
    for a in (-90, 30, 150):
        put(P, cx + r * 0.9 * math.cos(math.radians(a)), cy + r * 0.9 * math.sin(math.radians(a)), 'w')
    fill(P, circle(cx, cy, r * 0.32), 'y')


def bubble(P, x, y, r):
    outline(P, circle(x, y, r), 'l')
    put(P, x - r * 0.4, y - r * 0.4, 'w')


def draw(S):
    P = new(S, 'b', PAL)
    # ripples drifting across the pond
    streaks(P, [(2, 0.5, 0.6, 12, 12), (9, 2.2, 0.7, 10, -1), (15, 4.0, 0.6, 9, 30), (23, 1.3, 0.7, 8, -2),
                (31, 3.1, 0.6, 9, 31), (37, 0.2, 0.5, 11, 9)], 'l')
    for x, y, r in ((22, 4.5, 1.6), (4, 16, 1.6), (36, 27, 1.6)):
        bubble(P, x, y, r)

    # small pads around the edges, then lilies
    pad(P, 5, 34, 7, 4.5, 20)
    pad(P, 33, 6.5, 7, 4.5, 150)
    pad(P, 3, 4, 6, 3.8, 70, 6)
    pad(P, 38, 39, 6, 3.6, 220, 6)
    lily(P, 8, 25.5, 2.8)
    lily(P, 34, 6, 2.4)

    # reeds and cattails up the right side
    for x0, top, lean in ((36.5, 16, -1.5), (38.8, 20, -0.4), (34, 23, -1.8)):
        line(P, x0, 40, x0 + lean, top, 'G')
        fill(P, ellipse(x0 + lean * 1.05, top - 1.8, 0.7, 2.2, lean * 4), 'k')
        line(P, x0 + lean * 1.1, top - 3.8, x0 + lean * 1.12, top - 5, 'G')

    # dragonfly over the water, top left
    dx, dy = 12, 6.5
    for side in (-1, 1):
        for off, ln in ((-0.6, 4.5), (0.9, 4.0)):
            w = ellipse(dx + side * ln * 0.6, dy + off * 1.6, ln * 0.65, 1.3, side * (-12 if off < 0 else 10))
            fill(P, w, 'w')
            outline(P, w, 'l')
    line(P, dx, dy - 1.5, dx, dy + 5, 'p')
    put(P, dx, dy - 2, 'k')

    # the big lily pad the frog sits on
    big = pad(P, 20, 31, 15, 8, 75, 9)

    # --- the frog
    body = ellipse(20, 24, 8.5, 7.5)
    head = ellipse(20, 16.5, 8.5, 5.5)
    thighs = [ellipse(11.5, 28, 3.6, 5.2, 25), ellipse(28.5, 28, 3.6, 5.2, -25)]
    feet = [ellipse(8, 34, 3.4, 1.4, -10), ellipse(32, 34, 3.4, 1.4, 10)]
    for f in feet:
        fill(P, f, 'g')
        outline(P, f, 'G')
    for x in (5.2, 7.8, 10.6, 29.4, 32.2, 34.8):
        put(P, x, 35, 'y')
    for t in thighs:
        fill(P, t, 'g')
        outline(P, t, 'G')
    frog = union(body, head)
    fill(P, frog, 'g')
    outline(P, frog, 'G')
    belly = ellipse(20, 26, 5, 4.6)
    fill(P, belly, 'y')
    # front legs and toes
    for side in (-1, 1):
        line(P, 20 + side * 5.5, 23, 20 + side * 6.5, 31, 'G')
        for d in (-1, 0, 1):
            put(P, 20 + side * 6.5 + d * 1.1, 32, 'y')
        put(P, 20 + side * 6.5, 31, 'g')
    # spots on the back and thighs
    for x, y, r in ((13.5, 22, 0.9), (26.5, 22, 0.9), (11.2, 26.5, 0.8), (28.8, 26.5, 0.8),
                    (12.5, 30, 0.7), (27.5, 30, 0.7), (20, 19.6, 0.7)):
        fill(P, circle(x, y, r), 'k')
    # darker mottling across the head and shoulders
    for x, y, r in ((17, 13.2, 0.8), (23, 13.2, 0.8), (16, 21, 0.7), (24, 21, 0.7), (12, 19.5, 0.6),
                    (28, 19.5, 0.6), (9.8, 29.5, 0.6), (30.2, 29.5, 0.6), (13.5, 26, 0.6), (26.5, 26, 0.6)):
        fill(P, circle(x, y, r), 'G')
    # mouth, nostrils, highlight
    curve(P, lambda t: (t, 18.6 + 0.04 * (t - 20) ** 2), 14, 26, 'k')
    put(P, 18.5, 15.5, 'k')
    put(P, 21.5, 15.5, 'k')
    curve(P, lambda q: (20 + 6.5 * math.cos(q), 16.5 + 4.2 * math.sin(q)), 3.6, 4.2, 'w')
    # bulging eyes
    for ex in (14, 26):
        eye = circle(ex, 12.2, 3.2)
        fill(P, eye, 'y')
        outline(P, eye, 'G')
        fill(P, ellipse(ex, 12.4, 1.7, 1.0), 'k')
        put(P, ex - 1, 11.2, 'w')
    return P


if __name__ == '__main__':
    import sys
    P = draw(40)
    P.png(sys.argv[1], cell=12)
    print(P.counts())
