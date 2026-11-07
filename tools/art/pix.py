"""Tiny pixel-art helper: draw with palette keys, emit level rows, preview PNG."""
import math
from PIL import Image


class Pic:
    def __init__(self, w, h, bg, palette):
        self.w, self.h = w, h
        self.g = [[bg] * w for _ in range(h)]
        self.palette = palette

    def set(self, x, y, k):
        x, y = math.floor(x + 0.5), math.floor(y + 0.5)  # not round(): halves go to even
        if 0 <= x < self.w and 0 <= y < self.h:
            self.g[y][x] = k

    def get(self, x, y):
        if 0 <= x < self.w and 0 <= y < self.h:
            return self.g[y][x]
        return None

    def fill(self, pred, k):
        """Set every cell whose centre (x+.5, y+.5) satisfies pred(x, y)."""
        for y in range(self.h):
            for x in range(self.w):
                if pred(x + 0.5, y + 0.5):
                    self.g[y][x] = k

    def line(self, x0, y0, x1, y1, k):
        n = int(max(abs(x1 - x0), abs(y1 - y0)) * 2) + 1
        for i in range(n + 1):
            t = i / n
            self.set(x0 + (x1 - x0) * t - 0.5, y0 + (y1 - y0) * t - 0.5, k)

    def curve(self, fn, t0, t1, k, steps=400):
        """fn(t) -> (x, y) in continuous coords; plot a 4-connected path."""
        prev = None
        for i in range(steps + 1):
            x, y = fn(t0 + (t1 - t0) * i / steps)
            c = (int(math.floor(x)), int(math.floor(y)))
            if prev and c != prev and c[0] != prev[0] and c[1] != prev[1]:
                self.set(prev[0], c[1], k)  # keep it 4-connected
            self.set(*c, k)
            prev = c

    def outline(self, inside, k, where=None):
        """Draw k on cells inside the shape that touch a cell outside it."""
        cells = []
        for y in range(self.h):
            for x in range(self.w):
                if not inside(x + .5, y + .5):
                    continue
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    if not inside(x + dx + .5, y + dy + .5) and (where is None or where(x, y, dx, dy)):
                        cells.append((x, y))
                        break
        for x, y in cells:
            self.g[y][x] = k

    def rows(self):
        rs = [''.join(r) for r in self.g]
        assert all(len(r) == self.w for r in rs) and len(rs) == self.h
        return rs

    def counts(self):
        c = {}
        for r in self.g:
            for k in r:
                c[k] = c.get(k, 0) + 1
        return c

    def png(self, path, cell=12):
        im = Image.new('RGB', (self.w * cell, self.h * cell))
        px = im.load()
        for y in range(self.h):
            for x in range(self.w):
                hx = self.palette[self.g[y][x]].lstrip('#')
                rgb = tuple(int(hx[i:i + 2], 16) for i in (0, 2, 4))
                for yy in range(cell):
                    for xx in range(cell):
                        px[x * cell + xx, y * cell + yy] = rgb
        im.save(path)
