#!/usr/bin/env python3
"""OmniPress Universal Audio Mastering Runner.

Masters raw voiceover tracks into broadcast-grade audio complying with Rule 10:
- Adeclick (plosive and click removal)
- Highpass 80Hz (subsonic rumble suppression)
- Afftdn (spectral denoise)
- 4-band surgical EQ (320Hz boxiness notch, 2.8kHz presence, 6.5kHz studio air)
- Broadcast compression (ratio 2.5:1)
- EBU R128 loudness normalization strictly locked to -14.0 LUFS (TP <= -1.2 dBTP)

Usage:
    python scripts/omnipress_audio_master.py raw_voice.m4a -o mastered_voice.mp3
    python scripts/omnipress_audio_master.py raw_voice.wav -o mastered_voice.mp3 --target-lufs -14.0
"""

import argparse
import os
import sys
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Optional dotenv
try:
    from dotenv import load_dotenv
    load_dotenv(PROJECT_ROOT / ".env")
except ImportError:
    pass

from src.engine.universal_audio import UniversalAudioEngine, find_ffmpeg_binary


def main(argv: list = None) -> int:
    parser = argparse.ArgumentParser(
        prog="omnipress-audio-master",
        description="OmniPress Universal Audio Mastering Engine - Studio Voice Broadcast Treatment (Rule 10).",
    )
    parser.add_argument("input", help="Path to input voiceover file (.m4a, .wav, .mp3)")
    parser.add_argument("-o", "--output", required=True, help="Path to output mastered audio file (.mp3, .wav)")
    parser.add_argument("--target-lufs", type=float, default=-14.0, help="Target integrated loudness LUFS (default: -14.0)")
    parser.add_argument("--sample-rate", type=int, default=48000, help="Output sample rate in Hz (default: 48000)")
    parser.add_argument("--bitrate", default="192k", help="Output MP3 bitrate (default: 192k)")
    parser.add_argument("--no-declick", action="store_true", help="Disable adeclick stage")
    parser.add_argument("--no-denoise", action="store_true", help="Disable afftdn spectral denoise stage")
    parser.add_argument("--no-eq", action="store_true", help="Disable 4-band EQ stage")
    parser.add_argument("--no-compressor", action="store_true", help="Disable broadcast compression stage")
    parser.add_argument("--no-loudnorm", action="store_true", help="Disable EBU R128 loudness normalization")

    args = parser.parse_args(argv)

    input_path = Path(args.input).resolve()
    if not input_path.exists():
        print(f"❌ Error: Input voiceover file not found: {input_path}")
        return 1

    output_path = Path(args.output).resolve()
    ffmpeg_bin = find_ffmpeg_binary()

    print("============================================================")
    print("      OmniPress Universal Audio Mastering Engine (Rule 10)  ")
    print("============================================================")
    print(f"  Input        : {input_path.name}")
    print(f"  Output       : {output_path.name}")
    print(f"  Target LUFS  : {args.target_lufs} LUFS (EBU R128)")
    print(f"  Sample Rate  : {args.sample_rate} Hz (Broadcast)")
    print(f"  FFmpeg Bin   : {ffmpeg_bin}")
    print("------------------------------------------------------------")

    engine = UniversalAudioEngine(ffmpeg_bin=ffmpeg_bin)
    res = engine.master_voiceover(
        input_audio=input_path,
        output_audio=output_path,
        target_lufs=args.target_lufs,
        sample_rate=args.sample_rate,
        bitrate=args.bitrate,
        enable_declick=not args.no_declick,
        enable_denoise=not args.no_denoise,
        enable_eq=not args.no_eq,
        enable_compression=not args.no_compressor,
        enable_loudnorm=not args.no_loudnorm,
    )

    if res.get("success"):
        print(f"✅ Studio Voice Treatment successful!")
        print(f"   Output saved to: {output_path}")
        print(f"   Filtergraph: {res.get('filtergraph')}")
        return 0
    else:
        print(f"❌ Audio mastering failed: {res.get('error')}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
