"""Meta Unified Publishing Adapter for OmniPress (Instagram Graph, Facebook Pages, Threads)."""

import os
import time
import requests
from typing import List, Dict, Any, Optional, Tuple
from .base import BasePublisherAdapter


class MetaPublisherAdapter(BasePublisherAdapter):
    """
    Direct multi-platform publishing adapter for the official Meta Graph API ecosystem.
    Supports:
      - Instagram Professional: Single Image, Multi-slide Carousels (up to 10 items),
        Reels / Video with async container polling, Stories, and First-Comment automation.
      - Facebook Pages: Text updates, single/multi photos, and video posts.
      - Threads API: Text posts, single images, and video updates via graph.threads.net.
    """

    GRAPH_API_VERSION = "v19.0"
    BASE_URL = f"https://graph.facebook.com/{GRAPH_API_VERSION}"
    THREADS_BASE_URL = "https://graph.threads.net/v1.0"

    def __init__(self):
        # Credentials are dynamically resolved at call time via ChannelManager (Rule 14).
        pass

    def get_credentials(self, channel_slug: Optional[str] = None) -> Tuple[str, str]:
        """Resolves (instagram_access_token, instagram_account_id) with strict Rule 04 channel precedence."""
        creds = self.get_meta_credentials(channel_slug)
        return creds.get("instagram_token") or "", creds.get("instagram_account_id") or ""

    def get_meta_credentials(self, channel_slug: Optional[str] = None) -> Dict[str, str]:
        """Resolves full Meta credentials hierarchy for Instagram, Facebook, and Threads."""
        from src.core.channel_manager import ChannelManager

        cm = ChannelManager()
        ig_token = cm.get_credential("INSTAGRAM_ACCESS_TOKEN", channel_slug) or ""
        ig_acct = (
            cm.get_credential("INSTAGRAM_ACCOUNT_ID", channel_slug)
            or cm.get_credential("INSTAGRAM_BUSINESS_ACCOUNT_ID", channel_slug)
            or ""
        )

        fb_page_id = (
            cm.get_credential("FACEBOOK_PAGE_ID", channel_slug)
            or cm.get_credential("FB_PAGE_ID", channel_slug)
            or ""
        )
        fb_token = (
            cm.get_credential("FACEBOOK_ACCESS_TOKEN", channel_slug)
            or cm.get_credential("FB_ACCESS_TOKEN", channel_slug)
            or ig_token
        )

        threads_user = cm.get_credential("THREADS_USER_ID", channel_slug) or ""
        threads_token = (
            cm.get_credential("THREADS_ACCESS_TOKEN", channel_slug)
            or ig_token
        )

        return {
            "instagram_token": ig_token,
            "instagram_account_id": ig_acct,
            "facebook_page_id": fb_page_id,
            "facebook_token": fb_token,
            "threads_user_id": threads_user,
            "threads_token": threads_token,
        }

    def is_configured(self, channel_slug: Optional[str] = None, platform: str = "instagram") -> bool:
        """Returns True if required credentials exist for the specified target Meta platform."""
        creds = self.get_meta_credentials(channel_slug)
        target = (platform or "instagram").lower().strip()

        if target in ("instagram", "ig"):
            return bool(creds["instagram_token"] and creds["instagram_account_id"])
        elif target in ("facebook", "fb"):
            return bool(creds["facebook_page_id"] and creds["facebook_token"])
        elif target in ("threads",):
            return bool(creds["threads_user_id"] and creds["threads_token"])
        elif target in ("meta", "all"):
            return bool(
                (creds["instagram_token"] and creds["instagram_account_id"])
                or (creds["facebook_page_id"] and creds["facebook_token"])
                or (creds["threads_user_id"] and creds["threads_token"])
            )
        return bool(creds["instagram_token"] and creds["instagram_account_id"])

    @staticmethod
    def is_video(url: str, media_type: Optional[str] = None) -> bool:
        """Determines if a media asset URL represents a video file."""
        if media_type and media_type.lower() in ("video", "reels", "reel", "short", "shorts"):
            return True
        clean_url = (url or "").split("?")[0].lower()
        return clean_url.endswith((".mp4", ".mov", ".m4v", ".webm", ".avi"))

    def _wait_for_container(
        self,
        container_id: str,
        access_token: str,
        max_wait_seconds: int = 120,
        poll_interval: float = 3.0,
    ) -> Dict[str, Any]:
        """
        Polls Meta Graph API container status until FINISHED, ERROR, or timeout.
        Required for asynchronous video/Reels ingestion.
        """
        status_url = f"{self.BASE_URL}/{container_id}"
        headers = {"Authorization": f"Bearer {access_token}"}
        params = {"fields": "status_code,status"}

        start_time = time.time()
        while time.time() - start_time < max_wait_seconds:
            try:
                res = requests.get(status_url, params=params, headers=headers, timeout=15)
                if res.status_code == 200:
                    data = res.json()
                    code = str(data.get("status_code", "")).upper()
                    if code == "FINISHED":
                        return {"ready": True, "status": "FINISHED"}
                    if code in ("ERROR", "EXPIRED"):
                        err_detail = data.get("status") or code
                        return {"ready": False, "error": f"Meta container failed with status {code}: {err_detail}"}
                time.sleep(poll_interval)
            except requests.RequestException:
                time.sleep(poll_interval)

        return {
            "ready": False,
            "error": f"Timeout after {max_wait_seconds}s waiting for Meta container {container_id} processing.",
        }

    def post_comment(self, post_id: str, comment_text: str, access_token: str) -> Dict[str, Any]:
        """Posts an automated first comment (e.g. hashtags or call-to-action) to a published Instagram post."""
        if not comment_text or not comment_text.strip():
            return {"success": True, "skipped": True}

        comment_url = f"{self.BASE_URL}/{post_id}/comments"
        headers = {"Authorization": f"Bearer {access_token}"}
        payload = {"message": comment_text.strip()}

        try:
            res = requests.post(comment_url, data=payload, headers=headers, timeout=15)
            if res.status_code in (200, 201):
                return {"success": True, "comment_id": res.json().get("id")}
            return {"success": False, "error": f"Failed posting comment: {res.text}"}
        except Exception as exc:
            return {"success": False, "error": f"Exception posting comment: {str(exc)}"}

    def publish_facebook_page(
        self,
        text: str,
        media_urls: Optional[List[str]] = None,
        channel_slug: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Publishes text, photo, or video to a Facebook Page via Meta Graph API."""
        creds = self.get_meta_credentials(channel_slug)
        page_id = creds["facebook_page_id"]
        page_token = creds["facebook_token"]

        if not (page_id and page_token):
            return {
                "success": False,
                "provider": "facebook_graph_api",
                "error": "FACEBOOK_PAGE_ID or FACEBOOK_ACCESS_TOKEN is not configured.",
            }

        headers = {"Authorization": f"Bearer {page_token}"}
        urls = media_urls or []

        try:
            # 1. Video post to Facebook Page
            if urls and self.is_video(urls[0], kwargs.get("media_type")):
                url = f"{self.BASE_URL}/{page_id}/videos"
                payload = {
                    "file_url": urls[0],
                    "description": text,
                    "title": kwargs.get("title") or (text.split("\n")[0][:100] if text else "Video"),
                }
                res = requests.post(url, data=payload, headers=headers, timeout=30)
                if res.status_code in (200, 201):
                    post_id = res.json().get("id")
                    return {
                        "success": True,
                        "provider": "facebook_graph_api",
                        "post_id": post_id,
                        "type": "video",
                        "permalink": f"https://www.facebook.com/{post_id}",
                    }
                return {"success": False, "provider": "facebook_graph_api", "error": f"Facebook video post error: {res.text}"}

            # 2. Photo post to Facebook Page
            elif urls:
                url = f"{self.BASE_URL}/{page_id}/photos"
                payload = {"url": urls[0], "caption": text}
                res = requests.post(url, data=payload, headers=headers, timeout=30)
                if res.status_code in (200, 201):
                    post_id = res.json().get("id")
                    return {
                        "success": True,
                        "provider": "facebook_graph_api",
                        "post_id": post_id,
                        "type": "photo",
                        "permalink": f"https://www.facebook.com/{post_id}",
                    }
                return {"success": False, "provider": "facebook_graph_api", "error": f"Facebook photo post error: {res.text}"}

            # 3. Text / Link post to Facebook Page Feed
            else:
                url = f"{self.BASE_URL}/{page_id}/feed"
                payload = {"message": text}
                if kwargs.get("link"):
                    payload["link"] = kwargs["link"]
                res = requests.post(url, data=payload, headers=headers, timeout=20)
                if res.status_code in (200, 201):
                    post_id = res.json().get("id")
                    return {
                        "success": True,
                        "provider": "facebook_graph_api",
                        "post_id": post_id,
                        "type": "feed",
                        "permalink": f"https://www.facebook.com/{post_id}",
                    }
                return {"success": False, "provider": "facebook_graph_api", "error": f"Facebook feed post error: {res.text}"}

        except requests.RequestException as exc:
            return {
                "success": False,
                "provider": "facebook_graph_api",
                "error": f"Network exception on Facebook Graph API: {str(exc)}",
            }

    def publish_threads(
        self,
        text: str,
        media_urls: Optional[List[str]] = None,
        channel_slug: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Publishes text or media to Threads via the official Meta Threads API."""
        creds = self.get_meta_credentials(channel_slug)
        user_id = creds["threads_user_id"]
        token = creds["threads_token"]

        if not (user_id and token):
            return {
                "success": False,
                "provider": "threads_api",
                "error": "THREADS_USER_ID or THREADS_ACCESS_TOKEN is not configured.",
            }

        headers = {"Authorization": f"Bearer {token}"}
        urls = media_urls or []

        try:
            # 1. Create Threads Media Container
            container_url = f"{self.THREADS_BASE_URL}/{user_id}/threads"
            if urls and self.is_video(urls[0], kwargs.get("media_type")):
                payload = {"media_type": "VIDEO", "video_url": urls[0], "text": text}
            elif urls:
                payload = {"media_type": "IMAGE", "image_url": urls[0], "text": text}
            else:
                payload = {"media_type": "TEXT_POST", "text": text}

            res = requests.post(container_url, data=payload, headers=headers, timeout=20)
            if res.status_code not in (200, 201):
                return {"success": False, "provider": "threads_api", "error": f"Threads container error: {res.text}"}

            container_id = res.json().get("id")

            # 2. If video, poll status briefly
            if urls and self.is_video(urls[0], kwargs.get("media_type")):
                status_url = f"{self.THREADS_BASE_URL}/{container_id}"
                params = {"fields": "status,error_message"}
                for _ in range(20):
                    time.sleep(3)
                    st_res = requests.get(status_url, params=params, headers=headers, timeout=10)
                    if st_res.status_code == 200:
                        st_code = str(st_res.json().get("status", "")).upper()
                        if st_code == "FINISHED":
                            break
                        if st_code == "ERROR":
                            return {"success": False, "provider": "threads_api", "error": f"Threads processing failed: {st_res.text}"}

            # 3. Publish Threads Container
            pub_url = f"{self.THREADS_BASE_URL}/{user_id}/threads_publish"
            pub_res = requests.post(pub_url, data={"creation_id": container_id}, headers=headers, timeout=20)
            if pub_res.status_code in (200, 201):
                post_id = pub_res.json().get("id")
                return {
                    "success": True,
                    "provider": "threads_api",
                    "post_id": post_id,
                    "permalink": f"https://www.threads.net/post/{post_id}",
                }
            return {"success": False, "provider": "threads_api", "error": f"Threads publish error: {pub_res.text}"}

        except requests.RequestException as exc:
            return {
                "success": False,
                "provider": "threads_api",
                "error": f"Network exception on Threads API: {str(exc)}",
            }

    def queue_social_post(
        self,
        text: str,
        platforms: List[str],
        media_urls: Optional[List[str]] = None,
        schedule_time: Optional[str] = None,
        channel_slug: Optional[str] = None,
        mode: Optional[str] = None,
        allow_test: bool = False,
        force_duplicate: bool = False,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Publishes content across Meta platforms (Instagram, Facebook, Threads) via official Graph APIs.
        Protected by PublishingShield pre-flight validation and anti-duplicate ledger (Rule 09).
        """
        normalized_platforms = [p.lower().strip() for p in (platforms or ["instagram"])]
        urls = media_urls or []

        # If exclusively Facebook is requested, route directly to Facebook Page publisher
        if all(p in ("facebook", "fb") for p in normalized_platforms):
            return self.publish_facebook_page(
                text=text,
                media_urls=urls,
                channel_slug=channel_slug,
                **kwargs,
            )

        # If exclusively Threads is requested, route directly to Threads publisher
        if all(p in ("threads",) for p in normalized_platforms):
            return self.publish_threads(
                text=text,
                media_urls=urls,
                channel_slug=channel_slug,
                **kwargs,
            )

        # Default path: Instagram Graph Publishing (with optional cross-posting to Facebook)
        creds = self.get_meta_credentials(channel_slug)
        access_token = creds["instagram_token"]
        account_id = creds["instagram_account_id"]

        if not (access_token and account_id):
            return {
                "success": False,
                "error": "INSTAGRAM_ACCESS_TOKEN or INSTAGRAM_ACCOUNT_ID is not configured in .env",
            }

        resolved_mode = mode or ("customScheduled" if schedule_time else "shareNow")

        # Gate 1, 2, 3: Pre-flight validation (character limits, placeholder text, media required)
        from src.core.publishing_shield import PublishingShield

        is_valid, validation_err = PublishingShield.validate_post(
            text=text,
            platforms=normalized_platforms,
            media_urls=urls,
            mode=resolved_mode,
            allow_test=allow_test,
        )
        if not is_valid:
            return {
                "success": False,
                "provider": "publishing_shield",
                "error": validation_err,
            }

        # Gate 4: Anti-Duplicate Idempotency Check (Rule 09)
        effective_channel_id = account_id or channel_slug or "instagram_default"
        is_dup, dup_err = PublishingShield.check_duplicate(
            channel_id=effective_channel_id,
            text=text,
            media_urls=urls,
            force=force_duplicate,
        )
        if is_dup:
            return {
                "success": False,
                "provider": "publishing_shield",
                "error": dup_err,
            }

        headers = {"Authorization": f"Bearer {access_token}"}
        is_single_media = len(urls) == 1
        is_video_media = is_single_media and self.is_video(urls[0], kwargs.get("media_type"))

        try:
            # Case A: Instagram Reels / Video
            if is_video_media:
                container_url = f"{self.BASE_URL}/{account_id}/media"
                payload = {
                    "video_url": urls[0],
                    "caption": text,
                    "media_type": "REELS",
                    "share_to_feed": "true",
                }
                if kwargs.get("thumb_offset"):
                    payload["thumb_offset"] = str(kwargs["thumb_offset"])

                res = requests.post(container_url, data=payload, headers=headers, timeout=25)
                if res.status_code not in (200, 201):
                    return {
                        "success": False,
                        "provider": "instagram_graph_api",
                        "error": f"Failed creating Instagram Reels container: {res.text}",
                    }

                container_id = res.json().get("id")

                # Asynchronous container polling until FINISHED
                poll_res = self._wait_for_container(container_id, access_token)
                if not poll_res.get("ready"):
                    return {
                        "success": False,
                        "provider": "instagram_graph_api",
                        "error": poll_res.get("error", "Failed waiting for Reels processing"),
                    }

            # Case B: Single Image Post
            elif is_single_media:
                container_url = f"{self.BASE_URL}/{account_id}/media"
                payload = {
                    "image_url": urls[0],
                    "caption": text,
                }
                res = requests.post(container_url, data=payload, headers=headers, timeout=20)
                if res.status_code not in (200, 201):
                    return {
                        "success": False,
                        "provider": "instagram_graph_api",
                        "error": f"Failed creating Instagram media container: {res.text}",
                    }
                container_id = res.json().get("id")

            # Case C: Multi-Slide Carousel Post (Up to 10 slides)
            else:
                children_ids = []
                for item_url in urls[:10]:
                    is_item_vid = self.is_video(item_url)
                    item_payload = {
                        "is_carousel_item": "true",
                    }
                    if is_item_vid:
                        item_payload["video_url"] = item_url
                        item_payload["media_type"] = "VIDEO"
                    else:
                        item_payload["image_url"] = item_url

                    res_item = requests.post(
                        f"{self.BASE_URL}/{account_id}/media",
                        data=item_payload,
                        headers=headers,
                        timeout=20,
                    )
                    if res_item.status_code not in (200, 201):
                        return {
                            "success": False,
                            "provider": "instagram_graph_api",
                            "error": f"Failed creating carousel item {item_url}: {res_item.text}",
                        }
                    children_ids.append(res_item.json().get("id"))

                carousel_payload = {
                    "media_type": "CAROUSEL",
                    "caption": text,
                    "children": ",".join(children_ids),
                }
                res_parent = requests.post(
                    f"{self.BASE_URL}/{account_id}/media",
                    data=carousel_payload,
                    headers=headers,
                    timeout=20,
                )
                if res_parent.status_code not in (200, 201):
                    return {
                        "success": False,
                        "provider": "instagram_graph_api",
                        "error": f"Failed creating parent carousel container: {res_parent.text}",
                    }
                container_id = res_parent.json().get("id")

            # Step 2: Publish the media container
            publish_url = f"{self.BASE_URL}/{account_id}/media_publish"
            pub_res = requests.post(
                publish_url,
                data={"creation_id": container_id},
                headers=headers,
                timeout=20,
            )
            if pub_res.status_code in (200, 201):
                post_id = pub_res.json().get("id")

                # Step 3: Optional First-Comment (Hashtags)
                first_comment = kwargs.get("first_comment") or kwargs.get("comment")
                comment_result = None
                if first_comment:
                    comment_result = self.post_comment(post_id, first_comment, access_token)

                PublishingShield.record_published(
                    channel_id=effective_channel_id,
                    text=text,
                    media_urls=urls,
                    post_id=post_id,
                    provider="instagram_graph_api",
                )

                result_payload = {
                    "success": True,
                    "provider": "instagram_graph_api",
                    "post_id": post_id,
                    "media_count": len(urls),
                    "media_type": "REELS" if is_video_media else ("CAROUSEL" if len(urls) > 1 else "IMAGE"),
                    "permalink": f"https://www.instagram.com/p/{post_id}/" if post_id else None,
                }
                if comment_result:
                    result_payload["first_comment_status"] = comment_result.get("success", False)
                    if comment_result.get("comment_id"):
                        result_payload["comment_id"] = comment_result["comment_id"]

                # Optional Cross-posting to Facebook Page if requested
                if any(p in ("facebook", "fb") for p in normalized_platforms):
                    fb_res = self.publish_facebook_page(
                        text=text,
                        media_urls=urls,
                        channel_slug=channel_slug,
                        **kwargs,
                    )
                    result_payload["facebook_cross_post"] = fb_res

                return result_payload

            return {
                "success": False,
                "provider": "instagram_graph_api",
                "status_code": pub_res.status_code,
                "error": pub_res.text,
            }

        except requests.RequestException as exc:
            return {
                "success": False,
                "provider": "instagram_graph_api",
                "error": f"Network exception communicating with Instagram Graph API: {str(exc)}",
            }


# Canonical aliases for backward and architectural compatibility
MetaGraphAdapter = MetaPublisherAdapter
InstagramGraphAdapter = MetaPublisherAdapter
