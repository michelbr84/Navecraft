"""
Sistema de renderização procedural do Navecraft
"""

import pygame
import math
import random
from settings import *

class Renderer:
    def __init__(self):
        """Inicializa o renderer"""
        self.star_field = self.generate_star_field()
        self.particle_system = ParticleSystem()
        
    def generate_star_field(self):
        """Gera campo de estrelas procedural"""
        stars = []
        random.seed(SEED)
        
        for i in range(300):
            x = random.randint(0, SCREEN_WIDTH)
            y = random.randint(0, SCREEN_HEIGHT)
            brightness = random.randint(50, 255)
            size = random.randint(1, 3)
            
            stars.append({
                'x': x,
                'y': y,
                'brightness': brightness,
                'size': size,
                'twinkle': random.uniform(0, math.pi * 2)
            })
        
        return stars
    
    def render_stars(self, surface):
        """Renderiza campo de estrelas"""
        for star in self.star_field:
            # Aplica movimento parallax
            screen_x = (star['x'] - 0 * 0.1) % SCREEN_WIDTH
            screen_y = (star['y'] - 0 * 0.1) % SCREEN_HEIGHT
            
            # Efeito de twinkle
            twinkle = math.sin(star['twinkle']) * 0.3 + 0.7
            brightness = int(star['brightness'] * twinkle)
            
            color = (brightness, brightness, brightness)
            pygame.draw.circle(surface, color, (int(screen_x), int(screen_y)), star['size'])
            
            # Atualiza twinkle
            star['twinkle'] += 0.02
    
    def render_spaceship(self, surface, spaceship, camera_x, camera_y):
        """Renderiza nave espacial proceduralmente"""
        if not spaceship:
            return
            
        screen_x = int(spaceship.x - camera_x)
        screen_y = int(spaceship.y - camera_y)
        
        # Renderiza partículas de propulsão
        self.render_thrust_particles(surface, spaceship, camera_x, camera_y)
        
        # Corpo principal da nave
        self.render_ship_body(surface, spaceship, screen_x, screen_y)
        
        # Detalhes da nave
        self.render_ship_details(surface, spaceship, screen_x, screen_y)
        
        # Escudo
        self.render_shield(surface, spaceship, screen_x, screen_y)
    
    def render_thrust_particles(self, surface, spaceship, camera_x, camera_y):
        """Renderiza partículas de propulsão"""
        for particle in spaceship.thrust_particles:
            alpha = particle['life'] / particle['max_life']
            
            # Cor com fade
            color = (
                int(particle['color'][0] * alpha),
                int(particle['color'][1] * alpha),
                int(particle['color'][2] * alpha)
            )
            
            screen_x = int(particle['x'] - camera_x)
            screen_y = int(particle['y'] - camera_y)
            
            # Partícula principal
            pygame.draw.circle(surface, color, (screen_x, screen_y), 2)
            
            # Efeito de brilho
            glow_color = (255, 200, 100)
            pygame.draw.circle(surface, glow_color, (screen_x, screen_y), 4, 1)
    
    def render_ship_body(self, surface, spaceship, x, y):
        """Renderiza corpo principal da nave"""
        # Pontos do triângulo
        points = self.get_ship_points(spaceship, x, y)
        
        # Gradiente de cor
        color1 = CYAN
        color2 = (0, 200, 200)
        
        # Desenha gradiente
        for i in range(3):
            alpha = i / 2.0
            color = self.interpolate_color(color1, color2, alpha)
            pygame.draw.polygon(surface, color, points)
        
        # Borda
        pygame.draw.polygon(surface, WHITE, points, 2)
    
    def render_ship_details(self, surface, spaceship, x, y):
        """Renderiza detalhes da nave"""
        # Cockpit
        cockpit_x = x + math.cos(spaceship.angle) * spaceship.size * 0.3
        cockpit_y = y + math.sin(spaceship.angle) * spaceship.size * 0.3
        
        # Cockpit com gradiente
        pygame.draw.circle(surface, BLUE, (int(cockpit_x), int(cockpit_y)), 4)
        pygame.draw.circle(surface, (100, 100, 255), (int(cockpit_x), int(cockpit_y)), 2)
        
        # Asas
        wing_left_x = x + math.cos(spaceship.angle + math.pi/2) * spaceship.size * 0.4
        wing_left_y = y + math.sin(spaceship.angle + math.pi/2) * spaceship.size * 0.4
        wing_right_x = x + math.cos(spaceship.angle - math.pi/2) * spaceship.size * 0.4
        wing_right_y = y + math.sin(spaceship.angle - math.pi/2) * spaceship.size * 0.4
        
        # Asas com gradiente
        wing_color1 = WHITE
        wing_color2 = LIGHT_GRAY
        
        # Asa esquerda
        wing_points_left = [(x, y), (int(wing_left_x), int(wing_left_y))]
        pygame.draw.line(surface, wing_color1, wing_points_left[0], wing_points_left[1], 3)
        pygame.draw.line(surface, wing_color2, wing_points_left[0], wing_points_left[1], 1)
        
        # Asa direita
        wing_points_right = [(x, y), (int(wing_right_x), int(wing_right_y))]
        pygame.draw.line(surface, wing_color1, wing_points_right[0], wing_points_right[1], 3)
        pygame.draw.line(surface, wing_color2, wing_points_right[0], wing_points_right[1], 1)
    
    def render_shield(self, surface, spaceship, x, y):
        """Renderiza escudo da nave"""
        if spaceship.health < spaceship.max_health:
            shield_alpha = max(0, (spaceship.health / spaceship.max_health) * 255)
            
            # Cria superfície com transparência
            shield_surface = pygame.Surface((spaceship.size + 20, spaceship.size + 20), pygame.SRCALPHA)
            
            # Cor do escudo
            shield_color = (0, 255, 255, int(shield_alpha))
            
            # Desenha escudo
            pygame.draw.circle(shield_surface, shield_color, 
                             (spaceship.size//2 + 10, spaceship.size//2 + 10), 
                             spaceship.size//2 + 10, 3)
            
            # Aplica na tela
            surface.blit(shield_surface, (x - spaceship.size//2 - 10, y - spaceship.size//2 - 10))
    
    def get_ship_points(self, spaceship, x, y):
        """Retorna pontos do triângulo da nave"""
        # Pontos do triângulo (apontando para a direção do movimento)
        front_x = x + math.cos(spaceship.angle) * spaceship.size
        front_y = y + math.sin(spaceship.angle) * spaceship.size
        
        back_left_x = x + math.cos(spaceship.angle + math.pi * 2/3) * spaceship.size * 0.5
        back_left_y = y + math.sin(spaceship.angle + math.pi * 2/3) * spaceship.size * 0.5
        
        back_right_x = x + math.cos(spaceship.angle - math.pi * 2/3) * spaceship.size * 0.5
        back_right_y = y + math.sin(spaceship.angle - math.pi * 2/3) * spaceship.size * 0.5
        
        return [(front_x, front_y), (back_left_x, back_left_y), (back_right_x, back_right_y)]
    
    def interpolate_color(self, color1, color2, alpha):
        """Interpola entre duas cores"""
        return (
            int(color1[0] * (1 - alpha) + color2[0] * alpha),
            int(color1[1] * (1 - alpha) + color2[1] * alpha),
            int(color1[2] * (1 - alpha) + color2[2] * alpha)
        )
    
    def render_planet(self, surface, planet, camera_x, camera_y):
        """Renderiza planeta proceduralmente"""
        screen_x = int(planet.x - camera_x)
        screen_y = int(planet.y - camera_y)
        
        # Cor baseada no tipo
        colors = {
            'ROCK': PLANET_RED,
            'ICE': (240, 248, 255),
            'GAS': (255, 165, 0),
            'METAL': (192, 192, 192),
            'CRYSTAL': (138, 43, 226)
        }
        
        base_color = colors.get(planet.planet_type, PLANET_RED)
        
        # Renderiza planeta com gradiente
        for i in range(planet.radius, 0, -2):
            alpha = i / planet.radius
            color = self.interpolate_color(base_color, BLACK, 1 - alpha)
            pygame.draw.circle(surface, color, (screen_x, screen_y), i)
        
        # Borda
        pygame.draw.circle(surface, WHITE, (screen_x, screen_y), planet.radius, 2)
        
        # Detalhes da superfície
        self.render_planet_surface(surface, planet, screen_x, screen_y)
    
    def render_planet_surface(self, surface, planet, x, y):
        """Renderiza detalhes da superfície do planeta"""
        random.seed(planet.x + planet.y)  # Seed baseada na posição
        
        # Cria detalhes na superfície
        for _ in range(20):
            angle = random.uniform(0, math.pi * 2)
            distance = random.uniform(0, planet.radius * 0.8)
            
            detail_x = x + math.cos(angle) * distance
            detail_y = y + math.sin(angle) * distance
            
            # Cor do detalhe
            detail_color = self.interpolate_color(WHITE, BLACK, random.uniform(0, 0.5))
            
            # Desenha detalhe
            pygame.draw.circle(surface, detail_color, (int(detail_x), int(detail_y)), 1)

class ParticleSystem:
    def __init__(self):
        """Inicializa sistema de partículas"""
        self.particles = []
    
    def add_particle(self, x, y, vx, vy, color, lifetime):
        """Adiciona partícula ao sistema"""
        self.particles.append({
            'x': x, 'y': y, 'vx': vx, 'vy': vy,
            'color': color, 'lifetime': lifetime, 'max_lifetime': lifetime
        })
    
    def update(self):
        """Atualiza partículas"""
        for particle in self.particles[:]:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['lifetime'] -= 1
            
            if particle['lifetime'] <= 0:
                self.particles.remove(particle)
    
    def render(self, surface, camera_x, camera_y):
        """Renderiza partículas"""
        for particle in self.particles:
            alpha = particle['lifetime'] / particle['max_lifetime']
            color = (
                int(particle['color'][0] * alpha),
                int(particle['color'][1] * alpha),
                int(particle['color'][2] * alpha)
            )
            
            screen_x = int(particle['x'] - camera_x)
            screen_y = int(particle['y'] - camera_y)
            
            pygame.draw.circle(surface, color, (screen_x, screen_y), 2)
