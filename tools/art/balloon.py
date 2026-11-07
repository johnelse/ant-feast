"""Balloon: a hot-air balloon over patchwork fields (40x40)."""
import math
from shapes import *

PAL = {
    'c': '#9fd8f5', 'w': '#ffffff', 'g': '#66bb6a', 'y': '#fdd835',
    'r': '#e53935', 'B': '#3949ab', 'T': '#4e342e', 't': '#a1887f',
}


def small_balloon(P, x, y, r, k1, k2):
    b = union(circle(x, y, r), poly([(x - r * 0.8, y + r * 0.5), (x + r * 0.8, y + r * 0.5), (x, y + r * 1.6)]))
    fill(P, b, k1)
    line(P, x, y - r, x, y + r * 1.5, k2)
    put(P, x, y + r * 1.6 + 0.6, 'T')


def draw(S):
    P = new(S, 'c', PAL)
    # sky: clouds, wisps, birds, distant balloons
    cloud(P, 6, 9, 10, 'w')
    cloud(P, 34, 6, 9, 'w')
    cloud(P, 31, 22, 8, 'w')
    streaks(P, [(15, 0.8, 0.6, 7, 0), (3, 2.0, 0.5, 8, 14), (27, 3.5, 0.6, 6, 2), (11, 1.4, 0.7, 9, 30),
                (19, 4.2, 0.6, 8, 31), (22, 2.6, 0.6, 7, -1), (1.5, 0.3, 0.4, 7, 24)], 'w')
    for bx, by in ((4, 18), (7, 16.5), (37, 13), (34, 16), (10, 3.5), (13, 5)):
        line(P, bx - 1, by - 0.7, bx, by, 'T')
        line(P, bx, by, bx + 1, by - 0.7, 'T')
    small_balloon(P, 4.5, 24, 2.0, 'B', 'y')
    small_balloon(P, 36, 27.5, 1.8, 'y', 'r')
    small_balloon(P, 36, 3, 1.7, 'r', 'y')
    small_balloon(P, 10, 27.5, 1.6, 'y', 'B')
    small_balloon(P, 35.5, 19.5, 1.6, 'B', 'r')
    # land: hills with a patchwork of fields between hedgerows, a winding road
    hill = lambda x: 31.5 + 2.0 * math.sin(x * 0.17 + 0.6) + 0.7 * math.sin(x * 0.5)
    rows = lambda x, y: int((y - 0.6 * math.sin(x * 0.3) - 31) // 3.2)
    cols = lambda x, y: int((x - (y - 31) * 0.5) // 9)
    fill(P, lambda x, y: y > hill(x), 'g')
    fill(P, lambda x, y: y > hill(x) + 0.5 and (rows(x, y) + cols(x, y)) % 2 == 1, 'y')
    for y0 in (34.2, 37.4):
        curve(P, lambda t, y0=y0: (t, y0 + 0.6 * math.sin(t * 0.3)), -1, 41, 'T')
    for x0 in (9, 18, 27, 36):
        curve(P, lambda t, x0=x0: (x0 + (t - 31) * 0.5, t), hill(x0) + 0.6, 41, 'T')
    curve(P, lambda t: (13 + 3 * math.sin(t * 0.4), 31 + t), 0.5, 10, 't')
    # --- main balloon
    cx, cy, R = 20, 12, 11
    env = union(circle(cx, cy, R), poly([(cx - R * 0.86, cy + R * 0.5), (cx + R * 0.86, cy + R * 0.5),
                                          (cx + 3, cy + R + 3.6), (cx - 3, cy + R + 3.6)]))
    fill(P, env, 'r')
    # vertical panels: meridians curving with the envelope, alternating colours
    def half_width(y):
        if y < cy + R * 0.5:
            return math.sqrt(max(0.01, R * R - (y - cy) ** 2))
        t = (y - cy - R * 0.5) / (R * 0.5 + 3.6)
        return R * 0.86 * (1 - t) + 3 * t
    def panel(x, y):
        dx = (x - cx) / half_width(y)
        return math.floor((math.asin(max(-1, min(1, dx))) / math.pi + 0.5) * 7)
    fill(P, both(env, lambda x, y: panel(x, y) % 2 == 1), 'y')
    # trim bands: a blue band round the middle and above the skirt
    fill(P, both(env, lambda x, y: abs(y - (cy + 2.5 + 0.06 * (x - cx) ** 2 * 0.3)) < 0.8), 'B')
    fill(P, both(env, lambda x, y: y > cy + R + 1.8), 'B')
    # highlight
    curve(P, lambda a: (cx + R * 0.72 * math.cos(a), cy + R * 0.72 * math.sin(a)), 3.5, 4.3, 'w')
    outline(P, env, 'T')
    # ropes and woven basket
    for x0, x1 in ((cx - 3, cx - 2.5), (cx + 3, cx + 2.5)):
        line(P, x0, cy + R + 3.6, x1, cy + R + 5.5, 'T')
    basket = rect(cx - 3, cy + R + 5.5, cx + 3, cy + R + 9)
    fill(P, basket, 't')
    for yy in range(int(cy + R + 6), int(cy + R + 9), 2):
        for xx in range(int(cx - 3), int(cx + 3)):
            if (xx + yy // 2) % 2:
                put(P, xx + 0.5, yy + 0.5, 'T')
    outline(P, basket, 'T')
    return P


if __name__ == '__main__':
    import sys
    P = draw(40)
    P.png(sys.argv[1], cell=12)
    print(P.counts())
