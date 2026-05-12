"""
Tests for release helper and auto-updater stub.
"""

import os
os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')

import unittest


class TestAutoUpdater(unittest.TestCase):
    def test_version_parser(self):
        from utils.auto_updater import _parse_version, _newer
        self.assertEqual(_parse_version('1.2.3'), (1, 2, 3))
        self.assertEqual(_parse_version('1.2.3-dev'), (1, 2, 3))
        self.assertEqual(_parse_version('2.0.0'), (2, 0, 0))
        self.assertTrue(_newer('2.0.0', '1.9.9'))
        self.assertFalse(_newer('1.0.0', '1.0.0'))
        self.assertFalse(_newer('1.0.0', '1.0.1'))

    def test_check_for_update_returns_dict(self):
        """No network in CI — should silently fail and return a dict."""
        from utils import auto_updater, config
        # Force opt-in so the check actually runs against the network.
        prev = config.get('telemetry', 'consented', default=None)
        config.set('telemetry', 'consented', True)
        try:
            result = auto_updater.check_for_update(url='http://127.0.0.1:1/nope.json', timeout=0.1)
            self.assertIsInstance(result, dict)
            self.assertIn('available', result)
            # Failure path must not raise.
            self.assertFalse(result['available'])
        finally:
            config.set('telemetry', 'consented', prev)

    def test_check_skipped_without_consent(self):
        from utils import auto_updater, config
        prev = config.get('telemetry', 'consented', default=None)
        config.set('telemetry', 'consented', False)
        try:
            result = auto_updater.check_for_update()
            self.assertFalse(result['available'])
            self.assertEqual(result.get('reason'), 'telemetry-not-consented')
        finally:
            config.set('telemetry', 'consented', prev)


class TestReleaseHelper(unittest.TestCase):
    def test_bump_logic(self):
        # Import the module directly without invoking main().
        import importlib.util
        from pathlib import Path
        path = Path(__file__).resolve().parents[1] / 'scripts' / 'release.py'
        spec = importlib.util.spec_from_file_location('release_helper', path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        self.assertEqual(mod._bump('1.2.3', 'patch'), '1.2.4')
        self.assertEqual(mod._bump('1.2.3', 'minor'), '1.3.0')
        self.assertEqual(mod._bump('1.2.3', 'major'), '2.0.0')
        self.assertEqual(mod._bump('1.2.3-dev', 'patch'), '1.2.4')


if __name__ == '__main__':
    unittest.main()
