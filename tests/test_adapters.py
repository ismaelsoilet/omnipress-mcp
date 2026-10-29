"""Comprehensive Unit Tests for all OmniPress Adapters."""

import json
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest

from src.adapters.buffer_adapter import BufferPublisherAdapter
from src.adapters.webhook_adapter import WebhookPublisherAdapter
from src.adapters.reddit_adapter import RedditPublisherAdapter
from src.adapters.youtube_adapter import YouTubeStagingAdapter
from src.adapters.instagram_adapter import InstagramGraphAdapter
from src.adapters.markdown_adapter import MarkdownArchiveAdapter


# -------------------------------------------------------------
# Buffer Adapter Tests
# -------------------------------------------------------------
def test_buffer_adapter_configuration(monkeypatch):
    monkeypatch.delenv("BUFFER_API_KEY", raising=False)
    monkeypatch.delenv("BUFFER_ACCESS_TOKEN", raising=False)
    adapter = BufferPublisherAdapter()
    assert adapter.is_configured() is False

    monkeypatch.setenv("BUFFER_API_KEY", "test_key_123")
    adapter = BufferPublisherAdapter()
    assert adapter.is_configured() is True


def test_buffer_adapter_queue_post(monkeypatch):
    monkeypatch.setenv("BUFFER_API_KEY", "test_key_123")
    monkeypatch.setenv("BUFFER_LINKEDIN_PROFILE_ID", "prof_linkedin_99")
    adapter = BufferPublisherAdapter()

    with patch("requests.post") as mock_post:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "data": {
                "createPost": {
                    "post": {"id": "post_buff_1", "status": "scheduled"}
                }
            }
        }
        mock_post.return_value = mock_resp

        res = adapter.queue_social_post(
            text="Hello LinkedIn!",
            platforms=["linkedin"],
            schedule_time="2026-10-15T15:00:00Z"
        )
        assert res["success"] is True
        assert res["provider"] == "buffer_graphql"
        assert res["mode"] == "customScheduled"
        assert res["queued_profiles_count"] == 1
        
        # Verify mode passed to GraphQL variables
        call_payload = mock_post.call_args[1]["json"]
        assert call_payload["variables"]["input"]["mode"] == "customScheduled"
        assert call_payload["variables"]["input"]["dueAt"] == "2026-10-15T15:00:00Z"


def test_buffer_adapter_queue_linkedin_document(monkeypatch):
    monkeypatch.setenv("BUFFER_API_KEY", "test_key_123")
    monkeypatch.setenv("BUFFER_LINKEDIN_PROFILE_ID", "prof_linkedin_99")
    adapter = BufferPublisherAdapter()

    with patch("requests.post") as mock_post:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "data": {
                "createPost": {
                    "post": {"id": "post_doc_1", "status": "scheduled"}
                }
            }
        }
        mock_post.return_value = mock_resp

        res = adapter.queue_social_post(
            text="LinkedIn Document Carousel Post",
            platforms=["linkedin"],
            document_url="https://storage.example.com/dossie.pdf",
            document_title="Dossiê Tributário",
            document_thumbnail_url="https://storage.example.com/thumb.jpg",
            schedule_time="2026-10-15T15:00:00Z",
            allow_test=True,
            force_duplicate=True,
        )
        assert res["success"] is True
        call_payload = mock_post.call_args[1]["json"]
        assets = call_payload["variables"]["input"]["assets"]
        assert len(assets) == 1
        assert "document" in assets[0]
        assert assets[0]["document"]["url"] == "https://storage.example.com/dossie.pdf"
        assert assets[0]["document"]["title"] == "Dossiê Tributário"
        assert assets[0]["document"]["thumbnailUrl"] == "https://storage.example.com/thumb.jpg"


def test_buffer_adapter_publish_now_by_default(monkeypatch):
    monkeypatch.setenv("BUFFER_API_KEY", "test_key_123")
    monkeypatch.setenv("BUFFER_LINKEDIN_PROFILE_ID", "prof_linkedin_99")
    adapter = BufferPublisherAdapter()

    with patch("requests.post") as mock_post:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "data": {
                "createPost": {
                    "post": {"id": "post_buff_2", "status": "sent"}
                }
            }
        }
        mock_post.return_value = mock_resp

        res = adapter.queue_social_post(
            text="Postar na hora sem agendamento!",
            platforms=["linkedin"],
            schedule_time=None
        )
        assert res["success"] is True
        assert res["provider"] == "buffer_graphql"
        assert res["mode"] == "shareNow"
        assert "published" in res["message"]

        # Verify mode is shareNow and dueAt is absent
        call_payload = mock_post.call_args[1]["json"]
        assert call_payload["variables"]["input"]["mode"] == "shareNow"
        assert "dueAt" not in call_payload["variables"]["input"]


def test_buffer_adapter_instagram_metadata_and_delete(monkeypatch):
    monkeypatch.setenv("BUFFER_API_KEY", "test_key_123")
    monkeypatch.setenv("BUFFER_INSTAGRAM_PROFILE_ID", "prof_ig_123")
    adapter = BufferPublisherAdapter()

    # 1. Test Instagram metadata injection
    with patch("requests.post") as mock_post:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "data": {
                "createPost": {
                    "post": {"id": "post_ig_1", "status": "sent"}
                }
            }
        }
        mock_post.return_value = mock_resp

        res = adapter.queue_social_post(
            text="Carrossel Instagram!",
            platforms=["instagram"],
            media_urls=["https://example.com/slide1.jpg"],
        )
        assert res["success"] is True
        call_payload = mock_post.call_args[1]["json"]
        assert call_payload["variables"]["input"]["metadata"]["instagram"]["type"] == "post"
        assert call_payload["variables"]["input"]["metadata"]["instagram"]["shouldShareToFeed"] is True

    # 2. Test delete_post
    with patch("requests.post") as mock_post:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "data": {
                "deletePost": {
                    "id": "post_ig_1"
                }
            }
        }
        mock_post.return_value = mock_resp

        del_res = adapter.delete_post("post_ig_1")
        assert del_res["success"] is True
        assert del_res["deleted_id"] == "post_ig_1"


def test_buffer_adapter_multi_platform_resolution_and_no_contamination(monkeypatch):
    """Verify per-platform resolution from channel.json + .env and prevent metadata contamination."""
    monkeypatch.setenv("BUFFER_API_KEY", "test_key_123")
    monkeypatch.setenv("BUFFER_X_PROFILE_ID", "prof_x_99")
    monkeypatch.setenv("BUFFER_INSTAGRAM_PROFILE_ID", "prof_ig_123")
    adapter = BufferPublisherAdapter()

    # Suppose channel_manager returns a channel that only has instagram
    mock_channel = {
        "slug": "custom-brand",
        "social": {
            "instagram": {"buffer_channel_id": "ch_custom_ig"}
        }
    }
    with patch("src.core.channel_manager.ChannelManager.get_channel", return_value=mock_channel):
        ids = adapter._resolve_channel_ids(["instagram", "x"], channel_slug="custom-brand")
        assert "ch_custom_ig" in ids
        assert "prof_x_99" in ids

    # Verify queueing with both platforms does NOT inject instagram metadata into the X post
    with patch("requests.post") as mock_post:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "data": {
                "createPost": {
                    "post": {"id": "post_multi_1", "status": "sent"}
                }
            }
        }
        mock_post.return_value = mock_resp

        res = adapter.queue_social_post(
            text="Post simultâneo Instagram e Twitter sem contaminação!",
            platforms=["instagram", "x"],
            media_urls=["https://example.com/image.jpg"],
        )
        assert res["success"] is True
        calls = mock_post.call_args_list
        assert len(calls) == 2
        payload_1 = calls[0][1]["json"]["variables"]["input"]
        payload_2 = calls[1][1]["json"]["variables"]["input"]

        ch_payloads = {p["channelId"]: p for p in [payload_1, payload_2]}
        assert "prof_ig_123" in ch_payloads
        assert "prof_x_99" in ch_payloads

        assert "metadata" in ch_payloads["prof_ig_123"]
        assert "instagram" in ch_payloads["prof_ig_123"]["metadata"]

        assert "metadata" not in ch_payloads["prof_x_99"] or "instagram" not in ch_payloads["prof_x_99"].get("metadata", {})


def test_buffer_adapter_thread_no_linkedin_contamination(monkeypatch):
    """Adversarial check: Multi-platform dispatch with thread MUST NOT contaminate LinkedIn."""
    monkeypatch.setenv("BUFFER_API_KEY", "test_key_123")
    monkeypatch.setenv("BUFFER_LINKEDIN_PROFILE_ID", "prof_linkedin_88")
    monkeypatch.setenv("BUFFER_X_PROFILE_ID", "prof_x_99")
    adapter = BufferPublisherAdapter()

    thread_tweets = [
        "Tweet 1: Abertura sobre Arquitetura de Software",
        "Tweet 2: Detalhes de isolamento e desacoplamento",
        "Tweet 3: Conclusão e lições aprendidas",
    ]

    with patch("requests.post") as mock_post:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "data": {
                "createPost": {
                    "post": {"id": "post_thread_test", "status": "sent"}
                }
            }
        }
        mock_post.return_value = mock_resp

        res = adapter.queue_social_post(
            text="Texto completo para LinkedIn com múltiplos parágrafos.",
            platforms=["linkedin", "x"],
            thread=thread_tweets,
        )
        assert res["success"] is True
        calls = mock_post.call_args_list
        assert len(calls) == 2

        payloads = {c[1]["json"]["variables"]["input"]["channelId"]: c[1]["json"]["variables"]["input"] for c in calls}
        assert "prof_linkedin_88" in payloads
        assert "prof_x_99" in payloads

        # 1. LinkedIn payload verification: MUST NOT have twitter metadata, MUST NOT be truncated to tweet 1
        li_payload = payloads["prof_linkedin_88"]
        assert li_payload["text"] == "Texto completo para LinkedIn com múltiplos parágrafos."
        assert "metadata" not in li_payload or "twitter" not in li_payload.get("metadata", {})

        # 2. X payload verification: MUST have first tweet as text, and thread metadata with remaining tweets
        x_payload = payloads["prof_x_99"]
        assert x_payload["text"] == thread_tweets[0]
        assert "metadata" in x_payload
        assert "twitter" in x_payload["metadata"]
        assert "thread" in x_payload["metadata"]["twitter"]
        thread_items = x_payload["metadata"]["twitter"]["thread"]
        assert len(thread_items) == 2
        assert thread_items[0]["text"] == thread_tweets[1]
        assert thread_items[1]["text"] == thread_tweets[2]


# -------------------------------------------------------------
# Webhook Adapter Tests
# -------------------------------------------------------------
def test_webhook_adapter(monkeypatch):
    monkeypatch.setenv("OMNIPRESS_WEBHOOK_URL", "https://api.example.com/webhook")
    monkeypatch.setenv("OMNIPRESS_WEBHOOK_SECRET", "supersecret123")
    adapter = WebhookPublisherAdapter()
    assert adapter.is_configured() is True

    with patch("requests.post") as mock_post:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"ok": True}
        mock_post.return_value = mock_resp

        res = adapter.queue_social_post(
            text="Testing webhook",
            platforms=["slack", "n8n"]
        )
        assert res["success"] is True
        assert mock_post.called
        headers = mock_post.call_args[1]["headers"]
        assert "X-OmniPress-Signature" in headers
        # SHA-256 hexdigest has 64 characters
        assert len(headers["X-OmniPress-Signature"]) == 64


# -------------------------------------------------------------
# Reddit Adapter Tests
# -------------------------------------------------------------
def test_reddit_adapter(monkeypatch):
    monkeypatch.setenv("REDDIT_CLIENT_ID", "client123")
    monkeypatch.setenv("REDDIT_CLIENT_SECRET", "secret456")
    monkeypatch.setenv("REDDIT_USERNAME", "omni_bot")
    monkeypatch.setenv("REDDIT_PASSWORD", "pass789")
    monkeypatch.setenv("REDDIT_DEFAULT_SUBREDDIT", "SideProject")
    adapter = RedditPublisherAdapter()
    assert adapter.is_configured() is True

    with patch("requests.post") as mock_post:
        # 1st call: Token request, 2nd call: Submit request
        token_resp = MagicMock()
        token_resp.status_code = 200
        token_resp.json.return_value = {"access_token": "mock_token_abc"}

        submit_resp = MagicMock()
        submit_resp.status_code = 200
        submit_resp.json.return_value = {
            "json": {
                "errors": [],
                "data": {"url": "https://reddit.com/r/SideProject/comments/123/post"}
            }
        }
        mock_post.side_effect = [token_resp, submit_resp]

        res = adapter.queue_social_post(
            title="Show HN: OmniPress MCP",
            text="Agnostic publishing engine for AI agents",
            platforms=["reddit"]
        )
        assert res["success"] is True
        assert "reddit.com" in res["url"]


# -------------------------------------------------------------
# YouTube Staging Adapter Tests
# -------------------------------------------------------------
def test_youtube_staging_adapter(tmp_path: Path):
    adapter = YouTubeStagingAdapter(base_dir=str(tmp_path))

    # Test short formatting
    res = adapter.stage_video(
        title="O Segredo de Derinkuyu",
        description="Descrição completa do vídeo",
        tags=["historia", "arqueologia"],
        is_short=True,
    )
    assert Path(res["filepath"]).exists()
    assert "#Shorts" in res["manifest"]["title"]
    assert res["manifest"]["platform"] == "youtube_shorts"
    assert "historia" in res["manifest"]["tags"]


# -------------------------------------------------------------
# Instagram Graph Adapter Tests
# -------------------------------------------------------------
def test_instagram_adapter_without_media(monkeypatch):
    monkeypatch.setenv("INSTAGRAM_ACCESS_TOKEN", "token_insta")
    monkeypatch.setenv("INSTAGRAM_ACCOUNT_ID", "acc_insta_1")
    adapter = InstagramGraphAdapter()
    assert adapter.is_configured() is True

    res = adapter.queue_social_post("Post sem foto", ["instagram"], media_urls=[])
    assert res["success"] is False
    assert "requires at least one media" in res["error"]


def test_instagram_adapter_publish_carousel(monkeypatch):
    monkeypatch.setenv("INSTAGRAM_ACCESS_TOKEN", "token_insta")
    monkeypatch.setenv("INSTAGRAM_ACCOUNT_ID", "acc_insta_1")
    adapter = InstagramGraphAdapter()

    with patch("requests.post") as mock_post:
        # Mock item container 1, item container 2, carousel container, and publish
        resp_item1 = MagicMock(status_code=200)
        resp_item1.json.return_value = {"id": "item_1"}

        resp_item2 = MagicMock(status_code=200)
        resp_item2.json.return_value = {"id": "item_2"}

        resp_carous = MagicMock(status_code=200)
        resp_carous.json.return_value = {"id": "carous_99"}

        resp_pub = MagicMock(status_code=200)
        resp_pub.json.return_value = {"id": "media_published_100"}

        mock_post.side_effect = [resp_item1, resp_item2, resp_carous, resp_pub]

        res = adapter.queue_social_post(
            text="Legenda do carrossel no Instagram",
            platforms=["instagram"],
            media_urls=["https://example.com/img1.jpg", "https://example.com/img2.jpg"]
        )
        assert res["success"] is True
        assert res["post_id"] == "media_published_100"
        assert res["media_count"] == 2


def test_instagram_channel_scoped_credentials(monkeypatch):
    """Verify InstagramGraphAdapter resolves credentials via ChannelManager."""
    monkeypatch.delenv("INSTAGRAM_ACCESS_TOKEN", raising=False)
    monkeypatch.delenv("INSTAGRAM_ACCOUNT_ID", raising=False)
    monkeypatch.delenv("INSTAGRAM_BUSINESS_ACCOUNT_ID", raising=False)
    adapter = InstagramGraphAdapter()
    assert adapter.is_configured() is False

    def mock_get_cred(key, slug):
        if key == "INSTAGRAM_ACCESS_TOKEN":
            return "channel_ig_token_123"
        if key in ("INSTAGRAM_ACCOUNT_ID", "INSTAGRAM_BUSINESS_ACCOUNT_ID"):
            return "channel_ig_acct_456"
        return ""

    with patch("src.core.channel_manager.ChannelManager.get_credential", side_effect=mock_get_cred):
        assert adapter.is_configured(channel_slug="my-channel") is True
        token, acct = adapter.get_credentials(channel_slug="my-channel")
        assert token == "channel_ig_token_123"
        assert acct == "channel_ig_acct_456"


def test_reddit_channel_scoped_credentials(monkeypatch):
    """Verify RedditPublisherAdapter resolves credentials via ChannelManager."""
    monkeypatch.delenv("REDDIT_CLIENT_ID", raising=False)
    monkeypatch.delenv("REDDIT_CLIENT_SECRET", raising=False)
    monkeypatch.delenv("REDDIT_USERNAME", raising=False)
    monkeypatch.delenv("REDDIT_PASSWORD", raising=False)
    adapter = RedditPublisherAdapter()
    assert adapter.is_configured() is False

    def mock_get_cred(key, slug):
        return f"ch_{key.lower()}"

    with patch("src.core.channel_manager.ChannelManager.get_credential", side_effect=mock_get_cred):
        assert adapter.is_configured(channel_slug="my-channel") is True
        cid, csec, uname, pwd = adapter.get_credentials(channel_slug="my-channel")
        assert cid == "ch_reddit_client_id"
        assert csec == "ch_reddit_client_secret"
        assert uname == "ch_reddit_username"
        assert pwd == "ch_reddit_password"


if __name__ == "__main__":
    import pytest
    import sys
    sys.exit(pytest.main([__file__, "-v"]))
