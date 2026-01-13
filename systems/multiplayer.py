"""
Sistema de multiplayer local do Navecraft
"""

import pygame
import math
from settings import *
from entities.spaceship import Spaceship

class MultiplayerSystem:
    def __init__(self, game):
        """Inicializa o sistema de multiplayer"""
        self.game = game
        self.players = []
        self.active = False
        self.max_players = 4
        
        # Controles para jogador 2
        self.player2_controls = {
            'MOVE_UP': [pygame.K_i],
            'MOVE_DOWN': [pygame.K_k],
            'MOVE_LEFT': [pygame.K_j],
            'MOVE_RIGHT': [pygame.K_l],
            'SHOOT': [pygame.K_o],
            'MINE': [pygame.K_p],
            'BUILD': [pygame.K_SEMICOLON]
        }
        
        # Controles para jogador 3
        self.player3_controls = {
            'MOVE_UP': [pygame.K_t],
            'MOVE_DOWN': [pygame.K_g],
            'MOVE_LEFT': [pygame.K_f],
            'MOVE_RIGHT': [pygame.K_h],
            'SHOOT': [pygame.K_y],
            'MINE': [pygame.K_u],
            'BUILD': [pygame.K_i]
        }
        
        # Controles para jogador 4
        self.player4_controls = {
            'MOVE_UP': [pygame.K_RSHIFT],
            'MOVE_DOWN': [pygame.K_RCTRL],
            'MOVE_LEFT': [pygame.K_RETURN],
            'MOVE_RIGHT': [pygame.K_RALT],
            'SHOOT': [pygame.K_RSUPER],
            'MINE': [pygame.K_MENU],
            'BUILD': [pygame.K_RETURN]
        }
    
    def add_player(self, player_id):
        """Adiciona um novo jogador"""
        if len(self.players) >= self.max_players:
            return False
        
        # Cria nave para o novo jogador
        spawn_x = SCREEN_WIDTH // 2 + (player_id - 1) * 100
        spawn_y = SCREEN_HEIGHT // 2 + (player_id - 1) * 100
        
        player = {
            'id': player_id,
            'spaceship': Spaceship(spawn_x, spawn_y),
            'controls': self.get_player_controls(player_id),
            'color': self.get_player_color(player_id)
        }
        
        self.players.append(player)
        self.active = True
        
        return True
    
    def get_player_controls(self, player_id):
        """Retorna controles para um jogador específico"""
        if player_id == 1:
            return CONTROLS
        elif player_id == 2:
            return self.player2_controls
        elif player_id == 3:
            return self.player3_controls
        elif player_id == 4:
            return self.player4_controls
        return CONTROLS
    
    def get_player_color(self, player_id):
        """Retorna cor para um jogador específico"""
        colors = {
            1: (255, 255, 255),  # Branco
            2: (255, 0, 0),      # Vermelho
            3: (0, 255, 0),      # Verde
            4: (0, 0, 255)       # Azul
        }
        return colors.get(player_id, (255, 255, 255))
    
    def update(self, input_manager):
        """Atualiza todos os jogadores"""
        if not self.active:
            return
        
        # Atualiza jogador principal (já é feito no Game.update)
        
        # Atualiza jogadores adicionais
        for player in self.players[1:]:  # Pula jogador principal
            self.update_player(player, input_manager)
    
    def update_player(self, player, input_manager):
        """Atualiza um jogador específico"""
        spaceship = player['spaceship']
        controls = player['controls']
        
        # Movimento
        dx, dy = 0, 0
        
        if input_manager.is_key_pressed(controls['MOVE_UP'][0]):
            dy -= 1
        if input_manager.is_key_pressed(controls['MOVE_DOWN'][0]):
            dy += 1
        if input_manager.is_key_pressed(controls['MOVE_LEFT'][0]):
            dx -= 1
        if input_manager.is_key_pressed(controls['MOVE_RIGHT'][0]):
            dx += 1
        
        # Normaliza movimento diagonal
        if dx != 0 and dy != 0:
            dx *= 0.707
            dy *= 0.707
        
        # Aplica movimento
        if dx != 0 or dy != 0:
            move_angle = math.atan2(dy, dx)
            spaceship.vx += math.cos(move_angle) * SPACESHIP_ACCELERATION
            spaceship.vy += math.sin(move_angle) * SPACESHIP_ACCELERATION
            spaceship.angle = move_angle
        
        # Desaceleração
        spaceship.vx *= SPACESHIP_DECELERATION
        spaceship.vy *= SPACESHIP_DECELERATION
        
        # Limita velocidade
        speed = math.sqrt(spaceship.vx**2 + spaceship.vy**2)
        if speed > spaceship.max_speed:
            spaceship.vx = (spaceship.vx / speed) * spaceship.max_speed
            spaceship.vy = (spaceship.vy / speed) * spaceship.max_speed
        
        # Atualiza posição
        spaceship.x += spaceship.vx
        spaceship.y += spaceship.vy
        
        # Mantém dentro dos limites
        spaceship.x = max(0, min(spaceship.x, WORLD_SIZE * BLOCK_SIZE))
        spaceship.y = max(0, min(spaceship.y, WORLD_SIZE * BLOCK_SIZE))
        
        # Consome recursos
        if dx != 0 or dy != 0:
            spaceship.consume_energy(0.1 * spaceship.energy_efficiency)
        spaceship.consume_oxygen(0.05 * spaceship.oxygen_efficiency)
        
        # Mineração
        if input_manager.is_key_just_pressed(controls['MINE'][0]):
            mined_value = spaceship.mine(self.game.blocks)
            if mined_value > 0:
                print(f"Jogador {player['id']} minou: {mined_value} recursos!")
        
        # Construção
        if input_manager.is_key_just_pressed(controls['BUILD'][0]):
            mouse_x, mouse_y = input_manager.get_mouse_position()
            world_mouse_x = mouse_x + self.game.camera_x
            world_mouse_y = mouse_y + self.game.camera_y
            
            if spaceship.build(self.game.blocks, world_mouse_x, world_mouse_y):
                print(f"Jogador {player['id']} construiu bloco!")
    
    def render_players(self, surface, camera_x, camera_y):
        """Renderiza todos os jogadores"""
        if not self.active:
            return
        
        # Renderiza jogador principal (já é feito no Game.render)
        
        # Renderiza jogadores adicionais
        for player in self.players[1:]:
            self.render_player(player, surface, camera_x, camera_y)
    
    def render_player(self, player, surface, camera_x, camera_y):
        """Renderiza um jogador específico"""
        spaceship = player['spaceship']
        color = player['color']
        
        # Posição na tela
        screen_x = int(spaceship.x - camera_x)
        screen_y = int(spaceship.y - camera_y)
        
        # Verifica se está visível
        if (screen_x < -50 or screen_x > SCREEN_WIDTH + 50 or 
            screen_y < -50 or screen_y > SCREEN_HEIGHT + 50):
            return
        
        # Desenha nave
        points = spaceship.get_ship_points(screen_x, screen_y)
        pygame.draw.polygon(surface, color, points)
        pygame.draw.polygon(surface, WHITE, points, 2)
        
        # Desenha detalhes da nave
        spaceship.render_ship_details(surface, screen_x, screen_y)
        
        # Desenha identificador do jogador
        font = pygame.font.Font(None, 20)
        player_text = font.render(f"P{player['id']}", True, WHITE)
        text_rect = player_text.get_rect()
        text_rect.center = (screen_x, screen_y - 30)
        surface.blit(player_text, text_rect)
    
    def get_all_spaceships(self):
        """Retorna todas as naves dos jogadores"""
        ships = [self.game.spaceship] if self.game.spaceship else []
        for player in self.players:
            ships.append(player['spaceship'])
        return ships
    
    def toggle_multiplayer(self):
        """Ativa/desativa multiplayer"""
        if self.active:
            self.players.clear()
            self.active = False
            print("Multiplayer desativado")
        else:
            self.add_player(1)  # Adiciona jogador 2
            print("Multiplayer ativado - Jogador 2 adicionado")
            print("Pressione F7 para adicionar mais jogadores")
    
    def add_more_players(self):
        """Adiciona mais jogadores"""
        if not self.active:
            return
        
        current_players = len(self.players) + 1  # +1 para jogador principal
        if current_players < self.max_players:
            self.add_player(current_players + 1)
            print(f"Jogador {current_players + 1} adicionado!")
        else:
            print("Número máximo de jogadores atingido!")
