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
        elif target_provider in ("instagram", "instagram_graph", "meta", "facebook", "threads"):
            from src.adapters.meta_adapter import MetaPublisherAdapter
            adapter = MetaPublisherAdapter()
            provider_name = "meta_graph"
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

        # 4. Mandatory Post-Publication Health Check Gate (Rule 09 Gate 6)
        if res.get("success") and hasattr(adapter, "get_post_status"):
            posts = res.get("posts") or []
            verification_results = []
            all_verified = True
            for post_item in posts:
                p_id = post_item.get("post_id") or post_item.get("id")
                if p_id:
                    status_info = adapter.get_post_status(p_id, channel_slug=channel_slug)
                    if status_info.get("success"):
                        post_item["verified_status"] = status_info.get("status")
                        post_item["verified_dueAt"] = status_info.get("dueAt")
                        verification_results.append({
                            "id": p_id,
                            "service": post_item.get("service"),
                            "status": status_info.get("status"),
                            "dueAt": status_info.get("dueAt"),
                            "verified": True,
                        })
                    else:
                        all_verified = False
                        post_item["verification_error"] = status_info.get("error")
                        verification_results.append({
                            "id": p_id,
                            "service": post_item.get("service"),
                            "error": status_info.get("error"),
                            "verified": False,
                        })
            res["health_check"] = {
                "verified": all_verified,
                "results": verification_results,
            }

        # 5. Record to ledger on success
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

    def verify_post_execution(
        self,
        post_slug: str,
        channel_slug: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Rule 09 Gate 6: Audits and verifies the live execution status of scheduled posts.
        Inspects scheduling_log.json, queries Buffer/social API, and reports whether posts
        are pending, successfully sent, or encountered delivery errors.
        """
        from datetime import datetime, timezone
        from src.adapters.buffer_adapter import BufferPublisherAdapter

        eff_channel = channel_slug or self.channel_manager.get_active_channel().get("slug", "default")
        post_dir = PROJECT_ROOT / "channels" / eff_channel / "posts" / post_slug

        candidates = [
            post_dir / "posts" / "scheduling_log.json",
            post_dir / "scheduling_log.json",
        ]
        log_file = None
        for cand in candidates:
            if cand.exists():
                log_file = cand
                break

        if not log_file:
            return {
                "success": False,
                "error": f"scheduling_log.json not found for post '{post_slug}' in channel '{eff_channel}'.",
                "post_slug": post_slug,
                "channel_slug": eff_channel,
            }

        try:
            with open(log_file, "r", encoding="utf-8") as fp:
                log_data = json.load(fp)
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to parse scheduling_log.json: {e}",
            }

        posts = log_data.get("posts", [])
        if not posts:
            return {
                "success": False,
                "error": "No posts found in scheduling_log.json.",
            }

        adapter = BufferPublisherAdapter()
        now_utc = datetime.now(timezone.utc)
        results = []
        counts = {"sent": 0, "scheduled": 0, "error": 0, "unknown": 0}

        for p in posts:
            pid = p.get("post_id") or p.get("id")
            platform = p.get("platform") or p.get("service") or "unknown"
            due_at_str = p.get("due_at_utc") or p.get("dueAt")

            if not pid:
                continue

            status_res = adapter.get_post_status(pid, channel_slug=eff_channel)
            live_status = status_res.get("status", "unknown")
            is_error = not status_res.get("success") or live_status == "error"

            due_dt = None
            if due_at_str:
                try:
                    clean_due = due_at_str.replace("Z", "+00:00")
                    due_dt = datetime.fromisoformat(clean_due)
                except Exception:
                    pass

            expected_tweets = p.get("tweet_count")
            actual_threads = status_res.get("thread_count")
            thread_mismatch = None
            if expected_tweets and actual_threads is not None and actual_threads < expected_tweets:
                thread_mismatch = f"Thread incomplete: expected {expected_tweets} tweets, but Buffer sent {actual_threads} tweets."

            if live_status == "sent":
                if thread_mismatch:
                    execution_state = "PARTIAL_TRUNCATED"
                    counts["error"] += 1
                else:
                    execution_state = "SUCCESS_SENT"
                    counts["sent"] += 1
            elif is_error:
                execution_state = "FAILED_ERROR"
                counts["error"] += 1
            elif live_status == "scheduled":
                if due_dt and now_utc > due_dt:
                    execution_state = "IN_TRANSIT"
                    counts["scheduled"] += 1
                else:
                    execution_state = "PENDING_SCHEDULED"
                    counts["scheduled"] += 1
            else:
                execution_state = "UNKNOWN"
                counts["unknown"] += 1

            p["current_status"] = live_status
            p["execution_state"] = execution_state
            p["last_verified_at"] = now_utc.isoformat()
            if status_res.get("sentAt"):
                p["sent_at"] = status_res.get("sentAt")
            if status_res.get("externalLink"):
                p["external_link"] = status_res.get("externalLink")
            if status_res.get("thread_count") is not None:
                p["actual_thread_count"] = status_res.get("thread_count")
            if thread_mismatch:
                p["integrity_warning"] = thread_mismatch
            if status_res.get("error_message") or status_res.get("error"):
                p["live_error"] = status_res.get("error_message") or status_res.get("error")

            results.append({
                "post_id": pid,
                "platform": platform,
                "status": live_status,
                "execution_state": execution_state,
                "due_at": due_at_str,
                "sent_at": status_res.get("sentAt"),
                "external_link": status_res.get("externalLink"),
                "thread_count": actual_threads,
                "expected_thread_count": expected_tweets,
                "warning": thread_mismatch,
                "verified": status_res.get("success", False) and not thread_mismatch,
            })

        log_data["last_audit_at"] = now_utc.isoformat()
        log_data["audit_summary"] = counts

        try:
            with open(log_file, "w", encoding="utf-8") as fp:
                json.dump(log_data, fp, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.warning("Could not write back to %s: %s", log_file, e)

        all_ok = counts["error"] == 0
        return {
            "success": all_ok,
            "post_slug": post_slug,
            "channel_slug": eff_channel,
            "log_file": str(log_file),
            "summary": counts,
            "results": results,
        }
