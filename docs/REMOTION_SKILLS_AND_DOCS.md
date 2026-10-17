# Remotion Agent Skills & Official Documentation Reference
# (Guia de Skills do Remotion & Documentação Oficial)

> **Bilingual / Bilíngue**: Este documento detalha as 12 Agent Skills oficiais do Remotion instaladas no repositório (`.agents/skills/remotion-*`), o protocolo de consulta à documentação oficial (`llms.txt` e API Algolia) e as diretrizes de integração com o motor de vídeo do OmniPress MCP.

---

## 🇧🇷 Visão Geral e Ecossistema

O Remotion disponibiliza um ecossistema nativo de **Agent Skills** projetado especificamente para agentes de codificação de IA (Antigravity, Claude Code, Codex, Cursor, Kimi Code). 

### Por que Agent Skills em vez de MCP?
Conforme a documentação oficial da Remotion ([`mcp.mdx`](https://www.remotion.dev/docs/ai/mcp.md)), o servidor Remotion MCP hospedado foi descontinuado em favor das **Agent Skills** nativas e do comando `/remotion-docs`, pelos seguintes motivos:
1. **Dados em tempo real**: As skills ensinam o agente a consultar a documentação em Markdown diretamente na fonte (remotion.dev), garantindo que as APIs utilizadas sejam sempre as mais recentes.
2. **Eficiência de contexto & tokens**: As skills carregam apenas as regras e técnicas específicas necessárias para a tarefa atual (ex.: animação, legendas, mapas ou renderização).
3. **Padrão unificado de diretório**: As skills são instaladas nativamente em `.agents/skills/`, exatamente a mesma pasta que o OmniPress MCP utiliza para suas skills de publicação.

---

## 🛠️ As 12 Skills Instaladas no Repositório

Todas as 12 skills oficiais estão instaladas em [`.agents/skills/`](../.agents/skills/):

| Skill | Diretório | Descrição / Quando Utilizar |
|---|---|---|
| **`remotion-best-practices`** | [`.agents/skills/remotion-best-practices/`](../.agents/skills/remotion-best-practices/SKILL.md) | **Roteador universal**. Use quando não tiver certeza de qual skill específica utilizar. Envia para a técnica correta. |
| **`remotion-markup`** | [`.agents/skills/remotion-markup/`](../.agents/skills/remotion-markup/SKILL.md) | **Regras de ouro de JSX/React para vídeo**. Ensina a usar `useCurrentFrame()`, `interpolate()`, `spring()`, `useVideoConfig()`, shorthands CSS (`scale`, `translate`, `rotate`) e proíbe classes de transição CSS/Tailwind que não funcionam na renderização frame-a-frame. Contém 25+ guias de técnicas (áudio, visualizadores, 3D, light leaks, fontes locais/Google, etc.). |
| **`remotion-docs`** | [`.agents/skills/remotion-docs/`](../.agents/skills/remotion-docs/SKILL.md) | **Pesquisa de documentação oficial em tempo real**. Ensina o agente a fazer queries na API Algolia do Remotion e baixar páginas em Markdown (`.md`). |
| **`remotion-captions`** | [`.agents/skills/remotion-captions/`](../.agents/skills/remotion-captions/SKILL.md) | **Legendas dinâmicas e sincronização**. Transcrição, timestamps palavra por palavra, animações de texto e sincronismo com voz. |
| **`remotion-studio`** | [`.agents/skills/remotion-studio/`](../.agents/skills/remotion-studio/SKILL.md) | **Preview interativo**. Inicia o Remotion Studio no navegador (`npm run remotion:preview` ou `npx remotion studio`) para validação visual em tempo real antes de renderizar. |
| **`remotion-render`** | [`.agents/skills/remotion-render/`](../.agents/skills/remotion-render/SKILL.md) | **Exportação de vídeo e still frames**. Parâmetros de CLI, codecs, vídeos transparentes (ProRes 4444 / WebM VP9). |
| **`remotion-create`** | [`.agents/skills/remotion-create/`](../.agents/skills/remotion-create/SKILL.md) | **Criação de novos vídeos e composições**. Estruturação de novos templates, cenas e layouts. |
| **`remotion-interactivity`** | [`.agents/skills/remotion-interactivity/`](../.agents/skills/remotion-interactivity/SKILL.md) | **Edição visual interativa no Studio**. Estruturação com `Interactive.*` para permitir que o usuário altere textos, cores e keyframes diretamente pela interface gráfica. |
| **`remotion-maps`** | [`.agents/skills/remotion-maps/`](../.agents/skills/remotion-maps/SKILL.md) | **Animações cartográficas e mapas explicativos**. Integração com Mapbox, MapLibre, MapTiler, GeoJSON e sobrevoos 3D com CesiumJS. |
| **`remotion-multimedia`** | [`.agents/skills/remotion-multimedia/`](../.agents/skills/remotion-multimedia/SKILL.md) | **Manipulação multimídia via Mediabunny**. Cálculo preciso de dimensões de vídeo, duração de áudio e metadados no navegador. |
| **`remotion-saas`** | [`.agents/skills/remotion-saas/`](../.agents/skills/remotion-saas/SKILL.md) | **Arquitetura para aplicações e SaaS**. Integração com `@remotion/player`, renderização server-side e Remotion Lambda. |
| **`remotion-upgrade`** | [`.agents/skills/remotion-upgrade/`](../.agents/skills/remotion-upgrade/SKILL.md) | **Atualização contínua**. Atualiza versões do Remotion, pacotes do ecossistema e as próprias Agent Skills instaladas. |

---

## 🔍 Protocolo de Consulta à Documentação Oficial

Para garantir precisão absoluta nas implementações de vídeo sem alucinar props obsoletas:

### 1. `llms.txt` — Índice para Modelos de IA
A Remotion mantém um arquivo canônico otimizado para agentes em:
```
https://www.remotion.dev/llms.txt
```

### 2. Conversão Automática para Markdown (`.md`)
Qualquer página de documentação do Remotion pode ser baixada como Markdown limpo adicionando `.md` ao final da URL, ou enviando o cabeçalho `Accept: text/markdown`:
```bash
# Exemplo 1: Via URL direta
curl -s https://www.remotion.dev/docs/interpolate.md

# Exemplo 2: Via cabeçalho HTTP
curl -s -H "Accept: text/markdown" https://www.remotion.dev/docs/use-video-config
```

### 3. Busca em Tempo Real via Algolia API (Sem dependência de scraping)
Os agentes podem buscar termos, métodos ou erros diretamente no índice de documentação oficial do Remotion:
```bash
curl -s -X POST "https://plsduol1ca-dsn.algolia.net/1/indexes/*/queries?x-algolia-api-key=3e42dbd4f895fe93ff5cf40d860c4a85&x-algolia-application-id=PLSDUOL1CA" \
  -H "Content-Type: application/json" \
  -d '{"requests":[{"query":"<termo_de_busca>","indexName":"remotion","params":"attributesToRetrieve=[\"hierarchy.lvl0\",\"hierarchy.lvl1\",\"url\"]&hitsPerPage=5"}]}'
```

---

## ⚡ Comandos Úteis do Remotion no OmniPress

```bash
# Atualizar as Agent Skills instaladas para a versão mais recente
npx remotion skills update

# Abrir o Remotion Studio para pré-visualização interativa
npm run remotion:preview

# Verificar erros de tipos em TypeScript em todo o motor de vídeo
npm run typecheck

# Renderizar vinheta 16:9 de canal
npm run remotion:render:intro

# Renderizar vinheta 9:16 vertical (Shorts/Reels)
npm run remotion:render:intro:shorts
```

---

## 🎯 Integração com as Regras do OmniPress

Ao trabalhar com Remotion neste repositório, os agentes devem harmonizar as diretrizes da Remotion com as regras do OmniPress:

1. **Regra 08 ([`08_visual_contrast_and_carousel_legibility_standards.md`](../.agents/rules/08_visual_contrast_and_carousel_legibility_standards.md))**:
   - Todo texto sobreposto (títulos, legendas palavra por palavra, badges) deve possuir contêiner protetor escuro translúcido (`rgba(8, 10, 14, 0.90)`) e borda sutil de destaque (`#FFD700` ou tom de identidade do canal).
   - Textos devem possuir contorno de segurança (`stroke`) para impedir que fundos claros prejudiquem a leitura.

2. **Regra 10 ([`10_programmatic_video_and_remotion_engine.md`](../.agents/rules/10_programmatic_video_and_remotion_engine.md))**:
   - **Separação Motor vs. Ativos**: Motor central em `src/video/`, ativos específicos de canal em `channels/<slug>/media/`.
   - **Resolução Dupla Obrigatória**: Suporte a 16:9 (`1920x1080` @ 30fps) e 9:16 (`1080x1920` @ 30fps).
   - **Duração Padrão Vertical**: 62 a 68 segundos (alvo: 65s / 1.950 frames a 30fps) para qualificação monetizada no TikTok Creator Rewards e Shorts.
   - **Masterização Obrigatória de Voz**: De-click, highpass 80Hz, denoise espectral, EQ 4 bandas, compressão e EBU R128 (-14.0 LUFS).
   - **Teto de Volume Musical**: Volume sob a fala estritamente entre `0.12` e `0.18`. Nunca exceder `0.20`.
   - **Soberania do Usuário na Trilha**: Modo A (CC-BY com créditos) vs Modo B (áudio nativo na plataforma). Nunca inserir trilha por iniciativa do agente sem aprovação expressa do usuário.
