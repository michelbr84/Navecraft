"""
Sistema de áudio procedural do Navecraft
"""

import pygame
import numpy as np
import math
import random
from settings import *

class AudioSystem:
    def __init__(self):
        """Inicializa o sistema de áudio"""
        self.sounds = {}
        self.music_enabled = False
        self.sfx_enabled = False

        try:
            self.generate_basic_sounds()
            self.sfx_enabled = True
        except Exception as e:
            print(f"Aviso: Audio nao inicializado: {e}")
            self.sfx_enabled = False
    
    def convert_to_stereo(self, wave):
        """Converte onda mono para estéreo"""
        wave = (wave * 32767).astype(np.int16)
        wave_stereo = np.column_stack((wave, wave))  # Duplica para estéreo
        return pygame.sndarray.make_sound(wave_stereo)
    
    def generate_basic_sounds(self):
        """Gera sons básicos do jogo"""
        # Som de tiro (onda quadrada)
        self.sounds['laser'] = self.generate_laser_sound()
        
        # Som de explosão (ruído branco)
        self.sounds['explosion'] = self.generate_explosion_sound()
        
        # Som de coleta (onda senoidal)
        self.sounds['collect'] = self.generate_collect_sound()
        
        # Som de mineração (onda triangular)
        self.sounds['mine'] = self.generate_mine_sound()
        
        # Som de construção (onda senoidal)
        self.sounds['build'] = self.generate_build_sound()
        
        # Som de propulsão (ruído filtrado)
        self.sounds['thrust'] = self.generate_thrust_sound()

        # Alias
        self.sounds['shoot'] = self.sounds['laser']
    
    def generate_laser_sound(self):
        """Gera som de laser (onda quadrada)"""
        duration = 0.1  # 100ms
        samples = int(SAMPLE_RATE * duration)
        
        # Frequência do laser
        frequency = 800
        amplitude = 0.3
        
        # Gera onda quadrada
        t = np.linspace(0, duration, samples)
        wave = amplitude * np.sign(np.sin(2 * np.pi * frequency * t))
        
        # Aplica envelope (fade in/out)
        envelope = np.exp(-5 * t)
        wave = wave * envelope
        
        # Converte para formato do Pygame
        return self.convert_to_stereo(wave)
    
    def generate_explosion_sound(self):
        """Gera som de explosão (ruído branco filtrado)"""
        duration = 0.5  # 500ms
        samples = int(SAMPLE_RATE * duration)

        # Gera ruído branco
        noise_data = np.random.uniform(-1, 1, samples)

        # Aplica filtro passa-baixa
        cutoff = 0.1
        filtered_noise = np.convolve(noise_data, [cutoff], mode='same')

        # Aplica envelope
        t = np.linspace(0, duration, samples)
        envelope = np.exp(-3 * t)
        wave = filtered_noise * envelope * 0.4

        return self.convert_to_stereo(wave)
    
    def generate_collect_sound(self):
        """Gera som de coleta (onda senoidal)"""
        duration = 0.2  # 200ms
        samples = int(SAMPLE_RATE * duration)

        # Frequência ascendente
        t = np.linspace(0, duration, samples)
        frequency = np.linspace(400, 800, samples)

        # Gera onda senoidal com frequência variável
        wave = 0.3 * np.sin(2 * np.pi * frequency * t)

        # Aplica envelope
        envelope = np.exp(-2 * t)
        wave = wave * envelope

        return self.convert_to_stereo(wave)
    
    def generate_mine_sound(self):
        """Gera som de mineração (onda triangular)"""
        duration = 0.3  # 300ms
        samples = int(SAMPLE_RATE * duration)

        t = np.linspace(0, duration, samples)

        # Gera onda triangular
        wave = 0.2 * (2 / np.pi) * np.arcsin(np.sin(2 * np.pi * 300 * t))

        # Aplica envelope
        envelope = np.exp(-1.5 * t)
        wave = wave * envelope

        return self.convert_to_stereo(wave)
    
    def generate_build_sound(self):
        """Gera som de construção (onda senoidal)"""
        duration = 0.15  # 150ms
        samples = int(SAMPLE_RATE * duration)

        t = np.linspace(0, duration, samples)
        wave = 0.25 * np.sin(2 * np.pi * 600 * t)

        # Aplica envelope
        envelope = np.exp(-4 * t)
        wave = wave * envelope

        return self.convert_to_stereo(wave)
    
    def generate_thrust_sound(self):
        """Gera som de propulsão (ruído filtrado)"""
        duration = 0.1  # 100ms
        samples = int(SAMPLE_RATE * duration)

        # Gera ruído
        noise_data = np.random.uniform(-1, 1, samples)
        filtered_noise = np.convolve(noise_data, [0.8], mode='same')

        # Aplica envelope
        t = np.linspace(0, duration, samples)
        envelope = np.exp(-2 * t)
        wave = filtered_noise * envelope * 0.3

        return self.convert_to_stereo(wave)
    
    def play_sound(self, sound_name):
        """Toca um som"""
        if not self.sfx_enabled:
            return
            
        if sound_name in self.sounds:
            self.sounds[sound_name].play()
    
    def generate_music_loop(self):
        """Gera loop de música procedural"""
        duration = 4.0  # 4 segundos
        samples = int(SAMPLE_RATE * duration)
        
        # Frequências baseadas em escala pentatônica
        frequencies = [220, 246, 277, 329, 370]  # A, B, C#, E, F#
        
        # Gera melodia procedural
        melody = []
        for i in range(samples):
            t = i / SAMPLE_RATE
            freq = frequencies[int(t * 2) % len(frequencies)]
            note = 0.1 * np.sin(2 * np.pi * freq * t)
            melody.append(note)
        
        # Adiciona harmonia
        harmony = []
        for i in range(samples):
            t = i / SAMPLE_RATE
            freq = frequencies[int(t * 2) % len(frequencies)] * 2  # Oitava acima
            note = 0.05 * np.sin(2 * np.pi * freq * t)
            harmony.append(note)
        
        # Combina melodia e harmonia
        wave = np.array(melody) + np.array(harmony)
        
        # Aplica envelope suave
        envelope = np.exp(-0.1 * np.linspace(0, duration, samples))
        wave = wave * envelope
        
        # Converte para formato do Pygame
        wave = (wave * 32767).astype(np.int16)
        return pygame.sndarray.make_sound(wave)
    
    def play_music(self):
        """Toca música de fundo"""
        if not self.music_enabled:
            return

        try:
            music = self.generate_music_loop()
            music.play(-1)  # Loop infinito
        except Exception as e:
            print(f"Aviso: Musica nao inicializada: {e}")
            self.music_enabled = False
    
    def stop_music(self):
        """Para a música"""
        pygame.mixer.music.stop()
    
    def set_volume(self, volume):
        """Define volume (0.0 a 1.0)"""
        pygame.mixer.music.set_volume(volume)
        for sound in self.sounds.values():
            sound.set_volume(volume)
    
    def toggle_music(self):
        """Alterna música"""
        self.music_enabled = not self.music_enabled
        if not self.music_enabled:
            self.stop_music()
        else:
            self.play_music()
    
    def toggle_sfx(self):
        """Alterna efeitos sonoros"""
        self.sfx_enabled = not self.sfx_enabled
