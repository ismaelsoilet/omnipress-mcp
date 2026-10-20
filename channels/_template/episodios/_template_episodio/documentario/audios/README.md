# Pipeline de Áudio do Documentário (Regra 10)

Todas as faixas de locução devem obrigatoriamente passar pela **Cadeia de Masterização de Estúdio**:

1. **Locução Bruta (`raw/`)**: Áudios gravados pelo narrador (m4a, wav, mp3).
2. **Masterização Automática**:
   ```bash
   omnipress master-audio documentario/audios/raw/bloco_01.mp3 -o documentario/audios/mastered/bloco_01_master.mp3
   ```
3. **Padrão Obrigatório**:
   - High-pass em 80Hz (corte de rumble).
   - Denoise espectral (remoção de chiado).
   - Compressão dinâmica (2.5:1 a 3.5:1).
   - Sonoridade EBU R128 estritamente fixada em **-14.0 LUFS** (True Peak <= -1.2 dBTP).
4. **Trilha Sonora Sob a Voz**: Volume máximo calibrado entre **0.12 e 0.18** (-20dB a -24dB em relação à fala).
