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
            TutorialStep('mine', self._cond_mined, 'tutorial.mine', highlight='block'),
            TutorialStep('collected', self._cond_has_iron, 'tutorial.collected'),
            TutorialStep('select', self._cond_built, 'tutorial.select'),
            TutorialStep('fight', self._cond_shot, 'tutorial.fight', highlight='enemy'),
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
        elif step.highlight == 'enemy' and game.spaceship and game.enemies:
            best = None
            best_d = 1e9
            for e in game.enemies:
                d = math.hypot(e.x - game.spaceship.x, e.y - game.spaceship.y)
                if d < best_d:
                    best_d = d
                    best = e
            if best:
                return (best.x, best.y, getattr(best, 'size', 18) + 6)
        return None

    def _reward_key_for_step(self, step_key):
        """Map current tutorial step to a reward i18n key (or None)."""
        return {
            'approach':  'tutorial.reward.mine',
            'mine':      'tutorial.reward.mine',
            'select':    'tutorial.reward.build',
            'station':   'tutorial.reward.station',
        }.get(step_key)

    def get_progress(self, game):
        """Phase X.4 — return (current, target, label) for the active step's
        progress bar, or None if the step has no progress meter.

        Currently we surface mining progress: how many IRON units the player
        has collected toward a small target so they can see themselves
        approaching the goal in real time."""
        if not self.active or self.step_index >= len(self.steps):
            return None
        step = self.steps[self.step_index]
        if step.key in ('approach', 'mine') and game.spaceship:
            have = game.spaceship.inventory.get_item_count('IRON')
            target = 5
            return (min(have, target), target, 'IRON')
        return None

    def render(self, surface, game=None):
        if not self.active or self.step_index >= len(self.steps):
            return
        step = self.steps[self.step_index]
        msg = t(step.hint_key)
        font_hint = get_font(22)
        font_title = get_font(16)
        font_reward = get_font(16)

        # Compose three optional lines: goal header, hint, reward.
        goal_surf = render_outlined(font_title, t('tutorial.goal').upper(),
                                    (255, 220, 80), (0, 0, 0), 1)
        hint_surf = render_outlined(font_hint, msg, (255, 255, 255), (0, 0, 0), 2)
        reward_key = self._reward_key_for_step(step.key)
        reward_surf = render_outlined(font_reward, t(reward_key),
                                      (160, 230, 160), (0, 0, 0), 1) if reward_key else None

        lines = [goal_surf, hint_surf]
        if reward_surf is not None:
            lines.append(reward_surf)

        # Progress bar geometry (computed before panel so we can size it).
        progress = self.get_progress(game) if game is not None else None

        line_h = max(s.get_height() for s in lines) + 4
        max_w = max(s.get_width() for s in lines)
        panel_w = max_w + 40
        panel_h = line_h * len(lines) + 18
        if progress is not None:
            panel_h += 16  # extra height for progress bar
        x = (display.WIDTH - panel_w) // 2
        y = 32
        rect = pygame.Rect(x, y, panel_w, panel_h)
        draw_panel(surface, rect, bg=(20, 30, 60), border=(0, 255, 255),
                   bg_alpha=210, border_width=2, radius=8)

        cy = y + 8
        for s in lines:
            surface.blit(s, (x + (panel_w - s.get_width()) // 2, cy))
            cy += line_h

        # Progress bar (Phase X.4.3) — visible IRON count toward small target.
        if progress is not None:
            current, target, label = progress
            bar_w = panel_w - 60
            bar_x = x + 30
            bar_y = cy + 2
            pygame.draw.rect(surface, (40, 50, 70),
                             (bar_x, bar_y, bar_w, 8), border_radius=3)
            fill_w = int(bar_w * (current / max(target, 1)))
            if fill_w > 0:
                pygame.draw.rect(surface, (255, 220, 80),
                                 (bar_x, bar_y, fill_w, 8), border_radius=3)
            count_surf = render_outlined(font_reward, f"{current}/{target} {label}",
                                         (240, 240, 240), (0, 0, 0), 1)
            surface.blit(count_surf, (x + (panel_w - count_surf.get_width()) // 2, bar_y - 2))

        # Skip hint
        skip = render_outlined(get_font(14), t('tutorial.skip'), (200, 200, 200), (0, 0, 0), 1)
        surface.blit(skip, (x + 20, y + panel_h + 4))
