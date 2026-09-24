# 🌐 OmniPress MCP

[🇺🇸 English](README.md) | [🇧🇷 Português](README.pt-BR.md) | [📖 GitHub Wiki](https://github.com/ismaelsoilet/omnipress-mcp/wiki)

> **The Universal Agentic Publishing Protocol & Distribution Engine for AI Agents via Model Context Protocol (MCP)**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Node 18+](https://img.shields.io/badge/node-18+-green.svg)](https://nodejs.org/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![MCP Standard](https://img.shields.io/badge/MCP-1.0-orange.svg)](https://modelcontextprotocol.io/)
[![Antigravity Native](https://img.shields.io/badge/Antigravity-Native-purple.svg)](https://deepmind.google/technologies/gemini/)

**OmniPress MCP** is an open-source, domain-agnostic agentic publishing protocol. It empowers AI agents (like Antigravity, Claude, or ChatGPT) to ingest raw thoughts, codebases, research papers, court rulings, policy memos, or market data, and transform them into authoritative long-form publications and multi-channel social campaigns.

OmniPress is designed to be **truly "Omni"**:
- **Omni-Domain**: Universal ingestion engine extensible via modular niche skills.
- **Omni-Platform**: Native distribution across LinkedIn, X (Twitter), Meta Threads, Reddit, Webhooks (n8n/Make), and Markdown archives.
- **Omni-Runtime**: Zero-dependency Node.js engine + full Python FastMCP implementation.

---

## 🎯 The Vision & Objectives

Modern knowledge workers, developers, researchers, and specialists spend hours translating their work into different formats across fractured social platforms.

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
│   └── Scientific & Academic Research  └── Product & Founder Journey     │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
┌────────────────────────────────────▼────────────────────────────────────┐
│                    3. PRIVACY & SANITIZATION SHIELD                     │
│   Automated masking of API keys, client secrets, court case IDs, & PII  │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
┌────────────────────────────────────▼────────────────────────────────────┐
│                   4. MULTI-PLATFORM SYNDICATION                         │
│  ┌───────────────┐ ┌───────────────┐ ┌───────────────┐ ┌───────────────┐│
│  │   LinkedIn    │ │  X (Twitter)  │ │  Meta Threads │ │    Reddit     ││
│  │  (Leadership) │ │   (Threads)   │ │  (Bite-sized) │ │  (Subreddits) ││
│  └───────┬───────┘ └───────┬───────┘ └───────┬───────┘ └───────┬───────┘│
│          │                 │                 │                 │        │
│          └─────────────────┴────────┬────────┴─────────────────┘        │
│                                     ▼                                   │
│                        ┌────────────────────────┐                       │
│                        │ Long-form .md Archive  │                       │
│                        │ (Substack/Medium/Blog) │                       │
│                        └────────────────────────┘                       │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 🌟 Core Pillars

### 1. Truly Omni-Domain (Modular Niche Skills)
OmniPress separates the **distribution engine** (MCP tools) from the **domain intelligence** (Agent Skills).
You can author any kind of article by simply enabling or creating a specialized skill in `.agents/skills/<niche>`:
- **`tech-architecture`**: Deep code walkthroughs, system trade-offs, and GitHub release announcements.
- **`tax-and-legal`**: Authoritative tax analyses, compliance reviews, and judicial forensics with strict court secrecy (*segredo de justiça*) compliance.
- **`govtech-civic`**: Public policy commentary, municipal modernization, and public transparency.
- **`science-research`**: Academic breakdowns, literature digests, and scientific methodology.
- **`founder-buildinpublic`**: Product updates, transparent metrics, and startup lessons.

### 2. Universal Privacy & Secrets Shield
Before anything is staged or published, OmniPress runs an automated security and privacy scan:
- **Credentials**: Masks API keys, JWT tokens, Bearer secrets, and private IPs.
- **Legal/PII**: Masks judicial process numbers (CNJ standard), tax IDs (CPF/CNPJ), phone numbers, and emails.

### 3. Multi-Channel Syndication
One core thought produces five synchronized assets:
1. **Long-Form Article**: Clean Markdown with rich YAML frontmatter for Substack, Medium, Jusbrasil, Dev.to, or static site generators.
2. **LinkedIn Post**: Attention-retaining opening, bulleted takeaways, discussion prompt, and hashtags.
3. **X (Twitter) Thread**: 3–5 tweet narrative arc.
4. **Meta Threads Post**: Conversational, community-focused insight.
5. **Reddit Submission**: Problem-first, authentic breakdown formatted for specific subreddits (`r/programming`, `r/webdev`, `r/SideProject`, `r/direito`).

### 4. Dual-Runtime Architecture
- **Node.js (18+)**: **Zero dependencies**—uses native stdio, `fetch`, and `crypto`. No `npm install` needed!
- **Python (3.10+)**: FastMCP server with modular adapter inheritance (`BasePublisherAdapter`).

---

## ⚡ Quickstart

### 1. Test the Engine
Run the 6-scenario automated test suite on Node.js:
```bash
npm test
# or directly: node tests/test_omnipress.js
```

### 2. Setup Environment Variables
```bash
cp .env.example .env
```
*(OmniPress works out-of-the-box even without API keys by saving articles locally and formatting copy ready for manual pasting).*

See the [Setup & Account Configuration Guide (docs/SETUP_GUIDE.md)](docs/SETUP_GUIDE.md) to connect:
- **Buffer**: For LinkedIn, X, and Meta Threads draft review.
- **Reddit**: For direct subreddit posting via official Reddit Script App.
- **Webhooks**: For custom pipelines in n8n, Make, Slack, or Telegram.

---

## 🤖 Antigravity Integration

Configure OmniPress globally in `~/.gemini/config/mcp_config.json`:

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

### Example Prompts in Antigravity

**Technology & Architecture**:
> *"OmniPress: Analyze our database caching architecture in `src/cache`. Draft an in-depth technical article, a LinkedIn lessons-learned post, and an X thread."*

**Tax, Law & Public Administration**:
> *"OmniPress: Break down the constitutional implications of the new Tax Reform on municipal software licensing. Generate an article with YAML frontmatter, a LinkedIn post, and a Reddit breakdown for r/direito."*

**Founder & Build-in-Public**:
> *"OmniPress: Write a launch announcement for our open-source release. Prepare a LinkedIn post, a Threads teaser, and submit a self-post to Reddit r/SideProject."*

---

## 🛠️ MCP Tools Exposed

| Tool | Purpose |
| :--- | :--- |
| `omnipress_publish_article` | Archives long-form article locally with YAML frontmatter organized by `YYYY/MM/`. Runs privacy & de-identification scan. |
| `omnipress_queue_post` | Queues short-form post/thread to LinkedIn, X, Threads, or Reddit in Draft/Review mode. |
| `omnipress_inspect_content` | Standalone utility to scan text for credentials, PII, or confidential court IDs without publishing. |
| `omnipress_list_articles` | Lists recently archived articles and metadata (backward-compatible alias: `omnipress_list_recent`). |

---

## 📚 Documentation & Wiki

- **[GitHub Wiki](https://github.com/ismaelsoilet/omnipress-mcp/wiki)**: Comprehensive architectural deep dives and runbooks.
- **[Creating Niche Skills Guide](https://github.com/ismaelsoilet/omnipress-mcp/wiki/Creating-Niche-Skills)**: How to build custom skills for your specific domain.
- **[Setup Guide (English)](docs/SETUP_GUIDE.md)** | **[Guia em Português](docs/SETUP_GUIDE.pt-BR.md)**
- **[Agent Guidelines (AGENTS.md)](AGENTS.md)**

---

## 📄 License

Distributed under the [MIT License](LICENSE).
