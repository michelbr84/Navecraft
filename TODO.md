# TODO - Navecraft: Roadmap para AAA (v1.3)

> **Status atual real (2026-05-12, pos-v1.2 + observacoes em runtime):**
> Bug critico de tela branca CORRIGIDO. Jogo agora renderiza fundo, asteroides
> e planetas. Porem **novos bugs visuais** apareceram em uso real (ver Fase 0
> abaixo) e a **clareza de UX** continua sendo o maior bloqueio para qualidade
> AAA. Jogador ainda nao entende o que fazer mesmo com tutorial ativo.

---

## SUMARIO HONESTO (v1.3)

| Categoria | Status |
|-----------|--------|
| Fundacao v1 (mecanicas basicas) | FEITO |
| Arquitetura v1.1 (~36 modulos novos) | FEITO |
| Bugs criticos Fase 0 (tela branca / menus) | FEITO em v1.2 |
| Auditoria + integracao + testes dos 36 modulos | FEITO (148 testes) |
| **Novos bugs visuais (Fase 0.6+)** | **PENDENTE - PRIORIDADE MAXIMA** |
| **Clareza de UX (Fase X - novo)** | **PENDENTE - PRIORIDADE MAXIMA** |
| Polimento visual / audio (codigo) | PARCIAL |
| Conteudo & narrativa profunda | PARCIAL (50+ lore, falta roteiro) |
| Qualidade industrial (cobertura, fuzz, stress) | FEITO (61% baseline) |
| Documentacao publica | FEITO |
| Build pipeline + auto-updater stub | FEITO |
| Distribuicao em Steam/Switch/Xbox/PS, marketing, legal | **REQUIRES EXTERNAL ACTION** |

---

## FASE 0 (continuacao): NOVOS BUGS VISUAIS OBSERVADOS

> Reportados em runtime apos v1.2 mergeada. Visiveis em screenshot do jogo.

### 0.6 Halo branco saturado em volta da nave - URGENTE
- [ ] 0.6.1. **Causa raiz identificada:** `core/renderer.py:45-47` chama
      `lighting.add_transient` toda frame com `radius=48, intensity=1.0,
      lifetime=4`. Mas `systems/lighting.py:_light_sprite` IGNORA `intensity`
      (so usa `radius` e `color` no cache). Cada frame deposita um sprite
      novo com alpha ate 180; quatro lights overlapped saturam a area em
      branco/cyan claro - dai o "circulo branco" perceptivel.
- [ ] 0.6.2. Fix: aplicar `intensity` real ao gerar o sprite (ou multiplicar
      alpha por `intensity` no blit). Ver `_light_sprite()` linha 47-58.
- [ ] 0.6.3. Fix alternativo: cachear sprite por `(radius, color, intensity_bucket)`
      em buckets de 0.2 para nao explodir o cache.
- [ ] 0.6.4. Reduzir a frequencia: em vez de toda frame, atualizar a luz do
      motor com lifetime maior (ex: 12) e re-adicionar a cada 4 frames.
- [ ] 0.6.5. Teste de regressao: capturar pixel no centro da nave + 8px ao
      lado e verificar que NAO sao quase brancos quando HP=100% e nao boosting.

### 0.7 Visual ruidoso / amontoado de blocos em planetas
- [ ] 0.7.1. **Observado:** ao redor do planeta proximo, blocos de recursos
      ficam tao densamente empilhados que parecem um "pixelado roxo/amarelo".
      Nao da pra distinguir blocos individuais nem para mirar mineracao.
- [ ] 0.7.2. Ajustar densidade em `systems/generation.py` - espacamento minimo
      maior entre blocos, ou clusters menores.
- [ ] 0.7.3. Adicionar contorno/glow distinto por tipo de recurso para
      legibilidade (atualmente cores estao muito proximas no fundo escuro).
- [ ] 0.7.4. Reduzir count de blocos por planeta (atualmente parecem 100+; ideal 20-40).

### 0.8 Estrelas/asteroides distantes confundem com recursos
- [ ] 0.8.1. **Observado:** pontinhos pequenos espalhados pelo fundo parecem
      iguais aos blocos minerables - jogador nao distingue background de gameplay.
- [ ] 0.8.2. Background asteroides (parallax distante) devem ter cor neutra/desbotada
      claramente distinta dos blocos foreground.
- [ ] 0.8.3. Adicionar leve blur ou reducao de saturacao em camadas distantes.

### 0.9 Indicador de alcance de mineracao nao aparece
- [ ] 0.9.1. Tutorial diz "alcance amarelo" mas no screenshot nao ha circulo
      visivel ao redor da nave indicando alcance de E.
- [ ] 0.9.2. Verificar se o render esta condicionado a E pressionado e se
      jogador esta segurando a tecla durante o tutorial.
- [ ] 0.9.3. Considerar mostrar o alcance SEMPRE durante tutorial (nao so com E).

### 0.10 Texto sobre planeta ilegivel
- [ ] 0.10.1. Texto "Estacao: Posto Avancado / Custo: 20 IRON, 10 FUEL /
      Reconstruir estacao" no canto esquerdo aparece em cinza escuro sobre
      o planeta roxo - quase invisivel.
- [ ] 0.10.2. Adicionar painel semi-opaco escuro atras de TODO texto persistente.
- [ ] 0.10.3. Usar outline em texto sempre que sobreposto ao jogo.

---

## FASE X: CLAREZA DE UX (NOVO - PRIORIDADE MAXIMA)

> "O jogo continua bem confuso" - o jogador nao sabe o que fazer mesmo com
> tutorial passo-a-passo ativo. Esse e o principal bloqueio percebido para AAA.

### X.1 Diagnostico de confusao
- [ ] X.1.1. Conduzir 3 playtesting sessions com pessoas que nunca jogaram (silenciosas).
- [ ] X.1.2. Anotar cada momento em que o jogador para, hesita, ou pergunta "o que faco".
- [ ] X.1.3. Identificar gaps entre o tutorial e o gameplay real.

### X.2 Affordances visuais
- [ ] X.2.1. Highlight ANIMADO no proximo objetivo (asteroide a minerar pulsa em amarelo).
- [ ] X.2.2. Seta no chao apontando para alvo do tutorial.
- [ ] X.2.3. Tela inicial com cinematica curta mostrando o gameplay loop.
- [ ] X.2.4. Cursor que muda de forma em zonas interaveis (mineravel, construivel, atacavel).

### X.3 Mensagens de tutorial mais explicitas
- [ ] X.3.1. Em vez de "Pressione E para minerar (alcance amarelo)", explicar passo:
      "1. Aproxime sua nave do asteroide. 2. Quando ele estiver dentro do circulo
      amarelo, segure E. 3. Quebra em alguns segundos."
- [ ] X.3.2. Cada etapa tem um GIF/animacao demonstrando (mesmo procedural).
- [ ] X.3.3. Mostrar exemplo de sucesso ("Voce ganhou 5 IRON!") com destaque visual maximo.

### X.4 Objetivos imediatos sempre visiveis
- [ ] X.4.1. Painel "Proximo Passo" no topo da tela, com 1 frase.
- [ ] X.4.2. Recompensa visivel: "Minere 5 IRON para criar Tanque de Oxigenio".
- [ ] X.4.3. Progresso da tarefa atual em barra (3/5 IRON coletado).

### X.5 Eliminar fricoes
- [ ] X.5.1. Tutorial nao deve avancar enquanto jogador nao executar a acao corretamente.
- [ ] X.5.2. Em primeira sessao, desabilitar inimigos por 3 min (FEITO em v1.2; reconfirmar).
- [ ] X.5.3. Spawn perto de asteroides minerables - ja parece funcionar mas verificar densidade.
- [ ] X.5.4. Auto-aim leve durante tutorial.

### X.6 Feedback imediato
- [ ] X.6.1. Cada acao do jogador deve produzir um "ding" visual + sonoro distinto.
- [ ] X.6.2. Erro de acao (energia baixa, fora de alcance) explicado em texto temporario.
- [ ] X.6.3. Cooldowns visualizados (icone de mineracao com timer).

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

### Y.1 Polish visual procedural avancado
- [ ] Y.1.1. Iluminacao com gradiente real por light (radial falloff suave).
- [ ] Y.1.2. Shimmer especular em metais (IRON, GOLD reflective spots).
- [ ] Y.1.3. Distort/heat wave em motores via deslocamento de pixels.
- [ ] Y.1.4. Particulas seguindo curva (nao apenas linha reta).
- [ ] Y.1.5. Estelas (motion trails) longas e suaves em projeteis.

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

### Y.6 Acessibilidade extra
- [ ] Y.6.1. Modo daltonico aplicado a TODO render (atualmente so na nave).
- [ ] Y.6.2. UI scale dinamica em runtime (sem restart).
- [ ] Y.6.3. Captions on-screen para audio cues importantes (atualmente OFF default).
- [ ] Y.6.4. Auto-pause em perda de foco da janela.

### Y.7 Conteudo gerado proceduralmente
- [ ] Y.7.1. Quest generator com templates (escolta+sabotagem+caca).
- [ ] Y.7.2. Nomes procedurais para inimigos boss-tier (memoraveis).
- [ ] Y.7.3. Variantes visuais de inimigos por bioma.

### Y.8 Sistema social offline
- [ ] Y.8.1. Ranking local persistente (top 10).
- [ ] Y.8.2. Replay export/import via JSON.
- [ ] Y.8.3. Photo mode com filtros pos-processamento.

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

## METRICAS DE ESTADO (v1.3 - mantidas de v1.2)

- 148 testes automatizados
- Cobertura: 61% baseline
- 55 entradas de lore PT/EN/ES
- 3 merchants com pricing dinamico
- CI em 9 matrix cells (3 OS x 3 Python) + coverage job
- **+5 novos bugs visuais documentados** (Fase 0.6-0.10) aguardando fix
- **+1 fase nova** (Fase X) capturando clareza de UX

**REVISADO EM:** 2026-05-12 (apos observacao em runtime pos-v1.2)
**FILOSOFIA:** Honesto sobre o que funciona, o que esta quebrado, o que esta
fora do escopo de codigo - e o que e parametro vs arquitetura.
**METRICA DE AAA:** Pessoa random abre, joga 30 min, tem prazer, sem manual.
