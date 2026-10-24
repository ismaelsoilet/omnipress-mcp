---
name: content-factory
description: >
  Skill mestre da OmniPress Content Factory. Orquestra os 12 agentes especializados
  para produzir conteúdo audiovisual completo — de Shorts de 65s a documentários de
  30min — seguindo o pipeline de qualidade broadcast. Ativa o AG12 (Diretor) como
  ponto de entrada. Conteúdos simples usam apenas os agentes necessários.
---

# OmniPress Content Factory — Runbook Mestre

Use esta skill sempre que o usuário quiser produzir qualquer tipo de conteúdo audiovisual,
editorial ou social usando a esteira de agentes da Content Factory.

---

## 0. Ponto de Entrada Obrigatório — AG12 (Diretor)

Antes de qualquer ação, o **AG12 (Diretor Delegador)** DEVE ser ativado.
Ele é o único agente que interage diretamente com o usuário.
Leia `.agents/agents/12_director_orchestrator.md` para as regras completas de delegação.

**Nunca pule o AG12.** Ele determina o modo correto, os gates de aprovação e a ordem de execução.

---

## 1. Identificação do Modo de Operação

O AG12 analisa o briefing e seleciona o modo automaticamente:

| Sinal no briefing | Modo selecionado |
|---|---|
| "post", "thread", "artigo", "carrossel" | **Express** |
| "short", "reel", "vídeo curto", "vertical" | **Standard** |
| "documentário", "episódio", "longo", "YouTube" | **Full Production** |
| "reeditar", "remix", "usar o que já tenho" | **Remix** |

Quando ambíguo: AG12 apresenta as 4 opções ao usuário e aguarda escolha.

---

## 2. Agentes por Modo — Referência Rápida

### Express (5 min)
```
AG12 → AG01 [pesquisa + roteiro] → [GATE: usuário aprova] → AG04 [revisão] → entrega
```

### Standard (~20 min)
```
AG12 → AG01 [roteiro] → [GATE: formato] →
  parallel: AG02 [imagens] + AG10 [narração] → AG03 [masterização]
  → AG04 [revisão] + AG05 [timing]
  → AG11 [auditoria anti-duplicação e timing]
  → [GATE: usuário aprova] → publicar
```

### Full Production (~60–90 min)
```
AG12 → AG01 [roteiro] → [GATE: formato] →
  parallel: AG02 [imagens] + AG10 [narração] → AG03 [masterização]
  → AG04 + AG05 + AG06 [QA em paralelo]
  → AG07 [VFX] + AG08 [SFX]
  → AG09 [trilha] → [GATE: usuário aprova trilha]
  → AG11 [auditoria adversarial]
  → [score ≥ 80] → entrega final
```

### Remix (~30 min)
```
AG12 → (AG01 opcional se houver reescrita do roteiro)
  → AG02 [novas imagens] + AG07 [novos VFX]
  → AG08 [SFX] → AG09 [trilha] → [GATE: trilha]
  → AG06 [verificação visual] → AG11 [auditoria]
  → entrega
```

---

## 3. Schemas de Handoff (Contratos entre Agentes)

Todos os artefatos de handoff seguem schemas em `.agents/schemas/`:

| Schema | Path | Produzido por | Consumido por |
|---|---|---|---|
| `roteiro.schema.json` | `.agents/schemas/` | AG01 | AG02, AG05, AG06, AG07, AG10 |
| `production_log.schema.json` | `.agents/schemas/` | AG12 | Usuário |
| `audit_report.schema.json` | `.agents/schemas/` | AG11 | AG12 |

Artefatos intermediários produzidos pelos agentes:

| Arquivo | Produzido por | Consumido por |
|---|---|---|
| `roteiro.json` | AG01 | AG02, AG05, AG06, AG07, AG10 |
| `roteiro.md` | AG01 | AG04, AG10, AG12 |
| `image_manifest.json` | AG02 | AG05, AG06, AG07, AG11 |
| `whisper.json` | AG03 (pós-masterização) | AG04, AG05 |
| `audio_report.json` | AG03 | AG10, AG11 |
| `narration_report.json` | AG10 | AG03, AG12 |
| `language_review.json` | AG04 | AG11, AG12 |
| `timing_report.json` | AG05 | AG07, AG11 |
| `visual_qa_report.json` | AG06 | AG07, AG11 |
| `vfx_map.json` | AG07 | AG08, AG11 |
| `sfx_manifest.json` | AG08 | AG07, AG11 |
| `soundtrack_config.json` | AG09 | AG07, AG11 |
| `audit_report.json` | AG11 | AG12 |
| `production_log.json` | AG12 | Usuário |

---

## 4. Gates de Aprovação do Usuário

Existem **2 gates obrigatórios** onde a produção PARA e aguarda o usuário:

### Gate 1 — Formato do Conteúdo (AG01 → Usuário)
Disparado após AG01 concluir a pesquisa inicial.
AG01 apresenta **3 opções de formato** com justificativa.
Usuário escolhe. Somente então AG01 escreve o roteiro completo.

### Gate 2 — Trilha Sonora (AG09 → Usuário)  
Disparado após AG09 analisar o roteiro.
AG09 apresenta **5 sugestões de trilha** com mood, licença e risco de Content ID.
Usuário escolhe ou declina (Modo B: sem trilha).
**Nunca pular este gate.**

---

## 5. Critérios de Entrega Final

A entrega só ocorre quando:
1. `audit_report.json` tem `score ≥ 80` e `aprovado: true`
2. `audio_report.json` tem `lufs_integrated` entre -14.0 e -16.0 (se há áudio)
3. `timing_report.json` tem `duracao_ok: true` (se há vídeo)
4. `visual_qa_report.json` tem zero itens em `rejeitadas` (se há imagens)
5. Trilha sonora aprovada explicitamente pelo usuário ou Modo B declarado

---

## 6. Conformidade com AGENTS.md

Esta factory opera sob as seguintes regras obrigatórias do AGENTS.md:

- **Regra 08**: Contraste visual — todo texto sobre imagem usa backdrop card `rgba(8,10,14,215)`
- **Regra 09**: Anti-duplicação — AG12 verifica `list_posts` antes de qualquer publicação
- **Regra 10**: Áudio broadcast — AG03 obrigatório quando há voz; -14 LUFS; volume de trilha 0.12–0.18 sob voz
- **Regra 12**: Declarative-first — usar receitas em `.agents/recipes/`, nunca scripts avulsos
- **Regra 13**: Documentação — qualquer novo template ou episódio atualiza CHANGELOG.md

---

## 7. Referências dos Agentes

Leia o arquivo de definição de cada agente antes de ativá-lo:

- AG01: `.agents/agents/01_researcher_scriptwriter.md`
- AG02: `.agents/agents/02_image_curator.md`
- AG03: `.agents/agents/03_audio_engineer.md`
- AG04: `.agents/agents/04_language_reviewer.md`
- AG05: `.agents/agents/05_timing_checker.md`
- AG06: `.agents/agents/06_visual_verifier.md`
- AG07: `.agents/agents/07_vfx_remotion.md`
- AG08: `.agents/agents/08_sfx_designer.md`
- AG09: `.agents/agents/09_soundtrack_director.md`
- AG10: `.agents/agents/10_narration_director.md`
- AG11: `.agents/agents/11_adversarial_auditor.md`
- AG12: `.agents/agents/12_director_orchestrator.md`

Receitas: `.agents/recipes/` (express.json, standard.json, full_production.json, remix.json)
