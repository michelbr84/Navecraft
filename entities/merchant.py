"""
Merchant NPC - trader stations with dynamic supply/demand pricing.

Each merchant carries a per-resource "supply level" sampled from its world
position. Resources the local region is rich in are bought cheap and sold
cheap; resources the region is scarce in command higher prices. This gives
players an incentive to haul goods between merchants.
"""

import math
import random
import pygame


_BASE_BUY = {'IRON': 8, 'GOLD': 30, 'CRYSTAL': 60, 'FUEL': 4, 'OXYGEN': 12}
_BASE_SELL = {'REPAIR_KIT': 5, 'ENERGY_PACK': 6, 'OXYGEN_TANK': 8}


class Merchant:
    def __init__(self, x, y, faction='TRADERS'):
        self.x = x
        self.y = y
        self.size = 36
        self.faction = faction
        self.interaction_range = 80
        # Per-merchant supply factor in [0.6 .. 1.4] seeded by world position.
        rng = random.Random(int(x * 311 + y * 1109))
        # Supply multipliers for each resource (lower = abundant -> cheaper).
        self._supply = {item: rng.uniform(0.6, 1.4) for item in _BASE_BUY}
        # Specialization: one resource is *very* abundant (cheap to sell, low buy price).
        self.specialty = rng.choice(list(_BASE_BUY.keys()))
        self._supply[self.specialty] *= 0.7
        # Compute prices once at construction (stable for a session).
        self.inventory_buy = {
            item: max(1, int(round(_BASE_BUY[item] * self._supply[item])))
            for item in _BASE_BUY
        }
        self.inventory_sell = {
            item: max(1, int(round(_BASE_SELL[item] * rng.uniform(0.85, 1.2))))
            for item in _BASE_SELL
        }

    def in_range_of(self, ship):
        return math.hypot(ship.x - self.x, ship.y - self.y) <= self.interaction_range

    def sell_to_player(self, ship, item):
        """Player buys `item` from merchant for CRYSTAL."""
        price = self.inventory_sell.get(item)
        if price is None:
            return False
        if not ship.inventory.has_item('CRYSTAL', price):
            return False
        ship.inventory.remove_item('CRYSTAL', price)
        ship.inventory.add_item(item, 1)
        return True

    def buy_from_player(self, ship, item, amount=1):
        """Player sells `item` to merchant for CRYSTAL."""
        price_each = self.inventory_buy.get(item)
        if price_each is None:
            return False
        if not ship.inventory.has_item(item, amount):
            return False
        ship.inventory.remove_item(item, amount)
        ship.inventory.add_item('CRYSTAL', price_each * amount)
        return True

    def render(self, surface, camera_x, camera_y):
        sx = int(self.x - camera_x)
        sy = int(self.y - camera_y)
        # Octagonal merchant station
        points = []
        for i in range(8):
            a = i * math.pi / 4
            r = self.size
            points.append((sx + math.cos(a) * r, sy + math.sin(a) * r))
        pygame.draw.polygon(surface, (40, 100, 100), points)
        pygame.draw.polygon(surface, (0, 255, 200), points, 2)
        # $ marker
        font = pygame.font.Font(None, 28)
        text = font.render("$", True, (255, 220, 80))
        rect = text.get_rect(center=(sx, sy))
        surface.blit(text, rect)
