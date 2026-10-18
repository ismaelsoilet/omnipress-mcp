"""Universal Broadcast Audio Mastering Engine for OmniPress MCP.

Implements the 6-stage studio voice treatment and loudness mastering gate (Rule 10):
1. Mouth-click and plosive suppression (adeclick).
2. Subsonic highpass filter at 80Hz (cuts mic rumble & desk vibrations).
3. Spectral denoise (afftdn) eliminating room floor noise and preamp hiss.
4. 4-band surgical EQ (320Hz notch for boxiness, 2.8kHz presence, 6.5kHz air).
5. Dynamic broadcast compression (ratio 2.5:1, attack 10ms, release 100ms).
6. EBU R128 loudness normalization locking integrated loudness to -14.0 LUFS (TP <= -1.2 dBTP).
"""

import json
import logging
import os
import shutil
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

logger = logging.getLogger("omnipress.universal_audio")


def find_ffmpeg_binary() -> str:
    """Finds the active ffmpeg executable in PATH or standard system/user locations."""
    # 1. Environment override
    env_ffmpeg = os.getenv("FFMPEG_PATH")
    if env_ffmpeg and Path(env_ffmpeg).is_file() and os.access(env_ffmpeg, os.X_OK):
        return env_ffmpeg

    # 2. In PATH
    which_ffmpeg = shutil.which("ffmpeg")
    if which_ffmpeg:
        return which_ffmpeg

    # 3. Known fallback locations
    candidates = [
        Path.home() / ".local" / "bin" / "ffmpeg",
        Path("/usr/local/bin/ffmpeg"),
        Path("/usr/bin/ffmpeg"),
    ]
    for c in candidates:
        if c.is_file() and os.access(c, os.X_OK):
            return str(c)

    # Return default 'ffmpeg' and let subprocess fail with informative message
    return "ffmpeg"


class UniversalAudioEngine:
    """Universal Broadcast Voice Mastering Engine complying with Rule 10."""

    def __init__(self, ffmpeg_bin: Optional[str] = None):
        self.ffmpeg_bin = ffmpeg_bin or find_ffmpeg_binary()

    def build_mastering_filtergraph(
        self,
        target_lufs: float = -14.0,
        enable_declick: bool = True,
        enable_denoise: bool = True,
        enable_eq: bool = True,
        enable_compression: bool = True,
        enable_loudnorm: bool = True,
        true_peak: float = -1.2,
    ) -> str:
        """Constructs the broadcast audio filtergraph string according to Rule 10 standards."""
        filters: List[str] = []

        # 1. Declick & mouth plosives
        if enable_declick:
            filters.append("adeclick=window=55:overlap=75:threshold=2")

        # 2. Subsonic highpass filter
        filters.append("highpass=f=80")

        # 3. Spectral denoise
        if enable_denoise:
            filters.append("afftdn=nf=-25")

        # 4. 4-band surgical EQ
        if enable_eq:
            # Cut boxiness at 320Hz (-5.5dB)
            filters.append("equalizer=f=320:width_type=q:w=1.4:g=-5.5")
            # Boost speech clarity and presence at 2.8kHz (+3.5dB)
            filters.append("equalizer=f=2800:width_type=q:w=1.4:g=3.5")
            # Silky studio air at 6.5kHz (+4.0dB)
            filters.append("highshelf=f=6500:g=4.0")

        # 5. Broadcast studio compression
        if enable_compression:
            filters.append("acompressor=threshold=-20dB:ratio=2.5:attack=10:release=100:makeup=1.5")

        # 6. EBU R128 Loudness normalization strictly locked to target LUFS
        if enable_loudnorm:
            filters.append(f"loudnorm=I={target_lufs}:LRA=7:TP={true_peak}")

        return ",".join(filters)

    def master_voiceover(
        self,
        input_audio: Union[str, Path],
        output_audio: Union[str, Path],
        target_lufs: float = -14.0,
        sample_rate: int = 48000,
        bitrate: str = "192k",
        enable_declick: bool = True,
        enable_denoise: bool = True,
        enable_eq: bool = True,
        enable_compression: bool = True,
        enable_loudnorm: bool = True,
    ) -> Dict[str, Any]:
        """Runs the studio broadcast mastering pipeline on the input voiceover file."""
        input_path = Path(input_audio).resolve()
        output_path = Path(output_audio).resolve()

        if not input_path.exists():
            raise FileNotFoundError(f"Source voiceover file not found: {input_path}")

        output_path.parent.mkdir(parents=True, exist_ok=True)

        filtergraph = self.build_mastering_filtergraph(
            target_lufs=target_lufs,
            enable_declick=enable_declick,
            enable_denoise=enable_denoise,
            enable_eq=enable_eq,
            enable_compression=enable_compression,
            enable_loudnorm=enable_loudnorm,
        )

        cmd = [
            self.ffmpeg_bin,
            "-y",
            "-i", str(input_path),
            "-af", filtergraph,
            "-ar", str(sample_rate),
        ]

        if output_path.suffix.lower() == ".mp3":
            cmd.extend(["-c:a", "libmp3lame", "-b:a", bitrate])
        elif output_path.suffix.lower() == ".wav":
            cmd.extend(["-c:a", "pcm_s16le"])
        elif output_path.suffix.lower() in [".m4a", ".aac"]:
            cmd.extend(["-c:a", "aac", "-b:a", bitrate])

        cmd.append(str(output_path))

        try:
            res = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            return {
                "success": True,
                "input_file": str(input_path),
                "output_file": str(output_path),
                "target_lufs": target_lufs,
                "sample_rate": sample_rate,
                "filtergraph": filtergraph,
            }
        except subprocess.CalledProcessError as e:
            logger.error("FFmpeg mastering failed: %s", e.stderr)
            return {
                "success": False,
                "input_file": str(input_path),
                "output_file": str(output_path),
                "error": e.stderr or str(e),
                "filtergraph": filtergraph,
            }
        except FileNotFoundError:
            return {
                "success": False,
                "error": f"FFmpeg binary not found at '{self.ffmpeg_bin}'. Please install ffmpeg or set FFMPEG_PATH.",
            }
