"""Edge-TTS provider: neural narration without a hardcoded default voice."""

from __future__ import annotations

import asyncio
import concurrent.futures
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.engine.providers.base import ProviderError, RenderProvider, file_sha256, register


def _run_coroutine(coro: Any) -> Any:
    """Runs a coroutine from sync code, even inside a running event loop."""
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)

    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
        return pool.submit(asyncio.run, coro).result()


@register
class EdgeTTSProvider(RenderProvider):
    name = "edge_tts"
    capability = "edge_tts"
    supports = frozenset({"tts"})
    default_extension = "mp3"

    def validate(self, spec: Dict[str, Any]) -> List[str]:
        errors = super().validate(spec)
        errors.extend(self.check_required(spec, ["text", "voice"]))
        text = str(spec.get("text") or "")
        if text and len(text) > 20000:
            errors.append("text exceeds the 20,000 character safety limit")
        return errors

    def render(self, spec: Dict[str, Any], out_dir: Path) -> Dict[str, Any]:
        errors = self.validate(spec)
        if errors:
            raise ProviderError("; ".join(errors))
        self._require(spec.get("channel_slug"))

        output = self.resolve_output(out_dir, spec.get("output"), "voice")
        if output.suffix.lower() != ".mp3":
            output = output.with_suffix(".mp3")

        try:
            import edge_tts
        except ImportError as exc:
            raise ProviderError("edge-tts is not installed (`pip install edge-tts`).") from exc

        async def _speak() -> None:
            communicate = edge_tts.Communicate(
                text=str(spec["text"]),
                voice=str(spec["voice"]),
                rate=str(spec.get("rate") or "+0%"),
                volume=str(spec.get("volume") or "+0%"),
                pitch=str(spec.get("pitch") or "+0Hz"),
            )
            await communicate.save(str(output))

        try:
            _run_coroutine(_speak())
        except Exception as exc:
            raise ProviderError(f"Edge-TTS synthesis failed: {exc}") from exc

        if not output.exists() or output.stat().st_size == 0:
            raise ProviderError(f"Edge-TTS produced no audio at {output}")

        return {
            "status": "success",
            "provider": self.name,
            "output_path": str(output),
            "voice": spec["voice"],
            "file_size_bytes": output.stat().st_size,
            "sha256": file_sha256(output),
        }


def resolve_voice(
    channel_slug: Optional[str] = None,
    explicit: Optional[str] = None,
) -> str:
    """Resolves the narration voice: explicit -> channel.video.voice -> env -> error.

    No voice is hardcoded in the core (Rule 14).
    """
    if explicit and str(explicit).strip():
        return str(explicit).strip()

    if channel_slug:
        from src.core.channel_manager import ChannelManager

        channel = ChannelManager().get_channel(channel_slug) or {}
        channel_voice = (channel.get("video") or {}).get("voice")
        if channel_voice and str(channel_voice).strip():
            return str(channel_voice).strip()

    import os

    env_voice = os.getenv("OMNIPRESS_DEFAULT_VOICE", "").strip()
    if env_voice:
        return env_voice

    raise ProviderError(
        "No narration voice configured. Set `video.voice` in channel.json, "
        "pass an explicit voice, or define OMNIPRESS_DEFAULT_VOICE."
    )
