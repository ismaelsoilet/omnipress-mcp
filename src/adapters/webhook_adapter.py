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
        # Credentials are resolved at call time through ChannelManager (Rule 14).
        pass

    def get_credentials(self, channel_slug: Optional[str] = None) -> tuple[str, str]:
        """Resolves (webhook_url, secret) with strict Rule 04 channel precedence."""
        from src.core.channel_manager import ChannelManager

        cm = ChannelManager()
        return (
            cm.get_credential("OMNIPRESS_WEBHOOK_URL", channel_slug),
            cm.get_credential("OMNIPRESS_WEBHOOK_SECRET", channel_slug),
        )

    def is_configured(self, channel_slug: Optional[str] = None) -> bool:
        url, _ = self.get_credentials(channel_slug)
        return bool(url)

    def queue_social_post(
        self,
        text: str,
        platforms: List[str],
        media_urls: Optional[List[str]] = None,
        schedule_time: Optional[str] = None,
        channel_slug: Optional[str] = None,
        **kwargs: Any,
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
                "channel_slug": channel_slug,
                "draft": True,
            },
            channel_slug=channel_slug,
        )

    def dispatch_event(
        self,
        event_type: str,
        payload: Dict[str, Any],
        channel_slug: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Sends an arbitrary event payload to the configured webhook URL.
        """
        webhook_url, secret = self.get_credentials(channel_slug)
        if not webhook_url:
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
        from src import __version__
        headers = {
            "Content-Type": "application/json",
            "User-Agent": f"OmniPress-MCP/{__version__}",
        }

        if secret:
            signature = hmac.new(secret.encode("utf-8"), body_bytes, hashlib.sha256).hexdigest()
            headers["X-OmniPress-Signature"] = signature

        try:
            response = requests.post(webhook_url, data=body_bytes, headers=headers, timeout=15)
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
