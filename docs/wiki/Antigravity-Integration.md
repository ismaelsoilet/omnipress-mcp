# Antigravity Integration Guide 🤖

OmniPress was built natively to integrate with **Google Antigravity** via the Model Context Protocol (MCP) and Antigravity's Customization System (Skills & Rules).

---

## 1. Workspace / Global MCP Server Registration

Add the server to your Antigravity workspace or global MCP configuration file:
- **Location**: `.agents/mcp_config.json` (workspace) or `~/.gemini/config/mcp_config.json` (global)

```json
{
  "mcpServers": {
    "omnipress": {
      "command": "python",
      "args": [
        "-m",
        "src.server"
      ],
      "env": {
        "OMNIPRESS_ACTIVE_CHANNEL": "default"
      }
    }
  }
}
```

---

## 2. Global Skill Installation

OmniPress provides an agent runbook skill installed at:
- **Location**: `~/.gemini/config/skills/omnipress/SKILL.md`

Because skills use **progressive disclosure**, Antigravity automatically detects when you want to publish or adapt content and loads the runbook into context dynamically.

> **New video workflow:** use `omnipress video --scaffold-editable` and `omnipress studio` to refine agent-generated episodes. See [`docs/AGENT_COMPATIBILITY.md`](../AGENT_COMPATIBILITY.md) for the full matrix with Command Code and OpenCode.

---

## 3. How to Prompt Antigravity

You can trigger OmniPress with natural language prompts across any subject:

### Example A: Software Engineering
> *"OmniPress: Analyze the memory optimization we made in `src/buffer_adapter.py`. Write a technical article, a LinkedIn post on engineering best practices, and a Reddit post for r/programming."*

### Example B: Tax & Legal Tech
> *"OmniPress: Review the constitutional reform on indirect taxes (IBS/CBS). Generate an article with YAML frontmatter, an executive summary for LinkedIn, and a Reddit post for r/direito."*

### Example C: Public Policy & GovTech
> *"OmniPress: Draft a report on digital service delivery in municipal governments. Queue the summary as a draft for LinkedIn and Threads."*
