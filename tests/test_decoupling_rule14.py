"""Unit Tests for Strict Decoupling and Channel Isolation (Rule 14 & Rule 04)."""

import json
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest

from src.core.channel_manager import ChannelManager
from src.adapters.webhook_adapter import WebhookPublisherAdapter
from src.adapters.youtube_adapter import YouTubeStagingAdapter
from src.adapters.buffer_adapter import BufferPublisherAdapter
from src.adapters.reddit_adapter import RedditPublisherAdapter
from src.utils.storage import get_default_storage_provider, S3StorageProvider, LocalStaticStorageProvider
from src.engine.universal_publisher import UniversalPublisherEngine


@pytest.fixture
def isolated_channel_env(tmp_path):
    """Sets up a temporary multi-tenant workspace with an isolated channel."""
    channels_dir = tmp_path / "channels"
    channels_dir.mkdir(parents=True)
    ch_slug = "custom-brand"
    ch_dir = channels_dir / ch_slug
    ch_dir.mkdir()

    # channel.json
    ch_json = ch_dir / "channel.json"
    ch_json.write_text(
        json.dumps({
            "slug": ch_slug,
            "name": "Custom Brand",
            "social": {
                "linkedin": {"buffer_channel_id": "ch_buf_custom_li"},
                "x_twitter": {"buffer_channel_id": "ch_buf_custom_x"}
            }
        }),
        encoding="utf-8"
    )

    # channel .env
    ch_env = ch_dir / ".env"
    ch_env.write_text(
        "BUFFER_API_KEY=ch_secret_buffer_key\n"
        "BUFFER_THREADS_PROFILE_ID=ch_threads_profile_456\n"
        "OMNIPRESS_WEBHOOK_URL=https://custom.hooks.domain/events\n"
        "OMNIPRESS_WEBHOOK_SECRET=custom_secret_123\n"
        "YOUTUBE_WEBHOOK_URL=https://custom.hooks.domain/yt-dispatch\n"
        "REDDIT_DEFAULT_SUBREDDIT=CustomTechSub\n"
        "S3_BUCKET_NAME=custom-brand-bucket\n"
        "S3_PUBLIC_URL_PREFIX=https://cdn.custombrand.com\n",
        encoding="utf-8"
    )

    cm = ChannelManager(root_dir=tmp_path)
    return {"cm": cm, "slug": ch_slug, "ch_dir": ch_dir, "tmp_path": tmp_path}


def test_webhook_adapter_channel_decoupling(isolated_channel_env, monkeypatch):
    """WebhookPublisherAdapter resolves channel credentials with Rule 04 precedence."""
    monkeypatch.delenv("OMNIPRESS_WEBHOOK_URL", raising=False)
    monkeypatch.delenv("OMNIPRESS_WEBHOOK_SECRET", raising=False)

    adapter = WebhookPublisherAdapter()
    assert adapter.is_configured() is False

    with patch("src.core.channel_manager.ChannelManager", return_value=isolated_channel_env["cm"]):
        assert adapter.is_configured(channel_slug=isolated_channel_env["slug"]) is True
        url, sec = adapter.get_credentials(channel_slug=isolated_channel_env["slug"])
        assert url == "https://custom.hooks.domain/events"
        assert sec == "custom_secret_123"

        with patch("requests.post") as mock_post:
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.text = '{"status":"ok"}'
            mock_post.return_value = mock_resp

            res = adapter.queue_social_post(
                text="Channel isolated webhook post",
                platforms=["slack"],
                channel_slug=isolated_channel_env["slug"]
            )
            assert res["success"] is True
            assert mock_post.called
            call_url = mock_post.call_args[0][0]
            assert call_url == "https://custom.hooks.domain/events"


def test_youtube_adapter_channel_staging_isolation(isolated_channel_env, monkeypatch):
    """YouTubeStagingAdapter stages videos inside channels/<slug>/media/staging."""
    monkeypatch.delenv("YOUTUBE_WEBHOOK_URL", raising=False)

    adapter = YouTubeStagingAdapter()
    ch_slug = isolated_channel_env["slug"]

    with patch("src.core.channel_manager.ChannelManager", return_value=isolated_channel_env["cm"]):
        assert adapter.is_configured(channel_slug=ch_slug) is True
        assert adapter.get_credentials(channel_slug=ch_slug) == "https://custom.hooks.domain/yt-dispatch"

        res = adapter.stage_video(
            title="Isolated Episode",
            description="Testing channel staging directory",
            channel_slug=ch_slug,
            is_short=True
        )
        assert res["manifest"]["title"] == "Isolated Episode #Shorts"
        assert f"channels/{ch_slug}/media/staging" in res["filepath"]
        assert Path(res["filepath"]).exists()


def test_buffer_adapter_profile_decoupling_and_statelessness(isolated_channel_env, monkeypatch):
    """BufferPublisherAdapter resolves credentials from channel and preserves statelessness."""
    monkeypatch.delenv("BUFFER_API_KEY", raising=False)
    monkeypatch.delenv("BUFFER_THREADS_PROFILE_ID", raising=False)

    adapter = BufferPublisherAdapter()
    ch_slug = isolated_channel_env["slug"]

    with patch("src.core.channel_manager.ChannelManager", return_value=isolated_channel_env["cm"]):
        assert adapter.is_configured(channel_slug=ch_slug) is True
        assert adapter.get_api_key(channel_slug=ch_slug) == "ch_secret_buffer_key"

        targets = adapter._resolve_targets(platforms=["linkedin", "threads"], channel_slug=ch_slug)
        target_map = {t["service"]: t["id"] for t in targets}
        assert target_map.get("linkedin") == "ch_buf_custom_li"
        assert target_map.get("threads") == "ch_threads_profile_456"

        # Verify statelessness: _channel_services property remains an empty dict and doesn't leak state
        assert adapter._channel_services == {}


def test_reddit_adapter_subreddit_decoupling(isolated_channel_env, monkeypatch):
    """RedditPublisherAdapter resolves custom default subreddit from channel config."""
    adapter = RedditPublisherAdapter()
    ch_slug = isolated_channel_env["slug"]

    with patch("src.core.channel_manager.ChannelManager", return_value=isolated_channel_env["cm"]):
        sub = adapter.get_default_subreddit(channel_slug=ch_slug)
        assert sub == "CustomTechSub"


def test_storage_provider_channel_decoupling(isolated_channel_env, monkeypatch):
    """get_default_storage_provider resolves channel S3 credentials."""
    monkeypatch.delenv("S3_BUCKET_NAME", raising=False)
    monkeypatch.delenv("R2_BUCKET_NAME", raising=False)
    monkeypatch.delenv("OMNIPRESS_PUBLIC_URL", raising=False)

    ch_slug = isolated_channel_env["slug"]
    with patch("src.core.channel_manager.ChannelManager", return_value=isolated_channel_env["cm"]):
        provider = get_default_storage_provider(channel_slug=ch_slug)
        assert isinstance(provider, S3StorageProvider)
        assert provider.bucket_name == "custom-brand-bucket"
        assert provider.public_url_prefix == "https://cdn.custombrand.com"


def test_universal_publisher_modular_provider_routing(monkeypatch):
    """UniversalPublisherEngine routes to requested provider (Buffer, Webhook, Markdown)."""
    engine = UniversalPublisherEngine()

    with patch("src.adapters.webhook_adapter.WebhookPublisherAdapter.is_configured", return_value=True), \
         patch("src.adapters.webhook_adapter.WebhookPublisherAdapter.queue_social_post") as mock_webhook:
        mock_webhook.return_value = {"success": True, "provider": "webhook"}

        res = engine.publish_social_post(
            channel_slug="default",
            text="Hello Webhook Pipeline!",
            platforms=["slack"],
            provider="webhook",
            force_duplicate=True
        )
        assert res["success"] is True
        assert mock_webhook.called
