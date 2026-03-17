"""
Sistema de menus do Navecraft
"""

import pygame
from settings import *

class Menu:
    def __init__(self):
        """Inicializa o menu"""
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 32)
        self.font_small = pygame.font.Font(None, 24)
        
        self.current_menu = "main"
        self.parent_menu = "main"  # Menu para retornar de settings
        self.selected_option = 0
        self.menu_options = {
            "main": ["Jogar", "Configurações", "Sobre", "Sair"],
            "pause": ["Continuar", "Configurações", "Menu Principal", "Sair"],
            "settings": ["Volume", "Tela Cheia", "Voltar"]
        }
    
    def handle_input(self, event):
        """Processa entrada do menu"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_option = (self.selected_option - 1) % len(self.menu_options[self.current_menu])
            elif event.key == pygame.K_DOWN:
                self.selected_option = (self.selected_option + 1) % len(self.menu_options[self.current_menu])
            elif event.key == pygame.K_RETURN:
                return self.select_option()
            elif event.key == pygame.K_ESCAPE:
                if self.current_menu == "pause":
                    return "continue"
                elif self.current_menu == "settings":
                    self.current_menu = self.parent_menu
                    self.selected_option = 0
                    if self.parent_menu == "pause":
                        return None  # Stay in pause state
        
        return None
    
    def select_option(self):
        """Seleciona opção atual"""
        if self.current_menu == "main":
            if self.selected_option == 0:  # Jogar
                return "play"
            elif self.selected_option == 1:  # Configurações
                self.parent_menu = "main"
                self.current_menu = "settings"
                self.selected_option = 0
            elif self.selected_option == 2:  # Sobre
                return "about"
            elif self.selected_option == 3:  # Sair
                return "quit"

        elif self.current_menu == "pause":
            if self.selected_option == 0:  # Continuar
                return "continue"
            elif self.selected_option == 1:  # Configurações
                self.parent_menu = "pause"
                self.current_menu = "settings"
                self.selected_option = 0
            elif self.selected_option == 2:  # Menu Principal
                return "main_menu"
            elif self.selected_option == 3:  # Sair
                return "quit"

        elif self.current_menu == "settings":
            if self.selected_option == 0:  # Volume
                return "volume"
            elif self.selected_option == 1:  # Tela Cheia
                return "fullscreen"
            elif self.selected_option == 2:  # Voltar
                self.current_menu = self.parent_menu
                self.selected_option = 0

        return None
    
    def render(self, surface):
        """Renderiza o menu"""
        # Fundo
        surface.fill(SPACE_BLUE)
        
        # Título
        title = self.font_large.render("NAVECRAFT", True, WHITE)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 100))
        surface.blit(title, title_rect)
        
        # Subtítulo
        subtitle = self.font_medium.render("Minecraft no Espaço", True, CYAN)
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, 150))
        surface.blit(subtitle, subtitle_rect)
        
        # Opções do menu
        options = self.menu_options[self.current_menu]
        for i, option in enumerate(options):
            if i == self.selected_option:
                color = YELLOW
                # Seta de seleção
                arrow = self.font_small.render(">", True, YELLOW)
                arrow_rect = arrow.get_rect(right=SCREEN_WIDTH // 2 - 50, centery=250 + i * 50)
                surface.blit(arrow, arrow_rect)
            else:
                color = WHITE
            
            text = self.font_medium.render(option, True, color)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, 250 + i * 50))
            surface.blit(text, text_rect)
        
        # Instruções
        if self.current_menu == "main":
            instructions = [
                "Controles:",
                "WASD/Setas - Movimentação",
                "E - Mineração",
                "Q - Construção",
                "I - Inventário",
                "ESC - Pausa"
            ]
            
            for i, instruction in enumerate(instructions):
                text = self.font_small.render(instruction, True, LIGHT_GRAY)
                text_rect = text.get_rect(left=50, top=400 + i * 25)
                surface.blit(text, text_rect)
    
    def set_menu(self, menu_name):
        """Define menu atual"""
        self.current_menu = menu_name
        self.selected_option = 0

class PauseMenu(Menu):
    def __init__(self):
        """Inicializa menu de pausa"""
        super().__init__()
        self.current_menu = "pause"
    
    def render(self, surface):
        """Renderiza menu de pausa"""
        # Overlay semi-transparente
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        surface.blit(overlay, (0, 0))
        
        # Título
        title = self.font_large.render("PAUSADO", True, WHITE)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 200))
        surface.blit(title, title_rect)
        
        # Opções do menu
        options = self.menu_options[self.current_menu]
        for i, option in enumerate(options):
            if i == self.selected_option:
                color = YELLOW
                # Seta de seleção
                arrow = self.font_small.render(">", True, YELLOW)
                arrow_rect = arrow.get_rect(right=SCREEN_WIDTH // 2 - 50, centery=300 + i * 50)
                surface.blit(arrow, arrow_rect)
            else:
                color = WHITE
            
            text = self.font_medium.render(option, True, color)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, 300 + i * 50))
            surface.blit(text, text_rect)

class GameOverMenu(Menu):
    def __init__(self):
        """Inicializa menu de game over"""
        super().__init__()
        self.current_menu = "game_over"
        self.menu_options["game_over"] = ["Tentar Novamente", "Menu Principal", "Sair"]
    
    def render(self, surface, score=0):
        """Renderiza menu de game over"""
        # Overlay escuro
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        surface.blit(overlay, (0, 0))
        
        # Título
        title = self.font_large.render("GAME OVER", True, RED)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 200))
        surface.blit(title, title_rect)
        
        # Pontuação
        score_text = self.font_medium.render(f"Pontuação: {score}", True, WHITE)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, 250))
        surface.blit(score_text, score_rect)
        
        # Opções do menu
        options = self.menu_options[self.current_menu]
        for i, option in enumerate(options):
            if i == self.selected_option:
                color = YELLOW
                # Seta de seleção
                arrow = self.font_small.render(">", True, YELLOW)
                arrow_rect = arrow.get_rect(right=SCREEN_WIDTH // 2 - 50, centery=350 + i * 50)
                surface.blit(arrow, arrow_rect)
            else:
                color = WHITE
            
            text = self.font_medium.render(option, True, color)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, 350 + i * 50))
            surface.blit(text, text_rect)
    
    def select_option(self):
        """Seleciona opção atual"""
        if self.selected_option == 0:  # Tentar Novamente
            return "restart"
        elif self.selected_option == 1:  # Menu Principal
            return "main_menu"
        elif self.selected_option == 2:  # Sair
            return "quit"
        
        return None
