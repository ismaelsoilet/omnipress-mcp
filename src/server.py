"""OmniPress FastMCP Server - Exposes agentic publishing tools to Antigravity."""

import os
import sys
from pathlib import Path
from typing import List, Optional
# Ensure project root is in sys.path when executed directly
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Optional environment loading
try:
    from dotenv import load_dotenv
    load_dotenv(PROJECT_ROOT / ".env")
    load_dotenv()
except ImportError:
    pass

from src.adapters.markdown_adapter import MarkdownArchiveAdapter
from src.adapters.buffer_adapter import BufferPublisherAdapter
from src.adapters.webhook_adapter import WebhookPublisherAdapter
from src.adapters.reddit_adapter import RedditPublisherAdapter
from src.utils.sanitizer import sanitize_text, inspect_sensitive_data

# Initialize FastMCP Server with graceful fallback
try:
    from mcp.server.fastmcp import FastMCP
    mcp = FastMCP("OmniPress")
except ImportError:
    class FastMCP:
        def __init__(self, name: str):
            self.name = name
            self.tools = {}

        def tool(self, name: Optional[str] = None, description: Optional[str] = None):
            def decorator(func):
                tool_name = name or func.__name__
                self.tools[tool_name] = func
                return func
            return decorator

        def run(self):
            pass

    mcp = FastMCP("OmniPress")

# Initialize Adapters
markdown_adapter = MarkdownArchiveAdapter()
buffer_adapter = BufferPublisherAdapter()
webhook_adapter = WebhookPublisherAdapter()
reddit_adapter = RedditPublisherAdapter()


# MCP Tool Annotations for 2026 Protocol & TDQS Standards
MCP_TOOL_ANNOTATIONS = {
    "omnipress_publish_article": {
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": False,
    },
    "omnipress_queue_post": {
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": True,
    },
    "omnipress_inspect_content": {
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
    "omnipress_list_articles": {
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
    "omnipress_list_recent": {
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
}


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
    with YAML frontmatter (for Substack, Jusbrasil, Medium, or static blog) and optional event dispatch.

    Use when:
    - Archiving a completed markdown article with structured frontmatter metadata.
    - Publishing long-form thought leadership, legal tech, or tax analysis articles.
    - Ensuring content is checked and de-identified against CNJ court process numbers, CPFs, CNPJs, and personal emails before persistence.

    Do NOT use when:
    - Queuing short social media updates or micro-posts (use omnipress_queue_post instead).
    - Only checking for sensitive PII without writing files (use omnipress_inspect_content instead).

    Returns:
    - Formatted confirmation with filename, full storage path, category/tags, and detailed log of any sanitized privacy items.
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
    Queues a post, thread segment, or social announcement to distribution channels
    (LinkedIn, X/Twitter, Threads via Buffer, or Reddit) in draft/review mode.

    Use when:
    - Scheduling or queuing social media posts for human review or automated publishing.
    - Distributing snippets, summaries, or threads derived from long-form articles.
    - Targeting specific platforms such as LinkedIn, Threads, X, or a Reddit subreddit.

    Do NOT use when:
    - Storing long-form articles with frontmatter locally (use omnipress_publish_article instead).
    - Running a non-publishing privacy check (use omnipress_inspect_content instead).

    Returns:
    - Dispatch status report indicating successful queuing across configured providers (Buffer, Reddit, Webhook) or formatted draft fallback with sanitization notices.
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
    Pre-flight compliance scan that analyzes draft content for Brazilian lawsuit numbers (CNJ),
    tax IDs (CPF/CNPJ), personal emails, and phone numbers without modifying or publishing content.

    Use when:
    - Auditing draft text for LGPD compliance, judicial confidentiality (segredo de justiça), or privacy leaks before publishing.
    - Verifying if content requires anonymization or de-identification.

    Do NOT use when:
    - Saving the article to disk (use omnipress_publish_article instead).
    - Queuing social posts (use omnipress_queue_post instead).

    Returns:
    - Summary report stating whether the text is clean, or a detailed itemized list of detected sensitive matches with their classification types.
    """
    findings = inspect_sensitive_data(text)
    if not findings:
        return "✅ Content is clean! No sensitive lawsuit numbers, tax IDs, or PII detected."

    lines = [f"⚠️ Found {len(findings)} sensitive item(s) that should be anonymized:"]
    for item in findings:
        lines.append(f"  - [{item['type'].upper()}]: `{item['match']}`")
    return "\n".join(lines)


@mcp.tool()
def omnipress_list_articles(limit: int = 5) -> str:
    """
    Retrieves metadata of recently archived long-form articles from the local repository directory.

    Use when:
    - Discovering existing articles, file paths, and modification dates.
    - Verifying recently published drafts or checking past article slugs.

    Do NOT use when:
    - Inspecting text content for privacy leaks (use omnipress_inspect_content instead).
    - Publishing new content (use omnipress_publish_article instead).

    Returns:
    - Formatted list of recent articles including filename, file size in bytes, and ISO-8601 modification timestamp.
    """
    articles = markdown_adapter.list_recent(limit=limit)
    if not articles:
        return "No articles found in the archive directory."

    lines = [f"📚 Recent Articles ({len(articles)}):"]
    for a in articles:
        lines.append(f"- **{a['name']}** ({a['size_bytes']} bytes) — Modified: {a['modified']}")
    return "\n".join(lines)


@mcp.tool()
def omnipress_list_recent(limit: int = 5) -> str:
    """
    Backward-compatible alias for omnipress_list_articles.
    Retrieves metadata of recently archived long-form articles from the local repository directory.
    """
    return omnipress_list_articles(limit=limit)


def main():
    mcp.run()


if __name__ == "__main__":
    main()
