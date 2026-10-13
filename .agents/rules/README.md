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
| **Diretriz 06 / Regra 09** | Publicação Única (Anti-Duplicação) | [`09_single_publication_and_anti_duplicate_policy.md`](./09_single_publication_and_anti_duplicate_policy.md) | Verificação prévia mandatória (`list_posts`), exatamente-uma-vez e substituição limpa. |
| **Diretriz 07 / Regra 10** | Motor de Vídeo Remotion | [`AGENTS.md`](../../AGENTS.md#7-programmatic-video--remotion-engine-rule-10) | Resolução dupla (16:9 e 9:16), agnosticismo de marca por props e áudio com ducking cinemático. |

---

> [!NOTE]
> Os agentes devem consultar tanto o [`AGENTS.md`](../../AGENTS.md) quanto os arquivos normativos detalhados neste diretório para assegurar conformidade total antes de propor ou executar modificações.
