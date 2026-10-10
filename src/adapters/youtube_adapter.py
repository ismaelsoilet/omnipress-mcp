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
        self.base_dir = Path(
            base_dir or os.getenv("MEDIA_STAGING_DIR", "./media/staging")
        ).resolve()
        self.youtube_webhook_url = os.getenv("YOUTUBE_WEBHOOK_URL", "").strip()

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
    ) -> Dict[str, Any]:
        """Creates staging metadata JSON and prepares dispatch record."""
        clean_title = (title or "Vídeo Sem Título").strip()
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

        folder = self.base_dir / "youtube" / now.strftime("%Y") / now.strftime("%m")
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
