---
name: omnipress-darkchannel
description: Automated end-to-end production pipeline for viral dark channels and monetization across Instagram, YouTube (Shorts and long-form), X (Twitter), and Threads using OmniPress MCP tools.
---

# OmniPress — Dark Channel Production Runbook

Use this skill whenever the user or an autonomous agent (Hermes / Antigravity) wants to plan, brainstorm, script, produce, synthesize audio/video, or publish dark channel content for monetization on **Instagram**, **YouTube**, and **X (Twitter)**.

---

## 1. O que é um Canal Dark de Alta Retenção?

Canais Dark monetizam através do YouTube AdSense, Creator Rewards, marketing de afiliados e infoprodutos sem que o criador mostre o rosto. O sucesso reside em **3 pilares matemáticos**:
1. **Hook Visual e Sonoro (0-3s)**: Quebra de padrão imediata para reter a rolagem (scroll stop).
2. **Loop de Curiosidade Contínua (3-45s)**: Revelações em camadas para manter a retenção acima de 80%.
3. **Conversão / CTA (45-60s)**: Chamada precisa para inscrição, compartilhamento e comentários provocativos.

---

## 2. Fluxo Operacional de 5 Etapas (Fábrica Completa de Conteúdo)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                  1. IDEAÇÃO & BRANDING DO CANAL                         │
│   Chame: omnipress_brainstorm_channel(niche="historia", tone="mystery") │
│   Obtenha: Nomes de Alto CTR + 3 Pilares + 10 Pautas Virais com Ganchos │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
┌────────────────────────────────────▼────────────────────────────────────┐
│                  2. ROTEIRIZAÇÃO & PROMPTS DE IA                        │
│   Chame: omnipress_prepare_dark_script(topic=..., tone="mystery")       │
│   Obtenha: Roteiro 55s + 5 Prompts IA (9:16) + Carrossel IG + Thread X │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
┌────────────────────────────────────▼────────────────────────────────────┐
│                  3. LOCUÇÃO NEURAL (EDGE-TTS)                           │
│   Chame: omnipress_generate_speech(text="...", voice="pt-BR-Antonio...")│
│   Obtenha: Arquivo .mp3 com voz documental profunda e imersiva         │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
┌────────────────────────────────────▼────────────────────────────────────┐
│                  4. MONTAGEM & RENDERIZAÇÃO DE VÍDEO                    │
│   Chame: omnipress_render_dark_video(audio_path=..., image_paths=...)   │
│   Obtenha: Arquivo .mp4 vertical 9:16 renderizado via ffmpeg           │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
┌────────────────────────────────────▼────────────────────────────────────┐
│                  5. AGENDAMENTO & DISTRIBUIÇÃO MULTI-CANAL              │
│   Chame: omnipress_queue_media_post(                                   │
│     caption=..., platforms=["instagram", "youtube_shorts", "x"],       │
│     media_urls=["./media/output/<tema>.mp4"], media_type="short"       │
│   )                                                                    │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Diretrizes por Plataforma

### 📷 Instagram (Reels & Carrosséis)
- **Reels**: Vídeo vertical 9:16 (< 60s), áudio grave/documental, legenda com parágrafos limpos e até 15 hashtags nichadas.
- **Carrosséis**: 7 slides (Capa magnética com alto contraste + 5 slides de conteúdo denso + 1 slide de CTA para salvar).
- **Importante**: O Instagram exige ao menos uma mídia em `media_urls`.

### 🎬 YouTube (Shorts & Vídeos Longos)
- **Shorts**: Duração entre 45 e 58 segundos (evitar bater exatos 60s). Título irresistível (< 70 caracteres) terminando com `#Shorts`.
- **Vídeos Longos**: 16:9 (1920x1080), estrutura com capítulos com timestamps (00:00 - Introdução, etc.), tags de SEO e thumbnail com alto contraste (amarelo/vermelho sobre fundo escuro).
- O OmniPress salva automaticamente o manifesto em `media/staging/youtube/` para auditoria ou upload via Webhook/API.

### 🐦 X (Twitter) & Threads
- **Threads Narrativas**: Se o texto contiver quebras `---`, o OmniPress desmembra automaticamente em tweets numerados (`1/6`, `2/6`...).
- Tweet de gancho com emoji discreto (`🧵👇`) e tweet final com chamada para RT e follow.

---

## 4. Integração com Coolify e Hermes Agent (Oracle VPS)

### No Coolify:
1. Suba usando o arquivo [`docker-compose-coolify.yml`](file:///home/ismaelsoilet/omnipress-mcp/docker-compose-coolify.yml).
2. O container `omnipress_api_coolify` é automaticamente integrado à rede Docker `hermes-net` e ao proxy Traefik com SSL Let's Encrypt.
3. Volumes persistentes:
   - `omnipress_articles`: `/app/articles`
   - `omnipress_media`: `/app/media`

### Comunicação com o Hermes:
- **Rede Interna Docker**: O Hermes Agent pode chamar o OmniPress diretamente via `http://omnipress_api_coolify:3333` (ou `http://omnipress:3333`) sem sair para a internet pública!
- **Modos de Invocação**:
  - **REST API**:
    - `POST /api/brainstorm_channel`
    - `POST /api/prepare_dark_script`
    - `POST /api/generate_speech`
    - `POST /api/render_video`
    - `POST /api/queue_media_post`
  - **MCP Protocol**: `POST /mcp` (JSON-RPC 2.0).
  - **OpenAPI 3.1**: `GET /openapi.json` para registro dinâmico de ferramentas no Hermes.
