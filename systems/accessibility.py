"""
Accessibility - colorblind palettes, UI scale, reduce-motion, captions.
"""

from utils import config


def colorblind_filter(color):
    """Map an (r,g,b) color through the current colorblind palette."""
    mode = config.get('accessibility', 'colorblind_mode', default='none')
    if mode == 'none':
        return color
    r, g, b = color[0], color[1], color[2]
    if mode == 'protanopia':
        # Daltonism (no red) - shift red into green/blue
        nr = int(0.567 * r + 0.433 * g)
        ng = int(0.558 * r + 0.442 * g)
        nb = int(0.242 * g + 0.758 * b)
    elif mode == 'deuteranopia':
        nr = int(0.625 * r + 0.375 * g)
        ng = int(0.700 * r + 0.300 * g)
        nb = int(0.300 * g + 0.700 * b)
    elif mode == 'tritanopia':
        nr = int(0.950 * r + 0.050 * g)
        ng = int(0.433 * g + 0.567 * b)
        nb = int(0.475 * g + 0.525 * b)
    else:
        return color
    return (max(0, min(255, nr)), max(0, min(255, ng)), max(0, min(255, nb)))


def is_reduce_motion():
    return bool(config.get('accessibility', 'reduce_motion', default=False))


def captions_enabled():
    return bool(config.get('accessibility', 'captions', default=True))


def ui_scale_override():
    return float(config.get('accessibility', 'ui_scale', default=1.0))
