"""Provider-layer contract tests (Rule 14 / Rule 12)."""

from __future__ import annotations

from pathlib import Path

import pytest

from src.engine.providers.base import ProviderError, get_provider
from src.engine.providers.blender_provider import BlenderProvider
from src.engine.providers.ffmpeg_provider import FFmpegProvider
from src.engine.providers.prompt_export_provider import PromptExportProvider


def test_unknown_provider_raises():
    with pytest.raises(ProviderError, match="Unknown provider"):
        get_provider("does-not-exist")


def test_output_name_cannot_escape_out_dir(tmp_path: Path):
    provider = PromptExportProvider()
    with pytest.raises(ProviderError, match="path separators"):
        provider.resolve_output(tmp_path, "../escape.json")


def test_output_stays_inside_out_dir(tmp_path: Path):
    provider = PromptExportProvider()
    output = provider.resolve_output(tmp_path, "ok.json")
    assert output.parent == tmp_path.resolve()


def test_blender_rejects_unknown_format(tmp_path: Path):
    provider = BlenderProvider()
    errors = provider.validate(
        {
            "script_path": str(tmp_path / "template.py"),
            "format": "exe",
            "resolution": "1920x1080",
            "supported_formats": ["png"],
        }
    )
    assert any("unsupported format" in error for error in errors)


def test_blender_rejects_template_without_support(tmp_path: Path):
    script = tmp_path / "template.py"
    script.write_text("print('noop')", encoding="utf-8")
    provider = BlenderProvider()
    errors = provider.validate(
        {
            "script_path": str(script),
            "format": "webm",
            "resolution": "1920x1080",
            "supported_formats": ["png"],
        }
    )
    assert any("does not support format" in error for error in errors)


def test_blender_rejects_missing_script(tmp_path: Path):
    provider = BlenderProvider()
    errors = provider.validate(
        {
            "script_path": str(tmp_path / "missing.py"),
            "format": "png",
            "resolution": "512x512",
            "supported_formats": ["png"],
        }
    )
    assert any("not found" in error for error in errors)


def test_ffmpeg_rejects_bed_volume_above_ceiling():
    provider = FFmpegProvider()
    errors = provider.validate(
        {
            "op": "mix",
            "input": "voice.mp3",
            "output": "out.mp3",
            "mix_bed": "music.mp3",
            "bed_volume": 0.35,
        }
    )
    assert any("bed_volume" in error for error in errors)


def test_prompt_export_provider_is_always_available():
    assert PromptExportProvider().is_available()


def test_prompt_export_writes_structured_prompts(tmp_path: Path):
    provider = PromptExportProvider()
    result = provider.render(
        {
            "prompt": "A declassified dossier on a wooden desk",
            "aspect_ratio": "16:9",
            "output": "hero.png",
        },
        tmp_path,
    )
    assert result["status"] == "success"
    assert "midjourney" in result["prompts"]
    assert "--ar 16:9" in result["prompts"]["midjourney"]["prompt"]
    assert (tmp_path / "prompt_export.json").is_file()
    assert (tmp_path / "prompt_export.md").is_file()
