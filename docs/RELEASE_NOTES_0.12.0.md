# OmniPress MCP 0.12.0 — Release Notes

**Data:** 2026-11-03  
**Tema:** Novo fluxo de edição interativa do Remotion + Media Staging portátil

---

## Resumo

A versão 0.12.0 adapta o motor de vídeo do OmniPress ao novo fluxo de edição interativa do Remotion 4.0.540, sem abrir mão da arquitetura declarativa e do isolamento por canal.

O release também incorpora o **Meta Unified Publishing Suite** (Instagram Reels, Facebook Pages e Threads) e o **Active Health Check Gate** já publicados em `origin/main` na versão 0.11.0.

---

## Compatibilidade

| Item | Versão |
|---|---|
| Remotion | **4.0.540** (todos os pacotes `remotion` e `@remotion/*`) |
| Node.js | 18+ (validado em Node 22/24) |
| Python | 3.12 |
| OmniPress MCP | **0.12.0** |

O upgrade do Remotion é um patch da linha 4.0.x. Não há quebra de contrato MCP ou de recipes.

---

## Destaques

### 1. Episódio editável no Remotion Studio

```bash
omnipress video --recipe episode_config.json \
  --channel <slug> --scaffold-editable

omnipress studio --channel <slug> --episode <episode-slug>

omnipress video --recipe \
  channels/<slug>/video/episodes/<episode>-16x9/video_recipe.editable.json
```

O motor `EditableVideoEngine` gera:

```
channels/<slug>/video/episodes/<episode>-<aspect>/
├── Episode.tsx                 # um nó JSX por cena
├── index.ts                    # entry point próprio + composição
├── meta.json                   # hashes e registro
├── media.json                  # manifesto de staging portátil
├── data/captions.ts            # legendas tipadas
├── data/theme.ts               # tema resolvido do channel.json
├── video_recipe.editable.json  # recipe de render
└── public/                     # staging gerado (gitignored)
```

Após o scaffold, o TSX é a fonte de verdade do episódio. Edições manuais são protegidas por hash; `--force` cria backup antes de sobrescrever.

### 2. Timeline estruturada

- `<Track name="...">` para cenas, locução, trilha, SFX e vinheta.
- `name` descritivo em cada sequência.
- Lane packing automático para cenas e áudios sobrepostos (`Cenas 2`, `Áudio de Cena 2`, `SFX de Cena 2`).
- Previews conectados: `SceneKenBurns-Preview`, `SceneDocumentReveal-Preview`, `SceneHeraldic-Preview`, `SceneOutro-Preview`.

### 3. Componentes de cena interativos

`Interactive.create()` em:

- `SceneKenBurns`
- `SceneDocumentReveal`
- `SceneHeraldic`
- `SceneOutro`

Textos, badges, cores, imagens e timing podem ser editados no Studio e gravados no TSX.

### 4. Media Staging portátil

- `src/engine/media_stager.py` copia mídia para `public/` com validação de path safety.
- `media.json` usa caminhos relativos à raiz do projeto.
- `episode_config.json` também usa caminhos relativos para cena, trilha, locução e SFX.
- `RemotionProvider` aceita `entry_point`, `public_dir`, `media_manifest` e `editable`.
- `staticFile()` nunca recebe caminho absoluto.
- SFX/VO remoto é preservado e resolvido via `resolveMediaSrc()`.

### 5. Legendas multi-ato

- Normalização de payloads `align-captions` act-keyed e flat.
- `CaptionChunk` aceita `id` e `duration`.
- `actTimelines` é derivado cumulativamente quando ausente.
- `SynchronizedCaptions` prefere atos quando o payload completo também traz `chunks` no topo.
- Payload flat `{metadata, words, chunks}` continua funcionando no template.

### 6. CLI e MCP

- `omnipress video --scaffold-editable [--force] [--render] [--aspect-ratio]`
- `omnipress studio --channel <slug> --episode <slug>`
- MCP: `omnipress_prepare_editable_video`
- `RemotionProvider.open_studio()` mantém o subprocesso na camada de provider.

---

## Correções relevantes

- `RemotionProvider` agora resolve corretamente a raiz do projeto (`parents[3]`).
- `duration_frames` não é mais fixado em recipes editáveis; o provider ignora `--frames` quando `editable=true`.
- Falha de staging não deixa mais um episódio parcial sem `meta.json`.
- Escaping seguro de aspas, barras e newlines em atributos JSX (vinheta e música).
- Volume de trilha respeita `backgroundMusicVolume` no intro, pausas e silêncio.
- Avisos explícitos para soundtrack, locução ou SFX ausentes.
- Normalização de `language` (`pt-BR` → `pt`) e `cameraDirection` (`slow_zoom_in` → `zoom-in`) para o union type do Remotion.
- Schema documental declara `sfx`, `sfx_volume`, `captions` objeto e voiceover string/objeto.

---

## Meta Unified Publishing Suite (incorporado do 0.11.0)

- `MetaPublisherAdapter` para Instagram Reels, Facebook Pages e Threads.
- Publicação direta via Meta Graph API e Threads API.
- Primeiro comentário automatizado no Instagram.
- `omnipress meta-auth` para descoberta e vinculação de ativos Meta.
- Ferramentas MCP `omnipress_meta_auth_inspect` e `omnipress_meta_auth_bind`.
- Active Health Check Gate pós-publicação com `get_post_status()` e `scheduling_log.json`.

---

## Validação executada

| Verificação | Resultado |
|---|---|
| `npm run typecheck` | ✅ |
| `uv run pytest -q` | ✅ **246 passed, 3 skipped** |
| `npx remotion versions` | ✅ 4.0.540 |
| `npx remotion compositions src/video/index.ts` | ✅ 12 composições |
| Render editável (19s, 1920×1080, AAC) | ✅ |
| Render template com Ken Burns + document-reveal + heráldica + outro | ✅ |
| Stills comparativos antes/depois | ✅ 0 px de diferença nos núcleos |
| Hash guard + backup | ✅ |
| Re-scaffold/render em cópia do projeto | ✅ |
| SFX/VO remoto no episódio editável | ✅ |
| `npm audit` | ✅ 0 vulnerabilidades |

---

## Limitações conhecidas

- A interação visual manual no Studio não é automatizada; recomenda-se um QA final no navegador.
- O render completo de documentários longos (8–30 min) não faz parte do smoke automatizado.
- Mídia externa à raiz do canal, em modo `render`, é incorporada ao card interno; em modo `manifest`, é rejeitada.
- `public/` staging não é podado automaticamente.
- A migração completa de `transform` para `translate/scale/rotate` nos componentes internos permanece como follow-up não material.

---

## Upgrade

```bash
npm install
npx remotion upgrade
uv sync
npm run typecheck
uv run pytest -q
```

Consulte também:

- [`CHANGELOG.md`](../CHANGELOG.md)
- [`docs/AGENT_MANUAL.md`](./AGENT_MANUAL.md)
- [`docs/REMOTION_SKILLS_AND_DOCS.md`](./REMOTION_SKILLS_AND_DOCS.md)
- [`channels/_template/video/README.md`](../channels/_template/video/README.md)
