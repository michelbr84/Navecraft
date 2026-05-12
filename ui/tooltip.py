"""
Contextual tooltip - small text bubble near the cursor or a target.
"""

import pygame
from utils.font import get_font, draw_panel


def render_tooltip(surface, text, x, y, color=(255, 255, 255), bg=(0, 0, 0), max_width=320):
    if not text:
        return
    font = get_font(16)
    # Word wrap
    words = text.split(' ')
    lines = []
    cur = ''
    for w in words:
        test = (cur + ' ' + w).strip()
        if font.size(test)[0] > max_width:
            lines.append(cur)
            cur = w
        else:
            cur = test
    if cur:
        lines.append(cur)
    line_h = font.get_linesize()
    h = line_h * len(lines) + 12
    longest = max(font.size(l)[0] for l in lines) if lines else 0
    w = longest + 16
    # Clip to screen
    from utils import display as _d
    if x + w > _d.WIDTH:
        x = _d.WIDTH - w - 4
    if y + h > _d.HEIGHT:
        y = _d.HEIGHT - h - 4
    rect = pygame.Rect(x, y, w, h)
    draw_panel(surface, rect, bg=bg, border=(150, 150, 200), bg_alpha=200, border_width=1, radius=4)
    for i, line in enumerate(lines):
        text_surf = font.render(line, True, color)
        surface.blit(text_surf, (x + 8, y + 6 + i * line_h))
