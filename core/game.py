"""
Classe principal do jogo Navecraft
"""

import pygame
import math
import time
from settings import *
from core.input import InputManager
from core.renderer import Renderer
from core.audio import AudioSystem
from entities.spaceship import Spaceship, Projectile
from entities.enemy import Enemy
from systems.physics import PhysicsSystem
from systems.generation import WorldGenerator
from systems.particles import ParticleSystem
from systems.missions import MissionSystem
from systems.inventory import CraftingSystem
from systems.upgrades import UpgradeSystem
from systems.multiplayer import MultiplayerSystem
from systems.stations import StationSystem
from systems.save_system import SaveSystem
from ui.hud import HUD
from utils.debug import DebugSystem
from utils.logger import game_logger

class Game:
    def __init__(self):
        """Inicializa o jogo"""
        # Registra informações do sistema
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
        
        # Sistema de crafting será inicializado após a nave
        
        # Entidades do jogo
        self.spaceship = None
        self.planets = []
        self.blocks = []
        self.enemies = []
        self.projectiles = []
        self.particles = []
        
        # Sistema de câmera
        self.camera_x = 0
        self.camera_y = 0
        
        # HUD
        self.hud = HUD()
        
        # Estado do jogo
        self.game_state = "playing"

        # Pontuação
        self.score = 0
        
        # Performance tracking
        self.last_frame_time = time.time()
        
        # Sistema de missões
        self.game_time = 0
        self.visited_planets = set()
        
        # Sistema de save/load
        self.save_system = SaveSystem()

        # Inicializa o mundo
        self.initialize_world()
        self.audio_system.play_music() # Added music start
        
        game_logger.info("Jogo inicializado com sucesso")

    def initialize_world(self):
        """Inicializa o mundo do jogo"""
        game_logger.info("Inicializando mundo do jogo")
        
        # Cria a nave do jogador
        self.spaceship = Spaceship(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        
        # Inicializa sistema de crafting
        self.crafting_system = CraftingSystem(self.spaceship.inventory)
        
        # Inicializa sistema de upgrades
        self.upgrade_system = UpgradeSystem(self.spaceship)
        
        # Inicializa sistema de multiplayer
        self.multiplayer_system = MultiplayerSystem(self)

        # Inicializa sistema de estacoes
        self.station_system = StationSystem()
        
        # Gera planetas
        self.planets = self.world_generator.generate_planets()
        game_logger.info(f"Gerados {len(self.planets)} planetas")
        
        # Gera blocos
        self.blocks = self.world_generator.generate_blocks()
        game_logger.info(f"Gerados {len(self.blocks)} blocos")

        # Gera cavernas nos planetas
        cave_blocks = self.world_generator.generate_caves(self.planets)
        self.blocks.extend(cave_blocks)
        game_logger.info(f"Gerados {len(cave_blocks)} blocos de cavernas")
        
        # Gera inimigos
        self.enemies = self.world_generator.generate_enemies()
        game_logger.info(f"Gerados {len(self.enemies)} inimigos")
        
        game_logger.info("Mundo inicializado com sucesso")

    def update(self):
        """Atualiza a lógica do jogo"""
        # Mede tempo do frame
        current_time = time.time()
        frame_time = (current_time - self.last_frame_time) * 1000  # em ms
        self.last_frame_time = current_time
        
        # Atualiza tempo do jogo
        self.game_time += frame_time / 1000  # em segundos
        
        # Atualiza sistema de debug
        self.debug_system.update_fps()
        self.debug_system.update_frame_time(frame_time)
        
        # Atualiza input (posição do mouse, botões do mouse)
        # Nota: NÃO limpa keys_just_pressed aqui - isso é feito no fim do frame
        self.input_manager.update_mouse()

        # Atualiza nave
        if self.spaceship:
            self.spaceship.update(self.input_manager)
            
            # Atualiza informações de debug
            self.debug_system.set_debug_info('spaceship_pos', (self.spaceship.x, self.spaceship.y))
            self.debug_system.set_debug_info('camera_x', self.camera_x)
            self.debug_system.set_debug_info('camera_y', self.camera_y)
            
            # Efeitos de partículas para movimento
            dx, dy = self.input_manager.get_movement_vector()
            if dx != 0 or dy != 0:
                # Efeito de propulsão
                angle = math.atan2(dy, dx)
                self.particle_system.create_thrust_effect(self.spaceship.x, self.spaceship.y, angle)
            
            # Verifica tiro
            if self.input_manager.is_control_just_pressed('SHOOT'):
                if self.spaceship.shoot():
                    proj = Projectile(
                        self.spaceship.x + math.cos(self.spaceship.angle) * self.spaceship.size,
                        self.spaceship.y + math.sin(self.spaceship.angle) * self.spaceship.size,
                        self.spaceship.angle
                    )
                    self.projectiles.append(proj)
                    self.audio_system.play_sound('shoot')
                    game_logger.log_game_event("shooting", f"angle={self.spaceship.angle:.2f}")

            # Verifica mineração
            if self.input_manager.is_control_just_pressed('MINE'):
                mined_value = self.spaceship.mine(self.blocks)
                if mined_value > 0:
                    self.score += mined_value
                    print(f"Minado: {mined_value} recursos!")
                    self.audio_system.play_sound('mine')
                    self.audio_system.play_sound('collect')
                    self.particle_system.create_collect_effect(self.spaceship.x, self.spaceship.y) # Added particle effect
                    self.debug_system.log_info(f"Minado: {mined_value} recursos")
                    game_logger.log_game_event("mining", f"mined_value={mined_value}")
                    
                    # Atualiza missões de mineração
                    for block in self.blocks:
                        if block.collected and block.block_type:
                            reward = self.mission_system.update_mining_missions(block.block_type)
                            if reward:
                                self.score += 100
                                print(f"Missão completada! Recompensa: {reward}")
                                game_logger.log_game_event("mission_completed", f"reward={reward}")
            
            # Verifica construção
            if self.input_manager.is_control_just_pressed('BUILD'):
                mouse_x, mouse_y = self.input_manager.get_mouse_position()
                world_mouse_x = mouse_x + self.camera_x
                world_mouse_y = mouse_y + self.camera_y
                
                if self.spaceship.build(self.blocks, world_mouse_x, world_mouse_y):
                    self.score += 5
                    print(f"Construído bloco de {self.spaceship.selected_block_type}!")
                    self.audio_system.play_sound('build')
                    self.particle_system.create_collect_effect(world_mouse_x, world_mouse_y, (0, 255, 255)) # Added particle effect
                    self.debug_system.log_info(f"Construído bloco de {self.spaceship.selected_block_type}")
                    game_logger.log_game_event("building", f"block_type={self.spaceship.selected_block_type}")
                    
                    # Atualiza missões de construção
                    reward = self.mission_system.update_building_missions(self.spaceship.selected_block_type)
                    if reward:
                        self.score += 100
                        print(f"Missão de construção completada! Recompensa: {reward}")
                        game_logger.log_game_event("mission_completed", f"building_reward={reward}")
            
            # Verifica seleção de blocos
            if self.input_manager.is_control_just_pressed('SELECT_IRON'):
                self.spaceship.select_block_type('IRON')
                print("Selecionado: IRON")
                game_logger.log_game_event("block_selection", "IRON")
            elif self.input_manager.is_control_just_pressed('SELECT_GOLD'):
                self.spaceship.select_block_type('GOLD')
                print("Selecionado: GOLD")
                game_logger.log_game_event("block_selection", "GOLD")
            elif self.input_manager.is_control_just_pressed('SELECT_CRYSTAL'):
                self.spaceship.select_block_type('CRYSTAL')
                print("Selecionado: CRYSTAL")
                game_logger.log_game_event("block_selection", "CRYSTAL")
            elif self.input_manager.is_control_just_pressed('SELECT_FUEL'):
                self.spaceship.select_block_type('FUEL')
                print("Selecionado: FUEL")
                game_logger.log_game_event("block_selection", "FUEL")
            elif self.input_manager.is_control_just_pressed('SELECT_OXYGEN'):
                self.spaceship.select_block_type('OXYGEN')
                print("Selecionado: OXYGEN")
                game_logger.log_game_event("block_selection", "OXYGEN")
            
            # Verifica aceitar missão (tecla M)
            if self.input_manager.is_control_just_pressed('MISSION'):
                new_mission = self.mission_system.get_random_mission()
                if new_mission:
                    self.mission_system.accept_mission(new_mission)
                    print(f"Nova missão aceita: {new_mission.description}")
                    game_logger.log_game_event("mission_accepted", new_mission.description)
            
            # Verifica crafting
            if self.input_manager.is_control_just_pressed('CRAFT_REPAIR'):
                if self.crafting_system.craft_item('REPAIR_KIT'):
                    print("Craftado: REPAIR_KIT!")
                    self.audio_system.play_sound('collect')
                    self.particle_system.create_collect_effect(self.spaceship.x, self.spaceship.y, (0, 255, 0))
                    game_logger.log_game_event("crafting", "REPAIR_KIT")
                else:
                    print("Recursos insuficientes para REPAIR_KIT!")
            
            elif self.input_manager.is_control_just_pressed('CRAFT_ENERGY'):
                if self.crafting_system.craft_item('ENERGY_PACK'):
                    print("Craftado: ENERGY_PACK!")
                    self.audio_system.play_sound('collect')
                    self.particle_system.create_collect_effect(self.spaceship.x, self.spaceship.y, (255, 255, 0))
                    game_logger.log_game_event("crafting", "ENERGY_PACK")
                else:
                    print("Recursos insuficientes para ENERGY_PACK!")
            
            elif self.input_manager.is_control_just_pressed('CRAFT_OXYGEN'):
                if self.crafting_system.craft_item('OXYGEN_TANK'):
                    print("Craftado: OXYGEN_TANK!")
                    self.audio_system.play_sound('collect')
                    self.particle_system.create_collect_effect(self.spaceship.x, self.spaceship.y, (0, 255, 255))
                    game_logger.log_game_event("crafting", "OXYGEN_TANK")
                else:
                    print("Recursos insuficientes para OXYGEN_TANK!")
            
            elif self.input_manager.is_control_just_pressed('CRAFT_SHIELD'):
                if self.crafting_system.craft_item('SHIELD_BOOSTER'):
                    print("Craftado: SHIELD_BOOSTER!")
                    self.audio_system.play_sound('collect')
                    self.particle_system.create_collect_effect(self.spaceship.x, self.spaceship.y, (138, 43, 226))
                    game_logger.log_game_event("crafting", "SHIELD_BOOSTER")
                else:
                    print("Recursos insuficientes para SHIELD_BOOSTER!")
            
            # Verifica upgrades
            if self.input_manager.is_control_just_pressed('UPGRADE_ENGINE'):
                if self.upgrade_system.apply_upgrade('ENGINE_BOOST'):
                    print("Upgrade aplicado: Motor Aprimorado!")
                    self.audio_system.play_sound('collect')
                    self.particle_system.create_collect_effect(self.spaceship.x, self.spaceship.y, (255, 165, 0))
                    game_logger.log_game_event("upgrade", "ENGINE_BOOST")
                else:
                    print("Recursos insuficientes para upgrade de motor!")
            
            elif self.input_manager.is_control_just_pressed('UPGRADE_SHIELD'):
                if self.upgrade_system.apply_upgrade('SHIELD_ENHANCEMENT'):
                    print("Upgrade aplicado: Escudo Reforçado!")
                    self.audio_system.play_sound('collect')
                    self.particle_system.create_collect_effect(self.spaceship.x, self.spaceship.y, (0, 255, 0))
                    game_logger.log_game_event("upgrade", "SHIELD_ENHANCEMENT")
                else:
                    print("Recursos insuficientes para upgrade de escudo!")
            
            elif self.input_manager.is_control_just_pressed('UPGRADE_ENERGY'):
                if self.upgrade_system.apply_upgrade('ENERGY_EFFICIENCY'):
                    print("Upgrade aplicado: Eficiência Energética!")
                    self.audio_system.play_sound('collect')
                    self.particle_system.create_collect_effect(self.spaceship.x, self.spaceship.y, (255, 255, 0))
                    game_logger.log_game_event("upgrade", "ENERGY_EFFICIENCY")
                else:
                    print("Recursos insuficientes para upgrade de energia!")
            
            elif self.input_manager.is_control_just_pressed('UPGRADE_MINING'):
                if self.upgrade_system.apply_upgrade('MINING_LASER'):
                    print("Upgrade aplicado: Laser de Mineração!")
                    self.audio_system.play_sound('collect')
                    self.particle_system.create_collect_effect(self.spaceship.x, self.spaceship.y, (138, 43, 226))
                    game_logger.log_game_event("upgrade", "MINING_LASER")
                else:
                    print("Recursos insuficientes para upgrade de mineração!")
            
            elif self.input_manager.is_control_just_pressed('UPGRADE_OXYGEN'):
                if self.upgrade_system.apply_upgrade('OXYGEN_SYSTEM'):
                    print("Upgrade aplicado: Sistema de Oxigênio!")
                    self.audio_system.play_sound('collect')
                    self.particle_system.create_collect_effect(self.spaceship.x, self.spaceship.y, (0, 255, 255))
                    game_logger.log_game_event("upgrade", "OXYGEN_SYSTEM")
                else:
                    print("Recursos insuficientes para upgrade de oxigênio!")
            
            elif self.input_manager.is_control_just_pressed('UPGRADE_FUEL'):
                if self.upgrade_system.apply_upgrade('FUEL_TANK'):
                    print("Upgrade aplicado: Tanque de Combustível!")
                    self.audio_system.play_sound('collect')
                    self.particle_system.create_collect_effect(self.spaceship.x, self.spaceship.y, (255, 165, 0))
                    game_logger.log_game_event("upgrade", "FUEL_TANK")
                else:
                    print("Recursos insuficientes para upgrade de combustível!")
            
            # Verifica multiplayer
            if self.input_manager.is_control_just_pressed('MULTIPLAYER_TOGGLE'):
                self.multiplayer_system.toggle_multiplayer()
                game_logger.log_game_event("multiplayer", "toggle")
            
            elif self.input_manager.is_control_just_pressed('MULTIPLAYER_ADD_PLAYER'):
                self.multiplayer_system.add_more_players()
                game_logger.log_game_event("multiplayer", "add_player")

            # Quick save
            if self.input_manager.is_control_just_pressed('QUICK_SAVE'):
                self.save_system.save_game(self)
                game_logger.log_game_event("save", "quick_save")

            # Construir estacao espacial
            if self.input_manager.is_control_just_pressed('BUILD_STATION'):
                bp_name, bp = self.station_system.get_selected_blueprint()
                if self.station_system.build_station(
                    bp_name, self.spaceship.x, self.spaceship.y,
                    self.blocks, self.spaceship.inventory
                ):
                    self.score += 200
                    print(f"Estacao construida: {bp['name']}!")
                    self.audio_system.play_sound('build')
                    self.particle_system.create_collect_effect(self.spaceship.x, self.spaceship.y, (0, 255, 255))
                    game_logger.log_game_event("station_built", bp_name)
                else:
                    print(f"Recursos insuficientes ou espaco ocupado para {bp['name']}!")
                    self.station_system.cycle_blueprint()
        
        # Atualiza missões de sobrevivência
        self.mission_system.update_survival_missions(self.game_time, self.spaceship)
        
        # Atualiza sistema de multiplayer
        self.multiplayer_system.update(self.input_manager)

        # Aplica efeitos de estacoes espaciais
        if self.spaceship:
            self.station_system.apply_station_effects(self.spaceship)
        
        # Atualiza missões de exploração
        self.mission_system.update_exploration_missions(self.spaceship, self.visited_planets)
        
        # Atualiza inimigos (apenas os próximos)
        visible_enemies = 0
        for enemy in self.enemies:
            # Otimização: só atualiza inimigos próximos
            if self.spaceship:
                distance = math.sqrt((enemy.x - self.spaceship.x)**2 + (enemy.y - self.spaceship.y)**2)
                if distance < ENEMY_UPDATE_DISTANCE:  # Só atualiza inimigos a 500 pixels
                    enemy.update(self.spaceship)
                    visible_enemies += 1
        
        # Atualiza física
        self.physics_system.update(self.spaceship, self.planets, self.blocks)
        
        # Atualiza projéteis e verifica colisões com inimigos
        for projectile in self.projectiles[:]:
            projectile.update()
            if not projectile.is_alive():
                self.projectiles.remove(projectile)
                continue
            # Verifica colisão com inimigos
            for enemy in self.enemies[:]:
                dist = math.sqrt((projectile.x - enemy.x)**2 + (projectile.y - enemy.y)**2)
                if dist < enemy.size + projectile.size:
                    enemy.take_damage(projectile.damage)
                    self.particle_system.create_collect_effect(enemy.x, enemy.y, (255, 100, 0))
                    if projectile in self.projectiles:
                        self.projectiles.remove(projectile)
                    if not enemy.is_alive():
                        self.score += 50
                        self.enemies.remove(enemy)
                        self.particle_system.create_collect_effect(enemy.x, enemy.y, (255, 50, 0))
                        game_logger.log_game_event("enemy_killed", f"type={enemy.enemy_type}")
                    break
        
        # Atualiza partículas (otimização: só partículas próximas)
        if self.spaceship:
            self.particle_system.update()
            # Remove partículas muito distantes
            self.particle_system.particles = [p for p in self.particle_system.particles 
                                           if abs(p.x - self.spaceship.x) < PARTICLE_CLEANUP_DISTANCE and 
                                              abs(p.y - self.spaceship.y) < PARTICLE_CLEANUP_DISTANCE]
        
        # Atualiza camera para seguir nave(s)
        if self.spaceship:
            cam_center = self.multiplayer_system.get_camera_center()
            if cam_center:
                self.camera_x = cam_center[0] - SCREEN_WIDTH // 2
                self.camera_y = cam_center[1] - SCREEN_HEIGHT // 2
            else:
                self.camera_x = self.spaceship.x - SCREEN_WIDTH // 2
                self.camera_y = self.spaceship.y - SCREEN_HEIGHT // 2
        
        # Atualiza contadores de objetos visíveis
        visible_planets = len([p for p in self.planets if -p.size < p.x - self.camera_x < SCREEN_WIDTH + p.size and -p.size < p.y - self.camera_y < SCREEN_HEIGHT + p.size])
        visible_blocks = len([b for b in self.blocks if -BLOCK_SIZE < b.x - self.camera_x < SCREEN_WIDTH + BLOCK_SIZE and -BLOCK_SIZE < b.y - self.camera_y < SCREEN_HEIGHT + BLOCK_SIZE])
        visible_particles = len(self.particle_system.particles)
        visible_projectiles = len(self.projectiles)
        
        self.debug_system.update_visible_objects({
            'planets': visible_planets,
            'blocks': visible_blocks,
            'enemies': visible_enemies,
            'particles': visible_particles,
            'projectiles': visible_projectiles
        })
        
        # Registra performance periodicamente
        if hasattr(self, '_performance_counter'):
            self._performance_counter += 1
        else:
            self._performance_counter = 0
        
        if self._performance_counter % 60 == 0:  # A cada 60 frames
            self.score += 1  # Pontos por sobrevivência
            fps = self.debug_system.debug_info.get('fps', 0)
            object_counts = f"P:{visible_planets},B:{visible_blocks},E:{visible_enemies},Pt:{visible_particles}"
            game_logger.log_performance(fps, frame_time, object_counts)
        
        # Atualiza informações de inventário para debug
        if self.spaceship:
            inventory_info = f"Energia: {self.spaceship.energy:.0f}, Oxigênio: {self.spaceship.oxygen:.0f}, Combustível: {self.spaceship.fuel:.0f}"
            self.debug_system.set_debug_info('inventory_info', inventory_info)
        
        # Autosave
        self.save_system.check_autosave(self)

        # Verifica game over
        if self.spaceship and not self.spaceship.is_alive():
            self.game_state = "game_over"
            self.debug_system.log_info("Game Over - Nave destruída", "WARNING")
            game_logger.log_game_event("game_over", "spaceship_destroyed")

        # Limpa keys_just_pressed/released no fim do frame
        self.input_manager.clear_frame()

    def render(self, surface):
        """Renderiza o jogo"""
        # Limpa a tela
        surface.fill(BLACK)
        
        # Renderiza estrelas de fundo
        self.renderer.render_stars(surface)
        
        # Renderiza planetas (otimização: só planetas visíveis)
        for planet in self.planets:
            screen_x = planet.x - self.camera_x
            screen_y = planet.y - self.camera_y
            if -planet.size < screen_x < SCREEN_WIDTH + planet.size and -planet.size < screen_y < SCREEN_HEIGHT + planet.size:
                self.renderer.render_planet(surface, planet, screen_x, screen_y)
        
        # Renderiza blocos (otimização: só blocos visíveis)
        for block in self.blocks:
            screen_x = block.x - self.camera_x
            screen_y = block.y - self.camera_y
            if -BLOCK_SIZE < screen_x < SCREEN_WIDTH + BLOCK_SIZE and -BLOCK_SIZE < screen_y < SCREEN_HEIGHT + BLOCK_SIZE:
                block.render(surface, self.camera_x, self.camera_y)
        
        # Renderiza inimigos (otimização: só inimigos próximos)
        for enemy in self.enemies:
            if self.spaceship:
                distance = math.sqrt((enemy.x - self.spaceship.x)**2 + (enemy.y - self.spaceship.y)**2)
                if distance < CULLING_DISTANCE:  # Só renderiza inimigos a 600 pixels
                    screen_x = enemy.x - self.camera_x
                    screen_y = enemy.y - self.camera_y
                    if -50 < screen_x < SCREEN_WIDTH + 50 and -50 < screen_y < SCREEN_HEIGHT + 50:
                        enemy.render(surface, self.camera_x, self.camera_y)
        
        # Renderiza projéteis
        for projectile in self.projectiles:
            projectile.render(surface, self.camera_x, self.camera_y)
        
        # Renderiza partículas
        self.particle_system.render(surface, self.camera_x, self.camera_y)
        
        # Renderiza nave
        if self.spaceship:
            self.renderer.render_spaceship(surface, self.spaceship, self.camera_x, self.camera_y)
        
        # Renderiza jogadores multiplayer
        self.multiplayer_system.render_players(surface, self.camera_x, self.camera_y)
        
        # Renderiza HUD
        if self.spaceship:
            self.hud.render(surface, self.spaceship, self.camera_x, self.camera_y, self.score)
        
        # Renderiza missões
        self.mission_system.render_missions(surface)

        # Renderiza info de estacao selecionada
        self.station_system.render_blueprint_info(surface)
        
        # Renderiza informações de debug
        self.debug_system.render_debug_info(surface)
        
        # Renderiza caixas de colisão se habilitado
        if SHOW_COLLISION_BOXES:
            all_objects = self.planets + self.blocks + self.enemies + [self.spaceship] if self.spaceship else []
            self.debug_system.render_collision_boxes(surface, all_objects, self.camera_x, self.camera_y)

    def handle_event(self, event):
        """Processa eventos do jogo"""
        self.input_manager.handle_event(event)

    def is_game_over(self):
        """Verifica se o jogo acabou"""
        return self.game_state == "game_over"
