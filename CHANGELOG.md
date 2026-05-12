# Changelog

All notable changes are tracked here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project
uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
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

### Changed
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
