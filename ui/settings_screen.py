"""
Tabbed settings screen - Video, Audio, Controls, Gameplay, Accessibility.
"""

import pygame
from utils import display, config
from utils.font import get_font, draw_panel, render_outlined
from utils.i18n import t, set_language, available_languages


TABS = ['video', 'audio', 'controls', 'gameplay', 'accessibility']

# Callback invoked when audio settings change. Set by main.py to wire AudioSystem.refresh_volumes.
_audio_change_listener = None


def set_audio_change_listener(callback):
    """Register a callback() invoked whenever an audio setting changes."""
    global _audio_change_listener
    _audio_change_listener = callback

TAB_LABELS_KEY = {
    'video': 'settings.video',
    'audio': 'settings.audio',
    'controls': 'settings.controls',
    'gameplay': 'settings.gameplay',
    'accessibility': 'settings.accessibility',
}


class SettingsScreen:
    def __init__(self):
        self.visible = False
        self.tab_idx = 0
        self.selected = 0
        # Cached layout for mouse hit-testing — populated by render().
        self._tab_rects = []
        self._row_rects = []
        self._panel_rect = None

    def toggle(self):
        self.visible = not self.visible

    def handle_event(self, event):
        if not self.visible:
            return False

        # Mouse support
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            # Tab click?
            for i, rect in enumerate(self._tab_rects):
                if rect.collidepoint(mx, my):
                    self.tab_idx = i
                    self.selected = 0
                    return True
            # Row click?
            rows = self._rows()
            for i, rect in enumerate(self._row_rects):
                if rect.collidepoint(mx, my):
                    self.selected = i
                    if i < len(rows):
                        # Click left half = decrement, right half = increment.
                        center_x = rect.x + rect.width // 2
                        delta = 1 if mx >= center_x else -1
                        self._adjust(rows[i], delta=delta)
                    return True
            # Click outside panel closes it
            if self._panel_rect and not self._panel_rect.collidepoint(mx, my):
                self.visible = False
                config.save()
                return True
            return True  # Consume click even if nothing matched

        if event.type == pygame.MOUSEWHEEL:
            rows = self._rows()
            if rows:
                self._adjust(rows[self.selected], delta=event.y)
                return True

        if event.type != pygame.KEYDOWN:
            return False
        if event.key == pygame.K_ESCAPE:
            self.visible = False
            config.save()
            return True
        if event.key == pygame.K_TAB:
            self.tab_idx = (self.tab_idx + 1) % len(TABS)
            self.selected = 0
            return True
        rows = self._rows()
        if not rows:
            return True
        if event.key == pygame.K_UP:
            self.selected = (self.selected - 1) % len(rows)
            return True
        if event.key == pygame.K_DOWN:
            self.selected = (self.selected + 1) % len(rows)
            return True
        if event.key in (pygame.K_LEFT, pygame.K_RIGHT):
            self._adjust(rows[self.selected], delta=-1 if event.key == pygame.K_LEFT else 1)
            return True
        if event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_KP_ENTER):
            self._adjust(rows[self.selected], delta=1)
            return True
        return True  # Consume all KEYDOWN while visible to prevent leak to game

    def _rows(self):
        tab = TABS[self.tab_idx]
        if tab == 'video':
            return [
                ('fullscreen', 'settings.fullscreen', 'bool'),
                ('borderless', 'settings.borderless', 'bool'),
                ('resolution', 'settings.resolution', 'res'),
                ('vsync', 'settings.vsync', 'bool'),
                ('fps_cap', 'FPS Cap', 'int_list', [30, 60, 90, 120, 144, 240]),
            ]
        if tab == 'audio':
            return [
                ('master', 'settings.master_volume', 'volume'),
                ('music', 'settings.music_volume', 'volume'),
                ('sfx', 'settings.sfx_volume', 'volume'),
                ('ambient', 'settings.ambient_volume', 'volume'),
                ('ui', 'UI', 'volume'),
            ]
        if tab == 'controls':
            return [
                ('hold_to_shoot', 'Hold to shoot', 'bool'),
                ('hold_to_boost', 'Hold to boost', 'bool'),
            ]
        if tab == 'gameplay':
            return [
                ('difficulty', 'settings.difficulty', 'str_list', ['easy', 'normal', 'hard', 'hardcore']),
                ('mode', 'Modo', 'str_list', ['standard', 'hardcore', 'pacific', 'creative']),
                ('autosave_seconds', 'Autosave (s)', 'int_list', [15, 30, 60, 120, 300]),
                ('tutorial_completed', 'settings.tutorial', 'bool'),
                ('language', 'settings.language', 'str_list', available_languages()),
            ]
        if tab == 'accessibility':
            return [
                ('colorblind_mode', 'settings.colorblind', 'str_list',
                 ['none', 'protanopia', 'deuteranopia', 'tritanopia']),
                ('ui_scale', 'settings.ui_scale', 'volume', 0.75, 2.0),
                ('reduce_motion', 'settings.reduce_motion', 'bool'),
                ('captions', 'settings.captions', 'bool'),
                ('high_contrast', 'High Contrast', 'bool'),
            ]
        return []

    def _adjust(self, row, delta=1):
        tab = TABS[self.tab_idx]
        section = {
            'video': 'display', 'audio': 'audio', 'controls': 'gameplay',
            'gameplay': 'gameplay', 'accessibility': 'accessibility',
        }[tab]
        key = row[0]
        kind = row[2]
        # Special-case: language is under i18n not gameplay
        if tab == 'gameplay' and key == 'language':
            langs = available_languages()
            cur = config.get('i18n', 'language', default='auto')
            idx = langs.index(cur) if cur in langs else 0
            new_idx = (idx + delta) % len(langs)
            set_language(langs[new_idx])
            return
        if kind == 'bool':
            cur = bool(config.get(section, key, default=False))
            config.set(section, key, not cur)
        elif kind == 'volume':
            lo = row[3] if len(row) > 3 else 0.0
            hi = row[4] if len(row) > 4 else 1.0
            cur = float(config.get(section, key, default=lo))
            step = (hi - lo) / 10
            new = max(lo, min(hi, cur + delta * step))
            config.set(section, key, round(new, 2))
        elif kind == 'int_list':
            opts = row[3]
            cur = config.get(section, key, default=opts[0])
            try:
                i = opts.index(cur)
            except ValueError:
                i = 0
            config.set(section, key, opts[(i + delta) % len(opts)])
        elif kind == 'str_list':
            opts = row[3]
            cur = config.get(section, key, default=opts[0])
            try:
                i = opts.index(cur)
            except ValueError:
                i = 0
            config.set(section, key, opts[(i + delta) % len(opts)])
        elif kind == 'res':
            resolutions = display.SUPPORTED_RESOLUTIONS
            cur = (config.get('display', 'width', default=1200), config.get('display', 'height', default=800))
            try:
                i = resolutions.index(cur)
            except ValueError:
                i = 0
            new = resolutions[(i + delta) % len(resolutions)]
            config.set('display', 'width', new[0])
            config.set('display', 'height', new[1])
            display.set_mode(width=new[0], height=new[1], fullscreen=False, borderless=False)
        # Live-apply video
        if tab == 'video':
            display.apply_from_config(config.load()['display'])
        # Live-apply audio
        if tab == 'audio' and _audio_change_listener is not None:
            try:
                _audio_change_listener()
            except Exception:
                pass
        # Phase Y.6.2 — live-apply UI scale (clear cached fonts at the old
        # scale so the new scale takes effect this frame without a restart).
        if tab == 'accessibility' and key == 'ui_scale':
            try:
                from utils.font import clear_cache
                clear_cache()
            except Exception:
                pass
        # Persist immediately so a crash doesn't lose the change
        try:
            config.save()
        except Exception:
            pass

    def render(self, surface):
        if not self.visible:
            return
        w, h = display.WIDTH, display.HEIGHT
        overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 210))
        surface.blit(overlay, (0, 0))

        panel_w = min(720, w - 80)
        panel_h = min(560, h - 80)
        px = (w - panel_w) // 2
        py = (h - panel_h) // 2
        self._panel_rect = pygame.Rect(px, py, panel_w, panel_h)
        draw_panel(surface, self._panel_rect,
                   bg=(15, 15, 35), border=(0, 220, 255), bg_alpha=235, border_width=2, radius=10)

        title = render_outlined(get_font(30), t('menu.settings'), (255, 255, 255), (0, 0, 0), 2)
        surface.blit(title, (px + 20, py + 14))

        # Tabs row — record rects for click hit-testing
        self._tab_rects = []
        for i, tab in enumerate(TABS):
            tab_x = px + 20 + i * 130
            color = (255, 255, 0) if i == self.tab_idx else (180, 180, 180)
            text = render_outlined(get_font(18), t(TAB_LABELS_KEY[tab]), color, (0, 0, 0), 1)
            surface.blit(text, (tab_x, py + 60))
            self._tab_rects.append(pygame.Rect(tab_x, py + 60, max(text.get_width(), 120), text.get_height() + 4))

        # Rows — record rects for click hit-testing
        rows = self._rows()
        self._row_rects = []
        for i, row in enumerate(rows):
            y = py + 100 + i * 36
            row_rect = pygame.Rect(px + 20, y - 4, panel_w - 40, 32)
            if i == self.selected:
                hl = pygame.Surface((row_rect.width, row_rect.height), pygame.SRCALPHA)
                hl.fill((40, 60, 100, 90))
                surface.blit(hl, (row_rect.x, row_rect.y))
            color = (255, 255, 0) if i == self.selected else (220, 220, 220)
            label_key = row[1]
            label = t(label_key) if label_key.startswith(('settings.', 'hud.', 'menu.')) else label_key
            label_text = render_outlined(get_font(18), label, color, (0, 0, 0), 1)
            surface.blit(label_text, (px + 30, y))
            # Value
            value = self._format_value(row)
            value_text = render_outlined(get_font(18), str(value), (200, 230, 255), (0, 0, 0), 1)
            surface.blit(value_text, (px + panel_w - value_text.get_width() - 30, y))
            self._row_rects.append(row_rect)

        hint = render_outlined(get_font(14),
                               "TAB=trocar aba  /\\=navegar  <>=ajustar  Mouse=clicar  ESC=fechar",
                               (180, 180, 180), (0, 0, 0), 1)
        surface.blit(hint, (px + (panel_w - hint.get_width()) // 2, py + panel_h - 28))

    def _format_value(self, row):
        tab = TABS[self.tab_idx]
        section = {
            'video': 'display', 'audio': 'audio', 'controls': 'gameplay',
            'gameplay': 'gameplay', 'accessibility': 'accessibility',
        }[tab]
        key, _, kind = row[0], row[1], row[2]
        if tab == 'gameplay' and key == 'language':
            return config.get('i18n', 'language', default='auto')
        if kind == 'bool':
            return 'ON' if config.get(section, key, default=False) else 'OFF'
        if kind == 'volume':
            return f"{config.get(section, key, default=0):.2f}"
        if kind == 'res':
            return f"{config.get('display', 'width', default=1200)}x{config.get('display', 'height', default=800)}"
        return str(config.get(section, key, default='?'))
