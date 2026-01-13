"""
Sistema de inventário do Navecraft
"""

import pygame
from settings import *

class Inventory:
    def __init__(self):
        """Inicializa o inventário"""
        self.slots = INVENTORY_SLOTS
        self.items = {}  # {item_type: quantity}
        self.max_stack = 999
        
        # Inicializa com alguns recursos básicos
        self.add_item('FUEL', 50)
        self.add_item('OXYGEN', 100)
    
    def add_item(self, item_type, quantity):
        """Adiciona item ao inventário"""
        if item_type in self.items:
            self.items[item_type] = min(self.max_stack, self.items[item_type] + quantity)
        else:
            self.items[item_type] = min(self.max_stack, quantity)
        
        return self.items[item_type]
    
    def remove_item(self, item_type, quantity):
        """Remove item do inventário"""
        if item_type in self.items:
            if self.items[item_type] >= quantity:
                self.items[item_type] -= quantity
                if self.items[item_type] <= 0:
                    del self.items[item_type]
                return True
        return False
    
    def get_item_count(self, item_type):
        """Retorna quantidade de um item"""
        return self.items.get(item_type, 0)
    
    def has_item(self, item_type, quantity=1):
        """Verifica se tem quantidade suficiente de um item"""
        return self.get_item_count(item_type) >= quantity
    
    def get_total_items(self):
        """Retorna total de itens no inventário"""
        return sum(self.items.values())
    
    def is_full(self):
        """Verifica se o inventário está cheio"""
        return self.get_total_items() >= self.slots * self.max_stack
    
    def get_inventory_space(self):
        """Retorna espaço disponível no inventário"""
        return (self.slots * self.max_stack) - self.get_total_items()
    
    def render(self, surface, x, y):
        """Renderiza o inventário"""
        # Fundo do inventário
        inventory_width = self.slots * SLOT_SIZE + 20
        inventory_height = SLOT_SIZE + 20
        
        # Desenha fundo
        pygame.draw.rect(surface, DARK_GRAY, (x, y, inventory_width, inventory_height))
        pygame.draw.rect(surface, WHITE, (x, y, inventory_width, inventory_height), 2)
        
        # Renderiza slots
        for i in range(self.slots):
            slot_x = x + 10 + i * SLOT_SIZE
            slot_y = y + 10
            
            # Fundo do slot
            pygame.draw.rect(surface, GRAY, (slot_x, slot_y, SLOT_SIZE, SLOT_SIZE))
            pygame.draw.rect(surface, WHITE, (slot_x, slot_y, SLOT_SIZE, SLOT_SIZE), 1)
            
            # Se há item neste slot
            if i < len(list(self.items.keys())):
                item_type = list(self.items.keys())[i]
                quantity = self.items[item_type]
                
                # Cor do item
                colors = {
                    'IRON': (169, 169, 169),
                    'GOLD': (255, 215, 0),
                    'CRYSTAL': (138, 43, 226),
                    'FUEL': (255, 165, 0),
                    'OXYGEN': (135, 206, 235)
                }
                
                color = colors.get(item_type, WHITE)
                
                # Desenha item
                item_size = SLOT_SIZE - 4
                pygame.draw.rect(surface, color, (slot_x + 2, slot_y + 2, item_size, item_size))
                
                # Quantidade
                font = pygame.font.Font(None, 16)
                quantity_text = font.render(str(quantity), True, WHITE)
                text_rect = quantity_text.get_rect()
                text_rect.bottomright = (slot_x + SLOT_SIZE - 2, slot_y + SLOT_SIZE - 2)
                surface.blit(quantity_text, text_rect)
    
    def render_quick_inventory(self, surface, x, y):
        """Renderiza inventário rápido (HUD)"""
        # Mostra apenas os 5 itens mais importantes
        important_items = ['FUEL', 'OXYGEN', 'CRYSTAL', 'GOLD', 'IRON']
        
        for i, item_type in enumerate(important_items):
            if item_type in self.items:
                slot_x = x + i * (SLOT_SIZE + 5)
                slot_y = y
                
                # Fundo do slot
                pygame.draw.rect(surface, DARK_GRAY, (slot_x, slot_y, SLOT_SIZE, SLOT_SIZE))
                pygame.draw.rect(surface, WHITE, (slot_x, slot_y, SLOT_SIZE, SLOT_SIZE), 1)
                
                # Cor do item
                colors = {
                    'IRON': (169, 169, 169),
                    'GOLD': (255, 215, 0),
                    'CRYSTAL': (138, 43, 226),
                    'FUEL': (255, 165, 0),
                    'OXYGEN': (135, 206, 235)
                }
                
                color = colors.get(item_type, WHITE)
                
                # Desenha item
                item_size = SLOT_SIZE - 4
                pygame.draw.rect(surface, color, (slot_x + 2, slot_y + 2, item_size, item_size))
                
                # Quantidade
                font = pygame.font.Font(None, 14)
                quantity_text = font.render(str(self.items[item_type]), True, WHITE)
                text_rect = quantity_text.get_rect()
                text_rect.bottomright = (slot_x + SLOT_SIZE - 2, slot_y + SLOT_SIZE - 2)
                surface.blit(quantity_text, text_rect)

class CraftingSystem:
    def __init__(self, inventory):
        """Inicializa sistema de crafting"""
        self.inventory = inventory
        self.recipes = self.generate_recipes()
    
    def generate_recipes(self):
        """Gera receitas de crafting"""
        return {
            'REPAIR_KIT': {
                'IRON': 10,
                'FUEL': 5
            },
            'ENERGY_PACK': {
                'CRYSTAL': 5,
                'FUEL': 10
            },
            'OXYGEN_TANK': {
                'OXYGEN': 20,
                'IRON': 5
            },
            'SHIELD_BOOSTER': {
                'CRYSTAL': 10,
                'GOLD': 5
            }
        }
    
    def can_craft(self, recipe_name):
        """Verifica se pode craftar um item"""
        if recipe_name not in self.recipes:
            return False
        
        recipe = self.recipes[recipe_name]
        for item_type, quantity in recipe.items():
            if not self.inventory.has_item(item_type, quantity):
                return False
        
        return True
    
    def craft_item(self, recipe_name):
        """Crafta um item"""
        if not self.can_craft(recipe_name):
            return False
        
        recipe = self.recipes[recipe_name]
        
        # Remove ingredientes
        for item_type, quantity in recipe.items():
            self.inventory.remove_item(item_type, quantity)
        
        # Adiciona item craftado
        self.inventory.add_item(recipe_name, 1)
        
        return True
    
    def get_available_recipes(self):
        """Retorna receitas disponíveis"""
        available = []
        for recipe_name in self.recipes:
            if self.can_craft(recipe_name):
                available.append(recipe_name)
        return available
