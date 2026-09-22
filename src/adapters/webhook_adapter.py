"""Webhook publishing adapter for n8n, Make, Slack, Telegram, or custom pipelines."""

import os
import hmac
import hashlib
import json
import requests
from typing import List, Dict, Any, Optional
from .base import BasePublisherAdapter


class WebhookPublisherAdapter(BasePublisherAdapter):
    """Dispatches publishing events to a configured webhook endpoint."""

    def __init__(self):
        self.webhook_url = os.getenv("OMNIPRESS_WEBHOOK_URL", "").strip()
        self.secret = os.getenv("OMNIPRESS_WEBHOOK_SECRET", "").strip()

    def is_configured(self) -> bool:
        return bool(self.webhook_url)

    def queue_social_post(
        self,
        text: str,
        platforms: List[str],
        media_urls: Optional[List[str]] = None,
        schedule_time: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Dispatches social post event to webhook.
        """
        return self.dispatch_event(
            event_type="social_post_queued",
            payload={
                "text": text,
                "platforms": platforms,
                "media_urls": media_urls or [],
                "schedule_time": schedule_time,
                "draft": True,
            },
        )

    def dispatch_event(self, event_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sends an arbitrary event payload to the configured webhook URL.
        """
        if not self.webhook_url:
            return {
                "success": False,
                "error": "OMNIPRESS_WEBHOOK_URL is not configured in .env",
            }

        data = {
            "event": event_type,
            "source": "omnipress-mcp",
            "data": payload,
        }

        body_bytes = json.dumps(data).encode("utf-8")
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "OmniPress-MCP/0.1.0",
        }

        if self.secret:
            signature = hmac.new(self.secret.encode("utf-8"), body_bytes, hashlib.sha256).hexdigest()
            headers["X-OmniPress-Signature"] = signature

        try:
            response = requests.post(self.webhook_url, data=body_bytes, headers=headers, timeout=15)
            return {
                "success": response.status_code in (200, 201, 202, 204),
                "provider": "webhook",
                "status_code": response.status_code,
                "response_body": response.text[:500],
            }
        except requests.RequestException as e:
            return {
                "success": False,
                "provider": "webhook",
                "error": f"Failed to dispatch webhook: {str(e)}",
            }
