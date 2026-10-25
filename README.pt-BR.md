# 🌐 OmniPress MCP

[🇺🇸 English](README.md) | [🇧🇷 Português](README.pt-BR.md) | [🤖 Manual para Agentes](docs/AGENT_MANUAL.md) | [🎬 Skills de Vídeo](docs/VIDEO_CREATION_AND_PLATFORM_SKILLS.md) | [🎞️ Referência Remotion](docs/REMOTION_SKILLS_AND_DOCS.md) | [📜 Changelog](CHANGELOG.md)

> **O Protocolo Universal de Publicação Agêntica e Motor de Distribuição Multi-Canal para Agentes de IA via Model Context Protocol (MCP)**

[![PyPI Version](https://img.shields.io/pypi/v/omnipress-mcp?color=blue)](https://pypi.org/project/omnipress-mcp/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/)
[![Node 20+](https://img.shields.io/badge/node-20+-green.svg)](https://nodejs.org/)
[![Padrão MCP](https://img.shields.io/badge/MCP-2.0%20%2F%20TDQS%205.0-orange.svg)](https://modelcontextprotocol.io/)
[![Compatível com Smithery](https://img.shields.io/badge/Smithery-Compat%C3%ADvel-blueviolet.svg)](https://smithery.ai)
[![Nativo Antigravity](https://img.shields.io/badge/Antigravity-Native-purple.svg)](https://deepmind.google/technologies/gemini/)

O **OmniPress MCP** é um protocolo aberto e agnóstico a nichos para publicação agêntica. Ele capacita agentes de IA (como Google Antigravity, Claude ou ChatGPT) a ingerir ideias brutas, repositórios de código, decisões judiciais/tributárias, memorandos de políticas públicas, fatos históricos ou dados de mercado, transformando-os em artigos completos de alta autoridade, carrosséis visuais para redes sociais, roteiros para canais dark e campanhas estruturadas multi-plataforma.

O OmniPress é projetado para ser **verdadeiramente "Omni"**:
- **Omni-Domínio**: Motor de ingestão universal expansível através de 31 skills modulares (tech, tributário/perícia, govtech, dark channels, documentários longos de YouTube e vídeos verticais virais).
- **Omni-Plataforma**: Distribuição nativa para Dev.to, Ghost CMS, LinkedIn, X (Twitter), Meta Threads, Instagram (Reels & Carrosséis), Reddit, Webhooks (n8n/Make) e arquivos Markdown locais.
- **Omni-Ambiente**: Servidor MCP unificado em Python (suportando STDIO e HTTP/SSE ASGI) + motor de vídeo programático em Remotion React (12 skills oficiais) + renderizador de carrosséis Pillow em conformidade com a Regra 08.
- **Omni-Canal (Multi-Tenant)**: Espaço de trabalho isolado por canal (`channels/<slug>/`), permitindo gerenciar múltiplos veículos, marcas e canais sem colisão de ativos.

---

## 🎯 Visão e Pipeline Agêntico

Especialistas, engenheiros de software, tributaristas, pesquisadores e criadores de conteúdo perdem horas adaptando manualmente seu conhecimento para formatos fragmentados em diferentes redes sociais.

O OmniPress resolve isso oferecendo um fluxo unificado de **Publicação Agêntica**:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          1. INGESTÃO UNIVERSAL                          │
│   Ideias Brutas • Diffs de Git • Decisões Tributárias • Relatórios TI  │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
┌────────────────────────────────────▼────────────────────────────────────┐
│                    2. RUNTIME DE SKILLS MODULARES                       │
│   Cada nicho possui uma Skill dedicada que define tom, estilo e jargão: │
│   ├── Engenharia de Software e TI     ├── Direito Tributário e Perícia  │
│   ├── Gestão Pública e GovTech        ├── Finanças, Cripto e Mercados   │
│   └── Canais Dark e Retenção Viral    └── Jornada de Founders / Produto │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
┌────────────────────────────────────▼────────────────────────────────────┐
│                  3. ESCUDO DE PRIVACIDADE E SEGREDOS                    │
│   Mascaramento automático de chaves de API, processos CNJ, CPFs e LGPD  │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
┌────────────────────────────────────▼────────────────────────────────────┐
│                  4. MOTOR DE RENDERIZAÇÃO & MÍDIA                       │
│   Carrosséis 3:4 com identidade da marca • Scripts de Vídeo e TTS       │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
┌────────────────────────────────────▼────────────────────────────────────┐
│                    5. SINCRONIZAÇÃO MULTI-CANAL                         │
│  ┌───────────────┐ ┌───────────────┐ ┌───────────────┐ ┌───────────────┐│
│  │   LinkedIn    │ │  X (Twitter)  │ │  Meta Threads │ │   Instagram   ││
│  │  (Autoridade) │ │   (Threads)   │ │ (Conversas)   │ │  (Carrosséis) ││
│  └───────┬───────┘ └───────┬───────┘ └───────┬───────┘ └───────┬───────┘│
│          │                 │                 │                 │        │
│          └───────────────┬─┴─────────────────┴─────────────────┘        │
│                          │                                              │
│             ┌────────────▼───────────┐    ┌────────────────────────┐    │
│             │ Reddit (r/subreddits)  │    │ Artigo Long-Form .md   │    │
│             │ Webhooks (n8n / Make)  │    │ (Substack/Jusbrasil)   │    │
│             └────────────────────────┘    └────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 🌟 Pilares Fundamentais

### 1. Arquitetura Multi-Canal Agnóstica (`channels/`)
O OmniPress suporta múltiplos canais independentes (ex.: canal de história militar, canal de engenharia de software, canal jurídico, canais dark virais) com isolamento rigoroso:

```
channels/
  ├── dossie-historico/          # Canal configurado ativo
  │   ├── channel.json           # Paleta de cores, tipografia, arroba, Buffer ID
  │   ├── articles/              # Artigos long-form organizados por YYYY/MM/
  │   ├── media/
  │   │   ├── raw/               # Ativos de referência e imagens brutas
  │   │   ├── carousels/         # Carrosséis renderizados em formato 3:4
  │   │   ├── stories/           # Lâminas verticais 9:16
  │   │   └── highlights/        # Capas de destaques do Instagram
  │   └── scripts/               # Scripts e pipelines específicos do canal
  └── _template/                 # Boilerplate para criação instantânea de canais
```

### 2. Motor de Carrosséis para Redes Sociais (`CarouselBuilder`)
Renderizador gráfico integrado em Python (Pillow) para carrosséis 3:4 (retrato otimizado para feeds modernos de Instagram e LinkedIn):
- **Quebra por pixel**: cálculo exato de largura tipográfica sem palavras truncadas.
- **Gradientes de leitura**: escurecimento inferior suave sobre qualquer imagem de fundo para contraste legível.
- **Injeção de marca**: cores de destaque primária da marca, badge superior, `@handle` social, contador de páginas (`01/06`) e indicação de swipe (`Deslize →`).

### 3. Escudo Universal de Privacidade e Segredos (LGPD & CNJ)
Antes de qualquer post ser enfileirado ou arquivado, o OmniPress executa uma varredura automática:
- **Segredos técnicos**: Mascara chaves de API, tokens JWT/Bearer e senhas de ambiente.
- **Dados Pessoais e Jurídicos**: Mascara processos judiciais no padrão CNJ (`0000000-00.0000.0.00.0000`), CPFs, CNPJs, e-mails e telefones.

### 4. Blindagem de Publicação & Idempotência Anti-Duplicação (Regra 09)
Garante **zero postagens duplicadas**, intercepta vazamentos de textos de teste e valida as restrições estritas de cada rede social antes de chamar qualquer API externa:
- **Portão 1 (Interceptor de Testes)**: Bloqueia textos de placeholder (`"teste"`, `"test"`, `<12 caracteres`) enviados ao vivo no modo `shareNow`.
- **Portão 2 (Exigência Mandatória de Mídia)**: Rejeita tentativas de postar apenas texto no feed do Instagram antes do disparo de rede.
- **Portão 3 (Limites Rígidos de Caracteres)**: Aplica cortes estritos (Instagram: 2.196 caracteres no GraphQL do Buffer, X: 280, Threads: 500, LinkedIn: 3.000) e reporta o excesso exato.
- **Portão 4 (Livro-Razão de Idempotência em 24h)**: Registra a impressão digital SHA-256 em `media/staging/publishing_ledger.json` e barra automaticamente qualquer republicação do mesmo criativo em 24 horas.
- **Portão 5 (Metadados Nativos e Exclusão Limpa)**: Injeta automaticamente `metadata.instagram.type = "post"` e `shouldShareToFeed = true`, eliminando agendamentos obsoletos via mutação GraphQL `delete_post`.

### 5. Motor de Vídeos Programáticos & Motion Design (Remotion)
Motor de vídeo de alta fidelidade em React & TypeScript (`src/video/`) projetado para Documentários no YouTube (16:9) e Shorts/Reels/TikTok (9:16):
- **Composições Universais**: Renderize vídeos finais MP4 em 1080p em segundos via `npm run remotion:render`.
- **Padrão de Duração Vertical para Monetização**: Duração padronizada de 62 a 68 segundos (alvo: ~65s / 1.950 frames a 30fps) para qualificação obrigatória no TikTok Creator Rewards Program (>60s sem risco de arredondamento para 59s), respeitando o teto de 180s do YouTube Shorts e 90s do Reels.
- **Legendas Dinâmicas Sincronizadas (Whisper)**: Destacamento palavra por palavra em ouro (`#FFD700`) via `SynchronizedCaptions.tsx` sobre card translúcido escuro protetor.
- **Componentes Cinemáticos**: Decodificador militar (`ScrambledText`), partículas de poeira 3D (`DustParticles`), flare anamórfico dourado (`AnamorphicFlare`), carimbo oficial (`ClassifiedStamp`), grade tática (`TacticalGrid`), grão de película (`FilmGrain`) e zoom suave Ken Burns (`KenBurnsImage`).
- **Paisagem Sonora em 48kHz Sincronizada**: Áudio estéreo broadcast integrado via `<Audio />` com ducking dinâmico automático (-18dB a -22dB durante a voz).
- **Gerador Programático de Miniaturas (Thumbnails)**: Criação de capas 16:9 de alto CTR via código React (`ThumbnailEpisode.tsx`).

### 6. Publicação Multi-Canal & Integração Direta com YouTube
- **Integração Nativa com YouTube**: Conexão direta com canais do YouTube através do Buffer (`buffer_channel_id` configurado em `channel.json`).
- **Escalabilidade Multi-Marcas**: Expansão instantânea para múltiplos nichos (História, Geopolítica, Engenharia de Software, Direito Tributário e Gestão Pública) sem duplicar código.

### 7. OmniPress Content Factory — 12 Subagentes Especializados e Modos de Produção (v0.5.0)
Esteira modular de geração de conteúdo orquestrada pelo Diretor Central (AG12), operando em 4 modos de execução baseados em receitas declarativas:
- **`Express` (~5 min)**: Publicação ágil (AG12 → AG01 → Gate Usuário → AG04). Indicado para artigos Markdown, posts de autoridade no LinkedIn e threads conectadas no X.
- **`Standard` (~20 min)**: Vídeos verticais de alta retenção (Shorts / Reels / TikTok de 62 a 68s). Ativa pesquisa, curadoria de imagens sincronizadas (AG02), masterização broadcast de áudio (-14 LUFS, AG03), auditoria de narração (AG10), timing fala-imagem (AG05) e revisão editorial (AG04).
- **`Full Production` (~75 min)**: Produção audiovisual completa 16:9 em Remotion com todos os 12 subagentes: efeitos visuais (AG07), sonoplastia imersiva (AG08), curadoria musical com soberania do usuário (AG09) e auditoria adversarial independente (AG11).
- **`Remix` (~30 min)**: Modernização visual e acústica reaproveitando a locução pré-masterizada para atualizar B-roll, efeitos sonoros e transições.
- **Contratos de Handoff Rigorosos**: Schemas padronizados (`.agents/schemas/`) garantem integração fluida entre agentes (`roteiro.json`, `image_manifest.json`, `timing_report.json`, `audit_report.json`, `production_log.json`).

### 8. Motor Universal de Assets 3D & Mockups (Blender Headless / v0.6.0)
Geração declarativa de ativos 3D fotorrealistas isolados com canal alfa transparente (PNG/WebM) via Blender 4.2+ LTS headless:
- **Mockups de Dispositivos Dinâmicos**: Smartphone moderno em perspectiva com chassi chanfrado em titânio escuro e mapeamento dinâmico de textura de tela UV para carrosséis e artigos (`device_mockup.py`).
- **Medalhões e Moedas Metálicas Giratórias**: Medalhões 3D chanfrados com acabamentos metálicos (`gold`, `silver`, `chrome`, `obsidian`, `bronze`) e emblema frontal opcional (`rotating_badge.py`).
- **Tipografia Cinética 3D**: Títulos 3D extrudados e chanfrados com iluminação de estúdio e reflexos especulares (`kinetic_title.py`).
- **Bandeiras de Seda Ondulantes**: Simulação fotorrealista de bandeiras 3D em tecido de seda/cetim com deslocamento harmônico de ondas e mastro dourado polido (`brazil_flag.py`).
- **Controle via CLI e MCP**: Renderize diretamente via `omnipress render-3d` ou através da ferramenta MCP canônica `omnipress_render_3d`.

---

## 🚀 Guia Passo a Passo de Uso (Hands-on)

Abaixo está o roteiro prático para configurar, conectar e operar o OmniPress do zero ao seu primeiro post publicado.

### Passo 1: Início Rápido e Instalação

#### Opção A: Execução Zero-Clone via `uvx` (Recomendada)
Você pode executar o servidor MCP diretamente sem clonar o repositório nem criar ambientes virtuais:

```bash
# Executa o servidor MCP diretamente
uvx omnipress-mcp

# Executa o diagnóstico do ambiente
uvx --from omnipress-mcp omnipress doctor
```

#### Opção B: Instalação em 1-Clique via Smithery
Para Claude Desktop ou Cursor, instale automaticamente via Smithery:
```bash
npx -y @smithery/cli install omnipress-mcp --client claude
```

#### Opção C: Clonagem Local do Repositório para Desenvolvimento
```bash
# 1. Clonar o repositório
git clone https://github.com/ismaelsoilet/omnipress-mcp.git
cd omnipress-mcp

# 2. Instalar dependências com uv
uv sync

# 3. Executar a suíte de testes completa (131 testes):
uv run pytest -v     # Suíte de testes em Python
npm run typecheck    # Validação de tipos do Remotion
```

---

### Passo 2: Configuração das Credenciais (`.env`)

Você pode configurar o OmniPress de forma interativa via terminal ou editando o arquivo `.env`:

```bash
# Assistente interativo de configuração:
omnipress setup

# Diagnóstico de prontidão do sistema:
omnipress doctor

# Sincronização automática de perfis conectados do Buffer no channel.json:
omnipress sync-buffer [channel-slug]
```

#### Isolamento de Credenciais Multi-Canal (Regra 04)
O OmniPress suporta isolamento completo de credenciais entre canais:
- **`.env` na raiz**: Configura o canal principal padrão (**Dossiê Histórico** via `OMNIPRESS_ACTIVE_CHANNEL=dossie-historico`).
- **`channels/<slug>/.env`**: Canais individuais (como `channels/ismael-soilet/.env`) mantêm suas próprias chaves de API e perfis, totalmente desacoplados de outras marcas.
- **Ordem de Precedência**: `channels/<slug>/.env` → `<SLUG>_BUFFER_API_KEY` → `.env` da raiz.

> 💡 **Nota**: O OmniPress funciona perfeitamente **mesmo sem nenhuma chave externa**. Se nenhuma API for configurada, os artigos são arquivados localmente em Markdown e os textos das redes sociais são exibidos na tela prontos para você copiar e colar.

Principais integrações disponíveis:
1. **Artigos Técnicos e Engenharia (Dev.to)**:
   - Obtenha sua chave em: [dev.to/settings/extensions](https://dev.to/settings/extensions).
   - Configure `DEVTO_API_KEY`.
2. **Publicações Independentes e Newsletters (Ghost CMS)**:
   - Crie uma integração em Ghost Admin (`Settings -> Integrations`).
   - Configure `GHOST_API_URL` (ex: `https://meublog.ghost.io`) e `GHOST_ADMIN_API_KEY` (`{id}:{secret}`).
3. **Agendamento Multi-Redes (Buffer - LinkedIn, X, Threads, Instagram)**:
   - Obtenha seu token em: [publish.buffer.com/settings/api](https://publish.buffer.com/settings/api).
   - Configure `BUFFER_API_KEY` e os IDs de perfis (`BUFFER_LINKEDIN_PROFILE_ID`, `BUFFER_X_PROFILE_ID`, etc.).
4. **Instagram Graph API (Direto)**:
   - Configure `INSTAGRAM_ACCESS_TOKEN` e `INSTAGRAM_ACCOUNT_ID` para postagens diretas.
5. **Reddit (Publicação direta em subreddits)**:
   - Crie um aplicativo tipo "script" em: [reddit.com/prefs/apps](https://www.reddit.com/prefs/apps).
   - Configure `REDDIT_CLIENT_ID`, `REDDIT_CLIENT_SECRET`, `REDDIT_USERNAME` e `REDDIT_PASSWORD`.
6. **Webhooks (n8n / Make / Slack / Telegram)**:
   - Configure `OMNIPRESS_WEBHOOK_URL` para receber o payload JSON completo de cada postagem gerada.

---

### Passo 3: Conectar ao Agente de IA

#### No Google Antigravity (Recomendado)
Adicione o servidor no seu arquivo `~/.gemini/config/mcp_config.json` (ou no `mcp_config.json` da raiz do projeto):

```json
{
  "mcpServers": {
    "omnipress": {
      "command": "/caminho/ate/omnipress-mcp/.venv/bin/python",
      "args": ["-m", "src.server"],
      "env": {
        "OMNIPRESS_ACTIVE_CHANNEL": "dossie-historico"
      }
    }
  }
}
```

#### No Claude Desktop
No seu arquivo `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "omnipress": {
      "command": "python",
      "args": ["/caminho/ate/omnipress-mcp/src/server.py"],
      "env": {
        "ARTICLES_DIR": "/caminho/ate/omnipress-mcp/articles"
      }
    }
  }
}
```

---

### Passo 4: Gerenciando Canais (CLI ou MCP)

Você pode gerenciar canais de conteúdo diretamente pelo terminal ou pedindo ao agente.

#### Via Terminal (CLI):
```bash
# Listar canais existentes
python src/cli.py list-channels

# Criar um novo canal para tecnologia
python src/cli.py create-channel tech-insights \
  --name "Tech Insights" \
  --handle "@techinsights.dev" \
  --category "technology" \
  --color "#00E5FF"

# Ver detalhes e identidade visual de um canal
python src/cli.py info-channel tech-insights
```

#### Via Prompt do Agente:
> *"OmniPress: Liste todos os canais configurados e me mostre qual é o canal ativo."*

---

### Passo 5: Fluxos de Publicação na Prática

#### Fluxo A: Escrever e Arquivar Artigo Completo
Ao instruir o agente a criar um artigo longo:
1. O agente estrutura o conteúdo em Markdown.
2. Adiciona frontmatter YAML completo (`title`, `date`, `category`, `tags`, `author`, `status: draft`).
3. Executa a varredura contra vazamentos de dados (LGPD/CNJ).
4. Aciona a ferramenta `omnipress_publish_article`, gravando o arquivo em `channels/<slug>/articles/AAAA/MM/titulo-do-artigo.md`.

#### Fluxo B: Criar Carrossel Visual para o Instagram (3:4)
1. Crie ou baixe imagens de fundo em `channels/<slug>/media/raw/`.
2. Estruture o conteúdo das lâminas em um arquivo JSON (ou peça para a IA gerar):

```json
[
  {
    "bg_image": "channels/tech-insights/media/raw/bg_slide1.jpg",
    "headline": "A Morte dos Monólitos?",
    "body": "Por que sistemas distribuídos mal projetados custam 10x mais caro.",
    "page_str": "01/05"
  },
  {
    "bg_image": "channels/tech-insights/media/raw/bg_slide2.jpg",
    "headline": "O Paradoxo da Latência",
    "body": "Cada salto de rede entre microserviços adiciona overhead acumulado.",
    "page_str": "02/05"
  }
]
```

3. Renderize via CLI ou MCP:
```bash
python src/cli.py build-carousel \
  --channel tech-insights \
  --post morte-dos-monolitos \
  --config slides.json \
  --aspect-ratio 3:4
```
As lâminas finais serão geradas com badges, arroba, contrastes e fontes formatadas em:
`channels/tech-insights/media/carousels/morte-dos-monolitos/slide_01.jpg`.

#### Fluxo C: Disparar Posts Multi-Canal
O agente utiliza `omnipress_queue_post` especificando as plataformas:
- `platforms: ["linkedin", "twitter", "threads", "reddit:webdev"]`
- O texto é higienizado e enviado para os rascunhos de cada serviço conectado.

#### Fluxo D: Gerar Roteiros para Canais Dark (YouTube Shorts / Reels)
Use a ferramenta `omnipress_prepare_dark_script`:
- Gera gancho magnético nos primeiros 3 segundos.
- Divide o roteiro cena a cena com prompts detalhados para geradores de imagem com IA.
- Especifica instruções de locução TTS e metadados de SEO (tags, descrição, título viral).

#### Fluxo E: Renderizar Vídeos e Vinhetas Programáticas com Remotion
1. Abra o estúdio interativo com timeline ao vivo no navegador:
```bash
npm run remotion:preview
```
2. Renderize as vinhetas oficiais em 1080p (4.0s) com áudio cinemático embutido:
```bash
# Versão 16:9 Horizontal para Episódios no YouTube
npm run remotion:render:intro

# Versão 9:16 Vertical para YouTube Shorts, Reels e TikTok
npm run remotion:render:intro:shorts
```
Os arquivos finais são salvos em `media/output/intro_dossie_16x9.mp4` e `media/output/intro_dossie_9x16.mp4`.

#### Fluxo F: Narração com Voz Humana + Sincronização Dinâmica
1. Peça ao OmniPress para gerar o roteiro de teleprompter dividido por blocos de cena (`Cena 01`, `Cena 02`...).
2. Grave sua voz por cena no celular ou microfone (`01.mp3`, `02.mp3`...).
3. O Remotion calcula a duração real da sua fala dinamicamente, sincronizando os cortes visuais no seu ritmo natural com atenuação automática de trilha musical (ducking a -20dB sob a voz).

#### Fluxo G: Renderização 3D Headless com Blender (Regra 12)
Renderiza mockups 3D fotorrealistas (smartphones), medalhões metálicos giratórios e tipografia 3D cinética com fundo transparente para carrosséis e camadas de vídeo Remotion:
```bash
# Mockup 3D de Smartphone com Screenshot de Artigo/Carrossel
omnipress render-3d --template device_mockup --texture channels/tech-insights/media/carousels/slide_01.png -o channels/tech-insights/media/visuals/3d/hero_mockup.png

# Medalhão / Moeda 3D Metálica
omnipress render-3d --template rotating_badge --material gold -o channels/tech-insights/media/visuals/3d/badge_gold.png

# Tipografia Cinética 3D
omnipress render-3d --template kinetic_title --text "OMNIPRESS 3D" --material chrome -o channels/tech-insights/media/visuals/3d/title_chrome.png

# Via Arquivo de Receita 3D Declarativa
omnipress render-3d --recipe recipe_3d.json
```

---

### Passo 6: Galeria de Prompts Prontos para Uso

Copie e cole diretamente no chat do seu agente de IA:

#### 1. Campanha Tri-Formato de Tecnologia
```text
OmniPress: Analise o arquivo src/core/channel_manager.py e crie uma publicação completa:
1. Um artigo aprofundado para o blog explicando os trade-offs de multi-tenancy local.
2. Um post de autoridade para o LinkedIn com os aprendizados principais.
3. Uma thread de 4 posts para o X (Twitter).
Arquive o artigo e coloque os posts na fila de rascunhos para o canal ativo.
```

#### 2. Análise Tributária com Proteção LGPD
```text
OmniPress: Redija um memorando sobre a incidência de ISS vs IBS no licenciamento de software com base nas decisões recentes.
Certifique-se de que nenhum número de processo real ou dado de cliente permaneça no texto e enfileire o resumo para o Reddit r/direito e para o LinkedIn.
```

#### 3. Produção de Roteiro Dark Viral
```text
OmniPress: Crie um roteiro completo de 50 segundos para um Short no YouTube sobre 'A Batalha do Castelo Itter: O Dia em que Americanos e Alemães Lutaram Juntos'.
Inclua prompts para Midjourney para cada cena e as especificações de locução em tom sombrio e cinematográfico.
```

---

## 🛠️ Ferramentas MCP Disponíveis

| Ferramenta | Finalidade | Principais Argumentos |
| :--- | :--- | :--- |
| `omnipress_list_channels` | Lista todos os canais de conteúdo configurados e indica o canal ativo. | `include_templates` (bool) |
| `omnipress_get_channel` | Retorna as configurações completas de identidade visual, paleta e credenciais de um canal. | `channel_slug` (string) |
| `omnipress_create_channel` | Cria um novo canal isolado com pastas de artigos, mídias e configuração `channel.json`. | `slug`, `name`, `handle`, `category`, `primary_color` |
| `omnipress_build_carousel` | Renderiza lâminas de carrossel 3:4 com layout perfeito, quebra dinâmica e branding do canal. | `channel_slug`, `post_slug`, `slides_json`, `aspect_ratio` |
| `omnipress_publish_article` | Salva artigo em Markdown ou publica no Dev.to e Ghost CMS com idempotência do PublishingShield. | `title`, `content_markdown`, `category`, `tags`, `author`, `channel_slug`, `target_platform`, `canonical_url`, `published`, `force_duplicate`, `sanitize` |
| `omnipress_queue_post` | Envia post/thread de texto protegido pelo PublishingShield e livro-razão anti-duplicação. | `text`, `platforms`, `title`, `media_urls`, `schedule_time`, `channel_slug`, `mode`, `allow_test`, `force_duplicate` |
| `omnipress_queue_media_post` | Enfileira mídias ricas (Carrosséis Instagram, Shorts YouTube, posts com mídia no X) com PublishingShield. | `caption`, `platforms`, `media_urls`, `title`, `media_type`, `schedule_time`, `channel_slug`, `mode`, `allow_test`, `force_duplicate` |
| `omnipress_prepare_dark_script` | Gera roteiro dark viral de alta retenção, prompts de imagens para IA e especificações TTS. | `topic`, `format`, `tone`, `target_audience` |
| `omnipress_brainstorm_channel` | Cria conceitos de canal de alto CTR, pilares editoriais e backlog de tópicos virais com ganchos. | `niche`, `tone`, `target_audience`, `language` |
| `omnipress_generate_speech` | Sintetiza locução neural de alta definição (Edge-TTS) para Canais Dark, Reels e Shorts. | `text`, `voice`, `output_filename` |
| `omnipress_render_dark_video` | Renderiza vídeo MP4 (9:16 ou 16:9) unindo áudio neural e imagens de cenas via ffmpeg. | `text`, `audio_path`, `image_paths`, `output_filename`, `aspect_ratio`, `voice` |
| `omnipress_render_3d` | Renderiza ativos visuais 3D fotorrealistas com fundo transparente via Blender 4.2+ LTS headless. | `template`, `output_filename`, `texture_path`, `text`, `material`, `channel_slug`, `resolution`, `engine`, `samples` |
| `omnipress_inspect_content` | Utilitário isolado para auditar texto em busca de vazamentos de chaves, processos CNJ e CPFs. | `text` (string) |
| `omnipress_list_articles` | Lista os artigos arquivados recentemente no repositório ou por canal. | `limit` (int), `channel_slug` (string) |
| `omnipress_list_recent` | Alias retrocompatível para `omnipress_list_articles`. | `limit` (int) |

---

## 📚 Documentação e Recursos

- **[GitHub Wiki Oficial](https://github.com/ismaelsoilet/omnipress-mcp/wiki)**: Documentação aprofundada de arquitetura e runbooks.
- **[Guia de Configuração de Contas (docs/SETUP_GUIDE.pt-BR.md)](docs/SETUP_GUIDE.pt-BR.md)**: Passo a passo para obter tokens de Buffer, Instagram e Reddit.
- **[Diretrizes para Agentes de IA (AGENTS.md)](AGENTS.md)**: Regras de arquitetura e padrões TDQS para desenvolvedores e IAs.
- **[Guia de Criação de Skills de Nicho](https://github.com/ismaelsoilet/omnipress-mcp/wiki/Creating-Niche-Skills)**: Como customizar tom e formatação para novas áreas.

---

## 📄 Licença

Distribuído sob a licença [MIT](LICENSE).
