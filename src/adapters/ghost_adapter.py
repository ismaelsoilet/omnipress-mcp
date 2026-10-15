"""Ghost CMS Admin API v5.0 publisher adapter for independent publications and newsletters."""

import os
import time
import json
import hmac
import hashlib
import base64
import re
from typing import List, Dict, Any, Optional
import requests

from src.adapters.base import BasePublisherAdapter
from src.core.publishing_shield import PublishingShield


class GhostPublisherAdapter(BasePublisherAdapter):
    """
    Publishes long-form articles to Ghost CMS via the official Admin API v5.0.
    Generates short-lived HS256 JWT tokens dynamically from the Admin API Key.
    Supports draft and published states, tag taxonomies, and canonical URLs.
    Protected by PublishingShield anti-duplicate ledger (Rule 09).
    """

    def __init__(
        self,
        admin_api_key: Optional[str] = None,
        api_url: Optional[str] = None,
    ):
        self.admin_api_key = (admin_api_key or os.getenv("GHOST_ADMIN_API_KEY", "")).strip()
        self.api_url = (api_url or os.getenv("GHOST_API_URL", "")).strip().rstrip("/")

    def is_configured(self) -> bool:
        """Returns True if GHOST_ADMIN_API_KEY (with valid id:secret format) and GHOST_API_URL are set."""
        if not self.admin_api_key or not self.api_url:
            return False
        parts = self.admin_api_key.split(":")
        return len(parts) == 2 and len(parts[0]) > 0 and len(parts[1]) > 0

    def _generate_jwt_token(self) -> str:
        """
        Generates a 5-minute Ghost Admin API JWT token signed with HMAC-SHA256.
        The secret part of the Admin API key is hex-encoded.
        """
        parts = self.admin_api_key.split(":")
        if len(parts) != 2:
            raise ValueError("GHOST_ADMIN_API_KEY must be in '{id}:{secret}' format.")

        key_id, secret_hex = parts[0], parts[1]
        try:
            secret_bytes = bytes.fromhex(secret_hex)
        except ValueError as e:
            raise ValueError(f"Ghost Admin API secret is not valid hexadecimal: {e}")

        now = int(time.time())
        header = {"alg": "HS256", "typ": "JWT", "kid": key_id}
        payload = {
            "iat": now,
            "exp": now + 300,
            "aud": "/admin/",
        }

        def _b64url(data: bytes) -> str:
            return base64.urlsafe_b64encode(data).rstrip(b"=").decode("utf-8")

        encoded_header = _b64url(json.dumps(header, separators=(",", ":")).encode("utf-8"))
        encoded_payload = _b64url(json.dumps(payload, separators=(",", ":")).encode("utf-8"))

        signing_input = f"{encoded_header}.{encoded_payload}".encode("utf-8")
        signature = hmac.new(secret_bytes, signing_input, hashlib.sha256).digest()
        encoded_signature = _b64url(signature)

        return f"{encoded_header}.{encoded_payload}.{encoded_signature}"

    @staticmethod
    def _markdown_to_html(markdown_text: str) -> str:
        """
        Lightweight native markdown to HTML converter for Ghost's source=html endpoint.
        Converts headings, paragraphs, blockquotes, lists, and code fences.
        """
        lines = markdown_text.strip().split("\n")
        html_lines = []
        in_code_block = False
        in_list = False

        for line in lines:
            line_str = line.rstrip()

            # Code fence
            if line_str.startswith("```"):
                if not in_code_block:
                    in_code_block = True
                    html_lines.append("<pre><code>")
                else:
                    in_code_block = False
                    html_lines.append("</code></pre>")
                continue

            if in_code_block:
                escaped = (
                    line_str.replace("&", "&amp;")
                    .replace("<", "&lt;")
                    .replace(">", "&gt;")
                )
                html_lines.append(escaped)
                continue

            # Headings
            if line_str.startswith("### "):
                html_lines.append(f"<h3>{line_str[4:].strip()}</h3>")
            elif line_str.startswith("## "):
                html_lines.append(f"<h2>{line_str[3:].strip()}</h2>")
            elif line_str.startswith("# "):
                html_lines.append(f"<h1>{line_str[2:].strip()}</h1>")
            elif line_str.startswith("> "):
                html_lines.append(f"<blockquote><p>{line_str[2:].strip()}</p></blockquote>")
            elif line_str.startswith("- ") or line_str.startswith("* "):
                if not in_list:
                    in_list = True
                    html_lines.append("<ul>")
                html_lines.append(f"<li>{line_str[2:].strip()}</li>")
            else:
                if in_list:
                    html_lines.append("</ul>")
                    in_list = False
                if line_str:
                    # Bold & Italic
                    p_text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", line_str)
                    p_text = re.sub(r"\*(.+?)\*", r"<em>\1</em>", p_text)
                    html_lines.append(f"<p>{p_text}</p>")

        if in_list:
            html_lines.append("</ul>")
        if in_code_block:
            html_lines.append("</code></pre>")

        return "\n".join(html_lines)

    def publish_article(
        self,
        title: str,
        content_markdown: str,
        category: str = "technology",
        tags: Optional[List[str]] = None,
        author: Optional[str] = None,
        canonical_url: Optional[str] = None,
        published: bool = False,
        force_duplicate: bool = False,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Submits an article to Ghost CMS Admin API.
        If published=False, creates a draft post for review.
        """
        if not self.is_configured():
            return {
                "success": False,
                "error": "GHOST_ADMIN_API_KEY (with valid id:secret) and GHOST_API_URL must be configured.",
                "configured": False,
            }

        # Pre-flight Gate: PublishingShield anti-duplicate ledger check
        shield_text = f"{title.strip()}\n{content_markdown.strip()}"
        is_dup, err = PublishingShield.check_duplicate(
            channel_id="ghost",
            text=shield_text,
            media_urls=None,
        )
        if is_dup and not force_duplicate:
            return {
                "success": False,
                "error": f"PublishingShield blocked post: {err}",
                "blocked_by_shield": True,
            }

        try:
            token = self._generate_jwt_token()
        except ValueError as e:
            return {"success": False, "error": f"Failed to generate Ghost JWT: {str(e)}"}

        html_content = self._markdown_to_html(content_markdown)
        tag_list = tags or [category]
        ghost_tags = [{"name": t.strip()} for t in tag_list if t.strip()]

        post_data: Dict[str, Any] = {
            "title": title.strip(),
            "html": html_content,
            "status": "published" if published else "draft",
            "tags": ghost_tags,
        }
        if canonical_url:
            post_data["canonical_url"] = canonical_url.strip()

        endpoint = f"{self.api_url}/ghost/api/admin/posts/?source=html"
        headers = {
            "Authorization": f"Ghost {token}",
            "Content-Type": "application/json",
            "Accept-Version": "v5.0",
            "User-Agent": "OmniPress-MCP/0.1.0",
        }

        try:
            res = requests.post(
                endpoint,
                json={"posts": [post_data]},
                headers=headers,
                timeout=15,
            )

            if res.status_code == 201:
                data = res.json()
                created_post = data.get("posts", [{}])[0]
                post_id = str(created_post.get("id"))
                post_url = created_post.get("url")

                # Record in PublishingShield
                PublishingShield.record_published(
                    channel_id="ghost",
                    text=shield_text,
                    media_urls=None,
                    post_id=post_id,
                    provider="ghost_api",
                )

                return {
                    "success": True,
                    "id": post_id,
                    "url": post_url,
                    "title": created_post.get("title", title),
                    "status": created_post.get("status", "draft"),
                    "provider": "ghost",
                }

            if res.status_code in (401, 403):
                return {
                    "success": False,
                    "error": f"Ghost CMS authentication rejected ({res.status_code}). Check GHOST_ADMIN_API_KEY.",
                    "status_code": res.status_code,
                }

            if res.status_code == 422:
                return {
                    "success": False,
                    "error": f"Ghost post validation error (422): {res.text}",
                    "status_code": 422,
                }

            return {
                "success": False,
                "error": f"Ghost API returned status {res.status_code}: {res.text}",
                "status_code": res.status_code,
            }

        except requests.RequestException as e:
            return {"success": False, "error": f"Network error connecting to Ghost API: {str(e)}"}

    def queue_social_post(
        self,
        text: str,
        platforms: List[str],
        media_urls: Optional[List[str]] = None,
        schedule_time: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Ghost does not support micro-posts, only full articles/newsletters."""
        return {
            "success": False,
            "error": "GhostPublisherAdapter only supports long-form articles via publish_article().",
        }
