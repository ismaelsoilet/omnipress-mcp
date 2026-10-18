"""
OmniPress Dark Media Factory — Automated Audio & Video Generator for Dark Channels.
Generates neural TTS narrations (Edge-TTS) and stitches scenes into vertical 9:16 Shorts/Reels or 16:9 videos.
"""

import os
import shutil
import asyncio
import subprocess
from pathlib import Path
from typing import List, Optional

DEFAULT_VOICE = "pt-BR-AntonioNeural"  # Grave, imersivo, estilo documentário dark


async def generate_tts_audio(text: str, output_path: Path, voice: str = DEFAULT_VOICE) -> Path:
    """Generates natural neural speech using edge-tts."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        import edge_tts
    except ImportError:
        raise RuntimeError(
            "edge-tts não está instalado no ambiente. Instale com: uv add edge-tts ou pip install edge-tts"
        )

    try:
        communicate = edge_tts.Communicate(text, voice, rate="+2%", pitch="-2Hz")
        await communicate.save(str(output_path))
    except Exception as tts_err:
        if shutil.which("ffmpeg"):
            words = len(text.split())
            dur = max(3.0, round(words / 2.5, 1))
            cmd = [
                "ffmpeg", "-y", "-f", "lavfi",
                "-i", f"sine=frequency=180:duration={dur}",
                "-c:a", "libmp3lame", "-b:a", "128k",
                str(output_path)
            ]
            res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if res.returncode == 0 and output_path.exists():
                return output_path
        raise RuntimeError(f"Erro na síntese neural edge-tts e fallback indisponível: {tts_err}")
    return output_path


def render_video_with_ffmpeg(
    audio_path: Path,
    image_paths: List[Path],
    output_path: Path,
    aspect_ratio: str = "9:16"
) -> Path:
    """Combines images and narrated audio into a cinematic MP4 video."""
    if not shutil.which("ffmpeg"):
        return audio_path

    output_path = Path(output_path)
    audio_path = Path(audio_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Resolution settings
    res = "1080x1920" if aspect_ratio == "9:16" else "1920x1080"
    w, h = (1080, 1920) if aspect_ratio == "9:16" else (1920, 1080)

    # If only 1 image provided, create looping video with subtle zoom
    if len(image_paths) == 1:
        img = str(image_paths[0])
        cmd = [
            "ffmpeg", "-y",
            "-loop", "1", "-i", img,
            "-i", str(audio_path),
            "-vf", f"scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},zoompan=z='min(zoom+0.0015,1.2)':d=125:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={w}x{h}",
            "-c:v", "libx264", "-tune", "stillimage", "-c:a", "aac", "-b:a", "192k",
            "-pix_fmt", "yuv420p",
            "-shortest",
            str(output_path)
        ]
        subprocess.check_call(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return output_path

    # If multiple images, create slideshow
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

            cmd = [
                "ffmpeg", "-y",
                "-f", "concat", "-safe", "0", "-i", str(concat_list_file),
                "-i", str(audio_path),
                "-vf", f"scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h}",
                "-c:v", "libx264", "-c:a", "aac", "-b:a", "192k",
                "-pix_fmt", "yuv420p",
                "-shortest",
                str(output_path)
            ]
            subprocess.check_call(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return output_path
        finally:
            if concat_list_file.exists():
                concat_list_file.unlink()

    # Fallback if no images provided: create dark atmospheric background with audio
    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", f"color=c=0x0a0c10:s={w}x{h}",
        "-i", str(audio_path),
        "-c:v", "libx264", "-tune", "stillimage", "-c:a", "aac", "-b:a", "192k",
        "-pix_fmt", "yuv420p",
        "-shortest",
        str(output_path)
    ]
    subprocess.check_call(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return output_path
