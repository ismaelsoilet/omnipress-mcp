"""OmniPress FastMCP Server - Exposes agentic publishing tools to Antigravity."""

import os
import sys
from pathlib import Path
from typing import List, Optional
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

# Ensure project root is in sys.path when executed directly
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Load .env from project root or current working directory
load_dotenv(PROJECT_ROOT / ".env")
load_dotenv()

from src.adapters.markdown_adapter import MarkdownArchiveAdapter
from src.adapters.buffer_adapter import BufferPublisherAdapter
from src.adapters.webhook_adapter import WebhookPublisherAdapter
from src.adapters.reddit_adapter import RedditPublisherAdapter
from src.utils.sanitizer import sanitize_text, inspect_sensitive_data

# Initialize FastMCP Server
mcp = FastMCP("OmniPress")

# Initialize Adapters
markdown_adapter = MarkdownArchiveAdapter()
buffer_adapter = BufferPublisherAdapter()
webhook_adapter = WebhookPublisherAdapter()
reddit_adapter = RedditPublisherAdapter()


@mcp.tool()
def omnipress_publish_article(
    title: str,
    content_markdown: str,
    category: str = "technology",
    tags: Optional[List[str]] = None,
    author: Optional[str] = None,
    sanitize: bool = True,
) -> str:
    """
    Saves a complete, publication-ready long-form article to the local archive
    with YAML frontmatter (ready for Substack, Medium, Jusbrasil, or a static blog).
    Automatically checks and masks sensitive lawsuit/tax numbers and PII when sanitize=True.
    """
    sanitization_notes = []
    processed_content = content_markdown

    if sanitize:
        processed_content, findings = sanitize_text(content_markdown)
        if findings:
            sanitization_notes.append(f"🔒 Anonymized {len(findings)} sensitive item(s):")
            for f in findings:
                sanitization_notes.append(f"  - {f['type']}: {f['match']}")

    result = markdown_adapter.save_article(
        title=title,
        content_markdown=processed_content,
        category=category,
        tags=tags or [],
        author=author,
    )

    # If webhook configured, notify pipeline of new article
    if webhook_adapter.is_configured():
        webhook_adapter.dispatch_event("article_saved", result)

    output = [
        f"✅ Article archived successfully: **{result['filename']}**",
        f"📁 Path: `{result['filepath']}`",
        f"🏷️ Category: `{category}` | Tags: {tags or []}",
    ]

    if sanitization_notes:
        output.append("\n" + "\n".join(sanitization_notes))

    return "\n".join(output)


@mcp.tool()
def omnipress_queue_post(
    text: str,
    platforms: Optional[List[str]] = None,
    title: Optional[str] = None,
    media_urls: Optional[List[str]] = None,
    schedule_time: Optional[str] = None,
    sanitize: bool = True,
) -> str:
    """
    Queues a post or thread to social platforms (LinkedIn, X, Threads via Buffer, or Reddit)
    in Draft/Review mode.
    Platforms can be: ["linkedin"], ["x"], ["threads"], ["reddit:subreddit_name"], or ["all"].
    """
    target_platforms = platforms or ["linkedin"]
    processed_text = text
    sanitization_notes = []

    if sanitize:
        processed_text, findings = sanitize_text(text)
        if findings:
            sanitization_notes.append(f"🔒 Masked {len(findings)} sensitive item(s) prior to queuing.")

    results_summary = []

    # 1. Try Buffer Adapter (LinkedIn, X, Threads)
    if buffer_adapter.is_configured():
        res = buffer_adapter.queue_social_post(
            text=processed_text,
            platforms=target_platforms,
            media_urls=media_urls,
            schedule_time=schedule_time,
        )
        if res.get("success"):
            results_summary.append(
                f"✅ Queued to Buffer for {target_platforms} ({res.get('queued_profiles_count')} profile(s))."
            )
        else:
            results_summary.append(f"⚠️ Buffer notice: {res.get('error')}")

    # 2. Try Reddit Adapter
    if any(p.lower() == "reddit" or p.lower().startswith("reddit:") for p in target_platforms):
        res = reddit_adapter.queue_social_post(
            text=processed_text,
            platforms=target_platforms,
            title=title,
        )
        if res.get("success"):
            results_summary.append(f"✅ Published to Reddit r/{res.get('subreddit')}: {res.get('url')}")
        else:
            results_summary.append(f"⚠️ Reddit notice: {res.get('error')}")

    # 3. Try Webhook Adapter
    if webhook_adapter.is_configured():
        res = webhook_adapter.queue_social_post(
            text=processed_text,
            platforms=target_platforms,
            media_urls=media_urls,
            schedule_time=schedule_time,
        )
        if res.get("success"):
            results_summary.append("✅ Dispatched post event to configured Webhook / n8n pipeline.")
        else:
            results_summary.append(f"⚠️ Webhook notice: {res.get('error')}")

    # 4. Fallback if no provider configured
    has_provider = buffer_adapter.is_configured() or reddit_adapter.is_configured() or webhook_adapter.is_configured()
    if not has_provider:
        results_summary.append(
            "ℹ️ No external provider configured in `.env` (BUFFER_ACCESS_TOKEN, REDDIT_CLIENT_ID, or OMNIPRESS_WEBHOOK_URL).\n"
            "The post was formatted, de-identified, and is ready for manual copy:\n\n"
            f"```text\n{processed_text}\n```"
        )

    if sanitization_notes:
        results_summary.extend(sanitization_notes)

    return "\n".join(results_summary)


@mcp.tool()
def omnipress_inspect_content(text: str) -> str:
    """
    Scans any draft text for sensitive judicial lawsuit numbers, tax IDs (CPF/CNPJ),
    emails, or PII that must not be published publicly.
    """
    findings = inspect_sensitive_data(text)
    if not findings:
        return "✅ Content is clean! No sensitive lawsuit numbers, tax IDs, or PII detected."

    lines = [f"⚠️ Found {len(findings)} sensitive item(s) that should be anonymized:"]
    for item in findings:
        lines.append(f"  - [{item['type'].upper()}]: `{item['match']}`")
    return "\n".join(lines)


@mcp.tool()
def omnipress_list_recent(limit: int = 5) -> str:
    """
    Lists recent archived articles saved by OmniPress.
    """
    articles = markdown_adapter.list_recent(limit=limit)
    if not articles:
        return "No articles found in the archive directory."

    lines = [f"📚 Recent Articles ({len(articles)}):"]
    for a in articles:
        lines.append(f"- **{a['name']}** ({a['size_bytes']} bytes) — Modified: {a['modified']}")
    return "\n".join(lines)


def main():
    mcp.run()


if __name__ == "__main__":
    main()
