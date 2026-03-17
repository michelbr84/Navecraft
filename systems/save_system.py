"""
Sistema de save/load do Navecraft
"""

import json
import os
import pygame
from settings import SAVE_FILE, AUTO_SAVE_INTERVAL


class SaveSystem:
    def __init__(self, save_file=SAVE_FILE):
        self.save_file = save_file
        self.last_save_time = 0

    def save_game(self, game):
        """Salva o estado do jogo em JSON"""
        try:
            data = {
                'version': 1,
                'score': game.score,
                'game_time': game.game_time,
                'spaceship': self._serialize_spaceship(game.spaceship),
                'inventory': dict(game.spaceship.inventory.items),
                'upgrades': dict(game.upgrade_system.applied_upgrades),
                'visited_planets': list(game.visited_planets),
            }

            with open(self.save_file, 'w') as f:
                json.dump(data, f, indent=2)

            print("Jogo salvo!")
            return True
        except Exception as e:
            print(f"Erro ao salvar: {e}")
            return False

    def load_game(self, game):
        """Carrega o estado do jogo de JSON"""
        if not self.has_save():
            print("Nenhum save encontrado!")
            return False

        try:
            with open(self.save_file, 'r') as f:
                data = json.load(f)

            if data.get('version', 0) != 1:
                print("Save incompativel!")
                return False

            # Restaura pontuacao e tempo
            game.score = data.get('score', 0)
            game.game_time = data.get('game_time', 0)

            # Restaura nave
            ship_data = data.get('spaceship', {})
            ship = game.spaceship
            ship.x = ship_data.get('x', ship.x)
            ship.y = ship_data.get('y', ship.y)
            ship.health = ship_data.get('health', ship.health)
            ship.max_health = ship_data.get('max_health', ship.max_health)
            ship.energy = ship_data.get('energy', ship.energy)
            ship.max_energy = ship_data.get('max_energy', ship.max_energy)
            ship.oxygen = ship_data.get('oxygen', ship.oxygen)
            ship.max_oxygen = ship_data.get('max_oxygen', ship.max_oxygen)
            ship.fuel = ship_data.get('fuel', ship.fuel)
            ship.max_fuel = ship_data.get('max_fuel', ship.max_fuel)
            ship.angle = ship_data.get('angle', ship.angle)
            ship.selected_block_type = ship_data.get('selected_block_type', 'IRON')

            # Restaura inventario
            inv_data = data.get('inventory', {})
            ship.inventory.items = {}
            for item_type, quantity in inv_data.items():
                ship.inventory.add_item(item_type, quantity)

            # Restaura upgrades
            upgrades_data = data.get('upgrades', {})
            game.upgrade_system.applied_upgrades = {}
            for upgrade_name, level in upgrades_data.items():
                for _ in range(level):
                    current = game.upgrade_system.applied_upgrades.get(upgrade_name, 0)
                    game.upgrade_system.applied_upgrades[upgrade_name] = current + 1
                    game.upgrade_system.apply_upgrade_effects(upgrade_name, current + 1)

            # Restaura planetas visitados
            game.visited_planets = set(data.get('visited_planets', []))

            print("Jogo carregado!")
            return True
        except Exception as e:
            print(f"Erro ao carregar: {e}")
            return False

    def has_save(self):
        """Verifica se existe um save"""
        return os.path.exists(self.save_file)

    def delete_save(self):
        """Deleta o save"""
        if self.has_save():
            os.remove(self.save_file)

    def check_autosave(self, game):
        """Verifica se deve fazer autosave"""
        current_time = pygame.time.get_ticks()
        if current_time - self.last_save_time > AUTO_SAVE_INTERVAL:
            self.save_game(game)
            self.last_save_time = current_time

    def _serialize_spaceship(self, ship):
        return {
            'x': ship.x,
            'y': ship.y,
            'health': ship.health,
            'max_health': ship.max_health,
            'energy': ship.energy,
            'max_energy': ship.max_energy,
            'oxygen': ship.oxygen,
            'max_oxygen': ship.max_oxygen,
            'fuel': ship.fuel,
            'max_fuel': ship.max_fuel,
            'angle': ship.angle,
            'selected_block_type': ship.selected_block_type,
        }
