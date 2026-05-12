"""
Procedural renderer. Delegates background to systems.background. Adds bloom,
chromatic aberration on hit, and proper ship animation (boost, damage state).
"""

import math
import random
import pygame
from settings import *
from systems.accessibility import colorblind_filter, is_reduce_motion
from systems.background import background
from systems.lighting import lighting


class Renderer:
    def __init__(self):
        # Backwards-compat: provide a particle_system attribute (unused by Game)
        self.particle_system = _LegacyParticleSystem()
        # Frame counter so the engine glow is added every Nth frame instead
        # of every frame — prevents overlapping lights from saturating to white.
        self._engine_light_tick = 0

    def render_stars(self, surface, camera_x=0, camera_y=0):
        """Background = parallax stars + nebulas + distant planets."""
        background.render(surface, camera_x, camera_y)

    def render_spaceship(self, surface, spaceship, camera_x, camera_y):
        if not spaceship:
            return
        screen_x = int(spaceship.x - camera_x)
        screen_y = int(spaceship.y - camera_y)
        # Engine glow / boost trail
        if spaceship.boosting:
            self._render_boost_trail(surface, spaceship, camera_x, camera_y)
        # Body
        self._render_ship_body(surface, spaceship, screen_x, screen_y)
        # Details
        spaceship.render_ship_details(surface, screen_x, screen_y)
        # Damage state (sparks/smoke) when low HP
        if spaceship.health < spaceship.max_health * 0.35:
            self._render_damage_sparks(surface, spaceship, screen_x, screen_y)
        # Shield
        self._render_shield(surface, spaceship, screen_x, screen_y)
        # Hit flash overlay
        if spaceship.hit_flash > 0:
            self._render_hit_flash(surface, spaceship, screen_x, screen_y)
        # Engine light — only re-emit every 4 frames so transient lights
        # don't stack and saturate to white. Intensity is dimmer for ambient
        # cruise and boosted when actively thrusting.
        self._engine_light_tick = (self._engine_light_tick + 1) % 4
        if self._engine_light_tick == 0:
            ex = spaceship.x - math.cos(spaceship.angle) * spaceship.size
            ey = spaceship.y - math.sin(spaceship.angle) * spaceship.size
            base_intensity = 0.55 if spaceship.boosting else 0.30
            lighting.add_transient(ex, ey,
                                   radius=40, color=(120, 180, 255),
                                   intensity=base_intensity, lifetime=14)

    def _render_boost_trail(self, surface, spaceship, cx, cy):
        # Extended cone behind ship
        for i in range(4):
            offset = (i + 1) * 4
            tx = spaceship.x - math.cos(spaceship.angle) * (spaceship.size + offset)
            ty = spaceship.y - math.sin(spaceship.angle) * (spaceship.size + offset)
            sz = max(1, 6 - i)
            color = (int(255 * (1 - i / 4)), int(180 * (1 - i / 4)), 80)
            pygame.draw.circle(surface, color,
                               (int(tx - cx), int(ty - cy)), sz)

    def _render_ship_body(self, surface, spaceship, x, y):
        points = spaceship.get_ship_points(x, y)
        color = colorblind_filter(CYAN)
        # 3-pass gradient triangle
        for i in range(3):
            alpha = i / 2.0
            shade = self._interp(color, (0, 200, 200), alpha)
            pygame.draw.polygon(surface, shade, points)
        pygame.draw.polygon(surface, (255, 255, 255), points, 2)

    def _render_damage_sparks(self, surface, spaceship, x, y):
        if is_reduce_motion():
            return
        for _ in range(2):
            ox = random.randint(-spaceship.size // 2, spaceship.size // 2)
            oy = random.randint(-spaceship.size // 2, spaceship.size // 2)
            pygame.draw.circle(surface, (255, 200, 60),
                               (x + ox, y + oy), random.randint(1, 2))

    def _render_shield(self, surface, spaceship, x, y):
        if spaceship.health < spaceship.max_health:
            shield_alpha = max(0, (spaceship.health / spaceship.max_health) * 255)
            shield_surface = pygame.Surface(
                (spaceship.size + 20, spaceship.size + 20), pygame.SRCALPHA)
            shield_color = (0, 255, 255, int(shield_alpha))
            pygame.draw.circle(shield_surface, shield_color,
                               (spaceship.size // 2 + 10, spaceship.size // 2 + 10),
                               spaceship.size // 2 + 10, 3)
            surface.blit(shield_surface, (x - spaceship.size // 2 - 10, y - spaceship.size // 2 - 10))

    def _render_hit_flash(self, surface, spaceship, x, y):
        alpha = int(180 * spaceship.hit_flash / 8)
        flash = pygame.Surface((spaceship.size * 3, spaceship.size * 3), pygame.SRCALPHA)
        pygame.draw.circle(flash, (255, 80, 80, alpha),
                           (spaceship.size * 3 // 2, spaceship.size * 3 // 2),
                           spaceship.size + 8)
        surface.blit(flash, (x - spaceship.size * 3 // 2, y - spaceship.size * 3 // 2))

    def _interp(self, c1, c2, alpha):
        return (int(c1[0] * (1 - alpha) + c2[0] * alpha),
                int(c1[1] * (1 - alpha) + c2[1] * alpha),
                int(c1[2] * (1 - alpha) + c2[2] * alpha))

    def render_planet(self, surface, planet, camera_x, camera_y):
        """camera_x/camera_y are world-space camera offsets to subtract."""
        screen_x = int(planet.x - camera_x)
        screen_y = int(planet.y - camera_y)
        colors = {
            'ROCK': PLANET_RED, 'ICE': (240, 248, 255), 'GAS': (255, 165, 0),
            'METAL': (192, 192, 192), 'CRYSTAL': (138, 43, 226),
            'LAVA': (255, 69, 0), 'TOXIC': (50, 205, 50), 'RADIOACTIVE': (255, 255, 0),
            'WATER': (0, 191, 255), 'DESERT': (244, 164, 96),
        }
        base_color = colorblind_filter(colors.get(planet.planet_type, PLANET_RED))

        for i in range(planet.radius, 0, -2):
            alpha = i / planet.radius
            color = self._interp(base_color, (0, 0, 0), 1 - alpha)
            pygame.draw.circle(surface, color, (screen_x, screen_y), i)
        pygame.draw.circle(surface, (255, 255, 255), (screen_x, screen_y), planet.radius, 2)
        self._render_surface_detail(surface, planet, screen_x, screen_y)

        # Planet name floats above
        font = pygame.font.Font(None, 16)
        name = getattr(planet, 'name', planet.planet_type)
        text = font.render(name, True, (220, 220, 240))
        surface.blit(text, (screen_x - text.get_width() // 2, screen_y - planet.radius - 18))

    def _render_surface_detail(self, surface, planet, x, y):
        rng = random.Random(int(planet.x) + int(planet.y))
        for _ in range(20):
            angle = rng.uniform(0, math.pi * 2)
            dist = rng.uniform(0, planet.radius * 0.8)
            dx = x + math.cos(angle) * dist
            dy = y + math.sin(angle) * dist
            detail = self._interp((255, 255, 255), (0, 0, 0), rng.uniform(0, 0.5))
            pygame.draw.circle(surface, detail, (int(dx), int(dy)), 1)


class _LegacyParticleSystem:
    def __init__(self):
        self.particles = []

    def add_particle(self, *args, **kwargs):
        pass

    def update(self):
        pass

    def render(self, *args, **kwargs):
        pass
