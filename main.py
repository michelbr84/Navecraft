"""
Navecraft - Minecraft no Espaço
Arquivo principal do jogo
"""

import pygame
import sys
import time
from settings import *
from core.game import Game
from ui.menu import Menu, PauseMenu, GameOverMenu

class Navecraft:
    def __init__(self):
        """Inicializa o jogo Navecraft"""
        pygame.init()
        pygame.mixer.init()
        
        # Configuração da tela
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        
        # Estado do jogo
        self.running = True
        self.paused = False
        self.game_state = "menu"  # menu, playing, paused, game_over
        
        # Instância principal do jogo
        self.game = Game()
        
        # Menus
        self.main_menu = Menu()
        self.pause_menu = PauseMenu()
        self.game_over_menu = GameOverMenu()
        
        # Contadores para debug
        self.fps_counter = 0
        self.last_fps_time = time.time()
        
    def handle_events(self):
        """Processa eventos do Pygame"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F1:
                    global DEBUG_MODE
                    DEBUG_MODE = not DEBUG_MODE
            
            # Processa eventos baseado no estado do jogo
            if self.game_state == "menu":
                result = self.main_menu.handle_input(event)
                if result == "play":
                    self.game_state = "playing"
                elif result == "quit":
                    self.running = False
            elif self.game_state == "playing":
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.game_state = "paused"
                else:
                    self.game.handle_event(event)
            elif self.game_state == "paused":
                result = self.pause_menu.handle_input(event)
                if result == "continue":
                    self.game_state = "playing"
                elif result == "quit":
                    self.running = False
            elif self.game_state == "game_over":
                result = self.game_over_menu.handle_input(event)
                if result == "restart":
                    self.game_state = "playing"
                    self.game = Game()  # Reinicia o jogo
                elif result == "main_menu":
                    self.game_state = "menu"
                elif result == "quit":
                    self.running = False
    
    def update(self):
        """Atualiza lógica do jogo"""
        if self.game_state == "playing":
            self.game.update()
            
            # Verifica game over
            if self.game.spaceship and not self.game.spaceship.is_alive():
                self.game_state = "game_over"
        
        # Atualiza contador de FPS
        current_time = time.time()
        self.fps_counter += 1
        if current_time - self.last_fps_time >= 1.0:
            if SHOW_FPS:
                print(f"FPS: {self.fps_counter}")
            self.fps_counter = 0
            self.last_fps_time = current_time
    
    def render(self):
        """Renderiza o jogo"""
        # Renderiza baseado no estado do jogo
        if self.game_state == "menu":
            self.main_menu.render(self.screen)
        elif self.game_state == "playing":
            # Renderiza o jogo
            self.game.render(self.screen)
            
            # Renderiza informações de debug
            if DEBUG_MODE:
                self.render_debug_info()
        elif self.game_state == "paused":
            # Renderiza o jogo em pausa
            self.game.render(self.screen)
            self.pause_menu.render(self.screen)
        elif self.game_state == "game_over":
            # Renderiza o jogo e menu de game over
            self.game.render(self.screen)
            self.game_over_menu.render(self.screen, score=0)  # TODO: Implementar pontuação
        
        # Atualiza a tela
        pygame.display.flip()
    
    def render_debug_info(self):
        """Renderiza informações de debug"""
        font = pygame.font.Font(None, 24)
        
        # FPS
        fps_text = font.render(f"FPS: {self.clock.get_fps():.1f}", True, WHITE)
        self.screen.blit(fps_text, (10, 10))
        
        # Posição da nave
        if hasattr(self.game, 'spaceship'):
            pos_text = font.render(f"Pos: {self.game.spaceship.x:.1f}, {self.game.spaceship.y:.1f}", True, WHITE)
            self.screen.blit(pos_text, (10, 35))
        
        # Velocidade da nave
        if hasattr(self.game, 'spaceship'):
            vel_text = font.render(f"Vel: {self.game.spaceship.vx:.1f}, {self.game.spaceship.vy:.1f}", True, WHITE)
            self.screen.blit(vel_text, (10, 60))
        
        # Estado do jogo
        state_text = font.render(f"Paused: {self.paused}", True, WHITE)
        self.screen.blit(state_text, (10, 85))
    
    def run(self):
        """Loop principal do jogo"""
        print("Iniciando Navecraft...")
        print("Controles:")
        print("WASD/Setas - Movimentação")
        print("Espaço - Tiro")
        print("E - Mineração")
        print("Q - Construção")
        print("I - Inventário")
        print("ESC - Pausa")
        print("F1 - Debug")
        
        while self.running:
            # Processa eventos
            self.handle_events()
            
            # Atualiza lógica
            self.update()
            
            # Renderiza
            self.render()
            
            # Controla FPS
            self.clock.tick(FPS)
        
        self.cleanup()
    
    def cleanup(self):
        """Limpa recursos do jogo"""
        print("Finalizando Navecraft...")
        pygame.quit()
        sys.exit()

def main():
    """Função principal"""
    try:
        game = Navecraft()
        game.run()
    except Exception as e:
        print(f"Erro no jogo: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
