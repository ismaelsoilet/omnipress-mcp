# 📖 Manual Operacional do OmniPress MCP para Agentes de I.A.
*The Definitive Autonomous Publishing & Media Generation Guide for AI Agents*

> **Público-Alvo**: Este documento foi escrito especificamente para Agentes de Inteligência Artificial (Google Antigravity, Claude Desktop, OpenAI ChatGPT, Gemini CLI, Hermes Agent, subagentes autônomos e automações n8n) operando sobre o protocolo **Model Context Protocol (MCP)**.
> **Versão do Protocolo**: MCP 2026 / Glama TDQS A+ (5.0).
> **Idiomas / Languages**: 🇧🇷 Português (Principal) & 🇺🇸 English Reference.

---

## 1. Visão Geral e Filosofia Arquitetural

O **OmniPress MCP** é um motor agêntico de publicação editorial, distribuição social e geração programática de mídia. Ele converte briefings brutos, pesquisas técnicas, análises forenses, legislações tributárias e roteiros em campanhas sincronizadas multi-formato:
1. **Artigos Long-Form**: Markdown estruturado com frontmatter YAML para Substack, Medium, Jusbrasil ou blogs estáticos.
2. **Posts de Autoridade para LinkedIn**: Ganchos de alta retenção, tópicos densos e debates técnicos.
3. **Threads para X (Twitter)**: Sequências concisas com gancho, evidências e conclusão.
4. **Carrosséis Visuais de Alto Contraste (Regra 08)**: Decks de imagens 3:4 e 1:1 renderizados pelo Pillow com cards de proteção tipográfica.
5. **Vídeos Programáticos em Remotion (Regra 10)**: Episódios documentais 16:9 e Shorts/Reels 9:16 com legendas sincronizadas palavra por palavra e dynamic audio ducking.

### Topologia de Execução do Servidor
O servidor MCP é unificado em Python ([`src/server.py`](file:///home/ismaelsoilet/omnipress-mcp/src/server.py)) e opera em dois modos:
- **STDIO Mode**: Utilizado por clientes locais (Claude Desktop, Gemini CLI, Antigravity IDE). Executado via `python src/server.py`.
- **HTTP/SSE ASGI Mode**: Utilizado por ambientes conteinerizados (Docker, Docker Compose, Coolify na Oracle Cloud). Executado via `python src/server.py --http 3333` ou `OMNIPRESS_MODE=http`. Expõe endpoints SSE e a rota de monitoramento de saúde `/health`.

---

## 2. Catálogo Completo de Ferramentas MCP (TDQS A+ 5.0)

O OmniPress expõe **14 ferramentas** (13 canônicas e 1 alias retrocompatível no padrão `verb_noun`), todas enriquecidas com metadados de protocolo (`readOnlyHint`, `destructiveHint`, `idempotentHint`, `openWorldHint`):

### 2.1. `omnipress_publish_article`
Salva um artigo completo com metadados YAML na árvore de arquivos e emite evento webhook se configurado.

* **Anotações**: `readOnlyHint=False`, `destructiveHint=False`, `idempotentHint=False`, `openWorldHint=False`.
* **Quando USAR**: Quando o agente concluir a redação de um artigo longo de autoridade e precisar arquivá-lo permanentemente.
* **Quando NÃO USAR**: Para microposts sociais ou posts de redes sociais (use `omnipress_queue_post`).
* **Parâmetros**:
  | Parâmetro | Tipo | Obrigatório | Descrição |
  |---|---|---|---|
  | `title` | `string` | Sim | Título editorial do artigo. |
  | `content_markdown` | `string` | Sim | Conteúdo integral formatado em Markdown. |
  | `category` | `string` | Não | Categoria (ex: `technology`, `tax-legal`, `govtech`, `history`). Padrão: `technology`. |
  | `tags` | `array[string]` | Não | Lista de tags temáticas. |
  | `author` | `string` | Não | Nome do autor ou da publicação. Padrão: `OmniPress`. |
  | `channel_slug` | `string` | Não | Slug do canal de destino (ex: `dossie-historico`). Se omitido, salva na raiz `articles/`. |
  | `target_platform` | `string` | Não | Destino da publicação: `"markdown"` (padrão local), `"devto"`, `"ghost"` ou `"all"`. |
  | `canonical_url` | `string` | Não | URL canônica original para indexação SEO no Dev.to e Ghost. |
  | `published` | `boolean` | Não | Define se o artigo será publicado imediatamente (`true`) ou criado como rascunho (`false`). Padrão: `false`. |
  | `force_duplicate` | `boolean` | Não | Força envio ignorando o livro-razão de idempotência da Regra 09. Padrão: `false`. |
  | `sanitize` | `boolean` | Não | Ativa o filtro LGPD, credenciais e segredo de justiça. Padrão: `true`. |
* **Exemplo de Chamada pelo Agente (Publicando Rascunho no Dev.to e Ghost)**:
  ```json
  {
    "title": "Auditoria Forense de Bancos de Dados em Litígios Tributários",
    "content_markdown": "# Auditoria Forense...\n\nNeste estudo analisamos os logs do banco...",
    "category": "tax-legal",
    "tags": ["pericia", "sql", "tributario"],
    "channel_slug": "dossie-historico",
    "target_platform": "all",
    "published": false,
    "sanitize": true
  }
  ```

---

### 2.2. `omnipress_queue_post`
Envia publicações sociais para a fila de agendamento (Buffer, Reddit, Instagram Graph API ou Webhook).

* **Anotações**: `readOnlyHint=False`, `destructiveHint=False`, `idempotentHint=False`, `openWorldHint=True`.
* **Quando USAR**: Para agendar rascunhos para LinkedIn, X, Threads, Reddit ou Instagram.
* **Quando NÃO USAR**: Para arquivar artigos longos em Markdown (use `omnipress_publish_article`).
* **Parâmetros**:
  | Parâmetro | Tipo | Obrigatório | Descrição |
  |---|---|---|---|
  | `text` | `string` | Sim | Texto da publicação social formatado com hashtags e ganchos. |
  | `platforms` | `array[string]` | Não | Redes alvo: `["linkedin"]`, `["x"]`, `["threads"]`, `["instagram"]`, `["reddit:webdev"]`. |
  | `title` | `string` | Não | Título do post (obrigatório se publicar no Reddit). |
  | `media_urls` | `array[string]` | Não | URLs públicas HTTPS de imagens (obrigatório para carrossel no Instagram). |
  | `schedule_time` | `string` | Não | Data/hora ISO 8601 para agendamento programado. |
  | `channel_slug` | `string` | Não | Canal de origem para resolver IDs do Buffer dinamicamente. |
  | `mode` | `string` | Não | Modo de envio do Buffer: `"shareNow"` (imediato), `"customScheduled"` (agendado) ou `"addToQueue"`. |
  | `allow_test` | `boolean` | Não | Permite bypass do interceptor de strings de teste para testes unitários controlados. Padrão: `false`. |
  | `force_duplicate` | `boolean` | Não | Força envio ignorando o livro-razão de idempotência da Regra 09. Padrão: `false`. |
  | `sanitize` | `boolean` | Não | Ativa a desidentificação de dados sensíveis. Padrão: `true`. |

---

### 2.3. `omnipress_inspect_content`
Varre um texto em busca de números de processos judiciais (CNJ), CPFs, CNPJs, telefones e e-mails pessoais sem gravar arquivos.

* **Anotações**: `readOnlyHint=True`, `destructiveHint=False`, `idempotentHint=True`, `openWorldHint=False`.
* **Quando USAR**: Antes de publicar ou exibir rascunhos com dados de casos reais para garantir que não há violação de sigilo.
* **Quando NÃO USAR**: Se já estiver chamando `publish_article` ou `queue_post` com `sanitize=True`.
* **Retorno**: Relatório com o total de itens sensíveis e detalhamento de cada ocorrência.

---

### 2.4. `omnipress_list_channels`
Descobre todos os canais de mídia configurados no diretório `channels/`.

* **Anotações**: `readOnlyHint=True`, `destructiveHint=False`, `idempotentHint=True`, `openWorldHint=False`.
* **Parâmetros**: `include_templates` (`boolean`, opcional, padrão `false`).
* **Retorno**: Lista formatada de canais com slugs, nomes, categorias, handles e status de configuração social.

---

### 2.5. `omnipress_get_channel`
Lê a configuração estruturada completa (`channel.json`) de um canal específico.

* **Anotações**: `readOnlyHint=True`, `destructiveHint=False`, `idempotentHint=True`, `openWorldHint=False`.
* **Parâmetro**: `slug` (`string`, obrigatório).
* **Retorno**: JSON completo contendo paleta de cores (`theme_colors`), tipografia, handles sociais e IDs do Buffer.

---

### 2.6. `omnipress_create_channel`
Provisiona um novo espaço de trabalho de canal isolado com pastas e `channel.json`.

* **Anotações**: `readOnlyHint=False`, `destructiveHint=False`, `idempotentHint=False`, `openWorldHint=False`.
* **Parâmetros**: `slug`, `name`, `handle`, `category`, `description`, `primary_color`, `buffer_channel_id`, `default_hashtags`.

---

### 2.7. `omnipress_build_carousel`
Renderiza um conjunto completo de lâminas de carrossel em proporção 3:4 (ou 1:1) com conformidade visual estrita à Regra 08.

* **Anotações**: `readOnlyHint=False`, `destructiveHint=False`, `idempotentHint=True`, `openWorldHint=False`.
* **Parâmetros**:
  | Parâmetro | Tipo | Obrigatório | Descrição |
  |---|---|---|---|
  | `channel_slug` | `string` | Sim | Canal proprietário do criativo. |
  | `post_slug` | `string` | Sim | Identificador do post (cria pasta em `media/carousels/<post_slug>/`). |
  | `slides_json` | `string` | Sim | JSON string com array de lâminas (`bg_image_path`, `headline`, `body`, etc.). |
  | `aspect_ratio` | `string` | Não | `3:4` (padrão Instagram/LinkedIn) ou `1:1`. |
* **Estrutura de cada Lâmina em `slides_json`**:
  ```json
  [
    {
      "bg_image_path": "media/assets/fundo_slide1.jpg",
      "headline": "O SEGREDO DA ARQUITETURA LIMPA",
      "body": "Como desacoplar motores centrais de dados de canais.",
      "badge_text": "ARQUITETURA DE SOFTWARE",
      "swipe_str": "Deslize →"
    },
    {
      "bg_image_path": "media/assets/fundo_slide2.jpg",
      "headline": "BENEFÍCIOS DA SEPARAÇÃO",
      "body": "Zero acoplamento de código com dados de produção.",
      "swipe_str": "Salve & Compartilhe"
    }
  ]
  ```

---

### 2.8. `omnipress_prepare_dark_script`
Prepara o manifesto e os roteiros estruturados de um episódio ou vídeo curto para canais dark.

* **Anotações**: `readOnlyHint=False`, `destructiveHint=False`, `idempotentHint=False`, `openWorldHint=False`.
* **Parâmetros**: `title`, `hook_text`, `body_text`, `cta_text`, `category`, `channel_slug`, `estimated_duration_seconds`.

---

### 2.9. `omnipress_list_articles` & `omnipress_list_recent`
Lista artigos arquivados recentemente no repositório com suporte a paginação e filtro por canal.

* **Anotações**: `readOnlyHint=True`, `destructiveHint=False`, `idempotentHint=True`, `openWorldHint=False`.
* **Parâmetros**: `limit` (`integer`, padrão `10`), `channel_slug` (`string`, opcional).

---

### 2.10. `omnipress_queue_media_post`
Envia conteúdos multimídia (carrosséis do Instagram, YouTube Shorts, vídeos e posts com imagem no X/Twitter) com roteamento inteligente e proteção de 5 portões via `PublishingShield`.

* **Anotações**: `readOnlyHint=False`, `destructiveHint=False`, `idempotentHint=False`, `openWorldHint=True`.
* **Quando USAR**: Para publicar carrosséis prontos no Instagram, agendar Shorts no YouTube ou disparar tweets com imagens no X.
* **Parâmetros**:
  | Parâmetro | Tipo | Obrigatório | Descrição |
  |---|---|---|---|
  | `caption` | `string` | Sim | Legenda ou descrição completa do post. |
  | `platforms` | `array[string]` | Sim | Plataformas alvo (`["instagram"]`, `["youtube"]`, `["x"]`, `["all"]`). |
  | `media_urls` | `array[string]` | Não | Lista de URLs públicas HTTPS das imagens ou vídeos. |
  | `title` | `string` | Não | Título do vídeo no YouTube ou do criativo. |
  | `media_type` | `string` | Não | Tipo de mídia (`"image"`, `"carousel"`, `"short"`, `"video"`). |
  | `channel_slug` | `string` | Não | Canal proprietário para resolução de IDs de publicação. |
  | `mode` | `string` | Não | Modo de envio (`"shareNow"`, `"customScheduled"`, `"addToQueue"`). |
  | `schedule_time` | `string` | Não | Horário de agendamento ISO 8601 se não for imediato. |
  | `allow_test` | `boolean` | Não | Permite textos curtos de teste em ambiente de QA. Padrão: `false`. |
  | `force_duplicate` | `boolean` | Não | Permite republicação forçada ignorando a Regra 09. Padrão: `false`. |
  | `sanitize` | `boolean` | Não | Ativa o filtro LGPD e segredo de justiça. Padrão: `true`. |

### 2.11. `omnipress_brainstorm_channel`
Gera conceitos de canais de mídia, arquétipos psicológicos de retenção e 10 temas virais com ganchos de 0 a 3 segundos (curiosity loops) para YouTube, Instagram, TikTok e X.

* **Anotações**: `readOnlyHint=True`, `destructiveHint=False`, `idempotentHint=True`, `openWorldHint=False`.
* **Quando USAR**: Ao planejar o lançamento de um novo canal ou backlog de roteiros com alta taxa de clique (CTR).
* **Parâmetros**: `niche` (string, padrão `"historia"`), `tone` (string, padrão `"mystery"`), `target_audience` (string).
* **Retorno**: JSON com conceitos do canal, ganchos magnéticos e 10 ideias estruturadas para episódios.

---

### 2.12. `omnipress_generate_speech`
Converte roteiros e narrações em arquivos de áudio estéreo broadcast MP3 utilizando vozes neurais ultra-realistas.

* **Anotações**: `readOnlyHint=False`, `destructiveHint=False`, `idempotentHint=False`, `openWorldHint=False`.
* **Quando USAR**: Para gerar narrações de alta fidelidade para vídeos curtos, carrosséis falados ou episódios documentais.
* **Parâmetros**:
  | Parâmetro | Tipo | Obrigatório | Descrição |
  |---|---|---|---|
  | `text` | `string` | Sim | Texto da narração do roteiro. |
  | `voice` | `string` | Não | Voz neural (ex: `pt-BR-AntonioNeural`, `pt-BR-FranciscaNeural`, `en-US-ChristopherNeural`). |
  | `output_filename` | `string` | Não | Nome personalizado do arquivo MP3 em `media/output/`. |
* **Retorno**: JSON com `audio_path`, tamanho em bytes, modelo de voz e status de sucesso.

---

### 2.13. `omnipress_render_dark_video`
Renderiza vídeos MP4 em proporção 9:16 (Shorts/Reels/TikTok) ou 16:9 (YouTube) combinando áudio neural e imagens de cenas cinematográficas com ffmpeg e Remotion.

* **Anotações**: `readOnlyHint=False`, `destructiveHint=False`, `idempotentHint=False`, `openWorldHint=False`.
* **Quando USAR**: Para produzir vídeos finais prontos para publicação a partir de imagens e narrações.
* **Parâmetros**:
  | Parâmetro | Tipo | Obrigatório | Descrição |
  |---|---|---|---|
  | `text` | `string` | Não | Texto para geração e narração direta de áudio. |
  | `audio_path` | `string` | Não | Caminho de arquivo MP3 existente se já gravado. |
  | `image_paths` | `array[string]` | Não | Lista de caminhos para as imagens que compõem as cenas do vídeo. |
  | `aspect_ratio` | `string` | Não | `"9:16"` (vertical) ou `"16:9"` (widescreen). Padrão: `"9:16"`. |
  | `voice` | `string` | Não | Voz neural se o áudio for sintetizado do texto. |
* **Retorno**: JSON com caminho do vídeo gerado (`video_path`), proporção, áudio e diagnóstico de runtime.

---

### 2.14. `omnipress_render_3d`
Renderiza assets 3D fotorrealistas isolados com canal alfa transparente (PNG/WebM) via Blender 4.2+ LTS headless.

* **Anotações**: `readOnlyHint=False`, `destructiveHint=False`, `idempotentHint=True`, `openWorldHint=False`.
* **Quando USAR**:
  - Para criar mockups 3D de smartphones com textura dinâmica UV exibindo artigos ou carrosséis.
  - Para gerar moedas/medalhões metálicos 3D giratórios ou insígnias para b-rolls de vídeos.
  - Para criar títulos em tipografia 3D extrudada e chanfrada com reflexos de estúdio.
* **Parâmetros**:
  | Parâmetro | Tipo | Obrigatório | Descrição |
  |---|---|---|---|
  | `template` | `string` | Não | Nome do template (`device_mockup`, `rotating_badge`, `kinetic_title`). Padrão: `"device_mockup"`. |
  | `output_filename` | `string` | Não | Nome do arquivo de saída (ex: `hero_mockup.png`). Padrão: `"asset_3d.png"`. |
  | `texture_path` | `string` | Não | Caminho da imagem para textura de tela ou emblema frontal. |
  | `text` | `string` | Não | Texto para o template de tipografia 3D (`kinetic_title`). |
  | `material` | `string` | Não | Preset de material (`gold`, `silver`, `chrome`, `obsidian`, `bronze`). |
  | `channel_slug` | `string` | Não | Slug do canal de destino (salva em `channels/<slug>/media/visuals/3d/`). |
  | `resolution` | `string` | Não | Dimensões do render (`"1080x1080"`, `"1920x1080"`, `"1080x1920"`). |
  | `engine` | `string` | Não | Motor de render (`"BLENDER_EEVEE_NEXT"` ou `"CYCLES"`). Padrão: `"BLENDER_EEVEE_NEXT"`. |
  | `samples` | `int` | Não | Quantidade de samples de renderização. Padrão: `32`. |
* **Retorno**: JSON com status, caminho do arquivo gerado (`output_path`), template, resolução, engine e tamanho do arquivo.

---

### 2.15. Suíte CLI de Diagnóstico e Onboarding (`omnipress`)
Para inspeção e configuração interativa fora do contexto de chat do MCP, utilize o comando CLI `omnipress`:

```bash
# Diagnóstico completo de runtimes (Python, Node.js, FFmpeg, Edge-TTS, Blender 3D):
omnipress doctor

# Status do canal ativo e histórico do ledger PublishingShield:
omnipress status

# Assistente interativo de configuração de credenciais (.env):
omnipress setup
```

---

## 3. Playbooks Operacionais Passo a Passo para Agentes

### Playbook 1: Criação de Campanha Tri-Formato Completa
Quando o usuário pedir: *"Escreva sobre o tema X e prepare a publicação."*

1. **Geração do Conteúdo**:
   - Redija o artigo técnico completo em Markdown.
   - Crie o post de alta autoridade para LinkedIn (gancho + 3-5 tópicos + pergunta de debate + 3-5 hashtags).
   - Crie a thread para X (3 a 5 posts curtos numerados com 🧵).
2. **Apresentação & Confirmação**:
   - Exiba o rascunho dos 3 formatos no chat.
   - Pergunte ao usuário se ele aprova a persistência e agendamento.
3. **Execução das Ferramentas**:
   - Chame `omnipress_publish_article(title=..., content_markdown=..., category=..., tags=..., channel_slug=...)`.
   - Chame `omnipress_queue_post(text=linkedin_post, platforms=["linkedin"], channel_slug=...)`.
   - Chame `omnipress_queue_post(text=x_thread, platforms=["x"], channel_slug=...)`.

---

### Playbook 2: Criação de Carrossel de Alto Contraste (Regra 08)
Quando o usuário pedir: *"Gere um carrossel para o Instagram sobre este tema."*

1. **Identificar o Canal**:
   - Chame `omnipress_get_channel("slug-do-canal")` para conhecer a cor primária (`#D4AF37`, etc.) e o handle (`@canal`).
2. **Definir as Lâminas (4 a 7 slides)**:
   - Slide 1 (Capa): Gancho provocativo + badge de categoria.
   - Slides 2 a N-1 (Desenvolvimento): Cada lâmina com headline concisa (máximo 4 linhas) e corpo explicativo direto.
   - Slide Final (CTA): Chamada para ação ("Siga @canal", "Salve este post").
3. **Renderizar com `omnipress_build_carousel`**:
   - Certifique-se de que cada `bg_image_path` aponta para um arquivo existente em `channels/<slug>/media/raw/` ou `media/staging/`.
   - O `CarouselBuilder` aplicará automaticamente o card protetor escuro (`rgba(8, 10, 14, 215)`) e o contorno escuro nas fontes (`stroke_width=2`), garantindo legibilidade perfeita sob qualquer fundo.
4. **Hospedagem & Fila**:
   - Utilize o storage provider para obter as URLs públicas das lâminas geradas (`https://...`).
   - Chame `omnipress_queue_post(text=legenda, platforms=["instagram"], media_urls=[url_slide1, url_slide2, ...])`.

---

### Playbook 3: Renderização de Vídeo Programático com Remotion (Regra 10)
Quando o usuário pedir: *"Renderize a vinheta ou o episódio de vídeo do canal."*

1. **Respeitar os Padrões de Resolução**:
   - 16:9 widescreen (`1920x1080` a 30fps) para YouTube principal (`ChannelIntro-16x9`, `DocumentaryEpisode-16x9`).
   - 9:16 vertical (`1080x1920` a 30fps) para Shorts, Reels e TikTok (`ChannelIntro-9x16`, `DocumentaryShort-9x16`).
2. **Padrão de Duração de Vídeos Verticais (Monetização e Retenção)**:
   - Vídeos verticais (9:16) para TikTok, YouTube Shorts e Instagram Reels devem adotar duração padrão entre **62 e 68 segundos (alvo: ~65s / 1.950 frames a 30fps)**.
   - Isso cumpre o requisito de monetização obrigatória do TikTok Creator Rewards (>60s com margem contra arredondamento para 59s), enquadra-se no novo limite do YouTube Shorts (até 180s) e fica dentro do teto do Instagram Reels (90s).
3. **Legendas Dinâmicas Sincronizadas (Regra de Ouro: Timing da Fala, Texto do Roteiro & Destaque Ativo)**:
   - **Origem Estrita do Texto**: O texto da legenda deve vir **sempre do roteiro oficial aprovado (`roteiro.json` / `roteiro_revisado.md`)**, garantindo 100% de correção gramatical, concordância e nomes próprios perfeitos. O texto cru ou fonético do Whisper nunca deve ser exibido diretamente.
   - **Origem Estrita do Timing**: O Whisper é usado exclusivamente para extrair os timestamps de início e fim da fala real.
   - **Destaque Dinâmico Palavra por Palavra (Active Word Highlight)**: Utilize [`SynchronizedCaptions`](../src/video/components/SynchronizedCaptions.tsx) fornecendo o array `words` com `{ word, start, end }`. A palavra ativa falada no momento recebe destaque em ouro (`#FFD700`), escala (`1.06x`) e sublinhado dourado sobre o card protetor escuro (`rgba(8, 10, 14, 0.90)`). Chunks de 2 a 4 palavras.
4. **Agnosticismo de Marca**:
   - Nunca altere o código em `src/video/` para colocar o nome de um canal específico.
   - Passe os dados da marca via propriedades (`props`):
     ```bash
     npx remotion render src/video/index.ts DocumentaryEpisode-16x9 out/video.mp4 \
       --props='{"config": {"channelSlug": "meu-canal", "title": "Título do Episódio", "introProps": {"channelName": "MEU CANAL", "primaryColor": "#3B82F6"}}}'
     ```
5. **Tratamento Obrigatório de Estúdio e Masterização de Voz (Voiceover Gate)**:
   - Toda narração de voz (gravada ou sintética) deve passar obrigatoriamente pela Cadeia de Masterização Broadcast antes de ser renderizada no Remotion:
     1. De-click e supressão de ruídos de boca (`adeclick`).
     2. Filtro passa-alta em 80Hz (`highpass=80`) cortando ruídos subsônicos e batidas de mesa.
     3. Denoise espectral cirúrgico (`afftdn` a -28dB) eliminando chiado de sala e pré-amplificador.
     4. Equalização cirúrgica de 4 bandas (corte nasal em 300Hz, calor em 140Hz, presença em 3kHz, ar em 8.5kHz).
     5. Compressor dinâmico de estúdio (ratio ~3:1) para inteligibilidade uniforme.
     6. Normalização internacional EBU R128 travando o áudio entre **-14.0 e -16.0 LUFS** (alvo: **-14.0 LUFS**, True Peak <= -1.2 dBTP).
   - É expressamente proibido renderizar vídeos com voz crua ou baixa (< -20 LUFS).
6. **Suavização Acústica e Protocolo Anti-Ruído Pré-Fala**:
   - **Lead-in Zeroing**: Todo áudio de gravação real tem ruído ambiente antes da fala; deve-se silenciar digitalmente (`gain = 0.0`) o intervalo entre 0.00s e 80ms antes do primeiro fonema, aplicando curva suave de fade-in (60ms a 80ms) na entrada da voz.
   - **Fade-in na Trilha Musical**: No Remotion, a música de abertura deve sempre interpolar um fade-in progressivo nos primeiros 1.5 a 2.0 segundos, evitando impactos sonoros repentinos.
   - **Fade-in de Proteção na Locução**: Utilizar fade-in inicial de 0.5s no componente `<Audio />` de voz.
7. **Agendamento Direto Multiplataforma (Recomendado para Vídeos Verticais)**:
   - Para vídeos verticais (Shorts, Reels, TikTok), o agendamento direto nativo é a prática recomendada:
     - **YouTube Studio**: Upload do MP4, título e descrição com atribuição CC-BY, agendamento de data/hora na aba Visibilidade.
     - **Meta Business Suite / Instagram**: Upload do MP4 com capa 9:16 personalizada e enquadramento da grade do feed.
     - **TikTok Studio Desktop (tiktok.com/tiktokstudio)**: Upload do MP4 com ativação de "Agendar vídeo" (até 10 dias) e desativação de legendas automáticas da rede para não sobrepor as legendas do vídeo.
8. **Boas Práticas de Renderização & Performance (Remotion Engine)**:
   - **Configurações Globais Otimizadas (`remotion.config.ts`)**:
     - `Config.setCachingEnabled(true)`: Ativa cache persistente do bundle Webpack, eliminando a recompilação redundante de 7-9s por render.
     - `Config.setVideoImageFormat("jpeg")` e `Config.setJpegQuality(80)`: Captura de frames intermediários significativamente mais leve e rápida que PNG.
     - `Config.setX264Preset("fast")`: Acelera a codificação H.264 no FFmpeg sem perda perceptível de qualidade visual.
     - `Config.setChromiumMultiProcessOnLinux(true)`: Distribuição balanceada de processos Chromium no Linux/WSL2.
     - `Config.setConcurrency(4)`: Ponto ideal de concorrência calibrado para sistemas com 2.5–4GB de RAM livre, prevenindo thrashing de swap.
   - **Eficiência de Componentes Visuais**:
     - Texturas de ruído analógico em [`FilmGrain.tsx`](../src/video/components/FilmGrain.tsx) utilizam tiles seamless SVG em base64 cacheados em memória bitmap com deslocamento analógico (`transform: translate`), evitando recalcular filtros fractais de alta oitava (`feTurbulence`) na CPU por frame.
     - Imagens de arquivo devem ser preferencialmente pré-escaladas para resolução 1080p antes da renderização para reduzir a carga de decodificação e interpolação no Ken Burns.
   - **Fluxo de Trabalho Ágil**:
     - Durante testes visuais e validação de legendas/transições, renderize apenas pequenos trechos (`--frames=0-60`) ou capture stills estáticos (`npx remotion still ... --frame=150`).
9. **Uso das 12 Agent Skills Oficiais do Remotion**:
   - O projeto conta com as 12 skills oficiais instaladas em [`.agents/skills/remotion-*`](../.agents/skills/) e documentadas em [`REMOTION_SKILLS_AND_DOCS.md`](./REMOTION_SKILLS_AND_DOCS.md).
   - Para animações, utilize sempre `interpolate()` e `spring()` (nunca transições CSS/Tailwind).
   - Para pré-visualização em tempo real: `npm run remotion:preview`.
   - Para buscar documentação oficial: consulte o endpoint Algolia ou utilize URLs `.md` (ex.: `https://www.remotion.dev/docs/interpolate.md`).
   - Para atualizar as skills: `npx remotion skills update`.
10. **Biblioteca de Componentes Visuais e Dinâmica de Cena**:
    - [`ChannelOutro`](../src/video/components/ChannelOutro.tsx): Vinheta oficial de encerramento em 2 fases (Fase 1: chamada nobre para compartilhamento; Fase 2: chamada de inscrição com branding oficial e zonas de YouTube End Screen).
    - [`HeraldicSurgery`](../src/video/components/HeraldicSurgery.tsx): Animação da "Cirurgia Heráldica de 1889", com substituição cirúrgica em tempo real do Brasão Imperial pela Esfera Celeste com flash óptico e badge evolutivo.
    - [`KenBurnsImage`](../src/video/components/KenBurnsImage.tsx): Presets refinados de movimento de câmera (`zoom-in`, `zoom-out`, `pan-left`, `pan-right`, `subtle-zoom`, `snap-zoom`, `dramatic-push`, `tilt-down`).
    - [`DustParticles`](../src/video/components/DustParticles.tsx) & [`FilmGrain`](../src/video/components/FilmGrain.tsx): Partículas de poeira e granulação de filme otimizadas para GPU sem degradação de CPU.
    - **Sonoplastia Tátil por Cena**: Suporte direto em `DocumentaryScene` a `sfxSrc` e `sfxVolume` para sincronização precisa de efeitos de transição e impactos.
11. **Padrões de Luminância & Fidelidade Histórica**:
    - Luminância média obrigatória entre **45 e 180** (escala 0-255). Imagens com fundos pretos opacos (< 45) são sumariamente rejeitadas. Fundo em ardósia escura (`#12161F` / `#161B22`).
    - Portão Anti-Anacronismo: banimento de armas pré/pós-época ou bandeiras errôneas. Cenas de "Caso Encerrado" permitidas apenas no Ato Final.

---

### Playbook 4: Isolamento Multi-Canal e Arquitetura de Pastas (Regra 04)
Quando gerenciar múltiplos canais ou marcas:

- **Isolamento Completo**:
  ```
  channels/<slug>/
    ├── .env                 # Credenciais e segredos isolados do canal (BUFFER_API_KEY, IDs)
    ├── .env.example         # Template de variáveis do canal
    ├── channel.json         # Configuração exclusiva da marca e handles
    ├── campanhas/           # Campanhas e postagens cotidianas (personal_brand)
    ├── artigos/             # Artigos em AAAA/MM/
    ├── media/
    │   ├── raw/             # Imagens e fontes brutas
    │   ├── carousels/       # Lâminas geradas pelo Pillow
    │   ├── stories/         # Formatos 9:16
    │   └── highlights/      # Capas de destaque
    └── scripts/             # Scripts específicos do canal
  ```

- **Ambiente Central vs. Ambientes Isolados**:
  - **`.env` na raiz**: Configura o canal principal padrão (**Dossiê Histórico**), através de `OMNIPRESS_ACTIVE_CHANNEL=dossie-historico`.
  - **`channels/<slug>/.env`**: Cada canal secundário (ex.: `channels/ismael-soilet/.env`) possui seu próprio arquivo `.env` para suas chaves de API particulares (ex.: conta pessoal do Buffer).
  - **Ordem de Precedência de Credenciais**:
    1. `channels/<slug>/.env` (prioridade máxima do canal)
    2. Variáveis de ambiente prefixadas (ex.: `<SLUG>_BUFFER_API_KEY`)
    3. `.env` na raiz do repositório (fallback global / dossie-historico)

- **Sincronização Automática com Buffer (`sync-buffer`)**:
  - Para mapear instantaneamente os IDs de perfis sociais conectados (Instagram, LinkedIn, X, Threads, YouTube) para o `channel.json`:
    ```bash
    omnipress sync-buffer <slug>
    ```
  - O OmniPress consulta a API do Buffer usando a chave isolada do canal e atualiza o `channel.json` automaticamente.

- **Fallback Standalone**: Se uma ferramenta for chamada sem `channel_slug`, ela salvará em `articles/` e `media/` na raiz do repositório e usará as credenciais do `.env` da raiz, garantindo compatibilidade reversa.

---

### Playbook 5: Política de Publicação Única & Blindagem do PublishingShield (Regra 09)
Para evitar envios acidentais repetidos, vazamento de testes e estouro de limites de API:

1. **Portões Automáticos do `PublishingShield`**:
   - O adaptador rejeitará automaticamente qualquer post contendo palavras de teste (`"teste"`, `"test"`, `"asdf"`, `<12 caracteres`) disparado ao vivo com `mode="shareNow"`.
   - O adaptador rejeitará qualquer envio para Instagram sem URLs de mídia válidas.
   - O adaptador rejeitará textos acima do limite estrito de cada plataforma (Instagram: **2.196 caracteres**, X: **280 caracteres**, Threads: **500 caracteres**, LinkedIn: **3.000 caracteres**).
2. **Idempotência por Livro-Razão (24 Horas)**:
   - Todo post publicado é registrado em `media/staging/publishing_ledger.json` com hash SHA-256 do canal, texto e mídias. Disparos idênticos no período de 24h são bloqueados automaticamente com aviso da Regra 09.
3. **Atualização Limpa & Exclusão**:
   - Para substituir um agendamento ou post em rascunho, utilize `delete_post` para remover o registro no Buffer antes de enfileirar a nova versão.
4. **Respeito aos Limites de Velocidade da Meta**:
   - Se a API retornar erro de velocidade/spam, não realize retentativas em loop e nunca converta publicação imediata em agendamento automático. Avise o usuário e respeite o cooldown de 1 a 2 horas.

---

## 4. Camada de Armazenamento Agnóstico (`src/utils/storage.py`)

A API oficial do Instagram exige URLs públicas HTTPS acessíveis pela Meta. O OmniPress seleciona o provedor de storage automaticamente por ordem de prioridade:

1. **AWS S3 / Cloudflare R2 / MinIO**: Ativado se `S3_BUCKET_NAME` ou `R2_BUCKET_NAME` estiver presente no `.env`.
2. **Local Static Container Hosting**: Ativado se `OMNIPRESS_PUBLIC_URL` estiver definido (hospeda imagens em `media/staging/` servidas diretamente pelo container Docker/Coolify em `https://seu-dominio.com/media/staging/...`).
3. **Catbox.moe Fallback**: Utilizado automaticamente em desenvolvimento local quando nenhuma credencial em nuvem foi configurada.

---

## 5. Matriz de Tratamento de Erros e Recuperação para Agentes

| Cenário de Erro | Causa Provável | Ação Recomendada para o Agente |
|---|---|---|
| Buffer retorna `No channel found for service` | Canal do LinkedIn/X não conectado ou ID incorreto no `channel.json` / `.env`. | O agente deve avisar o usuário de forma transparente, exibir o texto formatado no chat para cópia manual e indicar o arquivo `docs/SETUP_GUIDE.md`. |
| Shield bloqueia com `Placeholder/test text` | Texto contém `"teste"` ou é muito curto para envio imediato ao vivo. | O agente deve usar conteúdo editorial real ou passar `allow_test=True` se for teste de integração controlado. |
| Shield bloqueia com `exceeds maximum allowed length` | Legenda do Instagram ultrapassou 2.196 caracteres ou tweet ultrapassou 280 caracteres. | Enxugar o texto pelo número exato de caracteres informado pelo Shield antes de disparar. |
| Shield bloqueia com `Rule 09 Exactly-Once` | Criativo idêntico já foi disparado para este canal nas últimas 24 horas. | Não reenviar duplicata. Se o usuário requisitar expressamente um repost, usar `force_duplicate=True`. |
| Instagram retorna `requires at least one media` | Tentativa de postar apenas texto no Instagram sem passar `media_urls`. | Gerar o carrossel primeiro via `omnipress_build_carousel`, obter as URLs e repassar para `media_urls`. |
| PII detectado no texto | Presença de CNJ, CPF, CNPJ ou e-mail pessoal. | O agente deve manter `sanitize=True` (comportamento padrão) para que os dados sejam automaticamente mascarados antes da persistência. |
| Imagem de fundo não encontrada para carrossel | O caminho em `bg_image_path` não existe no disco. | Verificar o caminho com antecedência ou gerar uma imagem base limpa antes de chamar a renderização. |

---

## 6. Comandos de Manutenção e Testes Rápidos

```bash
# Executar toda a suíte de testes unitários em Python (50+ testes):
uv run pytest -v

# Executar checagem estática de tipos do Remotion (TypeScript):
npm run typecheck

# Iniciar o servidor MCP localmente em modo STDIO:
python src/server.py

# Iniciar o servidor MCP em modo HTTP/SSE ASGI (Porta 3333):
python src/server.py --http 3333
```

---

## 7. Padrão de Receitas Declarativas & Motores Universais (Regra 12 / v0.3.0)

### 7.1. Anti-Pattern: Criação de Scripts Descartáveis
É **terminantemente proibido** aos agentes criar scripts pontuais em Python (`render_carousel_*.py`, `upload_carousel_*.py`, `schedule_carousel_*.py`) para processar carrosséis, tratar áudios ou postar em redes sociais. Esse padrão causou proliferação descontrolada de 90+ scripts com chaves expostas e caminhos absolutos hardcoded.

### 7.2. O Novo Padrão Operacional: Receita Declarativa
Todo conteúdo deve ser estruturado em arquivos declarativos JSON/YAML dentro da pasta do criativo no canal (ex: `channels/<slug>/media/carousels/<post>/carousel_recipe.json`).

O agente executa o pipeline por meio dos **Motores Universais do Repositório**:

```bash
# Execução completa de Carrossel (preparo de fundos + render com cards + upload CDN + agendamento Buffer):
omnipress carousel --recipe channels/<slug>/media/carousels/<post>/carousel_recipe.json --all

# Masterização de Áudio Broadcast (-14 LUFS EBU R128, adeclick, denoise, 4-band EQ e compressor):
omnipress master-audio channels/<slug>/media/voiceover/raw_vox.m4a -o channels/<slug>/media/voiceover/master_vox.mp3

# Formatação e Chunking de Legendas Whisper para Remotion:
omnipress align-captions channels/<slug>/shorts/<id>/whisper.json -o channels/<slug>/shorts/<id>/captions.json

# Publicação ou Agendamento Seguro com PublishingShield:
omnipress publish --recipe channels/<slug>/articles/<id>/post_recipe.json

# Renderização de Assets 3D Fotorrealistas Headless (Blender 4.2+ LTS / Regra 12):
omnipress render-3d --template device_mockup --texture channels/<slug>/media/carousels/<post>/slide_01.png -o channels/<slug>/media/visuals/3d/hero_mockup.png
omnipress render-3d --template rotating_badge --material gold -o channels/<slug>/media/visuals/3d/badge_gold.png
omnipress render-3d --recipe channels/<slug>/media/visuals/3d/recipe_3d.json
```

### 7.3. Quando Scripts Customizados São Permitidos?
Scripts em `channels/<slug>/scripts/` continuam plenamente suportados e recomendados quando o criativo demandar:
1. Raspagem de dados específica de fontes externas do canal.
2. Animação experimental de canvas/gráficos que fuja do padrão do `CarouselBuilder`.
3. Processamento estatístico de dados jurídicos, fiscais ou científicos exclusivos daquela publicação.
Para todas as publicações e carrosséis padrão, utilize exclusivamente as receitas declarativas e os motores universais.

---

## 8. Padrão de Presets Visuais & Guia de Estilo (v0.4.0)

O OmniPress v0.4.0 introduz o suporte nativo a múltiplos presets de layout e instruções de estilo por canal:

### 8.1. Arquétipos de Canal (`personal_brand` vs. `media_channel`)
- **`personal_brand`**: Ideal para perfis pessoais de liderança técnica no LinkedIn, X, Instagram e artigos no Dev.to. Foco em velocidade editorial, posts sociais e carrosséis sem pipeline pesado de vídeo. Pasta de trabalho: `channels/<slug>/campanhas/`.
- **`media_channel`**: Ideal para canais de mídia, produtoras e projetos documentais (ex: Dossiê Histórico). Habilita pipelines de vídeo Remotion (16:9), shorts verticais (9:16) e masterização de locução (-14 LUFS). Pasta de trabalho: `channels/<slug>/episodios/`.

### 8.2. Os 4 Presets Visuais Nativos
1. **`tweet_card` (Thiago Ramos / Social Proof)**: Fundo claro ou escuro, cabeçalho de rede social com avatar circular, nome em negrito, selo azul de verificado, handle cinza, headline punchy e imagens arredondadas abaixo (1 foto ampla ou 2 fotos lado a lado).
2. **`minimal_dark` (Rhaj Teixeira / Dark Editorial)**: Fundo preto puro (`#08080A`), tipografia serifada de alto padrão (`DejaVuSerif`), numeração de etapas ("Passo 1."), espaçamento generoso e mockup de interface (ex.: barra de busca com lupa, texto e botão de fechar).
3. **`split_editorial` (Portal da Reforma Tributária / Autoridade Corporativa)**: Layout bipartido com foto real de contexto no topo (45%), container sólido em azul marinho corporativo (55%), foto do autor em recorte circular sobrepondo o corte, marcadores quadrados dourados (`■`) e marca d'água no rodapé.
4. **`classic_card` (Dossiê Histórico / Regra 08)**: Foto de arquivo em tela cheia com vinheta, selo superior em pílula, card protetor translúcido escuro (`rgba(8, 10, 14, 215)`) e contorno de segurança nas fontes.

### 8.3. Instruções de Estilo & Herança
- Antes de gerar qualquer criativo, o agente deve obrigatoriamente inspecionar o arquivo `channels/<slug>/style_guide.md` e o bloco `visual_identity` em `channels/<slug>/channel.json`.
- É possível sobrescrever o preset no nível da campanha (no topo do `carousel_recipe.json`) ou individualmente em cada lâmina (`"layout": "minimal_dark"`).

---

## 9. Padrão de Atualização Contínua de Documentação, SemVer e Release (Regra 13)

É **norma operacional estrita** que nenhum agente submeta código novo ou alterações estruturais sem cumprir o ciclo de release sincronizado:

1. **Versionamento Semântico (SemVer)**: Atualizar a versão em todos os 10 arquivos canônicos (`pyproject.toml`, `package.json`, `package-lock.json`, `server.json`, `plugin.json`, `src/__init__.py`, `src/cli.py`, `src/server.py`, `config/openapi.json`, `CHANGELOG.md`).
2. **Changelog**: Registrar a nova versão em `CHANGELOG.md` no formato Keep a Changelog.
3. **Documentação Viva**: Refletir imediatamente as novas ferramentas, comandos e presets em `README.md` e `docs/AGENT_MANUAL.md`.
4. **Testes Unitários & Integração**: Validar a execução completa com `pytest`.
5. **Commit & Push**: Commitar com mensagem descritiva no padrão Conventional Commits e disparar push para `origin main`.

---

## 10. OmniPress Content Factory — Esteira de 12 Agentes Especializados (v0.5.0)

A partir da versão v0.5.0, o OmniPress introduz a **Content Factory**: uma arquitetura agêntica modular composta por **12 subagentes especializados** orquestrados pelo Diretor Central (AG12). A fábrica opera em pipeline variável: conteúdos simples ativam poucos agentes, enquanto documentários e produções de cinema ativam a esteira completa.

### 10.1. Visão Geral dos 12 Agentes
| ID | Arquivo Canônico | Papel | Modos Ativos |
|---|---|---|---|
| **AG01** | `.agents/agents/01_researcher_scriptwriter.md` | Pesquisador de Acervos & Roteirista (roteiro dois-colunas) | Todos |
| **AG02** | `.agents/agents/02_image_curator.md` | Curador de Imagens por Cena & Prompter Visual | Standard, Full, Remix |
| **AG03** | `.agents/agents/03_audio_engineer.md` | Engenheiro de Áudio Broadcast (-14 LUFS, EBU R128) | Standard, Full |
| **AG04** | `.agents/agents/04_language_reviewer.md` | Revisor Linguístico & Guardião Editorial | Todos |
| **AG05** | `.agents/agents/05_timing_checker.md` | Checker de Timing (Legendas e Trocas de Cena ±0.5s) | Standard, Full |
| **AG06** | `.agents/agents/06_visual_verifier.md` | Auditor de Qualidade Visual & Contraste (Regra 08) | Standard, Full, Remix |
| **AG07** | `.agents/agents/07_vfx_remotion.md` | Especialista em Efeitos Especiais & Remotion Dinâmico | Full, Remix |
| **AG08** | `.agents/agents/08_sfx_designer.md` | Designer de Efeitos Sonoros Imersivos | Full, Remix |
| **AG09** | `.agents/agents/09_soundtrack_director.md` | Diretor de Trilha Sonora (Gate de Soberania do Usuário) | Full, Remix |
| **AG10** | `.agents/agents/10_narration_director.md` | Diretor de Narração (Dicção, Ritmo e Coerência de Roteiro) | Standard, Full |
| **AG11** | `.agents/agents/11_adversarial_auditor.md` | Auditor Adversarial Independente (Score 0-100, Anti-Duplicação) | Full, Standard |
| **AG12** | `.agents/agents/12_director_orchestrator.md` | Diretor Delegador (Orquestrador Único e Interface com Usuário) | **SEMPRE** |

### 10.2. Os 4 Modos Operacionais & Receitas Declarativas
As receitas em `.agents/recipes/` definem os grafos de dependência e agentes ativados:
1. **`express.json` (Express - ~5 min)**: AG12 → AG01 → Gate Usuário → AG04 → Entrega. Para microposts, threads no X e artigos Markdown.
2. **`standard.json` (Standard - ~20 min)**: AG12 → AG01 → Gate Usuário → AG02 + AG10 (paralelo) → AG03 → AG04 + AG05 (paralelo) → AG11 → Entrega. Para Shorts/Reels/TikTok de 62 a 68s com locução masterizada.
3. **`full_production.json` (Full Production - ~75 min)**: Todos os 12 agentes ativados com 2 gates obrigatórios do usuário (formato e trilha sonora). Para episódios documentais 16:9 de 10 a 30 minutos.
4. **`remix.json` (Remix - ~30 min)**: Reaproveita o áudio broadcast masterizado já existente, ativando AG02, AG06, AG07, AG08, AG09 e AG11 para modernização de assets visuais, sonoplastia e efeitos Remotion.

### 10.3. Schemas de Handoff Contratual
Os artefatos intermediários trocados entre agentes são rigidamente validados contra os schemas em `.agents/schemas/`:
- `roteiro.schema.json`: Contrato mestre de roteiro dois-colunas com timestamps, emoções e notas de produção.
- `recipe.schema.json`: Contrato de receitas declarativas para esteiras.
- `audit_report.schema.json`: Relatório de conformidade cega com bloqueadores e score.
- `production_log.schema.json`: Livro de registros de sessão e tempos operacionais mantido pelo AG12.



