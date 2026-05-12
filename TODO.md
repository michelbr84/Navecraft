# TODO - Navecraft: Roadmap para AAA (v1.2)

> **Status atual real (2026-05-12, pos-v1.2):** Fase 0 (bugs criticos) e
> Fase 1 (auditoria dos 36 modulos) concluidas. Polimento de codigo em
> Fases 2-8 onde aplicavel. Itens que dependem de pessoas externas, contas,
> dinheiro ou parceria comercial estao agora agrupados em
> "REQUIRES EXTERNAL ACTION" e nao dependem mais de codigo.

---

## SUMARIO HONESTO (atualizado)

| Categoria | Status |
|-----------|--------|
| Fundacao v1 (mecanicas basicas) | FEITO |
| Arquitetura v1.1 (~36 modulos novos) | FEITO |
| Bugs criticos bloqueando jogabilidade (Fase 0) | **FEITO (PR atual)** |
| Auditoria + integracao + testes dos 36 modulos | **FEITO (148 testes)** |
| Polimento visual / audio que dependeu so de codigo | **FEITO em parte** |
| Conteudo: 50+ lore PT/EN/ES + economia dinamica | **FEITO** |
| Qualidade: cobertura + fuzz + property + stress + smoke | **FEITO (61% baseline)** |
| Documentacao publica (NOTICE, MANUAL, MODDING, etc) | **FEITO** |
| Build pipeline (cache, coverage job, semver, updater stub) | **FEITO** |
| Distribuicao em Steam/Switch/Xbox/PS, marketing, legal | **REQUIRES EXTERNAL ACTION** |

---

## FASE 0: BUGS CRITICOS - FEITO

### 0.1 Mundo nao renderiza (TELA BRANCA) - FEITO
- [x] 0.1.1. Identificado: `systems/lighting.py` fazia `light_buf.fill((255,255,255,0))` com `BLEND_RGBA_ADD`, pintando tudo de branco.
- [x] 0.1.2-0.1.5. Corrigido em `systems/lighting.py`. Default agora e `ambient=1.0` (sem alteracao), `ambient<1.0` darken multiplicativo.
- [x] 0.1.6. `tests/test_phase0_bugs.py` tem teste end-to-end `test_full_game_render_first_frame_is_not_uniform` que renderiza um frame real de `Game()` e exige >8 cores distintas + nao majoritariamente branco. `tests/test_smoke_render.py` adiciona 4 verificacoes complementares.

### 0.2 Menu de Configuracoes nao interativo - FEITO
- [x] 0.2.1-0.2.5. Reescrita do `ui/settings_screen.py`: UP/DOWN consomem evento (eram False), Enter/Espaco/Click ativam linha, setas Esq/Dir ajustam valores, ESC fecha, suporte a clique do mouse com hit-test em abas e linhas, suporte a roda do mouse.
- [x] 0.2.6. `tests/test_phase0_bugs.py::TestSettingsScreenInteractive` cobre toggle bool, ajuste de volume, consumo UP/DOWN, troca de aba, clique em aba.
- [x] **Bonus:** mudancas de audio agora aplicam ao vivo via `set_audio_change_listener` -> `AudioSystem.refresh_volumes()`.

### 0.3 Integracao de modulos novos - FEITO
- [x] 0.3.1. Auditados via grep + `tests/test_module_integration.py::test_all_36_new_modules_importable`.
- [x] 0.3.2. Os criticos (lighting, background, feedback, tutorial) estao wired em `Game.update`/`render`.
- [x] 0.3.3. `main.py` ja usa state machine + fade_then.
- [x] 0.3.4. **Codigo dead descoberto:** `systems/rebind.apply_rebinds` era criado mas NUNCA chamado. Wired em `core/input.py::InputManager.__init__`. Keybinds do usuario agora realmente funcionam.

### 0.4 HUD vs jogabilidade - FEITO
- [x] 0.4.1. HUD inspecionado em `ui/hud.py`.
- [x] 0.4.2. Spawn em (7860, 9760) e intencional (first_run spawn proximo ao planeta amigo).
- [x] 0.4.3. Minimap agora renderiza blocos de recursos proximos (sub-amostrados) - antes parecia vazio.
- [x] 0.4.4. Inventario rapido funciona corretamente (0 = recurso ainda nao coletado).

### 0.5 Suite de testes contra bugs visiveis - FEITO
- [x] 0.5.1. `test_full_game_render_first_frame_is_not_uniform` + `test_smoke_render`.
- [x] 0.5.2. `TestSettingsScreenInteractive` cobre toda navegacao + clique.
- [x] 0.5.3. (Fullscreen toggle ja era testavel; F11 nao crasha.)
- [x] 0.5.4. `tests/test_save_fuzz.py` tem 4 testes: missing file, JSON corrompido, arquivo truncado, 20 mutacoes aleatorias. Zero crashes.

---

## FASE 1: AUDITORIA DOS 36 MODULOS - FEITO

Cada item de 1.1.1 ate 1.1.36 esta coberto por pelo menos um teste de
integracao em `tests/test_module_integration.py` (39 testes). O modulo:
- (a) e importavel sem erro
- (b) tem sua API publica exercitada
- (c) e usado por `Game()` ou `Navecraft` em pelo menos um caminho

### 1.2 Integracao end-to-end - FEITO em parte
- [x] 1.2.1. Tutorial roda etapa por etapa (testado em `TestTutorialStateMachine`).
- [x] 1.2.2. Combate: tiros + hitstop + numbers + shake + sound + xp + drops todos disparam em `Game._update_enemies_and_projectiles`.
- [x] 1.2.3. Mineracao: alcance + cracks + drops + texto flutuante + som + xp testado em `tests/test_fixes.py::TestMining` + integracao em `Game._update_spaceship`.
- [x] 1.2.4. Construcao: preview + custo + som + inventario testado em `tests/test_fixes.py::TestStationSystem`.
- [x] 1.2.5. Save/load: `tests/test_save_fuzz.py` + `TestSaveSystem` em test_fixes.

---

## FASE 2: POLIMENTO VISUAL - FEITO em parte

### 2.1 Direcao de arte
- [ ] 2.1.1. **REQUIRES EXTERNAL ACTION:** definicao de paleta coesa precisa de artista.
- [ ] 2.1.2. **REQUIRES EXTERNAL ACTION:** mood board.
- [ ] 2.1.3. **REQUIRES EXTERNAL ACTION:** style guide escrito.
- [x] 2.1.4. Iluminacao funcional (apos correcao do bug); cria atmosfera nos eventos.
- [ ] 2.1.5. **DEFERIDO:** sombras reais exigem retrabalho de renderizador.

### 2.2 Animacoes 2D - parcial
- [ ] 2.2.1. **DEFERIDO:** skeletal animation precisa de framework.
- [ ] 2.2.2. **DEFERIDO:** inimigos com idle/move/attack/death.
- [ ] 2.2.3. **DEFERIDO:** UI animacoes (slide-in, fade, bounce).
- [ ] 2.2.4. **DEFERIDO:** laser progressivo (mineracao binaria atualmente).

### 2.3 Shaders / efeitos
- [ ] 2.3.x. **DEFERIDO:** moderngl/shader pipeline e refactor grande.

### 2.4 Texturas geradas
- [x] 2.4.1. Cada bloco agora tem 6 manchas procedurais (noise speckles) por instancia, calculadas uma vez no construtor. Veja `Block._generate_surface_detail`.
- [ ] 2.4.2. Naves: paneling lines - **DEFERIDO**.
- [ ] 2.4.3. Planetas com bandas de biomas - **DEFERIDO**.

### 2.5 Camera de qualidade
- [x] 2.5.1. Cinematic letterbox no spawn do boss - via `feedback.letterbox()`.
- [ ] 2.5.2. Zoom suave - camera ja tem easing, mas curves nao-lineares ficam para depois.
- [ ] 2.5.3-2.5.4. **DEFERIDO:** mais composicao e letterbox cobrem o caso AAA mais sentido.

---

## FASE 3: GAME FEEL - FEITO em parte

### 3.1 Audio que vende impacto
- [x] 3.1.1-3.1.2. SFX agora tem 3 camadas (sub + body + crack) via `_layered_hit`. Todos os 5 hits de inimigos foram refeitos.
- [ ] 3.1.3. **DEFERIDO:** reverbs/delays simulados precisam de convolution.
- [ ] 3.1.4. **DEFERIDO:** sidechain compression.
- [x] 3.1.5. Music ducking automatico via `AudioSystem.duck_music` + `update_duck`. Disparado no spawn do boss.

### 3.2 Music design
- [x] 3.2.x. Pre-existente: musica calma/combate com crossfade. Composicao real requer compositor humano (REQUIRES EXTERNAL ACTION).

### 3.3 Haptics
- [ ] 3.3.x. **DEFERIDO:** gamepad ja existe; padroes de vibracao distintos por evento sao polish.

---

## FASE 4: CONTEUDO - FEITO em parte

### 4.1 Narrativa real
- [x] 4.1.1. **PARCIAL:** primeiras missoes ja existem em `mission_chains.first_steps`. Roteiro completo seria escrita extensa (REQUIRES EXTERNAL ACTION para roteirista).
- [ ] 4.1.2-4.1.4. **REQUIRES EXTERNAL ACTION** (roteiro, voice acting, multiplos finais).

### 4.2 World building
- [x] 4.2.1. **FEITO:** `systems/codex.py` agora tem 55 entradas de lore em PT/EN/ES (era 3).
- [x] 4.2.2. Faccoes ja tem cultura distinta em `systems/factions.py`; visualmente distintas exige artista.
- [ ] 4.2.3-4.2.4. **DEFERIDO:** eventos dinamicos requerem simulacao mais complexa.

### 4.3 Sistema economico
- [x] 4.3.1. **FEITO:** cada merchant tem `_supply` factor por recurso (0.6-1.4) + uma especialidade. Precos calculados na construcao.
- [x] 4.3.2. Precos variam por merchant - jogadores tem incentivo para hauling entre estacoes.
- [ ] 4.3.3. **DEFERIDO:** especializacoes regionais por planeta.
- [ ] 4.3.4. **DEFERIDO:** eventos de mercado (escassez, boom).

### 4.4 Endgame
- [ ] 4.4.x. **DEFERIDO:** raids/NG+/prestigio/leaderboards exigem escopo de meses.

---

## FASE 5: UX - FEITO em parte

### 5.1 Onboarding
- [x] 5.1.1. Tutorial state machine ja existe e funciona.
- [ ] 5.1.2-5.1.4. **REQUIRES EXTERNAL ACTION** (playtesting com usuarios novos, telemetria de funil).

### 5.2 UI/UX
- [ ] 5.2.x. **REQUIRES EXTERNAL ACTION** (designer UX, heuristicas Nielsen).

### 5.3 Performance percebida
- [ ] 5.3.1-5.3.4. **DEFERIDO:** loading com progresso real, streaming, etc.

---

## FASE 6: QUALIDADE - FEITO em parte

### 6.1 Testes
- [x] 6.1.1. Cobertura **61% baseline** medida via `coverage`. Configuracao em `pyproject.toml`. Job dedicado no CI.
- [ ] 6.1.2. **DEFERIDO** (hypothesis): substituido por property tests manuais com seeds determinsticas em `tests/test_inventory_property.py`. Mesmo efeito sem nova dependencia.
- [x] 6.1.3. `tests/test_save_fuzz.py` faz fuzzing real de arquivos JSON (5 estrategias de mutacao, 20 iteracoes aleatorias).
- [x] 6.1.4. `tests/test_stress_and_perf.py` faz stress: 10k entidades no spatial hash, 60 frames full-game, 500 projectiles, todos com budget.
- [ ] 6.1.5. **DEFERIDO:** soak tests de 8h nao cabem em CI (precisa rodar offline em harness dedicada).
- [x] 6.1.6. `tests/test_smoke_render.py` verifica que o frame tem cores distintas, dark bg, bright pixels, nao pure-white.

### 6.2 Monitoramento
- [ ] 6.2.1. **REQUIRES EXTERNAL ACTION:** Sentry exige conta + endpoint. Substituido: `systems/telemetry.py` faz log_crash local opt-in.
- [ ] 6.2.2. **DEFERIDO:** performance budgets per-system (`profiler.py` ja mede; alertas ficam para outra issue).
- [ ] 6.2.3. **REQUIRES EXTERNAL ACTION:** retencao D1/D7/D30 precisa de analytics backend.

### 6.3 Localizacao
- [x] 6.3.1. Auditoria parcial: i18n keys ja existem para a maioria das UI. 55 entradas de lore agora em PT/EN/ES.
- [ ] 6.3.2-6.3.5. **REQUIRES EXTERNAL ACTION** (tradutor profissional, FR/DE/JA/KO/ZH/RU, RTL, regras plurais).

### 6.4 Acessibilidade WCAG
- [x] 6.4.1. Contraste medio nas barras de status (cores AAA inversas em estado critico).
- [ ] 6.4.2. **DEFERIDO:** screen reader (NVDA/JAWS) precisa de TTS API integration.
- [x] 6.4.3. Remapeavel via `systems/rebind` (agora REALMENTE funciona).
- [ ] 6.4.4-6.4.5. **DEFERIDO:** single-stick mode, font dyslexico.

---

## FASE 7: PRODUCAO - FEITO em parte (codigo) / RESTO REQUER EXTERNAL ACTION

### 7.1 Build pipeline
- [x] 7.1.1. CI ja roda testes em 3 OS x 3 Python na branch + PR. Adicionado pip cache + job de coverage.
- [x] 7.1.2. Versionamento semantico: `scripts/release.py` faz bump/set/tag.
- [ ] 7.1.3. **REQUIRES EXTERNAL ACTION:** code signing Windows (precisa cert EV).
- [ ] 7.1.4. **REQUIRES EXTERNAL ACTION:** notarization Apple (precisa Apple Developer Program).
- [x] 7.1.5. Auto-updater stub em `utils/auto_updater.py` - checa `latest.json` opt-in.

### 7.2 Plataformas - TODAS REQUIRES EXTERNAL ACTION
- [ ] 7.2.1. **REQUIRES EXTERNAL ACTION:** Steamworks (precisa Steamworks account, $100, achievements API).
- [ ] 7.2.2. **REQUIRES EXTERNAL ACTION:** itch.io (precisa upload).
- [ ] 7.2.3. **REQUIRES EXTERNAL ACTION:** GOG (precisa parceria).
- [ ] 7.2.4. **REQUIRES EXTERNAL ACTION:** Epic Games Store (precisa parceria).
- [ ] 7.2.5. **REQUIRES EXTERNAL ACTION:** consoles (Nintendo, Xbox, PlayStation - precisa NDA + dev kit).

### 7.3 Marketing - TODAS REQUIRES EXTERNAL ACTION
- [ ] 7.3.x. **REQUIRES EXTERNAL ACTION** (Steam page, wishlist campaign, demo Next Fest, press kit, streamers, Discord).

### 7.4 Pos-launch
- [x] 7.4.1. Roadmap publico: este TODO.md (versionado em git).
- [x] 7.4.2. Patch notes: `CHANGELOG.md` adicionado.
- [ ] 7.4.3. **REQUIRES EXTERNAL ACTION:** hotfix automatizado precisa de servidor de updates.
- [ ] 7.4.4-7.4.5. **REQUIRES EXTERNAL ACTION:** DLC e estrategia de vendas.

---

## FASE 8: LEGAL & PROFISSIONAL - parcialmente FEITO

### 8.1 Legal - quase tudo REQUIRES EXTERNAL ACTION
- [ ] 8.1.1. **REQUIRES EXTERNAL ACTION:** EULA - precisa advogado.
- [ ] 8.1.2. **REQUIRES EXTERNAL ACTION:** privacy policy GDPR/LGPD - precisa advogado. Mitigado parcialmente: `SECURITY.md` documenta que telemetria fica local.
- [x] 8.1.3. `NOTICE.md` lista todas as bibliotecas OSS e suas licencas.
- [ ] 8.1.4. **REQUIRES EXTERNAL ACTION:** trademark do nome.
- [ ] 8.1.5. **REQUIRES EXTERNAL ACTION:** ESRB/PEGI rating ($).

### 8.2 Documentacao - FEITO
- [ ] 8.2.1. **REQUIRES EXTERNAL ACTION:** wiki publica (precisa hospedagem + mods).
- [x] 8.2.2. Manual em Markdown (`docs/MANUAL.md`) - pode ser exportado para PDF.
- [x] 8.2.3. `docs/MODDING.md` com exemplos de mods.
- [x] 8.2.4. `.github/ISSUE_TEMPLATE/bug_report.md` + `feature_request.md` + PR template.

### 8.3 Suporte - REQUIRES EXTERNAL ACTION
- [ ] 8.3.x. **REQUIRES EXTERNAL ACTION** (Zendesk, FAQ publica, Discord moderado).

---

## REQUIRES EXTERNAL ACTION (resumo dos itens fora do escopo de codigo)

Estes itens nao podem ser feitos so com codigo. Precisam, conforme indicado:

| Item | Por que nao tem como ser so codigo |
|------|-------------------------------------|
| Steam / Switch / Xbox / PS | Conta, NDA, dev kit, certificacao |
| ESRB / PEGI | Submissao paga + revisao humana |
| EULA / Privacy Policy / Trademark | Advogado, registro |
| Voice acting humano | Atores reais ou licenca de TTS comercial |
| Tradutor profissional (10+ idiomas) | Tradutores nativos |
| Code signing Windows + notarization Apple | Certificado EV (~$300/ano), Apple Dev ($99/ano) |
| Sentry, Zendesk, analytics SaaS | Contas com SLA |
| Marketing, PR, streamer outreach | Equipe de marketing |
| Playtesting com usuarios novos | Recrutamento humano |
| Demos publicas, eventos (Steam Next Fest) | Coordenacao comercial |
| Composicao musical real (motifs, mixing) | Compositor profissional |
| Direcao de arte (paleta, animacoes skeletal) | Artista 2D |
| Roteiro completo de campanha | Roteirista de games |
| Wiki publica moderada / Discord comunidade | Comunidade ativa + mods humanos |

---

## METRICAS DE ESTADO (apos v1.2)

- 148 testes automatizados (era 64) - +131%
- Cobertura: 61% baseline (medida)
- 55 entradas de lore (era 3) - +1733%
- 3 merchants espalhados com pricing dinamico (era 1 fixo)
- CI rodando em 9 matrix cells (3 OS x 3 Python) + job de coverage
- Bugs criticos da Fase 0: **todos corrigidos** com testes de regressao

**REVISADO EM:** 2026-05-12 (apos PR de pragmatic completion)
**FILOSOFIA:** Ser honesto sobre o que existe, o que esta quebrado, o que ainda falta - e o que esta fora do escopo de codigo.
