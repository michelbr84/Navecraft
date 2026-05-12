"""
Game world - owns spaceship, planets, blocks, enemies, projectiles, systems.

This is the play-state. main.py owns the top-level state machine and window.
"""

import math
import random
import time
import pygame
from settings import *
from core.input import InputManager
from core.renderer import Renderer
from core.audio import AudioSystem
from entities.spaceship import Spaceship, Projectile
from entities.enemy import Enemy
from entities.merchant import Merchant
from systems.physics import PhysicsSystem
from systems.generation import WorldGenerator
from systems.particles import ParticleSystem
from systems.missions import MissionSystem
from systems.inventory import CraftingSystem
from systems.upgrades import UpgradeSystem
from systems.multiplayer import MultiplayerSystem
from systems.stations import StationSystem
from systems.save_system import SaveSystem
from systems.bosses import MiniBoss
from systems.feedback import feedback
from systems.camera import camera
from systems.lighting import lighting
from systems.background import background
from systems.weather import weather
from systems.day_night import day_night
from systems.tutorial import TutorialSystem
from systems.stats import RunStats, lifetime
from systems.achievements import achievement_system, ACHIEVEMENTS
from systems.game_modes import GameMode
from systems.galaxy import galaxy
from systems.factions import reputation
from systems.skills import skills
from systems.gamepad import gamepad
from systems.spatial_hash import SpatialHash
from systems.pool import ObjectPool
from systems.replay import replay
from systems.profiler import profiler, section as prof_section
from ui.hud import HUD
from ui.minimap import Minimap
from ui.compass import CompassSystem
from utils.debug import DebugSystem
from utils.logger import game_logger
from utils.i18n import t
from utils import config, display


class Game:
    def __init__(self):
        game_logger.log_system_info()
        game_logger.info("Iniciando jogo Navecraft")
        self.input_manager = InputManager()
        self.physics_system = PhysicsSystem()
        self.world_generator = WorldGenerator()
        self.renderer = Renderer()
        self.audio_system = AudioSystem()
        self.particle_system = ParticleSystem()
        self.mission_system = MissionSystem()
        self.debug_system = DebugSystem()
        self.minimap = Minimap()
        self.compass = CompassSystem()
        self.tutorial = TutorialSystem()
        self.run_stats = RunStats()
        self.spatial_hash = SpatialHash(cell_size=128)
        # Object pool for projectiles
        self._proj_pool = ObjectPool(
            factory=lambda x=0, y=0, a=0, owner='player': Projectile(x, y, a, owner),
            reset_fn=lambda p, x=0, y=0, a=0, owner='player': p.__init__(x, y, a, owner),
        )

        self.spaceship = None
        self.planets = []
        self.blocks = []
        self.enemies = []
        self.projectiles = []
        self.particles = []
        self.merchants = []

        self.camera_x = 0
        self.camera_y = 0
        self.hud = HUD()
        self.game_state = "playing"
        self.score = 0
        self.last_frame_time = time.time()
        self.game_time = 0
        self.visited_planets = set()
        self.save_system = SaveSystem()
        self.difficulty = config.get('gameplay', 'difficulty', default='normal')
        self.mode = GameMode.current()
        self.world_distance_accum = 0.0
        self._prev_pos = None
        self._boss_spawned = False
        self._first_run_grace_frames = 60 * 90  # 90s of no enemies on first run
        self.first_run = bool(config.get('gameplay', 'first_run', default=True))
        self.alert_cooldowns = {'oxygen': 0, 'energy': 0, 'fuel': 0, 'health': 0}

        self.initialize_world()
        self.audio_system.play_music()
        game_logger.info("Jogo inicializado com sucesso")

    def initialize_world(self):
        game_logger.info("Inicializando mundo do jogo")
        spawn_x = SCREEN_WIDTH // 2
        spawn_y = SCREEN_HEIGHT // 2
        self.spaceship = Spaceship(spawn_x, spawn_y)
        self.crafting_system = CraftingSystem(self.spaceship.inventory)
        self.upgrade_system = UpgradeSystem(self.spaceship)
        self.multiplayer_system = MultiplayerSystem(self)
        self.station_system = StationSystem()

        self.planets = self.world_generator.generate_planets()
        game_logger.info(f"Gerados {len(self.planets)} planetas")

        # First-session: spawn near a friendly planet with easy resources
        if self.first_run and self.planets:
            nearest = min(self.planets, key=lambda p: (p.x - spawn_x) ** 2 + (p.y - spawn_y) ** 2)
            self.spaceship.x = nearest.x + nearest.radius + 80
            self.spaceship.y = nearest.y

        self.blocks = self.world_generator.generate_blocks()
        game_logger.info(f"Gerados {len(self.blocks)} blocos")
        cave_blocks = self.world_generator.generate_caves(self.planets)
        self.blocks.extend(cave_blocks)
        game_logger.info(f"Gerados {len(cave_blocks)} blocos de cavernas")

        # Enemies — fewer for first run / pacific mode
        if GameMode.is_pacific():
            self.enemies = []
        else:
            self.enemies = self.world_generator.generate_enemies()
            if self.first_run:
                self.enemies = self.enemies[:3]
        game_logger.info(f"Gerados {len(self.enemies)} inimigos")

        # Merchants - one near origin, two more at scattered offsets so the
        # dynamic price system encourages trade routes between them.
        self.merchants.append(Merchant(spawn_x + 400, spawn_y - 200))
        self.merchants.append(Merchant(spawn_x - 800, spawn_y + 600))
        self.merchants.append(Merchant(spawn_x + 1200, spawn_y + 1500))
        # Pirate hunt mission chain auto-starts
        self.mission_system.start_chain('first_steps')

        # Initial start_time for stats
        self.run_stats.start_time = time.time()
        self._prev_pos = (self.spaceship.x, self.spaceship.y)

        # Start recording replay
        replay.start_recording()

    def update(self):
        with prof_section('update.frame'):
            current_time = time.time()
            frame_time = (current_time - self.last_frame_time) * 1000
            self.last_frame_time = current_time

            time_scale = feedback.time_scale()
            self.game_time += (frame_time / 1000) * time_scale

            # If hitstop is active, freeze the game
            if feedback.is_paused_by_hitstop():
                feedback.update()
                self.input_manager.clear_frame()
                return

            self.debug_system.update_fps()
            self.debug_system.update_frame_time(frame_time)
            self.input_manager.update_mouse()

            with prof_section('update.spaceship'):
                self._update_spaceship()

            with prof_section('update.systems'):
                self.mission_system.check_daily_refresh()
                self.mission_system.update_survival_missions(self.game_time, self.spaceship)
                self.multiplayer_system.update(self.input_manager)
                if self.spaceship:
                    self.station_system.apply_station_effects(self.spaceship)
                self.mission_system.update_exploration_missions(self.spaceship, self.visited_planets)
                self.mission_system.update_escort_missions(self.visited_planets)

            with prof_section('update.combat'):
                self._update_enemies_and_projectiles()

            # Update particles + transient lights
            with prof_section('update.particles'):
                self.particle_system.update()
                lighting.update()
                if self.spaceship:
                    self.particle_system.particles = [
                        p for p in self.particle_system.particles
                        if abs(p.x - self.spaceship.x) < PARTICLE_CLEANUP_DISTANCE
                        and abs(p.y - self.spaceship.y) < PARTICLE_CLEANUP_DISTANCE
                    ]

            # Camera
            with prof_section('update.camera'):
                if self.spaceship:
                    cam_center = self.multiplayer_system.get_camera_center()
                    if cam_center:
                        camera.follow(cam_center[0], cam_center[1])
                    else:
                        camera.follow(self.spaceship.x, self.spaceship.y,
                                      self.spaceship.vx, self.spaceship.vy)
                    camera.update()
                    self.camera_x, self.camera_y = camera.render_offset()

            # Effects & misc
            weather.update(self.spaceship)
            day_night.update(frame_time / 1000)
            background.update()
            feedback.update()
            achievement_system.update()
            replay.record(self.spaceship)

            # Track visited planets (close approach counts)
            self._track_visited()

            # Mark explored cells for world map
            if self.spaceship:
                try:
                    from ui.map_screen import WorldMap
                    if hasattr(self, '_world_map_ref'):
                        self._world_map_ref.mark_explored(self.spaceship.x, self.spaceship.y)
                except Exception:
                    pass

            # Music intensity based on nearby threats
            threat = 0
            if self.spaceship:
                for e in self.enemies:
                    if math.hypot(e.x - self.spaceship.x, e.y - self.spaceship.y) < 350:
                        threat += 1
            self.audio_system.update_combat_intensity(min(1.0, threat / 4.0))
            self.audio_system.update_duck()

            # Distance accumulation for stats
            if self.spaceship and self._prev_pos:
                d = math.hypot(self.spaceship.x - self._prev_pos[0],
                               self.spaceship.y - self._prev_pos[1])
                self.world_distance_accum += d
                self.run_stats.distance_traveled = self.world_distance_accum
            self._prev_pos = (self.spaceship.x, self.spaceship.y)

            # Survival time
            self.run_stats.survival_time = time.time() - self.run_stats.start_time

            # Low-resource alerts (visual + sfx)
            self._check_alerts()

            # First-run grace handling
            if self._first_run_grace_frames > 0:
                self._first_run_grace_frames -= 1
                if self._first_run_grace_frames == 0:
                    self.hud.push_alert("Inimigos se aproximam!", color=(255, 100, 100))

            # Boss trigger at high score
            if not self._boss_spawned and self.score > 500 and not GameMode.is_pacific():
                self._spawn_boss()

            # Boss letterbox auto-close
            if getattr(self, '_boss_letterbox_frames', 0) > 0:
                self._boss_letterbox_frames -= 1
                if self._boss_letterbox_frames == 0:
                    feedback.letterbox(0.0, text=None)

            # Autosave (skip in hardcore? still allow)
            try:
                self.save_system.check_autosave(self)
            except Exception:
                pass

            # Tutorial step machine
            self.tutorial.update(self)

            # Achievement checks
            achievement_system.check_run(self.run_stats, mode=self.mode)
            achievement_system.check_lifetime()

            # Game over check
            if self.spaceship and not self.spaceship.is_alive():
                self.game_state = "game_over"
                cause = self.spaceship.last_damage_cause or 'unknown'
                self.run_stats.cause_of_death = cause
                lifetime.merge_run(self.run_stats, self.score)
                from systems.telemetry import telemetry
                telemetry.log_death(cause, self.run_stats.to_dict())

            self.input_manager.clear_frame()

    def _update_spaceship(self):
        if not self.spaceship:
            return
        # Gamepad axes -> synthesize as input if connected
        if gamepad.connected:
            dx, dy = gamepad.get_movement_vector()
            if dx or dy:
                self.spaceship.angle = math.atan2(dy, dx) if (abs(dx) + abs(dy) > 0) else self.spaceship.angle
                self.spaceship.vx += dx * SPACESHIP_ACCELERATION
                self.spaceship.vy += dy * SPACESHIP_ACCELERATION
        self.spaceship.update(self.input_manager)
        self.debug_system.set_debug_info('spaceship_pos', (self.spaceship.x, self.spaceship.y))

        dx, dy = self.input_manager.get_movement_vector()
        if dx != 0 or dy != 0:
            angle = math.atan2(dy, dx)
            self.particle_system.create_thrust_effect(self.spaceship.x, self.spaceship.y, angle)
            self.spaceship.create_thrust_particles()

        # SHOOT
        if self.input_manager.is_control_just_pressed('SHOOT'):
            self._fire_player_shot()

        # MINE
        if self.input_manager.is_control_just_pressed('MINE'):
            mined_value = self.spaceship.mine(self.blocks)
            if mined_value > 0:
                self.score += mined_value
                self.run_stats.add_mined(self.spaceship.last_mine_result['type'], mined_value)
                self.tutorial.on_mine()
                self.audio_system.play_at('mine', self.spaceship.x, self.spaceship.y,
                                          self.spaceship.x, self.spaceship.y, variant=True)
                self.audio_system.play_sound('collect')
                self.particle_system.create_collect_effect(self.spaceship.x, self.spaceship.y)
                # Magnetic collect particles
                mr = self.spaceship.last_mine_result
                feedback.floating(mr['x'], mr['y'], f"+{mined_value} {mr['type']}",
                                  color=(120, 255, 120), lifetime=50, size=18)
                feedback.shake(intensity=3, frames=6)
                # Mission progress
                for b in self.blocks:
                    if b.collected and b.block_type:
                        rew = self.mission_system.update_mining_missions(b.block_type)
                        if rew:
                            self._on_mission_complete(rew)

        # BUILD
        if self.input_manager.is_control_just_pressed('BUILD'):
            mouse_x, mouse_y = self.input_manager.get_mouse_position()
            wx = mouse_x + self.camera_x
            wy = mouse_y + self.camera_y
            if self.spaceship.build(self.blocks, wx, wy):
                self.score += 5
                self.run_stats.blocks_built += 1
                self.tutorial.on_build()
                self.audio_system.play_sound('build')
                self.particle_system.create_collect_effect(wx, wy, (0, 255, 255))
                feedback.floating(wx, wy, t('feedback.built'), color=(0, 255, 255), lifetime=40)
                rew = self.mission_system.update_building_missions(self.spaceship.selected_block_type)
                if rew:
                    self._on_mission_complete(rew)

        # Block-type selection
        for key, btype in (('SELECT_IRON', 'IRON'), ('SELECT_GOLD', 'GOLD'),
                           ('SELECT_CRYSTAL', 'CRYSTAL'), ('SELECT_FUEL', 'FUEL'),
                           ('SELECT_OXYGEN', 'OXYGEN')):
            if self.input_manager.is_control_just_pressed(key):
                self.spaceship.select_block_type(btype)

        # Missions
        if self.input_manager.is_control_just_pressed('MISSION'):
            new_m = self.mission_system.get_random_mission()
            if new_m:
                self.mission_system.accept_mission(new_m)
                feedback.floating(0, 0, "Nova missão: " + new_m.description,
                                  color=(255, 255, 100), lifetime=120, size=18, world_space=False)

        # Crafting hotkeys
        for key, recipe in (('CRAFT_REPAIR', 'REPAIR_KIT'), ('CRAFT_ENERGY', 'ENERGY_PACK'),
                            ('CRAFT_OXYGEN', 'OXYGEN_TANK'), ('CRAFT_SHIELD', 'SHIELD_BOOSTER')):
            if self.input_manager.is_control_just_pressed(key):
                if self.crafting_system.craft_item(recipe):
                    self.run_stats.items_crafted += 1
                    self.audio_system.play_sound('collect')
                    self.particle_system.create_collect_effect(self.spaceship.x, self.spaceship.y, (255, 220, 100))
                    feedback.floating(self.spaceship.x, self.spaceship.y,
                                      t('feedback.crafted') + " " + recipe,
                                      color=(255, 220, 100), lifetime=40)

        # Upgrades (F1-F6) - F1 conflict is resolved: while playing, F1 is upgrade.
        # When not in playing state, main.py uses F1 differently.
        for key, upgrade_id in (
            ('UPGRADE_ENGINE', 'ENGINE_BOOST'),
            ('UPGRADE_SHIELD', 'SHIELD_ENHANCEMENT'),
            ('UPGRADE_ENERGY', 'ENERGY_EFFICIENCY'),
            ('UPGRADE_MINING', 'MINING_LASER'),
            ('UPGRADE_OXYGEN', 'OXYGEN_SYSTEM'),
            ('UPGRADE_FUEL', 'FUEL_TANK'),
        ):
            if self.input_manager.is_control_just_pressed(key):
                if self.upgrade_system.apply_upgrade(upgrade_id):
                    self.run_stats.upgrades_applied += 1
                    self.audio_system.play_sound('collect')
                    feedback.floating(self.spaceship.x, self.spaceship.y,
                                      t('feedback.upgraded') + " " + upgrade_id,
                                      color=(120, 220, 255), lifetime=50)

        if self.input_manager.is_control_just_pressed('MULTIPLAYER_TOGGLE'):
            self.multiplayer_system.toggle_multiplayer()
        elif self.input_manager.is_control_just_pressed('MULTIPLAYER_ADD_PLAYER'):
            self.multiplayer_system.add_more_players()

        if self.input_manager.is_control_just_pressed('QUICK_SAVE'):
            self.save_system.save_game(self)
            feedback.floating(0, 0, "Salvo!", color=(100, 255, 100), lifetime=40, world_space=False)

        if self.input_manager.is_control_just_pressed('BUILD_STATION'):
            bp_name, bp = self.station_system.get_selected_blueprint()
            if self.station_system.build_station(
                    bp_name, self.spaceship.x, self.spaceship.y,
                    self.blocks, self.spaceship.inventory):
                self.score += 200
                self.run_stats.stations_built += 1
                self.tutorial.on_station_built()
                self.audio_system.play_sound('build')
                self.particle_system.create_collect_effect(
                    self.spaceship.x, self.spaceship.y, (0, 255, 255))
                rew = self.mission_system.update_defense_missions('station')
                if rew:
                    self._on_mission_complete(rew)
            else:
                self.station_system.cycle_blueprint()

    def _fire_player_shot(self):
        if self.spaceship.shoot():
            proj = Projectile(
                self.spaceship.x + math.cos(self.spaceship.angle) * self.spaceship.size,
                self.spaceship.y + math.sin(self.spaceship.angle) * self.spaceship.size,
                self.spaceship.angle, owner='player')
            self.projectiles.append(proj)
            # Twin laser skill
            if skills.has('twin_laser'):
                proj2 = Projectile(
                    self.spaceship.x + math.cos(self.spaceship.angle + 0.2) * self.spaceship.size,
                    self.spaceship.y + math.sin(self.spaceship.angle + 0.2) * self.spaceship.size,
                    self.spaceship.angle + 0.2, owner='player')
                self.projectiles.append(proj2)
            self.run_stats.shots_fired += 1
            self.tutorial.on_shoot()
            self.audio_system.play_at('shoot', self.spaceship.x, self.spaceship.y,
                                      self.spaceship.x, self.spaceship.y, variant=True)
            feedback.shake(intensity=2, frames=4)
            lighting.add_transient(self.spaceship.x, self.spaceship.y,
                                    radius=64, color=(120, 200, 255), lifetime=8)

    def _update_enemies_and_projectiles(self):
        # Rebuild spatial hash periodically (every 10 frames)
        if not hasattr(self, '_hash_tick'):
            self._hash_tick = 0
        self._hash_tick += 1
        if self._hash_tick % 10 == 0:
            self.spatial_hash.rebuild(self.enemies, get_xy=lambda e: (e.x, e.y))

        # Enemies updated only if close
        for enemy in self.enemies:
            if self.spaceship:
                d = math.hypot(enemy.x - self.spaceship.x, enemy.y - self.spaceship.y)
                if d < ENEMY_UPDATE_DISTANCE:
                    enemy.update(self.spaceship)
                    enemy.deliver_attack_if_due(self.projectiles)
                    if enemy.last_hit_at:
                        pass

        # Physics
        self.physics_system.update(self.spaceship, self.planets, self.blocks)

        # Projectiles
        for projectile in self.projectiles[:]:
            projectile.update()
            if not projectile.is_alive():
                self.projectiles.remove(projectile)
                continue
            # Player-projectile vs enemies
            if projectile.owner == 'player':
                hit_enemy = None
                # broad-phase
                candidates = self.spatial_hash.query_radius(projectile.x, projectile.y, 50)
                for e in candidates:
                    if math.hypot(projectile.x - e.x, projectile.y - e.y) < e.size + projectile.size:
                        hit_enemy = e
                        break
                if hit_enemy:
                    hit_enemy.take_damage(projectile.damage)
                    self.run_stats.shots_hit += 1
                    self.run_stats.damage_dealt += projectile.damage
                    self.particle_system.create_collect_effect(hit_enemy.x, hit_enemy.y, (255, 100, 0))
                    feedback.damage_number(hit_enemy.x, hit_enemy.y, projectile.damage)
                    feedback.hitstop(frames=3)
                    feedback.flash(color=(255, 255, 255), strength=30)
                    sfx_map = {'DRONE': 'hit_drone', 'ANDROID': 'hit_android',
                               'SNIPER': 'hit_sniper', 'ARACHNOID': 'hit_arachnoid',
                               'BOSS_DREADNAUGHT': 'hit_boss'}
                    sfx = sfx_map.get(hit_enemy.enemy_type, 'hit_drone')
                    if self.spaceship:
                        self.audio_system.play_at(sfx, hit_enemy.x, hit_enemy.y,
                                                  self.spaceship.x, self.spaceship.y)
                    if projectile in self.projectiles:
                        self.projectiles.remove(projectile)
                    if not hit_enemy.is_alive():
                        self.score += 50
                        self.run_stats.enemies_killed += 1
                        self.enemies.remove(hit_enemy)
                        self.particle_system.create_explosion(hit_enemy.x, hit_enemy.y, (255, 60, 0))
                        self.audio_system.play_sound('explosion')
                        feedback.shake(intensity=5, frames=10)
                        feedback.flash(color=(255, 120, 0), strength=60)
                        lighting.add_transient(hit_enemy.x, hit_enemy.y,
                                                radius=100, color=(255, 180, 80), lifetime=20)
                        if hit_enemy.enemy_type == 'BOSS_DREADNAUGHT':
                            achievement_system.trigger('boss_slayer')
                            feedback.slowmo(0.25, 50)
                        rew = self.mission_system.update_combat_missions(hit_enemy.enemy_type)
                        if rew:
                            self._on_mission_complete(rew)
                        self.mission_system.update_defense_missions('enemy')
                        # Pirates hostile rep boost
                        reputation.adjust('PIRATES', -5)
                        reputation.adjust('FEDERATION', +2)
            else:
                # Enemy projectile vs player
                if self.spaceship and math.hypot(projectile.x - self.spaceship.x,
                                                  projectile.y - self.spaceship.y) < self.spaceship.size + projectile.size:
                    self.spaceship.take_damage(projectile.damage, source='combat')
                    feedback.flash(color=(255, 60, 60), strength=80)
                    feedback.shake(intensity=4, frames=8)
                    self.audio_system.play_sound('damage')
                    if projectile in self.projectiles:
                        self.projectiles.remove(projectile)

    def _spawn_boss(self):
        if not self.spaceship:
            return
        angle = random.uniform(0, math.pi * 2)
        x = self.spaceship.x + math.cos(angle) * 500
        y = self.spaceship.y + math.sin(angle) * 500
        self.enemies.append(MiniBoss(x, y))
        self._boss_spawned = True
        feedback.flash(color=(255, 0, 200), strength=120)
        feedback.shake(intensity=10, frames=20)
        feedback.slowmo(0.5, 30)
        # Cinematic letterbox during the boss intro; clears after a few seconds.
        feedback.letterbox(0.10, text="MINI-BOSS")
        self._boss_letterbox_frames = 180  # ~3 seconds at 60 fps
        self.audio_system.play_sound('stinger_boss')
        # Duck music briefly so the stinger lands.
        self.audio_system.duck_music(0.25, frames=90)
        self.hud.push_alert("MINI-BOSS APROXIMANDO", color=(255, 60, 200), duration_frames=120)

    def _on_mission_complete(self, reward):
        self.run_stats.missions_completed += 1
        self.score += 100
        if isinstance(reward, dict):
            for item, qty in reward.items():
                self.spaceship.inventory.add_item(item, qty)
        feedback.floating(0, 0, t('feedback.mission_complete'),
                          color=(100, 255, 200), lifetime=90, size=22, world_space=False)
        self.audio_system.play_sound('ui_confirm')
        skills.earn(1)

    def _track_visited(self):
        if not self.spaceship:
            return
        for i, p in enumerate(self.planets):
            d = math.hypot(self.spaceship.x - p.x, self.spaceship.y - p.y)
            if d < p.radius + 80:
                if i not in self.visited_planets:
                    self.visited_planets.add(i)
                    self.run_stats.planets_visited = len(self.visited_planets)
                    feedback.floating(p.x, p.y, p.name, color=(180, 230, 255), lifetime=60, size=20)

    def _check_alerts(self):
        if not self.spaceship:
            return
        for k in self.alert_cooldowns:
            if self.alert_cooldowns[k] > 0:
                self.alert_cooldowns[k] -= 1
        if self.spaceship.oxygen / max(self.spaceship.max_oxygen, 1) < 0.2 and self.alert_cooldowns['oxygen'] == 0:
            self.hud.push_alert(t('alert.oxygen_low'), color=(120, 220, 255))
            self.audio_system.play_sound('alert_low')
            self.alert_cooldowns['oxygen'] = 240
        if self.spaceship.health / max(self.spaceship.max_health, 1) < 0.2 and self.alert_cooldowns['health'] == 0:
            self.hud.push_alert(t('alert.health_critical'), color=(255, 80, 80))
            self.audio_system.play_sound('alert_critical')
            self.alert_cooldowns['health'] = 240
            feedback.set_vignette(0.6)
        elif self.spaceship.health / max(self.spaceship.max_health, 1) > 0.5:
            feedback.set_vignette(0.0)
        if self.spaceship.fuel / max(self.spaceship.max_fuel, 1) < 0.2 and self.alert_cooldowns['fuel'] == 0:
            self.hud.push_alert(t('alert.fuel_low'), color=(255, 200, 100))
            self.audio_system.play_sound('alert_low')
            self.alert_cooldowns['fuel'] = 240

    # ----- rendering -----
    def render(self, surface):
        with prof_section('render.bg'):
            surface.fill((4, 6, 22))
            self.renderer.render_stars(surface, self.camera_x, self.camera_y)

        with prof_section('render.planets'):
            for planet in self.planets:
                screen_x = planet.x - self.camera_x
                screen_y = planet.y - self.camera_y
                if -planet.size < screen_x < display.WIDTH + planet.size and -planet.size < screen_y < display.HEIGHT + planet.size:
                    self.renderer.render_planet(surface, planet, self.camera_x, self.camera_y)

        with prof_section('render.blocks'):
            tutorial_hl = self.tutorial.get_highlight_target(self) if self.tutorial.active else None
            for block in self.blocks:
                sx = block.x - self.camera_x
                sy = block.y - self.camera_y
                if -BLOCK_SIZE < sx < display.WIDTH + BLOCK_SIZE and -BLOCK_SIZE < sy < display.HEIGHT + BLOCK_SIZE:
                    block.render(surface, self.camera_x, self.camera_y)
            if tutorial_hl:
                hx, hy, hr = tutorial_hl
                pygame.draw.circle(surface, (255, 220, 80),
                                   (int(hx - self.camera_x), int(hy - self.camera_y)),
                                   hr + int(math.sin(time.time() * 4) * 4), 2)

        with prof_section('render.merchants'):
            for m in self.merchants:
                m.render(surface, self.camera_x, self.camera_y)

        with prof_section('render.enemies'):
            for enemy in self.enemies:
                if self.spaceship:
                    d = math.hypot(enemy.x - self.spaceship.x, enemy.y - self.spaceship.y)
                    if d < CULLING_DISTANCE:
                        sx = enemy.x - self.camera_x
                        sy = enemy.y - self.camera_y
                        if -50 < sx < display.WIDTH + 50 and -50 < sy < display.HEIGHT + 50:
                            enemy.render(surface, self.camera_x, self.camera_y)

        with prof_section('render.projectiles'):
            for p in self.projectiles:
                p.render(surface, self.camera_x, self.camera_y)

        with prof_section('render.particles'):
            self.particle_system.render(surface, self.camera_x, self.camera_y)

        with prof_section('render.ship'):
            if self.spaceship:
                # Mining range indicator
                sx = int(self.spaceship.x - self.camera_x)
                sy = int(self.spaceship.y - self.camera_y)
                if pygame.key.get_pressed()[pygame.K_e]:
                    pygame.draw.circle(surface, (255, 220, 80, 100), (sx, sy), self.spaceship.mine_range, 1)
                self.renderer.render_spaceship(surface, self.spaceship, self.camera_x, self.camera_y)

        with prof_section('render.replay'):
            ghost = replay.current_ghost() if replay.playback else None
            if ghost:
                gx, gy, ga = ghost
                pygame.draw.circle(surface, (100, 255, 100), (int(gx - self.camera_x), int(gy - self.camera_y)), 6, 1)

        # Multiplayer players
        self.multiplayer_system.render_players(surface, self.camera_x, self.camera_y)

        # Lighting overlay (additive)
        with prof_section('render.lighting'):
            lighting.render(surface, self.camera_x, self.camera_y, ambient=1.0)

        # World-space floating text (damage numbers, etc.)
        feedback.render_world(surface, self.camera_x, self.camera_y)

        # HUD
        with prof_section('render.hud'):
            if self.spaceship:
                self.hud.render(surface, self.spaceship, self.camera_x, self.camera_y, self.score)
            self.mission_system.render_missions(surface, display.WIDTH)
            self.station_system.render_blueprint_info(surface)
            self.minimap.render(surface, self)
            self.compass.render(surface, self, self.camera_x, self.camera_y)
            self.debug_system.render_debug_info(surface)
            # Achievement notifications
            self._render_achievement_notifications(surface)
            # Tutorial
            self.tutorial.render(surface)
            # Speedrun timer
            from systems.speedrun import speedrun as sr
            if sr.enabled:
                from utils.font import get_font, render_outlined
                txt = render_outlined(get_font(20), sr.format_time(), (255, 255, 100), (0, 0, 0), 2)
                surface.blit(txt, (display.WIDTH // 2 - txt.get_width() // 2, 10))
            # Storm visual
            if weather.is_active():
                overlay = pygame.Surface((display.WIDTH, display.HEIGHT), pygame.SRCALPHA)
                overlay.fill((40, 40, 200, 18))
                surface.blit(overlay, (0, 0))

        # Screen-space feedback (flashes, vignette, HUD-space floating text)
        feedback.render_screen(surface)

        if SHOW_COLLISION_BOXES:
            all_objects = self.planets + self.blocks + self.enemies
            if self.spaceship:
                all_objects = all_objects + [self.spaceship]
            self.debug_system.render_collision_boxes(surface, all_objects, self.camera_x, self.camera_y)

    def _render_achievement_notifications(self, surface):
        from utils.font import get_font, draw_panel, render_outlined
        from utils.i18n import get_language
        notifs = achievement_system.get_active_notifications()
        if not notifs:
            return
        lang_field = 'name_pt' if get_language() == 'pt' else 'name_en'
        for i, (aid, expire) in enumerate(notifs[:3]):
            data = ACHIEVEMENTS.get(aid)
            if not data:
                continue
            name = data.get(lang_field, data.get('name_pt', aid))
            text = render_outlined(get_font(20), f"★ {name}", (255, 220, 80), (0, 0, 0), 1)
            w = text.get_width() + 30
            h = text.get_height() + 12
            rect = pygame.Rect(display.WIDTH - w - 20, 220 + i * (h + 6), w, h)
            draw_panel(surface, rect, bg=(50, 30, 0), border=(255, 220, 80), bg_alpha=200, border_width=2, radius=6)
            surface.blit(text, (rect.x + 15, rect.y + 6))

    def handle_event(self, event):
        gamepad.update_input_type(event.type)
        self.input_manager.handle_event(event)

    def is_game_over(self):
        return self.game_state == "game_over"
