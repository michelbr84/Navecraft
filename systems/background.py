"""
Layered parallax background with nebulas, distant planets, and ambient asteroids.
"""

import math
import random
import pygame
from utils import display
from settings import SEED
from systems.accessibility import is_reduce_motion


class BackgroundSystem:
    def __init__(self):
        rng = random.Random(SEED)
        # Three star layers with different parallax depths
        self.layers = []
        for depth in (0.05, 0.15, 0.35):
            stars = []
            count = 250 if depth < 0.1 else 150 if depth < 0.2 else 80
            for _ in range(count):
                x = rng.randint(0, 4000)
                y = rng.randint(0, 4000)
                brightness = rng.randint(80, 255)
                size = 1 if depth < 0.15 else rng.choice([1, 2])
                stars.append((x, y, brightness, size, rng.uniform(0, math.pi * 2)))
            self.layers.append({'depth': depth, 'stars': stars, 'tile': 4000})

        # Nebulas (one-time procedurally-rendered surface, blitted with parallax)
        self.nebulas = []
        for _ in range(4):
            x = rng.randint(-1000, 4000)
            y = rng.randint(-1000, 4000)
            color = rng.choice([(80, 0, 120), (0, 60, 120), (120, 30, 100), (60, 30, 100)])
            radius = rng.randint(220, 420)
            self.nebulas.append({'x': x, 'y': y, 'color': color, 'radius': radius,
                                  'surface': self._make_nebula(radius, color)})

        # Distant planets (very far parallax)
        self.distant_planets = []
        for _ in range(3):
            self.distant_planets.append({
                'x': rng.randint(-500, 4000),
                'y': rng.randint(-500, 4000),
                'radius': rng.randint(30, 70),
                'color': rng.choice([(220, 140, 80), (80, 100, 200), (180, 200, 220)]),
            })

        # Distant asteroids drifting in deep background
        self.drift_asteroids = []
        for _ in range(20):
            self.drift_asteroids.append({
                'x': rng.uniform(0, 3000),
                'y': rng.uniform(0, 3000),
                'vx': rng.uniform(-0.2, 0.2),
                'vy': rng.uniform(-0.2, 0.2),
                'r': rng.randint(2, 5),
            })
        self.aurora_phase = 0.0
        self.aurora_chance = 0.0005
        self.aurora_active = False
        self.aurora_timer = 0

    def _make_nebula(self, radius, color):
        size = radius * 2
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        steps = 8
        for i in range(steps):
            r = int(radius * (1 - i / steps))
            alpha = int(50 * (1 - i / steps) ** 2)
            pygame.draw.circle(surf, (*color, alpha), (radius, radius), r)
        return surf

    def update(self):
        for ast in self.drift_asteroids:
            ast['x'] += ast['vx']
            ast['y'] += ast['vy']
        self.aurora_phase += 0.01
        if not self.aurora_active and not is_reduce_motion():
            if random.random() < self.aurora_chance:
                self.aurora_active = True
                self.aurora_timer = 600
        if self.aurora_active:
            self.aurora_timer -= 1
            if self.aurora_timer <= 0:
                self.aurora_active = False

    def render(self, surface, camera_x, camera_y):
        w, h = display.WIDTH, display.HEIGHT

        # Distant planets (very slow parallax)
        for p in self.distant_planets:
            dpx = p['x'] - camera_x * 0.02
            dpy = p['y'] - camera_y * 0.02
            # Tile
            tile = 4000
            dpx = dpx % tile
            dpy = dpy % tile
            if dpx > w + 100 or dpy > h + 100:
                continue
            pygame.draw.circle(surface, p['color'], (int(dpx), int(dpy)), p['radius'])
            pygame.draw.circle(surface, (255, 255, 255), (int(dpx), int(dpy)), p['radius'], 1)

        # Nebulas (slow parallax)
        for n in self.nebulas:
            nx = (n['x'] - camera_x * 0.08) % 4000
            ny = (n['y'] - camera_y * 0.08) % 4000
            surface.blit(n['surface'], (int(nx - n['radius']), int(ny - n['radius'])))

        # Drift asteroids
        for ast in self.drift_asteroids:
            ax = (ast['x'] - camera_x * 0.12) % 3000
            ay = (ast['y'] - camera_y * 0.12) % 3000
            pygame.draw.circle(surface, (90, 90, 110), (int(ax), int(ay)), ast['r'])

        # Star layers (true parallax)
        for layer in self.layers:
            depth = layer['depth']
            tile = layer['tile']
            for (sx, sy, brightness, size, twinkle) in layer['stars']:
                lx = (sx - camera_x * depth) % tile
                ly = (sy - camera_y * depth) % tile
                if lx > w or ly > h:
                    continue
                if not is_reduce_motion():
                    tw = math.sin(twinkle + self.aurora_phase * 3) * 0.2 + 0.8
                else:
                    tw = 1.0
                b = max(0, min(255, int(brightness * tw)))
                if size == 1:
                    surface.set_at((int(lx), int(ly)), (b, b, b))
                else:
                    pygame.draw.circle(surface, (b, b, b), (int(lx), int(ly)), size)

        # Aurora event - subtle color tint
        if self.aurora_active:
            overlay = pygame.Surface((w, h), pygame.SRCALPHA)
            phase = math.sin(self.aurora_phase * 2) * 30 + 50
            overlay.fill((0, int(phase), int(phase * 1.5), 12))
            surface.blit(overlay, (0, 0))


background = BackgroundSystem()
