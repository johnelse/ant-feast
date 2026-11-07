"""Snail: a snail crawling along a big leaf, with dew drops (40x40)."""
import math
from shapes import *

PAL = {
    'c': '#b3e5fc', 'w': '#ffffff', 'y': '#ffd54f', 'g': '#8bc34a',
    'G': '#558b2f', 's': '#d7c29e', 'd': '#5d4037', 'o': '#e08e2b',
}


def draw(S):
    P = new(S, 'c', PAL)
    # garden behind: big leaves at the edges, a few raindrops
    for x0, y0, ln, w, d in ((-3, 6, 14, 4.0, 15), (43, 3, 15, 4.2, 165), (30, -2, 11, 3.2, 110),
                             (6, -2, 10, 3.0, 70), (-2, 20, 10, 3.0, -15), (42, 17, 11, 3.2, 195)):
        leaf(P, x0, y0, ln, w, d, 'G', 'g', side_veins=False)
    for rx, ry in ((13, 11), (28, 13), (35, 25), (20, 4), (24, 7.5)):
        fill(P, union(circle(rx, ry, 0.9), poly([(rx - 0.8, ry), (rx + 0.8, ry), (rx, ry - 2)])), 'w')

    # grass and daisies along the bottom
    grass(P, 40.5, 'G', step=1.4, height=7, seed=0.5)
    grass(P, 40.5, 'g', x0=0.7, step=1.4, height=5, seed=2.2)
    for fx, fy in ((4, 33), (15, 36.5), (27, 35.5), (36, 32)):
        line(P, fx, fy, fx + 0.4, 40, 'G')
        flower(P, fx, fy, 'w', 'y')
    # the big leaf, lying diagonally across the bottom
    base = lambda x: 27 + (20 - x) * 0.18
    big = lambda x, y: -2 < x < 42 and abs(y - base(x)) < 7.5 * math.sin(math.pi * (x + 2) / 44) ** 0.6 + 0.5
    fill(P, big, 'g')
    outline(P, big, 'G')
    curve(P, lambda t: (t, base(t)), -2, 42, 'G')
    for x0 in range(3, 40, 7):
        for side in (-1, 1):
            curve_in(P, lambda t, x0=x0, side=side: (x0 + t, base(x0) + side * t * 0.8 - t * 0.18), 0, 6, 'G', big)
    # nibbled holes behind the snail, outlined in the darker green
    for hx, hy, hr in ((6, 27.5, 1.3), (9.5, 25, 1.0), (4, 31, 0.9), (13, 31.5, 1.1)):
        hole = both(circle(hx, hy, hr), big)
        fill(P, hole, 'c')
        fill(P, both(lambda x, y, hx=hx, hy=hy, hr=hr: hr <= math.hypot(x - hx, y - hy) < hr + 0.7, big), 'G')
    # dew drops on the leaf
    for dx, dy in ((5, 34), (33, 22), (24, 31.5), (17, 33.5), (36, 27), (28, 26.5), (10, 35.5), (2.5, 24.5)):
        fill(P, circle(dx, dy, 1.1), 'c')
        put(P, dx - 0.4, dy - 0.4, 'w')
    # silvery trail behind the snail
    curve(P, lambda t: (t, base(t) + 2.2 + 0.4 * math.sin(t * 0.6)), 0, 15, 'w')

    # --- snail, crawling right
    # body: long foot with a raised head and eye stalks
    foot = union(ellipse(23, 27.2, 9, 2.2, -10), ellipse(31, 23.5, 2.6, 3.2, -25))
    fill(P, foot, 'y')
    outline(P, foot, 'd', where=lambda x, y, dx, dy: dy != -1 or x > 29)
    for ex, ey in ((30.5, 15.5), (34, 16.5)):
        line(P, 31.2, 21.5, ex, ey, 'd')
        line(P, 31.7, 21.5, ex + 0.5, ey, 'y')
        fill(P, circle(ex, ey, 1.0), 'd')
    put(P, 33.5, 24.5, 'd')  # smile
    # shell: spiral line with growth ridges cutting it into chambers
    scx, scy, R = 20, 17.5, 8.5
    shell = circle(scx, scy, R)
    fill(P, shell, 'o')
    # whorls: alternate orange and cream between turns of a dark spiral line
    def spiral_r(a):
        return R * 0.97 * math.exp(-0.17 * a)
    def turn_of(x, y):
        a0 = math.atan2(y - scy, x - scx) % (2 * math.pi)
        r = math.hypot(x - scx, y - scy)
        for turn in range(5):
            a = a0 + 2 * math.pi * turn
            if spiral_r(a + 2 * math.pi) <= r <= spiral_r(a):
                return turn
        return 9
    def chamber(x, y):
        a = math.atan2(y - scy, x - scx) % (2 * math.pi)
        return turn_of(x, y) + int(a / (math.pi / 4))
    fill(P, both(shell, lambda x, y: chamber(x, y) % 2 == 1), 's')
    curve(P, lambda a: (scx + spiral_r(a) * math.cos(a), scy + spiral_r(a) * math.sin(a)), 0, 2 * math.pi * 2.6, 'd')
    # growth ridges right across the whorls, cutting them into chambers
    for a in range(22, 360, 45):
        r = math.radians(a)
        line(P, scx + (R - 0.6) * math.cos(r), scy + (R - 0.6) * math.sin(r),
             scx + R * 0.42 * math.cos(r), scy + R * 0.42 * math.sin(r), 'd')
    put(P, scx - 4, scy - 5, 'w')
    outline(P, shell, 'd')
    return P


if __name__ == '__main__':
    import sys
    P = draw(40)
    P.png(sys.argv[1], cell=12)
    print(P.counts())
