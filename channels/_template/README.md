# Workspace Template de Canal — OmniPress MCP

Este diretório define a estrutura canônica e universal para **qualquer canal de mídia, marca editorial ou perfil pessoal** no **OmniPress MCP**.

---

## 🧭 O que é um "Channel" no OmniPress?

No OmniPress, um **Channel não é apenas um canal do YouTube**.  
Um **Channel é o hub de intermediação e a persona editorial de uma marca ou indivíduo**, servindo como o intermediário oficial para criação, automação e distribuição de conteúdo.

Um canal pode ser utilizado para:
1. **Perfis Pessoais & Liderança Técnica** (ex.: `channels/ismael-soilet/`): Focado em posts no LinkedIn, threads no X, carrosséis de alto impacto no Instagram e artigos técnicos no Dev.to / Ghost / Substack. Não necessita de esteira de vídeos ou documentários.
2. **Canais Temáticos de Mídia & Documentários** (ex.: `channels/dossie-historico/`): Focado em documentários 16:9, shorts 9:16, locução masterizada em estúdio (-14 LUFS), recortes de arquivo e carrosséis.
3. **Canais Nichados de Especialistas** (ex.: GovTech, Direito Tributário, Finanças): Artigos profundos, carrosséis com dados e análises em threads.

---

## 📁 Estrutura Canônica de Diretórios (Multi-Arquétipo)

A estrutura suporta de forma modular tanto o fluxo leve de **Campanhas Sociais** quanto o fluxo pesado de **Episódios Audiovisuais**:

```
channels/<channel-slug>/
├── channel.json                     # Metadados, arquétipo, branding, cores, redes sociais e módulos ativos
├── README.md                        # Manifesto editorial, diretrizes de tom e checklist do canal
│
├── campanhas/                       # [ARQUÉTIPO: PERSONAL_BRAND / SOCIAL-FIRST]
│   └── <nome_da_campanha>/          # Workspace de postagens cotidianas, insights e lançamentos
│       ├── README.md                # Objetivos e checklist de distribuição da campanha
│       ├── artigo.md                # Artigo completo em Markdown (Dev.to / Ghost / Substack / Medium)
│       ├── carousel_recipe.json     # Receita declarativa para compilar carrossel 3:4 ou 4:5 via Pillow
│       ├── posts/                   # Textos adaptados para cada rede social
│       │   ├── linkedin_post.md     # Post formatado com gancho, bullets e debate
│       │   ├── x_thread.md          # Sequência de micro-posts conectada (280 chars)
│       │   └── instagram_copy.md    # Legenda estruturada com quebras de linha
│       └── midias/                  # Diagramas, fotos, prints de código e infográficos
│
├── episodios/                       # [ARQUÉTIPO: MEDIA_HOUSE / CANAL DE VÍDEO]
│   └── <slug_episodio>/             # Workspace autocontido de episódios longos e shorts
│       ├── README.md                # Sinopse, ganchos CTR, fontes desclassificadas e status
│       ├── documentario/            # Formato Widescreen 16:9 (YouTube Principal, 11 a 14 min)
│       │   ├── roteiros/            # Roteiro 16:9, teleprompter (110 WPM) e plano de B-Roll
│       │   ├── audios/              # Locução bruta (raw/) e masterizada (-14 LUFS)
│       │   ├── midias/              # Cenas 16:9, recortes de arquivo e thumbnails mobile-first
│       │   └── outputs/             # Vídeos finais renderizados (.mp4)
│       ├── shorts/                  # Formato Vertical 9:16 (Shorts / Reels / TikTok, ~65s)
│       │   ├── short_01/            # Short principal com indicação de "Vídeo Relacionado"
│       │   └── short_02/            # Segundo corte ou revelação secundária
│       ├── carrossel/               # Lâminas visuais 3:4 / 4:5 com cartões de contraste (Regra 08)
│       ├── artigos/                 # Artigo longo de pesquisa histórica
│       ├── midias/                  # Acervo compartilhado do episódio (fotos reais, documentos originais)
│       └── posts/                   # Copys para YouTube (com capítulos e fontes), Shorts e redes
│
├── recursos_globais/                # Ativos compartilhados e utilitários da marca
│   ├── branding/                    # Banner e avatar oficial do canal
│   ├── vinhetas/                    # Vinhetas oficiais 16:9 e 9:16 (quando canal de vídeo)
│   ├── trilhas_sonoras/             # Acervo de trilhas sonoras autorizadas
│   └── utilitarios/                 # Scripts auxiliares e ferramentas de conversão
│
└── scripts/                         # Automações e utilitários exclusivos do canal
    └── example_runner.py            # Exemplo de pipeline programático do canal
```

---

## 🎨 Os 4 Tipos de Mídias Geradas pelo OmniPress MCP

O motor do OmniPress já possui geradores universais e independentes para todas as mídias:

| Tipo de Mídia | Motores Responsáveis | Formato / Destino | Onde Vive no Canal |
|---|---|---|---|
| **1. Artigos Long-Form** | `DevToPublisherAdapter`, `GhostPublisherAdapter` | Markdown + YAML Frontmatter | `campanhas/*/artigo.md` ou `episodios/*/artigos/` |
| **2. Carrosséis Visuais** | `UniversalCarouselEngine`, `CarouselBuilder` (Pillow) | JPG 3:4 (`1080x1440`) ou 4:5 (`1080x1350`) com cards de contraste (Regra 08) | `campanhas/*/carousel_recipe.json` ou `episodios/*/carrossel/` |
| **3. Micro-Posts & Threads** | `UniversalPublisherEngine`, `BufferPublisherAdapter`, `PublishingShield` | Textos validados para LinkedIn (3.000 chars), X (280 chars), IG (2.196 chars) | `campanhas/*/posts/` ou `episodios/*/posts/` |
| **4. Vídeos Programáticos** | Remotion (`DocumentaryEpisode-16x9`, `DocumentaryShort-9x16`), EBU R128 (-14 LUFS) | MP4 16:9 (1920x1080) e 9:16 (1080x1920) | `episodios/*/documentario/` e `episodios/*/shorts/` |

---

## 🚀 Como Criar um Novo Canal

### Método 1: Para Perfil Pessoal / Social-First (`personal_brand`)
1. Crie a pasta do canal a partir do template:
   ```bash
   cp -r channels/_template channels/meu-perfil
   ```
2. No `channels/meu-perfil/channel.json`, ajuste:
   - `"archetype": "personal_brand"`
   - `"features": { "articles": true, "carousels": true, "social_posts": true, "video": false }`
   - Preencha seus handles e Buffer IDs de LinkedIn, X e Instagram.
3. Crie suas publicações duplicando `campanhas/_template_campanha/` para `campanhas/<nome-do-post>/`.

### Método 2: Para Canal de Mídia / Vídeo (`media_channel`)
1. Crie a pasta do canal:
   ```bash
   cp -r channels/_template channels/meu-canal-video
   ```
2. No `channel.json`, configure:
   - `"archetype": "media_channel"`
   - `"features": { "video": true }`
   - Preencha os canais de YouTube, Instagram, TikTok e remotion.
3. Produza seus dossiês duplicando `episodios/_template_episodio/` para `episodios/ep01_<slug>/`.

### Método 3: Via CLI OmniPress
```bash
omnipress create-channel meu-perfil --name "Meu Nome" --category "tecnologia"
```
