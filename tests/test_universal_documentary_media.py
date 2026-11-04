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
    (channel / "media" / "raw" / "clip.mp4").write_bytes(b"fake-clip")
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


def test_full_caption_payload_is_normalized_with_cumulative_timelines(tmp_path: Path):
    make_channel(tmp_path)
    recipe = make_recipe()
    act = lambda name, word: {
        "name": name,
        "duration": 1.0,
        "words": [{"word": word, "start": 0.0, "end": 1.0}],
        "chunks": [
            {
                "text": word,
                "start": 0.0,
                "end": 1.0,
                "words": [{"word": word, "start": 0.0, "end": 1.0}],
            }
        ],
    }
    recipe["captions"] = {
        "metadata": {"act_id": "act_01"},
        "words": [],
        "chunks": act("act_01", "UM")["chunks"],
        "act_01": act("act_01", "UM"),
        "act_02": act("act_02", "DOIS"),
    }
    result = UniversalDocumentaryEngine(ChannelManager(tmp_path)).execute_recipe(recipe)
    episode_config = json.loads(
        (Path(result["episode_config"])).read_text(encoding="utf-8")
    )
    assert set(episode_config["captions"].keys()) == {"act_01", "act_02"}
    assert episode_config["actTimelines"] == [
        {"id": "act_01", "globalStart": 0.0, "globalEnd": 1.0},
        {"id": "act_02", "globalStart": 1.0, "globalEnd": 2.0},
    ]


def test_remote_sfx_url_is_preserved(tmp_path: Path):
    make_channel(tmp_path)
    recipe = make_recipe()
    remote = "https://example.test/sfx.mp3"
    recipe["scenes"][0]["sfx"] = remote
    result = UniversalDocumentaryEngine(ChannelManager(tmp_path)).execute_recipe(recipe)
    episode_config = json.loads(
        (Path(result["episode_config"])).read_text(encoding="utf-8")
    )
    assert episode_config["scenes"][0]["sfxSrc"] == remote
    assert result["warnings"] == []


def test_documentary_maps_new_scene_types_in_render_mode(tmp_path: Path):
    make_channel(tmp_path)
    recipe = make_recipe()
    recipe["mode"] = "render"
    recipe["scenes"] = [
        {
            "id": "tactical",
            "type": "tactical_map",
            "media": "media/raw/scene.jpg",
            "duration_seconds": 3,
            "coordinates": "23°33′S 46°38′W",
        },
        {
            "id": "stat",
            "type": "stat_card",
            "media": "media/raw/scene.jpg",
            "duration_seconds": 3,
            "stat_value": 1889,
            "stat_label": "Documentos",
        },
        {
            "id": "clip",
            "type": "video_clip",
            "media": "media/raw/clip.mp4",
            "duration_seconds": 3,
            "video_muted": True,
            "overlay_text": "Registro original",
        },
    ]
    result = UniversalDocumentaryEngine(ChannelManager(tmp_path)).execute_recipe(recipe)
    episode_config = json.loads(
        (Path(result["episode_config"])).read_text(encoding="utf-8")
    )
    assert [scene["type"] for scene in episode_config["scenes"]] == [
        "tactical-map",
        "stat-counter",
        "video-clip",
    ]
    assert episode_config["scenes"][0]["coordinates"] == "23°33′S 46°38′W"
    assert episode_config["scenes"][1]["statValue"] == 1889
    assert episode_config["scenes"][2]["notes"] == "Registro original"
    assert all(
        scene["mediaSrc"].startswith("channels/test-channel/media/raw/")
        for scene in episode_config["scenes"]
    )
