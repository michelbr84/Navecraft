# Navecraft Mods

Drop mod packages here. Each mod is a directory with `__init__.py` exposing a `register(api)` function.

## Minimal example

```
mods/
  doubled_iron/
    __init__.py
```

```python
# mods/doubled_iron/__init__.py
def register(api):
    api.register_recipe("MEGA_REPAIR", {"IRON": 20, "GOLD": 10})

    def on_mine(block_type, value):
        # Hook fires every time a block is mined.
        pass

    api.on_event("mine", on_mine)
```

## API surface

`api.register_recipe(name, ingredients)` — add a craftable item
`api.register_block_type(name, color, value)` — add a new resource type
`api.on_event(name, callback)` — subscribe to game events: `"mine"`, `"build"`, `"kill"`, `"craft"`

See `systems/mod_loader.py` for the full surface.
