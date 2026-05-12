"""
Codex screen - resources, enemies, biomes, glossary, lore logs.
"""

import pygame
from utils import display
from utils.font import get_font, draw_panel, render_outlined
from utils.i18n import t
from systems.codex import CODEX_DATA, get_entry, LORE_LOG_ENTRIES
from systems.stats import lifetime


class CodexScreen:
    CATEGORIES = ['resources', 'enemies', 'biomes', 'glossary', 'logs']

    def __init__(self):
        self.visible = False
        self.category_idx = 0
        self.entry_idx = 0

    def toggle(self):
        self.visible = not self.visible

    def handle_event(self, event):
        if not self.visible:
            return False
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_ESCAPE, pygame.K_k):
                self.visible = False
                return True
            if event.key == pygame.K_LEFT:
                self.category_idx = (self.category_idx - 1) % len(self.CATEGORIES)
                self.entry_idx = 0
            elif event.key == pygame.K_RIGHT:
                self.category_idx = (self.category_idx + 1) % len(self.CATEGORIES)
                self.entry_idx = 0
            elif event.key == pygame.K_UP:
                self.entry_idx = max(0, self.entry_idx - 1)
            elif event.key == pygame.K_DOWN:
                cat = self.CATEGORIES[self.category_idx]
                count = len(LORE_LOG_ENTRIES) if cat == 'logs' else len(CODEX_DATA.get(cat, {}))
                self.entry_idx = min(count - 1, self.entry_idx + 1)
            return True
        return False

    def render(self, surface):
        if not self.visible:
            return
        w, h = display.WIDTH, display.HEIGHT
        overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 220))
        surface.blit(overlay, (0, 0))

        panel_w = min(820, w - 60)
        panel_h = min(580, h - 60)
        px = (w - panel_w) // 2
        py = (h - panel_h) // 2
        draw_panel(surface, pygame.Rect(px, py, panel_w, panel_h),
                   bg=(15, 25, 45), border=(0, 220, 255), bg_alpha=230, border_width=2, radius=10)

        title = render_outlined(get_font(32), t('codex.title'), (255, 255, 255), (0, 0, 0), 2)
        surface.blit(title, (px + 20, py + 14))

        # Category tabs
        for i, cat in enumerate(self.CATEGORIES):
            tab_x = px + 220 + i * 110
            label = {
                'resources': t('codex.resources'),
                'enemies': t('codex.enemies'),
                'biomes': t('codex.biomes'),
                'glossary': t('codex.glossary'),
                'logs': 'Logs',
            }[cat]
            color = (255, 255, 0) if i == self.category_idx else (180, 180, 180)
            text = render_outlined(get_font(18), label, color, (0, 0, 0), 1)
            surface.blit(text, (tab_x, py + 22))

        # Entry list
        cat = self.CATEGORIES[self.category_idx]
        list_x = px + 20
        list_y = py + 70
        list_w = 240

        if cat == 'logs':
            for i, e in enumerate(LORE_LOG_ENTRIES):
                selected = i == self.entry_idx
                color = (255, 220, 100) if selected else (200, 200, 200)
                line = render_outlined(get_font(15), e['id'], color, (0, 0, 0), 1)
                surface.blit(line, (list_x, list_y + i * 22))
            if 0 <= self.entry_idx < len(LORE_LOG_ENTRIES):
                self._render_log(surface, px, py, panel_w, panel_h,
                                 LORE_LOG_ENTRIES[self.entry_idx])
        else:
            keys = list(CODEX_DATA.get(cat, {}).keys())
            for i, k in enumerate(keys):
                selected = i == self.entry_idx
                entry = get_entry(cat, k)
                name = entry['name'] if entry else k
                color = (255, 220, 100) if selected else (200, 200, 200)
                line = render_outlined(get_font(15), name, color, (0, 0, 0), 1)
                surface.blit(line, (list_x, list_y + i * 22))
            if 0 <= self.entry_idx < len(keys):
                self._render_entry(surface, px, py, panel_w, panel_h, cat, keys[self.entry_idx])

        hint = render_outlined(get_font(14),
                               "<-/-> categorias  |  setas cima/baixo entradas  |  K ou ESC fechar",
                               (180, 180, 180), (0, 0, 0), 1)
        surface.blit(hint, (px + (panel_w - hint.get_width()) // 2, py + panel_h - 28))

    def _render_entry(self, surface, px, py, pw, ph, category, entry_id):
        entry = get_entry(category, entry_id)
        if not entry:
            return
        detail_x = px + 280
        detail_y = py + 70
        name = render_outlined(get_font(28), entry['name'], (0, 220, 255), (0, 0, 0), 2)
        surface.blit(name, (detail_x, detail_y))
        # Word wrap description
        font = get_font(18)
        words = entry['description'].split(' ')
        lines = []
        cur = ''
        max_w = pw - 300
        for word in words:
            test = (cur + ' ' + word).strip()
            if font.size(test)[0] > max_w:
                lines.append(cur)
                cur = word
            else:
                cur = test
        if cur:
            lines.append(cur)
        for i, line in enumerate(lines):
            text = font.render(line, True, (240, 240, 240))
            surface.blit(text, (detail_x, detail_y + 50 + i * 24))

    def _render_log(self, surface, px, py, pw, ph, log_entry):
        from utils.i18n import get_language
        detail_x = px + 280
        detail_y = py + 70
        lang = get_language()
        text_body = log_entry.get(lang, log_entry.get('pt', ''))
        name = render_outlined(get_font(24), log_entry['id'], (0, 220, 255), (0, 0, 0), 2)
        surface.blit(name, (detail_x, detail_y))
        font = get_font(18)
        words = text_body.split(' ')
        lines = []
        cur = ''
        for word in words:
            test = (cur + ' ' + word).strip()
            if font.size(test)[0] > pw - 300:
                lines.append(cur)
                cur = word
            else:
                cur = test
        if cur:
            lines.append(cur)
        for i, line in enumerate(lines):
            text = font.render(line, True, (240, 240, 240))
            surface.blit(text, (detail_x, detail_y + 40 + i * 24))
