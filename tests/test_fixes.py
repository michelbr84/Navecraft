"""
Tests for Navecraft game systems
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame
pygame.init()
pygame.display.set_mode((100, 100))

import unittest
from core.input import InputManager
from ui.menu import Menu, PauseMenu, GameOverMenu
from entities.spaceship import Spaceship, Projectile
from settings import *


class TestInputManagerFrameOrder(unittest.TestCase):
    """Test that input clearing happens at the right time"""

    def test_keys_just_pressed_survives_update_mouse(self):
        im = InputManager()
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_e)
        im.handle_event(event)
        im.update_mouse()
        self.assertIn(pygame.K_e, im.keys_just_pressed)

    def test_clear_frame_clears_keys(self):
        im = InputManager()
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_e)
        im.handle_event(event)
        im.clear_frame()
        self.assertNotIn(pygame.K_e, im.keys_just_pressed)

    def test_control_just_pressed_works_after_update_mouse(self):
        im = InputManager()
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_e)
        im.handle_event(event)
        im.update_mouse()
        self.assertTrue(im.is_control_just_pressed('MINE'))

    def test_correct_frame_lifecycle(self):
        im = InputManager()
        # Frame 1: press E
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_e)
        im.handle_event(event)
        im.update_mouse()
        self.assertTrue(im.is_control_just_pressed('MINE'))
        im.clear_frame()
        # Frame 2: no new events
        im.update_mouse()
        self.assertFalse(im.is_control_just_pressed('MINE'))


class TestPauseMenuNavigation(unittest.TestCase):
    """Test pause menu navigation"""

    def test_continue_returns_continue(self):
        menu = PauseMenu()
        menu.selected_option = 0
        self.assertEqual(menu.select_option(), "continue")

    def test_settings_from_pause_sets_parent(self):
        menu = PauseMenu()
        menu.selected_option = 1
        menu.select_option()
        self.assertEqual(menu.current_menu, "settings")
        self.assertEqual(menu.parent_menu, "pause")

    def test_voltar_from_settings_returns_to_pause(self):
        menu = PauseMenu()
        menu.selected_option = 1
        menu.select_option()
        menu.selected_option = 2
        menu.select_option()
        self.assertEqual(menu.current_menu, "pause")

    def test_esc_from_pause_returns_continue(self):
        menu = PauseMenu()
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)
        self.assertEqual(menu.handle_input(event), "continue")

    def test_menu_principal_returns_main_menu(self):
        menu = PauseMenu()
        menu.selected_option = 2
        self.assertEqual(menu.select_option(), "main_menu")


class TestMainMenuNavigation(unittest.TestCase):
    """Test main menu with new options"""

    def test_play_option(self):
        menu = Menu()
        menu.selected_option = 0
        self.assertEqual(menu.select_option(), "play")

    def test_load_option(self):
        menu = Menu()
        menu.selected_option = 1
        self.assertEqual(menu.select_option(), "load")

    def test_settings_option(self):
        menu = Menu()
        menu.selected_option = 2
        menu.select_option()
        self.assertEqual(menu.current_menu, "settings")

    def test_about_option(self):
        menu = Menu()
        menu.selected_option = 3
        menu.select_option()
        self.assertEqual(menu.current_menu, "about")

    def test_quit_option(self):
        menu = Menu()
        menu.selected_option = 4
        self.assertEqual(menu.select_option(), "quit")

    def test_about_voltar(self):
        menu = Menu()
        menu.selected_option = 3
        menu.select_option()  # Enter about
        menu.selected_option = 0
        menu.select_option()  # Voltar
        self.assertEqual(menu.current_menu, "main")

    def test_about_esc(self):
        menu = Menu()
        menu.current_menu = "about"
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)
        menu.handle_input(event)
        self.assertEqual(menu.current_menu, "main")


class TestProjectile(unittest.TestCase):
    def test_projectile_creation(self):
        proj = Projectile(100, 200, 0)
        self.assertAlmostEqual(proj.vx, LASER_SPEED, places=1)

    def test_projectile_lifetime(self):
        proj = Projectile(0, 0, 0)
        self.assertTrue(proj.is_alive())
        for _ in range(120):
            proj.update()
        self.assertFalse(proj.is_alive())


class TestMining(unittest.TestCase):
    def test_mine_block_in_range(self):
        ship = Spaceship(100, 100)
        ship.last_mine_time = 0
        from systems.generation import Block
        block = Block(120, 100, 'IRON')
        pygame.time.wait(600)
        initial_health = block.health
        ship.mine([block])
        self.assertLess(block.health, initial_health)

    def test_mine_block_out_of_range(self):
        ship = Spaceship(100, 100)
        from systems.generation import Block
        block = Block(200, 200, 'IRON')
        initial_health = block.health
        ship.mine([block])
        self.assertEqual(block.health, initial_health)


class TestScoreSystem(unittest.TestCase):
    def test_game_has_score(self):
        from core.game import Game
        g = Game()
        self.assertEqual(g.score, 0)
        g.score += 50
        self.assertEqual(g.score, 50)


class TestSaveSystem(unittest.TestCase):
    def test_save_and_load(self):
        from core.game import Game
        from systems.save_system import SaveSystem
        save = SaveSystem("test_save.json")

        g = Game()
        g.score = 999
        g.spaceship.x = 500
        g.spaceship.y = 300
        g.spaceship.health = 75
        save.save_game(g)

        g2 = Game()
        self.assertEqual(g2.score, 0)
        save.load_game(g2)
        self.assertEqual(g2.score, 999)
        self.assertEqual(g2.spaceship.x, 500)
        self.assertEqual(g2.spaceship.y, 300)
        self.assertEqual(g2.spaceship.health, 75)

        save.delete_save()
        self.assertFalse(save.has_save())

    def test_load_no_save(self):
        from core.game import Game
        from systems.save_system import SaveSystem
        save = SaveSystem("nonexistent_save.json")
        g = Game()
        self.assertFalse(save.load_game(g))


class TestAudioSystem(unittest.TestCase):
    def test_audio_init(self):
        from core.audio import AudioSystem
        audio = AudioSystem()
        self.assertTrue(audio.sfx_enabled)
        self.assertIn('laser', audio.sounds)
        self.assertIn('shoot', audio.sounds)
        self.assertIn('mine', audio.sounds)
        self.assertIn('collect', audio.sounds)
        self.assertIn('build', audio.sounds)

    def test_play_sound_no_crash(self):
        from core.audio import AudioSystem
        audio = AudioSystem()
        audio.play_sound('shoot')
        audio.play_sound('mine')
        audio.play_sound('nonexistent')


class TestStationSystem(unittest.TestCase):
    def test_blueprints_exist(self):
        from systems.stations import StationSystem
        ss = StationSystem()
        self.assertIn('SMALL_OUTPOST', ss.blueprints)
        self.assertIn('REFUEL_STATION', ss.blueprints)
        self.assertIn('MINING_PLATFORM', ss.blueprints)

    def test_cycle_blueprint(self):
        from systems.stations import StationSystem
        ss = StationSystem()
        first = ss.selected_blueprint
        ss.cycle_blueprint()
        self.assertNotEqual(ss.selected_blueprint, first)

    def test_build_without_resources(self):
        from systems.stations import StationSystem
        from systems.inventory import Inventory
        ss = StationSystem()
        inv = Inventory()
        inv.items = {}  # Empty inventory
        self.assertFalse(ss.can_build('SMALL_OUTPOST', inv))


class TestMultiplayerKeyConflicts(unittest.TestCase):
    def test_no_key_conflicts_with_main_controls(self):
        from systems.multiplayer import MultiplayerSystem
        # Get all main control keys
        main_keys = set()
        for keys in CONTROLS.values():
            main_keys.update(keys)

        ms = MultiplayerSystem(None)
        p2_keys = set()
        for keys in ms.player2_controls.values():
            p2_keys.update(keys)

        # No overlap between main and P2 controls
        conflicts = main_keys & p2_keys
        self.assertEqual(conflicts, set(),
                         f"Key conflicts found: {conflicts}")


class TestCaveGeneration(unittest.TestCase):
    def test_caves_generated(self):
        from systems.generation import WorldGenerator
        wg = WorldGenerator()
        planets = wg.generate_planets()
        caves = wg.generate_caves(planets)
        self.assertGreater(len(caves), 0)


if __name__ == '__main__':
    unittest.main(verbosity=2)
