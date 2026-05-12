"""
Reorganized HUD - zone-based layout, panels, outlined fonts, resolution-scaling.

Zones:
  bottom-left   : status bars (health, energy, oxygen, fuel)
  bottom-center : quick inventory + selected block
  top-right     : score + minimap + position/velocity
  top-center    : top-of-screen alerts and tutorial
  bottom-right  : station blueprint info + waypoint compass
"""

import pygame
from utils import display
from utils.font import get_font, draw_panel, render_outlined
from utils.i18n import t
from systems.accessibility import colorblind_filter
from settings import RESOURCE_TYPES, INVENTORY_SLOTS, SLOT_SIZE


class HUD:
    def __init__(self):
        self.spaceship = None
        self.score = 0
        self.last_alert = (0, '', (255, 80, 80))
        self.alert_timer = 0

    def render(self, surface, spaceship, camera_x, camera_y, score=0):
        if not spaceship:
            return
        self.spaceship = spaceship
        self.score = score
        scale = display.ui_scale()
        # Status panel
        self._render_status_panel(surface, scale)
        # Quick inventory + selected block
        self._render_quickbar(surface, scale)
        # Score & info (top-right)
        self._render_top_right(surface, scale)
        # Alerts (top-center)
        self._render_alerts(surface, scale)

    # ----- status bars (bottom-left) -----
    def _render_status_panel(self, surface, scale):
        bar_w = int(220 * scale)
        bar_h = int(18 * scale)
        gap = int(8 * scale)
        margin = int(14 * scale)
        rows = [
            (t('hud.health'), self.spaceship.health, self.spaceship.max_health, (0, 220, 100)),
            (t('hud.energy'), self.spaceship.energy, self.spaceship.max_energy, (60, 160, 255)),
            (t('hud.oxygen'), self.spaceship.oxygen, self.spaceship.max_oxygen, (100, 220, 255)),
            (t('hud.fuel'),   self.spaceship.fuel,   self.spaceship.max_fuel,   (255, 165, 50)),
        ]
        panel_w = bar_w + int(120 * scale)
        panel_h = len(rows) * (bar_h + gap) + int(20 * scale)
        x = margin
        y = display.HEIGHT - panel_h - margin

        draw_panel(surface, pygame.Rect(x, y, panel_w, panel_h),
                   bg=(0, 0, 0), border=(120, 180, 220), bg_alpha=140, border_width=1, radius=6)

        font = get_font(15)
        for i, (label, cur, mx, base_color) in enumerate(rows):
            ratio = max(0.0, min(1.0, cur / max(mx, 1)))
            color = colorblind_filter(self._bar_color(label, ratio, base_color))
            row_y = y + int(10 * scale) + i * (bar_h + gap)
            bar_rect = pygame.Rect(x + int(90 * scale), row_y, bar_w, bar_h)
            pygame.draw.rect(surface, (25, 30, 40), bar_rect, border_radius=3)
            fill_rect = pygame.Rect(bar_rect.x, bar_rect.y, int(bar_w * ratio), bar_h)
            pygame.draw.rect(surface, color, fill_rect, border_radius=3)
            pygame.draw.rect(surface, (220, 230, 240), bar_rect, 1, border_radius=3)
            label_text = render_outlined(font, label, (240, 240, 250), (0, 0, 0), 1)
            surface.blit(label_text, (x + int(10 * scale), row_y + (bar_h - label_text.get_height()) // 2))
            val_text = render_outlined(font, f"{int(cur)}/{int(mx)}", (255, 255, 255), (0, 0, 0), 1)
            surface.blit(val_text, (bar_rect.right - val_text.get_width() - 6,
                                    row_y + (bar_h - val_text.get_height()) // 2))

    def _bar_color(self, label, ratio, default):
        # Critical state shifts to red
        if label in (t('hud.health'), t('hud.oxygen'), t('hud.fuel'), t('hud.energy')):
            if ratio < 0.25:
                return (240, 60, 60)
            if ratio < 0.5:
                return (240, 200, 60)
        return default

    # ----- quick inventory + selected block (bottom-center) -----
    def _render_quickbar(self, surface, scale):
        slot = int(SLOT_SIZE * scale)
        gap = int(6 * scale)
        items = ['IRON', 'GOLD', 'CRYSTAL', 'FUEL', 'OXYGEN']
        bar_w = len(items) * (slot + gap) + int(20 * scale)
        bar_h = slot + int(28 * scale)
        x = (display.WIDTH - bar_w) // 2
        y = display.HEIGHT - bar_h - int(14 * scale)
        draw_panel(surface, pygame.Rect(x, y, bar_w, bar_h),
                   bg=(0, 0, 0), border=(120, 180, 220), bg_alpha=160, border_width=1, radius=8)

        selected = getattr(self.spaceship, 'selected_block_type', None)
        font_qty = get_font(13)
        font_label = get_font(11)
        for i, item in enumerate(items):
            sx = x + int(10 * scale) + i * (slot + gap)
            sy = y + int(14 * scale)
            rect = pygame.Rect(sx, sy, slot, slot)
            border_color = (255, 220, 50) if item == selected else (100, 140, 180)
            pygame.draw.rect(surface, (28, 32, 48), rect, border_radius=4)
            color = colorblind_filter(RESOURCE_TYPES[item]['color'])
            inner = rect.inflate(-int(8 * scale), -int(8 * scale))
            pygame.draw.rect(surface, color, inner, border_radius=3)
            pygame.draw.rect(surface, border_color, rect, 2, border_radius=4)
            qty = self.spaceship.inventory.get_item_count(item)
            qty_text = render_outlined(font_qty, str(qty), (255, 255, 255), (0, 0, 0), 1)
            surface.blit(qty_text, (rect.right - qty_text.get_width() - 3,
                                    rect.bottom - qty_text.get_height() - 1))
            key_label = render_outlined(font_label, str(i + 1), (200, 200, 200), (0, 0, 0), 1)
            surface.blit(key_label, (rect.x + 3, rect.y + 1))

        # Selected block summary
        if selected:
            summary = f"{t('hud.block')}: {selected}"
            text = render_outlined(get_font(15), summary, (255, 220, 100), (0, 0, 0), 1)
            surface.blit(text, ((display.WIDTH - text.get_width()) // 2, y - 22))

    # ----- top-right: score + position + velocity -----
    def _render_top_right(self, surface, scale):
        font = get_font(20)
        score_text = render_outlined(font, f"{t('hud.score')}: {self.score}",
                                     (255, 215, 50), (0, 0, 0), 2)
        x = display.WIDTH - score_text.get_width() - int(14 * scale)
        y = int(14 * scale)
        surface.blit(score_text, (x, y))

        small = get_font(14)
        pos_text = render_outlined(small,
                                   f"({int(self.spaceship.x)}, {int(self.spaceship.y)})",
                                   (200, 230, 255), (0, 0, 0), 1)
        surface.blit(pos_text, (display.WIDTH - pos_text.get_width() - int(14 * scale),
                                y + score_text.get_height() + 2))
        speed = (self.spaceship.vx ** 2 + self.spaceship.vy ** 2) ** 0.5
        vel_text = render_outlined(small, f"v={speed:.1f}", (200, 230, 255), (0, 0, 0), 1)
        surface.blit(vel_text, (display.WIDTH - vel_text.get_width() - int(14 * scale),
                                y + score_text.get_height() + 22))

    # ----- top-center alerts -----
    def push_alert(self, message, color=(255, 80, 80), duration_frames=90):
        self.last_alert = (duration_frames, message, color)
        self.alert_timer = duration_frames

    def _render_alerts(self, surface, scale):
        if self.alert_timer <= 0:
            return
        self.alert_timer -= 1
        _, msg, color = self.last_alert
        text = render_outlined(get_font(26), msg, color, (0, 0, 0), 2)
        bg_rect = pygame.Rect(0, 0, text.get_width() + 30, text.get_height() + 14)
        bg_rect.center = (display.WIDTH // 2, int(70 * scale))
        draw_panel(surface, bg_rect, bg=(60, 0, 0), border=color, bg_alpha=180, border_width=2, radius=6)
        surface.blit(text, (bg_rect.x + 15, bg_rect.y + 7))
