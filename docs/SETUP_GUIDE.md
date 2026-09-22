# ⚙️ OmniPress Setup & Account Configuration Guide

[🇺🇸 English](SETUP_GUIDE.md) | [🇧🇷 Versão em Português](SETUP_GUIDE.pt-BR.md)

This guide walks you through setting up credentials for **LinkedIn**, **X (Twitter)**, **Meta Threads**, **Reddit**, and custom **Webhooks** in OmniPress MCP.

---

## 1. Buffer Setup (LinkedIn, X, and Meta Threads)

Buffer manages scheduling for LinkedIn, X, and Meta Threads. OmniPress always queues posts as **Drafts/Review Items**, allowing you to preview and approve them before they go live.

### Step 1.1: Connect Your Social Channels
1. Go to [buffer.com](https://buffer.com) and create a free account.
2. Connect your desired channels:
   - **LinkedIn Profile or Company Page**
   - **X (Twitter) Profile**
   - **Meta Threads Profile**

### Step 1.2: Obtain Your Buffer Developer Token
1. Open the [Buffer Developer Portal](https://buffer.com/developers/apps/create).
2. Create a new Developer Application:
   - **Name**: `OmniPress-MCP`
   - **Description**: `Personal Agentic Publishing Assistant`
   - **Callback URL**: `http://localhost` (not used for personal tokens)
3. Once created, open your app settings and locate the **Developer Access Token**.
4. Copy this token.

### Step 1.3: Retrieve Channel Profile IDs
To find the unique ID for each connected network:
1. Open this URL in your browser:
   `https://api.bufferapp.com/1/profiles.json?access_token=YOUR_ACCESS_TOKEN` (replace with your token).
2. Look through the returned JSON objects for:
   - `service: "linkedin"` $\rightarrow$ copy its `"id"`
   - `service: "twitter"` $\rightarrow$ copy its `"id"`
   - `service: "threads"` $\rightarrow$ copy its `"id"`

### Step 1.4: Add to `.env`
```env
BUFFER_ACCESS_TOKEN=your_buffer_token_here
BUFFER_LINKEDIN_PROFILE_ID=your_linkedin_profile_id
BUFFER_X_PROFILE_ID=your_x_profile_id
BUFFER_THREADS_PROFILE_ID=your_threads_profile_id
```

---

## 2. Reddit API Setup (Direct Subreddit Submissions)

OmniPress connects directly to Reddit's official API using a standard developer Script App. This enables publishing rich self-posts directly to targeted communities (e.g., `r/programming`, `r/webdev`, `r/SideProject`, `r/direito`).

### Step 2.1: Create a Reddit Developer Script App
1. Log into your Reddit account and navigate to [reddit.com/prefs/apps](https://www.reddit.com/prefs/apps).
2. Scroll to the bottom and click **"are you a developer? create an app..."** (or **"create another app..."**).
3. Fill in the fields:
   - **name**: `omnipress`
   - **App type**: Select the radio button for **script** (*personal use script*).
   - **description**: `OmniPress MCP Content Automation`
   - **about url**: `https://github.com` (can be any valid URL)
   - **redirect uri**: `http://localhost:8080`
4. Click **create app**.

### Step 2.2: Retrieve Reddit Credentials
After creation:
- **Client ID**: The string located directly underneath the text `personal use script` (approx. 14 characters, e.g., `a1B2c3D4e5F6g7`).
- **Client Secret**: The string labeled `secret` inside the app box.
- **Username**: Your Reddit account username (without `/u/`).
- **Password**: Your Reddit account password.

### Step 2.3: Configure in `.env`
```env
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret
REDDIT_USERNAME=your_reddit_username
REDDIT_PASSWORD=your_reddit_password
REDDIT_DEFAULT_SUBREDDIT=SideProject
```

### Step 2.4: How to Target Specific Subreddits
In Antigravity chat, specify the target subreddit:
> *"OmniPress: Post this technical breakdown of our database indexing architecture to Reddit r/webdev and r/programming."*

Antigravity will pass `platforms: ["reddit:webdev", "reddit:programming"]` to the MCP tool.

---

## 3. Webhook & n8n Pipeline Setup (Optional)

OmniPress can dispatch full JSON event payloads to **n8n**, Make, Slack, Telegram, or custom webhooks.

### Step 3.1: Configure Webhook
```env
OMNIPRESS_WEBHOOK_URL=https://your-n8n-instance.com/webhook/omnipress
OMNIPRESS_WEBHOOK_SECRET=your_optional_hmac_secret
```

### Step 3.2: Payload Structure
```json
{
  "event": "social_post_queued",
  "source": "omnipress-mcp",
  "timestamp": "2026-09-22T06:30:00.000Z",
  "data": {
    "text": "Post content...",
    "platforms": ["linkedin", "threads", "reddit:SideProject"],
    "mediaUrls": [],
    "scheduleTime": null,
    "draft": true
  }
}
```
If `OMNIPRESS_WEBHOOK_SECRET` is set, OmniPress includes an `X-OmniPress-Signature` header computed via HMAC SHA-256.

---

## 4. Local Markdown Archive Settings

By default, articles are stored in:
```
articles/
└── YYYY/
    └── MM/
        └── YYYY-MM-DD-article-slug.md
```

To redirect archives to an Obsidian vault or blog repository:
```env
ARTICLES_DIR=C:/Users/Ismael/Documents/MyVault/Articles
```

---

## 5. Verification in Antigravity

1. Run the test suite:
   ```bash
   npm test
   ```
2. In Antigravity chat, test multi-platform queuing:
   > *"OmniPress: Prepare a release post for our open-source project and queue it for LinkedIn, Threads, and Reddit r/SideProject."*
