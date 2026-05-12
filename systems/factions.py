"""
Factions and reputation system.
"""


FACTIONS = {
    'TRADERS': {
        'name_pt': 'Guilda dos Mercadores',
        'name_en': 'Traders Guild',
        'color': (50, 200, 200),
        'hostile_to': [],
    },
    'PIRATES': {
        'name_pt': 'Sindicato Pirata',
        'name_en': 'Pirate Syndicate',
        'color': (200, 50, 50),
        'hostile_to': ['TRADERS', 'FEDERATION'],
    },
    'FEDERATION': {
        'name_pt': 'Federação Galáctica',
        'name_en': 'Galactic Federation',
        'color': (100, 100, 255),
        'hostile_to': ['PIRATES'],
    },
    'INDEPENDENT': {
        'name_pt': 'Independentes',
        'name_en': 'Independents',
        'color': (180, 180, 100),
        'hostile_to': [],
    },
}


class ReputationSystem:
    def __init__(self):
        self.rep = {fid: 0 for fid in FACTIONS}

    def adjust(self, faction_id, delta):
        if faction_id not in self.rep:
            return
        self.rep[faction_id] = max(-100, min(100, self.rep[faction_id] + delta))
        # Hostile faction reps move inversely
        for hostile in FACTIONS[faction_id]['hostile_to']:
            if hostile in self.rep:
                self.rep[hostile] = max(-100, min(100, self.rep[hostile] - delta // 2))

    def status(self, faction_id):
        val = self.rep.get(faction_id, 0)
        if val >= 50:
            return 'allied'
        if val >= 20:
            return 'friendly'
        if val > -20:
            return 'neutral'
        if val > -50:
            return 'hostile'
        return 'enemy'

    def is_hostile(self, faction_id):
        return self.status(faction_id) in ('hostile', 'enemy')


reputation = ReputationSystem()
