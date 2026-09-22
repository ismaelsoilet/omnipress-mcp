# Antigravity Integration Guide 🤖

OmniPress was built natively to integrate with **Google Antigravity** via the Model Context Protocol (MCP) and Antigravity's Customization System (Skills & Rules).

---

## 1. Global MCP Server Registration

Add the server to your Antigravity global MCP configuration file:
- **Location**: `~/.gemini/config/mcp_config.json`

```json
{
  "mcpServers": {
    "omnipress": {
      "command": "node",
      "args": [
        "C:/Users/Ismael/projects/omnipress-mcp/src/server.js"
      ],
      "env": {
        "ARTICLES_DIR": "C:/Users/Ismael/projects/omnipress-mcp/articles"
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

---

## 3. How to Prompt Antigravity

You can trigger OmniPress with natural language prompts across any subject:

### Example A: Software Engineering
> *"OmniPress: Analyze the memory optimization we made in `src/buffer_adapter.py`. Write a technical article, a LinkedIn post on engineering best practices, and a Reddit post for r/programming."*

### Example B: Tax & Legal Tech
> *"OmniPress: Review the constitutional reform on indirect taxes (IBS/CBS). Generate an article with YAML frontmatter, an executive summary for LinkedIn, and a Reddit post for r/direito."*

### Example C: Public Policy & GovTech
> *"OmniPress: Draft a report on digital service delivery in municipal governments. Queue the summary as a draft for LinkedIn and Threads."*
