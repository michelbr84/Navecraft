"""
Display manager - mutable screen dimensions, fullscreen modes, resolution switching.

All UI code that needs current screen size should read display.WIDTH / display.HEIGHT
instead of settings.SCREEN_WIDTH / settings.SCREEN_HEIGHT (which are defaults only).
"""

import pygame
import settings as _settings

WIDTH = _settings.SCREEN_WIDTH
HEIGHT = _settings.SCREEN_HEIGHT
FULLSCREEN = False
BORDERLESS = False
VSYNC = True
FPS_CAP = 60

_screen = None
_listeners = []

SUPPORTED_RESOLUTIONS = [
    (1280, 720),
    (1600, 900),
    (1920, 1080),
    (2560, 1440),
    (1200, 800),
    (1366, 768),
    (1440, 900),
]


def get_screen():
    return _screen


def add_listener(callback):
    """Register a callback(width, height) called whenever resolution changes."""
    _listeners.append(callback)


def _notify():
    for cb in _listeners:
        try:
            cb(WIDTH, HEIGHT)
        except Exception:
            pass


def set_mode(width=None, height=None, fullscreen=None, borderless=None, vsync=None):
    """Apply a new display mode. Returns the new screen surface."""
    global WIDTH, HEIGHT, FULLSCREEN, BORDERLESS, VSYNC, _screen

    if fullscreen is not None:
        FULLSCREEN = fullscreen
    if borderless is not None:
        BORDERLESS = borderless
    if vsync is not None:
        VSYNC = vsync

    flags = 0
    if FULLSCREEN:
        flags |= pygame.FULLSCREEN
        info = pygame.display.Info()
        WIDTH = info.current_w
        HEIGHT = info.current_h
    elif BORDERLESS:
        flags |= pygame.NOFRAME
        info = pygame.display.Info()
        WIDTH = info.current_w
        HEIGHT = info.current_h
    else:
        if width is not None and height is not None:
            WIDTH = width
            HEIGHT = height

    try:
        _screen = pygame.display.set_mode((WIDTH, HEIGHT), flags, vsync=1 if VSYNC else 0)
    except (TypeError, pygame.error):
        _screen = pygame.display.set_mode((WIDTH, HEIGHT), flags)

    _settings.SCREEN_WIDTH = WIDTH
    _settings.SCREEN_HEIGHT = HEIGHT
    _notify()
    return _screen


def toggle_fullscreen():
    set_mode(fullscreen=not FULLSCREEN, borderless=False)


def toggle_borderless():
    set_mode(fullscreen=False, borderless=not BORDERLESS)


def cycle_resolution():
    """Cycle to the next supported windowed resolution."""
    try:
        idx = SUPPORTED_RESOLUTIONS.index((WIDTH, HEIGHT))
    except ValueError:
        idx = -1
    idx = (idx + 1) % len(SUPPORTED_RESOLUTIONS)
    w, h = SUPPORTED_RESOLUTIONS[idx]
    set_mode(width=w, height=h, fullscreen=False, borderless=False)


def apply_from_config(cfg):
    """Apply settings from a config dict ({width, height, fullscreen, borderless, vsync, fps_cap})."""
    global FPS_CAP
    if 'fps_cap' in cfg:
        FPS_CAP = int(cfg['fps_cap'])
    set_mode(
        width=cfg.get('width', WIDTH),
        height=cfg.get('height', HEIGHT),
        fullscreen=cfg.get('fullscreen', FULLSCREEN),
        borderless=cfg.get('borderless', BORDERLESS),
        vsync=cfg.get('vsync', VSYNC),
    )


def export_config():
    return {
        'width': WIDTH,
        'height': HEIGHT,
        'fullscreen': FULLSCREEN,
        'borderless': BORDERLESS,
        'vsync': VSYNC,
        'fps_cap': FPS_CAP,
    }


def ui_scale():
    """UI scale factor based on actual height vs reference 800px."""
    return max(0.6, min(2.5, HEIGHT / 800.0))
