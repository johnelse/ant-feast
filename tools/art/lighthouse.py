"""Lighthouse: a striped lighthouse on rocks above rolling waves (40x40)."""
import math
from shapes import *

PAL = {
    'c': '#a8d8f0', 'w': '#ffffff', 'k': '#263238', 'y': '#ffe082',
    'r': '#d32f2f', 'B': '#1565c0', 'b': '#42a5f5', 'd': '#8d8d8d',
}


def draw(S):
    P = new(S, 'c', PAL)
    # sky: clouds, wisps, gulls
    cloud(P, 6, 8, 10, 'w')
    cloud(P, 33, 14, 9, 'w')
    streaks(P, [(3, 1.0, 0.5, 9, 26), (19, 2.4, 0.6, 7, 0), (9, 3.3, 0.6, 9, 21), (20, 0.6, 0.6, 9, 25),
                (14, 4.0, 0.5, 6, 0), (23.5, 2.0, 0.5, 7, 3), (1.5, 1.6, 0.4, 8, 3)], 'w')
    for gx, gy in ((29, 5), (34, 8), (8, 15), (25, 13.5), (37, 19), (4, 21)):
        line(P, gx - 1.5, gy - 1, gx, gy, 'k')
        line(P, gx, gy, gx + 1.5, gy - 1, 'k')
    # distant headland on the horizon
    fill(P, lambda x, y: x > 22 and y > 26 - 3.2 * math.sin(math.pi * (x - 22) / 22) ** 0.7 and y <= 26.5, 'd')
    # sea: deep blue with lighter wave streaks and a few foam crests
    fill(P, lambda x, y: y > 26.5, 'B')
    streaks(P, [(28.5, 0.0, 0.5, 12, 22), (30.5, 2.0, 0.6, 10, 30), (32, 1.0, 0.6, 9, -2), (34, 3.0, 0.6, 12, 25),
                (36.5, 4.4, 0.7, 10, 30), (38.5, 2.6, 0.6, 12, 14), (37.5, 0.7, 0.6, 8, -1)], 'b')
    for fx, fy, ln in ((25, 30, 3), (33, 33.5, 2.5), (20, 38, 3), (36, 38.5, 2.5), (29, 36, 2)):
        line(P, fx, fy, fx + ln, fy, 'w')
    # a little boat on the horizon
    fill(P, poly([(27, 30), (33, 30), (32, 31.5), (28, 31.5)]), 'k')
    fill(P, poly([(30.5, 22.5), (30.5, 29.8), (35, 29.8)]), 'w')
    line(P, 30, 22, 30, 30, 'k')

    # rocks under the lighthouse, with cracks
    rocks = union(ellipse(14, 34, 9, 4.5), ellipse(6, 37, 6, 4), ellipse(21, 37.5, 5, 3))
    fill(P, rocks, 'd')
    for x0, y0, x1, y1 in ((9, 32, 10, 35), (10, 35, 8, 37), (19, 32, 21, 35), (4, 36, 6, 39), (15, 35, 16, 38)):
        line(P, x0, y0, x1, y1, 'k')
    outline(P, rocks, 'k', where=lambda x, y, dx, dy: dy == -1 or dx != 0)
    # spray where waves hit the rocks
    for sx, sy in ((23.5, 32), (25, 34.5), (1, 33.5)):
        fill(P, circle(sx, sy, 0.8), 'w')

    # --- lighthouse
    cx, top, bot = 14, 10, 31
    hw = lambda y: 2.6 + (y - top) * 0.09  # half width, wider at the bottom
    tower = lambda x, y: top <= y <= bot and abs(x - cx) <= hw(y)
    fill(P, tower, 'w')
    # red bands, curved a little to show the roundness
    fill(P, both(tower, lambda x, y: int((y - 0.25 * ((x - cx) / hw(y)) ** 2 * -2 - top) // 3.4) % 2 == 1), 'r')
    # shading down the right side
    fill(P, both(tower, lambda x, y: x - cx > hw(y) * 0.55), 'd')
    where(P, ('d',), lambda x, y: tower(x, y) and int((y - top) // 3.4) % 2 == 1, 'r')
    # small windows and a door
    for wy in (14.5, 21):
        fill(P, rect(cx - 0.5, wy, cx + 0.5, wy + 1.5), 'k')
    fill(P, union(rect(cx - 1, 27, cx + 1, 30.5), circle(cx, 27, 1)), 'k')
    outline(P, tower, 'k', where=lambda x, y, dx, dy: dx != 0)
    # gallery with railing, lantern room with light, dome
    fill(P, rect(cx - 4, 9, cx + 4, 10.2), 'k')
    for x in range(int(cx - 4), int(cx + 4), 2):
        put(P, x + 0.5, 8.5, 'k')
    line(P, cx - 4, 7.8, cx + 4, 7.8, 'k')
    fill(P, rect(cx - 2.4, 4.5, cx + 2.4, 8.4), 'y')
    line(P, cx, 4.5, cx, 8.4, 'k')
    fill(P, both(circle(cx, 4.6, 2.9), lambda x, y: y < 4.6), 'r')
    put(P, cx, 1.2, 'k')
    # soft glow round the lantern
    fill(P, lambda x, y: 3.2 < math.hypot((x - cx) / 1.6, y - 6.5) < 3.9 and P.get(int(x * P.s), int(y * P.s)) == 'c', 'y')
    return P


if __name__ == '__main__':
    import sys
    P = draw(40)
    P.png(sys.argv[1], cell=12)
    print(P.counts())
