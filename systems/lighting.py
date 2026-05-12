"""
Simple 2D lighting - radial point lights composited as additive surfaces.
Ship engine, laser projectiles, explosions add light. Cheap; one per source.
"""

import pygame
from utils import display
from systems.accessibility import is_reduce_motion


class Light:
    __slots__ = ('x', 'y', 'radius', 'color', 'intensity', 'lifetime')

    def __init__(self, x, y, radius, color, intensity=1.0, lifetime=-1):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.intensity = intensity
        self.lifetime = lifetime  # -1 = persistent until removed


class LightingSystem:
    def __init__(self):
        self.lights = []
        self._sprite_cache = {}

    def add_persistent(self, x, y, radius, color, intensity=1.0):
        light = Light(x, y, radius, color, intensity, -1)
        self.lights.append(light)
        return light

    def add_transient(self, x, y, radius, color, intensity=1.0, lifetime=20):
        self.lights.append(Light(x, y, radius, color, intensity, lifetime))

    def clear_transients(self):
        self.lights = [l for l in self.lights if l.lifetime == -1]

    def update(self):
        for l in self.lights[:]:
            if l.lifetime > 0:
                l.lifetime -= 1
                l.intensity *= 0.92
                if l.lifetime <= 0 or l.intensity < 0.05:
                    self.lights.remove(l)

    def _light_sprite(self, radius, color):
        key = (radius, color)
        if key in self._sprite_cache:
            return self._sprite_cache[key]
        size = radius * 2
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        steps = 8
        for i in range(steps):
            r = int(radius * (1 - i / steps))
            alpha = int(180 * (1 - i / steps) ** 1.5)
            pygame.draw.circle(surf, (*color, alpha), (radius, radius), r)
        self._sprite_cache[key] = surf
        return surf

    def render(self, surface, camera_x, camera_y, ambient=0.85):
        if is_reduce_motion():
            return  # Skip lighting overlay entirely
        # Additive light pass: composite all lights onto a buffer, then overlay
        w, h = display.WIDTH, display.HEIGHT
        light_buf = pygame.Surface((w, h), pygame.SRCALPHA)
        light_buf.fill((int(255 * ambient), int(255 * ambient), int(255 * ambient), 0))
        for l in self.lights:
            sx = int(l.x - camera_x - l.radius)
            sy = int(l.y - camera_y - l.radius)
            if sx + l.radius * 2 < 0 or sy + l.radius * 2 < 0:
                continue
            if sx > w or sy > h:
                continue
            sprite = self._light_sprite(l.radius, l.color)
            light_buf.blit(sprite, (sx, sy), special_flags=pygame.BLEND_RGBA_ADD)
        surface.blit(light_buf, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)


lighting = LightingSystem()
