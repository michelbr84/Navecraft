"""
Interactive step-by-step tutorial. State-machine driven by gameplay events.
"""

import math
import pygame
from utils import display, config
from utils.font import get_font, render_outlined, draw_panel
from utils.i18n import t


class TutorialStep:
    def __init__(self, key, condition_fn, hint_key, highlight=None):
        self.key = key
        self.condition_fn = condition_fn  # called(game) -> bool when step is complete
        self.hint_key = hint_key
        self.highlight = highlight  # 'block' | 'enemy' | None


class TutorialSystem:
    def __init__(self):
        self.active = not config.get('gameplay', 'tutorial_completed', default=False)
        self.step_index = 0
        self.start_time = 0
        self.collected_iron = False
        self.steps = [
            TutorialStep('move', self._cond_moved, 'tutorial.move'),
            TutorialStep('approach', self._cond_near_block, 'tutorial.approach', highlight='block'),
            TutorialStep('mine', self._cond_mined, 'tutorial.mine'),
            TutorialStep('collected', self._cond_has_iron, 'tutorial.collected'),
            TutorialStep('select', self._cond_built, 'tutorial.select'),
            TutorialStep('fight', self._cond_shot, 'tutorial.fight'),
            TutorialStep('station', self._cond_station, 'tutorial.station'),
        ]
        self._moved = False
        self._initial_pos = None
        self._mined_once = False
        self._built_once = False
        self._shot_once = False
        self._station_built = False

    # --- step conditions ---
    def _cond_moved(self, game):
        if self._initial_pos is None and game.spaceship:
            self._initial_pos = (game.spaceship.x, game.spaceship.y)
        if game.spaceship and self._initial_pos:
            dx = game.spaceship.x - self._initial_pos[0]
            dy = game.spaceship.y - self._initial_pos[1]
            if dx * dx + dy * dy > 200 * 200:
                self._moved = True
        return self._moved

    def _cond_near_block(self, game):
        if not game.spaceship:
            return False
        for b in game.blocks:
            if getattr(b, 'collected', False):
                continue
            d = math.hypot(b.x - game.spaceship.x, b.y - game.spaceship.y)
            if d < 80:
                return True
        return False

    def _cond_mined(self, game):
        return self._mined_once

    def _cond_has_iron(self, game):
        if game.spaceship and game.spaceship.inventory.has_item('IRON', 1):
            return True
        return False

    def _cond_built(self, game):
        return self._built_once

    def _cond_shot(self, game):
        return self._shot_once

    def _cond_station(self, game):
        return self._station_built

    # --- event hooks ---
    def on_mine(self):
        self._mined_once = True

    def on_build(self):
        self._built_once = True

    def on_shoot(self):
        self._shot_once = True

    def on_station_built(self):
        self._station_built = True

    def skip(self):
        self.active = False
        config.set('gameplay', 'tutorial_completed', True)
        config.save()

    def update(self, game):
        if not self.active:
            return
        if self.step_index >= len(self.steps):
            self.active = False
            config.set('gameplay', 'tutorial_completed', True)
            config.save()
            from systems.feedback import feedback
            feedback.floating(display.WIDTH // 2, display.HEIGHT // 3, t('tutorial.done'),
                              color=(0, 255, 200), lifetime=120, size=32, world_space=False)
            return
        step = self.steps[self.step_index]
        if step.condition_fn(game):
            self.step_index += 1

    def get_highlight_target(self, game):
        """Return (x,y,radius) of the object to highlight, or None."""
        if not self.active or self.step_index >= len(self.steps):
            return None
        step = self.steps[self.step_index]
        if step.highlight == 'block' and game.spaceship:
            best = None
            best_d = 1e9
            for b in game.blocks:
                if getattr(b, 'collected', False):
                    continue
                d = math.hypot(b.x - game.spaceship.x, b.y - game.spaceship.y)
                if d < best_d:
                    best_d = d
                    best = b
            if best:
                return (best.x, best.y, 22)
        return None

    def render(self, surface):
        if not self.active or self.step_index >= len(self.steps):
            return
        step = self.steps[self.step_index]
        msg = t(step.hint_key)
        font = get_font(24)
        text = render_outlined(font, msg, (255, 255, 255), (0, 0, 0), 2)
        w = text.get_width() + 40
        h = text.get_height() + 30
        x = (display.WIDTH - w) // 2
        y = 60
        rect = pygame.Rect(x, y, w, h)
        draw_panel(surface, rect, bg=(20, 30, 60), border=(0, 255, 255), bg_alpha=200, border_width=2, radius=8)
        surface.blit(text, (x + 20, y + 15))

        # Skip hint
        skip = render_outlined(get_font(16), t('tutorial.skip'), (200, 200, 200), (0, 0, 0), 1)
        surface.blit(skip, (x + 20, y + h + 6))
