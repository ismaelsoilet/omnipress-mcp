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
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from src.core.capabilities import resolve_ffmpeg_binary
from src.engine.providers.ffmpeg_provider import FFmpegProvider

logger = logging.getLogger("omnipress.universal_audio")


def find_ffmpeg_binary() -> str:
    """Finds the active ffmpeg executable (env -> local bin -> PATH)."""
    return resolve_ffmpeg_binary() or "ffmpeg"


class UniversalAudioEngine:
    """Universal Broadcast Voice Mastering Engine complying with Rule 10."""

    def __init__(self, ffmpeg_bin: Optional[str] = None):
        self.ffmpeg_bin_override = ffmpeg_bin or ""
        self.provider = FFmpegProvider()

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

        # 4. 4-band surgical EQ (Rule 10)
        if enable_eq:
            # Body warmth at 140Hz (+2.5dB)
            filters.append("equalizer=f=140:width_type=q:w=1.2:g=2.5")
            # Cut nasal boxiness at 320Hz (-5.5dB)
            filters.append("equalizer=f=320:width_type=q:w=1.4:g=-5.5")
            # Boost speech clarity and presence at 2.8kHz (+3.5dB)
            filters.append("equalizer=f=2800:width_type=q:w=1.4:g=3.5")
            # Silky studio air at 8.5kHz (+4.0dB)
            filters.append("highshelf=f=8500:g=4.0")

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
            "-vn",
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
            self.provider.run_args(cmd)
            return {
                "success": True,
                "input_file": str(input_path),
                "output_file": str(output_path),
                "target_lufs": target_lufs,
                "sample_rate": sample_rate,
                "filtergraph": filtergraph,
            }
        except Exception as e:
            logger.error("FFmpeg mastering failed: %s", e)
            return {
                "success": False,
                "input_file": str(input_path),
                "output_file": str(output_path),
                "error": str(e),
                "filtergraph": filtergraph,
            }

    def mix_soundtrack(
        self,
        voice_path: Union[str, Path],
        music_path: Union[str, Path],
        output_path: Union[str, Path],
        music_volume: float = 0.18,
        ducking: bool = True,
        target_lufs: float = -14.0,
        channel_slug: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Mixes a soundtrack bed under narration with Rule 10 volume ceiling and ducking."""
        if music_volume > 0.20:
            return {
                "success": False,
                "error": "music_volume must be <= 0.20 (Rule 10 volume ceiling under speech).",
            }
        try:
            result = self.provider.mix_soundtrack(
                voice_path=Path(voice_path).resolve(),
                music_path=Path(music_path).resolve(),
                output_path=Path(output_path).resolve(),
                music_volume=music_volume,
                ducking=ducking,
                target_lufs=target_lufs,
                channel_slug=channel_slug,
            )
            return {"success": True, **result}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def surgical_debreather(
        self,
        raw_wav_path: Union[str, Path],
        captions_path: Union[str, Path, Dict[str, Any]],
        out_clean_wav_path: Union[str, Path],
        min_pause_sec: float = 0.12,
        fade_ms: float = 30.0,
    ) -> Dict[str, Any]:
        """Surgically purges breath sounds and ambient room noise during inter-phrase pauses using Whisper word timestamps."""
        try:
            import numpy as np
            import scipy.io.wavfile as wavfile
        except ImportError:
            raise RuntimeError("numpy and scipy are required for surgical_debreather. Install via 'uv add numpy scipy'.")

        raw_wav = Path(raw_wav_path).resolve()
        out_wav = Path(out_clean_wav_path).resolve()
        out_wav.parent.mkdir(parents=True, exist_ok=True)

        sr, data = wavfile.read(raw_wav)
        if np.issubdtype(data.dtype, np.floating):
            data_f = data.astype(np.float32)
        elif data.dtype == np.int32:
            data_f = data.astype(np.float32) / 2147483648.0
        else:
            data_f = data.astype(np.float32) / 32768.0

        if data_f.ndim == 1:
            data_f = data_f[:, np.newaxis]

        num_samples = len(data_f)

        if isinstance(captions_path, dict):
            captions_data = captions_path
        else:
            captions_data = json.loads(Path(captions_path).read_text(encoding="utf-8"))

        if "words" in captions_data:
            words = captions_data["words"]
        elif "short_01" in captions_data and "words" in captions_data["short_01"]:
            words = captions_data["short_01"]["words"]
        else:
            first_act = next(iter(captions_data.values()), {}) if captions_data else {}
            words = first_act.get("words", []) if isinstance(first_act, dict) else []

        if not words:
            wavfile.write(out_wav, sr, data)
            return {"success": True, "output_file": str(out_wav), "pauses_cleaned": 0}

        gain_mask = np.ones(num_samples, dtype=np.float32)
        fade_samples = int((fade_ms / 1000.0) * sr)

        # 1. Silence before first word
        first_word_start = words[0]["start"]
        first_speech_idx = int(max(0, (first_word_start - 0.08) * sr))
        if first_speech_idx > 0:
            gain_mask[:max(0, first_speech_idx - fade_samples)] = 0.0
            if first_speech_idx > fade_samples:
                gain_mask[first_speech_idx - fade_samples:first_speech_idx] = np.linspace(0.0, 1.0, fade_samples)

        # 2. Silence pauses between words where breaths occur
        pauses_cleaned = 0
        for i in range(len(words) - 1):
            w_curr = words[i]
            w_next = words[i + 1]
            pause_start_sec = w_curr["end"] + 0.04
            pause_end_sec = w_next["start"] - 0.04
            pause_dur = pause_end_sec - pause_start_sec
            if pause_dur >= min_pause_sec:
                pauses_cleaned += 1
                p_start = int(pause_start_sec * sr)
                p_end = int(pause_end_sec * sr)

                fo_end = min(num_samples, p_start + fade_samples)
                if fo_end > p_start:
                    gain_mask[p_start:fo_end] = np.linspace(1.0, 0.0, fo_end - p_start)

                mid_start = min(num_samples, p_start + fade_samples)
                mid_end = max(mid_start, min(num_samples, p_end - fade_samples))
                if mid_end > mid_start:
                    gain_mask[mid_start:mid_end] = 0.0

                fi_start = max(0, p_end - fade_samples)
                if p_end > fi_start:
                    gain_mask[fi_start:p_end] = np.linspace(0.0, 1.0, p_end - fi_start)

        # 3. Silence after last word
        last_word_end = words[-1]["end"]
        last_speech_idx = int(min(num_samples, (last_word_end + 0.06) * sr))
        if last_speech_idx < num_samples:
            fade_out_end = min(num_samples, last_speech_idx + fade_samples)
            gain_mask[last_speech_idx:fade_out_end] = np.linspace(1.0, 0.0, fade_out_end - last_speech_idx)
            gain_mask[fade_out_end:] = 0.0

        cleaned_f = data_f * gain_mask[:, np.newaxis]
        cleaned_int16 = (np.clip(cleaned_f, -1.0, 1.0) * 32767.0).astype(np.int16)
        wavfile.write(out_wav, sr, cleaned_int16)

        return {
            "success": True,
            "output_file": str(out_wav),
            "pauses_cleaned": pauses_cleaned,
            "sample_rate": sr,
        }
