"""Buffer publishing adapter for LinkedIn and X (Twitter)."""

import os
import requests
from typing import List, Dict, Any, Optional
from .base import BasePublisherAdapter


class BufferPublisherAdapter(BasePublisherAdapter):
    """Integrates with Buffer REST API to queue posts for LinkedIn and X."""

    API_URL = "https://api.bufferapp.com/1/updates/create.json"

    def __init__(self):
        self.access_token = os.getenv("BUFFER_ACCESS_TOKEN", "").strip()
        self.linkedin_profile_id = os.getenv("BUFFER_LINKEDIN_PROFILE_ID", "").strip()
        self.x_profile_id = os.getenv("BUFFER_X_PROFILE_ID", "").strip()
        self.threads_profile_id = os.getenv("BUFFER_THREADS_PROFILE_ID", "").strip()

    def is_configured(self) -> bool:
        return bool(self.access_token and (self.linkedin_profile_id or self.x_profile_id or self.threads_profile_id))

    def _resolve_profile_ids(self, platforms: List[str]) -> List[str]:
        target_ids = []
        normalized = [p.lower().strip() for p in platforms]

        if ("linkedin" in normalized or "all" in normalized) and self.linkedin_profile_id:
            target_ids.append(self.linkedin_profile_id)
        if ("x" in normalized or "twitter" in normalized or "all" in normalized) and self.x_profile_id:
            target_ids.append(self.x_profile_id)
        if ("threads" in normalized or "all" in normalized) and self.threads_profile_id:
            target_ids.append(self.threads_profile_id)

        return target_ids

    def queue_social_post(
        self,
        text: str,
        platforms: List[str],
        media_urls: Optional[List[str]] = None,
        schedule_time: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Submits post to Buffer queue in Draft/Review mode.
        """
        if not self.access_token:
            return {
                "success": False,
                "error": "BUFFER_ACCESS_TOKEN is not configured in .env",
            }

        profile_ids = self._resolve_profile_ids(platforms)
        if not profile_ids:
            return {
                "success": False,
                "error": f"No valid profile IDs found for requested platforms: {platforms}. Check .env configuration.",
            }

        payload: Dict[str, Any] = {
            "access_token": self.access_token,
            "profile_ids[]": profile_ids,
            "text": text,
            "top": False,
            "now": False,  # Always queue as draft for human-in-the-loop review
        }

        if schedule_time:
            payload["scheduled_at"] = schedule_time

        if media_urls and len(media_urls) > 0:
            payload["media[link]"] = media_urls[0]

        try:
            response = requests.post(self.API_URL, data=payload, timeout=20)
            if response.status_code in (200, 201):
                data = response.json()
                return {
                    "success": True,
                    "provider": "buffer",
                    "queued_profiles_count": len(profile_ids),
                    "buffer_response": data.get("message", "Post queued successfully as draft."),
                }
            return {
                "success": False,
                "provider": "buffer",
                "status_code": response.status_code,
                "error": response.text,
            }
        except requests.RequestException as e:
            return {
                "success": False,
                "provider": "buffer",
                "error": f"Network exception connecting to Buffer: {str(e)}",
            }
