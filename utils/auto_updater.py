"""
Auto-updater stub.

Checks a configurable URL for `latest.json` containing
`{"version": "...", "url": "...", "notes": "..."}` and surfaces
the result to the caller. Does NOT download or install anything by itself.

If telemetry opt-in is False, the check is skipped silently.
"""

import json
import os
import sys
from utils import config


# Module version, mirrored in pyproject.toml. Update via scripts/release.py.
CURRENT_VERSION = '1.2.0-dev'

DEFAULT_UPDATE_URL = 'https://raw.githubusercontent.com/michelbr84/Navecraft/main/latest.json'


def _parse_version(s):
    """Best-effort tuple parser: '1.2.3' -> (1, 2, 3); pre-release suffixes stripped."""
    head = s.split('-', 1)[0].split('+', 1)[0]
    parts = []
    for part in head.split('.'):
        try:
            parts.append(int(part))
        except ValueError:
            parts.append(0)
    return tuple(parts)


def _newer(a, b):
    """Return True if version string `a` is newer than `b`."""
    try:
        return _parse_version(a) > _parse_version(b)
    except Exception:
        return False


def check_for_update(url=None, timeout=3.0):
    """
    Query `url` for a `latest.json` manifest.

    Returns a dict with `available` (bool), `version`, `url`, `notes`
    on success, or `{'available': False, 'error': ...}` on any failure
    (the caller should treat all errors as "no update available, ignore").

    Does NOT raise on network errors.
    """
    if not config.get('telemetry', 'consented', default=False):
        return {'available': False, 'reason': 'telemetry-not-consented'}

    url = url or config.get('updates', 'url', default=DEFAULT_UPDATE_URL)
    try:
        # urllib instead of requests to avoid an extra dependency.
        import urllib.request
        req = urllib.request.Request(url, headers={'User-Agent': f'Navecraft/{CURRENT_VERSION}'})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            payload = json.loads(resp.read().decode('utf-8'))
    except Exception as e:
        return {'available': False, 'error': repr(e)}

    latest = str(payload.get('version', ''))
    if not latest:
        return {'available': False, 'error': 'malformed manifest'}

    return {
        'available': _newer(latest, CURRENT_VERSION),
        'version': latest,
        'url': payload.get('url', ''),
        'notes': payload.get('notes', ''),
        'current': CURRENT_VERSION,
    }


if __name__ == '__main__':
    # CLI debug: `python -m utils.auto_updater` prints the result.
    result = check_for_update()
    json.dump(result, sys.stdout, indent=2)
    sys.stdout.write('\n')
