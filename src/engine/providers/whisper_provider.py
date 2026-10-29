"""Whisper provider: optional local transcription/alignment.

When no local Whisper runtime is installed, callers must supply a Whisper JSON
externally (the caption engine keeps working).
"""

from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Dict, List

from src.engine.providers.base import ProviderError, RenderProvider, file_sha256, register


@register
class WhisperProvider(RenderProvider):
    name = "whisper"
    capability = "whisper"
    supports = frozenset({"stt"})
    default_extension = "json"

    def validate(self, spec: Dict[str, Any]) -> List[str]:
        errors = super().validate(spec)
        errors.extend(self.check_required(spec, ["audio"]))
        audio = Path(str(spec.get("audio", "")))
        if spec.get("audio") and not audio.is_file():
            errors.append(f"audio file not found: {audio}")
        return errors

    def transcribe(
        self,
        audio_path: Path,
        output_json: Path,
        model: str = "base",
        language: str = "",
    ) -> Dict[str, Any]:
        output_json.parent.mkdir(parents=True, exist_ok=True)

        cli = shutil.which("whisper") or shutil.which("whisper-ctranslate2")
        if cli:
            with tempfile.TemporaryDirectory() as tmp:
                cmd = [
                    cli,
                    str(audio_path),
                    "--model",
                    model,
                    "--output_format",
                    "json",
                    "--output_dir",
                    tmp,
                ]
                if language:
                    cmd.extend(["--language", language])
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=3600, check=False)
                if result.returncode != 0:
                    raise ProviderError(
                        f"Whisper CLI failed (code {result.returncode}): {(result.stderr or '')[-600:]}"
                    )
                produced = next(Path(tmp).glob("*.json"), None)
                if not produced:
                    raise ProviderError("Whisper CLI produced no JSON output.")
                output_json.write_text(produced.read_text(encoding="utf-8"), encoding="utf-8")
        else:
            try:
                from faster_whisper import WhisperModel  # type: ignore
            except ImportError as exc:
                raise ProviderError(
                    "No local Whisper runtime. Install `openai-whisper` / `faster-whisper` "
                    "or provide a pre-computed Whisper JSON file."
                ) from exc

            try:
                whisper_model = WhisperModel(model, device="auto", compute_type="int8")
                segments, info = whisper_model.transcribe(str(audio_path), language=language or None)
                words = []
                for segment in segments:
                    for word in getattr(segment, "words", []) or []:
                        words.append(
                            {
                                "word": word.word,
                                "start": float(word.start),
                                "end": float(word.end),
                            }
                        )
                payload = {
                    "language": getattr(info, "language", language),
                    "duration": getattr(info, "duration", None),
                    "words": words,
                }
                output_json.write_text(
                    json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
                )
            except Exception as exc:
                raise ProviderError(f"faster-whisper transcription failed: {exc}") from exc

        return {
            "status": "success",
            "provider": self.name,
            "output_path": str(output_json),
            "file_size_bytes": output_json.stat().st_size,
            "sha256": file_sha256(output_json),
        }

    def render(self, spec: Dict[str, Any], out_dir: Path) -> Dict[str, Any]:
        errors = self.validate(spec)
        if errors:
            raise ProviderError("; ".join(errors))
        self._require(spec.get("channel_slug"))
        output = self.resolve_output(out_dir, spec.get("output"), "whisper")
        return self.transcribe(
            audio_path=Path(spec["audio"]).resolve(),
            output_json=output,
            model=str(spec.get("model") or "base"),
            language=str(spec.get("language") or ""),
        )
