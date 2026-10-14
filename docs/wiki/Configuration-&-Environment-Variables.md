# Configuration & Environment Variables ⚙️

OmniPress is designed to be zero-friction. Without any credentials configured, it safely archives Markdown articles locally and outputs formatted social copy directly into your AI agent's chat interface.

To enable automated dispatch to LinkedIn, X, Meta Threads, Instagram, Reddit, or Webhooks, configure a `.env` file in the project root.

---

## 1. Environment Reference Table

| Variable | Required For | Example / Format | Description |
| :--- | :--- | :--- | :--- |
| `OMNIPRESS_ACTIVE_CHANNEL` | Channel Management | `dossie-historico` | Default active channel slug for isolated workspaces. |
| `ARTICLES_DIR` | Markdown Archive | `./articles` | Default destination folder for archived `.md` files. |
| `BUFFER_API_KEY` | Buffer Modern GraphQL | `1/0a1b2c3d4e5f...` | Personal API Key from `publish.buffer.com/settings/api`. |
| `BUFFER_ACCESS_TOKEN` | Buffer Legacy REST | `1/0a1b2c3d4e5f...` | Legacy developer access token. |
| `BUFFER_LINKEDIN_PROFILE_ID` | LinkedIn via Buffer | `64f1a2b3c4d5e6f7a8b9c0d1` | 24-character hex ID of your LinkedIn channel. |
| `BUFFER_X_PROFILE_ID` | X (Twitter) via Buffer | `64f1a2b3c4d5e6f7a8b9c0d2` | 24-character hex ID of your X channel. |
| `BUFFER_THREADS_PROFILE_ID` | Meta Threads via Buffer | `64f1a2b3c4d5e6f7a8b9c0d3` | 24-character hex ID of your Threads channel. |
| `BUFFER_INSTAGRAM_PROFILE_ID` | Instagram via Buffer | `64f1a2b3c4d5e6f7a8b9c0d4` | 24-character hex ID of your Instagram channel. |
| `INSTAGRAM_ACCESS_TOKEN` | Direct Meta Graph API | `EAAX...` | Meta Long-Lived Page Access Token for direct Instagram posting. |
| `INSTAGRAM_ACCOUNT_ID` | Direct Meta Graph API | `1784140...` | Instagram Business Account ID. |
| `REDDIT_CLIENT_ID` | Reddit Direct Submissions | `a1B2c3D4e5F6g7` | Script App client ID from `reddit.com/prefs/apps`. |
| `REDDIT_CLIENT_SECRET` | Reddit Direct Submissions | `xyz987_abc123...` | App secret key. |
| `REDDIT_USERNAME` | Reddit Direct Submissions | `my_reddit_username` | Reddit account username (without `/u/`). |
| `REDDIT_PASSWORD` | Reddit Direct Submissions | `my_secure_password` | Reddit account password. |
| `REDDIT_DEFAULT_SUBREDDIT` | Reddit Fallback | `SideProject` | Default subreddit when not specified in prompt. |
| `MEDIA_STAGING_DIR` | Video / Staging Assets | `./media/staging` | Staging folder for video renders, TTS audio, and dark channel scripts. |
| `S3_BUCKET_NAME` | Cloud Media Storage | `omnipress-media` | AWS S3, Cloudflare R2, or MinIO bucket for public media assets. |
| `S3_ENDPOINT_URL` | Cloud Media Storage | `https://<id>.r2.cloudflarestorage.com` | Custom endpoint URL for Cloudflare R2 or MinIO (omit for AWS S3). |
| `S3_PUBLIC_URL_PREFIX` | Cloud Media Storage | `https://media.mybrand.com` | Public HTTPS CDN domain prefix for uploaded media assets. |
| `OMNIPRESS_PUBLIC_URL` | Local Container Hosting | `https://omnipress.suitplus.com.br` | Public base URL when serving staged media directly from container. |
| `YOUTUBE_WEBHOOK_URL` | Video Automation | `https://n8n...` | Webhook URL for YouTube upload automation. |
| `TIKTOK_WEBHOOK_URL` | Video Automation | `https://n8n...` | Webhook URL for TikTok automation. |
| `OMNIPRESS_WEBHOOK_URL` | Webhook Pipeline | `https://n8n.../webhook` | Endpoint URL to receive JSON events. |
| `OMNIPRESS_WEBHOOK_SECRET` | Webhook HMAC Signature | `my_hmac_secret` | Secret key used to sign payloads. |
| `OMNIPRESS_MODE` | Server Transport | `stdio` / `http` | Transport mode: `stdio` (local agents) or `http` (Docker/Coolify SSE). |
| `PORT` | HTTP/SSE Server Port | `3333` | Port for the HTTP/SSE ASGI server. |

---

## 2. Storage & Directory Structure Conventions

OmniPress provides two layers of storage:
1. **Multi-Channel Workspaces (`channels/<slug>/`)**: Canonical, isolated directory for each media brand, containing its own `channel.json`, `articles/`, and `media/`.
2. **Root Fallback (`articles/` and `media/`)**: Standalone, general-purpose directories used when tools are invoked without an explicit channel slug.

---

## 3. Quick Setup Checklist

1. Copy the template:
   ```bash
   cp .env.example .env
   ```
2. Add the credentials for the services you wish to activate.
3. Test the setup:
   ```bash
   uv run pytest -v
   npm run typecheck
   ```
