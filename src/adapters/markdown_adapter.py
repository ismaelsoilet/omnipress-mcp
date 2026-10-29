"""Markdown file archive adapter for long-form publications."""

import os
import re
import datetime
import unicodedata
from pathlib import Path
from typing import List, Dict, Any, Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


def slugify(value: str) -> str:
    """Converts a title into a URL-safe, clean filename slug."""
    value = unicodedata.normalize("NFKD", str(value)).encode("ascii", "ignore").decode("ascii")
    value = re.sub(r"[^\w\s-]", "", value.lower())
    return re.sub(r"[-\s]+", "-", value).strip("-")


from src.adapters.base import BasePublisherAdapter


class MarkdownArchiveAdapter(BasePublisherAdapter):
    """Saves long-form articles with YAML frontmatter locally, with multi-channel support."""

    def __init__(self, base_dir: Optional[str] = None):
        self.base_dir_arg = Path(base_dir).resolve() if base_dir else None

    @property
    def default_dir(self) -> Path:
        """Resolves the global archive directory at call time (never a constructor snapshot)."""
        target = self.base_dir_arg or Path(os.getenv("ARTICLES_DIR", "./articles")).resolve()
        target.mkdir(parents=True, exist_ok=True)
        return target

    def is_configured(self, channel_slug: Optional[str] = None) -> bool:
        """Local file archive is always configured and ready."""
        return True

    def queue_social_post(
        self,
        text: str,
        platforms: List[str],
        media_urls: Optional[List[str]] = None,
        schedule_time: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Archives a social post locally as a markdown record."""
        title = kwargs.get("title", text.split("\n")[0][:50])
        channel_slug = kwargs.get("channel_slug")
        res = self.save_article(
            title=f"Social Post: {title}",
            content_markdown=text,
            category="social",
            tags=platforms,
            channel_slug=channel_slug,
        )
        return {
            "success": True,
            "provider": "markdown_archive",
            "path": res.get("path"),
            "platforms": platforms,
        }

    def publish_article(
        self,
        title: str,
        content_markdown: str,
        category: str = "technology",
        tags: Optional[List[str]] = None,
        author: Optional[str] = None,
        canonical_url: Optional[str] = None,
        published: bool = False,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Publishes/archives a full article locally."""
        channel_slug = kwargs.get("channel_slug")
        return self.save_article(
            title=title,
            content_markdown=content_markdown,
            category=category,
            tags=tags,
            author=author,
            channel_slug=channel_slug,
        )

    def _resolve_target_dir(self, channel_slug: Optional[str] = None) -> Path:
        """Resolves target directory, respecting channel isolation if available."""
        if channel_slug:
            from src.core.channel_manager import ChannelManager

            c_dir = ChannelManager().get_channel_dir(channel_slug) / "articles"
            c_dir.mkdir(parents=True, exist_ok=True)
            return c_dir

        if self.base_dir_arg:
            return self.default_dir

        from src.core.channel_manager import ChannelManager

        cm = ChannelManager()
        active_slug = cm.get_active_channel_slug()
        active_dir = cm.get_channel_dir(active_slug) / "articles"
        if active_dir.parent.exists():
            active_dir.mkdir(parents=True, exist_ok=True)
            return active_dir

        return self.default_dir

    def save_article(
        self,
        title: str,
        content_markdown: str,
        category: str = "general",
        tags: Optional[List[str]] = None,
        author: Optional[str] = None,
        channel_slug: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Saves the article to disk with YAML frontmatter.
        """
        now = datetime.datetime.now(datetime.timezone.utc)
        date_str = now.strftime("%Y-%m-%d")
        iso_str = now.isoformat()
        slug = slugify(title) or f"article-{int(now.timestamp())}"

        base_folder = self._resolve_target_dir(channel_slug)
        folder = base_folder / now.strftime("%Y") / now.strftime("%m")
        folder.mkdir(parents=True, exist_ok=True)

        filename = f"{date_str}-{slug}.md"
        filepath = folder / filename

        escaped_title = title.replace("\r", " ").replace("\n", " ").replace('"', '\\"')
        escaped_category = category.replace('"', '\\"')
        escaped_author = (author or "OmniPress").replace('"', '\\"')

        # Strip pre-existing frontmatter to avoid duplicate YAML blocks
        cleaned_content = content_markdown.strip()
        if cleaned_content.startswith("---"):
            parts = re.split(r"^---\s*$", cleaned_content, maxsplit=2, flags=re.MULTILINE)
            if len(parts) >= 3:
                cleaned_content = parts[2].strip()

        tags_list = tags or []
        yaml_tags = "\n".join([f"  - {t}" for t in tags_list])

        frontmatter = (
            "---\n"
            f'title: "{escaped_title}"\n'
            f'date: "{iso_str}"\n'
            f'category: "{escaped_category}"\n'
            f'author: "{escaped_author}"\n'
            "tags:\n"
            f"{yaml_tags}\n"
            "status: draft\n"
            "---\n\n"
        )

        full_content = frontmatter + cleaned_content + "\n"
        filepath.write_text(full_content, encoding="utf-8")

        return {
            "success": True,
            "filepath": str(filepath),
            "filename": filename,
            "slug": slug,
            "created_at": iso_str,
            "channel_slug": channel_slug,
        }

    def list_recent(self, limit: int = 5, channel_slug: Optional[str] = None) -> List[Dict[str, Any]]:
        """Lists recent archived markdown articles, optionally scoped to a channel."""
        target_dir = self._resolve_target_dir(channel_slug)
        files = list(target_dir.rglob("*.md"))

        # Also search root articles dir if channel dir has none and no explicit slug
        if not files and not channel_slug and self.default_dir.exists():
            files = list(self.default_dir.rglob("*.md"))

        files.sort(key=lambda p: p.stat().st_mtime, reverse=True)

        results = []
        for file in files[:limit]:
            results.append({
                "path": str(file),
                "name": file.name,
                "modified": datetime.datetime.fromtimestamp(file.stat().st_mtime).isoformat(),
                "size_bytes": file.stat().st_size,
            })
        return results
