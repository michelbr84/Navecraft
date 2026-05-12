"""
Player spaceship - movement, mining, building, combat with juice (hit flash, recoil).
"""

import math
import random
import pygame
from settings import *
from systems.accessibility import colorblind_filter


class Projectile:
    """Laser projectile fired by the player."""

    def __init__(self, x, y, angle, owner='player'):
        self.x = x
        self.y = y
        self.vx = math.cos(angle) * LASER_SPEED
        self.vy = math.sin(angle) * LASER_SPEED
        self.size = 4
        self.damage = LASER_DAMAGE
        self.lifetime = 120
        self.owner = owner
        self.angle = angle

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.lifetime -= 1

    def is_alive(self):
        return self.lifetime > 0

    def render(self, surface, camera_x, camera_y):
        sx = int(self.x - camera_x)
        sy = int(self.y - camera_y)
        pygame.draw.circle(surface, CYAN, (sx, sy), self.size)
        # Trail with chromatic glow
        for i in range(3):
            tx = int(self.x - self.vx * (0.3 + 0.15 * i) - camera_x)
            ty = int(self.y - self.vy * (0.3 + 0.15 * i) - camera_y)
            alpha = 255 - i * 60
            color = (max(0, min(255, alpha // 2)), alpha, alpha)
            pygame.draw.circle(surface, color, (tx, ty), max(1, self.size - i))


class Spaceship:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.angle = 0.0
        self.size = SPACESHIP_SIZE
        self.health = SPACESHIP_HEALTH
        self.max_health = SPACESHIP_HEALTH
        self.energy = SPACESHIP_ENERGY
        self.max_energy = SPACESHIP_ENERGY
        self.oxygen = SPACESHIP_OXYGEN
        self.max_oxygen = SPACESHIP_OXYGEN
        self.fuel = 100
        self.max_fuel = 100
        self.last_shot_time = 0
        self.shooting = False
        self.last_mine_time = 0
        self.mining = False
        self.thrust_particles = []
        self.thrust_timer = 0
        self.mine_range = 50
        self.mine_damage = 25
        self.mine_cooldown = 500
        self.build_range = 60
        self.build_cooldown = 300
        self.last_build_time = 0
        self.selected_block_type = 'IRON'
        from systems.inventory import Inventory
        self.inventory = Inventory()
        self.max_speed = MAX_VELOCITY
        self.energy_efficiency = 1.0
        self.oxygen_efficiency = 1.0
        # Juice / animation
        self.hit_flash = 0  # frames remaining of red flash
        self.recoil_timer = 0  # backward kick anim
        self.recoil_dir = (0.0, 0.0)
        self.boosting = False
        self.last_damage_cause = None  # 'combat' | 'oxygen' | 'energy' | 'storm'
        self.last_mine_result = None  # dict with block_type, value
        self._panel_jitter_phase = 0.0
        # Damage taken stat (read by Game)
        self.damage_taken_this_frame = 0.0

    def update(self, input_manager):
        dx, dy = input_manager.get_movement_vector()
        # Aim with mouse if mouse moved this frame (gives mouse aiming + WASD movement)
        try:
            mx, my = input_manager.get_mouse_position()
            # If mouse moved away from center, use as facing direction
            self._mouse_target = (mx, my)
        except Exception:
            self._mouse_target = None

        if dx != 0 or dy != 0:
            move_angle = math.atan2(dy, dx)
            self.vx += math.cos(move_angle) * SPACESHIP_ACCELERATION
            self.vy += math.sin(move_angle) * SPACESHIP_ACCELERATION
            self.angle = move_angle

        # Apply recoil offset to velocity
        if self.recoil_timer > 0:
            self.vx += self.recoil_dir[0] * 0.5
            self.vy += self.recoil_dir[1] * 0.5
            self.recoil_timer -= 1

        self.vx *= SPACESHIP_DECELERATION
        self.vy *= SPACESHIP_DECELERATION
        speed = math.sqrt(self.vx ** 2 + self.vy ** 2)
        if speed > self.max_speed:
            self.vx = (self.vx / speed) * self.max_speed
            self.vy = (self.vy / speed) * self.max_speed
        self.x += self.vx
        self.y += self.vy
        self.x = max(0, min(self.x, WORLD_SIZE * BLOCK_SIZE))
        self.y = max(0, min(self.y, WORLD_SIZE * BLOCK_SIZE))
        self.update_thrust_particles()

        from systems.game_modes import GameMode
        creative = GameMode.is_creative()
        if dx != 0 or dy != 0:
            if not creative:
                self.consume_energy(0.1 * self.energy_efficiency)
                self.consume_fuel(0.02)
            self.boosting = True
        else:
            self.boosting = False

        if not creative:
            self.consume_oxygen(0.05 * self.oxygen_efficiency)
        self.regenerate_energy(0.02)

        if self.hit_flash > 0:
            self.hit_flash -= 1

        if not creative:
            if self.oxygen <= 0 and self.health > 0:
                self.last_damage_cause = 'oxygen'
                self.health = 0
            elif self.energy <= 0 and self.health > 0:
                self.last_damage_cause = 'energy'
                self.health = 0

    def create_thrust_particles(self):
        thrust_x = self.x - math.cos(self.angle) * self.size
        thrust_y = self.y - math.sin(self.angle) * self.size
        thrust_x += random.uniform(-4, 4)
        thrust_y += random.uniform(-4, 4)
        particle = {
            'x': thrust_x, 'y': thrust_y,
            'vx': -math.cos(self.angle) * random.uniform(2, 5),
            'vy': -math.sin(self.angle) * random.uniform(2, 5),
            'life': random.uniform(10, 20),
            'max_life': 20,
            'color': (255, 165, 0),
        }
        self.thrust_particles.append(particle)
        if len(self.thrust_particles) > 24:
            self.thrust_particles.pop(0)

    def update_thrust_particles(self):
        for p in self.thrust_particles[:]:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['life'] -= 1
            if p['life'] <= 0:
                self.thrust_particles.remove(p)

    # ----- rendering helpers used by Renderer -----
    def get_ship_points(self, x, y):
        front_x = x + math.cos(self.angle) * self.size
        front_y = y + math.sin(self.angle) * self.size
        back_left_x = x + math.cos(self.angle + math.pi * 2 / 3) * self.size * 0.5
        back_left_y = y + math.sin(self.angle + math.pi * 2 / 3) * self.size * 0.5
        back_right_x = x + math.cos(self.angle - math.pi * 2 / 3) * self.size * 0.5
        back_right_y = y + math.sin(self.angle - math.pi * 2 / 3) * self.size * 0.5
        return [(front_x, front_y), (back_left_x, back_left_y), (back_right_x, back_right_y)]

    def render_ship_details(self, surface, x, y):
        cockpit_x = x + math.cos(self.angle) * self.size * 0.3
        cockpit_y = y + math.sin(self.angle) * self.size * 0.3
        pygame.draw.circle(surface, (60, 80, 220), (int(cockpit_x), int(cockpit_y)), 4)
        pygame.draw.circle(surface, (160, 200, 255), (int(cockpit_x), int(cockpit_y)), 2)
        # Side panels (extra detail)
        for side in (1, -1):
            wing_x = x + math.cos(self.angle + side * math.pi / 2) * self.size * 0.45
            wing_y = y + math.sin(self.angle + side * math.pi / 2) * self.size * 0.45
            pygame.draw.line(surface, (255, 255, 255), (x, y), (int(wing_x), int(wing_y)), 3)
            pygame.draw.line(surface, (170, 200, 220), (x, y), (int(wing_x), int(wing_y)), 1)
            # Antenna tip
            tip_x = wing_x + math.cos(self.angle + side * math.pi / 2 + math.pi / 2) * 4
            tip_y = wing_y + math.sin(self.angle + side * math.pi / 2 + math.pi / 2) * 4
            pygame.draw.line(surface, (255, 200, 100),
                             (int(wing_x), int(wing_y)), (int(tip_x), int(tip_y)), 1)

    # ----- combat -----
    def shoot(self):
        from systems.game_modes import GameMode
        cost = 0 if GameMode.is_creative() else 10
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot_time > LASER_COOLDOWN and self.energy >= cost:
            self.last_shot_time = current_time
            self.consume_energy(cost)
            # Recoil
            self.recoil_timer = 6
            self.recoil_dir = (-math.cos(self.angle) * 0.4, -math.sin(self.angle) * 0.4)
            return True
        return False

    def mine(self, blocks):
        from systems.game_modes import GameMode
        cost = 0 if GameMode.is_creative() else 5
        current_time = pygame.time.get_ticks()
        if current_time - self.last_mine_time > self.mine_cooldown and self.energy >= cost:
            self.last_mine_time = current_time
            self.consume_energy(cost)
            for block in blocks:
                d = math.hypot(self.x - block.x, self.y - block.y)
                if d <= self.mine_range and not block.collected:
                    block.damage_flash = 6
                    if block.take_damage(self.mine_damage):
                        resource_value = block.collect()
                        if resource_value > 0:
                            self.inventory.add_item(block.block_type, resource_value)
                            self.last_mine_result = {'type': block.block_type, 'value': resource_value, 'x': block.x, 'y': block.y}
                            return resource_value
            return 0
        return 0

    def build(self, blocks, mouse_x, mouse_y):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_build_time > self.build_cooldown:
            from systems.game_modes import GameMode
            has_resource = GameMode.is_creative() or self.inventory.has_item(self.selected_block_type, 1)
            if has_resource:
                build_x = mouse_x
                build_y = mouse_y
                distance = math.hypot(self.x - build_x, self.y - build_y)
                if distance <= self.build_range:
                    for block in blocks:
                        if abs(block.x - build_x) < BLOCK_SIZE and abs(block.y - build_y) < BLOCK_SIZE:
                            return False
                    if not GameMode.is_creative():
                        self.inventory.remove_item(self.selected_block_type, 1)
                    from systems.generation import Block
                    new_block = Block(build_x, build_y, self.selected_block_type)
                    blocks.append(new_block)
                    self.last_build_time = current_time
                    return True
        return False

    def select_block_type(self, block_type):
        if block_type in ['IRON', 'GOLD', 'CRYSTAL', 'FUEL', 'OXYGEN']:
            self.selected_block_type = block_type

    def take_damage(self, damage, source='combat'):
        from systems.game_modes import GameMode
        if GameMode.is_creative():
            return
        before = self.health
        self.health = max(0, self.health - damage)
        diff = before - self.health
        self.damage_taken_this_frame += diff
        self.hit_flash = 8
        self.recoil_timer = max(self.recoil_timer, 4)
        if self.health <= 0 and self.last_damage_cause is None:
            self.last_damage_cause = source

    def heal(self, amount):
        self.health = min(self.max_health, self.health + amount)

    def consume_energy(self, amount):
        self.energy = max(0, self.energy - amount)

    def regenerate_energy(self, amount):
        self.energy = min(self.max_energy, self.energy + amount)

    def consume_oxygen(self, amount):
        self.oxygen = max(0, self.oxygen - amount)

    def add_oxygen(self, amount):
        self.oxygen = min(self.max_oxygen, self.oxygen + amount)

    def consume_fuel(self, amount):
        self.fuel = max(0, self.fuel - amount)

    def add_fuel(self, amount):
        self.fuel = min(self.max_fuel, self.fuel + amount)

    def collides_with(self, entity):
        return math.hypot(self.x - entity.x, self.y - entity.y) < (self.size + entity.size) / 2

    def get_position(self):
        return self.x, self.y

    def get_velocity(self):
        return self.vx, self.vy

    def is_alive(self):
        return self.health > 0
