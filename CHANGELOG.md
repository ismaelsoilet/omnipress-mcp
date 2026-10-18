# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] — 2026-10-18

### Added
- **Universal Declarative Execution Engines (Rule 12)**:
  - Universal Carousel Engine (`src/engine/universal_carousel.py`): Aspect ratio bias auto-formatting, dynamic backdrop cards, CDN uploading, and Buffer scheduling.
  - Universal Audio Mastering Engine (`src/engine/universal_audio.py`): EBU R128 (-14.0 LUFS target, <= -1.2 dBTP), 4-band surgical EQ (140Hz warmth, 300Hz de-box, 3kHz presence, 8.5kHz air), dynamic broadcast compression, and speech-aware pause de-breather.
  - Universal Captions Engine (`src/engine/universal_captions.py`): Whisper timestamp parser supporting multi-act structures, 2-4 word kinetic chunking, and Remotion subtitle JSON generation.
  - Universal Multi-Platform Publisher (`src/engine/universal_publisher.py`): Multi-channel publisher with privacy sanitization and PublishingShield anti-duplicate protection.
  - Declarative recipes in `channels/_template/`: `carousel_recipe.json` and `post_recipe.json`.
- **Packaging & Hardening (SureForge Adversarial Round 2)**:
  - Added `.dockerignore` blocking `.env*`, `.git`, `.venv`, `channels/`, `.agents/`, `node_modules/`, `dist/`.
  - Added sdist excludes in `pyproject.toml` preventing internal assets leakage.
  - Integrated `src/engine/dark_media.py` directly into core engine.
  - Expanded `sanitize_text` with modern multi-segment gTLDs (`.technology`, `.solutions`), OpenAI/AWS/GitHub PAT/Ghost token detection.
  - Eliminated 30-word false-positive collisions in `PublishingShield.generate_fingerprint`.
  - Enforced strict Rule 10 ducking ceiling (`0.16`) and fixed Remotion React 19 loose component type compatibility.
  - Fixed multi-channel partial failures and ledger recording in `BufferAdapter`.
  - Implemented `BasePublisherAdapter` on `MarkdownAdapter`.

### Changed
- **Decoupled Channel Assets from Core Engine**:
  - Purged 24,000+ lines of channel-specific Whisper timestamps, configs, and audio assets from git tracking.
  - Refactored `src/video/Root.tsx` into a clean, brand-agnostic video engine template exposing universal compositions.
  - Decoupled `src/cli.py` fallback channels and `src/video/compositions/` default properties from hardcoded channel references.
  - Preserved historical channel assets securely in git-ignored `channels/dossie-historico/` workspace.
- **Canonical Channel Workspace Template (`channels/_template/`)**:
  - Expanded `channels/_template/` with full directory hierarchy for multi-channel scaling.


---

## [0.2.0] — 2026-10-17

### Added
- **Full Video Creation & Motion Graphics Skills Suite**:
  - Integrated 12 official Remotion Agent Skills (`remotion-dev/skills`) into `.agents/skills/`:
    - `remotion-best-practices`: Universal routing and video best practices.
    - `remotion-markup`: Animation with `interpolate()`, `spring()`, `useCurrentFrame()`, and CSS shorthands (`scale`, `translate`, `rotate`).
    - `remotion-captions`: Dynamic subtitle synchronization with Whisper word-level timestamps.
    - `remotion-docs`: Real-time official documentation lookup via Algolia Search API and `.md` retrieval convention.
    - `remotion-studio`: Interactive video preview in browser.
    - `remotion-render`: CLI video and still frame rendering.
    - `remotion-create`: Template and composition scaffolding.
    - `remotion-interactivity`: Making compositions editable directly in Remotion Studio.
    - `remotion-maps`: Animated maps and 3D flyovers (Mapbox, MapLibre, MapTiler, CesiumJS).
    - `remotion-multimedia`: Media inspection with Mediabunny.
    - `remotion-saas`: Architecture for web player and cloud rendering.
    - `remotion-upgrade`: Continuous ecosystem and skill upgrades.
- **Short-Form Vertical Video Skills Suite (TikTok, Reels & Shorts)**:
  - `viral-hooks`: 3-layer opening hook (visual, verbal, on-screen text) and proven creator frameworks.
  - `viral-youtube-shorts`: Shorts Feed optimization, VVSA metric (>70%), and long-form funnel bridging.
  - `viral-instagram-reels`: Instagram signal hierarchy (watch time, sends per reach), Trial Reels, and originality.
  - `viral-tiktok-content`: FYP pacing, completion rate math (>60s Creator Rewards), and trending audio.
  - `viral-captions-and-ctas`: Send/save-driving CTAs and muted watching captions.
  - `viral-short-form`: 4-stage retention architecture (Hook -> Escalation -> Payoff -> CTA).
  - `viral-short-form-ideas`: Volume ideation matrix and multi-angle topic expansion.
  - `reel-export`: 9:16 vertical exports with UI Safe Zones, H.264, yuv420p, bt709, and ffprobe validation.
- **YouTube Long-Form & Documentary Video Skills Suite**:
  - `omnipress-youtube-documentary`: Master runbook for 8–30+ minute documentaries (5-Act narrative arc, 0–30s hook window, pattern interrupts every 45–60s, visual variety every 3–5s, chapter cliffhangers, and Remotion rendering).
  - `technical-video-script`: Two-column beat sheet (visual/SFX vs narration), 30s hook, and YouTube timestamps.
  - `vox-explainer`: Visual journalism style (halftone, torn paper, bold typography, motion on twos).
  - `documentary-montage-production`: Source logging (`claim_id`), fact checking, and ethical archival use.
  - `cinematic-trailer-production`: Tension curves, audio-visual escalation, and teaser structures.
  - `youtube-thumbnail-design`: 120px mobile preview test, 3-element focal rule, and contrast optimization.
- **Documentation**:
  - Created [`docs/REMOTION_SKILLS_AND_DOCS.md`](docs/REMOTION_SKILLS_AND_DOCS.md): Reference guide for Remotion skills and live documentation protocols.
  - Created [`docs/VIDEO_CREATION_AND_PLATFORM_SKILLS.md`](docs/VIDEO_CREATION_AND_PLATFORM_SKILLS.md): Unified video platform guide for YouTube, TikTok, Reels, Shorts, and Documentaries.
  - Documented Image Sourcing & External Generation Protocol in `10_programmatic_video_and_remotion_engine.md` and `AGENTS.md`.
- **Compositions**:
  - Registered `DocumentaryShort-05-Mincemeat-9x16` in `src/video/Root.tsx` with 13 historical scenes, kinetic overlays, and soundscape alignment.
- **Tooling & Scripts**:
  - Added `"remotion:skills:update"` script to `package.json`.
  - Added `scratch/` to `.gitignore`.

### Fixed
- Fixed whitespace collapse in `ScrambledText` component by preserving non-breaking spaces (`\u00A0`) and enforcing `whiteSpace: "pre-wrap"` and `wordBreak: "break-word"`.

### Changed
- Bumped version to `0.2.0` across `pyproject.toml`, `package.json`, `src/__init__.py`, `src/server.py`, `src/cli.py`, and adapter User-Agents.
- Updated `AGENTS.md`, `.agents/rules/10_programmatic_video_and_remotion_engine.md`, and `docs/AGENT_MANUAL.md` with Remotion Agent Skills compliance.

---

## [0.1.0] — 2026-09-23

### Added
- Initial open-source release of OmniPress MCP.
- Universal multi-channel publishing protocol across Dev.to, Ghost CMS, LinkedIn, X, Meta Threads, Instagram, Reddit, and Markdown archives.
- Multi-channel agnostic architecture with channel isolation (`channels/<slug>/`).
- Privacy and judicial secrecy sanitization gate (`sanitize_text`).
- Social Carousel Builder (Pillow 3:4 high-contrast graphics engine).
- Basic Remotion programmatic video pipeline and Edge-TTS voiceover generation.
- CLI suite (`omnipress doctor`, `omnipress status`, `omnipress setup`).
