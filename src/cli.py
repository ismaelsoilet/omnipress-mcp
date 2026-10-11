"""OmniPress Multi-Channel CLI."""

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.core.channel_manager import ChannelManager


def main():
    parser = argparse.ArgumentParser(prog="omnipress", description="OmniPress Multi-Channel CLI")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Command: list-channels
    list_p = subparsers.add_parser("list-channels", help="List all configured channels")
    list_p.add_argument("--all", action="store_true", help="Include template channels")

    # Command: create-channel
    create_p = subparsers.add_parser("create-channel", help="Scaffold a new channel workspace")
    create_p.add_argument("slug", help="Channel slug (e.g. tech-daily)")
    create_p.add_argument("--name", required=True, help="Human-readable channel name")
    create_p.add_argument("--handle", required=True, help="Social handle (e.g. @techdaily.canal)")
    create_p.add_argument("--category", default="general", help="Content category")
    create_p.add_argument("--color", default="#D4AF37", help="Primary brand color hex (default: #D4AF37)")
    create_p.add_argument("--buffer-id", default="", help="Buffer channel ID")

    # Command: info-channel
    info_p = subparsers.add_parser("info-channel", help="Show details of a specific channel")
    info_p.add_argument("slug", help="Channel slug")

    # Command: build-carousel
    carousel_p = subparsers.add_parser("build-carousel", help="Build a multi-slide carousel for a channel")
    carousel_p.add_argument("--channel", required=True, help="Target channel slug")
    carousel_p.add_argument("--post", required=True, help="Post slug / folder name")
    carousel_p.add_argument("--config", required=True, help="Path to JSON file containing slides array")
    carousel_p.add_argument("--aspect-ratio", default="3:4", choices=["3:4", "1:1"], help="Slide ratio")

    args = parser.parse_args()
    cm = ChannelManager()

    if args.command == "list-channels":
        channels = cm.list_channels(include_templates=args.all)
        active = cm.get_active_channel_slug()
        print(f"📡 OmniPress Channels ({len(channels)}) — Active: {active}\n")
        for ch in channels:
            flag = " [ACTIVE]" if ch.get("slug") == active else ""
            print(f"- {ch.get('name')} ({ch.get('slug')}){flag}")
            print(f"  Handle: {ch.get('branding', {}).get('handle', 'N/A')}")
            print(f"  Path: {ch.get('path', '')}\n")

    elif args.command == "create-channel":
        res = cm.create_channel(
            slug=args.slug,
            name=args.name,
            handle=args.handle,
            category=args.category,
            primary_color=args.color,
            buffer_channel_id=args.buffer_id,
        )
        print(f"✅ Channel '{res['name']}' created successfully at: {res['path']}")

    elif args.command == "info-channel":
        ch = cm.get_channel(args.slug)
        if not ch:
            print(f"❌ Channel '{args.slug}' not found.")
            sys.exit(1)
        print(json.dumps(ch, indent=2, ensure_ascii=False))

    elif args.command == "build-carousel":
        config_file = Path(args.config)
        if not config_file.exists():
            print(f"❌ Config file not found: {args.config}")
            sys.exit(1)
        with open(config_file, "r", encoding="utf-8") as f:
            slides = json.load(f)
        try:
            from src.engine.carousel_builder import CarouselBuilder
        except ImportError:
            print("❌ Pillow is required for carousel generation. Run inside .venv or install Pillow.")
            sys.exit(1)
        builder = CarouselBuilder(cm)
        paths = builder.build_carousel(
            channel_slug=args.channel,
            post_slug=args.post,
            slides_data=slides,
            aspect_ratio=args.aspect_ratio,
        )
        print(f"✅ Generated {len(paths)} slides for channel '{args.channel}':")
        for p in paths:
            print(f"- {p}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
