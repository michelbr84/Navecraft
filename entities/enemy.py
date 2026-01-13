"""
Sistema de inimigos do Navecraft
"""

import pygame
import math
import random
from settings import *

class Enemy:
    def __init__(self, x, y, enemy_type):
        """Inicializa inimigo"""
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        self.enemy_type = enemy_type
        self.size = 24
        
        # Status
        self.health = ENEMY_HEALTH
        self.max_health = ENEMY_HEALTH
        self.damage = ENEMY_DAMAGE
        
        # IA
        self.state = "patrol"  # patrol, chase, attack, flee
        self.target = None
        self.last_attack_time = 0
        self.attack_cooldown = 1000  # milissegundos
        
        # Características baseadas no tipo
        self.setup_enemy_type()
    
    def setup_enemy_type(self):
        """Configura características baseadas no tipo"""
        if self.enemy_type == "DRONE":
            self.speed = ENEMY_SPEED * 1.5
            self.attack_range = 100
            self.detection_range = 150
            self.color = RED
        elif self.enemy_type == "ANDROID":
            self.speed = ENEMY_SPEED * 0.8
            self.attack_range = 80
            self.detection_range = 120
            self.color = MAGENTA
        elif self.enemy_type == "SNIPER":
            self.speed = ENEMY_SPEED * 0.6
            self.attack_range = 200
            self.detection_range = 250
            self.color = YELLOW
        elif self.enemy_type == "ARACHNOID":
            self.speed = ENEMY_SPEED * 1.2
            self.attack_range = 60
            self.detection_range = 100
            self.color = GREEN
        else:
            self.speed = ENEMY_SPEED
            self.attack_range = 80
            self.detection_range = 120
            self.color = RED
    
    def update(self, spaceship):
        """Atualiza IA do inimigo"""
        if not spaceship:
            return
        
        # Calcula distância até a nave
        dx = spaceship.x - self.x
        dy = spaceship.y - self.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        # Atualiza estado baseado na distância
        if distance <= self.attack_range:
            self.state = "attack"
        elif distance <= self.detection_range:
            self.state = "chase"
        else:
            self.state = "patrol"
        
        # Executa comportamento baseado no estado
        if self.state == "patrol":
            self.patrol_behavior()
        elif self.state == "chase":
            self.chase_behavior(spaceship)
        elif self.state == "attack":
            self.attack_behavior(spaceship)
    
    def patrol_behavior(self):
        """Comportamento de patrulha"""
        # Movimento aleatório
        if random.random() < 0.02:  # 2% de chance de mudar direção
            angle = random.uniform(0, math.pi * 2)
            self.vx = math.cos(angle) * self.speed * 0.5
            self.vy = math.sin(angle) * self.speed * 0.5
        
        # Aplica movimento
        self.x += self.vx
        self.y += self.vy
        
        # Limita velocidade
        speed = math.sqrt(self.vx**2 + self.vy**2)
        if speed > self.speed:
            self.vx = (self.vx / speed) * self.speed
            self.vy = (self.vy / speed) * self.speed
    
    def chase_behavior(self, spaceship):
        """Comportamento de perseguição"""
        # Move em direção à nave
        dx = spaceship.x - self.x
        dy = spaceship.y - self.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance > 0:
            # Normaliza direção
            dx /= distance
            dy /= distance
            
            # Aplica velocidade
            self.vx = dx * self.speed
            self.vy = dy * self.speed
        
        # Atualiza posição
        self.x += self.vx
        self.y += self.vy
    
    def attack_behavior(self, spaceship):
        """Comportamento de ataque"""
        current_time = pygame.time.get_ticks()
        
        if current_time - self.last_attack_time > self.attack_cooldown:
            self.last_attack_time = current_time
            
            # Diferentes tipos de ataque baseados no tipo de inimigo
            if self.enemy_type == "DRONE":
                # Ataque suicida
                self.suicide_attack(spaceship)
            elif self.enemy_type == "SNIPER":
                # Tiro de longa distância
                self.sniper_attack(spaceship)
            else:
                # Ataque normal
                self.normal_attack(spaceship)
    
    def suicide_attack(self, spaceship):
        """Ataque suicida do drone"""
        # Causa dano à nave
        spaceship.take_damage(self.damage * 2)
        # Destrói o inimigo
        self.health = 0
    
    def sniper_attack(self, spaceship):
        """Ataque de sniper"""
        # Tiro preciso
        spaceship.take_damage(self.damage)
    
    def normal_attack(self, spaceship):
        """Ataque normal"""
        # Dano de contato
        spaceship.take_damage(self.damage)
    
    def take_damage(self, damage):
        """Recebe dano"""
        self.health = max(0, self.health - damage)
        return self.health <= 0
    
    def render(self, surface, camera_x, camera_y):
        """Renderiza o inimigo"""
        screen_x = int(self.x - camera_x)
        screen_y = int(self.y - camera_y)
        
        # Renderiza baseado no tipo
        if self.enemy_type == "DRONE":
            self.render_drone(surface, screen_x, screen_y)
        elif self.enemy_type == "ANDROID":
            self.render_android(surface, screen_x, screen_y)
        elif self.enemy_type == "SNIPER":
            self.render_sniper(surface, screen_x, screen_y)
        elif self.enemy_type == "ARACHNOID":
            self.render_arachnoid(surface, screen_x, screen_y)
        else:
            self.render_generic(surface, screen_x, screen_y)
        
        # Barra de vida
        self.render_health_bar(surface, screen_x, screen_y)
    
    def render_drone(self, surface, x, y):
        """Renderiza drone"""
        # Corpo principal (círculo)
        pygame.draw.circle(surface, self.color, (x, y), self.size)
        pygame.draw.circle(surface, WHITE, (x, y), self.size, 2)
        
        # Propulsores
        pygame.draw.circle(surface, RED, (x - 8, y - 8), 3)
        pygame.draw.circle(surface, RED, (x + 8, y - 8), 3)
        pygame.draw.circle(surface, RED, (x - 8, y + 8), 3)
        pygame.draw.circle(surface, RED, (x + 8, y + 8), 3)
    
    def render_android(self, surface, x, y):
        """Renderiza androide"""
        # Corpo retangular
        rect = pygame.Rect(x - self.size//2, y - self.size//2, self.size, self.size)
        pygame.draw.rect(surface, self.color, rect)
        pygame.draw.rect(surface, WHITE, rect, 2)
        
        # Olhos
        pygame.draw.circle(surface, RED, (x - 5, y - 5), 2)
        pygame.draw.circle(surface, RED, (x + 5, y - 5), 2)
    
    def render_sniper(self, surface, x, y):
        """Renderiza sniper"""
        # Corpo triangular
        points = [
            (x, y - self.size),
            (x - self.size//2, y + self.size//2),
            (x + self.size//2, y + self.size//2)
        ]
        pygame.draw.polygon(surface, self.color, points)
        pygame.draw.polygon(surface, WHITE, points, 2)
        
        # Mira
        pygame.draw.circle(surface, RED, (x, y), 3)
    
    def render_arachnoid(self, surface, x, y):
        """Renderiza aracnoide"""
        # Corpo central
        pygame.draw.circle(surface, self.color, (x, y), self.size//2)
        pygame.draw.circle(surface, WHITE, (x, y), self.size//2, 2)
        
        # Pernas
        for i in range(8):
            angle = i * math.pi / 4
            leg_x = x + math.cos(angle) * self.size
            leg_y = y + math.sin(angle) * self.size
            pygame.draw.line(surface, self.color, (x, y), (leg_x, leg_y), 2)
    
    def render_generic(self, surface, x, y):
        """Renderiza inimigo genérico"""
        pygame.draw.circle(surface, self.color, (x, y), self.size)
        pygame.draw.circle(surface, WHITE, (x, y), self.size, 2)
    
    def render_health_bar(self, surface, x, y):
        """Renderiza barra de vida"""
        if self.health >= self.max_health:
            return
        
        bar_width = self.size * 2
        bar_height = 4
        bar_x = x - bar_width // 2
        bar_y = y - self.size - 10
        
        # Fundo
        pygame.draw.rect(surface, DARK_GRAY, (bar_x, bar_y, bar_width, bar_height))
        
        # Barra de vida
        health_percentage = self.health / self.max_health
        health_width = int(bar_width * health_percentage)
        
        if health_percentage > 0.6:
            color = GREEN
        elif health_percentage > 0.3:
            color = YELLOW
        else:
            color = RED
        
        pygame.draw.rect(surface, color, (bar_x, bar_y, health_width, bar_height))
        pygame.draw.rect(surface, WHITE, (bar_x, bar_y, bar_width, bar_height), 1)
    
    def collides_with(self, entity):
        """Verifica colisão com outra entidade"""
        distance = math.sqrt((self.x - entity.x)**2 + (self.y - entity.y)**2)
        return distance < (self.size + entity.size) / 2
    
    def is_alive(self):
        """Verifica se está vivo"""
        return self.health > 0
