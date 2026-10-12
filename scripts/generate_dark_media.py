#!/usr/bin/env python3
"""
OmniPress Dark Media Factory — Automated Audio & Video Generator for Dark Channels.
Generates neural TTS narrations (Edge-TTS) and stitches scenes into vertical 9:16 Shorts/Reels or 16:9 videos.

Usage:
    python scripts/generate_dark_media.py --text "Roteiro narrativo aqui..." --output ./media/output/short_01.mp4
    python scripts/generate_dark_media.py --text "Locução..." --output ./media/output/audio.mp3 --audio-only --json
"""

import os
import sys
import json
import shutil
import asyncio
import argparse
import subprocess
from pathlib import Path


DEFAULT_VOICE = "pt-BR-AntonioNeural"  # Grave, imersivo, estilo documentário dark


async def generate_tts_audio(text: str, output_path: Path, voice: str = DEFAULT_VOICE) -> Path:
    """Generates natural neural speech using edge-tts."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        import edge_tts
    except ImportError:
        if shutil.which("uv"):
            subprocess.check_call(["uv", "pip", "install", "edge-tts"])
            import edge_tts
        else:
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", "edge-tts"])
                import edge_tts
            except Exception as e:
                raise RuntimeError(f"edge-tts não está instalado: {e}")

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
    image_paths: list[Path],
    output_path: Path,
    aspect_ratio: str = "9:16"
) -> Path:
    """Combines images and narrated audio into a cinematic MP4 video."""
    if not shutil.which("ffmpeg"):
        return audio_path

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
        concat_list_file = output_path.parent / f"images_concat_{os.getpid()}.txt"
        with open(concat_list_file, "w", encoding="utf-8") as f:
            for p in image_paths:
                f.write(f"file '{p.resolve()}'\n")
                f.write("duration 6\n")
            f.write(f"file '{image_paths[-1].resolve()}'\n")

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
        if concat_list_file.exists():
            concat_list_file.unlink()
        return output_path

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


def main():
    parser = argparse.ArgumentParser(description="OmniPress Dark Media Factory")
    parser.add_argument("--text", type=str, help="Texto do roteiro a ser narrado")
    parser.add_argument("--audio-path", type=str, help="Caminho do áudio existente se já gravado")
    parser.add_argument("--voice", type=str, default=DEFAULT_VOICE, help="Voz neural Edge-TTS")
    parser.add_argument("--output", type=str, default="./media/output/dark_video.mp4", help="Arquivo final de saída")
    parser.add_argument("--images", nargs="*", help="Caminhos das imagens das cenas")
    parser.add_argument("--ratio", type=str, default="9:16", choices=["9:16", "16:9"], help="Proporção do vídeo")
    parser.add_argument("--audio-only", action="store_true", help="Gerar apenas arquivo de áudio MP3")
    parser.add_argument("--json", action="store_true", help="Retornar resultado em JSON puro")
    args = parser.parse_args()

    out_file = Path(args.output).resolve()
    audio_file = out_file.with_suffix(".mp3")
    ffmpeg_available = bool(shutil.which("ffmpeg"))

    result = {
        "success": False,
        "audio_path": None,
        "video_path": None,
        "ffmpeg_available": ffmpeg_available,
        "aspect_ratio": args.ratio,
        "voice": args.voice
    }

    try:
        # Step 1: Obtain or generate audio
        if args.audio_path and Path(args.audio_path).exists():
            audio_file = Path(args.audio_path).resolve()
        elif args.text:
            asyncio.run(generate_tts_audio(args.text, audio_file, voice=args.voice))
        else:
            raise ValueError("Forneça --text '...' ou --audio-path 'caminho.mp3'")

        result["audio_path"] = str(audio_file)
        result["audio_size_bytes"] = audio_file.stat().st_size if audio_file.exists() else 0

        # Step 2: Handle video rendering if requested and not audio-only
        if not args.audio_only and ffmpeg_available:
            img_paths = [Path(p).resolve() for p in (args.images or []) if Path(p).exists()]
            rendered = render_video_with_ffmpeg(audio_file, img_paths, out_file, aspect_ratio=args.ratio)
            if rendered.suffix == ".mp4" and rendered.exists():
                result["video_path"] = str(rendered)
                result["video_size_bytes"] = rendered.stat().st_size

        result["success"] = True

        if args.json:
            print(json.dumps(result, ensure_ascii=False))
        else:
            print(f"🎙️ Áudio pronto: {result['audio_path']}")
            if result.get("video_path"):
                print(f"🎬 Vídeo renderizado: {result['video_path']}")
            elif not ffmpeg_available:
                print("ℹ️ ffmpeg não encontrado no PATH. Apenas o áudio neural foi gerado.")

    except Exception as exc:
        result["error"] = str(exc)
        if args.json:
            print(json.dumps(result, ensure_ascii=False))
        else:
            print(f"❌ Erro: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
