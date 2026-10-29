"""Universal media factory: neural narration and video stitching via providers.

This module contains no brand identity, voice or locale. The narration voice is
resolved per channel (`video.voice`), and every external process goes through the
provider layer (`edge_tts`, `ffmpeg`).
"""

from pathlib import Path
from typing import List, Optional

from src.engine.providers.edge_tts_provider import EdgeTTSProvider, resolve_voice
from src.engine.providers.ffmpeg_provider import FFmpegProvider


async def generate_tts_audio(
    text: str,
    output_path: Path,
    voice: Optional[str] = None,
    channel_slug: Optional[str] = None,
) -> Path:
    """Generates neural speech using the edge_tts provider.

    Voice resolution: explicit `voice` -> `channel.video.voice` -> OMNIPRESS_DEFAULT_VOICE.
    Raises a ProviderError when no voice is configured (never silently picks one).
    """
    output_path = Path(output_path)
    resolved_voice = resolve_voice(channel_slug, voice)

    provider = EdgeTTSProvider()
    provider.render(
        {
            "text": text,
            "voice": resolved_voice,
            "channel_slug": channel_slug,
            "output": output_path.name,
            "rate": "+2%",
            "pitch": "-2Hz",
        },
        output_path.parent,
    )
    return output_path


def render_video_with_ffmpeg(
    audio_path: Path,
    image_paths: List[Path],
    output_path: Path,
    aspect_ratio: str = "9:16",
    channel_slug: Optional[str] = None,
) -> Path:
    """Combines images and narrated audio into a cinematic MP4 through the ffmpeg provider."""
    output_path = Path(output_path)
    audio_path = Path(audio_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    provider = FFmpegProvider()
    provider._require(channel_slug)

    w, h = (1080, 1920) if aspect_ratio == "9:16" else (1920, 1080)
    base_args = ["-c:v", "libx264", "-c:a", "aac", "-b:a", "192k", "-pix_fmt", "yuv420p", "-shortest"]

    if len(image_paths) == 1:
        img = str(image_paths[0])
        provider.run_args(
            [
                "-loop", "1", "-i", img,
                "-i", str(audio_path),
                "-vf",
                f"scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},"
                f"zoompan=z='min(zoom+0.0015,1.2)':d=125:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={w}x{h}",
                "-tune", "stillimage",
                *base_args,
                str(output_path),
            ],
            channel_slug=channel_slug,
        )
        return output_path

    if len(image_paths) > 1:
        import uuid

        concat_list_file = output_path.parent / f"images_concat_{uuid.uuid4().hex}.txt"
        try:
            with open(concat_list_file, "w", encoding="utf-8") as f:
                for p in image_paths:
                    escaped_p = str(Path(p).resolve()).replace("'", "'\\''")
                    f.write(f"file '{escaped_p}'\n")
                    f.write("duration 6\n")
                escaped_last = str(Path(image_paths[-1]).resolve()).replace("'", "'\\''")
                f.write(f"file '{escaped_last}'\n")

            provider.run_args(
                [
                    "-f", "concat", "-safe", "0", "-i", str(concat_list_file),
                    "-i", str(audio_path),
                    "-vf", f"scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h}",
                    *base_args,
                    str(output_path),
                ],
                channel_slug=channel_slug,
            )
            return output_path
        finally:
            if concat_list_file.exists():
                concat_list_file.unlink()

    provider.run_args(
        [
            "-f", "lavfi", "-i", f"color=c=0x0a0c10:s={w}x{h}",
            "-i", str(audio_path),
            "-tune", "stillimage",
            *base_args,
            str(output_path),
        ],
        channel_slug=channel_slug,
    )
    return output_path
