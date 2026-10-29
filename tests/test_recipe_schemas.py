"""Validate every declarative document in channels/ against its schema."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.core.schema_validator import infer_kind, load_schema, validate

ROOT = Path(__file__).resolve().parents[1]
CHANNELS = ROOT / "channels"


def _documents():
    for path in sorted(CHANNELS.rglob("*.json")):
        kind = infer_kind(path)
        if kind:
            yield kind, path


def test_all_channel_configs_are_valid():
    configs = sorted(CHANNELS.glob("*/channel.json"))
    assert configs, "No channel.json files found"
    for path in configs:
        validate("channel", json.loads(path.read_text(encoding="utf-8")), source=str(path))


def test_all_declarative_documents_are_valid():
    failures = []
    for kind, path in _documents():
        try:
            validate(kind, json.loads(path.read_text(encoding="utf-8")), source=str(path))
        except Exception as exc:
            failures.append(f"{path.relative_to(ROOT)} [{kind}]: {exc}")
    assert not failures, "\n\n".join(failures)


def test_required_recipe_families_exist():
    kinds = {kind for kind, _ in _documents()}
    assert "carousel_recipe" in kinds
    assert "documentary_recipe" in kinds
    assert "channel" in kinds


def test_every_schema_kind_loads():
    expected = {
        "channel",
        "carousel_recipe",
        "post_recipe",
        "thumbnail_recipe",
        "documentary_recipe",
        "caption_recipe",
        "3d_recipe",
        "template_manifest",
        "video_recipe",
        "audio_recipe",
        "voice_recipe",
        "image_recipe",
        "asset_recipe",
    }
    for kind in expected:
        schema = load_schema(kind)
        assert schema.get("$schema", "").startswith("http://json-schema.org/draft-07")


def test_recipe_schema_rejects_invalid_carousel():
    with pytest.raises(Exception):
        validate("carousel_recipe", {"slides": []}, strict=True)


def test_recipe_schema_rejects_unknown_post_provider():
    with pytest.raises(Exception):
        validate(
            "post_recipe",
            {"text": "hello", "provider": "not-a-provider"},
            strict=True,
        )
