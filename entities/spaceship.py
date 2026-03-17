"""
Nave espacial do jogador
"""

import pygame
import math
from settings import *


class Projectile:
    """Projétil laser disparado pela nave"""
    def __init__(self, x, y, angle):
        self.x = x
        self.y = y
        self.vx = math.cos(angle) * LASER_SPEED
        self.vy = math.sin(angle) * LASER_SPEED
        self.size = 4
        self.damage = LASER_DAMAGE
        self.lifetime = 120  # frames

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.lifetime -= 1

    def is_alive(self):
        return self.lifetime > 0

    def render(self, surface, camera_x, camera_y):
        screen_x = int(self.x - camera_x)
        screen_y = int(self.y - camera_y)
        pygame.draw.circle(surface, CYAN, (screen_x, screen_y), self.size)
        # Trail effect
        trail_x = int(self.x - self.vx * 0.3 - camera_x)
        trail_y = int(self.y - self.vy * 0.3 - camera_y)
        pygame.draw.line(surface, (0, 200, 255), (trail_x, trail_y), (screen_x, screen_y), 2)

class Spaceship:
    def __init__(self, x, y):
        """Inicializa a nave espacial"""
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.angle = 0.0
        self.size = SPACESHIP_SIZE
        
        # Status da nave
        self.health = SPACESHIP_HEALTH
        self.max_health = SPACESHIP_HEALTH
        self.energy = SPACESHIP_ENERGY
        self.max_energy = SPACESHIP_ENERGY
        self.oxygen = SPACESHIP_OXYGEN
        self.max_oxygen = SPACESHIP_OXYGEN
        self.fuel = 100
        self.max_fuel = 100
        
        # Controles
        self.last_shot_time = 0
        self.shooting = False
        self.last_mine_time = 0
        self.mining = False
        
        # Propulsão
        self.thrust_particles = []
        self.thrust_timer = 0
        
        # Mineração
        self.mine_range = 50
        self.mine_damage = 25
        self.mine_cooldown = 500  # milissegundos
        
        # Construção
        self.build_range = 60
        self.build_cooldown = 300  # milissegundos
        self.last_build_time = 0
        self.selected_block_type = 'IRON'  # Bloco selecionado para construção
        
        # Inventário
        from systems.inventory import Inventory
        self.inventory = Inventory()
        
        # Atributos para upgrades
        self.max_speed = MAX_VELOCITY
        self.energy_efficiency = 1.0
        self.oxygen_efficiency = 1.0
        
    def update(self, input_manager):
        """Atualiza a nave baseado no input"""
        # Movimento
        dx, dy = input_manager.get_movement_vector()
        
        # Aplica aceleração
        if dx != 0 or dy != 0:
            # Calcula ângulo de movimento
            move_angle = math.atan2(dy, dx)
            
            # Aplica aceleração na direção do movimento
            self.vx += math.cos(move_angle) * SPACESHIP_ACCELERATION
            self.vy += math.sin(move_angle) * SPACESHIP_ACCELERATION
            
            # Atualiza ângulo da nave
            self.angle = move_angle
            
            # Cria partículas de propulsão
            self.create_thrust_particles()
        
        # Aplica desaceleração
        self.vx *= SPACESHIP_DECELERATION
        self.vy *= SPACESHIP_DECELERATION
        
        # Limita velocidade máxima
        speed = math.sqrt(self.vx**2 + self.vy**2)
        if speed > self.max_speed:
            self.vx = (self.vx / speed) * self.max_speed
            self.vy = (self.vy / speed) * self.max_speed
        
        # Atualiza posição
        self.x += self.vx
        self.y += self.vy
        
        # Mantém nave dentro dos limites do mundo
        self.x = max(0, min(self.x, WORLD_SIZE * BLOCK_SIZE))
        self.y = max(0, min(self.y, WORLD_SIZE * BLOCK_SIZE))
        
        # Atualiza partículas de propulsão
        self.update_thrust_particles()
        
        # Consome energia ao se mover
        if dx != 0 or dy != 0:
            self.consume_energy(0.1 * self.energy_efficiency)
        
        # Consome oxigênio
        self.consume_oxygen(0.05 * self.oxygen_efficiency)
        
        # Consome combustível
        if dx != 0 or dy != 0:
            self.consume_fuel(0.02)
        
        # Regenera energia lentamente
        self.regenerate_energy(0.02)
        
        # Verifica morte por falta de recursos
        if self.oxygen <= 0 or self.energy <= 0:
            self.health = 0
    
    def create_thrust_particles(self):
        """Cria partículas de propulsão"""
        import random
        
        # Posição da propulsão (atrás da nave)
        thrust_x = self.x - math.cos(self.angle) * self.size
        thrust_y = self.y - math.sin(self.angle) * self.size
        
        # Adiciona variação
        thrust_x += random.uniform(-5, 5)
        thrust_y += random.uniform(-5, 5)
        
        # Cria partícula
        particle = {
            'x': thrust_x,
            'y': thrust_y,
            'vx': -math.cos(self.angle) * random.uniform(2, 5),
            'vy': -math.sin(self.angle) * random.uniform(2, 5),
            'life': random.uniform(10, 20),
            'max_life': 20,
            'color': (255, 165, 0)  # Laranja
        }
        
        self.thrust_particles.append(particle)
        
        # Limita número de partículas
        if len(self.thrust_particles) > 20:
            self.thrust_particles.pop(0)
    
    def update_thrust_particles(self):
        """Atualiza partículas de propulsão"""
        for particle in self.thrust_particles[:]:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['life'] -= 1
            
            if particle['life'] <= 0:
                self.thrust_particles.remove(particle)
    
    def render(self, surface, camera_x=0, camera_y=0):
        """Renderiza a nave proceduralmente"""
        # Posição na tela
        screen_x = int(self.x - camera_x)
        screen_y = int(self.y - camera_y)
        
        # Renderiza partículas de propulsão
        for particle in self.thrust_particles:
            alpha = particle['life'] / particle['max_life']
            color = (
                int(particle['color'][0] * alpha),
                int(particle['color'][1] * alpha),
                int(particle['color'][2] * alpha)
            )
            
            pygame.draw.circle(
                surface, color,
                (int(particle['x'] - camera_x), int(particle['y'] - camera_y)),
                2
            )
        
        # Corpo principal da nave (triângulo)
        points = self.get_ship_points(screen_x, screen_y)
        pygame.draw.polygon(surface, CYAN, points)
        
        # Borda da nave
        pygame.draw.polygon(surface, WHITE, points, 2)
        
        # Detalhes da nave
        self.render_ship_details(surface, screen_x, screen_y)
        
        # Escudo (se ativo)
        if self.health < self.max_health:
            shield_alpha = max(0, (self.health / self.max_health) * 255)
            shield_color = (0, 255, 255, int(shield_alpha))
            shield_surface = pygame.Surface((self.size + 10, self.size + 10), pygame.SRCALPHA)
            pygame.draw.circle(shield_surface, shield_color, (self.size//2 + 5, self.size//2 + 5), self.size//2 + 5, 3)
            surface.blit(shield_surface, (screen_x - self.size//2 - 5, screen_y - self.size//2 - 5))
    
    def get_ship_points(self, x, y):
        """Retorna pontos do triângulo da nave"""
        # Pontos do triângulo (apontando para a direção do movimento)
        front_x = x + math.cos(self.angle) * self.size
        front_y = y + math.sin(self.angle) * self.size
        
        back_left_x = x + math.cos(self.angle + math.pi * 2/3) * self.size * 0.5
        back_left_y = y + math.sin(self.angle + math.pi * 2/3) * self.size * 0.5
        
        back_right_x = x + math.cos(self.angle - math.pi * 2/3) * self.size * 0.5
        back_right_y = y + math.sin(self.angle - math.pi * 2/3) * self.size * 0.5
        
        return [(front_x, front_y), (back_left_x, back_left_y), (back_right_x, back_right_y)]
    
    def render_ship_details(self, surface, x, y):
        """Renderiza detalhes da nave"""
        # Cockpit
        cockpit_x = x + math.cos(self.angle) * self.size * 0.3
        cockpit_y = y + math.sin(self.angle) * self.size * 0.3
        pygame.draw.circle(surface, BLUE, (int(cockpit_x), int(cockpit_y)), 3)
        
        # Asas
        wing_left_x = x + math.cos(self.angle + math.pi/2) * self.size * 0.4
        wing_left_y = y + math.sin(self.angle + math.pi/2) * self.size * 0.4
        wing_right_x = x + math.cos(self.angle - math.pi/2) * self.size * 0.4
        wing_right_y = y + math.sin(self.angle - math.pi/2) * self.size * 0.4
        
        pygame.draw.line(surface, WHITE, (x, y), (int(wing_left_x), int(wing_left_y)), 2)
        pygame.draw.line(surface, WHITE, (x, y), (int(wing_right_x), int(wing_right_y)), 2)
    
    def shoot(self):
        """Dispara um projétil"""
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot_time > LASER_COOLDOWN and self.energy > 10:
            self.last_shot_time = current_time
            self.consume_energy(10)
            return True
        return False
    
    def mine(self, blocks):
        """Minera blocos próximos"""
        current_time = pygame.time.get_ticks()
        if current_time - self.last_mine_time > self.mine_cooldown and self.energy > 5:
            self.last_mine_time = current_time
            self.consume_energy(5)
            
            # Procura blocos no alcance
            for block in blocks:
                distance = math.sqrt((self.x - block.x)**2 + (self.y - block.y)**2)
                if distance <= self.mine_range and not block.collected:
                    # Aplica dano ao bloco
                    if block.take_damage(self.mine_damage):
                        # Bloco destruído, coleta recursos
                        resource_value = block.collect()
                        if resource_value > 0:
                            # Adiciona ao inventário
                            self.inventory.add_item(block.block_type, resource_value)
                            return resource_value
            return 0
        return 0
    
    def build(self, blocks, mouse_x, mouse_y):
        """Constrói um bloco na posição do mouse"""
        current_time = pygame.time.get_ticks()
        if current_time - self.last_build_time > self.build_cooldown:
            # Verifica se tem recursos para construir
            if self.inventory.has_item(self.selected_block_type, 1):
                # Calcula posição de construção
                build_x = mouse_x
                build_y = mouse_y
                
                # Verifica se está no alcance
                distance = math.sqrt((self.x - build_x)**2 + (self.y - build_y)**2)
                if distance <= self.build_range:
                    # Verifica se não há bloco na posição
                    for block in blocks:
                        if abs(block.x - build_x) < BLOCK_SIZE and abs(block.y - build_y) < BLOCK_SIZE:
                            return False  # Posição ocupada
                    
                    # Remove recursos do inventário
                    self.inventory.remove_item(self.selected_block_type, 1)
                    
                    # Cria novo bloco
                    from systems.generation import Block
                    new_block = Block(build_x, build_y, self.selected_block_type)
                    blocks.append(new_block)
                    
                    self.last_build_time = current_time
                    return True
        
        return False
    
    def select_block_type(self, block_type):
        """Seleciona tipo de bloco para construção"""
        if block_type in ['IRON', 'GOLD', 'CRYSTAL', 'FUEL', 'OXYGEN']:
            self.selected_block_type = block_type
    
    def take_damage(self, damage):
        """Recebe dano"""
        self.health = max(0, self.health - damage)
    
    def heal(self, amount):
        """Cura a nave"""
        self.health = min(self.max_health, self.health + amount)
    
    def consume_energy(self, amount):
        """Consome energia"""
        self.energy = max(0, self.energy - amount)
    
    def regenerate_energy(self, amount):
        """Regenera energia"""
        self.energy = min(self.max_energy, self.energy + amount)
    
    def consume_oxygen(self, amount):
        """Consome oxigênio"""
        self.oxygen = max(0, self.oxygen - amount)
    
    def add_oxygen(self, amount):
        """Adiciona oxigênio"""
        self.oxygen = min(self.max_oxygen, self.oxygen + amount)
    
    def consume_fuel(self, amount):
        """Consome combustível"""
        self.fuel = max(0, self.fuel - amount)
    
    def add_fuel(self, amount):
        """Adiciona combustível"""
        self.fuel = min(self.max_fuel, self.fuel + amount)
    
    def collides_with(self, entity):
        """Verifica colisão com outra entidade"""
        distance = math.sqrt((self.x - entity.x)**2 + (self.y - entity.y)**2)
        return distance < (self.size + entity.size) / 2
    
    def get_position(self):
        """Retorna posição da nave"""
        return self.x, self.y
    
    def get_velocity(self):
        """Retorna velocidade da nave"""
        return self.vx, self.vy
    
    def is_alive(self):
        """Verifica se a nave está viva"""
        return self.health > 0
