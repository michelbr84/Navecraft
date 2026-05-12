"""
Achievement / conquest system - tied to RunStats and LifetimeStats.
"""

import time
from systems.stats import lifetime


ACHIEVEMENTS = {
    'first_mine': {
        'name_pt': 'Primeiros Cristais',
        'name_en': 'First Crystals',
        'desc_pt': 'Minere seu primeiro bloco.',
        'desc_en': 'Mine your first block.',
    },
    'first_build': {
        'name_pt': 'Construtor',
        'name_en': 'Builder',
        'desc_pt': 'Construa seu primeiro bloco.',
        'desc_en': 'Build your first block.',
    },
    'first_kill': {
        'name_pt': 'Primeiro Sangue',
        'name_en': 'First Blood',
        'desc_pt': 'Destrua seu primeiro inimigo.',
        'desc_en': 'Kill your first enemy.',
    },
    'first_station': {
        'name_pt': 'Imperialista',
        'name_en': 'Imperialist',
        'desc_pt': 'Construa sua primeira estação espacial.',
        'desc_en': 'Build your first space station.',
    },
    'first_warp': {
        'name_pt': 'Salto Quântico',
        'name_en': 'Quantum Leap',
        'desc_pt': 'Realize seu primeiro warp entre sistemas.',
        'desc_en': 'Perform your first warp.',
    },
    'mined_100': {
        'name_pt': 'Mineiro Veterano',
        'name_en': 'Veteran Miner',
        'desc_pt': 'Acumule 100 blocos minerados.',
        'desc_en': 'Mine 100 blocks across all runs.',
    },
    'killed_50': {
        'name_pt': 'Caçador',
        'name_en': 'Hunter',
        'desc_pt': 'Acumule 50 inimigos abatidos.',
        'desc_en': 'Kill 50 enemies across all runs.',
    },
    'survived_10min': {
        'name_pt': 'Sobrevivente',
        'name_en': 'Survivor',
        'desc_pt': 'Sobreviva 10 minutos em uma única partida.',
        'desc_en': 'Survive 10 minutes in a single run.',
    },
    'fully_upgraded': {
        'name_pt': 'Tecnologia de Ponta',
        'name_en': 'Cutting Edge',
        'desc_pt': 'Aplique 5 upgrades em uma partida.',
        'desc_en': 'Apply 5 upgrades in a single run.',
    },
    'crafted_5': {
        'name_pt': 'Artesão',
        'name_en': 'Artisan',
        'desc_pt': 'Crie 5 itens craftados em uma partida.',
        'desc_en': 'Craft 5 items in a single run.',
    },
    'visited_all_biomes': {
        'name_pt': 'Explorador Cósmico',
        'name_en': 'Cosmic Explorer',
        'desc_pt': 'Visite 5 planetas diferentes em uma partida.',
        'desc_en': 'Visit 5 different planets in a single run.',
    },
    'boss_slayer': {
        'name_pt': 'Caçador de Bosses',
        'name_en': 'Boss Slayer',
        'desc_pt': 'Derrote um Mini-Boss.',
        'desc_en': 'Defeat a mini-boss.',
    },
    'photo_taken': {
        'name_pt': 'Fotógrafo Espacial',
        'name_en': 'Space Photographer',
        'desc_pt': 'Use o modo foto.',
        'desc_en': 'Use photo mode.',
    },
    'hardcore_survivor': {
        'name_pt': 'Lenda Hardcore',
        'name_en': 'Hardcore Legend',
        'desc_pt': 'Sobreviva 5 minutos no modo Hardcore.',
        'desc_en': 'Survive 5 minutes in Hardcore mode.',
    },
}


class AchievementSystem:
    def __init__(self):
        self.notifications = []  # list of (achievement_id, expire_at)

    def trigger(self, achievement_id):
        if lifetime.unlock_achievement(achievement_id):
            self.notifications.append((achievement_id, time.time() + 4.0))
            return True
        return False

    def check_run(self, run, mode='standard'):
        if run.blocks_mined >= 1:
            self.trigger('first_mine')
        if run.blocks_built >= 1:
            self.trigger('first_build')
        if run.enemies_killed >= 1:
            self.trigger('first_kill')
        if run.stations_built >= 1:
            self.trigger('first_station')
        if run.upgrades_applied >= 5:
            self.trigger('fully_upgraded')
        if run.items_crafted >= 5:
            self.trigger('crafted_5')
        if run.survival_time >= 600:
            self.trigger('survived_10min')
        if run.planets_visited >= 5:
            self.trigger('visited_all_biomes')
        if mode == 'hardcore' and run.survival_time >= 300:
            self.trigger('hardcore_survivor')

    def check_lifetime(self):
        if lifetime.data['total_blocks_mined'] >= 100:
            self.trigger('mined_100')
        if lifetime.data['total_enemies_killed'] >= 50:
            self.trigger('killed_50')

    def update(self):
        now = time.time()
        self.notifications = [(aid, exp) for aid, exp in self.notifications if exp > now]

    def get_active_notifications(self):
        return list(self.notifications)


achievement_system = AchievementSystem()
