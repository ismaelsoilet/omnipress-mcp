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
        # Credentials and profile IDs are resolved at call time through ChannelManager
        # with Rule 04 precedence (Rule 14: no constructor-time env snapshots).
        pass

    @property
    def _channel_services(self) -> Dict[str, str]:
        """Stateless backward-compatibility property (Rule 14)."""
        return {}

    def get_api_key(self, channel_slug: Optional[str] = None) -> str:
        """
        Resolves the effective Buffer API key with strict Rule 04 precedence:
        1. channels/<channel_slug>/.env (BUFFER_API_KEY or BUFFER_ACCESS_TOKEN)
        2. Channel-prefixed process env var (e.g. <SLUG>_BUFFER_API_KEY)
        3. Global process env var (BUFFER_API_KEY or BUFFER_ACCESS_TOKEN)
        4. self.api_key instance default
        """
        try:
            from src.core.channel_manager import ChannelManager
            cm = ChannelManager()
            key = cm.get_credential("BUFFER_API_KEY", channel_slug) or cm.get_credential("BUFFER_ACCESS_TOKEN", channel_slug)
            if key:
                return key
        except Exception:
            pass

        return ""

    def is_configured(self, channel_slug: Optional[str] = None) -> bool:
        """Returns True if Buffer API key/token is configured globally or for channel."""
        return bool(self.get_api_key(channel_slug))

    def list_channels(self, channel_slug: Optional[str] = None, api_key: Optional[str] = None) -> Dict[str, Any]:
        """
        Fetches all connected channels across organizations using modern GraphQL API.
        Useful for discovering channel IDs automatically. Supports per-channel or explicit API key.
        """
        effective_key = api_key or self.get_api_key(channel_slug)
        if not effective_key:
            return {"success": False, "error": "BUFFER_API_KEY is not configured."}

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {effective_key}",
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

    PLATFORM_ALIASES = {
        "instagram": "instagram",
        "ig": "instagram",
        "x": "x",
        "twitter": "x",
        "x_twitter": "x",
        "linkedin": "linkedin",
        "threads": "threads",
    }

    @classmethod
    def _canonical_platform(cls, plat: str) -> str:
        plat_lower = plat.lower().strip()
        return cls.PLATFORM_ALIASES.get(plat_lower, plat_lower)

    def _resolve_targets(self, platforms: List[str], channel_slug: Optional[str] = None) -> List[Dict[str, str]]:
        """
        Resolves list of target profile dictionaries: [{"id": channel_id, "service": platform}, ...]
        Precedence:
        1. channels/<slug>/channel.json (social[plat].buffer_channel_id or social.x_twitter.buffer_channel_id)
        2. channels/<slug>/.env (BUFFER_<PLAT>_PROFILE_ID)
        3. Global process env / instance profile ID
        4. Auto-discovery from Buffer GraphQL API
        """
        target_dict: Dict[str, str] = {}
        normalized = [p.lower().strip() for p in platforms]
        if "all" in normalized:
            requested_platforms = ["linkedin", "x", "threads", "instagram"]
        else:
            requested_platforms = [self._canonical_platform(p) for p in normalized]

        ch_social = {}
        ch_env = {}
        if channel_slug:
            try:
                from src.core.channel_manager import ChannelManager
                cm = ChannelManager()
                ch = cm.get_channel(channel_slug)
                if ch:
                    ch_social = ch.get("social", {})
                ch_env = cm.get_channel_env(channel_slug)
            except Exception:
                pass

        effective_key = self.get_api_key(channel_slug)
        cached_remote_channels = None

        for plat in requested_platforms:
            resolved_id = None

            # Step 1: check channel.json
            if plat in ch_social and ch_social[plat].get("buffer_channel_id"):
                resolved_id = ch_social[plat].get("buffer_channel_id")
            elif plat == "x" and "x_twitter" in ch_social and ch_social["x_twitter"].get("buffer_channel_id"):
                resolved_id = ch_social["x_twitter"].get("buffer_channel_id")

            # Step 2: check channel credentials via ChannelManager (Rule 04 / Rule 14)
            if not resolved_id:
                try:
                    from src.core.channel_manager import ChannelManager
                    cm = ChannelManager()
                    env_plat_key = f"BUFFER_{plat.upper()}_PROFILE_ID"
                    cred_id = cm.get_credential(env_plat_key, channel_slug)
                    if cred_id:
                        resolved_id = cred_id
                except Exception:
                    pass

            # Step 3: fall back to auto-discovery from Buffer (instance env snapshots removed)

            # Step 4: if still not found, auto-discover from connected channels in Buffer using effective key
            if not resolved_id and effective_key:
                if cached_remote_channels is None:
                    channels_info = self.list_channels(channel_slug=channel_slug, api_key=effective_key)
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

            if resolved_id and resolved_id not in target_dict:
                target_dict[resolved_id] = plat

        return [{"id": r_id, "service": srv} for r_id, srv in target_dict.items()]

    def _resolve_channel_ids(self, platforms: List[str], channel_slug: Optional[str] = None) -> List[str]:
        """Backward-compatible helper returning flat list of channel IDs."""
        targets = self._resolve_targets(platforms, channel_slug=channel_slug)
        return [t["id"] for t in targets]

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
        effective_key = self.get_api_key(channel_slug)
        if not effective_key:
            return {
                "success": False,
                "error": "BUFFER_API_KEY or BUFFER_ACCESS_TOKEN is not configured in .env",
            }

        targets = self._resolve_targets(platforms, channel_slug=channel_slug)
        if not targets:
            return {
                "success": False,
                "error": f"No valid channel IDs found for requested platforms: {platforms}. Configure BUFFER_INSTAGRAM_PROFILE_ID or verify connected channels.",
            }
        target_ids = [t["id"] for t in targets]

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {effective_key}",
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

        created_posts = []
        for target in targets:
            ch_id = target["id"]
            service = target["service"]

            # Enforce platform-specific media limits (LinkedIn max 9, X max 4, Instagram max 10)
            service_limit = 10
            if service == "linkedin":
                service_limit = 9
            elif service in ("x", "twitter"):
                service_limit = 4
            elif service == "instagram":
                service_limit = 10

            doc_url = kwargs.get("document_url")
            doc_title = kwargs.get("document_title") or "Documento"
            doc_thumb = kwargs.get("document_thumbnail_url") or (media_urls[0] if media_urls else "")

            target_assets = []
            if service == "linkedin" and doc_url:
                target_assets.append({
                    "document": {
                        "url": doc_url,
                        "title": doc_title,
                        "thumbnailUrl": doc_thumb or doc_url,
                    }
                })
            elif media_urls:
                for url in media_urls[:service_limit]:
                    target_assets.append({"image": {"url": url}})

            input_payload: Dict[str, Any] = {
                "text": text,
                "channelId": ch_id,
                "schedulingType": "automatic",
                "mode": resolved_mode,
            }
            if schedule_time and resolved_mode == "customScheduled":
                input_payload["dueAt"] = schedule_time
            if target_assets:
                input_payload["assets"] = target_assets

            # Inject Instagram post metadata strictly when target is Instagram
            if service == "instagram":
                input_payload["metadata"] = {
                    "instagram": {
                        "type": "post",
                        "shouldShareToFeed": True
                    }
                }

            # Inject Twitter thread metadata strictly when target is Twitter/X
            if service in ("x", "twitter"):
                thread = kwargs.get("thread") or kwargs.get("thread_items")
                if thread and isinstance(thread, list) and len(thread) > 1:
                    input_payload["text"] = thread[0]
                    thread_objs = []
                    for item in thread[1:]:
                        if isinstance(item, str):
                            thread_objs.append({"text": item, "assets": []})
                        elif isinstance(item, dict):
                            if "assets" not in item:
                                item["assets"] = []
                            thread_objs.append(item)
                    input_payload["metadata"] = {
                        "twitter": {
                            "thread": thread_objs
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

        return self._fallback_rest_queue(
            text, target_ids, media_urls, schedule_time,
            mode=resolved_mode, channel_slug=channel_slug,
        )

    def _fallback_rest_queue(
        self,
        text: str,
        profile_ids: List[str],
        media_urls: Optional[List[str]] = None,
        schedule_time: Optional[str] = None,
        mode: Optional[str] = None,
        channel_slug: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Fallback to Buffer legacy REST endpoint (only for legacy 1/... OAuth tokens)."""
        effective_key = self.get_api_key(channel_slug)
        if not effective_key.startswith("1/"):
            return {
                "success": False,
                "provider": "buffer_graphql",
                "error": "Buffer GraphQL request failed and legacy REST API is deprecated/incompatible with public API keys.",
            }
        publish_now = (mode == "shareNow") or (not schedule_time and mode != "addToQueue")
        payload: Dict[str, Any] = {
            "access_token": effective_key,
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

    def delete_post(self, post_id: str, channel_slug: Optional[str] = None) -> Dict[str, Any]:
        """
        Deletes a post from Buffer via GraphQL deletePost mutation.
        Enforces Rule 09 (Single Publication & Clean Replacement Overwrite).
        """
        effective_key = self.get_api_key(channel_slug)
        if not effective_key:
            return {"success": False, "error": "BUFFER_API_KEY is not configured."}

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {effective_key}",
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
