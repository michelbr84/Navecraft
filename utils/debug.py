import pygame
import time
from settings import *

class DebugSystem:
    def __init__(self):
        """Inicializa o sistema de debug"""
        self.font = pygame.font.Font(None, 24)
        self.fps_counter = 0
        self.fps_timer = time.time()
        self.frame_times = []
        self.max_frame_times = 60
        
        # Contadores de performance
        self.visible_objects = {
            'planets': 0,
            'blocks': 0,
            'enemies': 0,
            'particles': 0,
            'projectiles': 0
        }
        
        # Informações de debug
        self.debug_info = {}
    
    def update_fps(self):
        """Atualiza contador de FPS"""
        current_time = time.time()
        self.fps_counter += 1
        
        if current_time - self.fps_timer >= 1.0:
            fps = self.fps_counter / (current_time - self.fps_timer)
            self.debug_info['fps'] = int(fps)
            self.fps_counter = 0
            self.fps_timer = current_time
    
    def update_frame_time(self, frame_time):
        """Atualiza tempo do frame"""
        self.frame_times.append(frame_time)
        if len(self.frame_times) > self.max_frame_times:
            self.frame_times.pop(0)
        
        if self.frame_times:
            avg_frame_time = sum(self.frame_times) / len(self.frame_times)
            self.debug_info['avg_frame_time'] = avg_frame_time
    
    def update_visible_objects(self, objects_dict):
        """Atualiza contadores de objetos visíveis"""
        for key, count in objects_dict.items():
            self.visible_objects[key] = count
    
    def render_debug_info(self, surface):
        """Renderiza informações de debug"""
        if not DEBUG_MODE:
            return
        
        y_offset = 10
        line_height = 25
        
        # FPS
        if SHOW_FPS and 'fps' in self.debug_info:
            fps_text = f"FPS: {self.debug_info['fps']}"
            fps_surface = self.font.render(fps_text, True, (255, 255, 0))
            surface.blit(fps_surface, (10, y_offset))
            y_offset += line_height
        
        # Tempo médio do frame
        if 'avg_frame_time' in self.debug_info:
            frame_text = f"Frame: {self.debug_info['avg_frame_time']:.2f}ms"
            frame_surface = self.font.render(frame_text, True, (255, 255, 0))
            surface.blit(frame_surface, (10, y_offset))
            y_offset += line_height
        
        # Objetos visíveis
        if SHOW_PERFORMANCE_INFO:
            for obj_type, count in self.visible_objects.items():
                obj_text = f"{obj_type.capitalize()}: {count}"
                obj_surface = self.font.render(obj_text, True, (0, 255, 255))
                surface.blit(obj_surface, (10, y_offset))
                y_offset += line_height
        
        # Informações de câmera
        if SHOW_CAMERA_INFO and 'camera_x' in self.debug_info and 'camera_y' in self.debug_info:
            cam_text = f"Camera: ({self.debug_info['camera_x']:.0f}, {self.debug_info['camera_y']:.0f})"
            cam_surface = self.font.render(cam_text, True, (255, 0, 255))
            surface.blit(cam_surface, (10, y_offset))
            y_offset += line_height
        
        # Informações da nave
        if 'spaceship_pos' in self.debug_info:
            ship_text = f"Ship: ({self.debug_info['spaceship_pos'][0]:.0f}, {self.debug_info['spaceship_pos'][1]:.0f})"
            ship_surface = self.font.render(ship_text, True, (0, 255, 0))
            surface.blit(ship_surface, (10, y_offset))
            y_offset += line_height
        
        # Informações de inventário
        if 'inventory_info' in self.debug_info:
            inv_text = f"Inventory: {self.debug_info['inventory_info']}"
            inv_surface = self.font.render(inv_text, True, (255, 165, 0))
            surface.blit(inv_surface, (10, y_offset))
            y_offset += line_height
    
    def render_collision_boxes(self, surface, game_objects, camera_x, camera_y):
        """Renderiza caixas de colisão"""
        if not SHOW_COLLISION_BOXES:
            return
        
        for obj in game_objects:
            if hasattr(obj, 'get_collision_rect'):
                rect = obj.get_collision_rect()
                screen_rect = pygame.Rect(
                    rect.x - camera_x,
                    rect.y - camera_y,
                    rect.width,
                    rect.height
                )
                pygame.draw.rect(surface, (255, 0, 0), screen_rect, 2)
    
    def log_info(self, message, level="INFO"):
        """Registra informações no log"""
        if not LOG_ENABLED:
            return
        
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] [{level}] {message}"
        
        try:
            with open(LOG_FILE, 'a', encoding='utf-8') as f:
                f.write(log_message + '\n')
        except:
            pass  # Ignora erros de log
    
    def set_debug_info(self, key, value):
        """Define uma informação de debug"""
        self.debug_info[key] = value
