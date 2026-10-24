# OmniPress Content Factory — Índice de Agentes

> **Versão**: 1.0.0 | **Criado em**: 2026-10-24 | **Skill mestre**: `.agents/skills/content-factory/SKILL.md`

A Content Factory é uma esteira modular de 12 agentes especializados para produção de conteúdo audiovisual e editorial.  
Conteúdos simples usam apenas os agentes necessários. Conteúdos completos percorrem todos os estágios.

---

## Modos de Operação

| Modo | Agentes | Tempo | Caso de Uso |
|---|---|---|---|
| **Express** | AG12, AG01, AG04 | ~5 min | Posts, threads, artigos |
| **Standard** | AG12, AG01–05, AG10 | ~20 min | Short/Reel com voz |
| **Full Production** | Todos (AG01–AG12) | ~60–90 min | Episódio documentário |
| **Remix** | AG12, AG02, AG06–09, AG11 | ~30 min | Reedição de material existente |

---

## Índice dos Agentes

| ID | Arquivo | Papel | Ativa em |
|---|---|---|---|
| AG01 | `01_researcher_scriptwriter.md` | Pesquisador & Roteirista | Todos |
| AG02 | `02_image_curator.md` | Curador de Imagens | Standard, Full, Remix |
| AG03 | `03_audio_engineer.md` | Engenheiro de Áudio Broadcast | Standard, Full |
| AG04 | `04_language_reviewer.md` | Revisor Linguístico | Todos |
| AG05 | `05_timing_checker.md` | Checker de Timing | Standard, Full |
| AG06 | `06_visual_verifier.md` | Verificador Visual | Standard, Full, Remix |
| AG07 | `07_vfx_remotion.md` | VFX & Efeitos Especiais (Remotion) | Full, Remix |
| AG08 | `08_sfx_designer.md` | Designer de Efeitos Sonoros | Full, Remix |
| AG09 | `09_soundtrack_director.md` | Diretor de Trilha Sonora | Full, Remix |
| AG10 | `10_narration_director.md` | Diretor de Narração | Standard, Full |
| AG11 | `11_adversarial_auditor.md` | Auditor Adversarial | Full (obrigatório), Standard (recomendado) |
| AG12 | `12_director_orchestrator.md` | Diretor Delegador (Orquestrador) | **SEMPRE** (ponto de entrada) |

---

## Schemas de Handoff

Os contratos entre agentes são definidos em `.agents/schemas/`:

- `roteiro.schema.json` — Schema universal do roteiro (produzido por AG01)
- `production_log.schema.json` — Log de produção (mantido por AG12)
- `audit_report.schema.json` — Relatório de auditoria (produzido por AG11)

---

## Receitas Declarativas

As receitas em `.agents/recipes/` definem a configuração de cada modo:

- `express.json`
- `standard.json`
- `full_production.json`
- `remix.json`

---

## Gates de Aprovação do Usuário

1. **Gate de Formato** (após AG01): usuário escolhe entre 3 opções de formato
2. **Gate de Trilha** (após AG09): usuário aprova a trilha sonora — **NUNCA automático**

---

## Referência Rápida de Artefatos

```
channels/<slug>/episodios/<episode-slug>/
├── roteiros/
│   ├── roteiro.json          # AG01 → AG02, AG05, AG06, AG07, AG10
│   └── roteiro.md            # AG01 → AG04, AG10, AG12
├── image_manifest.json       # AG02 → AG05, AG06, AG07, AG11
├── audio_report.json         # AG03 → AG10, AG11
├── narration_report.json     # AG10 → AG03, AG12
├── language_review.json      # AG04 → AG11
├── timing_report.json        # AG05 → AG07, AG11
├── visual_qa_report.json     # AG06 → AG07, AG11
├── vfx_map.json              # AG07 → AG08, AG11
├── sfx_manifest.json         # AG08 → AG07, AG11
├── soundtrack_config.json    # AG09 → AG07, AG11
├── audit_report.json         # AG11 → AG12
└── production_log.json       # AG12 → Usuário

channels/<slug>/media/
├── visuals/                  # AG02 → Imagens curadas (cena_001_titulo.jpg)
├── voiceover/                # AG03 → Locução masterizada (-14 LUFS)
├── sfx/                      # AG08 → Efeitos sonoros baixados (-12dBFS)
└── soundtrack/               # AG09 → Faixa aprovada pelo usuário
```
