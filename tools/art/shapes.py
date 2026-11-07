"""Shared shapes for the drawing scripts.

Coordinates are in design units: pictures are designed on a 40x40 grid, and
P.s = size / 40 scales them, so the same script can draw at other sizes.
A "shape" is a predicate inside(x, y) over design coordinates (cell centres).
"""
import math
from pix import Pic


def new(S, bg, palette):
    P = Pic(S, S, bg, palette)
    P.s = S / 40
    return P


# --- shapes (predicates) ---------------------------------------------------

def rot(x, y, cx, cy, deg):
    a = math.radians(deg)
    dx, dy = x - cx, y - cy
    return dx * math.cos(a) + dy * math.sin(a), -dx * math.sin(a) + dy * math.cos(a)


def ellipse(cx, cy, rx, ry, deg=0):
    def inside(x, y):
        u, v = rot(x, y, cx, cy, deg)
        return (u / rx) ** 2 + (v / ry) ** 2 <= 1
    return inside


def circle(cx, cy, r):
    return lambda x, y: (x - cx) ** 2 + (y - cy) ** 2 <= r * r


def rect(x0, y0, x1, y1):
    return lambda x, y: x0 <= x < x1 and y0 <= y < y1


def poly(points):
    """Point-in-polygon (even-odd)."""
    def inside(x, y):
        c = False
        n = len(points)
        for i in range(n):
            x1, y1 = points[i]
            x2, y2 = points[(i + 1) % n]
            if (y1 > y) != (y2 > y) and x < x1 + (y - y1) * (x2 - x1) / (y2 - y1):
                c = not c
        return c
    return inside


def union(*shapes):
    return lambda x, y: any(f(x, y) for f in shapes)


def minus(a, b):
    return lambda x, y: a(x, y) and not b(x, y)


def both(a, b):
    return lambda x, y: a(x, y) and b(x, y)


# --- drawing ---------------------------------------------------------------

def fill(P, shape, k):
    s = P.s
    P.fill(lambda x, y: shape(x / s, y / s), k)


def outline(P, shape, k, where=None):
    s = P.s
    P.outline(lambda x, y: shape(x / s, y / s), k, where)


def put(P, x, y, k):
    """Colour the cell containing design point (x, y)."""
    P.set(x * P.s - 0.5, y * P.s - 0.5, k)


def line(P, x0, y0, x1, y1, k):
    s = P.s
    P.line(x0 * s, y0 * s, x1 * s, y1 * s, k)


def curve(P, fn, t0, t1, k, steps=400):
    s = P.s
    P.curve(lambda t: tuple(v * s for v in fn(t)), t0, t1, k, steps)


def where(P, keys, shape, k):
    """Recolour cells of the given keys inside shape (e.g. shading only on the body)."""
    s = P.s
    for y in range(P.h):
        for x in range(P.w):
            if P.g[y][x] in keys and shape((x + .5) / s, (y + .5) / s):
                P.g[y][x] = k


def despeckle(P, k, bg):
    """Turn cells of k with no 4-neighbour of k into bg (lone pixels read as noise)."""
    lone = [(x, y) for y in range(P.h) for x in range(P.w) if P.g[y][x] == k and
            not any(P.get(x + dx, y + dy) == k for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))]
    for x, y in lone:
        P.g[y][x] = bg


# --- scenery ---------------------------------------------------------------

def leaf(P, x0, y0, length, width, deg, k, vein=None, side_veins=True):
    """A pointed leaf from its stalk end, with an optional midrib and side veins."""
    a = math.radians(deg)
    ux, uy = math.cos(a), math.sin(a)
    def inside(x, y):
        dx, dy = x - x0, y - y0
        u = dx * ux + dy * uy
        v = -dx * uy + dy * ux
        return 0 <= u <= length and abs(v) <= width * math.sin(math.pi * u / length) ** 0.8
    fill(P, inside, k)
    if vein:
        curve(P, lambda t: (x0 + ux * t, y0 + uy * t), 0.5, length * 0.85, vein)
        if side_veins and width >= 3:
            for t in range(3, int(length * 0.7), 4):
                for side in (-1, 1):
                    bx, by = x0 + ux * t, y0 + uy * t
                    line(P, bx, by, bx + ux * 1.2 - uy * side * width * 0.7,
                         by + uy * 1.2 + ux * side * width * 0.7, vein)


def fern(P, x0, y0, length, deg, bend, k):
    """An arching fern frond: a stem with paired leaflets that taper."""
    def stem(t):
        x, y = x0, y0
        n = int(t * 4) + 1
        d = math.radians(deg)
        for i in range(n):
            d = math.radians(deg + bend * (i / 4) / length)
            x += math.cos(d) / 4
            y += math.sin(d) / 4
        return x, y, d
    curve(P, lambda t: stem(t)[:2], 0, length, k)
    for t in range(1, int(length), 2):
        x, y, d = stem(t)
        ln = 3.0 * (1 - t / length) + 0.8
        for side in (-1, 1):
            line(P, x, y, x + math.cos(d + side * 0.95) * ln, y + math.sin(d + side * 0.95) * ln, k)


def streaks(P, specs, k):
    """Wavy horizontal streaks (water currents, wisps of cloud, wind).
    specs: (y, phase, amplitude, length, x_start)."""
    for y0, ph, amp, ln, x0 in specs:
        curve(P, lambda t: (t, y0 + amp * math.sin(t * 0.33 + ph)), x0, x0 + ln, k)
        curve(P, lambda t: (t, y0 + 1 + amp * math.sin(t * 0.33 + ph)), x0 + 2, x0 + ln - 3, k)


def cloud(P, cx, cy, w, k, edge=None):
    """A puffy cloud: a flat base with bumps on top. Optional edge colour underneath."""
    bumps = []
    n = max(2, int(w / 3))
    for i in range(n):
        bx = cx - w / 2 + (i + 0.5) * w / n
        r = 1.6 + 1.2 * math.sin(i * 2.1 + cx) ** 2 + (1.0 if 0 < i < n - 1 else 0)
        bumps.append(circle(bx, cy - r * 0.4, r))
    base = rect(cx - w / 2, cy - 1, cx + w / 2, cy + 1.2)
    shape = union(base, *bumps)
    fill(P, shape, k)
    if edge:
        outline(P, shape, edge, where=lambda x, y, dx, dy: dy == 1)
    return shape


def grass(P, y0, k, x0=0, x1=40, step=1.5, height=3.0, seed=0.0):
    """Grass blades rising from y0, leaning a little, varying in height."""
    x = x0
    i = 0
    while x < x1:
        h = height * (0.6 + 0.4 * math.sin(i * 1.7 + seed) ** 2)
        lean = 0.6 * math.sin(i * 0.9 + seed)
        line(P, x, y0, x + lean, y0 - h, k)
        x += step
        i += 1


def flower(P, x, y, petal, centre):
    for dx, dy in ((0, -1), (-1, 0), (1, 0), (0, 1)):
        put(P, x + dx, y + dy, petal)
    put(P, x, y, centre)


def curve_in(P, fn, t0, t1, k, shape, steps=400):
    """Like curve(), but only colours cells whose centres are inside shape."""
    s = P.s
    for i in range(steps + 1):
        x, y = fn(t0 + (t1 - t0) * i / steps)
        cx, cy = math.floor(x * s), math.floor(y * s)
        if shape((cx + 0.5) / s, (cy + 0.5) / s):
            P.set(cx, cy, k)
