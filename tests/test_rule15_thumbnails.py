"""Tests for Rule 15 using the production validator and engine."""

from __future__ import annotations

from pathlib import Path

from PIL import Image

from src.core.channel_manager import ChannelManager
from src.engine.rule15_validator import validate_thumbnail_recipe
from src.engine.universal_thumbnail import UniversalThumbnailEngine


def _valid_recipe(media: Path) -> dict:
    return {
        "headline": "SEGREDO REVELADO",
        "highlight_word": "REVELADO",
        "badge_text": "CASO REAL",
        "tagline": "ARQUIVO 1963",
        "media": str(media),
        "aspect_ratio": "16:9",
        "typography": {
            "headline_font_size": 190,
            "badge_font_size": 56,
            "stroke_width": 12,
        },
        "safe_zones": {"respect_youtube_duration_zone": True, "text_area_ratio": 0.55},
    }


def _media(tmp_path: Path) -> Path:
    media = tmp_path / "media.jpg"
    Image.new("RGB", (1600, 900), (40, 60, 90)).save(media)
    return media


def test_valid_thumbnail_passes_rule15(tmp_path: Path):
    assert validate_thumbnail_recipe(_valid_recipe(_media(tmp_path))) == []


def test_headline_word_limit(tmp_path: Path):
    recipe = _valid_recipe(_media(tmp_path))
    recipe["headline"] = "UM SEGREDO MUITO REVELADO AGORA"
    errors = validate_thumbnail_recipe(recipe)
    assert any("words" in error for error in errors)


def test_headline_font_floor_and_ceiling(tmp_path: Path):
    media = _media(tmp_path)
    for size in (140, 240):
        recipe = _valid_recipe(media)
        recipe["typography"]["headline_font_size"] = size
        assert any(
            "headline_font_size" in error for error in validate_thumbnail_recipe(recipe)
        )


def test_badge_font_floor_and_stroke(tmp_path: Path):
    recipe = _valid_recipe(_media(tmp_path))
    recipe["typography"]["badge_font_size"] = 40
    recipe["typography"]["stroke_width"] = 8
    errors = validate_thumbnail_recipe(recipe)
    assert any("badge_font_size" in error for error in errors)
    assert any("stroke_width" in error for error in errors)


def test_media_and_highlight_are_required(tmp_path: Path):
    recipe = _valid_recipe(tmp_path / "missing.jpg")
    recipe["highlight_word"] = "INEXISTENTE"
    errors = validate_thumbnail_recipe(recipe)
    assert any("highlight_word" in error for error in errors)

    recipe["media"] = ""
    errors = validate_thumbnail_recipe(recipe)
    assert any("media is required" in error for error in errors)


def test_thumbnail_rendering_and_mobile_previews(tmp_path: Path):
    cm = ChannelManager(root_dir=tmp_path)
    cm.create_channel("qa-thumb", "QA Thumb", "@qathumb")

    media = tmp_path / "channels" / "qa-thumb" / "media" / "raw" / "source.jpg"
    media.parent.mkdir(parents=True, exist_ok=True)
    Image.new("RGB", (1600, 900), (40, 60, 90)).save(media)

    engine = UniversalThumbnailEngine(cm)
    recipe = _valid_recipe(media)
    recipe.update({"channel_slug": "qa-thumb", "post_slug": "qa-thumb"})

    result = engine.render_recipe(recipe)
    output = Path(result["output_path"])
    assert output.is_file()
    with Image.open(output) as img:
        assert img.size == (1920, 1080)

    previews = engine.mobile_previews(output)
    assert {path.name for path in previews} == {
        "thumbnail_120px.jpg",
        "thumbnail_320px.jpg",
    }
    with Image.open(previews[0]) as preview:
        assert preview.width == 120
    with Image.open(previews[1]) as preview:
        assert preview.width == 320


def test_thumbnail_validate_only_does_not_render(tmp_path: Path):
    cm = ChannelManager(root_dir=tmp_path)
    cm.create_channel("qa-thumb", "QA Thumb", "@qathumb")
    media = tmp_path / "channels" / "qa-thumb" / "media" / "raw" / "source.jpg"
    media.parent.mkdir(parents=True, exist_ok=True)
    Image.new("RGB", (1600, 900), (40, 60, 90)).save(media)

    engine = UniversalThumbnailEngine(cm)
    recipe = _valid_recipe(media)
    recipe["channel_slug"] = "qa-thumb"
    result = engine.render_recipe(recipe, validate_only=True)
    assert result["status"] == "valid"
    assert not (tmp_path / "channels" / "qa-thumb" / "media" / "thumbnails").exists()
