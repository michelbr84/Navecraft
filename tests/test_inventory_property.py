"""
Property-based tests for inventory math invariants.

Properties checked under random op sequences:
  add+remove cancels exactly.
  remove without enough quantity fails and leaves inventory unchanged.
  count is always >= 0.
  has_item is monotonic with count.
  total never exceeds slots * max_stack.
"""

import os
os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')

import random
import unittest
import pygame

pygame.init()
pygame.display.set_mode((1, 1))

from systems.inventory import Inventory


ITEMS = ('IRON', 'GOLD', 'CRYSTAL', 'FUEL', 'OXYGEN', 'REPAIR_KIT')


def _snapshot(inv):
    return dict(inv.items)


class TestInventoryProperties(unittest.TestCase):

    def test_add_then_remove_cancels(self):
        rng = random.Random(0xC0FFEE)
        for _ in range(100):
            inv = Inventory()
            before = _snapshot(inv)
            item = rng.choice(ITEMS)
            qty = rng.randint(1, 50)
            inv.add_item(item, qty)
            ok = inv.remove_item(item, qty)
            self.assertTrue(ok)
            after = _snapshot(inv)
            # Counts must match across operations.
            self.assertEqual(before.get(item, 0), after.get(item, 0))

    def test_remove_more_than_available_fails_safely(self):
        rng = random.Random(0xBEEF)
        for _ in range(100):
            inv = Inventory()
            item = rng.choice(ITEMS)
            have = inv.get_item_count(item)
            tried = have + rng.randint(1, 30)
            ok = inv.remove_item(item, tried)
            self.assertFalse(ok)
            # Inventory must be unchanged.
            self.assertEqual(inv.get_item_count(item), have)

    def test_counts_never_negative(self):
        rng = random.Random(0xCAFE)
        inv = Inventory()
        for _ in range(500):
            op = rng.choice(['add', 'remove'])
            item = rng.choice(ITEMS)
            qty = rng.randint(1, 10)
            if op == 'add':
                inv.add_item(item, qty)
            else:
                inv.remove_item(item, qty)
            for it in ITEMS:
                self.assertGreaterEqual(inv.get_item_count(it), 0)

    def test_has_item_consistent_with_count(self):
        rng = random.Random(0xDEAD)
        inv = Inventory()
        for _ in range(200):
            item = rng.choice(ITEMS)
            qty = rng.randint(1, 20)
            inv.add_item(item, qty)
            cnt = inv.get_item_count(item)
            # has_item(item, n) iff cnt >= n.
            for n in (0, 1, cnt, cnt + 1, cnt * 2 + 1):
                self.assertEqual(inv.has_item(item, n), cnt >= n)

    def test_stack_cap_respected(self):
        inv = Inventory()
        inv.add_item('IRON', 10_000_000)
        self.assertLessEqual(inv.get_item_count('IRON'), inv.max_stack)


if __name__ == '__main__':
    unittest.main()
