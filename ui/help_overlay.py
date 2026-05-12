"""
Help overlay (H key) - lists all controls grouped by category.
"""

import pygame
from utils import display
from utils.font import get_font, draw_panel, render_outlined
from utils.i18n import t


class HelpOverlay:
    def __init__(self):
        self.visible = False

    def toggle(self):
        self.visible = not self.visible

    def handle_event(self, event):
        if not self.visible:
            return False
        if event.type == pygame.KEYDOWN and event.key in (pygame.K_h, pygame.K_ESCAPE):
            self.visible = False
            return True
        return False

    def render(self, surface):
        if not self.visible:
            return
        w, h = display.WIDTH, display.HEIGHT
        overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        surface.blit(overlay, (0, 0))

        panel_w = min(820, w - 60)
        panel_h = min(620, h - 60)
        px = (w - panel_w) // 2
        py = (h - panel_h) // 2
        draw_panel(surface, pygame.Rect(px, py, panel_w, panel_h),
                   bg=(10, 10, 40), border=(0, 220, 255), bg_alpha=235, border_width=2, radius=10)

        title = render_outlined(get_font(36), t('help.title'), (255, 255, 255), (0, 0, 0), 2)
        surface.blit(title, (px + (panel_w - title.get_width()) // 2, py + 16))

        sections = [
            (t('help.movement'), [
                ("WASD / Setas", "Mover a nave"),
                ("ESPACO", "Atirar"),
            ]),
            (t('help.actions'), [
                ("E", "Minerar (alcance ~50px)"),
                ("Q", "Construir (posição do mouse)"),
                ("1-5", "Selecionar bloco IRON/GOLD/CRYSTAL/FUEL/OXYGEN"),
                ("M", "Aceitar missão / abrir mapa"),
                ("B", "Construir estação espacial"),
                ("I", "Inventário"),
                ("C", "Tela de Crafting"),
            ]),
            (t('help.craft'), [
                ("R", "Repair Kit"),
                ("T", "Energy Pack"),
                ("Y", "Oxygen Tank"),
                ("U", "Shield Booster"),
            ]),
            (t('help.upgrade'), [
                ("F1-F6", "Engine, Shield, Energy, Mining, Oxygen, Fuel"),
            ]),
            (t('help.system'), [
                ("ESC", "Pausa"),
                ("F11", "Tela cheia"),
                ("F10", "Borderless"),
                ("F9", "Quick save"),
                ("F8", "Quick load"),
                ("F7 / F8", "Multiplayer toggle / add player"),
                ("F3", "Debug profiler"),
                ("F12", "Modo foto"),
                ("H", "Esta tela de ajuda"),
                ("TAB", "Pular tutorial"),
            ]),
        ]

        col_w = (panel_w - 40) // 2
        x_cols = [px + 20, px + 20 + col_w]
        y_cur = [py + 80, py + 80]
        for idx, (heading, lines) in enumerate(sections):
            col = idx % 2
            cx = x_cols[col]
            cy = y_cur[col]
            head = render_outlined(get_font(22), heading, (0, 220, 255), (0, 0, 0), 1)
            surface.blit(head, (cx, cy))
            cy += 30
            for key, desc in lines:
                key_text = render_outlined(get_font(16), key, (255, 255, 100), (0, 0, 0), 1)
                desc_text = render_outlined(get_font(16), desc, (220, 220, 220), (0, 0, 0), 1)
                surface.blit(key_text, (cx, cy))
                surface.blit(desc_text, (cx + 120, cy))
                cy += 22
            y_cur[col] = cy + 16

        hint = render_outlined(get_font(16), t('help.close'), (180, 180, 180), (0, 0, 0), 1)
        surface.blit(hint, (px + (panel_w - hint.get_width()) // 2, py + panel_h - 28))
