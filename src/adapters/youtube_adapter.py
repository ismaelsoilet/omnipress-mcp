"""YouTube staging and upload adapter for Shorts and long-form video publications."""

import os
import json
import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from src.adapters.markdown_adapter import slugify


class YouTubeStagingAdapter:
    """Stages video metadata, scripts, and media files for YouTube and YouTube Shorts."""

    def __init__(self, base_dir: Optional[str] = None):
        self.base_dir_arg = Path(base_dir).resolve() if base_dir else None

    @property
    def base_dir(self) -> Path:
        """Resolves the global staging root at call time (never a constructor snapshot)."""
        target = self.base_dir_arg or Path(os.getenv("MEDIA_STAGING_DIR", "./media/staging")).resolve()
        target.mkdir(parents=True, exist_ok=True)
        return target

    def get_credentials(self, channel_slug: Optional[str] = None) -> str:
        """Resolves YOUTUBE_WEBHOOK_URL with strict Rule 04 channel precedence."""
        from src.core.channel_manager import ChannelManager

        return ChannelManager().get_credential("YOUTUBE_WEBHOOK_URL", channel_slug)

    def is_configured(self, channel_slug: Optional[str] = None) -> bool:
        return bool(self.get_credentials(channel_slug))

    def _resolve_staging_dir(self, channel_slug: Optional[str] = None) -> Path:
        """Resolves target staging directory, respecting channel isolation."""
        if self.base_dir_arg:
            return self.base_dir

        try:
            from src.core.channel_manager import ChannelManager

            cm = ChannelManager()
            slug = channel_slug or cm.get_active_channel_slug()
            c_dir = cm.get_channel_dir(slug) / "media" / "staging"
            c_dir.mkdir(parents=True, exist_ok=True)
            return c_dir
        except Exception:
            return self.base_dir

    def stage_video(
        self,
        title: str,
        description: str,
        tags: Optional[List[str]] = None,
        is_short: bool = False,
        category_id: str = "27",
        privacy_status: str = "private",
        media_urls: Optional[List[str]] = None,
        thumbnail_url: Optional[str] = None,
        schedule_time: Optional[str] = None,
        channel_slug: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Creates staging metadata JSON and prepares dispatch record."""
        clean_title = (title or "Untitled").strip()
        if is_short and "#shorts" not in clean_title.lower():
            clean_title = f"{clean_title} #Shorts"
        if len(clean_title) > 100:
            clean_title = clean_title[:97] + "..."

        formatted_desc = (description or "").strip()
        tags_list = tags or []
        if tags_list:
            hashtags = " ".join(
                [t if t.startswith("#") else f"#{t.replace(' ', '')}" for t in tags_list[:5]]
            )
            formatted_desc += f"\n\n{hashtags}"

        now = datetime.datetime.now(datetime.timezone.utc)
        date_str = now.strftime("%Y-%m-%d")
        slug = slugify(clean_title) or f"yt-{int(now.timestamp())}"

        base_staging = self._resolve_staging_dir(channel_slug)
        folder = base_staging / "youtube" / now.strftime("%Y") / now.strftime("%m")
        folder.mkdir(parents=True, exist_ok=True)

        manifest = {
            "platform": "youtube_shorts" if is_short else "youtube",
            "title": clean_title,
            "description": formatted_desc,
            "tags": [t.lstrip("#") for t in tags_list],
            "categoryId": category_id,
            "privacyStatus": privacy_status,
            "isShort": is_short,
            "mediaUrls": media_urls or [],
            "thumbnailUrl": thumbnail_url,
            "scheduleTime": schedule_time,
            "stagedAt": now.isoformat(),
            "status": "staged_draft",
        }

        filename = f"{date_str}-{slug}.json"
        filepath = folder / filename

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)

        return {
            "filename": filename,
            "filepath": str(filepath),
            "manifest": manifest,
        }
