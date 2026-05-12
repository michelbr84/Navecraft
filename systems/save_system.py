"""
Save/load system with multi-slot, autosave, backups, schema validation, thumbnails.

Format:
  navecraft_save_{slot}.json   - save file
  navecraft_save_{slot}.bak1   - rolling backup (kept last 3)
  navecraft_save_{slot}.png    - thumbnail screenshot
"""

import base64
import io
import json
import os
import time
import pygame
from settings import SAVE_FILE, AUTO_SAVE_INTERVAL


SCHEMA_VERSION = 2
MAX_SLOTS = 4
BACKUP_RETENTION = 3


class SaveSchemaError(Exception):
    pass


class SaveSystem:
    def __init__(self, save_file=None, slot=0):
        self.slot = slot
        # If a specific save_file was given (legacy / test), keep it; else use slot path.
        self.save_file = save_file if save_file else self._slot_path(slot)
        self.last_save_time = 0

    def _slot_path(self, slot):
        return f"navecraft_save_{slot}.json"

    def use_slot(self, slot):
        self.slot = slot
        self.save_file = self._slot_path(slot)

    # ----- serialization -----
    def _serialize_spaceship(self, ship):
        return {
            'x': ship.x, 'y': ship.y,
            'vx': ship.vx, 'vy': ship.vy,
            'angle': ship.angle,
            'health': ship.health, 'max_health': ship.max_health,
            'energy': ship.energy, 'max_energy': ship.max_energy,
            'oxygen': ship.oxygen, 'max_oxygen': ship.max_oxygen,
            'fuel': ship.fuel, 'max_fuel': ship.max_fuel,
            'selected_block_type': ship.selected_block_type,
        }

    def _capture_thumbnail(self, surface):
        try:
            thumb = pygame.transform.smoothscale(surface, (160, 100))
            buf = io.BytesIO()
            pygame.image.save(thumb, buf, namehint=".png")
            return base64.b64encode(buf.getvalue()).decode('ascii')
        except Exception:
            return None

    # ----- save / load -----
    def save_game(self, game, surface=None):
        try:
            data = {
                'version': SCHEMA_VERSION,
                'timestamp': time.time(),
                'slot': self.slot,
                'score': game.score,
                'game_time': game.game_time,
                'spaceship': self._serialize_spaceship(game.spaceship),
                'inventory': dict(game.spaceship.inventory.items),
                'upgrades': dict(getattr(game.upgrade_system, 'applied_upgrades', {})),
                'visited_planets': list(game.visited_planets),
                'difficulty': getattr(game, 'difficulty', 'normal'),
                'mode': getattr(game, 'mode', 'standard'),
                'thumbnail': self._capture_thumbnail(surface) if surface else None,
            }
            self._rotate_backups()
            with open(self.save_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            print(f"Jogo salvo (slot {self.slot})!")
            return True
        except Exception as e:
            print(f"Erro ao salvar: {e}")
            return False

    def _rotate_backups(self):
        if not os.path.exists(self.save_file):
            return
        # Shift back1->back2->back3
        for i in range(BACKUP_RETENTION, 1, -1):
            old_b = f"{self.save_file}.bak{i - 1}"
            new_b = f"{self.save_file}.bak{i}"
            if os.path.exists(old_b):
                try:
                    if os.path.exists(new_b):
                        os.remove(new_b)
                    os.rename(old_b, new_b)
                except Exception:
                    pass
        try:
            import shutil
            shutil.copy2(self.save_file, f"{self.save_file}.bak1")
        except Exception:
            pass

    def _validate_schema(self, data):
        required_top = ['version', 'score', 'game_time', 'spaceship']
        for k in required_top:
            if k not in data:
                raise SaveSchemaError(f"missing key: {k}")
        ship = data['spaceship']
        for k in ('x', 'y', 'health', 'max_health'):
            if k not in ship:
                raise SaveSchemaError(f"spaceship missing key: {k}")

    def load_game(self, game):
        if not self.has_save():
            print("Nenhum save encontrado!")
            return False
        try:
            with open(self.save_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            try:
                self._validate_schema(data)
            except SaveSchemaError as e:
                print(f"Save corrompido ({e}). Tentando backup...")
                if not self._restore_from_backup():
                    return False
                with open(self.save_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self._validate_schema(data)

            # Version migration (v1 -> v2 is forward-compatible)
            if data.get('version', 0) < 1:
                print("Save incompatível!")
                return False

            game.score = data.get('score', 0)
            game.game_time = data.get('game_time', 0)

            ship_data = data.get('spaceship', {})
            ship = game.spaceship
            for k in ('x', 'y', 'vx', 'vy', 'angle',
                      'health', 'max_health', 'energy', 'max_energy',
                      'oxygen', 'max_oxygen', 'fuel', 'max_fuel'):
                if k in ship_data:
                    setattr(ship, k, ship_data[k])
            ship.selected_block_type = ship_data.get('selected_block_type', 'IRON')

            inv_data = data.get('inventory', {})
            ship.inventory.items = {}
            for item_type, qty in inv_data.items():
                ship.inventory.add_item(item_type, qty)

            up_data = data.get('upgrades', {})
            if hasattr(game, 'upgrade_system'):
                game.upgrade_system.applied_upgrades = {}
                for upgrade_name, level in up_data.items():
                    for _ in range(level):
                        cur = game.upgrade_system.applied_upgrades.get(upgrade_name, 0)
                        game.upgrade_system.applied_upgrades[upgrade_name] = cur + 1
                        game.upgrade_system.apply_upgrade_effects(upgrade_name, cur + 1)

            game.visited_planets = set(data.get('visited_planets', []))
            print(f"Jogo carregado (slot {self.slot})!")
            return True
        except Exception as e:
            print(f"Erro ao carregar: {e}")
            return False

    def _restore_from_backup(self):
        for i in range(1, BACKUP_RETENTION + 1):
            bak = f"{self.save_file}.bak{i}"
            if os.path.exists(bak):
                try:
                    import shutil
                    shutil.copy2(bak, self.save_file)
                    print(f"Restaurado do backup bak{i}.")
                    return True
                except Exception:
                    continue
        return False

    def has_save(self):
        return os.path.exists(self.save_file)

    def delete_save(self):
        if self.has_save():
            os.remove(self.save_file)

    def check_autosave(self, game):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_save_time > AUTO_SAVE_INTERVAL:
            self.save_game(game)
            self.last_save_time = current_time

    # ----- multi-slot enumeration -----
    @staticmethod
    def list_slots():
        slots = []
        for i in range(MAX_SLOTS):
            path = f"navecraft_save_{i}.json"
            if os.path.exists(path):
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        d = json.load(f)
                    slots.append({
                        'slot': i,
                        'timestamp': d.get('timestamp', 0),
                        'score': d.get('score', 0),
                        'time_played': d.get('game_time', 0),
                        'has_thumbnail': bool(d.get('thumbnail')),
                    })
                except Exception:
                    slots.append({'slot': i, 'corrupt': True})
            else:
                slots.append({'slot': i, 'empty': True})
        return slots
