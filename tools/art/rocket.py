"""Rocket: a rocket climbing past a ringed planet and a moon (40x40)."""
import math
from shapes import *

PAL = {
    'n': '#0d1b2a', 'w': '#eceff1', 'y': '#ffeb3b', 'o': '#ff9800',
    'r': '#e53935', 'B': '#1e88e5', 'c': '#80deea', 'k': '#37474f',
}


def draw(S):
    P = new(S, 'n', PAL)
    # ringed planet, top right: bands, ring passing in front and behind
    px, py, pr = 31, 9, 6
    planet = circle(px, py, pr)
    ring = lambda x, y: 0.75 < math.hypot((x - px) / 2.1, (y - py - (x - px) * -0.25) / 0.6) / 4.6 < 1.0
    fill(P, both(ring, lambda x, y: y < py - (x - px) * 0.25), 'c')
    fill(P, planet, 'B')
    fill(P, both(planet, lambda x, y: math.sin((y - py) * 1.1 + (x - px) * 0.25) > 0.55), 'c')
    fill(P, both(planet, lambda x, y: (x - px) + (y - py) > pr * 0.7), 'k')
    fill(P, both(ring, lambda x, y: y >= py - (x - px) * 0.25), 'c')
    # moon, bottom left, with craters
    moon = circle(4, 34, 6.5)
    fill(P, moon, 'k')
    fill(P, both(moon, lambda x, y: x - 4 < -1.5 or y - 34 < -2), 'w')
    for mx, my, mr in ((2, 31, 1.3), (5.5, 36, 1.6), (0.5, 37, 1.0), (7, 30.5, 0.8)):
        outline(P, both(circle(mx, my, mr), moon), 'k')
    # comet with a tail
    fill(P, circle(8, 6, 1.0), 'w')
    for i in range(6):
        put(P, 9.2 + i * 0.9, 6.6 + i * 0.5, 'c' if i < 3 else 'B')
    # stars: a few bright crosses and some single points
    for sx, sy, big in ((16, 3, True), (3, 14, False), (23, 17, False), (37, 21, True), (13, 23, False),
                        (36, 30, False), (20, 36, True), (29, 38, False), (2, 22, False), (15, 13, False)):
        put(P, sx, sy, 'y' if big else 'w')
        if big:
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                put(P, sx + dx, sy + dy, 'w')

    # nebula wisps drifting across the dark
    streaks(P, [(18, 0.3, 1.0, 12, -2), (26, 2.0, 1.1, 10, 28), (13, 3.6, 0.8, 9, 0), (31, 1.1, 0.9, 9, 22),
                (3, 2.4, 0.7, 9, 22), (24, 4.4, 0.9, 7, 1), (36, 0.8, 0.8, 8, 28), (8, 1.9, 0.6, 7, -2)], 'k')
    # asteroids: lumpy grey rocks with a lit edge and a crater
    for ax, ay, ar in ((33.5, 34, 2.2), (6, 18.5, 1.6), (36, 23.5, 1.3), (11.5, 3.5, 1.2)):
        rock = union(circle(ax, ay, ar), circle(ax + ar * 0.6, ay - ar * 0.3, ar * 0.7))
        fill(P, rock, 'k')
        fill(P, both(rock, lambda x, y, ax=ax, ay=ay: (x - ax) + (y - ay) < -ar * 0.4), 'w')
        put(P, ax + 0.3, ay + 0.3, 'n')
    # a little satellite
    fill(P, rect(6, 11.5, 8, 13.5), 'w')
    fill(P, rect(3, 12, 5.6, 13), 'B')
    fill(P, rect(8.4, 12, 11, 13), 'B')
    put(P, 7, 10.8, 'y')

    # --- rocket, upright, climbing
    cx = 20
    def half(y):  # body half-width down the rocket
        if y < 5:
            return 0
        if y < 13:
            return 4.6 * math.sqrt((y - 5) / 8)
        return 4.6 if y < 27 else 4.6 - (y - 27) * 0.5
    body = lambda x, y: 5 <= y <= 30 and abs(x - cx) <= half(y)
    fins = union(poly([(cx - 4, 18), (cx - 10, 27), (cx - 10, 32.5), (cx - 4, 28.5)]),
                 poly([(cx + 4, 18), (cx + 10, 27), (cx + 10, 32.5), (cx + 4, 28.5)]))
    # flame: layers getting brighter towards the nozzle, smoke puffs either side
    for k, top, bot, w in (('r', 30, 40, 3.6), ('o', 30, 38, 2.6), ('y', 30, 35, 1.5)):
        fill(P, lambda x, y, top=top, bot=bot, w=w: top <= y <= bot and abs(x - cx) <= w * (1 - (y - top) / (bot - top + 0.5)) ** 0.6, k)
    for sx, sy, r, k in ((cx - 6, 38, 2.0, 'w'), (cx + 6.5, 37.5, 1.8, 'w'), (cx - 9.5, 39.5, 1.4, 'k'), (cx + 10, 39.5, 1.3, 'k')):
        fill(P, circle(sx, sy, r), k)
    fill(P, fins, 'r')
    fill(P, both(fins, lambda x, y: y > 30.5), 'k')
    fill(P, body, 'w')
    # nose cone, band near the base, nozzle
    fill(P, lambda x, y: body(x, y) and y < 11.5, 'r')
    fill(P, lambda x, y: body(x, y) and 24 <= y < 25.4, 'r')
    fill(P, rect(cx - 2.6, 30, cx + 2.6, 31.3), 'k')
    # shading down the right side
    fill(P, lambda x, y: body(x, y) and x > cx + half(y) * 0.5 and 11.5 <= y < 24, 'c')
    # porthole with a rim and a glint, rivets
    fill(P, circle(cx, 16.5, 3.0), 'k')
    fill(P, circle(cx, 16.5, 2.2), 'B')
    fill(P, circle(cx - 0.8, 15.7, 0.7), 'c')
    for ry in (12.5, 21.5):
        for rx in (-2.5, 2.5):
            put(P, cx + rx, ry, 'k')
    outline(P, union(body, fins), 'k')
    return P


if __name__ == '__main__':
    import sys
    P = draw(40)
    P.png(sys.argv[1], cell=12)
    print(P.counts())
