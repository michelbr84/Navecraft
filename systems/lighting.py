"""
Simple 2D lighting - radial point lights composited as additive surfaces.
Ship engine, laser projectiles, explosions add light. Cheap; one per source.
"""

import numpy as np
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

    def _light_sprite(self, radius, color, intensity=1.0):
        """Build a translucent radial-gradient light sprite.

        Phase 0.6 fix: previous implementation stamped 8–12 concentric circles
        with descending alpha onto an SRCALPHA surface. Pygame's draw uses
        source-over compositing on SRCALPHA, so each inner circle ADDED alpha
        on top of the outer ones, leaving the center near-opaque and producing
        a saturated white halo after additive blit. We now build a true radial
        gradient with numpy so center alpha == peak_alpha exactly, falling off
        quadratically to zero at the radius. Cache keyed on (radius, color,
        bucketed intensity) to keep memory bounded.
        """
        ibucket = max(0.0, min(1.0, round(intensity * 5) / 5.0))
        key = (radius, color, ibucket)
        if key in self._sprite_cache:
            return self._sprite_cache[key]
        size = max(2, radius * 2)
        peak_alpha = 180 * ibucket  # 0..180 — controls the gradient strength

        # Build a quadratic radial falloff in [0, 1].
        y, x = np.ogrid[0:size, 0:size]
        d = np.sqrt((x - radius) ** 2 + (y - radius) ** 2)
        falloff = np.clip(1.0 - d / max(radius, 1), 0.0, 1.0) ** 2  # (size, size) float

        # CRITICAL: pygame's BLEND_RGBA_ADD ignores per-pixel source alpha and
        # adds source RGB directly. So we must PREMULTIPLY the gradient into
        # the RGB channels — otherwise every pixel of the sprite would dump
        # the full base color onto dst and a half-dozen stacked lights would
        # saturate the screen white. (This is the actual Phase 0.6 root cause.)
        contribution = falloff * (peak_alpha / 255.0)  # 0..ibucket effective gain
        r_arr = (color[0] * contribution).astype(np.uint8)
        g_arr = (color[1] * contribution).astype(np.uint8)
        b_arr = (color[2] * contribution).astype(np.uint8)

        # Compose RGBA buffer. numpy axes are (y, x); pygame.image.frombuffer
        # expects row-major (height, width, channels) data, then a (w, h) size.
        rgba = np.stack([r_arr, g_arr, b_arr,
                         (falloff * peak_alpha).astype(np.uint8)], axis=-1)
        surf = pygame.image.frombuffer(rgba.tobytes(), (size, size), 'RGBA').convert_alpha()
        self._sprite_cache[key] = surf
        return surf

    def render(self, surface, camera_x, camera_y, ambient=1.0):
        # ambient < 1.0 darkens the scene (multiplicative); lights are then added on top.
        # Default ambient=1.0 means "no darkening" — additive lights only.
        if is_reduce_motion():
            return  # Skip lighting overlay entirely
        w, h = display.WIDTH, display.HEIGHT

        # 1) Optional darkening pass (only when ambient < 1.0).
        if ambient < 1.0:
            v = int(255 * max(0.0, min(1.0, ambient)))
            dark = pygame.Surface((w, h))
            dark.fill((v, v, v))
            surface.blit(dark, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

        # 2) Additive light pass: composite lights onto a transparent buffer.
        if not self.lights:
            return
        light_buf = pygame.Surface((w, h), pygame.SRCALPHA)
        # Buffer starts fully transparent — DO NOT pre-fill with RGB > 0.
        # A pre-fill with non-zero RGB and BLEND_RGBA_ADD turns the whole screen white.
        for l in self.lights:
            sx = int(l.x - camera_x - l.radius)
            sy = int(l.y - camera_y - l.radius)
            if sx + l.radius * 2 < 0 or sy + l.radius * 2 < 0:
                continue
            if sx > w or sy > h:
                continue
            sprite = self._light_sprite(l.radius, l.color, l.intensity)
            light_buf.blit(sprite, (sx, sy), special_flags=pygame.BLEND_RGBA_ADD)
        surface.blit(light_buf, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)


lighting = LightingSystem()
