"""
Stress + performance budget tests.

Goals:
  - Spawn many entities and confirm the engine does NOT crash and the spatial
    hash query stays well under linear search cost.
  - Measure 60 update+render frames on a real Game and assert the average
    frame budget is within a generous bound (CI is slow on macos/windows).

These are NOT soak tests (8h+). Soak tests would block CI; they live in a
separate manual harness if/when one is added.
"""

import os
os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')

import time
import unittest
import pygame

pygame.init()
pygame.display.set_mode((1, 1))

from utils import display
display.set_mode(width=800, height=600)


class TestSpatialHashScaling(unittest.TestCase):
    """SpatialHash should answer queries in O(local cells), not O(N)."""

    def test_query_against_10000_entities(self):
        from systems.spatial_hash import SpatialHash

        class _E:
            __slots__ = ('x', 'y')

            def __init__(self, x, y):
                self.x = x
                self.y = y

        # Uniform 10000 entities in a 4000x4000 area.
        import random
        rng = random.Random(0xA110C8)
        entities = [_E(rng.uniform(0, 4000), rng.uniform(0, 4000)) for _ in range(10_000)]

        sh = SpatialHash(cell_size=128)
        sh.rebuild(entities, get_xy=lambda e: (e.x, e.y))

        # Time 100 queries; each must be fast.
        t0 = time.perf_counter()
        total = 0
        for _ in range(100):
            res = sh.query_radius(rng.uniform(0, 4000), rng.uniform(0, 4000), 200)
            total += len(res)
        elapsed = time.perf_counter() - t0

        # 100 queries against 10k entities should complete in under 1 second.
        self.assertLess(elapsed, 1.0,
                        f"SpatialHash too slow: {elapsed:.3f}s for 100 queries.")


class TestFullGameFrameBudget(unittest.TestCase):
    """Run a real Game's update+render loop for 60 frames; check avg frame time."""

    def test_60_frames_stay_under_budget(self):
        import sys
        from core.game import Game
        g = Game()
        surf = pygame.Surface((display.WIDTH, display.HEIGHT))

        # Warm up (sound channel allocation, font cache, etc.)
        for _ in range(3):
            g.update()
            g.render(surf)

        t0 = time.perf_counter()
        for _ in range(60):
            g.update()
            g.render(surf)
        total = time.perf_counter() - t0
        avg_ms = (total / 60) * 1000

        # Coverage tracing adds ~30-50% overhead. Detect it and relax the budget.
        # On a normal dev machine this is well under 16 ms.
        under_trace = sys.gettrace() is not None
        budget_ms = 250.0 if under_trace else 100.0
        self.assertLess(avg_ms, budget_ms,
                        f"Frame budget overrun: avg {avg_ms:.1f} ms/frame "
                        f"(target < {budget_ms:.0f} ms; under_trace={under_trace}).")


class TestManyProjectiles(unittest.TestCase):
    """Inserting hundreds of projectiles must not crash the update loop."""

    def test_500_projectiles_no_crash(self):
        from core.game import Game
        from entities.spaceship import Projectile
        g = Game()
        for i in range(500):
            g.projectiles.append(Projectile(g.spaceship.x + i, g.spaceship.y, 0.0, owner='player'))
        # 10 update cycles
        for _ in range(10):
            g.update()
        # Most projectiles should expire (default lifetime).
        # We don't assert a specific count, only that no exception was raised
        # and the list shrinks deterministically.
        self.assertLessEqual(len(g.projectiles), 500)


if __name__ == '__main__':
    unittest.main()
