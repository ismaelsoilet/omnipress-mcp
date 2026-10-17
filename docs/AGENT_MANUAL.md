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

### 2.14. Suíte CLI de Diagnóstico e Onboarding (`omnipress`)
Para inspeção e configuração interativa fora do contexto de chat do MCP, utilize o comando CLI `omnipress`:

```bash
# Diagnóstico completo de runtimes (Python, Node.js, FFmpeg, Edge-TTS):
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
3. **Legendas Dinâmicas Sincronizadas (Whisper)**:
   - Utilize [`SynchronizedCaptions`](../src/video/components/SynchronizedCaptions.tsx) com transcrição palavra por palavra alimentada por timestamps JSON do Whisper. As palavras ativas recebem destaque em ouro (`#FFD700`) e animação de escala (`1.08x`), encapsuladas em card protetor escuro (`rgba(8, 10, 14, 0.90)`).
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
8. **Uso das 12 Agent Skills Oficiais do Remotion**:
   - O projeto conta com as 12 skills oficiais instaladas em [`.agents/skills/remotion-*`](../.agents/skills/) e documentadas em [`REMOTION_SKILLS_AND_DOCS.md`](./REMOTION_SKILLS_AND_DOCS.md).
   - Para animações, utilize sempre `interpolate()` e `spring()` (nunca transições CSS/Tailwind).
   - Para pré-visualização em tempo real: `npm run remotion:preview`.
   - Para buscar documentação oficial: consulte o endpoint Algolia ou utilize URLs `.md` (ex.: `https://www.remotion.dev/docs/interpolate.md`).
   - Para atualizar as skills: `npx remotion skills update`.

---

### Playbook 4: Isolamento Multi-Canal e Arquitetura de Pastas (Regra 04)
Quando gerenciar múltiplos canais ou marcas:

- **Isolamento Completo**:
  ```
  channels/<slug>/
    ├── channel.json         # Configuração exclusiva da marca
    ├── articles/            # Artigos em AAAA/MM/
    ├── media/
    │   ├── raw/             # Imagens e fontes brutas
    │   ├── carousels/       # Lâminas geradas pelo Pillow
    │   ├── stories/         # Formatos 9:16
    │   └── highlights/      # Capas de destaque
    └── scripts/             # Scripts específicos do canal
  ```
- **Fallback Standalone**: Se uma ferramenta for chamada sem `channel_slug`, ela salvará em `articles/` e `media/` na raiz do repositório, garantindo compatibilidade reversa.

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
