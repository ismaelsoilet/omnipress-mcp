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
- [`SynchronizedCaptions`](file:///home/ismaelsoilet/omnipress-mcp/src/video/components/SynchronizedCaptions.tsx): Word-by-word dynamic subtitle highlighting powered by Whisper speech timestamps aligned strictly with the official script text (script text authority, speech timing lock, active word `#FFD700` karaoke highlight with WordTiming objects), wrapped in a frosted dark backdrop container with gold border accents.
- [`TacticalGrid`](file:///home/ismaelsoilet/omnipress-mcp/src/video/components/TacticalGrid.tsx) & [`FilmGrain`](file:///home/ismaelsoilet/omnipress-mcp/src/video/components/FilmGrain.tsx): Atmospheric tactile overlays for investigative and historical documentary aesthetics.
- [`ThumbnailEpisode`](file:///home/ismaelsoilet/omnipress-mcp/src/video/compositions/ThumbnailEpisode.tsx): High-CTR programmatic thumbnail generator in 16:9 with dramatic badges, typography stroke, and cinematic vignette.

### 5. Broadcast Audio Soundscape & Dynamic Ducking
- **Audio Fidelity**: All sound files must be processed and output at 48kHz stereo broadcast quality via `<Audio />`.
- **Dynamic Ducking & Volume Ceiling**:
  - The voiceover narration must remain the absolute primary acoustic focal point at full volume (**`volume: 1.0` / 0dB**).
  - Background soundtrack volume under voiceover must strictly follow a safe ceiling of **0.12 to 0.18 (-20dB to -24dB relative to speech)**.
  - **CRITICAL WARNING**: Never set background music above `0.20` when voice is playing. Higher values (such as `0.28` or `0.35`) sound acceptable on studio monitors but drown the voice on mobile phone speakers and budget earbuds.
  - Music should swell back to ambience (**`volume: ~0.35–0.40`**) only during dramatic pauses (>1.5s) and final scene transitions.
  - Include an automated fade-out over the final 2.0 to 2.5 seconds of the composition.
- **Tactile SFX**: Pair on-screen text reveals, stamps, and cuts with tactile Foley sound effects (typewriter clicks, sub-bass impacts, paper rustles, metallic whooshes).

### 6. Soundtrack Licensing, Content ID & Platform-Native Audio Architecture
- **User-Exclusive Soundtrack Authority Gate (CRITICAL)**: Agents must NEVER choose, define, or embed a background soundtrack on their own initiative from workspace stock, past projects, or library catalogs. The soundtrack must ALWAYS be explicitly commanded by the user for the specific episode or short. In the absence of an explicit user command specifying the track, the agent must render the video in **Mode B** (Voiceover + SFX only, no embedded soundtrack) or explicitly request the user's choice before embedding any musical audio.
Automated Content ID systems (such as *We Are Era Music BV* on behalf of Creative Commons composers like Scott Buckley) automatically claim matching audio fingerprints. In vertical formats (Shorts), claims on embedded tracks >60s can trigger worldwide blocks. The engine supports two operational paths:
- **Mode A (Embedded Soundtrack)**: Rendered directly with music. Requires strict volume ducking (`0.12–0.18`), mandatory attribution credit in the video description (e.g. `'Signal to Noise' by Scott Buckley - released under CC-BY 4.0. www.scottbuckley.com.au`) and dispute/whitelist registration.
- **Mode B (Platform-Native Audio Post-Addition — Recommended for Shorts/Reels/TikTok)**: Render the video with **Voiceover + tactile SFX only** (no embedded background music). The creator selects and layers background music directly inside the mobile upload interface (YouTube Shorts Audio Library, TikTok Sound Picker, Instagram Reels Audio) at 10%–15% volume.
  - *Benefits*: 100% immune to Content ID copyright claims/blocks, zero dispute friction, and receives algorithmic reach boosts from native sound catalog usage.

### 7. Multi-Platform Social Publishing Deliverable Standards
Every video asset generated by an agent must include a tailored, production-ready publishing guide for each target social platform:
1. **Instagram Reels**: Optimized hook in the first 2 lines, structured storytelling body with clean line breaks and bullet emojis, custom 9:16 cover thumbnail path and profile grid centering instructions, pinned first comment CTA, and topic categorization.
2. **TikTok**: Punchy caption within mobile character limits, exact cover video frame recommendation (e.g. 0:04s with text overlay), pinned discussion question comment, and instruction to disable TikTok auto-generated captions to prevent overlapping subtitles.
3. **YouTube Shorts**: High-CTR title with `#Shorts`, full description with CC-BY licensing credits (for Mode A), and targeted search tags for YouTube Studio.
4. **YouTube Long-Form Documentaries**: Widescreen 16:9 thumbnail, chapter timestamps (`00:00 - Intro`, etc.), complete description with source references, and full attribution blocks.

### 8. Official Remotion Agent Skills & Live Documentation Protocol
All programmatic video code written by AI agents must strictly comply with the 12 official Remotion Agent Skills installed in `.agents/skills/remotion-*` and described in [`docs/REMOTION_SKILLS_AND_DOCS.md`](file:///home/ismaelsoilet/omnipress-mcp/docs/REMOTION_SKILLS_AND_DOCS.md):
- **Universal Best Practices & Routing**: Prioritize [`.agents/skills/remotion-best-practices/`](file:///home/ismaelsoilet/omnipress-mcp/.agents/skills/remotion-best-practices/SKILL.md) and [`.agents/skills/remotion-markup/`](file:///home/ismaelsoilet/omnipress-mcp/.agents/skills/remotion-markup/SKILL.md) when authoring JSX for Remotion.
- **Strict Frame & Interpolation Rule**: Always compute animations via `useCurrentFrame()`, `interpolate()`, and `spring()` from `remotion`. Never use CSS `transition`, `@keyframes`, or Tailwind animations (they break offline frame-by-frame rendering).
- **Inline Shorthands over Matrix Transforms**: Prefer CSS `scale`, `translate`, and `rotate` inline in the `style` prop over complex `transform` strings to maintain full editability in Remotion Studio.
- **Real-Time Documentation Discovery**: When researching new Remotion APIs, query the Algolia Search API directly or append `.md` to docs URLs (e.g., `https://www.remotion.dev/docs/interpolate.md`). Never guess deprecated props.

### 9. Image Sourcing, Quota Fallback & Collaborative External Generation Protocol
When AI image generation models (Gemini Flash Image, Imagen, OpenAI, etc.) encounter quota exhaustion (HTTP 429), rate limits, or unavailability, agents must NEVER stall or block video production:
1. **Authentic Internet & Archive Search**:
   - Proactively query open public archives, museum records, Wikimedia Commons, the National Archives, Imperial War Museum, Library of Congress, and web search for genuine historical or real-world photographs/illustrations.
   - Download high-resolution originals, crop/center or apply blurred backdrop letterboxing to match the composition's target aspect ratio (16:9 or 9:16), and place them in the channel's media directory.
2. **Collaborative External Generation Prompts for the User**:
   - Simultaneously formulate a dedicated prompt document (e.g. `roteiros/PROMPTS_IMAGENS_EXTERNAS.md`) containing production-ready, hyper-detailed prompts tailored for external generators (Midjourney v6, FLUX.1 [dev], Stable Diffusion XL, Ideogram, Leonardo AI).
   - Each prompt must specify:
     - Exact aspect ratio tag (e.g. `--ar 16:9` or `--ar 9:16`).
     - Subject, historical authenticity, uniform/gear details, lighting, camera lens/focal length, sensor/film stock grain.
     - Target save path (e.g. `channels/<slug>/documentarios/<ep>/midias/cinematic_16x9/scene_XX.jpg`).
   - Present these prompts clearly to the user so they can generate and provide the assets back into the project for instant integration.

---

### 10. Audio-First Synchronization & Visual Dynamics Standard (Speech-to-Frame Lock)
- **Audio as the Master Timeline**: The recorded voiceover narration track is the absolute, authoritative master clock of the entire video. Visual scene cuts, b-roll switches, document reveals, text overlays, and graphic transitions must be strictly frame-locked to the exact millisecond when the corresponding topic or phrase is uttered in the speech.
- **Strict Prohibition of Arbitrary Durations**: Agents are strictly forbidden from distributing scene durations uniformly, estimating time slices linearly, or using arbitrary timestamps when an audio track exists. Scene start and end points must be derived directly from speech alignment (e.g., Whisper word/segment timestamps or acoustic speech detection).
- **Remotion Visual Dynamics & Anti-Static Rule**: A documentary or short must never devolve into a passive or static photo slideshow with slow linear zooms. Compositions must harness Remotion's programmatic engine for dynamic retention:
  1. **Spring-Based Camera Dynamics**: Utilize `spring()` and multi-point `interpolate()` for rapid push-ins on punchy words, camera whip-pans, and subtle directional drifting.
  2. **Tactile Optical Transitions**: Pair scene cuts with dynamic flash frames, subtle light leaks, optical lens flares, and vignette pulses to create fluid motion between historical assets.
  3. **Kinetic Typography & Badges**: Lower-thirds, classified stamps, and evidence tags must enter with spring physics, typewriter reveals, or scrambled text decoders, accompanied by subtle dark contrast backing cards (Rule 08).
  4. **Tactical Overlays & Atmosphere**: Combine tactical grid borders, scanning reticles, ambient dust particles, and organic 35mm film grain (`<FilmGrain />`) to maintain deep cinematic atmosphere.

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

### 5. Tratamento de Estúdio Obrigatório para Voz & Paisagem Sonora Broadcast
- **Tratamento Obrigatório de Estúdio (Voiceover Gate)**: É terminantemente proibido incorporar gravações cruas ("raw") diretamente ao vídeo. Todo áudio de voz falada (seja gravado pelo criador ou gerado sinteticamente) deve passar pela cadeia obrigatória de masterização em estúdio antes da renderização:
  1. **De-click / De-plosive (`adeclick`)**: Remoção de estalos salivares, toques acidentais e plosivas de ar.
  2. **Corte Passa-Alta Subsônico (`highpass=f=80`)**: Eliminação de ruídos infra-graves (<80Hz), vibrações de pedestal e impactos de mesa.
  3. **Redução Espectral de Ruído (`afftdn=nf=-28`)**: Limpeza cirúrgica do ruído de fundo (room floor), chiado de pré-amplificador e ruídos de ventoinha/ar-condicionado.
  4. **Equalização de Presença Broadcast (4 Bandas)**:
     - Dip em 300Hz (-3.5dB) para remover ressonância nasal/ambientes sem tratamento acústico.
     - Boost em 3.000Hz (+3.2dB) para clareza e destaque dos fonemas consonantais sobre a música.
     - High-shelf em 8.500Hz (+3.5dB) para brilho "air" e sedosidade de microfone condensador de broadcast.
     - Warmth em 140Hz (+1.8dB) para ressonância de peito e solidez tonal.
  5. **Compressor Dinâmico Broadcast (`acompressor`)**: Nivelamento da faixa dinâmica (ratio ~3:1) para que sussurros dramáticos e palavras enfáticas soem equilibrados e perfeitamente audíveis.
  6. **Normalização EBU R128 (-14.0 a -16.0 LUFS)**: Travamento do volume integrado na norma internacional de streaming móvel (**alvo: -14.0 LUFS**, True Peak <= -1.2 dBTP). Gravações cruas gravadas a -30 ou -35 LUFS devem ser obrigatoriamente masterizadas antes de qualquer composição.
- **Qualidade de Áudio**: Todos os áudios devem ser renderizados a 48kHz estéreo via `<Audio />`.
- **Hierarquia Acústica & Teto de Volume da Música**:
  - A voz do narrador masterizada é o elemento dominante absoluto (**`volume: 1.0` / 0dB**).
  - O volume da trilha musical de fundo sob a locução deve respeitar estritamente a faixa de **0.12 a 0.18 (-20dB a -24dB relativo à fala)**.
  - **AVISO CRÍTICO**: Jamais utilizar volumes musicais superiores a `0.20` enquanto houver fala ativa. Valores como `0.28` ou `0.35` soam aceitáveis em caixas de som de estúdio, mas abafam e competem com a voz em alto-falantes de smartphones e fones de ouvido comuns.
  - A trilha só deve crescer (**`volume: ~0.35–0.40`**) em pausas dramáticas de fala (>1.5s) e transições de cena.
  - Aplicar fade-out automático nos últimos 2.0 a 2.5 segundos do encerramento do vídeo.
- **Efeitos Sonoros (SFX)**: Cada aparição de texto, carimbo ou transição de corte deve vir acompanhada de SFX tátil (impactos graves, cliques mecânicos de máquina de escrever, estalos de película).

### 6. Licenciamento de Trilha Sonora, Content ID e Áudio Nativo das Plataformas
- **Soberania Exclusiva do Usuário na Escolha da Trilha Sonora (MANDATÓRIO)**: É expressamente proibido ao agente de IA escolher, supor ou embutir trilhas sonoras por iniciativa própria a partir de arquivos em estoque, episódios anteriores ou preferências internas. A trilha sonora deve SEMPRE ser definida única e exclusivamente mediante ordem expressa do usuário para aquele criativo específico. Se o usuário não tiver determinado a trilha sonora, o agente deve renderizar o vídeo no **Modo B** (apenas locução masterizada e efeitos SFX, sem música de fundo) ou perguntar diretamente ao usuário qual faixa utilizar antes de qualquer embutimento.
Sistemas automatizados de Content ID (como *We Are Era Music BV* representando compositores sob licença Creative Commons como Scott Buckley) aplicam reivindicações automáticas por impressão digital sonora. Em vídeos curtos (Shorts), o uso de faixas no Content ID por >60s pode acarretar bloqueio mundial do vídeo. O OmniPress suporta oficialmente dois fluxos de áudio:
- **Modo A (Trilha Incorporada na Renderização)**: Trilha embutida no Remotion com ducking rigoroso (`0.12–0.18`). Exige obrigatoriamente a inclusão da linha canônica de créditos na descrição do vídeo (`'Signal to Noise' by Scott Buckley - released under CC-BY 4.0. www.scottbuckley.com.au`) e/ou liberação via formulário/contestação.
- **Modo B (Adição Tardia de Áudio Nativo — Altamente Recomendado para Shorts/Reels/TikTok)**: O vídeo é renderizado no Remotion contendo **apenas a Locução Masterizada + Efeitos Sonoros (SFX)**. O criador adiciona a trilha sonora de fundo diretamente no aplicativo no momento do upload (biblioteca oficial do YouTube Shorts, TikTok ou Instagram Reels), configurando o volume da música para 10% a 15%.
  - *Vantagens*: Imunidade total contra reivindicações e bloqueios de Content ID, zero fricção com formulários de liberação e forte benefício algorítmico, já que as redes sociais priorizam a entrega de vídeos que utilizam faixas nativas de seus catálogos oficiais.

### 7. Padrão de Guias de Publicação Multiplataforma
Toda entrega de vídeo realizada por um agente de IA deve incluir obrigatoriamente um guia de publicação detalhado e individualizado para cada rede social de destino:
1. **Instagram Reels**: Gancho nos primeiros 2 segundos, corpo narrativo espaçado com quebras de linha e marcadores, arquivo de capa vertical 9:16 com instruções de enquadramento na grade do perfil, primeiro comentário fixado e tópicos de categorização.
2. **TikTok**: Legenda concisa adaptada ao limite de caracteres e ritmo da plataforma, frame exato recomendado para a capa do vídeo (ex.: 0:04s com sobreposição de texto), pergunta provocativa para fixar nos comentários e instrução expressa para desativar legendas automáticas da plataforma (evitando sobreposição com as legendas do vídeo).
3. **YouTube Shorts**: Título de alto CTR contendo a hashtag `#Shorts`, descrição completa com bloco de SEO e atribuição da licença musical (quando em Modo A), e tags de busca para o painel do YouTube Studio.
4. **YouTube Vídeo Longo**: Thumbnail de alto contraste 16:9, sumário com capítulos e minutagem (`00:00 - Introdução`, etc.), descrição documental completa com referências e créditos de licença.

### 8. Skills Oficiais do Remotion & Protocolo de Documentação em Tempo Real
Todo código de vídeo programático gerado por agentes deve cumprir as 12 Agent Skills oficiais do Remotion instaladas em `.agents/skills/remotion-*` e catalogadas em [`docs/REMOTION_SKILLS_AND_DOCS.md`](file:///home/ismaelsoilet/omnipress-mcp/docs/REMOTION_SKILLS_AND_DOCS.md):
- **Boas Práticas e Roteamento Universal**: Priorize [`.agents/skills/remotion-best-practices/`](file:///home/ismaelsoilet/omnipress-mcp/.agents/skills/remotion-best-practices/SKILL.md) e [`.agents/skills/remotion-markup/`](file:///home/ismaelsoilet/omnipress-mcp/.agents/skills/remotion-markup/SKILL.md) ao criar componentes e composições.
- **Animações Frame a Frame**: Utilize exclusivamente `useCurrentFrame()`, `interpolate()` e `spring()` do Remotion. É proibido usar transições CSS nativas ou classes de animação do Tailwind, pois colapsam na renderização estática quadro a quadro.
- **Propriedades Inline (`scale`, `translate`, `rotate`)**: Prefira shorthands CSS inline em vez de strings compostas de `transform`, garantindo compatibilidade e edição visual no Studio.
- **Consulta em Tempo Real**: Consulte a documentação oficial via endpoint Algolia ou adicionando `.md` às URLs oficiais (ex.: `https://www.remotion.dev/docs/interpolate.md`), sem alucinar props obsoletas.

### 9. Protocolo de Aquisição de Imagens, Fallback de Cotas e Geração Externa Colaborativa
Caso os modelos de geração de imagens por IA (Gemini Flash Image, Imagen, etc.) atinjam exaustão de cota (HTTP 429), limites de taxa ou indisponibilidade, é TERMINANTEMENTE PROIBIDO ao agente de IA interromper a produção ou ficar ocioso:
1. **Busca Ativa de Imagens Reais na Internet e Arquivos Públicos**:
   - O agente deve proativamente pesquisar em arquivos públicos desclassificados, acervos de museus, Wikimedia Commons, National Archives, Imperial War Museum, Library of Congress e busca na web por fotografias e ilustrações históricas autênticas em alta resolução.
   - Baixar os arquivos originais, processar enquadramentos ou aplicar letterbox com fundo difuso/desfocado para adequação estrita à proporção alvo (16:9 ou 9:16), salvando-os na biblioteca de mídia do canal.
2. **Geração Estruturada de Prompts para o Usuário (Geração Externa)**:
   - Simultaneamente, o agente deve gerar um manifesto de prompts prontos para uso (ex.: `roteiros/PROMPTS_IMAGENS_EXTERNAS.md`) otimizados para ferramentas externas de ponta (Midjourney v6, FLUX.1 [dev], Stable Diffusion XL, Ideogram, Leonardo AI).
   - Cada prompt deve incluir obrigatoriamente:
     - Parâmetro de aspecto explícito (`--ar 16:9` ou `--ar 9:16`).
     - Descrição cinematográfica minuciosa (iluminação, lente, enquadramento, textura de filme de época, detalhes de figurino e equipamentos).
     - Caminho exato de destino onde o usuário deve salvar a imagem (ex.: `channels/<slug>/documentarios/<ep>/midias/cinematic_16x9/scene_XX.jpg`).
   - Apresentar esses prompts de forma limpa e organizada no chat e no repositório, permitindo que o usuário gere as imagens em outras ferramentas e as entregue para incorporação imediata na esteira do Remotion.

### 10. Padrão de Linha do Tempo Guiada pelo Áudio & Dinâmica Visual do Remotion (Casamento Estrito Fala-Frame)
- **O Áudio como Relógio Mestre Absoluto**: A gravação de locução de voz é o relógio mestre irrevogável de toda a composição. Cada corte de imagem, mudança de plano, entrada de documento, carimbo pericial e transição visual deve estar milimetricamente travado no frame exato em que a respectiva palavra ou assunto é pronunciado pelo narrador.
- **Proibição Estrita de Durações Arbitrárias**: É expressamente proibido aos agentes definir durações uniformes, dividir o tempo total linearmente por estimativa ou usar tempos arbitrários quando houver áudio gravado. O início e o término de cada beat visual devem ser obrigatoriamente extraídos do alinhamento fonético da fala (timestamps de frases e palavras via Whisper ou segmentação acústica).
- **Dinâmica Visual do Remotion (Regra Anti-Estática)**: Documentários e shorts jamais devem parecer apresentações lentas de slides estáticos com zoom linear simples. O motor programático do Remotion deve ser utilizado para retenção visual dinâmica e ritmo de cinema:
  1. **Movimentos de Câmera com Física Spring**: Uso de `spring()` e `interpolate()` multi-ponto para zoom-in dinâmico em palavras-chave enfáticas, whip-pans direcionais e micro-drifts orgânicos.
  2. **Transições Ópticas e Flashes**: Cortes entre cenas devem receber flashes sutis de transição, vazamentos de luz (light leaks) e pulsações de vinheta escura para conectar os ativos históricos sem cortes duros monótonos.
  3. **Tipografia Cinética e Badges**: Lower-thirds, carimbos confidenciais e etiquetas de arquivo devem entrar com física de mola (spring), efeito datilográfico ou decodificação de texto cifrado (`ScrambledText`), sempre sobre cards protetores de alto contraste (Regra 08).
  4. **Atmosfera Tátil & HUD Investigativo**: Sobreposição contínua de granulação de filme 35mm (`<FilmGrain />`), partículas de poeira suspensa (`<DustParticles />`) e retículas táticas de arquivo (`<TacticalGrid />`).

### 11. Padrão de Iluminação Documental, Luminância Mínima & Verificação Anti-Anacronismo
- **Proibição Estrita de Imagens Escuras / Vazio Negro**: Qualquer cena com luminância média inferior a **45.0** (em escala de 0 a 255) é sumariamente rejeitada pelo motor de QA. Texturas de fundo devem empregar ardósia escura sutil (`#12161F` / `#161B22`) em vez de preto puro opaco (`#000000`). Os assuntos principais (retratos, pinturas, documentos) devem permanecer radiantes, bem contrastados e iluminados.
- **Tolerância Zero a Anacronismos Históricos**:
  - Armamentos: Proibido o uso de armas de fogo ou mosquetes em períodos medievais pré-pólvora (ex.: 1385 na Batalha de Aljubarrota).
  - Vexilologia: Proibido utilizar pavilhões republicanos pós-1889 ou pós-1910 em contextos da monarquia portuguesa medieval ou do Império do Brasil de 1822.
  - Personalidades: A imagem deve corresponder indubitavelmente à figura citada na locução (ex.: retrato autêntico de Dom João I, José Bonifácio, Napoleão Bonaparte).
- **Coerência de Fase Narrativa**: O selo ou arte de "CASO ENCERRADO" é restrito exclusivamente aos 5% finais do vídeo (Ato de Conclusão). Em introduções ou no meio da investigação, deve-se empregar "DOSSIÊ ABERTO / INVESTIGAÇÃO EM ANDAMENTO".
- **Padrão Broadcast para Telas Finais**: Telas de encerramento devem adotar o design premium de produções do YouTube (branding em alta definição, chamadas dinâmicas para inscrição e compartilhamento), sendo proibidos layouts rústicos estáticos semelhantes a caixas de texto de menus de jogos retrô.

