---
name: omnipress
description: Agentic publishing engine. Turns raw thoughts, case studies, codebases, tax legislation, and public admin topics into authoritative long-form articles, LinkedIn carousels/posts, and X threads, dispatching them via OmniPress MCP tools.
---

# OmniPress — Agentic Publishing Runbook

Use this skill whenever the user asks to write, draft, adapt, or publish articles or social media posts across Technology, Tax Law, Judicial Expert Analysis (Perícia Judicial), Public Administration, or general thought leadership.

---

## 1. Dynamic Tone & Domain Adaptation

OmniPress dynamically adapts tone based on the user's subject:
- **Tax & Fiscal (Tributário)**: Authoritative, analytical, anchored in legislation, administrative rulings (CARF), or judicial precedents (STF/STJ). Focus on fiscal impact, compliance, and technological feasibility.
- **Judicial Expert Analysis (Perícia Judicial)**: Forensic, objective, strictly separating technical evidence from subjective interpretations. Explains complex algorithms, database audits, or system logs in clear language for judges and lawyers.
- **Technology & Software**: Pragmatic engineering focus—trade-offs, system architecture, performance, clean code, and practical implementations.
- **Public Administration & GovTech**: Civic impact, regulatory compliance, digital transformation, efficiency, and public transparency.

---

## 2. Privacy, Ethics & De-Identification Rules

> [!CAUTION]
> **Strict Anonymization**: Never publish private lawsuit numbers, confidential process details (*segredo de justiça*), or identifiable PII (tax IDs, names of disputing parties, internal server IPs).

- Always replace company or litigant names with generic descriptors (e.g., *"Uma grande empresa do setor varejista"*, *"Empresa A"*).
- When in doubt, call `omnipress_inspect_content(text)` to verify zero PII leakage.

---

## 3. The Tri-Format Repurposing Workflow

When processing a topic, generate three cohesive assets:

### Asset 1: Long-Form Technical Article & Syndication (Markdown / Dev.to / Ghost CMS)
- **Title**: High-impact, search-optimized.
- **Structure**:
  - Context / The Real-World Problem
  - The Core Mechanism / Legal-Tech Breakdown
  - Forensic or Practical Evidence
  - Actionable Recommendations
- **Syndication Targets**:
  - Local Markdown Archive: `target_platform="markdown"` (default)
  - Developer Community: `target_platform="devto"` (Dev.to REST API)
  - Independent Publication: `target_platform="ghost"` (Ghost CMS Admin API v5.0)
  - Full Syndication: `target_platform="all"`
- **Tool**: Call `omnipress_publish_article(title=..., content_markdown=..., category=..., tags=[...], target_platform="...", published=False)`.

### Asset 2: High-Authority LinkedIn Post
- **Opening (Hook)**: One compelling line highlighting a counter-intuitive finding or critical risk.
- **Body**: 3 to 5 clean bullet points detailing the insight.
- **Closing**: Direct question to spark professional debate in the comments.
- **Hashtags**: 3 to 5 targeted tags (e.g., `#DireitoTributario #LegalTech #PericiaJudicial #GovTech`).
- **Tool**: Call `omnipress_queue_post(text=..., platforms=["linkedin"])`.

### Asset 3: Punchy X Thread
- **Tweet 1 (Hook)**: Summary statement + thread emoji (🧵).
- **Tweets 2-4**: Concise, high-signal takeaways.
- **Final Tweet**: Summary conclusion + call-to-action.
- **Tool**: Call `omnipress_queue_post(text=..., platforms=["x"])`.

### Asset 4: Meta Threads & Reddit Community Breakdown
- **Meta Threads**: Engaging, bite-sized conversational insight.
  - **Tool**: Call `omnipress_queue_post(text=..., platforms=["threads"])`.
- **Reddit Community Submission**: Transparent, authentic breakdown without promotional fluff.
  - Includes clear descriptive title.
  - **Tool**: Call `omnipress_queue_post(text=..., platforms=["reddit:sub_name"], title="...")`.

### Asset 5: High-Contrast Visual Carousel Deck (Instagram / LinkedIn - Rule 08)
- 4 to 7 portrait slides (3:4 ratio) with dark protective card backdrop (`rgba(8, 10, 14, 215)`) and safety typography stroke (`stroke_width=2`).
- **Tool**: Call `omnipress_build_carousel(channel_slug="...", post_slug="...", slides_json="...", aspect_ratio="3:4")`.

### Asset 6: Viral Dark Channel Pipeline (YouTube Shorts / Reels / TikTok)
- **Concept & CTR Hook**: Call `omnipress_brainstorm_channel(niche="...", tone="...")`.
- **Scene Script Bundle**: Call `omnipress_prepare_dark_script(topic="...", channel_slug="...")`.
- **Neural Voiceover**: Call `omnipress_generate_speech(text="...", voice="pt-BR-AntonioNeural")`.
- **MP4 Video Render**: Call `omnipress_render_dark_video(audio_path="...", image_paths=[...], aspect_ratio="9:16")`.
- **Media Queue**: Call `omnipress_queue_media_post(caption="...", platforms=["instagram", "youtube"], media_urls=[...])`.

---

## 4. Interaction Standard & Reference Manual

1. Present the draft assets clearly to the user in chat for rapid review.
2. Ask for a quick confirmation: *"Should I archive the article (and syndicate to Dev.to/Ghost) and queue the social posts?"*
3. Execute the corresponding MCP tools (`omnipress_publish_article`, `omnipress_queue_post`, `omnipress_build_carousel`) upon user green light.
4. For diagnostics, verify the host environment with `omnipress doctor` or `omnipress status`.
5. For comprehensive tool schemas, JSON payloads, and execution playbooks, see [`docs/AGENT_MANUAL.md`](file:///home/ismaelsoilet/omnipress-mcp/docs/AGENT_MANUAL.md).
