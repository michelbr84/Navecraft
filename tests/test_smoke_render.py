"""
Smoke render test - asserts the first rendered frame of a fresh Game has the
visual hallmarks of a populated scene (non-uniform, multi-color, has the dark
space background, includes at least one bright pixel from a planet or ship).

Acts as a generic guard against future regressions like the lighting white-screen.
"""

import os
os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')

import unittest
import pygame

pygame.init()
pygame.display.set_mode((1, 1))

from utils import display
display.set_mode(width=800, height=600)


class TestSmokeRender(unittest.TestCase):
    """Visual smoke tests — sampled-pixel histogram."""

    @classmethod
    def setUpClass(cls):
        from core.game import Game
        cls.game = Game()
        cls.surf = pygame.Surface((display.WIDTH, display.HEIGHT))
        cls.game.render(cls.surf)

    def _sample(self):
        w, h = self.surf.get_size()
        sx = max(1, w // 32)
        sy = max(1, h // 24)
        colors = []
        for y in range(0, h, sy):
            for x in range(0, w, sx):
                colors.append(self.surf.get_at((x, y))[:3])
        return colors

    def test_not_uniform(self):
        colors = set(self._sample())
        self.assertGreater(len(colors), 12,
                           f"Frame appears uniform - only {len(colors)} distinct colors.")

    def test_has_dark_background(self):
        """Frame should contain dark space-color pixels (background)."""
        colors = self._sample()
        dark_pixels = sum(1 for r, g, b in colors if r < 30 and g < 30 and b < 60)
        self.assertGreater(dark_pixels, len(colors) // 4,
                           "Less than 25% of the frame is dark — background may be broken.")

    def test_has_bright_pixels(self):
        """Stars, planets, or the ship outline should produce some bright pixels."""
        colors = self._sample()
        bright_pixels = sum(1 for r, g, b in colors if r > 180 or g > 180 or b > 180)
        self.assertGreater(bright_pixels, 0,
                           "No bright pixels in frame — scene may be empty/missing.")

    def test_not_pure_white(self):
        """The lighting bug painted everything white — guard against regression."""
        colors = self._sample()
        white = sum(1 for c in colors if c == (255, 255, 255))
        self.assertLess(white, len(colors) // 4,
                        f"Frame is {white}/{len(colors)} pure white — lighting regression?")


if __name__ == '__main__':
    unittest.main()
