"""Penguin: an emperor penguin and chick on an ice floe (40x40)."""
import math
from shapes import *

PAL = {
    'c': '#cfe8fc', 'B': '#90caf9', 'w': '#ffffff', 's': '#b0bec5',
    'k': '#1c1c24', 'n': '#37474f', 'y': '#ffca28', 'o': '#fb8c00',
}


def draw(S):
    P = new(S, 'c', PAL)
    # sky: high cirrus wisps, bluer streaks, distant seabirds
    streaks(P, [(4, 0.5, 0.7, 12, -2), (9, 2.2, 0.6, 10, 26), (14, 3.8, 0.6, 8, 3)], 'B')
    streaks(P, [(2, 1.4, 0.5, 9, 13), (7, 3.0, 0.5, 8, 4), (17, 0.6, 0.6, 9, 24), (12, 4.4, 0.5, 7, 13),
                (19.5, 2.0, 0.5, 7, 0)], 'w')
    for bx, by in ((3, 6.5), (8.5, 4.5), (7, 10), (3, 14)):
        line(P, bx - 1, by - 0.7, bx, by, 'k')
        line(P, bx, by, bx + 1, by - 0.7, 'k')
    # low sun with a halo round it
    sx, sy = 32, 8.5
    fill(P, lambda x, y: abs(math.hypot(x - sx, y - sy) - 6.2) < 0.5, 'w')
    fill(P, circle(sx, sy, 2.8), 'y')
    # snowy mountains with shaded right faces
    for mx, mh, mw in ((8, 11, 11), (22, 15, 10), (34, 9, 9)):
        mount = lambda x, y, mx=mx, mh=mh, mw=mw: y >= 25 - mh * (1 - abs(x - mx) / mw) and y <= 26
        fill(P, mount, 'w')
        fill(P, both(mount, lambda x, y, mx=mx: x > mx + 0.3 * (25 - y) * 0.1), 's')
        # streaks of bare rock down the shaded face
        for i, off in enumerate((1.5, 4)):
            top = 25 - mh * (1 - off / mw) + 1.5
            curve_in(P, lambda t, mx=mx, off=off, top=top: (mx + off + t * 0.45, top + t), 0, 6 - i * 2, 'n', mount)
    # dark sea with ripples and drifting ice
    fill(P, lambda x, y: y > 26, 'n')
    streaks(P, [(28, 0.0, 0.4, 8, 28), (31, 2.0, 0.4, 7, -1), (36, 1.0, 0.5, 6, 33), (38.5, 3.0, 0.4, 7, 1)], 'B')
    for ix, iy, iw in ((34, 30, 3.5), (4, 35, 3)):
        fill(P, ellipse(ix, iy, iw, 0.9), 'w')
        line(P, ix - iw + 0.5, iy + 0.7, ix + iw - 0.5, iy + 0.7, 's')
    # ice floe
    floe = poly([(6, 31), (31, 30), (35, 34), (30, 38.5), (9, 39), (4, 35)])
    fill(P, floe, 'w')
    fill(P, both(floe, lambda x, y: y > 36.5 + 0.5 * math.sin(x * 0.7)), 's')
    curve(P, lambda t: (12 + t, 33.5 + 0.8 * math.sin(t * 0.8)), 0, 6, 'B')  # a crack
    outline(P, floe, 'B', where=lambda x, y, dx, dy: dy == -1)

    # --- emperor penguin
    cx = 17
    body = union(ellipse(cx, 22, 6.5, 10), ellipse(cx, 9, 3.8, 3.6))
    fill(P, body, 'k')
    belly = union(ellipse(cx + 0.8, 23, 4.8, 8.6), ellipse(cx + 1.5, 13.5, 2.4, 2.2))
    fill(P, belly, 'w')
    fill(P, both(belly, lambda x, y: x < cx - 1.8), 's')  # shading on the belly
    # neck patch: yellow fading to orange
    fill(P, ellipse(cx + 1.8, 12.8, 1.8, 2.4, -20), 'y')
    fill(P, ellipse(cx + 2.2, 11.8, 1.0, 1.2, -20), 'o')
    # beak, eye
    fill(P, poly([(cx + 3.2, 8.4), (cx + 7, 9.6), (cx + 3.2, 10.2)]), 'k')
    line(P, cx + 3.5, 9.8, cx + 5.8, 9.9, 'o')
    put(P, cx + 1.5, 8.2, 'w')
    # flipper
    fill(P, ellipse(cx - 4.2, 23, 1.8, 6.5, 12), 'n')
    outline(P, ellipse(cx - 4.2, 23, 1.8, 6.5, 12), 'k')
    # feet
    fill(P, ellipse(cx - 1.5, 32.4, 1.8, 0.8), 'o')
    fill(P, ellipse(cx + 3, 32.4, 1.8, 0.8), 'o')

    # --- chick: fluffy grey with a black-and-white head
    hx = 26.5
    chick = union(ellipse(hx, 28, 3.2, 3.6), circle(hx, 22.8, 2.4))
    fill(P, chick, 's')
    for a in range(0, 360, 40):  # fluffy edge
        r = math.radians(a)
        put(P, hx + 3.2 * math.cos(r), 28 + 3.6 * math.sin(r), 's')
    fill(P, both(circle(hx, 22.8, 2.4), lambda x, y: y < 22.4 or x < hx - 1.5), 'k')
    fill(P, ellipse(hx + 0.6, 23.4, 1.4, 1.0), 'w')
    put(P, hx + 0.7, 23, 'k')
    put(P, hx - 2.4, 22.8, 'k')
    line(P, hx - 3.4, 23.2, hx - 2.4, 23.2, 'k')
    fill(P, ellipse(hx - 0.8, 31.6, 1.0, 0.5), 'o')
    fill(P, ellipse(hx + 1.2, 31.6, 1.0, 0.5), 'o')
    return P


if __name__ == '__main__':
    import sys
    P = draw(40)
    P.png(sys.argv[1], cell=12)
    print(P.counts())
