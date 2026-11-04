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


def test_prune_removes_only_previously_generated_files_and_preserves_users(tmp_path: Path):
    source = _make_media(tmp_path)
    stager = MediaStager(tmp_path)
    public = tmp_path / "channels/test-channel/public"
    old_manifest = {
        "files": [
            {
                "source": "channels/test-channel/media/raw/a.jpg",
                "target": "scenes/old.jpg",
            }
        ]
    }
    stager.ensure(old_manifest, "channels/test-channel/public")
    previous_index = stager.read_index("channels/test-channel/public")

    (public / "scenes/custom.jpg").write_bytes(b"user-file")
    (public / "scenes/.gitkeep").write_bytes(b"")
    (public / "custom-dir").mkdir()
    (public / "custom-dir/user.txt").write_bytes(b"keep")

    new_manifest = {
        "files": [
            {
                "source": "channels/test-channel/media/raw/a.jpg",
                "target": "scenes/01.jpg",
            }
        ]
    }
    stager.ensure(new_manifest, "channels/test-channel/public", write_index=False)
    report = stager.prune(
        new_manifest,
        "channels/test-channel/public",
        previous=previous_index,
    )

    assert "scenes/old.jpg" in report["removed"]
    assert (public / "scenes/01.jpg").is_file()
    assert (public / "scenes/custom.jpg").is_file()
    assert (public / "scenes/.gitkeep").is_file()
    assert (public / "custom-dir/user.txt").is_file()
    assert (public / ".staging-index.json").is_file()
    assert source.is_file()

    second = stager.prune(new_manifest, "channels/test-channel/public")
    assert second["removed"] == []
