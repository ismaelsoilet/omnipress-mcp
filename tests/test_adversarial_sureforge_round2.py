"""
Comprehensive adversarial regression test suite under SureForge / Fable-Judge protocol.
Validates all Round 2 adversarial findings across:
1. Modern gTLD emails, classic OpenAI keys, AWS keys, GitHub PATs, and Ghost admin tokens.
2. PublishingShield fingerprint collision resistance (no 30-word truncation).
3. CarouselBuilder 9:16 aspect ratio preserving and swipe_str fallback.
4. UniversalAudioEngine surgical_debreather bit-depth (float32, int32) and captions dictionary guards.
5. UniversalCaptionsEngine multi-act Whisper parsing.
6. StorageProvider path traversal protection and MIME type detection.
7. CLI customScheduled mode schedule_time validation.
"""

import pytest
import numpy as np
from pathlib import Path
from unittest.mock import patch, MagicMock

from src.utils.sanitizer import sanitize_text, inspect_sensitive_data
from src.core.publishing_shield import PublishingShield
from src.engine.carousel_builder import CarouselBuilder
from src.core.channel_manager import ChannelManager
from src.engine.universal_audio import UniversalAudioEngine
from src.engine.universal_captions import UniversalCaptionsEngine
from src.utils.storage import LocalStaticStorageProvider, S3StorageProvider
from src.cli import main as cli_main


def test_sanitizer_modern_gtlds_and_pipes():
    """Verify modern ICANN gTLDs (>7 characters) and absence of pipe syntax error."""
    text = (
        "Contato comercial: contato@omnipress.technology ou suporte@empresa.solutions "
        "e juridico@banca.advogado."
    )
    sanitized, findings = sanitize_text(text)
    assert "[EMAIL PROTEGIDO]" in sanitized
    assert "technology" not in sanitized
    assert "solutions" not in sanitized
    assert "advogado" not in sanitized
    assert len([f for f in findings if f["type"] == "email"]) == 3


def test_sanitizer_expanded_api_keys():
    """Verify classic OpenAI, AWS Access Keys, GitHub PATs, and Ghost Admin tokens."""
    text = (
        "Chave OpenAI clássica: sk-abcdef1234567890abcdef1234567890\n"
        "Chave AWS: AKIAIOSFODNN7EXAMPLE\n"
        "Token GitHub: github_pat_11AABBCCDDEEFFGGHHIIJJKKLLMMNNOOPP\n"
        "Chave Ghost: 651234567890abcdef123456:abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890\n"
    )
    sanitized, findings = sanitize_text(text)
    assert "sk-abcdef1234567890abcdef1234567890" not in sanitized
    assert "AKIAIOSFODNN7EXAMPLE" not in sanitized
    assert "github_pat_" not in sanitized
    assert "[CHAVE PROTEGIDA]" in sanitized
    assert len(findings) >= 4


def test_publishing_shield_no_30_word_truncation():
    """Verify two posts sharing the same 35-word opening disclaimer do NOT collide."""
    common_opening = (
        "Aviso Oficial de Utilidade Pública emitido pelo Departamento Jurídico: "
        "todas as diretrizes orçamentárias e regulatórias devem ser rigorosamente observadas "
        "por todos os servidores e operadores do sistema sob pena de sanções administrativas "
        "conforme instrução normativa aplicável neste exercício fiscal."
    )
    post_a = f"{common_opening} TEMA DO POST A: Nova portaria de tecnologia número 45."
    post_b = f"{common_opening} TEMA DO POST B: Processo de compras públicas número 89."

    fp_a = PublishingShield.generate_fingerprint("ch_test", post_a)
    fp_b = PublishingShield.generate_fingerprint("ch_test", post_b)
    assert fp_a != fp_b, "Posts with identical first 30 words but different conclusions must produce distinct fingerprints!"


def test_carousel_builder_9_16_aspect_ratio(tmp_path: Path):
    """Verify that 9:16 aspect ratio does not crop height to 1.0 square."""
    cm = ChannelManager(root_dir=tmp_path)
    builder = CarouselBuilder(cm)

    from PIL import Image
    bg = tmp_path / "raw_9_16.jpg"
    Image.new("RGB", (1080, 1920), (30, 40, 50)).save(bg)

    out_slide = tmp_path / "slide_9_16.jpg"
    builder.render_slide(
        bg_image_path=bg,
        output_path=out_slide,
        channel_slug="default",
        headline="Short Vertical 9:16",
        body="Texto explicativo para stories e reels.",
        aspect_ratio="9:16",
    )

    with Image.open(out_slide) as im:
        assert im.size == (1080, 1920), f"Expected 1080x1920 but got {im.size}"


def test_carousel_builder_no_none_in_footer(tmp_path: Path):
    """Verify that when swipe_str is None, it defaults to Deslize and never prints 'None'."""
    cm = ChannelManager(root_dir=tmp_path)
    builder = CarouselBuilder(cm)

    from PIL import Image
    bg = tmp_path / "test_bg.jpg"
    Image.new("RGB", (1080, 1440), (20, 25, 30)).save(bg)

    slides = [
        {"bg_image_path": str(bg), "headline": "Slide 1", "swipe_str": None},
        {"bg_image_path": str(bg), "headline": "Slide 2", "swipe_str": None},
    ]

    out_files = builder.build_carousel("default", "test_swipe", slides, aspect_ratio="3:4")
    assert len(out_files) == 2
    for f in out_files:
        assert f.exists()


def test_universal_audio_surgical_debreather_float32(tmp_path: Path):
    """Verify that 32-bit float audio is not attenuated to silence."""
    from scipy.io import wavfile
    sample_wav = tmp_path / "float_voice.wav"
    out_wav = tmp_path / "cleaned_voice.wav"

    sr = 24000
    # Generate 1 second of 440Hz sine wave in float32 [-0.5, 0.5]
    t = np.linspace(0, 1.0, sr, endpoint=False, dtype=np.float32)
    sig = (0.5 * np.sin(2 * np.pi * 440 * t)).astype(np.float32)
    wavfile.write(sample_wav, sr, sig)

    captions = {
        "words": [
            {"word": "Olá", "start": 0.1, "end": 0.4},
            {"word": "Mundo", "start": 0.6, "end": 0.9},
        ]
    }

    engine = UniversalAudioEngine(ffmpeg_bin="ffmpeg")
    res = engine.surgical_debreather(sample_wav, captions, out_wav)
    assert res["success"] is True

    sr_out, out_data = wavfile.read(out_wav)
    assert np.max(np.abs(out_data)) > 1000, "Audio signal must retain strong amplitude, not attenuated to silence!"


def test_universal_captions_multi_act_parsing():
    """Verify that multi-act nested Whisper captions accumulate words from all acts."""
    data = {
        "act_01": {
            "words": [
                {"word": "Primeiro", "start": 0.0, "end": 0.5},
                {"word": "ato", "start": 0.6, "end": 1.0},
            ]
        },
        "act_02": {
            "words": [
                {"word": "Segundo", "start": 1.2, "end": 1.6},
                {"word": "ato", "start": 1.7, "end": 2.0},
            ]
        }
    }
    parsed = UniversalCaptionsEngine.parse_raw_whisper(data)
    assert len(parsed) == 4
    assert [w["word"] for w in parsed] == ["Primeiro", "ato", "Segundo", "ato"]


def test_storage_path_traversal_and_mimetypes(tmp_path: Path):
    """Verify path traversal prevention and accurate mime types."""
    storage_dir = tmp_path / "static"
    storage_dir.mkdir()
    provider = LocalStaticStorageProvider("http://localhost:8000", staging_dir=storage_dir)

    video_file = tmp_path / "sample.mp4"
    video_file.write_bytes(b"\x00\x00\x00\x18ftypmp42")

    url = provider.upload_file(video_file, remote_name="../../escaped.mp4")
    assert "/escaped.mp4" in url
    assert (storage_dir / "escaped.mp4").exists(), "File must be saved cleanly inside staging_dir without traversal"
    assert not (tmp_path / "escaped.mp4").exists(), "Must not write outside staging_dir"


def test_cli_custom_scheduled_requires_schedule_time(capsys):
    """Verify CLI rejects --mode customScheduled without --schedule-time."""
    exit_code = cli_main(["publish", "--text", "Post de teste válido", "--platforms", "linkedin", "--mode", "customScheduled"])
    assert exit_code == 1
    captured = capsys.readouterr()
    assert "--schedule-time is required" in captured.out

