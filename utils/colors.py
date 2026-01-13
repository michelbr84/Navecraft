"""
Sistema de geração procedural de cores do Navecraft
"""

import random
import math
from settings import *

class ColorGenerator:
    def __init__(self):
        """Inicializa o gerador de cores"""
        self.color_palettes = self.generate_color_palettes()
        
    def generate_color_palettes(self):
        """Gera paletas de cores proceduralmente"""
        palettes = {
            'space': self.generate_space_palette(),
            'planets': self.generate_planet_palettes(),
            'spaceship': self.generate_spaceship_palette(),
            'effects': self.generate_effect_palettes(),
            'ui': self.generate_ui_palette()
        }
        return palettes
    
    def generate_space_palette(self):
        """Gera paleta de cores espaciais"""
        return {
            'background': SPACE_BLUE,
            'stars': [(255, 255, 255), (255, 215, 0), (135, 206, 235)],
            'nebula': [(138, 43, 226), (255, 20, 147), (0, 255, 255)],
            'dust': [(128, 128, 128), (64, 64, 64), (192, 192, 192)]
        }
    
    def generate_planet_palettes(self):
        """Gera paletas de cores para planetas"""
        return {
            'ROCK': {
                'primary': PLANET_RED,
                'secondary': (139, 69, 19),
                'accent': (255, 140, 0),
                'surface': [(139, 69, 19), (160, 82, 45), (205, 133, 63)]
            },
            'ICE': {
                'primary': (240, 248, 255),
                'secondary': (176, 196, 222),
                'accent': (135, 206, 235),
                'surface': [(240, 248, 255), (176, 196, 222), (135, 206, 235)]
            },
            'GAS': {
                'primary': (255, 165, 0),
                'secondary': (255, 69, 0),
                'accent': (255, 215, 0),
                'surface': [(255, 165, 0), (255, 69, 0), (255, 215, 0)]
            },
            'METAL': {
                'primary': (192, 192, 192),
                'secondary': (128, 128, 128),
                'accent': (255, 215, 0),
                'surface': [(192, 192, 192), (128, 128, 128), (105, 105, 105)]
            },
            'CRYSTAL': {
                'primary': (138, 43, 226),
                'secondary': (75, 0, 130),
                'accent': (255, 20, 147),
                'surface': [(138, 43, 226), (75, 0, 130), (148, 0, 211)]
            }
        }
    
    def generate_spaceship_palette(self):
        """Gera paleta de cores para a nave"""
        return {
            'primary': CYAN,
            'secondary': (0, 200, 200),
            'accent': BLUE,
            'thrust': (255, 165, 0),
            'shield': (0, 255, 255),
            'damage': RED
        }
    
    def generate_effect_palettes(self):
        """Gera paletas de cores para efeitos"""
        return {
            'explosion': [(255, 0, 0), (255, 165, 0), (255, 255, 0)],
            'laser': [(255, 0, 0), (255, 100, 100), (255, 200, 200)],
            'thrust': [(255, 165, 0), (255, 200, 100), (255, 255, 200)],
            'collect': [(0, 255, 0), (100, 255, 100), (200, 255, 200)]
        }
    
    def generate_ui_palette(self):
        """Gera paleta de cores para interface"""
        return {
            'background': DARK_GRAY,
            'foreground': WHITE,
            'accent': CYAN,
            'health': [GREEN, YELLOW, RED],
            'energy': [BLUE, CYAN],
            'oxygen': [CYAN, RED]
        }
    
    def get_random_color_from_palette(self, palette_name, color_type='primary'):
        """Obtém cor aleatória de uma paleta"""
        if palette_name in self.color_palettes:
            palette = self.color_palettes[palette_name]
            if color_type in palette:
                if isinstance(palette[color_type], list):
                    return random.choice(palette[color_type])
                else:
                    return palette[color_type]
        return WHITE
    
    def interpolate_color(self, color1, color2, alpha):
        """Interpola entre duas cores"""
        return (
            int(color1[0] * (1 - alpha) + color2[0] * alpha),
            int(color1[1] * (1 - alpha) + color2[1] * alpha),
            int(color1[2] * (1 - alpha) + color2[2] * alpha)
        )
    
    def generate_gradient(self, color1, color2, steps):
        """Gera gradiente entre duas cores"""
        gradient = []
        for i in range(steps):
            alpha = i / (steps - 1)
            gradient.append(self.interpolate_color(color1, color2, alpha))
        return gradient
    
    def generate_noise_color(self, x, y, base_color, variation=0.3):
        """Gera cor com ruído procedural"""
        # Usa coordenadas para gerar ruído
        noise = (math.sin(x * 0.1) + math.cos(y * 0.1)) * 0.5 + 0.5
        
        # Aplica variação
        variation_amount = variation * noise
        
        return (
            max(0, min(255, int(base_color[0] * (1 + variation_amount)))),
            max(0, min(255, int(base_color[1] * (1 + variation_amount)))),
            max(0, min(255, int(base_color[2] * (1 + variation_amount))))
        )
    
    def generate_planet_color(self, planet_type, x, y):
        """Gera cor procedural para planeta"""
        palette = self.color_palettes['planets'].get(planet_type, self.color_palettes['planets']['ROCK'])
        base_color = palette['primary']
        
        # Adiciona variação baseada na posição
        return self.generate_noise_color(x, y, base_color, 0.2)
    
    def generate_spaceship_color(self, health_percentage):
        """Gera cor da nave baseada na saúde"""
        if health_percentage > 0.7:
            return self.color_palettes['spaceship']['primary']
        elif health_percentage > 0.3:
            return self.color_palettes['spaceship']['secondary']
        else:
            return self.color_palettes['spaceship']['damage']
    
    def generate_effect_color(self, effect_type, intensity=1.0):
        """Gera cor para efeitos"""
        palette = self.color_palettes['effects'].get(effect_type, self.color_palettes['effects']['laser'])
        
        if isinstance(palette, list):
            base_color = random.choice(palette)
        else:
            base_color = palette
        
        # Aplica intensidade
        return (
            int(base_color[0] * intensity),
            int(base_color[1] * intensity),
            int(base_color[2] * intensity)
        )
    
    def generate_ui_color(self, ui_type, value_percentage=1.0):
        """Gera cor para interface baseada em valor"""
        palette = self.color_palettes['ui']
        
        if ui_type == 'health':
            if value_percentage > 0.6:
                return palette['health'][0]  # Verde
            elif value_percentage > 0.3:
                return palette['health'][1]  # Amarelo
            else:
                return palette['health'][2]  # Vermelho
        elif ui_type == 'energy':
            return self.interpolate_color(palette['energy'][0], palette['energy'][1], value_percentage)
        elif ui_type == 'oxygen':
            if value_percentage > 0.5:
                return palette['oxygen'][0]  # Ciano
            else:
                return palette['oxygen'][1]  # Vermelho
        else:
            return palette['foreground']
    
    def generate_star_color(self, brightness, temperature=1.0):
        """Gera cor de estrela baseada em temperatura e brilho"""
        # Temperatura afeta a cor (azul = quente, vermelho = frio)
        if temperature > 0.8:
            # Estrela azul/quente
            base_color = (100, 150, 255)
        elif temperature > 0.5:
            # Estrela amarela
            base_color = (255, 255, 100)
        else:
            # Estrela vermelha/fria
            base_color = (255, 100, 100)
        
        # Aplica brilho
        return (
            int(base_color[0] * brightness),
            int(base_color[1] * brightness),
            int(base_color[2] * brightness)
        )
    
    def generate_nebula_color(self, x, y):
        """Gera cor de nebulosa procedural"""
        # Usa funções trigonométricas para criar padrões
        r = int(128 + 127 * math.sin(x * 0.01) * math.cos(y * 0.01))
        g = int(128 + 127 * math.sin(x * 0.015) * math.cos(y * 0.02))
        b = int(128 + 127 * math.sin(x * 0.02) * math.cos(y * 0.015))
        
        return (r, g, b)
