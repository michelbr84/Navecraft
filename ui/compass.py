"""
Compass + off-screen markers - arrow on screen edge pointing to mission objective,
plus indicator arrows for enemies and stations outside the viewport.
"""

import math
import pygame
from utils import display


class CompassSystem:
    def __init__(self):
        self.waypoint = None  # (world_x, world_y, label) or None

    def set_waypoint(self, x, y, label=None):
        self.waypoint = (x, y, label or "?")

    def clear_waypoint(self):
        self.waypoint = None

    def _draw_edge_arrow(self, surface, ship_screen, world_x, world_y, camera_x, camera_y, color, size=10):
        w, h = display.WIDTH, display.HEIGHT
        target_screen_x = world_x - camera_x
        target_screen_y = world_y - camera_y
        cx, cy = w / 2, h / 2
        if 0 < target_screen_x < w and 0 < target_screen_y < h:
            return  # on-screen, no arrow
        dx = target_screen_x - cx
        dy = target_screen_y - cy
        if dx == 0 and dy == 0:
            return
        # Clip ray to screen rectangle
        margin = 36
        ax, ay = w - margin, h - margin
        bx, by = margin, margin
        tx_scale = (ax - cx) / dx if dx != 0 else float('inf')
        if dx < 0:
            tx_scale = (bx - cx) / dx
        ty_scale = (ay - cy) / dy if dy != 0 else float('inf')
        if dy < 0:
            ty_scale = (by - cy) / dy
        scale = min(abs(tx_scale), abs(ty_scale))
        px = cx + dx * scale
        py = cy + dy * scale
        # Arrow triangle
        ang = math.atan2(dy, dx)
        p1 = (px + math.cos(ang) * size, py + math.sin(ang) * size)
        p2 = (px + math.cos(ang + 2.5) * size, py + math.sin(ang + 2.5) * size)
        p3 = (px + math.cos(ang - 2.5) * size, py + math.sin(ang - 2.5) * size)
        pygame.draw.polygon(surface, color, [p1, p2, p3])
        pygame.draw.polygon(surface, (255, 255, 255), [p1, p2, p3], 1)

    def render(self, surface, game, camera_x, camera_y):
        ship = game.spaceship
        if not ship:
            return
        ship_screen = (ship.x - camera_x, ship.y - camera_y)
        # Waypoint arrow
        if self.waypoint:
            wx, wy, _ = self.waypoint
            self._draw_edge_arrow(surface, ship_screen, wx, wy, camera_x, camera_y, (255, 220, 0), size=14)
        # Enemy off-screen arrows
        for e in getattr(game, 'enemies', []):
            dist = math.hypot(e.x - ship.x, e.y - ship.y)
            if dist > 700:
                continue
            self._draw_edge_arrow(surface, ship_screen, e.x, e.y, camera_x, camera_y, (255, 80, 80), size=10)
