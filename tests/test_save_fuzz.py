"""
Save-file fuzzing — corrupt save JSONs in various ways and confirm graceful
fallback (.bak1/.bak2/.bak3) or clean no-save handling. No crashes allowed.
"""

import os
os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')

import json
import random
import tempfile
import unittest
import pygame

pygame.init()
pygame.display.set_mode((1, 1))

from utils import display
display.set_mode(width=400, height=300)


def _mutate(text, rng):
    """Return a random string-level mutation of `text`."""
    if not text:
        return text
    op = rng.choice(['truncate', 'delete_char', 'flip_char', 'insert_garbage', 'replace_token'])
    if op == 'truncate':
        return text[:rng.randint(0, max(1, len(text) - 1))]
    if op == 'delete_char':
        i = rng.randint(0, len(text) - 1)
        return text[:i] + text[i + 1:]
    if op == 'flip_char':
        i = rng.randint(0, len(text) - 1)
        return text[:i] + chr(((ord(text[i]) + 1) % 127) or 32) + text[i + 1:]
    if op == 'insert_garbage':
        i = rng.randint(0, len(text))
        return text[:i] + '###GARBAGE###' + text[i:]
    if op == 'replace_token':
        return text.replace('"version"', '"vrsion"', 1)


class TestSaveFuzz(unittest.TestCase):
    """SaveSystem.load_game must NEVER crash, regardless of file content."""

    def setUp(self):
        # Use an isolated tempdir + redirect file paths
        self.tmp = tempfile.mkdtemp(prefix='nc_savefuzz_')
        self._orig_cwd = os.getcwd()
        os.chdir(self.tmp)
        from core.game import Game
        from systems.save_system import SaveSystem
        self.Game = Game
        self.SaveSystem = SaveSystem

    def tearDown(self):
        os.chdir(self._orig_cwd)

    def _make_baseline_save(self):
        game = self.Game()
        ss = self.SaveSystem(slot=0)
        ss.save_game(game)
        return ss

    def test_load_missing_file_returns_false(self):
        ss = self.SaveSystem(slot=99)
        # Definitely no file at this slot.
        result = ss.load_game(self.Game())
        self.assertFalse(result)

    def test_load_corrupted_json_no_crash(self):
        ss = self._make_baseline_save()
        path = ss._save_path() if hasattr(ss, '_save_path') else 'navecraft_save_0.json'
        # Corrupt it.
        with open(path, 'w', encoding='utf-8') as f:
            f.write('{ this is not valid json #####')
        # Load must not crash. May return False or recover from .bak.
        result = ss.load_game(self.Game())
        # We don't assert True/False here — only "no crash and bool result".
        self.assertIsInstance(result, bool)

    def test_load_truncated_no_crash(self):
        ss = self._make_baseline_save()
        path = 'navecraft_save_0.json'
        with open(path, 'r', encoding='utf-8') as f:
            data = f.read()
        with open(path, 'w', encoding='utf-8') as f:
            f.write(data[:len(data) // 2])
        result = ss.load_game(self.Game())
        self.assertIsInstance(result, bool)

    def test_random_mutations_no_crash(self):
        """Run 20 random mutations; each must produce a bool result, never a crash."""
        ss = self._make_baseline_save()
        path = 'navecraft_save_0.json'
        with open(path, 'r', encoding='utf-8') as f:
            base = f.read()
        rng = random.Random(0xFEEDFACE)
        for i in range(20):
            mutated = _mutate(base, rng)
            with open(path, 'w', encoding='utf-8') as f:
                f.write(mutated)
            try:
                result = ss.load_game(self.Game())
            except Exception as e:
                self.fail(f"Mutation #{i} crashed load_game: {e!r}")
            self.assertIsInstance(result, bool)


if __name__ == '__main__':
    unittest.main()
