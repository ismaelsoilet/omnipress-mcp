# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.13.2] — 2026-11-11

### Added
- **Suporte a Ênfase e Negrito Inline Markdown (`**texto**`) no CarouselBuilder**:
  - Implementação de tokenização e quebra de linha de dois estágios (`_tokenize_inline_markdown` e `_wrap_styled_words_two_stage`) no preset `tweet_card`.
  - Termos envolvidos por `**` são renderizados com peso bold e cor de destaque de alto contraste (`bold_color`), com tratamento de pontuações anexas.
  - Suporte a realce seletivo de palavras-chave nos títulos (`headline_highlight_color`) via marcação `**palavra**`.
  - Cobertura de testes unitários em `tests/test_carousel_builder.py` validando negritos inline e realce cromático de títulos.

### Changed
- **Paleta Executiva Sóbria e Alto Contraste**:
  - Ajuste no fallback de realce para utilizar o acento institucional do canal (`#0A66C2` no modo claro e `#38BDF8` no modo escuro), eliminando amarelos de baixo contraste sobre cartões claros.

## [0.13.1] — 2026-11-07

### Added
- **Insígnias e Pílulas de Categoria Semântica no CarouselBuilder**:
  - `badge_text` no preset `tweet_card` renderiza pílula temática com fundo e borda coloridos de acordo com a semântica (`PERIGO/ALERTA`, `NOVO/SOLUÇÃO`, `LEGISLAÇÃO/GUIA` ou cor de destaque).
  - Suporte a `headline_color` explícito por slide ou no canal, permitindo realçar títulos em cores institucionais.
  - Expansão de categorias semânticas automáticas com termos do ecossistema fiscal (`TRAVA`, `BLOQUEIO`, `GLOSA`, `SPLIT PAYMENT`, `PLENO`, `À VISTA`, `CUSTO`, `CHECKLIST`).

### Changed
- **Espaçamento e Posicionamento Dinâmico de Imagens no CarouselBuilder**:
  - Eliminação do vácuo de espaçamento vertical forçado quando o corpo do slide tem poucas linhas (como slides de capa com <= 2 parágrafos).
  - Posicionamento proporcional da imagem interna logo abaixo do texto dinamicamente (`curr_y + gap`) ou via flag `tight_image` / `img_top_ratio`.

### Fixed
- **Diagramação e Vácuo no Slide 1**:
  - Correção de vão em branco de 218px entre o texto e a ilustração 3D em carrosséis executivos.

## [0.13.0] — 2026-11-03

### Added
- **Cenas Interativas Dedicadas**:
  - `SceneTacticalMap` (`src/video/components/scenes/SceneTacticalMap.tsx`): mapa de arquivo com grade tática, coordenadas, headline e card protetor da Regra 08.
  - `SceneStatCounter` (`src/video/components/scenes/SceneStatCounter.tsx`): contador animado com `spring()`/`interpolate()`, prefixo, sufixo, rótulo e fundo opcional.
  - `SceneVideoClip` (`src/video/components/scenes/SceneVideoClip.tsx`): clipe de arquivo via `<OffthreadVideo>` com overlay, badge e controle de mute.
  - Previews conectados `SceneTacticalMap-Preview`, `SceneStatCounter-Preview` e `SceneVideoClip-Preview`.
  - `EditableVideoEngine` e `DocumentaryEpisode` agora emitem esses componentes para `tactical-map`, `stat-counter` e `video-clip`.
- **Prune de Staging**:
  - `MediaStager.prune()` usa o índice `.staging-index.json` e remove somente arquivos gerados em execuções anteriores; arquivos do usuário, `.gitkeep` aninhados e diretórios do usuário são preservados.
  - Symlinks de diretório são ignorados e symlinks de arquivo são removidos sem seguir o alvo, evitando deleção de arquivos compartilhados.
  - `prune_media: true` no recipe; episódios editáveis ativam prune no scaffold e no render.
- **Compatibilidade de Harness**:
  - `opencode.json` para OpenCode (MCP local + descoberta de `.agents/skills/`).
  - `.mcp.json` para Command Code (project scope, stdio).
  - `.agents/mcp_config.json` para Antigravity workspace; `mcp_config.json` da raiz é shim de compatibilidade.
  - `docs/AGENT_COMPATIBILITY.md` com snippets, skills, tool prefixes e troubleshooting para Antigravity, Command Code e OpenCode.
- **CI**:
  - Smoke de `remotion compositions` para o Root core e para o fixture de episódio editável.

### Changed
- `documentary_recipe.schema.json` declara `video_clip`, `coordinates`, `stat_value`, `stat_prefix`, `stat_suffix`, `stat_label` e `video_muted`.
- `video_recipe.schema.json` aceita `prune_media`.
- `README.md`, `README.pt-BR.md`, `docs/SETUP_GUIDE.md`, `docs/SETUP_GUIDE.pt-BR.md`, `docs/AGENT_MANUAL.md`, `docs/wiki/Antigravity-Integration.md` e `channels/_template/video/README.md` documentam o fluxo e os três harnesses.
- Versão sincronizada em **0.13.0** (sem publicação de release).

### Fixed
- Cenas `tactical-map`, `stat-counter` e `video-clip` não caem mais em `SceneKenBurns` silenciosamente.
- `public/` de episódios editáveis não acumula mais mídia antiga após re-scaffold/render.
- `SceneVideoClip` usa variáveis de tema em vez de dourado hardcoded (invariante de arquitetura).
- `omnipress status` agora mostra o canal ativo resolvido (fallback) e o override de ambiente quando `OMNIPRESS_ACTIVE_CHANNEL` aponta para um slug inexistente.
- Documentação de canais privados: `channels/*` ignorado pelo Git, backup separado e configuração explícita de `OMNIPRESS_ACTIVE_CHANNEL`/`channel_slug`.

## [0.12.0] — 2026-11-03

### Added
- **Novo Fluxo de Edição Interativa do Remotion (4.0.540)**:
  - `EditableVideoEngine` (`src/engine/editable_video.py`): gera um episódio Remotion editável por canal em `channels/<slug>/video/episodes/<episode>-<aspect>/`, com `Episode.tsx` contendo **um nó JSX por cena**, `index.ts` com entry point próprio, `meta.json` com hash guard, `media.json`, `data/captions.ts`, `data/theme.ts` e `video_recipe.editable.json`.
  - `MediaStager` (`src/engine/media_stager.py`): staging determinístico de mídia para `public/`, com validação de path safety, manifesto versionado e normalização de caminhos absolutos legados.
  - `createEpisodeRoot()` e `public.ts` em `src/video/`: fábrica genérica de root Remotion e superfície pública estável para código gerado.
  - Componentes de cena interativos com `Interactive.create()`: `SceneKenBurns`, `SceneDocumentReveal`, `SceneHeraldic`, `SceneOutro`, mais previews conectados no Root.
  - `EpisodeShell`: shell universal de tema, trilha, locução, ducking e legendas para episódios editáveis.
  - CLI `omnipress video --scaffold-editable [--force] [--render] [--aspect-ratio]` e `omnipress studio --channel ... --episode ...`.
  - MCP tool `omnipress_prepare_editable_video` com anotações e docstring canônica.
  - Suporte a `entry_point`, `public_dir`, `media_manifest`, `normalize_media` e `stage_legacy_media` no `video_recipe.schema.json` e no `RemotionProvider`.
  - Workspace `channels/_template/video/` com README canônico do fluxo editável.
- **Timeline Estruturada**: `<Track name="...">` e `name` descritivo em cenas, locução, trilha, SFX e vinheta; previews de cena conectados.
- **Testes**: `test_media_stager.py`, `test_editable_video_scaffold.py`, `test_remotion_provider_entrypoint.py`, fixture TypeScript de episódio editável e validação do workspace `video/`.

### Changed
- **Integração com `origin/main` (0.11.0)**: incorpora o Meta Unified Publishing Suite (Instagram Reels, Facebook Pages e Threads), o Active Health Check Gate e os comandos/ferramentas `meta-auth`, sem conflito com o fluxo de vídeo.
- **Remotion 4.0.535 → 4.0.540**: todos os pacotes `remotion`/`@remotion/*` alinhados; skills oficiais atualizadas.
- `DocumentaryEpisode` e `DocumentaryShort` agora usam cenas interativas, tracks nomeadas e `resolveMediaSrc()`.
- `Root.tsx` extraído para `CoreCompositions` + `Root`, com tipagem explícita e `defaultProps` inline.
- `RemotionProvider` corrigido para resolver a raiz do projeto (`parents[3]`), validar entry point/public dir e aplicar staging/normalização de mídia.
- `UniversalDocumentaryEngine` emite `media.json` e normaliza soundtrack, locução e SFX.
- `tsconfig.json` inclui `channels/*/video/**/*` e o fixture de episódio editável.
- Documentação sincronizada em `AGENTS.md`, `README.md`, `docs/AGENT_MANUAL.md`, `docs/REMOTION_SKILLS_AND_DOCS.md` e `channels/_template/README.md`.

### Fixed
- **`staticFile()` com caminhos absolutos**: mídia de canal agora passa por staging e `--public-dir`; caminhos absolutos legados são normalizados automaticamente.
- **TSX gerado com aspas/newlines**: atributos da vinheta agora usam expressões JSX (`prop={"..."}`) e escapam corretamente aspas, barras e quebras de linha.
- **Legendas do `align-captions`**: payloads act-keyed e flat são normalizados; `id`/`duration` são aceitos por `CaptionChunk`; `actTimelines` é derivado automaticamente quando ausente, com inícios cumulativos para múltiplos atos.
- **Precedência de atos**: `SynchronizedCaptions` prefere chaves de ato quando existem, mesmo que o payload também traga `chunks` no topo; o template e o modo editável compartilham a mesma linha do tempo cumulativa.
- **SFX remoto**: URLs `http(s)` de SFX são preservadas no `episode_config` e não tentam staging local; o TSX editável usa `resolveMediaSrc()` para áudio/SFX remoto.
- **Mídia fora da raiz**: no modo manifesto, fontes fora do projeto/canal são rejeitadas com erro claro; no modo render, a imagem externa é incorporada ao card interno e o manifesto permanece portátil.
- **Payload flat de legendas**: `SynchronizedCaptions` agora lê `{metadata, words, chunks}` no template sem exigir chave de ato.
- **`episode_config.json` portátil**: `mediaSrc`, trilha, locução e SFX são gravados relativos à raiz do projeto; o provider normaliza via manifesto.
- **Áudio/SFX de cenas sobrepostas**: lane packing também se aplica às tracks `Áudio de Cena` e `SFX de Cena`.
- **Atributos de música**: `backgroundMusicSrc` e `outroMusicSrc` usam expressão JSX segura para nomes com aspas/barras.
- **Re-render após edição de duração**: recipes editáveis não fixam mais `duration_frames`; o provider ignora `--frames` quando `editable=true`.
- **`media.json` portátil**: fontes são gravadas relativas à raiz do projeto, permitindo reconstruir o staging em outro clone/máquina.
- **SFX documental**: `sfx` relativo agora é resolvido para caminho absoluto no `episode_config`, evitando 404 no render template.
- **Overlap de cenas**: cenas sobrepostas são distribuídas em múltiplas tracks (`Cenas`, `Cenas 2`, ...) no TSX gerado.
- **Staging antes da escrita**: falha de staging não deixa mais um episódio parcial sem `meta.json`.
- **Volume da trilha**: `EpisodeShell` respeita `backgroundMusicVolume` também no intro e nas pausas; volume 0 permanece silencioso.
- **Studio provider**: `remotion studio` passa pelo `RemotionProvider`, mantendo o subprocesso na camada de provider.
- **`RemotionProvider` PROJECT_ROOT**: corrigido de `src/` para a raiz do repositório.
- **Overlap de tracks**: locução, SFX, trilha e música de encerramento foram separados em tracks próprias.
- **Guard de edição manual**: scaffold recusa sobrescrever TSX editado sem `--force` e cria backup no overwrite forçado.
## [0.11.0] — 2026-10-30

### Added
- **Meta Unified Publishing Suite (Instagram Reels, Facebook Pages & Threads API)**:
  - `src/adapters/meta_adapter.py`: novo adaptador direto `MetaPublisherAdapter` (com aliases `MetaGraphAdapter` e `InstagramGraphAdapter`) integrado à Meta Graph API v19.0+ e Threads API oficial (`graph.threads.net`).
  - **Suporte a Vídeos e Reels no Instagram**: contêiner `media_type: "REELS"`, `video_url` e polling assíncrono do status do contêiner (`GET /{container_id}?fields=status_code`) até `FINISHED` antes da publicação.
  - **Automação de Primeiro Comentário (*First Comment*)**: disparo opcional de `POST /{post_id}/comments` para inserção automática de hashtags sem poluir a legenda principal.
  - **Publicação Direta em Páginas do Facebook**: suporte a posts de texto/link (`POST /{page_id}/feed`), fotos (`POST /{page_id}/photos`) e vídeos (`POST /{page_id}/videos`) sem intermediários.
  - **Publicação Oficial no Threads**: suporte a posts de texto, imagens e vídeos direto no Threads via `graph.threads.net/v1.0/{threads_user_id}`.
  - `src/adapters/instagram_adapter.py`: reexportação retrocompatível para garantir continuidade e interoperabilidade com todos os fluxos legados.
  - `src/server.py`: ferramentas MCP `omnipress_queue_media_post` e `omnipress_queue_post` atualizadas para despachar diretamente para Facebook Pages e Threads via Meta Suite quando configurados.
  - `src/core/capabilities.py`: busca de binário `ffmpeg` expandida para incluir `~/.local/bin/ffmpeg`.
  - `src/core/publishing_shield.py`: inclusão de limites oficiais de caracteres (`63206`) e mídias (`10`) para `facebook` e `fb`.
- **Meta Sign-In & Asset Discovery Manager (Contas com Centenas/Milhares de Ativos)**:
  - `src/core/meta_asset_manager.py`: motor de inspeção de tokens Meta, paginação por cursor (`/me/accounts`), busca textual/filtragem em tempo real e vinculação atômica em `channels/<slug>/.env`.
  - `src/cli.py`: comando interativo `omnipress meta-auth` com seleção de canais existentes, criação dinâmica de novos canais, busca e paginação de ativos e verificação de saúde ao vivo.
  - `src/server.py`: ferramentas MCP `omnipress_meta_auth_inspect` e `omnipress_meta_auth_bind` para permitir que agentes de IA e clientes MCP descubram ativos da Meta e configurem canais programaticamente.

## [0.10.2] — 2026-10-30

### Added
- **Portão Mandatório de Verificação Ativa Pós-Publicação (Regra 09 Gate 6 - Health Check)**:
  - `src/adapters/buffer_adapter.py`: adicionado método `get_post_status(post_id, channel_slug)` via consulta GraphQL `GetPost($input: PostInput!)` para checagem ao vivo de status (`scheduled`, `sent`, `error`) e confirmação do timestamp `dueAt`.
  - `src/engine/universal_publisher.py`: validação pós-disparo obrigatória integrada ao `publish_social_post()` e `execute_recipe()`. Interroga ativamente cada post ID gerado e registra `health_check.verified` e `health_check.results`.
  - `src/cli.py`: comando `omnipress verify-posts --post <slug> --channel <channel>` para auditar o status pós-disparo e checagem de integridade contra suposições silenciosas de envio.
  - `src/engine/universal_publisher.py`: adicionado método `verify_post_execution(post_slug, channel_slug)` que lê o `scheduling_log.json`, cruza os timestamps com o horário atual UTC e atualiza o estado de execução (`SUCCESS_SENT`, `PENDING_SCHEDULED`, `IN_TRANSIT`, `FAILED_ERROR`).
  - `.agents/rules/09_single_publication_and_anti_duplicate_policy.md` e `AGENTS.md`: formalização normativa do Portão 6 (Health Check Gate) em inglês e português, proibindo suposição silenciosa de sucesso e exigindo persistência auditável em `scheduling_log.json`.

## [0.10.1] — 2026-10-29

### Added
- **Suporte Nativo a Documentos no Buffer (LinkedIn PDF Carousels)**:
  - `src/adapters/buffer_adapter.py`: adicionado suporte a `DocumentAssetInput` (`document_url`, `document_title`, `document_thumbnail_url`) na mutação GraphQL do Buffer para publicação nativa de documentos no LinkedIn.
  - `src/engine/universal_publisher.py`: extração e encaminhamento automático de `document_path`, `document_url`, `document_title` e `document_thumbnail_url` no `execute_recipe()`.
  - Suporte a hosting com headers HTTP completos e Content-Length via GitHub CDN / CDN pública para evitar rejeição do scraper do Buffer.

### Fixed
- **Publicação de Carrossel PDF Ignorado no LinkedIn**:
  - Corrigido gap no `execute_recipe()` onde arquivos PDF especificados em `document_path` não eram repassados para `publish_social_post()`.
  - Corrigido bypass de anti-duplicação e compatibilidade com o validador de similaridade do Buffer.

## [0.10.0] — 2026-10-29

### Added
- **Camada de Providers e Capability Registry (Regra 14)**:
  - `src/core/capabilities.py`: fonte única de sondagem de runtimes (Python, FFmpeg, Node/npm, Remotion, Blender, Edge-TTS, Whisper, IA de imagem/música, rede), com versão, binário resolvido, env var, consumidores e hint de instalação.
  - `src/engine/providers/`: contrato `RenderProvider` stateless, capability-gated e path-safe, com implementações `blender`, `remotion`, `ffmpeg`, `edge_tts`, `whisper`, `ai_image`, `prompt_export` e `stock_asset`.
  - `omnipress doctor --json` expõe o registry para CI e agentes.
- **Engines Universais Faltantes (Regra 12)**:
  - `universal_thumbnail` + `rule15_validator`: thumbnails 16:9/9:16 com limite de 3–4 palavras, tipografia 160–220px, stroke ≥ 11px, chiaroscuro e death zone do YouTube livre, além de previews mobile de 120px/320px.
  - `universal_documentary`: cenas documentais com mídia autêntica obrigatória, card protetor da Regra 08, modos `render` e `manifest`, e geração de `episode_config.json` compatível com Remotion.
  - `universal_video`: render Remotion via recipe (`video_recipe.json` e `intro_recipe.json` legado).
  - `universal_assets`: aquisição de acervos públicos com allowlist de domínios, licença e atribuição.
  - `universal_deploy`: entrega de arquivos em `public/` com manifesto de hashes.
  - `universal_audio.mix_soundtrack`: mixagem de trilha com ducking e teto de volume `0.20` (Regra 10).
  - `universal_captions.verify_timeline`: linter de gaps/duração/sobreposição de chunks (`align-captions --verify`).
- **Schemas Declarativos (Draft-07)**: `channel`, `carousel_recipe`, `post_recipe`, `thumbnail_recipe`, `documentary_recipe`, `caption_recipe`, `3d_recipe`, `template_manifest`, `video_recipe`, `audio_recipe`, `voice_recipe`, `image_recipe`, `asset_recipe`, com validação em runtime (`OMNIPRESS_SCHEMA_STRICT`).
- **Registry Declarativo de Templates 3D**: `src/engine/templates_3d/<name>/{template.py, manifest.json}` + `channels/<slug>/blender_templates/`, com allowlist por canal e `--validate-only`/`--list-templates`.
- **CLI/MCP**: comandos `thumbnail`, `documentary`, `video`, `assets`, `deploy`; `render-3d` com `--validate-only`, `--dry-run` e `--list-templates`; ferramentas MCP `omnipress_render_thumbnail`, `omnipress_render_documentary`, `omnipress_render_video` e `omnipress_fetch_assets`.
- **Migração do dossiê**: 27 `carousel_recipe.json` (210 slides) e 3 `documentary_recipe.json` (246 cenas) gerados por ferramentas AST idempotentes em `scripts/migrations/`.
- **Travas de CI**: `test_architecture_invariants`, `test_recipe_schemas`, `test_release_invariants`, `test_channel_layout_contract`, `test_providers` e `test_rule15_thumbnails` reescrito para o validador de produção.

### Changed
- **Cascade Top-Down (Regra 14)**: `card_bg_alpha` canônico com alias `card_alpha`; `gradient_start_ratio`, `enable_text_card`, `top_bias`, `contrast_boost` e `color_boost` agora percorrem slide → recipe → preset → canal → branding; `settings.default_aspect_ratio` é respeitado.
- **Paleta e tipografia no cascade**: novo `_resolve_palette`/`_resolve_fonts`; `tweet_card` e `split_editorial` passaram a usar fontes do canal; `classic_card` usa `visual_identity.palette` e `presets`.
- **Defaults neutros**: accent padrão `#3B82F6`, background `#0B1220`; removidos dourado, voz `pt-BR-AntonioNeural`, nomes/handles e prompts editoriais do `src/`.
- **Remotion agnóstico**: novo `src/video/theme.ts` com CSS custom properties; 40 ocorrências de dourado substituídas; defaults textuais de câmera/carimbo/tagline neutralizados; `WordByWordCaptions` sem vocabulário embutido.
- **Adaptadores stateless (Regra 14)**: removidos snapshots de `os.getenv` dos construtores de Buffer, Dev.to, Ghost, Instagram, Reddit, Webhook, YouTube e Markdown; credenciais somente via `ChannelManager.get_credential`.
- **Sanitização por perfil**: `sanitize_text(text, profiles)` com perfis `br`, `generic_pii`, `intl` e `none`; canal define via `settings.sanitize_profiles`.

### Removed
- 67 scripts de carrossel (`render_carousel_*`, `upload_carousel_*`, `schedule_carousel_*`, `publish_carousel_*`) e `auto_queue_runner.py`.
- Scripts de geração de cenas documentais de `ep03`/`ep04` substituídos pelos manifests.
- `src/engine/blender_templates/brazil_flag.py` e o registry hardcoded de templates.
- `channels/default/` e `channels/test-channel/` (diretórios scratch).

### Deprecated
- Aliases legados preservados: `omnipress_list_recent`, `slides_json` em `omnipress_build_carousel`, `brazil_flag` retorna erro direcionado a template de canal, e `intro_recipe.json` é normalizado para `video_recipe`.

## [0.9.1] — 2026-10-29

### Added
- **Desacoplamento Universal de Adaptadores e Isolamento de Canal (Regra 04 & Regra 14)**:
  - `WebhookPublisherAdapter`: adicionado `get_credentials(channel_slug)` e suporte a `channel_slug` em `is_configured`, `queue_social_post` e `dispatch_event`, lendo `OMNIPRESS_WEBHOOK_URL` e `OMNIPRESS_WEBHOOK_SECRET` isolados em `channels/<slug>/.env`.
  - `YouTubeStagingAdapter`: implementada resolução de pasta de staging isolada via `_resolve_staging_dir(channel_slug)` direcionando metadados e mídias para `channels/<slug>/media/staging`, e webhook com precedência por canal.
  - `RedditPublisherAdapter`: adicionada resolução de `REDDIT_DEFAULT_SUBREDDIT` via `ChannelManager.get_credential("REDDIT_DEFAULT_SUBREDDIT", channel_slug)`.
  - `get_default_storage_provider`: suporte a `channel_slug`, permitindo buckets S3/R2 ou endpoints locais isolados por marca/canal.
  - `UniversalPublisherEngine`: suporte a despacho modular para múltiplos provedores (`buffer`, `instagram`, `reddit`, `webhook`, `markdown`) via parâmetro `provider` ou campo declarativo no recipe JSON.
  - `omnipress_generate_speech` e `omnipress_render_dark_video`: adicionado parâmetro `channel_slug` para salvar arquivos diretamente no workspace do canal (`channels/<slug>/media/voiceover` e `channels/<slug>/media/output`).
  - `tests/test_decoupling_rule14.py`: 6 novos testes unitários cobrindo isolamento de credenciais, staging por canal e roteamento modular de adaptadores.

### Changed
- **Imutabilidade e Execução Sem Estado (Statelessness)**:
  - `BufferPublisherAdapter`: removido atributo mutável de instância `self._channel_services` e leitura manual de `.env`, substituídos por resolução funcional direta via `ChannelManager.get_credential("BUFFER_<PLAT>_PROFILE_ID", channel_slug)`.
  - `CarouselBuilder`: substituída concatenação direta `Path(f"channels/{slug}/{item}")` por `ChannelManager.get_channel_dir(slug)`.
  - `src/server.py`: propagação explícita de `channel_slug` em `omnipress_publish_article` (para Dev.to, Ghost e Webhooks), `omnipress_queue_post` (para Buffer, Reddit e Webhook) e `omnipress_queue_media_post` (para Instagram Graph, Buffer e YouTube).
  - Purgadas menções e exemplos a canais específicos em `src/core/channel_manager.py` e `src/server.py` (`@dossiedopassado`).

## [0.9.0] — 2026-10-26

### Added
- **Normativa Canônica — Regra 15 (Tipografia Titânica e Embalagem de Thumbnails de Alto CTR)**:
  - Adicionado documento normativo [`.agents/rules/15_high_ctr_thumbnail_typography_and_packaging_standards.md`](.agents/rules/15_high_ctr_thumbnail_typography_and_packaging_standards.md) e incorporação em `AGENTS.md` (Seção 12 em EN/PT), `.agents/rules/README.md` e `docs/AGENT_MANUAL.md` (Playbook 3.1).
  - Estipuladas as 8 Leis da Embalagem de Alto CTR para documentários de YouTube (revertendo estagnação de 0,90%–1,5% para benchmarks de 5,0%–10,0%+):
    1. Limite estrito de 3 a 4 palavras de alto impacto emocional (zero bulas de remédio, subtítulos, bullets ou metadados na capa).
    2. Escala Tipográfica Titânica: headlines em `Anton` ou `Impact` entre 160px e 220px, badges entre 50px e 65px e proibição absoluta de micro-fontes (< 50px).
    3. Safety Heavy Stroke: contorno preto espesso (10px a 16px, `stroke_width >= 11`) e drop-shadow profundo (`0 12px 28px rgba(0,0,0,0.98)`).
    4. Cromática de alta luminância periférica: combinação bi-tonal de Branco Puro (`#FFFFFF`) e Amarelo Alerta (`#FFE500` / `#FFD700`).
    5. Isolamento Chiaroscuro: gradiente escuro tático (`rgba(4,6,10,0.96)`) na metade esquerda do canvas garantindo contraste total.
    6. Escudo Anti-Timestamp do YouTube: canto inferior direito (320px x 140px) 100% livre de textos e badges para não colidir com o marcador de tempo da plataforma.
    7. Regra dos 3 Elementos Focais: Sujeito Dramático (Direita) + Tipografia Titânica (Esquerda) + Selo de Autoridade/Badge.
    8. Teste Obrigatório dos 120px no Celular: inspeção obrigatória em resolução reduzida para garantir leitura instantânea em < 1 segundo.
- **Refatoração do Componente Universal Remotion `ThumbnailEpisode.tsx`**:
  - Reestruturado o layout com tipografia titânica (títulos em 175px/195px, badge em 52px, callout em 56px).
  - Removidos cards com micro-fontes de 22px e purgado qualquer elemento no canto inferior direito para proteção contra o badge de duração do YouTube.
- **Suíte de Testes da Regra 15 (`tests/test_rule15_thumbnails.py`)**:
  - Adicionados 4 testes automatizados para contagem de palavras, escala tipográfica, zona de morte do YouTube e geração de preview mobile de 120px, elevando a suíte para 151 testes automatizados (100% aprovados).

### Changed
- **Alinhamento de Skills e Templates**:
  - `.agents/skills/youtube-thumbnail-design/SKILL.md`: atualizado para a Escala Titânica da Regra 15 e limite de 3-4 palavras.
  - `.agents/skills/omnipress-youtube-documentary/SKILL.md`: Seção 3 atualizada com o protocolo de embalagem da Regra 15.
  - `channels/_template/episodios/_template_episodio/`: atualizados checklists e diretrizes de thumbnails.

### Fixed
- **Desempacotamento de Tupla no `tests/test_carousel_builder.py`**:
  - Corrigido desempacotamento de 5 valores da tupla retornada por `_parse_semantic_line` em `test_parse_semantic_line` e `test_parse_semantic_line_custom_categories`.

## [0.8.3] — 2026-10-26

### Fixed
- **Compatibilidade do Runner de CI sem GPU/Blender**:
  - `tests/test_universal_3d.py`: marcados testes de renderização 3D ao vivo com `@pytest.mark.skipif(not HAS_BLENDER, ...)`.
  - Adicionado `test_blender_binary_discovery_mocked` para testar o algoritmo de descoberta de binário com mock no PATH.
  - Adicionados testes para o fluxo sem Blender (`test_render_when_blender_missing` e `test_mcp_tool_when_blender_missing`), garantindo que tanto ambientes com Blender instalado (estações locais com GPU) quanto ambientes headless sem Blender (como runners do GitHub Actions) executem 100% dos testes com sucesso.
  - `src/utils/runtime_checker.py`: unificada a descoberta de binário do Blender com `Universal3DEngine.find_blender_binary()` para detecção precisa em caminhos locais (`~/.local/bin/blender`).

## [0.8.2] — 2026-10-26

### Added
- **Normativa Canônica — Regra 14 (Desacoplamento Estrito & Anti-Engenharia Errada)**:
  - Adicionado documento normativo [`.agents/rules/14_strict_decoupling_channel_isolation_and_anti_bad_engineering.md`](.agents/rules/14_strict_decoupling_channel_isolation_and_anti_bad_engineering.md) e incorporação formal em `AGENTS.md` (Seção 11) e `.agents/rules/README.md`.
  - Estipulados os 6 princípios invioláveis: Invariância do Core (Zero Hardcoded Slugs), Cascata Declarativa Top-Down, Imutabilidade e Execução Sem Estado (Statelessness), Resolução Universal de Credenciais via `ChannelManager.get_credential`, Cache por Assinatura de Disco e Generalização Obrigatória de Recursos Visuais (Zero Gambiarras).
- **Cascata Top-Down de Parâmetros de Layout no `UniversalCarouselEngine`**:
  - `UniversalCarouselEngine.prepare_assets` agora extrai parâmetros visuais e geométricos declarados no nível raiz ou no bloco `layout_parameters` de `carousel_recipe.json` (`start_y_ratio`, `margin_ratio`, `split_ratio`, `border_radius`, `headline_scale`, `body_scale`, `card_alpha`, etc.) e os propaga automaticamente para cada slide individual, eliminando código boilerplate e garantindo precedência rigorosa de overrides locais.
- **Validação Automatizada de Cascata**:
  - Adicionado novo teste unitário `test_universal_carousel_recipe_layout_cascade` em `tests/test_carousel_builder.py`, elevando a suíte de testes para 141 testes automatizados (100% aprovados).

### Changed
- Universalização de docstrings e exemplos em `src/engine/universal_3d.py`, substituindo menções a canais específicos por `<slug>`.

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
