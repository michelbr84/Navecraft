# TODO - Navecraft: Roadmap para AAA (v1.2)

> **Status atual real (2026-05-12):** Muitos sistemas foram criados em codigo (~36 novos modulos),
> mas o jogo apresenta bugs criticos que impedem a jogabilidade. A versao anterior do TODO marcava
> tudo como "concluido" - isso era prematuro. Esta revisao e honesta sobre o que funciona, o que
> esta quebrado, e o que ainda falta para AAA real.

---

## SUMARIO HONESTO

| Categoria | Status real |
|-----------|------------|
| Fundacao v1 (mecanicas basicas) | FEITO (60/60) |
| Arquitetura v1.1 (modulos novos criados) | FEITO (codigo existe) |
| **Bugs criticos bloqueando jogabilidade** | **PENDENTE - PRIORIDADE MAXIMA** |
| Integracao real dos sistemas (todos funcionando juntos) | PARCIAL |
| Qualidade visual AAA (arte coesa, nao apenas formas) | PENDENTE |
| Conteudo & Narrativa (existe mas raso) | PARCIAL |
| Acessibilidade & Localizacao (existe mas nao testado) | PARCIAL |
| QA & Estabilidade real | PENDENTE |
| Distribuicao & Plataformas | PENDENTE |

---

## FASE 0: BUGS CRITICOS (BLOQUEIAM JOGABILIDADE - URGENTE)

> Observados em screenshots ao iniciar o jogo. Sem resolver isso, nada mais importa.

### 0.1 Mundo nao renderiza (TELA BRANCA)
- [ ] 0.1.1. Ao entrar no jogo, a area jogavel fica branca/vazia - estrelas, planetas, asteroides invisiveis
- [ ] 0.1.2. Investigar ordem de renderizacao em `core/game.py` (background system pode estar limpando tela depois do draw)
- [ ] 0.1.3. Verificar se `systems/background.py` ou `systems/lighting.py` esta sobrescrevendo o canvas
- [ ] 0.1.4. Verificar se `SmoothCamera` esta passando offset correto para o renderer
- [ ] 0.1.5. Confirmar que `display.WIDTH/HEIGHT` dinamicos nao quebraram coordenadas do mundo
- [ ] 0.1.6. Adicionar teste de smoke que detecta "tela majoritariamente uniforme" (pixel sampling)

### 0.2 Menu de Configuracoes nao interativo
- [ ] 0.2.1. Opcoes "Volume Mestre" e "Tela Cheia" aparecem mas nao respondem a clique/Enter
- [ ] 0.2.2. Verificar handler de eventos em `ui/settings_screen.py` (provavelmente nao retornando acao)
- [ ] 0.2.3. Garantir que Enter/Espaco/Click ativam a opcao selecionada
- [ ] 0.2.4. Setas Esq/Dir devem ajustar valores numericos (volume slider)
- [ ] 0.2.5. ESC deve voltar ao menu anterior consistentemente
- [ ] 0.2.6. Teste manual completo de navegacao em TODOS os submenus

### 0.3 Integracao de modulos novos com main.py / game.py
- [ ] 0.3.1. Verificar que TODOS os ~36 modulos novos estao realmente importados e utilizados
- [ ] 0.3.2. Em particular: `systems/lighting`, `systems/background`, `systems/feedback`, `systems/tutorial`
- [ ] 0.3.3. Ver se `main.py` foi atualizado para o novo fluxo (state machine, fade_then, etc.)
- [ ] 0.3.4. Detectar codigo dead/orfão (modulos criados mas nunca chamados)

### 0.4 HUD reorganizado vs jogabilidade
- [ ] 0.4.1. Confirmar que a nova reorganizacao de HUD nao escondeu elementos importantes
- [ ] 0.4.2. Posicao do jogador (7860, 9760) sugere spawn distante da origem - validar
- [ ] 0.4.3. Minimap deve mostrar entidades do mundo (atualmente parece quase vazio)
- [ ] 0.4.4. Inventario rapido (1-5) com numeros zerados - confirmar que coleta soma corretamente

### 0.5 Suite de testes contra bugs visiveis
- [ ] 0.5.1. Teste headless que renderiza 1 frame e verifica que nao e tela uniforme
- [ ] 0.5.2. Teste de navegacao de menu (todas as opcoes devem produzir uma acao)
- [ ] 0.5.3. Teste de toggle fullscreen sem crash
- [ ] 0.5.4. Teste de carregar save corrompido sem crash

---

## FASE 1: ESTADO DA IMPLEMENTACAO ANTERIOR (auditoria)

> Sistemas criados em codigo mas nao verificados em runtime. Cada item precisa de teste manual + automatizado.

### 1.1 Modulos a auditar (~36 novos)
- [ ] 1.1.1. `utils/display.py` - resolucao dinamica funciona em fullscreen real?
- [ ] 1.1.2. `utils/config.py` - persistencia em JSON salva/carrega corretamente?
- [ ] 1.1.3. `utils/font.py` - render_outlined / draw_panel renderizam sem artefatos?
- [ ] 1.1.4. `utils/i18n.py` - troca de idioma realmente afeta todos os textos da UI?
- [ ] 1.1.5. `systems/feedback.py` - shake, flash, slowmo aparecem em jogo?
- [ ] 1.1.6. `systems/tutorial.py` - state machine avanca pelas 7 etapas sem travar?
- [ ] 1.1.7. `systems/codex.py` + `ui/codex_screen.py` - tecla K abre e funciona?
- [ ] 1.1.8. `systems/lighting.py` - luzes additive blending aparecem corretamente?
- [ ] 1.1.9. `systems/background.py` - parallax 3 camadas + nebulas + planetas distantes visiveis?
- [ ] 1.1.10. `systems/galaxy.py` - 12 sistemas solares acessiveis via warp?
- [ ] 1.1.11. `systems/factions.py` - reputacao realmente afeta NPCs?
- [ ] 1.1.12. `systems/bosses.py` - mini-boss spawna e ataca em 2 fases?
- [ ] 1.1.13. `systems/skills.py` - skill tree gasta pontos e aplica buffs?
- [ ] 1.1.14. `systems/achievements.py` - 13 conquistas sao realmente trigerizaveis?
- [ ] 1.1.15. `systems/gamepad.py` - controle Xbox/PS funciona end-to-end?
- [ ] 1.1.16. `systems/profiler.py` - F3 mostra overlay com timings reais?
- [ ] 1.1.17. `systems/pool.py` - ObjectPool reduz GC pressure (medir antes/depois)?
- [ ] 1.1.18. `systems/spatial_hash.py` - broad-phase realmente acelera colisoes (benchmark)?
- [ ] 1.1.19. `systems/telemetry.py` - opt-in funciona, logs locais sao escritos?
- [ ] 1.1.20. `systems/mod_loader.py` - mod de exemplo carrega e altera comportamento?
- [ ] 1.1.21. `systems/photo_mode.py` - F12 ativa, PNG salvo corretamente?
- [ ] 1.1.22. `systems/day_night.py` - ciclo visualmente perceptivel?
- [ ] 1.1.23. `systems/weather.py` - tempestades solares afetam sistemas da nave?
- [ ] 1.1.24. `systems/replay.py` - gravacao + playback fidedignos?
- [ ] 1.1.25. `systems/speedrun.py` - timer F4 funciona e e preciso?
- [ ] 1.1.26. `systems/rebind.py` - keybinds customizados persistem?
- [ ] 1.1.27. `systems/accessibility.py` - filtros daltonicos aplicam corretamente?
- [ ] 1.1.28. `ui/minimap.py` - mostra entidades, atualiza em tempo real?
- [ ] 1.1.29. `ui/compass.py` - aponta para waypoint e inimigos off-screen?
- [ ] 1.1.30. `ui/inventory_screen.py` - grid clicavel, drag-drop, sort?
- [ ] 1.1.31. `ui/crafting_screen.py` - lista receitas, custos coloridos, fila?
- [ ] 1.1.32. `ui/map_screen.py` - mapa com fog of war + waypoints?
- [ ] 1.1.33. `ui/death_screen.py` - stats + screenshot + causa exibidos?
- [ ] 1.1.34. `ui/tooltip.py` - word-wrap, posicao inteligente?
- [ ] 1.1.35. `ui/help_overlay.py` - tecla H mostra todos controles agrupados?
- [ ] 1.1.36. `entities/merchant.py` - dialogo + compra/venda funcionais?

### 1.2 Integracao end-to-end
- [ ] 1.2.1. Tutorial completo: novo jogador roda etapa por etapa sem confusao
- [ ] 1.2.2. Combate: tiros + hitstop + numbers + shake + sound + xp + drops
- [ ] 1.2.3. Mineracao: alcance + cracks + drops + texto flutuante + som + xp
- [ ] 1.2.4. Construcao: preview + custo + som + integracao com inventario
- [ ] 1.2.5. Save/load: persiste TODOS os sistemas novos (factions, skills, achievements, etc.)

---

## FASE 2: POLIMENTO VISUAL AAA REAL (alem do "implementado")

> Codigo de iluminacao/background existe mas o resultado visual e generico. AAA exige direcao de arte.

### 2.1 Direcao de arte
- [ ] 2.1.1. Definir paleta de cores coesa (atualmente: tudo brilha igual, sem hierarquia)
- [ ] 2.1.2. Mood board: refs de FTL, Stellaris, Hardspace Shipbreaker, Everspace
- [ ] 2.1.3. Style guide escrito para mantenedor (espessura de linhas, glow, contrastes)
- [ ] 2.1.4. Iluminacao deve criar atmosfera (atualmente apenas adiciona brilho)
- [ ] 2.1.5. Sombras reais (nao apenas falloff radial)

### 2.2 Animacoes 2D
- [ ] 2.2.1. Skeletal animation simples para a nave (tilt em curvas, recoil em tiros)
- [ ] 2.2.2. Inimigos com idle/move/attack/death distinguiveis
- [ ] 2.2.3. UI animacoes (slide-in, fade, bounce) consistentes
- [ ] 2.2.4. Mineracao com animacao real (laser progressivo, nao binario)

### 2.3 Shaders / efeitos
- [ ] 2.3.1. Implementar shader real (via pygame.Surface manipulations ou moderngl)
- [ ] 2.3.2. Heat distortion em motores
- [ ] 2.3.3. Refracao em campos de forca
- [ ] 2.3.4. Volumetric fog em nebulas
- [ ] 2.3.5. Lens dirt / scratches sutis para imersao

### 2.4 Texturas geradas
- [ ] 2.4.1. Asteroides com cracks/texturas geradas por noise
- [ ] 2.4.2. Naves com paneling detectado (lines, rivets) procedural
- [ ] 2.4.3. Planetas com biomas visiveis (gelo, lava, vegetacao) - nao apenas cor unica

### 2.5 Camera de qualidade
- [ ] 2.5.1. Cinematic camera durante eventos (boss intro, descoberta de planeta)
- [ ] 2.5.2. Zoom suave com easing curves (nao linear)
- [ ] 2.5.3. Frame composition rules (regra dos tercos em alguns eventos)
- [ ] 2.5.4. Letterbox bars em cenas cinematograficas

---

## FASE 3: GAME FEEL REAL (juice perceptivel)

### 3.1 Audio que vende impacto
- [ ] 3.1.1. Audit dos sons procedurais - muitos soam "beeps de calculadora"
- [ ] 3.1.2. Sintetizar sons com camadas (sub + body + crack + tail) - nao apenas tons
- [ ] 3.1.3. Reverbs e delays simulados para profundidade espacial
- [ ] 3.1.4. Sidechain compression simulada para "punch" em bass
- [ ] 3.1.5. Ducking automatico de musica em momentos de SFX importante

### 3.2 Music design
- [ ] 3.2.1. Composicao real (loops procedurais soam aleatorios) - usar motifs e progressoes
- [ ] 3.2.2. Camadas adaptativas (drums + bass + lead + ambient com fade independente)
- [ ] 3.2.3. Stingers tematicos (lembravel, nao apenas barulho)
- [ ] 3.2.4. Boss themes proprios e memoraveis

### 3.3 Haptics expandidos
- [ ] 3.3.1. Padroes de vibracao distintos por tipo de evento (nao apenas duracao)
- [ ] 3.3.2. Audio haptico via subwoofer (para PC desktop)
- [ ] 3.3.3. Mouse rumble (alguns mouses gaming suportam)

---

## FASE 4: CONTEUDO PROFUNDO

### 4.1 Narrativa real
- [ ] 4.1.1. Roteiro de campanha principal (atualmente apenas lore esparso)
- [ ] 4.1.2. 3-5 personagens recorrentes com arcos
- [ ] 4.1.3. Multiplos finais baseados em escolhas
- [ ] 4.1.4. Voice acting opcional (mesmo que sintetico via TTS de qualidade)

### 4.2 World building
- [ ] 4.2.1. 50+ entradas de lore (nao apenas 3)
- [ ] 4.2.2. Cada faccao com cultura, simbolos, naves visualmente distintas
- [ ] 4.2.3. Eventos dinamicos no mundo (guerras entre faccoes, invasoes)
- [ ] 4.2.4. Pontos de interesse memoraveis (estacoes abandonadas, naufragos)

### 4.3 Sistema economico
- [ ] 4.3.1. Oferta e demanda dinamica entre estacoes
- [ ] 4.3.2. Comercio com flutuacao de precos
- [ ] 4.3.3. Especializacoes regionais (alguns planetas produzem mais X)
- [ ] 4.3.4. Eventos de mercado (escassez, boom)

### 4.4 Endgame
- [ ] 4.4.1. Conteudo pos-campanha (raids, dungeons proceduralmente geradas)
- [ ] 4.4.2. New Game+ com modificadores realmente novos (nao apenas dificuldade)
- [ ] 4.4.3. Sistema de prestigio (resets com bonus permanentes)
- [ ] 4.4.4. Bosses semanais/mensais com leaderboards

---

## FASE 5: UX SEM FRICCAO

### 5.1 Onboarding profissional
- [ ] 5.1.1. Tutorial nao linear (usuario explora, jogo reage)
- [ ] 5.1.2. Difficulty curve testada (playtesting com usuarios novos)
- [ ] 5.1.3. Telemetria de funil para identificar pontos de abandono
- [ ] 5.1.4. Dicas progressivas (so mostra construcao quando jogador tem recursos)

### 5.2 UI/UX
- [ ] 5.2.1. Auditoria de UX por designer (heuristicas Nielsen)
- [ ] 5.2.2. Consistencia visual (atualmente alguns menus diferem em estilo)
- [ ] 5.2.3. Animacoes de feedback em CADA acao do usuario
- [ ] 5.2.4. Tooltips contextuais inteligentes (mostram dica relevante ao momento)

### 5.3 Performance percebida
- [ ] 5.3.1. Loading screens com progresso real (nao apenas spinner)
- [ ] 5.3.2. Texturas e sons em streaming (carregamento assincrono)
- [ ] 5.3.3. Auto-save invisivel (sem freeze)
- [ ] 5.3.4. Quick-resume (volta exatamente onde parou)

---

## FASE 6: QUALIDADE & ESTABILIDADE AAA

### 6.1 Testes
- [ ] 6.1.1. Cobertura > 80% (atualmente ~64 testes mas cobertura desconhecida)
- [ ] 6.1.2. Property-based testing (hipoteticos com hypothesis)
- [ ] 6.1.3. Fuzzing de save files
- [ ] 6.1.4. Stress tests (1000+ inimigos, manter 60 FPS)
- [ ] 6.1.5. Soak tests (rodar 8h sem memory leak)
- [ ] 6.1.6. Smoke test visual (compara frames com snapshots aprovados)

### 6.2 Monitoramento
- [ ] 6.2.1. Sentry / equivalente para crash reporting
- [ ] 6.2.2. Performance budgets por sistema (alarmar se ultrapassar)
- [ ] 6.2.3. Metricas de gameplay (tempo medio de sessao, retencao D1/D7/D30)

### 6.3 Localizacao real
- [ ] 6.3.1. Auditoria de strings (atualmente strings hardcoded em multiplos lugares)
- [ ] 6.3.2. Tradutor profissional (nao Google Translate) para EN/ES
- [ ] 6.3.3. Adicionar FR, DE, JA, KO, ZH, RU
- [ ] 6.3.4. Right-to-left support (AR)
- [ ] 6.3.5. Plural rules e contexto cultural

### 6.4 Acessibilidade WCAG
- [ ] 6.4.1. Contraste minimo AA em todo texto
- [ ] 6.4.2. Suporte a leitor de tela (NVDA/JAWS)
- [ ] 6.4.3. Remapeavel para usuarios com mobilidade reduzida
- [ ] 6.4.4. Single-stick mode (jogavel com uma mao)
- [ ] 6.4.5. Modo dyslexico (fonte OpenDyslexic)

---

## FASE 7: PRODUCAO & DISTRIBUICAO

### 7.1 Build pipeline
- [ ] 7.1.1. CI/CD com testes obrigatorios antes de merge
- [ ] 7.1.2. Versionamento semantico automatico
- [ ] 7.1.3. Code signing para Windows e macOS (sem alertas SmartScreen)
- [ ] 7.1.4. Notarizacao Apple
- [ ] 7.1.5. Auto-updater integrado

### 7.2 Plataformas
- [ ] 7.2.1. Steam (Steamworks: achievements, cloud saves, workshop)
- [ ] 7.2.2. itch.io (versao demo)
- [ ] 7.2.3. GOG (DRM-free)
- [ ] 7.2.4. Epic Games Store
- [ ] 7.2.5. Console: Nintendo Switch, Xbox, PlayStation (necessita partner)

### 7.3 Marketing
- [ ] 7.3.1. Steam page com trailer profissional
- [ ] 7.3.2. Wishlist campaign 6+ meses antes do launch
- [ ] 7.3.3. Demo publica (Steam Next Fest)
- [ ] 7.3.4. Press kit (logos, screenshots HD, fact sheet)
- [ ] 7.3.5. Engagement de streamers/youtubers
- [ ] 7.3.6. Comunidade Discord moderada

### 7.4 Pos-launch
- [ ] 7.4.1. Roadmap publico de updates
- [ ] 7.4.2. Patch notes detalhados
- [ ] 7.4.3. Hotfix automatizado para crashes
- [ ] 7.4.4. DLC plan (cosmetics, expansoes)
- [ ] 7.4.5. Sales strategy (descontos sazonais)

---

## FASE 8: ASPECTOS LEGAIS & PROFISSIONAIS

### 8.1 Legal
- [ ] 8.1.1. EULA + Termos de uso
- [ ] 8.1.2. Privacy policy (GDPR/LGPD compliant)
- [ ] 8.1.3. Atribuicoes de bibliotecas open-source (NOTICE.md)
- [ ] 8.1.4. Trademark do nome "Navecraft" (verificar disponibilidade)
- [ ] 8.1.5. ESRB/PEGI rating

### 8.2 Documentacao
- [ ] 8.2.1. Wiki publica para jogadores
- [ ] 8.2.2. Manual em PDF
- [ ] 8.2.3. Documentacao tecnica para modders
- [ ] 8.2.4. Bug report template + triage process

### 8.3 Suporte
- [ ] 8.3.1. Sistema de tickets (Zendesk ou similar)
- [ ] 8.3.2. FAQ publica
- [ ] 8.3.3. Comunidade moderada (Discord + forum)

---

## O QUE DE FATO FALTA PARA SER AAA

Ser AAA exige tres coisas que **nao podem ser produzidas apenas por geracao procedural ou codigo**:

### 1. Direcao de arte coesa e atrativa
Codigo procedural produz blocos quadrados ou poligonos irregulares.
AAA exige um **artista** definindo style guide, paleta, formas, animacoes.
Solucao temporaria: investir tempo significativo refinando o procedural com referencias de jogos AAA.

### 2. Conteudo curado e narrativo
Geracao procedural cria quantidade; nao cria significado.
AAA exige **roteirista** criando arcos, personagens memoraveis, missoes com gancho emocional.
Solucao temporaria: escrever pelo menos 1 campanha curta scriptada como onboarding.

### 3. Polimento obsessivo (1000 detalhes pequenos)
AAA tem cada transicao, cada som, cada animacao, cada texto, cada estado vazio cuidado.
Solucao temporaria: passes de polimento sistematicos area por area, com QA dedicado.

### Adicional: O que distingue AAA de bons jogos indies
- Producao audio profissional (composicao real, mix profissional, foley)
- Localizacao em 10+ idiomas por tradutores profissionais
- Suporte oficial a multiplas plataformas e dispositivos
- Marketing/PR significativo
- Equipe dedicada a longo prazo (anos de suporte pos-launch)

---

## PROXIMOS PASSOS RECOMENDADOS (ordem de prioridade)

1. **AGORA**: Corrigir bugs criticos da FASE 0 (tela branca, menus). Sem isso, nada importa.
2. **Esta semana**: Auditar todos os 36 modulos novos (FASE 1.1) - confirmar o que de fato funciona.
3. **Este mes**: Polish loop (FASE 2 + 3) - tornar o existente bonito e satisfatorio antes de adicionar mais.
4. **Trimestre**: Profundidade de conteudo (FASE 4) e UX (FASE 5).
5. **Semestre**: Qualidade industrial (FASE 6) e producao (FASE 7).

---

**REVISADO EM:** 2026-05-12
**FILOSOFIA:** Ser honesto sobre o que existe, o que esta quebrado, e o que ainda falta.
**METRICA DE SUCESSO AAA:** Quando um jogador comum, sem instrucao previa, abre o jogo e
joga 30 minutos com prazer, sem confusao, sem bugs visiveis, sem precisar consultar nada externo.
