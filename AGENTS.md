# AGENTS.md — Guidelines for AI Coding Agents & Pair Programmers

> **Bilingual / Bilíngue**: This file provides strict operational rules for AI assistants (such as Antigravity) working on or utilizing the **OmniPress MCP** codebase.
> **Operational Manual**: For the complete, tool-by-tool operational guide and execution playbooks, see [`docs/AGENT_MANUAL.md`](docs/AGENT_MANUAL.md).
> **Rule Hierarchy / Hierarquia de Regras**: Foundational guidelines 1 to 6 are defined in this core document. Detailed normative standards (Rules 07 to 10) reside in [`.agents/rules/`](.agents/rules/README.md).

---


## 🇺🇸 English Guidelines

### 1. Architectural Principles
- **KISS & DRY**: Keep adapters simple and avoid duplicate publishing logic.
- **Adapter Contract**: Any new social network or distribution channel must inherit from [`BasePublisherAdapter`](src/adapters/base.py) and implement:
  - `is_configured() -> bool`
  - `queue_social_post(...) -> dict`
- **Zero Hardcoded Secrets**: Never write API keys, profile IDs, or tokens into code. All credentials must be read from environment variables via `python-dotenv`.
- **Privacy & Legal Safety Gate (LGPD / Judicial Secrecy)**:
  - All content passing through `omnipress_publish_article` and `omnipress_queue_post` must be scanned via [`sanitize_text`](src/utils/sanitizer.py).
  - Never disable sanitization by default.

### 2. Tri-Format Content Standard
When an agent generates a content campaign, it must produce three synchronized assets:
1. **Long-Form Article**: Markdown with standard YAML frontmatter (title, date, category, tags, author, status).
2. **LinkedIn Post**: Attention-grabbing opening hook, 3–5 bulleted insights, discussion question, 3–5 hashtags.
3. **X Thread**: 3 to 5 connected micro-posts (hook, evidence, conclusion).

### 3. Modifying MCP Tools & Protocol Standards (Rule 07)
- **Glama TDQS A+ (5.0) Standards**: All tools must comply with [`.agents/rules/07_mcp_quality_and_tdqs_standards.md`](.agents/rules/07_mcp_quality_and_tdqs_standards.md).
- **Mandatory Annotations**: `readOnlyHint`, `destructiveHint`, `idempotentHint`, and `openWorldHint` must be declared.
- **Canonical Naming**: Use canonical `verb_noun` format (`omnipress_publish_article`, `omnipress_queue_post`, `omnipress_inspect_content`, `omnipress_list_articles`).
- **Backward Compatibility**: Always maintain legacy aliases (`omnipress_list_recent`) in tool dispatchers.
- **Structured Guidance**: Docstrings and descriptions must specify `Use when:`, `Do NOT use when:`, and `Returns:`.

### 4. Multi-Channel Agnostic Architecture
- **Isolation by Default**: Every media brand or publication must live in its own directory under `channels/<slug>/` containing `channel.json`, `articles/`, `media/` (`raw/`, `carousels/`, `stories/`, `highlights/`), and `scripts/`.
- **Engine vs. Channel Asset Separation**: Core layout engines, publisher adapters, and MCP tools remain in `src/` (`src/core/`, `src/engine/`, `src/adapters/`). Channel-specific generation scripts and post definitions belong in `channels/<slug>/scripts/`.
- **Dynamic Configuration**: Publisher adapters resolve credentials and channel IDs (e.g., `buffer_channel_id`) dynamically from `channel.json` before falling back to `.env`.

### 5. Visual Contrast & Carousel Legibility Standards (Rule 08)
- **Universal Readability**: All carousel slides must comply with [`.agents/rules/08_visual_contrast_and_carousel_legibility_standards.md`](.agents/rules/08_visual_contrast_and_carousel_legibility_standards.md).
- **Protective Backdrop Container**: Text blocks must always be rendered over a dark translucent/opaque backdrop card (`rgba(8, 10, 14, 215)`) with rounded corners and subtle brand accent borders to prevent legibility collapse over light, white, or textured background images.
- **Safety Typography Stroke**: All text elements (headline, body, and footer) must carry a dark protective stroke (`stroke_width >= 2`, `stroke_fill=(4, 5, 8, 255)`) to guarantee crisp legibility under any lighting conditions.

### 6. Single Publication & Anti-Duplicate Policy (Rule 09)
- **Exactly-Once Publishing**: All content must be published or scheduled **EXACTLY ONCE**. Never dispatch duplicate posts or maintain redundant scheduled items for the same creative.
- **Mandatory Pre-Publish Verification**: Agents must check the channel's recent posts and queue via `list_posts` prior to invoking `create_post`. If a post is already `sent` or `scheduled`, do not create a duplicate.
- **Clean Replacement Overwrite**: When updating an existing scheduled post, always call `delete_post` to purge the obsolete scheduled draft before enqueueing the replacement.
- **Immediate Publishing First**: When the user requests publishing "na hora" (immediate), always use `mode: "shareNow"`. Never convert an immediate request into a scheduled post without explicit confirmation.
- **Rate Limit & Velocity Compliance**: Adhere to [`.agents/rules/09_single_publication_and_anti_duplicate_policy.md`](.agents/rules/09_single_publication_and_anti_duplicate_policy.md). If social APIs return velocity/spam warnings, never loop retries; immediately purge failed drafts via `delete_post` and report to the user instead of automatically scheduling.

### 7. Programmatic Video & Remotion Engine (Rule 10)
- **Universal Video Engine in `src/video/`**: All programmatic video rendering logic belongs in `src/video/` (`Root.tsx`, `compositions/`, `components/`). Channel-specific assets (media, audio voiceovers, episode configs) belong in `channels/<slug>/media/` and `channels/<slug>/scripts/`.
- **Dual-Aspect Standard**: Every video template or bumper must support both 16:9 widescreen (1920x1080) for long-form YouTube episodes and 9:16 vertical (1080x1920) for YouTube Shorts, Reels, and TikTok.
- **Brand Agnosticism**: Compositions must receive styling, titles, badges, and colors via props (`ChannelIntroProps`, `EpisodeConfig`), resolving defaults from `channels/<slug>/channel.json`. Never hardcode channel names into core video components.
- **Embedded Broadcast Soundscape**: Always pair visual animations with broadcast-quality 48kHz audio (`<Audio />`), sound effects (SFX), and volume ducking (-18dB to -22dB under voiceover).
- **Cross-Platform Vertical Duration Standard (Monetization & Retention)**: Vertical cuts (9:16) for TikTok, YouTube Shorts, and Instagram Reels must adopt a standard duration between **62 and 68 seconds (target: ~65s / 1,950 frames @ 30fps)**. This satisfies the strict >60s requirement for the TikTok Creator Rewards Program (preventing disqualification from sub-minute rounding bugs), aligns with YouTube Shorts (expanded up to 180s), and fits comfortably within Instagram Reels (up to 90s).

---

## 🇧🇷 Diretrizes em Português

### 1. Princípios de Arquitetura
- **KISS e DRY**: Mantenha os adaptadores simples e evite lógica de publicação duplicada.
- **Contrato de Adaptadores**: Qualquer novo canal deve herdar de [`BasePublisherAdapter`](src/adapters/base.py) e implementar:
  - `is_configured() -> bool`
  - `queue_social_post(...) -> dict`
- **Zero Segredos no Código**: Jamais insira chaves de API, IDs de perfis ou tokens no código-fonte. Sempre utilize variáveis de ambiente via `.env`.
- **Filtro de Privacidade e Ética (LGPD e Segredo de Justiça)**:
  - Qualquer texto processado para publicação deve passar por [`sanitize_text`](src/utils/sanitizer.py).
  - Nunca desabilite a sanitização por padrão. Processos judiciais no padrão CNJ (`0000000-00.0000.0.00.0000`), CPFs e CNPJs devem ser mascarados.

### 2. Padrão de Conteúdo Tri-Formato
Ao gerar campanhas de conteúdo, o agente deve produzir 3 formatos integrados:
1. **Artigo Completo**: Markdown com frontmatter YAML para Substack, Jusbrasil, Medium ou blogs estáticos.
2. **Post para LinkedIn**: Gancho forte inicial, 3 a 5 pontos objetivos, pergunta para engajamento e 3 a 5 hashtags.
3. **Thread para X**: Sequência de 3 a 5 posts curtos e de alto impacto.

### 3. Modificação das Ferramentas MCP e Padrões de Protocolo (Regra 07)
- **Padrões Glama TDQS A+ (5.0)**: Todas as ferramentas devem cumprir [`.agents/rules/07_mcp_quality_and_tdqs_standards.md`](.agents/rules/07_mcp_quality_and_tdqs_standards.md).
- **Anotações Mandatórias**: Inclua `readOnlyHint`, `destructiveHint`, `idempotentHint` e `openWorldHint`.
- **Nomenclatura Canônica**: Padrão `verb_noun` (`omnipress_publish_article`, `omnipress_queue_post`, `omnipress_inspect_content`, `omnipress_list_articles`).
- **Compatibilidade Retroativa**: Mantenha aliases legados (`omnipress_list_recent`) nos despachantes.
- **Estruturação**: Descrições e docstrings devem conter `Use when:`, `Do NOT use when:` e `Returns:`.

### 4. Arquitetura Agnóstica Multi-Canal
- **Isolamento por Canal**: Cada canal de mídia reside exclusivamente em sua pasta em `channels/<slug>/` com seu respectivo `channel.json`, `articles/`, `media/` (`raw/`, `carousels/`, `stories/`, `highlights/`) e `scripts/`.
- **Separação Motor vs. Canal**: Motores universais de layout, adaptadores e ferramentas MCP pertencem a `src/` (`src/core/`, `src/engine/`, `src/adapters/`). Scripts e criativos específicos do canal pertencem a `channels/<slug>/scripts/`.
- **Configuração Dinâmica**: Adaptadores de publicação resolvem IDs de canal (ex.: `buffer_channel_id`) diretamente de `channel.json` antes de consultar `.env`.

### 5. Padrão de Contraste Visual e Segurança Tipográfica em Carrosséis (Regra 08)
- **Legibilidade Universal**: Todos os slides gerados devem obedecer estritamente a [`.agents/rules/08_visual_contrast_and_carousel_legibility_standards.md`](.agents/rules/08_visual_contrast_and_carousel_legibility_standards.md).
- **Contêiner Protetor Opaco/Translúcido**: Blocos de texto devem sempre ser renderizados sobre um card escuro translúcido (`rgba(8, 10, 14, 215)`) com cantos arredondados e borda sutil no tom da identidade visual do canal, impedindo colapso de contraste em fundos brancos, documentos ou fotos ruidosas.
- **Contorno de Segurança nas Fontes**: Todos os textos (headline, body e rodapés) devem receber contorno de proteção escuro (`stroke_width >= 2`, `stroke_fill=(4, 5, 8, 255)`) para máxima nitidez visual em qualquer condição de iluminação.

### 6. Política de Publicação Única e Anti-Duplicação (Regra 09)
- **Publicação Estritamente Única (Exactly-Once)**: Todo post deve ser publicado ou agendado **EXATAMENTE UMA VEZ**. É expressamente proibido disparar publicações repetidas ou manter agendamentos duplicados do mesmo criativo na fila.
- **Verificação Prévia Mandatória**: Antes de acionar qualquer ferramenta de publicação (`create_post`), o agente deve obrigatoriamente inspecionar os posts recentes e a fila do canal (`list_posts`). Se o conteúdo já foi enviado (`sent`) ou agendado (`scheduled`), interrompa novas chamadas.
- **Substituição Limpa de Versões**: Para atualizar um post agendado, invoque `delete_post` para purgar a versão antiga antes de inserir a nova.
- **Publicação Imediata por Padrão**: Se o usuário solicitar publicação na hora, sempre utilize `mode: "shareNow"`. Nunca converta uma ordem de envio imediato em post agendado sem consentimento explícito.
- **Conformidade com Limites de Frequência**: Cumpra integralmente [`.agents/rules/09_single_publication_and_anti_duplicate_policy.md`](.agents/rules/09_single_publication_and_anti_duplicate_policy.md). Diante de restrições de velocidade de APIs, nunca repita envios em laço; purgue imediatamente posts com erro via `delete_post` e informe o usuário em vez de agendar silenciosamente.

### 7. Padrão de Vídeos Programáticos & Motor Remotion (Regra 10)
- **Motor Central em `src/video/`**: Toda a lógica de renderização em Remotion reside em `src/video/` (`Root.tsx`, `compositions/`, `components/`). Ativos específicos do canal (áudios de voz gravados, imagens de episódios) pertencem a `channels/<slug>/media/` e `channels/<slug>/scripts/`.
- **Padrão Duplo de Resolução**: Todo template ou vinheta deve suportar nativamente 16:9 (1920x1080) para episódios longos no YouTube e 9:16 (1080x1920) para Shorts, Reels e TikTok.
- **Agnosticismo de Marca**: As composições devem receber cores, títulos, badges e logos via propriedades (`ChannelIntroProps`, `EpisodeConfig`), resolvendo os padrões a partir do `channel.json` do canal ativo. Nunca chumbe o nome de um canal dentro dos componentes universais.
- **Paisagem Sonora Cinemática**: Animações de vídeo devem sempre integrar áudio padrão broadcast em 48kHz (`<Audio />`), efeitos sonoros de retenção (SFX) e atenuação automática de trilha (ducking a -18dB a -22dB sob a voz humana).
- **Padrão de Duração de Vídeos Verticais (Monetização e Retenção)**: Vídeos verticais (9:16) para TikTok, YouTube Shorts e Instagram Reels devem adotar duração padrão entre **62 e 68 segundos (alvo: ~65s / 1.950 frames a 30fps)**. Isso cumpre o requisito de monetização obrigatória do TikTok Creator Rewards (>60s com margem de segurança contra arredondamento para 59s), enquadra-se no novo limite do YouTube Shorts (até 180s) e fica dentro do teto do Instagram Reels (90s).

