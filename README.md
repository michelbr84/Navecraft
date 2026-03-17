# Navecraft

Um jogo de sobrevivência e exploração espacial inspirado no Minecraft, desenvolvido em Python com Pygame.

## Descrição

Navecraft é um jogo de sobrevivência espacial onde você controla uma nave que deve explorar planetas, minerar recursos, construir estruturas e combater inimigos espaciais. Tudo no jogo é gerado proceduralmente - desde os gráficos até os sons - sem necessidade de arquivos externos.

## Características

### 🚀 **Mecânicas Principais**
- **Movimentação da Nave**: Controle uma nave espacial com física realista (inércia, desaceleração)
- **Mineração**: Use feixes de energia para minerar blocos planetários
- **Construção**: Construa estruturas no espaço usando recursos coletados
- **Combate**: Enfrente inimigos espaciais com armas laser
- **Sobrevivência**: Gerencie energia, oxigênio e combustível da nave

### 🌌 **Geração Procedural**
- **Planetas**: Gerados proceduralmente com diferentes tamanhos, tipos e recursos
- **Blocos**: Distribuição procedural de recursos (ferro, ouro, cristal, combustível, oxigênio)
- **Inimigos**: IA procedural com diferentes comportamentos (patrulha, perseguição, ataque)
- **Efeitos Visuais**: Partículas, explosões e efeitos de propulsão gerados por código

### 🎵 **Áudio Procedural**
- **Sons**: Todos os efeitos sonoros são gerados sinteticamente
- **Música**: Loops musicais criados proceduralmente
- **Feedback**: Sons de mineração, construção, coleta e combate

### 🎮 **Interface**
- **HUD**: Barras de vida, energia, oxigênio e combustível
- **Inventário**: Sistema de gerenciamento de recursos
- **Menus**: Menu principal, pausa e game over
- **Debug**: Informações de performance e debug (F1 para ativar)

## Instalação

### Pré-requisitos
- Python 3.8 ou superior
- Pygame 2.5.0 ou superior

### Instalação das Dependências
```bash
pip install -r requirements.txt
```

### Executar o Jogo
```bash
python main.py
```

## Controles

### Movimentação
- **WASD** ou **Setas**: Movimentação da nave
- **Mouse**: Mira para mineração e construção

### Ações
- **Espaço**: Disparar laser
- **E**: Mineração (aproxime-se dos blocos)
- **Q**: Construção (posição do mouse)
- **I**: Inventário
- **1-5**: Selecionar tipo de bloco (Ferro, Ouro, Cristal, Combustível, Oxigênio)

### Crafting
- **R**: Craft Kit de Reparo
- **T**: Craft Pacote de Energia
- **Y**: Craft Tanque de Oxigênio
- **U**: Craft Reforço de Escudo

### Upgrades
- **F1**: Upgrade Motor
- **F2**: Upgrade Escudo
- **F3**: Upgrade Energia
- **F4**: Upgrade Mineração
- **F5**: Upgrade Oxigênio
- **F6**: Upgrade Combustível

### Missões e Multiplayer
- **M**: Aceitar nova missão
- **F7**: Alternar multiplayer local
- **F8**: Adicionar jogador

### Interface
- **ESC**: Menu de pausa
- **F11**: Alternar tela cheia
- **F1**: Ativar/desativar modo debug (quando não em jogo)

## Estrutura do Projeto

```
navecraft/
├── main.py                 # Loop principal do jogo
├── settings.py             # Configurações globais
├── requirements.txt        # Dependências Python
├── TODO.md                # Lista de tarefas e progresso
├── core/                  # Sistemas principais
│   ├── game.py           # Lógica principal do jogo
│   ├── input.py          # Sistema de entrada
│   ├── renderer.py       # Renderização procedural
│   └── audio.py          # Sistema de áudio
├── entities/              # Entidades do jogo
│   ├── spaceship.py      # Nave do jogador
│   └── enemy.py          # Inimigos
├── systems/               # Sistemas especializados
│   ├── physics.py        # Física espacial
│   ├── generation.py     # Geração procedural
│   ├── inventory.py      # Sistema de inventário e crafting
│   ├── particles.py      # Sistema de partículas
│   ├── missions.py       # Sistema de missões
│   ├── upgrades.py       # Sistema de upgrades
│   └── multiplayer.py    # Multiplayer local
├── ui/                    # Interface do usuário
│   ├── hud.py            # Heads-Up Display
│   └── menu.py           # Menus do jogo
├── tests/                 # Testes automatizados
│   └── test_fixes.py    # Testes de input, menus, mineração e projéteis
└── utils/                 # Utilitários
    ├── colors.py         # Paletas de cores
    ├── debug.py          # Sistema de debug
    └── logger.py         # Sistema de logging
```

## Mecânicas Detalhadas

### Sistema de Mineração
- A nave dispara feixes de energia para destruir blocos
- Recursos coletados vão para o inventário
- Diferentes tipos de blocos têm diferentes valores
- Sistema de cooldown para evitar spam

### Sistema de Construção
- Selecione o tipo de bloco com as teclas 1-5
- Clique para construir na posição do mouse
- Consome recursos do inventário
- Construa estruturas, plataformas e estações

### Sistema de Sobrevivência
- **Energia**: Consumida por movimentação e mineração
- **Oxigênio**: Diminui gradualmente no espaço
- **Combustível**: Necessário para movimentação
- **Escudo**: Proteção contra dano

### IA dos Inimigos
- **Drone**: Inimigo básico que persegue o jogador
- **Android**: Inimigo mais resistente
- **Sniper**: Ataca à distância
- **Arachnoid**: Inimigo mecânico com comportamento complexo

## Otimizações Implementadas

### Performance
- **Culling**: Só renderiza objetos próximos à câmera
- **LOD**: Nível de detalhe baseado na distância
- **Pooling**: Reutilização de objetos para reduzir alocação
- **Spatial Partitioning**: Otimização de colisões

### Debug e Monitoramento
- **FPS Counter**: Monitoramento de performance
- **Object Counters**: Contagem de objetos visíveis
- **Collision Boxes**: Visualização de colisões (F1)
- **Performance Info**: Informações detalhadas de performance

## Configurações

O arquivo `settings.py` contém todas as configurações do jogo:

- **Dimensões da tela** e configurações de display
- **Propriedades da nave** (velocidade, energia, etc.)
- **Configurações de física** (gravidade, atrito, etc.)
- **Parâmetros de geração procedural** (noise, seeds, etc.)
- **Configurações de áudio** (frequência, volume, etc.)
- **Limites de otimização** (distâncias de culling, etc.)

## Desenvolvimento

### Estrutura de Desenvolvimento
O projeto foi desenvolvido em 12 fases:

1. **FASE 1**: Setup básico (Pygame, nave, movimentação)
2. **FASE 2**: Renderização procedural (estrelas, planetas, nave)
3. **FASE 3**: Geração procedural (planetas, blocos, inimigos)
4. **FASE 4**: Mineração e inventário
5. **FASE 5**: Combate e IA
6. **FASE 6**: Construção
7. **FASE 7**: Áudio procedural
8. **FASE 8**: Sobrevivência e HUD
9. **FASE 9**: Efeitos e partículas
10. **FASE 10**: Menus e interface
11. **FASE 11**: Polimento e otimização
12. **FASE 12**: Expansão (futuro)

### Tecnologias Utilizadas
- **Pygame**: Framework principal para desenvolvimento de jogos
- **NumPy**: Geração de áudio procedural
- **Noise**: Geração procedural de terreno e recursos
- **Python**: Linguagem principal

## Contribuição

Para contribuir com o projeto:

1. Fork o repositório
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

## Licença

Este projeto está sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.

## Autores

- Desenvolvido como projeto de demonstração de geração procedural
- Inspirado no Minecraft e jogos de exploração espacial

## Agradecimentos

- Comunidade Pygame por fornecer uma base sólida para desenvolvimento de jogos
- Inspiração do Minecraft para as mecânicas de mineração e construção
- Conceitos de geração procedural para criar um universo dinâmico

## Screenshots

*Screenshots do jogo serão adicionados aqui*

## Notas Adicionais

- O jogo é completamente procedural - não há imagens ou sons externos
- Todos os gráficos são gerados usando formas geométricas básicas do Pygame
- Todos os sons são sintetizados usando ondas senoidais, quadradas e triangulares
- O sistema de geração procedural garante que cada sessão seja única
- O código está otimizado para performance em diferentes configurações de hardware

---

**Navecraft** - Explore, mine, construa e sobreviva no espaço infinito!
