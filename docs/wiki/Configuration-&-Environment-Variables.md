# Configuration & Environment Variables ⚙️

OmniPress is designed to be zero-friction. Without any credentials configured, it safely archives Markdown articles locally and outputs formatted social copy directly into your AI agent's chat interface.

To enable automated dispatch to LinkedIn, X, Meta Threads, Reddit, or Webhooks, configure a `.env` file in the project root.

---

## 1. Environment Reference Table

| Variable | Required For | Example / Format | Description |
| :--- | :--- | :--- | :--- |
| `ARTICLES_DIR` | Markdown Archive | `./articles` or `C:/MyVault/Articles` | Destination folder for archived `.md` files. |
| `BUFFER_ACCESS_TOKEN` | Buffer (LinkedIn/X/Threads) | `1/0a1b2c3d4e5f...` | Developer token from Buffer Apps portal. |
| `BUFFER_LINKEDIN_PROFILE_ID` | LinkedIn via Buffer | `64f1a2b3c4d5e6f7a8b9c0d1` | 24-character hex ID of your LinkedIn channel. |
| `BUFFER_X_PROFILE_ID` | X (Twitter) via Buffer | `64f1a2b3c4d5e6f7a8b9c0d2` | 24-character hex ID of your X channel. |
| `BUFFER_THREADS_PROFILE_ID` | Meta Threads via Buffer | `64f1a2b3c4d5e6f7a8b9c0d3` | 24-character hex ID of your Threads channel. |
| `REDDIT_CLIENT_ID` | Reddit Direct Submissions | `a1B2c3D4e5F6g7` | Script App client ID from `reddit.com/prefs/apps`. |
| `REDDIT_CLIENT_SECRET` | Reddit Direct Submissions | `xyz987_abc123...` | App secret key. |
| `REDDIT_USERNAME` | Reddit Direct Submissions | `my_reddit_username` | Reddit account username (without `/u/`). |
| `REDDIT_PASSWORD` | Reddit Direct Submissions | `my_secure_password` | Reddit account password. |
| `REDDIT_DEFAULT_SUBREDDIT` | Reddit Fallback | `SideProject` | Default subreddit when not specified in prompt. |
| `OMNIPRESS_WEBHOOK_URL` | Webhook Pipeline | `https://n8n.myorg.com/webhook/omnipress` | Endpoint URL to receive JSON events. |
| `OMNIPRESS_WEBHOOK_SECRET` | Webhook HMAC Signature | `my_hmac_secret` | Secret key used to sign payloads. |

---

## 2. Quick Setup Checklist

1. Copy the template:
   ```bash
   cp .env.example .env
   ```
2. Add the credentials for the services you wish to activate.
3. Test the setup:
   ```bash
   npm test
   ```
