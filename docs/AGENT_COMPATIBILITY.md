# Compatibilidade com Agentes — Antigravity, Command Code e OpenCode

Este documento descreve como conectar o OmniPress MCP e carregar as skills do projeto nos três harnesses usados no dia a dia.

O OmniPress é um servidor MCP padrão via **stdio** (`python -m src.server`) e também suporta **HTTP/SSE** (`python src/server.py --http 3333`). As skills do projeto ficam em [`.agents/skills/`](../.agents/skills/) e usam o padrão Agent Skills (`SKILL.md`).

---

## 1. Pré-requisitos

```bash
# Dependências Python
uv sync

# Dependências Node/Remotion
npm install

# Diagnóstico
uv run omnipress doctor
```

O comando padrão do servidor é:

```bash
.venv/bin/python -m src.server
```

Todos os exemplos abaixo assumem que o repositório está em `/caminho/para/omnipress-mcp`. Ajuste o caminho se necessário.

---

## 2. Matriz de compatibilidade

| Harness | Config MCP | Skills | Observações |
|---|---|---|---|
| **Google Antigravity** | `.agents/mcp_config.json` (workspace) ou `~/.gemini/config/mcp_config.json` (global) | `.agents/skills/` (workspace) ou `~/.gemini/config/skills/<skill>/SKILL.md` (global) | Skills do workspace são carregadas automaticamente; global é opcional |
| **Command Code** | `.mcp.json` (project scope) ou `cmd mcp add` | `.agents/skills/` é lido automaticamente | `/skills`, `/mcp`; ferramentas com prefixo `mcp__omnipress__` |
| **OpenCode** | `opencode.json` (project) ou `~/.config/opencode/opencode.json` | `.agents/skills/` é lido automaticamente | Ferramenta `skill`; MCP local em `mcp` |
| **Claude Desktop** | `claude_desktop_config.json` | `~/.claude/skills/` | Compatibilidade legada |
| **Codex** | Configuração MCP do Codex | Skills por plugin | WebMCP do Studio só é suportado no Codex |

---

## 3. Google Antigravity

### 3.1 MCP

Use o arquivo **workspace** [`.agents/mcp_config.json`](../.agents/mcp_config.json). O `mcp_config.json` da raiz é mantido apenas como shim de compatibilidade.

```json
{
  "mcpServers": {
    "omnipress": {
      "command": ".venv/bin/python",
      "args": ["-m", "src.server"],
      "env": {
        "OMNIPRESS_ACTIVE_CHANNEL": "default"
      }
    }
  }
}
```

Para disponibilidade global, copie o mesmo bloco para `~/.gemini/config/mcp_config.json` e use um caminho absoluto para o interpretador.

### 3.2 Skills

O Antigravity carrega skills do workspace em `.agents/skills/` automaticamente. A exposição global em `~/.gemini/config/skills/` é **opcional**, útil apenas para reutilizar as skills em outros projetos.

Se quiser expor globalmente:

```bash
mkdir -p ~/.gemini/config/skills
for skill in .agents/skills/*/; do
  ln -sfn "$(pwd)/$skill" "$HOME/.gemini/config/skills/$(basename "$skill")"
done
```

### 3.3 Prompt de exemplo

> Use a skill `omnipress` para gerar um episódio documental editável a partir de `channels/<slug>/episodios/<ep>/documentario/episode_config.json`, abra no Studio e renderize após a edição.

---

## 4. Command Code

### 4.1 MCP via `.mcp.json` (project scope)

O arquivo [`.mcp.json`](../.mcp.json) já está no projeto:

```json
{
  "mcpServers": {
    "omnipress": {
      "transport": "stdio",
      "command": ".venv/bin/python",
      "args": ["-m", "src.server"],
      "env": {
        "OMNIPRESS_ACTIVE_CHANNEL": "default"
      }
    }
  }
}
```

Alternativa via CLI:

```bash
cmd mcp add --env OMNIPRESS_ACTIVE_CHANNEL=default omnipress \
  -- .venv/bin/python -m src.server

# Verificar
cmd mcp list
cmd mcp get omnipress
```

As ferramentas aparecem com prefixo `mcp__omnipress__<tool>`, por exemplo:

```text
mcp__omnipress__omnipress_publish_article
mcp__omnipress__omnipress_prepare_editable_video
mcp__omnipress__omnipress_render_video
```

### 4.2 Skills

Command Code lê `.agents/skills/` automaticamente. Não é necessário copiar nada.

```text
/skills          # lista as skills
/skill:omnipress # executa a skill mesmo se houver colisão de nome
```

Se você já configurou OpenCode, o Command Code também pode importar:

```text
/import opencode
```

### 4.3 Prompt de exemplo

> Use a skill `omnipress-youtube-documentary` para produzir o episódio. Depois use `mcp__omnipress__omnipress_prepare_editable_video` e abra o Studio.

---

## 5. OpenCode

### 5.1 MCP via `opencode.json`

O arquivo [`opencode.json`](../opencode.json) já está no projeto:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "omnipress": {
      "type": "local",
      "command": [".venv/bin/python", "-m", "src.server"],
      "enabled": true,
      "environment": {
        "OMNIPRESS_ACTIVE_CHANNEL": "default"
      }
    }
  }
}
```

Alternativa global: `~/.config/opencode/opencode.json` com o mesmo bloco `mcp`.

### 5.2 Skills

OpenCode lê `.agents/skills/` do projeto automaticamente, além de `.opencode/skills/`, `.claude/skills/` e `~/.agents/skills/`.

```text
Use the skill tool to load `omnipress` and follow its runbook.
```

### 5.3 Prompt de exemplo

> Use a skill `omnipress` e a ferramenta `omnipress_prepare_editable_video` para criar o episódio editável. Depois rode `omnipress studio --channel <slug> --episode <slug>`.

---

## 6. Ferramentas novas de vídeo

### Gerar episódio editável

```bash
omnipress video --recipe <episode_config.json> \
  --channel <slug> --scaffold-editable
```

### Abrir no Studio

```bash
omnipress studio --channel <slug> --episode <episode-slug>
```

### Renderizar o episódio editado

```bash
omnipress video --recipe \
  channels/<slug>/video/episodes/<episode>-16x9/video_recipe.editable.json
```

### MCP equivalente

```text
omnipress_prepare_editable_video(
  recipe_path=".../episode_config.json",
  channel_slug="<slug>",
  aspect_ratio="16:9",
  force=False
)
```

---

## 7. WebMCP do Remotion Studio

O Remotion 4.0.540 expõe ferramentas WebMCP dentro do Studio (selecionar cena, seek, render jobs, transcrição). Entre os harnesses principais, **apenas o ChatGPT Codex suporta WebMCP**; OpenCode e Command Code ainda não. Não construa automação dependente disso. O fluxo `omnipress studio` continua sendo manual para humanos.

---

## 8. Verificação rápida

```bash
# Servidor MCP
.venv/bin/python -m src.server --help

# Versão
uv run omnipress --version

# Composições Remotion
npm run remotion:compositions

# Testes
uv run pytest -q
```

Se o agente não encontrar as ferramentas:

1. Confirme o caminho absoluto do `.venv/bin/python`.
2. Rode o servidor manualmente e veja se há erro de import.
3. Verifique `OMNIPRESS_ACTIVE_CHANNEL` e o `channel.json` do canal.
4. Em Command Code/OpenCode, confirme que o MCP está `enabled`.
5. Em Antigravity, confirme `.agents/mcp_config.json` (workspace) e `.agents/skills/<skill>/SKILL.md`; `~/.gemini/config/` é o fallback global.
