#!/usr/bin/env python3
"""
OmniPress Dark Media Factory — Automated Audio & Video Generator for Dark Channels.
Generates neural TTS narrations (Edge-TTS) and stitches scenes into vertical 9:16 Shorts/Reels.

Usage:
    python scripts/generate_dark_media.py --text "Roteiro narrativo aqui..." --output ./media/output/short_01.mp4
    python scripts/generate_dark_media.py --from-json ./media/staging/youtube/2026/10/manifest.json
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
        print("⚠️ edge-tts não está instalado. Instalando automaticamente via pip...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "edge-tts"])
        import edge_tts

    communicate = edge_tts.Communicate(text, voice, rate="+2%", pitch="-2Hz")
    await communicate.save(str(output_path))
    print(f"🎙️ Áudio gerado com sucesso: {output_path}")
    return output_path


def render_video_with_ffmpeg(
    audio_path: Path,
    image_paths: list[Path],
    output_path: Path,
    aspect_ratio: str = "9:16"
) -> Path:
    """Combines images and narrated audio into a cinematic MP4 video."""
    if not shutil.which("ffmpeg"):
        print("⚠️ ffmpeg não foi encontrado no PATH.")
        print("   Para habilitar renderização automática de vídeo, instale com: sudo apt-get install -y ffmpeg")
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
        subprocess.check_call(cmd)
        print(f"🎬 Vídeo vertical gerado com sucesso: {output_path}")
        return output_path

    # If multiple images, create slideshow
    concat_list_file = output_path.parent / "images_concat.txt"
    # Approximate duration per slide
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
    subprocess.check_call(cmd)
    if concat_list_file.exists():
        concat_list_file.unlink()
    print(f"🎬 Vídeo multi-cenas gerado com sucesso: {output_path}")
    return output_path


def main():
    parser = argparse.ArgumentParser(description="OmniPress Dark Media Factory")
    parser.add_argument("--text", type=str, help="Texto do roteiro a ser narrado")
    parser.add_argument("--voice", type=str, default=DEFAULT_VOICE, help="Voz neural Edge-TTS")
    parser.add_argument("--output", type=str, default="./media/output/dark_video.mp4", help="Arquivo final de saída")
    parser.add_argument("--images", nargs="*", help="Caminhos das imagens das cenas")
    parser.add_argument("--ratio", type=str, default="9:16", choices=["9:16", "16:9"], help="Proporção do vídeo")
    args = parser.parse_args()

    out_file = Path(args.output).resolve()
    audio_file = out_file.with_suffix(".mp3")

    if not args.text:
        print("Erro: Forneça o texto com --text '...'")
        sys.exit(1)

    print("🚀 Iniciando produção de mídia Dark Channel com OmniPress...")
    asyncio.run(generate_tts_audio(args.text, audio_file, voice=args.voice))

    if args.images:
        img_paths = [Path(p).resolve() for p in args.images if Path(p).exists()]
        if img_paths:
            render_video_with_ffmpeg(audio_file, img_paths, out_file, aspect_ratio=args.ratio)
        else:
            print("⚠️ Nenhuma imagem válida encontrada. Áudio gravado com sucesso.")
    else:
        print(f"ℹ️ Imagens não fornecidas. Áudio final disponível em: {audio_file}")


if __name__ == "__main__":
    main()
