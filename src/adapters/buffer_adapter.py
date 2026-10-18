"""Buffer publishing adapter supporting both modern GraphQL API (api.buffer.com) and legacy REST."""

import os
import requests
from typing import List, Dict, Any, Optional
from .base import BasePublisherAdapter


class BufferPublisherAdapter(BasePublisherAdapter):
    """
    Integrates with Buffer API.
    Supports modern GraphQL API (https://api.buffer.com) with Personal API Keys
    as well as backward-compatible legacy REST API.
    """

    GRAPHQL_URL = "https://api.buffer.com"
    REST_API_URL = "https://api.bufferapp.com/1/updates/create.json"

    def __init__(self):
        # Support both BUFFER_API_KEY (modern) and BUFFER_ACCESS_TOKEN (legacy)
        self.api_key = (
            os.getenv("BUFFER_API_KEY", "").strip()
            or os.getenv("BUFFER_ACCESS_TOKEN", "").strip()
        )
        self.linkedin_profile_id = os.getenv("BUFFER_LINKEDIN_PROFILE_ID", "").strip()
        self.x_profile_id = os.getenv("BUFFER_X_PROFILE_ID", "").strip()
        self.threads_profile_id = os.getenv("BUFFER_THREADS_PROFILE_ID", "").strip()
        self.instagram_profile_id = os.getenv("BUFFER_INSTAGRAM_PROFILE_ID", "").strip()
        self._channel_services: Dict[str, str] = {}

    def is_configured(self) -> bool:
        """Returns True if Buffer API key/token is configured."""
        return bool(self.api_key)

    def list_channels(self) -> Dict[str, Any]:
        """
        Fetches all connected channels across organizations using modern GraphQL API.
        Useful for discovering channel IDs automatically.
        """
        if not self.api_key:
            return {"success": False, "error": "BUFFER_API_KEY is not configured."}

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

        # Step 1: Query organizations
        org_query = """
        query GetOrganizations {
          account {
            organizations {
              id
              name
            }
          }
        }
        """
        try:
            res = requests.post(
                self.GRAPHQL_URL,
                json={"query": org_query},
                headers=headers,
                timeout=15,
            )
            if res.status_code != 200:
                return {
                    "success": False,
                    "error": f"Failed fetching organizations ({res.status_code}): {res.text}",
                }

            data = res.json().get("data", {})
            orgs = data.get("account", {}).get("organizations", [])
            if not orgs:
                return {"success": True, "channels": []}

            all_channels = []
            channel_query = """
            query GetChannels($input: ChannelsInput!) {
              channels(input: $input) {
                id
                name
                service
              }
            }
            """
            for org in orgs:
                c_res = requests.post(
                    self.GRAPHQL_URL,
                    json={
                        "query": channel_query,
                        "variables": {"input": {"organizationId": org["id"]}},
                    },
                    headers=headers,
                    timeout=15,
                )
                if c_res.status_code == 200:
                    ch_data = c_res.json().get("data", {}).get("channels", [])
                    for ch in ch_data:
                        ch["organization_id"] = org["id"]
                        all_channels.append(ch)

            return {"success": True, "channels": all_channels}
        except requests.RequestException as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def _canonical_platform(plat: str) -> str:
        plat_lower = plat.lower().strip()
        if plat_lower in ("instagram", "ig"):
            return "instagram"
        if plat_lower in ("x", "twitter"):
            return "x"
        if plat_lower in ("linkedin",):
            return "linkedin"
        if plat_lower in ("threads",):
            return "threads"
        return plat_lower

    def _resolve_channel_ids(self, platforms: List[str], channel_slug: Optional[str] = None) -> List[str]:
        target_ids = []
        normalized = [p.lower().strip() for p in platforms]
        if "all" in normalized:
            requested_platforms = ["linkedin", "x", "threads", "instagram"]
        else:
            requested_platforms = [self._canonical_platform(p) for p in normalized]

        if not hasattr(self, "_channel_services"):
            self._channel_services = {}

        # 1. If channel_slug is specified, look up channel-specific buffer_channel_id
        ch_social = {}
        if channel_slug:
            from src.core.channel_manager import ChannelManager
            ch = ChannelManager().get_channel(channel_slug)
            if ch:
                ch_social = ch.get("social", {})

        cached_remote_channels = None

        for plat in requested_platforms:
            resolved_id = None

            # Step 1: check channel.json
            if plat in ch_social:
                resolved_id = ch_social[plat].get("buffer_channel_id")

            # Step 2: fall back to environment profile ID for this specific platform
            if not resolved_id:
                if plat == "linkedin" and self.linkedin_profile_id:
                    resolved_id = self.linkedin_profile_id
                elif plat == "x" and self.x_profile_id:
                    resolved_id = self.x_profile_id
                elif plat == "threads" and self.threads_profile_id:
                    resolved_id = self.threads_profile_id
                elif plat == "instagram" and self.instagram_profile_id:
                    resolved_id = self.instagram_profile_id

            # Step 3: if still not found, auto-discover from connected channels in Buffer
            if not resolved_id and self.api_key:
                if cached_remote_channels is None:
                    channels_info = self.list_channels()
                    cached_remote_channels = (
                        channels_info.get("channels", []) if channels_info.get("success") else []
                    )
                for remote_ch in cached_remote_channels:
                    srv = remote_ch.get("service", "").lower()
                    if plat == "instagram" and srv == "instagram":
                        resolved_id = remote_ch["id"]
                        break
                    elif plat == "linkedin" and srv == "linkedin":
                        resolved_id = remote_ch["id"]
                        break
                    elif plat == "x" and srv in ("twitter", "x"):
                        resolved_id = remote_ch["id"]
                        break
                    elif plat == "threads" and srv == "threads":
                        resolved_id = remote_ch["id"]
                        break

            if resolved_id and resolved_id not in target_ids:
                target_ids.append(resolved_id)
                self._channel_services[resolved_id] = plat

        return target_ids

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
        Submits post to Buffer via modern GraphQL API (with fallback to legacy REST).
        When schedule_time is None (or empty), defaults to mode='shareNow' to publish immediately.
        Supports channel_slug to dispatch to channel-specific Buffer accounts.
        Enforces PublishingShield pre-flight checks and anti-duplicate ledger (Rule 09).
        """
        if not self.is_configured():
            return {
                "success": False,
                "error": "BUFFER_API_KEY or BUFFER_ACCESS_TOKEN is not configured in .env",
            }

        normalized = [p.lower().strip() for p in platforms]
        target_ids = self._resolve_channel_ids(platforms, channel_slug=channel_slug)
        if not target_ids:
            return {
                "success": False,
                "error": f"No valid channel IDs found for requested platforms: {platforms}. Configure BUFFER_INSTAGRAM_PROFILE_ID or verify connected channels.",
            }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

        # Resolve publishing mode:
        if mode:
            resolved_mode = mode
        elif schedule_time:
            resolved_mode = "customScheduled"
        else:
            resolved_mode = "shareNow"

        # Gate 1 & 2 & 3: Run PublishingShield pre-flight validation (character limits, test texts, media requirements)
        from src.core.publishing_shield import PublishingShield
        is_valid, validation_err = PublishingShield.validate_post(
            text=text,
            platforms=platforms,
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

        # Gate 4: Run Anti-Duplicate Idempotency Check (Rule 09)
        for ch_id in target_ids:
            is_dup, dup_err = PublishingShield.check_duplicate(
                channel_id=ch_id,
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

        # Attempt modern GraphQL createPost mutation
        mutation = """
        mutation CreatePost($input: CreatePostInput!) {
          createPost(input: $input) {
            ... on PostActionSuccess {
              post {
                id
                text
                dueAt
              }
            }
            ... on MutationError {
              message
            }
          }
        }
        """

        assets = []
        if media_urls:
            for url in media_urls[:10]:
                assets.append({"image": {"url": url}})

        created_posts = []
        for ch_id in target_ids:
            input_payload: Dict[str, Any] = {
                "text": text,
                "channelId": ch_id,
                "schedulingType": "automatic",
                "mode": resolved_mode,
            }
            if schedule_time and resolved_mode == "customScheduled":
                input_payload["dueAt"] = schedule_time
            if assets:
                input_payload["assets"] = assets

            # If target channel is Instagram, inject mandatory Instagram post metadata
            service_for_ch = getattr(self, "_channel_services", {}).get(ch_id)
            is_instagram = (
                service_for_ch == "instagram"
                or ch_id == self.instagram_profile_id
                or (len(target_ids) == 1 and any(p in ("instagram", "ig") for p in normalized))
            )
            if not is_instagram and channel_slug:
                try:
                    from src.core.channel_manager import ChannelManager
                    ch_conf = ChannelManager().get_channel(channel_slug)
                    if ch_conf and ch_conf.get("social", {}).get("instagram", {}).get("buffer_channel_id") == ch_id:
                        is_instagram = True
                except Exception:
                    pass

            if is_instagram:
                input_payload["metadata"] = {
                    "instagram": {
                        "type": "post",
                        "shouldShareToFeed": True
                    }
                }

            try:
                res = requests.post(
                    self.GRAPHQL_URL,
                    json={"query": mutation, "variables": {"input": input_payload}},
                    headers=headers,
                    timeout=20,
                )
                if res.status_code == 200:
                    data = res.json().get("data", {}).get("createPost", {})
                    if "post" in data:
                        post_obj = data["post"]
                        if not post_obj.get("channelId"):
                            post_obj["channelId"] = ch_id
                        created_posts.append(post_obj)
                    elif "message" in data:
                        msg = data.get("message", "")
                        return {
                            "success": False,
                            "provider": "buffer_graphql",
                            "error": msg,
                        }
                else:
                    remaining_channels = [c for c in target_ids if c not in [p.get("channelId") for p in created_posts]]
                    if remaining_channels:
                        fallback_res = self._fallback_rest_queue(text, remaining_channels, media_urls, schedule_time, mode=resolved_mode)
                        if not created_posts:
                            return fallback_res
                    break
            except requests.RequestException:
                remaining_channels = [c for c in target_ids if c not in [p.get("channelId") for p in created_posts]]
                if remaining_channels:
                    fallback_res = self._fallback_rest_queue(text, remaining_channels, media_urls, schedule_time, mode=resolved_mode)
                    if not created_posts:
                        return fallback_res
                break

        if created_posts:
            from src.core.publishing_shield import PublishingShield
            for p in created_posts:
                post_ch_id = p.get("channelId") or (target_ids[0] if target_ids else "")
                PublishingShield.record_published(
                    channel_id=post_ch_id,
                    text=text,
                    media_urls=media_urls,
                    post_id=p.get("id"),
                    provider="buffer_graphql",
                )
            return {
                "success": True,
                "provider": "buffer_graphql",
                "mode": resolved_mode,
                "queued_profiles_count": len(created_posts),
                "posts": created_posts,
                "message": f"Successfully {'published' if resolved_mode == 'shareNow' else 'queued'} {len(created_posts)} post(s) via Buffer.",
            }

        return self._fallback_rest_queue(text, target_ids, media_urls, schedule_time, mode=resolved_mode)

    def _fallback_rest_queue(
        self,
        text: str,
        profile_ids: List[str],
        media_urls: Optional[List[str]] = None,
        schedule_time: Optional[str] = None,
        mode: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Fallback to Buffer legacy REST endpoint (only for legacy 1/... OAuth tokens)."""
        if not self.api_key.startswith("1/"):
            return {
                "success": False,
                "provider": "buffer_graphql",
                "error": "Buffer GraphQL request failed and legacy REST API is deprecated/incompatible with public API keys.",
            }
        publish_now = (mode == "shareNow") or (not schedule_time and mode != "addToQueue")
        payload: Dict[str, Any] = {
            "access_token": self.api_key,
            "profile_ids[]": profile_ids,
            "text": text,
            "top": False,
            "now": publish_now,
        }
        if schedule_time and not publish_now:
            payload["scheduled_at"] = schedule_time
        if media_urls and len(media_urls) > 0:
            payload["media[link]"] = media_urls[0]

        try:
            response = requests.post(self.REST_API_URL, data=payload, timeout=20)
            if response.status_code in (200, 201):
                data = response.json()
                return {
                    "success": True,
                    "provider": "buffer_rest",
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

    def delete_post(self, post_id: str) -> Dict[str, Any]:
        """
        Deletes a post from Buffer via GraphQL deletePost mutation.
        Enforces Rule 09 (Single Publication & Clean Replacement Overwrite).
        """
        if not self.api_key:
            return {"success": False, "error": "BUFFER_API_KEY is not configured."}

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

        mutation = """
        mutation DeletePost($input: DeletePostInput!) {
          deletePost(input: $input) {
            ... on DeletePostSuccess {
              id
            }
            ... on VoidMutationError {
              message
            }
          }
        }
        """
        try:
            res = requests.post(
                self.GRAPHQL_URL,
                json={"query": mutation, "variables": {"input": {"id": post_id}}},
                headers=headers,
                timeout=15,
            )
            if res.status_code == 200:
                data = res.json().get("data", {}).get("deletePost", {})
                if "id" in data:
                    from src.core.publishing_shield import PublishingShield
                    PublishingShield.remove_entry(data["id"])
                    return {"success": True, "provider": "buffer_graphql", "deleted_id": data["id"]}
                elif "message" in data:
                    return {"success": False, "provider": "buffer_graphql", "error": data["message"]}
            return {"success": False, "provider": "buffer_graphql", "status_code": res.status_code, "error": res.text}
        except requests.RequestException as e:
            return {"success": False, "provider": "buffer_graphql", "error": str(e)}
