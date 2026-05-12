"""
Space weather - solar storms that affect ship systems.
"""

import random
from systems.feedback import feedback


class SolarStorm:
    def __init__(self, duration=300):
        self.duration = duration
        self.lifetime = duration


class WeatherSystem:
    def __init__(self):
        self.active_storm = None
        self.next_storm_in = random.randint(60 * 60, 120 * 60)  # 1-2 min at 60 FPS

    def update(self, spaceship):
        if self.active_storm:
            self.active_storm.lifetime -= 1
            if spaceship:
                spaceship.consume_energy(0.05)
            if random.random() < 0.005:
                feedback.flash(color=(100, 100, 255), strength=40)
                feedback.shake(intensity=2, frames=4)
            if self.active_storm.lifetime <= 0:
                self.active_storm = None
                self.next_storm_in = random.randint(60 * 60, 120 * 60)
        else:
            self.next_storm_in -= 1
            if self.next_storm_in <= 0:
                self.active_storm = SolarStorm(duration=random.randint(180, 480))
                feedback.floating(0, 0, "TEMPESTADE SOLAR", color=(255, 100, 100),
                                  lifetime=120, size=28, world_space=False)
                feedback.shake(intensity=4, frames=12)

    def is_active(self):
        return self.active_storm is not None


weather = WeatherSystem()
