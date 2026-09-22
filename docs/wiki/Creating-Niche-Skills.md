# Creating Niche Skills 🧩

OmniPress separates the **publishing machinery** (the MCP server) from the **domain intelligence** (Agent Skills). This enables anyone to build and share custom skills for any industry, discipline, or community.

---

## 1. What is an OmniPress Skill?

An OmniPress Skill is a markdown document (`SKILL.md`) located in `.agents/skills/<skill-name>/` that instructs the AI agent on:
- **Audience & Tone**: The exact vocabulary, formality, and analytical depth required.
- **Ethical & Compliance Rules**: Industry-specific constraints (e.g., medical disclaimers, judicial secrecy, financial compliance).
- **Target Platform Tuning**: Which platforms matter most for this niche and how to frame posts for each.

---

## 2. Skill Template

Create a folder `.agents/skills/omnipress-<your-niche>/` and add a `SKILL.md`:

```markdown
---
name: omnipress-<your-niche>
description: OmniPress Niche Skill for <Your Domain/Industry Name>.
---

# OmniPress <Domain Name> Skill

Use this skill when drafting content related to <specific topic>.

## 1. Persona & Tone Guidelines
- **Audience**: Who is reading this? (e.g., CTOs, corporate attorneys, medical researchers, retail investors).
- **Tone**: How should it sound? (e.g., analytical, empirical, provocative, institutional).
- **Formatting Standards**: Bullets, code blocks, or citation styles.

## 2. Domain Constraints & Safety Rules
- Mention any sensitive regulations (e.g., HIPAA, LGPD, SEC rules, judicial secrecy).
- Instruct the agent to call `omnipress_inspect_content` if uncertain.

## 3. Platform Distribution Strategy
1. **Long-form Article**:
   - Structure: Problem $\rightarrow$ Evidence $\rightarrow$ Practical Implementation $\rightarrow$ Takeaways.
   - Frontmatter tags to apply.
2. **LinkedIn**:
   - Executive-level summary with 3-5 structured takeaways.
3. **X & Threads**:
   - Micro-insights and provocative questions.
4. **Reddit**:
   - Target subreddits (e.g., `r/sub1`, `r/sub2`).
   - Frame posts around problems solved rather than self-promotion.

## 4. MCP Tool Invocation Runbook
- Save article via `omnipress_publish_article(...)`.
- Queue social drafts via `omnipress_queue_post(text=..., platforms=[...])`.
```

---

## 3. Included Niche Skills

OmniPress comes bundled with starter skills in `.agents/skills/`:

| Skill Name | Target Niche | Key Channels |
| :--- | :--- | :--- |
| `omnipress-tech` | Software Engineering, Open Source, Architecture | Dev.to, LinkedIn, X, Reddit `r/programming`, `r/webdev` |
| `omnipress-tax-legal` | Tax Law, Judicial Forensics (*Perícia*), LegalTech | Jusbrasil, Substack, LinkedIn, Reddit `r/direito` |
| `omnipress-govtech` | Public Administration, Civic Tech, Digital Policy | Medium, LinkedIn, Threads, X |

---

## 4. Community Contribution

Have you built a specialized skill for **Biomedical Research**, **Crypto & Web3**, **Real Estate**, or **Growth Marketing**?
Submit a Pull Request to add your skill to `.agents/skills/`!
