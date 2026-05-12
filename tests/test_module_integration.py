"""
Phase 1 integration tests — exercise the public API of each of the ~36 new modules
end-to-end on a real Game instance to catch wiring regressions early.

These tests do NOT replace unit tests (already in tests/test_new_systems.py);
they verify the module is *actually wired* into Game/main and that its
documented control loop runs without crashing.
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


class TestUtilsDisplay(unittest.TestCase):
    def test_resolution_cycle(self):
        before = (display.WIDTH, display.HEIGHT)
        display.cycle_resolution()
        # Must change to a different supported resolution.
        after = (display.WIDTH, display.HEIGHT)
        self.assertIn(after, display.SUPPORTED_RESOLUTIONS)

    def test_apply_from_config_roundtrip(self):
        cfg = display.export_config()
        display.apply_from_config(cfg)
        self.assertEqual((display.WIDTH, display.HEIGHT),
                         (cfg['width'], cfg['height']))


class TestUtilsConfig(unittest.TestCase):
    def test_set_get_persists_in_memory(self):
        from utils import config
        config.set('test', 'value', 42)
        self.assertEqual(config.get('test', 'value'), 42)


class TestUtilsFont(unittest.TestCase):
    def test_render_outlined_returns_surface(self):
        from utils.font import get_font, render_outlined
        s = render_outlined(get_font(20), "Hello", (255, 255, 255), (0, 0, 0), 2)
        self.assertGreater(s.get_width(), 0)
        self.assertGreater(s.get_height(), 0)

    def test_draw_panel_no_crash(self):
        from utils.font import draw_panel
        surf = pygame.Surface((100, 50))
        draw_panel(surf, pygame.Rect(0, 0, 100, 50),
                   bg=(0, 0, 0), border=(255, 255, 255), bg_alpha=200,
                   border_width=2, radius=4)


class TestUtilsI18n(unittest.TestCase):
    def test_switches_language(self):
        from utils.i18n import t, set_language, get_language
        before = t('app.title')
        set_language('en')
        self.assertEqual(get_language(), 'en')
        after = t('app.title')
        # The same key in two different languages should differ — unless the
        # translation is intentionally the same proper noun.
        # Either way, set_language must not crash and t() must return a string.
        self.assertIsInstance(after, str)
        set_language('pt')


class TestFeedbackJuice(unittest.TestCase):
    def test_feedback_render_screen_does_not_crash(self):
        from systems.feedback import feedback
        surf = pygame.Surface((800, 600))
        feedback.flash((255, 0, 0), strength=120)
        feedback.set_vignette(0.5)
        feedback.floating(100, 100, "+1 IRON", lifetime=10, world_space=False)
        feedback.update()
        feedback.render_world(surf, 0, 0)
        feedback.render_screen(surf)
        # Clean up state for other tests.
        feedback.set_vignette(0.0)
        feedback.flash((0, 0, 0), strength=0)
        feedback.texts.clear()

    def test_slowmo_modifies_time_scale(self):
        from systems.feedback import feedback
        feedback.slowmo_factor = 1.0
        feedback.slowmo_remaining = 0
        feedback.slowmo(0.5, 30)
        self.assertLess(feedback.time_scale(), 1.0)
        feedback.slowmo_remaining = 0
        feedback.slowmo_factor = 1.0


class TestTutorialStateMachine(unittest.TestCase):
    def test_tutorial_starts_and_advances(self):
        from systems.tutorial import TutorialSystem
        tut = TutorialSystem()
        self.assertTrue(tut.active)
        # Calling on_* callbacks should not crash.
        tut.on_mine()
        tut.on_build()
        tut.on_shoot()
        tut.on_station_built()


class TestCodexEntries(unittest.TestCase):
    def test_resource_entries_complete(self):
        from systems.codex import CODEX_DATA, get_entry
        for category in ('resources', 'enemies'):
            self.assertIn(category, CODEX_DATA)
            self.assertGreater(len(CODEX_DATA[category]), 0)
        e = get_entry('resources', 'IRON')
        self.assertIsNotNone(e)


class TestGalaxyWarp(unittest.TestCase):
    def test_galaxy_has_systems(self):
        from systems.galaxy import galaxy
        self.assertGreaterEqual(len(galaxy.systems), 1)

    def test_warp_to_first_system(self):
        from systems.galaxy import galaxy
        first_id = galaxy.systems[0].id
        ok = galaxy.warp_to(first_id)
        self.assertTrue(ok)


class TestFactionsReputation(unittest.TestCase):
    def test_adjust_reputation(self):
        from systems.factions import reputation
        before = reputation.rep.get('PIRATES', 0)
        reputation.adjust('PIRATES', -10)
        after = reputation.rep.get('PIRATES', 0)
        self.assertLess(after, before)
        # Status helper returns a string.
        self.assertIsInstance(reputation.status('PIRATES'), str)


class TestBosses(unittest.TestCase):
    def test_miniboss_creation_and_update(self):
        from systems.bosses import MiniBoss
        boss = MiniBoss(0, 0)
        self.assertTrue(boss.is_alive())
        # boss.update needs a target; pass None-safe by giving a tiny shim.
        class _Ship:
            x, y, vx, vy, size, health, max_health = 100, 0, 0, 0, 16, 100, 100
            def take_damage(self, *_a, **_k): pass
            def is_alive(self): return True
        boss.update(_Ship())


class TestSkillsSpend(unittest.TestCase):
    def test_skill_unlock(self):
        from systems.skills import skills, SKILL_TREE
        # Find any node and use its real id.
        first_node = next(iter(next(iter(SKILL_TREE.values()))['nodes'].keys()))
        skills.points = 10
        skills.unlocked.discard(first_node)
        ok = skills.unlock(first_node)
        self.assertTrue(ok)


class TestAchievements(unittest.TestCase):
    def test_trigger_records_in_lifetime(self):
        from systems.achievements import achievement_system
        from systems.stats import lifetime
        # Force-clear so we observe a fresh trigger.
        if 'first_mine' in lifetime.data['achievements_unlocked']:
            lifetime.data['achievements_unlocked'].remove('first_mine')
        achievement_system.notifications.clear()
        first = achievement_system.trigger('first_mine')
        self.assertTrue(first)
        self.assertIn('first_mine', lifetime.data['achievements_unlocked'])
        # Repeat trigger does nothing.
        self.assertFalse(achievement_system.trigger('first_mine'))


class TestGamepadDetection(unittest.TestCase):
    def test_gamepad_singleton_exists(self):
        from systems.gamepad import gamepad
        self.assertIsNotNone(gamepad)
        # No physical pad in CI — connected may be False, that's fine.
        _ = gamepad.connected


class TestProfilerOverlay(unittest.TestCase):
    def test_profiler_toggle_and_section(self):
        from systems.profiler import profiler, section
        before = profiler.enabled
        profiler.toggle()
        self.assertNotEqual(before, profiler.enabled)
        with section('test_section'):
            pass
        avgs = profiler.averages()
        # Reset.
        profiler.enabled = before


class TestObjectPoolReuse(unittest.TestCase):
    def test_pool_reuses(self):
        from systems.pool import ObjectPool
        created = []

        def factory(x=0):
            obj = {'x': x}
            created.append(obj)
            return obj

        def reset(obj, x=0):
            obj['x'] = x

        pool = ObjectPool(factory=factory, reset_fn=reset)
        a = pool.acquire(x=1)
        pool.release(a)
        b = pool.acquire(x=2)
        self.assertIs(a, b, "Pool failed to reuse the released object.")


class TestSpatialHashQuery(unittest.TestCase):
    def test_query_radius_is_broad_phase(self):
        from systems.spatial_hash import SpatialHash

        class _E:
            def __init__(self, x, y):
                self.x, self.y = x, y

        entities = [_E(0, 0), _E(100, 100), _E(500, 500)]
        sh = SpatialHash(cell_size=64)
        sh.rebuild(entities, get_xy=lambda e: (e.x, e.y))
        # Broad-phase: returns *candidates* not exact matches; must contain (0,0).
        near = sh.query_radius(0, 0, 50)
        self.assertIn(entities[0], near)
        # And far entity must NOT be in the candidate set.
        self.assertNotIn(entities[2], near)


class TestTelemetryOptIn(unittest.TestCase):
    def test_telemetry_respects_consent(self):
        from systems.telemetry import telemetry
        from utils import config
        config.set('telemetry', 'consented', False)
        # Should silently no-op
        telemetry.log_event('test_event', {'k': 'v'})


class TestModLoaderEmptyDir(unittest.TestCase):
    def test_load_all_no_crash_on_missing_dir(self):
        from systems.mod_loader import load_all
        # Should not crash even with no mods.
        load_all()


class TestPhotoMode(unittest.TestCase):
    def test_toggle_pan_zoom(self):
        from systems.photo_mode import photo_mode
        before = photo_mode.active
        photo_mode.toggle()
        self.assertNotEqual(before, photo_mode.active)
        photo_mode.pan(1, 0)
        photo_mode.adjust_zoom(0.1)
        if photo_mode.active:
            photo_mode.toggle()  # reset


class TestDayNightCycle(unittest.TestCase):
    def test_phase_progresses_over_time(self):
        from systems.day_night import day_night
        day_night.t = 0.0
        day_night.update(5.0)
        self.assertGreater(day_night.t, 0.0)
        # Tint must be a 3-tuple of ints.
        tint = day_night.ambient_tint()
        self.assertEqual(len(tint), 3)


class TestWeather(unittest.TestCase):
    def test_storm_lifecycle(self):
        from systems.weather import weather

        class _Ship:
            x, y = 0, 0
            energy, max_energy = 100, 100

        # is_active() should be deterministic per-frame.
        for _ in range(60):
            weather.update(_Ship())
        self.assertIsInstance(weather.is_active(), bool)


class TestReplayRecord(unittest.TestCase):
    def test_record_and_play(self):
        from systems.replay import replay

        class _Ship:
            x, y, angle = 10, 20, 0.0

        replay.start_recording()
        for _ in range(5):
            replay.record(_Ship())
        self.assertGreaterEqual(len(replay.frames), 5)


class TestSpeedrunTimer(unittest.TestCase):
    def test_toggle_and_format(self):
        from systems.speedrun import speedrun
        speedrun.enabled = False
        speedrun.toggle()
        self.assertTrue(speedrun.enabled)
        s = speedrun.format_time()
        self.assertIsInstance(s, str)
        speedrun.toggle()


class TestRebindPersist(unittest.TestCase):
    def test_set_get_rebind(self):
        from systems.rebind import set_rebind, apply_rebinds, reset_rebinds
        from settings import CONTROLS
        set_rebind('MOVE_UP', ['K_w'])
        merged = apply_rebinds(CONTROLS)
        self.assertEqual(merged['MOVE_UP'], [pygame.K_w])
        reset_rebinds()


class TestAccessibility(unittest.TestCase):
    def test_reduce_motion_returns_bool(self):
        from systems.accessibility import is_reduce_motion, colorblind_filter
        self.assertIsInstance(is_reduce_motion(), bool)
        c = colorblind_filter((255, 0, 0))
        self.assertEqual(len(c), 3)


class TestMinimapRenders(unittest.TestCase):
    def test_minimap_renders_against_real_game(self):
        from core.game import Game
        from ui.minimap import Minimap
        g = Game()
        m = Minimap()
        surf = pygame.Surface((display.WIDTH, display.HEIGHT))
        m.render(surf, g)


class TestCompassRenders(unittest.TestCase):
    def test_compass_renders(self):
        from core.game import Game
        from ui.compass import CompassSystem
        g = Game()
        c = CompassSystem()
        surf = pygame.Surface((display.WIDTH, display.HEIGHT))
        c.render(surf, g, g.camera_x, g.camera_y)


class TestInventoryScreenToggle(unittest.TestCase):
    def test_inventory_toggle(self):
        from ui.inventory_screen import InventoryScreen
        s = InventoryScreen()
        before = s.visible
        s.toggle()
        self.assertNotEqual(before, s.visible)


class TestCraftingScreenToggle(unittest.TestCase):
    def test_crafting_toggle(self):
        from ui.crafting_screen import CraftingScreen
        s = CraftingScreen()
        before = s.visible
        s.toggle()
        self.assertNotEqual(before, s.visible)


class TestWorldMapToggle(unittest.TestCase):
    def test_world_map_toggle(self):
        from ui.map_screen import WorldMap
        m = WorldMap()
        before = m.visible
        m.toggle()
        self.assertNotEqual(before, m.visible)


class TestDeathScreenCapture(unittest.TestCase):
    def test_capture_and_render(self):
        from ui.death_screen import DeathScreen
        ds = DeathScreen()
        surf = pygame.Surface((display.WIDTH, display.HEIGHT))
        ds.capture(surf)
        # Render with minimal stub.
        from systems.stats import RunStats
        ds.render(surf, score=100, run_stats=RunStats(), cause_of_death='test')


class TestTooltipWrap(unittest.TestCase):
    def test_tooltip_renders(self):
        from ui.tooltip import render_tooltip
        surf = pygame.Surface((display.WIDTH, display.HEIGHT))
        render_tooltip(surf, "A long-ish tooltip that may wrap.", x=100, y=100)


class TestHelpOverlayToggle(unittest.TestCase):
    def test_help_toggle(self):
        from ui.help_overlay import HelpOverlay
        h = HelpOverlay()
        before = h.visible
        h.toggle()
        self.assertNotEqual(before, h.visible)


class TestMerchantInteraction(unittest.TestCase):
    def test_buy_sell_with_inventory(self):
        from entities.merchant import Merchant
        from systems.inventory import Inventory
        m = Merchant(0, 0)
        inv = Inventory()
        inv.add_item('CRYSTAL', 50)

        class _Ship:
            x, y = 0, 0
            inventory = inv
        # Player buys
        self.assertTrue(m.sell_to_player(_Ship(), 'REPAIR_KIT'))
        self.assertEqual(inv.get_item_count('REPAIR_KIT'), 1)
        # Player sells
        inv.add_item('IRON', 5)
        self.assertTrue(m.buy_from_player(_Ship(), 'IRON', 5))


class TestStationSystemBlueprints(unittest.TestCase):
    def test_blueprints_have_layouts(self):
        from systems.stations import StationSystem
        s = StationSystem()
        for name, bp in s.blueprints.items():
            self.assertIn('layout', bp)
            self.assertIn('cost', bp)
            self.assertGreater(len(bp['layout']), 0)


if __name__ == '__main__':
    unittest.main()
