"""Universal Social Publishing & Syndication Engine for OmniPress MCP.

Provides a unified, instruction-driven interface for publishing social posts,
threads, and long-form articles across channels with built-in legal sanitization,
character limits, anti-duplicate ledger protection (Rule 09), and multi-platform routing.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from src.core.channel_manager import ChannelManager
from src.core.publishing_shield import PublishingShield
from src.utils.sanitizer import sanitize_text

logger = logging.getLogger("omnipress.universal_publisher")

PLATFORM_LIMITS = {
    "instagram": 2196,
    "x": 280,
    "twitter": 280,
    "linkedin": 3000,
    "threads": 500,
}


class UniversalPublisherEngine:
    """Universal social publishing and syndication orchestrator."""

    def __init__(self, channel_manager: Optional[ChannelManager] = None):
        self.channel_manager = channel_manager or ChannelManager()

    def load_recipe(self, recipe_input: Union[str, Path, Dict[str, Any]]) -> Dict[str, Any]:
        """Loads and parses a publishing recipe JSON or dict."""
        if isinstance(recipe_input, dict):
            return recipe_input

        path = Path(recipe_input).resolve()
        if not path.exists():
            raise FileNotFoundError(f"Publish recipe not found: {path}")

        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in publish recipe: {e}")

    def validate_content(
        self,
        text: str,
        platforms: List[str],
    ) -> Tuple[str, List[str]]:
        """Sanitizes text and validates platform character limits."""
        cleaned_text, _ = sanitize_text(text)
        errors = []

        for p in platforms:
            p_lower = p.lower()
            limit = PLATFORM_LIMITS.get(p_lower)
            if limit and len(cleaned_text) > limit:
                errors.append(
                    f"Content length ({len(cleaned_text)} chars) exceeds {p} limit ({limit} chars)."
                )

        return cleaned_text, errors

    def publish_social_post(
        self,
        channel_slug: str,
        text: str,
        platforms: Optional[List[str]] = None,
        media_urls: Optional[List[str]] = None,
        schedule_time: Optional[str] = None,
        mode: Optional[str] = None,
        force_duplicate: bool = False,
        dry_run: bool = False,
    ) -> Dict[str, Any]:
        """Dispatches social post to configured adapter with pre-flight checks."""
        from src.adapters.buffer_adapter import BufferPublisherAdapter

        target_platforms = platforms or ["instagram"]
        effective_mode = mode or ("customScheduled" if schedule_time else "shareNow")

        # 1. Sanitize and validate length
        cleaned_text, validation_errors = self.validate_content(text, target_platforms)
        if validation_errors:
            return {
                "success": False,
                "error": "; ".join(validation_errors),
                "channel_slug": channel_slug,
            }

        # 2. Check duplicate via PublishingShield (Rule 09)
        is_dup, reason = PublishingShield.check_duplicate(
            channel_id=channel_slug,
            text=cleaned_text,
            media_urls=media_urls,
            force=force_duplicate,
        )

        if is_dup and not force_duplicate:
            logger.warning("PublishingShield blocked duplicate post: %s", reason)
            return {
                "success": False,
                "error": f"PublishingShield duplicate protection: {reason}",
                "channel_slug": channel_slug,
            }

        if dry_run:
            return {
                "success": True,
                "dry_run": True,
                "channel_slug": channel_slug,
                "platforms": target_platforms,
                "mode": effective_mode,
                "schedule_time": schedule_time,
                "media_count": len(media_urls or []),
                "sanitized_text_preview": cleaned_text[:120],
            }

        # 3. Dispatch to publisher adapter
        adapter = BufferPublisherAdapter()
        if not adapter.is_configured(channel_slug=channel_slug):
            return {
                "success": False,
                "error": f"Buffer publisher adapter is not configured for channel '{channel_slug}' or in .env.",
                "channel_slug": channel_slug,
            }

        res = adapter.queue_social_post(
            text=cleaned_text,
            platforms=target_platforms,
            media_urls=media_urls or [],
            schedule_time=schedule_time,
            channel_slug=channel_slug,
            mode=effective_mode,
        )

        # 4. Record to ledger on success
        if res.get("success"):
            PublishingShield.record_published(
                channel_id=channel_slug,
                text=cleaned_text,
                media_urls=media_urls,
                provider="buffer",
                status="queued" if schedule_time else "published",
                response=res,
            )

        return res

    def execute_recipe(
        self,
        recipe_input: Union[str, Path, Dict[str, Any]],
        force_duplicate: bool = False,
        dry_run: bool = False,
    ) -> Dict[str, Any]:
        """Executes a declarative post or article recipe."""
        recipe = self.load_recipe(recipe_input)

        channel_slug = recipe.get("channel_slug") or self.channel_manager.get_active_channel().get("slug", "default")
        text = recipe.get("text") or recipe.get("caption") or ""
        if not text and "slides" in recipe:
            # Fallback to publish block inside carousel recipe
            publish_block = recipe.get("publish", {})
            text = publish_block.get("caption", "")

        if not text:
            return {"success": False, "error": "Recipe contains no 'text' or 'caption'."}

        platforms = recipe.get("platforms")
        if not platforms and "publish" in recipe:
            platforms = recipe.get("publish", {}).get("platforms")

        media_urls = recipe.get("media_urls") or recipe.get("media")
        if not media_urls and "cdn_urls" in recipe:
            media_urls = recipe.get("cdn_urls")

        schedule_time = recipe.get("schedule_time") or recipe.get("publish", {}).get("schedule_time")
        mode = recipe.get("mode") or recipe.get("publish", {}).get("mode")

        return self.publish_social_post(
            channel_slug=channel_slug,
            text=text,
            platforms=platforms,
            media_urls=media_urls,
            schedule_time=schedule_time,
            mode=mode,
            force_duplicate=force_duplicate,
            dry_run=dry_run,
        )
