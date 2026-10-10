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
from src.adapters.youtube_adapter import YouTubeStagingAdapter
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
youtube_adapter = YouTubeStagingAdapter()


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
    "omnipress_prepare_dark_script": {
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
    "omnipress_queue_media_post": {
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": True,
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


@mcp.tool()
def omnipress_prepare_dark_script(
    topic: str,
    format: str = "all",
    tone: str = "mystery",
    target_audience: str = "geral",
) -> str:
    """
    Generates a high-retention viral dark channel script, scene-by-scene AI image prompts,
    voice narration specs (TTS), Instagram carousel/caption, X viral thread, and YouTube SEO metadata.

    Use when:
    - Creating a complete production bundle for dark channels across YouTube, Instagram, X (Twitter), and TikTok.
    - Generating scene-by-scene visual image prompts for AI generators.
    - Formatting YouTube SEO tags, descriptions with timestamps, and Instagram carousel copy.
    """
    import json
    clean_topic = topic.strip()
    bundle = {
        "topic": clean_topic,
        "tone": tone,
        "targetAudience": target_audience,
        "audioDirection": {
            "voice": "pt-BR-AntonioNeural (grave, pausado, tom documental investigativo)",
            "bgm": "Dark Ambient / Drone misterioso com sub-graves (80-90 BPM)",
            "pacing": "Pausas dramáticas a cada 5 segundos",
        },
        "shortScript": {
            "durationSeconds": 55,
            "hook_0_3s": f"Você NUNCA deveria saber sobre isso... mas a verdade sobre {clean_topic} finalmente veio à tona.",
            "retention_3_15s": "A maioria das pessoas acredita na versão que contam por aí. Mas se você analisar os registros confidenciais, algo perturbador não fecha.",
            "development_15_45s": "Nos bastidores, o que realmente aconteceu foi orquestrado em silêncio. Três anomalias foram apagadas dos livros: o sumiço dos relatórios originais, o isolamento dos envolvidos e o padrão que continua se repetindo hoje.",
            "climax_45_50s": "E a pergunta que ninguém quer responder é: quem realmente lucrou com o silêncio desse caso?",
            "cta_50_55s": "Comente sua teoria abaixo e se inscreva antes que derrubem este conteúdo.",
        },
        "visualScenePrompts": [
            {
                "scene": 1,
                "timecode": "00:00 - 00:03",
                "aiPrompt": "Cinematic 8k, dark moody atmosphere, mysterious silhouette holding classified dossier, dramatic volumetric lighting, 9:16 aspect ratio, ultra-detailed",
            },
            {
                "scene": 2,
                "timecode": "00:03 - 00:15",
                "aiPrompt": "Close-up macro of ancient classified parchment papers with redacted black marks, vintage magnifying glass, dark wooden archival desk, 9:16 aspect ratio, photorealistic",
            },
            {
                "scene": 3,
                "timecode": "00:15 - 00:30",
                "aiPrompt": "Epic wide angle of an underground vault or forgotten monolithic chamber, brutalist architecture, moody dark cinematography, 9:16 aspect ratio",
            },
            {
                "scene": 4,
                "timecode": "00:30 - 00:45",
                "aiPrompt": "Dramatic high contrast portrait of powerful shadowy figures around a dimly lit boardroom map, cinematic rim lighting, 9:16 aspect ratio",
            },
            {
                "scene": 5,
                "timecode": "00:45 - 00:55",
                "aiPrompt": "Surreal conceptual artwork of a clock ticking backwards inside a shattered hourglass, dark cosmic backdrop, cinematic illumination, 9:16 aspect ratio",
            },
        ],
        "instagramCarousel": {
            "slide1_cover": f"O que esconderam sobre: {clean_topic} ⚠️",
            "slide2_context": "Durante anos contaram a versão conveniente. Os documentos desclassificados mostram o oposto.",
            "slide7_cta": "Salve para não esquecer e siga a página para os próximos relatórios secretos.",
        },
        "youtubeMetadata": {
            "title": f"O Segredo Oculto Sobre {clean_topic} (O Que Apagaram da História)",
            "description": f"Investigação aprofundada revelando anomalias e documentos esquecidos sobre {clean_topic}.",
            "tags": [clean_topic, "misterio", "documentario dark", "canal dark", "curiosidades"],
        },
    }
    return json.dumps(bundle, indent=2, ensure_ascii=False)


@mcp.tool()
def omnipress_queue_media_post(
    caption: str,
    platforms: List[str],
    title: Optional[str] = None,
    media_urls: Optional[List[str]] = None,
    media_type: str = "image",
    tags: Optional[List[str]] = None,
    thumbnail_url: Optional[str] = None,
    schedule_time: Optional[str] = None,
    sanitize: bool = True,
) -> str:
    """
    Queues rich media content (Images, Carousels, Video Reels, YouTube Shorts) to Instagram,
    YouTube, X/Twitter, and Threads with platform-specific formatting and asset staging.
    """
    processed_caption = caption
    sanitization_notes = []

    if sanitize:
        processed_caption, findings = sanitize_text(caption)
        if findings:
            sanitization_notes.append(f"🔒 Masked {len(findings)} sensitive item(s).")

    results = []
    normalized = [p.lower().strip() for p in platforms]

    # Instagram
    if "instagram" in normalized or "ig" in normalized or "all" in normalized:
        if not media_urls:
            results.append("⚠️ Instagram Warning: Media is required for Instagram posts.")
        if buffer_adapter.is_configured() and buffer_adapter.instagram_profile_id:
            res = buffer_adapter.queue_social_post(
                processed_caption, ["instagram"], media_urls, schedule_time
            )
            results.append(f"✅ Queued to Instagram via Buffer: {res.get('buffer_response', 'Draft queued')}")
        else:
            results.append(f"📷 Instagram Draft Formatted:\n```text\n{processed_caption}\n```")

    # YouTube
    if "youtube" in normalized or "youtube_shorts" in normalized or "shorts" in normalized or "all" in normalized:
        is_short = "youtube_shorts" in normalized or "shorts" in normalized or media_type == "short"
        yt_res = youtube_adapter.stage_video(
            title=title or (processed_caption.split("\n")[0] if processed_caption else "Vídeo Dark"),
            description=processed_caption,
            tags=tags or [],
            is_short=is_short,
            media_urls=media_urls or [],
            thumbnail_url=thumbnail_url,
            schedule_time=schedule_time,
        )
        results.append(f"🎬 YouTube ({'Shorts' if is_short else 'Long-form'}) Staged at: `{yt_res['filepath']}`")

    # X / Twitter
    if "x" in normalized or "twitter" in normalized or "all" in normalized:
        if buffer_adapter.is_configured() and buffer_adapter.x_profile_id:
            res = buffer_adapter.queue_social_post(
                processed_caption, ["x"], media_urls, schedule_time
            )
            results.append(f"✅ Queued to X via Buffer: {res.get('buffer_response', 'Draft queued')}")
        else:
            results.append(f"🐦 X (Twitter) Content Formatted:\n```text\n{processed_caption}\n```")

    if sanitization_notes:
        results.append("\n" + "\n".join(sanitization_notes))

    return "\n\n".join(results)


def main():
    mcp.run()


if __name__ == "__main__":
    main()
