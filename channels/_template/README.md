# Workspace Template de Canal — OmniPress MCP

Este diretório define a estrutura canônica e universal para qualquer canal de mídia, marca ou publicação no **OmniPress MCP**.

Toda produção de conteúdo (artigos, carrosséis, vídeos longos, shorts, locuções e roteiros) de um canal deve residir **exclusivamente** dentro de `channels/<channel-slug>/`. O motor do OmniPress (`src/`) permanece agnóstico, reutilizável e desacoplado.

---

## 📁 Estrutura Canônica de Diretórios (Arquitetura Episódica Unificada)

```
channels/<channel-slug>/
├── channel.json                     # Metadados, branding, cores, tipografia, redes sociais e configurações de vídeo
├── README.md                        # Manifesto editorial, diretrizes de tom e checklist do canal
│
├── episodios/                       # Dossiês e episódios autocontidos (unifica todos os formatos)
│   └── <slug_episodio>/             # Workspace completo do episódio
│       ├── README.md                # Sinopse, ganchos CTR, fontes desclassificadas e status dos entregáveis
│       ├── documentario/            # Formato Widescreen 16:9 (YouTube Principal, 11 a 14 min)
│       │   ├── roteiros/            # Roteiro 16:9, teleprompter calibrado e plano de B-Roll
│       │   ├── audios/              # Locução bruta (raw/) e masterizada (-14 LUFS)
│       │   ├── midias/              # Cenas 16:9, recortes de arquivo e thumbnails de alto CTR
│       │   ├── outputs/             # Vídeo final renderizado (.mp4)
│       │   └── scripts/             # Scripts dedicados de montagem ou alinhamento Whisper
│       ├── shorts/                  # Formato Vertical 9:16 (Shorts / Reels / TikTok, ~65s)
│       │   ├── short_01/            # Short principal com indicação de "Vídeo Relacionado"
│       │   └── short_02/            # Segundo corte ou ângulo investigativo alternativo
│       ├── carrossel/               # Formato 3:4 / 4:5 (Instagram / LinkedIn)
│       │   ├── carousel_recipe.json # Receita declarativa de lâminas com cards de contraste (Regra 08)
│       │   ├── slides/              # Lâminas renderizadas em alta resolução
│       │   └── midias/              # Elementos visuais e catbox_urls.json
│       ├── artigos/                 # Artigo longo de pesquisa com YAML frontmatter (Substack / Jusbrasil / Medium)
│       ├── midias/                  # Acervo compartilhado do episódio (fotos reais, documentos históricos originais)
│       └── posts/                   # Textos prontos para distribuição
│           ├── youtube_description.md # Título CTR, capítulos cronometrados e links de fontes
│           ├── shorts_copy.md       # Legenda otimizada apontando para o vídeo longo
│           └── social_copy.md       # Copys para Instagram, LinkedIn e Thread do X
│
├── recursos_globais/                # Ativos compartilhados e utilitários da marca
│   ├── branding/                    # Banner e avatar oficial do canal
│   ├── vinhetas/                    # Vinhetas oficiais 16:9 e 9:16 com áudio broadcast
│   ├── trilhas_sonoras/             # Acervo de trilhas sonoras autorizadas
│   └── utilitarios/                 # Scripts auxiliares e ferramentas de conversão
│
└── scripts/                         # Automações e utilitários exclusivos do canal
    └── example_runner.py            # Exemplo de pipeline programático do canal
```

---

## 🚀 Como Criar um Novo Canal

### Método 1: Via Linha de Comando (CLI)
```bash
omnipress create-channel meu-novo-canal --name "Meu Novo Canal" --category "tecnologia"
```

### Método 2: Manualmente via Template
1. Duplique esta pasta `_template` para o slug desejado:
   ```bash
   cp -r channels/_template channels/meu-novo-canal
   ```
2. Abra `channels/meu-novo-canal/channel.json` e configure:
   - `id` e `slug`: identificador seguro (sem espaços ou acentos, em minúsculas).
   - `name`: Nome público do canal.
   - `branding`: Cores primárias, secundárias e caminhos de fontes TTF.
   - `social`: Handles e `buffer_channel_id` das redes sociais.
   - `video`: Títulos e badges padrão para renderização no Remotion.

3. Defina o canal ativo no seu arquivo `.env`:
   ```bash
   OMNIPRESS_ACTIVE_CHANNEL=meu-novo-canal
   ```

---

## 🎬 Integração com o Motor de Vídeo Remotion

O OmniPress possui componentes universais de vídeo sob `src/video/` (`ChannelIntro`, `DocumentaryEpisode`, `DocumentaryShort`, `ThumbnailEpisode`). Para renderizar vídeos do seu canal sem acoplar código no repositório:

### 1. Renderizando Shorts / Reels / TikTok (9:16)
```bash
npm run remotion:render -- DocumentaryShort-9x16 channels/meu-novo-canal/media/output/short_01.mp4 \
  --props='{
    "title": "Título do Short",
    "badge": "CURIOSIDADE // HISTÓRIA",
    "voiceoverSrc": "meu-novo-canal/media/voiceover/short_01_vox.mp3",
    "musicSrc": "meu-novo-canal/media/soundtrack/trilha_01.mp3",
    "musicVolume": 0.15,
    "scenes": [
      { "id": "sc1", "type": "ken-burns", "mediaSrc": "meu-novo-canal/media/visuals/cena1.jpg", "durationInSeconds": 5.0 }
    ]
  }'
```

### 2. Renderizando Episódios Documentais (16:9)
```bash
npm run remotion:render -- DocumentaryEpisode-16x9 channels/meu-novo-canal/media/output/ep01.mp4 \
  --props='{
    "config": {
      "id": "ep01",
      "title": "Título do Episódio",
      "channelSlug": "meu-novo-canal",
      "introProps": {
        "channelName": "MEU NOVO CANAL",
        "primaryColor": "#3B82F6"
      },
      "scenes": []
    }
  }'
```

---

## 📜 Padrão de Receitas Declarativas & Motores Universais (v0.3.0)

Para evitar scripts descartáveis duplicados (`render_*.py`, `upload_*.py`, `schedule_*.py`), o OmniPress MCP utiliza o **Padrão de Receitas Declarativas**. Você define o conteúdo em JSON/YAML e aciona os motores universais do repositório:

### 1. Carrosséis com Receita Declarativa (`carousel_recipe.json`)
Crie sua receita em `channels/<slug>/media/carousels/<post>/carousel_recipe.json` (veja modelo em `channels/_template/media/carousels/_template_carousel/carousel_recipe.json`) e execute:
```bash
# Renderizar lâminas com contraste seguro (Regra 08)
omnipress carousel --recipe channels/meu-canal/media/carousels/post_01/carousel_recipe.json --render

# Pipeline completo: Preparar backgrounds + Renderizar + Upload CDN + Agendar via Buffer
omnipress carousel --recipe channels/meu-canal/media/carousels/post_01/carousel_recipe.json --all
```

### 2. Masterização Broadcast de Locução (`omnipress master-audio`)
Aplica a cadeia completa de estúdio (adeclick, 80Hz highpass, spectral denoise, 4-band EQ cirúrgico, compressor e EBU R128 a -14.0 LUFS):
```bash
omnipress master-audio channels/meu-canal/media/voiceover/raw_voz.m4a -o channels/meu-canal/media/voiceover/master_voz.mp3
```

### 3. Alinhamento de Legendas Whisper (`omnipress align-captions`)
Converte o JSON bruto gerado pelo Whisper em chunks de alta retenção prontos para o Remotion:
```bash
omnipress align-captions channels/meu-canal/documentarios/ep01/whisper_raw.json -o channels/meu-canal/documentarios/ep01/captions.json
```

### 4. Publicação e Agendamento Universal (`omnipress publish`)
Despacha posts com higienização LGPD e proteção anti-duplicação (`PublishingShield`):
```bash
omnipress publish --recipe channels/meu-canal/articles/post_01/post_recipe.json
```

---

## 🛡️ Políticas de Isolamento & Segurança (Regras 04 e 09)

1. **Zero Vazamento no Git**: Diretórios sob `channels/*` (exceto `channels/_template/`) estão estritamente incluídos no `.gitignore`. Suas mídias, áudios e credenciais privadas jamais serão enviadas ao repositório público.
2. **Agnosticismo Total**: Jamais hardcode nomes de canais ou arquivos de episódios dentro de `src/video/`. Passe tudo via propriedades (`props`) ou arquivos de configuração do canal.
3. **Publicação Estritamente Única (Exactly-Once)**: Todas as publicações feitas via `omnipress_queue_post` ou `omnipress_publish_article` são registradas no livro-razão `media/staging/publishing_ledger.json` para evitar envios duplicados acidentais.

