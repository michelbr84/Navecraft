"""
Smooth camera with lerp, lead-the-target, speed zoom, and shake hook.
"""

import math
from utils import display
from systems.feedback import feedback
from systems.accessibility import is_reduce_motion


class SmoothCamera:
    def __init__(self):
        self.x = 0.0
        self.y = 0.0
        self.target_x = 0.0
        self.target_y = 0.0
        self.zoom = 1.0
        self.target_zoom = 1.0
        self.smoothness = 0.12
        self.lead_factor = 8.0
        self.shake_x = 0.0
        self.shake_y = 0.0

    def follow(self, x, y, vx=0.0, vy=0.0):
        """Center on (x,y), leading slightly based on velocity."""
        sx, sy = display.WIDTH / 2.0, display.HEIGHT / 2.0
        lead_x = x + vx * self.lead_factor
        lead_y = y + vy * self.lead_factor
        self.target_x = lead_x - sx
        self.target_y = lead_y - sy

        # Speed-based zoom: faster = zoom out slightly
        if is_reduce_motion():
            self.target_zoom = 1.0
        else:
            speed = math.sqrt(vx * vx + vy * vy)
            self.target_zoom = max(0.85, 1.05 - speed * 0.015)

    def snap_to(self, x, y):
        sx, sy = display.WIDTH / 2.0, display.HEIGHT / 2.0
        self.target_x = x - sx
        self.target_y = y - sy
        self.x = self.target_x
        self.y = self.target_y

    def update(self):
        if is_reduce_motion():
            self.x = self.target_x
            self.y = self.target_y
            self.zoom = 1.0
        else:
            self.x += (self.target_x - self.x) * self.smoothness
            self.y += (self.target_y - self.y) * self.smoothness
            self.zoom += (self.target_zoom - self.zoom) * 0.05
        sx, sy = feedback.get_shake_offset()
        self.shake_x = sx
        self.shake_y = sy

    def render_offset(self):
        """Returns the camera-x, camera-y to subtract from world coords for rendering."""
        return self.x + self.shake_x, self.y + self.shake_y


camera = SmoothCamera()
