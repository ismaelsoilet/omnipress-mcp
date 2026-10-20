# Regra 13 — Padrão de Atualização Contínua de Documentação, Versionamento Semântico e Release

> **Norma Operacional Obrigatória**: Qualquer alteração de código, nova funcionalidade, expansão de motor universal, novo adaptador ou melhoria de template no **OmniPress MCP** deve obrigatoriamente acompanhar a atualização simultânea de documentação, registro em changelog e incremento de versão (SemVer).

---

## 🎯 1. Princípio da Documentação Viva e Sincronizada

No OmniPress MCP, **o código e a documentação são uma única entidade indissociável**.
Um recurso sem documentação atualizada é considerado código incompleto e com falha de qualidade.

### Proibições Estritas:
- ❌ **Proibido Commitar sem Documentar**: Jamais submeter commits com novas ferramentas MCP, novos comandos de CLI, novos presets visuais ou novos adaptadores sem atualizar o `README.md`, o `CHANGELOG.md` e o `docs/AGENT_MANUAL.md`.
- ❌ **Proibido Desincronizar Versões**: Jamais alterar a versão em um arquivo (ex.: apenas no `pyproject.toml`) deixando os demais desatualizados.
- ❌ **Proibido Changelog Vago**: Registros como "pequenos ajustes", "correções" ou "update" são inaceitáveis. O changelog deve seguir o padrão *Keep a Changelog* com seções explícitas (`Added`, `Changed`, `Fixed`, `Deprecated`, `Removed`).

---

## 🏷️ 2. Versionamento Semântico (SemVer)

O OmniPress adota rigorosamente a especificação [SemVer 2.0.0](https://semver.org/):

$$\text{MAJOR} . \text{MINOR} . \text{PATCH}$$

| Nível | Quando Incrementar | Exemplos no OmniPress |
|---|---|---|
| **PATCH** (`0.3.x`) | Correções de bugs, pequenas melhorias de teste, refatorações internas sem alteração de contratos ou interfaces. | Ajuste de regex no sanitizador, fix de cálculo de padding no Pillow, melhoria de fallback de fontes. |
| **MINOR** (`0.x.0`) | Novas funcionalidades, novos presets visuais, novos motores, novos adaptadores de publicação, novos comandos CLI com compatibilidade retroativa mantida. | Introdução dos 4 presets visuais (`tweet_card`, `minimal_dark`, `split_editorial`), suporte a arquétipos de canais (`personal_brand`), adição de motores universais. |
| **MAJOR** (`x.0.0`) | Alterações que quebram compatibilidade retroativa (breaking changes), remoção de ferramentas MCP legadas sem fallback, reestruturação profunda de esquemas de canais. | Mudança incompatível na API de contratos MCP, alteração estrutural no `channel.json` que invalide workspaces legados. |

---

## 📂 3. Checklist Obrigatório de Arquivos de Versão

Ao realizar qualquer bump de versão, o agente deve sincronizar simultaneamente todos os arquivos canônicos:

1. [`pyproject.toml`](../../pyproject.toml): Campo `version = "x.y.z"`.
2. [`package.json`](../../package.json): Campo `"version": "x.y.z"`.
3. [`package-lock.json`](../../package-lock.json): Campos `"version": "x.y.z"`.
4. [`src/__init__.py`](../../src/__init__.py): Constante `__version__ = "x.y.z"`.
5. [`server.json`](../../server.json): Campos de versão do manifesto MCP.
6. [`plugin.json`](../../plugin.json): Campo de versão do plugin.
7. [`src/server.py`](../../src/server.py): Resposta do tool info / server metadata.
8. [`src/cli.py`](../../src/cli.py): Flag `--version`.
9. [`config/openapi.json`](../../config/openapi.json): Versão da API OpenAPI.
10. [`CHANGELOG.md`](../../CHANGELOG.md): Nova seção com data `## [x.y.z] — YYYY-MM-DD`.

---

## 📝 4. Checklist Obrigatório de Documentação

Toda alteração que introduza ou modifique capacidades deve refletir nos seguintes documentos:

1. **[`README.md`](../../README.md)**:
   - Badges de versão atualizados.
   - Diagrama de arquitetura revisado se houver novos componentes.
   - Tabela de motores universais e ferramentas MCP atualizada.
   - Exemplos reais de uso (com snippets e comandos CLI).
2. **[`CHANGELOG.md`](../../CHANGELOG.md)**:
   - Descrição detalhada dos recursos adicionados (`### Added`), modificados (`### Changed`) e corrigidos (`### Fixed`).
   - Links para os issues ou PRs relevantes quando aplicável.
3. **[`docs/AGENT_MANUAL.md`](../../docs/AGENT_MANUAL.md)**:
   - Playbooks de execução atualizados para que outros agentes de IA saibam invocar os novos motores e presets.
   - Exemplos de receitas e formatos suportados.
4. **[`channels/_template/`](../../channels/_template/)**:
   - `channel.json` deve conter os novos campos e tokens de configuração.
   - `style_guide.md` deve refletir as diretrizes estéticas mais recentes.
   - Pastas de exemplo e receitas modelo em `campanhas/` e `episodios/` devem ser atualizadas.

---

## 🚀 5. Protocolo de Commit e Release

Ao finalizar a implementação e a documentação sincronizada:
1. Executar a suíte de testes completa (`pytest`) garantindo 100% de aprovação.
2. Criar commit descritivo no padrão **Conventional Commits**:
   - Exemplo: `feat(visual): implement multi-preset carousel system and bump to v0.4.0`
3. Incluir corpo do commit detalhando cada módulo alterado.
4. Realizar o push para o branch principal (`origin main`).
