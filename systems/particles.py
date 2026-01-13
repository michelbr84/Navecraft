"""
Sistema de partículas do Navecraft
"""

import pygame
import random
import math
from settings import *

class Particle:
    def __init__(self, x, y, vx, vy, color, lifetime, size=2):
        """Inicializa uma partícula"""
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.size = size
        self.alpha = 255
    
    def update(self):
        """Atualiza a partícula"""
        self.x += self.vx
        self.y += self.vy
        self.lifetime -= 1
        
        # Atualiza alpha baseado na vida
        self.alpha = int((self.lifetime / self.max_lifetime) * 255)
        
        # Aplica gravidade
        self.vy += 0.1
        
        # Aplica atrito
        self.vx *= 0.98
        self.vy *= 0.98
    
    def should_remove(self):
        """Verifica se a partícula deve ser removida"""
        return self.lifetime <= 0
    
    def render(self, surface, camera_x, camera_y):
        """Renderiza a partícula"""
        screen_x = int(self.x - camera_x)
        screen_y = int(self.y - camera_y)
        
        # Cor com alpha
        color_with_alpha = (
            int(self.color[0] * self.alpha / 255),
            int(self.color[1] * self.alpha / 255),
            int(self.color[2] * self.alpha / 255)
        )
        
        pygame.draw.circle(surface, color_with_alpha, (screen_x, screen_y), self.size)

class ParticleSystem:
    def __init__(self):
        """Inicializa o sistema de partículas"""
        self.particles = []
    
    def add_particle(self, x, y, vx, vy, color, lifetime, size=2):
        """Adiciona uma partícula"""
        particle = Particle(x, y, vx, vy, color, lifetime, size)
        self.particles.append(particle)
    
    def create_explosion(self, x, y, color=(255, 100, 100)):
        """Cria efeito de explosão"""
        for _ in range(20):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(2, 8)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            lifetime = random.randint(30, 60)
            size = random.randint(1, 4)
            
            self.add_particle(x, y, vx, vy, color, lifetime, size)
    
    def create_collect_effect(self, x, y, color=(0, 255, 0)):
        """Cria efeito de coleta"""
        for _ in range(10):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(1, 4)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed - 2  # Movimento para cima
            lifetime = random.randint(20, 40)
            size = random.randint(1, 3)
            
            self.add_particle(x, y, vx, vy, color, lifetime, size)
    
    def create_thrust_effect(self, x, y, angle):
        """Cria efeito de propulsão"""
        for _ in range(5):
            # Partículas na direção oposta ao movimento
            thrust_angle = angle + math.pi + random.uniform(-0.3, 0.3)
            speed = random.uniform(3, 7)
            vx = math.cos(thrust_angle) * speed
            vy = math.sin(thrust_angle) * speed
            lifetime = random.randint(15, 30)
            size = random.randint(1, 3)
            
            # Cor laranja/amarela para propulsão
            color = (255, random.randint(150, 200), 0)
            
            self.add_particle(x, y, vx, vy, color, lifetime, size)
    
    def create_laser_effect(self, x, y, angle):
        """Cria efeito de laser"""
        for _ in range(8):
            # Partículas na direção do laser
            speed = random.uniform(5, 10)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            lifetime = random.randint(10, 20)
            size = random.randint(1, 2)
            
            # Cor vermelha/azul para laser
            color = (255, random.randint(0, 100), random.randint(0, 100))
            
            self.add_particle(x, y, vx, vy, color, lifetime, size)
    
    def create_damage_effect(self, x, y):
        """Cria efeito de dano"""
        for _ in range(15):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(1, 5)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            lifetime = random.randint(25, 45)
            size = random.randint(1, 3)
            
            # Cor vermelha para dano
            color = (255, random.randint(0, 50), random.randint(0, 50))
            
            self.add_particle(x, y, vx, vy, color, lifetime, size)
    
    def update(self):
        """Atualiza todas as partículas"""
        for particle in self.particles[:]:
            particle.update()
            if particle.should_remove():
                self.particles.remove(particle)
    
    def render(self, surface, camera_x, camera_y):
        """Renderiza todas as partículas"""
        for particle in self.particles:
            particle.render(surface, camera_x, camera_y)
    
    def clear(self):
        """Limpa todas as partículas"""
        self.particles.clear()
