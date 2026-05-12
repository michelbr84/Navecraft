"""
Procedural memorable planet name generator.
"""

import random


PREFIXES = ['Ax', 'Vel', 'Ko', 'Tau', 'Zen', 'Cor', 'Nyx', 'Sol', 'Vor', 'Ke',
            'Aldo', 'Bri', 'Cer', 'Dro', 'Erin', 'Pri', 'Quor', 'Ry', 'Sere', 'Tri',
            'Ul', 'Var', 'Wae', 'Xa', 'Yli', 'Zor', 'Hel', 'Mar', 'Ner', 'Phae']
ROOTS = ['ion', 'ara', 'eth', 'oris', 'ix', 'ara', 'ulo', 'andra', 'ire',
         'ax', 'eus', 'aris', 'umon', 'ina', 'opolis', 'orum', 'arion', 'esus']
SUFFIXES = ['', '', '', 'a', 'us', 'is', '-IV', '-VII', '-Prime', 'on',
            '-Beta', '-2', '-Alpha', ' Major', ' Minor']


def generate_name(seed=None):
    rng = random.Random(seed)
    return rng.choice(PREFIXES) + rng.choice(ROOTS) + rng.choice(SUFFIXES)


def generate_system_name(seed=None):
    rng = random.Random(seed)
    return rng.choice(PREFIXES) + rng.choice(ROOTS) + ' System'
