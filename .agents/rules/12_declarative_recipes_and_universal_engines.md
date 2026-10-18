# Rule 12 — Declarative-First Execution Engines & Anti-Script Standard

> **Scope**: Universal execution engines, CLI commands, declarative recipes, and anti-script architecture.  
> **Authority**: Mandatory standard for all AI agents and developers operating in OmniPress MCP.

---

## 1. Context & Motivation

Historically, creating creative assets across media channels (carousels, shorts, articles, voiceovers) led agents to generate bespoke procedural Python scripts for each individual post (e.g., `render_carousel_*.py`, `upload_carousel_*.py`, `schedule_carousel_*.py`).

Across 30 carousels, this spawned over 90 repetitive scripts duplicating PIL image manipulation, multipart HTTP uploads, hardcoded paths, exposed third-party API keys, and bypassed central safety gates.

**Rule 12 establishes the Declarative-First Publishing Standard:**
Content and campaigns are defined declaratively via structured instruction manifests (`recipe.json`), while generation, audio mastering, CDN upload, and syndication are executed exclusively by the core **Universal Execution Engines**.

---

## 2. Core Mandatory Guidelines

### 2.1 Zero Disposable Scripts for Standard Assets
- **Strictly Prohibited**: Agents must NEVER write ad-hoc `render_*.py`, `upload_*.py`, or `schedule_*.py` scripts to generate or publish standard carousels, audio tracks, or social posts.
- **Declarative Specification**: All standard assets must be authored as JSON/YAML recipes (see canonical templates in `channels/_template/`).

### 2.2 Invocations via Core Universal Engines
Agents must trigger production pipelines using the core CLI commands or their Python engine counterparts in `src/engine/`:

1. **Carousels**:
   ```bash
   omnipress carousel --recipe channels/<slug>/media/carousels/<post>/carousel_recipe.json --all
   ```
   - Automatically crops and prepares background images (with `top_bias` and contrast boost).
   - Renders slides with Rule 08 protective cards and safety typography strokes.
   - Uploads to configured CDN (S3/R2 or Catbox fallback).
   - Verifies character limits and PublishingShield anti-duplicate protection before scheduling.

2. **Studio Audio Voiceover Mastering**:
   ```bash
   omnipress master-audio <raw_voice.m4a> -o <master_voice.mp3> [--target-lufs -14.0]
   ```
   - Enforces the 6-stage studio mastering chain from Rule 10 (adeclick, 80Hz highpass, afftdn, 4-band surgical EQ, compression, EBU R128 loudness locking to strictly -14.0 LUFS).

3. **Whisper Caption Alignment & Chunking**:
   ```bash
   omnipress align-captions <whisper_raw.json> -o <captions_clean.json>
   ```
   - Standardizes word timestamps and groups them into 2-to-4 word high-retention chunks for Remotion vertical videos.

4. **Multi-Channel Publishing**:
   ```bash
   omnipress publish --recipe channels/<slug>/articles/<post>/post_recipe.json
   ```
   - Applies Rule 01 privacy sanitization (masking CPFs, CNPJs, CNJ judicial process numbers).
   - Checks Rule 09 anti-duplicate ledger (`PublishingShield`).
   - Dispatches across Buffer, Instagram, Dev.to, or Ghost.

### 2.3 Channel Workspace Flexibility
- The existence of Universal Engines does NOT prevent channels from creating custom scripts in `channels/<slug>/scripts/` when a task is genuinely bespoke (such as proprietary data scraping, specialized third-party API integrations, or non-standard experimental visual formats).
- However, standard production tasks must ALWAYS leverage the universal engines in the core repo.
