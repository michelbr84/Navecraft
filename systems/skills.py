"""
Skill tree - upgrades unlocked by spending skill points earned from gameplay.
"""

from utils import config


SKILL_TREE = {
    'piloting': {
        'name_pt': 'Pilotagem', 'name_en': 'Piloting',
        'nodes': {
            'agile_turn': {'pt': 'Curva Ágil', 'en': 'Agile Turn', 'cost': 1, 'effect': 'turn_rate +20%'},
            'boost_drive': {'pt': 'Boost', 'en': 'Boost Drive', 'cost': 2, 'effect': 'boost +30%'},
        },
    },
    'combat': {
        'name_pt': 'Combate', 'name_en': 'Combat',
        'nodes': {
            'twin_laser': {'pt': 'Laser Duplo', 'en': 'Twin Laser', 'cost': 2, 'effect': '+1 projectile'},
            'crit_chance': {'pt': 'Crítico', 'en': 'Critical Hit', 'cost': 3, 'effect': '+10% crit chance'},
        },
    },
    'mining': {
        'name_pt': 'Mineração', 'name_en': 'Mining',
        'nodes': {
            'ore_extractor': {'pt': 'Extrator', 'en': 'Ore Extractor', 'cost': 2, 'effect': 'yield +30%'},
            'long_beam': {'pt': 'Feixe Longo', 'en': 'Long Beam', 'cost': 1, 'effect': 'range +25%'},
        },
    },
    'survival': {
        'name_pt': 'Sobrevivência', 'name_en': 'Survival',
        'nodes': {
            'oxygen_loop': {'pt': 'Reciclagem O2', 'en': 'O2 Recycling', 'cost': 2, 'effect': 'oxygen drain -40%'},
            'auto_repair': {'pt': 'Reparo Automático', 'en': 'Auto Repair', 'cost': 3, 'effect': 'heal 1/s'},
        },
    },
}


class SkillSystem:
    def __init__(self):
        self.points = 0
        self.unlocked = set(config.get('controls', 'unlocked_skills', default=[]) or [])

    def earn(self, n=1):
        self.points += n

    def can_unlock(self, node_id):
        for cat in SKILL_TREE.values():
            if node_id in cat['nodes']:
                cost = cat['nodes'][node_id]['cost']
                return self.points >= cost and node_id not in self.unlocked
        return False

    def unlock(self, node_id):
        for cat in SKILL_TREE.values():
            if node_id in cat['nodes']:
                cost = cat['nodes'][node_id]['cost']
                if self.points >= cost and node_id not in self.unlocked:
                    self.points -= cost
                    self.unlocked.add(node_id)
                    config.set('controls', 'unlocked_skills', list(self.unlocked))
                    config.save()
                    return True
        return False

    def has(self, node_id):
        return node_id in self.unlocked


skills = SkillSystem()
