#!/usr/bin/env python3
"""
Example Channel Automation Script — OmniPress MCP.
Demonstrates how to interact with the channel workspace and invoke OmniPress publishing modules.
"""

import sys
from pathlib import Path

# Resolve project root dynamically
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.core.channel_manager import ChannelManager


def main():
    cm = ChannelManager()
    channel_dir = Path(__file__).resolve().parent.parent
    channel_slug = channel_dir.name

    print(f"🚀 Running channel automation for: {channel_slug}")
    channel_config = cm.get_channel(channel_slug)
    if not channel_config:
        print(f"⚠️ Warning: Channel configuration not found for {channel_slug}. Using template defaults.")
    else:
        print(f"✅ Channel Loaded: {channel_config.get('name')} ({channel_config.get('category')})")

    # Example: List articles in this channel
    articles_dir = cm.get_articles_dir(channel_slug)
    articles = list(articles_dir.glob("**/*.md"))
    print(f"📄 Articles found: {len(articles)}")


if __name__ == "__main__":
    main()
