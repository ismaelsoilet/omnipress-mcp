"""Direct Meta Instagram Graph API publishing adapter for OmniPress."""

import os
import requests
from typing import List, Dict, Any, Optional
from .base import BasePublisherAdapter


class InstagramGraphAdapter(BasePublisherAdapter):
    """
    Direct publishing adapter using official Meta Instagram Graph API.
    Enables autonomous publishing of single images and carousels to Instagram Professional accounts.
    """

    GRAPH_API_VERSION = "v19.0"
    BASE_URL = f"https://graph.facebook.com/{GRAPH_API_VERSION}"

    def __init__(self):
        self.access_token = os.getenv("INSTAGRAM_ACCESS_TOKEN", "").strip()
        self.account_id = (
            os.getenv("INSTAGRAM_ACCOUNT_ID", "").strip()
            or os.getenv("INSTAGRAM_BUSINESS_ACCOUNT_ID", "").strip()
        )

    def is_configured(self) -> bool:
        """Returns True if Meta Instagram Graph API credentials are set in environment."""
        return bool(self.access_token and self.account_id)

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
        Publishes a single image or multi-slide carousel to Instagram via Meta Graph API.
        Protected by PublishingShield pre-flight validation and anti-duplicate ledger (Rule 09).
        """
        if not self.is_configured():
            return {
                "success": False,
                "error": "INSTAGRAM_ACCESS_TOKEN or INSTAGRAM_ACCOUNT_ID is not configured in .env",
            }

        resolved_mode = mode or ("customScheduled" if schedule_time else "shareNow")

        # Gate 1, 2, 3: Pre-flight validation (character limits, placeholder text, media required)
        from src.core.publishing_shield import PublishingShield
        is_valid, validation_err = PublishingShield.validate_post(
            text=text,
            platforms=platforms or ["instagram"],
            media_urls=media_urls,
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
        is_dup, dup_err = PublishingShield.check_duplicate(
            channel_id=self.account_id,
            text=text,
            media_urls=media_urls,
            force=force_duplicate,
        )
        if is_dup:
            return {
                "success": False,
                "provider": "publishing_shield",
                "error": dup_err,
            }

        headers = {"Authorization": f"Bearer {self.access_token}"}

        try:
            # Case A: Single Image Post
            if len(media_urls) == 1:
                container_url = f"{self.BASE_URL}/{self.account_id}/media"
                payload = {
                    "image_url": media_urls[0],
                    "caption": text,
                }
                res = requests.post(container_url, data=payload, headers=headers, timeout=20)
                if res.status_code not in (200, 201):
                    return {
                        "success": False,
                        "error": f"Failed creating Instagram media container: {res.text}",
                    }

                container_id = res.json().get("id")

            # Case B: Multi-Image Carousel Post
            else:
                # 1. Create items for each slide
                children_ids = []
                for img_url in media_urls[:10]:  # Max 10 slides on Instagram
                    item_payload = {
                        "image_url": img_url,
                        "is_carousel_item": "true",
                    }
                    res_item = requests.post(
                        f"{self.BASE_URL}/{self.account_id}/media",
                        data=item_payload,
                        headers=headers,
                        timeout=20,
                    )
                    if res_item.status_code not in (200, 201):
                        return {
                            "success": False,
                            "error": f"Failed creating carousel item {img_url}: {res_item.text}",
                        }
                    children_ids.append(res_item.json().get("id"))

                # 2. Create parent carousel container
                carousel_payload = {
                    "media_type": "CAROUSEL",
                    "caption": text,
                    "children": ",".join(children_ids),
                }
                res_parent = requests.post(
                    f"{self.BASE_URL}/{self.account_id}/media",
                    data=carousel_payload,
                    headers=headers,
                    timeout=20,
                )
                if res_parent.status_code not in (200, 201):
                    return {
                        "success": False,
                        "error": f"Failed creating parent carousel container: {res_parent.text}",
                    }
                container_id = res_parent.json().get("id")

            # Step 2: Publish the media container
            publish_url = f"{self.BASE_URL}/{self.account_id}/media_publish"
            pub_res = requests.post(
                publish_url,
                data={"creation_id": container_id},
                headers=headers,
                timeout=20,
            )
            if pub_res.status_code in (200, 201):
                post_id = pub_res.json().get("id")
                from src.core.publishing_shield import PublishingShield
                PublishingShield.record_published(
                    channel_id=self.account_id,
                    text=text,
                    media_urls=media_urls,
                    post_id=post_id,
                    provider="instagram_graph_api",
                )
                return {
                    "success": True,
                    "provider": "instagram_graph_api",
                    "post_id": post_id,
                    "media_count": len(media_urls),
                    "permalink": f"https://www.instagram.com/p/{post_id}/" if post_id else None,
                }

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
