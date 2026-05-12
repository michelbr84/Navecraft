"""
Replay recording - logs ship position at fixed intervals; can play back as a ghost trail.
"""

import json
import os
import time


class ReplaySystem:
    def __init__(self):
        self.recording = False
        self.playback = False
        self.frames = []  # list of (t, x, y, angle)
        self.start_time = 0.0
        self.playback_idx = 0
        self.playback_start = 0.0

    def start_recording(self):
        self.recording = True
        self.playback = False
        self.frames = []
        self.start_time = time.time()

    def stop_recording(self):
        self.recording = False

    def record(self, spaceship):
        if not self.recording or not spaceship:
            return
        t = time.time() - self.start_time
        self.frames.append((t, spaceship.x, spaceship.y, spaceship.angle))

    def save(self, filename="navecraft_replay.json"):
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump({'frames': self.frames, 'duration': self.frames[-1][0] if self.frames else 0}, f)
            return True
        except Exception:
            return False

    def load(self, filename="navecraft_replay.json"):
        if not os.path.exists(filename):
            return False
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.frames = [tuple(fr) for fr in data.get('frames', [])]
            return True
        except Exception:
            return False

    def start_playback(self):
        if not self.frames:
            return False
        self.playback = True
        self.playback_idx = 0
        self.playback_start = time.time()
        return True

    def current_ghost(self):
        """Return (x,y,angle) for the ghost at current playback time, or None."""
        if not self.playback or not self.frames:
            return None
        t = time.time() - self.playback_start
        # find nearest frame
        while (self.playback_idx + 1 < len(self.frames)
               and self.frames[self.playback_idx + 1][0] <= t):
            self.playback_idx += 1
        if self.playback_idx >= len(self.frames):
            self.playback = False
            return None
        _, x, y, ang = self.frames[self.playback_idx]
        return x, y, ang


replay = ReplaySystem()
