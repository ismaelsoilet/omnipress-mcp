"""FFmpeg provider: the only place that spawns the ffmpeg/ffprobe binaries."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.core.capabilities import resolve_ffmpeg_binary
from src.engine.providers.base import ProviderError, RenderProvider, register
from src.engine.providers import base as provider_base


@register
class FFmpegProvider(RenderProvider):
    name = "ffmpeg"
    capability = "ffmpeg"
    supports = frozenset({"audio", "video"})
    default_extension = "mp3"

    def validate(self, spec: Dict[str, Any]) -> List[str]:
        errors = super().validate(spec)
        op = str(spec.get("op") or "mix")
        if op in ("mix", "master"):
            errors.extend(self.check_required(spec, ["input", "output"]))
        bed_volume = spec.get("bed_volume")
        if bed_volume is not None:
            try:
                if float(bed_volume) > 0.20:
                    errors.append("bed_volume must be <= 0.20 to keep narration dominant.")
            except (TypeError, ValueError):
                errors.append("bed_volume must be a number.")
        return errors

    def resolve_binary(self, channel_slug: Optional[str] = None) -> str:
        binary = resolve_ffmpeg_binary(channel_slug=channel_slug)
        if not binary:
            raise ProviderError("FFmpeg binary not found. Set FFMPEG_PATH or install FFmpeg.")
        return binary

    def run_args(
        self,
        args: List[str],
        timeout: int = 900,
        channel_slug: Optional[str] = None,
    ) -> subprocess.CompletedProcess:
        """Runs ffmpeg with the shared isolation flags."""
        self._require(channel_slug)
        binary = self.resolve_binary(channel_slug)
        cmd = [binary, "-hide_banner", "-nostdin", "-y", *args]
        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=timeout, check=False
            )
        except subprocess.TimeoutExpired as exc:
            raise ProviderError(f"FFmpeg timed out after {timeout}s") from exc
        if result.returncode != 0:
            tail = (result.stderr or result.stdout or "")[-600:]
            raise ProviderError(f"FFmpeg failed (code {result.returncode}): {tail}")
        return result

    def probe(self, path: Path) -> Dict[str, Any]:
        binary = self.resolve_binary()
        ffprobe = str(Path(binary).with_name("ffprobe"))
        try:
            result = subprocess.run(
                [ffprobe, "-v", "error", "-show_format", "-show_streams", "-of", "json", str(path)],
                capture_output=True,
                text=True,
                timeout=60,
                check=False,
            )
        except Exception as exc:
            raise ProviderError(f"ffprobe failed: {exc}") from exc
        if result.returncode != 0:
            raise ProviderError(f"ffprobe failed: {(result.stderr or '')[:400]}")
        return json.loads(result.stdout or "{}")

    def mix_soundtrack(
        self,
        voice_path: Path,
        music_path: Path,
        output_path: Path,
        music_volume: float = 0.18,
        ducking: bool = True,
        target_lufs: float = -14.0,
        true_peak: float = -1.2,
        channel_slug: Optional[str] = None,
    ) -> Dict[str, Any]:
        if music_volume > 0.20:
            raise ProviderError("music_volume must be <= 0.20 (Rule 10 volume ceiling).")
        output_path.parent.mkdir(parents=True, exist_ok=True)

        loudnorm = f"loudnorm=I={target_lufs}:TP={true_peak}:LRA=7"
        if ducking:
            graph = (
                f"[0:a]asplit=2[voice][sc];"
                f"[1:a]volume={music_volume},highpass=f=80[music];"
                f"[music][sc]sidechaincompress=threshold=0.02:ratio=6:attack=5:release=300[ducked];"
                f"[voice][ducked]amix=inputs=2:duration=first:normalize=0,{loudnorm}[out]"
            )
        else:
            graph = (
                f"[0:a]volume=1.0[voice];"
                f"[1:a]volume={music_volume},highpass=f=80[music];"
                f"[voice][music]amix=inputs=2:duration=first:normalize=0,{loudnorm}[out]"
            )

        self.run_args(
            [
                "-i", str(voice_path),
                "-i", str(music_path),
                "-filter_complex", graph,
                "-map", "[out]",
                "-ar", "48000",
                "-c:a", "libmp3lame",
                "-b:a", "192k",
                str(output_path),
            ],
            channel_slug=channel_slug,
        )
        return {
            "status": "success",
            "output_path": str(output_path),
            "provider": self.name,
            "music_volume": music_volume,
            "ducking": ducking,
            "target_lufs": target_lufs,
            "file_size_bytes": output_path.stat().st_size if output_path.exists() else 0,
            "sha256": provider_base.file_sha256(output_path) if output_path.exists() else None,
        }

    def render(self, spec: Dict[str, Any], out_dir: Path) -> Dict[str, Any]:
        errors = self.validate(spec)
        if errors:
            raise ProviderError("; ".join(errors))
        self._require(spec.get("channel_slug"))

        op = str(spec.get("op") or "mix")
        if op == "mix":
            output = self.resolve_output(out_dir, spec.get("output"))
            return self.mix_soundtrack(
                voice_path=Path(spec["input"]).resolve(),
                music_path=Path(spec["mix_bed"] if spec.get("mix_bed") else spec["music"]).resolve(),
                output_path=output,
                music_volume=float(spec.get("bed_volume", 0.18)),
                ducking=bool(spec.get("ducking", True)),
                target_lufs=float(spec.get("target_lufs", -14.0)),
                true_peak=float(spec.get("true_peak", -1.2)),
                channel_slug=spec.get("channel_slug"),
            )

        if op == "concat":
            output = self.resolve_output(out_dir, spec.get("output"))
            inputs: List[str] = []
            for item in spec.get("inputs", []):
                inputs.extend(["-i", str(Path(item).resolve())])
            self.run_args([*inputs, "-c", "copy", str(output)], channel_slug=spec.get("channel_slug"))
            return {"status": "success", "output_path": str(output), "provider": self.name}

        raise ProviderError(f"Unsupported ffmpeg op '{op}'.")
