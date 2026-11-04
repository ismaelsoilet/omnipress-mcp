"""Media staging and staticFile path-safety tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from src.engine.media_stager import MediaStageError, MediaStager


def _make_media(root: Path) -> Path:
    source = root / "channels" / "test-channel" / "media" / "raw" / "a.jpg"
    source.parent.mkdir(parents=True, exist_ok=True)
    source.write_bytes(b"fake-image-content")
    return source


def test_stage_and_normalize_props(tmp_path: Path):
    source = _make_media(tmp_path)
    manifest = {
        "files": [
            {
                "source": "channels/test-channel/media/raw/a.jpg",
                "target": "scenes/01.jpg",
            }
        ]
    }
    stager = MediaStager(tmp_path)
    report = stager.ensure(manifest, "channels/test-channel/public")

    assert report["files"][0]["copied"] is True
    assert (tmp_path / "channels/test-channel/public/scenes/01.jpg").is_file()
    assert report["mapping"][str(source)] == "scenes/01.jpg"

    props = {"src": str(source), "nested": {"before": str(source)}}
    normalized, replacements = stager.normalize_props(
        props, "channels/test-channel/public", mapping=report["mapping"]
    )
    assert normalized == {
        "src": "scenes/01.jpg",
        "nested": {"before": "scenes/01.jpg"},
    }
    assert len(replacements) == 2


def test_staging_is_idempotent(tmp_path: Path):
    _make_media(tmp_path)
    manifest = {
        "files": [
            {
                "source": "channels/test-channel/media/raw/a.jpg",
                "target": "scenes/01.jpg",
            }
        ]
    }
    stager = MediaStager(tmp_path)
    first = stager.ensure(manifest, "channels/test-channel/public")
    second = stager.ensure(manifest, "channels/test-channel/public")
    assert first["files"][0]["copied"] is True
    assert second["files"][0]["copied"] is False


def test_rejects_source_outside_project(tmp_path: Path):
    outside = tmp_path.parent / "outside.jpg"
    outside.write_bytes(b"outside")
    stager = MediaStager(tmp_path)
    with pytest.raises(MediaStageError, match="escapes the project root"):
        stager.ensure(
            {"files": [{"source": str(outside), "target": "a.jpg"}]},
            "public",
        )


def test_rejects_unsafe_target(tmp_path: Path):
    _make_media(tmp_path)
    stager = MediaStager(tmp_path)
    with pytest.raises(MediaStageError, match="Unsafe media target"):
        stager.ensure(
            {
                "files": [
                    {
                        "source": "channels/test-channel/media/raw/a.jpg",
                        "target": "../escape.jpg",
                    }
                ]
            },
            "public",
        )


def test_legacy_normalization_accepts_absolute_media(tmp_path: Path):
    source = _make_media(tmp_path)
    stager = MediaStager(tmp_path)
    normalized, replacements = stager.normalize_props(
        {"src": str(source)}, "channels/test-channel/public"
    )
    target = normalized["src"]
    assert target.startswith("_legacy/")
    assert (tmp_path / "channels/test-channel/public" / target).is_file()
    assert replacements[0]["from"] == str(source)


def test_remote_and_relative_paths_are_left_untouched(tmp_path: Path):
    stager = MediaStager(tmp_path)
    props = {
        "remote": "https://example.test/image.jpg",
        "relative": "scenes/01.jpg",
        "empty": "",
    }
    normalized, replacements = stager.normalize_props(
        props, "channels/test-channel/public"
    )
    assert normalized == props
    assert replacements == []


def test_relative_source_mapping_rewrites_props(tmp_path: Path):
    _make_media(tmp_path)
    manifest = {
        "files": [
            {
                "source": "channels/test-channel/media/raw/a.jpg",
                "target": "scenes/01.jpg",
            }
        ]
    }
    stager = MediaStager(tmp_path)
    report = stager.ensure(manifest, "channels/test-channel/public")
    normalized, replacements = stager.normalize_props(
        {"src": "channels/test-channel/media/raw/a.jpg"},
        "channels/test-channel/public",
        mapping=report["mapping"],
    )
    assert normalized["src"] == "scenes/01.jpg"
    assert replacements == [
        {
            "from": "channels/test-channel/media/raw/a.jpg",
            "to": "scenes/01.jpg",
        }
    ]


def test_prune_removes_stale_generated_files_and_preserves_user_files(tmp_path: Path):
    source = _make_media(tmp_path)
    manifest = {
        "files": [
            {
                "source": "channels/test-channel/media/raw/a.jpg",
                "target": "scenes/01.jpg",
            }
        ]
    }
    stager = MediaStager(tmp_path)
    stager.ensure(manifest, "channels/test-channel/public")
    public = tmp_path / "channels/test-channel/public"
    (public / "scenes/stale.jpg").write_bytes(b"stale")
    (public / ".gitkeep").write_bytes(b"")
    (public / "custom.txt").write_bytes(b"keep")

    report = stager.prune(manifest, "channels/test-channel/public")

    assert "scenes/stale.jpg" in report["removed"]
    assert (public / "scenes/01.jpg").is_file()
    assert (public / "custom.txt").is_file()
    assert (public / ".gitkeep").is_file()
    assert source.is_file()
