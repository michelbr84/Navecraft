"""
Sistema de geração procedural do mundo
"""

import random
import math
import noise
from settings import *
from entities.enemy import Enemy

class WorldGenerator:
    def __init__(self):
        """Inicializa o gerador de mundo"""
        random.seed(SEED)
        self.noise_generator = noise.pnoise2
        
    def generate_planets(self):
        """Gera planetas proceduralmente"""
        planets = []
        
        # Evita sobreposição de planetas
        used_positions = []
        
        for i in range(PLANET_COUNT):
            attempts = 0
            while attempts < 100:
                # Posição aleatória
                x = random.randint(200, WORLD_SIZE * BLOCK_SIZE - 200)
                y = random.randint(200, WORLD_SIZE * BLOCK_SIZE - 200)
                
                # Verifica se está longe o suficiente de outros planetas
                too_close = False
                for pos in used_positions:
                    distance = math.sqrt((x - pos[0])**2 + (y - pos[1])**2)
                    if distance < 400:  # Distância mínima entre planetas
                        too_close = True
                        break
                
                if not too_close:
                    used_positions.append((x, y))
                    break
                
                attempts += 1
            
            if attempts >= 100:
                continue  # Pula este planeta se não conseguir posição
            
            # Tamanho baseado em ruído
            noise_value = self.noise_generator(x * 0.001, y * 0.001)
            size_factor = (noise_value + 1) / 2  # Normaliza para 0-1
            radius = int(MIN_PLANET_SIZE + (MAX_PLANET_SIZE - MIN_PLANET_SIZE) * size_factor)
            
            # Tipo de planeta baseado em ruído
            type_noise = self.noise_generator(x * 0.002, y * 0.002)
            planet_types = ['ROCK', 'ICE', 'GAS', 'METAL', 'CRYSTAL', 'LAVA', 'TOXIC', 'RADIOACTIVE', 'WATER', 'DESERT']
            planet_type = planet_types[int((type_noise + 1) / 2 * len(planet_types))]
            
            # Gera características do planeta
            atmosphere = random.uniform(0, 1)
            temperature = random.uniform(-1, 1)
            gravity = random.uniform(0.5, 2.0)
            
            # Cria planeta
            planet = Planet(x, y, radius, planet_type, atmosphere, temperature, gravity)
            planets.append(planet)
        
        return planets
    
    def generate_blocks(self):
        """Gera blocos proceduralmente"""
        blocks = []
        
        # Gera blocos baseados em ruído
        for x in range(0, WORLD_SIZE * BLOCK_SIZE, BLOCK_SIZE * 2):
            for y in range(0, WORLD_SIZE * BLOCK_SIZE, BLOCK_SIZE * 2):
                # Usa ruído para determinar se há bloco aqui
                noise_value = self.noise_generator(x * 0.01, y * 0.01)
                
                if noise_value > 0.3:  # Apenas 30% das posições têm blocos
                    # Determina tipo baseado em ruído
                    type_noise = self.noise_generator(x * 0.02, y * 0.02)
                    
                    if type_noise > 0.7:
                        block_type = 'CRYSTAL'
                    elif type_noise > 0.5:
                        block_type = 'GOLD'
                    elif type_noise > 0.3:
                        block_type = 'IRON'
                    elif type_noise > 0.1:
                        block_type = 'FUEL'
                    else:
                        block_type = 'OXYGEN'
                    
                    # Adiciona variação na posição
                    offset_x = random.randint(-BLOCK_SIZE//2, BLOCK_SIZE//2)
                    offset_y = random.randint(-BLOCK_SIZE//2, BLOCK_SIZE//2)
                    
                    block = Block(x + offset_x, y + offset_y, block_type)
                    blocks.append(block)
        
        return blocks
    
    def generate_caves(self, planets):
        """Gera cavernas dentro/ao redor dos planetas"""
        cave_blocks = []
        for planet in planets:
            if planet.planet_type in ('GAS',):
                continue

            num_caves = random.randint(1, 3)
            for _ in range(num_caves):
                # Entrada na superficie do planeta
                entrance_angle = random.uniform(0, math.pi * 2)
                cx = planet.x + math.cos(entrance_angle) * planet.radius * 0.9
                cy = planet.y + math.sin(entrance_angle) * planet.radius * 0.9

                tunnel_length = random.randint(8, 20)

                for step in range(tunnel_length):
                    # Direcao para o centro do planeta
                    to_cx = planet.x - cx
                    to_cy = planet.y - cy
                    dist = math.sqrt(to_cx ** 2 + to_cy ** 2)

                    if dist > 0:
                        bias_x = to_cx / dist * 0.6
                        bias_y = to_cy / dist * 0.6
                    else:
                        bias_x, bias_y = 0, 0

                    cx += (bias_x + random.uniform(-0.5, 0.5)) * BLOCK_SIZE * 1.5
                    cy += (bias_y + random.uniform(-0.5, 0.5)) * BLOCK_SIZE * 1.5

                    # Paredes do tunel
                    wall_w = random.randint(2, 4)
                    for wx in range(-wall_w, wall_w + 1):
                        for wy in range(-wall_w, wall_w + 1):
                            if abs(wx) >= wall_w - 1 or abs(wy) >= wall_w - 1:
                                bx = cx + wx * BLOCK_SIZE
                                by = cy + wy * BLOCK_SIZE
                                bt = self._cave_block_type(planet.planet_type)
                                cave_blocks.append(Block(bx, by, bt))

                    # Camaras ocasionais
                    if random.random() < 0.2:
                        for angle_deg in range(0, 360, 20):
                            a = math.radians(angle_deg)
                            r = random.randint(3, 5)
                            bx = cx + math.cos(a) * r * BLOCK_SIZE
                            by = cy + math.sin(a) * r * BLOCK_SIZE
                            bt = self._cave_block_type(planet.planet_type)
                            cave_blocks.append(Block(bx, by, bt))

        return cave_blocks

    def _cave_block_type(self, planet_type):
        """Tipo de bloco para paredes de caverna baseado no planeta"""
        mapping = {
            'ROCK': ['IRON', 'IRON', 'GOLD'],
            'ICE': ['OXYGEN', 'CRYSTAL', 'OXYGEN'],
            'METAL': ['IRON', 'GOLD', 'IRON'],
            'CRYSTAL': ['CRYSTAL', 'GOLD', 'CRYSTAL'],
            'LAVA': ['IRON', 'FUEL', 'GOLD'],
            'RADIOACTIVE': ['CRYSTAL', 'GOLD', 'CRYSTAL'],
            'WATER': ['OXYGEN', 'IRON', 'OXYGEN'],
            'DESERT': ['IRON', 'GOLD', 'IRON'],
            'TOXIC': ['CRYSTAL', 'FUEL', 'OXYGEN'],
        }
        choices = mapping.get(planet_type, ['IRON', 'GOLD', 'CRYSTAL'])
        return random.choice(choices)

    def generate_enemies(self):
        """Gera inimigos proceduralmente"""
        enemies = []
        
        # Gera inimigos baseados em ruído
        for i in range(10):  # 10 inimigos iniciais
            # Posição aleatória
            x = random.randint(200, WORLD_SIZE * BLOCK_SIZE - 200)
            y = random.randint(200, WORLD_SIZE * BLOCK_SIZE - 200)
            
            # Tipo baseado em ruído
            type_noise = self.noise_generator(x * 0.003, y * 0.003)
            enemy_types = ['DRONE', 'ANDROID', 'SNIPER', 'ARACHNOID']
            enemy_type = enemy_types[int((type_noise + 1) / 2 * len(enemy_types))]
            
            # Cria inimigo
            enemy = Enemy(x, y, enemy_type)
            enemies.append(enemy)
        
        return enemies

# Classes temporárias para completar a FASE 1
class Planet:
    def __init__(self, x, y, radius, planet_type, atmosphere=0.5, temperature=0.0, gravity=1.0):
        self.x = x
        self.y = y
        self.radius = radius
        self.size = radius
        self.planet_type = planet_type
        self.mass = radius * 0.1 * gravity
        self.atmosphere = atmosphere
        self.temperature = temperature
        self.gravity = gravity
        # Procedural memorable name
        from systems.planet_names import generate_name
        self.name = generate_name(int(x * 31 + y * 17))
        self.surface_features = self.generate_surface_features()
        self.resources = self.generate_resources()
    
    def generate_surface_features(self):
        """Gera características da superfície do planeta"""
        features = []
        random.seed(self.x + self.y)  # Seed baseada na posição
        
        # Características específicas por tipo de planeta
        if self.planet_type == 'LAVA':
            # Vulcões e rios de lava
            feature_count = random.randint(8, 20)
            for _ in range(feature_count):
                angle = random.uniform(0, math.pi * 2)
                distance = random.uniform(0, self.radius * 0.8)
                size = random.uniform(0.1, 0.4)
                
                features.append({
                    'type': random.choice(['volcano', 'lava_river', 'magma_pool']),
                    'angle': angle,
                    'distance': distance,
                    'size': size
                })
        
        elif self.planet_type == 'TOXIC':
            # Nuvens tóxicas e poços
            feature_count = random.randint(10, 25)
            for _ in range(feature_count):
                angle = random.uniform(0, math.pi * 2)
                distance = random.uniform(0, self.radius * 0.8)
                size = random.uniform(0.1, 0.3)
                
                features.append({
                    'type': random.choice(['toxic_cloud', 'poison_pool', 'acid_rain']),
                    'angle': angle,
                    'distance': distance,
                    'size': size
                })
        
        elif self.planet_type == 'RADIOACTIVE':
            # Cristais radioativos
            feature_count = random.randint(12, 30)
            for _ in range(feature_count):
                angle = random.uniform(0, math.pi * 2)
                distance = random.uniform(0, self.radius * 0.8)
                size = random.uniform(0.1, 0.3)
                
                features.append({
                    'type': random.choice(['radioactive_crystal', 'nuclear_waste', 'radiation_zone']),
                    'angle': angle,
                    'distance': distance,
                    'size': size
                })
        
        elif self.planet_type == 'WATER':
            # Ilhas e oceanos
            feature_count = random.randint(6, 15)
            for _ in range(feature_count):
                angle = random.uniform(0, math.pi * 2)
                distance = random.uniform(0, self.radius * 0.8)
                size = random.uniform(0.1, 0.4)
                
                features.append({
                    'type': random.choice(['island', 'ocean_deep', 'coral_reef']),
                    'angle': angle,
                    'distance': distance,
                    'size': size
                })
        
        elif self.planet_type == 'DESERT':
            # Dunas e oásis
            feature_count = random.randint(15, 35)
            for _ in range(feature_count):
                angle = random.uniform(0, math.pi * 2)
                distance = random.uniform(0, self.radius * 0.8)
                size = random.uniform(0.1, 0.3)
                
                features.append({
                    'type': random.choice(['dune', 'oasis', 'sandstorm']),
                    'angle': angle,
                    'distance': distance,
                    'size': size
                })
        
        else:
            # Características padrão para outros tipos
            feature_count = random.randint(5, 15)
            for _ in range(feature_count):
                angle = random.uniform(0, math.pi * 2)
                distance = random.uniform(0, self.radius * 0.8)
                size = random.uniform(0.1, 0.3)
                
                features.append({
                    'type': random.choice(['crater', 'mountain', 'valley', 'plateau']),
                    'angle': angle,
                    'distance': distance,
                    'size': size
                })
        
        return features
    
    def generate_resources(self):
        """Gera recursos do planeta"""
        resources = []
        random.seed(self.x + self.y + 1000)  # Seed diferente
        
        # Baseado no tipo de planeta
        resource_chances = {
            'ROCK': {'IRON': 0.8, 'GOLD': 0.3, 'CRYSTAL': 0.1},
            'ICE': {'OXYGEN': 0.9, 'CRYSTAL': 0.4, 'FUEL': 0.2},
            'GAS': {'FUEL': 0.9, 'OXYGEN': 0.6, 'CRYSTAL': 0.1},
            'METAL': {'IRON': 0.9, 'GOLD': 0.7, 'CRYSTAL': 0.3},
            'CRYSTAL': {'CRYSTAL': 0.9, 'GOLD': 0.5, 'IRON': 0.3},
            'LAVA': {'IRON': 0.7, 'GOLD': 0.4, 'FUEL': 0.8},
            'TOXIC': {'OXYGEN': 0.3, 'CRYSTAL': 0.6, 'FUEL': 0.2},
            'RADIOACTIVE': {'CRYSTAL': 0.9, 'GOLD': 0.8, 'IRON': 0.5},
            'WATER': {'OXYGEN': 0.9, 'CRYSTAL': 0.3, 'FUEL': 0.1},
            'DESERT': {'IRON': 0.5, 'GOLD': 0.3, 'OXYGEN': 0.2}
        }
        
        chances = resource_chances.get(self.planet_type, resource_chances['ROCK'])
        
        for resource_type, chance in chances.items():
            if random.random() < chance:
                # Posição do recurso na superfície
                angle = random.uniform(0, math.pi * 2)
                distance = random.uniform(self.radius * 0.7, self.radius * 0.9)
                
                resources.append({
                    'type': resource_type,
                    'angle': angle,
                    'distance': distance,
                    'amount': random.randint(10, 50)
                })
        
        return resources
        
    def render(self, surface, camera_x, camera_y):
        # Renderização básica - círculo colorido
        screen_x = int(self.x - camera_x)
        screen_y = int(self.y - camera_y)
        
        # Cor baseada no tipo
        colors = {
            'ROCK': PLANET_RED,
            'ICE': (240, 248, 255),
            'GAS': (255, 165, 0),
            'METAL': (192, 192, 192),
            'CRYSTAL': (138, 43, 226),
            'LAVA': (255, 69, 0),
            'TOXIC': (50, 205, 50),
            'RADIOACTIVE': (255, 255, 0),
            'WATER': (0, 191, 255),
            'DESERT': (244, 164, 96)
        }
        
        color = colors.get(self.planet_type, PLANET_RED)
        pygame.draw.circle(surface, color, (screen_x, screen_y), self.radius)
        
        # Borda
        pygame.draw.circle(surface, WHITE, (screen_x, screen_y), self.radius, 2)

class Block:
    def __init__(self, x, y, block_type):
        self.x = x
        self.y = y
        self.block_type = block_type
        self.size = BLOCK_SIZE
        self.health = RESOURCE_TYPES[block_type]['value'] * 10
        self.max_health = self.health
        self.collected = False
        self.brightness = random.uniform(0.8, 1.2)
        self.rotation = random.uniform(0, math.pi * 2)
        self.rotation_speed = random.uniform(-0.005, 0.005)
        self.damage_flash = 0  # frames remaining of mining flash
        # Pre-compute irregular polygon offsets
        self._poly_offsets = self._generate_irregular_offsets()
        # Procedural surface speckles (cached per-instance)
        self._surface_detail = self._generate_surface_detail()
        # Sparkle phase
        self._sparkle_phase = random.uniform(0, math.pi * 2)

    def _generate_irregular_offsets(self):
        offsets = []
        rng = random.Random(int(self.x * 13 + self.y * 7))
        for i in range(8):
            angle = i * math.pi / 4
            r = (self.size / 2) * rng.uniform(0.85, 1.15)
            offsets.append((angle, r))
        return offsets

    def _generate_surface_detail(self):
        """Procedural noise-based surface speckles unique per block."""
        rng = random.Random(int(self.x * 23 + self.y * 41 + 7))
        details = []
        for _ in range(6):
            ang = rng.uniform(0, math.pi * 2)
            r = rng.uniform(0, self.size * 0.35)
            shade = rng.uniform(0.5, 0.85)
            sz = rng.choice([1, 1, 1, 2])
            details.append((ang, r, shade, sz))
        return details

    def render(self, surface, camera_x, camera_y):
        screen_x = int(self.x - camera_x)
        screen_y = int(self.y - camera_y)
        from systems.accessibility import colorblind_filter

        colors = {
            'IRON': (169, 169, 169),
            'GOLD': (255, 215, 0),
            'CRYSTAL': (138, 43, 226),
            'FUEL': (255, 165, 0),
            'OXYGEN': (135, 206, 235),
        }
        base_color = colors.get(self.block_type, GRAY)
        color = (
            max(0, min(255, int(base_color[0] * self.brightness))),
            max(0, min(255, int(base_color[1] * self.brightness))),
            max(0, min(255, int(base_color[2] * self.brightness))),
        )
        color = colorblind_filter(color)

        # Irregular polygon body
        self.rotation += self.rotation_speed
        pts = []
        for ang, r in self._poly_offsets:
            a = ang + self.rotation
            pts.append((screen_x + math.cos(a) * r, screen_y + math.sin(a) * r))
        pygame.draw.polygon(surface, color, pts)

        # Damage cracks - drawn proportional to missing health
        damage_ratio = 1.0 - (self.health / max(self.max_health, 1))
        if damage_ratio > 0.1:
            n_cracks = int(1 + damage_ratio * 4)
            crack_rng = random.Random(int(self.x * 17 + self.y * 3))
            for _ in range(n_cracks):
                a1 = crack_rng.uniform(0, math.pi * 2)
                a2 = a1 + crack_rng.uniform(0.5, 1.5)
                r = self.size / 2
                p1 = (screen_x + math.cos(a1) * r, screen_y + math.sin(a1) * r)
                p2 = (screen_x + math.cos(a2) * r * 0.4, screen_y + math.sin(a2) * r * 0.4)
                pygame.draw.line(surface, (0, 0, 0), p1, p2, 1)

        # Procedural speckles (noise detail — gives each block a unique surface)
        for ang_off, r_off, shade, sz in self._surface_detail:
            a = ang_off + self.rotation * 0.3
            dx = math.cos(a) * r_off
            dy = math.sin(a) * r_off
            sc = (int(color[0] * shade), int(color[1] * shade), int(color[2] * shade))
            if sz == 1:
                surface.set_at((int(screen_x + dx), int(screen_y + dy)), sc)
            else:
                pygame.draw.circle(surface, sc, (int(screen_x + dx), int(screen_y + dy)), 1)

        # Border
        pygame.draw.polygon(surface, (240, 240, 240), pts, 1)

        # Sparkle on crystal/gold
        if self.block_type in ('CRYSTAL', 'GOLD'):
            self._sparkle_phase += 0.05
            twinkle = (math.sin(self._sparkle_phase) + 1) * 0.5
            sparkle_color = (255, 255, 255) if self.block_type == 'CRYSTAL' else (255, 230, 100)
            r = int(2 + twinkle * 2)
            pygame.draw.circle(surface, sparkle_color, (screen_x, screen_y - 2), r)

        # Mining hit flash
        if self.damage_flash > 0:
            flash_alpha = int(220 * self.damage_flash / 6)
            flash_surf = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
            pygame.draw.circle(flash_surf, (255, 255, 200, flash_alpha),
                               (self.size, self.size), self.size)
            surface.blit(flash_surf, (screen_x - self.size, screen_y - self.size))
            self.damage_flash -= 1

    def take_damage(self, damage):
        self.health = max(0, self.health - damage)
        self.damage_flash = 6
        return self.health <= 0

    def collect(self):
        if not self.collected and self.health <= 0:
            self.collected = True
            return RESOURCE_TYPES[self.block_type]['value']
        return 0
