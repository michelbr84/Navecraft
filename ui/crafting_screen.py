"""
Crafting screen - lists recipes with cost preview, color-coded affordability.
"""

import pygame
from utils import display
from utils.font import get_font, draw_panel, render_outlined


class CraftingScreen:
    def __init__(self):
        self.visible = False
        self.selected = 0
        self.queue = []  # crafted items pending

    def toggle(self):
        self.visible = not self.visible

    def handle_event(self, event, crafting_system, audio=None):
        if not self.visible:
            return False
        if event.type == pygame.KEYDOWN:
            recipes = list(crafting_system.recipes.keys())
            if event.key in (pygame.K_ESCAPE, pygame.K_c):
                self.visible = False
                return True
            elif event.key in (pygame.K_UP, pygame.K_w):
                self.selected = (self.selected - 1) % len(recipes)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.selected = (self.selected + 1) % len(recipes)
            elif event.key == pygame.K_RETURN:
                recipe = recipes[self.selected]
                if crafting_system.craft_item(recipe):
                    self.queue.append(recipe)
                    if audio:
                        audio.play_sound('collect')
                    return True
            return True
        return False

    def render(self, surface, crafting_system):
        if not self.visible:
            return
        w, h = display.WIDTH, display.HEIGHT
        overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))

        panel_w = min(680, w - 80)
        panel_h = min(520, h - 80)
        panel_x = (w - panel_w) // 2
        panel_y = (h - panel_h) // 2
        rect = pygame.Rect(panel_x, panel_y, panel_w, panel_h)
        draw_panel(surface, rect, bg=(10, 30, 30), border=(0, 220, 220), bg_alpha=220, border_width=2, radius=10)

        title = render_outlined(get_font(32), "CRAFTING", (255, 255, 255), (0, 0, 0), 2)
        surface.blit(title, (panel_x + 20, panel_y + 16))

        recipes = list(crafting_system.recipes.items())
        for i, (name, ingredients) in enumerate(recipes):
            y = panel_y + 70 + i * 70
            selected = i == self.selected
            color = (255, 220, 100) if selected else (255, 255, 255)
            name_text = render_outlined(get_font(22), name, color, (0, 0, 0), 1)
            surface.blit(name_text, (panel_x + 30, y))
            # Cost
            cost_parts = []
            affordable = True
            for item, qty in ingredients.items():
                have = crafting_system.inventory.get_item_count(item)
                col = "OK" if have >= qty else "X"
                if have < qty:
                    affordable = False
                cost_parts.append(f"{item}:{have}/{qty}{col}")
            cost_text = render_outlined(get_font(16), " | ".join(cost_parts),
                                        (100, 255, 100) if affordable else (255, 100, 100), (0, 0, 0), 1)
            surface.blit(cost_text, (panel_x + 30, y + 30))

        # Queue
        if self.queue:
            queue_text = render_outlined(get_font(16), "Fila: " + ", ".join(self.queue[-5:]),
                                         (200, 200, 200), (0, 0, 0), 1)
            surface.blit(queue_text, (panel_x + 20, panel_y + panel_h - 30))

        hint = render_outlined(get_font(14), "ENTER=craft  SETAS=navegar  ESC=fechar", (180, 180, 180), (0, 0, 0), 1)
        surface.blit(hint, (panel_x + panel_w - hint.get_width() - 10, panel_y + panel_h - 22))
