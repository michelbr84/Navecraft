"""
Day/night cycle on planets - subtle ambient tint based on world time.
"""

import math


class DayNightCycle:
    def __init__(self, period_seconds=180.0):
        self.period = period_seconds
        self.t = 0.0

    def update(self, dt):
        self.t = (self.t + dt) % self.period

    def phase(self):
        """0..1, where 0=midnight, 0.5=noon."""
        return self.t / self.period

    def ambient_tint(self):
        """Return an (r,g,b) tint factor where 1.0=daylight, lower=dimmer."""
        phase = self.phase()
        # Cosine eased: bright at 0.5, dim at 0 and 1
        intensity = 0.55 + 0.45 * (math.cos((phase - 0.5) * math.pi * 2) + 1) / 2
        # Slight blue at night, slight warm at day
        if phase < 0.25 or phase > 0.75:
            return (int(intensity * 200), int(intensity * 220), int(intensity * 255))
        else:
            return (int(intensity * 255), int(intensity * 245), int(intensity * 230))


day_night = DayNightCycle()
