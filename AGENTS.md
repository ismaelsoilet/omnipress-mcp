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

### 3. Modifying MCP Tools & Protocol Standards (Rule 07)
- **Glama TDQS A+ (5.0) Standards**: All tools must comply with [`.agents/rules/07_mcp_quality_and_tdqs_standards.md`](.agents/rules/07_mcp_quality_and_tdqs_standards.md).
- **Mandatory Annotations**: `readOnlyHint`, `destructiveHint`, `idempotentHint`, and `openWorldHint` must be declared.
- **Canonical Naming**: Use canonical `verb_noun` format (`omnipress_publish_article`, `omnipress_queue_post`, `omnipress_inspect_content`, `omnipress_list_articles`).
- **Backward Compatibility**: Always maintain legacy aliases (`omnipress_list_recent`) in tool dispatchers.
- **Structured Guidance**: Docstrings and descriptions must specify `Use when:`, `Do NOT use when:`, and `Returns:`.

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

### 3. Modificação das Ferramentas MCP e Padrões de Protocolo (Regra 07)
- **Padrões Glama TDQS A+ (5.0)**: Todas as ferramentas devem cumprir [`.agents/rules/07_mcp_quality_and_tdqs_standards.md`](.agents/rules/07_mcp_quality_and_tdqs_standards.md).
- **Anotações Mandatórias**: Inclua `readOnlyHint`, `destructiveHint`, `idempotentHint` e `openWorldHint`.
- **Nomenclatura Canônica**: Padrão `verb_noun` (`omnipress_publish_article`, `omnipress_queue_post`, `omnipress_inspect_content`, `omnipress_list_articles`).
- **Compatibilidade Retroativa**: Mantenha aliases legados (`omnipress_list_recent`) nos despachantes.
- **Estruturação**: Descrições e docstrings devem conter `Use when:`, `Do NOT use when:` e `Returns:`.
