"""Fish: a clownfish swimming over seaweed and rocks (40x40)."""
import math
from shapes import *

PAL = {
    'a': '#2a9d8f', 'u': '#d8f3f0', 'B': '#1a4f8b', 'b': '#2f86d6',
    'l': '#9fd3f5', 'w': '#ffffff', 'k': '#111111', 'o': '#ff8f00',
}


def draw(S):
    P = new(S, 'b', PAL)
    # lit water near the surface, current streaks deeper down
    fill(P, lambda x, y: y < 2.5 + 0.8 * math.sin(x * 0.45), 'l')
    streaks(P, [(7, 0.0, 1.2, 14, -2), (10, 2.6, 1.0, 12, 26), (24, 1.2, 1.2, 13, 27),
                (28, 4.1, 1.4, 12, -1), (16, 3.3, 1.0, 9, 31)], 'l')
    # seabed: sand, dark rocks
    fill(P, lambda x, y: y > 35 + 1.2 * math.sin(x * 0.3) + 0.5 * math.sin(x * 0.9), 'u')
    for rx, ry, rw, rh in ((7, 35, 5, 3.2), (31, 34.5, 6, 3.8), (19, 37.5, 3.5, 2)):
        rock = ellipse(rx, ry, rw, rh)
        fill(P, rock, 'B')
        curve(P, lambda a, rx=rx, ry=ry, rw=rw, rh=rh: (rx + rw * 0.6 * math.cos(a), ry + rh * 0.6 * math.sin(a)),
              3.6, 4.6, 'l')
    # seaweed: wavy teal fronds from the bed
    for sx, h, ph in ((2.5, 18, 0.0), (5, 13, 1.5), (12, 10, 2.8), (26, 11, 0.7), (35, 17, 2.2), (37.5, 12, 3.6)):
        for dx in (0, 1):
            curve(P, lambda t, sx=sx, ph=ph, dx=dx: (sx + dx + 1.4 * math.sin(t * 0.5 + ph) * (t / h), 38 - t),
                  0, h, 'a')
    # bubbles rising
    for bx, by, r in ((33, 6, 1.3), (35, 11, 0.9), (31.5, 14.5, 1.1), (8, 9, 1.0), (6, 4, 0.8)):
        fill(P, lambda x, y, bx=bx, by=by, r=r: abs(math.hypot(x - bx, y - by) - r) < 0.55, 'l')
        put(P, bx - r * 0.6, by - r * 0.6, 'w')

    # --- clownfish, facing right
    cx, cy = 19, 20
    body = ellipse(cx, cy, 12, 6.8)
    tail = poly([(cx - 10.5, cy), (cx - 16, cy - 5.5), (cx - 14, cy), (cx - 16, cy + 5.5)])
    dorsal = union(ellipse(cx - 2, cy - 6, 6, 2.6, 8), ellipse(cx + 5, cy - 5.3, 3.2, 2.0, 25))
    belly_fin = ellipse(cx + 1, cy + 6.2, 3.5, 1.8, -20)
    side_fin = ellipse(cx + 3.2, cy + 2.8, 2.4, 1.3, 35)
    fins = union(tail, dorsal, belly_fin)
    fill(P, fins, 'o')
    # fin edges dark, with fine rays
    outline(P, fins, 'k')
    for t in (-3, 0, 3):
        line(P, cx - 12, cy, cx - 15, cy + t * 1.4, 'w' if t == 0 else 'o')
    fill(P, body, 'o')
    # three white bands with black edges, following the body's curve
    for bx, bw in ((cx + 5.2, 0.9), (cx - 1.0, 1.2), (cx - 7.6, 0.7)):
        band = both(body, lambda x, y, bx=bx, bw=bw: abs(x - bx + 0.045 * (y - cy) ** 2) < bw)
        edge = both(body, lambda x, y, bx=bx, bw=bw: abs(x - bx + 0.045 * (y - cy) ** 2) < bw + 0.75)
        fill(P, edge, 'k')
        fill(P, band, 'w')
    outline(P, body, 'k')
    fill(P, side_fin, 'o')
    outline(P, side_fin, 'k')
    # eye and mouth
    fill(P, circle(cx + 9.3, cy - 1.8, 1.3), 'w')
    fill(P, circle(cx + 9.6, cy - 1.7, 0.75), 'k')
    
    line(P, cx + 10.4, cy + 1.8, cx + 11.6, cy + 1.3, 'k')
    # highlight along the back
    curve(P, lambda a: (cx + 8.5 * math.cos(a), cy + 4.4 * math.sin(a)), 3.75, 4.3, 'u')
    return P


if __name__ == '__main__':
    import sys
    P = draw(40)
    P.png(sys.argv[1], cell=12)
    print(P.counts())
