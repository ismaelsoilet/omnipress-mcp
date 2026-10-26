# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.8.1] — 2026-10-26

### Added
- **Resolução Universal de Credenciais por Canal (Regras 01 e 04)**:
  - Adicionado `ChannelManager.get_credential(key, channel_slug, default="")` com cascata estrita em 3 níveis:
    1. `channels/<slug>/.env` (credenciais privadas e isoladas do canal).
    2. `<SLUG>_<KEY>` no ambiente global / `.env`.
    3. `<KEY>` no ambiente global padrão.
  - Integração nativa em todos os adaptadores de publicação: `BufferAdapter`, `InstagramAdapter`, `DevtoAdapter`, `GhostAdapter` e `RedditAdapter`.
- **Cache em Memória de Assinatura de Arquivo (`mtime_ns`, `size`) no `ChannelManager`**:
  - `get_channel()` e `get_channel_env()` agora utilizam cache em memória validado pela assinatura em nanossegundos `(st_mtime_ns, st_size)`, eliminando I/O redundante de disco em loops de publicação com invalidação automática imediata se o arquivo for modificado externamente.
  - Adicionado método `clear_cache()` para limpeza determinística de cache em testes e reloads.

### Fixed
- **Isolamento de Alvos e Correção de Contaminação de Threads no `BufferAdapter` (Regras 06 e 09)**:
  - Corrigido defeito crítico em que postagens multi-rede contendo `linkedin` e `x` (`platforms=["linkedin", "x"]`) contaminavam o payload do LinkedIn com metadados de thread do Twitter e substituíam o texto do artigo/post pelo tweet 1 devido a uma heurística booleana gulosa.
  - Implementado `BufferAdapter._resolve_targets(platforms, channel_slug) -> List[Dict[str, str]]`, que resolve cada destino individualmente com seu respectivo serviço canônico e elimina dicionários mutáveis de estado (`self._channel_services`).
  - Preservado `_resolve_channel_ids` como wrapper para compatibilidade retroativa estrita.

### Changed
- **Modernização de User-Agents nos Adaptadores**:
  - Substituídos User-Agents legados e hardcoded (`0.2.0`) em `DevtoAdapter`, `GhostAdapter` e `RedditAdapter` por `OmniPress-MCP/{__version__}` dinâmico.
- **Limpeza de Docstrings no `CarouselBuilder`**:
  - Purgadas menções a criadores específicos em comentários internos, padronizando a documentação técnica dos componentes de mockup.

## [0.8.0] — 2026-10-25

### Added
- **Desacoplamento Paramétrico Total do `CarouselBuilder` (Regras 04, 08 e 12)**:
  - Adicionado resolvedor hierárquico de parâmetros `_resolve_param`:
    - Resolução em cascata: `slide_data` (recipe) > `channel.visual_identity.presets[preset]` > `channel.visual_identity.layout_parameters` > `channel.branding` (legado) > fallbacks universais da engine.
  - Parâmetros declarativos suportados por canal em `visual_identity.layout_parameters`:
    - Margens e geometria: `margin_ratio`, `border_radius`, `split_ratio`, `start_y_ratio`.
    - Escalas tipográficas: `headline_scale`, `body_scale`, `step_scale`, `badge_scale`, `footer_scale`.
    - Entrelinhas e espaçamento: `line_height_head`, `line_height_body`.
    - Contraste e segurança: `card_alpha`, `card_pad_x_ratio`, `card_pad_y_ratio`, `stroke_width`.
    - Elementos e avatares: `avatar_size_ratio`, `show_verified_badge`.
  - **Vocabulário Semântico Desacoplado**:
    - `_parse_semantic_line` agora suporta dicionários de categorias customizados (`semantic_categories`: `danger`, `success`, `warning`, `accent`) e tags explícitas (`semantic_tags`), permitindo que canais de tecnologia, direito ou história definam suas próprias palavras-chave de destaque sem tocar no código Python do motor.
  - Atualização dos canais de referência (`channels/_template/channel.json`, `channels/ismael-soilet/channel.json`, `channels/dossie-historico/channel.json`) demonstrando parametrização customizada e vocabulário semântico próprio.
  - Novos testes unitários dedicados em `tests/test_carousel_builder.py` cobrindo a hierarquia de parâmetros, categorias semânticas e renderização orientada a dados.

### Changed
- Removidas referências a criadores ou canais específicos nos docstrings e comentários do `carousel_builder.py`, universalizando os presets como `classic_card` (Archival Contrast), `tweet_card` (Social Proof & Post Mockup), `minimal_dark` (Dark Editorial) e `split_editorial` (Corporate & Editorial Authority).
- `_render_classic_card` agora aceita `channel_data` e `slide_data` e extrai parâmetros dinâmicos de layout e contraste de forma idêntica aos demais presets.

## [0.7.0] — 2026-10-25

### Added
- **Desacoplamento e Universalização Arquitetural de `src/` (Regra 04)**:
  - `src/engine/carousel_builder.py`: método estático agnóstico `_parse_semantic_line` com suporte a qualquer tag semântica em maiúsculas (`TAG:`), listas numeradas (`1.`) e marcadores (`•`), mapeando cores dinamicamente da paleta do canal (`danger`, `success`, `warning`, `accent`) ou de dicionários customizados (`prefixes`, `tag_colors`).
  - Suporte a marcas d'água (`watermark_text`) e badges editoriais (`badge_text`) dinâmicos, extraídos diretamente do `channel.json` ou do slide, sem fallbacks hardcoded.
  - Dimensionamento responsivo ampliado de tipografia no carrossel (`headline` a 5.0% e `body` a 3.5% da largura da imagem) garantindo legibilidade perfeita no feed do Instagram e LinkedIn.
- **Suporte Nativo a Threads Encadeadas no X (Twitter)**:
  - Adicionado suporte a `metadata.twitter.thread` no `BufferAdapter` (`src/adapters/buffer_adapter.py`) e `UniversalPublisher` (`src/engine/universal_publisher.py`), permitindo a publicação automática de threads completas com validação estrita de 280 caracteres por tweet.
- **Universal 3D Waving Flag Template (`src/engine/blender_templates/waving_flag.py`)**:
  - Template 3D agnóstico no Blender para simulação fotorrealista de bandeiras e estandartes ondulantes em tecido de seda/cetim com mastro dourado polido, canal alfa transparente e textura dinâmica configurável via `--texture`.
  - Mapeado no `Universal3DEngine` (`src/engine/universal_3d.py`) e CLI `omnipress render-3d --template waving_flag`. O antigo `brazil_flag.py` atua como forwarder retrocompatível.
- **Camada Universal de Impacto Psicológico & Metamorfose (`src/video/components/`)**:
  - `MitoRealidadeOverlays.tsx`: suporte a carimbos táteis universais (`stamp-alert`, `stamp-negative`, `stamp-success`, `stamp-positive`) com cores customizáveis (`color`, `borderColor`, `subtextColor`) aplicáveis a qualquer nicho de canal (tributário, tecnologia, história, saúde).
  - `HeraldicSurgery.tsx`: universalizado com props `beforeSrc`, `afterSrc`, `beforeBadge` e `afterBadge` para metamorfose visual e transição de documentos entre dois estados visuais (Antes e Depois).
  - `WordByWordCaptions.tsx`: adicionada propriedade `customHighlightWords` (`red`, `green`, `gold`) permitindo aos canais injetar suas próprias palavras-chave emocionais mantendo vocabulário padrão universal.

### Changed
- **Purga de Acoplamentos e Hardcodings em Componentes de Vídeo**:
  - `DocumentaryEpisode.tsx`: removido áudio fixo (`sb_signaltonoise.mp3`), frame counts hardcoded (`27890`) e IDs de cena vinculados a episódios específicos (`scene_57`, `scene_71`). Áudios secundários agora são configurados opcionalmente via `EpisodeConfig.outroMusicSrc` e sincronizados via `useVideoConfig().durationInFrames`.
  - `ChannelOutro.tsx`: totalmente parametrizado (`title`, `subtitle`, `stampText`, `playlistTitle`, `debateQuestion`), removendo títulos de episódios históricos e caminhos de avatares fixos em favor de padrões genéricos universais.
  - `ThumbnailEpisode.tsx`: tratamento seguro para URLs remotas e caminhos vazios de imagem.

### Fixed
- Correção de conflito de argumentos em `universal_publisher.py` ao repassar `thread` para adaptadores sociais.
- Correção de parênteses excedentes na resolução de cores de perigo/alerta no `carousel_builder.py`.

## [0.6.0] — 2026-10-24

### Added
- **Isolamento de Credenciais Multi-Canal (`channels/<slug>/.env`)**:
  - Suporte a arquivos `.env` dedicados e isolados dentro de cada workspace de canal (`channels/<slug>/.env`), garantindo isolamento total de chaves de API, contas Buffer e perfis sociais entre marcas e canais diferentes (Regra 04).
  - O arquivo `.env` na raiz do repositório foi formalmente dedicado ao canal flagship **Dossiê Histórico** (`OMNIPRESS_ACTIVE_CHANNEL=dossie-historico`).
  - Ordem de precedência estrita: `channels/<slug>/.env` → variáveis com prefixo do canal (`<SLUG>_BUFFER_API_KEY`) → `.env` da raiz do projeto.
- **CLI Subcommand `omnipress sync-buffer` (`src/cli.py`)**:
  - Descoberta automática de canais conectados no Buffer usando a API Key isolada do canal, sincronizando instantaneamente os IDs de Instagram, LinkedIn, X (Twitter), Threads e YouTube diretamente no `channel.json`.
- **Criação do Canal Pessoal `channels/ismael-soilet/`**:
  - Workspace canônico com arquétipo `personal_brand` (LinkedIn, X, Instagram) pré-configurado com presets `tweet_card`, templates de campanha e `.env` isolado.
- **Universal 3D Engine & Blender Headless Integration (`src/engine/universal_3d.py`)**:
  - Motor central declarativo para renderização 3D fotorrealista isolada com canal alfa transparente (PNG/WebM) via Blender 4.2+ LTS headless.
  - Suporte completo a render engines `BLENDER_EEVEE_NEXT` e `CYCLES`.
  - Descoberta automática do binário do Blender em PATH e diretórios de usuário (`~/.local/bin/blender`).
- **Templates Procedurais 3D em Python (`src/engine/blender_templates/`)**:
  - `device_mockup.py`: Smartphone moderno em perspectiva com chassi chanfrado em titânio escuro, mapeamento de textura dinâmica UV para captura de tela do artigo/carrossel, iluminação de estúdio 3 pontos e fundo transparente.
  - `rotating_badge.py`: Moeda/medalhão 3D chanfrado com acabamentos metálicos (`gold`, `silver`, `bronze`, `obsidian`), rotação configurável e emblema frontal opcional.
  - `kinetic_title.py`: Tipografia 3D extrudada e chanfrada com reflexos especulares e iluminação volumétrica.
  - `brazil_flag.py`: Bandeira do Brasil 3D ondulante em tecido de seda/cetim com deslocamento harmônico de ondas, mastro dourado polido e fundo transparente com canal alfa.
- **Componentes Avançados e Dinâmica no Motor Remotion (`src/video/components/`)**:
  - `ChannelOutro.tsx`: Vinheta oficial de encerramento agnóstica de canal estruturada em 2 fases (Fase 1: chamada nobre para compartilhamento de verdade histórica; Fase 2: inscrição no canal com branding oficial e zonas de YouTube End Screen).
  - `HeraldicSurgery.tsx`: Animação dinâmica da "Cirurgia Heráldica de 1889", com substituição cirúrgica em tempo real do Brasão Imperial de 1822 pela Esfera Celeste Republicana com flash óptico e badge evolutivo.
  - `DocumentaryEpisode.tsx` & `types.ts`: Suporte nativo a cenas do tipo `channel-outro` e `heraldic-surgery`, integração de efeitos sonoros táteis por cena (`sfxSrc`, `sfxVolume`), novas direções dinâmicas de câmera (`subtle-zoom`), e crossfade com fade-in/fade-out de trilha sonora de encerramento (`Signal to Noise`).
  - `DustParticles.tsx`: Refatoração para alta performance substituindo filtros caros de `blur` e `boxShadow` por gradiente radial nativo.
  - `KenBurnsImage.tsx`: Presets refinados de movimento de câmera e tratamento visual aprimorado.
- **Aprimoramentos no Motor Universal de Carrosséis (`src/engine/carousel_builder.py`)**:
  - Sanitização de emojis em headlines e corpos de texto para evitar caracteres ausentes (tofu boxes) em fontes do Pillow.
  - Suporte inteligente a quebras de parágrafo preservadas e blocos temáticos com marcadores coloridos `MITO:` e `VERDADE:` e numeração com destaque na cor accent da marca.
  - Resolução robusta de caminhos relativos para avatares e imagens incorporadas dentro do workspace do canal ativo (`channels/<slug>/...`).
- **Padrões de Governança Editorial e Qualidade nos Agentes (AG02, AG04, AG06 e Regra 10)**:
  - **Regra de Ouro das Legendas**: Texto exibido estritamente do roteiro oficial aprovado (`roteiro.json`), Whisper utilizado exclusivamente para extração dos timestamps de timing da fala real, chunks de 2 a 4 palavras, e destaque dinâmico da palavra ativa em karaoke (`#FFD700`, escala `1.06x` e sublinhado dourado) via objetos `WordTiming` no componente `SynchronizedCaptions`.
  - **Portão de Luminância & Anti-Vazio Negro (Anti-Dark Void Gate)**: Luminância média mínima obrigatória de 45.0 (escala 0-255) em imagens e cenas; fundos em ardósia escura (`#12161F` / `#161B22`) em vez de preto puro opaco (`#000000`).
  - **Portão Anti-Anacronismo e Fidelidade Histórica**: Banimento estrito de armas ou bandeiras anacrônicas e validação de correspondência documental autêntica de personalidades históricas.
  - **Padrão Broadcast para Telas Finais e Mosaicos**: Proibição de caixas cinzas rudimentares ou menus retrô; uso obrigatório de artes de alta definição e tipografia oficial do canal.
- **Estrutura Canônica de Recursos Globais e SFX (`channels/_template/`)**:
  - Inclusão da taxonomia profissional de diretórios com `.gitkeep` em `channels/_template/recursos_globais/` (`branding`, `fontes`, `sfx`, `trilhas_sonoras`, `utilitarios`, `vinhetas`) e `channels/_template/media/sfx/` (`01_transicoes`, `02_impactos`, `03_documentos_foley`, `04_epoca_tecnologia`, `05_tensao_risers`, `README.md`).
- **CLI Subcommand `omnipress render-3d` (`src/cli.py`)**:
  - Execução declarativa por arquivo de receita (`omnipress render-3d --recipe recipe_3d.json`) ou parâmetros diretos (`--template`, `--texture`, `--text`, `--material`, `--output`, `--engine`, `--resolution`, `--samples`).
- **Ferramenta MCP Canônica `omnipress_render_3d` (`src/server.py`)**:
  - Registrada com anotações de protocolo MCP 2026 e conformidade Glama TDQS A+ (5.0): `readOnlyHint=False`, `destructiveHint=False`, `idempotentHint=True`, `openWorldHint=False`.
- **Diagnóstico no `omnipress doctor` (`src/utils/runtime_checker.py`)**:
  - Detecção ativa e verificação de prontidão para Blender 3D.
- **Otimização de Performance da Engine Remotion (`remotion.config.ts` & `FilmGrain.tsx`)**:
  - Ativação de cache persistente de compilação Webpack (`Config.setCachingEnabled(true)`), eliminando recompilações redundantes de 7 a 9s.
  - Otimização do pipeline de frames intermediários com `Config.setJpegQuality(80)` e codificação H.264 acelerada com `Config.setX264Preset("fast")`.
  - Multi-processamento ativo no Linux (`Config.setChromiumMultiProcessOnLinux(true)`) e concorrência calibrada em 4 instâncias para evitar swap de disco no WSL2.
  - Refatoração do componente [`FilmGrain.tsx`](src/video/components/FilmGrain.tsx): substituição do filtro procedural SVG `<feTurbulence>` dinâmico na CPU por textura seamless SVG base64 (200x200) cacheada em bitmap com deslocamento analógico leve, reduzindo o tempo de renderização de frames em ~31.2% e o tempo de codificação em ~62.7%.
- **Suíte de Testes Automatizados (`tests/test_universal_3d.py` e `tests/test_channels.py`)**:
  - Testes cobrindo isolamento de `.env` por canal, precedência de chave de API no `BufferPublisherAdapter`, renderização 3D e anotações MCP.

### Changed
- Versão MINOR bump: `0.5.0` → `0.6.0` (novo motor declarativo 3D, isolamento de credenciais por canal e ferramenta MCP sem quebra retroativa).

---

## [0.5.0] — 2026-10-24

### Added
- **OmniPress Content Factory — Sistema de 12 Agentes Especializados**:
  - AG01 `01_researcher_scriptwriter.md`: Agente Pesquisador & Roteirista — analisa canal, pesquisa tema, propõe 3 formatos e escreve roteiro completo dois-colunas com `roteiro.json` e `roteiro.md`.
  - AG02 `02_image_curator.md`: Agente Curador de Imagens — busca imagens cena a cena (Wikimedia, Unsplash, Pexels, Internet Archive) com fallback para prompts Midjourney/FLUX e produz `image_manifest.json`.
  - AG03 `03_audio_engineer.md`: Agente Engenheiro de Áudio — executa pipeline broadcast completo (adeclick, highpass 80Hz, afftdn, EQ 4-bandas, compressão 3:1, EBU R128 -14 LUFS) produzindo `audio_report.json`.
  - AG04 `04_language_reviewer.md`: Agente Revisor Linguístico — revisa roteiro, legendas, hashtags e CTAs sem alterar o tom do canal; produz `language_review.json` com score de qualidade.
  - AG05 `05_timing_checker.md`: Agente Checker de Timing — valida sincronização imagem/fala (±0.5s), duração de shorts (62–68s), chunks de legenda (2–4 palavras); produz `timing_report.json`.
  - AG06 `06_visual_verifier.md`: Agente Verificador Visual — audita relevância semântica, resolução mínima (1080p), ausência de watermarks e conformidade com Regra 08; produz `visual_qa_report.json`.
  - AG07 `07_vfx_remotion.md`: Agente de Efeitos Especiais (Remotion) — implementa Ken Burns `spring()`, whip pans, kinetic typography, HUD overlays, PiP e camera shake via `useCurrentFrame()`/`interpolate()`/`spring()`; produz `vfx_map.json`.
  - AG08 `08_sfx_designer.md`: Agente de Efeitos Sonoros — mapeia transições para SFX (whoosh, impact, glitch, ping), busca em Freesound/Pixabay/ZapSplat, normaliza a -12dBFS; produz `sfx_manifest.json`.
  - AG09 `09_soundtrack_director.md`: Agente Diretor de Trilha Sonora — sugere 5 trilhas com mood/licença/risco Content ID, aguarda aprovação explícita do usuário (gate obrigatório), define ducking 0.12–0.18 sob voz; produz `soundtrack_config.json`.
  - AG10 `10_narration_director.md`: Agente Diretor de Narração — analisa ritmo/dicção/ênfases, compara com roteiro, classifica problemas por severidade (CRÍTICO/MODERADO/LEVE); produz `narration_report.json`.
  - AG11 `11_adversarial_auditor.md`: Agente Auditor Adversarial — auditoria cruzada de todos os relatórios, score 0–100, threshold ≥ 80 para aprovação, checklist de conformidade Regras 07–13; produz `audit_report.json`.
  - AG12 `12_director_orchestrator.md`: Agente Diretor Delegador — ponto de entrada único, determina modo (Express/Standard/Full/Remix), orquestra delegação paralela, gerencia gates de aprovação e entrega; mantém `production_log.json`.
- **Schemas de Handoff Universal** em `.agents/schemas/`:
  - `roteiro.schema.json` — Schema JSON Draft-07 para o roteiro dois-colunas (contrato AG01 → AG02/05/06/07/10).
  - `production_log.schema.json` — Schema do log de produção com rastreamento de etapas e artefatos (AG12).
  - `audit_report.schema.json` — Schema do relatório adversarial com score, bloqueadores e advertências (AG11).
- **Skill Mestre** `.agents/skills/content-factory/SKILL.md` — Runbook completo de orquestração com modos, fluxos, gates, critérios de entrega e tabela de handoff de artefatos.
- **Receitas Declarativas** em `.agents/recipes/` — `express.json`, `standard.json`, `full_production.json`, `remix.json` (conforme Regra 12 — anti-script declarativo-first).
- **Índice da Factory** em `.agents/agents/README.md` — Tabela de todos os agentes, modos de ativação e mapa completo de artefatos por episódio.

### Changed
- Versão MINOR bump: `0.4.1` → `0.5.0` (nova feature arquitetural sem breaking changes de MCP).

---

## [0.4.1] — 2026-10-21

### Fixed
- **UniversalCarouselEngine (`build_from_recipe`)**: Added `build_from_recipe(recipe_input)` method to load and compile carousel recipes into slide images directly.
- **Universal Pipeline Test Suite**: Fixed fixture unpacking error in `tests/test_universal_pipeline.py::test_universal_carousel_recipe_with_presets` (`ValueError: too many values to unpack`) by reading channel and manager from dictionary mapping.

## [0.4.0] — 2026-10-20

### Added
- **Multi-Preset Visual Carousel System (4 Presets)**:
  - `tweet_card` (Thiago Ramos style): Social-proof layout with circular author avatar, Twitter blue verified badge, `@handle`, bold statement headline, subtitle, and single/dual comparison photo frames with rounded corners (`radius=18`).
  - `minimal_dark` (Rhaj Teixeira style): Minimalist dark-mode editorial with pure dark background (`#08080A`), elegant serif typography (`DejaVuSerif`), step counter ("Passo 1."), high-contrast text, and vector search bar mockup with magnifying glass and clear icons.
  - `split_editorial` (Portal da Reforma Tributária style): Corporate & GovTech authority layout with top contextual photo (45%), deep navy blue solid block (55%), circular author cutout overlapping the division line, opinion badge, square bullet markers (`■`), and watermark logo.
  - `classic_card` (Rule 08 Dossiê Histórico style): Full-screen archival background photo, top badge pill, protective dark translucent backdrop card (`rgba(8, 10, 14, 215)`), and dark safety stroke on fonts.
  - Multi-family TrueType font loader (`load_font_by_family`) safely supporting `sans`, `serif`, and `mono` font families with cross-platform fallbacks.
  - Vector drawing primitives in `CarouselBuilder`: `_draw_verified_badge`, `_draw_search_bar_mockup`, `_draw_circular_avatar`, `_draw_rounded_image`.
- **Channel Archetypes (`personal_brand` vs. `media_channel`)**:
  - `personal_brand` archetype: Lightweight workspace (`campanhas/`, `articles/`, `media/`) focused on LinkedIn, X, Instagram, and technical articles with zero Remotion/video overhead.
  - `media_channel` archetype: Full documentary workspace (`episodios/`, `documentarios/`, `shorts/`, `media/`) with 16:9 Remotion pipelines and -14 LUFS audio mastering.
- **Canonical Channel Style Guides & Design Tokens**:
  - `channels/_template/style_guide.md`: Complete human- and AI-readable style guide defining visual moodboards, palette tokens, typography rules, and editorial dos/don'ts.
  - `channels/dossie-historico/style_guide.md`: Channel-specific style guide for Dossiê Histórico.
  - `visual_identity` block in `channel.json` with customizable palettes, typography paths, author metadata, and UI elements.
- **Continuous Documentation, SemVer & Release Policy (Rule 13)**:
  - Normative rule in `.agents/rules/13_continuous_documentation_versioning_and_release_policy.md`.
  - Added to `AGENTS.md` (English & Portuguese sections) and `.agents/rules/README.md`.
  - Enforces mandatory synchronized documentation, SemVer version bump, and changelog updates on every change.
- **Example Declarative Recipes**:
  - Added `recipe_tweet_card.json`, `recipe_minimal_dark.json`, and `recipe_split_editorial.json` in `channels/_template/campanhas/_template_campanha/exemplos_presets/`.

### Changed
- **Modular Carousel Engine (`CarouselBuilder` & `UniversalCarouselEngine`)**:
  - `CarouselBuilder.render_slide` dynamically routes to preset renderers based on recipe, slide, or channel defaults.
  - `UniversalCarouselEngine.build_from_recipe` supports solid canvas backgrounds and recipe-level overrides without failing on missing background image files.
  - `ChannelManager.create_channel` automatically generates `visual_identity` and creates `style_guide.md`.
- **Root Directory Decoupling & Sanitization**:
  - Eliminated legacy root `articles/` and `media/assets/` folders.
  - Configured `media/staging/` as volatile runtime cache in `.gitignore`.

---

## [0.3.0] — 2026-10-18

### Added
- **Universal Declarative Execution Engines (Rule 12)**:
  - Universal Carousel Engine (`src/engine/universal_carousel.py`): Aspect ratio bias auto-formatting, dynamic backdrop cards, CDN uploading, and Buffer scheduling.
  - Universal Audio Mastering Engine (`src/engine/universal_audio.py`): EBU R128 (-14.0 LUFS target, <= -1.2 dBTP), 4-band surgical EQ (140Hz warmth, 300Hz de-box, 3kHz presence, 8.5kHz air), dynamic broadcast compression, and speech-aware pause de-breather.
  - Universal Captions Engine (`src/engine/universal_captions.py`): Whisper timestamp parser supporting multi-act structures, 2-4 word kinetic chunking, and Remotion subtitle JSON generation.
  - Universal Multi-Platform Publisher (`src/engine/universal_publisher.py`): Multi-channel publisher with privacy sanitization and PublishingShield anti-duplicate protection.
  - Declarative recipes in `channels/_template/`: `carousel_recipe.json` and `post_recipe.json`.
- **Packaging & Hardening (SureForge Adversarial Round 2)**:
  - Added `.dockerignore` blocking `.env*`, `.git`, `.venv`, `channels/`, `.agents/`, `node_modules/`, `dist/`.
  - Added sdist excludes in `pyproject.toml` preventing internal assets leakage.
  - Integrated `src/engine/dark_media.py` directly into core engine.
  - Expanded `sanitize_text` with modern multi-segment gTLDs (`.technology`, `.solutions`), OpenAI/AWS/GitHub PAT/Ghost token detection.
  - Eliminated 30-word false-positive collisions in `PublishingShield.generate_fingerprint`.
  - Enforced strict Rule 10 ducking ceiling (`0.16`) and fixed Remotion React 19 loose component type compatibility.
  - Fixed multi-channel partial failures and ledger recording in `BufferAdapter`.
  - Implemented `BasePublisherAdapter` on `MarkdownAdapter`.

### Changed
- **Decoupled Channel Assets from Core Engine**:
  - Purged 24,000+ lines of channel-specific Whisper timestamps, configs, and audio assets from git tracking.
  - Refactored `src/video/Root.tsx` into a clean, brand-agnostic video engine template exposing universal compositions.
  - Decoupled `src/cli.py` fallback channels and `src/video/compositions/` default properties from hardcoded channel references.
  - Preserved historical channel assets securely in git-ignored `channels/dossie-historico/` workspace.
- **Canonical Channel Workspace Template (`channels/_template/`)**:
  - Expanded `channels/_template/` with full directory hierarchy for multi-channel scaling.


---

## [0.2.0] — 2026-10-17

### Added
- **Full Video Creation & Motion Graphics Skills Suite**:
  - Integrated 12 official Remotion Agent Skills (`remotion-dev/skills`) into `.agents/skills/`:
    - `remotion-best-practices`: Universal routing and video best practices.
    - `remotion-markup`: Animation with `interpolate()`, `spring()`, `useCurrentFrame()`, and CSS shorthands (`scale`, `translate`, `rotate`).
    - `remotion-captions`: Dynamic subtitle synchronization with Whisper word-level timestamps.
    - `remotion-docs`: Real-time official documentation lookup via Algolia Search API and `.md` retrieval convention.
    - `remotion-studio`: Interactive video preview in browser.
    - `remotion-render`: CLI video and still frame rendering.
    - `remotion-create`: Template and composition scaffolding.
    - `remotion-interactivity`: Making compositions editable directly in Remotion Studio.
    - `remotion-maps`: Animated maps and 3D flyovers (Mapbox, MapLibre, MapTiler, CesiumJS).
    - `remotion-multimedia`: Media inspection with Mediabunny.
    - `remotion-saas`: Architecture for web player and cloud rendering.
    - `remotion-upgrade`: Continuous ecosystem and skill upgrades.
- **Short-Form Vertical Video Skills Suite (TikTok, Reels & Shorts)**:
  - `viral-hooks`: 3-layer opening hook (visual, verbal, on-screen text) and proven creator frameworks.
  - `viral-youtube-shorts`: Shorts Feed optimization, VVSA metric (>70%), and long-form funnel bridging.
  - `viral-instagram-reels`: Instagram signal hierarchy (watch time, sends per reach), Trial Reels, and originality.
  - `viral-tiktok-content`: FYP pacing, completion rate math (>60s Creator Rewards), and trending audio.
  - `viral-captions-and-ctas`: Send/save-driving CTAs and muted watching captions.
  - `viral-short-form`: 4-stage retention architecture (Hook -> Escalation -> Payoff -> CTA).
  - `viral-short-form-ideas`: Volume ideation matrix and multi-angle topic expansion.
  - `reel-export`: 9:16 vertical exports with UI Safe Zones, H.264, yuv420p, bt709, and ffprobe validation.
- **YouTube Long-Form & Documentary Video Skills Suite**:
  - `omnipress-youtube-documentary`: Master runbook for 8–30+ minute documentaries (5-Act narrative arc, 0–30s hook window, pattern interrupts every 45–60s, visual variety every 3–5s, chapter cliffhangers, and Remotion rendering).
  - `technical-video-script`: Two-column beat sheet (visual/SFX vs narration), 30s hook, and YouTube timestamps.
  - `vox-explainer`: Visual journalism style (halftone, torn paper, bold typography, motion on twos).
  - `documentary-montage-production`: Source logging (`claim_id`), fact checking, and ethical archival use.
  - `cinematic-trailer-production`: Tension curves, audio-visual escalation, and teaser structures.
  - `youtube-thumbnail-design`: 120px mobile preview test, 3-element focal rule, and contrast optimization.
- **Documentation**:
  - Created [`docs/REMOTION_SKILLS_AND_DOCS.md`](docs/REMOTION_SKILLS_AND_DOCS.md): Reference guide for Remotion skills and live documentation protocols.
  - Created [`docs/VIDEO_CREATION_AND_PLATFORM_SKILLS.md`](docs/VIDEO_CREATION_AND_PLATFORM_SKILLS.md): Unified video platform guide for YouTube, TikTok, Reels, Shorts, and Documentaries.
  - Documented Image Sourcing & External Generation Protocol in `10_programmatic_video_and_remotion_engine.md` and `AGENTS.md`.
- **Compositions**:
  - Registered `DocumentaryShort-05-Mincemeat-9x16` in `src/video/Root.tsx` with 13 historical scenes, kinetic overlays, and soundscape alignment.
- **Tooling & Scripts**:
  - Added `"remotion:skills:update"` script to `package.json`.
  - Added `scratch/` to `.gitignore`.

### Fixed
- Fixed whitespace collapse in `ScrambledText` component by preserving non-breaking spaces (`\u00A0`) and enforcing `whiteSpace: "pre-wrap"` and `wordBreak: "break-word"`.

### Changed
- Bumped version to `0.2.0` across `pyproject.toml`, `package.json`, `src/__init__.py`, `src/server.py`, `src/cli.py`, and adapter User-Agents.
- Updated `AGENTS.md`, `.agents/rules/10_programmatic_video_and_remotion_engine.md`, and `docs/AGENT_MANUAL.md` with Remotion Agent Skills compliance.

---

## [0.1.0] — 2026-09-23

### Added
- Initial open-source release of OmniPress MCP.
- Universal multi-channel publishing protocol across Dev.to, Ghost CMS, LinkedIn, X, Meta Threads, Instagram, Reddit, and Markdown archives.
- Multi-channel agnostic architecture with channel isolation (`channels/<slug>/`).
- Privacy and judicial secrecy sanitization gate (`sanitize_text`).
- Social Carousel Builder (Pillow 3:4 high-contrast graphics engine).
- Basic Remotion programmatic video pipeline and Edge-TTS voiceover generation.
- CLI suite (`omnipress doctor`, `omnipress status`, `omnipress setup`).
