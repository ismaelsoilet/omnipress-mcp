# Architecture & Protocol 🏛️

OmniPress implements the official **Model Context Protocol (MCP)** specification over standard I/O (`stdio`). This allows any MCP-compatible AI agent (such as Antigravity, Claude Desktop, or Gemini CLI) to dynamically discover and invoke its publishing tools.

---

## 1. High-Level Flow

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
│   ├── 2. Privacy Sanitizer (LGPD, CNJ, PII, Secrets)   │
│   └── 3. Modular Adapters Dispatcher                   │
└───────────────────────────┬────────────────────────────┘
                            │
         ┌──────────────────┼──────────────────┐
         ▼                  ▼                  ▼
┌─────────────────┐┌─────────────────┐┌─────────────────┐
│ Buffer Adapter  ││ Reddit Adapter  ││ Markdown Archive│
│ (LinkedIn, X,   ││ (OAuth2 Script) ││ (Local YAML .md)│
│     Threads)    │└─────────────────┘└─────────────────┘
└────────┬────────┘
         │
┌────────▼────────┐
│ Webhook Adapter │
│  (n8n / Make)   │
└─────────────────┘
```

---

## 2. The 4 Core Stages

### Stage 1: Ingestion
The agent receives the user's raw input: a git diff, meeting notes, a court ruling, or high-level thoughts.

### Stage 2: Skill-Driven Transformation
The active niche skill guides the agent to structure the content into the tri-format or quint-format:
- Long-form Markdown with YAML metadata.
- LinkedIn post.
- X/Twitter thread.
- Meta Threads post.
- Reddit community breakdown.

### Stage 3: Automated Sanitization
Before dispatching to any external network or disk:
- `sanitizeText()` scans for sensitive information:
  - Brazilian CNJ court process numbers (`\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}`) $\rightarrow$ `[PROCESSO ANÔNIMO]`
  - Tax IDs (CPF / CNPJ) $\rightarrow$ `[CPF PROTEGIDO]`, `[CNPJ PROTEGIDO]`
  - Emails and phone numbers $\rightarrow$ `[EMAIL PROTEGIDO]`
  - API keys and tokens.

### Stage 4: Execution & Staging
- Long-form articles are saved to `articles/YYYY/MM/YYYY-MM-DD-slug.md`.
- Social posts are queued to Buffer or Reddit as **Drafts** for human-in-the-loop review.

---

## 3. Protocol Implementation (Dual-Runtime)

### Node.js Engine (`src/server.js`)
- Zero external dependencies.
- Native `readline` on `process.stdin` / `process.stdout`.
- Native `fetch` for Buffer, Reddit, and Webhooks.
- Native `node:crypto` for HMAC SHA-256 signatures.

### Python Engine (`src/server.py`)
- Built on `mcp.server.fastmcp.FastMCP`.
- Implements class-based adapter hierarchy (`BasePublisherAdapter`).
