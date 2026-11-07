"""Pizza: pepperoni, olives, basil and mozzarella on a gingham tablecloth (40x40).
Kept close to the original 28x28 picture, which the user liked."""
import math
from shapes import *

PAL = {
    'B': '#3f7fd9', 'W': '#f6f6f2', 'k': '#4a2c17', 'c': '#e0a458',
    'r': '#d84315', 'y': '#ffd54f', 'p': '#a3192f', 'g': '#43a047',
}


def draw(S):
    P = new(S, 'W', PAL)
    # gingham tablecloth
    fill(P, lambda x, y: (int(x // 3) + int(y // 3)) % 2 == 0, 'B')

    cx, cy, R = 20, 20, 18.6
    pizza = circle(cx, cy, R)
    fill(P, pizza, 'c')
    outline(P, pizza, 'k')
    # a few toasted bubbles on the crust
    for a in range(20, 360, 40):
        r = math.radians(a)
        put(P, cx + (R - 1.6) * math.cos(r), cy + (R - 1.6) * math.sin(r), 'k' if a % 80 == 20 else 'r')
    # sauce, then melted cheese in lumpy blobs with sauce between
    top = circle(cx, cy, R - 2.6)
    fill(P, top, 'r')
    blobs = []
    for i in range(22):
        a = i * 2.39996
        rr = 13.5 * math.sqrt((i + 0.5) / 22)
        blobs.append(circle(cx + rr * math.cos(a), cy + rr * math.sin(a), 2.5 + 0.4 * math.sin(i * 1.3)))
    fill(P, both(union(*blobs), circle(cx, cy, R - 3.3)), 'y')
    # mozzarella bits
    for i in range(14):
        a = i * 2.39996 + 1.1
        rr = 13.8 * math.sqrt((i + 0.5) / 14)
        put(P, cx + rr * math.cos(a), cy + rr * math.sin(a), 'W')
    # pepperoni: dark red rounds with a glossy fleck
    peps = ((12, 10), (23.5, 7.5), (31, 14), (19, 17), (9, 21), (27, 22.5), (15.5, 28), (25, 31), (33, 27))
    for px, py in peps:
        pep = circle(px, py, 2.6)
        fill(P, pep, 'p')
        put(P, px - 1, py - 1, 'r')
    # black olives: dark rings with the topping showing through
    for ox, oy in ((17, 9.5), (29.5, 9), (12.5, 16), (24, 15), (33.5, 20.5), (20.5, 24),
                   (9.5, 28), (20, 33), (30, 30)):
        fill(P, lambda x, y, ox=ox, oy=oy: 0.9 < math.hypot(x - ox, y - oy) <= 1.9, 'k')
    # basil: small leaves scattered
    for bx, by, d in ((15, 13, 20), (26.5, 11.5, 150), (6.5, 16, 80), (22, 21, 200), (13.5, 22.5, -30),
                      (31.5, 24.5, 110), (11, 33, -60), (23.5, 27, 30), (16.5, 35, 170)):
        leaf(P, bx, by, 3.2, 1.1, d, 'g')
    return P


if __name__ == '__main__':
    import sys
    P = draw(40)
    P.png(sys.argv[1], cell=12)
    print(P.counts())
