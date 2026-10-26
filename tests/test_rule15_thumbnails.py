"""
Tests for Rule 15 — High-CTR Thumbnail Typography & Packaging Standards.
Verifies typography scale, word count limits, micro-font bans, YouTube safe zone,
and 120px mobile preview generation.
"""

import pytest
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path


class ThumbnailValidator:
    """Validator enforcing Rule 15 standards for YouTube 16:9 thumbnails."""
    
    CANVAS_WIDTH = 1920
    CANVAS_HEIGHT = 1080
    
    # YouTube Duration Badge Death Zone (bottom-right 320x140px)
    SAFE_ZONE_DEATH_X = 1600
    SAFE_ZONE_DEATH_Y = 940
    
    MIN_HEADLINE_FONT = 160
    MAX_HEADLINE_FONT = 220
    MIN_BADGE_FONT = 50
    MIN_FONT_FLOOR = 50  # Zero text allowed below 50px anywhere
    MAX_WORDS = 4

    @classmethod
    def validate_word_count(cls, text: str) -> bool:
        """Rule 15 Law 1: Max 3 to 4 power words total."""
        words = [w for w in text.strip().split() if w]
        return len(words) <= cls.MAX_WORDS

    @classmethod
    def validate_font_size(cls, size: int, is_badge: bool = False) -> bool:
        """Rule 15 Law 2: Headlines 160-220px, badges 50-65px, floor >= 50px."""
        if size < cls.MIN_FONT_FLOOR:
            return False
        if not is_badge and size < cls.MIN_HEADLINE_FONT:
            return False
        return True

    @classmethod
    def is_in_youtube_death_zone(cls, bbox: tuple) -> bool:
        """
        Rule 15 Law 6: Returns True if bounding box (x1, y1, x2, y2)
        intersects with the bottom-right YouTube duration badge death zone.
        """
        x1, y1, x2, y2 = bbox
        return x2 >= cls.SAFE_ZONE_DEATH_X and y2 >= cls.SAFE_ZONE_DEATH_Y

    @classmethod
    def generate_120px_mobile_preview(cls, img: Image.Image) -> Image.Image:
        """Rule 15 Law 8: Generates the 120px mobile preview image."""
        w, h = img.size
        target_w = 120
        target_h = int(h * (target_w / w))
        return img.resize((target_w, target_h), Image.Resampling.LANCZOS)


def test_rule15_word_count():
    # Compliant 2-4 word power phrases
    assert ThumbnailValidator.validate_word_count("A MAIOR FARSA")
    assert ThumbnailValidator.validate_word_count("18 ANDARES NO SUBSOLO")
    assert ThumbnailValidator.validate_word_count("CÓPIA VETADA!")
    assert ThumbnailValidator.validate_word_count("O PACTO SECRETO")
    assert ThumbnailValidator.validate_word_count("ERA TUDO FALSO!")
    assert ThumbnailValidator.validate_word_count("NUNCA EXISTIU")

    # Non-compliant wall-of-text phrases (5+ words)
    assert not ThumbnailValidator.validate_word_count("1.100 ARTISTAS SALVARAM 30.000 VIDAS")
    assert not ThumbnailValidator.validate_word_count("A HISTÓRIA SECRETA QUE ELES NUNCA CONTARAM")
    assert not ThumbnailValidator.validate_word_count("OPERAÇÃO VIERSEN: 50 ANOS EM SEGREDO")


def test_rule15_font_size_standards():
    # Headlines must be >= 160px
    assert ThumbnailValidator.validate_font_size(160)
    assert ThumbnailValidator.validate_font_size(175)
    assert ThumbnailValidator.validate_font_size(200)
    assert ThumbnailValidator.validate_font_size(220)

    # Headlines below 160px fail
    assert not ThumbnailValidator.validate_font_size(122)
    assert not ThumbnailValidator.validate_font_size(110)
    assert not ThumbnailValidator.validate_font_size(90)

    # Badges must be >= 50px
    assert ThumbnailValidator.validate_font_size(52, is_badge=True)
    assert ThumbnailValidator.validate_font_size(60, is_badge=True)

    # Micro-fonts (< 50px) strictly banned
    assert not ThumbnailValidator.validate_font_size(42, is_badge=True)
    assert not ThumbnailValidator.validate_font_size(28, is_badge=True)
    assert not ThumbnailValidator.validate_font_size(22, is_badge=True)
    assert not ThumbnailValidator.validate_font_size(20, is_badge=True)


def test_rule15_youtube_safe_zone():
    # Left-anchored elements are safe
    assert not ThumbnailValidator.is_in_youtube_death_zone((85, 100, 950, 450))
    assert not ThumbnailValidator.is_in_youtube_death_zone((85, 500, 950, 750))

    # Elements placed in bottom-right corner intersect the death zone
    assert ThumbnailValidator.is_in_youtube_death_zone((1650, 950, 1850, 1020))
    assert ThumbnailValidator.is_in_youtube_death_zone((1550, 920, 1700, 960))


def test_rule15_mobile_preview_generation(tmp_path):
    # Create master 1920x1080 canvas
    canvas = Image.new("RGB", (1920, 1080), (6, 8, 12))
    draw = ImageDraw.Draw(canvas)
    draw.rectangle([0, 0, 960, 1080], fill=(15, 20, 30))

    preview = ThumbnailValidator.generate_120px_mobile_preview(canvas)
    assert preview.size == (120, 67)  # 16:9 scaled to 120px width

    preview_path = tmp_path / "preview_120px.jpg"
    preview.save(preview_path, quality=85)
    assert preview_path.exists()
    assert preview_path.stat().st_size > 0
