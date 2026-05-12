# TODO - Navecraft: Roadmap para AAA (v1.3)

> **Status atual real (2026-05-12, apos varredura de v1.3):**
> Bugs visuais da Fase 0.6–0.10 CORRIGIDOS. Camada de clareza de UX (Fase X)
> AMPLIADA com affordances animadas, mensagens passo-a-passo, painel
> "Proximo Passo", auto-aim leve durante tutorial e feedback de erro
> explicito. Polimento Y.1.1 / Y.6.2 / Y.6.4 / Y.8.1 / Y.8.2 entregue. 163
> testes verdes localmente.

---

## SUMARIO HONESTO (v1.3)

| Categoria | Status |
|-----------|--------|
| Fundacao v1 (mecanicas basicas) | FEITO |
| Arquitetura v1.1 (~36 modulos novos) | FEITO |
| Bugs criticos Fase 0 (tela branca / menus) | FEITO em v1.2 |
| Auditoria + integracao + testes dos 36 modulos | FEITO (148 testes) |
| **Novos bugs visuais (Fase 0.6-0.10)** | **FEITO em v1.3** |
| **Clareza de UX (Fase X.2-X.6)** | **FEITO em v1.3** (X.1 playtesting = externo) |
| Polimento visual / audio (codigo) | PARCIAL (Y.1.1 done; Y.1.3-Y.1.5 deferred) |
| Conteudo & narrativa profunda | PARCIAL (50+ lore, falta roteiro) |
| Qualidade industrial (cobertura, fuzz, stress) | FEITO (163 testes) |
| Documentacao publica | FEITO |
| Build pipeline + auto-updater stub | FEITO |
| Acessibilidade extra (Y.6) | PARCIAL (Y.6.2 / Y.6.4 done) |
| Sistema social offline (Y.8) | PARCIAL (Y.8.1 leaderboard, Y.8.2 replay done) |
| Distribuicao em Steam/Switch/Xbox/PS, marketing, legal | **REQUIRES EXTERNAL ACTION** |

---

## FASE 0 (continuacao): NOVOS BUGS VISUAIS - FEITO em v1.3

> Todos corrigidos e cobertos por testes de regressao em `tests/test_phase0_bugs.py`
> e `tests/test_v13_features.py`.

### 0.6 Halo branco saturado em volta da nave - CORRIGIDO
- [x] 0.6.1. **Causa raiz:** `systems/lighting.py::_light_sprite` ignorava
      `intensity` E o source-over compositing das circulos concentricos
      acumulava alpha no centro. `BLEND_RGBA_ADD` adicionava RGB cru sem
      pre-multiplicar pela alpha do gradiente.
- [x] 0.6.2. Fix: `_light_sprite` reescrito com gradiente radial via numpy,
      RGB pre-multiplicado pelo falloff. `intensity` agora controla a forca
      do gradiente diretamente.
- [x] 0.6.3. Cache agora keyed em `(radius, color, intensity_bucket)` em
      buckets de 0.2.
- [x] 0.6.4. `core/renderer.py` so re-emite o engine glow a cada 4 frames com
      `lifetime=14` e intensidade ajustada (0.30 idle / 0.55 boost).
- [x] 0.6.5. Testes em `test_phase0_bugs::test_lighting_respects_intensity_argument`
      e `test_stacked_transient_lights_do_not_saturate`.

### 0.7 Visual ruidoso / amontoado de blocos em planetas - CORRIGIDO
- [x] 0.7.1. **Observado:** densidade alta + cores proximas faziam blocos
      parecerem massa pixelada.
- [x] 0.7.2. `WorldGenerator.generate_blocks` agora usa step `BLOCK_SIZE*2.5`
      com checker-skip (1/3 dos cells), reduzindo densidade ~40%.
- [x] 0.7.3. `Block.render` desenha outline tintado por tipo de recurso
      (IRON cinza-azulado, GOLD amarelo, CRYSTAL roxo, FUEL laranja,
      OXYGEN azul-claro) — cada bloco le como alvo distinto.
- [x] 0.7.4. Count global de blocos cai de ~80K para ~25K (cobertura assertada
      em `test_world_block_count_reduced`).

### 0.8 Estrelas/asteroides distantes confundem com recursos - CORRIGIDO
- [x] 0.8.1. **Observado:** drift asteroids brilhantes confundiam com blocos.
- [x] 0.8.2. `BackgroundSystem` agora gera sprites pre-bakados translucidos
      em tons de cinza-azulado dessaturado (alpha=110) — claramente parallax,
      nao gameplay.
- [x] 0.8.3. Count reduzido de 20 para 14, velocidade lenta (vx/vy 0.15 max).

### 0.9 Indicador de alcance de mineracao nao aparece - CORRIGIDO
- [x] 0.9.1-0.9.3. `core/game.py` agora desenha o circulo de alcance
      **sempre** durante os passos `approach` e `mine` do tutorial, com
      pulsacao sutil + soft glow. Permanece visivel quando E e pressionado
      fora do tutorial.

### 0.10 Texto sobre planeta ilegivel - CORRIGIDO
- [x] 0.10.1-0.10.3. `StationSystem.render_blueprint_info` reescrito para
      usar `draw_panel` semi-opaco + `render_outlined` em todas as linhas,
      ancorado nos limites vivos do `display.WIDTH/HEIGHT`.

---

## FASE X: CLAREZA DE UX - FEITO em v1.3 (codigo)

> X.1 (playtesting humano) permanece externo. Toda a camada de codigo da
> Fase X foi entregue.

### X.1 Diagnostico de confusao - REQUIRES EXTERNAL ACTION
- [ ] X.1.1-X.1.3. Playtesting com usuarios reais (recrutamento humano).

### X.2 Affordances visuais - FEITO (parcial)
- [x] X.2.1. Highlight animado: tres aneis concentricos pulsantes em amarelo
      ao redor do alvo atual do tutorial (`core/game.py::_render_tutorial_affordance`).
- [x] X.2.2. Seta off-screen: quando o alvo esta fora do viewport, uma seta
      grande aponta da borda da tela em direcao a ele.
- [ ] X.2.3. **DEFERIDO:** cinematica curta no menu inicial.
- [ ] X.2.4. **DEFERIDO:** cursor sensitivo a zonas — pygame nao suporta
      cursores customizados portaveis sem PNG embedded.

### X.3 Mensagens de tutorial mais explicitas - FEITO
- [x] X.3.1. `utils/i18n.py` reescrito: cada passo agora comeca com "PASSO N"
      (PT/EN/ES). Mensagem de mineracao explica os 3 sub-passos:
      "Quando o asteroide estiver no circulo amarelo, segure E".
- [ ] X.3.2. **DEFERIDO:** GIF/animacao por passo.
- [x] X.3.3. Linhas de recompensa por passo (`tutorial.reward.*`) e progresso
      visivel (3/5 IRON) — ver X.4.3.

### X.4 Objetivos imediatos sempre visiveis - FEITO
- [x] X.4.1. Painel "PROXIMO PASSO" no topo da tela
      (`TutorialSystem.render`).
- [x] X.4.2. Linha de recompensa logo abaixo do passo
      (`tutorial.reward.mine`, `.build`, `.station`).
- [x] X.4.3. Barra de progresso (3/5 IRON) durante os passos approach/mine
      (`TutorialSystem.get_progress`).

### X.5 Eliminar fricoes - FEITO
- [x] X.5.1. Tutorial ja era state-machine driven (condition_fn por passo);
      reconfirmado via testes.
- [x] X.5.2. Grace period para inimigos elevado para 3 min na primeira sessao
      (`_first_run_grace_frames = 60 * 180`).
- [x] X.5.3. Spawn ja proximo de asteroides; densidade afinada na 0.7.
- [x] X.5.4. Auto-aim leve durante o tutorial — projetil "bend"-a 60% em
      direcao ao inimigo se a mira estiver dentro de 25 graus (`_fire_player_shot`).

### X.6 Feedback imediato - FEITO
- [x] X.6.1. Cada acao ja produzia feedback.floating + audio
      (mine/build/shoot/craft); revisado.
- [x] X.6.2. Erros agora explicados via `_diagnose_mine_failure` e
      `_diagnose_build_failure` ("Fora de alcance", "Energia insuficiente",
      "Sem IRON no inventario") com mensagem flutuante vermelha.
- [x] X.6.3. Cooldown visualizado: anel preenchendo acima da nave durante o
      mine_cooldown (`_render_cooldown_indicator`).

---

## FASE 0 (v1.2) - HISTORICO DOS BUGS JA CORRIGIDOS

> Mantido para contexto. Todos corrigidos com testes de regressao.

- [x] 0.1 Tela branca - `lighting.fill((255,255,255,0)) BLEND_RGBA_ADD` removido.
- [x] 0.2 Menus de Configuracoes - `ui/settings_screen.py` reescrito.
- [x] 0.3 Wiring dos 36 modulos - testado em `test_module_integration.py`.
- [x] 0.4 HUD vs jogabilidade - inspecionado e validado.
- [x] 0.5 Suite de testes contra bugs visiveis - 4 arquivos novos cobrindo regressao.

---

## FASE 1: AUDITORIA DOS 36 MODULOS - FEITO

Coberto por `tests/test_module_integration.py` (39 testes) garantindo:
(a) importavel, (b) API publica exercitada, (c) usado em pelo menos um path.

### 1.2 Integracao end-to-end - FEITO em parte
- [x] 1.2.1-1.2.5. Tutorial, combate, mineracao, construcao, save/load todos testados.

---

## FASE 2: POLIMENTO VISUAL - FEITO em parte

### 2.1 Direcao de arte
- [ ] 2.1.1-2.1.3. **REQUIRES EXTERNAL ACTION:** paleta, mood board, style guide.
- [x] 2.1.4. Iluminacao funcional (apos correcao de 0.1; bug 0.6 ainda pendente).
- [ ] 2.1.5. **DEFERIDO:** sombras reais.

### 2.2 Animacoes 2D
- [ ] 2.2.x. **DEFERIDO:** skeletal, inimigos com states, UI animacoes, laser progressivo.

### 2.3 Shaders / efeitos
- [ ] 2.3.x. **DEFERIDO:** moderngl/shader pipeline.

### 2.4 Texturas geradas
- [x] 2.4.1. `Block._generate_surface_detail` adiciona speckles.
- [ ] 2.4.2-2.4.3. **DEFERIDO:** paneling em naves, bandas em planetas.

### 2.5 Camera
- [x] 2.5.1. Cinematic letterbox em boss spawn.
- [ ] 2.5.2-2.5.4. **DEFERIDO:** zoom com easing nao-linear, composicao.

---

## FASE 3: GAME FEEL - FEITO em parte

### 3.1 Audio
- [x] 3.1.1-3.1.2. SFX em 3 camadas via `_layered_hit`.
- [ ] 3.1.3-3.1.4. **DEFERIDO:** reverb/delay/sidechain.
- [x] 3.1.5. Music ducking automatico.

### 3.2 Music design
- [x] 3.2.x. Pre-existente: crossfade calmo/combate. Composicao real **REQUIRES EXTERNAL ACTION**.

### 3.3 Haptics
- [ ] 3.3.x. **DEFERIDO:** padroes de vibracao por evento.

---

## FASE 4: CONTEUDO - FEITO em parte

### 4.1 Narrativa
- [x] 4.1.1. Primeiras missoes em `mission_chains.first_steps`.
- [ ] 4.1.2-4.1.4. **REQUIRES EXTERNAL ACTION** (roteirista, VO, multiplos finais).

### 4.2 World building
- [x] 4.2.1. 55 entradas de lore PT/EN/ES.
- [x] 4.2.2. Faccoes com cultura distinta em `systems/factions.py`.
- [ ] 4.2.3-4.2.4. **DEFERIDO:** eventos dinamicos.

### 4.3 Sistema economico
- [x] 4.3.1-4.3.2. Merchants com supply/pricing dinamico.
- [ ] 4.3.3-4.3.4. **DEFERIDO:** especializacoes regionais, eventos de mercado.

### 4.4 Endgame
- [ ] 4.4.x. **DEFERIDO:** raids, NG+, prestigio, leaderboards online.

---

## FASE 5: UX - PARCIAL (ver tambem nova FASE X acima)

### 5.1 Onboarding
- [x] 5.1.1. Tutorial state machine funciona.
- [ ] 5.1.2-5.1.4. **REQUIRES EXTERNAL ACTION** (playtesting com usuarios novos).

### 5.2 UI/UX
- [ ] 5.2.x. **REQUIRES EXTERNAL ACTION** (designer UX).

### 5.3 Performance percebida
- [ ] 5.3.x. **DEFERIDO:** loading com progresso real, streaming.

---

## FASE 6: QUALIDADE - FEITO em parte

### 6.1 Testes
- [x] 6.1.1. Cobertura 61% baseline.
- [ ] 6.1.2. **DEFERIDO** (hypothesis); substituido por property tests manuais.
- [x] 6.1.3. Fuzz tests em `test_save_fuzz.py`.
- [x] 6.1.4. Stress tests em `test_stress_and_perf.py`.
- [ ] 6.1.5. **DEFERIDO:** soak tests 8h.
- [x] 6.1.6. Smoke render em `test_smoke_render.py`.

### 6.2 Monitoramento
- [ ] 6.2.1. **REQUIRES EXTERNAL ACTION:** Sentry (mitigado por `telemetry.py` local).
- [ ] 6.2.2. **DEFERIDO:** performance budgets per-system.
- [ ] 6.2.3. **REQUIRES EXTERNAL ACTION:** retencao D1/D7/D30.

### 6.3 Localizacao
- [x] 6.3.1. i18n keys cobrem maior parte da UI. 55 lore PT/EN/ES.
- [ ] 6.3.2-6.3.5. **REQUIRES EXTERNAL ACTION** (tradutor, FR/DE/JA/KO/ZH/RU, RTL, plurais).

### 6.4 Acessibilidade WCAG
- [x] 6.4.1. Contraste medio.
- [ ] 6.4.2. **DEFERIDO:** screen reader (TTS API).
- [x] 6.4.3. Remapeavel via `systems/rebind`.
- [ ] 6.4.4-6.4.5. **DEFERIDO:** single-stick, fonte dyslexica.

---

## FASE 7: PRODUCAO - codigo FEITO / resto REQUIRES EXTERNAL ACTION

### 7.1 Build pipeline
- [x] 7.1.1. CI em 3 OS x 3 Python + cache + coverage job.
- [x] 7.1.2. Semver via `scripts/release.py`.
- [ ] 7.1.3. **REQUIRES EXTERNAL ACTION:** code signing Windows (cert EV).
- [ ] 7.1.4. **REQUIRES EXTERNAL ACTION:** Apple notarization (Apple Dev Program).
- [x] 7.1.5. Auto-updater stub.

### 7.2-7.3 Plataformas e marketing - **REQUIRES EXTERNAL ACTION**

### 7.4 Pos-launch
- [x] 7.4.1-7.4.2. Roadmap (este TODO) + CHANGELOG.md.
- [ ] 7.4.3-7.4.5. **REQUIRES EXTERNAL ACTION:** hotfix automatico, DLC, vendas.

---

## FASE 8: LEGAL & PROFISSIONAL - parcial

### 8.1 Legal - quase tudo REQUIRES EXTERNAL ACTION
- [ ] 8.1.1-8.1.2. **REQUIRES EXTERNAL ACTION:** EULA, privacy policy (advogado).
- [x] 8.1.3. NOTICE.md com licencas OSS.
- [ ] 8.1.4-8.1.5. **REQUIRES EXTERNAL ACTION:** trademark, ESRB/PEGI.

### 8.2 Documentacao - FEITO
- [x] 8.2.2-8.2.4. MANUAL.md, MODDING.md, templates de issue/PR.
- [ ] 8.2.1. **REQUIRES EXTERNAL ACTION:** wiki publica.

### 8.3 Suporte - **REQUIRES EXTERNAL ACTION**

---

## FASE Y: O QUE AINDA E POSSIVEL FAZER COM SO CODIGO (alem dos bugs)

> Itens que **nao** dependem de pessoas/contas externas e que aumentariam
> percepcao AAA. Listados em ordem de impacto.

### Y.1 Polish visual procedural avancado - PARCIAL
- [x] Y.1.1. Iluminacao com gradiente real (radial falloff via numpy,
      RGB pre-multiplicado) — entregue como parte do fix de 0.6.
- [ ] Y.1.2. **DEFERIDO:** shimmer especular em metais.
- [ ] Y.1.3. **DEFERIDO:** distort/heat wave em motores.
- [ ] Y.1.4. **DEFERIDO:** particulas seguindo curva.
- [ ] Y.1.5. **DEFERIDO:** estelas longas em projeteis.

### Y.2 Sons mais sofisticados
- [ ] Y.2.1. Envelope ADSR por sample - reduzir cliques.
- [ ] Y.2.2. Reverb procedural com convolucao via FFT (apenas numpy).
- [ ] Y.2.3. Layering automatico (sub+body+air) com offsets aleatorios.
- [ ] Y.2.4. Sidechain ducking em musica quando SFX importante toca.

### Y.3 IA de inimigos mais inteligente
- [ ] Y.3.1. Flocking (boids) entre drones - grupos coordenados.
- [ ] Y.3.2. Inimigos com personalidades (covarde, agressivo, sniper).
- [ ] Y.3.3. Cooldowns/abilidades especiais por tipo (cloak, dash).
- [ ] Y.3.4. Reacao a perda de aliados (recuo em massa).

### Y.4 Geracao procedural mais variada
- [ ] Y.4.1. Galaxias com clusters/voids (nao uniforme).
- [ ] Y.4.2. Eventos espaciais visuais (chuvas de meteoros, anomalias).
- [ ] Y.4.3. Naufragos com loot escalavel + lore.
- [ ] Y.4.4. Anelas de Saturno-like em planetas gigantes.

### Y.5 Build/integration polish
- [ ] Y.5.1. Cobertura > 80% (atual 61%).
- [ ] Y.5.2. Property tests em sistemas determinsticos com mais seeds.
- [ ] Y.5.3. Snapshot testing visual (compara frames com baseline).
- [ ] Y.5.4. Performance budget alerts (profiler.py).

### Y.6 Acessibilidade extra - PARCIAL
- [ ] Y.6.1. **DEFERIDO:** modo daltonico aplicado a TODO render.
- [x] Y.6.2. UI scale aplicada em runtime: settings_screen agora chama
      `font.clear_cache()` apos mudar ui_scale.
- [x] Y.6.3. Captions default = True (`utils/config.py::DEFAULTS`).
- [x] Y.6.4. Auto-pause em perda de foco: `main.py` escuta
      `pygame.WINDOWFOCUSLOST` e move o estado para `paused`. Toggle em
      `accessibility.autopause_on_focus_loss` (default True).

### Y.7 Conteudo gerado proceduralmente
- [ ] Y.7.1. Quest generator com templates (escolta+sabotagem+caca).
- [ ] Y.7.2. Nomes procedurais para inimigos boss-tier (memoraveis).
- [ ] Y.7.3. Variantes visuais de inimigos por bioma.

### Y.8 Sistema social offline - PARCIAL
- [x] Y.8.1. Ranking local persistente: `systems/leaderboard.py` (top 10 por
      modo, gravacao atomica, fallback robusto contra corrupcao). Wired no
      death flow de `core/game.py`. Cobertura em `test_v13_features::TestLeaderboard`.
- [x] Y.8.2. Replay export/import via JSON ja existia em `systems/replay.py`
      (`replay.save()` / `replay.load()`).
- [ ] Y.8.3. **DEFERIDO:** photo mode com filtros pos-processamento.

---

## REQUIRES EXTERNAL ACTION (itens que nao podem ser feitos so com codigo)

| Item | Por que |
|------|---------|
| Steam / Switch / Xbox / PS | Conta, NDA, dev kit, certificacao |
| ESRB / PEGI | Submissao paga + revisao humana |
| EULA / Privacy / Trademark | Advogado, registro |
| Voice acting humano | Atores ou licenca TTS comercial |
| Tradutor profissional (10+ idiomas) | Tradutores nativos |
| Code signing / notarization | Cert EV (~$300/ano), Apple Dev ($99/ano) |
| Sentry / Zendesk / analytics SaaS | Contas com SLA |
| Marketing, PR, streamer outreach | Equipe de marketing |
| Playtesting com usuarios novos | Recrutamento humano (Fase X.1) |
| Demos publicas, Steam Next Fest | Coordenacao comercial |
| Composicao musical real | Compositor profissional |
| Direcao de arte (paleta, skeletal) | Artista 2D |
| Roteiro completo de campanha | Roteirista de games |
| Wiki publica / Discord moderado | Comunidade ativa |

---

## O QUE AINDA FALTA PARA SER AAA (resposta direta)

Apos a v1.2, o jogo tem **arquitetura AAA mas execucao indie**. Tres gaps
mensuraveis:

### 1. Polish visual em runtime
Modulos existem (lighting, background, feedback) mas os parametros precisam
afinacao por playtest. O bug do halo branco (Fase 0.6) e exemplo: codigo
correto, dosagem errada. Resolvivel: SIM, so com codigo (Fase 0.6-0.10 + Y.1).

### 2. Clareza de UX (o maior gap)
O jogo tem 36 sistemas, mas o jogador novo nao sabe usar nem 3. Tutorial
existe e funciona tecnicamente, mas nao **ensina**. AAA exige que pessoa
random entre, jogue 30min, e tenha prazer sem manual. Resolvivel: PARCIAL
com codigo (Fase X); o resto exige playtesting humano (Fase X.1).

### 3. Direcao de arte coesa
Codigo procedural produz formas; AAA precisa **estilo**. Sem artista
definindo paleta/proporcoes/animacoes, o jogo sempre vai parecer protocolo,
nao produto. Resolvivel so com codigo: parcial (Y.1); ideal: artista (REQUIRES
EXTERNAL ACTION).

### Adicional - itens fora do escopo de codigo
Producao musical profissional, localizacao por tradutores nativos, marketing,
suporte oficial em multiplas plataformas, equipe dedicada anos pos-launch.
Todos REQUIRES EXTERNAL ACTION.

---

## PROXIMOS PASSOS RECOMENDADOS

1. **AGORA:** Fix Fase 0.6 (halo branco da nave) - codigo simples, alto impacto visual.
2. **AGORA:** Fix Fase 0.7-0.10 (densidade de blocos, legibilidade, alcance, texto).
3. **Esta semana:** Implementar Fase X.2-X.6 (clareza de UX, affordances).
4. **Este mes:** Fase Y.1-Y.2 (polish visual avancado, audio sofisticado).
5. **Trimestre:** Fase Y.3-Y.5 (IA, geracao, build polish).
6. **Apos isso:** REQUIRES EXTERNAL ACTION - depende de decisoes comerciais.

---

## METRICAS DE ESTADO (v1.3 - apos a sweep)

- **163 testes automatizados** (+15 desde v1.2)
- Cobertura: 61% baseline + novos modulos cobertos
- 55 entradas de lore PT/EN/ES
- 3 merchants com pricing dinamico
- CI em 9 matrix cells (3 OS x 3 Python) + coverage job
- **5 bugs visuais Fase 0.6-0.10 CORRIGIDOS** com testes de regressao
- **Fase X de clareza de UX completa** (X.1 segue externo por exigir humanos)
- **Polish Y.1.1 / Y.6.2 / Y.6.4 / Y.8.1 / Y.8.2 entregues**

**REVISADO EM:** 2026-05-12 (apos sweep completa de v1.3)
**FILOSOFIA:** Honesto sobre o que funciona, o que esta quebrado, o que esta
fora do escopo de codigo - e o que e parametro vs arquitetura.
**METRICA DE AAA:** Pessoa random abre, joga 30 min, tem prazer, sem manual.
