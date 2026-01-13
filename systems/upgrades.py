"""
Sistema de upgrades da nave espacial
"""

import pygame
from settings import *

class UpgradeSystem:
    def __init__(self, spaceship):
        """Inicializa o sistema de upgrades"""
        self.spaceship = spaceship
        self.upgrades = self.generate_upgrades()
        self.applied_upgrades = {}
        
    def generate_upgrades(self):
        """Gera lista de upgrades disponíveis"""
        return {
            'ENGINE_BOOST': {
                'name': 'Motor Aprimorado',
                'description': 'Aumenta velocidade máxima em 20%',
                'cost': {'IRON': 20, 'FUEL': 10},
                'max_level': 3,
                'effect': 'speed_boost'
            },
            'SHIELD_ENHANCEMENT': {
                'name': 'Escudo Reforçado',
                'description': 'Aumenta vida máxima em 25%',
                'cost': {'CRYSTAL': 15, 'GOLD': 10},
                'max_level': 3,
                'effect': 'health_boost'
            },
            'ENERGY_EFFICIENCY': {
                'name': 'Eficiência Energética',
                'description': 'Reduz consumo de energia em 30%',
                'cost': {'CRYSTAL': 20, 'GOLD': 5},
                'max_level': 2,
                'effect': 'energy_efficiency'
            },
            'MINING_LASER': {
                'name': 'Laser de Mineração',
                'description': 'Aumenta alcance e dano de mineração',
                'cost': {'CRYSTAL': 25, 'IRON': 15},
                'max_level': 3,
                'effect': 'mining_boost'
            },
            'OXYGEN_SYSTEM': {
                'name': 'Sistema de Oxigênio',
                'description': 'Reduz consumo de oxigênio em 40%',
                'cost': {'OXYGEN': 30, 'CRYSTAL': 10},
                'max_level': 2,
                'effect': 'oxygen_efficiency'
            },
            'FUEL_TANK': {
                'name': 'Tanque de Combustível',
                'description': 'Aumenta capacidade de combustível em 50%',
                'cost': {'FUEL': 40, 'IRON': 20},
                'max_level': 2,
                'effect': 'fuel_capacity'
            }
        }
    
    def can_afford_upgrade(self, upgrade_name):
        """Verifica se pode comprar um upgrade"""
        if upgrade_name not in self.upgrades:
            return False
        
        upgrade = self.upgrades[upgrade_name]
        current_level = self.applied_upgrades.get(upgrade_name, 0)
        
        if current_level >= upgrade['max_level']:
            return False
        
        cost = upgrade['cost']
        for item_type, quantity in cost.items():
            if not self.spaceship.inventory.has_item(item_type, quantity):
                return False
        
        return True
    
    def apply_upgrade(self, upgrade_name):
        """Aplica um upgrade à nave"""
        if not self.can_afford_upgrade(upgrade_name):
            return False
        
        upgrade = self.upgrades[upgrade_name]
        cost = upgrade['cost']
        
        # Remove recursos do inventário
        for item_type, quantity in cost.items():
            self.spaceship.inventory.remove_item(item_type, quantity)
        
        # Aplica o upgrade
        current_level = self.applied_upgrades.get(upgrade_name, 0)
        self.applied_upgrades[upgrade_name] = current_level + 1
        
        # Aplica efeitos
        self.apply_upgrade_effects(upgrade_name, current_level + 1)
        
        return True
    
    def apply_upgrade_effects(self, upgrade_name, level):
        """Aplica os efeitos de um upgrade"""
        if upgrade_name == 'ENGINE_BOOST':
            # Aumenta velocidade máxima
            speed_boost = 1.0 + (level * 0.2)  # 20% por nível
            self.spaceship.max_speed = MAX_VELOCITY * speed_boost
        
        elif upgrade_name == 'SHIELD_ENHANCEMENT':
            # Aumenta vida máxima
            health_boost = 1.0 + (level * 0.25)  # 25% por nível
            self.spaceship.max_health = SPACESHIP_HEALTH * health_boost
            self.spaceship.health = min(self.spaceship.health, self.spaceship.max_health)
        
        elif upgrade_name == 'ENERGY_EFFICIENCY':
            # Reduz consumo de energia
            self.spaceship.energy_efficiency = 1.0 - (level * 0.15)  # 15% por nível
        
        elif upgrade_name == 'MINING_LASER':
            # Aumenta alcance e dano de mineração
            range_boost = 1.0 + (level * 0.3)  # 30% por nível
            damage_boost = 1.0 + (level * 0.2)  # 20% por nível
            self.spaceship.mine_range = int(50 * range_boost)
            self.spaceship.mine_damage = int(25 * damage_boost)
        
        elif upgrade_name == 'OXYGEN_SYSTEM':
            # Reduz consumo de oxigênio
            self.spaceship.oxygen_efficiency = 1.0 - (level * 0.2)  # 20% por nível
        
        elif upgrade_name == 'FUEL_TANK':
            # Aumenta capacidade de combustível
            fuel_boost = 1.0 + (level * 0.5)  # 50% por nível
            self.spaceship.max_fuel = int(100 * fuel_boost)
    
    def get_upgrade_info(self, upgrade_name):
        """Retorna informações de um upgrade"""
        if upgrade_name not in self.upgrades:
            return None
        
        upgrade = self.upgrades[upgrade_name]
        current_level = self.applied_upgrades.get(upgrade_name, 0)
        
        return {
            'name': upgrade['name'],
            'description': upgrade['description'],
            'cost': upgrade['cost'],
            'current_level': current_level,
            'max_level': upgrade['max_level'],
            'can_afford': self.can_afford_upgrade(upgrade_name)
        }
    
    def get_available_upgrades(self):
        """Retorna upgrades disponíveis"""
        available = []
        for upgrade_name in self.upgrades:
            info = self.get_upgrade_info(upgrade_name)
            if info:
                available.append(info)
        return available
    
    def render_upgrades(self, surface, x, y):
        """Renderiza interface de upgrades"""
        font = pygame.font.Font(None, 24)
        small_font = pygame.font.Font(None, 18)
        
        # Título
        title = font.render("UPGRADES", True, WHITE)
        surface.blit(title, (x, y))
        
        y += 40
        
        # Lista de upgrades
        for upgrade_name, upgrade in self.upgrades.items():
            info = self.get_upgrade_info(upgrade_name)
            if not info:
                continue
            
            # Nome do upgrade
            name_text = small_font.render(f"{info['name']} (Nível {info['current_level']}/{info['max_level']})", True, WHITE)
            surface.blit(name_text, (x, y))
            
            # Descrição
            desc_text = small_font.render(info['description'], True, LIGHT_GRAY)
            surface.blit(desc_text, (x, y + 20))
            
            # Custo
            cost_text = "Custo: "
            for item_type, quantity in info['cost'].items():
                cost_text += f"{quantity} {item_type} "
            
            cost_color = GREEN if info['can_afford'] else RED
            cost_render = small_font.render(cost_text, True, cost_color)
            surface.blit(cost_render, (x, y + 40))
            
            y += 70
