"""
Polished menus - animated planet background, hover-anim selection, fade transitions,
title with gradient. Includes Main, Pause, GameOver menus.
"""

import math
import random
import time
import pygame
from utils import display
from utils.font import get_font, draw_panel, render_outlined
from utils.i18n import t


class Menu:
    """Main menu (current_menu = 'main'/'settings'/'about')."""

    def __init__(self):
        self.current_menu = "main"
        self.parent_menu = "main"
        self.selected_option = 0
        self.menu_options = {
            "main": [
                ("menu.play", "play"),
                ("menu.load", "load"),
                ("menu.settings", "settings"),
                ("menu.about", "about"),
                ("menu.quit", "quit"),
            ],
            "pause": [
                ("menu.continue", "continue"),
                ("menu.settings", "settings"),
                ("menu.main", "main_menu"),
                ("menu.quit", "quit"),
            ],
            "settings": [
                ("settings.master_volume", "volume"),
                ("settings.fullscreen", "fullscreen"),
                ("menu.back", "back"),
            ],
            "about": [("menu.back", "back")],
        }
        self.start_time = time.time()
        self._planet_phase = 0.0
        self._stars = [(random.uniform(0, 4000), random.uniform(0, 4000), random.randint(80, 255))
                       for _ in range(180)]
        self._scroll = 0.0
        self._hover_scale = {}

    def handle_input(self, event):
        if event.type != pygame.KEYDOWN:
            return None
        opts = self.menu_options[self.current_menu]
        if event.key == pygame.K_UP:
            self.selected_option = (self.selected_option - 1) % len(opts)
        elif event.key == pygame.K_DOWN:
            self.selected_option = (self.selected_option + 1) % len(opts)
        elif event.key == pygame.K_RETURN:
            return self.select_option()
        elif event.key == pygame.K_ESCAPE:
            if self.current_menu == "pause":
                return "continue"
            elif self.current_menu == "settings":
                self.current_menu = self.parent_menu
                self.selected_option = 0
            elif self.current_menu == "about":
                self.current_menu = "main"
                self.selected_option = 0
        return None

    def select_option(self):
        opts = self.menu_options[self.current_menu]
        if self.selected_option >= len(opts):
            return None
        _, action = opts[self.selected_option]
        if action == "settings":
            self.parent_menu = self.current_menu
            self.current_menu = "settings"
            self.selected_option = 0
            return None
        if action == "about":
            self.current_menu = "about"
            self.selected_option = 0
            return None
        if action == "back":
            target = self.parent_menu if self.current_menu == "settings" else "main"
            self.current_menu = target
            self.selected_option = 0
            return None
        return action

    def set_menu(self, name):
        self.current_menu = name
        self.selected_option = 0

    # ----- rendering -----
    def render(self, surface):
        # Animated background
        self._render_background(surface)
        # Title
        title = render_outlined(get_font(56), "NAVECRAFT", (220, 240, 255), (0, 0, 0), 3)
        glow = self._title_glow_surface(title)
        glow_rect = glow.get_rect(center=(display.WIDTH // 2, 100))
        surface.blit(glow, glow_rect)
        title_rect = title.get_rect(center=(display.WIDTH // 2, 100))
        surface.blit(title, title_rect)
        sub = render_outlined(get_font(24), t('menu.subtitle'), (100, 200, 220), (0, 0, 0), 2)
        sub_rect = sub.get_rect(center=(display.WIDTH // 2, 150))
        surface.blit(sub, sub_rect)

        # Menu options
        opts = self.menu_options[self.current_menu]
        if self.current_menu == "about":
            self._render_about(surface)
        else:
            for i, (key, _) in enumerate(opts):
                self._hover_scale.setdefault(i, 1.0)
                target_scale = 1.15 if i == self.selected_option else 1.0
                self._hover_scale[i] += (target_scale - self._hover_scale[i]) * 0.2
                color = (255, 230, 50) if i == self.selected_option else (255, 255, 255)
                font_size = int(28 * self._hover_scale[i])
                text = render_outlined(get_font(font_size), t(key), color, (0, 0, 0), 2)
                rect = text.get_rect(center=(display.WIDTH // 2, 250 + i * 50))
                if i == self.selected_option:
                    arrow = render_outlined(get_font(24), ">", color, (0, 0, 0), 1)
                    surface.blit(arrow, (rect.left - 30, rect.centery - arrow.get_height() // 2))
                surface.blit(text, rect)

        # Help footer
        if self.current_menu == "main":
            hint = render_outlined(get_font(14),
                                   "WASD/Setas mover  E=minerar  Q=construir  H=ajuda  M=mapa  K=codex  F11=tela cheia",
                                   (180, 200, 220), (0, 0, 0), 1)
            surface.blit(hint, ((display.WIDTH - hint.get_width()) // 2, display.HEIGHT - 30))

    def _render_about(self, surface):
        lines = [
            "Navecraft — Minecraft no Espaço",
            "",
            "Jogo de sobrevivência e exploração espacial",
            "100% procedural: gráficos, sons e mundo gerados por código.",
            "",
            "Controle uma nave, explore planetas, minere e sobreviva!",
            "",
            "Desenvolvido em Python + Pygame",
            "github.com/michelbr84/Navecraft",
        ]
        for i, line in enumerate(lines):
            color = (0, 220, 255) if i == 0 else (220, 230, 240)
            font = get_font(22 if i == 0 else 16)
            text = render_outlined(font, line, color, (0, 0, 0), 1)
            surface.blit(text, ((display.WIDTH - text.get_width()) // 2, 200 + i * 28))
        back_hint = render_outlined(get_font(16), "[ENTER ou ESC voltar]", (200, 200, 200), (0, 0, 0), 1)
        surface.blit(back_hint, ((display.WIDTH - back_hint.get_width()) // 2, display.HEIGHT - 60))

    def _render_background(self, surface):
        # Space gradient bg
        surface.fill((6, 8, 28))
        # Drifting stars
        self._scroll += 0.4
        for sx, sy, brightness in self._stars:
            lx = (sx - self._scroll) % 4000
            ly = sy % 4000
            x = int(lx % display.WIDTH)
            y = int(ly % display.HEIGHT)
            surface.set_at((x, y), (brightness, brightness, brightness))
        # Animated planet bottom-left
        self._planet_phase += 0.005
        cx = int(display.WIDTH * 0.25)
        cy = int(display.HEIGHT * 0.75)
        radius = int(min(display.WIDTH, display.HEIGHT) * 0.18)
        for i in range(radius, 0, -3):
            alpha = i / radius
            r_col = int(80 + 50 * math.sin(self._planet_phase + i * 0.05))
            g_col = int(100 + 60 * math.cos(self._planet_phase + i * 0.04))
            b_col = int(200 + 40 * math.sin(self._planet_phase * 2 + i * 0.03))
            col = (max(0, min(255, int(r_col * alpha))),
                   max(0, min(255, int(g_col * alpha))),
                   max(0, min(255, int(b_col * alpha))))
            pygame.draw.circle(surface, col, (cx, cy), i)
        pygame.draw.circle(surface, (200, 220, 255), (cx, cy), radius, 1)

    def _title_glow_surface(self, title_surface):
        glow = pygame.Surface(title_surface.get_size(), pygame.SRCALPHA)
        glow.fill((0, 220, 255, 30))
        for _ in range(3):
            glow.blit(title_surface, (0, 0))
        return glow


class PauseMenu(Menu):
    def __init__(self):
        super().__init__()
        self.current_menu = "pause"
        self.parent_menu = "pause"

    def render(self, surface):
        # Dark overlay (blur-ish by drawing a translucent rect)
        overlay = pygame.Surface((display.WIDTH, display.HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        surface.blit(overlay, (0, 0))

        title = render_outlined(get_font(48), t('menu.paused'), (255, 255, 255), (0, 0, 0), 3)
        rect = title.get_rect(center=(display.WIDTH // 2, 160))
        surface.blit(title, rect)

        opts = self.menu_options[self.current_menu]
        for i, (key, _) in enumerate(opts):
            self._hover_scale.setdefault(i, 1.0)
            target_scale = 1.15 if i == self.selected_option else 1.0
            self._hover_scale[i] += (target_scale - self._hover_scale[i]) * 0.2
            color = (255, 230, 50) if i == self.selected_option else (255, 255, 255)
            font_size = int(28 * self._hover_scale[i])
            text = render_outlined(get_font(font_size), t(key), color, (0, 0, 0), 2)
            r = text.get_rect(center=(display.WIDTH // 2, 280 + i * 50))
            surface.blit(text, r)


class GameOverMenu(Menu):
    def __init__(self):
        super().__init__()
        self.current_menu = "game_over"
        self.menu_options["game_over"] = [
            ("menu.restart", "restart"),
            ("menu.main", "main_menu"),
            ("menu.quit", "quit"),
        ]

    def select_option(self):
        opts = self.menu_options["game_over"]
        if self.selected_option < len(opts):
            return opts[self.selected_option][1]
        return None

    def render(self, surface, score=0):
        overlay = pygame.Surface((display.WIDTH, display.HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        surface.blit(overlay, (0, 0))
        title = render_outlined(get_font(56), t('menu.game_over'), (255, 50, 50), (0, 0, 0), 3)
        rect = title.get_rect(center=(display.WIDTH // 2, 180))
        surface.blit(title, rect)
        score_text = render_outlined(get_font(28), f"{t('hud.score')}: {score}",
                                     (255, 255, 100), (0, 0, 0), 2)
        rect = score_text.get_rect(center=(display.WIDTH // 2, 250))
        surface.blit(score_text, rect)
        opts = self.menu_options[self.current_menu]
        for i, (key, _) in enumerate(opts):
            color = (255, 220, 50) if i == self.selected_option else (255, 255, 255)
            text = render_outlined(get_font(28), t(key), color, (0, 0, 0), 2)
            r = text.get_rect(center=(display.WIDTH // 2, 330 + i * 50))
            surface.blit(text, r)
