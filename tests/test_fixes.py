"""
Tests for the bug fixes in Navecraft
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Must init pygame before importing game modules
import pygame
pygame.init()
pygame.display.set_mode((100, 100))

import unittest
from unittest.mock import MagicMock
from core.input import InputManager
from ui.menu import Menu, PauseMenu, GameOverMenu
from entities.spaceship import Spaceship, Projectile
from settings import *


class TestInputManagerFrameOrder(unittest.TestCase):
    """Test that input clearing happens at the right time"""

    def test_keys_just_pressed_survives_update_mouse(self):
        """keys_just_pressed should NOT be cleared by update_mouse()"""
        im = InputManager()
        # Simulate a key press event
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_e)
        im.handle_event(event)
        self.assertIn(pygame.K_e, im.keys_just_pressed)

        # update_mouse should NOT clear keys_just_pressed
        im.update_mouse()
        self.assertIn(pygame.K_e, im.keys_just_pressed)

    def test_clear_frame_clears_keys(self):
        """clear_frame() should clear keys_just_pressed"""
        im = InputManager()
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_e)
        im.handle_event(event)
        self.assertIn(pygame.K_e, im.keys_just_pressed)

        im.clear_frame()
        self.assertNotIn(pygame.K_e, im.keys_just_pressed)

    def test_control_just_pressed_works_after_update_mouse(self):
        """is_control_just_pressed should work after update_mouse (not cleared)"""
        im = InputManager()
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_e)
        im.handle_event(event)

        im.update_mouse()
        self.assertTrue(im.is_control_just_pressed('MINE'))

    def test_control_just_pressed_cleared_after_clear_frame(self):
        """is_control_just_pressed should NOT work after clear_frame"""
        im = InputManager()
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_e)
        im.handle_event(event)
        im.clear_frame()
        self.assertFalse(im.is_control_just_pressed('MINE'))

    def test_correct_frame_lifecycle(self):
        """Simulates the correct frame lifecycle: events -> update_mouse -> logic -> clear"""
        im = InputManager()

        # Frame 1: press E
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_e)
        im.handle_event(event)
        im.update_mouse()
        # Game logic checks - should be True
        self.assertTrue(im.is_control_just_pressed('MINE'))
        im.clear_frame()

        # Frame 2: no new events
        im.update_mouse()
        # Should be False now
        self.assertFalse(im.is_control_just_pressed('MINE'))
        im.clear_frame()


class TestPauseMenuNavigation(unittest.TestCase):
    """Test pause menu navigation fixes"""

    def test_continue_returns_continue(self):
        """Pressing Enter on 'Continuar' should return 'continue'"""
        menu = PauseMenu()
        self.assertEqual(menu.current_menu, "pause")
        menu.selected_option = 0
        result = menu.select_option()
        self.assertEqual(result, "continue")

    def test_settings_from_pause_sets_parent(self):
        """Entering settings from pause should set parent_menu to 'pause'"""
        menu = PauseMenu()
        menu.selected_option = 1  # Configurações
        menu.select_option()
        self.assertEqual(menu.current_menu, "settings")
        self.assertEqual(menu.parent_menu, "pause")

    def test_voltar_from_settings_returns_to_pause(self):
        """'Voltar' in settings should return to pause menu (not main)"""
        menu = PauseMenu()
        # Enter settings from pause
        menu.selected_option = 1
        menu.select_option()
        self.assertEqual(menu.current_menu, "settings")

        # Click 'Voltar'
        menu.selected_option = 2
        menu.select_option()
        self.assertEqual(menu.current_menu, "pause")

    def test_esc_from_settings_returns_to_pause(self):
        """ESC in settings (from pause) should return to pause menu"""
        menu = PauseMenu()
        # Enter settings from pause
        menu.selected_option = 1
        menu.select_option()
        self.assertEqual(menu.current_menu, "settings")

        # Press ESC
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)
        menu.handle_input(event)
        self.assertEqual(menu.current_menu, "pause")

    def test_esc_from_pause_returns_continue(self):
        """ESC on pause menu should return 'continue'"""
        menu = PauseMenu()
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)
        result = menu.handle_input(event)
        self.assertEqual(result, "continue")

    def test_menu_principal_returns_main_menu(self):
        """'Menu Principal' should return 'main_menu' signal"""
        menu = PauseMenu()
        menu.selected_option = 2  # Menu Principal
        result = menu.select_option()
        self.assertEqual(result, "main_menu")

    def test_settings_from_main_menu_sets_parent(self):
        """Entering settings from main menu should set parent to 'main'"""
        menu = Menu()
        menu.selected_option = 1  # Configurações
        menu.select_option()
        self.assertEqual(menu.current_menu, "settings")
        self.assertEqual(menu.parent_menu, "main")

    def test_voltar_from_settings_returns_to_main(self):
        """'Voltar' in settings from main menu should return to main"""
        menu = Menu()
        menu.selected_option = 1
        menu.select_option()
        menu.selected_option = 2  # Voltar
        menu.select_option()
        self.assertEqual(menu.current_menu, "main")


class TestProjectile(unittest.TestCase):
    """Test projectile mechanics"""

    def test_projectile_creation(self):
        """Projectile should be created with correct properties"""
        import math
        proj = Projectile(100, 200, 0)
        self.assertEqual(proj.x, 100)
        self.assertEqual(proj.y, 200)
        self.assertAlmostEqual(proj.vx, LASER_SPEED, places=1)
        self.assertAlmostEqual(proj.vy, 0, places=1)

    def test_projectile_movement(self):
        """Projectile should move in the correct direction"""
        proj = Projectile(0, 0, 0)
        proj.update()
        self.assertGreater(proj.x, 0)

    def test_projectile_lifetime(self):
        """Projectile should die after lifetime expires"""
        proj = Projectile(0, 0, 0)
        self.assertTrue(proj.is_alive())
        for _ in range(120):
            proj.update()
        self.assertFalse(proj.is_alive())


class TestMining(unittest.TestCase):
    """Test mining mechanics"""

    def test_mine_block_in_range(self):
        """Should be able to mine a block within range"""
        ship = Spaceship(100, 100)
        # Ensure cooldown is satisfied by setting last_mine_time far in the past
        ship.last_mine_time = 0
        from systems.generation import Block
        block = Block(120, 100, 'IRON')  # 20px away, within 50px range
        blocks = [block]

        # Wait enough for cooldown (pygame.time.get_ticks must be > 500)
        pygame.time.wait(600)

        initial_health = block.health
        result = ship.mine(blocks)
        # Should have damaged the block
        self.assertLess(block.health, initial_health)

    def test_mine_block_out_of_range(self):
        """Should NOT mine a block outside range"""
        ship = Spaceship(100, 100)
        from systems.generation import Block
        block = Block(200, 200, 'IRON')  # ~141px away, outside 50px range
        blocks = [block]

        initial_health = block.health
        ship.mine(blocks)
        self.assertEqual(block.health, initial_health)


class TestFullscreen(unittest.TestCase):
    """Test fullscreen toggle"""

    def test_navecraft_has_fullscreen_attr(self):
        """Navecraft should have fullscreen attribute"""
        from main import Navecraft
        nav = Navecraft()
        self.assertFalse(nav.fullscreen)
        pygame.quit()
        pygame.init()
        pygame.display.set_mode((100, 100))


if __name__ == '__main__':
    unittest.main(verbosity=2)
