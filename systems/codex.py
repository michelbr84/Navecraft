"""
In-game codex - lore entries, resource/enemy/biome descriptions, glossary.
"""

import json
import os
from utils.i18n import get_language


CODEX_DATA = {
    'resources': {
        'IRON': {
            'pt': ('Ferro', 'Material estrutural comum. Usado para construção e crafting de kits.'),
            'en': ('Iron', 'Common structural material. Used in construction and repair kits.'),
            'es': ('Hierro', 'Material estructural común. Usado en construcción y kits.'),
        },
        'GOLD': {
            'pt': ('Ouro', 'Metal precioso de alta condutividade. Necessário para upgrades avançados.'),
            'en': ('Gold', 'High-conductivity precious metal. Needed for advanced upgrades.'),
            'es': ('Oro', 'Metal precioso conductor. Necesario para mejoras avanzadas.'),
        },
        'CRYSTAL': {
            'pt': ('Cristal', 'Cristais energéticos raros. Coração dos sistemas de propulsão e escudo.'),
            'en': ('Crystal', 'Rare energy crystals. Core of propulsion and shield systems.'),
            'es': ('Cristal', 'Cristales energéticos raros. Núcleo de propulsión y escudo.'),
        },
        'FUEL': {
            'pt': ('Combustível', 'Compostos voláteis que alimentam os motores.'),
            'en': ('Fuel', 'Volatile compound powering the engines.'),
            'es': ('Combustible', 'Compuesto volátil que alimenta los motores.'),
        },
        'OXYGEN': {
            'pt': ('Oxigênio', 'Cristais de O2 condensado. Mantém você vivo.'),
            'en': ('Oxygen', 'Condensed O2 crystals. Keeps you alive.'),
            'es': ('Oxígeno', 'Cristales de O2 condensado. Te mantiene vivo.'),
        },
    },
    'enemies': {
        'DRONE': {
            'pt': ('Drone', 'Rápido e frágil. Carga suicida — mantenha distância.'),
            'en': ('Drone', 'Fast and fragile. Suicide rusher — keep distance.'),
            'es': ('Dron', 'Rápido y frágil. Cargador suicida — mantén distancia.'),
        },
        'ANDROID': {
            'pt': ('Andróide', 'Resistente e metódico. Boa armadura.'),
            'en': ('Android', 'Tough and methodical. Heavy armor.'),
            'es': ('Androide', 'Resistente y metódico. Armadura pesada.'),
        },
        'SNIPER': {
            'pt': ('Sniper', 'Atira de longe. Aproxime-se ou faça curvas.'),
            'en': ('Sniper', 'Long-range attacker. Close in or zig-zag.'),
            'es': ('Sniper', 'Ataca a distancia. Acércate o zigzaguea.'),
        },
        'ARACHNOID': {
            'pt': ('Aracnoide', 'Multi-pernas. Veloz em terreno irregular.'),
            'en': ('Arachnoid', 'Multi-legged. Fast on rough terrain.'),
            'es': ('Aracnoide', 'Multipata. Veloz en terreno irregular.'),
        },
        'BOSS_DREADNAUGHT': {
            'pt': ('Dreadnaught', 'Mini-boss blindado. Múltiplas fases de combate.'),
            'en': ('Dreadnaught', 'Armored mini-boss. Multiple combat phases.'),
            'es': ('Dreadnaught', 'Mini-boss blindado. Varias fases de combate.'),
        },
    },
    'biomes': {
        'ROCK': {
            'pt': ('Rochoso', 'Mundos áridos ricos em ferro e ouro.'),
            'en': ('Rocky', 'Arid worlds rich in iron and gold.'),
            'es': ('Rocoso', 'Mundos áridos ricos en hierro y oro.'),
        },
        'ICE': {
            'pt': ('Gelado', 'Reservas de oxigênio e cristais frios.'),
            'en': ('Icy', 'Reserves of oxygen and cold crystals.'),
            'es': ('Helado', 'Reservas de oxígeno y cristales fríos.'),
        },
        'GAS': {
            'pt': ('Gasoso', 'Gigantes gasosos — apenas atmosfera, sem mineração.'),
            'en': ('Gas', 'Gas giants — atmosphere only, no mining.'),
            'es': ('Gaseoso', 'Gigantes gaseosos — solo atmósfera.'),
        },
        'METAL': {
            'pt': ('Metálico', 'Crostas de metais pesados.'),
            'en': ('Metal', 'Heavy-metal crusts.'),
            'es': ('Metálico', 'Cortezas de metales pesados.'),
        },
        'CRYSTAL': {
            'pt': ('Cristalino', 'Mundos prismáticos repletos de cristais energéticos.'),
            'en': ('Crystal', 'Prismatic worlds full of energy crystals.'),
            'es': ('Cristalino', 'Mundos prismáticos llenos de cristales.'),
        },
        'LAVA': {
            'pt': ('Vulcânico', 'Vulcões ativos e combustível abundante.'),
            'en': ('Volcanic', 'Active volcanoes and abundant fuel.'),
            'es': ('Volcánico', 'Volcanes activos y combustible abundante.'),
        },
        'TOXIC': {
            'pt': ('Tóxico', 'Nuvens venenosas — perigoso aproximar-se.'),
            'en': ('Toxic', 'Poisonous clouds — dangerous to approach.'),
            'es': ('Tóxico', 'Nubes venenosas — peligroso acercarse.'),
        },
        'RADIOACTIVE': {
            'pt': ('Radioativo', 'Cristais radioativos. Recompensa alta, risco alto.'),
            'en': ('Radioactive', 'Radioactive crystals. High reward, high risk.'),
            'es': ('Radiactivo', 'Cristales radiactivos. Alta recompensa, alto riesgo.'),
        },
        'WATER': {
            'pt': ('Aquático', 'Oceanos profundos com oxigênio abundante.'),
            'en': ('Water', 'Deep oceans rich in oxygen.'),
            'es': ('Acuático', 'Océanos profundos ricos en oxígeno.'),
        },
        'DESERT': {
            'pt': ('Desértico', 'Dunas infinitas e tempestades de areia.'),
            'en': ('Desert', 'Endless dunes and sandstorms.'),
            'es': ('Desierto', 'Dunas infinitas y tormentas de arena.'),
        },
    },
    'glossary': {
        'HUD': {
            'pt': ('HUD', 'Heads-Up Display: barras de status sobrepostas no jogo.'),
            'en': ('HUD', 'Heads-Up Display: status bars overlaid on the game.'),
            'es': ('HUD', 'Visor de cabeza: barras de estado superpuestas.'),
        },
        'WARP': {
            'pt': ('Warp', 'Salto entre sistemas solares através de coordenadas estelares.'),
            'en': ('Warp', 'Jump between solar systems via stellar coordinates.'),
            'es': ('Warp', 'Salto entre sistemas vía coordenadas estelares.'),
        },
        'CULLING': {
            'pt': ('Culling', 'Otimização que descarta objetos fora da tela.'),
            'en': ('Culling', 'Optimization that discards off-screen objects.'),
            'es': ('Culling', 'Optimización que descarta objetos fuera de pantalla.'),
        },
    },
}

LORE_LOG_ENTRIES = [
    {
        'id': 'log_01',
        'pt': "Log do Capitão #01: 'O sinal de socorro veio de uma estação esquecida...'",
        'en': "Captain Log #01: 'The distress signal came from a forgotten station...'",
        'es': "Log del Capitán #01: 'La señal de auxilio vino de una estación olvidada...'",
    },
    {
        'id': 'log_02',
        'pt': "Log #02: 'A radiação do sistema Veridian-3 distorce qualquer comunicação.'",
        'en': "Log #02: 'Veridian-3 system radiation scrambles all communication.'",
        'es': "Log #02: 'La radiación del sistema Veridian-3 distorsiona toda comunicación.'",
    },
    {
        'id': 'log_03',
        'pt': "Log #03: 'Encontrei destroços de uma frota desconhecida. Cristais cintilam.'",
        'en': "Log #03: 'Found wreckage of an unknown fleet. Crystals shimmer.'",
        'es': "Log #03: 'Encontré restos de una flota desconocida. Cristales brillan.'",
    },
]


def get_entry(category, entry_id):
    lang = get_language()
    data = CODEX_DATA.get(category, {}).get(entry_id)
    if not data:
        return None
    name, desc = data.get(lang, data.get('pt', ('?', '?')))
    return {'name': name, 'description': desc}


def all_entries(category):
    return [(eid, get_entry(category, eid)) for eid in CODEX_DATA.get(category, {})]


def random_lore_entry():
    import random
    e = random.choice(LORE_LOG_ENTRIES)
    return e.get(get_language(), e.get('pt'))
