"""Rule 15 — High-CTR thumbnail validator (production code, not test-local)."""

from __future__ import annotations

import re
from typing import Any, Dict, List

MIN_HEADLINE_FONT = 160
MAX_HEADLINE_FONT = 220
MIN_BADGE_FONT = 50
MIN_STROKE = 11
MAX_HEADLINE_WORDS = 4
MAX_BADGE_WORDS = 3
YOUTUBE_DEATH_ZONE = (320, 140)


def word_count(text: str) -> int:
    return len([w for w in re.split(r"\s+", str(text or "").strip()) if w])


def validate_thumbnail_recipe(recipe: Dict[str, Any]) -> List[str]:
    """Returns a list of Rule 15 violations. Empty means approved."""
    errors: List[str] = []

    headline = str(recipe.get("headline") or "").strip()
    if not headline:
        errors.append("headline is required")
    else:
        count = word_count(headline)
        if count > MAX_HEADLINE_WORDS:
            errors.append(
                f"headline has {count} words (max {MAX_HEADLINE_WORDS}); thumbnails must be 2-4 power words"
            )
        if re.search(r"[.;:!?]\s", headline) or "\n" in headline:
            errors.append("headline must not contain sentences, bullets or line breaks")

    badge = str(recipe.get("badge_text") or "").strip()
    if badge and word_count(badge) > MAX_BADGE_WORDS:
        errors.append(f"badge_text has more than {MAX_BADGE_WORDS} words")

    tagline = str(recipe.get("tagline") or "").strip()
    if tagline and word_count(tagline) > MAX_HEADLINE_WORDS:
        errors.append(f"tagline has more than {MAX_HEADLINE_WORDS} words")

    if not str(recipe.get("media") or "").strip():
        errors.append("media is required (authentic visual foundation)")

    aspect = str(recipe.get("aspect_ratio") or "16:9")
    if aspect not in ("16:9", "9:16"):
        errors.append("aspect_ratio must be 16:9 or 9:16")

    typography = recipe.get("typography") or {}
    headline_size = int(typography.get("headline_font_size") or 190)
    if not (MIN_HEADLINE_FONT <= headline_size <= MAX_HEADLINE_FONT):
        errors.append(
            f"headline_font_size must be between {MIN_HEADLINE_FONT} and {MAX_HEADLINE_FONT}px"
        )

    badge_size = int(typography.get("badge_font_size") or 56)
    if badge_size < MIN_BADGE_FONT:
        errors.append(f"badge_font_size must be >= {MIN_BADGE_FONT}px")

    stroke_width = int(typography.get("stroke_width") or 12)
    if stroke_width < MIN_STROKE:
        errors.append(f"stroke_width must be >= {MIN_STROKE}px")

    safe = recipe.get("safe_zones") or {}
    text_area = float(safe.get("text_area_ratio") or 0.55)
    if text_area > 0.60:
        errors.append("text_area_ratio must be <= 0.60 to respect the YouTube death zone")

    highlight = str(recipe.get("highlight_word") or "").strip()
    if highlight and highlight.lower() not in headline.lower():
        errors.append("highlight_word must appear in the headline")

    return errors
