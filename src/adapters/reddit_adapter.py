"""Reddit direct posting adapter via official Reddit Script App API."""

import os
import requests
from typing import List, Dict, Any, Optional
from .base import BasePublisherAdapter


class RedditPublisherAdapter(BasePublisherAdapter):
    """Integrates with Reddit OAuth2 API to publish self-posts directly to subreddits."""

    TOKEN_URL = "https://www.reddit.com/api/v1/access_token"
    SUBMIT_URL = "https://oauth.reddit.com/api/submit"

    def __init__(self):
        # Credentials are resolved at call time through ChannelManager (Rule 14).
        pass

    def get_credentials(self, channel_slug: Optional[str] = None) -> tuple[str, str, str, str]:
        """Resolves Reddit credentials with Rule 04 channel precedence."""
        from src.core.channel_manager import ChannelManager

        cm = ChannelManager()
        return (
            cm.get_credential("REDDIT_CLIENT_ID", channel_slug),
            cm.get_credential("REDDIT_CLIENT_SECRET", channel_slug),
            cm.get_credential("REDDIT_USERNAME", channel_slug),
            cm.get_credential("REDDIT_PASSWORD", channel_slug),
        )

    def get_default_subreddit(self, channel_slug: Optional[str] = None) -> str:
        """Resolves the default subreddit from channel.json, then channel/global env."""
        try:
            from src.core.channel_manager import ChannelManager

            cm = ChannelManager()
            channel = cm.get_channel(channel_slug) if channel_slug else cm.get_active_channel()
            social = (channel or {}).get("social", {}) or {}
            configured = (social.get("reddit") or {}).get("default_subreddit")
            if configured and str(configured).strip():
                return str(configured).strip()
            return cm.get_credential("REDDIT_DEFAULT_SUBREDDIT", channel_slug)
        except Exception:
            return ""

    def is_configured(self, channel_slug: Optional[str] = None) -> bool:
        cid, csec, uname, pwd = self.get_credentials(channel_slug)
        return bool(cid and csec and uname and pwd)

    def _get_access_token(self, channel_slug: Optional[str] = None) -> Optional[str]:
        cid, csec, uname, pwd = self.get_credentials(channel_slug)
        if not (cid and csec and uname and pwd):
            return None
        from src import __version__
        auth = requests.auth.HTTPBasicAuth(cid, csec)
        headers = {"User-Agent": f"OmniPress/{__version__} by /u/{uname}"}
        data = {
            "grant_type": "password",
            "username": uname,
            "password": pwd,
        }

        try:
            res = requests.post(self.TOKEN_URL, auth=auth, data=data, headers=headers, timeout=15)
            if res.status_code == 200:
                return res.json().get("access_token")
            return None
        except requests.RequestException:
            return None

    def queue_social_post(
        self,
        text: str,
        platforms: List[str],
        media_urls: Optional[List[str]] = None,
        schedule_time: Optional[str] = None,
        title: Optional[str] = None,
        channel_slug: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Submits text post to Reddit.
        """
        if not self.is_configured(channel_slug):
            return {
                "success": False,
                "provider": "reddit",
                "error": "Reddit credentials (REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USERNAME, REDDIT_PASSWORD) not configured in .env",
            }

        # Determine target subreddit
        target_sub = self.get_default_subreddit(channel_slug)
        for p in platforms:
            if p.lower().startswith("reddit:"):
                target_sub = p.split(":", 1)[1].strip()
                break

        if not target_sub:
            return {
                "success": False,
                "provider": "reddit",
                "error": "No target subreddit configured. Set social.reddit.default_subreddit in channel.json, "
                "REDDIT_DEFAULT_SUBREDDIT in channels/<slug>/.env, or pass 'reddit:<subreddit>' as a platform.",
            }

        # Extract title if not explicitly provided
        post_title = title
        post_body = text
        if not post_title:
            lines = text.strip().split("\n")
            post_title = lines[0].lstrip("#* \t").strip()
            if len(post_title) > 250:
                post_title = post_title[:247] + "..."
            post_body = "\n".join(lines[1:]).strip() or text

        token = self._get_access_token(channel_slug)
        if not token:
            return {
                "success": False,
                "provider": "reddit",
                "error": "Failed to authenticate with Reddit API. Check username/password and client credentials.",
            }

        cid, csec, uname, pwd = self.get_credentials(channel_slug)
        from src import __version__
        headers = {
            "Authorization": f"Bearer {token}",
            "User-Agent": f"OmniPress/{__version__} by /u/{uname}",
        }
        payload = {
            "api_type": "json",
            "kind": "self",
            "sr": target_sub,
            "title": post_title,
            "text": post_body,
        }

        try:
            res = requests.post(self.SUBMIT_URL, headers=headers, data=payload, timeout=20)
            data = res.json()
            errors = data.get("json", {}).get("errors", [])
            if errors:
                return {
                    "success": False,
                    "provider": "reddit",
                    "error": f"Reddit API errors: {errors}",
                }

            post_url = data.get("json", {}).get("data", {}).get("url") or f"https://reddit.com/r/{target_sub}"
            return {
                "success": True,
                "provider": "reddit",
                "subreddit": target_sub,
                "url": post_url,
            }
        except requests.RequestException as e:
            return {
                "success": False,
                "provider": "reddit",
                "error": f"Network exception calling Reddit: {str(e)}",
            }
