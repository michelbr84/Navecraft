"""
Procedural audio - ADSR envelopes, per-enemy SFX, panning + falloff, adaptive music.
"""

import math
import random
import numpy as np
import pygame
from settings import SAMPLE_RATE
from utils import config


def _adsr(samples_n, attack=0.05, decay=0.1, sustain=0.7, release=0.2):
    """ADSR envelope as a numpy array of length samples_n."""
    a = int(samples_n * attack)
    d = int(samples_n * decay)
    r = int(samples_n * release)
    s = samples_n - (a + d + r)
    if s < 0:
        s = max(0, samples_n - (a + d + r))
    env = np.zeros(samples_n)
    if a > 0:
        env[:a] = np.linspace(0, 1, a)
    if d > 0:
        env[a:a + d] = np.linspace(1, sustain, d)
    if s > 0:
        env[a + d:a + d + s] = sustain
    if r > 0:
        env[a + d + s:a + d + s + r] = np.linspace(sustain, 0, r)
    return env


def _to_stereo(wave):
    if wave.max() == 0:
        wave = wave + 1e-9
    peak = max(np.abs(wave).max(), 0.01)
    wave = wave / peak * 0.9
    out = (wave * 32767).astype(np.int16)
    stereo = np.column_stack((out, out))
    return pygame.sndarray.make_sound(stereo)


def _stereo_panned(left, right):
    peak = max(np.abs(left).max(), np.abs(right).max(), 0.01)
    left = (left / peak * 0.9 * 32767).astype(np.int16)
    right = (right / peak * 0.9 * 32767).astype(np.int16)
    return pygame.sndarray.make_sound(np.column_stack((left, right)))


class AudioSystem:
    def __init__(self):
        self.sounds = {}
        self.variants = {}  # name -> [Sound, Sound, ...] for variation
        self.sfx_enabled = False
        self.music_enabled = True
        self.master_volume = 1.0
        self.sfx_volume = 1.0
        self.music_volume = 0.6
        self.ambient_volume = 0.4
        self.ui_volume = 0.7
        self.refresh_volumes()
        try:
            self._build_sounds()
            self.sfx_enabled = True
        except Exception as e:
            print(f"[audio] init failed: {e}")
        self._music_channel = None
        self._ambient_channel = None
        self._combat_intensity = 0.0  # 0..1, drives music switching
        self._music_calm = None
        self._music_combat = None
        try:
            self._music_calm = self._make_music(combat=False)
            self._music_combat = self._make_music(combat=True)
        except Exception:
            pass

    # ----- configuration -----
    def refresh_volumes(self):
        self.master_volume = float(config.get('audio', 'master', default=0.8))
        self.sfx_volume = float(config.get('audio', 'sfx', default=0.8))
        self.music_volume = float(config.get('audio', 'music', default=0.6))
        self.ambient_volume = float(config.get('audio', 'ambient', default=0.5))
        self.ui_volume = float(config.get('audio', 'ui', default=0.7))

    # ----- sound generation -----
    def _make_tone(self, freq, dur, attack=0.05, decay=0.1, sustain=0.7, release=0.2, wave='sine', amp=0.3, freq_end=None):
        n = int(SAMPLE_RATE * dur)
        t = np.linspace(0, dur, n)
        if freq_end is not None:
            f = np.linspace(freq, freq_end, n)
        else:
            f = freq
        phase = 2 * np.pi * f * t
        if wave == 'sine':
            w = np.sin(phase)
        elif wave == 'square':
            w = np.sign(np.sin(phase))
        elif wave == 'tri':
            w = (2 / np.pi) * np.arcsin(np.sin(phase))
        elif wave == 'saw':
            w = 2 * (t * f - np.floor(0.5 + t * f))
        elif wave == 'noise':
            w = np.random.uniform(-1, 1, n)
        else:
            w = np.sin(phase)
        env = _adsr(n, attack, decay, sustain, release)
        return amp * w * env

    def _build_sounds(self):
        # Laser / shoot
        wave = self._make_tone(900, 0.12, attack=0.01, decay=0.05, sustain=0.5, release=0.06, wave='square', amp=0.35, freq_end=300)
        self.sounds['shoot'] = _to_stereo(wave)
        self.sounds['laser'] = self.sounds['shoot']
        self.variants['shoot'] = [
            _to_stereo(self._make_tone(800 + 50 * i, 0.12, wave='square', amp=0.3, freq_end=260 + 30 * i)) for i in range(3)
        ]

        # Mine - rough triangular with low rumble
        m = self._make_tone(320, 0.18, attack=0.02, decay=0.06, sustain=0.6, release=0.1, wave='tri', amp=0.3)
        m += self._make_tone(120, 0.18, wave='sine', amp=0.15)
        self.sounds['mine'] = _to_stereo(m)
        self.variants['mine'] = [
            _to_stereo(self._make_tone(300 + 30 * i, 0.18, wave='tri', amp=0.3)) for i in range(3)
        ]

        # Collect - rising chime
        wave = self._make_tone(440, 0.18, attack=0.01, decay=0.07, sustain=0.5, release=0.1, wave='sine', amp=0.3, freq_end=880)
        wave += self._make_tone(660, 0.18, wave='sine', amp=0.12, freq_end=1320)
        self.sounds['collect'] = _to_stereo(wave)

        # Build - dual-tone confirm
        wave = self._make_tone(500, 0.12, wave='sine', amp=0.25)
        wave += self._make_tone(750, 0.12, wave='sine', amp=0.2)
        self.sounds['build'] = _to_stereo(wave)

        # Explosion - filtered white noise with pitch drop
        n = int(SAMPLE_RATE * 0.5)
        noise = np.random.uniform(-1, 1, n)
        env = np.exp(-3 * np.linspace(0, 0.5, n))
        rumble = self._make_tone(80, 0.5, wave='sine', amp=0.3, freq_end=40)
        self.sounds['explosion'] = _to_stereo(noise * env * 0.5 + rumble)

        # Thrust - low whoosh
        wave = self._make_tone(200, 0.08, wave='noise', amp=0.18)
        self.sounds['thrust'] = _to_stereo(wave)

        # Per-enemy hit/death distinctive sounds
        self.sounds['hit_drone'] = _to_stereo(self._make_tone(700, 0.08, wave='square', amp=0.25, freq_end=400))
        self.sounds['hit_android'] = _to_stereo(self._make_tone(280, 0.12, wave='tri', amp=0.3))
        self.sounds['hit_sniper'] = _to_stereo(self._make_tone(1200, 0.06, wave='sine', amp=0.25, freq_end=600))
        self.sounds['hit_arachnoid'] = _to_stereo(self._make_tone(400, 0.1, wave='saw', amp=0.25))
        self.sounds['hit_boss'] = _to_stereo(self._make_tone(180, 0.18, wave='tri', amp=0.4))

        # UI - click, hover, confirm, cancel
        self.sounds['ui_click'] = _to_stereo(self._make_tone(900, 0.05, wave='sine', amp=0.2))
        self.sounds['ui_hover'] = _to_stereo(self._make_tone(1200, 0.03, wave='sine', amp=0.12))
        self.sounds['ui_confirm'] = _to_stereo(self._make_tone(600, 0.12, wave='sine', amp=0.22, freq_end=1200))
        self.sounds['ui_cancel'] = _to_stereo(self._make_tone(440, 0.1, wave='tri', amp=0.18, freq_end=220))

        # Alerts (visual cue companions)
        self.sounds['alert_low'] = _to_stereo(self._make_tone(700, 0.2, wave='square', amp=0.25))
        self.sounds['alert_critical'] = _to_stereo(self._make_tone(1500, 0.15, wave='square', amp=0.3, freq_end=800))

        # Damage taken
        self.sounds['damage'] = _to_stereo(self._make_tone(220, 0.18, wave='saw', amp=0.3, freq_end=80))

        # Boss appearance stinger
        wave = self._make_tone(120, 0.6, wave='saw', amp=0.4)
        wave += self._make_tone(180, 0.6, wave='sine', amp=0.2)
        self.sounds['stinger_boss'] = _to_stereo(wave)

    def _make_music(self, combat=False):
        duration = 8.0
        n = int(SAMPLE_RATE * duration)
        t = np.linspace(0, duration, n)
        wave = np.zeros(n)
        if not combat:
            # Calm pentatonic
            notes = [220, 246, 277, 329, 370]
            step = 0.7
            amp = 0.08
        else:
            # Combat - more energy, lower notes, rhythmic
            notes = [110, 130, 155, 175, 196]
            step = 0.25
            amp = 0.12
        for i, freq in enumerate(notes * 4):
            start = int(i * step * SAMPLE_RATE)
            end = int((i * step + step) * SAMPLE_RATE)
            if end > n:
                end = n
            seg_t = np.linspace(0, step, end - start)
            tone = np.sin(2 * np.pi * freq * seg_t) * amp
            env = np.exp(-2 * seg_t / step)
            wave[start:end] += tone * env
            if combat:
                # Add bass thump on each beat
                bass = np.sin(2 * np.pi * 55 * seg_t) * 0.08 * np.exp(-6 * seg_t / step)
                wave[start:end] += bass
        return _to_stereo(wave)

    # ----- playback -----
    def play_sound(self, name, pan=0.0, volume_mult=1.0, ui=False, variant=False):
        if not self.sfx_enabled:
            return
        snd = None
        if variant and name in self.variants and self.variants[name]:
            snd = random.choice(self.variants[name])
        elif name in self.sounds:
            snd = self.sounds[name]
        if snd is None:
            return
        try:
            base = self.ui_volume if ui else self.sfx_volume
            vol = max(0.0, min(1.0, self.master_volume * base * volume_mult))
            ch = snd.play()
            if ch is not None:
                # Pan: -1..1 mapped to L=1-x, R=1+x
                left = max(0.0, min(1.0, vol * (1.0 - max(0.0, pan))))
                right = max(0.0, min(1.0, vol * (1.0 + min(0.0, pan))))
                # Pygame stereo set_volume(left,right) supported on some versions
                try:
                    ch.set_volume(left, right)
                except TypeError:
                    ch.set_volume(vol)
        except Exception:
            pass

    def play_at(self, name, source_x, source_y, listener_x, listener_y, max_dist=600, ui=False, variant=False):
        """Position-aware play - falloff + stereo pan based on relative position."""
        dx = source_x - listener_x
        dy = source_y - listener_y
        dist = math.hypot(dx, dy)
        if dist > max_dist:
            return
        vol = 1.0 - (dist / max_dist) ** 1.5
        pan = max(-1.0, min(1.0, dx / max_dist))
        # Low-pass when far (simulate by amplitude only - simple)
        self.play_sound(name, pan=pan, volume_mult=vol, ui=ui, variant=variant)

    # ----- music -----
    def play_music(self):
        if not self.music_enabled or self._music_calm is None:
            return
        try:
            self._music_channel = self._music_calm.play(loops=-1)
            if self._music_channel:
                self._music_channel.set_volume(self.master_volume * self.music_volume)
        except Exception as e:
            print(f"[audio] music failed: {e}")

    def update_combat_intensity(self, intensity):
        """0..1. Crossfades between calm and combat tracks."""
        if not self.music_enabled or self._music_calm is None or self._music_combat is None:
            return
        target = float(intensity)
        self._combat_intensity += (target - self._combat_intensity) * 0.04
        try:
            calm_vol = self.master_volume * self.music_volume * (1.0 - self._combat_intensity)
            combat_vol = self.master_volume * self.music_volume * self._combat_intensity
            if self._music_channel:
                self._music_channel.set_volume(calm_vol)
            # Start combat track if needed
            if self._combat_intensity > 0.1:
                if not pygame.mixer.find_channel(False):
                    return
                if not getattr(self, '_combat_channel', None):
                    self._combat_channel = self._music_combat.play(loops=-1)
                if self._combat_channel:
                    self._combat_channel.set_volume(combat_vol)
            elif getattr(self, '_combat_channel', None):
                self._combat_channel.set_volume(0)
        except Exception:
            pass

    def stop_music(self):
        if self._music_channel:
            self._music_channel.stop()
        ch = getattr(self, '_combat_channel', None)
        if ch:
            ch.stop()

    # ----- compatibility shims -----
    def toggle_music(self):
        self.music_enabled = not self.music_enabled
        if not self.music_enabled:
            self.stop_music()
        else:
            self.play_music()

    def toggle_sfx(self):
        self.sfx_enabled = not self.sfx_enabled

    def set_volume(self, v):
        config.set('audio', 'master', max(0.0, min(1.0, v)))
        config.save()
        self.refresh_volumes()
