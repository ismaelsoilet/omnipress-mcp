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


sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.engine.dark_media import generate_tts_audio, render_video_with_ffmpeg, DEFAULT_VOICE


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
