# Contributing to Navecraft

Thanks for your interest. Below is the short version of how to land a change.

## Setup

```powershell
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Linux/macOS
pip install -r requirements.txt
pip install coverage ruff       # dev extras
```

## Running the game

```powershell
python main.py
```

## Tests

The full suite is `unittest`-based. All tests are headless-safe.

```powershell
$env:SDL_VIDEODRIVER='dummy'; $env:SDL_AUDIODRIVER='dummy'
python -m unittest discover -s tests -v
```

CI runs the suite on Ubuntu, Windows, and macOS for Python 3.10 / 3.11 / 3.12.
**All checks must be green before merging to `main`.**

## Coverage

```powershell
python -m coverage run -m unittest discover -s tests
python -m coverage report
python -m coverage html       # writes htmlcov/index.html
```

## Lint

```powershell
ruff check .
```

(Config lives in `pyproject.toml`. Ruff is informational today, not required
to be clean.)

## Branch + PR workflow

1. Branch from `main`: `feature/<short-slug>` or `fix/<short-slug>`.
2. Keep commits focused — one concern per commit. Conventional-commit
   prefixes are encouraged (`feat:`, `fix:`, `test:`, `chore:`, `docs:`).
3. Open a PR. Fill out the template.
4. Wait for CI to go green across all 9 matrix cells.
5. Squash-or-rebase merge to `main`.

## Code style notes

- Source code comments and in-game text are in Portuguese (PT-BR). Add
  English/Spanish translations to `utils/i18n.py` for any new user-visible
  string.
- Modules in `core/`, `systems/`, `ui/`, `utils/`, `entities/`.
- Subsystems are constructed in `Game.initialize_world()` in dependency
  order. See `CLAUDE.md` for the architectural conventions.
- Settings constants live in `settings.py`; do not duplicate elsewhere.
- The live screen size lives in `utils/display`, NOT in
  `settings.SCREEN_WIDTH`/`HEIGHT`.

## Adding a new control

1. Add the action key to `settings.CONTROLS`.
2. Make sure it does NOT collide with multiplayer bindings —
   `TestMultiplayerKeyConflicts` enforces this.
3. Document it in `docs/MANUAL.md`.
4. Add a test exercising `is_control_just_pressed(<KEY>)` if it triggers
   a non-trivial game action.

## Adding a new translation key

1. Append the key to every dict in `utils/i18n.py` (`pt`, `en`, `es`).
2. Use it via `t('your.new.key')`.
3. PT-BR is the fallback — never omit it.

## Reporting a bug

Use the bug-report issue template in `.github/ISSUE_TEMPLATE/`.

## Security

Crash reports (when telemetry is opted-in) go to `navecraft_telemetry.jsonl`
local to the user's install. We do not transmit telemetry off-device.
For security issues, please open a private security advisory instead of a
public issue.
