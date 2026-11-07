"""House: a cottage with a tiled roof, flower boxes and a picket fence (40x40)."""
import math
from shapes import *

PAL = {
    'c': '#bbdefb', 'W': '#fff3d6', 'R': '#c62828', 'r': '#7f1d1d',
    'b': '#4fc3f7', 'd': '#6d4c41', 'g': '#7cb342', 'y': '#ffd54f',
}


def draw(S):
    P = new(S, 'c', PAL)
    # sky: sun with short rays, clouds
    fill(P, circle(14, 4.5, 2.6), 'y')
    for a in range(0, 360, 45):
        r = math.radians(a + 22)
        line(P, 14 + 3.8 * math.cos(r), 4.5 + 3.8 * math.sin(r), 14 + 5 * math.cos(r), 4.5 + 5 * math.sin(r), 'y')
    cloud(P, 31, 8, 9, 'W')
    streaks(P, [(13, 1.0, 0.6, 7, 31), (3, 2.5, 0.5, 6, 15)], 'W')
    # big trees either side: leafy crowns with branches and fruit
    for tx, side in ((1.5, 1), (38.5, -1)):
        fill(P, rect(tx - 1.2, 16, tx + 1.2, 33), 'd')
        crown = union(circle(tx, 9, 7), circle(tx + side * 3.5, 15, 5.5), circle(tx, 20, 5))
        fill(P, crown, 'g')
        for x1, y1 in ((tx + side * 5, 12), (tx + side * 2.5, 7), (tx + side * 6, 18)):
            line(P, tx, 22, x1, y1, 'd')
        for bx, by in ((tx + side * 4, 9), (tx + side * 1.5, 16), (tx + side * 5.5, 18), (tx - side * 1, 12)):
            put(P, bx, by, 'R')
        outline(P, crown, 'd', where=lambda x, y, dx, dy: dy == 1)
    # grass
    fill(P, lambda x, y: y > 31 + 0.5 * math.sin(x * 0.4), 'g')

    # walls
    walls = rect(8, 19, 32, 33)
    fill(P, walls, 'W')
    for x in (8.5, 17, 23, 31.5):
        line(P, x, 19, x, 33, 'd')
    for y in (21.2, 29.8):
        line(P, 8, y, 32, y, 'd')
    for x0, x1 in ((8.5, 10.3), (31.5, 29.7)):
        line(P, x0, 29.8, x1, 32.5, 'd')
        line(P, x0, 21.2, x1, 19.2, 'd')
    outline(P, walls, 'd')
    # roof: triangle of tiles, a dark line every third row with staggered joints
    roof = poly([(5, 20.5), (20, 6.5), (35, 20.5)])
    fill(P, roof, 'R')
    for i, row in enumerate(range(10, 21, 3)):
        curve_in(P, lambda t, row=row: (t, row + 0.5), 4, 36, 'r', roof)
        for x in range(0, 40, 4):
            xx = x + (2 if i % 2 else 0)
            curve_in(P, lambda t, xx=xx: (xx + 0.5, t), row - 1.5, row - 0.5, 'r', roof)
    outline(P, roof, 'r')
    # chimney standing above the roof, with smoke
    chim = rect(25, 7, 28, 14)
    fill(P, minus(chim, lambda x, y: roof(x, y) and y > 12), 'R')
    fill(P, rect(24.5, 6, 28.5, 7.2), 'r')
    for sx, sy, sr in ((26.5, 4.0, 0.9), (25.5, 2.3, 1.1), (23.5, 1.0, 1.2)):
        fill(P, circle(sx, sy, sr), 'W')
    # windows: glass, cream cross frame, reflection, flower box beneath
    for wx in (10.5, 23.5):
        win = rect(wx, 21.5, wx + 6, 27.5)
        fill(P, win, 'b')
        line(P, wx + 3, 21.5, wx + 3, 27.5, 'W')
        line(P, wx, 24.5, wx + 6, 24.5, 'W')
        put(P, wx + 1, 22.5, 'W')
        outline(P, win, 'd')
        fill(P, rect(wx - 0.5, 27.5, wx + 6.5, 29), 'd')
        for i, fx in enumerate(range(int(wx), int(wx) + 7)):
            put(P, fx + 0.5, 27, 'R' if i % 2 else 'y')
    # ivy climbing the left wall, with roses
    ivy = lambda t: (9.5 + 1.5 * math.sin(t * 0.6), 33 - t)
    curve(P, ivy, 0, 13, 'g')
    for t in range(1, 13, 2):
        x, y = ivy(t)
        side = 1 if (t // 2) % 2 else -1
        put(P, x + side, y, 'g')
        put(P, x + side, y - 1, 'g')
    for t in (3, 8, 12):
        x, y = ivy(t)
        put(P, x, y, 'R')
    # door with a round top, knob
    door = union(rect(18, 26, 22, 33), circle(20, 26, 2))
    fill(P, door, 'd')
    line(P, 20, 25, 20, 33, 'r')
    put(P, 21.5, 29.5, 'y')
    # path: stepping stones curving down from the door
    for px, py in ((20, 34.2), (19, 36.2), (20.5, 38.2), (19.5, 40.2)):
        fill(P, ellipse(px, py, 1.8, 0.7), 'W')
    # white picket fence across the garden, gap for the path
    for x in range(1, 40, 2):
        if 16 <= x <= 23:
            continue
        fill(P, rect(x, 34.5, x + 1, 38.5), 'W')
        put(P, x + 0.5, 34, 'W')
    for y0 in (35.5, 37.5):
        fill(P, minus(rect(0, y0, 40, y0 + 0.9), rect(16, 0, 24, 40)), 'W')
    # flowers in the grass behind the fence
    for fx, fy in ((4, 32.5), (13, 33), (28, 33), (35, 32.5)):
        flower(P, fx, fy, 'y', 'R')
    return P


if __name__ == '__main__':
    import sys
    P = draw(40)
    P.png(sys.argv[1], cell=12)
    print(P.counts())
