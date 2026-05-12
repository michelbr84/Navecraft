"""
Mini-bosses - bigger, multi-phase enemies. Trigger camera shake/zoom-in on appearance.
"""

import math
import pygame
from entities.enemy import Enemy
from systems.feedback import feedback


class MiniBoss(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, 'BOSS_DREADNAUGHT')
        self.size = 56
        self.max_health = 350
        self.health = self.max_health
        self.damage = 18
        self.speed = 1.4
        self.attack_range = 140
        self.detection_range = 320
        self.color = (200, 50, 200)
        self.phase = 1
        self.last_special = 0
        self.special_cooldown = 4000

    def update(self, spaceship):
        super().update(spaceship)
        # Phase transition at half HP
        if self.phase == 1 and self.health < self.max_health * 0.5:
            self.phase = 2
            self.speed *= 1.4
            self.attack_range = 180
            self.special_cooldown = 2500
            feedback.flash(color=(255, 80, 200), strength=80)
            feedback.shake(intensity=8, frames=20)
        # Special attack: radial burst
        if spaceship and self.state == 'attack':
            now = pygame.time.get_ticks()
            if now - self.last_special > self.special_cooldown:
                self.last_special = now
                self._radial_burst(spaceship)

    def _radial_burst(self, spaceship):
        # Tag-along: just deal AoE damage if in range, plus a screen-flash cue
        dist = math.hypot(spaceship.x - self.x, spaceship.y - self.y)
        if dist < 220:
            spaceship.take_damage(self.damage)
            feedback.flash(color=(255, 100, 100), strength=80)

    def render(self, surface, camera_x, camera_y):
        sx = int(self.x - camera_x)
        sy = int(self.y - camera_y)
        # Outer ring
        pygame.draw.circle(surface, (255, 0, 200), (sx, sy), self.size + 4, 3)
        pygame.draw.circle(surface, self.color, (sx, sy), self.size)
        pygame.draw.circle(surface, (255, 255, 255), (sx, sy), self.size, 2)
        # Spikes
        for i in range(8):
            a = i * math.pi / 4 + pygame.time.get_ticks() * 0.001
            ex = sx + math.cos(a) * (self.size + 12)
            ey = sy + math.sin(a) * (self.size + 12)
            pygame.draw.line(surface, (255, 0, 100), (sx, sy), (int(ex), int(ey)), 2)
        # HP bar
        bar_w = self.size * 2
        ratio = max(0.0, self.health / self.max_health)
        pygame.draw.rect(surface, (30, 30, 30), (sx - bar_w // 2, sy - self.size - 16, bar_w, 6))
        pygame.draw.rect(surface, (255, 50, 50), (sx - bar_w // 2, sy - self.size - 16, int(bar_w * ratio), 6))
        pygame.draw.rect(surface, (255, 255, 255), (sx - bar_w // 2, sy - self.size - 16, bar_w, 6), 1)
