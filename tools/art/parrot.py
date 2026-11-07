"""Parrot: a macaw on a branch in the jungle, drawn from shapes (designed at 40x40).

    python3 tools/art/install.py picture tools/art/parrot.py 40 "Parrot" --png /tmp/p.png
"""
import math
from pix import Pic

PAL = {
    'G': '#1b5e20', 'g': '#4caf50', 'y': '#ffd600', 'B': '#1e88e5',
    't': '#6d4c41', 'r': '#e53935', 'w': '#fafafa', 'k': '#212121',
}


def rot(x, y, cx, cy, deg):
    """(x, y) in the frame of an ellipse centred (cx, cy) and turned by deg."""
    a = math.radians(deg)
    dx, dy = x - cx, y - cy
    return dx * math.cos(a) + dy * math.sin(a), -dx * math.sin(a) + dy * math.cos(a)


def ellipse(cx, cy, rx, ry, deg=0):
    def inside(x, y):
        u, v = rot(x, y, cx, cy, deg)
        return (u / rx) ** 2 + (v / ry) ** 2 <= 1
    return inside


def leaf(P, s, x0, y0, length, width, deg, k='g', vein='G'):
    """A pointed leaf from its stalk end (x0, y0), with a midrib and side veins."""
    a = math.radians(deg)
    ux, uy = math.cos(a), math.sin(a)
    def inside(x, y):
        dx, dy = x / s - x0, y / s - y0
        u = dx * ux + dy * uy
        v = -dx * uy + dy * ux
        return 0 <= u <= length and abs(v) <= width * math.sin(math.pi * u / length) ** 0.8
    P.fill(inside, k)
    P.curve(lambda t: (s * (x0 + ux * t), s * (y0 + uy * t)), 0.5, length * 0.85, vein)
    for t in (range(3, int(length * 0.7), 4) if width >= 3 else ()):
        for side in (-1, 1):
            # side veins angle forward from the midrib
            bx, by = x0 + ux * t, y0 + uy * t
            ex = bx + ux * 1.2 - uy * side * width * 0.7
            ey = by + uy * 1.2 + ux * side * width * 0.7
            P.line(s * bx, s * by, s * ex, s * ey, vein)


def fern(P, s, x0, y0, length, deg, bend, k='g'):
    """An arching fern frond from (x0, y0): a stem with alternating leaflets that taper."""
    def stem(t):
        a = math.radians(deg + bend * t / length)
        # integrate the turning direction in small steps
        x, y, d = x0, y0, math.radians(deg)
        n = int(t * 4) + 1
        for i in range(n):
            d = math.radians(deg + bend * (i / 4) / length)
            x += math.cos(d) / 4
            y += math.sin(d) / 4
        return x, y, d
    P.curve(lambda t: tuple(v * s for v in stem(t)[:2]), 0, length, k)
    for t in range(1, int(length), 2):
        x, y, d = stem(t)
        ln = 3.0 * (1 - t / length) + 0.8
        for side in (-1, 1):
            ex = x + math.cos(d + side * 0.95) * ln
            ey = y + math.sin(d + side * 0.95) * ln
            P.line(s * x, s * y, s * ex, s * ey, k)


def draw(S):
    s = S / 40
    P = Pic(S, S, 'G', PAL)
    sc = lambda f: (lambda x, y: f(x / s, y / s))  # shapes are designed in 40-unit coords

    # --- jungle behind: big veined leaves, hanging vines, flowers, a butterfly
    # fern fronds in the gaps, behind the big leaves
    for x0, y0, ln, d, bend in ((-1, 12, 14, 10, 40), (41, 9, 13, 170, -40), (-1, 33, 12, -25, 30),
                                (41, 33, 12, 200, -30), (19, -1, 11, 75, 30), (16, 41, 10, -80, -30),
                                (30, 41, 11, -100, 35), (10, 26, 9, -60, 35)):
        fern(P, s, x0, y0, ln, d, bend)
    for x0, y0, ln, w, d in ((-3, 4, 16, 4.2, 15), (43, 3, 16, 4.2, 165), (-2, 19, 13, 3.6, -20),
                             (42, 18, 14, 3.8, 200), (1, 41, 15, 4.0, -45), (40, 41, 15, 4.0, 230),
                             (27, -2, 12, 3.4, 115), (12, -2, 11, 3.2, 65), (20, 41, 10, 3.2, -95),
                             (-2, 30, 9, 2.8, 10), (42, 29, 9, 2.8, 175)):
        leaf(P, s, x0, y0, ln, w, d)
    # hanging vines with small leaves and clusters of red berries
    for vx, ph, ln, amp in ((5.5, 0.0, 24, 1.4), (11, 2.4, 13, 1.0), (31, 1.0, 15, 1.1), (36, 1.9, 22, 1.4)):
        vine = lambda t, vx=vx, ph=ph, amp=amp: (s * (vx + amp * math.sin(t * 0.45 + ph)), s * t)
        P.curve(vine, 0, ln, 't')
        for t in range(4, ln - 1, 5):
            x, y = vine(t)
            side = 1 if (t // 5) % 2 else -1
            leaf(P, s, x / s, y / s, 3.2, 1.0, 90 - side * 50, 'g', 'g')
        x, y = vine(ln)  # berries at the end
        for dx, dy in ((0, 0), (-1, 1), (1, 1), (0, 2)):
            P.set(x + dx * max(1, s) - 0.5, y + dy * max(1, s) - 0.5, 'r')
    # flowers: yellow petals round a red centre
    for fx, fy in ((2.5, 25), (37.5, 30), (13, 37), (27.5, 3.5), (32.5, 36.5), (37, 13)):
        for dx, dy in ((0, -1), (-1, 0), (1, 0), (0, 1)):
            P.set(s * fx + dx * max(1, s) - 0.5, s * fy + dy * max(1, s) - 0.5, 'y')
        P.set(s * fx - 0.5, s * fy - 0.5, 'r')
    # blue butterflies
    for bx, by, sz in ((33, 8.5, 1.0), (8.5, 21.5, 0.8)):
        bx, by = bx * s, by * s
        for side in (-1, 1):
            P.fill(lambda x, y, side=side: ((x - bx - side * 1.4 * s * sz) / (1.3 * s * sz)) ** 2 +
                   ((y - by + 0.6 * s * sz) / (1.4 * s * sz)) ** 2 <= 1, 'B')
            P.fill(lambda x, y, side=side: ((x - bx - side * 1.1 * s * sz) / (0.9 * s * sz)) ** 2 +
                   ((y - by - 1.3 * s * sz) / (0.9 * s * sz)) ** 2 <= 1, 'B')
        P.line(bx, by - 2 * s * sz, bx, by + 2 * s * sz, 'k')

    # --- branch, rising to the right, with moss and a knot
    bl = lambda x: 31.5 - x * 0.12  # top edge of the branch at x
    branch = sc(lambda x, y: bl(x) <= y <= bl(x) + 3.2)
    P.fill(branch, 't')
    P.fill(sc(lambda x, y: bl(x) + 2.4 < y <= bl(x) + 3.2), 'k')  # shadow underneath
    P.fill(sc(lambda x, y: bl(x) <= y < bl(x) + 0.9 and math.sin(x * 0.9) > 0.35), 'g')  # moss
    P.fill(sc(lambda x, y: math.hypot(x - 33, y - bl(33) - 1.4) < 0.9), 'k')  # knot
    leaf(P, s, 14, bl(14) + 2.5, 6, 1.6, 115)
    leaf(P, s, 30, bl(30) + 2.5, 5, 1.4, 70)

    # --- parrot (facing left)
    head = ellipse(16.5, 9.5, 5.2, 5.0)
    body = ellipse(21, 19.5, 6.2, 9.5, -18)
    tail = lambda x, y: (y > 25 and y < 39.5 and
                         abs(x - (23 + (y - 25) * 0.32)) < 3.2 - (y - 25) * 0.08)
    beak = lambda x, y: ((x - 12.4) / 2.6) ** 2 + ((y - 10.6) / 2.7) ** 2 <= 1 and x < 13
    hook = lambda x, y: math.hypot(x - 10.3, y - 12.9) < 0.9
    bird = lambda x, y: head(x, y) or body(x, y) or tail(x, y) or beak(x, y) or hook(x, y)

    P.fill(sc(lambda x, y: head(x, y) or body(x, y)), 'r')
    # tail: a long red centre feather between blue-tipped outer feathers
    P.fill(sc(tail), 'r')
    P.fill(sc(lambda x, y: tail(x, y) and abs(x - (23 + (y - 25) * 0.32)) > 1.1 and y > 29), 'B')
    # folded wing: shoulder red, then yellow coverts with green tips, then blue flight feathers
    wing = ellipse(23.2, 21, 4.4, 8.6, -18)
    def wing_band(x, y):
        u, v = rot(x, y, 23.2, 21, -18)
        t = v / 8.6 + 0.12 * math.sin(u * 2.4)  # scalloped band edges
        return t
    P.fill(sc(lambda x, y: wing(x, y) and -0.55 < wing_band(x, y) <= -0.05), 'y')
    P.fill(sc(lambda x, y: wing(x, y) and -0.05 < wing_band(x, y) <= 0.25), 'g')
    P.fill(sc(lambda x, y: wing(x, y) and wing_band(x, y) > 0.25), 'B')
    P.outline(sc(wing), 'k', where=lambda x, y, dx, dy: dx != -1)  # wing edge, not the chest side
    # face: bare white patch with fine red feather lines, yellow eye with dark pupil
    face = ellipse(15.2, 9.6, 2.6, 2.0)
    P.fill(sc(face), 'w')
    P.fill(sc(lambda x, y: face(x, y) and y > 10.5 and int(x) % 2 == 0), 'r')
    P.fill(sc(lambda x, y: math.hypot(x - 16, y - 8.9) < 1.25), 'y')
    P.set(16 * s - 0.5, 8.9 * s - 0.5, 'k')
    # beak: pale hooked upper, dark lower mandible
    P.fill(sc(lambda x, y: beak(x, y) or hook(x, y)), 'w')
    P.fill(sc(lambda x, y: beak(x, y) and y > 11.4 and x > 11.2), 'k')
    # outline the whole bird
    P.outline(sc(bird), 'k')
    # feet gripping the branch
    for fx in (20, 24):
        P.fill(sc(lambda x, y, fx=fx: abs(x - fx) < 1.3 and bl(x) - 1 <= y < bl(x) + 0.8), 'k')
    return P


if __name__ == '__main__':
    import sys
    P = draw(int(sys.argv[1]))
    P.png(sys.argv[2], cell=max(4, 480 // P.w))
    print(P.counts())
