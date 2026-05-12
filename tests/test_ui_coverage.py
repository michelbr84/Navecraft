"""
UI render coverage - exercise the render paths of menus and screens so they
contribute to coverage. None of these assert pixel content (smoke tests
elsewhere handle that); they only confirm the code paths run.
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


class TestUIRenderCoverage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from core.game import Game
        cls.game = Game()
        cls.surf = pygame.Surface((display.WIDTH, display.HEIGHT))

    def test_codex_screen_renders(self):
        from ui.codex_screen import CodexScreen
        s = CodexScreen()
        s.visible = True
        s.render(self.surf)

    def test_crafting_screen_renders(self):
        from ui.crafting_screen import CraftingScreen
        s = CraftingScreen()
        s.visible = True
        s.render(self.surf, self.game.crafting_system)

    def test_inventory_screen_renders(self):
        from ui.inventory_screen import InventoryScreen
        s = InventoryScreen()
        s.visible = True
        s.render(self.surf, self.game.spaceship.inventory)

    def test_map_screen_renders_with_explored_cells(self):
        from ui.map_screen import WorldMap
        m = WorldMap()
        m.visible = True
        for i in range(5):
            m.mark_explored(self.game.spaceship.x + i * 200, self.game.spaceship.y)
        m.render(self.surf, self.game)

    def test_map_screen_handle_zoom_keys(self):
        from ui.map_screen import WorldMap
        m = WorldMap()
        m.visible = True
        before = m.scale
        plus = pygame.event.Event(pygame.KEYDOWN,
                                  {'key': pygame.K_EQUALS, 'mod': 0, 'unicode': '+', 'scancode': 0})
        self.assertTrue(m.handle_event(plus, self.game))
        self.assertGreater(m.scale, before)
        minus = pygame.event.Event(pygame.KEYDOWN,
                                   {'key': pygame.K_MINUS, 'mod': 0, 'unicode': '-', 'scancode': 0})
        self.assertTrue(m.handle_event(minus, self.game))

    def test_help_overlay_renders(self):
        from ui.help_overlay import HelpOverlay
        h = HelpOverlay()
        h.visible = True
        h.render(self.surf)

    def test_compass_renders_with_waypoints(self):
        from ui.compass import CompassSystem
        c = CompassSystem()
        c.render(self.surf, self.game, self.game.camera_x, self.game.camera_y)

    def test_settings_screen_renders_each_tab(self):
        from ui.settings_screen import SettingsScreen, TABS
        s = SettingsScreen()
        s.visible = True
        for i in range(len(TABS)):
            s.tab_idx = i
            s.render(self.surf)

    def test_menu_renders(self):
        from ui.menu import Menu, PauseMenu, GameOverMenu
        for cls in (Menu, PauseMenu, GameOverMenu):
            m = cls()
            m.render(self.surf)


class TestUpgradeSystemFlow(unittest.TestCase):
    """Boost upgrades.py coverage from 12% by exercising apply paths."""

    def test_apply_each_upgrade_with_resources(self):
        from core.game import Game
        g = Game()
        # Stock inventory with plenty of resources.
        for item, qty in [('IRON', 200), ('GOLD', 200), ('CRYSTAL', 200),
                          ('FUEL', 200), ('OXYGEN', 200)]:
            g.spaceship.inventory.add_item(item, qty)
        # Apply one of each upgrade.
        for upgrade in g.upgrade_system.upgrades.keys():
            info_before = g.upgrade_system.get_upgrade_info(upgrade)
            ok = g.upgrade_system.apply_upgrade(upgrade)
            self.assertTrue(ok or info_before is None)

    def test_render_upgrades_does_not_crash(self):
        from core.game import Game
        surf = pygame.Surface((display.WIDTH, display.HEIGHT))
        g = Game()
        g.upgrade_system.render_upgrades(surf, 0, 0)


class TestColorsImport(unittest.TestCase):
    """Importing utils.colors should be safe."""

    def test_imports_constants(self):
        from utils import colors
        # At least one constant should be defined.
        self.assertTrue(hasattr(colors, 'CYAN') or hasattr(colors, 'WHITE') or
                        any(c.isupper() and len(c) > 1 for c in dir(colors)))


if __name__ == '__main__':
    unittest.main()
