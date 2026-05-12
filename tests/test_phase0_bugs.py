"""
Phase 0 regression tests - bugs that block gameplay.

These tests catch bugs reproduced from screenshots at launch:
- white-screen on world entry (lighting blend bug)
- settings menu non-interactive
- module integration gaps
- HUD/quick-inventory mismatch
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

from systems.lighting import LightingSystem


def _frame_diversity(surface):
    """Return number of distinct pixel colors sampled from a grid on the surface."""
    w, h = surface.get_size()
    colors = set()
    step_x = max(1, w // 16)
    step_y = max(1, h // 12)
    for y in range(0, h, step_y):
        for x in range(0, w, step_x):
            colors.add(surface.get_at((x, y))[:3])
    return colors


class TestWhiteScreenRegression(unittest.TestCase):
    """Lighting render must NOT paint the whole screen white."""

    def test_lighting_render_with_no_lights_does_not_paint_white(self):
        surf = pygame.Surface((800, 600))
        surf.fill((30, 40, 80))  # known dark background
        lighting = LightingSystem()
        lighting.render(surf, 0, 0, ambient=1.0)
        # Center pixel must still be the background — not white.
        center = surf.get_at((400, 300))[:3]
        self.assertNotEqual(center, (255, 255, 255),
                            "Lighting overlay painted everything white (regression).")
        # And several distinct sampled pixels should still match the bg.
        colors = _frame_diversity(surf)
        self.assertIn((30, 40, 80), colors,
                      "Background pixels were destroyed by the lighting overlay.")

    def test_lighting_with_ambient_one_keeps_scene_visible(self):
        """Default ambient=1.0 should be a no-op when there are no lights."""
        surf = pygame.Surface((400, 300))
        surf.fill((50, 70, 120))
        lighting = LightingSystem()
        lighting.render(surf, 0, 0, ambient=1.0)
        self.assertEqual(surf.get_at((200, 150))[:3], (50, 70, 120))

    def test_lighting_ambient_below_one_darkens(self):
        """ambient < 1.0 should darken (multiplicative), never brighten."""
        surf = pygame.Surface((200, 150))
        surf.fill((200, 200, 200))
        lighting = LightingSystem()
        lighting.render(surf, 0, 0, ambient=0.5)
        r, g, b = surf.get_at((100, 75))[:3]
        # After 0.5 multiply, ~100. Tolerate ±15.
        self.assertLess(r, 130)
        self.assertLess(g, 130)
        self.assertLess(b, 130)

    def test_full_game_render_first_frame_is_not_uniform(self):
        """End-to-end: instantiate Game, render one frame, assert non-uniform output."""
        from core.game import Game
        # Reduce world size for speed by using existing seed
        game = Game()
        surf = pygame.Surface((display.WIDTH, display.HEIGHT))
        game.render(surf)
        colors = _frame_diversity(surf)
        # Expect at least 8 distinct colors in a 16x12 sample grid (stars + planets + ship + bg).
        self.assertGreater(len(colors), 8,
                           f"World render is uniform — possible white-screen regression. "
                           f"Only {len(colors)} distinct colors sampled.")
        # And specifically, NOT mostly white.
        white_count = sum(1 for c in colors if c == (255, 255, 255))
        self.assertLess(white_count, len(colors) // 2,
                        "Frame is dominated by white pixels — lighting regression.")

    def test_lighting_respects_intensity_argument(self):
        """Phase 0.6 regression: a low-intensity light must produce a much
        dimmer halo than a full-intensity light. Pre-fix the `intensity`
        argument was discarded inside `_light_sprite`, so every transient
        light depositing every frame stacked into a saturated white halo.
        """
        from systems.lighting import LightingSystem

        # High-intensity light → bright halo
        full = pygame.Surface((200, 200))
        full.fill((20, 20, 40))
        bright = LightingSystem()
        bright.add_transient(100, 100, radius=48, color=(120, 180, 255),
                             intensity=1.0, lifetime=1)
        bright.render(full, 0, 0, ambient=1.0)

        # Low-intensity light → faint halo on identical bg
        dim_surf = pygame.Surface((200, 200))
        dim_surf.fill((20, 20, 40))
        dim = LightingSystem()
        dim.add_transient(100, 100, radius=48, color=(120, 180, 255),
                         intensity=0.2, lifetime=1)
        dim.render(dim_surf, 0, 0, ambient=1.0)

        # Sample the pixel a few px from the light center.
        full_b = full.get_at((110, 100))[2]
        dim_b  = dim_surf.get_at((110, 100))[2]
        # Both must be brighter than bg (light is being applied),
        self.assertGreater(full_b, 40, "Full-intensity light did not brighten pixel.")
        self.assertGreater(dim_b, 40, "Low-intensity light did not brighten pixel at all.")
        # And the dim variant must be measurably less bright (≥ 25 units),
        # confirming intensity is actually consulted by the sprite.
        self.assertGreater(full_b - dim_b, 25,
                           f"Light intensity ignored: full={full_b} vs dim={dim_b}. "
                           "Phase 0.6 fix regressed.")

    def test_stacked_transient_lights_do_not_saturate(self):
        """Phase 0.6 follow-up: even if many transient engine-style lights
        re-add at the same point, the cumulative additive blend with
        bucketed-intensity sprites must NOT saturate the destination to
        pure white. Pre-fix this was the root cause of the visible halo."""
        from systems.lighting import LightingSystem
        surf = pygame.Surface((200, 200))
        surf.fill((20, 20, 40))
        lit = LightingSystem()
        # 6 stacked low-intensity lights — well more than the renderer
        # would ever emit in flight (cap is ~3 simultaneous).
        for _ in range(6):
            lit.add_transient(100, 100, radius=48, color=(120, 180, 255),
                              intensity=0.3, lifetime=1)
        lit.render(surf, 0, 0, ambient=1.0)
        # Pixel directly at the light center should be brighter than bg
        # but not driven all the way to (255,255,255).
        r, g, b = surf.get_at((100, 100))[:3]
        self.assertGreater(b, 60, "Stacked lights produced no visible glow.")
        self.assertLess(min(r, g, b), 240,
                        f"Stacked lights saturated to ({r},{g},{b}) — halo regression.")


class TestSettingsScreenInteractive(unittest.TestCase):
    """Settings menu must respond to keyboard + mouse."""

    def setUp(self):
        from ui.settings_screen import SettingsScreen
        self.screen = SettingsScreen()
        self.screen.visible = True

    def _key_event(self, key):
        return pygame.event.Event(pygame.KEYDOWN, {'key': key, 'mod': 0, 'unicode': '', 'scancode': 0})

    def _click_event(self, x, y, button=1):
        return pygame.event.Event(pygame.MOUSEBUTTONDOWN,
                                  {'button': button, 'pos': (x, y)})

    def test_enter_toggles_bool(self):
        from utils import config
        before = bool(config.get('display', 'fullscreen', default=False))
        self.screen.selected = 0  # video → fullscreen is row 0
        handled = self.screen.handle_event(self._key_event(pygame.K_RETURN))
        self.assertTrue(handled, "ENTER must be consumed by the settings screen.")
        after = bool(config.get('display', 'fullscreen', default=False))
        self.assertNotEqual(before, after, "ENTER did not toggle fullscreen.")

    def test_arrows_adjust_volume(self):
        from utils import config
        self.screen.tab_idx = 1  # audio
        self.screen.selected = 0  # master
        before = float(config.get('audio', 'master', default=0.8))
        handled = self.screen.handle_event(self._key_event(pygame.K_RIGHT))
        self.assertTrue(handled)
        after = float(config.get('audio', 'master', default=0.8))
        self.assertNotEqual(before, after, "RIGHT arrow did not adjust master volume.")

    def test_up_down_consumed(self):
        """UP/DOWN must return True so events don't leak to the game."""
        handled_up = self.screen.handle_event(self._key_event(pygame.K_UP))
        handled_dn = self.screen.handle_event(self._key_event(pygame.K_DOWN))
        self.assertTrue(handled_up, "UP arrow leaked through.")
        self.assertTrue(handled_dn, "DOWN arrow leaked through.")

    def test_tab_switches_tab(self):
        before = self.screen.tab_idx
        self.screen.handle_event(self._key_event(pygame.K_TAB))
        self.assertNotEqual(before, self.screen.tab_idx)

    def test_mouse_click_on_tab(self):
        # Render once to populate hit rects
        surf = pygame.Surface((display.WIDTH, display.HEIGHT))
        self.screen.render(surf)
        if not self.screen._tab_rects:
            self.skipTest("No tab rects after render.")
        # Click the second tab
        rect = self.screen._tab_rects[1]
        handled = self.screen.handle_event(
            self._click_event(rect.x + 5, rect.y + 5))
        self.assertTrue(handled)
        self.assertEqual(self.screen.tab_idx, 1)


class TestModuleIntegration(unittest.TestCase):
    """Phase 0.3 — verify the 36 new modules are actually wired."""

    def test_input_manager_uses_rebinds(self):
        from core.input import InputManager
        im = InputManager()
        # Controls dict must be present and non-empty.
        self.assertTrue(im.controls)
        self.assertIn('MOVE_UP', im.controls)
        # reload_rebinds must exist and be callable.
        im.reload_rebinds()

    def test_all_36_new_modules_importable(self):
        modules = [
            'utils.display', 'utils.config', 'utils.font', 'utils.i18n',
            'systems.feedback', 'systems.tutorial', 'systems.codex',
            'systems.lighting', 'systems.background', 'systems.galaxy',
            'systems.factions', 'systems.bosses', 'systems.skills',
            'systems.achievements', 'systems.gamepad', 'systems.profiler',
            'systems.pool', 'systems.spatial_hash', 'systems.telemetry',
            'systems.mod_loader', 'systems.photo_mode', 'systems.day_night',
            'systems.weather', 'systems.replay', 'systems.speedrun',
            'systems.rebind', 'systems.accessibility', 'systems.camera',
            'ui.minimap', 'ui.compass', 'ui.inventory_screen',
            'ui.crafting_screen', 'ui.map_screen', 'ui.death_screen',
            'ui.tooltip', 'ui.help_overlay', 'entities.merchant',
        ]
        for name in modules:
            try:
                __import__(name)
            except Exception as e:
                self.fail(f"Module {name} failed to import: {e}")

    def test_game_initializes_all_subsystems(self):
        from core.game import Game
        g = Game()
        # All subsystems must be attached as attributes.
        for attr in ('input_manager', 'physics_system', 'world_generator',
                     'renderer', 'audio_system', 'particle_system',
                     'mission_system', 'debug_system', 'minimap', 'compass',
                     'tutorial', 'run_stats', 'spatial_hash', 'spaceship',
                     'crafting_system', 'upgrade_system', 'multiplayer_system',
                     'station_system', 'save_system'):
            self.assertTrue(hasattr(g, attr), f"Game is missing subsystem: {attr}")

    def test_world_has_content(self):
        from core.game import Game
        g = Game()
        self.assertGreater(len(g.planets), 0, "No planets generated.")
        self.assertGreater(len(g.blocks), 0, "No blocks generated.")
        self.assertIsNotNone(g.spaceship, "Spaceship not spawned.")


if __name__ == '__main__':
    unittest.main()
