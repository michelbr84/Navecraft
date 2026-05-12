# Third-Party Notices

Navecraft is released under the MIT license (see `LICENSE` — if missing, the
`pyproject.toml` declares `license = MIT`). The following third-party
components are bundled or required at runtime, each under its own license.

## Runtime dependencies

| Package    | License        | Project                                                   |
|------------|----------------|-----------------------------------------------------------|
| pygame     | LGPL v2.1+     | https://www.pygame.org/                                   |
| numpy      | BSD-3-Clause   | https://numpy.org/                                        |
| noise      | MIT            | https://github.com/caseman/noise                          |

## Development / packaging

| Package      | License        | Purpose                                          |
|--------------|----------------|--------------------------------------------------|
| pyinstaller  | GPL with exception for bundled apps | Packaging frozen distributables |
| coverage     | Apache 2.0     | Test coverage measurement                        |
| ruff         | MIT            | Lint                                             |

## SDL2

Pygame links to SDL2, SDL2_image, SDL2_mixer, SDL2_ttf — all under the
zlib license. https://www.libsdl.org/

## Fonts

Navecraft renders all in-game text using procedurally generated bitmaps or
the default pygame font (which embeds DejaVu Sans, licensed under the
Bitstream Vera Fonts Copyright with the "no infringement" addendum and the
Arev Fonts Copyright). No custom font files are bundled.

## Procedural assets

All graphics, sound effects, and music are procedurally generated at runtime
from code in `core/audio.py`, `core/renderer.py`, and `systems/background.py`.
No third-party art, sound, or music assets are bundled.

## Attribution

If you fork or redistribute Navecraft, please preserve this `NOTICE.md` and
the original `LICENSE` declaration in `pyproject.toml`.

For corrections or omissions, open an issue at
https://github.com/michelbr84/Navecraft/issues.
