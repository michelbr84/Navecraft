"""
Gamepad support - polls joysticks, exposes virtual buttons / axes, prompt switching.
"""

import pygame


class Gamepad:
    def __init__(self):
        self.joystick = None
        self.connected = False
        self.last_input_type = 'keyboard'
        try:
            pygame.joystick.init()
            self._scan()
        except pygame.error:
            pass

    def _scan(self):
        if pygame.joystick.get_count() > 0:
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()
            self.connected = True

    def update_input_type(self, event_type):
        if event_type in (pygame.KEYDOWN, pygame.KEYUP, pygame.MOUSEMOTION,
                          pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP):
            self.last_input_type = 'keyboard'
        elif event_type in (pygame.JOYBUTTONDOWN, pygame.JOYBUTTONUP, pygame.JOYAXISMOTION):
            self.last_input_type = 'gamepad'

    def axis(self, idx, deadzone=0.2):
        if not self.connected:
            return 0.0
        try:
            v = self.joystick.get_axis(idx)
            if abs(v) < deadzone:
                return 0.0
            return v
        except pygame.error:
            return 0.0

    def button(self, idx):
        if not self.connected:
            return False
        try:
            return bool(self.joystick.get_button(idx))
        except pygame.error:
            return False

    def get_movement_vector(self):
        """Left stick axes (0=X, 1=Y)."""
        dx = self.axis(0)
        dy = self.axis(1)
        return dx, dy

    def get_aim_vector(self):
        """Right stick axes (2 or 3, 3 or 4 depending on driver)."""
        # Common: axis 2/3 = right stick on Xbox; PS controllers vary
        return self.axis(3, 0.25), self.axis(4, 0.25) if self.connected else (0, 0)

    def rumble(self, low_freq=0.3, high_freq=0.3, duration_ms=200):
        if not self.connected:
            return
        try:
            self.joystick.rumble(low_freq, high_freq, duration_ms)
        except Exception:
            pass

    # Button mappings (Xbox layout)
    A = 0
    B = 1
    X = 2
    Y = 3
    LB = 4
    RB = 5
    BACK = 6
    START = 7

    def pressed_a(self):
        return self.button(self.A)

    def pressed_b(self):
        return self.button(self.B)


gamepad = Gamepad()
