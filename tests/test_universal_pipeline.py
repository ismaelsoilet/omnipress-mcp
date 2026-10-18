"""Unit tests for OmniPress Universal Execution Engines and Declarative Recipes (v0.3.0)."""

import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch
from PIL import Image
import pytest

from src.core.channel_manager import ChannelManager
from src.core.publishing_shield import PublishingShield
from src.engine.universal_carousel import UniversalCarouselEngine
from src.engine.universal_audio import UniversalAudioEngine
from src.engine.universal_captions import UniversalCaptionsEngine
from src.engine.universal_publisher import UniversalPublisherEngine
from src.utils.storage import BaseStorageProvider


class MockStorageProvider(BaseStorageProvider):
    """Mock storage provider returning simulated public CDN URLs."""
    def upload_file(self, file_path: Path, remote_name=None) -> str:
        return f"https://cdn.omnipress.mock/{file_path.name}"


@pytest.fixture
def temp_workspace():
    """Sets up a temporary channel workspace for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        ch_dir = root / "channels" / "test-channel"
        ch_dir.mkdir(parents=True, exist_ok=True)
        (ch_dir / "media" / "carousels").mkdir(parents=True, exist_ok=True)
        (ch_dir / "media" / "raw").mkdir(parents=True, exist_ok=True)

        channel_json = {
            "id": "test-channel",
            "slug": "test-channel",
            "name": "Test Channel",
            "branding": {
                "theme_colors": {"primary": "#3B82F6"},
                "handle": "@testchannel",
                "badge_text": "TEST • BADGE",
            },
        }
        (ch_dir / "channel.json").write_text(json.dumps(channel_json), encoding="utf-8")

        # Create a dummy background image
        bg_path = ch_dir / "media" / "raw" / "bg_test.jpg"
        img = Image.new("RGB", (1200, 1600), color=(100, 150, 200))
        img.save(bg_path, "JPEG")

        cm = ChannelManager(root_dir=root)
        yield {
            "root": root,
            "cm": cm,
            "channel_slug": "test-channel",
            "bg_path": bg_path,
            "ch_dir": ch_dir,
        }


# ==========================================
# 1. Universal Carousel Engine Tests
# ==========================================

def test_carousel_prepare_background(temp_workspace):
    engine = UniversalCarouselEngine(channel_manager=temp_workspace["cm"])
    src_bg = temp_workspace["bg_path"]
    dst_bg = temp_workspace["ch_dir"] / "prepared.jpg"

    engine.prepare_background(
        src_path=src_bg,
        dst_path=dst_bg,
        aspect_ratio="3:4",
        top_bias=0.20,
        contrast_boost=1.15,
    )

    assert dst_bg.exists()
    with Image.open(dst_bg) as img:
        assert img.size == (1080, 1440)


def test_carousel_execute_recipe(temp_workspace):
    storage = MockStorageProvider()
    engine = UniversalCarouselEngine(
        channel_manager=temp_workspace["cm"],
        storage_provider=storage,
    )

    recipe = {
        "channel_slug": temp_workspace["channel_slug"],
        "post_slug": "post_unit_test",
        "aspect_ratio": "3:4",
        "slides": [
            {
                "headline": "TEST SLIDE ONE",
                "body": "First test slide body.",
                "badge_text": "BADGE 1",
                "bg_image": str(temp_workspace["bg_path"]),
            },
            {
                "headline": "TEST SLIDE TWO",
                "body": "Second test slide body.",
                "badge_text": "BADGE 2",
                "bg_image": str(temp_workspace["bg_path"]),
            },
        ],
        "publish": {
            "caption": "Test publication caption for social post.",
            "platforms": ["instagram"],
        },
    }

    result = engine.execute_recipe(recipe, render=True, upload=True, schedule=False)

    assert len(result["rendered_slides"]) == 2
    for s in result["rendered_slides"]:
        assert Path(s).exists()

    assert len(result["cdn_urls"]) == 2
    assert "https://cdn.omnipress.mock/slide_01.jpg" in result["cdn_urls"]


# ==========================================
# 2. Universal Audio Engine Tests
# ==========================================

def test_audio_filtergraph_rule10_compliance():
    engine = UniversalAudioEngine(ffmpeg_bin="ffmpeg")
    fg = engine.build_mastering_filtergraph(target_lufs=-14.0)

    # Verify all 6 mandatory stages from Rule 10
    assert "adeclick=" in fg
    assert "highpass=f=80" in fg
    assert "afftdn=" in fg
    assert "equalizer=f=320" in fg
    assert "equalizer=f=2800" in fg
    assert "acompressor=" in fg
    assert "loudnorm=I=-14.0:LRA=7:TP=-1.2" in fg


def test_audio_mastering_nonexistent_file():
    engine = UniversalAudioEngine()
    with pytest.raises(FileNotFoundError):
        engine.master_voiceover("nonexistent_voice.m4a", "out.mp3")


# ==========================================
# 3. Universal Captions Engine Tests
# ==========================================

def test_captions_whisper_parsing_and_chunking(tmp_path):
    whisper_raw = {
        "words": [
            {"word": "No", "start": 0.1, "end": 0.3},
            {"word": "início", "start": 0.32, "end": 0.7},
            {"word": "da", "start": 0.72, "end": 0.9},
            {"word": "Guerra", "start": 0.95, "end": 1.4},
            {"word": "Fria,", "start": 1.45, "end": 1.8},
            {"word": "a", "start": 2.0, "end": 2.1},
            {"word": "CIA", "start": 2.15, "end": 2.5},
            {"word": "criou", "start": 2.55, "end": 2.9},
            {"word": "gatos", "start": 2.95, "end": 3.4},
            {"word": "espiões.", "start": 3.45, "end": 3.9},
        ]
    }

    engine = UniversalCaptionsEngine()
    words = engine.parse_raw_whisper(whisper_raw)
    assert len(words) == 10
    assert words[0]["word"] == "No"

    chunks = engine.chunk_words_for_shorts(words, words_per_chunk=3, uppercase=True)
    assert len(chunks) >= 3
    # First chunk text uppercase
    assert "NO INÍCIO DA" in chunks[0]["text"]

    out_json = tmp_path / "captions_out.json"
    res = engine.process_and_export(whisper_raw, out_json)
    assert res["success"] is True
    assert out_json.exists()


# ==========================================
# 4. Universal Publisher Engine Tests
# ==========================================

def test_publisher_validation_and_sanitization():
    engine = UniversalPublisherEngine()

    # Test character limit validation
    long_text = "A" * 2250
    cleaned, errors = engine.validate_content(long_text, platforms=["instagram"])
    assert len(errors) == 1
    assert "exceeds instagram limit" in errors[0].lower()

    # Test sanitization (Rule 01)
    text_with_cpf = "Post sobre o caso do réu CPF: 123.456.789-00 em segredo."
    cleaned, errors = engine.validate_content(text_with_cpf, platforms=["instagram"])
    assert "123.456.789-00" not in cleaned
    assert "[CPF PROTEGIDO]" in cleaned or "[DADO PROTEGIDO]" in cleaned or "***" in cleaned or "PROTEGIDO" in cleaned


def test_publisher_dry_run_and_duplicate_check(temp_workspace):
    engine = UniversalPublisherEngine(channel_manager=temp_workspace["cm"])

    # Dry-run execution
    res = engine.publish_social_post(
        channel_slug=temp_workspace["channel_slug"],
        text="Unique post caption for dry-run verification.",
        platforms=["instagram"],
        dry_run=True,
    )
    assert res["success"] is True
    assert res["dry_run"] is True

    # Pre-flight duplicate protection check
    with patch.object(PublishingShield, "check_duplicate", return_value=(True, "Duplicate content detected in ledger")):
        res_dup = engine.publish_social_post(
            channel_slug=temp_workspace["channel_slug"],
            text="Same content",
            platforms=["instagram"],
            dry_run=False,
            force_duplicate=False,
        )
        assert res_dup["success"] is False
        assert "duplicate" in res_dup["error"].lower()
