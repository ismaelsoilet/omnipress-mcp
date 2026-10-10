---
name: omnipress-darkchannel
description: Automated end-to-end production pipeline for viral dark channels and monetization across Instagram, YouTube (Shorts and long-form), X (Twitter), and Threads using OmniPress MCP tools.
---

# OmniPress — Dark Channel Production Runbook

Use this skill whenever the user or an autonomous agent (Hermes / Antigravity) wants to plan, script, produce, or publish dark channel content for monetization on **Instagram**, **YouTube**, and **X (Twitter)**.

---

## 1. O que é um Canal Dark de Alta Retenção?

Canais Dark monetizam através do YouTube AdSense, Creator Rewards, marketing de afiliados e infoprodutos sem que o criador mostre o rosto. O sucesso reside em **3 pilares matemáticos**:
1. **Hook Visual e Sonoro (0-3s)**: Quebra de padrão imediata para reter a rolagem (scroll stop).
2. **Loop de Curiosidade Contínua (3-45s)**: Revelações em camadas para manter a retenção acima de 80%.
3. **Conversão / CTA (45-60s)**: Chamada precisa para inscrição, compartilhamento e comentários provocativos.

---

## 2. Fluxo Operacional Passo a Passo

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      1. ESCOLHA DO TEMA & ROTEIRO                       │
│      Chame: omnipress_prepare_dark_script(topic=..., tone=...)          │
│      Obtenha: Roteiro (Short/Reel) + Prompts de IA + Carrossel + Thread │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
┌────────────────────────────────────▼────────────────────────────────────┐
│                      2. GERAÇÃO DE MÍDIAS VISUAIS                       │
│      Gere as imagens das cenas (9:16 ou 16:9) usando os prompts de IA   │
│      Salvar em: ./media/assets/<tema>/cena_01.png, cena_02.png...       │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
┌────────────────────────────────────▼────────────────────────────────────┐
│                      3. LOCUÇÃO NEURAL & VÍDEO                          │
│      Execute: python scripts/generate_dark_media.py                     │
│               --text "<roteiro>" --images <imagens...>                  │
│               --output ./media/output/<tema>.mp4                        │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
┌────────────────────────────────────▼────────────────────────────────────┐
│                      4. AGENDAMENTO & DISTRIBUIÇÃO                      │
│      Chame: omnipress_queue_media_post(                                 │
│        caption=..., platforms=["instagram", "youtube_shorts", "x"],     │
│        media_urls=["./media/output/<tema>.mp4"], media_type="short"     │
│      )                                                                  │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Diretrizes por Plataforma

### 📷 Instagram (Reels & Carrosséis)
- **Reels**: Vídeo vertical 9:16 (< 60s), áudio grave/documental, legenda com parágrafos limpos e até 15 hashtags nichadas.
- **Carrosséis**: 7 slides (Capa magnética + 5 slides de conteúdo denso + 1 slide de CTA para salvar).
- **Importante**: O Instagram não permite postagens de texto puro; `media_urls` é obrigatório.

### 🎬 YouTube (Shorts & Vídeos Longos)
- **Shorts**: Duração entre 45 e 58 segundos (evitar bater exatos 60s). Título irresistível (< 70 caracteres) terminando com `#Shorts`.
- **Vídeos Longos**: 16:9 (1920x1080), estrutura com capítulos com timestamps (00:00 - Introdução, etc.), tags de SEO e thumbnail com alto contraste (amarelo/vermelho sobre fundo escuro).
- O OmniPress salva automaticamente o manifesto em `media/staging/youtube/` para auditoria ou upload via Webhook/API.

### 🐦 X (Twitter)
- **Threads Narrativas**: Se o texto contiver quebras `---`, o OmniPress desmembra automaticamente em tweets numerados (`1/6`, `2/6`...).
- Tweet de gancho com emoji discreto (`🧵👇`) e tweet final com chamada para RT e follow.

---

## 4. Integração com o Hermes e VPN (Tailscale)

Quando o Hermes estiver rodando em uma VPS Oracle ou remotamente:
1. O OmniPress pode rodar em modo servidor local HTTP:
   ```bash
   node src/server.js --http
   # Disponível na porta 3333
   ```
2. O Hermes conecta-se com segurança pelo IP do Tailscale (sem portas públicas na internet):
   `http://100.x.y.z:3333/api/queue_media_post` ou executando comandos via SSH no túnel WireGuard.
3. Notificação no Telegram: Hermes envia a prévia do vídeo para aprovação do usuário antes de publicar.
