# Supported Platforms & Adapters 🌐

OmniPress provides built-in modular adapters for major social networks, direct media publishing, and automation webhooks.

---

## 1. LinkedIn (via Buffer)
- **Format**: Text posts, bulleted takeaways, discussion prompts, and carousel copy.
- **Queue Mode**: Queued as a **Draft** in Buffer for human review before going live.
- **Environment**:
  - `BUFFER_API_KEY` (or `BUFFER_ACCESS_TOKEN`)
  - `BUFFER_LINKEDIN_PROFILE_ID`
- **Tool Invocation**:
  ```json
  {
    "platforms": ["linkedin"]
  }
  ```

---

## 2. X / Twitter (via Buffer)
- **Format**: Single tweets or multi-tweet connected narrative threads.
- **Queue Mode**: Queued as Draft in Buffer.
- **Environment**:
  - `BUFFER_API_KEY` (or `BUFFER_ACCESS_TOKEN`)
  - `BUFFER_X_PROFILE_ID`
- **Tool Invocation**:
  ```json
  {
    "platforms": ["x"]
  }
  ```

---

## 3. Meta Threads (via Buffer)
- **Format**: Conversational, community-focused insights.
- **Queue Mode**: Queued as Draft in Buffer.
- **Environment**:
  - `BUFFER_API_KEY` (or `BUFFER_ACCESS_TOKEN`)
  - `BUFFER_THREADS_PROFILE_ID`
- **Tool Invocation**:
  ```json
  {
    "platforms": ["threads"]
  }
  ```

---

## 4. Instagram (Direct Graph API & Buffer)
- **Format**: Single images and 3:4 portrait carousel decks (up to 10 slides).
- **Direct Publishing via Meta Graph API**:
  - `INSTAGRAM_ACCESS_TOKEN`
  - `INSTAGRAM_ACCOUNT_ID`
- **Alternative Publishing via Buffer GraphQL**:
  - `BUFFER_API_KEY` (or `BUFFER_ACCESS_TOKEN`)
  - `BUFFER_INSTAGRAM_PROFILE_ID` (or dynamic `buffer_channel_id` mapped in `channels/<slug>/channel.json`)
  - Automatically injects required `metadata.instagram.type = "post"` and `shouldShareToFeed = true`.
- **Publishing Shield Safeguards**:
  - **Character limit**: Strict cutoff at **2,196 characters** (Buffer GraphQL limit).
  - **Media requirement**: Rejects text-only posts without media URLs.
  - **Anti-duplicate**: Blocks duplicate submissions within 24 hours.
  - **Test interceptor**: Blocks dummy `"teste"` texts on live `shareNow`.
- **Tool Invocation**:
  ```json
  {
    "platforms": ["instagram"],
    "media_urls": ["https://example.com/slide1.jpg", "https://example.com/slide2.jpg"],
    "channel_slug": "dossie-historico",
    "mode": "shareNow"
  }
  ```

---

## 5. Reddit (Direct Script OAuth2 API)
- **Format**: Rich Markdown self-posts submitted directly to targeted communities.
- **Targeting**: Specify the target subreddit dynamically in the platform argument:
  ```json
  {
    "platforms": ["reddit:webdev", "reddit:SideProject"],
    "title": "How we built a zero-dependency MCP server"
  }
  ```
- **Environment**:
  - `REDDIT_CLIENT_ID`
  - `REDDIT_CLIENT_SECRET`
  - `REDDIT_USERNAME`
  - `REDDIT_PASSWORD`
  - `REDDIT_DEFAULT_SUBREDDIT`

---

## 6. Local Markdown Archive (Multi-Channel)
- **Format**: GitHub-flavored Markdown with complete YAML frontmatter:
  ```markdown
  ---
  title: "Article Title"
  date: "2026-10-11T12:00:00.000Z"
  category: "technology"
  author: "OmniPress"
  tags:
    - mcp
    - agentic
  status: draft
  ---
  ```
- **Storage**: Organized by channel in `channels/<slug>/articles/YYYY/MM/` or globally in `articles/YYYY/MM/`.
- **Environment**: `ARTICLES_DIR=./articles`

---

## 7. Custom Webhooks & n8n
- **Format**: JSON event payload dispatched via HTTP POST.
- **Signature**: If `OMNIPRESS_WEBHOOK_SECRET` is set, includes `X-OmniPress-Signature` HMAC SHA-256 header.
- **Integration**: Connects to n8n, Make, Slack incoming webhooks, Telegram bots, or Discord channels.

---

## 8. Carousel Graphics Engine (`CarouselBuilder`)
- **Format**: 3:4 Portrait (1080x1440) or 1:1 Square.
- **Features**: Contrast gradient overlays, pixel-accurate word wrap, and channel branding injection.
- **Tool Invocation**: `omnipress_build_carousel(channel_slug, post_slug, slides_json)`.
