"""
Local persistent leaderboard - top 10 scores per game mode.

Phase Y.8.1 — saves results to navecraft_leaderboard.json after each run.
Persists across sessions and survives crashes (atomic write). Lives entirely
offline — no network calls.
"""

import json
import os
import tempfile
import time

LEADERBOARD_FILE = "navecraft_leaderboard.json"
MAX_ENTRIES_PER_MODE = 10


def _empty():
    return {'standard': [], 'hardcore': [], 'pacific': [], 'creative': []}


def load():
    if not os.path.exists(LEADERBOARD_FILE):
        return _empty()
    try:
        with open(LEADERBOARD_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        # Backfill any missing mode keys so downstream code can assume them.
        base = _empty()
        for k in base:
            if k not in data or not isinstance(data[k], list):
                data[k] = []
        return data
    except Exception:
        return _empty()


def _atomic_save(data):
    """Write to a temp file then rename — crash-safe."""
    dir_ = os.path.dirname(os.path.abspath(LEADERBOARD_FILE)) or "."
    fd, tmp = tempfile.mkstemp(prefix=".lb-", dir=dir_)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        os.replace(tmp, LEADERBOARD_FILE)
    except Exception:
        # Clean up the temp file if rename fails.
        try:
            os.remove(tmp)
        except OSError:
            pass


def record(mode, score, run_stats=None, player_label='player'):
    """Insert a new score; truncate the per-mode list at MAX_ENTRIES_PER_MODE.

    Returns the 1-based rank if it made the top 10, else None.
    """
    if not isinstance(score, (int, float)) or score < 0:
        return None
    data = load()
    if mode not in data:
        data[mode] = []
    entry = {
        'score': int(score),
        'time': time.time(),
        'player': str(player_label)[:32],
    }
    # Attach lightweight run summary if provided — useful for display.
    if run_stats is not None:
        try:
            entry['stats'] = {
                'survival_time': float(getattr(run_stats, 'survival_time', 0.0)),
                'enemies_killed': int(getattr(run_stats, 'enemies_killed', 0)),
                'planets_visited': int(getattr(run_stats, 'planets_visited', 0)),
            }
        except Exception:
            pass

    rows = data[mode]
    rows.append(entry)
    rows.sort(key=lambda r: r.get('score', 0), reverse=True)
    del rows[MAX_ENTRIES_PER_MODE:]
    _atomic_save(data)

    # Determine rank (1-based) if entry is still present.
    for i, r in enumerate(rows):
        if r is entry:
            return i + 1
    return None


def top(mode, limit=MAX_ENTRIES_PER_MODE):
    return load().get(mode, [])[:limit]


def clear():
    """Wipe all leaderboard entries — useful for tests and 'reset progress'."""
    _atomic_save(_empty())
