"""
Minimap in the corner showing ship, nearby planets, enemies and stations.
"""

import math
import pygame
from utils import display


class Minimap:
    def __init__(self, size=160, scale=0.05):
        self.size = size
        self.scale = scale

    def render(self, surface, game):
        ship = game.spaceship
        if not ship:
            return

        ms = self.size
        mx = display.WIDTH - ms - 14
        my = 14

        # Background panel
        panel = pygame.Surface((ms, ms), pygame.SRCALPHA)
        pygame.draw.rect(panel, (0, 0, 0, 170), panel.get_rect(), border_radius=6)
        pygame.draw.rect(panel, (0, 255, 255), panel.get_rect(), 2, border_radius=6)
        surface.blit(panel, (mx, my))

        cx = mx + ms // 2
        cy = my + ms // 2

        # Resource blocks (small dots, color-keyed) — only those near the ship.
        # Sub-sampled so we don't burn frames at large block counts.
        blocks = getattr(game, 'blocks', [])
        block_colors = {
            'IRON': (180, 180, 200), 'GOLD': (255, 215, 0),
            'CRYSTAL': (200, 80, 240), 'FUEL': (255, 140, 60),
            'OXYGEN': (120, 220, 255),
        }
        max_d = (ms / 2 - 4) / self.scale
        # Step by ~6 blocks to avoid clutter and per-frame overhead.
        for b in blocks[::6]:
            if getattr(b, 'collected', False):
                continue
            dx = b.x - ship.x
            dy = b.y - ship.y
            if abs(dx) > max_d or abs(dy) > max_d:
                continue
            ox = dx * self.scale
            oy = dy * self.scale
            col = block_colors.get(getattr(b, 'block_type', None), (140, 160, 180))
            surface.set_at((int(cx + ox), int(cy + oy)), col)

        # Planets
        for p in getattr(game, 'planets', []):
            ox = (p.x - ship.x) * self.scale
            oy = (p.y - ship.y) * self.scale
            if abs(ox) > ms / 2 - 4 or abs(oy) > ms / 2 - 4:
                continue
            color = (200, 100, 100)
            r = max(2, int(p.radius * self.scale))
            pygame.draw.circle(surface, color, (int(cx + ox), int(cy + oy)), r)

        # Stations
        for st in getattr(getattr(game, 'station_system', None), 'stations', []):
            ox = (st.x - ship.x) * self.scale
            oy = (st.y - ship.y) * self.scale
            if abs(ox) > ms / 2 - 4 or abs(oy) > ms / 2 - 4:
                continue
            pygame.draw.rect(surface, (0, 255, 200), (int(cx + ox - 2), int(cy + oy - 2), 4, 4))

        # Enemies
        for e in getattr(game, 'enemies', []):
            ox = (e.x - ship.x) * self.scale
            oy = (e.y - ship.y) * self.scale
            if abs(ox) > ms / 2 - 4 or abs(oy) > ms / 2 - 4:
                continue
            pygame.draw.circle(surface, (255, 100, 100), (int(cx + ox), int(cy + oy)), 2)

        # Player at center
        pygame.draw.circle(surface, (0, 255, 255), (cx, cy), 3)
        # Heading line
        hx = cx + math.cos(ship.angle) * 8
        hy = cy + math.sin(ship.angle) * 8
        pygame.draw.line(surface, (0, 255, 255), (cx, cy), (int(hx), int(hy)), 2)
