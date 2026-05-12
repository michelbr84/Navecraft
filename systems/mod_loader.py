"""
Mod loader - discovers mod packages in ./mods/ and imports their entrypoint.

Mod structure:
    mods/my_mod/
        __init__.py     # must define `register(api)`
        ...

The API exposes hooks: `register_recipe`, `register_block_type`, etc.
"""

import importlib.util
import os
import sys


class ModAPI:
    """A minimal API surface mods can call to extend the game."""

    def __init__(self):
        self.recipes = []
        self.blocks = []
        self.events = {}

    def register_recipe(self, name, ingredients):
        self.recipes.append({'name': name, 'ingredients': dict(ingredients)})

    def register_block_type(self, name, color, value):
        self.blocks.append({'name': name, 'color': color, 'value': value})

    def on_event(self, event_name, callback):
        self.events.setdefault(event_name, []).append(callback)

    def fire(self, event_name, *args, **kwargs):
        for cb in self.events.get(event_name, []):
            try:
                cb(*args, **kwargs)
            except Exception as e:
                print(f"[mod_loader] handler for {event_name} crashed: {e}")


mod_api = ModAPI()
_loaded_mods = []


def load_all(mods_dir="mods"):
    if not os.path.isdir(mods_dir):
        return _loaded_mods
    for entry in os.listdir(mods_dir):
        path = os.path.join(mods_dir, entry)
        init_py = os.path.join(path, '__init__.py')
        if os.path.isdir(path) and os.path.exists(init_py):
            try:
                spec = importlib.util.spec_from_file_location(f"mod_{entry}", init_py)
                module = importlib.util.module_from_spec(spec)
                sys.modules[spec.name] = module
                spec.loader.exec_module(module)
                if hasattr(module, 'register'):
                    module.register(mod_api)
                    _loaded_mods.append(entry)
                    print(f"[mod_loader] loaded mod: {entry}")
            except Exception as e:
                print(f"[mod_loader] failed to load {entry}: {e}")
    return _loaded_mods


def list_loaded():
    return list(_loaded_mods)
