# AGENTS.md — Guidelines for AI Coding Agents & Pair Programmers

> **Bilingual / Bilíngue**: This file provides strict operational rules for AI assistants (such as Antigravity) working on or utilizing the **OmniPress MCP** codebase.

---

## 🇺🇸 English Guidelines

### 1. Architectural Principles
- **KISS & DRY**: Keep adapters simple and avoid duplicate publishing logic.
- **Adapter Contract**: Any new social network or distribution channel must inherit from [`BasePublisherAdapter`](src/adapters/base.py) and implement:
  - `is_configured() -> bool`
  - `queue_social_post(...) -> dict`
- **Zero Hardcoded Secrets**: Never write API keys, profile IDs, or tokens into code. All credentials must be read from environment variables via `python-dotenv`.
- **Privacy & Legal Safety Gate (LGPD / Judicial Secrecy)**:
  - All content passing through `omnipress_publish_article` and `omnipress_queue_post` must be scanned via [`sanitize_text`](src/utils/sanitizer.py).
  - Never disable sanitization by default.

### 2. Tri-Format Content Standard
When an agent generates a content campaign, it must produce three synchronized assets:
1. **Long-Form Article**: Markdown with standard YAML frontmatter (title, date, category, tags, author, status).
2. **LinkedIn Post**: Attention-grabbing opening hook, 3–5 bulleted insights, discussion question, 3–5 hashtags.
3. **X Thread**: 3 to 5 connected micro-posts (hook, evidence, conclusion).

### 3. Modifying MCP Tools
- Do not break existing tool signatures in [`src/server.py`](src/server.py).
- Tool descriptions must be explicit, describing parameters and expected formats to guide LLM tool calling.

---

## 🇧🇷 Diretrizes em Português

### 1. Princípios de Arquitetura
- **KISS e DRY**: Mantenha os adaptadores simples e evite lógica de publicação duplicada.
- **Contrato de Adaptadores**: Qualquer novo canal deve herdar de [`BasePublisherAdapter`](src/adapters/base.py) e implementar:
  - `is_configured() -> bool`
  - `queue_social_post(...) -> dict`
- **Zero Segredos no Código**: Jamais insira chaves de API, IDs de perfis ou tokens no código-fonte. Sempre utilize variáveis de ambiente via `.env`.
- **Filtro de Privacidade e Ética (LGPD e Segredo de Justiça)**:
  - Qualquer texto processado para publicação deve passar por [`sanitize_text`](src/utils/sanitizer.py).
  - Nunca desabilite a sanitização por padrão. Processos judiciais no padrão CNJ (`0000000-00.0000.0.00.0000`), CPFs e CNPJs devem ser mascarados.

### 2. Padrão de Conteúdo Tri-Formato
Ao gerar campanhas de conteúdo, o agente deve produzir 3 formatos integrados:
1. **Artigo Completo**: Markdown com frontmatter YAML para Substack, Jusbrasil, Medium ou blogs estáticos.
2. **Post para LinkedIn**: Gancho forte inicial, 3 a 5 pontos objetivos, pergunta para engajamento e 3 a 5 hashtags.
3. **Thread para X**: Sequência de 3 a 5 posts curtos e de alto impacto.

### 3. Modificação das Ferramentas MCP
- Mantenha a retrocompatibilidade das ferramentas em [`src/server.py`](src/server.py).
- Docstrings devem ser claras e descritivas para orientar o modelo na seleção dos parâmetros.
