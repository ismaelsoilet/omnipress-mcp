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

---

## 3. Unified Runtime Architecture

### Unified Python Engine (`src/server.py`)
- **Dual Transport Support**: Operates seamlessly over standard I/O (`stdio` mode for Claude Desktop / Gemini CLI) and HTTP/SSE ASGI mode (for Docker / Coolify / remote agent hosting).
- **mcp 2.x & 1.x Compatibility**: Dynamically integrates with `mcp.server.mcpserver.MCPServer` (and falls back to `FastMCP` in 1.x environments).
- **Healthcheck & Monitoring**: Provides built-in `/health` route for Docker and Coolify orchestration.
- **Glama TDQS A+ (5.0)**: Implements all 10 MCP tools with full channel isolation, structured guidance, and mandatory protocol annotations (`readOnlyHint`, `destructiveHint`, `idempotentHint`, `openWorldHint`).

### Remotion Video Engine (`src/video/`)
- Modern React/TypeScript video rendering engine powered by Remotion.
- Supports both 16:9 widescreen and 9:16 vertical video compositions.
- Decoupled from channel-specific data via dynamic props and configuration payloads.
