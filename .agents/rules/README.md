# Índice e Hierarquia Normativa de Regras — OmniPress MCP

Este diretório contém os padrões e regras operacionais para agentes de IA e desenvolvedores.

---

## Mapeamento de Regras e Diretrizes

| Regra / Norma | Título | Localização Canônica | Descrição Sumária |
|---|---|---|---|
| **Diretriz 01** | Princípios de Arquitetura | [`AGENTS.md`](../../AGENTS.md#1-architectural-principles) | KISS, DRY, Contrato de Adaptadores, Zero Segredos e Filtro de Privacidade (LGPD). |
| **Diretriz 02** | Padrão Tri-Formato | [`AGENTS.md`](../../AGENTS.md#2-tri-format-content-standard) | Produção sincronizada de Artigo Longo, Post LinkedIn e Thread X. |
| **Diretriz 03 / Regra 07** | Qualidade MCP e Glama TDQS 5.0 | [`07_mcp_quality_and_tdqs_standards.md`](./07_mcp_quality_and_tdqs_standards.md) | Nomenclatura verb_noun, anotações de hints (readOnly, destructive, idempotent), docstrings estruturadas. |
| **Diretriz 04** | Arquitetura Multi-Canal Agnóstica | [`AGENTS.md`](../../AGENTS.md#4-multi-channel-agnostic-architecture) | Isolamento em `channels/<slug>/`, separação entre motor universal (`src/`) e ativos do canal. |
| **Diretriz 05 / Regra 08** | Contraste Visual e Legibilidade | [`08_visual_contrast_and_carousel_legibility_standards.md`](./08_visual_contrast_and_carousel_legibility_standards.md) | Backdrop container protetor translúcido/opaco e safety typography stroke em carrosséis. |
| **Diretriz 06 / Regra 09** | Publicação Única (Anti-Duplicação) | [`09_single_publication_and_anti_duplicate_policy.md`](./09_single_publication_and_anti_duplicate_policy.md) | Verificação prévia mandatória (`list_posts`), exatamente-uma-vez e livro-razão de idempotência (PublishingShield). |
| **Diretriz 07 / Regra 10** | Motor de Vídeo Remotion | [`10_programmatic_video_and_remotion_engine.md`](./10_programmatic_video_and_remotion_engine.md) | Resolução dupla (16:9 e 9:16), duração padrão de 65s para monetização vertical, agnosticismo de marca por props e áudio com ducking cinemático. |
| **Diretriz 08 / Regra 11** | Sindicação Multi-CMS & CLI | [`AGENTS.md`](../../AGENTS.md#8-multi-cms-article-syndication--cli-standards-rule-11) | Contrato universal de artigos, sanitização de tags/tokens, diagnósticos com `doctor` e `status`. |
| **Diretriz 09 / Regra 12** | Motores Universais & Receitas | [`12_declarative_recipes_and_universal_engines.md`](./12_declarative_recipes_and_universal_engines.md) | Padrão declarativo anti-scripts; motores universais de carrossel, áudio broadcast (-14 LUFS), legendas e publicação. |

---

> [!NOTE]
> Os agentes devem consultar tanto o [`AGENTS.md`](../../AGENTS.md) quanto os arquivos normativos detalhados neste diretório para assegurar conformidade total antes de propor ou executar modificações.
