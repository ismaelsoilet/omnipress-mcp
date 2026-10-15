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
    active_slug = os.getenv("OMNIPRESS_ACTIVE_CHANNEL", "dossie-historico")

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
    curr_channel = current_env.get("OMNIPRESS_ACTIVE_CHANNEL", "dossie-historico")
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

    rendered = builder.render_carousel_deck(
        channel_slug=args.channel,
        post_slug=args.post,
        slides=slides_data,
        aspect_ratio=args.aspect_ratio,
    )
    print(f"✅ Rendered {len(rendered)} carousel slide(s):")
    for p in rendered:
        print(f"  - {p}")
    return 0


def main(argv: Optional[list] = None) -> int:
    parser = argparse.ArgumentParser(
        prog="omnipress",
        description="OmniPress CLI - Universal Agentic Publishing Protocol & Management Suite",
    )
    parser.add_argument("--version", action="version", version="OmniPress MCP 0.1.0")

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

    # info-channel
    info_p = subparsers.add_parser("info-channel", help="Show detailed configuration for a channel")
    info_p.add_argument("slug", help="Channel slug to inspect")

    # build-carousel
    build_p = subparsers.add_parser("build-carousel", help="Render portrait carousel slides from JSON definition")
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
    elif args.command == "build-carousel":
        return cmd_build_carousel(args)
    else:
        # Default action: show help
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main())
