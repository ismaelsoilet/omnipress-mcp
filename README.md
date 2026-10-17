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
Integrated Python (Pillow) graphics engine specifically engineered for 3:4 portrait carousels (optimized for Instagram & LinkedIn feeds):
- **Pixel-perfect dynamic wrapping**: Guarantees zero text truncation or clipping.
- **Contrast gradient overlays**: Seamless readability over any background image.
- **Brand injection**: Primary accent color, top badge text, social `@handle`, page pagination counters (`01/06`), and swipe cues (`Deslize →`).

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
- **Programmatic Thumbnail Generator**: High-CTR 16:9 thumbnails rendered directly from React (`ThumbnailEpisode.tsx`).

### 6. Multi-Channel Syndication & YouTube Integration
- **YouTube Direct Integration**: Connects seamlessly with YouTube via Buffer (`buffer_channel_id` mapped in `channel.json`).
- **Multi-Brand Scalability**: Easily expand across multiple verticals (History, Geopolitics, Software Architecture, and Tax Law / Public Governance) with zero code duplication.

---

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
```

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

#### Workflow B: Render a Branded Instagram Carousel (3:4)
1. Place background images into `channels/<slug>/media/raw/`.
2. Define the slides array in a JSON file (or have the AI generate it):

```json
[
  {
    "bg_image": "channels/tech-insights/media/raw/bg_slide1.jpg",
    "headline": "The Death of Monoliths?",
    "body": "Why poorly designed distributed systems cost 10x more to maintain.",
    "page_str": "01/05"
  },
  {
    "bg_image": "channels/tech-insights/media/raw/bg_slide2.jpg",
    "headline": "The Latency Paradox",
    "body": "Every network hop across microservices accumulates latency overhead.",
    "page_str": "02/05"
  }
]
```

3. Render using the CLI or MCP tool:
```bash
python src/cli.py build-carousel \
  --channel tech-insights \
  --post death-of-monoliths \
  --config slides.json \
  --aspect-ratio 3:4
```
Rendered slides are output to `channels/tech-insights/media/carousels/death-of-monoliths/slide_01.jpg`.

#### Workflow C: Queue Social Posts
The agent calls `omnipress_queue_post` specifying target platforms:
- `platforms: ["linkedin", "twitter", "threads", "reddit:webdev"]`
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
| `omnipress_inspect_content` | Standalone utility to scan text for credentials, PII, or lawsuit IDs without publishing. | `text` (string) |
| `omnipress_list_articles` | Lists recently archived articles and metadata from the repository or channel. | `limit` (int), `channel_slug` (string) |
| `omnipress_list_recent` | Backward-compatible alias for `omnipress_list_articles`. | `limit` (int) |

---

## 📚 Documentation & Resources

- **[GitHub Wiki](https://github.com/ismaelsoilet/omnipress-mcp/wiki)**: Architectural deep dives and operational runbooks.
- **[Setup Guide (English)](docs/SETUP_GUIDE.md)** | **[Guia em Português](docs/SETUP_GUIDE.pt-BR.md)**: Credentials setup for Buffer, Instagram, and Reddit.
- **[Agent Guidelines (AGENTS.md)](AGENTS.md)**: Architectural and TDQS standards for AI assistants.
- **[Creating Niche Skills Guide](https://github.com/ismaelsoilet/omnipress-mcp/wiki/Creating-Niche-Skills)**: How to build custom skills for new industries.

---

## 📄 License

Distributed under the [MIT License](LICENSE).
