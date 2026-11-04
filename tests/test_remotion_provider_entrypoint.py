"""Remotion provider entry-point, public-dir and media-normalisation tests."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.engine.providers.base import ProviderError
from src.engine.providers.remotion_provider import RemotionProvider


def make_entry(root: Path) -> Path:
    entry = (
        root
        / "channels"
        / "test-channel"
        / "video"
        / "episodes"
        / "ep-test-16x9"
        / "index.ts"
    )
    entry.parent.mkdir(parents=True, exist_ok=True)
    entry.write_text("// entry\n", encoding="utf-8")
    return entry


def test_entry_point_and_public_dir_are_used(tmp_path: Path):
    entry = make_entry(tmp_path)
    public = tmp_path / "channels/test-channel/video/episodes/ep-test-16x9/public"
    public.mkdir(parents=True, exist_ok=True)
    media = tmp_path / "channels/test-channel/media/raw/a.jpg"
    media.parent.mkdir(parents=True, exist_ok=True)
    media.write_bytes(b"image")
    manifest = tmp_path / "channels/test-channel/video/episodes/ep-test-16x9/media.json"
    manifest.write_text(
        json.dumps(
            {
                "files": [
                    {
                        "source": "channels/test-channel/media/raw/a.jpg",
                        "target": "scenes/01.jpg",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    provider = RemotionProvider(project_root=tmp_path)
    provider._require = MagicMock(return_value=None)  # type: ignore[method-assign]
    out_dir = tmp_path / "out"

    def fake_run(cmd, **kwargs):
        Path(cmd[5]).write_bytes(b"rendered")
        return MagicMock(returncode=0, stdout="", stderr="")

    spec = {
        "composition": "Episode-ep-test-16x9",
        "channel_slug": "test-channel",
        "entry_point": entry.relative_to(tmp_path).as_posix(),
        "public_dir": public.relative_to(tmp_path).as_posix(),
        "media_manifest": manifest.relative_to(tmp_path).as_posix(),
        "props": {"imageSrc": str(media)},
        "output": "out.mp4",
        "format": "mp4",
    }
    with patch("src.engine.providers.remotion_provider.subprocess.run", side_effect=fake_run) as run:
        result = provider.render(spec, out_dir)

    cmd = run.call_args.args[0]
    assert entry.relative_to(tmp_path).as_posix() in " ".join(cmd)
    assert "--public-dir" in cmd
    assert result["media_replacements"] == 1
    props = json.loads((out_dir / "remotion_props.json").read_text(encoding="utf-8"))
    assert props["imageSrc"] == "scenes/01.jpg"
    assert result["entry_point"].endswith("index.ts")


def test_entry_point_outside_channel_is_rejected(tmp_path: Path):
    entry = make_entry(tmp_path)
    other = tmp_path / "channels" / "other" / "video" / "index.ts"
    other.parent.mkdir(parents=True, exist_ok=True)
    other.write_text("// other\n", encoding="utf-8")

    provider = RemotionProvider(project_root=tmp_path)
    errors = provider.validate(
        {
            "composition": "Episode-x",
            "channel_slug": "test-channel",
            "entry_point": other.relative_to(tmp_path).as_posix(),
        }
    )
    assert any("must stay inside channels/test-channel" in error for error in errors)


def test_entry_point_escape_is_rejected(tmp_path: Path):
    provider = RemotionProvider(project_root=tmp_path)
    errors = provider.validate(
        {
            "composition": "Episode-x",
            "channel_slug": "test-channel",
            "entry_point": "../../outside.ts",
        }
    )
    assert any("escapes the project root" in error for error in errors)


def test_public_dir_escape_is_rejected(tmp_path: Path):
    entry = make_entry(tmp_path)
    provider = RemotionProvider(project_root=tmp_path)
    errors = provider.validate(
        {
            "composition": "Episode-x",
            "channel_slug": "test-channel",
            "entry_point": entry.relative_to(tmp_path).as_posix(),
            "public_dir": "public",
        }
    )
    assert any("must stay inside channels/test-channel" in error for error in errors)


def test_missing_media_manifest_is_reported(tmp_path: Path):
    entry = make_entry(tmp_path)
    provider = RemotionProvider(project_root=tmp_path)
    errors = provider.validate(
        {
            "composition": "Episode-x",
            "channel_slug": "test-channel",
            "entry_point": entry.relative_to(tmp_path).as_posix(),
            "media_manifest": "channels/test-channel/missing.json",
        }
    )
    assert any("Media manifest not found" in error for error in errors)


def test_editable_recipe_does_not_force_stale_frame_range(tmp_path: Path):
    entry = make_entry(tmp_path)
    provider = RemotionProvider(project_root=tmp_path)
    provider._require = MagicMock(return_value=None)  # type: ignore[method-assign]
    out_dir = tmp_path / "out"

    def fake_run(cmd, **kwargs):
        Path(cmd[5]).write_bytes(b"rendered")
        return MagicMock(returncode=0, stdout="", stderr="")

    spec = {
        "composition": "Episode-ep-test-16x9",
        "channel_slug": "test-channel",
        "entry_point": entry.relative_to(tmp_path).as_posix(),
        "output": "out.mp4",
        "format": "mp4",
        "editable": True,
        "duration_frames": 100,
    }
    with patch(
        "src.engine.providers.remotion_provider.subprocess.run",
        side_effect=fake_run,
    ) as run:
        provider.render(spec, out_dir)
    cmd = run.call_args.args[0]
    assert "--frames" not in cmd


def test_open_studio_uses_provider_command(tmp_path: Path):
    entry = make_entry(tmp_path)
    public = tmp_path / "channels/test-channel/video/episodes/ep-test-16x9/public"
    public.mkdir(parents=True, exist_ok=True)
    provider = RemotionProvider(project_root=tmp_path)
    provider._require = MagicMock(return_value=None)  # type: ignore[method-assign]
    with patch(
        "src.engine.providers.remotion_provider.subprocess.run",
        return_value=MagicMock(returncode=0),
    ) as run:
        code = provider.open_studio(
            entry.relative_to(tmp_path).as_posix(),
            public_dir=public.relative_to(tmp_path).as_posix(),
            port=3010,
        )
    assert code == 0
    cmd = run.call_args.args[0]
    assert cmd[:4] == ["npx", "remotion", "studio", str(entry.resolve())]
    assert "--public-dir" in cmd
    assert "--port" in cmd


def test_prune_media_requires_episode_local_public_dir(tmp_path: Path):
    entry = make_entry(tmp_path)
    provider = RemotionProvider(project_root=tmp_path)
    base = {
        "composition": "Episode-x",
        "channel_slug": "test-channel",
        "entry_point": entry.relative_to(tmp_path).as_posix(),
        "prune_media": True,
    }
    errors = provider.validate(
        {
            **base,
            "public_dir": "channels/test-channel/public",
        }
    )
    assert any("episode-local public dir" in error for error in errors)
    errors = provider.validate(
        {
            **base,
            "public_dir": "channels/test-channel/video/episodes",
        }
    )
    assert any("episode-local public dir" in error for error in errors)

    episode_public = (
        tmp_path
        / "channels/test-channel/video/episodes/ep-test-16x9/public"
    )
    episode_public.mkdir(parents=True, exist_ok=True)
    errors = provider.validate(
        {**base, "public_dir": episode_public.relative_to(tmp_path).as_posix()}
    )
    assert errors == []


def test_provider_prunes_only_indexed_stale_media(tmp_path: Path):
    from src.engine.media_stager import MediaStager

    entry = make_entry(tmp_path)
    public = tmp_path / "channels/test-channel/video/episodes/ep-test-16x9/public"
    public.mkdir(parents=True, exist_ok=True)
    media = tmp_path / "channels/test-channel/media/raw/a.jpg"
    media.parent.mkdir(parents=True, exist_ok=True)
    media.write_bytes(b"image")
    old_manifest = tmp_path / "channels/test-channel/video/episodes/ep-test-16x9/old.json"
    old_manifest.write_text(
        json.dumps(
            {
                "files": [
                    {
                        "source": "channels/test-channel/media/raw/a.jpg",
                        "target": "scenes/old.jpg",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    stager = MediaStager(tmp_path)
    stager.ensure(old_manifest, public.relative_to(tmp_path).as_posix())
    user_file = public / "scenes/custom.jpg"
    user_file.write_bytes(b"user")
    new_manifest = tmp_path / "channels/test-channel/video/episodes/ep-test-16x9/media.json"
    new_manifest.write_text(
        json.dumps(
            {
                "files": [
                    {
                        "source": "channels/test-channel/media/raw/a.jpg",
                        "target": "scenes/01.jpg",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    provider = RemotionProvider(project_root=tmp_path)
    provider._require = MagicMock(return_value=None)  # type: ignore[method-assign]
    out_dir = tmp_path / "out"

    def fake_run(cmd, **kwargs):
        Path(cmd[5]).write_bytes(b"rendered")
        return MagicMock(returncode=0, stdout="", stderr="")

    spec = {
        "composition": "Episode-ep-test-16x9",
        "channel_slug": "test-channel",
        "entry_point": entry.relative_to(tmp_path).as_posix(),
        "public_dir": public.relative_to(tmp_path).as_posix(),
        "media_manifest": new_manifest.relative_to(tmp_path).as_posix(),
        "prune_media": True,
        "props": {},
        "output": "out.mp4",
        "format": "mp4",
    }
    with patch(
        "src.engine.providers.remotion_provider.subprocess.run",
        side_effect=fake_run,
    ):
        result = provider.render(spec, out_dir)

    assert not (public / "scenes/old.jpg").exists()
    assert (public / "scenes/01.jpg").is_file()
    assert user_file.is_file()
    assert result["media_pruned"]["files"] == 1
