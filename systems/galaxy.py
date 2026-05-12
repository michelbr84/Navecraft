"""
Galaxy - multiple solar systems, warp navigation. Each system is a Game world seed.
"""

import random
from systems.planet_names import generate_system_name


class SolarSystem:
    def __init__(self, system_id, x, y, seed, name=None):
        self.id = system_id
        self.x = x  # Galactic coordinate
        self.y = y
        self.seed = seed
        self.name = name or generate_system_name(seed)
        self.visited = False


class Galaxy:
    def __init__(self, seed=42, num_systems=12):
        rng = random.Random(seed)
        self.systems = []
        for i in range(num_systems):
            sys = SolarSystem(
                system_id=i,
                x=rng.uniform(-1000, 1000),
                y=rng.uniform(-1000, 1000),
                seed=rng.randint(1, 99999),
            )
            self.systems.append(sys)
        # First system always at center, visited
        self.systems[0].x = 0
        self.systems[0].y = 0
        self.systems[0].visited = True
        self.current = self.systems[0]

    def warp_to(self, system_id):
        for s in self.systems:
            if s.id == system_id:
                self.current = s
                s.visited = True
                return s
        return None

    def neighbors(self, max_distance=400):
        return [s for s in self.systems
                if s.id != self.current.id
                and ((s.x - self.current.x) ** 2 + (s.y - self.current.y) ** 2) ** 0.5 <= max_distance]


galaxy = Galaxy()
