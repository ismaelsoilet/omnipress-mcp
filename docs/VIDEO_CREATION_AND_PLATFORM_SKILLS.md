# Guia de Skills de Criação de Vídeos, Verticais e Documentários Longos
# (Video Creation Best Practices: YouTube, TikTok, Reels, Shorts & Documentaries)

> **Bilingual / Bilíngue**: Este catálogo documenta as **31 Agent Skills** instaladas no OmniPress MCP ([`.agents/skills/`](../.agents/skills/)), organizadas por formato de distribuição (Vídeos Verticais, Documentários Longos do YouTube e Motor Remotion Programático).

---

## 📱 1. Vídeos Verticais de Alta Retenção (TikTok, Reels & YouTube Shorts)

| Skill | Diretório | Descrição / Boas Práticas |
|---|---|---|
| **`viral-hooks`** | [`.agents/skills/viral-hooks/`](../.agents/skills/viral-hooks/SKILL.md) | **Ganchos dos primeiros 1 a 3 segundos**. Três camadas sincronizadas (visual, verbal e texto em tela). Frameworks de criadores de elite (Kallaway, MrBeast, Hormozi, Brunson). Elimina anti-padrões que derrubam a retenção inicial. |
| **`viral-youtube-shorts`** | [`.agents/skills/viral-youtube-shorts/`](../.agents/skills/viral-youtube-shorts/SKILL.md) | **Otimização para o algoritmo do Shorts Feed**. Maximização da métrica **VVSA** (Viewed vs Swiped Away > 70%), eliminação da queda aos 3s, loops perfeitos (>100% retenção) e construção de ponte (funil) de Shorts para vídeos longos. |
| **`viral-instagram-reels`** | [`.agents/skills/viral-instagram-reels/`](../.agents/skills/viral-instagram-reels/SKILL.md) | **Alcance orgânico no Instagram**. Foco na hierarquia de sinais do algoritmo do Reels (tempo de exibição, *sends per reach*, *likes per reach*), uso de Trial Reels, diretrizes de originalidade (sem marca d'água) e legendas para SEO interno. |
| **`viral-tiktok-content`** | [`.agents/skills/viral-tiktok-content/`](../.agents/skills/viral-tiktok-content/SKILL.md) | **Roteirização para a For You Page (FYP)**. Ritmo de retenção acelerado, cálculo de taxa de conclusão por tempo de vídeo (>60s para o Creator Rewards), timing de sons nativos e etiquetas de divulgação de IA. |
| **`viral-captions-and-ctas`** | [`.agents/skills/viral-captions-and-ctas/`](../.agents/skills/viral-captions-and-ctas/SKILL.md) | **Legendas e CTAs que convertem**. Foco em salvamentos e compartilhamentos (*sends*), técnicas para visualização sem som (*muted watching*), quebra de primeira linha e prevenção de penalidades por *engagement bait*. |
| **`viral-short-form`** | [`.agents/skills/viral-short-form/`](../.agents/skills/viral-short-form/SKILL.md) | **Arquitetura Geral de Formato Curto**. Estrutura de retenção comprovada de 4 etapas: **Gancho -> Escalação -> Payoff -> CTA**. Adaptável para talking head, tutoriais e listas. |
| **`viral-short-form-ideas`** | [`.agents/skills/viral-short-form-ideas/`](../.agents/skills/viral-short-form-ideas/SKILL.md) | **Geração de Ideias em Escala**. Matriz de pilares de conteúdo, mineração de dúvidas no Reddit/YouTube e desdobramento de 1 tema em 5 ângulos virais. |
| **`reel-export`** | [`.agents/skills/reel-export/`](../.agents/skills/reel-export/SKILL.md) | **Exportação Técnica Vertical 9:16 (1080x1920)**. Respeito às **Safe Zones** de interface (evitando botões nativos de like/comentário), codecs H.264, yuv420p, bt709 e verificação por ffprobe. |

---

## 🎬 2. Documentários Longos de YouTube (Long-Form Documentaries & Dossiers)

| Skill | Diretório | Descrição / Boas Práticas |
|---|---|---|
| **`omnipress-youtube-documentary`** | [`.agents/skills/omnipress-youtube-documentary/`](../.agents/skills/omnipress-youtube-documentary/SKILL.md) | **Runbook Mestre de Documentários OmniPress (8 a 30+ min)**. Arco narrativo em 5 atos, superação do abismo dos primeiros 30s, **Pattern Interrupts a cada 45–60s**, variação visual a cada 3–5s, cliffhangers entre capítulos, embalagem de alto CTR e renderização Remotion. |
| **`technical-video-script`** | [`.agents/skills/technical-video-script/`](../.agents/skills/technical-video-script/SKILL.md) | **Roteiro de Produção em Duas Colunas**. Visual/B-Roll/SFX na coluna 1 e Narração na coluna 2. Gancho de 30s, orçamento de minutagem, cortes precisos e blocos de timestamps para o YouTube. |
| **`vox-explainer`** | [`.agents/skills/vox-explainer/`](../.agents/skills/vox-explainer/SKILL.md) | **Estilo Jornalismo Visual / Vox**. Animação documental com textura de papel rasgado, halftone, tipografia condensada em blocos, movimento cadenciado (*motion on twos*) e rigor de fontes para cada fato. |
| **`documentary-montage-production`** | [`.agents/skills/documentary-montage-production/`](../.agents/skills/documentary-montage-production/SKILL.md) | **Pesquisa Factual & Registro de Evidências**. Metodologia para manter log de fontes (`claim_id`), checagem de fatos, uso ético de arquivos históricos e dramatizações sintéticas. |
| **`cinematic-trailer-production`** | [`.agents/skills/cinematic-trailer-production/`](../.agents/skills/cinematic-trailer-production/SKILL.md) | **Trailers e Teasers Cinemáticos**. Curvas de tensão, drops sonoros e cortes dinâmicos para aberturas e trailers de novos episódios documentais. |
| **`youtube-thumbnail-design`** | [`.agents/skills/youtube-thumbnail-design/`](../.agents/skills/youtube-thumbnail-design/SKILL.md) | **Design de Thumbnails de Alto CTR**. O **Teste dos 120px no mobile**, regra dos 3 elementos focais, psicologia de expressão facial, contraste contra o feed do YouTube e complementação de título sem repetição de texto. |

---

## ⚙️ 3. Motor Programático Remotion (Renderização de Código para Vídeo)

As 12 skills do ecossistema oficial do Remotion residem em [`.agents/skills/remotion-*`](../.agents/skills/):
- **`remotion-best-practices`**: Roteador mestre para animações.
- **`remotion-markup`**: Uso estrito de `useCurrentFrame()`, `interpolate()` e `spring()` (proibidas transições CSS/Tailwind).
- **`remotion-captions`**: Legendas sincronizadas palavra por palavra via Whisper timestamps.
- **`remotion-maps`**: Rotas animadas e sobrevoos 3D (Mapbox, MapLibre, MapTiler, CesiumJS).
- **`remotion-studio`**: Preview interativo via `npm run remotion:preview`.
- **`remotion-render`**: Parâmetros de CLI e renderização MP4/ProRes.
- **`remotion-docs`**: Consulta em tempo real à documentação oficial via API Algolia e arquivos `.md`.
- **`remotion-upgrade`**: Atualizador contínuo de versões e skills.

---

## 🎯 Síntese de Regras de Ouro para Agentes

1. **Vídeos Verticais (Shorts/Reels/TikTok)**:
   - Duração padrão: **62 a 68 segundos (alvo: 65s / 1.950 frames @ 30fps)** para monetização no TikTok Creator Rewards e Shorts.
   - Primeiro frame já contém o gancho visual e verbal (VVSA > 70%).
   - Modo B de áudio recomendado: exportar com narração masterizada (-14 LUFS) + SFX táteis, inserindo a trilha musical nativamente no aplicativo da rede.
2. **Vídeos Longos de YouTube (Documentários)**:
   - Resolução 16:9 (`1920x1080` @ 30fps).
   - Primeiro minuto sem vinhetas corporativas longas; promessa imediata de resposta à pergunta central.
   - Pattern Interrupt obrigatório a cada 45–60 segundos (mudança de ritmo sonoro ou visual).
   - Miniatura com 3 elementos e contraste validado no teste de 120px mobile.
