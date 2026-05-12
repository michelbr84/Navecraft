"""
Game modes - standard, hardcore (1 life), pacific (no enemies), creative (infinite resources).
"""

from utils import config


class GameMode:
    STANDARD = 'standard'
    HARDCORE = 'hardcore'
    PACIFIC = 'pacific'
    CREATIVE = 'creative'

    @staticmethod
    def current():
        return config.get('gameplay', 'mode', default='standard')

    @staticmethod
    def set(mode):
        config.set('gameplay', 'mode', mode)
        config.save()

    @staticmethod
    def is_hardcore():
        return GameMode.current() == GameMode.HARDCORE

    @staticmethod
    def is_pacific():
        return GameMode.current() == GameMode.PACIFIC

    @staticmethod
    def is_creative():
        return GameMode.current() == GameMode.CREATIVE

    @staticmethod
    def all_modes():
        return [GameMode.STANDARD, GameMode.HARDCORE, GameMode.PACIFIC, GameMode.CREATIVE]

    @staticmethod
    def cycle():
        modes = GameMode.all_modes()
        cur = GameMode.current()
        try:
            idx = modes.index(cur)
        except ValueError:
            idx = 0
        new = modes[(idx + 1) % len(modes)]
        GameMode.set(new)
        return new


def difficulty_multiplier():
    """Return a (enemy_health, enemy_damage, resource_yield) tuple."""
    d = config.get('gameplay', 'difficulty', default='normal')
    if d == 'easy':
        return (0.7, 0.7, 1.3)
    if d == 'hard':
        return (1.5, 1.4, 0.85)
    if d == 'hardcore':
        return (2.0, 1.8, 0.7)
    return (1.0, 1.0, 1.0)
