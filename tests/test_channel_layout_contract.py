"""Channel workspace layout contract (Rule 12 / Rule 14)."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHANNELS = ROOT / "channels"

FORBIDDEN_SCRIPT_PATTERNS = (
    "render_*.py",
    "upload_*.py",
    "schedule_*.py",
)

CHANNEL_SCRIPTS_ALLOWLIST = {
    "Root.dossie.tsx",
    "example_runner.py",
    ".gitkeep",
}


def _channels():
    return [
        path
        for path in CHANNELS.iterdir()
        if path.is_dir() and (path / "channel.json").is_file()
    ]


def test_no_forbidden_generation_scripts_under_channels():
    offenders = []
    for channel in CHANNELS.iterdir():
        if not channel.is_dir():
            continue
        for pattern in FORBIDDEN_SCRIPT_PATTERNS:
            offenders.extend(str(path.relative_to(ROOT)) for path in channel.rglob(pattern))
    assert not offenders, "Forbidden bespoke scripts (use the universal engines):\n" + "\n".join(offenders)


def test_channel_level_scripts_are_allowlisted():
    offenders = []
    for channel in _channels():
        scripts_dir = channel / "scripts"
        if not scripts_dir.is_dir():
            continue
        for path in scripts_dir.iterdir():
            if path.is_file() and path.name not in CHANNEL_SCRIPTS_ALLOWLIST:
                offenders.append(str(path.relative_to(ROOT)))
    assert not offenders, f"Unexpected channel-level scripts: {offenders}"


def test_canonical_directories_per_archetype():
    for channel in _channels():
        config = json.loads((channel / "channel.json").read_text(encoding="utf-8"))
        archetype = config.get("archetype", "personal_brand")
        assert (channel / "articles").is_dir(), f"{channel.name}: missing articles/"
        assert (channel / "media").is_dir(), f"{channel.name}: missing media/"
        assert (channel / "scripts").is_dir(), f"{channel.name}: missing scripts/"
        if archetype in ("personal_brand", "hybrid"):
            assert (channel / "campanhas").is_dir(), f"{channel.name}: missing campanhas/"
        if archetype in ("media_channel", "media_house", "hybrid"):
            assert (channel / "episodios").is_dir(), f"{channel.name}: missing episodios/"


def test_carousel_recipes_live_in_canonical_episode_paths():
    for recipe in CHANNELS.rglob("carousel_recipe.json"):
        if "episodios" in recipe.parts:
            assert recipe.parent.name == "carrossel", (
                f"{recipe.relative_to(ROOT)} must live in episodios/<ep>/carrossel/"
            )


def test_legacy_migration_report_exists():
    assert (ROOT / "docs" / "MIGRATION_DOSSIE.md").is_file()
    assert (ROOT / "docs" / "MIGRATION_DOCUMENTARY.md").is_file()
