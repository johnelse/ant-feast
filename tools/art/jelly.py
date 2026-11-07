"""Jellyfish drawn from shapes, at any square size S (designed at 40)."""
import math, sys, json
from pix import Pic

PAL = {
    'n': '#0b1d3a', 'b': '#1e4b8f', 'm': '#8e1e6a', 'p': '#f48fc4',
    'v': '#9c6ade', 'c': '#5ee0e6', 'w': '#f2fbff', 'y': '#fff176',
}


def _surface(P, s):
    """Lit surface along the top with a gently rippled underside."""
    P.fill(lambda x, y: y < s * (2.0 + 0.9 * math.sin(x / s * 0.42 + 0.6) + 0.5 * math.sin(x / s * 1.1)), 'b')


def _despeckle(P, k, bg):
    """Remove k cells with no k neighbour (they read as noise, not light)."""
    lone = [(x, y) for y in range(P.h) for x in range(P.w) if P.g[y][x] == k and
            not any(P.get(x + dx, y + dy) == k for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))]
    for x, y in lone:
        P.g[y][x] = bg


def water_shafts(P, s):
    """The original: straight diagonal light shafts."""
    P.fill(lambda x, y: y < s * (2.2 + 0.8 * math.sin(x / s * 0.5)), 'b')
    for x0, w0, ln in ((-2, 1.3, 38), (9, 1.0, 30), (24, 1.2, 36)):
        P.fill(lambda x, y, x0=x0, w0=w0, ln=ln: y < s * ln and
               abs(x - s * (x0 + 0.45 * y / s)) < s * w0, 'b')


def water_caustics(P, s):
    """Rippling light net, like sunlight through waves, fading with depth."""
    _surface(P, s)
    def f(x, y):
        u, v = x / s, y / s
        a = math.sin(u * 0.42 + math.sin(v * 0.3) * 1.6) + math.sin(v * 0.5 + math.sin(u * 0.33) * 1.4)
        return a
    P.fill(lambda x, y: abs(f(x, y)) < 0.5 * max(0.0, 1 - (y / s) / 40), 'b')
    _despeckle(P, 'b', 'n')


def water_currents(P, s):
    """Long wavy current streaks drifting across the water."""
    _surface(P, s)
    for y0, ph, amp, ln, x0 in ((7, 0.0, 1.4, 17, -2), (11, 2.6, 1.2, 15, 23), (17, 2.0, 1.3, 12, 27),
                                 (23, 4.1, 1.6, 16, -1), (28, 1.2, 1.2, 14, 25), (33, 3.3, 1.5, 15, 3),
                                 (37, 5.0, 1.0, 14, 21)):
        P.curve(lambda t, y0=y0, ph=ph, amp=amp: (s * t, s * (y0 + amp * math.sin(t * 0.33 + ph))),
                x0, x0 + ln, 'b')
        P.curve(lambda t, y0=y0, ph=ph, amp=amp: (s * t, s * (y0 + 1 + amp * math.sin(t * 0.33 + ph))),
                x0 + 2, x0 + ln - 3, 'b')


def water_glow(P, s):
    """Soft pools of light: blobby, irregular patches, larger near the surface."""
    _surface(P, s)
    def f(x, y):
        u, v = x / s, y / s
        return (math.sin(u * 0.31 + 1.3) * math.sin(v * 0.27 + 0.4) +
                0.6 * math.sin(u * 0.73 + v * 0.41 + 2.0) +
                0.4 * math.sin(u * 0.17 - v * 0.83 + 0.7))
    P.fill(lambda x, y: f(x, y) > 0.55 + (y / s) / 45, 'b')


WATER = {'shafts': water_shafts, 'caustics': water_caustics,
         'currents': water_currents, 'glow': water_glow}


def draw(S, water='currents'):
    s = S / 40
    P = Pic(S, S, 'n', PAL)
    # --- water (see WATER below for the styles)
    WATER[water](P, s)
    # bubbles rising on the right
    for bx, by, r in ((35, 33, 1.6), (33.5, 26, 1.2), (36, 19, 1.4), (34, 12, 0.9)):
        bx, by, r = bx * s, by * s, max(0.7, r * s)
        P.fill(lambda x, y: abs(math.hypot(x - bx, y - by) - r) < 0.55, 'c')
        P.set(bx - r * 0.6 - 0.5, by - r * 0.6 - 0.5, 'w')

    cx, rimy, rx, ry = 20 * s, 19 * s, 14 * s, 15 * s
    dome = lambda x, y: y <= rimy and ((x - cx) / rx) ** 2 + ((y - rimy) / ry) ** 2 <= 1

    # --- tentacles (behind the bell): thin wavy lines from the rim downwards
    tents = [(-12, 'v', 0.0, -0.10), (-8.5, 'c', 1.7, -0.05), (-5, 'p', 3.1, 0.02),
             (5, 'v', 4.4, -0.02), (8.5, 'c', 0.9, 0.06), (12, 'p', 2.3, 0.12)]
    for dx, k, ph, drift in tents:
        x0 = cx + dx * s
        P.curve(lambda t, x0=x0, ph=ph, drift=drift:
                (x0 + s * (2.6 * math.sin(t * 0.22 + ph) + drift * t), rimy + t * s),
                1, 21, k)

    # --- oral arms: two pairs of frilly curtains with a dark spine
    for ax, ph, amp in ((-6, 0.0, 1.8), (-2, 2.2, 1.2), (2, 3.6, 1.2), (6, 5.4, 1.8)):
        def centre(y, ax=ax, ph=ph, amp=amp):
            t = (y - rimy) / s
            return cx + s * (ax * (1 + t * 0.03) + amp * math.sin(t * 0.33 + ph))
        def width(y):
            t = (y - rimy) / s
            return s * max(0.7, 1.9 - t * 0.075)
        L = 15 if abs(ax) < 3 else 12
        arm = lambda x, y: rimy < y < rimy + L * s and abs(x - centre(y)) < width(y)
        P.fill(arm, 'p')
        P.curve(lambda t: (centre(rimy + t * s) - 0.0, rimy + t * s), 0.5, L - 1, 'm')
        # frills: light ruffles down the outer edge, every other unit
        side = 1 if ax > 0 else -1
        for y in range(S):
            yc = y + 0.5
            if rimy + s < yc < rimy + (L - 1) * s and int((yc - rimy) / s) % 4 == 1:
                P.set(centre(yc) + side * (width(yc) - 0.3) - 0.5, y, 'w')

    # --- bell
    P.fill(dome, 'p')
    # shadow crescent on the right
    P.fill(lambda x, y: dome(x, y) and ((x - cx + 4.5 * s) / (rx * 0.97)) ** 2 + ((y - rimy + 1.5 * s) / (ry * 0.95)) ** 2 > 1, 'v')
    P.outline(dome, 'm', where=lambda x, y, dx, dy: dy != 1)
    # highlight arcs, upper left
    for f, a0, a1 in ((0.80, 200, 245), (0.66, 215, 232)):
        P.curve(lambda a: (cx + rx * f * math.cos(math.radians(a)),
                           rimy + ry * f * math.sin(math.radians(a))), a0, a1, 'w')
    # radial canals
    for a in (195, 222, 249, 291, 318, 345):
        r = math.radians(a)
        P.curve(lambda t: (cx + rx * t * math.cos(r), rimy + ry * t * math.sin(r)), 0.62, 0.9, 'c')
    # gonads: four horseshoes round the centre, seen through the bell
    gy = rimy - 7 * s
    for qx, qy in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
        px, py = cx + qx * 3.2 * s, gy + qy * 2.4 * s
        out = math.degrees(math.atan2(qy * 2.4, qx * 3.2))
        P.curve(lambda a, px=px, py=py: (px + 2.2 * s * math.cos(math.radians(a)),
                                         py + 1.7 * s * math.sin(math.radians(a))),
                out - 120, out + 120, 'v')
    P.fill(lambda x, y: math.hypot((x - cx) / s, (y - gy) / s) < 1.2, 'm')
    # rim: scalloped lappets with a light in each
    n = 9
    for i in range(n):
        lx = cx - rx * 0.92 + i * (2 * rx * 0.92) / (n - 1)
        lr = 1.5 * s
        lap = lambda x, y: y > rimy - 0.5 and math.hypot(x - lx, y - rimy) <= lr + 0.3
        P.fill(lap, 'p')
        P.outline(lap, 'm', where=lambda x, y, dx, dy: dy != -1)
        P.set(lx - 0.5, rimy + 0.5 * s - 0.5 + 0.5, 'y')
    # rim line
    P.fill(lambda x, y: abs(y - rimy + 0.5) < 0.5 and abs(x - cx) < rx * 0.95, 'm')
    return P


if __name__ == '__main__':
    S = int(sys.argv[1])
    P = draw(S)
    P.png(sys.argv[2], cell=max(4, 480 // S))
    print(json.dumps(P.rows()))
    print(P.counts(), file=sys.stderr)
