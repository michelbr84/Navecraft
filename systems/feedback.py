"""
Feedback system - floating text, hitstop, screen flashes, camera shake, slow-mo.
"""

import math
import random
import pygame
from utils import display
from utils.font import get_font, render_outlined
from systems.accessibility import is_reduce_motion


class FloatingText:
    """A short text label that floats upward and fades out."""

    def __init__(self, x, y, text, color=(255, 255, 255), lifetime=60, vy=-1.5, size=20, world_space=True):
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.vy = vy
        self.size = size
        self.world_space = world_space

    def update(self):
        self.y += self.vy
        self.lifetime -= 1

    def is_alive(self):
        return self.lifetime > 0

    def render(self, surface, camera_x, camera_y):
        alpha_ratio = max(0.0, min(1.0, self.lifetime / self.max_lifetime))
        if alpha_ratio <= 0:
            return
        font = get_font(self.size)
        col = tuple(int(c * alpha_ratio + 255 * (1 - alpha_ratio) * 0.0) for c in self.color)
        text_surf = render_outlined(font, self.text, col, (0, 0, 0), outline_width=2)
        text_surf.set_alpha(int(alpha_ratio * 255))
        if self.world_space:
            sx = int(self.x - camera_x - text_surf.get_width() // 2)
            sy = int(self.y - camera_y - text_surf.get_height() // 2)
        else:
            sx = int(self.x - text_surf.get_width() // 2)
            sy = int(self.y - text_surf.get_height() // 2)
        surface.blit(text_surf, (sx, sy))


class FeedbackSystem:
    """Centralized juice — floating text, hitstop, flash, shake, slow-mo."""

    def __init__(self):
        self.texts = []
        self.hitstop_frames = 0  # time-paused frames remaining
        self.shake_intensity = 0.0
        self.shake_duration = 0
        self.flash_color = None
        self.flash_alpha = 0
        self.flash_decay = 12
        self.vignette_intensity = 0.0
        self.slowmo_factor = 1.0
        self.slowmo_remaining = 0

    # --- Floating text ---
    def floating(self, x, y, text, color=(255, 255, 0), lifetime=50, size=22, world_space=True):
        if len(self.texts) > 80:
            self.texts.pop(0)
        self.texts.append(FloatingText(x, y, text, color, lifetime, vy=-1.5, size=size, world_space=world_space))

    def damage_number(self, x, y, amount, color=(255, 100, 100)):
        self.floating(x + random.uniform(-10, 10), y - 20, str(int(amount)), color=color, lifetime=40, size=20)

    # --- Hitstop ---
    def hitstop(self, frames=4):
        if is_reduce_motion():
            return
        if frames > self.hitstop_frames:
            self.hitstop_frames = frames

    # --- Screen flash ---
    def flash(self, color=(255, 255, 255), strength=120, decay=12):
        if is_reduce_motion():
            strength = strength // 3
        self.flash_color = color
        self.flash_alpha = strength
        self.flash_decay = decay

    # --- Camera shake ---
    def shake(self, intensity=6.0, frames=10):
        if is_reduce_motion():
            return
        if intensity > self.shake_intensity:
            self.shake_intensity = intensity
            self.shake_duration = frames

    def get_shake_offset(self):
        if self.shake_intensity <= 0 or self.shake_duration <= 0:
            return 0, 0
        a = random.uniform(0, math.pi * 2)
        r = self.shake_intensity * (self.shake_duration / 10.0)
        return math.cos(a) * r, math.sin(a) * r

    # --- Slow-motion ---
    def slowmo(self, factor=0.3, frames=30):
        if is_reduce_motion():
            return
        self.slowmo_factor = factor
        self.slowmo_remaining = frames

    def time_scale(self):
        if self.slowmo_remaining > 0:
            return self.slowmo_factor
        return 1.0

    # --- Vignette ---
    def set_vignette(self, intensity):
        self.vignette_intensity = max(0.0, min(1.0, intensity))

    # --- Lifecycle ---
    def update(self):
        for t in self.texts[:]:
            t.update()
            if not t.is_alive():
                self.texts.remove(t)
        if self.hitstop_frames > 0:
            self.hitstop_frames -= 1
        if self.shake_duration > 0:
            self.shake_duration -= 1
            if self.shake_duration <= 0:
                self.shake_intensity = 0.0
        if self.flash_alpha > 0:
            self.flash_alpha = max(0, self.flash_alpha - self.flash_decay)
        if self.slowmo_remaining > 0:
            self.slowmo_remaining -= 1
            if self.slowmo_remaining <= 0:
                self.slowmo_factor = 1.0

    def render_world(self, surface, camera_x, camera_y):
        for t in self.texts:
            if t.world_space:
                t.render(surface, camera_x, camera_y)

    def render_screen(self, surface):
        # Non-world (HUD-space) texts
        for t in self.texts:
            if not t.world_space:
                t.render(surface, 0, 0)
        # Flash
        if self.flash_color and self.flash_alpha > 0:
            overlay = pygame.Surface((display.WIDTH, display.HEIGHT), pygame.SRCALPHA)
            overlay.fill((*self.flash_color, self.flash_alpha))
            surface.blit(overlay, (0, 0))
        # Vignette
        if self.vignette_intensity > 0:
            self._render_vignette(surface)

    def _render_vignette(self, surface):
        w, h = display.WIDTH, display.HEIGHT
        vignette = pygame.Surface((w, h), pygame.SRCALPHA)
        intensity = int(self.vignette_intensity * 180)
        steps = 6
        cx, cy = w // 2, h // 2
        max_r = int(math.sqrt(cx * cx + cy * cy))
        for i in range(steps):
            r = int(max_r * (1 - i / steps))
            alpha = int(intensity * (i / steps))
            pygame.draw.circle(vignette, (0, 0, 0, alpha), (cx, cy), r, width=max_r // steps + 2)
        surface.blit(vignette, (0, 0))

    def is_paused_by_hitstop(self):
        return self.hitstop_frames > 0


feedback = FeedbackSystem()
