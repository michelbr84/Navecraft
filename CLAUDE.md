# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Navecraft is a 2D space survival/exploration game built with Pygame. Everything (graphics, sounds, music, world) is **procedurally generated at runtime** — no asset files. Source code comments and in-game text are in **Portuguese** (with full English + Spanish localizations via `utils/i18n`); preserve PT-BR as the base language when editing strings.

## Commands

A `.venv/` already exists at the repo root. Activate it before running anything:

```powershell
.venv\Scripts\activate      # Windows
# source .venv/bin/activate # Linux/macOS
pip install -r requirements.txt
```

- **Run the game:** `python main.py`
- **Run all tests:** `python -m unittest discover -s tests -v`
- **Run a single test file:** `python -m unittest tests.test_new_systems`
- **Run a single test:** `python -m unittest tests.test_fixes.TestInputManagerFrameOrder.test_keys_just_pressed_survives_update_mouse`
- **Build a frozen distributable:** `pyinstaller Navecraft.spec`

Tests construct a `pygame.display` at module import — running them headless requires `SDL_VIDEODRIVER=dummy` *and* `SDL_AUDIODRIVER=dummy` (Windows PowerShell: `$env:SDL_VIDEODRIVER='dummy'; $env:SDL_AUDIODRIVER='dummy'`). The suite (`tests/test_fixes.py` + `tests/test_new_systems.py`) is 64 tests and takes a few seconds — several construct a full `core.game.Game()` and trigger world generation.

There is no linter/formatter configured. Runtime deps: `pygame>=2.5`, `numpy`, `noise`.

## Architecture

### State machine in `main.py`; world in `core/game.py`

`main.py` (`Navecraft` class) owns the pygame window, the clock, the top-level state machine, and the overlay screens (help, codex, settings, inventory, crafting, world map, death). States: `menu` → `playing` → `paused` / `game_over`. The `Game` class in `core/game.py` owns the play-state world: spaceship, planets, blocks, enemies, projectiles, particles, camera, score, and every gameplay subsystem. Anything world/gameplay-related belongs in `Game`; window/state/overlay routing belongs in `Navecraft`.

### `utils/display` replaces `settings.SCREEN_WIDTH/HEIGHT` as the live source of size

Settings exposes only **default** dimensions. The live current width/height live in `utils/display` (`display.WIDTH`, `display.HEIGHT`). All HUD/UI/menu code reads from `display.*`, not from `settings.SCREEN_*`. `display.set_mode(...)` updates these and also mirrors back to `settings.SCREEN_WIDTH/HEIGHT` for legacy code that still reads from `settings`. Fullscreen, borderless, resolution cycling, and vsync all route through `display.set_mode`.

If you add UI that depends on screen dimensions, **import `from utils import display`** and read `display.WIDTH` / `display.HEIGHT` / `display.ui_scale()` per-render — don't snapshot them at module import.

### Input has a strict per-frame lifecycle — don't move `clear_frame()`

`InputManager` (`core/input.py`) tracks three sets: `keys_pressed`, `keys_just_pressed`, `keys_just_released`. Contract:

1. `pygame.event.get()` in `Navecraft.handle_events()` → `Game.handle_event(event)` → `InputManager.handle_event()` populates `keys_just_pressed`.
2. `Game.update()` calls `input_manager.update_mouse()` near the start.
3. All `is_control_just_pressed(...)` checks happen during `Game.update()`.
4. **`input_manager.clear_frame()` is called at the END of `Game.update()`** — not the start.

If you reorder this, every `is_control_just_pressed` check silently breaks. `TestInputManagerFrameOrder` exists specifically to catch this regression.

### F1 dual-binding is resolved by state, not by key

In the `menu` state, `main.py` consumes F1 to toggle `settings.DEBUG_MODE`. In the `playing` state, F1 is delegated to `Game` where it triggers the Engine upgrade. Both bindings coexist intentionally — keep that routing in `Navecraft.handle_events()`, don't add F1 to `CONTROLS` for menu use.

### Subsystems are constructed in `Game.initialize_world()` in dependency order

Order matters: Spaceship first → `CraftingSystem(ship.inventory)`, `UpgradeSystem(ship)`, `MultiplayerSystem(game)`, `StationSystem()`. Then `WorldGenerator` produces planets/blocks/caves/enemies from `settings.SEED`. Merchants and starting mission chains spawn last.

`Game.update()` dispatches subsystems by control key and runs the per-frame ordering: spaceship → missions → multiplayer → physics → enemies + projectiles (with `SpatialHash` broad-phase) → particles → camera → weather/day-night/background/feedback → stats/achievements → autosave.

### Camera is smooth-follow + shake (additive)

`systems/camera.SmoothCamera` lerps toward a lead-the-target point, applies speed-based zoom-out, and adds `feedback.get_shake_offset()` each frame. Render code reads the final world-space offset from `camera.render_offset()` and subtracts it. Reduce-motion (accessibility) makes the camera snap directly. Don't add a `pygame.transform`-based camera.

### Feedback / juice is centralized

`systems/feedback.FeedbackSystem` (singleton `feedback`) is the single entry point for:
- Floating text (world or screen space) with optional damage numbers
- Hitstop (`hitstop(frames)`) — pauses everything for N frames
- Screen flash (`flash(color, strength, decay)`)
- Camera shake (`shake(intensity, frames)`)
- Slow-motion (`slowmo(factor, frames)`) — modifies `time_scale`
- Vignette (set/clear via `set_vignette(intensity)`)

Use `feedback.floating(...)` for all "+5 IRON", "Built!", "Mission complete!" messages — don't manually render floating text.

### Multiplayer key bindings must not collide with `settings.CONTROLS`

`MultiplayerSystem` uses numpad keys for player 2+. `TestMultiplayerKeyConflicts` enforces zero overlap. If you add a new main control, re-run that test.

### Save/load is a versioned, schema-validated JSON snapshot with rolling backups

`SaveSystem` writes `navecraft_save_{slot}.json` with `version: 2`. Loads validate schema and fall back to `.bak1`/`.bak2`/`.bak3` if the main file is corrupt. Includes a base64 PNG thumbnail captured at save time. Multi-slot via `SaveSystem(slot=N)`; legacy single-file path still works via constructor arg. Autosave fires every `AUTO_SAVE_INTERVAL` ms (30s); F9 = manual quick save.

### Audio is synthesized at startup with ADSR envelopes

`core/audio.py` builds all SFX from numpy waveforms with `_make_tone(freq, dur, wave='sine|square|tri|saw|noise', adsr...)`. Per-action variants (e.g. `variants['mine']` has 3 pitches) give natural variation. `play_at(name, sx, sy, lx, ly)` adds stereo pan + distance falloff. Music has two pre-rendered loops (calm, combat) and `update_combat_intensity(0..1)` crossfades between them based on enemy proximity.

### Persistent user config lives in `navecraft_config.json`

`utils/config.py` is the single source of truth for user-mutable settings: display, audio, gameplay (difficulty, mode, tutorial state, language), accessibility, controls (rebinds), telemetry consent. Use `config.get('section', 'key', default=...)` and `config.set('section', 'key', value)`; call `config.save()` to flush. Defaults are in `DEFAULTS` at the top of the file.

### Internationalization

`utils/i18n.py` defines a `STRINGS` dict per language (pt/en/es) and exposes `t('hud.health')` → translated string. Add keys at the top and use `t('your.new.key')` everywhere user-visible. `'pt'` is the fallback. `set_language(lang)` updates the persisted config and clears the cache.

### Accessibility

`systems/accessibility.colorblind_filter(color)` re-maps colors through protanopia/deuteranopia/tritanopia matrices when the matching mode is set. `is_reduce_motion()` is consulted by camera shake, slowmo, parallax, and the lighting system — respect it in any new motion-heavy code. `ui_scale_override()` is multiplied into `display.ui_scale()`.

### Settings & global tunables

`settings.py` is the single source for physics constants, FPS, generation seed/noise params, default control bindings (`CONTROLS`), culling distances, biome/resource tables, audio sample rate, and save/log paths. Modules use `from settings import *` — new tunables go here.

## Logging

`utils/logger.py` exposes a module-level `game_logger` singleton writing to `navecraft.log` (gitignored). Use `game_logger.log_game_event(category, detail)` for gameplay events. Crash reports go through `systems/telemetry.log_crash(...)` (opt-in only).
