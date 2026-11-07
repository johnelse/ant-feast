"""Watermelon: a slice and a whole melon on a picnic blanket, with ants (40x40)."""
import math
from shapes import *

PAL = {
    'r': '#c62828', 'w': '#fafafa', 'g': '#7cb342', 'G': '#2e7d32',
    'y': '#fdd835', 'f': '#e8f5c8', 'm': '#f06272', 'k': '#212121',
}


ANT = ("k...k",
       ".k.k.",
       "..k..",
       "k.k.k",
       ".kkk.",
       "k.k.k",
       ".kkk.",
       "..k..")


def ant(P, x, y, flip=False):
    """A top-down ant from a pixel pattern, top-left at (x, y); flip turns it upside down."""
    rows = ANT[::-1] if flip else ANT
    for j, row in enumerate(rows):
        for i, ch in enumerate(row):
            if ch == 'k':
                put(P, x + i + 0.5, y + j + 0.5, 'k')


def draw(S):
    P = new(S, 'w', PAL)
    # picnic blanket: yellow and white gingham
    fill(P, lambda x, y: (int(x // 3) + int(y // 3)) % 2 == 0, 'y')
    # grass along the top edge, beyond the blanket
    fill(P, lambda x, y: y < 4 + 0.7 * math.sin(x * 0.6), 'g')
    grass(P, 4.5, 'G', step=1.4, height=2.5, seed=0.4)
    for fx in (6, 17, 29, 36):
        flower(P, fx, 2.2, 'w', 'm')

    # whole melon behind, with wavy dark stripes
    mel = ellipse(30, 12.5, 8.5, 6.3, -8)
    fill(P, mel, 'g')
    fill(P, both(mel, lambda x, y: math.sin((x - 30) * 0.9 + 1.2 * math.sin((y - 12) * 0.7)) > 0.25), 'G')
    curve(P, lambda a: (30 + 6 * math.cos(a), 12.5 + 4 * math.sin(a)), 3.6, 4.4, 'f')
    outline(P, mel, 'G')
    line(P, 38, 11, 39.5, 9.5, 'G')

    # --- slice: a wedge, rind at the bottom, with a bite out of the top left
    cx, cy, R = 18, 15, 18
    wedge = both(circle(cx, cy, R), lambda x, y: y >= cy + 2 + 0.0 * x)
    bite = union(circle(7, 17.5, 2.6), circle(10.5, 17, 2.4))
    fill(P, wedge, 'G')
    fill(P, both(wedge, circle(cx, cy, R - 1.2)), 'g')
    fill(P, both(wedge, circle(cx, cy, R - 2.4)), 'f')
    fill(P, both(wedge, circle(cx, cy, R - 3.4)), 'm')
    flesh = both(wedge, circle(cx, cy, R - 4.6))
    fill(P, flesh, 'r')
    # stripes on the rind
    for a in range(20, 170, 14):
        r = math.radians(a)
        line(P, cx + (R - 1.2) * math.cos(r), cy + (R - 1.2) * math.sin(r), cx + R * math.cos(r), cy + R * math.sin(r), 'g')
    # seeds: teardrops in two arcs, each with a glint
    for rr, n, off in ((7.5, 6, 0.2), (11.5, 8, 0.0)):
        for i in range(n):
            a = math.radians(15 + (150 / (n - 1)) * i + off * 20)
            sx, sy = cx + rr * math.cos(a), cy + 2 + rr * 0.9 * math.sin(a)
            if flesh(sx, sy):
                fill(P, ellipse(sx, sy, 0.6, 1.1, math.degrees(a) - 90), 'k')
                put(P, sx, sy, 'k')
                put(P, sx - 0.5, sy - 0.6, 'w')
    # the bite: blanket shows through, with a pale bitten edge
    fill(P, bite, 'w')
    fill(P, both(bite, lambda x, y: (int(x // 3) + int(y // 3)) % 2 == 0), 'y')
    outline(P, both(minus(wedge, bite), lambda x, y: True), 'k',
            where=lambda x, y, dx, dy: dy == 1)
    for x0 in range(4, 14):
        for y0 in range(16, 22):
            if wedge(x0 + .5, y0 + .5) and not bite(x0 + .5, y0 + .5) and any(
                    bite(x0 + .5 + dx, y0 + .5 + dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                put(P, x0 + 0.5, y0 + 0.5, 'm')
    # flat cut face along the top
    line(P, cx - R + 1.5, cy + 2.2, cx + R - 1.5, cy + 2.2, 'm')
    # ants carrying off a dropped seed
    ant(P, 33, 24)
    ant(P, 28, 31)
    fill(P, ellipse(30.5, 30, 0.7, 1.0), 'k')  # the seed it's carrying
    put(P, 30.2, 29.5, 'w')
    return P


if __name__ == '__main__':
    import sys
    P = draw(40)
    P.png(sys.argv[1], cell=12)
    print(P.counts())
