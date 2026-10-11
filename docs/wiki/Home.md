# Welcome to the OmniPress MCP Wiki 🌐

> **The Universal Agentic Publishing Protocol & Distribution Engine for AI Agents via Model Context Protocol (MCP)**

**OmniPress MCP** is an open-source, domain-agnostic publishing protocol designed to give AI agents the power to transform raw thoughts, codebases, research papers, court rulings, policy memos, or market data into authoritative long-form publications and multi-channel social campaigns.

---

## 🎯 The "Truly Omni" Philosophy

OmniPress is built around four core dimensions of universality:

1. **Omni-Domain**: Extensible via **Modular Niche Skills** (`tech`, `tax-legal`, `govtech`, `darkchannel`), allowing AI agents to write with the exact tone and compliance constraints of any field.
2. **Omni-Platform**: Automatically syndicates content to **LinkedIn**, **X (Twitter)**, **Meta Threads**, **Instagram** (Carousels & Reels), **Reddit** (targeted subreddits), **Webhooks** (n8n, Make), and **Markdown Archives** (Substack, Medium).
3. **Omni-Runtime**: Dual-runtime architecture: native **Node.js (18+) with zero external dependencies** + full **Python (3.10+) FastMCP** engine with PIL carousel rendering.
4. **Omni-Channel**: Isolated multi-tenant channel workspaces (`channels/<slug>/`) to manage multiple publications or dark channels cleanly.

---

## 🧭 Wiki Navigation

Explore the documentation:

- **[Step-by-Step Hands-On Guide](Step-by-Step-Guide)**: Complete practical tutorial from setup to publishing.
- **[Architecture & Protocol](Architecture-&-Protocol)**: How OmniPress handles JSON-RPC 2.0, stdio transport, ChannelManager, and CarouselBuilder.
- **[Creating Niche Skills](Creating-Niche-Skills)**: Step-by-step guide to building custom skills for your specific industry.
- **[Supported Platforms & Adapters](Supported-Platforms-&-Adapters)**: Complete configuration for Buffer, Instagram Graph API, Reddit, and Webhooks.
- **[Privacy & De-Identification](Privacy-&-De-Identification)**: How OmniPress shields sensitive credentials, PII, and court secrecy.
- **[Configuration & Environment Variables](Configuration-&-Environment-Variables)**: Complete reference for `.env` and account credentials.
- **[Antigravity Integration](Antigravity-Integration)**: How to register and use OmniPress inside Google Antigravity.

---

## ⚡ Quick Example

In Google Antigravity or Claude Desktop:

```text
OmniPress: Analyze our channel architecture in src/core/channel_manager.py.
Generate:
1. An in-depth technical article with Markdown frontmatter for Substack.
2. A leadership lessons-learned post for LinkedIn.
3. A 4-tweet narrative thread for X (Twitter).
4. An authentic problem-solution breakdown for Reddit r/webdev.
```

OmniPress will formulate all assets, run an automatic privacy scan to mask credentials, and queue the drafts directly to your channels upon confirmation.
