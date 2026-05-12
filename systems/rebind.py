"""
Rebindable controls - merges base CONTROLS with user overrides from config.
"""

import pygame
from utils import config


def apply_rebinds(controls_dict):
    """Return a copy of the CONTROLS dict with user rebinds applied."""
    out = {k: list(v) for k, v in controls_dict.items()}
    rebinds = config.get('controls', 'rebinds', default={}) or {}
    for action, key_names in rebinds.items():
        if action in out and isinstance(key_names, list):
            resolved = []
            for kn in key_names:
                key = getattr(pygame, kn, None)
                if isinstance(key, int):
                    resolved.append(key)
            if resolved:
                out[action] = resolved
    return out


def set_rebind(action, key_names):
    """Save a rebind. key_names is a list of pygame K_* identifier strings."""
    rebinds = config.get('controls', 'rebinds', default={}) or {}
    rebinds = dict(rebinds)
    rebinds[action] = list(key_names)
    config.set('controls', 'rebinds', rebinds)
    config.save()


def reset_rebinds():
    config.set('controls', 'rebinds', {})
    config.save()
