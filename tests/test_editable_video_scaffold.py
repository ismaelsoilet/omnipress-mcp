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
    for name in ("a.jpg", "b.jpg", "vo.wav", "bed.wav", "sfx.wav", "clip.mp4"):
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
    assert "resolveMediaSrc(" in tsx
    assert 'resolveMediaSrc("sfx/03' in tsx
    assert "createEpisodeRoot" in index
    assert "Episode-ep-test-16x9" in index
    assert meta["config_hash"]
    assert meta["generated_files"]["Episode.tsx"]
    assert len(media["files"]) == 6
    assert all(not item["source"].startswith("/") for item in media["files"])
    recipe = json.loads(
        (episode / "video_recipe.editable.json").read_text(encoding="utf-8")
    )
    assert recipe["editable"] is True
    assert "duration_frames" not in recipe
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


def test_intro_attributes_escape_quotes_newlines_and_backslashes(tmp_path: Path):
    make_channel(tmp_path)
    config = make_episode_config()
    config["introProps"]["channelName"] = 'CANAL "TESTE" \\quoted'
    config["introProps"]["subText"] = "LINHA\nNOVA"
    result = EditableVideoEngine(project_root=tmp_path).scaffold(config)
    tsx = (Path(result["episode_dir"]) / "Episode.tsx").read_text(encoding="utf-8")
    assert r'channelName={"CANAL \"TESTE\" \\quoted"}' in tsx
    assert r'subText={"LINHA\nNOVA"}' in tsx


def test_align_captions_payload_is_normalized_and_timeline_derived(tmp_path: Path):
    make_channel(tmp_path)
    config = make_episode_config()
    config["captions"] = {
        "metadata": {"act_id": "act_01", "duration_seconds": 0.5},
        "words": [{"word": "OLA", "start": 0.0, "end": 0.5}],
        "chunks": [
            {
                "id": 1,
                "text": "OLA",
                "start": 0.0,
                "end": 0.5,
                "duration": 0.5,
                "words": [{"word": "OLA", "start": 0.0, "end": 0.5}],
            }
        ],
        "act_01": {
            "name": "act_01",
            "duration": 0.5,
            "words": [{"word": "OLA", "start": 0.0, "end": 0.5}],
            "chunks": [
                {
                    "id": 1,
                    "text": "OLA",
                    "start": 0.0,
                    "end": 0.5,
                    "duration": 0.5,
                    "words": [{"word": "OLA", "start": 0.0, "end": 0.5}],
                }
            ],
        },
    }
    result = EditableVideoEngine(project_root=tmp_path).scaffold(config)
    episode = Path(result["episode_dir"])
    captions_ts = (episode / "data/captions.ts").read_text(encoding="utf-8")
    tsx = (episode / "Episode.tsx").read_text(encoding="utf-8")
    assert "Record<string, ActData>" in captions_ts
    assert '"id": 1' in captions_ts
    assert '"act_01"' in captions_ts
    assert '"globalEnd": 0.5' in tsx


def test_flat_caption_chunks_use_array_type(tmp_path: Path):
    make_channel(tmp_path)
    config = make_episode_config()
    config["captions"] = [
        {
            "text": "OLA",
            "start": 0.0,
            "end": 0.5,
            "words": [{"word": "OLA", "start": 0.0, "end": 0.5}],
        }
    ]
    result = EditableVideoEngine(project_root=tmp_path).scaffold(config)
    captions_ts = (
        Path(result["episode_dir"]) / "data/captions.ts"
    ).read_text(encoding="utf-8")
    assert "CaptionChunk[]" in captions_ts


def test_media_manifest_sources_are_project_relative(tmp_path: Path):
    make_channel(tmp_path)
    result = EditableVideoEngine(project_root=tmp_path).scaffold(
        make_episode_config()
    )
    media = json.loads(
        (Path(result["episode_dir"]) / "media.json").read_text(encoding="utf-8")
    )
    assert media["files"]
    assert all(not item["source"].startswith("/") for item in media["files"])


def test_overlapping_scenes_are_packed_into_separate_tracks(tmp_path: Path):
    make_channel(tmp_path)
    config = make_episode_config()
    config["scenes"][1]["startInSeconds"] = 2
    result = EditableVideoEngine(project_root=tmp_path).scaffold(config)
    tsx = (Path(result["episode_dir"]) / "Episode.tsx").read_text(encoding="utf-8")
    assert 'Track name="Cenas 2"' in tsx


def test_staging_failure_does_not_leave_partial_episode(tmp_path: Path):
    make_channel(tmp_path)
    outside = tmp_path.parent / f"outside-{tmp_path.name}.jpg"
    outside.write_bytes(b"outside")
    config = make_episode_config()
    config["scenes"][0]["mediaSrc"] = str(outside)
    with pytest.raises(EditableVideoError, match="escapes the project root"):
        EditableVideoEngine(project_root=tmp_path).scaffold(config)
    episode = tmp_path / "channels/test-channel/video/episodes/ep-test-16x9"
    assert not (episode / "Episode.tsx").exists()


def test_language_and_camera_are_normalized_for_typescript(tmp_path: Path):
    make_channel(tmp_path)
    config = make_episode_config()
    config["language"] = "pt-BR"
    config["scenes"][0]["cameraDirection"] = "slow_zoom_in"
    result = EditableVideoEngine(project_root=tmp_path).scaffold(config)
    tsx = (Path(result["episode_dir"]) / "Episode.tsx").read_text(encoding="utf-8")
    assert 'language={"pt"}' in tsx
    assert 'direction={"zoom-in"}' in tsx


def test_overlapping_scene_audio_is_lane_packed(tmp_path: Path):
    make_channel(tmp_path)
    config = make_episode_config()
    config["scenes"][0]["voiceoverAudioSrc"] = "media/raw/vo.wav"
    config["scenes"][1]["voiceoverAudioSrc"] = "media/raw/vo.wav"
    config["scenes"][1]["startInSeconds"] = 2
    result = EditableVideoEngine(project_root=tmp_path).scaffold(config)
    tsx = (Path(result["episode_dir"]) / "Episode.tsx").read_text(encoding="utf-8")
    assert 'Track name="Áudio de Cena 2"' in tsx


def test_music_attribute_escaping_uses_jsx_expression(tmp_path: Path):
    channel = make_channel(tmp_path)
    quote_file = channel / "media/raw/bed.wav\""
    quote_file.write_bytes(b"fake-quote-bed")
    config = make_episode_config()
    config["backgroundMusicSrc"] = 'media/raw/bed.wav"'
    result = EditableVideoEngine(project_root=tmp_path).scaffold(config)
    tsx = (Path(result["episode_dir"]) / "Episode.tsx").read_text(encoding="utf-8")
    assert r'backgroundMusicSrc={"music/bed.wav\""}' in tsx


def test_multi_act_captions_derive_cumulative_timelines(tmp_path: Path):
    make_channel(tmp_path)
    config = make_episode_config()
    config["captions"] = {
        "act_01": {
            "name": "act_01",
            "duration": 1.0,
            "words": [{"word": "UM", "start": 0.0, "end": 1.0}],
            "chunks": [
                {
                    "text": "UM",
                    "start": 0.0,
                    "end": 1.0,
                    "words": [{"word": "UM", "start": 0.0, "end": 1.0}],
                }
            ],
        },
        "act_02": {
            "name": "act_02",
            "duration": 1.0,
            "words": [{"word": "DOIS", "start": 0.0, "end": 1.0}],
            "chunks": [
                {
                    "text": "DOIS",
                    "start": 0.0,
                    "end": 1.0,
                    "words": [{"word": "DOIS", "start": 0.0, "end": 1.0}],
                }
            ],
        },
    }
    result = EditableVideoEngine(project_root=tmp_path).scaffold(config)
    tsx = (Path(result["episode_dir"]) / "Episode.tsx").read_text(encoding="utf-8")
    assert '"id": "act_01", "globalStart": 0.0, "globalEnd": 1.0' in tsx
    assert '"id": "act_02", "globalStart": 1.0, "globalEnd": 2.0' in tsx


def test_overlapping_scene_sfx_is_lane_packed(tmp_path: Path):
    make_channel(tmp_path)
    config = make_episode_config()
    config["scenes"][0]["sfxSrc"] = "media/raw/sfx.wav"
    config["scenes"][1]["sfxSrc"] = "media/raw/sfx.wav"
    config["scenes"][1]["startInSeconds"] = 2
    result = EditableVideoEngine(project_root=tmp_path).scaffold(config)
    tsx = (Path(result["episode_dir"]) / "Episode.tsx").read_text(encoding="utf-8")
    assert 'Track name="SFX de Cena 2"' in tsx


def test_outro_music_attribute_escaping_uses_jsx_expression(tmp_path: Path):
    channel = make_channel(tmp_path)
    quote_file = channel / "media/raw/outro.wav\""
    quote_file.write_bytes(b"fake-quote-outro")
    config = make_episode_config()
    config["outroMusicSrc"] = 'media/raw/outro.wav"'
    result = EditableVideoEngine(project_root=tmp_path).scaffold(config)
    tsx = (Path(result["episode_dir"]) / "Episode.tsx").read_text(encoding="utf-8")
    assert r'outroMusicSrc={"music/outro.wav\""}' in tsx


def test_remote_scene_audio_uses_resolve_media_src(tmp_path: Path):
    make_channel(tmp_path)
    config = make_episode_config()
    config["scenes"][0]["voiceoverAudioSrc"] = "https://example.test/vo.mp3"
    config["scenes"][2]["sfxSrc"] = "https://example.test/sfx.mp3"
    result = EditableVideoEngine(project_root=tmp_path).scaffold(config)
    tsx = (Path(result["episode_dir"]) / "Episode.tsx").read_text(encoding="utf-8")
    assert 'resolveMediaSrc("https://example.test/vo.mp3")' in tsx
    assert 'resolveMediaSrc("https://example.test/sfx.mp3")' in tsx
    assert 'staticFile("https://' not in tsx


def test_new_scene_types_generate_first_class_components(tmp_path: Path):
    make_channel(tmp_path)
    config = make_episode_config()
    config["scenes"] = [
        {
            "id": "tactical",
            "type": "tactical-map",
            "mediaSrc": "media/raw/a.jpg",
            "startInSeconds": 0,
            "durationInSeconds": 3,
            "headline": "Rota do arquivo",
            "badge": "MAPA",
            "coordinates": "23°33′S 46°38′W",
        },
        {
            "id": "stat",
            "type": "stat-counter",
            "startInSeconds": 3,
            "durationInSeconds": 3,
            "headline": "O número",
            "statValue": 1889,
            "statPrefix": "",
            "statSuffix": "",
            "statLabel": "Documentos",
        },
        {
            "id": "clip",
            "type": "video-clip",
            "mediaSrc": "media/raw/clip.mp4",
            "startInSeconds": 6,
            "durationInSeconds": 3,
            "headline": "Arquivo em movimento",
            "badge": "CLIPE",
            "notes": "Registro original",
            "videoMuted": True,
        },
    ]
    result = EditableVideoEngine(project_root=tmp_path).scaffold(config)
    tsx = (Path(result["episode_dir"]) / "Episode.tsx").read_text(encoding="utf-8")
    assert "<SceneTacticalMap" in tsx
    assert "<SceneStatCounter" in tsx
    assert "<SceneVideoClip" in tsx
    assert "value={1889}" in tsx
    assert "coordinates=\"23°33′S 46°38′W\"" in tsx or "23°33′S 46°38′W" in tsx
    assert "media/raw/clip.mp4" not in tsx
    assert "scenes/03_clip.mp4" in tsx


def test_scaffold_prunes_only_previous_generated_assets(tmp_path: Path):
    make_channel(tmp_path)
    old_config = make_episode_config()
    old_config["scenes"][0]["id"] = "old"
    old_result = EditableVideoEngine(project_root=tmp_path).scaffold(old_config)
    episode = Path(old_result["episode_dir"])
    old_target = episode / "public/scenes/01_old.jpg"
    assert old_target.is_file()
    user_file = episode / "public/scenes/custom.jpg"
    user_file.write_bytes(b"user")
    nested_keep = episode / "public/scenes/.gitkeep"
    nested_keep.write_bytes(b"")

    forced = EditableVideoEngine(project_root=tmp_path).scaffold(
        make_episode_config()
    )
    assert not old_target.exists()
    assert user_file.is_file()
    assert nested_keep.is_file()
    assert forced["pruned_files"] >= 1
