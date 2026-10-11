# Architecture & Protocol 🏛️

OmniPress implements the official **Model Context Protocol (MCP)** specification over standard I/O (`stdio`). This allows any MCP-compatible AI agent (such as Google Antigravity, Claude Desktop, or Gemini CLI) to dynamically discover and invoke its publishing tools.

---

## 1. High-Level Architecture Flow

```
┌────────────────────────────────────────────────────────┐
│                        AI AGENT                        │
│   (Ingests prompt, context, codebase, or documents)    │
└───────────────────────────┬────────────────────────────┘
                            │ JSON-RPC 2.0 (stdio)
┌───────────────────────────▼────────────────────────────┐
│                  OmniPress MCP Engine                  │
│                                                        │
│   ├── 1. Protocol Handler (initialize, tools/list)     │
│   ├── 2. ChannelManager (channels/<slug>/ resolution)  │
│   ├── 3. Privacy Sanitizer (LGPD, CNJ, PII, Secrets)   │
│   ├── 4. CarouselBuilder (PIL 3:4 graphics engine)     │
│   └── 5. Modular Publisher Adapters                    │
└───────────────────────────┬────────────────────────────┘
                            │
         ┌──────────────────┼─────────────────────────┐
         ▼                  ▼                         ▼
┌─────────────────┐┌─────────────────┐┌───────────────────────────────┐
│ Buffer Adapter  ││ Reddit Adapter  ││ Markdown Channel Archive      │
│ (GraphQL / REST ││ (OAuth2 Script) ││ (channels/<slug>/articles/)   │
│  Draft Queue)   │└─────────────────┘└───────────────────────────────┘
└────────┬────────┘
         │
         ├──────────────────┐
         ▼                  ▼
┌─────────────────┐┌─────────────────┐
│ Instagram Graph ││ Webhook Adapter │
│ (Direct API)    ││  (n8n / Make)   │
└─────────────────┘└─────────────────┘
```

---

## 2. Core Architectural Components

### 1. ChannelManager (`src/core/channel_manager.py`)
- Discovers, reads, and scaffolds channel workspaces in `channels/<slug>/`.
- Resolves active channel via `OMNIPRESS_ACTIVE_CHANNEL` env variable or per-request tool parameter (`channel_slug`).
- Reads branding, typography, color palettes, and social identifiers from `channel.json`.

### 2. CarouselBuilder (`src/engine/carousel_builder.py`)
- Channel-agnostic layout engine using Python Pillow.
- Generates 3:4 portrait (1080x1440) or 1:1 square slides.
- Dynamic pixel-width word wrapping without clipping or hyphenation breaks.
- Dark gradient overlay for guaranteed text legibility over any background visual.
- Injects channel branding: primary color accents, badge pill, `@handle`, pagination (`01/05`), and swipe prompt (`Deslize →`).

### 3. Privacy & De-Identification Shield (`src/utils/sanitizer.py`)
- Scans all text before publication or queueing:
  - Brazilian CNJ lawsuit IDs (`\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}`) $\rightarrow$ `[PROCESSO ANÔNIMO]`
  - Brazilian CPFs and CNPJs $\rightarrow$ `[CPF PROTEGIDO]`, `[CNPJ PROTEGIDO]`
  - Emails, phone numbers, API keys, JWTs, and private IPs.

### 4. Publisher Adapters (`src/adapters/`)
- `MarkdownArchiveAdapter`: Organizes long-form markdown by `YYYY/MM/` with YAML frontmatter.
- `BufferAdapter`: Connects to Buffer using GraphQL `createPost` mutation with fallback to legacy REST API, always queuing as drafts for human review.
- `InstagramAdapter`: Publishes direct images and carousels via Meta Graph API.
- `RedditAdapter`: Submits self-posts to specific subreddits (`r/programming`, `r/direito`, etc.).
- `WebhookAdapter`: Emits signed HMAC SHA-256 event payloads to external automation runners.

---

## 3. Dual-Runtime Support

### Python Engine (`src/server.py`)
- Built on `mcp.server.fastmcp.FastMCP`.
- Implements all 10 MCP tools with full channel isolation and Pillow carousel rendering.
- Recommended for production use with Antigravity and Claude.

### Node.js Engine (`src/server.js`)
- **Zero external dependencies** (uses native `node:fs`, `node:crypto`, `readline`, `fetch`).
- Runs immediately on Node 18+ without requiring `npm install`.
- Ideal for lightweight environments, serverless deployment, or quick local testing.
