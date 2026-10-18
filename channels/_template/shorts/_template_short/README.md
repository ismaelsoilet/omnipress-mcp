# Template de Vídeo Curto / Short (9:16 Vertical)

Este diretório serve como molde para a produção de vídeos verticais para YouTube Shorts, Instagram Reels e TikTok.

## Padrão de Duração & Monetização (Regra 10)
- **Duração Padrão**: Entre **62 e 68 segundos (alvo: ~65s / 1.950 frames a 30fps)**.
- Essa duração garante elegibilidade ao programa de monetização TikTok Creator Rewards (>60s) e excelente retenção no YouTube Shorts e Instagram Reels.

## Estrutura do Short
- `roteiros/`: Roteiro estruturado (Gancho nos primeiros 3s, Escalação, Clímax, CTA final) e legendas Whisper sincronizadas (`short_captions.json`).
- `audios/`: Locução gravada e cortes sonoros exclusivos.
- `midias/`: Cenas verticais (`1080x1920`) ou horizontais preparadas com letterbox/fundo desfocado cinematográfico.
- `scripts/`: Scripts de alinhamento e montagem automática do short.

## Comando de Renderização
```bash
npx remotion render src/video/index.ts DocumentaryShort-9x16 media/output/short_01.mp4 \
  --props='{"title": "Título", "badge": "DESTAQUE // 9:16", "scenes": []}'
```
