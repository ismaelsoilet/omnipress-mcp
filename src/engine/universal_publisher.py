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
from src.core.schema_validator import validate as validate_schema
from src.utils.sanitizer import resolve_profiles, sanitize_text

logger = logging.getLogger("omnipress.universal_publisher")
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

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
        """Loads, parses and schema-validates a publishing recipe JSON or dict."""
        if isinstance(recipe_input, dict):
            validate_schema("post_recipe", recipe_input, source="<dict>")
            return recipe_input

        path = Path(recipe_input).resolve()
        if not path.exists():
            raise FileNotFoundError(f"Publish recipe not found: {path}")

        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in publish recipe: {e}")

        validate_schema("post_recipe", data, source=str(path))
        return data

    def validate_content(
        self,
        text: str,
        platforms: List[str],
        channel_slug: Optional[str] = None,
    ) -> Tuple[str, List[str]]:
        """Sanitizes text and validates platform character limits."""
        cleaned_text, _ = sanitize_text(text, resolve_profiles(channel_slug))
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
        provider: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Dispatches social post to configured adapter with pre-flight checks."""
        from src.adapters.buffer_adapter import BufferPublisherAdapter

        target_platforms = platforms or ["instagram"]
        effective_mode = mode or ("customScheduled" if schedule_time else "shareNow")

        # Handle thread length validation if thread is provided for X/Twitter
        thread = kwargs.get("thread") or kwargs.get("thread_items")
        if thread and any(p.lower() in ("x", "twitter") for p in target_platforms):
            for idx_t, t_item in enumerate(thread, 1):
                t_str = t_item if isinstance(t_item, str) else t_item.get("text", "")
                if len(t_str) > 280:
                    return {
                        "success": False,
                        "error": f"Tweet {idx_t} length ({len(t_str)} chars) exceeds X limit (280 chars).",
                        "channel_slug": channel_slug,
                    }
            if not text and thread:
                text = thread[0] if isinstance(thread[0], str) else thread[0].get("text", "")

        # 1. Sanitize and validate length
        cleaned_text, validation_errors = self.validate_content(text, target_platforms, channel_slug)
        if validation_errors:
            # If thread is present on X, the main text is just tweet 1
            if not (thread and any(p.lower() in ("x", "twitter") for p in target_platforms)):
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
                "thread_count": len(thread) if thread else 0,
            }

        # 3. Resolve and dispatch to publisher adapter
        target_provider = (provider or kwargs.get("publisher") or "buffer").lower().strip()
        provider_name = target_provider
        if target_provider == "buffer":
            adapter = BufferPublisherAdapter()
        elif target_provider in ("instagram", "instagram_graph", "meta"):
            from src.adapters.instagram_adapter import InstagramGraphAdapter
            adapter = InstagramGraphAdapter()
            provider_name = "instagram_graph"
        elif target_provider == "reddit":
            from src.adapters.reddit_adapter import RedditPublisherAdapter
            adapter = RedditPublisherAdapter()
            provider_name = "reddit"
        elif target_provider == "webhook":
            from src.adapters.webhook_adapter import WebhookPublisherAdapter
            adapter = WebhookPublisherAdapter()
            provider_name = "webhook"
        elif target_provider in ("markdown", "archive"):
            from src.adapters.markdown_adapter import MarkdownArchiveAdapter
            adapter = MarkdownArchiveAdapter()
            provider_name = "markdown_archive"
        else:
            adapter = BufferPublisherAdapter()
            provider_name = "buffer"

        if not adapter.is_configured(channel_slug=channel_slug):
            return {
                "success": False,
                "error": f"{adapter.__class__.__name__} is not configured for channel '{channel_slug}' or in .env.",
                "channel_slug": channel_slug,
            }

        passed_kwargs = dict(kwargs)
        passed_kwargs.pop("thread", None)
        passed_kwargs.pop("publisher", None)

        res = adapter.queue_social_post(
            text=cleaned_text,
            platforms=target_platforms,
            media_urls=media_urls or [],
            schedule_time=schedule_time,
            channel_slug=channel_slug,
            mode=effective_mode,
            thread=thread,
            force_duplicate=force_duplicate,
            **passed_kwargs,
        )

        # 4. Record to ledger on success
        if res.get("success"):
            PublishingShield.record_published(
                channel_id=channel_slug,
                text=cleaned_text,
                media_urls=media_urls,
                provider=provider_name,
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

        thread = recipe.get("thread") or recipe.get("thread_items")
        if not text and thread and isinstance(thread, list) and len(thread) > 0:
            text = thread[0] if isinstance(thread[0], str) else thread[0].get("text", "")

        if not text:
            return {"success": False, "error": "Recipe contains no 'text', 'caption', or 'thread'."}

        platforms = recipe.get("platforms")
        if not platforms and "publish" in recipe:
            platforms = recipe.get("publish", {}).get("platforms")

        media_urls = recipe.get("media_urls") or recipe.get("media")
        if not media_urls and "cdn_urls" in recipe:
            media_urls = recipe.get("cdn_urls")

        schedule_time = recipe.get("schedule_time") or recipe.get("publish", {}).get("schedule_time")
        mode = recipe.get("mode") or recipe.get("publish", {}).get("mode")
        provider = recipe.get("provider") or recipe.get("publisher") or recipe.get("publish", {}).get("provider")

        document_url = recipe.get("document_url") or recipe.get("publish", {}).get("document_url")
        document_title = recipe.get("document_title") or recipe.get("publish", {}).get("document_title")
        document_thumbnail_url = recipe.get("document_thumbnail_url") or recipe.get("publish", {}).get("document_thumbnail_url")
        document_path = recipe.get("document_path") or recipe.get("publish", {}).get("document_path")

        if document_path and not document_url:
            from src.utils.storage import get_default_storage_provider, CatboxStorageProvider
            doc_file = Path(document_path)
            if not doc_file.is_absolute():
                doc_file = PROJECT_ROOT / doc_file
            if doc_file.exists():
                storage = get_default_storage_provider(channel_slug)
                if isinstance(storage, CatboxStorageProvider):
                    logger.warning(
                        "Catbox storage provider is active. Buffer's document crawler may reject "
                        "Catbox URLs due to Content-Length headers. For automated LinkedIn PDF carousels, "
                        "configure S3_BUCKET_NAME/R2_BUCKET_NAME or OMNIPRESS_PUBLIC_URL."
                    )
                try:
                    document_url = storage.upload_file(doc_file)
                except Exception as e:
                    logger.warning("Failed to auto-upload document_path '%s': %s", document_path, e)

        return self.publish_social_post(
            channel_slug=channel_slug,
            text=text,
            platforms=platforms,
            media_urls=media_urls,
            schedule_time=schedule_time,
            mode=mode,
            force_duplicate=force_duplicate,
            dry_run=dry_run,
            thread=thread,
            provider=provider,
            document_url=document_url,
            document_title=document_title,
            document_thumbnail_url=document_thumbnail_url,
            document_path=document_path,
        )
