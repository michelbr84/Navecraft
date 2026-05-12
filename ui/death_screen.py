"""
Death/game-over screen with detailed run stats.
"""

import pygame
from utils import display
from utils.font import get_font, render_outlined, draw_panel
from utils.i18n import t


class DeathScreen:
    def __init__(self):
        self.selected = 0
        self.options = ['menu.restart', 'menu.main', 'menu.quit']
        self.death_screenshot = None

    def capture(self, game_surface):
        """Capture a screenshot at moment of death."""
        try:
            self.death_screenshot = game_surface.copy()
        except Exception:
            self.death_screenshot = None

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected = (self.selected - 1) % len(self.options)
            elif event.key == pygame.K_DOWN:
                self.selected = (self.selected + 1) % len(self.options)
            elif event.key == pygame.K_RETURN:
                key = self.options[self.selected]
                if key == 'menu.restart':
                    return "restart"
                if key == 'menu.main':
                    return "main_menu"
                if key == 'menu.quit':
                    return "quit"
        return None

    def render(self, surface, score=0, run_stats=None, cause_of_death=None):
        w, h = display.WIDTH, display.HEIGHT
        # Dim the world below
        overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 220))
        surface.blit(overlay, (0, 0))

        # Snapshot in upper-left
        if self.death_screenshot:
            try:
                thumb = pygame.transform.smoothscale(self.death_screenshot, (220, 140))
                surface.blit(thumb, (40, 80))
                pygame.draw.rect(surface, (200, 50, 50), pygame.Rect(40, 80, 220, 140), 2)
            except Exception:
                pass

        title = render_outlined(get_font(58), t('death.title'), (255, 80, 80), (0, 0, 0), 3)
        surface.blit(title, ((w - title.get_width()) // 2, 60))

        # Cause of death
        cause_label = render_outlined(
            get_font(22),
            f"{t('death.cause')}: {self._format_cause(cause_of_death)}",
            (255, 200, 100), (0, 0, 0), 1)
        surface.blit(cause_label, ((w - cause_label.get_width()) // 2, 140))

        # Score
        score_label = render_outlined(get_font(36), f"{t('death.score')}: {score}", (255, 255, 100), (0, 0, 0), 2)
        surface.blit(score_label, ((w - score_label.get_width()) // 2, 200))

        # Stats panel
        if run_stats:
            panel_w = 540
            panel_h = 200
            panel_x = (w - panel_w) // 2
            panel_y = 260
            rect = pygame.Rect(panel_x, panel_y, panel_w, panel_h)
            draw_panel(surface, rect, bg=(0, 0, 0), border=(200, 200, 200), bg_alpha=180, border_width=1, radius=6)

            lines = [
                (t('death.time'), f"{int(run_stats.survival_time // 60)}m {int(run_stats.survival_time % 60)}s"),
                (t('death.mined'), str(run_stats.blocks_mined)),
                (t('death.killed'), str(run_stats.enemies_killed)),
                ('Construidos', str(run_stats.blocks_built)),
                ('Crafted', str(run_stats.items_crafted)),
                ('Upgrades', str(run_stats.upgrades_applied)),
                ('Planetas visitados', str(run_stats.planets_visited)),
            ]
            for i, (k, v) in enumerate(lines):
                line = render_outlined(get_font(18), f"{k}: {v}", (220, 220, 240), (0, 0, 0), 1)
                surface.blit(line, (panel_x + 20, panel_y + 15 + i * 24))

        # Options
        for i, key in enumerate(self.options):
            color = (255, 255, 0) if i == self.selected else (255, 255, 255)
            text = render_outlined(get_font(28), t(key), color, (0, 0, 0), 2)
            surface.blit(text, ((w - text.get_width()) // 2, h - 200 + i * 50))

    def _format_cause(self, cause):
        return {
            'oxygen': 'Sufocamento (oxigênio zerado)',
            'energy': 'Sistemas exauridos (energia zerada)',
            'combat': 'Destruído em combate',
            'storm': 'Tempestade solar',
        }.get(cause, 'Causa desconhecida')
