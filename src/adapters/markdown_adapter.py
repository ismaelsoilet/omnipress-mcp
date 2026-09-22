"""Markdown file archive adapter for long-form publications."""

import os
import re
import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional


def slugify(value: str) -> str:
    """Converts a title into a URL-safe, clean filename slug."""
    value = re.sub(r"[^\w\s-]", "", value.lower())
    return re.sub(r"[-\s]+", "-", value).strip("-")


class MarkdownArchiveAdapter:
    """Saves long-form articles with YAML frontmatter locally."""

    def __init__(self, base_dir: Optional[str] = None):
        self.base_dir = Path(base_dir or os.getenv("ARTICLES_DIR", "./articles")).resolve()
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def save_article(
        self,
        title: str,
        content_markdown: str,
        category: str = "general",
        tags: Optional[List[str]] = None,
        author: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Saves the article to disk with YAML frontmatter.
        """
        now = datetime.datetime.now(datetime.timezone.utc)
        date_str = now.strftime("%Y-%m-%d")
        iso_str = now.isoformat()
        slug = slugify(title) or f"article-{int(now.timestamp())}"

        # Group articles by year/month for clean organization
        folder = self.base_dir / now.strftime("%Y") / now.strftime("%m")
        folder.mkdir(parents=True, exist_ok=True)

        filename = f"{date_str}-{slug}.md"
        filepath = folder / filename

        tags_list = tags or []
        yaml_tags = "\n".join([f"  - {t}" for t in tags_list])

        frontmatter = (
            "---\n"
            f'title: "{title}"\n'
            f'date: "{iso_str}"\n'
            f'category: "{category}"\n'
            f'author: "{author or "OmniPress"}"\n'
            "tags:\n"
            f"{yaml_tags}\n"
            "status: draft\n"
            "---\n\n"
        )

        full_content = frontmatter + content_markdown.strip() + "\n"
        filepath.write_text(full_content, encoding="utf-8")

        return {
            "success": True,
            "filepath": str(filepath),
            "filename": filename,
            "slug": slug,
            "created_at": iso_str,
        }

    def list_recent(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Lists recent archived markdown articles."""
        files = list(self.base_dir.rglob("*.md"))
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
