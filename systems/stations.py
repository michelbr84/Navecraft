"""
Sistema de estacoes espaciais do Navecraft
"""

import pygame
import math
from settings import *
from systems.generation import Block


class SpaceStation:
    def __init__(self, x, y, station_type, blocks):
        self.x = x
        self.y = y
        self.station_type = station_type
        self.blocks = blocks


class StationSystem:
    def __init__(self):
        self.stations = []
        self.blueprints = self._generate_blueprints()
        self.selected_blueprint = 0
        self.blueprint_names = list(self.blueprints.keys())

    def _generate_blueprints(self):
        return {
            'SMALL_OUTPOST': {
                'name': 'Posto Avancado',
                'cost': {'IRON': 20, 'FUEL': 10},
                'layout': [
                    (0, 0, 'IRON'),
                    (-1, 0, 'IRON'), (1, 0, 'IRON'),
                    (0, -1, 'IRON'), (0, 1, 'IRON'),
                    (-1, -1, 'IRON'), (1, -1, 'IRON'),
                    (-1, 1, 'IRON'), (1, 1, 'IRON'),
                ],
                'benefit': 'Ponto de referencia no mapa',
            },
            'REFUEL_STATION': {
                'name': 'Estacao de Reabastecimento',
                'cost': {'IRON': 30, 'FUEL': 20, 'OXYGEN': 15},
                'layout': [
                    (0, 0, 'FUEL'),
                    (-1, 0, 'IRON'), (1, 0, 'IRON'),
                    (0, -1, 'IRON'), (0, 1, 'IRON'),
                    (-2, 0, 'FUEL'), (2, 0, 'FUEL'),
                    (0, -2, 'OXYGEN'), (0, 2, 'OXYGEN'),
                    (-1, -1, 'IRON'), (1, -1, 'IRON'),
                    (-1, 1, 'IRON'), (1, 1, 'IRON'),
                ],
                'benefit': 'Regenera combustivel e oxigenio ao ficar proximo',
            },
            'MINING_PLATFORM': {
                'name': 'Plataforma de Mineracao',
                'cost': {'IRON': 40, 'CRYSTAL': 10},
                'layout': [
                    (0, 0, 'CRYSTAL'),
                    (-1, 0, 'IRON'), (1, 0, 'IRON'),
                    (0, -1, 'IRON'), (0, 1, 'IRON'),
                    (-2, 0, 'IRON'), (2, 0, 'IRON'),
                    (0, -2, 'IRON'), (0, 2, 'IRON'),
                    (-2, -1, 'IRON'), (2, -1, 'IRON'),
                    (-2, 1, 'IRON'), (2, 1, 'IRON'),
                    (-1, -2, 'CRYSTAL'), (1, -2, 'CRYSTAL'),
                    (-1, 2, 'CRYSTAL'), (1, 2, 'CRYSTAL'),
                ],
                'benefit': 'Aumenta alcance de mineracao quando proximo',
            },
        }

    def get_selected_blueprint(self):
        name = self.blueprint_names[self.selected_blueprint]
        return name, self.blueprints[name]

    def cycle_blueprint(self):
        self.selected_blueprint = (self.selected_blueprint + 1) % len(self.blueprint_names)
        name, bp = self.get_selected_blueprint()
        print(f"Estacao selecionada: {bp['name']}")

    def can_build(self, blueprint_name, inventory):
        bp = self.blueprints[blueprint_name]
        for item_type, qty in bp['cost'].items():
            if not inventory.has_item(item_type, qty):
                return False
        return True

    def build_station(self, blueprint_name, center_x, center_y, game_blocks, inventory):
        bp = self.blueprints[blueprint_name]

        if not self.can_build(blueprint_name, inventory):
            return False

        # Verifica espaco livre
        for dx, dy, _ in bp['layout']:
            bx = center_x + dx * BLOCK_SIZE
            by = center_y + dy * BLOCK_SIZE
            for block in game_blocks:
                if abs(block.x - bx) < BLOCK_SIZE and abs(block.y - by) < BLOCK_SIZE:
                    return False

        # Deduz recursos
        for item_type, qty in bp['cost'].items():
            inventory.remove_item(item_type, qty)

        # Coloca blocos
        station_blocks = []
        for dx, dy, block_type in bp['layout']:
            bx = center_x + dx * BLOCK_SIZE
            by = center_y + dy * BLOCK_SIZE
            block = Block(bx, by, block_type)
            game_blocks.append(block)
            station_blocks.append(block)

        station = SpaceStation(center_x, center_y, blueprint_name, station_blocks)
        self.stations.append(station)
        return True

    def apply_station_effects(self, spaceship):
        """Aplica efeitos de estacoes proximas"""
        for station in self.stations:
            dist = math.sqrt((spaceship.x - station.x) ** 2 + (spaceship.y - station.y) ** 2)
            if dist > 150:
                continue

            if station.station_type == 'REFUEL_STATION':
                spaceship.add_fuel(0.05)
                spaceship.add_oxygen(0.03)
            elif station.station_type == 'MINING_PLATFORM':
                # Boost temporario de range (sera resetado a cada frame)
                spaceship.mine_range = max(spaceship.mine_range, 80)

    def render_blueprint_info(self, surface):
        """Renderiza info da estacao selecionada no HUD.

        Phase 0.10 fix: previous version drew grey text directly onto the
        scene, which became invisible over bright planets. Now uses a
        semi-opaque panel + outlined text and reads from live display dims.
        """
        from utils import display
        from utils.font import get_font, render_outlined, draw_panel

        name, bp = self.get_selected_blueprint()
        font = get_font(20)

        cost_parts = [f"{qty} {t}" for t, qty in bp['cost'].items()]
        title_str   = f"Estacao: {bp['name']}"
        cost_str    = "Custo: " + ", ".join(cost_parts)
        benefit_str = bp['benefit']
        hint_str    = "B=construir estacao"

        title_surf   = render_outlined(font, title_str,   CYAN,        (0, 0, 0), 2)
        cost_surf    = render_outlined(font, cost_str,    LIGHT_GRAY,  (0, 0, 0), 2)
        benefit_surf = render_outlined(font, benefit_str, LIGHT_GRAY,  (0, 0, 0), 2)
        hint_surf    = render_outlined(font, hint_str,    (200, 200, 200), (0, 0, 0), 2)

        line_h = title_surf.get_height() + 2
        panel_w = max(title_surf.get_width(), cost_surf.get_width(),
                      benefit_surf.get_width(), hint_surf.get_width()) + 24
        panel_h = line_h * 4 + 14

        x = display.WIDTH - panel_w - 16
        y = display.HEIGHT - panel_h - 16
        rect = pygame.Rect(x, y, panel_w, panel_h)
        draw_panel(surface, rect, bg=(8, 12, 28), border=(40, 80, 120),
                   bg_alpha=210, border_width=1, radius=6)

        ty = y + 8
        surface.blit(title_surf,   (x + 12, ty));            ty += line_h
        surface.blit(cost_surf,    (x + 12, ty));            ty += line_h
        surface.blit(benefit_surf, (x + 12, ty));            ty += line_h
        surface.blit(hint_surf,    (x + 12, ty))
