"""
Simple in-game profiler. Tracks named sections, exposes per-frame ms.
Toggled with F3.
"""

import time


class Profiler:
    def __init__(self):
        self.enabled = False
        self.sections = {}
        self._stack = []

    def toggle(self):
        self.enabled = not self.enabled

    def begin(self, name):
        if not self.enabled:
            return
        self._stack.append((name, time.perf_counter()))

    def end(self):
        if not self.enabled or not self._stack:
            return
        name, t0 = self._stack.pop()
        ms = (time.perf_counter() - t0) * 1000.0
        bucket = self.sections.setdefault(name, [0.0, 0])  # [sum_ms, count]
        bucket[0] += ms
        bucket[1] += 1

    def reset(self):
        self.sections.clear()

    def averages(self):
        return [(name, total / count, count) for name, (total, count) in self.sections.items()]


profiler = Profiler()


class _Section:
    def __init__(self, name):
        self.name = name

    def __enter__(self):
        profiler.begin(self.name)
        return self

    def __exit__(self, *_):
        profiler.end()


def section(name):
    return _Section(name)
