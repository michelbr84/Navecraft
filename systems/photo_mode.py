"""
Photo mode - free camera, hide HUD, save PNG screenshots.
"""

import os
import time
import pygame
from utils import display


class PhotoMode:
    def __init__(self):
        self.active = False
        self.hide_hud = False
        self.cam_x = 0.0
        self.cam_y = 0.0
        self.zoom = 1.0

    def toggle(self):
        self.active = not self.active
        if self.active:
            self.hide_hud = False
            self.zoom = 1.0

    def pan(self, dx, dy):
        self.cam_x += dx * 5
        self.cam_y += dy * 5

    def adjust_zoom(self, delta):
        self.zoom = max(0.25, min(2.5, self.zoom + delta))

    def save_screenshot(self, surface):
        os.makedirs("screenshots", exist_ok=True)
        path = os.path.join("screenshots", f"navecraft_{int(time.time())}.png")
        try:
            pygame.image.save(surface, path)
            return path
        except Exception as e:
            print(f"[photo] save failed: {e}")
            return None


photo_mode = PhotoMode()
