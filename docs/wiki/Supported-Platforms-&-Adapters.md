# Supported Platforms & Adapters 🌐

OmniPress provides built-in modular adapters for major professional and community networks, as well as arbitrary webhook targets.

---

## 1. LinkedIn (via Buffer)
- **Format**: Text posts and carousel copy.
- **Queue Mode**: Queued as a **Draft** in Buffer. You receive a notification on your phone/browser to review before it goes live.
- **Environment**:
  - `BUFFER_ACCESS_TOKEN`
  - `BUFFER_LINKEDIN_PROFILE_ID`
- **Tool Invocation**:
  ```json
  {
    "platforms": ["linkedin"]
  }
  ```

---

## 2. X / Twitter (via Buffer)
- **Format**: Concise tweets or multi-tweet threads.
- **Queue Mode**: Queued as Draft.
- **Environment**:
  - `BUFFER_ACCESS_TOKEN`
  - `BUFFER_X_PROFILE_ID`
- **Tool Invocation**:
  ```json
  {
    "platforms": ["x"]
  }
  ```

---

## 3. Meta Threads (via Buffer)
- **Format**: Conversational community insights.
- **Queue Mode**: Queued as Draft.
- **Environment**:
  - `BUFFER_ACCESS_TOKEN`
  - `BUFFER_THREADS_PROFILE_ID`
- **Tool Invocation**:
  ```json
  {
    "platforms": ["threads"]
  }
  ```

---

## 4. Reddit (Direct Script OAuth2 API)
- **Format**: Rich Markdown self-posts submitted directly to communities.
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

## 5. Local Markdown Archive
- **Format**: GitHub-flavored Markdown with standard YAML frontmatter:
  ```markdown
  ---
  title: "Article Title"
  date: "2026-09-22T06:00:00.000Z"
  category: "technology"
  author: "OmniPress"
  tags:
    - mcp
    - agentic
  status: draft
  ---
  ```
- **Storage**: Automatically grouped by `YYYY/MM/`.
- **Environment**: `ARTICLES_DIR=./articles`

---

## 6. Custom Webhooks & n8n
- **Format**: JSON event payload dispatched via HTTP POST.
- **Signature**: If `OMNIPRESS_WEBHOOK_SECRET` is set, includes `X-OmniPress-Signature` HMAC SHA-256 header.
- **Integration**: Easily connects to n8n, Make, Slack incoming webhooks, Telegram bots, or Discord webhooks.
