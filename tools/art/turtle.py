"""Turtle: a sea turtle swimming over sea grass (40x40)."""
import math
from shapes import *

PAL = {
    'a': '#1e88a8', 'u': '#a7e3f0', 's': '#e6cf9a', 'd': '#4e3b1f',
    'o': '#b8862b', 'y': '#e3c46a', 'g': '#7cb342', 'G': '#33691e',
}


def dapple(P, shape, k, step=2.2, r=0.55, phase=0.0):
    """Regular scale spots inside a shape (staggered rows)."""
    for j in range(int(40 / step) + 1):
        for i in range(int(40 / step) + 1):
            x = i * step + (step / 2 if j % 2 else 0) + phase
            y = j * step
            if shape(x, y):
                fill(P, both(circle(x, y, r + 0.2), shape), k)


def draw(S):
    P = new(S, 'a', PAL)
    # sunlit surface and current streaks
    fill(P, lambda x, y: y < 2 + 0.7 * math.sin(x * 0.5 + 1), 'u')
    streaks(P, [(6, 0.0, 1.1, 13, -2), (9, 2.6, 0.9, 11, 27), (31, 1.2, 1.0, 12, 22), (28, 4.1, 1.2, 10, -1),
                (15, 3.0, 0.8, 8, 32), (4, 5.0, 0.7, 9, 14)], 'u')
    # seabed: sand ripples, pebbles, sea grass
    fill(P, lambda x, y: y > 35 + 1.0 * math.sin(x * 0.28), 's')
    for x0 in range(-2, 40, 7):
        curve(P, lambda t, x0=x0: (x0 + t, 37.5 + 0.6 * math.sin(t * 0.9) + 0.03 * x0), 0, 4, 'y')
    for px, py in ((6, 38.5), (17, 39), (30, 38), (36, 39.2)):
        fill(P, ellipse(px, py, 1.1, 0.6), 'd')
    for sx, h, ph, k in ((1.5, 13, 0.0, 'g'), (3.5, 9, 1.7, 'G'), (11, 7, 2.5, 'g'), (25, 8, 0.9, 'G'),
                         (35, 12, 2.0, 'g'), (37.5, 9, 3.3, 'G'), (32, 6, 1.1, 'g')):
        curve(P, lambda t, sx=sx, ph=ph, h=h: (sx + 1.3 * math.sin(t * 0.5 + ph) * (t / h), 38 - t), 0, h, k)
    # tall kelp at both sides, reaching up towards the light, with leafy blades
    for kx, h, ph, k, blade in ((1.5, 33, 0.0, 'G', 'g'), (38.8, 30, 2.6, 'G', 'g')):
        stalk = lambda t, kx=kx, ph=ph: (kx + 1.2 * math.sin(t * 0.3 + ph), 39 - t)
        curve(P, stalk, 0, h, k)
        for t in range(4, h, 4):
            x, y = stalk(t)
            side = 1 if (t // 4) % 2 else -1
            leaf(P, x, y, 3.5, 1.0, -90 + side * 55, blade)
    # bubbles
    for bx, by, r in ((33, 4, 1.0), (35, 8, 1.2), (32.5, 12.5, 0.9), (6, 24, 1.0)):
        fill(P, lambda x, y, bx=bx, by=by, r=r: abs(math.hypot(x - bx, y - by) - r) < 0.55, 'u')
    # small fish
    for fx, fy, k in ((10, 6, 'y'), (15, 4.5, 's'), (13, 9.5, 'y'), (23, 33, 's')):
        fish = union(ellipse(fx, fy, 2.4, 1.2), poly([(fx - 1.8, fy), (fx - 3.8, fy - 1.5), (fx - 3.8, fy + 1.5)]))
        fill(P, fish, k)
        line(P, fx - 0.3, fy - 1, fx - 0.3, fy + 1, 'o')
        put(P, fx + 1.3, fy - 0.3, 'd')

    # --- turtle, swimming up and to the right
    cx, cy, ang = 20, 20, -15
    # flippers: big front ones swept back, small rear ones
    flips = (ellipse(27, 11, 8, 2.6, -40), ellipse(28.5, 28, 7, 2.4, 35),
             ellipse(11.5, 14.5, 3.6, 1.7, 30), ellipse(12, 26, 3.6, 1.7, -40))
    for f in flips:
        fill(P, f, 'g')
        dapple(P, f, 'G', step=2.0, r=0.4)
        outline(P, f, 'G')
    # head and neck
    head = union(ellipse(34, 17, 4.0, 3.0, ang), ellipse(30.5, 18.2, 2.8, 2.3, ang))
    fill(P, head, 'g')
    dapple(P, head, 'G', step=1.8, r=0.35, phase=0.6)
    outline(P, head, 'G')
    put(P, 35.3, 16.0, 'd')
    put(P, 36.5, 17.8, 'd')
    # shell: plates in a ring round three central plates
    shell = ellipse(cx, cy, 11.5, 8.5, ang)
    fill(P, shell, 'o')
    inner = ellipse(cx, cy, 7.2, 4.8, ang)
    outline(P, inner, 'd')
    for a in range(0, 360, 36):
        r = math.radians(a)
        u, v = 7.2 * math.cos(r), 4.8 * math.sin(r)
        u2, v2 = 11.5 * math.cos(r), 8.5 * math.sin(r)
        c, s_ = math.cos(math.radians(ang)), math.sin(math.radians(ang))
        line(P, cx + u * c - v * s_, cy + u * s_ + v * c, cx + u2 * c - v2 * s_, cy + u2 * s_ + v2 * c, 'd')
    for t in (-2.6, 2.6):
        u, c, s_ = t, math.cos(math.radians(ang)), math.sin(math.radians(ang))
        line(P, cx + t * c - 4.8 * -s_ * -1, cy + t * s_ - 4.8 * c, cx + t * c + 4.8 * -s_, cy + t * s_ + 4.8 * c, 'd')
    where(P, ('d',), lambda x, y: not ellipse(cx, cy, 11.8, 8.8, ang)(x, y) and not head(x, y), 'a')
    # a light patch in the middle of each plate
    for a in range(18, 360, 36):
        r = math.radians(a)
        u, v = 9.4 * math.cos(r), 6.7 * math.sin(r)
        c, s_ = math.cos(math.radians(ang)), math.sin(math.radians(ang))
        put(P, cx + u * c - v * s_, cy + u * s_ + v * c, 'y')
    for t in (-5, 0, 5):
        c, s_ = math.cos(math.radians(ang)), math.sin(math.radians(ang))
        fill(P, circle(cx + t * c, cy + t * s_, 0.9), 'y')
    outline(P, shell, 'd')
    return P


if __name__ == '__main__':
    import sys
    P = draw(40)
    P.png(sys.argv[1], cell=12)
    print(P.counts())
