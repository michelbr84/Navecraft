"""
Release helper - bumps version in pyproject.toml and utils/auto_updater.py,
optionally creates a git tag.

Usage:
    python scripts/release.py --bump patch          # 1.2.0 -> 1.2.1
    python scripts/release.py --bump minor          # 1.2.x -> 1.3.0
    python scripts/release.py --bump major          # 1.x.y -> 2.0.0
    python scripts/release.py --set 1.5.0           # explicit
    python scripts/release.py --bump patch --tag    # also `git tag vN.N.N`

The script does NOT push. Run `git push origin v<version>` manually after
confirming the tag.
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PYPROJECT = ROOT / 'pyproject.toml'
UPDATER = ROOT / 'utils' / 'auto_updater.py'

VERSION_RE = re.compile(r'^version\s*=\s*"([^"]+)"', re.MULTILINE)
UPDATER_VERSION_RE = re.compile(r"^CURRENT_VERSION\s*=\s*'([^']+)'", re.MULTILINE)


def _read_pyproject_version():
    text = PYPROJECT.read_text(encoding='utf-8')
    m = VERSION_RE.search(text)
    if not m:
        raise SystemExit("Could not find `version = ...` in pyproject.toml")
    return m.group(1), text


def _bump(version, kind):
    parts = [int(p) for p in version.split('-')[0].split('.')[:3]]
    while len(parts) < 3:
        parts.append(0)
    major, minor, patch = parts
    if kind == 'major':
        return f"{major + 1}.0.0"
    if kind == 'minor':
        return f"{major}.{minor + 1}.0"
    if kind == 'patch':
        return f"{major}.{minor}.{patch + 1}"
    raise ValueError(kind)


def _write_pyproject(new_version, text):
    new_text = VERSION_RE.sub(f'version = "{new_version}"', text, count=1)
    PYPROJECT.write_text(new_text, encoding='utf-8')


def _write_updater(new_version):
    text = UPDATER.read_text(encoding='utf-8')
    new_text = UPDATER_VERSION_RE.sub(f"CURRENT_VERSION = '{new_version}'", text, count=1)
    UPDATER.write_text(new_text, encoding='utf-8')


def main():
    ap = argparse.ArgumentParser(description="Navecraft release helper.")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--bump', choices=['major', 'minor', 'patch'])
    g.add_argument('--set', dest='set_version')
    ap.add_argument('--tag', action='store_true', help='Create a git tag v<version> after bump.')
    args = ap.parse_args()

    current, text = _read_pyproject_version()
    new_version = args.set_version if args.set_version else _bump(current, args.bump)

    _write_pyproject(new_version, text)
    _write_updater(new_version)

    print(f"Bumped: {current} -> {new_version}")
    print(f"  pyproject.toml")
    print(f"  utils/auto_updater.py")

    if args.tag:
        try:
            subprocess.run(['git', 'add', 'pyproject.toml', 'utils/auto_updater.py'], check=True, cwd=ROOT)
            subprocess.run(['git', 'commit', '-m', f'chore(release): v{new_version}'], check=True, cwd=ROOT)
            subprocess.run(['git', 'tag', f'v{new_version}'], check=True, cwd=ROOT)
            print(f"  Created git tag v{new_version}. Push with: git push origin v{new_version}")
        except subprocess.CalledProcessError as e:
            print(f"git operation failed: {e}", file=sys.stderr)
            sys.exit(1)


if __name__ == '__main__':
    main()
