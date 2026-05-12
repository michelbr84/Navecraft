# Security Policy

## Supported versions

Only the latest tag on the `main` branch is supported. Older tags are
archived only.

## Reporting a vulnerability

If you believe you've found a security issue:

1. **Do not** open a public issue.
2. Open a **private GitHub security advisory** at
   https://github.com/michelbr84/Navecraft/security/advisories/new — or
   email the maintainer (see `pyproject.toml`).
3. Include reproduction steps, the affected commit SHA, and (if relevant)
   sample save files.

We aim to acknowledge advisories within 5 business days.

## Threat model

Navecraft is a single-player desktop game. The relevant attack surface is:

- **Mod loading** — `systems/mod_loader.py` `exec`s arbitrary Python from
  `mods/`. Mods are NOT sandboxed. Users should only install mods from
  trusted sources.
- **Save file parsing** — `SaveSystem.load_game` parses JSON from disk.
  Failures are caught and the game falls back to backups. Save fuzzing is
  tested in `tests/test_save_fuzz.py`.
- **Telemetry** — opt-in only. Crash reports are written locally to
  `navecraft_telemetry.jsonl` and never transmitted off-device.

## Out of scope

- Multiplayer / network attacks — there is no networked play.
- Memory corruption — Navecraft is pure Python; common C-class
  vulnerabilities are not applicable.
- Denial of service via crafted save files — saves load on user demand
  only, and corrupt saves degrade gracefully.
