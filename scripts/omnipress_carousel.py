#!/usr/bin/env python3
"""OmniPress Universal Carousel Runner.

Executes declarative carousel recipes (JSON) end-to-end:
- Prepares backgrounds (crops, resizes, contrast enhancement)
- Renders branded slides (Rule 08 cards & typography safety stroke)
- Uploads slide images to CDN (S3/R2/Catbox)
- Publishes or schedules to Buffer/Instagram via PublishingShield (Rule 09)

Usage:
    python scripts/omnipress_carousel.py --recipe path/to/recipe.json --all
    python scripts/omnipress_carousel.py --recipe path/to/recipe.json --render
    python scripts/omnipress_carousel.py --recipe path/to/recipe.json --upload --schedule
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
from src.engine.universal_carousel import UniversalCarouselEngine


def main(argv: list = None) -> int:
    parser = argparse.ArgumentParser(
        prog="omnipress-carousel",
        description="OmniPress Universal Carousel Engine - Execute declarative carousel recipes.",
    )
    parser.add_argument(
        "--recipe", "-r",
        required=True,
        help="Path to declarative carousel recipe JSON file",
    )
    parser.add_argument(
        "--channel", "-c",
        help="Target channel slug (overrides channel_slug in recipe if provided)",
    )
    parser.add_argument(
        "--render",
        action="store_true",
        help="Render slide images from recipe definitions",
    )
    parser.add_argument(
        "--upload",
        action="store_true",
        help="Upload rendered slide images to CDN storage",
    )
    parser.add_argument(
        "--schedule",
        action="store_true",
        help="Schedule or publish the post via publisher adapter & PublishingShield",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Run all stages: render, upload, and schedule/publish",
    )
    parser.add_argument(
        "--force-duplicate",
        action="store_true",
        help="Bypass PublishingShield anti-duplicate protection gate",
    )

    args = parser.parse_args(argv)

    recipe_path = Path(args.recipe).resolve()
    if not recipe_path.exists():
        print(f"❌ Error: Recipe file not found: {recipe_path}")
        return 1

    do_render = args.render or args.all
    do_upload = args.upload or args.all
    do_schedule = args.schedule or args.all

    if not (do_render or do_upload or do_schedule):
        # Default behavior when no flag specified is render
        do_render = True

    cm = ChannelManager(root_dir=PROJECT_ROOT)
    engine = UniversalCarouselEngine(channel_manager=cm)

    try:
        recipe_data, _ = engine.load_recipe(recipe_path)
    except Exception as e:
        print(f"❌ Error loading recipe: {e}")
        return 1

    if args.channel:
        recipe_data["channel_slug"] = args.channel

    channel_slug = recipe_data.get("channel_slug", "default")
    post_slug = recipe_data.get("post_slug", recipe_path.stem)
    recipe_data["post_slug"] = post_slug

    print(f"============================================================")
    print(f"         OmniPress Universal Carousel Execution Engine      ")
    print(f"============================================================")
    print(f"  Channel : {channel_slug}")
    print(f"  Post    : {post_slug}")
    print(f"  Recipe  : {recipe_path.name}")
    print(f"  Actions : render={do_render}, upload={do_upload}, schedule={do_schedule}")
    print(f"------------------------------------------------------------")

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

        print(f"============================================================")
        print(f"✅ Pipeline completed successfully.")
        return 0

    except Exception as e:
        print(f"❌ Pipeline failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
