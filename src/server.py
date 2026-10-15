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
from src.adapters.instagram_adapter import InstagramGraphAdapter
from src.adapters.devto_adapter import DevToPublisherAdapter
from src.adapters.ghost_adapter import GhostPublisherAdapter
from src.core.channel_manager import ChannelManager
from src.engine.carousel_builder import CarouselBuilder
from src.utils.sanitizer import sanitize_text, inspect_sensitive_data

# Initialize FastMCP Server / MCPServer with graceful fallback
try:
    from mcp.server.mcpserver import MCPServer as FastMCP
    mcp = FastMCP("OmniPress")
except (ImportError, ModuleNotFoundError):
    try:
        from mcp.server.fastmcp import FastMCP
        mcp = FastMCP("OmniPress")
    except (ImportError, ModuleNotFoundError):
        class FastMCP:
            def __init__(self, name: str):
                self.name = name
                self.tools = {}

            def tool(self, name: Optional[str] = None, description: Optional[str] = None, annotations: Optional[Any] = None, **kwargs):
                def decorator(func):
                    tool_name = name or func.__name__
                    self.tools[tool_name] = func
                    return func
                return decorator

            def run(self, *args, **kwargs):
                pass

        mcp = FastMCP("OmniPress")

# Register /health endpoint for Docker container and Coolify healthchecks
if hasattr(mcp, "custom_route"):
    try:
        from starlette.requests import Request
        from starlette.responses import JSONResponse

        @mcp.custom_route("/health", methods=["GET"])
        async def health_check(request: Request) -> JSONResponse:
            return JSONResponse({
                "status": "healthy",
                "service": "omnipress-mcp",
                "version": "0.1.0",
            })
    except (ImportError, Exception):
        pass


# Initialize Core Managers & Adapters
channel_manager = ChannelManager()
carousel_builder = CarouselBuilder(channel_manager)
markdown_adapter = MarkdownArchiveAdapter()
buffer_adapter = BufferPublisherAdapter()
webhook_adapter = WebhookPublisherAdapter()
reddit_adapter = RedditPublisherAdapter()
youtube_adapter = YouTubeStagingAdapter()
instagram_adapter = InstagramGraphAdapter()
devto_adapter = DevToPublisherAdapter()
ghost_adapter = GhostPublisherAdapter()


# MCP Tool Annotations for 2026 Protocol & TDQS Standards
MCP_TOOL_ANNOTATIONS = {
    "omnipress_list_channels": {
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
    "omnipress_get_channel": {
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
    "omnipress_create_channel": {
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": False,
    },
    "omnipress_build_carousel": {
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
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
    "omnipress_brainstorm_channel": {
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
    "omnipress_generate_speech": {
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": False,
    },
    "omnipress_render_dark_video": {
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": False,
    },
}


def get_tool_annotations(name: str):
    ann = MCP_TOOL_ANNOTATIONS.get(name)
    if not ann:
        return None
    try:
        from mcp.types import ToolAnnotations
        return ToolAnnotations(**ann)
    except Exception:
        return ann


@mcp.tool(annotations=get_tool_annotations("omnipress_publish_article"))
def omnipress_publish_article(
    title: str,
    content_markdown: str,
    category: str = "technology",
    tags: Optional[List[str]] = None,
    author: Optional[str] = None,
    channel_slug: Optional[str] = None,
    target_platform: str = "markdown",
    canonical_url: Optional[str] = None,
    published: bool = False,
    force_duplicate: bool = False,
    sanitize: bool = True,
) -> str:
    """
    Saves and syndicates long-form articles to the local Markdown archive and/or online publication platforms
    (Dev.to, Ghost CMS) with YAML frontmatter, automated privacy sanitization, and anti-duplicate ledger (Rule 09).

    Use when:
    - Archiving a completed markdown article with structured frontmatter metadata.
    - Publishing or drafting long-form thought leadership, legal tech, or engineering articles to Dev.to or Ghost.
    - Ensuring content is checked and de-identified against CNJ court process numbers, CPFs, CNPJs, personal emails, and API keys before publication.

    Do NOT use when:
    - Queuing short social media updates or micro-posts (use omnipress_queue_post instead).
    - Only checking for sensitive PII without writing or publishing files (use omnipress_inspect_content instead).

    Returns:
    - Formatted confirmation with local storage path, online publication status/URL, and audit log of any sanitized items.
    """
    sanitization_notes = []
    processed_content = content_markdown

    if sanitize:
        processed_content, findings = sanitize_text(content_markdown)
        if findings:
            sanitization_notes.append(f"🔒 Anonymized {len(findings)} sensitive item(s):")
            for f in findings:
                sanitization_notes.append(f"  - {f['type']}: {f['match']}")

    # 1. Local archive is always preserved as single source of truth
    result = markdown_adapter.save_article(
        title=title,
        content_markdown=processed_content,
        category=category,
        tags=tags or [],
        author=author,
        channel_slug=channel_slug,
    )

    # If webhook configured, notify pipeline of new article
    if webhook_adapter.is_configured():
        webhook_adapter.dispatch_event("article_saved", result)

    ch_label = f" | Channel: `{channel_slug}`" if channel_slug else ""
    output = [
        f"✅ Article archived locally: **{result['filename']}**",
        f"📁 Path: `{result['filepath']}`",
        f"🏷️ Category: `{category}` | Tags: {tags or []}{ch_label}",
    ]

    # 2. Multi-platform syndication (Dev.to, Ghost CMS)
    raw_targets = [p.lower().strip() for p in (target_platform or "markdown").split(",") if p.strip()]
    if "all" in raw_targets:
        targets = ["devto", "ghost"]
    else:
        targets = raw_targets

    if "devto" in targets:
        dev_res = devto_adapter.publish_article(
            title=title,
            content_markdown=processed_content,
            category=category,
            tags=tags,
            author=author,
            canonical_url=canonical_url,
            published=published,
            force_duplicate=force_duplicate,
        )
        if dev_res.get("success"):
            output.append(f"🌐 Dev.to ({dev_res.get('status')}): {dev_res.get('url')}")
        else:
            output.append(f"⚠️ Dev.to Notice: {dev_res.get('error')}")

    if "ghost" in targets:
        ghost_res = ghost_adapter.publish_article(
            title=title,
            content_markdown=processed_content,
            category=category,
            tags=tags,
            author=author,
            canonical_url=canonical_url,
            published=published,
            force_duplicate=force_duplicate,
        )
        if ghost_res.get("success"):
            output.append(f"👻 Ghost CMS ({ghost_res.get('status')}): {ghost_res.get('url')}")
        else:
            output.append(f"⚠️ Ghost CMS Notice: {ghost_res.get('error')}")

    if sanitization_notes:
        output.append("\n" + "\n".join(sanitization_notes))

    return "\n".join(output)


@mcp.tool(annotations=get_tool_annotations("omnipress_queue_post"))
def omnipress_queue_post(
    text: str,
    platforms: Optional[List[str]] = None,
    title: Optional[str] = None,
    media_urls: Optional[List[str]] = None,
    schedule_time: Optional[str] = None,
    channel_slug: Optional[str] = None,
    mode: Optional[str] = None,
    allow_test: bool = False,
    force_duplicate: bool = False,
    sanitize: bool = True,
) -> str:
    """
    Queues a post, thread segment, or social announcement to distribution channels
    (LinkedIn, X/Twitter, Threads via Buffer, or Reddit) in draft/review mode.
    Supports multi-channel dispatch via channel_slug.
    Protected by PublishingShield pre-flight validation and anti-duplicate ledger (Rule 09).

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

    # 1. Try Buffer Adapter (LinkedIn, X, Threads, Instagram)
    if buffer_adapter.is_configured():
        res = buffer_adapter.queue_social_post(
            text=processed_text,
            platforms=target_platforms,
            media_urls=media_urls,
            schedule_time=schedule_time,
            channel_slug=channel_slug,
            mode=mode,
            allow_test=allow_test,
            force_duplicate=force_duplicate,
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


@mcp.tool(annotations=get_tool_annotations("omnipress_inspect_content"))
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


@mcp.tool(annotations=get_tool_annotations("omnipress_list_articles"))
def omnipress_list_articles(limit: int = 5, channel_slug: Optional[str] = None) -> str:
    """
    Retrieves metadata of recently archived long-form articles from the repository.
    Can be scoped to a specific channel via channel_slug.

    Use when:
    - Discovering existing articles, file paths, and modification dates.
    - Verifying recently published drafts or checking past article slugs for a specific channel.

    Do NOT use when:
    - Inspecting text content for privacy leaks (use omnipress_inspect_content instead).
    - Publishing new content (use omnipress_publish_article instead).

    Returns:
    - Formatted list of recent articles including filename, file size in bytes, and ISO-8601 modification timestamp.
    """
    articles = markdown_adapter.list_recent(limit=limit, channel_slug=channel_slug)
    if not articles:
        target = f"in channel `{channel_slug}`" if channel_slug else "in the archive directory"
        return f"No articles found {target}."

    scope = f" for Channel `{channel_slug}`" if channel_slug else ""
    lines = [f"📚 Recent Articles{scope} ({len(articles)}):"]
    for a in articles:
        lines.append(f"- **{a['name']}** ({a['size_bytes']} bytes) — Modified: {a['modified']}")
    return "\n".join(lines)


@mcp.tool(annotations=get_tool_annotations("omnipress_list_channels"))
def omnipress_list_channels(include_templates: bool = False) -> str:
    """
    Lists all configured content channels in the OmniPress multi-channel architecture.

    Use when:
    - Discovering available channels and their active configurations.
    - Inspecting channel slugs, handles, categories, and storage paths.

    Do NOT use when:
    - Querying individual channel brand details (use omnipress_get_channel instead).

    Returns:
    - Formatted list of channels with slug, handle, category, and workspace path.
    """
    channels = channel_manager.list_channels(include_templates=include_templates)
    if not channels:
        return "ℹ️ No channels configured yet. Use `omnipress_create_channel` to create one."

    active_slug = channel_manager.get_active_channel_slug()
    lines = [f"📡 OmniPress Channels ({len(channels)}) — Active: `{active_slug}`:\n"]
    for ch in channels:
        slug = ch.get("slug", "unknown")
        name = ch.get("name", slug)
        handle = ch.get("branding", {}).get("handle", "N/A")
        cat = ch.get("category", "general")
        is_active = " 🟢 (ACTIVE)" if slug == active_slug else ""
        lines.append(f"- **{name}** (`{slug}`){is_active}")
        lines.append(f"  • Handle: `{handle}` | Categoria: `{cat}`")
        lines.append(f"  • Workspace: `{ch.get('path', '')}`")
    return "\n".join(lines)


@mcp.tool(annotations=get_tool_annotations("omnipress_get_channel"))
def omnipress_get_channel(channel_slug: str) -> str:
    """
    Retrieves full configuration and brand identity for a specific channel.

    Use when:
    - Inspecting brand colors, typography, handles, and Buffer channel IDs.
    - Verifying channel settings before generating carousels or dispatching posts.

    Do NOT use when:
    - Discovering all channels (use omnipress_list_channels instead).

    Returns:
    - Formatted JSON summary of channel parameters and status.
    """
    import json
    channel = channel_manager.get_channel(channel_slug)
    if not channel:
        return f"⚠️ Channel `{channel_slug}` not found. Use `omnipress_list_channels` to see available channels."
    return json.dumps(channel, indent=2, ensure_ascii=False)


@mcp.tool(annotations=get_tool_annotations("omnipress_create_channel"))
def omnipress_create_channel(
    slug: str,
    name: str,
    handle: str,
    category: str = "general",
    description: str = "",
    primary_color: str = "#D4AF37",
    buffer_channel_id: str = "",
) -> str:
    """
    Scaffolds a new isolated channel workspace with dedicated articles, media, and scripts directories.

    Use when:
    - Creating a new content channel (e.g. tech, finance, legal, dark channel).
    - Setting up a distinct brand identity with its own handle and Buffer channel ID.

    Do NOT use when:
    - Querying or modifying an existing channel configuration.

    Returns:
    - Confirmation with created directories and channel configuration path.
    """
    config = channel_manager.create_channel(
        slug=slug,
        name=name,
        handle=handle,
        category=category,
        description=description,
        primary_color=primary_color,
        buffer_channel_id=buffer_channel_id,
    )
    return (
        f"✅ Channel **{name}** (`{config['slug']}`) created successfully!\n"
        f"📁 Workspace: `{config['path']}`\n"
        f"🏷️ Handle: `{config['branding']['handle']}` | Categoria: `{category}`\n"
        f"⚙️ Config: `{config['path']}/channel.json`\n"
        f"Diretórios prontos: `articles/`, `media/carousels/`, `media/stories/`, `media/raw/`, `scripts/`"
    )


@mcp.tool(annotations=get_tool_annotations("omnipress_build_carousel"))
def omnipress_build_carousel(
    channel_slug: str,
    post_slug: str,
    slides_json: str,
    aspect_ratio: str = "3:4",
) -> str:
    """
    Renders a branded, high-contrast Instagram carousel deck for a channel using CarouselBuilder.
    Dynamically applies the channel's brand colors, fonts, badge, and handle with pixel-perfect wrapping.

    Use when:
    - Generating production-ready 3:4 portrait carousel slides from an array of slide definitions.
    - Ensuring zero text clipping and safe unicode glyphs tailored to the channel's identity.

    Do NOT use when:
    - Publishing directly to social channels without inspecting slides first.

    Returns:
    - Summary with paths of all rendered slides.
    """
    import json
    try:
        slides_data = json.loads(slides_json)
    except Exception as e:
        return f"⚠️ Invalid slides_json: {e}"

    if not isinstance(slides_data, list) or not slides_data:
        return "⚠️ slides_json must be a non-empty JSON list of slide objects."

    generated = carousel_builder.build_carousel(
        channel_slug=channel_slug,
        post_slug=post_slug,
        slides_data=slides_data,
        aspect_ratio=aspect_ratio,
    )

    lines = [f"✅ Carousel generated for channel `{channel_slug}` ({len(generated)} slides):"]
    for path in generated:
        lines.append(f"- 🖼️ `{path}`")
    return "\n".join(lines)


@mcp.tool(annotations=get_tool_annotations("omnipress_list_recent"))
def omnipress_list_recent(limit: int = 5) -> str:
    """
    Backward-compatible alias for omnipress_list_articles.
    Retrieves metadata of recently archived long-form articles from the local repository directory.

    Use when:
    - Querying recent articles using legacy integrations or scripts expecting omnipress_list_recent.
    - Inspecting recently published content drafts and titles.

    Do NOT use when:
    - Writing new agent workflows (prefer the canonical omnipress_list_articles instead).
    - Querying configured channels (use omnipress_list_channels instead).

    Returns:
    - Formatted list of recently saved articles with filenames, sizes, and modification dates.
    """
    return omnipress_list_articles(limit=limit)


@mcp.tool(annotations=get_tool_annotations("omnipress_prepare_dark_script"))
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

    Do NOT use when:
    - You want to render final audio or video files directly (use omnipress_generate_speech or omnipress_render_dark_video instead).
    - Publishing or queuing finished posts to social networks (use omnipress_queue_media_post or omnipress_queue_post instead).

    Returns:
    - JSON string containing audioDirection, shortScript, visualScenePrompts, instagramCarousel, and youtubeMetadata.
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


@mcp.tool(annotations=get_tool_annotations("omnipress_queue_media_post"))
def omnipress_queue_media_post(
    caption: str,
    platforms: List[str],
    title: Optional[str] = None,
    media_urls: Optional[List[str]] = None,
    media_type: str = "image",
    tags: Optional[List[str]] = None,
    thumbnail_url: Optional[str] = None,
    schedule_time: Optional[str] = None,
    channel_slug: Optional[str] = None,
    mode: Optional[str] = None,
    allow_test: bool = False,
    force_duplicate: bool = False,
    sanitize: bool = True,
) -> str:
    """
    Queues rich media content (Images, Carousels, Video Reels, YouTube Shorts) to Instagram,
    YouTube, X/Twitter, and Threads with platform-specific formatting and asset staging.
    Protected by PublishingShield pre-flight validation and anti-duplicate ledger (Rule 09).

    Use when:
    - Publishing or staging rich visual media (Instagram single image, carousel, video reel, or YouTube Short).
    - Dispatching media campaigns to social networks with automated privacy masking.

    Do NOT use when:
    - Publishing text-only long-form markdown articles (use omnipress_publish_article instead).
    - Queuing standard text-only social posts or threads without media files (use omnipress_queue_post instead).

    Returns:
    - Status message summarizing publishing, staging, or queue results across all target platforms.
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
        if instagram_adapter.is_configured():
            res = instagram_adapter.queue_social_post(
                text=processed_caption,
                platforms=["instagram"],
                media_urls=media_urls,
                schedule_time=schedule_time,
                channel_slug=channel_slug,
                mode=mode,
                allow_test=allow_test,
                force_duplicate=force_duplicate,
            )
            if res.get("success"):
                results.append(f"✅ Published directly to Instagram via Meta Graph API: Post ID {res.get('post_id')} ({res.get('permalink')})")
            else:
                results.append(f"⚠️ Instagram Graph API notice: {res.get('error')}")
        elif buffer_adapter.is_configured():
            res = buffer_adapter.queue_social_post(
                text=processed_caption,
                platforms=["instagram"],
                media_urls=media_urls,
                schedule_time=schedule_time,
                channel_slug=channel_slug,
                mode=mode,
                allow_test=allow_test,
                force_duplicate=force_duplicate,
            )
            if res.get("success"):
                results.append(f"✅ Queued to Instagram via Buffer: {res.get('message', 'Draft queued')}")
            else:
                results.append(f"⚠️ Buffer Instagram notice: {res.get('error')}")
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
        if buffer_adapter.is_configured():
            res = buffer_adapter.queue_social_post(
                text=processed_caption,
                platforms=["x"],
                media_urls=media_urls,
                schedule_time=schedule_time,
                channel_slug=channel_slug,
                mode=mode,
                allow_test=allow_test,
                force_duplicate=force_duplicate,
            )
            if res.get("success"):
                results.append(f"✅ Queued to X via Buffer: {res.get('message', 'Draft queued')}")
            else:
                results.append(f"⚠️ Buffer X notice: {res.get('error')}")
        else:
            results.append(f"🐦 X (Twitter) Content Formatted:\n```text\n{processed_caption}\n```")

    if sanitization_notes:
        results.append("\n" + "\n".join(sanitization_notes))

    return "\n\n".join(results)


@mcp.tool(annotations=get_tool_annotations("omnipress_brainstorm_channel"))
def omnipress_brainstorm_channel(
    niche: str = "historia",
    tone: str = "mystery",
    target_audience: str = "geral",
    language: str = "pt-BR",
) -> str:
    """
    Generates high-retention channel concepts, psychological CTR names, 3 core content pillars,
    and a backlog of 10 viral video topics with tested 0-3s scroll-stop hooks for dark or niche channels.

    Use when:
    - Brainstorming a new content channel on YouTube, Instagram, TikTok, or X.
    - Creating viral backlog topics with tested 0-3s curiosity loops.

    Do NOT use when:
    - Scaffolding the channel workspace directory on disk (use omnipress_create_channel instead).
    - Writing full production scripts for an episode (use omnipress_prepare_dark_script instead).

    Returns:
    - JSON string with channel concepts, psychological CTR angles, and 10 viral video topics with hooks.
    """
    import json
    clean_niche = niche.lower().strip()
    if any(k in clean_niche for k in ["hist", "antig", "passad", "guerra"]):
        concepts = [
            {
                "name": "Dossiê Histórico",
                "handle": "@dossiehistorico",
                "tagline": "O que os livros oficiais apagaram do passado.",
                "ctrAngle": "Gatilho de segredo de estado e conspiração desclassificada.",
                "visualPalette": ["#0A0C10", "#D4AF37", "#8B0000"]
            },
            {
                "name": "Crônicas Ocultas",
                "handle": "@cronicasocultas.oficial",
                "tagline": "Fatos reais que parecem pesadelo ou ficção.",
                "ctrAngle": "Gatilho de bizarrice e choque factual.",
                "visualPalette": ["#070809", "#C0C0C0", "#4A0E17"]
            },
            {
                "name": "O Passado Redigido",
                "handle": "@passadoredigido",
                "tagline": "Documentos confidenciais que você nunca deveria ler.",
                "ctrAngle": "Gatilho de censura e conhecimento proibido.",
                "visualPalette": ["#111215", "#E63946", "#F1FAEE"]
            },
            {
                "name": "Sombras da História",
                "handle": "@sombrasdahistoria",
                "tagline": "As decisões mais sombrias que moldaram o mundo moderno.",
                "ctrAngle": "Gatilho de poder, decisões secretas de bastidores.",
                "visualPalette": ["#050505", "#DAA520", "#1C2541"]
            },
            {
                "name": "Arquivos do Tempo",
                "handle": "@arquivosdotempo",
                "tagline": "Investigação profunda das maiores anomalias da humanidade.",
                "ctrAngle": "Gatilho investigativo e documental solene.",
                "visualPalette": ["#0D1117", "#C9D1D9", "#58A6FF"]
            }
        ]
        pillars = [
            {"pillar": "1. Documentos Desclassificados & Conspirações Reais", "description": "Arquivos de inteligência e operações militares secretas."},
            {"pillar": "2. Batalhas Bizarras & O Pior Erro Militar", "description": "Exércitos que lutaram contra si mesmos e blefes inacreditáveis."},
            {"pillar": "3. Anomalias & Mistérios Não Resolvidos", "description": "Surtos coletivos e artefatos arqueológicos fora do tempo."}
        ]
        viral_topics = [
            {"id": 1, "title": "O Exército Fantasma da Segunda Guerra", "hook_0_3s": "Você sabia que os EUA venceram uma batalha usando tanques de borracha e caixas de som?", "curiosityLoop": "Cenografia de Hollywood enganou 20 divisões alemãs.", "format": "Shorts / Reels (9:16)"},
            {"id": 2, "title": "A Dança de São Vito de 1518", "hook_0_3s": "Em julho de 1518, uma mulher começou a dançar na rua. Em 30 dias, 400 pessoas dançavam sem parar até a morte.", "curiosityLoop": "Histeria coletiva que médicos tentaram conter com orquestra ao vivo.", "format": "Shorts / Reels (9:16)"},
            {"id": 3, "title": "A Batalha de Karánsebes", "hook_0_3s": "Um exército de 100 mil homens perdeu 10 mil soldados sem nenhum inimigo por perto.", "curiosityLoop": "Briga por aguardente gerou fogo amigo generalizado.", "format": "Shorts / Reels (9:16)"},
            {"id": 4, "title": "O Submarino B-59 e o Fim do Mundo", "hook_0_3s": "Em 1962, a Terceira Guerra Mundial foi evitada pelo voto solitário de um único oficial.", "curiosityLoop": "Recusa de lançamento de torpedo nuclear soviético a 50 metros de profundidade.", "format": "Shorts / Reels (9:16)"},
            {"id": 5, "title": "O Mecanismo de Anticítera", "hook_0_3s": "Cientistas encontraram um computador analógico de 2.000 anos no fundo do mar.", "curiosityLoop": "Engrenagens de bronze que calculavam eclipses desafiando a história.", "format": "Shorts / Reels (9:16)"}
        ]
    else:
        concepts = [
            {"name": f"{clean_niche.capitalize()} Revelado", "handle": f"@{clean_niche}.revelado", "tagline": f"Os bastidores de {clean_niche}."}
        ]
        pillars = [{"pillar": "1. Bastidores", "description": "Casos reais e revelações."}]
        viral_topics = [{"id": 1, "title": f"O grande segredo sobre {clean_niche}", "hook_0_3s": "A maioria das pessoas ignora isso...", "format": "Shorts (9:16)"}]

    bundle = {
        "niche": clean_niche,
        "tone": tone,
        "targetAudience": target_audience,
        "channelConcepts": concepts,
        "contentPillars": pillars,
        "viralTopicsBacklog": viral_topics,
        "productionSpecs": {
            "audioVoice": "pt-BR-AntonioNeural (Edge-TTS gravado com tom documental solene)",
            "audioBgm": "Dark Ambient / Drone com sub-graves em 80-90 BPM",
            "visualAiPrompts": "Cinematic 8k, dark moody atmosphere, historical archival textures, volumetric amber rim lighting, 9:16 aspect ratio",
            "recommendedPacing": "Cortes visuais a cada 3 a 5 segundos, pausas dramáticas na locução"
        }
    }
    return json.dumps(bundle, indent=2, ensure_ascii=False)


@mcp.tool(annotations=get_tool_annotations("omnipress_generate_speech"))
async def omnipress_generate_speech(
    text: str,
    voice: str = "pt-BR-AntonioNeural",
    output_filename: Optional[str] = None,
) -> str:
    """
    Synthesizes natural, high-definition neural narration audio (Edge-TTS) for Dark Channels, Reels, Shorts.

    Use when:
    - Converting script narrations into immersive MP3 voice files.

    Do NOT use when:
    - Full video rendering is required (use omnipress_render_dark_video instead).
    - Text-only content archiving without voiceover generation.

    Returns:
    - JSON string with audio file path, file size in bytes, voice identifier, and operation status.
    """
    import json
    import time
    from pathlib import Path
    from scripts.generate_dark_media import generate_tts_audio

    filename = output_filename or f"speech-{int(time.time()*1000)}.mp3"
    out_path = PROJECT_ROOT / "media" / "output" / filename
    out_path.parent.mkdir(parents=True, exist_ok=True)

    await generate_tts_audio(text, out_path, voice=voice)
    result = {
        "success": True,
        "audio_path": str(out_path.resolve()),
        "audio_size_bytes": out_path.stat().st_size if out_path.exists() else 0,
        "voice": voice
    }
    return json.dumps(result, indent=2, ensure_ascii=False)


@mcp.tool(annotations=get_tool_annotations("omnipress_render_dark_video"))
async def omnipress_render_dark_video(
    text: Optional[str] = None,
    audio_path: Optional[str] = None,
    image_paths: Optional[List[str]] = None,
    output_filename: Optional[str] = None,
    aspect_ratio: str = "9:16",
    voice: str = "pt-BR-AntonioNeural",
) -> str:
    """
    Renders an MP4 video (vertical 9:16 or 16:9) by combining neural audio narration with images using ffmpeg.

    Use when:
    - Producing ready-to-publish MP4 video files from script narrations and scene images.

    Do NOT use when:
    - Only voiceover audio is required (use omnipress_generate_speech instead).
    - Generating static image carousels without video animation (use omnipress_build_carousel instead).

    Returns:
    - JSON string containing audio path, rendered video path, aspect ratio, voice model, and status.
    """
    import json
    import time
    import shutil
    from pathlib import Path
    from scripts.generate_dark_media import generate_tts_audio, render_video_with_ffmpeg

    filename = output_filename or f"video-{int(time.time()*1000)}.mp4"
    out_path = PROJECT_ROOT / "media" / "output" / filename
    out_path.parent.mkdir(parents=True, exist_ok=True)
    audio_file = out_path.with_suffix(".mp3")

    if audio_path and Path(audio_path).exists():
        audio_file = Path(audio_path).resolve()
    elif text:
        await generate_tts_audio(text, audio_file, voice=voice)
    else:
        return json.dumps({"success": False, "error": "Forneça text ou audio_path válido."})

    ffmpeg_available = bool(shutil.which("ffmpeg"))
    video_path = None
    if ffmpeg_available:
        valid_images = [Path(p).resolve() for p in (image_paths or []) if Path(p).exists()]
        rendered = render_video_with_ffmpeg(audio_file, valid_images, out_path, aspect_ratio=aspect_ratio)
        if rendered.suffix == ".mp4" and rendered.exists():
            video_path = str(rendered.resolve())

    result = {
        "success": True,
        "audio_path": str(audio_file.resolve()),
        "video_path": video_path,
        "ffmpeg_available": ffmpeg_available,
        "aspect_ratio": aspect_ratio,
        "voice": voice
    }
    return json.dumps(result, indent=2, ensure_ascii=False)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="OmniPress MCP Server")
    parser.add_argument("--http", type=int, default=None, help="Run HTTP/SSE server on specified port")
    parser.add_argument("--sse", type=int, default=None, help="Run SSE transport on specified port")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host interface (default: 0.0.0.0)")
    args, _ = parser.parse_known_args()

    port = args.http or args.sse
    if not port and os.environ.get("OMNIPRESS_MODE") == "http":
        try:
            port = int(os.environ.get("PORT", "3333"))
        except ValueError:
            port = 3333

    if port:
        print(f"🚀 Iniciando OmniPress MCP Server em http://{args.host}:{port} via transporte SSE...", file=sys.stderr)
        mcp.run(transport="sse", host=args.host, port=port)
    else:
        mcp.run()


if __name__ == "__main__":
    main()

