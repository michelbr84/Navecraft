"""
Navecraft - entry point. State machine: menu / playing / paused / game_over / photo / replay.

Handles top-level windowing (via utils.display) and routes input to the active state.
F1 dual binding resolved:
  - In MENU state: F1 toggles DEBUG_MODE.
  - In PLAYING state: F1 is the Engine upgrade (handled by Game).
"""

import sys
import time
import traceback
import pygame

import settings
from settings import TITLE, FPS
from utils import config, display
from utils.i18n import t
from core.game import Game
from systems.feedback import feedback
from systems.telemetry import telemetry
from systems.mod_loader import load_all as load_mods
from systems.speedrun import speedrun
from systems.replay import replay
from systems.photo_mode import photo_mode
from systems.achievements import achievement_system
from ui.menu import Menu, PauseMenu, GameOverMenu
from ui.help_overlay import HelpOverlay
from ui.codex_screen import CodexScreen
from ui.settings_screen import SettingsScreen
from ui.inventory_screen import InventoryScreen
from ui.crafting_screen import CraftingScreen
from ui.map_screen import WorldMap
from ui.death_screen import DeathScreen


class Navecraft:
    def __init__(self):
        pygame.init()
        try:
            pygame.mixer.pre_init(44100, -16, 2, 512)
        except Exception:
            pass
        pygame.mixer.init()

        # Apply persisted config
        cfg = config.load()
        # Apply display settings
        self.screen = display.set_mode(
            width=cfg['display']['width'],
            height=cfg['display']['height'],
            fullscreen=cfg['display']['fullscreen'],
            borderless=cfg['display']['borderless'],
            vsync=cfg['display']['vsync'],
        )
        pygame.display.set_caption(t('app.title'))
        self.clock = pygame.time.Clock()

        # Load any mods
        load_mods()

        self.running = True
        self.paused = False
        self.game_state = "menu"
        self.fade_alpha = 0
        self.fade_target = 0
        self.fade_callback = None

        self.game = Game()

        self.main_menu = Menu()
        self.pause_menu = PauseMenu()
        self.game_over_menu = GameOverMenu()
        self.help_overlay = HelpOverlay()
        self.codex_screen = CodexScreen()
        self.settings_screen = SettingsScreen()
        self.inventory_screen = InventoryScreen()
        self.crafting_screen = CraftingScreen()
        self.world_map = WorldMap()
        self.game._world_map_ref = self.world_map
        self.death_screen = DeathScreen()

        self.fps_counter = 0
        self.last_fps_time = time.time()

        # First-run telemetry consent prompt (simple stub)
        self._first_consent_shown = config.get('telemetry', 'consented', default=None) is not None

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                continue

            # Common system shortcuts
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    display.toggle_fullscreen()
                    config.set('display', 'fullscreen', display.FULLSCREEN)
                    config.set('display', 'width', display.WIDTH)
                    config.set('display', 'height', display.HEIGHT)
                    config.save()
                    continue
                if event.key == pygame.K_F10:
                    display.toggle_borderless()
                    config.set('display', 'borderless', display.BORDERLESS)
                    config.save()
                    continue
                if event.key == pygame.K_F3:
                    from systems.profiler import profiler
                    profiler.toggle()
                    continue
                if event.key == pygame.K_F12 and self.game_state == "playing":
                    photo_mode.toggle()
                    if photo_mode.active:
                        achievement_system.trigger('photo_taken')
                    continue
                if event.key == pygame.K_F4 and self.game_state == "playing":
                    # Speedrun timer toggle
                    speedrun.toggle()
                    continue
                if event.key == pygame.K_F8 and self.game_state == "playing" and not pygame.key.get_mods() & pygame.KMOD_SHIFT:
                    # Quickload (shift+F8 used by multiplayer add player as F8 raw)
                    pass

            # Overlay screens have priority while visible
            if self.help_overlay.visible:
                if self.help_overlay.handle_event(event):
                    continue
            if self.codex_screen.visible:
                if self.codex_screen.handle_event(event):
                    continue
            if self.settings_screen.visible:
                if self.settings_screen.handle_event(event):
                    continue
            if self.inventory_screen.visible and self.game_state == "playing":
                if self.inventory_screen.handle_event(event):
                    continue
            if self.crafting_screen.visible and self.game_state == "playing":
                if self.crafting_screen.handle_event(event, self.game.crafting_system, self.game.audio_system):
                    continue
            if self.world_map.visible and self.game_state == "playing":
                if self.world_map.handle_event(event, self.game):
                    continue

            # Photo mode controls
            if photo_mode.active and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    photo_mode.pan(-1, 0)
                elif event.key == pygame.K_RIGHT:
                    photo_mode.pan(1, 0)
                elif event.key == pygame.K_UP:
                    photo_mode.pan(0, -1)
                elif event.key == pygame.K_DOWN:
                    photo_mode.pan(0, 1)
                elif event.key in (pygame.K_EQUALS, pygame.K_PLUS):
                    photo_mode.adjust_zoom(0.1)
                elif event.key == pygame.K_MINUS:
                    photo_mode.adjust_zoom(-0.1)
                elif event.key == pygame.K_h:
                    photo_mode.hide_hud = not photo_mode.hide_hud
                elif event.key == pygame.K_RETURN:
                    photo_mode.save_screenshot(self.screen)
                continue

            # State-routed events
            if self.game_state == "menu":
                # F1 in menu = toggle DEBUG (resolves the F1 vs upgrade conflict)
                if event.type == pygame.KEYDOWN and event.key == pygame.K_F1:
                    settings.DEBUG_MODE = not settings.DEBUG_MODE
                    continue
                if event.type == pygame.KEYDOWN and event.key == pygame.K_h:
                    self.help_overlay.toggle()
                    continue
                if event.type == pygame.KEYDOWN and event.key == pygame.K_k:
                    self.codex_screen.toggle()
                    continue
                result = self.main_menu.handle_input(event)
                if result == "play":
                    self._fade_then(lambda: self._start_new_game())
                elif result == "load":
                    if self.game.save_system.load_game(self.game):
                        self.game_state = "playing"
                elif result == "settings":
                    self.settings_screen.toggle()
                elif result == "quit":
                    self.running = False
            elif self.game_state == "playing":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.game_state = "paused"
                        continue
                    if event.key == pygame.K_TAB and self.game.tutorial.active:
                        self.game.tutorial.skip()
                        continue
                    if event.key == pygame.K_h:
                        self.help_overlay.toggle()
                        continue
                    if event.key == pygame.K_k:
                        self.codex_screen.toggle()
                        continue
                    if event.key == pygame.K_i:
                        self.inventory_screen.toggle()
                        continue
                    if event.key == pygame.K_c:
                        self.crafting_screen.toggle()
                        continue
                    if event.key == pygame.K_m:
                        # M is overloaded — quick tap opens map, otherwise game accepts mission via event
                        # Let game.update handle MISSION; also open map on M with Shift
                        if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                            self.world_map.toggle()
                            continue
                self.game.handle_event(event)
            elif self.game_state == "paused":
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.game_state = "playing"
                    continue
                result = self.pause_menu.handle_input(event)
                if result == "continue":
                    self.game_state = "playing"
                elif result == "main_menu":
                    self.pause_menu.current_menu = "pause"
                    self.pause_menu.selected_option = 0
                    self.game_state = "menu"
                    self.game = Game()
                    self.game._world_map_ref = self.world_map
                elif result == "settings":
                    self.settings_screen.toggle()
                elif result == "quit":
                    self.running = False
            elif self.game_state == "game_over":
                result = self.death_screen.handle_input(event)
                if result == "restart":
                    self._start_new_game()
                elif result == "main_menu":
                    self.game_state = "menu"
                elif result == "quit":
                    self.running = False

    def _start_new_game(self):
        self.game = Game()
        self.game._world_map_ref = self.world_map
        self.game_state = "playing"
        # First-run flag clears once you start playing
        if config.get('gameplay', 'first_run', default=True):
            config.set('gameplay', 'first_run', False)
            config.save()

    def _fade_then(self, cb):
        self.fade_target = 255
        self.fade_callback = cb

    def update(self):
        # Crossfade alpha
        if self.fade_alpha < self.fade_target:
            self.fade_alpha = min(255, self.fade_alpha + 18)
            if self.fade_alpha >= 255 and self.fade_callback:
                self.fade_callback()
                self.fade_callback = None
                self.fade_target = 0
        elif self.fade_alpha > self.fade_target:
            self.fade_alpha = max(0, self.fade_alpha - 18)

        if self.game_state == "playing" and not photo_mode.active:
            self.game.update()
            if self.game.spaceship and not self.game.spaceship.is_alive():
                # Capture screenshot at death
                self.death_screen.capture(self.screen)
                self.game_state = "game_over"

        # Update fps counter
        current_time = time.time()
        self.fps_counter += 1
        if current_time - self.last_fps_time >= 1.0:
            self.fps_counter = 0
            self.last_fps_time = current_time

    def render(self):
        if self.game_state == "menu":
            self.main_menu.render(self.screen)
        elif self.game_state == "playing":
            self.game.render(self.screen)
        elif self.game_state == "paused":
            self.game.render(self.screen)
            self.pause_menu.render(self.screen)
        elif self.game_state == "game_over":
            self.game.render(self.screen)
            self.death_screen.render(self.screen, score=self.game.score,
                                     run_stats=self.game.run_stats,
                                     cause_of_death=self.game.run_stats.cause_of_death)

        # Overlay screens (drawn on top regardless of state)
        if not photo_mode.hide_hud or not photo_mode.active:
            self.help_overlay.render(self.screen)
            self.codex_screen.render(self.screen)
            self.settings_screen.render(self.screen)
            if self.game_state == "playing":
                self.inventory_screen.render(self.screen, self.game.spaceship.inventory)
                self.crafting_screen.render(self.screen, self.game.crafting_system)
                self.world_map.render(self.screen, self.game)

        # Photo mode hint
        if photo_mode.active:
            from utils.font import get_font, render_outlined
            hint = render_outlined(get_font(16), t('photo.hint'), (255, 255, 255), (0, 0, 0), 1)
            self.screen.blit(hint, ((display.WIDTH - hint.get_width()) // 2, display.HEIGHT - 32))

        # Profiler panel
        try:
            from systems.profiler import profiler
            if profiler.enabled:
                from utils.font import get_font, render_outlined
                lines = [(name, ms) for name, ms, _ in profiler.averages()]
                lines.sort(key=lambda x: -x[1])
                for i, (n, ms) in enumerate(lines[:12]):
                    txt = render_outlined(get_font(14), f"{n}: {ms:.2f}ms", (255, 255, 0), (0, 0, 0), 1)
                    self.screen.blit(txt, (10, 200 + i * 18))
        except Exception:
            pass

        # Fade overlay
        if self.fade_alpha > 0:
            overlay = pygame.Surface((display.WIDTH, display.HEIGHT))
            overlay.fill((0, 0, 0))
            overlay.set_alpha(self.fade_alpha)
            self.screen.blit(overlay, (0, 0))

        pygame.display.flip()

    def run(self):
        print("Iniciando Navecraft...")
        print(f"Idioma: {t('app.title')}")
        try:
            while self.running:
                self.handle_events()
                self.update()
                self.render()
                self.clock.tick(display.FPS_CAP or FPS)
        except Exception as e:
            tb = traceback.format_exc()
            print(tb)
            telemetry.log_crash(tb)
            try:
                # Attempt emergency save
                if self.game and self.game.spaceship and self.game.spaceship.is_alive():
                    self.game.save_system.save_game(self.game)
            except Exception:
                pass
        finally:
            self.cleanup()

    def cleanup(self):
        print("Finalizando Navecraft...")
        config.save()
        pygame.quit()


def main():
    try:
        game = Navecraft()
        game.run()
    except Exception as e:
        print(f"Erro no jogo: {e}")
        traceback.print_exc()
    sys.exit(0)


if __name__ == "__main__":
    main()
