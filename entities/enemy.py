"""
Enemy AI with juice - hit-flash, wind-up telegraph, ranged projectiles.
"""

import math
import random
import pygame
from settings import *


class Enemy:
    def __init__(self, x, y, enemy_type):
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        self.enemy_type = enemy_type
        self.size = 24
        self.health = ENEMY_HEALTH
        self.max_health = ENEMY_HEALTH
        self.damage = ENEMY_DAMAGE
        self.state = "patrol"
        self.target = None
        self.last_attack_time = 0
        self.attack_cooldown = 1000
        # Juice
        self.hit_flash = 0
        self.windup_timer = 0
        self.windup_duration = 25  # frames of telegraph before attack
        self.last_hit_at = 0
        self.setup_enemy_type()

    def setup_enemy_type(self):
        from systems.game_modes import difficulty_multiplier
        hp_mul, dmg_mul, _ = difficulty_multiplier()
        if self.enemy_type == "DRONE":
            self.speed = ENEMY_SPEED * 1.5
            self.attack_range = 100
            self.detection_range = 150
            self.color = RED
        elif self.enemy_type == "ANDROID":
            self.speed = ENEMY_SPEED * 0.8
            self.attack_range = 80
            self.detection_range = 120
            self.color = MAGENTA
        elif self.enemy_type == "SNIPER":
            self.speed = ENEMY_SPEED * 0.6
            self.attack_range = 220
            self.detection_range = 280
            self.color = YELLOW
        elif self.enemy_type == "ARACHNOID":
            self.speed = ENEMY_SPEED * 1.2
            self.attack_range = 60
            self.detection_range = 100
            self.color = GREEN
        else:
            self.speed = ENEMY_SPEED
            self.attack_range = 80
            self.detection_range = 120
            self.color = RED
        self.health = int(ENEMY_HEALTH * hp_mul)
        self.max_health = self.health
        self.damage = int(ENEMY_DAMAGE * dmg_mul)

    def update(self, spaceship):
        if not spaceship:
            return
        dx = spaceship.x - self.x
        dy = spaceship.y - self.y
        distance = math.hypot(dx, dy)
        if distance <= self.attack_range:
            self.state = "attack"
        elif distance <= self.detection_range:
            self.state = "chase"
        else:
            self.state = "patrol"

        if self.state == "patrol":
            self.patrol_behavior()
        elif self.state == "chase":
            self.chase_behavior(spaceship)
        elif self.state == "attack":
            self.attack_behavior(spaceship)

        if self.hit_flash > 0:
            self.hit_flash -= 1

    def patrol_behavior(self):
        if random.random() < 0.02:
            angle = random.uniform(0, math.pi * 2)
            self.vx = math.cos(angle) * self.speed * 0.5
            self.vy = math.sin(angle) * self.speed * 0.5
        self.x += self.vx
        self.y += self.vy
        speed = math.hypot(self.vx, self.vy)
        if speed > self.speed:
            self.vx = (self.vx / speed) * self.speed
            self.vy = (self.vy / speed) * self.speed

    def chase_behavior(self, spaceship):
        dx = spaceship.x - self.x
        dy = spaceship.y - self.y
        d = math.hypot(dx, dy)
        if d > 0:
            self.vx = dx / d * self.speed
            self.vy = dy / d * self.speed
        self.x += self.vx
        self.y += self.vy

    def attack_behavior(self, spaceship):
        current_time = pygame.time.get_ticks()
        if self.windup_timer > 0:
            self.windup_timer -= 1
            # During windup, freeze
            return
        if current_time - self.last_attack_time > self.attack_cooldown:
            # Start windup
            self.windup_timer = self.windup_duration
            self.last_attack_time = current_time
            # Resolve at end of windup via separate callback below
            pygame.time.set_timer(pygame.USEREVENT + 1, 0, loops=0)  # no-op cosmetic
            self._pending_attack = spaceship

    def deliver_attack_if_due(self, projectile_pool):
        """Called every frame by Game; if windup just finished, do the actual attack."""
        if hasattr(self, '_pending_attack') and self.windup_timer == 0 and self._pending_attack is not None:
            spaceship = self._pending_attack
            self._pending_attack = None
            if not spaceship:
                return
            dist = math.hypot(spaceship.x - self.x, spaceship.y - self.y)
            if dist > self.attack_range * 1.2:
                return
            if self.enemy_type == "DRONE":
                self.suicide_attack(spaceship)
            elif self.enemy_type == "SNIPER":
                # Fires a projectile instead of instant damage
                from entities.spaceship import Projectile
                angle = math.atan2(spaceship.y - self.y, spaceship.x - self.x)
                proj = Projectile(self.x, self.y, angle, owner='enemy')
                proj.damage = self.damage
                projectile_pool.append(proj)
            else:
                self.normal_attack(spaceship)

    def suicide_attack(self, spaceship):
        spaceship.take_damage(self.damage * 2, source='combat')
        self.health = 0

    def normal_attack(self, spaceship):
        spaceship.take_damage(self.damage, source='combat')

    def take_damage(self, damage):
        self.health = max(0, self.health - damage)
        self.hit_flash = 6
        self.last_hit_at = pygame.time.get_ticks()
        return self.health <= 0

    def render(self, surface, camera_x, camera_y):
        sx = int(self.x - camera_x)
        sy = int(self.y - camera_y)
        if self.enemy_type == "DRONE":
            self.render_drone(surface, sx, sy)
        elif self.enemy_type == "ANDROID":
            self.render_android(surface, sx, sy)
        elif self.enemy_type == "SNIPER":
            self.render_sniper(surface, sx, sy)
        elif self.enemy_type == "ARACHNOID":
            self.render_arachnoid(surface, sx, sy)
        else:
            self.render_generic(surface, sx, sy)

        # Hit flash overlay
        if self.hit_flash > 0:
            flash_alpha = int(180 * self.hit_flash / 6)
            flash_surf = pygame.Surface((self.size * 3, self.size * 3), pygame.SRCALPHA)
            pygame.draw.circle(flash_surf, (255, 255, 255, flash_alpha),
                               (self.size * 3 // 2, self.size * 3 // 2), self.size + 4)
            surface.blit(flash_surf, (sx - self.size * 3 // 2, sy - self.size * 3 // 2))

        # Windup telegraph - growing ring
        if self.windup_timer > 0:
            pct = 1.0 - (self.windup_timer / self.windup_duration)
            ring_r = int(self.size + 4 + pct * 14)
            pygame.draw.circle(surface, (255, 80, 80), (sx, sy), ring_r, 2)

        self.render_health_bar(surface, sx, sy)

    def render_drone(self, surface, x, y):
        pygame.draw.circle(surface, self.color, (x, y), self.size)
        pygame.draw.circle(surface, WHITE, (x, y), self.size, 2)
        for ex, ey in [(-8, -8), (8, -8), (-8, 8), (8, 8)]:
            pygame.draw.circle(surface, RED, (x + ex, y + ey), 3)

    def render_android(self, surface, x, y):
        rect = pygame.Rect(x - self.size // 2, y - self.size // 2, self.size, self.size)
        pygame.draw.rect(surface, self.color, rect)
        pygame.draw.rect(surface, WHITE, rect, 2)
        pygame.draw.circle(surface, RED, (x - 5, y - 5), 2)
        pygame.draw.circle(surface, RED, (x + 5, y - 5), 2)

    def render_sniper(self, surface, x, y):
        points = [
            (x, y - self.size),
            (x - self.size // 2, y + self.size // 2),
            (x + self.size // 2, y + self.size // 2),
        ]
        pygame.draw.polygon(surface, self.color, points)
        pygame.draw.polygon(surface, WHITE, points, 2)
        pygame.draw.circle(surface, RED, (x, y), 3)

    def render_arachnoid(self, surface, x, y):
        pygame.draw.circle(surface, self.color, (x, y), self.size // 2)
        pygame.draw.circle(surface, WHITE, (x, y), self.size // 2, 2)
        for i in range(8):
            a = i * math.pi / 4 + pygame.time.get_ticks() * 0.002
            lx = x + math.cos(a) * self.size
            ly = y + math.sin(a) * self.size
            pygame.draw.line(surface, self.color, (x, y), (int(lx), int(ly)), 2)

    def render_generic(self, surface, x, y):
        pygame.draw.circle(surface, self.color, (x, y), self.size)
        pygame.draw.circle(surface, WHITE, (x, y), self.size, 2)

    def render_health_bar(self, surface, x, y):
        if self.health >= self.max_health:
            return
        bar_width = self.size * 2
        bar_height = 4
        bar_x = x - bar_width // 2
        bar_y = y - self.size - 10
        pygame.draw.rect(surface, DARK_GRAY, (bar_x, bar_y, bar_width, bar_height))
        ratio = self.health / max(self.max_health, 1)
        width = int(bar_width * ratio)
        color = GREEN if ratio > 0.6 else (YELLOW if ratio > 0.3 else RED)
        pygame.draw.rect(surface, color, (bar_x, bar_y, width, bar_height))
        pygame.draw.rect(surface, WHITE, (bar_x, bar_y, bar_width, bar_height), 1)

    def collides_with(self, entity):
        return math.hypot(self.x - entity.x, self.y - entity.y) < (self.size + entity.size) / 2

    def is_alive(self):
        return self.health > 0
