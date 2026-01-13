"""
Sistema de física espacial do Navecraft
"""

import math
from settings import *

class PhysicsSystem:
    def __init__(self):
        """Inicializa o sistema de física"""
        self.gravity_wells = []
        self.force_fields = []
        
    def update(self, spaceship, planets, blocks):
        """Atualiza física do mundo"""
        if not spaceship:
            return
            
        # Aplica gravidade dos planetas
        self.apply_planet_gravity(spaceship, planets)
        
        # Aplica colisões com blocos
        self.check_block_collisions(spaceship, blocks)
        
        # Aplica atrito espacial
        self.apply_space_friction(spaceship)
        
        # Limita velocidade
        self.limit_velocity(spaceship)
    
    def apply_planet_gravity(self, spaceship, planets):
        """Aplica gravidade dos planetas na nave"""
        for planet in planets:
            # Calcula distância até o planeta
            dx = planet.x - spaceship.x
            dy = planet.y - spaceship.y
            distance = math.sqrt(dx*dx + dy*dy)
            
            # Se está muito longe, não aplica gravidade
            if distance > planet.radius * 3:
                continue
                
            # Calcula força gravitacional
            gravity_strength = GRAVITY * (planet.mass / (distance * distance))
            
            # Aplica força na direção do planeta
            if distance > 0:
                spaceship.vx += (dx / distance) * gravity_strength
                spaceship.vy += (dy / distance) * gravity_strength
    
    def check_block_collisions(self, spaceship, blocks):
        """Verifica colisões com blocos"""
        ship_rect = pygame.Rect(
            spaceship.x - spaceship.size//2,
            spaceship.y - spaceship.size//2,
            spaceship.size,
            spaceship.size
        )
        
        for block in blocks:
            # Calcula distância até o bloco
            dx = block.x - spaceship.x
            dy = block.y - spaceship.y
            distance = math.sqrt(dx*dx + dy*dy)
            
            # Se está muito longe, pula
            if distance > BLOCK_SIZE * 2:
                continue
                
            block_rect = pygame.Rect(
                block.x - BLOCK_SIZE//2,
                block.y - BLOCK_SIZE//2,
                BLOCK_SIZE,
                BLOCK_SIZE
            )
            
            if ship_rect.colliderect(block_rect):
                # Resolve colisão
                self.resolve_collision(spaceship, block)
    
    def resolve_collision(self, spaceship, block):
        """Resolve colisão entre nave e bloco"""
        # Calcula direção da colisão
        dx = spaceship.x - block.x
        dy = spaceship.y - block.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance == 0:
            return
            
        # Normaliza vetor de direção
        dx /= distance
        dy /= distance
        
        # Move a nave para fora do bloco
        min_distance = (spaceship.size + BLOCK_SIZE) / 2
        if distance < min_distance:
            spaceship.x = block.x + dx * min_distance
            spaceship.y = block.y + dy * min_distance
        
        # Aplica bounce (reflexão da velocidade)
        dot_product = spaceship.vx * dx + spaceship.vy * dy
        
        # Reflete velocidade
        spaceship.vx -= 2 * dot_product * dx
        spaceship.vy -= 2 * dot_product * dy
        
        # Reduz velocidade após colisão
        spaceship.vx *= 0.8
        spaceship.vy *= 0.8
    
    def apply_space_friction(self, spaceship):
        """Aplica atrito espacial"""
        # Atrito muito baixo no espaço
        spaceship.vx *= 0.999
        spaceship.vy *= 0.999
    
    def limit_velocity(self, spaceship):
        """Limita velocidade máxima"""
        speed = math.sqrt(spaceship.vx**2 + spaceship.vy**2)
        if speed > MAX_VELOCITY:
            spaceship.vx = (spaceship.vx / speed) * MAX_VELOCITY
            spaceship.vy = (spaceship.vy / speed) * MAX_VELOCITY
    
    def calculate_trajectory(self, start_x, start_y, vx, vy, steps=100):
        """Calcula trajetória de um projétil"""
        trajectory = []
        x, y = start_x, start_y
        
        for _ in range(steps):
            trajectory.append((x, y))
            
            # Aplica gravidade
            # (simplificado - apenas gravidade constante)
            vy += GRAVITY * 0.1
            
            # Atualiza posição
            x += vx
            y += vy
            
            # Verifica se saiu dos limites
            if x < 0 or x > WORLD_SIZE * BLOCK_SIZE or y < 0 or y > WORLD_SIZE * BLOCK_SIZE:
                break
        
        return trajectory
    
    def check_line_of_sight(self, start_x, start_y, end_x, end_y, blocks):
        """Verifica se há linha de visão entre dois pontos"""
        # Calcula vetor de direção
        dx = end_x - start_x
        dy = end_y - start_y
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance == 0:
            return True
            
        # Normaliza
        dx /= distance
        dy /= distance
        
        # Verifica cada ponto ao longo da linha
        for i in range(0, int(distance), BLOCK_SIZE//2):
            check_x = start_x + dx * i
            check_y = start_y + dy * i
            
            # Verifica se há bloco neste ponto
            for block in blocks:
                block_dx = check_x - block.x
                block_dy = check_y - block.y
                block_distance = math.sqrt(block_dx*block_dx + block_dy*block_dy)
                
                if block_distance < BLOCK_SIZE//2:
                    return False
        
        return True
    
    def apply_force_field(self, entity, force_x, force_y):
        """Aplica campo de força em uma entidade"""
        entity.vx += force_x
        entity.vy += force_y
    
    def calculate_orbital_velocity(self, distance, planet_mass):
        """Calcula velocidade orbital para uma distância"""
        # v = sqrt(GM/r)
        return math.sqrt(GRAVITY * planet_mass / distance)
    
    def is_in_orbit(self, spaceship, planet):
        """Verifica se a nave está em órbita do planeta"""
        dx = spaceship.x - planet.x
        dy = spaceship.y - planet.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        # Calcula velocidade orbital esperada
        orbital_velocity = self.calculate_orbital_velocity(distance, planet.mass)
        
        # Calcula velocidade atual
        current_velocity = math.sqrt(spaceship.vx**2 + spaceship.vy**2)
        
        # Se a velocidade está próxima da orbital, está em órbita
        return abs(current_velocity - orbital_velocity) < 1.0
