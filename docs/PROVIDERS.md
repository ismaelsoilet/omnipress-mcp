# Providers — External Runtime Contract

> Every subprocess and external service in OmniPress goes through a provider.
> No engine may call `subprocess` directly (enforced by `tests/test_architecture_invariants.py`).

---

## 1. Contract

`src/engine/providers/base.py`:

```python
class Provider:
    name: str
    capability: str
    supports: frozenset[str]

    def is_available(self) -> bool
    def info(self) -> dict
    def validate(self, spec: dict) -> list[str]

class RenderProvider(Provider):
    def render(self, spec: dict, out_dir: Path) -> dict
```

Mandatory rules:

1. **Stateless** — no mutable attributes outside `__init__`; binaries resolved on every call.
2. **Capability-gated** — `render()` calls `require_capability()` before doing work.
3. **Path-safe** — `resolve_output()` rejects separators and paths that escape `out_dir`.
4. **Fail-fast** — `validate()` runs before any subprocess/network call.
5. **Manifest-driven** — templates are only executed if registered and allowed by the channel.

---

## 2. Capability registry

`src/core/capabilities.py` defines every runtime:

| Capability | Required | Env var | Consumers |
|---|---|---|---|
| `python` | yes | — | all |
| `ffmpeg` | yes | `FFMPEG_PATH` | audio, video, documentary |
| `node` / `npm` | no | — | remotion |
| `remotion` | no | — | video, intro |
| `blender` | no | `BLENDER_PATH` | 3D, thumbnails, mockups |
| `edge_tts` | no | — | narration |
| `whisper` | no | — | captions (optional transcription) |
| `ai_image` | no | `GEMINI_API_KEY` / `OPENAI_API_KEY` / … | image recipes |
| `ai_music` | no (planned) | `GOOGLE_API_KEY` | music recipes |
| `network` | no | — | stock assets |

Probes run at call time. `omnipress doctor --json` exposes the registry.

---

## 3. Providers

### 3.1 `blender`

Spec fields: `script_path`, `format` (`png`/`webm`/`mp4`/`glb`), `supported_formats`, `resolution`, `engine`, `samples`, `params`, `output_name`.

Command shape:

```bash
blender -b --factory-startup --python-exit-code 1 -noaudio \
  -P template.py -- --output OUT --resolution 1920x1080 \
  --engine BLENDER_EEVEE_NEXT --samples 32 [--param value ...]
```

Only parameters declared in the template `manifest.json` are passed. Unknown parameters fail validation.

### 3.2 `remotion`

Spec fields: `composition`, `props`, `output`, `format`, `codec`, `fps`, `duration_frames`.
Runs `npx remotion render src/video/index.ts <composition> <output> --props=<json>` from the repo root.

### 3.3 `ffmpeg`

- `run_args(args)` — shared isolation flags, timeout and error tail.
- `mix_soundtrack(voice, music, output, music_volume=0.18, ducking=True)` — music ceiling `0.20`, sidechain ducking, loudnorm `-14 LUFS`.
- `probe(path)` — ffprobe JSON.

### 3.4 `edge_tts`

Spec: `text`, `voice`, `rate`, `pitch`, `volume`, `output`.
No default voice is hardcoded: `resolve_voice(explicit)` → `channel.video.voice` → `OMNIPRESS_DEFAULT_VOICE` → error.

### 3.5 `whisper`

Local CLI (`whisper`, `whisper-ctranslate2`) or `faster-whisper`. When neither is installed, captions still work with a pre-computed Whisper JSON provided by the caller.

### 3.6 `ai_image` + `prompt_export`

`ai_image` supports OpenAI Images and Gemini Imagen. On missing key or HTTP 429 it fails with a clear error; the image pipeline then falls back to `prompt_export`, which writes structured prompts for Midjourney, FLUX, Stable Diffusion, Ideogram and Leonardo with exact aspect ratio flags and target save paths.

### 3.7 `stock_asset`

Wikimedia Commons search/download with an explicit domain allowlist. Records `source_url`, `license`, `attribution` and a manifest. Arbitrary domains are rejected.

---

## 4. Adding a provider

1. Register the capability in `src/core/capabilities.py`.
2. Create `src/engine/providers/<name>_provider.py` implementing `RenderProvider` and decorate with `@register`.
3. Add a schema for its recipe (if it introduces a new document kind).
4. Add agnostic tests in `tests/test_providers.py`.
5. Document the runtime in this file and in `omnipress doctor`.

## 5. Adding a 3D template

Generic template:

```
src/engine/templates_3d/<name>/
  template.py       # Blender script; parses --output, --resolution, --engine, --samples + manifest params
  manifest.json     # name, description, outputs, params[]
```

Channel template:

```
channels/<slug>/blender_templates/<name>/
  template.py
  manifest.json
```

Then reference it from `3d_recipe.json`:

```json
{
  "channel_slug": "my-channel",
  "template": "my_custom_seal",
  "format": "png",
  "resolution": "1080x1080",
  "params": { "text": "BRAND", "material": "gold" }
}
```

Validate without Blender:

```bash
omnipress render-3d --recipe recipe.json --validate-only
```
