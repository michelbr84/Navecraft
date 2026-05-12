"""
Font helpers - outlined text rendering for HUD legibility, cached fonts at scaled sizes.
"""

import pygame
from utils import display

_font_cache = {}


def get_font(size):
    """Return cached pygame Font at logical `size` (scaled by display.ui_scale())."""
    scaled = max(8, int(size * display.ui_scale()))
    key = ('default', scaled)
    if key not in _font_cache:
        _font_cache[key] = pygame.font.Font(None, scaled)
    return _font_cache[key]


def clear_cache():
    _font_cache.clear()


def render_outlined(font, text, color, outline=(0, 0, 0), outline_width=2):
    """Render text with outline. Returns a Surface."""
    base = font.render(text, True, color)
    w, h = base.get_width() + 2 * outline_width, base.get_height() + 2 * outline_width
    out = pygame.Surface((w, h), pygame.SRCALPHA)
    o = font.render(text, True, outline)
    for dx in range(-outline_width, outline_width + 1):
        for dy in range(-outline_width, outline_width + 1):
            if dx == 0 and dy == 0:
                continue
            out.blit(o, (dx + outline_width, dy + outline_width))
    out.blit(base, (outline_width, outline_width))
    return out


def render_shadow(font, text, color, shadow=(0, 0, 0), offset=2):
    """Render text with drop shadow."""
    base = font.render(text, True, color)
    sh = font.render(text, True, shadow)
    out = pygame.Surface((base.get_width() + offset, base.get_height() + offset), pygame.SRCALPHA)
    out.blit(sh, (offset, offset))
    out.blit(base, (0, 0))
    return out


def draw_panel(surface, rect, bg=(0, 0, 0), border=(255, 255, 255), bg_alpha=170, border_width=1, radius=4):
    """Draw a translucent panel with optional border. Returns the panel surface."""
    panel = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    pygame.draw.rect(panel, (*bg, bg_alpha), panel.get_rect(), border_radius=radius)
    if border_width > 0:
        pygame.draw.rect(panel, border, panel.get_rect(), border_width, border_radius=radius)
    surface.blit(panel, rect.topleft)
    return panel
