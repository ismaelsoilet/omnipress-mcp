"""OmniPress CLI - Interactive onboarding wizard, diagnostics, and management utility."""

import os
import sys
import argparse
from pathlib import Path
from typing import Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Optional dotenv
try:
    from dotenv import load_dotenv
    load_dotenv(PROJECT_ROOT / ".env")
except ImportError:
    pass

from src.utils.runtime_checker import format_doctor_report, get_runtime_capabilities
from src.core.publishing_shield import PublishingShield
from src.core.channel_manager import ChannelManager


def cmd_doctor(args: argparse.Namespace) -> int:
    """Runs system diagnostics on Node, ffmpeg, Python, and TTS."""
    print(format_doctor_report())
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    """Reports configured channels, active channel workspace, and ledger entries."""
    cm = ChannelManager()
    channels = cm.list_channels(include_templates=False)
    active_slug = os.getenv("OMNIPRESS_ACTIVE_CHANNEL", "default")

    print("============================================================")
    print("                 OmniPress MCP — System Status              ")
    print("============================================================")
    print(f"  Active Channel Workspace : {active_slug}")
    print(f"  Configured Channels Count: {len(channels)}")
    for ch in channels:
        marker = "👉 " if ch.get("slug") == active_slug else "   "
        ch_cat = ch.get("category") or ch.get("niche") or "general"
        ch_name = ch.get("name", ch.get("slug", "unknown"))
        print(f"  {marker}• [{ch.get('slug')}] {ch_name} (Category: {ch_cat})")

    ledger = PublishingShield.load_ledger()
    print("------------------------------------------------------------")
    print(f"  PublishingShield Ledger  : {len(ledger)} recorded publication(s)")
    if ledger:
        print("  Recent Publications (Last 5):")
        for entry in ledger[-5:]:
            ts = entry.get("timestamp", 0)
            ch_id = entry.get("channel_id", "unknown")
            preview = entry.get("text_preview", "")[:50]
            prov = entry.get("provider", "social")
            print(f"    - [{prov}] ({ch_id}): {preview}...")
    print("============================================================")
    return 0


def cmd_setup(args: argparse.Namespace) -> int:
    """Interactive onboarding wizard to configure .env credentials cleanly."""
    env_file = PROJECT_ROOT / ".env"
    example_file = PROJECT_ROOT / ".env.example"

    print("============================================================")
    print("           OmniPress MCP — Interactive Setup Wizard         ")
    print("============================================================")

    if not env_file.exists() and example_file.exists():
        print(f"ℹ️  Creating fresh .env from .env.example...")
        env_file.write_text(example_file.read_text(encoding="utf-8"), encoding="utf-8")

    current_env = {}
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                current_env[k.strip()] = v.strip()

    if getattr(args, "non_interactive", False):
        print("Non-interactive mode requested. Existing .env preserved.")
        return 0

    print("Configure your publishing platforms (Press Enter to keep current/blank):")

    # Buffer
    curr_buffer = current_env.get("BUFFER_API_KEY", "")
    mask_buffer = (curr_buffer[:4] + "..." + curr_buffer[-4:]) if len(curr_buffer) > 8 else curr_buffer
    buf_prompt = f"  Buffer API Key [{mask_buffer}]: "
    buf_input = input(buf_prompt).strip()
    if buf_input:
        current_env["BUFFER_API_KEY"] = buf_input

    # Dev.to
    curr_devto = current_env.get("DEVTO_API_KEY", "")
    mask_devto = (curr_devto[:4] + "..." + curr_devto[-4:]) if len(curr_devto) > 8 else curr_devto
    devto_prompt = f"  Dev.to API Key [{mask_devto}]: "
    devto_input = input(devto_prompt).strip()
    if devto_input:
        current_env["DEVTO_API_KEY"] = devto_input

    # Ghost CMS
    curr_ghost_key = current_env.get("GHOST_ADMIN_API_KEY", "")
    curr_ghost_url = current_env.get("GHOST_API_URL", "")
    ghost_url_prompt = f"  Ghost API URL (e.g. https://myblog.ghost.io) [{curr_ghost_url}]: "
    ghost_url_input = input(ghost_url_prompt).strip()
    if ghost_url_input:
        current_env["GHOST_API_URL"] = ghost_url_input

    ghost_key_prompt = f"  Ghost Admin API Key (id:secret) [{curr_ghost_key}]: "
    ghost_key_input = input(ghost_key_prompt).strip()
    if ghost_key_input:
        current_env["GHOST_ADMIN_API_KEY"] = ghost_key_input

    # Active channel
    curr_channel = current_env.get("OMNIPRESS_ACTIVE_CHANNEL", "default")
    channel_prompt = f"  Active Channel Slug [{curr_channel}]: "
    ch_input = input(channel_prompt).strip()
    if ch_input:
        current_env["OMNIPRESS_ACTIVE_CHANNEL"] = ch_input

    # Write back
    lines = []
    for k, v in current_env.items():
        lines.append(f"{k}={v}")
    env_file.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("\n✅ Configuration saved to .env successfully!")
    print("Run `omnipress doctor` to verify your environment readiness.")
    return 0


def cmd_list_channels(args: argparse.Namespace) -> int:
    """Lists all configured channel workspaces."""
    cm = ChannelManager()
    channels = cm.list_channels(include_templates=getattr(args, "include_templates", False))
    print("============================================================")
    print("                 OmniPress Configured Channels              ")
    print("============================================================")
    if not channels:
        print("  No channels found. Create one with `omnipress create-channel`.")
    for ch in channels:
        handle = ch.get("branding", {}).get("handle", "@unknown")
        cat = ch.get("category", "general")
        print(f"  • [{ch.get('slug')}] {ch.get('name')} (Handle: {handle}, Category: {cat})")
    print("============================================================")
    return 0


def cmd_create_channel(args: argparse.Namespace) -> int:
    """Scaffolds a new channel workspace."""
    cm = ChannelManager()
    res = cm.create_channel(
        slug=args.slug,
        name=args.name,
        handle=args.handle,
        category=args.category,
        description=args.description or "",
        primary_color=args.color,
        buffer_channel_id=getattr(args, "buffer_id", "") or "",
        archetype=getattr(args, "archetype", "personal_brand") or "personal_brand",
    )
    print(f"✅ Channel '{res['name']}' created successfully at {res.get('path', '')}")
    return 0


def cmd_info_channel(args: argparse.Namespace) -> int:
    """Displays full JSON configuration and branding for a specific channel."""
    import json
    cm = ChannelManager()
    ch = cm.get_channel(args.slug)
    if not ch:
        print(f"❌ Channel '{args.slug}' not found.")
        return 1
    print(json.dumps(ch, indent=2, ensure_ascii=False))
    return 0


def cmd_sync_buffer(args: argparse.Namespace) -> int:
    """Discovers connected channels from Buffer and syncs them into channel.json."""
    import json
    from src.adapters.buffer_adapter import BufferPublisherAdapter
    cm = ChannelManager()
    slug = args.channel or cm.get_active_channel_slug()
    channel = cm.get_channel(slug)
    if not channel:
        print(f"❌ Channel '{slug}' not found.")
        return 1

    adapter = BufferPublisherAdapter()
    ch_env = cm.get_channel_env(slug)
    env_file = Path(channel["path"]) / ".env"
    if env_file.exists() and not ch_env.get("BUFFER_API_KEY"):
        print(f"⚠️ Atenção: O arquivo 'channels/{slug}/.env' existe, mas 'BUFFER_API_KEY' ainda está vazia.")
        print(f"   Por favor, insira o Personal API Key do Buffer da sua conta em channels/{slug}/.env antes de sincronizar.")
        return 1

    if not adapter.is_configured(channel_slug=slug):
        print(f"❌ Buffer is not configured for channel '{slug}'.")
        print(f"   Please define BUFFER_API_KEY in channels/{slug}/.env or root .env.")
        return 1

    print(f"🔍 Querying Buffer API for channel '{slug}'...")
    res = adapter.list_channels(channel_slug=slug)
    if not res.get("success"):
        print(f"❌ Failed fetching channels from Buffer: {res.get('error')}")
        return 1

    remote_channels = res.get("channels", [])
    if not remote_channels:
        print(f"⚠️ No connected social channels found in Buffer for this account.")
        return 0

    print(f"✅ Found {len(remote_channels)} connected profile(s) in Buffer:")
    social = channel.setdefault("social", {})
    synced = []

    for rc in remote_channels:
        srv = rc.get("service", "").lower()
        cid = rc.get("id")
        cname = rc.get("name")
        print(f"  • [{srv.upper()}] {cname} (ID: {cid})")

        if srv == "instagram":
            social.setdefault("instagram", {})["buffer_channel_id"] = cid
            social["instagram"]["handle"] = cname
            synced.append(f"Instagram -> {cid}")
        elif srv == "linkedin":
            social.setdefault("linkedin", {})["buffer_channel_id"] = cid
            social["linkedin"]["handle"] = cname
            synced.append(f"LinkedIn -> {cid}")
        elif srv in ("twitter", "x"):
            social.setdefault("x_twitter", {})["buffer_channel_id"] = cid
            social["x_twitter"]["handle"] = cname
            synced.append(f"X (Twitter) -> {cid}")
        elif srv == "threads":
            social.setdefault("threads", {})["buffer_channel_id"] = cid
            social["threads"]["handle"] = cname
            synced.append(f"Threads -> {cid}")
        elif srv == "youtube":
            social.setdefault("youtube", {})["buffer_channel_id"] = cid
            social["youtube"]["name"] = cname
            synced.append(f"YouTube -> {cid}")

    config_path = Path(channel["path"]) / "channel.json"
    save_data = {k: v for k, v in channel.items() if k != "path"}
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(save_data, f, indent=2, ensure_ascii=False)

    print(f"\n🎉 Successfully synced {len(synced)} profile(s) into {config_path}")
    for s in synced:
        print(f"   ✓ {s}")
    return 0


def cmd_build_carousel(args: argparse.Namespace) -> int:
    """Renders carousel slides using CarouselBuilder."""
    import json
    from src.engine.carousel_builder import CarouselBuilder
    cm = ChannelManager()
    builder = CarouselBuilder(cm)

    config_path = Path(args.config)
    if not config_path.exists():
        print(f"❌ Config file not found: {args.config}")
        return 1

    try:
        slides_data = json.loads(config_path.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"❌ Failed parsing slides JSON: {e}")
        return 1

    rendered = builder.build_carousel(
        channel_slug=args.channel,
        post_slug=args.post,
        slides_data=slides_data,
        aspect_ratio=args.aspect_ratio,
    )
    print(f"✅ Rendered {len(rendered)} carousel slide(s):")
    for p in rendered:
        print(f"  - {p}")
    return 0


def cmd_carousel(args: argparse.Namespace) -> int:
    """Executes declarative carousel recipes via UniversalCarouselEngine."""
    import json
    from src.engine.universal_carousel import UniversalCarouselEngine

    recipe_path = Path(args.recipe).resolve()
    if not recipe_path.exists():
        print(f"❌ Error: Recipe file not found: {recipe_path}")
        return 1

    do_render = args.render or args.all
    do_upload = args.upload or args.all
    do_schedule = args.schedule or args.all
    if not (do_render or do_upload or do_schedule):
        do_render = True

    cm = ChannelManager()
    engine = UniversalCarouselEngine(channel_manager=cm)

    try:
        recipe_data, _ = engine.load_recipe(recipe_path)
    except Exception as e:
        print(f"❌ Error loading recipe: {e}")
        return 1

    if args.channel:
        recipe_data["channel_slug"] = args.channel
    if getattr(args, "post", None):
        recipe_data["post_slug"] = args.post

    channel_slug = recipe_data.get("channel_slug", "default")
    post_slug = recipe_data.get("post_slug", recipe_path.stem)
    recipe_data["post_slug"] = post_slug
    recipe_data["_recipe_dir"] = str(recipe_path.parent)

    print("============================================================")
    print("         OmniPress Universal Carousel Execution Engine      ")
    print("============================================================")
    print(f"  Channel : {channel_slug}")
    print(f"  Post    : {post_slug}")
    print(f"  Recipe  : {recipe_path.name}")
    print(f"  Actions : render={do_render}, upload={do_upload}, schedule={do_schedule}")
    print("------------------------------------------------------------")

    try:
        result = engine.execute_recipe(
            recipe_input=recipe_data,
            render=do_render,
            upload=do_upload,
            schedule=do_schedule,
            force_duplicate=args.force_duplicate,
        )

        if do_render and result.get("rendered_slides"):
            print(f"✅ Rendered {len(result['rendered_slides'])} slide(s):")
            for p in result["rendered_slides"]:
                print(f"   • {p}")

        if do_upload and result.get("cdn_urls"):
            print(f"📤 Uploaded {len(result['cdn_urls'])} slide(s) to CDN:")
            for u in result["cdn_urls"]:
                print(f"   • {u}")

        if do_schedule and result.get("publish_result"):
            pub_res = result["publish_result"]
            if pub_res.get("success"):
                print(f"🎉 Publication/Scheduling successful:")
                print(f"   {json.dumps(pub_res, indent=2, ensure_ascii=False)}")
            elif pub_res.get("skipped"):
                print(f"ℹ️  Publication skipped: {pub_res.get('reason')}")
            else:
                print(f"⚠️ Publication failed or blocked: {pub_res.get('error')}")
                return 1

        print("============================================================")
        print("✅ Pipeline completed successfully.")
        return 0
    except Exception as e:
        print(f"❌ Pipeline failed: {e}")
        return 1


def cmd_master_audio(args: argparse.Namespace) -> int:
    """Masters voiceover to broadcast standards (Rule 10)."""
    from src.engine.universal_audio import UniversalAudioEngine, find_ffmpeg_binary

    input_path = Path(args.input).resolve()
    if not input_path.exists():
        print(f"❌ Error: Input voiceover file not found: {input_path}")
        return 1

    output_path = Path(args.output).resolve()
    ffmpeg_bin = find_ffmpeg_binary()

    print("============================================================")
    print("      OmniPress Universal Audio Mastering Engine (Rule 10)  ")
    print("============================================================")
    print(f"  Input       : {input_path.name}")
    print(f"  Output      : {output_path.name}")
    print(f"  Target LUFS : {args.target_lufs} LUFS")
    print(f"  Sample Rate : {args.sample_rate} Hz")
    print("------------------------------------------------------------")

    engine = UniversalAudioEngine(ffmpeg_bin=ffmpeg_bin)
    res = engine.master_voiceover(
        input_audio=input_path,
        output_audio=output_path,
        target_lufs=args.target_lufs,
        sample_rate=args.sample_rate,
        bitrate=args.bitrate,
    )

    if res.get("success"):
        print(f"✅ Mastered audio generated successfully: {output_path}")
        return 0
    else:
        print(f"❌ Audio mastering failed: {res.get('error')}")
        return 1


def cmd_align_captions(args: argparse.Namespace) -> int:
    """Formats Whisper JSON into Remotion chunked captions."""
    from src.engine.universal_captions import UniversalCaptionsEngine

    input_path = Path(args.input).resolve()
    if not input_path.exists():
        print(f"❌ Error: Whisper input file not found: {input_path}")
        return 1

    output_path = Path(args.output).resolve()
    engine = UniversalCaptionsEngine()
    res = engine.process_and_export(
        input_whisper=input_path,
        output_json=output_path,
        words_per_chunk=args.words_per_chunk,
        uppercase=not args.lowercase,
        act_id=getattr(args, "act_id", "short_01"),
    )

    if res.get("success"):
        print(f"✅ Chunked captions exported to: {output_path}")
        print(f"   Act ID      : {res.get('act_id')}")
        print(f"   Total Words : {res.get('total_words')}")
        print(f"   Total Chunks: {res.get('total_chunks')}")
        print(f"   Duration    : {res.get('duration')}s")
        return 0
    else:
        print(f"❌ Captions alignment failed: {res.get('error')}")
        return 1


def cmd_publish(args: argparse.Namespace) -> int:
    """Publishes or schedules posts via UniversalPublisherEngine with PublishingShield."""
    import json
    from src.engine.universal_publisher import UniversalPublisherEngine

    cm = ChannelManager()
    engine = UniversalPublisherEngine(channel_manager=cm)

    print("============================================================")
    print("      OmniPress Universal Social Publisher Engine (Rule 09) ")
    print("============================================================")

    if args.recipe:
        recipe_path = Path(args.recipe).resolve()
        if not recipe_path.exists():
            print(f"❌ Error: Recipe file not found: {recipe_path}")
            return 1
        res = engine.execute_recipe(
            recipe_input=recipe_path,
            force_duplicate=args.force_duplicate,
            dry_run=args.dry_run,
        )
    else:
        if not args.text:
            print("❌ Error: Must provide either --recipe or --text.")
            return 1

        if args.mode == "customScheduled" and not args.schedule_time:
            print("❌ Error: --schedule-time is required when --mode is 'customScheduled'.")
            return 1

        channel_slug = args.channel or cm.get_active_channel().get("slug", "default")
        res = engine.publish_social_post(
            channel_slug=channel_slug,
            text=args.text,
            platforms=args.platforms,
            media_urls=args.media or [],
            schedule_time=args.schedule_time,
            mode=args.mode,
            force_duplicate=args.force_duplicate,
            dry_run=args.dry_run,
        )

    if res.get("success"):
        if res.get("dry_run"):
            print("✅ Dry-run pre-flight validation passed successfully:")
        else:
            print("🎉 Publication dispatched and recorded to PublishingShield ledger:")
        print(json.dumps(res, indent=2, ensure_ascii=False))
        return 0
    else:
        print(f"❌ Publication failed: {res.get('error')}")
        return 1


def cmd_render_3d(args: argparse.Namespace) -> int:
    """Renders 3D assets via Universal3DEngine using Blender 4.2+ LTS headless."""
    import json
    from src.engine.universal_3d import Universal3DEngine, BlenderRenderError

    cm = ChannelManager()
    engine = Universal3DEngine(channel_manager=cm)

    print("============================================================")
    print("      OmniPress Universal 3D Blender Engine (Rule 12)       ")
    print("============================================================")

    if not engine.is_available():
        print("❌ Error: Blender binary not found in PATH or standard user directories.")
        print("   Install Blender 4.2+ LTS to use 3D asset rendering.")
        return 1

    try:
        if args.recipe:
            recipe_path = Path(args.recipe).resolve()
            if not recipe_path.exists():
                print(f"❌ Error: Recipe file not found: {recipe_path}")
                return 1
            print(f"Executing declarative 3D recipe: {recipe_path}")
            res = engine.render_recipe(recipe=recipe_path, channel_slug=args.channel)
        else:
            if not args.output:
                print("❌ Error: Must specify --output when running without a --recipe.")
                return 1

            template = args.template or "device_mockup"
            print(f"Rendering 3D template '{template}' to: {args.output}")
            rendered_path = engine.render(
                template=template,
                output_path=args.output,
                texture=args.texture,
                text=args.text,
                material=args.material,
                resolution=args.resolution,
                engine=args.engine,
                samples=args.samples,
            )
            res = {
                "status": "success",
                "output_path": str(rendered_path),
                "template": template,
                "resolution": args.resolution,
                "engine": args.engine,
                "file_size_bytes": rendered_path.stat().st_size if rendered_path.exists() else 0,
            }

        print("🎉 3D Asset rendered successfully:")
        print(json.dumps(res, indent=2, ensure_ascii=False))
        return 0
    except BlenderRenderError as e:
        print(f"❌ Blender render error: {e}")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error during 3D rendering: {e}")
        return 1


def main(argv: Optional[list] = None) -> int:
    parser = argparse.ArgumentParser(
        prog="omnipress",
        description="OmniPress CLI - Universal Agentic Publishing Protocol & Management Suite",
    )
    parser.add_argument("--version", action="version", version="OmniPress MCP 0.8.2")

    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # doctor
    subparsers.add_parser("doctor", help="Run system environment and runtime capability diagnostics")

    # status
    subparsers.add_parser("status", help="Show active channels and publication ledger history")

    # setup
    setup_p = subparsers.add_parser("setup", help="Interactive terminal configuration wizard")
    setup_p.add_argument("--non-interactive", action="store_true", help="Run setup non-interactively")

    # list-channels
    list_p = subparsers.add_parser("list-channels", help="List all configured channel workspaces")
    list_p.add_argument("--include-templates", action="store_true", help="Include boilerplate templates")

    # create-channel
    create_p = subparsers.add_parser("create-channel", help="Scaffold a new channel workspace")
    create_p.add_argument("slug", help="Unique URL-safe channel slug (e.g. tech-insights)")
    create_p.add_argument("--name", required=True, help="Display brand name")
    create_p.add_argument("--handle", required=True, help="Primary social handle (e.g. @techinsights)")
    create_p.add_argument("--category", default="technology", help="Content niche/category")
    create_p.add_argument("--description", default="", help="Channel editorial description")
    create_p.add_argument("--color", default="#00E5FF", help="Primary brand accent color hex (e.g. #00E5FF)")
    create_p.add_argument("--buffer-id", default="", help="Buffer channel/profile ID for automated publishing")
    create_p.add_argument("--archetype", default="personal_brand", choices=["personal_brand", "media_channel", "hybrid"], help="Channel archetype (default: personal_brand)")

    # info-channel
    info_p = subparsers.add_parser("info-channel", help="Show detailed configuration for a channel")
    info_p.add_argument("slug", help="Channel slug to inspect")

    # sync-buffer
    sync_p = subparsers.add_parser("sync-buffer", help="Discover and sync connected Buffer profiles into channel.json")
    sync_p.add_argument("channel", nargs="?", default="", help="Channel slug to sync (defaults to active channel)")

    # carousel (Universal Engine)
    carousel_p = subparsers.add_parser("carousel", help="Execute declarative carousel recipes (render, upload, schedule)")
    carousel_p.add_argument("--recipe", "-r", required=True, help="Path to carousel recipe JSON file")
    carousel_p.add_argument("--channel", "-c", help="Override channel slug")
    carousel_p.add_argument("--post", help="Override post slug")
    carousel_p.add_argument("--render", action="store_true", help="Render slides from recipe")
    carousel_p.add_argument("--upload", action="store_true", help="Upload slides to CDN")
    carousel_p.add_argument("--schedule", action="store_true", help="Schedule or publish post")
    carousel_p.add_argument("--all", action="store_true", help="Execute all pipeline stages")
    carousel_p.add_argument("--force-duplicate", action="store_true", help="Bypass duplicate check")

    # master-audio (Universal Engine)
    audio_p = subparsers.add_parser("master-audio", help="Master voiceover audio to broadcast standards (Rule 10)")
    audio_p.add_argument("input", help="Source voiceover audio (.m4a, .wav, .mp3)")
    audio_p.add_argument("-o", "--output", required=True, help="Output mastered audio file (.mp3, .wav)")
    audio_p.add_argument("--target-lufs", type=float, default=-14.0, help="Target loudness (default: -14.0 LUFS)")
    audio_p.add_argument("--sample-rate", type=int, default=48000, help="Sample rate in Hz (default: 48000)")
    audio_p.add_argument("--bitrate", default="192k", help="MP3 bitrate (default: 192k)")

    # align-captions (Universal Engine)
    captions_p = subparsers.add_parser("align-captions", help="Convert Whisper JSON to Remotion chunked captions")
    captions_p.add_argument("input", help="Raw Whisper JSON file")
    captions_p.add_argument("-o", "--output", required=True, help="Output captions JSON file")
    captions_p.add_argument("--words-per-chunk", type=int, default=3, help="Words per subtitle chunk (default: 3)")
    captions_p.add_argument("--lowercase", action="store_true", help="Keep original casing instead of uppercase")
    captions_p.add_argument("--act-id", default="short_01", help="Act ID key for Remotion synchronization (default: short_01)")

    # publish (Universal Engine)
    publish_p = subparsers.add_parser("publish", help="Publish or schedule posts with PublishingShield (Rule 09)")
    publish_p.add_argument("--recipe", "-r", help="Path to post_recipe.json")
    publish_p.add_argument("--channel", "-c", help="Target channel workspace slug")
    publish_p.add_argument("--text", "-t", help="Post caption / body text")
    publish_p.add_argument("--platforms", "-p", nargs="+", default=["instagram"], help="Target platforms")
    publish_p.add_argument("--media", "-m", nargs="*", default=[], help="Media URLs to attach")
    publish_p.add_argument("--schedule-time", help="ISO 8601 UTC timestamp")
    publish_p.add_argument("--mode", choices=["shareNow", "customScheduled", "addToQueue"], help="Publish mode")
    publish_p.add_argument("--dry-run", action="store_true", help="Dry run validation without dispatch")
    publish_p.add_argument("--force-duplicate", action="store_true", help="Bypass PublishingShield duplicate check")

    # render-3d (Universal 3D Engine)
    render_3d_p = subparsers.add_parser("render-3d", help="Render 3D visual assets via Blender headless (Rule 12)")
    render_3d_p.add_argument("--recipe", "-r", help="Path to 3D recipe JSON file")
    render_3d_p.add_argument("--template", choices=["device_mockup", "rotating_badge", "kinetic_title", "waving_flag", "brazil_flag"], default="device_mockup", help="Template name")
    render_3d_p.add_argument("--texture", help="Path to image texture (device screen or coin emblem)")
    render_3d_p.add_argument("--text", help="Text string for kinetic_title")
    render_3d_p.add_argument("--material", help="Material preset (gold, silver, chrome, obsidian)")
    render_3d_p.add_argument("-o", "--output", help="Output file path for rendered image")
    render_3d_p.add_argument("-c", "--channel", help="Target channel slug")
    render_3d_p.add_argument("--resolution", default="1080x1080", help="Render resolution (e.g. 1080x1080, 1920x1080)")
    render_3d_p.add_argument("--engine", choices=["BLENDER_EEVEE_NEXT", "CYCLES"], default="BLENDER_EEVEE_NEXT", help="Render engine")
    render_3d_p.add_argument("--samples", type=int, default=32, help="Render sample count")

    # build-carousel (legacy alias)
    build_p = subparsers.add_parser("build-carousel", help="Render portrait carousel slides (legacy)")
    build_p.add_argument("--channel", required=True, help="Target channel slug")
    build_p.add_argument("--post", required=True, help="Unique post slug for output directory")
    build_p.add_argument("--config", required=True, help="Path to JSON file with slides array")
    build_p.add_argument("--aspect-ratio", default="3:4", choices=["3:4", "1:1"], help="Carousel aspect ratio")

    args = parser.parse_args(argv)

    if args.command == "doctor":
        return cmd_doctor(args)
    elif args.command == "status":
        return cmd_status(args)
    elif args.command == "setup":
        return cmd_setup(args)
    elif args.command == "list-channels":
        return cmd_list_channels(args)
    elif args.command == "create-channel":
        return cmd_create_channel(args)
    elif args.command == "info-channel":
        return cmd_info_channel(args)
    elif args.command == "sync-buffer":
        return cmd_sync_buffer(args)
    elif args.command == "carousel":
        return cmd_carousel(args)
    elif args.command == "master-audio":
        return cmd_master_audio(args)
    elif args.command == "align-captions":
        return cmd_align_captions(args)
    elif args.command == "publish":
        return cmd_publish(args)
    elif args.command == "render-3d":
        return cmd_render_3d(args)
    elif args.command == "build-carousel":
        return cmd_build_carousel(args)
    else:
        # Default action: show help
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main())

