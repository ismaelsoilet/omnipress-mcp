"""Unit tests for OmniPress Publishing Shield (Safety Gates & Rule 09 Anti-Duplicate Ledger)."""

import pytest
import time
from unittest.mock import patch, MagicMock
from pathlib import Path

from src.core.publishing_shield import PublishingShield, PLATFORM_CHAR_LIMITS
from src.adapters.buffer_adapter import BufferPublisherAdapter
from src.adapters.instagram_adapter import InstagramGraphAdapter


@pytest.fixture
def temp_ledger(tmp_path, monkeypatch):
    """Isolates tests with a clean temporary ledger file."""
    test_ledger_path = tmp_path / "test_publishing_ledger.json"
    monkeypatch.setattr(PublishingShield, "get_ledger_path", classmethod(lambda cls: test_ledger_path))
    return test_ledger_path


class TestPublishingShieldGates:
    """Tests the 4 pre-flight safety gates of PublishingShield."""

    def test_gate1_placeholder_test_text_blocked(self):
        """Live shareNow posts with dummy/placeholder test words must be intercepted."""
        test_strings = ["teste", "test", "testing", "asdf", "hello world", "foo", "post de teste", "ola mundo"]
        for dummy in test_strings:
            is_valid, err = PublishingShield.validate_post(
                text=dummy,
                platforms=["instagram"],
                media_urls=["https://files.catbox.moe/slide1.jpg"],
                mode="shareNow",
                allow_test=False,
            )
            assert not is_valid, f"Expected '{dummy}' to be blocked on shareNow"
            assert "Placeholder/test text" in err

        # Short strings under 12 characters are also intercepted on shareNow
        is_valid, err = PublishingShield.validate_post(
            text="oi gente",
            platforms=["instagram"],
            media_urls=["https://files.catbox.moe/slide1.jpg"],
            mode="shareNow",
            allow_test=False,
        )
        assert not is_valid
        assert "Placeholder/test text" in err

    def test_gate1_allow_test_flag_bypasses(self):
        """When allow_test=True, explicit test scripts are permitted."""
        is_valid, err = PublishingShield.validate_post(
            text="teste",
            platforms=["instagram"],
            media_urls=["https://files.catbox.moe/slide1.jpg"],
            mode="shareNow",
            allow_test=True,
        )
        assert is_valid
        assert err is None

    def test_gate2_instagram_media_requirement(self):
        """Instagram strictly requires at least one media URL."""
        # Without media on Instagram -> blocked
        is_valid, err = PublishingShield.validate_post(
            text="Um post perfeitamente estruturado e detalhado sobre história.",
            platforms=["instagram"],
            media_urls=None,
            mode="shareNow",
        )
        assert not is_valid
        assert "Instagram strictly requires at least one media URL" in err

        # With media on Instagram -> valid
        is_valid, err = PublishingShield.validate_post(
            text="Um post perfeitamente estruturado e detalhado sobre história.",
            platforms=["instagram"],
            media_urls=["https://files.catbox.moe/image.jpg"],
            mode="shareNow",
        )
        assert is_valid
        assert err is None

        # Text-only on LinkedIn or X -> valid (media is optional)
        is_valid, err = PublishingShield.validate_post(
            text="Um post perfeitamente estruturado e detalhado sobre engenharia de software.",
            platforms=["linkedin", "x"],
            media_urls=None,
            mode="shareNow",
        )
        assert is_valid

    def test_gate3_instagram_character_limit(self):
        """Instagram caption cannot exceed 2,196 characters (Buffer cutoff)."""
        limit = PLATFORM_CHAR_LIMITS["instagram"]
        assert limit == 2196

        valid_text = "A" * 2190
        is_valid, err = PublishingShield.validate_post(
            text=valid_text,
            platforms=["instagram"],
            media_urls=["https://files.catbox.moe/image.jpg"],
        )
        assert is_valid

        excessive_text = "A" * 2250
        is_valid, err = PublishingShield.validate_post(
            text=excessive_text,
            platforms=["instagram"],
            media_urls=["https://files.catbox.moe/image.jpg"],
        )
        assert not is_valid
        assert "exceeds maximum allowed length for INSTAGRAM: 2250 characters (limit: 2196)" in err
        assert "54 character(s)" in err

    def test_gate3_x_character_limit(self):
        """X/Twitter posts cannot exceed 280 characters."""
        valid_text = "A" * 280
        is_valid, err = PublishingShield.validate_post(
            text=valid_text,
            platforms=["x"],
        )
        assert is_valid

        excessive_text = "A" * 281
        is_valid, err = PublishingShield.validate_post(
            text=excessive_text,
            platforms=["x"],
        )
        assert not is_valid
        assert "exceeds maximum allowed length for X" in err

    def test_gate3_threads_character_limit(self):
        """Threads posts cannot exceed 500 characters."""
        valid_text = "A" * 500
        is_valid, err = PublishingShield.validate_post(
            text=valid_text,
            platforms=["threads"],
        )
        assert is_valid

        excessive_text = "A" * 501
        is_valid, err = PublishingShield.validate_post(
            text=excessive_text,
            platforms=["threads"],
        )
        assert not is_valid
        assert "exceeds maximum allowed length for THREADS" in err


class TestPublishingShieldLedger:
    """Tests the Rule 09 anti-duplicate idempotency ledger."""

    def test_fingerprint_generation_deterministic(self):
        ch = "channel_123"
        text1 = "Operação Prato: o segredo de 1977 desclassificado pela Aeronáutica."
        text2 = "OPERAÇÃO PRATO:   o segredo de 1977 desclassificado pela aeronáutica."
        media = ["https://files.catbox.moe/slide1.jpg", "https://files.catbox.moe/slide2.jpg"]

        fp1 = PublishingShield.generate_fingerprint(ch, text1, media)
        fp2 = PublishingShield.generate_fingerprint(ch, text2, list(reversed(media)))
        assert fp1 == fp2, "Fingerprint must be case-insensitive and order-agnostic for media"

        different_text = "Outro caso histórico totalmente diferente."
        fp3 = PublishingShield.generate_fingerprint(ch, different_text, media)
        assert fp1 != fp3

    def test_duplicate_prevention_flow(self, temp_ledger):
        ch = "channel_test_456"
        text = "Post exclusivo sobre documentos da FAB em Colares/PA."
        media = ["https://catbox.moe/s1.jpg"]

        # Step 1: Check before publishing -> not duplicate
        is_dup, err = PublishingShield.check_duplicate(ch, text, media)
        assert not is_dup
        assert err is None

        # Step 2: Record post publication in ledger
        PublishingShield.record_published(ch, text, media, post_id="post_999", provider="buffer_graphql")

        # Step 3: Check again -> blocked duplicate!
        is_dup, err = PublishingShield.check_duplicate(ch, text, media)
        assert is_dup
        assert "🛡️ Shield Block (Rule 09 Exactly-Once)" in err
        assert "post_999" in err

        # Step 4: With force=True -> bypassed
        is_dup, err = PublishingShield.check_duplicate(ch, text, media, force=True)
        assert not is_dup

        # Step 5: If deleted via delete_post -> entry removed, publishing allowed again
        PublishingShield.remove_entry("post_999")
        is_dup, err = PublishingShield.check_duplicate(ch, text, media)
        assert not is_dup


class TestAdapterShieldIntegration:
    """Verifies that adapters invoke PublishingShield and reject forbidden posts before network calls."""

    @patch("requests.post")
    def test_buffer_adapter_rejects_test_text_before_http(self, mock_post, monkeypatch, temp_ledger):
        monkeypatch.setenv("BUFFER_API_KEY", "mock_key")
        monkeypatch.setenv("BUFFER_INSTAGRAM_PROFILE_ID", "mock_ig_channel")

        adapter = BufferPublisherAdapter()
        res = adapter.queue_social_post(
            text="teste",
            platforms=["instagram"],
            media_urls=["https://files.catbox.moe/slide.jpg"],
            mode="shareNow",
        )

        assert not res["success"]
        assert res["provider"] == "publishing_shield"
        assert "Placeholder/test text" in res["error"]
        # Network request was never made!
        mock_post.assert_not_called()

    @patch("requests.post")
    def test_buffer_adapter_rejects_oversized_instagram_caption_before_http(self, mock_post, monkeypatch, temp_ledger):
        monkeypatch.setenv("BUFFER_API_KEY", "mock_key")
        monkeypatch.setenv("BUFFER_INSTAGRAM_PROFILE_ID", "mock_ig_channel")

        adapter = BufferPublisherAdapter()
        oversized = "B" * 2200
        res = adapter.queue_social_post(
            text=oversized,
            platforms=["instagram"],
            media_urls=["https://files.catbox.moe/slide.jpg"],
            mode="shareNow",
        )

        assert not res["success"]
        assert res["provider"] == "publishing_shield"
        assert "exceeds maximum allowed length for INSTAGRAM" in res["error"]
        mock_post.assert_not_called()

    @patch("requests.post")
    def test_buffer_adapter_blocks_duplicate_before_http(self, mock_post, monkeypatch, temp_ledger):
        monkeypatch.setenv("BUFFER_API_KEY", "mock_key")
        monkeypatch.setenv("BUFFER_INSTAGRAM_PROFILE_ID", "mock_ig_channel")

        adapter = BufferPublisherAdapter()
        text = "Post legítimo sobre a Operação Prato de 1977 com documentação real."
        media = ["https://files.catbox.moe/slide1.jpg"]

        # Pre-seed ledger
        PublishingShield.record_published("mock_ig_channel", text, media, post_id="existing_post_1")

        # Attempt to post duplicate
        res = adapter.queue_social_post(
            text=text,
            platforms=["instagram"],
            media_urls=media,
            mode="shareNow",
        )

        assert not res["success"]
        assert res["provider"] == "publishing_shield"
        assert "Exactly-Once" in res["error"]
        mock_post.assert_not_called()

    @patch("requests.post")
    def test_instagram_adapter_rejects_placeholder_text_before_http(self, mock_post, monkeypatch, temp_ledger):
        monkeypatch.setenv("INSTAGRAM_ACCESS_TOKEN", "mock_ig_token")
        monkeypatch.setenv("INSTAGRAM_ACCOUNT_ID", "mock_ig_acc")

        adapter = InstagramGraphAdapter()
        res = adapter.queue_social_post(
            text="teste",
            platforms=["instagram"],
            media_urls=["https://files.catbox.moe/slide.jpg"],
            mode="shareNow",
        )

        assert not res["success"]
        assert res["provider"] == "publishing_shield"
        assert "Placeholder/test text" in res["error"]
        mock_post.assert_not_called()
