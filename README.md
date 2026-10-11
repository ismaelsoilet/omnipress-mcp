# 🌐 OmniPress MCP

[🇺🇸 English](README.md) | [🇧🇷 Português](README.pt-BR.md) | [📖 GitHub Wiki](https://github.com/ismaelsoilet/omnipress-mcp/wiki)

> **The Universal Agentic Publishing Protocol & Distribution Engine for AI Agents via Model Context Protocol (MCP)**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Node 18+](https://img.shields.io/badge/node-18+-green.svg)](https://nodejs.org/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![MCP Standard](https://img.shields.io/badge/MCP-1.0-orange.svg)](https://modelcontextprotocol.io/)
[![Antigravity Native](https://img.shields.io/badge/Antigravity-Native-purple.svg)](https://deepmind.google/technologies/gemini/)

**OmniPress MCP** is an open-source, domain-agnostic agentic publishing protocol. It empowers AI agents (like Google Antigravity, Claude, or ChatGPT) to ingest raw thoughts, codebases, research papers, court rulings, policy memos, or market data, and transform them into authoritative long-form publications, high-contrast visual social carousels, viral dark channel scripts, and multi-platform distribution campaigns.

OmniPress is designed to be **truly "Omni"**:
- **Omni-Domain**: Universal intake engine extensible via modular niche skills (`tech`, `tax-legal`, `govtech`, `darkchannel`).
- **Omni-Platform**: Native distribution across LinkedIn, X (Twitter), Meta Threads, Instagram (Reels & Carousels), Reddit, Webhooks (n8n/Make), and Markdown archives.
- **Omni-Runtime**: Dual-runtime architecture featuring a zero-dependency Node.js engine + a full Python FastMCP implementation with PIL carousel rendering.
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

### 4. Human-in-the-Loop by Default
No social post goes live without human verification:
- All posts are placed into your **Drafts / Review queue** in Buffer or Instagram, allowing you to preview and approve them on your phone or web dashboard before publication.

---

## 🚀 Step-by-Step Hands-On Guide

Here is the complete walkthrough to install, configure, and use OmniPress from scratch to your first published piece.

### Step 1: Installation & Environment Setup

Clone the repository and set up the Python virtual environment:

```bash
# 1. Clone the repository
git clone https://github.com/ismaelsoilet/omnipress-mcp.git
cd omnipress-mcp

# 2. Create and activate a Python virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
```

*(Optional: The Node.js runtime requires no `npm install` because it uses only Node 18+ standard modules).*

Verify that all test suites pass:
```bash
pytest        # Runs the Python FastMCP & Multi-Channel suite (12 tests)
npm test      # Runs the Node.js zero-dependency suite (15 tests)
```

---

### Step 2: Configure Environment Variables (`.env`)

Create your `.env` file from the provided template:

```bash
cp .env.example .env
```

Edit `.env` to configure your target integrations:

> 💡 **Note**: OmniPress works out-of-the-box **without any API keys**. In offline mode, articles are safely stored locally in Markdown and social copies are printed in chat ready for manual copying.

Key integrations:
1. **Buffer (LinkedIn, X / Twitter, Meta Threads)**:
   - Obtain your Personal API Key at: [publish.buffer.com/settings/api](https://publish.buffer.com/settings/api).
   - Set `BUFFER_API_KEY` and profile IDs (`BUFFER_LINKEDIN_PROFILE_ID`, `BUFFER_X_PROFILE_ID`, etc.).
2. **Direct Meta Instagram Graph API**:
   - Set `INSTAGRAM_ACCESS_TOKEN` and `INSTAGRAM_ACCOUNT_ID` for direct Instagram publishing.
3. **Reddit (Direct Subreddit Submissions)**:
   - Create a "script" app at: [reddit.com/prefs/apps](https://www.reddit.com/prefs/apps).
   - Set `REDDIT_CLIENT_ID`, `REDDIT_CLIENT_SECRET`, `REDDIT_USERNAME`, and `REDDIT_PASSWORD`.
4. **Webhooks (n8n / Make / Slack / Telegram)**:
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
| `omnipress_publish_article` | Archives long-form Markdown article organized by `YYYY/MM/` with YAML frontmatter. | `title`, `content`, `category`, `tags`, `author`, `channel_slug` |
| `omnipress_queue_post` | Queues short-form post/thread to LinkedIn, X, Threads, Instagram, or Reddit as draft. | `platforms`, `text`, `media_urls`, `schedule_time`, `channel_slug` |
| `omnipress_queue_media_post` | Queues rich media content (Instagram Carousels, YouTube Shorts, X media posts). | `platforms`, `caption`, `media_urls`, `schedule_time`, `title` |
| `omnipress_prepare_dark_script` | Generates high-retention viral dark channel script, scene image prompts, and TTS specs. | `topic`, `niche`, `duration_target_sec`, `language` |
| `omnipress_inspect_content` | Standalone utility to scan text for credentials, PII, or lawsuit IDs without publishing. | `text` (string) |
| `omnipress_list_articles` | Lists recently archived articles and metadata (alias: `omnipress_list_recent`). | `limit` (int), `channel_slug` (string) |

---

## 📚 Documentation & Resources

- **[GitHub Wiki](https://github.com/ismaelsoilet/omnipress-mcp/wiki)**: Architectural deep dives and operational runbooks.
- **[Setup Guide (English)](docs/SETUP_GUIDE.md)** | **[Guia em Português](docs/SETUP_GUIDE.pt-BR.md)**: Credentials setup for Buffer, Instagram, and Reddit.
- **[Agent Guidelines (AGENTS.md)](AGENTS.md)**: Architectural and TDQS standards for AI assistants.
- **[Creating Niche Skills Guide](https://github.com/ismaelsoilet/omnipress-mcp/wiki/Creating-Niche-Skills)**: How to build custom skills for new industries.

---

## 📄 License

Distributed under the [MIT License](LICENSE).
