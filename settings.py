"""
Configurações globais do Navecraft
"""

import pygame

# Configurações da tela
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
FPS = 60
TITLE = "Navecraft - Minecraft no Espaço"

# Cores (RGB)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)
LIGHT_GRAY = (192, 192, 192)

# Cores espaciais
SPACE_BLUE = (25, 25, 112)
STAR_YELLOW = (255, 215, 0)
PLANET_GREEN = (34, 139, 34)
PLANET_RED = (139, 69, 19)
PLANET_BLUE = (70, 130, 180)

# Configurações da nave
SPACESHIP_SPEED = 5.0
SPACESHIP_ACCELERATION = 0.5
SPACESHIP_DECELERATION = 0.98
SPACESHIP_SIZE = 32
SPACESHIP_HEALTH = 100
SPACESHIP_ENERGY = 100
SPACESHIP_OXYGEN = 100

# Configurações de física
GRAVITY = 0.1
MAX_VELOCITY = 10.0
FRICTION = 0.95

# Configurações de blocos
BLOCK_SIZE = 16
CHUNK_SIZE = 16
WORLD_SIZE = 1000

# Configurações de planetas
MIN_PLANET_SIZE = 100
MAX_PLANET_SIZE = 300
PLANET_COUNT = 5

# Configurações de inimigos
ENEMY_SPEED = 2.0
ENEMY_HEALTH = 50
ENEMY_DAMAGE = 10

# Configurações de armas
LASER_SPEED = 15.0
LASER_DAMAGE = 25
LASER_COOLDOWN = 200  # milissegundos

# Configurações de áudio
SAMPLE_RATE = 44100
AUDIO_CHUNK_SIZE = 1024

# Configurações de geração procedural
SEED = 42
NOISE_SCALE = 50.0
OCTAVES = 4
PERSISTENCE = 0.5
LACUNARITY = 2.0

# Configurações de interface
HUD_HEIGHT = 100
INVENTORY_SLOTS = 10
SLOT_SIZE = 40

# Configurações de partículas
MAX_PARTICLES = 100
PARTICLE_LIFETIME = 60

# Configurações de Debug e Otimização
DEBUG_MODE = False
SHOW_FPS = True
SHOW_COLLISION_BOXES = False
SHOW_CAMERA_INFO = False
SHOW_PERFORMANCE_INFO = False

# Limites de otimização
MAX_VISIBLE_ENEMIES = 20
MAX_VISIBLE_PARTICLES = 100
MAX_VISIBLE_BLOCKS = 200
CULLING_DISTANCE = 800
ENEMY_UPDATE_DISTANCE = 500
PARTICLE_CLEANUP_DISTANCE = 800

# Configurações de Save/Load
SAVE_FILE = "navecraft_save.json"
AUTO_SAVE_INTERVAL = 30000  # 30 segundos

# Configurações de Log
LOG_ENABLED = True
LOG_FILE = "navecraft.log"
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR

# Configurações de performance
MAX_ENTITIES = 1000
MAX_PROJECTILES = 100
MAX_PARTICLES_PER_EFFECT = 20

# Configurações de biomas
BIOME_TYPES = {
    'ROCK': {'color': PLANET_RED, 'hardness': 1.0},
    'ICE': {'color': (240, 248, 255), 'hardness': 0.5},
    'GAS': {'color': (255, 165, 0), 'hardness': 0.3},
    'METAL': {'color': (192, 192, 192), 'hardness': 2.0},
    'CRYSTAL': {'color': (138, 43, 226), 'hardness': 1.5}
}

# Configurações de recursos
RESOURCE_TYPES = {
    'IRON': {'color': (169, 169, 169), 'value': 10},
    'GOLD': {'color': (255, 215, 0), 'value': 25},
    'CRYSTAL': {'color': (138, 43, 226), 'value': 50},
    'FUEL': {'color': (255, 165, 0), 'value': 5},
    'OXYGEN': {'color': (135, 206, 235), 'value': 15}
}

# Configurações de controles
CONTROLS = {
    'MOVE_UP': [pygame.K_w, pygame.K_UP],
    'MOVE_DOWN': [pygame.K_s, pygame.K_DOWN],
    'MOVE_LEFT': [pygame.K_a, pygame.K_LEFT],
    'MOVE_RIGHT': [pygame.K_d, pygame.K_RIGHT],
    'SHOOT': [pygame.K_SPACE],
    'MINE': [pygame.K_e],
    'BUILD': [pygame.K_q],
    'INVENTORY': [pygame.K_i],
    'PAUSE': [pygame.K_ESCAPE],
    'SELECT_IRON': [pygame.K_1],
    'SELECT_GOLD': [pygame.K_2],
    'SELECT_CRYSTAL': [pygame.K_3],
    'SELECT_FUEL': [pygame.K_4],
    'SELECT_OXYGEN': [pygame.K_5],
    'MISSION': [pygame.K_m],
    'CRAFT_REPAIR': [pygame.K_r],
    'CRAFT_ENERGY': [pygame.K_t],
    'CRAFT_OXYGEN': [pygame.K_y],
    'CRAFT_SHIELD': [pygame.K_u],
    'UPGRADE_ENGINE': [pygame.K_F1],
    'UPGRADE_SHIELD': [pygame.K_F2],
    'UPGRADE_ENERGY': [pygame.K_F3],
    'UPGRADE_MINING': [pygame.K_F4],
    'UPGRADE_OXYGEN': [pygame.K_F5],
    'UPGRADE_FUEL': [pygame.K_F6],
    'MULTIPLAYER_TOGGLE': [pygame.K_F7],
    'MULTIPLAYER_ADD_PLAYER': [pygame.K_F8]
}
