"""Editable episode codegen, hash guard and media manifest tests."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.engine.editable_video import EditableVideoEngine, EditableVideoError

ROOT = Path(__file__).resolve().parents[1]
CHANNEL_TEMPLATE = ROOT / "channels" / "_template" / "channel.json"


def make_channel(root: Path, slug: str = "test-channel") -> Path:
    channel = root / "channels" / slug
    for directory in ("articles", "scripts", "campanhas", "media/raw"):
        (channel / directory).mkdir(parents=True, exist_ok=True)
    config = json.loads(CHANNEL_TEMPLATE.read_text(encoding="utf-8"))
    config["id"] = slug
    config["slug"] = slug
    config["features"]["video"] = True
    (channel / "channel.json").write_text(
        json.dumps(config, ensure_ascii=False), encoding="utf-8"
    )
    for name in ("a.jpg", "b.jpg", "vo.wav", "bed.wav", "sfx.wav"):
        (channel / "media" / "raw" / name).write_bytes(b"fake-" + name.encode())
    return channel


def make_episode_config(slug: str = "test-channel") -> dict:
    return {
        "id": "ep-test",
        "title": "Ep Teste",
        "channelSlug": slug,
        "language": "pt",
        "enableIntro": True,
        "introDurationFrames": 90,
        "introProps": {
            "channelName": "CANAL TESTE",
            "primaryColor": "#D4AF37",
            "subText": "HISTORIA",
        },
        "theme": {"accent": "#D4AF37", "danger": "#EF4444"},
        "backgroundMusicSrc": "media/raw/bed.wav",
        "backgroundMusicVolume": 0.16,
        "voiceovers": [
            {
                "id": "vo_01",
                "src": "media/raw/vo.wav",
                "startInSeconds": 0,
                "durationInSeconds": 10,
            }
        ],
        "scenes": [
            {
                "id": "s1",
                "type": "ken-burns",
                "mediaSrc": "media/raw/a.jpg",
                "startInSeconds": 0,
                "durationInSeconds": 5,
                "headline": "Cena Um",
                "badge": "ARQUIVO",
            },
            {
                "id": "s2",
                "type": "document-reveal",
                "headline": "Documento",
                "subheadline": "1889",
                "badge": "CONFIDENCIAL",
                "startInSeconds": 5,
                "durationInSeconds": 6,
            },
            {
                "id": "s3",
                "type": "heraldic-surgery",
                "beforeSrc": "media/raw/a.jpg",
                "afterSrc": "media/raw/b.jpg",
                "startInSeconds": 11,
                "durationInSeconds": 5,
                "badge": "METAMORFOSE",
                "sfxSrc": "media/raw/sfx.wav",
                "sfxVolume": 0.3,
            },
        ],
        "captions": {},
        "actTimelines": [],
    }


def test_scaffold_generates_explicit_scene_nodes(tmp_path: Path):
    make_channel(tmp_path)
    engine = EditableVideoEngine(project_root=tmp_path)
    result = engine.scaffold(make_episode_config())

    episode = tmp_path / "channels/test-channel/video/episodes/ep-test-16x9"
    tsx = (episode / "Episode.tsx").read_text(encoding="utf-8")
    index = (episode / "index.ts").read_text(encoding="utf-8")
    meta = json.loads((episode / "meta.json").read_text(encoding="utf-8"))
    media = json.loads((episode / "media.json").read_text(encoding="utf-8"))

    assert result["status"] == "success"
    assert "<SceneKenBurns" in tsx
    assert "<SceneDocumentReveal" in tsx
    assert "<SceneHeraldic" in tsx
    assert "scenes.map" not in tsx
    assert "staticFile(" in tsx
    assert 'staticFile("sfx/03' in tsx
    assert "createEpisodeRoot" in index
    assert "Episode-ep-test-16x9" in index
    assert meta["config_hash"]
    assert meta["generated_files"]["Episode.tsx"]
    assert len(media["files"]) == 6
    assert (episode / "public/scenes/01_s1.jpg").is_file()
    assert (episode / "data/captions.ts").is_file()
    assert (episode / "data/theme.ts").is_file()


def test_scaffold_9x16_dimensions(tmp_path: Path):
    make_channel(tmp_path)
    result = EditableVideoEngine(project_root=tmp_path).scaffold(
        make_episode_config(), aspect_ratio="9:16"
    )
    index = (Path(result["episode_dir"]) / "index.ts").read_text(encoding="utf-8")
    assert "width: 1080" in index
    assert "height: 1920" in index
    assert "Episode-ep-test-9x16" in index


def test_hash_guard_refuses_manual_edits_and_force_backs_up(tmp_path: Path):
    make_channel(tmp_path)
    engine = EditableVideoEngine(project_root=tmp_path)
    result = engine.scaffold(make_episode_config())
    episode = Path(result["episode_dir"])
    tsx = episode / "Episode.tsx"
    tsx.write_text(tsx.read_text(encoding="utf-8") + "\n// manual\n", encoding="utf-8")

    with pytest.raises(EditableVideoError, match="manual changes"):
        engine.scaffold(make_episode_config())

    forced = engine.scaffold(make_episode_config(), force=True)
    assert forced["backup"]
    assert Path(forced["backup"]).is_dir()
    assert not (Path(forced["backup"]) / "public").exists()
    assert "// manual" not in tsx.read_text(encoding="utf-8")


def test_unknown_scene_type_warns_and_falls_back(tmp_path: Path):
    make_channel(tmp_path)
    config = make_episode_config()
    config["scenes"][0]["type"] = "mystery-scene"
    result = EditableVideoEngine(project_root=tmp_path).scaffold(config)
    assert any("unsupported type" in warning for warning in result["warnings"])
    tsx = (Path(result["episode_dir"]) / "Episode.tsx").read_text(encoding="utf-8")
    assert "<SceneKenBurns" in tsx


def test_missing_media_raises(tmp_path: Path):
    make_channel(tmp_path)
    config = make_episode_config()
    config["scenes"][0]["mediaSrc"] = "media/raw/missing.jpg"
    with pytest.raises(EditableVideoError, match="Media not found"):
        EditableVideoEngine(project_root=tmp_path).scaffold(config)


def test_video_recipe_wrapper_is_accepted(tmp_path: Path):
    make_channel(tmp_path)
    wrapped = {"config": make_episode_config(), "enableIntro": True}
    result = EditableVideoEngine(project_root=tmp_path).scaffold(wrapped)
    assert result["composition"] == "Episode-ep-test-16x9"


def test_unknown_channel_raises(tmp_path: Path):
    with pytest.raises(EditableVideoError, match="Channel not found"):
        EditableVideoEngine(project_root=tmp_path).scaffold(
            make_episode_config(), channel_slug="missing"
        )
