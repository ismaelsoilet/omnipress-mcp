# OmniPress MCP 0.13.0 — Internal Readiness & Agent Compatibility

**Data:** 2026-11-03  
**Foco:** uso interno, novas cenas, prune de staging e compatibilidade com Antigravity, Command Code e OpenCode.

---

## Resumo

A versão 0.13.0 fecha as lacunas funcionais do fluxo de edição interativa:

- Cenas dedicadas para mapas táticos, contadores estatísticos e clipes de vídeo.
- Prune automático de mídia antiga em episódios editáveis.
- Configuração plug-and-play para os três harnesses usados internamente.
- CI com smoke de composições Remotion.
- Documentação e versão sincronizadas.

Não há publicação de release/tag/PyPI nesta entrega.

---

## Novas cenas

| Cena | Componente | Props principais |
|---|---|---|
| `tactical-map` | `SceneTacticalMap` | `imageSrc`, `headline`, `badge`, `coordinates`, `accentColor` |
| `stat-counter` | `SceneStatCounter` | `value`, `prefix`, `suffix`, `label`, `headline`, `backgroundSrc`, `accentColor` |
| `video-clip` | `SceneVideoClip` | `videoSrc`, `headline`, `badge`, `overlayText`, `muted` |

Todas usam `Interactive.create()`, aparecem na timeline do Studio e são editáveis pelo Inspetor. O `EditableVideoEngine` gera o componente correto e faz o staging da mídia; o template `DocumentaryEpisode` também suporta os três tipos.

---

## Prune de staging

- `MediaStager.prune()` usa o índice `.staging-index.json` e remove somente arquivos gerados em execuções anteriores; arquivos do usuário, `.gitkeep` aninhados e diretórios do usuário são preservados.
- Episódios criados antes do índice existir não são podados automaticamente (migração segura).
- `prune_media: true` no recipe; episódios editáveis ativam automaticamente.
- Resultado inclui `pruned_files` no scaffold e `media_pruned` no provider.

---

## Compatibilidade de agentes

| Harness | Config | Skills |
|---|---|---|
| Antigravity | `.agents/mcp_config.json` / `~/.gemini/config/mcp_config.json` | `.agents/skills/` (workspace) / global opcional |
| Command Code | `.mcp.json` / `cmd mcp add` | `.agents/skills/` automático |
| OpenCode | `opencode.json` | `.agents/skills/` automático |

Consulte [`AGENT_COMPATIBILITY.md`](./AGENT_COMPATIBILITY.md) para snippets completos, prefixos de ferramentas e troubleshooting.

---

## Como usar

```bash
# 1. Gerar episódio editável
omnipress video --recipe episode_config.json \
  --channel <slug> --scaffold-editable

# 2. Abrir no Studio
omnipress studio --channel <slug> --episode <episode-slug>

# 3. Renderizar o resultado editado
omnipress video --recipe \
  channels/<slug>/video/episodes/<episode>-16x9/video_recipe.editable.json
```

Para Command Code/OpenCode/Antigravity, use as configurações de MCP do projeto e as skills em `.agents/skills/`.

---

## Validação

| Verificação | Resultado |
|---|---|
| `npm run typecheck` | ✅ |
| `uv run pytest -q` | ✅ 265 passed, 3 skipped |
| `npx remotion compositions src/video/index.ts` | ✅ 15 composições (com previews das novas cenas) |
| Fixture editável | ✅ typecheck + composição carregada |
| Prune de staging | ✅ testes de remoção indexada e preservação de arquivos do usuário |
| Configs de agentes | ✅ JSON, workspace Antigravity, OpenCode e Command Code cobertos por testes |

---

## Limitações

- WebMCP do Studio continua disponível apenas no Codex.
- O clique-a-clique do Studio não é automatizado.
- Render completo de documentários longos não faz parte do smoke.
- `@remotion/effects` não foi adotado.
- Não há release público/tag nesta versão.
