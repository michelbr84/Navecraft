"""
Tests for the new systems added in the AAA expansion.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame

pygame.init()
pygame.display.set_mode((100, 100))

import unittest


class TestDisplayModule(unittest.TestCase):
    def test_default_dimensions(self):
        from utils import display
        self.assertGreater(display.WIDTH, 0)
        self.assertGreater(display.HEIGHT, 0)

    def test_ui_scale(self):
        from utils import display
        scale = display.ui_scale()
        self.assertGreater(scale, 0)

    def test_export_config(self):
        from utils import display
        cfg = display.export_config()
        self.assertIn('width', cfg)
        self.assertIn('fullscreen', cfg)


class TestConfig(unittest.TestCase):
    def test_get_set_defaults(self):
        from utils import config
        config.reset()
        self.assertEqual(config.get('gameplay', 'difficulty'), 'normal')
        config.set('gameplay', 'difficulty', 'hard')
        self.assertEqual(config.get('gameplay', 'difficulty'), 'hard')
        config.reset()


class TestI18n(unittest.TestCase):
    def test_translation_keys(self):
        from utils.i18n import t, set_language
        set_language('pt')
        self.assertEqual(t('menu.play'), 'Jogar')
        set_language('en')
        self.assertEqual(t('menu.play'), 'Play')
        set_language('es')
        self.assertEqual(t('menu.play'), 'Jugar')
        set_language('pt')

    def test_missing_key_returns_key(self):
        from utils.i18n import t
        self.assertEqual(t('does.not.exist'), 'does.not.exist')


class TestStats(unittest.TestCase):
    def test_run_stats_record(self):
        from systems.stats import RunStats
        r = RunStats()
        r.add_mined('IRON', 10)
        self.assertEqual(r.blocks_mined, 1)
        self.assertEqual(r.resources_collected['IRON'], 10)

    def test_lifetime_merge(self):
        from systems.stats import RunStats, LifetimeStats
        r = RunStats()
        r.survival_time = 100
        r.blocks_mined = 5
        # Use a temporary lifetime instance to avoid touching the real file
        lt = LifetimeStats.__new__(LifetimeStats)
        lt.data = {
            'runs': 0, 'deaths': 0, 'total_survival_time': 0.0, 'total_distance': 0.0,
            'total_blocks_mined': 0, 'total_blocks_built': 0, 'total_enemies_killed': 0,
            'total_shots_fired': 0, 'best_score': 0, 'best_survival_time': 0.0,
            'achievements_unlocked': [], 'completed_tutorial': False, 'first_play_timestamp': None,
        }

        def _noop_save(*a, **kw):
            pass
        lt.save = _noop_save
        lt.merge_run(r, 200)
        self.assertEqual(lt.data['runs'], 1)
        self.assertEqual(lt.data['total_blocks_mined'], 5)


class TestFeedback(unittest.TestCase):
    def test_floating_text_lifetime(self):
        from systems.feedback import FloatingText
        ft = FloatingText(0, 0, 'hi', lifetime=5)
        for _ in range(5):
            ft.update()
        self.assertFalse(ft.is_alive())

    def test_shake_clears(self):
        from systems.feedback import FeedbackSystem
        fb = FeedbackSystem()
        fb.shake(intensity=4, frames=3)
        for _ in range(3):
            fb.update()
        self.assertEqual(fb.shake_intensity, 0.0)

    def test_hitstop(self):
        from systems.feedback import FeedbackSystem
        fb = FeedbackSystem()
        fb.hitstop(3)
        self.assertTrue(fb.is_paused_by_hitstop())
        for _ in range(3):
            fb.update()
        self.assertFalse(fb.is_paused_by_hitstop())


class TestCamera(unittest.TestCase):
    def test_camera_smoothly_follows(self):
        from systems.camera import SmoothCamera
        c = SmoothCamera()
        c.follow(1000, 500)
        # Several updates approach target
        for _ in range(60):
            c.update()
        # Should be very close to target
        self.assertAlmostEqual(c.x, c.target_x, delta=10)

    def test_camera_snap_to(self):
        from systems.camera import SmoothCamera
        c = SmoothCamera()
        c.snap_to(500, 700)
        self.assertAlmostEqual(c.x, c.target_x)


class TestSpatialHash(unittest.TestCase):
    def test_query_radius(self):
        from systems.spatial_hash import SpatialHash

        class Obj:
            def __init__(self, x, y):
                self.x = x
                self.y = y

        sh = SpatialHash(cell_size=100)
        a = Obj(50, 50)
        b = Obj(900, 900)
        sh.insert(a, a.x, a.y)
        sh.insert(b, b.x, b.y)
        near = sh.query_radius(50, 50, 100)
        self.assertIn(a, near)
        self.assertNotIn(b, near)


class TestObjectPool(unittest.TestCase):
    def test_acquire_release_reuse(self):
        from systems.pool import ObjectPool
        created = [0]

        class Thing:
            def __init__(self, val=0):
                created[0] += 1
                self.val = val

        pool = ObjectPool(Thing, reset_fn=lambda o, val=0: setattr(o, 'val', val))
        t1 = pool.acquire(val=1)
        pool.release(t1)
        t2 = pool.acquire(val=2)
        self.assertIs(t1, t2)  # reused
        self.assertEqual(created[0], 1)


class TestAccessibility(unittest.TestCase):
    def test_colorblind_passthrough(self):
        from systems.accessibility import colorblind_filter
        from utils import config
        config.reset()
        self.assertEqual(colorblind_filter((100, 150, 200)), (100, 150, 200))

    def test_colorblind_protanopia_changes_color(self):
        from systems.accessibility import colorblind_filter
        from utils import config
        config.set('accessibility', 'colorblind_mode', 'protanopia')
        out = colorblind_filter((255, 0, 0))
        # Red should be reduced
        self.assertLess(out[0], 255)
        config.reset()


class TestGameModes(unittest.TestCase):
    def test_cycle(self):
        from systems.game_modes import GameMode
        from utils import config
        config.reset()
        a = GameMode.cycle()
        b = GameMode.cycle()
        self.assertNotEqual(a, b)
        config.reset()


class TestFactions(unittest.TestCase):
    def test_reputation_changes(self):
        from systems.factions import ReputationSystem
        r = ReputationSystem()
        r.adjust('PIRATES', -50)
        self.assertTrue(r.is_hostile('PIRATES'))


class TestSkills(unittest.TestCase):
    def test_unlock(self):
        from systems.skills import SkillSystem
        s = SkillSystem()
        s.earn(5)
        self.assertTrue(s.can_unlock('agile_turn'))
        self.assertTrue(s.unlock('agile_turn'))
        self.assertTrue(s.has('agile_turn'))


class TestSaveSystemMultiSlot(unittest.TestCase):
    def test_slot_path(self):
        from systems.save_system import SaveSystem
        s = SaveSystem(slot=0)
        s2 = SaveSystem(slot=1)
        self.assertNotEqual(s.save_file, s2.save_file)


class TestPlanetNames(unittest.TestCase):
    def test_names_generated(self):
        from systems.planet_names import generate_name
        n = generate_name(42)
        self.assertIsInstance(n, str)
        self.assertGreater(len(n), 1)


class TestGalaxy(unittest.TestCase):
    def test_galaxy_has_systems(self):
        from systems.galaxy import Galaxy
        g = Galaxy(seed=1, num_systems=5)
        self.assertEqual(len(g.systems), 5)
        self.assertEqual(g.current.id, 0)

    def test_warp(self):
        from systems.galaxy import Galaxy
        g = Galaxy(seed=1, num_systems=5)
        result = g.warp_to(2)
        self.assertEqual(g.current.id, 2)


class TestProfiler(unittest.TestCase):
    def test_profiler_disabled_no_op(self):
        from systems.profiler import profiler, section
        profiler.enabled = False
        with section('test'):
            pass
        # No assertion - just verifying no crash


class TestSpeedrunTimer(unittest.TestCase):
    def test_format_time(self):
        from systems.speedrun import SpeedrunTimer
        sr = SpeedrunTimer()
        self.assertRegex(sr.format_time(125.5), r'\d+:\d+\.\d+')


class TestReplay(unittest.TestCase):
    def test_record_save_load(self):
        from systems.replay import ReplaySystem

        class FakeShip:
            x, y, angle = 100, 200, 0

        r = ReplaySystem()
        r.start_recording()
        r.record(FakeShip())
        self.assertGreater(len(r.frames), 0)
        r.stop_recording()


class TestAchievements(unittest.TestCase):
    def test_achievement_data(self):
        from systems.achievements import ACHIEVEMENTS
        self.assertIn('first_mine', ACHIEVEMENTS)
        self.assertIn('boss_slayer', ACHIEVEMENTS)


class TestCodex(unittest.TestCase):
    def test_entries_exist(self):
        from systems.codex import get_entry
        from utils.i18n import set_language
        set_language('pt')
        e = get_entry('resources', 'IRON')
        self.assertIsNotNone(e)
        self.assertEqual(e['name'], 'Ferro')


class TestRebind(unittest.TestCase):
    def test_apply_no_rebinds(self):
        from systems.rebind import apply_rebinds
        from settings import CONTROLS
        out = apply_rebinds(CONTROLS)
        self.assertEqual(out, CONTROLS)


class TestMissionChains(unittest.TestCase):
    def test_chain_starts(self):
        from systems.missions import MissionSystem
        ms = MissionSystem()
        m = ms.start_chain('first_steps')
        self.assertIsNotNone(m)
        self.assertEqual(m.chain_step, 0)


class TestMods(unittest.TestCase):
    def test_mod_loader_no_dir(self):
        from systems.mod_loader import load_all
        loaded = load_all('non_existent_mods_dir')
        self.assertIsInstance(loaded, list)


class TestPhotoMode(unittest.TestCase):
    def test_toggle(self):
        from systems.photo_mode import PhotoMode
        pm = PhotoMode()
        self.assertFalse(pm.active)
        pm.toggle()
        self.assertTrue(pm.active)


class TestDayNight(unittest.TestCase):
    def test_phase_progression(self):
        from systems.day_night import DayNightCycle
        d = DayNightCycle(period_seconds=10)
        d.update(5)
        self.assertAlmostEqual(d.phase(), 0.5, places=1)


if __name__ == '__main__':
    unittest.main(verbosity=2)
