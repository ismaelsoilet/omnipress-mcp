"""Documentary media manifest portability and SFX resolution tests."""

from __future__ import annotations

import json
from pathlib import Path

from src.core.channel_manager import ChannelManager
from src.engine.universal_documentary import UniversalDocumentaryEngine

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "channels" / "_template" / "channel.json"


def make_channel(root: Path, slug: str = "test-channel") -> Path:
    channel = root / "channels" / slug
    (channel / "media" / "raw").mkdir(parents=True, exist_ok=True)
    config = json.loads(TEMPLATE.read_text(encoding="utf-8"))
    config["id"] = slug
    config["slug"] = slug
    config["features"]["video"] = True
    (channel / "channel.json").write_text(
        json.dumps(config, ensure_ascii=False), encoding="utf-8"
    )
    (channel / "media" / "raw" / "scene.jpg").write_bytes(b"fake-image")
    (channel / "media" / "raw" / "sfx.wav").write_bytes(b"fake-sfx")
    (channel / "media" / "raw" / "vo.wav").write_bytes(b"fake-vo")
    (channel / "media" / "raw" / "bed.wav").write_bytes(b"fake-bed")
    return channel


def make_recipe(slug: str = "test-channel") -> dict:
    return {
        "channel_slug": slug,
        "episode_slug": "ep-media",
        "title": "Media Test",
        "mode": "manifest",
        "scenes": [
            {
                "id": "scene_01",
                "type": "archive_photo",
                "media": "media/raw/scene.jpg",
                "duration_seconds": 3,
                "headline": "Cena",
                "sfx": "media/raw/sfx.wav",
                "sfx_volume": 0.3,
            }
        ],
        "audio": {
            "soundtrack": "media/raw/bed.wav",
            "voiceover": "media/raw/vo.wav",
        },
    }


def test_documentary_manifest_is_portable_and_sfx_is_resolved(tmp_path: Path):
    make_channel(tmp_path)
    engine = UniversalDocumentaryEngine(ChannelManager(tmp_path))
    result = engine.execute_recipe(make_recipe())
    episode_dir = Path(result["episode_config"]).parent

    media = json.loads((episode_dir / "media.json").read_text(encoding="utf-8"))
    assert media["files"]
    assert all(not item["source"].startswith("/") for item in media["files"])
    assert any(item["target"] == "sfx/01.wav" for item in media["files"])

    episode_config = json.loads(
        (episode_dir / "episode_config.json").read_text(encoding="utf-8")
    )
    sfx_src = episode_config["scenes"][0]["sfxSrc"]
    assert not Path(sfx_src).is_absolute()
    assert sfx_src.startswith("channels/test-channel/")
    assert episode_config["backgroundMusicSrc"].startswith("channels/test-channel/")
    assert result["warnings"] == []


def test_missing_voiceover_and_sfx_return_warnings(tmp_path: Path):
    make_channel(tmp_path)
    recipe = make_recipe()
    recipe["audio"]["voiceover"] = "media/raw/missing-vo.wav"
    recipe["scenes"][0]["sfx"] = "media/raw/missing-sfx.wav"
    result = UniversalDocumentaryEngine(ChannelManager(tmp_path)).execute_recipe(recipe)
    assert any("Voiceover not found" in warning for warning in result["warnings"])
    assert any("SFX not found" in warning for warning in result["warnings"])
