# 🚀 Guia de Submissão e Publicação do OmniPress MCP

Este guia contém as instruções passo a passo e os templates prontos para publicar e registrar o **OmniPress MCP** nos principais registries, marketplaces e diretórios globais do ecossistema MCP.

---

## 1. Publicação no PyPI (Python Package Index)

A publicação no PyPI permite que qualquer desenvolvedor execute o OmniPress com `uvx omnipress-mcp` ou instale via `pip install omnipress-mcp` sem precisar clonar o repositório.

### Opção A: Publicação Automática via GitHub Actions (Recomendada)
O repositório já inclui o workflow [`.github/workflows/release.yml`](../.github/workflows/release.yml) configurado com **PyPI Trusted Publishing**:
1. Acesse sua conta em [pypi.org/manage/account/publishing/](https://pypi.org/manage/account/publishing/).
2. Adicione um novo *Trusted Publisher*:
   - **PyPI Project Name**: `omnipress-mcp`
   - **Owner**: `ismaelsoilet`
   - **Repository name**: `omnipress-mcp`
   - **Workflow name**: `release.yml`
   - **Environment**: `pypi`
3. Crie e envie uma tag Git no terminal:
   ```bash
   git tag v0.1.0
   git push origin v0.1.0
   ```
4. O GitHub Actions executará os testes, compilará os wheels e publicará automaticamente no PyPI e no GHCR.

### Opção B: Publicação Manual via `uv`
```bash
# 1. Gerar os pacotes de distribuição (.tar.gz e .whl)
uv build

# 2. Publicar diretamente usando seu API Token do PyPI
uv publish --token pypi-SEU_TOKEN_AQUI
```

---

## 2. Registro no Official MCP Registry (`registry.modelcontextprotocol.io`)

O **Official MCP Registry** é o catálogo primário padronizado pelo consórcio MCP. O arquivo de metadados [`server.json`](../server.json) já está criado na raiz do repositório.

### Passo a Passo:
1. Instale a ferramenta oficial `mcp-publisher`:
   ```bash
   # Via npm
   npx @modelcontextprotocol/publisher login github
   ```
2. Autorize a aplicação no seu navegador via GitHub Device Flow (`https://github.com/login/device`).
3. Na raiz do repositório `omnipress-mcp`, publique os metadados:
   ```bash
   npx @modelcontextprotocol/publisher publish
   ```
4. Verifique a listagem no endpoint REST público:
   ```bash
   curl "https://registry.modelcontextprotocol.io/v0.1/servers?search=io.github.ismaelsoilet/omnipress-mcp"
   ```

---

## 3. Publicação no Smithery.ai

O **Smithery** é o principal marketplace de instalação em 1-clique (`npx -y @smithery/cli install omnipress-mcp`). O arquivo [`smithery.yaml`](../smithery.yaml) já está na raiz do projeto.

### Passo a Passo:
1. Acesse **[smithery.ai/new](https://smithery.ai/new)**.
2. Conecte sua conta do GitHub e selecione o repositório `ismaelsoilet/omnipress-mcp`.
3. O Smithery lerá automaticamente o `smithery.yaml`, validará o schema de variáveis (`BUFFER_API_KEY`, `DEVTO_API_KEY`, etc.) e gerará a página oficial do servidor.
4. Como alternativa via CLI:
   ```bash
   npx -y @smithery/cli publish
   ```

---

## 4. Cadastro no Glama.ai (TDQS 5.0 A+)

O **Glama** avalia a qualidade semântica das ferramentas MCP. O OmniPress MCP foi projetado para nota máxima (**5.0 / A+**).

### Passo a Passo:
1. Acesse **[glama.ai/mcp/hosting](https://glama.ai/mcp/hosting)**.
2. Conecte o repositório `ismaelsoilet/omnipress-mcp`.
3. O Glama indexará as 14 ferramentas, detectará as anotações (`readOnlyHint`, `idempotentHint`, etc.) e validará as docstrings (`Use when`, `Do NOT use when`, `Returns`).
4. Ative a visibilidade pública para listar o OmniPress no diretório oficial da Glama.
5. Copie o badge gerado e adicione ao topo do `README.md`.

---

## 5. Submissão ao `punkpeye/awesome-mcp-servers`

O repositório **[punkpeye/awesome-mcp-servers](https://github.com/punkpeye/awesome-mcp-servers)** é a lista curada mais famosa da comunidade MCP.

### Passo a Passo:
1. Faça um Fork do repositório: `https://github.com/punkpeye/awesome-mcp-servers`.
2. Edite o arquivo `README.md` adicionando a linha abaixo na seção **Content & Media** ou **Publishing / Marketing**:

```markdown
- [OmniPress MCP](https://github.com/ismaelsoilet/omnipress-mcp) - Universal agentic publishing protocol and media distribution engine. Transforms briefings into long-form articles (Dev.to, Ghost, Markdown), 3:4 high-contrast social carousels (Instagram, LinkedIn), and viral videos (Remotion, TTS).
```

3. Abra um Pull Request com o título:
   `Add OmniPress MCP to Content & Publishing servers`
4. Descrição do PR:
   ```markdown
   ### Add OmniPress MCP Server

   - **Name**: OmniPress MCP
   - **Repository**: https://github.com/ismaelsoilet/omnipress-mcp
   - **Category**: Content & Media / Publishing
   - **Description**: Universal agentic publishing protocol, multi-network social syndication, and programmatic media engine for AI agents via Model Context Protocol (MCP).
   - **Quality Standards**: Full compliance with Glama TDQS 5.0, PublishingShield anti-duplicate ledger, and LGPD/secrets sanitization.
   ```
