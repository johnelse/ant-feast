"""Octopus: an octopus sprawled over a coral reef (40x40)."""
import math
from shapes import *

PAL = {
    'n': '#123a6b', 'c': '#5ee0e6', 'o': '#f4733c', 'O': '#8e2a1c',
    's': '#f3dfa2', 'p': '#d45fb0', 'g': '#4caf50', 'w': '#ffffff',
}


def path(x, y, deg, length, curl, wave=25, step=0.25):
    """Points along an arm: a gentle S-wave, then a curl over the last third."""
    pts = [(x, y, 0.0)]
    t = 0.0
    while t < length:
        f = t / length
        d = math.radians(deg + wave * math.sin(f * math.pi * 1.6))
        if f > 0.65:
            d += math.radians(curl) * ((f - 0.65) / 0.35) ** 1.3
        x += math.cos(d) * step
        y += math.sin(d) * step
        t += step
        pts.append((x, y, t / length))
    return pts


def tube(pts, r0, r1):
    """Inside a tapering tube along the points."""
    def inside(x, y):
        for px, py, f in pts:
            r = r0 + (r1 - r0) * f
            if (x - px) ** 2 + (y - py) ** 2 <= r * r:
                return True
        return False
    return inside


def coral(P, x, y, deg, length, k, depth=3):
    """A branching coral: a stem that forks twice."""
    a = math.radians(deg)
    x1, y1 = x + math.cos(a) * length, y + math.sin(a) * length
    line(P, x, y, x1, y1, k)
    line(P, x + 0.6, y, x1 + 0.6, y1, k)
    if depth:
        coral(P, x1, y1, deg - 28, length * 0.7, k, depth - 1)
        coral(P, x1, y1, deg + 30, length * 0.65, k, depth - 1)
    else:
        put(P, x1, y1 - 0.6, 'w')


def kelp(P, x0, top, k, phase):
    curve(P, lambda t: (x0 + 1.2 * math.sin(t * 0.45 + phase), t), top, 40, k)
    for y in range(int(top) + 2, 40, 3):
        side = 1 if (y // 3) % 2 else -1
        xs = x0 + 1.2 * math.sin(y * 0.45 + phase)
        fill(P, ellipse(xs + side * 1.6, y, 1.7, 0.7, side * -30), k)


def fish(P, x, y, d):
    """A tiny fish facing direction d (1 = right)."""
    fill(P, ellipse(x, y, 1.6, 0.8), 'c')
    put(P, x - d * 2, y - 0.6, 'c')
    put(P, x - d * 2, y + 0.6, 'c')
    put(P, x + d * 0.8, y - 0.2, 'n')


def bubble(P, x, y, r):
    outline(P, circle(x, y, r), 'c')
    put(P, x - r * 0.4, y - r * 0.4, 'w')


def draw(S):
    P = new(S, 'n', PAL)
    # currents
    streaks(P, [(3, 0.4, 0.6, 10, -1), (8, 2.2, 0.7, 9, 30), (14, 3.8, 0.6, 7, -2), (21, 1.0, 0.7, 7, 33),
                (26, 4.6, 0.6, 6, -1), (1, 2.9, 0.5, 8, 17)], 'c')
    for x, y, r in ((30, 3, 1.6), (33.5, 15, 1.2), (7, 9, 1.3)):
        bubble(P, x, y, r)
    fish(P, 10, 4, 1)
    fish(P, 36, 11, -1)
    fish(P, 4, 20, 1)

    # kelp at the sides
    kelp(P, 1.5, 12, 'g', 0.0)
    kelp(P, 38.5, 16, 'g', 2.0)

    # sandy floor with ripples, a shell and pebbles
    floor = lambda x, y: y > 34.5 + 1.2 * math.sin(x * 0.25 + 1.0)
    fill(P, floor, 's')
    for y0, x0, ln in ((37, 2, 7), (38.5, 26, 9), (36.5, 14, 5)):
        curve(P, lambda t, y0=y0: (t, y0 + 0.5 * math.sin(t * 0.7)), x0, x0 + ln, 'O')
    for x, y, r in ((9.5, 35.5, 1.6), (31.5, 35, 1.8)):
        rock = circle(x, y, r)
        fill(P, rock, 'O')
        put(P, x - 0.5, y - 0.6, 's')

    # coral in two colours rising from the floor
    coral(P, 6, 36, -80, 6, 'p')
    coral(P, 34, 36, -100, 6, 'p')
    coral(P, 15, 37, -95, 4, 'g', 2)
    coral(P, 26, 37, -85, 4, 'g', 2)

    # --- the octopus
    arms = [(-1, 168, 16, -200), (-1, 142, 17, 190), (-1, 118, 16, -200), (-1, 100, 13, 200),
            (1, 80, 13, -200), (1, 62, 16, 200), (1, 38, 17, -190), (1, 12, 16, 200)]
    shapes = []
    for side, deg, ln, curl in arms:
        bx = 20 + side * (2.5 + abs(math.cos(math.radians(deg))) * 3)
        pts = path(bx, 20, deg, ln, curl, wave=side * 22)
        shapes.append((pts, tube(pts, 2.3, 0.75)))
    # back arms first so the front ones overlap them
    for i in (0, 7, 1, 6, 2, 5, 3, 4):
        pts, arm = shapes[i]
        fill(P, arm, 'o')
        outline(P, arm, 'O')
        for j in range(12, len(pts) - 16, 12):
            put(P, pts[j][0], pts[j][1], 's')
    mantle = union(ellipse(20, 12, 7.5, 8.5), ellipse(20, 19, 6.5, 3.5))
    fill(P, mantle, 'o')
    outline(P, mantle, 'O')
    # shading down one side, a highlight, pale spots
    fill(P, both(mantle, lambda x, y: x > 20 + 5.2 * math.sqrt(max(0, 1 - ((y - 11) / 9) ** 2))), 'O')
    curve(P, lambda q: (20 + 5 * math.cos(q), 11 + 6 * math.sin(q)), 3.5, 4.5, 'w')
    for x, y, r in ((20.5, 7, 0.9), (17.5, 10.5, 0.7), (23, 11.5, 0.8), (20, 14, 0.6), (16, 14.5, 0.6), (24.5, 7.5, 0.6)):
        fill(P, circle(x, y, r), 's')
    # eyes with bar pupils
    for ex in (16.8, 23.2):
        fill(P, circle(ex, 17.5, 1.8), 'w')
        line(P, ex - 1, 17.5, ex + 1, 17.5, 'O')
    return P


if __name__ == '__main__':
    import sys
    P = draw(40)
    P.png(sys.argv[1], cell=12)
    print(P.counts())
