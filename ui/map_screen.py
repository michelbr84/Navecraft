"""
World map screen - shows explored area (fog of war), planets, stations, custom waypoints.
"""

import math
import pygame
from utils import display
from utils.font import get_font, draw_panel, render_outlined


class WorldMap:
    def __init__(self):
        self.visible = False
        self.scale = 0.04
        self.player_waypoints = []  # list of (world_x, world_y, label)
        self.explored = set()  # set of (cell_x, cell_y) tuples
        self.cell_size = 200  # world units per fog cell

    def toggle(self):
        self.visible = not self.visible

    def mark_explored(self, x, y):
        self.explored.add((int(x // self.cell_size), int(y // self.cell_size)))

    def handle_event(self, event, game):
        if not self.visible:
            return False
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_ESCAPE, pygame.K_m):
                self.visible = False
                return True
            if event.key == pygame.K_EQUALS or event.key == pygame.K_PLUS:
                self.scale = min(0.2, self.scale * 1.25)
                return True
            if event.key == pygame.K_MINUS:
                self.scale = max(0.01, self.scale / 1.25)
                return True
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and game.spaceship:
            mx, my = event.pos
            wx = (mx - display.WIDTH // 2) / self.scale + game.spaceship.x
            wy = (my - display.HEIGHT // 2) / self.scale + game.spaceship.y
            self.player_waypoints.append((wx, wy, f"WP{len(self.player_waypoints) + 1}"))
            from ui.compass import CompassSystem
            return True
        return False

    def render(self, surface, game):
        if not self.visible:
            return
        w, h = display.WIDTH, display.HEIGHT
        # Background
        bg = pygame.Surface((w, h), pygame.SRCALPHA)
        bg.fill((0, 0, 0, 220))
        surface.blit(bg, (0, 0))

        title = render_outlined(get_font(32), "MAPA GALÁCTICO", (200, 240, 255), (0, 0, 0), 2)
        surface.blit(title, ((w - title.get_width()) // 2, 18))

        cx, cy = w // 2, h // 2
        ship = game.spaceship

        # Fog grid - draw dark gray over unexplored, light gray over explored
        if ship:
            for ex, ey in self.explored:
                px = cx + (ex * self.cell_size - ship.x) * self.scale
                py = cy + (ey * self.cell_size - ship.y) * self.scale
                size = self.cell_size * self.scale
                if -size < px < w and -size < py < h:
                    rect = pygame.Rect(int(px), int(py), int(size), int(size))
                    pygame.draw.rect(surface, (30, 50, 80, 80), rect)

        # Planets
        for p in getattr(game, 'planets', []):
            px = cx + (p.x - (ship.x if ship else 0)) * self.scale
            py = cy + (p.y - (ship.y if ship else 0)) * self.scale
            if 0 < px < w and 0 < py < h:
                pygame.draw.circle(surface, (180, 120, 80), (int(px), int(py)),
                                   max(3, int(p.radius * self.scale)))
                name = render_outlined(get_font(13), getattr(p, 'name', p.planet_type),
                                       (255, 220, 200), (0, 0, 0), 1)
                surface.blit(name, (int(px) + 6, int(py) - 6))

        # Stations
        for st in getattr(getattr(game, 'station_system', None), 'stations', []):
            px = cx + (st.x - (ship.x if ship else 0)) * self.scale
            py = cy + (st.y - (ship.y if ship else 0)) * self.scale
            if 0 < px < w and 0 < py < h:
                pygame.draw.rect(surface, (0, 255, 200), (int(px) - 3, int(py) - 3, 6, 6))

        # Waypoints
        for wx, wy, label in self.player_waypoints:
            px = cx + (wx - (ship.x if ship else 0)) * self.scale
            py = cy + (wy - (ship.y if ship else 0)) * self.scale
            if 0 < px < w and 0 < py < h:
                pygame.draw.polygon(surface, (255, 220, 50),
                                    [(int(px), int(py) - 8), (int(px) - 6, int(py) + 4), (int(px) + 6, int(py) + 4)])
                lab = render_outlined(get_font(12), label, (255, 220, 50), (0, 0, 0), 1)
                surface.blit(lab, (int(px) + 8, int(py)))

        # Player
        if ship:
            pygame.draw.circle(surface, (0, 255, 255), (cx, cy), 6)
            heading_x = cx + math.cos(ship.angle) * 12
            heading_y = cy + math.sin(ship.angle) * 12
            pygame.draw.line(surface, (0, 255, 255), (cx, cy), (int(heading_x), int(heading_y)), 2)

        hint = render_outlined(get_font(14),
                               "Clique para criar waypoint  |  +/- zoom  |  M ou ESC fechar",
                               (180, 180, 180), (0, 0, 0), 1)
        surface.blit(hint, ((w - hint.get_width()) // 2, h - 28))
