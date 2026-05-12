"""
Mission system - mining, building, survival, exploration, escort, defense, hunt, daily.
Includes mission chains, quest log, and daily procedural rotation.
"""

import random
import time
import pygame
from settings import SCREEN_WIDTH


class Mission:
    def __init__(self, mission_type, description, target, reward,
                 chain_id=None, chain_step=0, daily=False):
        self.mission_type = mission_type
        self.description = description
        self.target = target
        self.reward = reward
        self.completed = False
        self.progress = 0
        self.id = random.randint(1000, 9999)
        self.chain_id = chain_id
        self.chain_step = chain_step
        self.daily = daily
        self.accepted_at = time.time()

    def update_progress(self, amount=1):
        if self.completed:
            return False
        self.progress += amount
        if self.progress >= self.target:
            self.completed = True
            return True
        return False

    def get_progress_percentage(self):
        return min(100, (self.progress / max(self.target, 1)) * 100)


# Mission chains - linked story missions unlocking in sequence
MISSION_CHAINS = {
    'first_steps': [
        ('mining', "Cadeia: Mine 5 blocos de qualquer tipo", 5, {'IRON': 30}),
        ('building', "Cadeia: Construa 3 blocos", 3, {'CRYSTAL': 5}),
        ('combat', "Cadeia: Derrote 3 inimigos", 3, {'GOLD': 25}),
    ],
    'pirate_hunt': [
        ('combat', "Cadeia: Localize a base pirata - destrua 5 inimigos", 5, {'CRYSTAL': 15}),
        ('combat', "Cadeia: Derrote o Dreadnaught", 1, {'CRYSTAL': 50, 'GOLD': 100}),
    ],
    'merchant_supply': [
        ('mining', "Cadeia: Entrega aos mercadores - mine 20 IRON", 20, {'CRYSTAL': 10}),
        ('exploration', "Cadeia: Visite uma estação mercante", 1, {'GOLD': 40}),
    ],
}


class MissionSystem:
    def __init__(self):
        self.active_missions = []
        self.completed_missions = []
        self.available_missions = self._generate_pool()
        self.active_chains = {}  # chain_id -> step_idx
        self.last_daily_refresh = 0
        self.daily_missions = []
        self._refresh_dailies()

    def _generate_pool(self):
        missions = []
        # Mining
        missions += [
            Mission("mining", "Mine 10 blocos de ferro", 10, {"IRON": 50}),
            Mission("mining", "Mine 5 blocos de ouro", 5, {"GOLD": 30}),
            Mission("mining", "Mine 3 blocos de cristal", 3, {"CRYSTAL": 20}),
            Mission("mining", "Mine 15 blocos de combustível", 15, {"FUEL": 100}),
            Mission("mining", "Mine 20 blocos de oxigênio", 20, {"OXYGEN": 80}),
        ]
        # Building
        missions += [
            Mission("building", "Construa 5 blocos de ferro", 5, {"IRON": 25}),
            Mission("building", "Construa 3 blocos de ouro", 3, {"GOLD": 15}),
            Mission("building", "Construa 2 blocos de cristal", 2, {"CRYSTAL": 10}),
        ]
        # Survival
        missions += [
            Mission("survival", "Sobreviva por 5 minutos", 300, {"FUEL": 50, "OXYGEN": 50}),
            Mission("survival", "Mantenha energia acima de 80% por 3 minutos", 180, {"FUEL": 30}),
        ]
        # Exploration
        missions += [
            Mission("exploration", "Visite 3 planetas diferentes", 3, {"CRYSTAL": 15}),
            Mission("exploration", "Viaje 1000 pixels", 1000, {"FUEL": 40}),
        ]
        # Combat / hunt
        missions += [
            Mission("combat", "Derrote 5 inimigos", 5, {"GOLD": 25, "CRYSTAL": 5}),
            Mission("combat", "Derrote um Sniper", 1, {"CRYSTAL": 10}),
            Mission("combat", "Derrote 3 Aracnoides", 3, {"GOLD": 30}),
        ]
        # Defense
        missions += [
            Mission("defense", "Sobreviva a 10 inimigos sem morrer", 10, {"CRYSTAL": 25}),
            Mission("defense", "Construa uma estação espacial", 1, {"GOLD": 50}),
        ]
        # Escort (placeholder - completed by visiting a planet while protected)
        missions += [
            Mission("escort", "Escolte mercadores - visite 2 planetas sem morrer", 2, {"GOLD": 80}),
        ]
        return missions

    # ----- daily missions -----
    def _refresh_dailies(self):
        rng = random.Random(int(time.time() // 86400))  # day-stable
        self.daily_missions = []
        self.daily_missions.append(Mission("mining", "DIÁRIA: Mine 25 blocos",
                                           25, {"CRYSTAL": rng.randint(20, 50)}, daily=True))
        self.daily_missions.append(Mission("combat", "DIÁRIA: Derrote 10 inimigos",
                                           10, {"GOLD": rng.randint(50, 120)}, daily=True))
        self.daily_missions.append(Mission("exploration", "DIÁRIA: Viaje 3000 pixels",
                                           3000, {"FUEL": rng.randint(80, 160)}, daily=True))
        self.last_daily_refresh = int(time.time())

    def check_daily_refresh(self):
        """Refresh daily missions every 24h."""
        now = int(time.time())
        if now - self.last_daily_refresh >= 86400:
            self._refresh_dailies()

    # ----- chains -----
    def start_chain(self, chain_id):
        if chain_id in MISSION_CHAINS and chain_id not in self.active_chains:
            self.active_chains[chain_id] = 0
            return self._spawn_chain_step(chain_id, 0)
        return None

    def _spawn_chain_step(self, chain_id, step_idx):
        chain = MISSION_CHAINS.get(chain_id)
        if not chain or step_idx >= len(chain):
            return None
        mt, desc, target, reward = chain[step_idx]
        m = Mission(mt, desc, target, reward, chain_id=chain_id, chain_step=step_idx)
        self.active_missions.append(m)
        return m

    def _advance_chain(self, completed_mission):
        if completed_mission.chain_id and completed_mission.chain_id in self.active_chains:
            next_step = completed_mission.chain_step + 1
            self.active_chains[completed_mission.chain_id] = next_step
            self._spawn_chain_step(completed_mission.chain_id, next_step)

    # ----- API -----
    def get_random_mission(self, include_dailies=True):
        pool = list(self.available_missions)
        if include_dailies:
            pool += [m for m in self.daily_missions if m not in self.active_missions]
        if not pool:
            return None
        m = random.choice(pool)
        if m in self.available_missions:
            self.available_missions.remove(m)
        return m

    def accept_mission(self, mission):
        if mission and mission not in self.active_missions:
            self.active_missions.append(mission)
            return True
        return False

    def complete_mission(self, mission):
        if mission in self.active_missions and mission.completed:
            self.active_missions.remove(mission)
            self.completed_missions.append(mission)
            self._advance_chain(mission)
            return mission.reward
        return None

    # ----- progress hooks (callable from Game) -----
    def update_mining_missions(self, block_type):
        for m in self.active_missions:
            if m.mission_type == 'mining' and not m.completed:
                d = m.description.lower()
                if 'mine' in d or 'cadeia' in d or 'diária' in d.lower():
                    if 'qualquer' in d or block_type.lower() in d or 'diária' in d or 'cadeia' in d:
                        if m.update_progress():
                            return self.complete_mission(m)
        return None

    def update_building_missions(self, block_type):
        for m in self.active_missions:
            if m.mission_type == 'building' and not m.completed:
                d = m.description.lower()
                if block_type.lower() in d or 'cadeia' in d or 'qualquer' in d:
                    if m.update_progress():
                        return self.complete_mission(m)
        return None

    def update_combat_missions(self, enemy_type):
        for m in self.active_missions:
            if m.mission_type == 'combat' and not m.completed:
                d = m.description.lower()
                if 'inimigos' in d or 'cadeia' in d or 'diária' in d or enemy_type.lower() in d:
                    if m.update_progress():
                        return self.complete_mission(m)
                elif 'dreadnaught' in d and enemy_type == 'BOSS_DREADNAUGHT':
                    if m.update_progress():
                        return self.complete_mission(m)
        return None

    def update_defense_missions(self, kind):
        for m in self.active_missions:
            if m.mission_type == 'defense' and not m.completed:
                d = m.description.lower()
                if kind == 'enemy' and 'inimigos' in d:
                    if m.update_progress():
                        return self.complete_mission(m)
                if kind == 'station' and 'estação' in d:
                    if m.update_progress():
                        return self.complete_mission(m)
        return None

    def update_survival_missions(self, game_time, spaceship):
        for m in self.active_missions:
            if m.mission_type == 'survival' and not m.completed:
                d = m.description.lower()
                if 'sobreviva' in d:
                    if m.update_progress():
                        return self.complete_mission(m)
                elif 'energia' in d and spaceship:
                    if spaceship.energy / max(spaceship.max_energy, 1) > 0.8:
                        if m.update_progress():
                            return self.complete_mission(m)
                    else:
                        m.progress = 0
        return None

    def update_exploration_missions(self, spaceship, visited_planets):
        for m in self.active_missions:
            if m.mission_type == 'exploration' and not m.completed:
                d = m.description.lower()
                if 'visite' in d:
                    if len(visited_planets) >= m.target:
                        m.progress = len(visited_planets)
                        if m.update_progress():
                            return self.complete_mission(m)
                elif 'viaje' in d or 'diária' in d:
                    if spaceship:
                        distance = abs(spaceship.x) + abs(spaceship.y)
                        m.progress = min(distance, m.target)
                        if m.progress >= m.target:
                            m.completed = True
                            return self.complete_mission(m)
        return None

    def update_escort_missions(self, visited_planets):
        for m in self.active_missions:
            if m.mission_type == 'escort' and not m.completed:
                if len(visited_planets) >= m.target:
                    m.progress = len(visited_planets)
                    if m.update_progress():
                        return self.complete_mission(m)
        return None

    # ----- rendering / quest log -----
    def render_missions(self, surface, screen_width=None):
        from utils import display
        if not self.active_missions:
            return
        font = pygame.font.Font(None, 20)
        sw = screen_width if screen_width is not None else display.WIDTH
        x = sw - 320
        y = 80

        title = font.render("Missões Ativas:", True, (255, 255, 0))
        surface.blit(title, (x, y))
        y += 26

        for mission in self.active_missions[:4]:
            text = font.render(mission.description[:46], True, (255, 255, 255))
            surface.blit(text, (x, y))
            y += 20
            prog = font.render(
                f"  {mission.progress}/{mission.target} ({mission.get_progress_percentage():.0f}%)",
                True, (0, 255, 255))
            surface.blit(prog, (x, y))
            y += 18
            bar_w = 200
            bar_h = 6
            pygame.draw.rect(surface, (40, 40, 40), (x, y, bar_w, bar_h))
            fill = int(bar_w * mission.progress / max(mission.target, 1))
            color = (0, 220, 100) if mission.daily else (0, 180, 200)
            if mission.chain_id:
                color = (200, 140, 255)
            pygame.draw.rect(surface, color, (x, y, fill, bar_h))
            y += 16
