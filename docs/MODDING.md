# Navecraft — Modding Guide

Navecraft supports lightweight Python mods loaded at startup. A mod is a
`.py` file dropped into the `mods/` directory at the repo root.

## Quick start

1. Create `mods/my_mod.py`.
2. Define a `register(game)` function. It will be called once after the
   game initializes but before the main loop starts.
3. Mutate any subsystem you like. Common targets:
   - `game.spaceship` — player ship stats.
   - `game.audio_system.sounds` — pre-rendered SFX (replace with your own).
   - `systems.codex.CODEX_DATA` — add lore entries.
   - `systems.skills.SKILL_TREE` — add skill nodes.
   - `systems.upgrades.UpgradeSystem` — add new upgrade definitions.

## Minimal example

```python
# mods/example_double_speed.py
def register(game):
    game.spaceship.max_speed *= 2.0
    print("Mod: Double max speed enabled.")
```

Run `python main.py` and watch the console — your mod prints when the
game loads.

## Loading order

`systems/mod_loader.py` enumerates every `.py` file under `mods/` and calls
`register(game)` on each, in alphabetical order. Mods cannot depend on each
other's order beyond that.

## Adding a codex entry

```python
# mods/lore_my_faction.py
from systems.codex import CODEX_DATA

def register(game):
    CODEX_DATA.setdefault('factions', {})['MY_CLAN'] = {
        'pt': ('Clã do Cometa', 'Pioneiros nômades dos cinturões externos.'),
        'en': ('Comet Clan', 'Nomadic pioneers of the outer belts.'),
        'es': ('Clan del Cometa', 'Pioneros nómadas de los cinturones exteriores.'),
    }
```

## Adding a recipe

```python
# mods/recipe_super_shield.py
def register(game):
    game.crafting_system.recipes['SUPER_SHIELD'] = {
        'CRYSTAL': 30, 'GOLD': 20, 'IRON': 50,
    }
```

## Adding a skill node

```python
# mods/skill_warp_drive.py
from systems.skills import SKILL_TREE

def register(game):
    SKILL_TREE['piloting']['nodes']['warp_drive'] = {
        'pt': 'Motor de Dobra', 'en': 'Warp Drive',
        'cost': 5,
        'effect': 'warp_speed +50%',
    }
```

## Replacing a procedural SFX

```python
# mods/sfx_laser.py
import numpy as np
from core.audio import _make_tone, _to_stereo  # internal helpers

def register(game):
    sample = _make_tone(880, 0.2, wave='square', amp=0.5, freq_end=200)
    game.audio_system.sounds['shoot'] = _to_stereo(sample)
```

## Listening to game events

The game does not currently expose an event bus. The recommended pattern
is to wrap a system method:

```python
# mods/log_kills.py
def register(game):
    original = game.mission_system.update_combat_missions
    def wrapped(enemy_type):
        print(f"[mod] kill: {enemy_type}")
        return original(enemy_type)
    game.mission_system.update_combat_missions = wrapped
```

## Distribution

Distribute mods as single `.py` files. Users drop them in their `mods/`
directory and restart the game. There is no signing or sandboxing — mods
run with full Python privileges, so only install mods you trust.

## Future work

- Hot-reload (currently restart-only).
- Event bus.
- Mod manifest (`mod.json`) with version, dependencies, author.
- In-game mod browser.

Contributions welcome — see `CONTRIBUTING.md`.
