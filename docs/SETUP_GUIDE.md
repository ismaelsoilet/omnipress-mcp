# ⚙️ OmniPress Setup & Account Configuration Guide

[🇺🇸 English](SETUP_GUIDE.md) | [🇧🇷 Versão em Português](SETUP_GUIDE.pt-BR.md)

This document provides a comprehensive step-by-step guide to configuring publishing credentials for **Buffer** (LinkedIn, X, Threads), direct **Instagram Graph API**, **Reddit**, **Webhooks**, and the **Multi-Channel Architecture** in OmniPress MCP.

---

## 1. Buffer Setup (LinkedIn, X / Twitter, and Meta Threads)

Buffer manages scheduling for LinkedIn, X (Twitter), and Meta Threads. OmniPress always queues posts as **Drafts/Review Items**, allowing you to preview and approve them on your phone or web dashboard before they go live.

### Step 1.1: Connect Your Social Channels
1. Go to [buffer.com](https://buffer.com) and log in to your account.
2. Connect your desired channels:
   - **LinkedIn Profile or Company Page**
   - **X (Twitter) Profile**
   - **Meta Threads Profile**
   - **Instagram Business / Creator Account** (optional, if publishing via Buffer)

### Step 1.2: Obtain Your Buffer API Key
OmniPress supports both Buffer's modern GraphQL API and the legacy REST API:
1. Navigate to [publish.buffer.com/settings/api](https://publish.buffer.com/settings/api).
2. Copy your **Personal API Key** (or create an app in the [Buffer Developer Portal](https://buffer.com/developers/apps/create)).
3. Add to your `.env` file:
   ```env
   BUFFER_API_KEY=your_buffer_token_here
   BUFFER_ACCESS_TOKEN=your_buffer_token_here
   ```

### Step 1.3: Retrieve Channel Profile IDs
To find the unique ID for each connected network:
1. Open this URL in your browser:
   `https://api.bufferapp.com/1/profiles.json?access_token=YOUR_ACCESS_TOKEN` (replace with your token).
2. Look through the returned JSON objects for:
   - `service: "linkedin"` $\rightarrow$ copy its `"id"`
   - `service: "twitter"` $\rightarrow$ copy its `"id"`
   - `service: "threads"` $\rightarrow$ copy its `"id"`
   - `service: "instagram"` $\rightarrow$ copy its `"id"`
   - `service: "youtube"` $\rightarrow$ copy its `"id"`

### Step 1.4: Add to `.env`
```env
BUFFER_API_KEY=your_token_here
BUFFER_ACCESS_TOKEN=your_token_here
BUFFER_LINKEDIN_PROFILE_ID=your_linkedin_profile_id
BUFFER_X_PROFILE_ID=your_x_profile_id
BUFFER_THREADS_PROFILE_ID=your_threads_profile_id
BUFFER_INSTAGRAM_PROFILE_ID=your_instagram_profile_id
BUFFER_YOUTUBE_PROFILE_ID=your_youtube_channel_id
```

> 💡 **Multi-Channel Tip**: If you manage multiple brands, you can configure `buffer_channel_id` directly in each channel's `channels/<slug>/channel.json` under `social.instagram` or `social.youtube`! OmniPress prioritizes the channel-specific ID before falling back to `.env`.

---

## 2. Direct Instagram Graph API Setup (Autonomous Publishing)

If you prefer to publish single images and carousel posts directly to your Instagram Professional Account without Buffer:

### Step 2.1: Prerequisites
- An **Instagram Professional Account** (Business or Creator).
- A **Facebook Page** linked to your Instagram Account.
- A Meta Developer App at [developers.facebook.com](https://developers.facebook.com/) with:
  - `instagram_basic`
  - `instagram_content_publish` permissions.

### Step 2.2: Configure in `.env`
```env
INSTAGRAM_ACCESS_TOKEN=your_long_lived_meta_access_token
INSTAGRAM_ACCOUNT_ID=your_instagram_business_account_id
```

---

## 3. Reddit API Setup (Direct Subreddit Submissions)

OmniPress connects directly to Reddit's official API using a standard developer Script App. This enables publishing rich self-posts directly to targeted communities (e.g., `r/programming`, `r/webdev`, `r/SideProject`, `r/direito`, `r/contabilidade`).

### Step 3.1: Create a Reddit Developer Script App
1. Log into your Reddit account and navigate to [reddit.com/prefs/apps](https://www.reddit.com/prefs/apps).
2. Scroll to the bottom and click **"are you a developer? create an app..."** (or **"create another app..."**).
3. Fill in the fields:
   - **name**: `omnipress`
   - **App type**: Select the radio button for **script** (*personal use script*).
   - **description**: `OmniPress MCP Content Automation`
   - **about url**: `https://github.com`
   - **redirect uri**: `http://localhost:8080`
4. Click **create app**.

### Step 3.2: Retrieve Reddit Credentials
After creation:
- **Client ID**: The string located directly underneath the text `personal use script` (approx. 14 characters, e.g., `a1B2c3D4e5F6g7`).
- **Client Secret**: The string labeled `secret` inside the app box.
- **Username**: Your Reddit account username (without `/u/`).
- **Password**: Your Reddit account password.

### Step 3.3: Configure in `.env`
```env
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret
REDDIT_USERNAME=your_reddit_username
REDDIT_PASSWORD=your_reddit_password
REDDIT_DEFAULT_SUBREDDIT=SideProject
```

### Step 3.4: How to Target Specific Subreddits
In Antigravity or Claude chat, specify the target subreddit:
> *"OmniPress: Post this technical breakdown of our database indexing architecture to Reddit r/webdev and r/programming."*

The agent will automatically pass `platforms: ["reddit:webdev", "reddit:programming"]` to the MCP tool!

---

## 4. Multi-Channel Architecture & Command-Line Interface (CLI)

OmniPress supports multiple isolated channels (history, tech, legal, dark channels, finance) with zero asset overlap:

### Channel Directory Structure
```
channels/dossie-historico/
  ├── channel.json             # Branding metadata, color palette, handles, and buffer ID
  ├── articles/                # Long-form archived articles organized by YYYY/MM/
  ├── media/
  │   ├── raw/                 # Source and reference assets
  │   ├── carousels/           # Generated 3:4 portrait carousel decks
  │   ├── stories/             # 9:16 vertical stories
  │   └── highlights/          # Instagram highlight covers
  └── scripts/                 # Channel-specific pipelines
```

### CLI Commands (`src/cli.py`)
```bash
# 1. List all configured channels
python src/cli.py list-channels

# 2. Scaffold a new channel workspace
python src/cli.py create-channel fin-pro \
  --name "Finance Pro" \
  --handle "@finance.pro" \
  --category "finance" \
  --color "#10B981"

# 3. View details and brand configuration of a channel
python src/cli.py info-channel fin-pro

# 4. Render a branded 3:4 carousel deck
python src/cli.py build-carousel \
  --channel fin-pro \
  --post compound-interest \
  --config path/to/slides.json \
  --aspect-ratio 3:4
```

### Setting the Default Active Channel
In your `.env` file:
```env
OMNIPRESS_ACTIVE_CHANNEL=fin-pro
```

---

## 5. Webhook & n8n Pipeline Setup (Optional)

OmniPress can dispatch full JSON event payloads to **n8n**, Make, Slack, Telegram, or custom webhooks:

```env
OMNIPRESS_WEBHOOK_URL=https://your-n8n-instance.com/webhook/omnipress
OMNIPRESS_WEBHOOK_SECRET=your_optional_hmac_secret
```

If `OMNIPRESS_WEBHOOK_SECRET` is set, OmniPress includes an `X-OmniPress-Signature` header in every HTTP POST request containing an HMAC SHA-256 signature for cryptographic verification.

---

## 6. Antigravity & Claude Desktop Configuration

### Google Antigravity (`~/.gemini/config/mcp_config.json`)
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

### Claude Desktop (`claude_desktop_config.json`)
```json
{
  "mcpServers": {
    "omnipress": {
      "command": "python",
      "args": ["/path/to/omnipress-mcp/src/server.py"],
      "env": {
        "ARTICLES_DIR": "/path/to/omnipress-mcp/articles"
      }
    }
  }
}
```

---

## 7. Testing & Verification

To verify that all publisher adapters and channel workspace engines are functioning properly:

```bash
# Run the Python test suite:
uv run pytest -v

# Run the Remotion TypeScript typecheck:
npm run typecheck
```
