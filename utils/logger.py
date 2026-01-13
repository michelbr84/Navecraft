import logging
import os
from datetime import datetime
from settings import LOG_ENABLED, LOG_FILE, LOG_LEVEL

class GameLogger:
    def __init__(self):
        """Inicializa o sistema de logs"""
        self.logger = None
        
        if LOG_ENABLED:
            self.setup_logger()
    
    def setup_logger(self):
        """Configura o sistema de logs"""
        # Cria o diretório de logs se não existir
        log_dir = os.path.dirname(LOG_FILE)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # Configura o logger
        self.logger = logging.getLogger('Navecraft')
        self.logger.setLevel(getattr(logging, LOG_LEVEL))
        
        # Evita duplicação de handlers
        if not self.logger.handlers:
            # Handler para arquivo
            file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
            file_handler.setLevel(getattr(logging, LOG_LEVEL))
            
            # Handler para console (apenas em modo debug)
            if LOG_LEVEL == 'DEBUG':
                console_handler = logging.StreamHandler()
                console_handler.setLevel(logging.DEBUG)
                self.logger.addHandler(console_handler)
            
            # Formato das mensagens
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
    
    def log(self, message, level="INFO"):
        """Registra uma mensagem no log"""
        if not LOG_ENABLED or not self.logger:
            return
        
        level_func = getattr(self.logger, level.lower(), self.logger.info)
        level_func(message)
    
    def debug(self, message):
        """Registra mensagem de debug"""
        self.log(message, "DEBUG")
    
    def info(self, message):
        """Registra mensagem de informação"""
        self.log(message, "INFO")
    
    def warning(self, message):
        """Registra mensagem de aviso"""
        self.log(message, "WARNING")
    
    def error(self, message):
        """Registra mensagem de erro"""
        self.log(message, "ERROR")
    
    def critical(self, message):
        """Registra mensagem crítica"""
        self.log(message, "CRITICAL")
    
    def log_game_event(self, event_type, details=""):
        """Registra eventos do jogo"""
        message = f"GAME_EVENT: {event_type}"
        if details:
            message += f" - {details}"
        self.info(message)
    
    def log_performance(self, fps, frame_time, object_counts):
        """Registra informações de performance"""
        message = f"PERFORMANCE: FPS={fps}, FrameTime={frame_time:.2f}ms, Objects={object_counts}"
        self.debug(message)
    
    def log_error_with_context(self, error, context=""):
        """Registra erro com contexto"""
        message = f"ERROR: {error}"
        if context:
            message += f" - Context: {context}"
        self.error(message)
    
    def log_system_info(self):
        """Registra informações do sistema"""
        import platform
        import pygame
        
        system_info = {
            'platform': platform.platform(),
            'python_version': platform.python_version(),
            'pygame_version': pygame.version.ver,
            'screen_size': f"{pygame.display.Info().current_w}x{pygame.display.Info().current_h}"
        }
        
        for key, value in system_info.items():
            self.info(f"SYSTEM: {key}={value}")

# Instância global do logger
game_logger = GameLogger()
