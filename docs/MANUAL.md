# Navecraft — Player Manual

A short, practical guide to playing Navecraft.

## Starting out

- Run `python main.py` from the project root.
- On first run you spawn next to a friendly planet with reduced enemy
  pressure and a 90-second "grace period". Use this time to mine, build, and
  read the on-screen tutorial steps.
- Press **H** at any time to see the controls overlay.

## Controls (defaults)

| Action               | Key(s)                              |
|----------------------|-------------------------------------|
| Move                 | W A S D or Arrow Keys               |
| Boost                | Shift                               |
| Shoot                | Space or Left Mouse Button          |
| Mine                 | E                                   |
| Build at cursor      | B                                   |
| Select block type    | 1–5                                 |
| Open inventory       | I                                   |
| Open crafting        | C                                   |
| Open world map       | Shift + M                           |
| Codex (lore + items) | K                                   |
| Help overlay         | H                                   |
| Accept mission       | M                                   |
| Build station        | T (cycle blueprint, then place)     |
| Quick save           | F9                                  |
| Quick load           | F8                                  |
| Toggle fullscreen    | F11                                 |
| Toggle borderless    | F10                                 |
| Photo mode           | F12                                 |
| Speedrun timer       | F4                                  |
| Profiler overlay     | F3                                  |
| Engine upgrade       | F1 (in-game; F1 is DEBUG in menu)   |
| Pause                | ESC                                 |

All keys are remappable from **Settings → Controls** (persisted to
`navecraft_config.json`).

## HUD legend

- Bottom-left: health, energy, oxygen, fuel bars. Each turns yellow at 50%
  and red at 25%.
- Bottom-center: quickbar showing 5 most-used resources (1–5 hotkeys).
- Top-right: score, position, velocity.
- Top-right minimap: planets (red), stations (green), enemies (red), and
  nearby resource blocks (color-coded).
- Top-center: alerts and tutorial prompts.

## Resources

| Resource | Use                                                        |
|----------|------------------------------------------------------------|
| IRON     | Structural — building, repair kits                         |
| GOLD     | Conductive — advanced upgrades                             |
| CRYSTAL  | Energy — shields, propulsion, special crafting             |
| FUEL     | Engines                                                    |
| OXYGEN   | Life support                                               |

## Crafting recipes (defaults)

| Item            | Cost                  | Hotkey |
|-----------------|-----------------------|--------|
| REPAIR_KIT      | 10 IRON + 5 FUEL      | 6      |
| ENERGY_PACK     | 5 CRYSTAL + 10 FUEL   | 7      |
| OXYGEN_TANK     | 20 OXYGEN + 5 IRON    | 8      |
| SHIELD_BOOSTER  | 10 CRYSTAL + 5 GOLD   | 9      |

## Upgrades

Apply via the F1–F6 keys in-game (each spends inventory resources and
permanently improves a stat). Each upgrade has a max level (typically 2–3).

## Stations

Press **T** to cycle blueprints (`SMALL_OUTPOST`, `REFUEL_STATION`,
`MINING_PLATFORM`). Press **T** again when in clear space to build at the
ship's location, paying the IRON / FUEL / CRYSTAL / OXYGEN cost.

## Missions

Press **M** to accept a procedurally generated mission. Daily missions
refresh every 24 in-game hours (Run Stats clock). Mission types:
mining quotas, exploration, escort, defense, combat.

## Saving

- Autosave: every 30 seconds.
- Manual save: **F9** (slot 0).
- The save format is versioned JSON with rolling backups (`.bak1`, `.bak2`,
  `.bak3`). If the main file is corrupt, the game silently falls back.

## Accessibility

In **Settings → Accessibility**:
- Colorblind filters (protanopia / deuteranopia / tritanopia).
- Reduce motion (disables camera shake, slowmo, flashes, parallax).
- UI scale (0.75x – 2.0x).
- Captions for audio cues.
- High-contrast mode.

## Photo mode

Press **F12** mid-game to enter photo mode. Use arrows to pan, +/- to zoom,
**H** to hide HUD, **Enter** to save a PNG to `screenshots/`.

## Speedrun mode

Press **F4** to start/stop a millisecond-accurate run timer rendered at the
top of the screen.

## Troubleshooting

| Symptom                       | Try                                                  |
|-------------------------------|------------------------------------------------------|
| Black or white screen at start| Update graphics drivers; toggle F11 (fullscreen) once |
| No sound                      | Settings → Audio: bump master volume                  |
| Gamepad not detected          | Plug in before launching the game                     |
| Game stutters on big worlds   | Settings → Video: lower FPS cap or disable VSync     |
| Saved game won't load         | The game auto-falls-back to `.bak1/.bak2/.bak3`      |

Logs go to `navecraft.log`. Crash reports (opt-in only) go to
`navecraft_telemetry.jsonl`.
