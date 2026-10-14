# Hands-On Step-by-Step Guide 🚀

This guide provides an end-to-end walkthrough for getting started, configuring, and publishing with **OmniPress MCP** using AI agents like Google Antigravity or Claude Desktop.

---

## Step 1: Environment Setup & Installation

Clone the repository and set up the Python virtual environment:

```bash
# 1. Clone repository
git clone https://github.com/ismaelsoilet/omnipress-mcp.git
cd omnipress-mcp

# 2. Install Python dependencies with uv
uv sync
```

Verify your environment by running the test suites:
```bash
uv run pytest -v     # Python test suite
npm run typecheck    # Remotion TypeScript integrity check
```

---

## Step 2: Environment Variables (`.env`)

Copy the configuration template:
```bash
cp .env.example .env
```

> **Offline Mode**: If no API keys are provided in `.env`, OmniPress operates safely in offline mode. Articles are archived locally in Markdown and social post texts are formatted in chat ready for manual copying.

To enable live social queues and direct publishing, configure:
- **Buffer**: `BUFFER_API_KEY`, `BUFFER_LINKEDIN_PROFILE_ID`, `BUFFER_X_PROFILE_ID`, `BUFFER_THREADS_PROFILE_ID`
- **Instagram Graph API**: `INSTAGRAM_ACCESS_TOKEN`, `INSTAGRAM_ACCOUNT_ID`
- **Reddit**: `REDDIT_CLIENT_ID`, `REDDIT_CLIENT_SECRET`, `REDDIT_USERNAME`, `REDDIT_PASSWORD`
- **Webhooks**: `OMNIPRESS_WEBHOOK_URL`, `OMNIPRESS_WEBHOOK_SECRET`

---

## Step 3: Registering OmniPress in Your AI Agent

### Google Antigravity
Add to `~/.gemini/config/mcp_config.json`:
```json
{
  "mcpServers": {
    "omnipress": {
      "command": "/path/to/omnipress-mcp/.venv/bin/python",
      "args": ["-m", "src.server"],
      "env": {
        "OMNIPRESS_ACTIVE_CHANNEL": "dossie-historico"
      }
    }
  }
}
```

### Claude Desktop
Add to `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "omnipress": {
      "command": "python",
      "args": ["/path/to/omnipress-mcp/src/server.py"]
    }
  }
}
```

---

## Step 4: Multi-Channel Management (CLI & MCP)

OmniPress provides isolated workspaces for each content channel in `channels/<slug>/`.

### Using the CLI (`src/cli.py`)
```bash
# List all channels
python src/cli.py list-channels

# Create a new channel
python src/cli.py create-channel dev-bytes \
  --name "Developer Bytes" \
  --handle "@devbytes.io" \
  --category "tech" \
  --color "#2563EB"

# Inspect channel brand details
python src/cli.py info-channel dev-bytes
```

### Using MCP Prompts
> *"OmniPress: List all configured channels and show the current active channel."*

---

## Step 5: Publishing Workflows in Practice

### 1. Long-Form Article Archiving (`omnipress_publish_article`)
Prompts like:
> *"OmniPress: Write an in-depth article analyzing modern microservices latency. Archive it for the active channel."*

OmniPress generates clean Markdown with YAML frontmatter, runs privacy filters, and saves to:
`channels/<slug>/articles/YYYY/MM/YYYY-MM-DD-article-slug.md`.

### 2. Social Carousel Generation 3:4 (`omnipress_build_carousel`)
1. Place reference background images in `channels/<slug>/media/raw/`.
2. Provide slide JSON data:
```json
[
  {
    "bg_image": "channels/dev-bytes/media/raw/slide1.jpg",
    "headline": "Why Rust Over C++ in 2026?",
    "body": "Memory safety guarantees without garbage collection overhead.",
    "page_str": "01/04"
  }
]
```
3. Run the CLI renderer or ask the AI:
```bash
python src/cli.py build-carousel \
  --channel dev-bytes \
  --post rust-vs-cpp \
  --config slides.json \
  --aspect-ratio 3:4
```
Outputs high-contrast portrait slides in `channels/dev-bytes/media/carousels/rust-vs-cpp/`.

### 3. Queueing Social Posts (`omnipress_queue_post`)
Dispatches sanitized text to LinkedIn, X, Threads, Instagram, or Reddit:
> *"OmniPress: Queue this summary to LinkedIn, Threads, and Reddit r/programming."*

Posts arrive as **Drafts** in your Buffer or Instagram queue for human review.

### 4. Viral Dark Channel Video Production (`omnipress_prepare_dark_script`)
> *"OmniPress: Prepare a 50-second high-retention dark channel script on 'The Ghost Army of WWII'."*

Returns:
- 3-second retention hook.
- Scene-by-scene script with Midjourney / AI image generation prompts.
- TTS voice direction and Instagram/YouTube SEO tags.

### 5. Privacy & Data Leak Inspection (`omnipress_inspect_content`)
Use this tool before publishing any legal or code document:
> *"OmniPress: Inspect this case study text to ensure no lawsuits, CPFs, or API tokens leak."*
