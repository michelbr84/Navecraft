"""
Speedrun timer - millisecond-precision timer with split tracking.
"""

import time


class SpeedrunTimer:
    def __init__(self):
        self.enabled = False
        self.start_at = None
        self.splits = []

    def toggle(self):
        if not self.enabled:
            self.enabled = True
            self.start_at = time.time()
            self.splits.clear()
        else:
            self.enabled = False

    def reset(self):
        self.start_at = time.time()
        self.splits.clear()

    def elapsed(self):
        if self.start_at is None:
            return 0.0
        return time.time() - self.start_at

    def split(self, label):
        self.splits.append((label, self.elapsed()))

    def format_time(self, t=None):
        if t is None:
            t = self.elapsed()
        m = int(t // 60)
        s = int(t % 60)
        ms = int((t - int(t)) * 1000)
        return f"{m:02d}:{s:02d}.{ms:03d}"


speedrun = SpeedrunTimer()
