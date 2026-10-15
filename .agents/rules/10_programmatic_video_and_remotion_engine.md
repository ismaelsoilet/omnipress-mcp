# Rule 10 — Programmatic Video & Remotion Engine Standards (Padrão de Vídeos Programáticos & Motor Remotion)

> **Priority**: MANDATORY (Obrigatório para agentes de IA e desenvolvedores que criam, editam ou renderizam vídeos programáticos no OmniPress).

---

## 🇺🇸 English Guidelines

### 1. Central Engine vs. Channel Asset Separation
- **Universal Engine in `src/video/`**: All video generation code, composition logic, and UI visual components reside exclusively in `src/video/` (`Root.tsx`, `compositions/`, `components/`, `types.ts`).
- **Channel Isolation**: Channel-specific assets (voiceover audio recordings, scene imagery, episode configurations, scripts) reside in `channels/<slug>/media/` and `channels/<slug>/scripts/`.
- **Brand Agnosticism**: Core Remotion components must never hardcode channel titles, logos, or colors. Styling, branding, and copy must be passed dynamically via composition props (`ChannelIntroProps`, `EpisodeConfig`, `DocumentaryShortProps`), resolving defaults from `channels/<slug>/channel.json`.

### 2. Dual-Aspect Ratio Standard
Every video template, episode generator, or bumper composition must support both target aspect ratios:
1. **16:9 Landscape (`1920x1080` @ 30fps)**: For long-form YouTube documentary episodes, master presentations, and widescreen distribution.
2. **9:16 Vertical (`1080x1920` @ 30fps)**: For YouTube Shorts, Instagram Reels, and TikTok viral cuts.

### 3. Cross-Platform Vertical Duration Standard (Monetization & Retention)
Vertical cuts (9:16) for TikTok, YouTube Shorts, and Instagram Reels must adopt a standard duration between **62 and 68 seconds (target: ~65s / 1,950 frames @ 30fps)**.
- **TikTok Creator Rewards Program Compliance**: Requires videos to be strictly longer than 60 seconds (>60.0s). The 65-second target provides a 5-second buffer that protects against platform rounding bugs (which can classify 60.1s as 59.9s and disqualify monetization).
- **YouTube Shorts Alignment**: Fits within the expanded Shorts limit (up to 180 seconds).
- **Instagram Reels Compatibility**: Fits comfortably within Reels' standard 90-second boundary.

### 4. Cinematic Components Library
The Remotion engine provides pre-built cinematic components:
- [`KenBurnsImage`](file:///home/ismaelsoilet/omnipress-mcp/src/video/components/KenBurnsImage.tsx): Smooth slow-zoom and pan movements with dynamic headline scaling and high-contrast badges.
- [`SynchronizedCaptions`](file:///home/ismaelsoilet/omnipress-mcp/src/video/components/SynchronizedCaptions.tsx): Word-by-word dynamic subtitle highlighting powered by Whisper timestamps, wrapped in a frosted dark backdrop container with gold border accents.
- [`TacticalGrid`](file:///home/ismaelsoilet/omnipress-mcp/src/video/components/TacticalGrid.tsx) & [`FilmGrain`](file:///home/ismaelsoilet/omnipress-mcp/src/video/components/FilmGrain.tsx): Atmospheric tactile overlays for investigative and historical documentary aesthetics.
- [`ThumbnailEpisode`](file:///home/ismaelsoilet/omnipress-mcp/src/video/compositions/ThumbnailEpisode.tsx): High-CTR programmatic thumbnail generator in 16:9 with dramatic badges, typography stroke, and cinematic vignette.

### 5. Broadcast Audio Soundscape & Dynamic Ducking
- **Audio Fidelity**: All sound files must be processed and output at 48kHz stereo broadcast quality via `<Audio />`.
- **Dynamic Ducking**: Background soundtrack volume must automatically drop to **-18dB to -22dB (volume: ~0.15–0.18)** while voiceover narration is speaking, and swell back to full ambience (**volume: ~0.40–0.45**) during dramatic silences and scene transitions.
- **Tactile SFX**: Pair on-screen text reveals, stamps, and cuts with tactile Foley sound effects (typewriter clicks, sub-bass impacts, paper rustles, metallic whooshes).

### 6. Soundtrack Licensing, Content ID & Platform-Native Audio Architecture
Automated Content ID systems (such as *We Are Era Music BV* on behalf of Creative Commons composers like Scott Buckley) automatically claim matching audio fingerprints. In vertical formats (Shorts), claims on embedded tracks >60s can trigger worldwide blocks. The engine supports two operational paths:
- **Mode A (Embedded Soundtrack)**: Rendered directly with music. Requires mandatory attribution credit in the video description (e.g. `'Signal to Noise' by Scott Buckley - released under CC-BY 4.0. www.scottbuckley.com.au`) and dispute/whitelist registration.
- **Mode B (Platform-Native Audio Post-Addition — Recommended for Shorts/Reels/TikTok)**: Render the video with **Voiceover + tactile SFX only** (no embedded background music). The creator selects and layers background music directly inside the mobile upload interface (YouTube Shorts Audio Library, TikTok Sound Picker, Instagram Reels Audio).
  - *Benefits*: 100% immune to Content ID copyright claims/blocks, zero dispute friction, and receives algorithmic reach boosts from native sound catalog usage.

---

## 🇧🇷 Diretrizes em Português

### 1. Separação Motor Universal vs. Ativos do Canal
- **Motor Central em `src/video/`**: Toda a lógica de renderização em Remotion reside em `src/video/` (`Root.tsx`, `compositions/`, `components/`, `types.ts`).
- **Isolamento de Canais**: Ativos específicos do canal (áudios de voz gravados, imagens de episódios, manifestos JSON) pertencem exclusivamente a `channels/<slug>/media/` e `channels/<slug>/scripts/`.
- **Agnosticismo de Marca**: Os componentes universais nunca devem chumbar nomes de canais, logotipos ou cores no código. Todas as propriedades visuais devem ser injetadas via props (`ChannelIntroProps`, `EpisodeConfig`), lendo as preferências de `channels/<slug>/channel.json`.

### 2. Padrão Duplo de Resolução
Todo template ou gerador de vídeo deve suportar nativamente as duas proporções canônicas:
1. **16:9 Widescreen (`1920x1080` a 30fps)**: Para episódios longos no YouTube e documentários completos.
2. **9:16 Vertical (`1080x1920` a 30fps)**: Para YouTube Shorts, Instagram Reels e TikTok.

### 3. Padrão de Duração de Vídeos Verticais (Monetização e Retenção)
Vídeos verticais (9:16) para TikTok, YouTube Shorts e Instagram Reels devem adotar duração padrão entre **62 e 68 segundos (alvo: ~65s / 1.950 frames a 30fps)**.
- **Monetização Obrigatória do TikTok Creator Rewards**: Exige vídeos estritamente superiores a 60 segundos (>60.0s). O alvo de 65s oferece margem de segurança contra bugs de arredondamento de plataformas (que desclassificam vídeos de 60s arredondados para 59.9s).
- **Alinhamento com YouTube Shorts**: Compatível com a expansão de Shorts para até 180s.
- **Teto do Instagram Reels**: Enquadra-se com folga no teto de 90s do Reels.

### 4. Biblioteca de Componentes Cinemáticos
O motor Remotion inclui componentes prontos para uso:
- [`KenBurnsImage`](file:///home/ismaelsoilet/omnipress-mcp/src/video/components/KenBurnsImage.tsx): Efeito zoom e pan suave com escalonamento dinâmico de títulos e badges contrastantes.
- [`SynchronizedCaptions`](file:///home/ismaelsoilet/omnipress-mcp/src/video/components/SynchronizedCaptions.tsx): Legendas dinâmicas sincronizadas palavra por palavra a partir de timestamps do Whisper, sobre card translúcido escuro e borda dourada.
- [`TacticalGrid`](file:///home/ismaelsoilet/omnipress-mcp/src/video/components/TacticalGrid.tsx) e [`FilmGrain`](file:///home/ismaelsoilet/omnipress-mcp/src/video/components/FilmGrain.tsx): Sobreposições táteis para documentários investigativos e históricos.
- [`ThumbnailEpisode`](file:///home/ismaelsoilet/omnipress-mcp/src/video/compositions/ThumbnailEpisode.tsx): Renderizador programático de miniaturas (thumbnails) 16:9 de alto CTR com contorno de fonte protetor e vinheta cinemática.

### 5. Paisagem Sonora Broadcast & Atenuação Automática (Ducking)
- **Qualidade de Áudio**: Todos os áudios devem ser renderizados a 48kHz estéreo via `<Audio />`.
- **Ducking de Volume**: A trilha musical de fundo deve ser atenuada automaticamente para **-18dB a -22dB (volume: ~0.15–0.18)** durante a voz humana e retornar ao volume pleno (**volume: ~0.40–0.45**) em pausas dramáticas e transições de cena.
- **Efeitos Sonoros (SFX)**: Cada aparição de texto, carimbo ou transição de corte deve vir acompanhada de SFX tátil (impactos graves, cliques mecânicos de máquina de escrever, estalos de película).

### 6. Licenciamento de Trilha Sonora, Content ID e Áudio Nativo das Plataformas
Sistemas automatizados de Content ID (como *We Are Era Music BV* representando compositores sob licença Creative Commons como Scott Buckley) aplicam reivindicações automáticas por impressão digital sonora. Em vídeos curtos (Shorts), o uso de faixas no Content ID por >60s pode acarretar bloqueio mundial do vídeo. O OmniPress suporta oficialmente dois fluxos de áudio:
- **Modo A (Trilha Incorporada na Renderização)**: Trilha embutida no Remotion com ducking automático. Exige obrigatoriamente a inclusão da linha canônica de créditos na descrição do vídeo (`'Signal to Noise' by Scott Buckley - released under CC-BY 4.0. www.scottbuckley.com.au`) e/ou liberação via formulário/contestação.
- **Modo B (Adição Tardia de Áudio Nativo — Altamente Recomendado para Shorts/Reels/TikTok)**: O vídeo é renderizado no Remotion contendo **apenas a Locução Masterizada + Efeitos Sonoros (SFX)**. O criador adiciona a trilha sonora de fundo diretamente no aplicativo no momento do upload (biblioteca oficial do YouTube Shorts, TikTok ou Instagram Reels), configurando o volume da música para 10% a 15%.
  - *Vantagens*: Imunidade total contra reivindicações e bloqueios de Content ID, zero fricção com formulários de liberação e forte benefício algorítmico, já que as redes sociais priorizam a entrega de vídeos que utilizam faixas nativas de seus catálogos oficiais.
