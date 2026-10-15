"""Dev.to API publisher adapter for technical articles and developer thought leadership."""

import os
import re
from typing import List, Dict, Any, Optional
import requests

from src.adapters.base import BasePublisherAdapter
from src.core.publishing_shield import PublishingShield


class DevToPublisherAdapter(BasePublisherAdapter):
    """
    Publishes long-form technical articles to Dev.to via the official REST API v0.
    Supports draft and published states, tag sanitization, and canonical URLs.
    Protected by PublishingShield anti-duplicate ledger (Rule 09).
    """

    DEFAULT_API_URL = "https://dev.to/api/articles"

    def __init__(self, api_key: Optional[str] = None, api_url: Optional[str] = None):
        self.api_key = (api_key or os.getenv("DEVTO_API_KEY", "")).strip()
        self.api_url = (api_url or os.getenv("DEVTO_API_URL", self.DEFAULT_API_URL)).strip()

    def is_configured(self) -> bool:
        """Returns True if DEVTO_API_KEY is configured."""
        return bool(self.api_key)

    @staticmethod
    def _sanitize_tags(tags: Optional[List[str]]) -> List[str]:
        """
        Sanitizes tags for Dev.to: max 4 tags, lowercase alphanumeric + underscore, no spaces.
        """
        if not tags:
            return []
        cleaned = []
        for t in tags:
            clean_tag = re.sub(r"[^a-zA-Z0-9_]", "", str(t).lower().strip())
            if clean_tag and clean_tag not in cleaned:
                cleaned.append(clean_tag)
            if len(cleaned) == 4:
                break
        return cleaned

    def publish_article(
        self,
        title: str,
        content_markdown: str,
        category: str = "technology",
        tags: Optional[List[str]] = None,
        author: Optional[str] = None,
        canonical_url: Optional[str] = None,
        series: Optional[str] = None,
        published: bool = False,
        force_duplicate: bool = False,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Submits an article to Dev.to.
        If published=False, creates a draft in the user's Dev.to dashboard.
        """
        if not self.is_configured():
            return {
                "success": False,
                "error": "DEVTO_API_KEY is not configured.",
                "configured": False,
            }

        # Pre-flight Gate: PublishingShield anti-duplicate ledger check
        shield_text = f"{title.strip()}\n{content_markdown.strip()}"
        is_dup, err = PublishingShield.check_duplicate(
            channel_id="devto",
            text=shield_text,
            media_urls=None,
        )
        if is_dup and not force_duplicate:
            return {
                "success": False,
                "error": f"PublishingShield blocked post: {err}",
                "blocked_by_shield": True,
            }

        clean_tags = self._sanitize_tags(tags or [category])

        article_payload: Dict[str, Any] = {
            "title": title.strip(),
            "body_markdown": content_markdown.strip(),
            "published": published,
            "tags": clean_tags,
        }
        if canonical_url:
            article_payload["canonical_url"] = canonical_url.strip()
        if series:
            article_payload["series"] = series.strip()

        headers = {
            "api-key": self.api_key,
            "Content-Type": "application/json",
            "User-Agent": "OmniPress-MCP/0.1.0 (https://github.com/ismaelsoilet/omnipress-mcp)",
        }

        try:
            res = requests.post(
                self.api_url,
                json={"article": article_payload},
                headers=headers,
                timeout=15,
            )

            if res.status_code == 201:
                data = res.json()
                article_id = str(data.get("id"))
                article_url = data.get("url")
                
                # Record in PublishingShield idempotency ledger
                PublishingShield.record_published(
                    channel_id="devto",
                    text=shield_text,
                    media_urls=None,
                    post_id=article_id,
                    provider="devto_api",
                )

                return {
                    "success": True,
                    "id": article_id,
                    "url": article_url,
                    "title": data.get("title", title),
                    "status": "published" if published else "draft",
                    "provider": "devto",
                }

            if res.status_code == 401:
                return {
                    "success": False,
                    "error": "Dev.to API key invalid or unauthorized (401). Check DEVTO_API_KEY.",
                    "status_code": 401,
                }

            if res.status_code == 422:
                return {
                    "success": False,
                    "error": f"Dev.to article validation error (422): {res.text}",
                    "status_code": 422,
                }

            return {
                "success": False,
                "error": f"Dev.to API returned status {res.status_code}: {res.text}",
                "status_code": res.status_code,
            }

        except requests.RequestException as e:
            return {"success": False, "error": f"Network error connecting to Dev.to API: {str(e)}"}

    def queue_social_post(
        self,
        text: str,
        platforms: List[str],
        media_urls: Optional[List[str]] = None,
        schedule_time: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Dev.to does not support micro-posts, only full articles."""
        return {
            "success": False,
            "error": "DevToPublisherAdapter only supports long-form articles via publish_article().",
        }
