# Template de Episódio Documental (16:9 Widescreen)

Este diretório serve como molde para a produção de episódios longos para o YouTube.

## Estrutura do Episódio

- `roteiros/`: Roteiro completo (`roteiro.md`), guia de teleprompter e legendas sincronizadas (`captions.json`).
- `midias/`: Arquivos de imagens em proporção 16:9 (`1920x1080`), documentos desclassificados, B-roll e fotografias de arquivo.
- `scripts/`: Scripts auxiliares específicos para este episódio (ex.: masterização de áudio, alinhamento Whisper).

## Fluxo de Produção

1. **Roteiro & Locução**: Grave ou sintetize a narração e salve em `media/voiceover/`.
2. **Masterização de Estúdio (Voiceover Gate)**: Garanta que a locução passe pela cadeia broadcast (corte 80Hz, de-noise, compressão e normalização EBU R128 para **-14.0 LUFS**).
3. **Alinhamento Whisper**: Gere o arquivo de legendas palavra por palavra com timestamps precisos.
4. **Renderização via Remotion**:
   ```bash
   npx remotion render src/video/index.ts DocumentaryEpisode-16x9 media/output/ep01.mp4 \
     --props='{"config": {"id": "ep01", "title": "Título", "channelSlug": "meu-canal", "scenes": []}}'
   ```
