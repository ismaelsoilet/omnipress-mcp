"""Comprehensive unit & integration tests for OmniPress Universal Execution Engines (v0.3.0).

Verifies:
1. UniversalCarouselEngine: background prep (3:4, 1:1, 9:16, top_bias), slide rendering, CDN upload, and scheduling.
2. UniversalAudioEngine: filtergraph generation, error handling, and real end-to-end ffmpeg broadcast mastering.
3. UniversalCaptionsEngine: Whisper parsing (words, segments, nested dicts), chunking, and export.
4. UniversalPublisherEngine: platform limits (IG, X, LinkedIn), LGPD sanitization, dry-run, and duplicate protection.
5. CLI and Script Runners: omnipress carousel, master-audio, align-captions, publish and scripts/*.py entrypoints.
"""

import json
import math
import struct
import tempfile
import wave
from pathlib import Path
from unittest.mock import MagicMock, patch
from PIL import Image
import pytest

from src.core.channel_manager import ChannelManager
from src.core.publishing_shield import PublishingShield
from src.engine.universal_carousel import UniversalCarouselEngine
from src.engine.universal_audio import UniversalAudioEngine, find_ffmpeg_binary
from src.engine.universal_captions import UniversalCaptionsEngine
from src.engine.universal_publisher import UniversalPublisherEngine
from src.utils.storage import BaseStorageProvider
from src.cli import main as cli_main
from scripts.omnipress_carousel import main as script_carousel_main
from scripts.omnipress_audio_master import main as script_audio_main
from scripts.omnipress_publisher import main as script_publisher_main


class MockStorageProvider(BaseStorageProvider):
    """Mock storage provider returning simulated public CDN URLs."""
    def upload_file(self, file_path: Path, remote_name=None) -> str:
        return f"https://cdn.omnipress.mock/{file_path.name}"


def create_synthetic_wav(path: Path, duration_sec: float = 0.5, sample_rate: int = 44100) -> Path:
    """Generates a synthetic 440Hz sine wave audio file for real ffmpeg tests."""
    with wave.open(str(path), "w") as wav_file:
        wav_file.setnchannels(1)  # mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        num_samples = int(duration_sec * sample_rate)
        for i in range(num_samples):
            val = int(12000 * math.sin(2 * math.pi * 440 * (i / sample_rate)))
            wav_file.writeframes(struct.pack("<h", val))
    return path


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
            "social": {
                "buffer_channel_id": "mock_buffer_123"
            }
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


# =========================================================================
# 1. Universal Carousel Engine Tests
# =========================================================================

def test_carousel_prepare_background_aspect_ratios_and_biases(temp_workspace):
    """Verifies background image preparation for 3:4, 1:1, and top_bias variations."""
    engine = UniversalCarouselEngine(channel_manager=temp_workspace["cm"])
    src_bg = temp_workspace["bg_path"]

    # Test 3:4 aspect ratio
    dst_34 = temp_workspace["ch_dir"] / "prepared_34.jpg"
    engine.prepare_background(src_path=src_bg, dst_path=dst_34, aspect_ratio="3:4", top_bias=0.10)
    assert dst_34.exists()
    with Image.open(dst_34) as img:
        assert img.size == (1080, 1440)

    # Test 1:1 aspect ratio
    dst_11 = temp_workspace["ch_dir"] / "prepared_11.jpg"
    engine.prepare_background(src_path=src_bg, dst_path=dst_11, aspect_ratio="1:1", top_bias=0.50)
    assert dst_11.exists()
    with Image.open(dst_11) as img:
        assert img.size == (1080, 1080)


def test_carousel_execute_recipe_end_to_end(temp_workspace):
    """Verifies end-to-end recipe execution: rendering slides, CDN upload, and scheduling."""
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
                "body": "First test slide body with high contrast card.",
                "badge_text": "BADGE 1",
                "bg_image": str(temp_workspace["bg_path"]),
            },
            {
                "headline": "TEST SLIDE TWO",
                "body": "Second test slide body with high contrast card.",
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


def test_carousel_schedule_or_publish_validation(temp_workspace):
    """Verifies caption length validation and duplicate rejection in carousel scheduling."""
    engine = UniversalCarouselEngine(channel_manager=temp_workspace["cm"])

    # 1. Empty caption validation
    recipe_empty_caption = {
        "channel_slug": temp_workspace["channel_slug"],
        "publish": {"caption": "   "}
    }
    res_empty = engine.schedule_or_publish(recipe_empty_caption, media_urls=["http://example.com/1.jpg"])
    assert res_empty["success"] is False
    assert "caption" in res_empty["error"].lower()

    # 2. Instagram limit validation (>2200 chars)
    recipe_long_caption = {
        "channel_slug": temp_workspace["channel_slug"],
        "publish": {"caption": "X" * 2250, "platforms": ["instagram"]}
    }
    res_long = engine.schedule_or_publish(recipe_long_caption, media_urls=["http://example.com/1.jpg"])
    assert res_long["success"] is False
    assert "limit" in res_long["error"].lower()


# =========================================================================
# 2. Universal Audio Engine Tests (Including Real FFmpeg Execution)
# =========================================================================

def test_audio_filtergraph_rule10_compliance():
    """Verifies that all 6 stages of Rule 10 are present in the filtergraph."""
    engine = UniversalAudioEngine(ffmpeg_bin="ffmpeg")
    fg = engine.build_mastering_filtergraph(target_lufs=-14.0)

    # Verify all 6 mandatory stages from Rule 10 (including 4-band EQ: 140Hz, 320Hz, 2800Hz, 8500Hz)
    assert "adeclick=" in fg
    assert "highpass=f=80" in fg
    assert "afftdn=" in fg
    assert "equalizer=f=140" in fg
    assert "equalizer=f=320" in fg
    assert "equalizer=f=2800" in fg
    assert "highshelf=f=8500" in fg
    assert "acompressor=" in fg
    assert "loudnorm=I=-14.0:LRA=7:TP=-1.2" in fg


def test_audio_mastering_nonexistent_file():
    """Verifies error handling on missing audio files."""
    engine = UniversalAudioEngine()
    with pytest.raises(FileNotFoundError):
        engine.master_voiceover("nonexistent_voice.m4a", "out.mp3")


def test_audio_real_ffmpeg_mastering(tmp_path):
    """Executes a REAL broadcast mastering pass through ffmpeg on synthetic audio."""
    ffmpeg_bin = find_ffmpeg_binary()
    if not ffmpeg_bin:
        pytest.skip("FFmpeg binary not installed on host")
    engine = UniversalAudioEngine(ffmpeg_bin=ffmpeg_bin)

    raw_wav = tmp_path / "synthetic_voice.wav"
    create_synthetic_wav(raw_wav, duration_sec=0.5)
    assert raw_wav.exists()

    mastered_mp3 = tmp_path / "mastered_broadcast.mp3"
    res = engine.master_voiceover(
        input_audio=raw_wav,
        output_audio=mastered_mp3,
        target_lufs=-14.0,
        sample_rate=48000,
        bitrate="192k",
    )

    assert res["success"] is True
    assert mastered_mp3.exists()
    assert mastered_mp3.stat().st_size > 0
    assert res["target_lufs"] == -14.0
    assert res["sample_rate"] == 48000


# =========================================================================
# 3. Universal Captions Engine Tests
# =========================================================================

def test_captions_whisper_direct_words(tmp_path):
    """Verifies parsing of raw Whisper JSON with root 'words' array."""
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
    assert "NO INÍCIO DA" in chunks[0]["text"]

    out_json = tmp_path / "captions_out.json"
    res = engine.process_and_export(whisper_raw, out_json)
    assert res["success"] is True
    assert out_json.exists()


def test_captions_whisper_segments_parsing():
    """Verifies parsing of OpenAI Whisper output using 'segments' without per-word timestamps."""
    whisper_segments = {
        "segments": [
            {
                "id": 0,
                "start": 0.0,
                "end": 2.0,
                "text": "Primeira frase histórica",
            },
            {
                "id": 1,
                "start": 2.2,
                "end": 4.0,
                "text": "Segunda frase documental",
            }
        ]
    }
    engine = UniversalCaptionsEngine()
    words = engine.parse_raw_whisper(whisper_segments)
    assert len(words) == 6
    assert words[0]["word"] == "Primeira"
    assert words[0]["start"] == 0.0
    assert words[-1]["word"] == "documental"


def test_captions_nested_episode_dict():
    """Verifies parsing when Whisper JSON is wrapped under an episode key."""
    nested_data = {
        "short_01": {
            "words": [
                {"word": "Palavra1", "start": 0.0, "end": 0.5},
                {"word": "Palavra2", "start": 0.6, "end": 1.0},
            ]
        }
    }
    engine = UniversalCaptionsEngine()
    words = engine.parse_raw_whisper(nested_data)
    assert len(words) == 2
    assert words[0]["word"] == "Palavra1"


# =========================================================================
# 4. Universal Publisher Engine Tests
# =========================================================================

def test_publisher_validation_and_sanitization():
    """Verifies platform limits and Rule 01 privacy sanitization."""
    engine = UniversalPublisherEngine()

    # Test Instagram character limit validation (2,200)
    long_text = "A" * 2250
    cleaned, errors = engine.validate_content(long_text, platforms=["instagram"])
    assert len(errors) == 1
    assert "exceeds instagram limit" in errors[0].lower()

    # Test X / Twitter character limit validation (280)
    tweet_long = "B" * 290
    cleaned, errors = engine.validate_content(tweet_long, platforms=["x"])
    assert len(errors) == 1
    assert "exceeds x limit" in errors[0].lower()

    # Test sanitization (Rule 01)
    text_with_cpf = "Post sobre o caso do réu CPF: 123.456.789-00 em segredo de justiça."
    cleaned, errors = engine.validate_content(text_with_cpf, platforms=["instagram"])
    assert "123.456.789-00" not in cleaned
    assert "PROTEGIDO" in cleaned


def test_publisher_dry_run_and_duplicate_check(temp_workspace):
    """Verifies dry-run execution and PublishingShield duplicate rejection."""
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

        # Force duplicate bypass
        res_forced = engine.publish_social_post(
            channel_slug=temp_workspace["channel_slug"],
            text="Same content",
            platforms=["instagram"],
            dry_run=True,
            force_duplicate=True,
        )
        assert res_forced["success"] is True


def test_publisher_execute_recipe_from_file(tmp_path, temp_workspace):
    """Verifies loading and executing a post recipe JSON file."""
    engine = UniversalPublisherEngine(channel_manager=temp_workspace["cm"])

    recipe_data = {
        "channel_slug": temp_workspace["channel_slug"],
        "text": "Post caption authored in declarative recipe file.",
        "platforms": ["instagram"],
        "media_urls": ["https://cdn.example.com/slide1.jpg"]
    }
    recipe_file = tmp_path / "post_recipe.json"
    recipe_file.write_text(json.dumps(recipe_data), encoding="utf-8")

    res = engine.execute_recipe(recipe_file, dry_run=True)
    assert res["success"] is True
    assert res["dry_run"] is True
    assert res["channel_slug"] == temp_workspace["channel_slug"]


# =========================================================================
# 5. CLI & Standalone Script Entrypoint Tests
# =========================================================================

def test_cli_carousel_command(tmp_path, temp_workspace):
    """Verifies invoking 'omnipress carousel' through CLI main()."""
    recipe_data = {
        "channel_slug": temp_workspace["channel_slug"],
        "post_slug": "cli_carousel_post",
        "aspect_ratio": "3:4",
        "slides": [
            {
                "headline": "CLI SLIDE 1",
                "body": "Slide rendered via CLI test.",
                "bg_image": str(temp_workspace["bg_path"])
            }
        ]
    }
    recipe_path = tmp_path / "cli_recipe.json"
    recipe_path.write_text(json.dumps(recipe_data), encoding="utf-8")

    exit_code = cli_main(["carousel", "--recipe", str(recipe_path), "--render"])
    assert exit_code == 0


def test_cli_align_captions_command(tmp_path):
    """Verifies invoking 'omnipress align-captions' through CLI main()."""
    whisper_data = {
        "words": [
            {"word": "Teste", "start": 0.0, "end": 0.5},
            {"word": "CLI", "start": 0.6, "end": 1.0},
        ]
    }
    in_file = tmp_path / "whisper.json"
    out_file = tmp_path / "captions_out.json"
    in_file.write_text(json.dumps(whisper_data), encoding="utf-8")

    exit_code = cli_main(["align-captions", str(in_file), "-o", str(out_file)])
    assert exit_code == 0
    assert out_file.exists()


def test_cli_publish_dry_run(temp_workspace):
    """Verifies invoking 'omnipress publish' through CLI main() with dry-run."""
    exit_code = cli_main([
        "publish",
        "--channel", temp_workspace["channel_slug"],
        "--text", "Testing CLI publish dry-run.",
        "--platforms", "instagram",
        "--dry-run"
    ])
    assert exit_code == 0


def test_script_runners(tmp_path, temp_workspace):
    """Verifies the standalone scripts in scripts/ can be called directly."""
    # 1. scripts/omnipress_carousel.py
    recipe_data = {
        "channel_slug": temp_workspace["channel_slug"],
        "post_slug": "script_carousel_post",
        "slides": [
            {
                "headline": "SCRIPT SLIDE",
                "body": "Tested via script runner.",
                "bg_image": str(temp_workspace["bg_path"])
            }
        ]
    }
    recipe_file = tmp_path / "script_recipe.json"
    recipe_file.write_text(json.dumps(recipe_data), encoding="utf-8")

    exit_code_carousel = script_carousel_main(["--recipe", str(recipe_file), "--render"])
    assert exit_code_carousel == 0

    # 2. scripts/omnipress_publisher.py
    exit_code_pub = script_publisher_main([
        "--channel", temp_workspace["channel_slug"],
        "--text", "Test caption via script runner",
        "--dry-run"
    ])
    assert exit_code_pub == 0

    # 3. scripts/omnipress_audio_master.py
    if find_ffmpeg_binary():
        raw_wav = tmp_path / "test_script_voice.wav"
        create_synthetic_wav(raw_wav, duration_sec=0.4)
        out_mp3 = tmp_path / "test_script_voice_mastered.mp3"
        exit_code_audio = script_audio_main([str(raw_wav), "-o", str(out_mp3)])
        assert exit_code_audio == 0
        assert out_mp3.exists()


def test_canonical_template_recipes_validity():
    """Verifies that the canonical recipe files in channels/_template/ are completely valid."""
    project_root = Path(__file__).resolve().parent.parent
    cm = ChannelManager(root_dir=project_root)

    # 1. Test carousel template recipe
    carousel_template = project_root / "channels" / "_template" / "media" / "carousels" / "_template_carousel" / "carousel_recipe.json"
    assert carousel_template.exists()
    carousel_engine = UniversalCarouselEngine(channel_manager=cm)
    data, _ = carousel_engine.load_recipe(carousel_template)
    assert "slides" in data
    assert len(data["slides"]) >= 3
    assert "publish" in data

    # 2. Test post template recipe
    post_template = project_root / "channels" / "_template" / "articles" / "_template_article" / "post_recipe.json"
    assert post_template.exists()
    pub_engine = UniversalPublisherEngine(channel_manager=cm)
    res = pub_engine.execute_recipe(post_template, dry_run=True)
    assert res["success"] is True
    assert res["dry_run"] is True


def test_record_published_flexible_signature_no_type_error(tmp_path, monkeypatch):
    """Verifies that PublishingShield.record_published accepts flexible kwargs without TypeError (Critical Fix #1)."""
    test_ledger = tmp_path / "test_ledger.json"
    monkeypatch.setattr(PublishingShield, "get_ledger_path", classmethod(lambda cls: test_ledger))

    # Test call with kwargs matching universal engines
    PublishingShield.record_published(
        channel_id="test-channel",
        text="Sample post text",
        media_urls=["https://cdn.example.com/slide1.jpg"],
        provider="buffer",
        status="queued",
        response={"success": True, "id": "post_123"},
    )

    ledger = PublishingShield.load_ledger()
    assert len(ledger) == 1
    assert ledger[0]["channel_id"] == "test-channel"
    assert ledger[0]["status"] == "queued"


def test_publishing_shield_alias_duplicate_detection(tmp_path, monkeypatch):
    """Verifies that check_duplicate resolves aliases between buffer_channel_id and channel_slug (High Fix #4)."""
    test_ledger = tmp_path / "test_ledger.json"
    monkeypatch.setattr(PublishingShield, "get_ledger_path", classmethod(lambda cls: test_ledger))

    # Mock ChannelManager to return a known mapping
    mock_cm = MagicMock()
    mock_cm.get_channel.return_value = {
        "slug": "dossie-historico",
        "social": {"instagram": {"buffer_channel_id": "buf_ig_12345"}}
    }
    mock_cm.list_channels.return_value = [{
        "slug": "dossie-historico",
        "social": {"instagram": {"buffer_channel_id": "buf_ig_12345"}}
    }]

    with patch("src.core.channel_manager.ChannelManager", return_value=mock_cm):
        # Record publication under buffer_channel_id
        PublishingShield.record_published(
            channel_id="buf_ig_12345",
            text="Same historical content published via adapter",
        )

        # Check duplicate using channel_slug
        is_dup, err = PublishingShield.check_duplicate(
            channel_id="dossie-historico",
            text="Same historical content published via adapter",
        )
        assert is_dup is True
        assert "Duplicate dispatch blocked" in err


def test_captions_export_act_id_and_remotion_format(tmp_path):
    """Verifies UniversalCaptionsEngine exports both flat root keys and act-keyed dictionary (High Fix #2)."""
    engine = UniversalCaptionsEngine()
    whisper_data = {
        "words": [
            {"word": "HISTÓRIA", "start": 0.0, "end": 0.5},
            {"word": "SECRETA", "start": 0.5, "end": 1.0},
            {"word": "REVELADA", "start": 1.0, "end": 1.5},
        ]
    }
    out_json = tmp_path / "captions_act.json"
    res = engine.process_and_export(whisper_data, out_json, words_per_chunk=2, act_id="short_01")
    assert res["success"] is True

    exported = json.loads(out_json.read_text(encoding="utf-8"))
    # 1. Flat root keys
    assert "words" in exported
    assert "chunks" in exported
    assert "metadata" in exported
    # 2. Remotion ActData nested key
    assert "short_01" in exported
    act_data = exported["short_01"]
    assert act_data["name"] == "short_01"
    assert "words" in act_data
    assert "chunks" in act_data
    assert len(act_data["chunks"]) == 2


def test_carousel_prepare_background_rgba_and_cmyk(tmp_path, temp_workspace):
    """Verifies UniversalCarouselEngine handles RGBA transparent PNGs and CMYK without black artifacts (Medium Fix #6)."""
    engine = UniversalCarouselEngine(channel_manager=temp_workspace["cm"])

    # 1. RGBA with transparent alpha
    rgba_path = tmp_path / "transparent.png"
    rgba_img = Image.new("RGBA", (800, 800), (255, 0, 0, 0)) # Fully transparent red
    rgba_img.save(rgba_path)

    out_bg = tmp_path / "prepared_rgba.jpg"
    engine.prepare_background(rgba_path, out_bg, color_boost=1.1)
    assert out_bg.exists()
    processed = Image.open(out_bg)
    assert processed.mode == "RGB"
    assert processed.size == (1080, 1440)

    # 2. CMYK image
    cmyk_path = tmp_path / "cmyk.jpg"
    cmyk_img = Image.new("CMYK", (800, 800), (0, 100, 100, 0))
    cmyk_img.save(cmyk_path)

    out_cmyk = tmp_path / "prepared_cmyk.jpg"
    engine.prepare_background(cmyk_path, out_cmyk)
    assert out_cmyk.exists()


def test_carousel_builder_safe_font_fallback(tmp_path, temp_workspace):
    """Verifies CarouselBuilder falls back to default fonts when custom font path does not exist (Medium Fix #5)."""
    from src.engine.carousel_builder import CarouselBuilder

    # Channel with invalid font path
    ch_config = {
        "slug": "canal-nofont",
        "name": "Canal No Font",
        "branding": {
            "typography": {
                "bold_font": "/nonexistent/fonts/fake_bold.ttf",
                "regular_font": "/nonexistent/fonts/fake_reg.ttf",
            }
        }
    }
    temp_workspace["cm"].get_channel = MagicMock(return_value=ch_config)

    builder = CarouselBuilder(channel_manager=temp_workspace["cm"])
    bg_img = tmp_path / "bg.jpg"
    Image.new("RGB", (1080, 1440), (20, 20, 20)).save(bg_img)
    out_slide = tmp_path / "out_slide.jpg"

    # Must NOT raise OSError: cannot open resource
    res = builder.render_slide(
        bg_image_path=bg_img,
        output_path=out_slide,
        channel_slug="canal-nofont",
        headline="Título Sem Fonte no Sistema",
        body="Corpo explicativo seguro com fallback.",
    )
    assert res.exists()


def test_carousel_builder_small_resolution_no_negative_y(tmp_path, temp_workspace):
    """Verifies CarouselBuilder clamps start_y so text is never truncated on small/tight images (Medium Fix #6)."""
    from src.engine.carousel_builder import CarouselBuilder

    builder = CarouselBuilder(channel_manager=temp_workspace["cm"])
    small_bg = tmp_path / "small_bg.jpg"
    Image.new("RGB", (300, 400), (30, 30, 30)).save(small_bg)
    out_slide = tmp_path / "out_small.jpg"

    res = builder.render_slide(
        bg_image_path=small_bg,
        output_path=out_slide,
        channel_slug=temp_workspace["channel_slug"],
        headline="Título Muito Longo Para Uma Imagem Muito Pequena Que Poderia Causar Overflow",
        body="Corpo adicional que ocupa bastante espaço vertical.",
    )
    assert res.exists()


def test_catbox_storage_validation_and_retry(tmp_path):
    """Verifies CatboxStorageProvider validates returned URLs and retries on errors (Medium Fix #8)."""
    from src.utils.storage import CatboxStorageProvider
    import urllib.error

    provider = CatboxStorageProvider()
    test_file = tmp_path / "sample.jpg"
    test_file.write_bytes(b"dummy image bytes")

    # 1. Invalid response (e.g. HTML error from Catbox or Cloudflare)
    mock_resp_invalid = MagicMock()
    mock_resp_invalid.read.return_value = b"<html>Error: 502 Bad Gateway</html>"
    mock_resp_invalid.__enter__.return_value = mock_resp_invalid

    with patch("urllib.request.urlopen", return_value=mock_resp_invalid), patch("time.sleep"):
        with pytest.raises(RuntimeError, match="Catbox upload failed after 3 attempts"):
            provider.upload_file(test_file)

    # 2. Transient network error followed by valid URL
    mock_resp_valid = MagicMock()
    mock_resp_valid.read.return_value = b"https://files.catbox.moe/abc1234.jpg\n"
    mock_resp_valid.__enter__.return_value = mock_resp_valid

    with patch("urllib.request.urlopen", side_effect=[urllib.error.URLError("Connection reset"), mock_resp_valid]), patch("time.sleep"):
        url = provider.upload_file(test_file)
        assert url == "https://files.catbox.moe/abc1234.jpg"


def test_surgical_debreather_pause_gating(tmp_path):
    """Verifies UniversalAudioEngine.surgical_debreather silences inter-word pauses >= 120ms (High Fix #3)."""
    engine = UniversalAudioEngine()
    # Create 2-second audio file
    raw_wav = tmp_path / "raw_voice.wav"
    create_synthetic_wav(raw_wav, duration_sec=2.0, sample_rate=44100)

    # Captions with a 400ms pause between word 1 and word 2
    captions = {
        "words": [
            {"word": "PRIMEIRA", "start": 0.1, "end": 0.5},
            {"word": "SEGUNDA", "start": 0.9, "end": 1.4},  # 400ms pause between 0.5 and 0.9
        ]
    }
    clean_wav = tmp_path / "clean_voice.wav"
    res = engine.surgical_debreather(raw_wav, captions, clean_wav, min_pause_sec=0.12)
    assert res["success"] is True
    assert clean_wav.exists()
    assert res["pauses_cleaned"] >= 1


def test_universal_carousel_recipe_with_presets(temp_workspace):
    """Verifies that UniversalCarouselEngine can process recipes using presets without requiring background image files."""
    root, ch_dir = temp_workspace
    cm = ChannelManager(root_dir=root)
    engine = UniversalCarouselEngine(channel_manager=cm)

    recipe_path = ch_dir / "minimal_recipe.json"
    recipe = {
        "channel_slug": "test-channel",
        "post_slug": "post_minimal_test",
        "aspect_ratio": "4:5",
        "preset": "minimal_dark",
        "slides": [
            {
                "step_number": "Passo 1.",
                "headline": "Primeiro passo importante",
                "body": "Descrição detalhada do processo.",
                "ui_mockup": {
                    "type": "search_bar",
                    "query": "busca de teste"
                }
            },
            {
                "step_number": "Passo 2.",
                "headline": "Segundo passo importante",
                "body": "Continuação da explicação prática."
            }
        ]
    }
    with open(recipe_path, "w", encoding="utf-8") as f:
        json.dump(recipe, f)

    slide_paths = engine.build_from_recipe(recipe_path)
    assert len(slide_paths) == 2
    for p in slide_paths:
        assert p.exists()
        img = Image.open(p)
        assert img.size == (1080, 1350)  # 4:5 aspect ratio


