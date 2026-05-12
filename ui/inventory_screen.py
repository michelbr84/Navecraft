"""
Full-screen inventory with grid, tooltips, sort, and rarity colors.
"""

import pygame
from utils import display
from utils.font import get_font, draw_panel, render_outlined
from utils.i18n import t
from systems.codex import get_entry as codex_get


RARITY_COLOR = {
    'common': (200, 200, 200),
    'uncommon': (100, 255, 100),
    'rare': (100, 150, 255),
    'epic': (200, 100, 255),
    'legendary': (255, 180, 50),
}

ITEM_RARITY = {
    'IRON': 'common',
    'FUEL': 'common',
    'OXYGEN': 'common',
    'GOLD': 'rare',
    'CRYSTAL': 'epic',
    'REPAIR_KIT': 'uncommon',
    'ENERGY_PACK': 'uncommon',
    'OXYGEN_TANK': 'uncommon',
    'SHIELD_BOOSTER': 'rare',
}


class InventoryScreen:
    def __init__(self):
        self.visible = False
        self.sort_mode = 'type'  # type | qty | value
        self.hover = None

    def toggle(self):
        self.visible = not self.visible

    def handle_event(self, event):
        if not self.visible:
            return False
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_ESCAPE, pygame.K_i):
                self.visible = False
                return True
            if event.key == pygame.K_TAB:
                modes = ['type', 'qty', 'value']
                self.sort_mode = modes[(modes.index(self.sort_mode) + 1) % len(modes)]
                return True
        return False

    def render(self, surface, inventory):
        if not self.visible:
            return
        w, h = display.WIDTH, display.HEIGHT
        overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))

        panel_w = min(720, w - 80)
        panel_h = min(540, h - 80)
        panel_x = (w - panel_w) // 2
        panel_y = (h - panel_h) // 2
        rect = pygame.Rect(panel_x, panel_y, panel_w, panel_h)
        draw_panel(surface, rect, bg=(10, 20, 40), border=(0, 200, 220), bg_alpha=220, border_width=2, radius=10)

        title = render_outlined(get_font(32), t('hud.inventory'), (255, 255, 255), (0, 0, 0), 2)
        surface.blit(title, (panel_x + 20, panel_y + 16))

        sort_hint = render_outlined(get_font(16), f"TAB: sort ({self.sort_mode})", (180, 180, 180), (0, 0, 0), 1)
        surface.blit(sort_hint, (panel_x + panel_w - sort_hint.get_width() - 16, panel_y + 22))

        items = list(inventory.items.items())
        if self.sort_mode == 'qty':
            items.sort(key=lambda kv: -kv[1])
        elif self.sort_mode == 'value':
            from settings import RESOURCE_TYPES
            items.sort(key=lambda kv: -RESOURCE_TYPES.get(kv[0], {}).get('value', 0))
        else:
            items.sort(key=lambda kv: kv[0])

        cell = 64
        cols = (panel_w - 40) // (cell + 8)
        font_qty = get_font(16)
        font_name = get_font(14)

        for i, (item, qty) in enumerate(items):
            col = i % cols
            row = i // cols
            x = panel_x + 20 + col * (cell + 8)
            y = panel_y + 70 + row * (cell + 28)
            rarity = ITEM_RARITY.get(item, 'common')
            color = RARITY_COLOR[rarity]

            slot = pygame.Rect(x, y, cell, cell)
            pygame.draw.rect(surface, (30, 30, 50), slot, border_radius=4)
            pygame.draw.rect(surface, color, slot, 2, border_radius=4)
            # Inner glyph (square colored)
            glyph_color = self._item_color(item)
            inner = slot.inflate(-16, -16)
            pygame.draw.rect(surface, glyph_color, inner, border_radius=4)
            # Qty
            qty_text = font_qty.render(str(qty), True, (255, 255, 255))
            surface.blit(qty_text, (x + cell - qty_text.get_width() - 4, y + cell - qty_text.get_height() - 2))
            # Name
            name_text = font_name.render(item, True, color)
            surface.blit(name_text, (x + (cell - name_text.get_width()) // 2, y + cell + 4))

        # Hover tooltip
        mx, my = pygame.mouse.get_pos()
        for i, (item, qty) in enumerate(items):
            col = i % cols
            row = i // cols
            x = panel_x + 20 + col * (cell + 8)
            y = panel_y + 70 + row * (cell + 28)
            if pygame.Rect(x, y, cell, cell).collidepoint(mx, my):
                from ui.tooltip import render_tooltip
                entry = codex_get('resources', item)
                if entry:
                    desc = f"{entry['name']} ({ITEM_RARITY.get(item, 'common')})\n{entry['description']}"
                else:
                    desc = f"{item}"
                render_tooltip(surface, desc, mx + 16, my + 16)
                break

    def _item_color(self, item):
        colors = {
            'IRON': (169, 169, 169),
            'GOLD': (255, 215, 0),
            'CRYSTAL': (138, 43, 226),
            'FUEL': (255, 165, 0),
            'OXYGEN': (135, 206, 235),
            'REPAIR_KIT': (50, 200, 50),
            'ENERGY_PACK': (255, 255, 100),
            'OXYGEN_TANK': (100, 220, 255),
            'SHIELD_BOOSTER': (180, 100, 255),
        }
        return colors.get(item, (200, 200, 200))
