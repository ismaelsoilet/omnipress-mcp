# 🌐 OmniPress MCP

[🇺🇸 English](README.md) | [🇧🇷 Português](README.pt-BR.md) | [🤖 AI Agent Manual](docs/AGENT_MANUAL.md) | [🎬 Video Skills](docs/VIDEO_CREATION_AND_PLATFORM_SKILLS.md) | [🎞️ Remotion Reference](docs/REMOTION_SKILLS_AND_DOCS.md) | [📜 Changelog](CHANGELOG.md)

> **The Universal Agentic Publishing Protocol & Media Distribution Engine for AI Agents via Model Context Protocol (MCP)**

[![PyPI Version](https://img.shields.io/pypi/v/omnipress-mcp?color=blue)](https://pypi.org/project/omnipress-mcp/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/)
[![Node 20+](https://img.shields.io/badge/node-20+-green.svg)](https://nodejs.org/)
[![MCP Standard](https://img.shields.io/badge/MCP-2.0%20%2F%20TDQS%205.0-orange.svg)](https://modelcontextprotocol.io/)
[![Smithery Compatible](https://img.shields.io/badge/Smithery-Compatible-blueviolet.svg)](https://smithery.ai)
[![Antigravity Native](https://img.shields.io/badge/Antigravity-Native-purple.svg)](https://deepmind.google/technologies/gemini/)

**OmniPress MCP** is an open-source, domain-agnostic agentic publishing protocol. It empowers AI agents (like Google Antigravity, Claude, or ChatGPT) to ingest raw thoughts, codebases, research papers, court rulings, policy memos, or market data, and transform them into authoritative long-form publications, high-contrast visual social carousels, viral dark channel scripts, and multi-platform distribution campaigns.

OmniPress is designed to be **truly "Omni"**:
- **Omni-Domain**: Universal intake engine extensible via 31 modular skills (tech, tax-legal, govtech, darkchannel, YouTube long-form documentary, and vertical short-form suites).
- **Omni-Platform**: Native distribution across Dev.to, Ghost CMS, LinkedIn, X (Twitter), Meta Threads, Instagram (Reels & Carousels), Reddit, Webhooks (n8n/Make), and Markdown archives.
- **Omni-Runtime**: Unified Python MCP engine (supporting STDIO and HTTP/SSE ASGI) + Remotion React programmatic video engine (12 official skills) + Pillow high-contrast carousel builder.
- **Omni-Channel (Multi-Tenant)**: Isolated channel workspaces (`channels/<slug>/`) enabling seamless management of multiple brands, publications, or dark channels without asset collisions.

---

## 🎯 The Vision & Publishing Pipeline

Modern knowledge workers, developers, researchers, and creators spend hours translating their work into different formats across fractured social platforms.

OmniPress solves this by providing a unified **Agentic Publishing Pipeline**:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          1. UNIVERSAL INTAKE                            │
│   Raw Thoughts • Code Diffs • Whitepapers • Tax Rulings • Research Data │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
┌────────────────────────────────────▼────────────────────────────────────┐
│                       2. MODULAR SKILL RUNTIME                          │
│   Each niche has a dedicated skill directing tone, style & jargon:       │
│   ├── Tech & Software Architecture    ├── Tax, Law & Forensic Auditing  │
│   ├── Public Governance & GovTech     ├── Finance, Crypto & Markets     │
│   └── Viral Dark Channel Engine       └── Product & Founder Journey     │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
┌────────────────────────────────────▼────────────────────────────────────┐
│                    3. PRIVACY & SANITIZATION SHIELD                     │
│   Automated masking of API keys, client secrets, court case IDs, & PII  │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
┌────────────────────────────────────▼────────────────────────────────────┐
│                   4. VISUAL RENDERING & MEDIA ENGINE                    │
│   3:4 Branded Portrait Carousels • TTS Voice Narration • Video Staging  │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
┌────────────────────────────────────▼────────────────────────────────────┐
│                   5. MULTI-PLATFORM SYNDICATION                         │
│  ┌───────────────┐ ┌───────────────┐ ┌───────────────┐ ┌───────────────┐│
│  │   LinkedIn    │ │  X (Twitter)  │ │  Meta Threads │ │   Instagram   ││
│  │  (Leadership) │ │   (Threads)   │ │  (Bite-sized) │ │  (Carousels)  ││
│  └───────┬───────┘ └───────┬───────┘ └───────┬───────┘ └───────┬───────┘│
│          │                 │                 │                 │        │
│          └───────────────┬─┴─────────────────┴─────────────────┘        │
│                          │                                              │
│             ┌────────────▼───────────┐    ┌────────────────────────┐    │
│             │ Reddit (r/subreddits)  │    │ Long-form .md Archive  │    │
│             │ Webhooks (n8n / Make)  │    │ (Substack/Medium/Blog) │    │
│             └────────────────────────┘    └────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 🌟 Core Pillars

### 1. Multi-Channel & Agnostic Workspace Architecture
OmniPress supports multiple isolated channels (e.g., military history, tech architecture, tax law, viral dark channels) with zero asset overlap:

```
channels/
  ├── dossie-historico/          # Active channel workspace
  │   ├── channel.json           # Branding, palette, fonts, handles, Buffer IDs
  │   ├── articles/              # Long-form articles organized by YYYY/MM/
  │   ├── media/
  │   │   ├── raw/               # Source & reference assets
  │   │   ├── carousels/         # Rendered 3:4 portrait carousel decks
  │   │   ├── stories/           # 9:16 vertical stories
  │   │   └── highlights/        # Highlight covers
  │   └── scripts/               # Channel-specific pipelines
  └── _template/                 # Boilerplate for instant channel scaffolding
```

### 2. Social Carousel Rendering Engine (`CarouselBuilder`)
Fully decoupled, data-driven Python (Pillow) graphics engine parameterized via `channel.json`:
- **Hierarchical Parameter Resolution**: Configurable margins (`margin_ratio`), typography scales (`headline_scale`, `body_scale`, `step_scale`, `footer_scale`), line heights, card backdrop alphas, and border radiuses resolved per slide, per preset, or from channel-wide defaults.
- **Agnostic Semantic Callouts**: Decoupled category vocabularies (`semantic_categories`: `danger`, `success`, `warning`, `accent`) and custom tags (`semantic_tags`), enabling any vertical (Software, Law, History) to define custom highlighted phrases without engine code modifications.
- **4 Visual Presets**: `classic_card` (Rule 08 contrast cards over archival photos), `tweet_card` (social proof post cards with avatar & verified badge), `minimal_dark` (dark editorial with serif typography & UI search mockups), and `split_editorial` (corporate authority with top photo & circular avatar cutout).
- **Pixel-perfect dynamic wrapping**: Guarantees zero text truncation or clipping under any aspect ratio (3:4, 4:5, 1:1, 9:16).

### 3. Universal Privacy & Secrets Shield (LGPD, CNJ & Secrets)
Before anything is staged or published, OmniPress automatically runs security and privacy sanitization:
- **Technical Credentials**: Masks API keys, JWT tokens, Bearer secrets, and private IPs.
- **Legal/PII**: Masks judicial process numbers (CNJ standard `0000000-00.0000.0.00.0000`), Brazilian tax IDs (CPF/CNPJ), phone numbers, and emails.

### 4. Publishing Shield & Anti-Duplicate Idempotency (Rule 09)
Guarantees **zero accidental duplicates**, prevents placeholder test text leaks, and enforces strict social platform constraints before touching external network APIs:
- **Gate 1 (Test Text Interceptor)**: Blocks dummy/test strings (`"teste"`, `"test"`, `<12 chars`) from broadcasting live on production feeds with `shareNow`.
- **Gate 2 (Media Requirement Gate)**: Rejects text-only posts destined for Instagram before network dispatch.
- **Gate 3 (Platform Character Limits)**: Enforces hard limits (Instagram: 2,196 chars for Buffer GraphQL, X: 280, Threads: 500, LinkedIn: 3,000) and reports exact excess length.
- **Gate 4 (24h Idempotency Ledger)**: Stores deterministic SHA-256 fingerprints in `media/staging/publishing_ledger.json` to block duplicate posts within a 24-hour window.
- **Gate 5 (Native API Metadata & Clean Overwrites)**: Automatically injects `metadata.instagram.type = "post"` and `shouldShareToFeed = true`, and purges obsolete drafts with atomic `delete_post` GraphQL mutations.

### 5. Programmatic Video & Motion Design Engine (Remotion)
Full React & TypeScript video engine (`src/video/`) engineered for YouTube Documentaries (16:9) and Shorts/Reels/TikTok (9:16):
- **Universal Compositions**: Render broadcast-grade MP4s in seconds using `npm run remotion:render`.
- **Vertical Duration Standard for Monetization**: Standardized 62–68 second target (~65s / 1,950 frames @ 30fps) to qualify for the TikTok Creator Rewards Program (>60s requirement) without risking sub-minute rounding disqualifications, while fitting seamlessly within YouTube Shorts (up to 180s) and Instagram Reels (up to 90s).
- **Synchronized Whisper Subtitles**: Word-by-word dynamic highlighting (`SynchronizedCaptions.tsx`) powered by Whisper JSON timestamps over frosted dark backdrop cards.
- **Cinematic Components**: Built-in military cipher decryption (`ScrambledText`), 3D floating dust motes (`DustParticles`), anamorphic golden flares (`AnamorphicFlare`), distressed official stamps with camera shake (`ClassifiedStamp`), tactical grids (`TacticalGrid`), film grain (`FilmGrain`), and Ken Burns camera movements (`KenBurnsImage`).
- **Synchronized Broadcast Soundscape**: Multi-layered 48kHz stereo audio embedded via `<Audio />` with dynamic audio ducking (-18dB to -22dB under speech).
- **Programmatic Thumbnail Generator (Rule 15)**: High-CTR 16:9 thumbnails rendered directly from React (`ThumbnailEpisode.tsx`) complying with the Titanic Typography Scale (160px–220px, 3-word limit, zero micro-fonts < 50px, and YouTube duration badge clear zone).

### 6. Multi-Channel Syndication & YouTube Integration
- **YouTube Direct Integration**: Connects seamlessly with YouTube via Buffer (`buffer_channel_id` mapped in `channel.json`).
- **Multi-Brand Scalability**: Easily expand across multiple verticals (History, Geopolitics, Software Architecture, and Tax Law / Public Governance) with zero code duplication.

### 7. OmniPress Content Factory — 12 Specialized Subagents & Production Modes (v0.5.0)
A modular, assembly-line content generation factory driven by **12 specialized subagents** orchestrated by the Central Director (AG12). Operates across 4 execution modes configured via declarative recipes:
- **`Express` (~5 min)**: Rapid publishing (AG12 → AG01 → User Gate → AG04). Designed for Markdown articles, LinkedIn authority posts, and connected X threads.
- **`Standard` (~20 min)**: High-retention vertical videos (Shorts / Reels / TikTok). Activates research, synchronized imagery curation (AG02), audio broadcast mastering (-14 LUFS, AG03), narration audit (AG10), timing verification (AG05), and editorial QA (AG04).
- **`Full Production` (~75 min)**: Broadcast-grade 16:9 documentary production orchestrating all 12 subagents: Remotion visual effects (AG07), immersive sound design (AG08), user-sovereign soundtrack curation (AG09), and adversarial quality review (AG11).
- **`Remix` (~30 min)**: Visual and acoustic modernizer reusing pre-mastered voice tracks to refresh B-roll, SFX, and Remotion motion dynamics.
- **Strict Contract Handoffs**: Standardized JSON schemas (`.agents/schemas/`) guarantee seamless data flow across agents (`roteiro.json`, `image_manifest.json`, `timing_report.json`, `audit_report.json`, `production_log.json`).

### 8. Universal 3D Asset & Mockup Engine (Blender Headless / v0.6.0)
Declarative photorealistic 3D asset generation powered by headless Blender 4.2+ LTS with alpha transparency (PNG/WebM):
- **Dynamic Device Mockups**: Smartphone in perspective with beveled dark titanium chassis and automatic UV screen mapping for carousel/article screenshots (`device_mockup.py`).
- **Rotating Metallic Badges & Coins**: 3D beveled medallions with customizable metallic shaders (`gold`, `silver`, `chrome`, `obsidian`, `bronze`) and optional front insignia (`rotating_badge.py`).
- **3D Kinetic Typography**: Extruded beveled 3D text with studio lighting and specular highlights (`kinetic_title.py`).
- **Waving Silk Flags & Banners**: Photorealistic 3D waving flags and banners with harmonic cloth displacement, satin shaders, custom texture mapping, and polished golden pole (`waving_flag.py` / `brazil_flag.py`).
- **CLI & MCP Control**: Render via `omnipress render-3d` or canonical MCP tool `omnipress_render_3d`.

---

### 9. Universal Factory Architecture — Providers, Recipes & Schemas (v0.10.0)

`src/` is a **factory**: universal engines and providers that know nothing about a specific channel. `channels/<slug>/` is **data**: recipes, assets and channel templates. See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) and [`docs/PROVIDERS.md`](docs/PROVIDERS.md).

| Layer | Responsibility |
|---|---|
| `src/core/` | Channel discovery, credentials, cache, schema validation, capability registry |
| `src/engine/` | `universal_carousel`, `universal_publisher`, `universal_audio`, `universal_captions`, `universal_thumbnail`, `universal_documentary`, `universal_video`, `universal_assets`, `universal_3d`, `universal_deploy` |
| `src/engine/providers/` | The only door to external runtimes: Blender, Remotion, FFmpeg, Edge-TTS, Whisper, AI image, prompt export, stock assets |
| `src/adapters/` | Publishing providers (Buffer, Instagram, Dev.to, Ghost, Reddit, Webhook, Markdown) |
| `src/video/` | Remotion compositions with a fully prop-driven theme (`theme.ts`) |

Declarative recipes are validated against `.agents/schemas/*.schema.json` before any work:

```bash
omnipress carousel    --recipe channels/<slug>/episodios/<ep>/carrossel/carousel_recipe.json --all
omnipress thumbnail   --recipe channels/<slug>/media/thumbnails/<post>/thumbnail_recipe.json --preview 120 320
omnipress documentary --recipe channels/<slug>/episodios/<ep>/documentario/documentary_recipe.json
omnipress video       --recipe channels/<slug>/recursos_globais/vinhetas/intro_recipe.json
omnipress master-audio voice.mp3 -o master.mp3 --mix-bed soundtrack.mp3 --bed-volume 0.18
omnipress align-captions whisper.json -o captions.json --verify
omnipress assets      --recipe channels/<slug>/media/raw/assets/asset_recipe.json
omnipress render-3d   --recipe channels/<slug>/media/visuals/3d/3d_recipe.json --validate-only
omnipress deploy      public/episode.mp4 --target-dir public
omnipress doctor --json
```

Adding a channel or a 3D template requires **zero Python**: only JSON and channel files. Adding a new external runtime requires one provider and one capability entry.

## 🚀 Step-by-Step Hands-On Guide

Here is the complete walkthrough to install, configure, and use OmniPress from scratch to your first published piece.

### Step 1: Installation & Environment Setup

### Step 1: Quickstart & Installation

#### Option A: Zero-Clone Execution via `uvx` (Recommended)
You can run OmniPress immediately without cloning or setting up virtual environments:

```bash
# Run the MCP server directly
uvx omnipress-mcp

# Or run the environment diagnostic
uvx --from omnipress-mcp omnipress doctor
```

#### Option B: Smithery 1-Click Install
If using Claude Desktop or Cursor, install directly via Smithery:
```bash
npx -y @smithery/cli install omnipress-mcp --client claude
```

#### Option C: Local Git Clone for Contributors
```bash
# 1. Clone repository
git clone https://github.com/ismaelsoilet/omnipress-mcp.git
cd omnipress-mcp

# 2. Install dependencies with uv
uv sync

# 3. Verify that all test suites pass (80 tests):
uv run pytest -v     # Python test suite
npm run typecheck    # Remotion TypeScript integrity
```

---

### Step 2: Configure Credentials & Environment

You can configure OmniPress interactively via the CLI or manually via `.env`:

```bash
# Run the interactive setup wizard:
omnipress setup

# Run environment and capability diagnostics:
omnipress doctor

# Automatically sync connected social profiles from Buffer into channel.json:
omnipress sync-buffer [channel-slug]
```

#### Multi-Channel Environment Isolation (Rule 04)
OmniPress supports true multi-tenant workspace isolation:
- **Root `.env`**: Serves as the primary configuration for the flagship channel (**Dossiê Histórico** via `OMNIPRESS_ACTIVE_CHANNEL=dossie-historico`).
- **Channel `.env` (`channels/<slug>/.env`)**: Channels (e.g. `channels/ismael-soilet/.env`) maintain their own isolated API keys and profile IDs, completely decoupled from other brands.
- **Precedence Order**: `channels/<slug>/.env` → `<SLUG>_BUFFER_API_KEY` → root `.env`.

> 💡 **Offline Mode**: OmniPress works out-of-the-box **without any API keys**. In offline mode, articles are safely stored locally in Markdown and social copies are printed in chat ready for manual copying.

Key integrations:
1. **Developer Thought Leadership (Dev.to)**:
   - Obtain your API Key at: [dev.to/settings/extensions](https://dev.to/settings/extensions).
   - Set `DEVTO_API_KEY`.
2. **Independent Publications & Newsletters (Ghost CMS)**:
   - Create a Custom Integration in Ghost Admin (`Settings -> Integrations`).
   - Set `GHOST_API_URL` (e.g., `https://myblog.ghost.io`) and `GHOST_ADMIN_API_KEY` (`{id}:{secret}`).
3. **Multi-Network Social Syndication (Buffer - LinkedIn, X, Threads, Instagram)**:
   - Obtain your Personal API Key at: [publish.buffer.com/settings/api](https://publish.buffer.com/settings/api).
   - Set `BUFFER_API_KEY` and profile IDs (`BUFFER_LINKEDIN_PROFILE_ID`, `BUFFER_X_PROFILE_ID`, etc.).
4. **Direct Meta Instagram Graph API**:
   - Set `INSTAGRAM_ACCESS_TOKEN` and `INSTAGRAM_ACCOUNT_ID` for direct Instagram publishing.
5. **Reddit (Direct Subreddit Submissions)**:
   - Set `REDDIT_CLIENT_ID`, `REDDIT_CLIENT_SECRET`, `REDDIT_USERNAME`, and `REDDIT_PASSWORD`.
6. **Webhooks (n8n / Make / Slack / Telegram)**:
   - Set `OMNIPRESS_WEBHOOK_URL` to receive full JSON payloads of generated posts and articles.

---

### Step 3: Connect to Your AI Agent

#### Google Antigravity (Recommended)
Add the server to `~/.gemini/config/mcp_config.json` (or the project root `mcp_config.json`):

```json
{
  "mcpServers": {
    "omnipress": {
      "command": "/path/to/omnipress-mcp/.venv/bin/python",
      "args": ["-m", "src.server"],
      "env": {
        "OMNIPRESS_ACTIVE_CHANNEL": "dossie-historico"
      }
    }
  }
}
```

#### Claude Desktop
In your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "omnipress": {
      "command": "python",
      "args": ["/path/to/omnipress-mcp/src/server.py"],
      "env": {
        "ARTICLES_DIR": "/path/to/omnipress-mcp/articles"
      }
    }
  }
}
```

---

### Step 4: Managing Channels (CLI or MCP)

Manage multiple publications via the built-in CLI or directly via AI chat prompts.

#### Via Terminal CLI:
```bash
# List all configured channels
python src/cli.py list-channels

# Create a new channel workspace
python src/cli.py create-channel tech-insights \
  --name "Tech Insights" \
  --handle "@techinsights.dev" \
  --category "technology" \
  --color "#00E5FF"

# View channel details and branding
python src/cli.py info-channel tech-insights
```

#### Via AI Chat Prompt:
> *"OmniPress: List all configured channels and show me the active channel configuration."*

---

### Step 5: Publishing Workflows in Practice

#### Workflow A: Author & Archive a Long-Form Article
When you ask the AI to draft an article:
1. The AI formats content in clean Markdown.
2. Attaches complete YAML frontmatter (`title`, `date`, `category`, `tags`, `author`, `status: draft`).
3. Runs the privacy and secrets scanner.
4. Invokes `omnipress_publish_article`, saving to `channels/<slug>/articles/YYYY/MM/article-title.md`.

#### Workflow B: Universal Carousel Engine, Multi-Presets & Archetypes (v0.4.0)
OmniPress v0.4.0 features native support for **Channel Archetypes** (`personal_brand` vs. `media_channel`) and **4 Modular Visual Presets**:
- **`tweet_card`** (Thiago Ramos style): Social-proof card with author avatar, Twitter blue verified badge, `@handle`, punchy headline, and single/dual comparison photo frames (`radius=18`).
- **`minimal_dark`** (Rhaj Teixeira style): Minimalist dark-mode editorial with pure dark canvas (`#08080A`), elegant serif typography (`DejaVuSerif`), step counter ("Passo 1."), and vector search bar mockup with magnifying glass and clear icons.
- **`split_editorial`** (Portal da Reforma Tributária style): Corporate & GovTech authority layout with top contextual photo (45%), deep navy blue solid block (55%), circular author cutout overlapping the division line, opinion badge, square bullet markers (`■`), and watermark logo.
- **`classic_card`** (Dossiê Histórico / Rule 08): Full-screen archival background photo, top badge pill, protective dark translucent backdrop card (`rgba(8, 10, 14, 215)`), and dark safety stroke on fonts.

Instead of writing repetitive Python scripts, create a declarative `carousel_recipe.json`:
```json
{
  "channel_slug": "tech-insights",
  "post_slug": "death-of-monoliths",
  "aspect_ratio": "4:5",
  "preset": "tweet_card",
  "slides": [
    {
      "headline": "The Death of Monoliths?",
      "body": "Why poorly designed distributed systems cost 10x more to maintain.",
      "images": ["architecture_diagram.jpg"],
      "swipe_str": "Deslize →"
    }
  ],
  "publish": {
    "caption": "Why distributed systems cost 10x more when done wrong...\n\n#architecture #microservices #devops",
    "platforms": ["linkedin", "instagram"],
    "mode": "shareNow"
  }
}
```

Run the complete pipeline (background prep + contrast rendering + CDN upload + Buffer scheduling):
```bash
omnipress carousel --recipe channels/tech-insights/campanhas/death-of-monoliths/carousel_recipe.json --all
```

#### Workflow C: Studio Broadcast Audio Mastering (Rule 10)
Masters raw human or AI voiceover through the 6-stage studio mastering chain (-14.0 LUFS EBU R128):
```bash
omnipress master-audio channels/tech-insights/media/voiceover/raw_voice.m4a -o channels/tech-insights/media/voiceover/master_voice.mp3
```

#### Workflow D: Whisper Captions Alignment
Extracts word timestamps from Whisper JSON and chunks them into punchy 2-4 word captions for Remotion video:
```bash
omnipress align-captions channels/tech-insights/shorts/s01/whisper.json -o channels/tech-insights/shorts/s01/captions.json
```

#### Workflow E: Queue Social Posts with PublishingShield
```bash
omnipress publish --recipe channels/tech-insights/articles/post_01/post_recipe.json
```

- Sanitized text is delivered into each platform's draft queue.

#### Workflow D: Produce Dark Channel Scripts (YouTube Shorts / Reels)
Use `omnipress_prepare_dark_script`:
- Produces high-hook openings within the first 3 seconds.
- Breaks down scenes with AI image generator prompts.
- Specifies voice narration instructions and YouTube/Instagram SEO metadata.

#### Workflow E: Render Programmatic Videos & Intros with Remotion
1. Preview your compositions live in the interactive browser studio:
```bash
npm run remotion:preview
```
2. Render broadcast-quality 1080p intro bumpers (4.0s) with multi-layered audio:
```bash
# 16:9 Landscape for Main YouTube Episodes
npm run remotion:render:intro

# 9:16 Vertical for YouTube Shorts, Reels, and TikTok
npm run remotion:render:intro:shorts
```
Rendered MP4s are saved to `media/output/intro_dossie_16x9.mp4` and `media/output/intro_dossie_9x16.mp4`.

#### Workflow F: Human Voiceover + Dynamic Remotion Timing
1. Have OmniPress draft the teleprompter script broken down by scenes (`Scene 01`, `Scene 02`...).
2. Record your voice audio per scene using your phone or microphone (`01.mp3`, `02.mp3`...).
3. Remotion reads audio durations dynamically, adapting visual cuts to your natural speech pace with background music ducking (-20dB under voice).

#### Workflow G: Headless 3D Asset Rendering with Blender (Rule 12)
Renders photorealistic 3D mockups (smartphones, tablets), rotating metallic coins/badges, and 3D kinetic typography with transparent backgrounds for carousels and Remotion video layers:
```bash
# 3D Smartphone Mockup with Article/Carousel Screenshot
omnipress render-3d --template device_mockup --texture channels/tech-insights/media/carousels/slide_01.png -o channels/tech-insights/media/visuals/3d/hero_mockup.png

# 3D Metallic Badge / Coin
omnipress render-3d --template rotating_badge --material gold -o channels/tech-insights/media/visuals/3d/badge_gold.png

# 3D Kinetic Typography
omnipress render-3d --template kinetic_title --text "OMNIPRESS 3D" --material chrome -o channels/tech-insights/media/visuals/3d/title_chrome.png

# Via Declarative 3D Recipe
omnipress render-3d --recipe recipe_3d.json
```

---

### Step 6: Ready-to-Use Prompt Templates

Copy and paste these directly into Antigravity or Claude:

#### 1. Software Engineering Tri-Format Campaign
```text
OmniPress: Analyze the file src/core/channel_manager.py and create a full publishing package:
1. An in-depth technical article for Substack exploring the trade-offs of local multi-tenancy.
2. A thought-leadership LinkedIn post with key takeaways.
3. A 4-tweet narrative thread for X (Twitter).
Archive the article and queue the social posts as drafts for the active channel.
```

#### 2. Legal / Tax Analysis with Privacy Shield
```text
OmniPress: Draft a compliance memo on municipal software tax rulings.
Ensure all court lawsuit numbers and client identifiers are masked, and queue the executive summary to LinkedIn and Reddit r/direito.
```

#### 3. High-Retention Dark Channel Script
```text
OmniPress: Write a high-retention 50-second YouTube Short script about 'Operation Mincemeat: The Corpse That Fooled Hitler'.
Include scene-by-scene AI image prompts and TTS voice direction with a cinematic, suspenseful tone.
```

---

## 🛠️ MCP Tools Exposed

| Tool | Purpose | Key Arguments |
| :--- | :--- | :--- |
| `omnipress_list_channels` | Lists all configured channels, active channel, and workspace paths. | `include_templates` (bool) |
| `omnipress_get_channel` | Retrieves full brand identity, color palette, and credentials for a channel. | `channel_slug` (string) |
| `omnipress_create_channel` | Scaffolds a new isolated channel workspace with dedicated subdirectories. | `slug`, `name`, `handle`, `category`, `primary_color` |
| `omnipress_build_carousel` | Renders production-ready 3:4 portrait carousel slides with channel branding. | `channel_slug`, `post_slug`, `slides_json`, `aspect_ratio` |
| `omnipress_publish_article` | Archives long-form Markdown or syndicates to Dev.to and Ghost CMS with PublishingShield idempotency. | `title`, `content_markdown`, `category`, `tags`, `author`, `channel_slug`, `target_platform`, `canonical_url`, `published`, `force_duplicate`, `sanitize` |
| `omnipress_queue_post` | Queues short-form post/thread with PublishingShield safety checks & anti-duplicate ledger. | `text`, `platforms`, `title`, `media_urls`, `schedule_time`, `channel_slug`, `mode`, `allow_test`, `force_duplicate` |
| `omnipress_queue_media_post` | Queues rich media content (Instagram Carousels, YouTube Shorts, X media posts) with PublishingShield. | `caption`, `platforms`, `media_urls`, `title`, `media_type`, `schedule_time`, `channel_slug`, `mode`, `allow_test`, `force_duplicate` |
| `omnipress_prepare_dark_script` | Generates high-retention viral dark channel script, scene image prompts, and TTS specs. | `topic`, `format`, `tone`, `target_audience` |
| `omnipress_brainstorm_channel` | Ideates high-retention channel concepts, psychological CTR angles, and viral backlog topics. | `niche`, `tone`, `target_audience`, `language` |
| `omnipress_generate_speech` | Synthesizes natural, high-definition neural narration audio (Edge-TTS) for Dark Channels, Reels, Shorts. | `text`, `voice`, `output_filename` |
| `omnipress_render_dark_video` | Renders MP4 video (9:16 or 16:9) combining neural audio narration and scene images via ffmpeg. | `text`, `audio_path`, `image_paths`, `output_filename`, `aspect_ratio`, `voice` |
| `omnipress_render_3d` | Renders photorealistic 3D visual assets with transparent background via headless Blender 4.2+ LTS. | `template`, `output_filename`, `texture_path`, `text`, `material`, `channel_slug`, `resolution`, `engine`, `samples` |
| `omnipress_inspect_content` | Standalone utility to scan text for credentials, PII, or lawsuit IDs without publishing. | `text` (string) |
| `omnipress_list_articles` | Lists recently archived articles and metadata from the repository or channel. | `limit` (int), `channel_slug` (string) |
| `omnipress_list_recent` | Backward-compatible alias for `omnipress_list_articles`. | `limit` (int) |

---

## 📚 Documentation & Resources

- **[Agent Manual (docs/AGENT_MANUAL.md)](docs/AGENT_MANUAL.md)**: Complete operational manual, tool guides, execution playbooks, and preset recipes.
- **[Agent Guidelines (AGENTS.md)](AGENTS.md)**: Architectural, TDQS standards, and normative rules for AI assistants.
- **[Rule 13 Policy (.agents/rules/13_continuous_documentation_versioning_and_release_policy.md)](.agents/rules/13_continuous_documentation_versioning_and_release_policy.md)**: Mandatory documentation, changelog, and SemVer versioning synchronization gate.
- **[Changelog (CHANGELOG.md)](CHANGELOG.md)**: Complete release history and version notes.
- **[Setup Guide (English)](docs/SETUP_GUIDE.md)** | **[Guia em Português](docs/SETUP_GUIDE.pt-BR.md)**: Credentials setup for Buffer, Instagram, and Reddit.
- **[GitHub Wiki](https://github.com/ismaelsoilet/omnipress-mcp/wiki)**: Architectural deep dives and operational runbooks.
- **[Creating Niche Skills Guide](https://github.com/ismaelsoilet/omnipress-mcp/wiki/Creating-Niche-Skills)**: How to build custom skills for new industries.

---

## 📄 License

Distributed under the [MIT License](LICENSE).
