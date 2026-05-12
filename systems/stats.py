"""
Run-stats and lifetime-stats tracking - powers death screen, achievements, telemetry.
"""

import json
import os

LIFETIME_FILE = "navecraft_lifetime.json"


class RunStats:
    """Per-run counters. Reset on new game."""

    def __init__(self):
        self.start_time = 0.0
        self.survival_time = 0.0
        self.distance_traveled = 0.0
        self.blocks_mined = 0
        self.blocks_built = 0
        self.enemies_killed = 0
        self.shots_fired = 0
        self.shots_hit = 0
        self.damage_dealt = 0.0
        self.damage_taken = 0.0
        self.resources_collected = {}
        self.missions_completed = 0
        self.stations_built = 0
        self.upgrades_applied = 0
        self.items_crafted = 0
        self.planets_visited = 0
        self.cause_of_death = None  # 'oxygen' | 'energy' | 'combat' | 'unknown'

    def add_mined(self, block_type, amount):
        self.blocks_mined += 1
        self.resources_collected[block_type] = self.resources_collected.get(block_type, 0) + amount

    def to_dict(self):
        return {
            'survival_time': self.survival_time,
            'distance_traveled': self.distance_traveled,
            'blocks_mined': self.blocks_mined,
            'blocks_built': self.blocks_built,
            'enemies_killed': self.enemies_killed,
            'shots_fired': self.shots_fired,
            'shots_hit': self.shots_hit,
            'damage_dealt': self.damage_dealt,
            'damage_taken': self.damage_taken,
            'resources_collected': dict(self.resources_collected),
            'missions_completed': self.missions_completed,
            'stations_built': self.stations_built,
            'upgrades_applied': self.upgrades_applied,
            'items_crafted': self.items_crafted,
            'planets_visited': self.planets_visited,
            'cause_of_death': self.cause_of_death,
        }


class LifetimeStats:
    """Accumulated across all runs. Persisted in navecraft_lifetime.json."""

    def __init__(self):
        self.data = {
            'runs': 0,
            'deaths': 0,
            'total_survival_time': 0.0,
            'total_distance': 0.0,
            'total_blocks_mined': 0,
            'total_blocks_built': 0,
            'total_enemies_killed': 0,
            'total_shots_fired': 0,
            'best_score': 0,
            'best_survival_time': 0.0,
            'achievements_unlocked': [],
            'completed_tutorial': False,
            'first_play_timestamp': None,
        }
        self.load()

    def load(self):
        if not os.path.exists(LIFETIME_FILE):
            return
        try:
            with open(LIFETIME_FILE, 'r', encoding='utf-8') as f:
                loaded = json.load(f)
            self.data.update(loaded)
        except Exception:
            pass

    def save(self):
        try:
            with open(LIFETIME_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2)
        except Exception:
            pass

    def merge_run(self, run, score):
        self.data['runs'] += 1
        if run.cause_of_death:
            self.data['deaths'] += 1
        self.data['total_survival_time'] += run.survival_time
        self.data['total_distance'] += run.distance_traveled
        self.data['total_blocks_mined'] += run.blocks_mined
        self.data['total_blocks_built'] += run.blocks_built
        self.data['total_enemies_killed'] += run.enemies_killed
        self.data['total_shots_fired'] += run.shots_fired
        if score > self.data['best_score']:
            self.data['best_score'] = score
        if run.survival_time > self.data['best_survival_time']:
            self.data['best_survival_time'] = run.survival_time
        self.save()

    def unlock_achievement(self, achievement_id):
        if achievement_id not in self.data['achievements_unlocked']:
            self.data['achievements_unlocked'].append(achievement_id)
            self.save()
            return True
        return False

    def has_achievement(self, achievement_id):
        return achievement_id in self.data['achievements_unlocked']


lifetime = LifetimeStats()
