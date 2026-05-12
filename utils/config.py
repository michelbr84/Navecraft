"""
Persistent user config (config.json) - resolution, audio, controls, accessibility, gameplay.
"""

import json
import os

CONFIG_FILE = "navecraft_config.json"

DEFAULTS = {
    'display': {
        'width': 1200,
        'height': 800,
        'fullscreen': False,
        'borderless': False,
        'vsync': True,
        'fps_cap': 60,
    },
    'audio': {
        'master': 0.8,
        'music': 0.6,
        'sfx': 0.8,
        'ambient': 0.5,
        'ui': 0.7,
    },
    'gameplay': {
        'difficulty': 'normal',  # easy, normal, hard, hardcore
        'autosave_seconds': 30,
        'tutorial_completed': False,
        'first_run': True,
        'hold_to_shoot': False,
        'hold_to_boost': False,
        'pause_anywhere': True,
        'mode': 'standard',  # standard, hardcore, pacific, creative
    },
    'accessibility': {
        'colorblind_mode': 'none',  # none, protanopia, deuteranopia, tritanopia
        'ui_scale': 1.0,
        'reduce_motion': False,
        'captions': True,
        'high_contrast': False,
        # Phase Y.6.4 — pause automatically when the window loses focus.
        'autopause_on_focus_loss': True,
    },
    'i18n': {
        'language': 'auto',
    },
    'controls': {
        'rebinds': {},
    },
    'telemetry': {
        'enabled': False,
        'consented': False,
    },
}

_cfg = None


def _deep_merge(base, override):
    out = dict(base)
    for k, v in override.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _deep_merge(out[k], v)
        else:
            out[k] = v
    return out


def load():
    global _cfg
    if _cfg is not None:
        return _cfg
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            _cfg = _deep_merge(DEFAULTS, data)
        except Exception:
            _cfg = json.loads(json.dumps(DEFAULTS))
    else:
        _cfg = json.loads(json.dumps(DEFAULTS))
    return _cfg


def save():
    if _cfg is None:
        return
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(_cfg, f, indent=2)
    except Exception as e:
        print(f"[config] save failed: {e}")


def get(*keys, default=None):
    cfg = load()
    node = cfg
    for k in keys:
        if not isinstance(node, dict) or k not in node:
            return default
        node = node[k]
    return node


def set(*args):
    """set('audio','master',0.5) - sets nested key."""
    if len(args) < 2:
        raise ValueError("set requires at least one key and a value")
    cfg = load()
    *keys, value = args
    node = cfg
    for k in keys[:-1]:
        if k not in node or not isinstance(node[k], dict):
            node[k] = {}
        node = node[k]
    node[keys[-1]] = value


def reset():
    global _cfg
    _cfg = json.loads(json.dumps(DEFAULTS))
    save()
