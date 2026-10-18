# Workspace Template de Canal — OmniPress MCP

Este diretório define a estrutura canônica e universal para qualquer canal de mídia, marca ou publicação no **OmniPress MCP**.

Toda produção de conteúdo (artigos, carrosséis, vídeos longos, shorts, locuções e roteiros) de um canal deve residir **exclusivamente** dentro de `channels/<channel-slug>/`. O motor do OmniPress (`src/`) permanece agnóstico, reutilizável e desacoplado.

---

## 📁 Estrutura Canônica de Diretórios

```
channels/<channel-slug>/
├── channel.json                     # Metadados, branding, cores, tipografia, redes sociais e configurações de vídeo
├── README.md                        # Manifesto editorial, diretrizes de tom e checklist do canal
│
├── articles/                        # Artigos long-form em Markdown com YAML frontmatter
│   └── AAAA/MM/                     # Organização recomendada por ano e mês
│
├── media/                           # Biblioteca e pipeline de ativos de mídia
│   ├── raw/                         # Imagens brutas, documentos históricos e fontes originais
│   ├── carousels/                   # Lâminas geradas pelo CarouselBuilder (Pillow)
│   ├── stories/                     # Criativos verticais 9:16
│   ├── visuals/                     # Imagens tratadas, recortes e B-roll para composições de vídeo
│   ├── voiceover/                   # Locuções brutas e faixas masterizadas (-14 LUFS)
│   ├── soundtrack/                  # Trilhas sonoras brutas (raw/) e cortes pontuais (cuts/)
│   └── output/                      # Vídeos finais renderizados (.mp4) prontos para distribuição
│
├── documentarios/                   # Episódios longos em widescreen 16:9 (YouTube)
│   └── <slug_episodio>/             # Workspace isolado de cada episódio
│       ├── roteiros/                # Roteiros Markdown, guia teleprompter, legendas Whisper (.json)
│       ├── midias/                  # Ativos visuais e sonoros exclusivos do episódio
│       └── scripts/                 # Scripts auxiliares de masterização, montagem ou exportação
│
├── shorts/                          # Vídeos curtos verticais 9:16 (Shorts / Reels / TikTok, ~65s)
│   └── <slug_short>/                # Workspace isolado de cada short
│       ├── roteiros/                # Roteiro, cards de impacto e legendas sincronizadas (.json)
│       ├── audios/                  # Locução masterizada e cortes de áudio
│       ├── midias/                  # B-roll vertical, imagens 9:16 e capas
│       └── scripts/                 # Scripts específicos de renderização ou montagem
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

## 🛡️ Políticas de Isolamento & Segurança (Regras 04 e 09)

1. **Zero Vazamento no Git**: Diretórios sob `channels/*` (exceto `channels/_template/`) estão estritamente incluídos no `.gitignore`. Suas mídias, áudios e credenciais privadas jamais serão enviadas ao repositório público.
2. **Agnosticismo Total**: Jamais hardcode nomes de canais ou arquivos de episódios dentro de `src/video/`. Passe tudo via propriedades (`props`) ou arquivos de configuração do canal.
3. **Publicação Estritamente Única (Exactly-Once)**: Todas as publicações feitas via `omnipress_queue_post` ou `omnipress_publish_article` são registradas no livro-razão `media/staging/publishing_ledger.json` para evitar envios duplicados acidentais.
