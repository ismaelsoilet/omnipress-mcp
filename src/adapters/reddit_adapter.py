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
        self.client_id = os.getenv("REDDIT_CLIENT_ID", "").strip()
        self.client_secret = os.getenv("REDDIT_CLIENT_SECRET", "").strip()
        self.username = os.getenv("REDDIT_USERNAME", "").strip()
        self.password = os.getenv("REDDIT_PASSWORD", "").strip()
        self.default_subreddit = os.getenv("REDDIT_DEFAULT_SUBREDDIT", "SideProject").strip()

    def is_configured(self) -> bool:
        return bool(self.client_id and self.client_secret and self.username and self.password)

    def _get_access_token(self) -> Optional[str]:
        auth = requests.auth.HTTPBasicAuth(self.client_id, self.client_secret)
        headers = {"User-Agent": f"OmniPress/0.1.0 by /u/{self.username}"}
        data = {
            "grant_type": "password",
            "username": self.username,
            "password": self.password,
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
    ) -> Dict[str, Any]:
        """
        Submits text post to Reddit.
        """
        if not self.is_configured():
            return {
                "success": False,
                "provider": "reddit",
                "error": "Reddit credentials (REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USERNAME, REDDIT_PASSWORD) not configured in .env",
            }

        # Determine target subreddit
        target_sub = self.default_subreddit
        for p in platforms:
            if p.lower().startswith("reddit:"):
                target_sub = p.split(":", 1)[1].strip()
                break

        # Extract title if not explicitly provided
        post_title = title
        post_body = text
        if not post_title:
            lines = text.strip().split("\n")
            post_title = lines[0].lstrip("#* \t").strip()
            if len(post_title) > 250:
                post_title = post_title[:247] + "..."
            post_body = "\n".join(lines[1:]).strip() or text

        token = self._get_access_token()
        if not token:
            return {
                "success": False,
                "provider": "reddit",
                "error": "Failed to authenticate with Reddit API. Check username/password and client credentials.",
            }

        headers = {
            "Authorization": f"Bearer {token}",
            "User-Agent": f"OmniPress/0.1.0 by /u/{self.username}",
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
