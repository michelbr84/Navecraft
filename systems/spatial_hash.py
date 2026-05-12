"""
Spatial hash grid - broad-phase collision and proximity queries.
"""

import math


class SpatialHash:
    def __init__(self, cell_size=128):
        self.cell_size = cell_size
        self.grid = {}

    def _key(self, x, y):
        return (int(x // self.cell_size), int(y // self.cell_size))

    def clear(self):
        self.grid.clear()

    def insert(self, obj, x, y):
        self.grid.setdefault(self._key(x, y), []).append(obj)

    def rebuild(self, objects, get_xy=lambda o: (o.x, o.y)):
        self.clear()
        for o in objects:
            x, y = get_xy(o)
            self.insert(o, x, y)

    def query_radius(self, x, y, r):
        cells_r = int(math.ceil(r / self.cell_size))
        cx, cy = self._key(x, y)
        out = []
        for dx in range(-cells_r, cells_r + 1):
            for dy in range(-cells_r, cells_r + 1):
                bucket = self.grid.get((cx + dx, cy + dy))
                if bucket:
                    out.extend(bucket)
        return out

    def query_rect(self, x, y, w, h):
        x1 = self._key(x, y)
        x2 = self._key(x + w, y + h)
        out = []
        for cx in range(x1[0], x2[0] + 1):
            for cy in range(x1[1], x2[1] + 1):
                bucket = self.grid.get((cx, cy))
                if bucket:
                    out.extend(bucket)
        return out
