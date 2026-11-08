"""Ladybird: a ladybird on a big leaf among pink flowers (40x40)."""
import math
from shapes import *

PAL = {
    'c': '#b3e5fc', 'w': '#ffffff', 'g': '#9ccc65', 'G': '#33691e',
    'r': '#e53935', 'k': '#1b1b1b', 'y': '#ffeb3b', 'p': '#f48fb1',
}


def daisy(P, x, y, r, petal, centre):
    for a in range(0, 360, 45):
        rr = math.radians(a)
        fill(P, ellipse(x + r * 0.9 * math.cos(rr), y + r * 0.9 * math.sin(rr), r * 0.55, r * 0.35, a), petal)
    fill(P, circle(x, y, r * 0.45), centre)


def draw(S):
    P = new(S, 'c', PAL)
    # thin cloud wisps in the sky
    streaks(P, [(3, 0.4, 0.5, 8, 18), (9, 2.0, 0.6, 9, 22), (18, 3.3, 0.5, 7, 0), (29, 1.1, 0.5, 6, 31),
                (12, 4.4, 0.5, 6, 8)], 'w')
    # small leaves and flowers around the edges
    for x0, y0, ln, w, d in ((-2, 2, 11, 3.0, 30), (42, 4, 10, 3.0, 160), (-2, 33, 10, 3.0, -30),
                             (42, 36, 11, 3.0, 205), (16, -2, 8, 2.4, 80), (25, 42, 9, 2.6, -80)):
        leaf(P, x0, y0, ln, w, d, 'g', 'G', side_veins=False)
    for fx, fy, r in ((5, 14, 3.2), (35, 24, 3.0), (31, 5, 2.6), (8, 27, 2.4)):
        daisy(P, fx, fy, r, 'p', 'y')
    for dx, dy in ((14, 6), (23, 3), (37, 15), (3, 21)):
        fill(P, circle(dx, dy, 0.9), 'w')

    # grass along the bottom, a couple of white daisies
    grass(P, 40.5, 'G', step=1.4, height=7, seed=0.9)
    grass(P, 40.5, 'g', x0=0.7, step=1.4, height=5, seed=2.7)
    for fx, fy in ((22, 37), (35, 33.5), (13, 3.5)):
        flower(P, fx, fy, 'w', 'y')
    # the big leaf, pointing up and to the right
    a = math.radians(-40)
    ux, uy = math.cos(a), math.sin(a)
    x0, y0, L, Wd = 4, 40, 44, 12.5
    def big(x, y):
        dx, dy = x - x0, y - y0
        u = dx * ux + dy * uy
        v = -dx * uy + dy * ux
        return 0 <= u <= L and abs(v) <= Wd * math.sin(math.pi * u / L) ** 0.75
    fill(P, big, 'g')
    outline(P, big, 'G')
    curve(P, lambda t: (x0 + ux * t, y0 + uy * t), 0, L * 0.92, 'G')
    for t in range(4, int(L * 0.9), 4):
        for side in (-1, 1):
            bx, by = x0 + ux * t, y0 + uy * t
            curve_in(P, lambda q, bx=bx, by=by, side=side: (bx + ux * q * 0.7 - uy * side * q, by + uy * q * 0.7 + ux * side * q),
                     0, 16, 'G', big)
    # aphids on the leaf
    for ax, ay in ((12, 31), (13.5, 32.5), (30, 13), (31.5, 11.8)):
        put(P, ax, ay, 'y')

    # --- ladybird, walking up the leaf
    cx, cy, ang = 20.5, 21, -40
    shell = ellipse(cx, cy, 10, 8.5, ang)
    head = ellipse(cx + 9.4 * math.cos(math.radians(ang)), cy + 9.4 * math.sin(math.radians(ang)), 3.2, 4.0, ang)
    hx, hy = cx + 9.4 * math.cos(math.radians(ang)), cy + 9.4 * math.sin(math.radians(ang))
    # legs and antennae first, so the body covers their roots
    for t in (-4.5, 0, 4.5):
        for side in (-1, 1):
            px = cx + t * math.cos(math.radians(ang))
            py = cy + t * math.sin(math.radians(ang))
            nx, ny = -math.sin(math.radians(ang)) * side, math.cos(math.radians(ang)) * side
            line(P, px, py, px + nx * 10 + math.cos(math.radians(ang)) * t * 0.2,
                 py + ny * 10 + math.sin(math.radians(ang)) * t * 0.2, 'k')
    for side in (-1, 1):
        d = math.radians(ang + side * 30)
        line(P, hx, hy, hx + 5 * math.cos(d), hy + 5 * math.sin(d), 'k')
        put(P, hx + 5.3 * math.cos(d), hy + 5.3 * math.sin(d), 'k')
    fill(P, head, 'k')
    for side in (-1, 1):
        d = math.radians(ang + side * 60)
        fill(P, circle(hx + 1.6 * math.cos(d), hy + 1.6 * math.sin(d), 0.7), 'w')
    fill(P, shell, 'r')
    # spots, mirrored across the centre line
    c, s_ = math.cos(math.radians(ang)), math.sin(math.radians(ang))
    for u, v, r in ((4.0, 3.6, 1.3), (-1, 5.0, 1.4), (-5.5, 3.0, 1.2)):
        for side in (-1, 1):
            fill(P, both(circle(cx + u * c - side * v * s_, cy + u * s_ + side * v * c, r), shell), 'k')
    # centre line between the wing cases, a black collar, highlight
    line(P, cx - 9.5 * c, cy - 9.5 * s_, cx + 8 * c, cy + 8 * s_, 'k')
    fill(P, both(shell, lambda x, y: (x - cx) * c + (y - cy) * s_ > 8.2), 'k')
    curve(P, lambda q: (cx + 7.5 * math.cos(q) * c - 6.2 * math.sin(q) * s_,
                        cy + 7.5 * math.cos(q) * s_ + 6.2 * math.sin(q) * c), 3.4, 4.0, 'w')
    outline(P, shell, 'k')
    return P


if __name__ == '__main__':
    import sys
    P = draw(40)
    P.png(sys.argv[1], cell=12)
    print(P.counts())
