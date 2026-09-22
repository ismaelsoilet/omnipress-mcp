# 🚀 OmniPress MCP

[🇺🇸 English](README.md) | [🇧🇷 Português](README.pt-BR.md)

> **The Agentic Publishing & Thought-Leadership Engine for Antigravity via Model Context Protocol (MCP)**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Node 18+](https://img.shields.io/badge/node-18+-green.svg)](https://nodejs.org/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![MCP Standard](https://img.shields.io/badge/MCP-1.0-orange.svg)](https://modelcontextprotocol.io/)
[![Built for Antigravity](https://img.shields.io/badge/Antigravity-Native-purple.svg)](https://deepmind.google/technologies/gemini/)

**OmniPress MCP** empowers AI agents to transform raw technical ideas, judicial forensic case studies, tax/fiscal rulings, and software architectures into high-authority publications and social media campaigns with built-in privacy protection (LGPD/judicial secrecy) and human-in-the-loop review.

---

## 🌟 Key Features

- 🎯 **Dynamic Tone Adaptation**: Effortlessly transitions between **Technology/Software Architecture**, **Tax Law (Tributário)**, **Judicial Forensic Analysis (Perícia Judicial)**, and **Public Administration/GovTech**.
- 🛡️ **Privacy & Legal De-Identification**: Built-in scanning and masking for judicial lawsuit numbers (CNJ format `0000000-00.0000.0.00.0000`), sensitive tax IDs (CPF/CNPJ), and confidential litigant data to safeguard professional secrecy (*segredo de justiça*) and LGPD/GDPR compliance.
- 📐 **Tri-Format Repurposing**: Takes one core idea and produces:
  1. **Long-Form Article**: Markdown with rich YAML frontmatter for Substack, Jusbrasil, Medium, or static site generators.
  2. **LinkedIn Post**: High-retention hooks, structured bulleted takeaways, and discussion prompts.
  3. **X (Twitter) Thread**: 3 to 5 tweet sequence for fast micro-blogging consumption.
- 🔌 **Modular Multi-Provider Engine**:
  - **Buffer API**: Queues posts to **LinkedIn**, **X (Twitter)**, and **Meta Threads** in draft mode for 1-click mobile approval.
  - **Direct Reddit Engine**: Publishes rich self-posts with Markdown formatting directly to subreddits (e.g., `r/webdev`, `r/SideProject`, `r/direito`).
  - **Generic Webhook**: Dispatches rich JSON payloads to **n8n**, Make, Slack, Telegram, or custom automation pipelines.
  - **Local Markdown Archive**: Automated file organization sorted by `YYYY/MM/`.
- ⚡ **Dual-Runtime Support**: Runs natively on **Node.js (18+) with zero external dependencies** as well as on **Python (FastMCP)**.

---

## 🏛️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                       ANTIGRAVITY                       │
│    (Drafts, refines, and adapts content across domains)  │
└────────────────────────────┬────────────────────────────┘
                             │ Model Context Protocol (MCP)
┌────────────────────────────▼────────────────────────────┐
│                    OmniPress MCP Server                 │
│  ├── Sanitizer & Privacy Engine (LGPD / Judicial De-ID) │
│  └── Modular Adapters Layer                             │
└──────────────┬───────────────────┬───────────────────┬──┘
               │                   │                   │
               ▼                   ▼                   ▼
      ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
      │  Buffer Adapter │ │  Reddit Adapter │ │ Markdown Archive│
      │ (LinkedIn, X,   │ │ (Direct Subreddit│ │  (Local Files)  │
      │    Threads)     │ │   Submissions)  │ └─────────────────┘
      └─────────────────┘ └────────┬────────┘
                                   │
                          ┌────────▼────────┐
                          │ Webhook Adapter │
                          │  (n8n / Make)   │
                          └─────────────────┘
```

---

## 📦 Project Structure

```
omnipress-mcp/
├── .agents/skills/omnipress/   # Antigravity skill runbook
├── docs/                      # Setup and account configuration guides
│   ├── SETUP_GUIDE.md         # English Setup Guide
│   └── SETUP_GUIDE.pt-BR.md   # Portuguese Setup Guide
├── src/
│   ├── adapters/              # Python Buffer, Webhook, and Markdown adapters
│   ├── utils/                 # Python privacy sanitizer
│   ├── server.js              # Pure Node.js FastMCP server (Zero external dependencies)
│   └── server.py              # Python FastMCP server
├── tests/
│   ├── test_omnipress.js      # Node.js automated unit test suite
│   └── test_omnipress.py      # Python automated unit test suite
├── AGENTS.md                  # Operational rules for AI agents and pair programmers
├── plugin.json                # Antigravity plugin manifest
├── mcp_config.json            # Local MCP configuration
├── package.json               # Node.js / npm package definition
├── pyproject.toml             # Python package specification
└── .env.example               # Environment variables template
```

---

## ⚡ Quickstart & Testing

### 1. Run Automated Unit Tests (Node.js)
The project runs natively on Node.js without requiring third-party package installations:

```bash
npm test
# or directly: node tests/test_omnipress.js
```

### 2. Configure Environment
Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Follow the [Setup & Account Configuration Guide (docs/SETUP_GUIDE.md)](docs/SETUP_GUIDE.md) to obtain your Buffer developer token and channel IDs for LinkedIn and X.

---

## 🤖 Antigravity Integration

Add OmniPress to your global `~/.gemini/config/mcp_config.json`:

```json
{
  "mcpServers": {
    "omnipress": {
      "command": "node",
      "args": ["C:/Users/Ismael/projects/omnipress-mcp/src/server.js"],
      "env": {
        "ARTICLES_DIR": "C:/Users/Ismael/projects/omnipress-mcp/articles"
      }
    }
  }
}
```

### Using in Antigravity Chat
Simply converse with Antigravity:

> *"OmniPress: Analyze the technical and fiscal impact of recent judicial rulings on software license taxation (ISS vs ICMS). Prepare an in-depth article, a high-impact LinkedIn post, and an X thread. Anonymize all court references."*

Antigravity will draft the content, present a preview for your review, and upon your confirmation, save the article to the archive and queue the social drafts to Buffer.

---

## 🛠️ Exposed MCP Tools

| Tool | Description |
| :--- | :--- |
| `omnipress_publish_article` | Saves long-form article to local archive with YAML frontmatter. Runs de-identification check. |
| `omnipress_queue_post` | Queues short-form post/thread to LinkedIn and/or X via Buffer or Webhook in draft mode. |
| `omnipress_inspect_content` | Utility to inspect text for sensitive lawsuit numbers, tax IDs (CPF/CNPJ), or PII. |
| `omnipress_list_recent` | Lists recently saved articles and metadata. |

---

## 📄 License

Distributed under the [MIT License](LICENSE).
