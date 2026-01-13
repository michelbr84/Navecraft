"""
Sistema de missões do Navecraft
"""

import random
from settings import *

class Mission:
    def __init__(self, mission_type, description, target, reward):
        self.mission_type = mission_type
        self.description = description
        self.target = target
        self.reward = reward
        self.completed = False
        self.progress = 0
        self.id = random.randint(1000, 9999)
    
    def update_progress(self, amount=1):
        """Atualiza progresso da missão"""
        self.progress += amount
        if self.progress >= self.target:
            self.completed = True
            return True
        return False
    
    def get_progress_percentage(self):
        """Retorna porcentagem de progresso"""
        return min(100, (self.progress / self.target) * 100)

class MissionSystem:
    def __init__(self):
        """Inicializa o sistema de missões"""
        self.active_missions = []
        self.completed_missions = []
        self.available_missions = self.generate_mission_pool()
        
    def generate_mission_pool(self):
        """Gera pool de missões disponíveis"""
        missions = []
        
        # Missões de mineração
        missions.extend([
            Mission("mining", "Mine 10 blocos de ferro", 10, {"IRON": 50}),
            Mission("mining", "Mine 5 blocos de ouro", 5, {"GOLD": 30}),
            Mission("mining", "Mine 3 blocos de cristal", 3, {"CRYSTAL": 20}),
            Mission("mining", "Mine 15 blocos de combustível", 15, {"FUEL": 100}),
            Mission("mining", "Mine 20 blocos de oxigênio", 20, {"OXYGEN": 80}),
        ])
        
        # Missões de construção
        missions.extend([
            Mission("building", "Construa 5 blocos de ferro", 5, {"IRON": 25}),
            Mission("building", "Construa 3 blocos de ouro", 3, {"GOLD": 15}),
            Mission("building", "Construa 2 blocos de cristal", 2, {"CRYSTAL": 10}),
        ])
        
        # Missões de sobrevivência
        missions.extend([
            Mission("survival", "Sobreviva por 5 minutos", 300, {"FUEL": 50, "OXYGEN": 50}),
            Mission("survival", "Mantenha energia acima de 80% por 3 minutos", 180, {"FUEL": 30}),
        ])
        
        # Missões de exploração
        missions.extend([
            Mission("exploration", "Visite 3 planetas diferentes", 3, {"CRYSTAL": 15}),
            Mission("exploration", "Viaje 1000 pixels", 1000, {"FUEL": 40}),
        ])
        
        return missions
    
    def get_random_mission(self):
        """Retorna uma missão aleatória disponível"""
        if not self.available_missions:
            return None
        
        mission = random.choice(self.available_missions)
        self.available_missions.remove(mission)
        return mission
    
    def accept_mission(self, mission):
        """Aceita uma missão"""
        if mission and mission not in self.active_missions:
            self.active_missions.append(mission)
            return True
        return False
    
    def complete_mission(self, mission):
        """Completa uma missão"""
        if mission in self.active_missions and mission.completed:
            self.active_missions.remove(mission)
            self.completed_missions.append(mission)
            return mission.reward
        return None
    
    def update_mining_missions(self, block_type):
        """Atualiza missões de mineração"""
        for mission in self.active_missions:
            if mission.mission_type == "mining" and not mission.completed:
                if "mining" in mission.description.lower() and block_type.lower() in mission.description.lower():
                    if mission.update_progress():
                        return self.complete_mission(mission)
    
    def update_building_missions(self, block_type):
        """Atualiza missões de construção"""
        for mission in self.active_missions:
            if mission.mission_type == "building" and not mission.completed:
                if "construa" in mission.description.lower() and block_type.lower() in mission.description.lower():
                    if mission.update_progress():
                        return self.complete_mission(mission)
    
    def update_survival_missions(self, game_time, spaceship):
        """Atualiza missões de sobrevivência"""
        for mission in self.active_missions:
            if mission.mission_type == "survival" and not mission.completed:
                if "sobreviva" in mission.description.lower():
                    # Missão de sobrevivência por tempo
                    if mission.update_progress():
                        return self.complete_mission(mission)
                elif "energia" in mission.description.lower():
                    # Missão de manter energia
                    if spaceship.energy / spaceship.max_energy > 0.8:
                        if mission.update_progress():
                            return self.complete_mission(mission)
                    else:
                        mission.progress = 0  # Reset se energia baixa
    
    def update_exploration_missions(self, spaceship, visited_planets):
        """Atualiza missões de exploração"""
        for mission in self.active_missions:
            if mission.mission_type == "exploration" and not mission.completed:
                if "visite" in mission.description.lower():
                    # Missão de visitar planetas
                    if len(visited_planets) >= mission.target:
                        mission.progress = len(visited_planets)
                        if mission.update_progress():
                            return self.complete_mission(mission)
                elif "viaje" in mission.description.lower():
                    # Missão de distância
                    distance = abs(spaceship.x) + abs(spaceship.y)
                    mission.progress = min(distance, mission.target)
                    if mission.update_progress():
                        return self.complete_mission(mission)
    
    def render_missions(self, surface):
        """Renderiza interface de missões"""
        if not self.active_missions:
            return
        
        font = pygame.font.Font(None, 20)
        y_offset = 200
        
        # Título
        title = font.render("Missões Ativas:", True, (255, 255, 0))
        surface.blit(title, (SCREEN_WIDTH - 300, y_offset))
        y_offset += 30
        
        for mission in self.active_missions[:3]:  # Mostra apenas 3 missões
            # Descrição da missão
            desc_text = font.render(mission.description, True, (255, 255, 255))
            surface.blit(desc_text, (SCREEN_WIDTH - 300, y_offset))
            y_offset += 20
            
            # Progresso
            progress_text = font.render(f"Progresso: {mission.progress}/{mission.target} ({mission.get_progress_percentage():.0f}%)", True, (0, 255, 255))
            surface.blit(progress_text, (SCREEN_WIDTH - 300, y_offset))
            y_offset += 30
            
            # Barra de progresso
            bar_width = 200
            bar_height = 10
            progress_width = int(bar_width * (mission.progress / mission.target))
            
            pygame.draw.rect(surface, (50, 50, 50), (SCREEN_WIDTH - 300, y_offset, bar_width, bar_height))
            pygame.draw.rect(surface, (0, 255, 0), (SCREEN_WIDTH - 300, y_offset, progress_width, bar_height))
            y_offset += 20
