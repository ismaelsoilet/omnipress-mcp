"""AI image provider (optional): OpenAI Images and Gemini Imagen.

When no provider is configured or a quota error (HTTP 429) occurs, callers must
fall back to `prompt_export_provider` so production never stalls (Rule 10).
"""

from __future__ import annotations

import base64
import os
from pathlib import Path
from typing import Any, Dict, List

from src.engine.providers.base import ProviderError, RenderProvider, file_sha256, register

_ASPECT_TO_SIZE = {
    "1:1": "1024x1024",
    "16:9": "1536x1024",
    "9:16": "1024x1536",
    "4:5": "1024x1280",
    "3:4": "1024x1365",
}


@register
class AIImageProvider(RenderProvider):
    name = "ai_image"
    capability = "ai_image"
    supports = frozenset({"image"})
    default_extension = "png"

    def validate(self, spec: Dict[str, Any]) -> List[str]:
        errors = super().validate(spec)
        errors.extend(self.check_required(spec, ["prompt"]))
        if len(str(spec.get("prompt", ""))) > 8000:
            errors.append("prompt exceeds 8,000 characters")
        return errors

    def _openai(self, prompt: str, size: str, model: str) -> bytes:
        import requests

        api_key = os.getenv("OPENAI_API_KEY", "").strip()
        if not api_key:
            raise ProviderError("OPENAI_API_KEY is not configured.")
        response = requests.post(
            "https://api.openai.com/v1/images/generations",
            headers={"Authorization": f"Bearer {api_key}"},
            json={"model": model, "prompt": prompt, "size": size, "n": 1},
            timeout=180,
        )
        if response.status_code == 429:
            raise ProviderError("OpenAI image quota exhausted (HTTP 429). Fall back to prompt export.")
        if response.status_code >= 400:
            raise ProviderError(f"OpenAI image error {response.status_code}: {response.text[:400]}")
        payload = response.json()
        item = (payload.get("data") or [{}])[0]
        if item.get("b64_json"):
            return base64.b64decode(item["b64_json"])
        if item.get("url"):
            download = requests.get(item["url"], timeout=180)
            download.raise_for_status()
            return download.content
        raise ProviderError("OpenAI image response contained no image data.")

    def _gemini(self, prompt: str, aspect_ratio: str, model: str) -> bytes:
        import requests

        api_key = os.getenv("GEMINI_API_KEY", "").strip() or os.getenv("GOOGLE_API_KEY", "").strip()
        if not api_key:
            raise ProviderError("GEMINI_API_KEY/GOOGLE_API_KEY is not configured.")
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:predict"
        response = requests.post(
            url,
            params={"key": api_key},
            json={
                "instances": [{"prompt": prompt}],
                "parameters": {"sampleCount": 1, "aspectRatio": aspect_ratio},
            },
            timeout=180,
        )
        if response.status_code == 429:
            raise ProviderError("Gemini image quota exhausted (HTTP 429). Fall back to prompt export.")
        if response.status_code >= 400:
            raise ProviderError(f"Gemini image error {response.status_code}: {response.text[:400]}")
        predictions = response.json().get("predictions") or []
        encoded = (predictions[0] if predictions else {}).get("bytesBase64Encoded")
        if not encoded:
            raise ProviderError("Gemini image response contained no image data.")
        return base64.b64decode(encoded)

    def render(self, spec: Dict[str, Any], out_dir: Path) -> Dict[str, Any]:
        errors = self.validate(spec)
        if errors:
            raise ProviderError("; ".join(errors))
        self._require(spec.get("channel_slug"))

        output = self.resolve_output(out_dir, spec.get("output"), "generated")
        if output.suffix.lower() not in (".png", ".jpg", ".jpeg", ".webp"):
            output = output.with_suffix(".png")

        aspect = str(spec.get("aspect_ratio") or "16:9")
        prompt = str(spec["prompt"])
        if spec.get("negative_prompt"):
            prompt = f"{prompt}\n\nAvoid: {spec['negative_prompt']}"

        preferred = os.getenv("OMNIPRESS_IMAGE_PROVIDER", "").strip().lower()
        has_openai = bool(os.getenv("OPENAI_API_KEY", "").strip())
        has_gemini = bool(
            os.getenv("GEMINI_API_KEY", "").strip() or os.getenv("GOOGLE_API_KEY", "").strip()
        )

        if preferred == "gemini" and has_gemini:
            data = self._gemini(prompt, aspect, str(spec.get("model") or "imagen-3.0-generate-002"))
            used = "gemini"
        elif preferred == "openai" and has_openai:
            data = self._openai(prompt, _ASPECT_TO_SIZE.get(aspect, "1024x1024"), str(spec.get("model") or "gpt-image-1"))
            used = "openai"
        elif has_openai:
            data = self._openai(prompt, _ASPECT_TO_SIZE.get(aspect, "1024x1024"), str(spec.get("model") or "gpt-image-1"))
            used = "openai"
        elif has_gemini:
            data = self._gemini(prompt, aspect, str(spec.get("model") or "imagen-3.0-generate-002"))
            used = "gemini"
        else:
            raise ProviderError("No AI image provider configured. Use prompt_export fallback.")

        output.write_bytes(data)
        return {
            "status": "success",
            "provider": self.name,
            "provider_backend": used,
            "output_path": str(output),
            "file_size_bytes": output.stat().st_size,
            "sha256": file_sha256(output),
        }
