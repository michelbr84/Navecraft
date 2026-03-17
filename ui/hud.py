"""
Interface do usuário (HUD) do Navecraft
"""

import pygame
from settings import *

class HUD:
    def __init__(self):
        """Inicializa o HUD"""
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
        
    def update(self, spaceship):
        """Atualiza informações do HUD"""
        # Por enquanto, apenas armazena referência à nave
        self.spaceship = spaceship
    
    def render(self, surface, spaceship, camera_x, camera_y, score=0):
        """Renderiza o HUD"""
        if not spaceship:
            return

        # Atualiza referência à nave
        self.spaceship = spaceship
        self.score = score
            
        # Barra de vida
        self.render_health_bar(surface)
        
        # Barra de energia
        self.render_energy_bar(surface)
        
        # Barra de oxigênio
        self.render_oxygen_bar(surface)
        
        # Barra de combustível
        self.render_fuel_bar(surface)
        
        # Inventário rápido
        self.render_quick_inventory(surface)
        
        # Informações de posição
        self.render_position_info(surface)
        
        # Informações de velocidade
        self.render_velocity_info(surface)
        
        # Bloco selecionado
        self.render_selected_block(surface)

        # Pontuação
        self.render_score(surface)
    
    def render_selected_block(self, surface):
        """Renderiza bloco selecionado para construção"""
        if not self.spaceship or not hasattr(self.spaceship, 'selected_block_type'):
            return
            
        x = 10
        y = SCREEN_HEIGHT - 150
        
        # Título
        font = pygame.font.Font(None, 18)
        title_text = font.render(f"Bloco: {self.spaceship.selected_block_type}", True, WHITE)
        surface.blit(title_text, (x, y))
        
        # Mostra quantidade no inventário
        quantity = self.spaceship.inventory.get_item_count(self.spaceship.selected_block_type)
        quantity_text = font.render(f"Quantidade: {quantity}", True, WHITE)
        surface.blit(quantity_text, (x, y + 20))
    
    def render_quick_inventory(self, surface):
        """Renderiza inventário rápido"""
        if not self.spaceship or not hasattr(self.spaceship, 'inventory'):
            return
            
        x = SCREEN_WIDTH // 2 - 150
        y = SCREEN_HEIGHT - 120
        
        # Título
        font = pygame.font.Font(None, 20)
        title_text = font.render("Inventário:", True, WHITE)
        surface.blit(title_text, (x, y - 25))
        
        # Renderiza inventário rápido
        self.spaceship.inventory.render_quick_inventory(surface, x, y)
    
    def render_health_bar(self, surface):
        """Renderiza barra de vida"""
        bar_width = 200
        bar_height = 20
        x = 10
        y = SCREEN_HEIGHT - 80
        
        # Fundo da barra
        pygame.draw.rect(surface, DARK_GRAY, (x, y, bar_width, bar_height))
        
        # Barra de vida
        health_percentage = self.spaceship.health / self.spaceship.max_health
        health_width = int(bar_width * health_percentage)
        
        # Cor baseada na vida
        if health_percentage > 0.6:
            color = GREEN
        elif health_percentage > 0.3:
            color = YELLOW
        else:
            color = RED
        
        pygame.draw.rect(surface, color, (x, y, health_width, bar_height))
        
        # Borda
        pygame.draw.rect(surface, WHITE, (x, y, bar_width, bar_height), 2)
        
        # Texto
        health_text = self.font.render(f"Vida: {int(self.spaceship.health)}/{self.spaceship.max_health}", True, WHITE)
        surface.blit(health_text, (x + 5, y - 25))
    
    def render_energy_bar(self, surface):
        """Renderiza barra de energia"""
        bar_width = 200
        bar_height = 20
        x = 10
        y = SCREEN_HEIGHT - 50
        
        # Fundo da barra
        pygame.draw.rect(surface, DARK_GRAY, (x, y, bar_width, bar_height))
        
        # Barra de energia
        energy_percentage = self.spaceship.energy / self.spaceship.max_energy
        energy_width = int(bar_width * energy_percentage)
        
        pygame.draw.rect(surface, BLUE, (x, y, energy_width, bar_height))
        
        # Borda
        pygame.draw.rect(surface, WHITE, (x, y, bar_width, bar_height), 2)
        
        # Texto
        energy_text = self.font.render(f"Energia: {int(self.spaceship.energy)}/{self.spaceship.max_energy}", True, WHITE)
        surface.blit(energy_text, (x + 5, y - 25))
    
    def render_oxygen_bar(self, surface):
        """Renderiza barra de oxigênio"""
        bar_width = 200
        bar_height = 20
        x = 10
        y = SCREEN_HEIGHT - 20
        
        # Fundo da barra
        pygame.draw.rect(surface, DARK_GRAY, (x, y, bar_width, bar_height))
        
        # Barra de oxigênio
        oxygen_percentage = self.spaceship.oxygen / self.spaceship.max_oxygen
        oxygen_width = int(bar_width * oxygen_percentage)
        
        # Cor baseada no oxigênio
        if oxygen_percentage > 0.5:
            color = CYAN
        else:
            color = RED
        
        pygame.draw.rect(surface, color, (x, y, oxygen_width, bar_height))
        
        # Borda
        pygame.draw.rect(surface, WHITE, (x, y, bar_width, bar_height), 2)
        
        # Texto
        oxygen_text = self.font.render(f"Oxigênio: {int(self.spaceship.oxygen)}/{self.spaceship.max_oxygen}", True, WHITE)
        surface.blit(oxygen_text, (x + 5, y - 25))
    
    def render_fuel_bar(self, surface):
        """Renderiza barra de combustível"""
        bar_width = 200
        bar_height = 20
        x = 10
        y = SCREEN_HEIGHT - 110
        
        # Fundo da barra
        pygame.draw.rect(surface, DARK_GRAY, (x, y, bar_width, bar_height))
        
        # Barra de combustível
        fuel_percentage = self.spaceship.fuel / self.spaceship.max_fuel
        fuel_width = int(bar_width * fuel_percentage)
        
        # Cor baseada no combustível
        if fuel_percentage > 0.5:
            color = (255, 165, 0)  # Laranja
        else:
            color = RED
        
        pygame.draw.rect(surface, color, (x, y, fuel_width, bar_height))
        
        # Borda
        pygame.draw.rect(surface, WHITE, (x, y, bar_width, bar_height), 2)
        
        # Texto
        fuel_text = self.font.render(f"Combustível: {int(self.spaceship.fuel)}/{self.spaceship.max_fuel}", True, WHITE)
        surface.blit(fuel_text, (x + 5, y - 25))
    
    def render_score(self, surface):
        """Renderiza pontuação"""
        score_text = self.font.render(f"Pontos: {self.score}", True, STAR_YELLOW)
        surface.blit(score_text, (SCREEN_WIDTH - 200, 50))

    def render_position_info(self, surface):
        """Renderiza informações de posição"""
        x = SCREEN_WIDTH - 200
        y = 10
        
        pos_text = self.small_font.render(f"Pos: ({int(self.spaceship.x)}, {int(self.spaceship.y)})", True, WHITE)
        surface.blit(pos_text, (x, y))
    
    def render_velocity_info(self, surface):
        """Renderiza informações de velocidade"""
        x = SCREEN_WIDTH - 200
        y = 30
        
        speed = (self.spaceship.vx**2 + self.spaceship.vy**2)**0.5
        vel_text = self.small_font.render(f"Vel: {speed:.1f}", True, WHITE)
        surface.blit(vel_text, (x, y))
    
    def render_debug_info(self, surface, game):
        """Renderiza informações de debug"""
        if not DEBUG_MODE:
            return
            
        x = 10
        y = 10
        
        # FPS
        fps_text = self.small_font.render(f"FPS: {pygame.time.Clock().get_fps():.1f}", True, WHITE)
        surface.blit(fps_text, (x, y))
        
        # Entidades
        entity_text = self.small_font.render(f"Entidades: {len(game.planets) + len(game.blocks) + len(game.enemies)}", True, WHITE)
        surface.blit(entity_text, (x, y + 20))
        
        # Câmera
        camera_text = self.small_font.render(f"Câmera: ({int(game.camera_x)}, {int(game.camera_y)})", True, WHITE)
        surface.blit(camera_text, (x, y + 40))
