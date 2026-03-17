"""
Sistema de entrada do Navecraft
"""

import pygame
from settings import CONTROLS

class InputManager:
    def __init__(self):
        """Inicializa o gerenciador de entrada"""
        self.keys_pressed = set()
        self.keys_just_pressed = set()
        self.keys_just_released = set()
        self.mouse_pos = (0, 0)
        self.mouse_buttons = [False, False, False]  # Left, Middle, Right
        self.mouse_buttons_just_pressed = [False, False, False]
        self.mouse_buttons_just_released = [False, False, False]
        
    def update(self):
        """Atualiza estado das teclas e mouse (compatibilidade)"""
        self.clear_frame()
        self.update_mouse()

    def update_mouse(self):
        """Atualiza posição e botões do mouse"""
        self.mouse_pos = pygame.mouse.get_pos()

        mouse_buttons = pygame.mouse.get_pressed()
        for i in range(3):
            if mouse_buttons[i] and not self.mouse_buttons[i]:
                self.mouse_buttons_just_pressed[i] = True
            elif not mouse_buttons[i] and self.mouse_buttons[i]:
                self.mouse_buttons_just_released[i] = True
            self.mouse_buttons[i] = mouse_buttons[i]

    def clear_frame(self):
        """Limpa estados de just pressed/released no fim do frame"""
        self.keys_just_pressed.clear()
        self.keys_just_released.clear()
        self.mouse_buttons_just_pressed = [False, False, False]
        self.mouse_buttons_just_released = [False, False, False]
    
    def handle_event(self, event):
        """Processa um evento do Pygame"""
        if event.type == pygame.KEYDOWN:
            self.keys_pressed.add(event.key)
            self.keys_just_pressed.add(event.key)
        elif event.type == pygame.KEYUP:
            self.keys_pressed.discard(event.key)
            self.keys_just_released.add(event.key)
    
    def is_key_pressed(self, key):
        """Verifica se uma tecla está pressionada"""
        return key in self.keys_pressed
    
    def is_key_just_pressed(self, key):
        """Verifica se uma tecla foi pressionada neste frame"""
        return key in self.keys_just_pressed
    
    def is_key_just_released(self, key):
        """Verifica se uma tecla foi solta neste frame"""
        return key in self.keys_just_released
    
    def is_control_pressed(self, control_name):
        """Verifica se um controle está pressionado"""
        if control_name in CONTROLS:
            return any(self.is_key_pressed(key) for key in CONTROLS[control_name])
        return False
    
    def is_control_just_pressed(self, control_name):
        """Verifica se um controle foi pressionado neste frame"""
        if control_name in CONTROLS:
            return any(self.is_key_just_pressed(key) for key in CONTROLS[control_name])
        return False
    
    def get_movement_vector(self):
        """Retorna vetor de movimento baseado nas teclas pressionadas"""
        dx, dy = 0, 0
        
        if self.is_control_pressed('MOVE_UP'):
            dy -= 1
        if self.is_control_pressed('MOVE_DOWN'):
            dy += 1
        if self.is_control_pressed('MOVE_LEFT'):
            dx -= 1
        if self.is_control_pressed('MOVE_RIGHT'):
            dx += 1
        
        # Normaliza movimento diagonal
        if dx != 0 and dy != 0:
            dx *= 0.707  # 1/sqrt(2)
            dy *= 0.707
        
        return dx, dy
    
    def get_mouse_position(self):
        """Retorna posição do mouse"""
        return self.mouse_pos
    
    def is_mouse_button_pressed(self, button):
        """Verifica se botão do mouse está pressionado (0=left, 1=middle, 2=right)"""
        return self.mouse_buttons[button]
    
    def is_mouse_button_just_pressed(self, button):
        """Verifica se botão do mouse foi pressionado neste frame"""
        return self.mouse_buttons_just_pressed[button]
    
    def is_mouse_button_just_released(self, button):
        """Verifica se botão do mouse foi solto neste frame"""
        return self.mouse_buttons_just_released[button]
