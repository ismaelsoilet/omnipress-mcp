#!/usr/bin/env python3
"""OmniPress Universal Publisher Runner.

Dispatches social posts and campaign assets across platforms with:
- LGPD / Judicial secrecy sanitization (Rule 01)
- Character length verification per platform
- Pre-flight anti-duplicate protection via PublishingShield (Rule 09)
- Execution via Buffer GraphQL or direct publisher adapters

Usage:
    python scripts/omnipress_publisher.py --recipe path/to/post_recipe.json
    python scripts/omnipress_publisher.py --channel dossie-historico --text "Caption..." --platforms instagram
"""

import argparse
import json
import os
import sys
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Optional dotenv
try:
    from dotenv import load_dotenv
    load_dotenv(PROJECT_ROOT / ".env")
except ImportError:
    pass

from src.core.channel_manager import ChannelManager
from src.engine.universal_publisher import UniversalPublisherEngine


def main(argv: list = None) -> int:
    parser = argparse.ArgumentParser(
        prog="omnipress-publisher",
        description="OmniPress Universal Publisher Engine - Multi-Channel Syndication with PublishingShield.",
    )
    parser.add_argument(
        "--recipe", "-r",
        help="Path to post_recipe.json file",
    )
    parser.add_argument(
        "--channel", "-c",
        help="Target channel workspace slug (e.g. dossie-historico)",
    )
    parser.add_argument(
        "--text", "-t",
        help="Post caption / body text",
    )
    parser.add_argument(
        "--platforms", "-p",
        nargs="+",
        default=["instagram"],
        help="Target social platforms (instagram, linkedin, x, etc.)",
    )
    parser.add_argument(
        "--media", "-m",
        nargs="*",
        default=[],
        help="Public media URLs to attach to the post",
    )
    parser.add_argument(
        "--schedule-time",
        help="ISO 8601 UTC timestamp for scheduled publication (e.g. 2026-10-31T23:00:00.000Z)",
    )
    parser.add_argument(
        "--mode",
        choices=["shareNow", "customScheduled", "addToQueue"],
        help="Publication mode (default: shareNow or customScheduled if schedule-time is set)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Perform pre-flight checks and validation without sending network requests",
    )
    parser.add_argument(
        "--force-duplicate",
        action="store_true",
        help="Bypass PublishingShield duplicate protection gate",
    )

    args = parser.parse_args(argv)

    cm = ChannelManager(root_dir=PROJECT_ROOT)
    engine = UniversalPublisherEngine(channel_manager=cm)

    print("============================================================")
    print("      OmniPress Universal Social Publisher Engine (Rule 09) ")
    print("============================================================")

    if args.recipe:
        recipe_path = Path(args.recipe).resolve()
        if not recipe_path.exists():
            print(f"❌ Error: Recipe file not found: {recipe_path}")
            return 1
        print(f"  Recipe : {recipe_path.name}")
        res = engine.execute_recipe(
            recipe_input=recipe_path,
            force_duplicate=args.force_duplicate,
            dry_run=args.dry_run,
        )
    else:
        if not args.text:
            print("❌ Error: Must provide either --recipe or --text.")
            return 1

        channel_slug = args.channel or cm.get_active_channel().get("slug", "default")
        print(f"  Channel   : {channel_slug}")
        print(f"  Platforms : {args.platforms}")
        print(f"  Media URLs: {len(args.media)}")
        print(f"  Dry Run   : {args.dry_run}")
        print("------------------------------------------------------------")

        res = engine.publish_social_post(
            channel_slug=channel_slug,
            text=args.text,
            platforms=args.platforms,
            media_urls=args.media,
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


if __name__ == "__main__":
    sys.exit(main())
