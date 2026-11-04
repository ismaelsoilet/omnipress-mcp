"""Generate editable per-episode Remotion TSX from an episode config.

The generated episode lives entirely inside the channel workspace:

    channels/<slug>/video/episodes/<episode>-<aspect>/
        Episode.tsx
        index.ts
        meta.json
        media.json
        data/captions.ts
        data/theme.ts
        video_recipe.editable.json
        public/  (generated staging, gitignored)

After scaffolding, the generated TSX is the source of truth for that episode.
The JSON config remains the input used to (re)generate it.
"""

from __future__ import annotations

import datetime
import hashlib
import json
import re
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from src.core.channel_manager import ChannelManager, slugify_channel
from src.engine.media_stager import MediaStager

PROJECT_ROOT = Path(__file__).resolve().parents[2]

ASPECT_DIMENSIONS: Dict[str, Tuple[int, int]] = {
    "16:9": (1920, 1080),
    "9:16": (1080, 1920),
    "1:1": (1080, 1080),
    "4:5": (1080, 1350),
    "3:4": (1080, 1440),
}

REMOTE_PREFIXES = ("http://", "https://", "data:", "blob:")

DEFAULT_THEME = {
    "primary": "#3B82F6",
    "accent": "#3B82F6",
    "highlight": "#FACC15",
    "background": "#0B1220",
    "text": "#FFFFFF",
    "secondaryText": "#94A3B8",
    "success": "#10B981",
    "danger": "#EF4444",
}

CORE_PUBLIC = "../../../../../src/video/public"
CORE_PUBLIC_DATA = "../../../../../../src/video/public"


class EditableVideoError(RuntimeError):
    """Raised when an editable episode cannot be generated safely."""


def _js(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False)


def _js_prop(name: str, value: Any, *, number: bool = False) -> str:
    if number:
        return f'{name}={{{int(value)}}}'
    return f"{name}={{{_js(value)}}}"


def _slug(value: str, fallback: str = "episode") -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9_-]+", "-", str(value or "").strip().lower())
    cleaned = re.sub(r"-{2,}", "-", cleaned).strip("-")
    return cleaned or fallback


def _aspect_slug(aspect_ratio: str) -> str:
    return str(aspect_ratio).replace(":", "x").replace("/", "x")


def _hash_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _hash_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class EditableVideoEngine:
    """Scaffold a single Remotion episode with explicit, editable scene nodes."""

    def __init__(
        self,
        channel_manager: Optional[ChannelManager] = None,
        project_root: Optional[Union[str, Path]] = None,
    ):
        self.project_root = Path(
            project_root
            or (getattr(channel_manager, "root_dir", None) if channel_manager else None)
            or PROJECT_ROOT
        ).resolve()
        self.channel_manager = channel_manager or ChannelManager(self.project_root)
        self.stager = MediaStager(self.project_root)

    # ------------------------------------------------------------------
    # Input loading
    # ------------------------------------------------------------------
    def _load_config(
        self,
        config: Union[str, Path, Dict[str, Any]],
    ) -> Tuple[Dict[str, Any], Optional[Path]]:
        source_path: Optional[Path] = None
        if isinstance(config, (str, Path)):
            source_path = Path(config).resolve()
            if not source_path.is_file():
                raise EditableVideoError(f"Config not found: {source_path}")
            data = json.loads(source_path.read_text(encoding="utf-8"))
        else:
            data = dict(config)

        # Accept a video_recipe.json wrapper as a convenience.
        if isinstance(data.get("config"), dict):
            wrapped = dict(data["config"])
            for key in ("enableIntro", "introDurationFrames", "enable_intro", "intro_duration_frames"):
                if key in data and key not in wrapped:
                    wrapped[key] = data[key]
            data = wrapped

        if not isinstance(data.get("scenes"), list):
            raise EditableVideoError("Config must contain a scenes list")
        return data, source_path

    def _resolve_channel(self, slug: str) -> Tuple[str, Dict[str, Any], Path]:
        clean_slug = slugify_channel(slug)
        channel = self.channel_manager.get_channel(clean_slug)
        if not channel:
            raise EditableVideoError(f"Channel not found: {clean_slug}")
        return clean_slug, channel, self.channel_manager.get_channel_dir(clean_slug)

    # ------------------------------------------------------------------
    # Theme and media
    # ------------------------------------------------------------------
    @staticmethod
    def _build_theme(config: Dict[str, Any], channel: Dict[str, Any]) -> Dict[str, str]:
        vis = channel.get("visual_identity") or {}
        palette = vis.get("palette") or {}
        branding = channel.get("branding") or {}
        brand_colors = branding.get("theme_colors") or {}
        source = config.get("theme") or {}

        def pick(*values: Any) -> str:
            for value in values:
                if isinstance(value, str) and value.strip():
                    return value.strip()
            return ""

        return {
            "primary": pick(source.get("primary"), brand_colors.get("primary"), palette.get("primary"), DEFAULT_THEME["primary"]),
            "accent": pick(source.get("accent"), palette.get("accent"), palette.get("primary"), DEFAULT_THEME["accent"]),
            "highlight": pick(source.get("highlight"), palette.get("highlight"), DEFAULT_THEME["highlight"]),
            "background": pick(source.get("background"), brand_colors.get("background"), palette.get("background"), DEFAULT_THEME["background"]),
            "text": pick(source.get("text"), brand_colors.get("text"), palette.get("text"), DEFAULT_THEME["text"]),
            "secondaryText": pick(source.get("secondaryText"), source.get("secondary_text"), brand_colors.get("secondary_text"), palette.get("secondary_text"), DEFAULT_THEME["secondaryText"]),
            "success": pick(source.get("success"), palette.get("success"), DEFAULT_THEME["success"]),
            "danger": pick(source.get("danger"), DEFAULT_THEME["danger"]),
        }

    def _resolve_media(self, value: Any, channel_dir: Path) -> Optional[Path]:
        raw = str(value or "").strip()
        if not raw:
            return None
        if raw.startswith(REMOTE_PREFIXES):
            return None
        candidate = Path(raw)
        candidates = (
            [candidate]
            if candidate.is_absolute()
            else [
                self.project_root / candidate,
                channel_dir / candidate,
                self.project_root / "public" / candidate,
            ]
        )
        for item in candidates:
            if item.is_file():
                return item.resolve()
        raise EditableVideoError(f"Media not found for editable episode: {raw}")

    @staticmethod
    def _target_suffix(source: Path, fallback: str) -> str:
        return source.suffix.lower() or fallback

    def _build_media_plan(
        self,
        config: Dict[str, Any],
        channel_dir: Path,
        episode_slug: str,
        aspect_slug: str,
        intro_frames: int,
        fps: int,
    ) -> Tuple[List[Dict[str, str]], Dict[str, str], List[str]]:
        entries: List[Dict[str, str]] = []
        targets: Dict[str, str] = {}
        warnings: List[str] = []

        def add(source_value: Any, target: str) -> str:
            source = self._resolve_media(source_value, channel_dir)
            if source is None:
                return str(source_value or "")
            try:
                source_ref = source.relative_to(self.project_root).as_posix()
            except ValueError as exc:
                raise EditableVideoError(
                    f"Media source escapes the project root: {source}"
                ) from exc
            entries.append({"source": source_ref, "target": target})
            return target

        scenes = config.get("scenes") or []
        for index, scene in enumerate(scenes, start=1):
            scene_id = _slug(str(scene.get("id") or f"scene-{index:02d}"))
            scene_type = str(scene.get("type") or "ken-burns")

            media_value = scene.get("mediaSrc") or scene.get("media")
            if scene_type in ("ken-burns", "tactical-map", "video-clip"):
                if media_value:
                    suffix = self._target_suffix(
                        self._resolve_media(media_value, channel_dir) or Path("x.jpg"),
                        ".jpg",
                    )
                    targets[f"media:{index}"] = add(
                        media_value, f"scenes/{index:02d}_{scene_id}{suffix}"
                    )
                else:
                    warnings.append(f"Scene {scene_id} has no mediaSrc")
            elif scene_type == "stat-counter":
                if media_value:
                    suffix = self._target_suffix(
                        self._resolve_media(media_value, channel_dir) or Path("x.jpg"),
                        ".jpg",
                    )
                    targets[f"media:{index}"] = add(
                        media_value, f"scenes/{index:02d}_{scene_id}{suffix}"
                    )
            elif scene_type in ("heraldic-surgery", "image-morph"):
                before_value = scene.get("beforeSrc") or media_value
                after_value = scene.get("afterSrc")
                if before_value:
                    before_source = self._resolve_media(before_value, channel_dir)
                    suffix = self._target_suffix(before_source or Path("x.jpg"), ".jpg")
                    targets[f"before:{index}"] = add(
                        before_value, f"scenes/{index:02d}_{scene_id}_before{suffix}"
                    )
                if after_value:
                    after_source = self._resolve_media(after_value, channel_dir)
                    suffix = self._target_suffix(after_source or Path("x.jpg"), ".jpg")
                    targets[f"after:{index}"] = add(
                        after_value, f"scenes/{index:02d}_{scene_id}_after{suffix}"
                    )
            elif scene_type == "channel-outro":
                for key in ("avatarSrc", "bannerSrc"):
                    if scene.get(key):
                        source = self._resolve_media(scene[key], channel_dir)
                        suffix = self._target_suffix(source or Path("x.jpg"), ".jpg")
                        targets[f"{key}:{index}"] = add(
                            scene[key], f"scenes/{index:02d}_{scene_id}_{key}{suffix}"
                        )

            if scene.get("voiceoverAudioSrc"):
                source = self._resolve_media(scene["voiceoverAudioSrc"], channel_dir)
                suffix = self._target_suffix(source or Path("x.mp3"), ".mp3")
                targets[f"scene-vo:{index}"] = add(
                    scene["voiceoverAudioSrc"], f"audio/scene_{index:02d}{suffix}"
                )
            if scene.get("sfxSrc"):
                source = self._resolve_media(scene["sfxSrc"], channel_dir)
                suffix = self._target_suffix(source or Path("x.mp3"), ".mp3")
                targets[f"sfx:{index}"] = add(
                    scene["sfxSrc"], f"sfx/{index:02d}{suffix}"
                )

        for index, voiceover in enumerate(config.get("voiceovers") or [], start=1):
            src = voiceover.get("src")
            if not src:
                continue
            source = self._resolve_media(src, channel_dir)
            suffix = self._target_suffix(source or Path("x.mp3"), ".mp3")
            voiceover_id = _slug(str(voiceover.get("id") or f"vo-{index:02d}"))
            targets[f"vo:{index}"] = add(
                src, f"audio/vo_{index:02d}_{voiceover_id}{suffix}"
            )

        music = config.get("backgroundMusicSrc")
        if music:
            source = self._resolve_media(music, channel_dir)
            suffix = self._target_suffix(source or Path("x.mp3"), ".mp3")
            targets["music"] = add(music, f"music/bed{suffix}")

        outro_music = config.get("outroMusicSrc")
        if outro_music:
            source = self._resolve_media(outro_music, channel_dir)
            suffix = self._target_suffix(source or Path("x.mp3"), ".mp3")
            targets["outro-music"] = add(outro_music, f"music/outro{suffix}")

        return entries, targets, warnings

    # ------------------------------------------------------------------
    # TSX generation
    # ------------------------------------------------------------------
    def _scene_tsx(
        self,
        scene: Dict[str, Any],
        index: int,
        start_frame: int,
        duration_frames: int,
        targets: Dict[str, str],
        theme: Dict[str, str],
        intro_props: Dict[str, Any],
        channel: Dict[str, Any],
    ) -> Tuple[str, bool]:
        scene_id = _slug(str(scene.get("id") or f"scene-{index:02d}"))
        scene_type = str(scene.get("type") or "ken-burns")
        headline = str(scene.get("headline") or "")
        scene_name = f"Cena {index:02d} — {headline or scene_type}"
        common = [
            _js_prop("name", scene_name),
            _js_prop("from", start_frame, number=True),
            _js_prop("durationInFrames", duration_frames, number=True),
        ]

        media = targets.get(f"media:{index}")
        if not media:
            raw = scene.get("mediaSrc") or scene.get("media") or ""
            media = str(raw) if str(raw).startswith(REMOTE_PREFIXES) else ""

        if scene_type == "document-reveal":
            props = [
                *common,
                _js_prop("headline", headline),
                _js_prop("subheadline", str(scene.get("subheadline") or "")),
                _js_prop("badge", str(scene.get("badge") or "")),
                _js_prop("accentColor", theme["accent"]),
                _js_prop("dangerColor", theme["danger"]),
            ]
            return f"<SceneDocumentReveal {' '.join(props)} />", False

        if scene_type == "channel-outro":
            props = [
                *common,
                _js_prop(
                    "channelName",
                    str(intro_props.get("channelName") or (channel.get("branding") or {}).get("name") or ""),
                ),
                _js_prop(
                    "primaryColor",
                    str(intro_props.get("primaryColor") or theme["primary"]),
                ),
                _js_prop("tagline", str(intro_props.get("subText") or "")),
            ]
            if f"avatarSrc:{index}" in targets:
                props.append(_js_prop("avatarSrc", targets[f"avatarSrc:{index}"]))
            if f"bannerSrc:{index}" in targets:
                props.append(_js_prop("bannerSrc", targets[f"bannerSrc:{index}"]))
            return f"<SceneOutro {' '.join(props)} />", False

        if scene_type == "tactical-map":
            props = [
                *common,
                _js_prop("imageSrc", media),
                _js_prop("headline", headline),
                _js_prop("badge", str(scene.get("badge") or "")),
                _js_prop("coordinates", str(scene.get("coordinates") or "")),
                _js_prop("accentColor", theme["accent"]),
            ]
            return f"<SceneTacticalMap {' '.join(props)} />", False

        if scene_type == "stat-counter":
            raw_value = scene.get("statValue", scene.get("value", 0))
            try:
                stat_value = int(float(raw_value or 0))
            except (TypeError, ValueError):
                stat_value = 0
            props = [
                *common,
                _js_prop("value", stat_value, number=True),
                _js_prop("prefix", str(scene.get("statPrefix") or "")),
                _js_prop("suffix", str(scene.get("statSuffix") or "")),
                _js_prop(
                    "label",
                    str(scene.get("statLabel") or scene.get("subheadline") or ""),
                ),
                _js_prop("headline", headline),
                _js_prop("accentColor", theme["highlight"]),
                _js_prop("backgroundSrc", media),
            ]
            return f"<SceneStatCounter {' '.join(props)} />", False

        if scene_type == "video-clip":
            muted = bool(scene.get("videoMuted", True))
            props = [
                *common,
                _js_prop("videoSrc", media),
                _js_prop("headline", headline),
                _js_prop("badge", str(scene.get("badge") or "")),
                _js_prop("overlayText", str(scene.get("notes") or "")),
                f"muted={{{'true' if muted else 'false'}}}",
            ]
            return f"<SceneVideoClip {' '.join(props)} />", False

        if scene_type in ("heraldic-surgery", "image-morph"):
            props = [
                *common,
                _js_prop("beforeSrc", targets.get(f"before:{index}", "")),
                _js_prop("afterSrc", targets.get(f"after:{index}", "")),
                _js_prop("badge", str(scene.get("badge") or "METAMORFOSE VISUAL")),
            ]
            return f"<SceneHeraldic {' '.join(props)} />", False

        # ken-burns fallback for unknown scene types
        direction_map = {
            "slow_zoom_in": "zoom-in",
            "slow_zoom_out": "zoom-out",
            "pan_left": "pan-left",
            "pan_right": "pan-right",
            "static": "subtle-zoom",
        }
        direction_raw = str(scene.get("cameraDirection") or "zoom-in")
        direction = direction_map.get(direction_raw, direction_raw)
        valid_directions = {
            "zoom-in",
            "zoom-out",
            "pan-left",
            "pan-right",
            "snap-zoom",
            "dramatic-push",
            "tilt-down",
            "subtle-zoom",
        }
        if direction not in valid_directions:
            direction = "zoom-in"
        props = [
            *common,
            _js_prop("imageSrc", media),
            _js_prop("direction", direction),
            _js_prop("badge", str(scene.get("badge") or "")),
            _js_prop("headline", headline),
            _js_prop("caption", str(scene.get("notes") or "")),
        ]
        unknown = scene_type not in (
            "ken-burns",
        )
        return f"<SceneKenBurns {' '.join(props)} />", unknown

    @staticmethod
    def _pack_track_blocks(
        items: List[Tuple[int, int, str]], base_name: str
    ) -> str:
        lanes: List[List[Tuple[int, int, str]]] = []
        for item in items:
            placed = False
            for lane in lanes:
                if all(
                    item[1] <= other[0] or item[0] >= other[1]
                    for other in lane
                ):
                    lane.append(item)
                    placed = True
                    break
            if not placed:
                lanes.append([item])

        blocks: List[str] = []
        for lane_index, lane in enumerate(lanes):
            track_name = (
                base_name if lane_index == 0 else f"{base_name} {lane_index + 1}"
            )
            blocks.append(
                f'      <Track name="{track_name}">\n'
                + "\n".join(node for _, _, node in lane)
                + "\n      </Track>"
            )
        return "\n".join(blocks)

    def _build_tsx(
        self,
        config: Dict[str, Any],
        channel: Dict[str, Any],
        theme: Dict[str, str],
        targets: Dict[str, str],
        intro_frames: int,
        fps: int,
        duration_frames: int,
        episode_slug: str,
        warnings: List[str],
        act_timelines: List[Dict[str, Any]],
    ) -> str:
        scenes = config.get("scenes") or []
        intro_props = config.get("introProps") or {}
        cursor = 0.0
        scene_timeline: List[Tuple[int, int, str]] = []
        scene_audio_timeline: List[Tuple[int, int, str]] = []
        sfx_timeline: List[Tuple[int, int, str]] = []

        for index, scene in enumerate(scenes, start=1):
            start_seconds = scene.get("startInSeconds")
            if start_seconds is None:
                start_seconds = cursor
            start_seconds = float(start_seconds)
            duration_seconds = float(scene.get("durationInSeconds") or 3.0)
            start_frame = intro_frames + round(start_seconds * fps)
            scene_frames = max(1, round(duration_seconds * fps))
            cursor = max(cursor, start_seconds + duration_seconds)

            node, unknown = self._scene_tsx(
                scene,
                index,
                start_frame,
                scene_frames,
                targets,
                theme,
                intro_props,
                channel,
            )
            scene_timeline.append(
                (start_frame, start_frame + scene_frames, f"        {node}")
            )
            if unknown:
                warnings.append(
                    f"Scene {scene.get('id') or index} has unsupported type "
                    f"'{scene.get('type')}'; rendered as SceneKenBurns"
                )

            scene_vo = targets.get(f"scene-vo:{index}")
            if scene_vo:
                node = f"""        <Sequence name="VO de cena {index:02d}" from={{{start_frame}}} durationInFrames={{{scene_frames}}}>
          <Audio src={{resolveMediaSrc({_js(scene_vo)})}} volume={{1.0}} />
        </Sequence>"""
                scene_audio_timeline.append(
                    (start_frame, start_frame + scene_frames, node)
                )
            scene_sfx = targets.get(f"sfx:{index}")
            if scene_sfx:
                sfx_frames = min(scene_frames, 120)
                node = f"""        <Sequence name="SFX de cena {index:02d}" from={{{start_frame}}} durationInFrames={{{sfx_frames}}}>
          <Audio src={{resolveMediaSrc({_js(scene_sfx)})}} volume={{{float(scene.get("sfxVolume") or 0.35)}}} />
        </Sequence>"""
                sfx_timeline.append(
                    (start_frame, start_frame + sfx_frames, node)
                )

        scene_tracks_block = self._pack_track_blocks(scene_timeline, "Cenas")

        voiceovers: List[Dict[str, Any]] = []
        for index, voiceover in enumerate(config.get("voiceovers") or [], start=1):
            target = targets.get(f"vo:{index}")
            if not target:
                continue
            voiceovers.append(
                {
                    "id": str(voiceover.get("id") or f"vo_{index:02d}"),
                    "src": target,
                    "startInSeconds": float(
                        voiceover.get("startInSeconds")
                        or voiceover.get("start_seconds")
                        or 0
                    )
                    + intro_frames / fps,
                    "durationInSeconds": float(
                        voiceover.get("durationInSeconds")
                        or voiceover.get("duration_seconds")
                        or cursor
                        or 1.0
                    ),
                    "volume": float(voiceover.get("volume") or 1.0),
                }
            )

        intro_block = ""
        if intro_frames > 0:
            language_raw = str(
                intro_props.get("language")
                or config.get("language")
                or "pt"
            ).lower()
            intro_language = "en" if language_raw.startswith("en") else "pt"
            intro_attrs = " ".join(
                [
                    _js_prop(
                        "channelName", str(intro_props.get("channelName") or "")
                    ),
                    _js_prop(
                        "badgeText", str(intro_props.get("badgeText") or "")
                    ),
                    _js_prop("subText", str(intro_props.get("subText") or "")),
                    _js_prop(
                        "classifiedCode",
                        str(intro_props.get("classifiedCode") or ""),
                    ),
                    _js_prop(
                        "primaryColor",
                        str(intro_props.get("primaryColor") or theme["primary"]),
                    ),
                    _js_prop(
                        "backgroundColor",
                        str(
                            intro_props.get("backgroundColor")
                            or theme["background"]
                        ),
                    ),
                    _js_prop("language", intro_language),
                ]
            )
            intro_block = f"""      <Track name="Vinheta">
        <Sequence name="Vinheta de abertura" from={{0}} durationInFrames={{{intro_frames}}}>
          <ChannelIntro {intro_attrs} />
        </Sequence>
      </Track>
"""

        scene_audio_block = self._pack_track_blocks(
            scene_audio_timeline, "Áudio de Cena"
        )
        if scene_audio_block:
            scene_audio_block += "\n"

        sfx_block = self._pack_track_blocks(sfx_timeline, "SFX de Cena")
        if sfx_block:
            sfx_block += "\n"

        background_music = targets.get("music", "")
        outro_music = targets.get("outro-music", "")
        outro_start = float(config.get("outroMusicStartSec") or 0)
        music_volume = float(config.get("backgroundMusicVolume") or 0.16)

        return f"""// AUTO-GENERATED by OmniPress — manual edits are protected by the hash guard.
// Retiming from/durationInFrames can desync narration and captions. Prefer visual edits.
import React from "react";
import {{ Audio, Sequence, Track }} from "remotion";
import {{
  ChannelIntro,
  EpisodeShell,
  SceneDocumentReveal,
  SceneHeraldic,
  SceneKenBurns,
  SceneOutro,
  SceneStatCounter,
  SceneTacticalMap,
  SceneVideoClip,
  resolveMediaSrc,
}} from {_js(CORE_PUBLIC)};
import {{ captions }} from "./data/captions";
import {{ theme }} from "./data/theme";

export const Episode: React.FC = () => {{
  return (
    <EpisodeShell
      theme={{theme}}
      {_js_prop("backgroundMusicSrc", background_music)}
      backgroundMusicVolume={{{music_volume}}}
      {_js_prop("outroMusicSrc", outro_music)}
      outroMusicStartSec={{{outro_start}}}
      voiceovers={{{json.dumps(voiceovers, ensure_ascii=False)}}}
      captions={{captions}}
      actTimelines={{{json.dumps(act_timelines, ensure_ascii=False)}}}
      captionsIntroDurationFrames={{{intro_frames}}}
      introDurationFrames={{{intro_frames}}}
    >
{intro_block}{scene_tracks_block}
{scene_audio_block}{sfx_block}    </EpisodeShell>
  );
}};
"""

    def _build_index_ts(self, composition_id: str, duration_frames: int, width: int, height: int, fps: int) -> str:
        return f"""// AUTO-GENERATED by OmniPress — manual edits are protected by the hash guard.
import {{ registerRoot }} from "remotion";
import {{ createEpisodeRoot }} from {_js(CORE_PUBLIC)};
import {{ Episode }} from "./Episode";

registerRoot(
  createEpisodeRoot({{
    id: {_js(composition_id)},
    component: Episode,
    width: {width},
    height: {height},
    fps: {fps},
    durationInFrames: {duration_frames},
    defaultProps: {{}},
  }}),
);
"""

    @staticmethod
    def _normalize_captions(
        captions: Any,
    ) -> Tuple[Any, List[Dict[str, Any]], str]:
        """Normalize align-captions payloads into a Studio-safe captions shape."""
        if isinstance(captions, list):
            return captions, [], "CaptionChunk[]"
        if not isinstance(captions, dict):
            return {}, [], "Record<string, ActData>"

        acts = {
            key: value
            for key, value in captions.items()
            if isinstance(value, dict) and isinstance(value.get("chunks"), list)
        }
        if acts:
            timelines: List[Dict[str, Any]] = []
            cursor = 0.0
            for act_id, act in acts.items():
                start = float(act.get("start") or cursor)
                duration = float(act.get("duration") or 0)
                if duration <= 0 and act.get("chunks"):
                    duration = max(
                        float(chunk.get("end") or 0)
                        for chunk in act["chunks"]
                    )
                global_end = start + duration
                timelines.append(
                    {
                        "id": str(act_id),
                        "globalStart": start,
                        "globalEnd": global_end,
                    }
                )
                cursor = max(cursor, global_end)
            return acts, timelines, "Record<string, ActData>"

        if isinstance(captions.get("chunks"), list):
            return captions["chunks"], [], "CaptionChunk[]"

        return captions, [], "Record<string, ActData>"

    @staticmethod
    def _build_captions_ts(captions: Any, type_name: str) -> str:
        return f"""// AUTO-GENERATED by OmniPress — manual edits are protected by the hash guard.
import type {{ ActData, CaptionChunk }} from {_js(CORE_PUBLIC_DATA)};

export const captions: {type_name} = {json.dumps(captions, ensure_ascii=False, indent=2)};
"""

    @staticmethod
    def _build_theme_ts(theme: Dict[str, str]) -> str:
        return f"""// AUTO-GENERATED by OmniPress — manual edits are protected by the hash guard.
import type {{ EpisodeTheme }} from {_js(CORE_PUBLIC_DATA)};

export const theme: EpisodeTheme = {json.dumps(theme, ensure_ascii=False, indent=2)};
"""

    # ------------------------------------------------------------------
    # Guard and writing
    # ------------------------------------------------------------------
    def _check_guard(
        self,
        episode_dir: Path,
        generated: Dict[str, str],
        force: bool,
    ) -> Optional[Path]:
        meta_path = episode_dir / "meta.json"
        manual = False
        if episode_dir.exists() and (episode_dir / "Episode.tsx").exists():
            if not meta_path.is_file():
                manual = True
            else:
                try:
                    meta = json.loads(meta_path.read_text(encoding="utf-8"))
                except Exception:
                    meta = {}
                previous = meta.get("generated_files") or {}
                for relative in generated:
                    path = episode_dir / relative
                    if not path.is_file():
                        manual = True
                        break
                    if previous.get(relative) != _hash_file(path):
                        manual = True
                        break

        if not manual:
            return None
        if not force:
            raise EditableVideoError(
                "Editable episode has manual changes. Re-run with force=True/--force "
                "to overwrite (a backup is created)."
            )

        timestamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        backup = episode_dir.with_name(f"{episode_dir.name}.bak-{timestamp}")
        suffix = 1
        while backup.exists():
            backup = episode_dir.with_name(
                f"{episode_dir.name}.bak-{timestamp}-{suffix}"
            )
            suffix += 1
        if episode_dir.exists():
            shutil.copytree(
                episode_dir,
                backup,
                ignore=shutil.ignore_patterns("public"),
            )
        return backup

    @staticmethod
    def _write(path: Path, content: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    # ------------------------------------------------------------------
    # Main entry point
    # ------------------------------------------------------------------
    def scaffold(
        self,
        config: Union[str, Path, Dict[str, Any]],
        channel_slug: Optional[str] = None,
        aspect_ratio: str = "16:9",
        episode_slug: Optional[str] = None,
        force: bool = False,
    ) -> Dict[str, Any]:
        data, source_path = self._load_config(config)
        target_slug_raw = (
            channel_slug
            or data.get("channelSlug")
            or data.get("channel_slug")
            or ""
        )
        if not target_slug_raw:
            raise EditableVideoError("channel_slug is required for editable episodes")
        target_slug, channel, channel_dir = self._resolve_channel(str(target_slug_raw))

        if aspect_ratio not in ASPECT_DIMENSIONS:
            raise EditableVideoError(
                f"Unsupported aspect_ratio '{aspect_ratio}'. "
                f"Use one of {', '.join(ASPECT_DIMENSIONS)}"
            )
        width, height = ASPECT_DIMENSIONS[aspect_ratio]
        aspect_slug = _aspect_slug(aspect_ratio)

        raw_episode = (
            episode_slug
            or data.get("id")
            or data.get("episodeSlug")
            or data.get("episode_slug")
            or "episode"
        )
        episode_name = _slug(str(raw_episode))
        folder_name = _slug(f"{episode_name}-{aspect_slug}")
        composition_id = f"Episode-{episode_name}-{aspect_slug}"

        fps = int(data.get("fps") or 30)
        enable_intro = bool(
            data.get("enableIntro", data.get("enable_intro", False))
        )
        intro_frames = (
            int(
                data.get("introDurationFrames")
                or data.get("intro_duration_frames")
                or 120
            )
            if enable_intro
            else 0
        )
        intro_props = data.get("introProps") or {}

        scenes = data.get("scenes") or []
        if not scenes:
            raise EditableVideoError("Editable episode needs at least one scene")

        cursor = 0.0
        for scene in scenes:
            start = float(scene.get("startInSeconds", cursor))
            duration = float(scene.get("durationInSeconds") or 3.0)
            cursor = max(cursor, start + duration)
        duration_frames = max(1, intro_frames + round(cursor * fps))

        theme = self._build_theme(data, channel)
        entries, targets, warnings = self._build_media_plan(
            data,
            channel_dir,
            episode_name,
            aspect_slug,
            intro_frames,
            fps,
        )

        episode_dir = (
            channel_dir / "video" / "episodes" / folder_name
        )
        captions_data, derived_act_timelines, captions_type = (
            self._normalize_captions(data.get("captions"))
        )
        act_timelines = data.get("actTimelines") or derived_act_timelines
        public_dir = episode_dir / "public"
        public_rel = public_dir.relative_to(self.project_root).as_posix()
        entry_rel = (episode_dir / "index.ts").relative_to(self.project_root).as_posix()
        media_rel = (episode_dir / "media.json").relative_to(self.project_root).as_posix()
        recipe_rel = (
            episode_dir / "video_recipe.editable.json"
        ).relative_to(self.project_root).as_posix()
        output_name = f"video_{aspect_slug}.mp4"
        output_rel = (
            channel_dir
            / "media"
            / "output"
            / episode_name
            / output_name
        ).relative_to(self.project_root).as_posix()

        episode_tsx = self._build_tsx(
            data,
            channel,
            theme,
            targets,
            intro_frames,
            fps,
            duration_frames,
            episode_name,
            warnings,
            act_timelines=act_timelines,
        )
        index_ts = self._build_index_ts(
            composition_id, duration_frames, width, height, fps
        )
        captions_ts = self._build_captions_ts(captions_data, captions_type)
        theme_ts = self._build_theme_ts(theme)

        generated = {
            "Episode.tsx": episode_tsx,
            "index.ts": index_ts,
            "data/captions.ts": captions_ts,
            "data/theme.ts": theme_ts,
            "media.json": json.dumps({"files": entries}, ensure_ascii=False, indent=2),
        }
        backup = self._check_guard(episode_dir, generated, force)
        staged = self.stager.ensure({"files": entries}, public_rel)
        pruned = self.stager.prune({"files": entries}, public_rel)

        for relative, content in generated.items():
            self._write(episode_dir / relative, content)

        config_hash = _hash_text(
            json.dumps(data, ensure_ascii=False, sort_keys=True)
        )
        meta = {
            "episode_slug": episode_name,
            "aspect_ratio": aspect_ratio,
            "composition_id": composition_id,
            "entry_point": entry_rel,
            "public_dir": public_rel,
            "media_manifest": media_rel,
            "editable_recipe": recipe_rel,
            "output": output_rel,
            "fps": fps,
            "duration_in_frames": duration_frames,
            "width": width,
            "height": height,
            "source_config": str(source_path) if source_path else None,
            "config_hash": config_hash,
            "generated_files": {
                relative: _hash_text(content)
                for relative, content in generated.items()
            },
            "generated_at": datetime.datetime.now(
                datetime.timezone.utc
            ).isoformat(),
            "warnings": warnings,
            "pruned_files": len(pruned.get("removed", [])),
        }
        self._write(
            episode_dir / "meta.json",
            json.dumps(meta, ensure_ascii=False, indent=2),
        )

        editable_recipe = {
            "$schema": "../../../../../.agents/schemas/video_recipe.schema.json",
            "channel_slug": target_slug,
            "episode_slug": episode_name,
            "composition": composition_id,
            "entry_point": entry_rel,
            "public_dir": public_rel,
            "media_manifest": media_rel,
            "output": output_name,
            "format": "mp4",
            "fps": fps,
            "editable": True,
            "normalize_media": False,
            "prune_media": True,
            "props": {},
        }
        self._write(
            episode_dir / "video_recipe.editable.json",
            json.dumps(editable_recipe, ensure_ascii=False, indent=2),
        )

        return {
            "status": "success",
            "engine": "editable_video",
            "channel_slug": target_slug,
            "episode_slug": episode_name,
            "aspect_ratio": aspect_ratio,
            "composition": composition_id,
            "episode_dir": str(episode_dir),
            "episode_tsx": str(episode_dir / "Episode.tsx"),
            "entry_point": entry_rel,
            "public_dir": public_rel,
            "media_manifest": media_rel,
            "editable_recipe": str(episode_dir / "video_recipe.editable.json"),
            "output": output_rel,
            "duration_in_frames": duration_frames,
            "scenes": len(scenes),
            "media_files": len(staged.get("files", [])),
            "pruned_files": len(pruned.get("removed", [])),
            "backup": str(backup) if backup else None,
            "warnings": warnings,
            "studio_command": (
                f"npx remotion studio {entry_rel} --public-dir {public_rel}"
            ),
            "render_command": (
                f"omnipress video --recipe {recipe_rel}"
            ),
        }
