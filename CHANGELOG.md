# Changelog

All notable changes are tracked here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project
uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added — v1.3 sweep
- Phase 0.6–0.10 fixes for runtime-observed visual bugs (white halo around
  ship, packed-block readability, parallax/foreground confusion, missing
  mining-range indicator, illegible station HUD over planets).
- Phase X UX clarity: animated tutorial highlight + off-screen arrow,
  rewritten step-by-step tutorial strings (PT/EN/ES), top-of-screen "PRÓXIMO
  PASSO" panel with reward + progress bar, gentle auto-aim during tutorial,
  cooldown ring above the ship, error feedback ("Fora de alcance", "Energia
  insuficiente", "Sem IRON").
- `systems/leaderboard.py`: local persistent top-10 per game mode with
  crash-safe atomic write.
- Auto-pause on window focus loss (toggleable in accessibility settings).
- Live UI scale: changing it in settings clears the font cache immediately.
- `tests/test_v13_features.py` covering all of the above (13 new tests).

### Added — v1.2
- Phase 0 / 1 regression tests covering all 36 v1.1 modules (`tests/test_phase0_bugs.py`, `tests/test_module_integration.py`).
- Save-file fuzz tests, property tests for inventory math, stress test for
  spatial hash, full-game frame budget test, visual smoke test, UI render
  coverage tests.
- `docs/MANUAL.md`, `docs/MODDING.md`, `CONTRIBUTING.md`, `SECURITY.md`,
  `NOTICE.md`, `CHANGELOG.md`.
- GitHub issue and PR templates.
- 50+ codex lore entries in PT/EN/ES.
- Dynamic supply/demand pricing on merchant stations.
- Cinematic letterbox cue during boss spawn.
- Layered SFX synthesis (sub + body + crack + tail) for combat and mining.
- Music ducking during important SFX.
- Mouse + keyboard interaction on the settings overlay.
- Auto-updater stub (`utils/auto_updater.py`) checking `latest.json`.
- Semver release helper (`scripts/release.py`).

### Changed — v1.3 sweep
- `systems/lighting.py`: `_light_sprite` rewritten as a true radial gradient
  via numpy with RGB pre-multiplied by the falloff, fixing the saturated
  white halo around the ship (`BLEND_RGBA_ADD` ignores per-pixel source
  alpha, so the gradient had to be baked into RGB). Cache keyed on
  (radius, color, intensity-bucket).
- `core/renderer.py`: engine glow only re-emits every 4 frames with
  `lifetime=14` and dimmer base intensity, preventing stacking saturation.
- `systems/generation.py`: block placement uses `BLOCK_SIZE*2.5` step + a
  3-cell checker skip → ~40% fewer blocks, cleaner read at gameplay zoom.
  `Block.render` now draws a per-resource-type outline color.
- `systems/background.py`: drift asteroids pre-baked as translucent
  desaturated sprites (count 20→14, vx/vy capped at ±0.15).
- `systems/stations.py`: `render_blueprint_info` uses `draw_panel` +
  `render_outlined`, reads live `display.WIDTH/HEIGHT`.
- `systems/tutorial.py`: enemy highlight target, progress bar, reward line.

### Changed — v1.2
- `systems/lighting.py`: removed the pre-fill that painted the whole screen
  white with `BLEND_RGBA_ADD`. Ambient < 1.0 now darkens multiplicatively.
- `ui/settings_screen.py`: UP/DOWN consume events; ENTER/SPACE/click work
  on every row; audio changes apply live to `AudioSystem`.
- `core/input.py`: actually applies user rebinds via `systems.rebind`.
- `ui/minimap.py`: shows nearby resource blocks (sub-sampled) so the map
  is informative during early exploration.
- `.github/workflows/build.yml`: caches pip; runs coverage on Ubuntu.

### Fixed
- White-screen on world entry (lighting bug).
- Settings menu inputs ignored (handler returned False, mouse unhandled).
- User keybinds in `navecraft_config.json` were never applied.

## [1.1.0] — 2026-05-12

Initial AAA v1.1 implementation: ~36 new modules, multi-slot saves with
backup fallback, procedural audio with ADSR, layered parallax background,
galaxy with 12 systems, factions, skills, achievements, gamepad support,
profiler, object pool, spatial hash, telemetry, mod loader, photo mode,
day/night cycle, weather, replay, speedrun timer, rebind, accessibility,
new HUD/minimap/compass, codex screen, full settings screen, world map,
death screen, tooltip, help overlay, merchant.

## [1.0.0] — Earlier

Foundation: 2D survival/exploration loop, mining, building, crafting,
shooting, planets, blocks, enemies, projectiles, score, autosave,
multiplayer (split-screen), caves, stations.
