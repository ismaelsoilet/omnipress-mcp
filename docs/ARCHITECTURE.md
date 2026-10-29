# OmniPress Architecture — `src/` is a Factory, `channels/` are Recipes

> Normative contract for Rules 12 and 14. If code violates this document, the build is wrong.

---

## 1. The two layers

| Layer | What it is | What may live there | What must never live there |
|---|---|---|---|
| **Factory** (`src/`) | Universal, channel-agnostic engines, providers and adapters | Recipes parsing, rendering, mastering, publishing, provider contracts, schemas | Channel slugs, brand names, palettes, voices, handles, editorial content, channel asset paths |
| **Channel** (`channels/<slug>/`) | Declarative data and assets for one brand | `channel.json`, recipes, media, fonts, channel 3D templates, niche packs | Standard production scripts that duplicate an engine |

**Golden rule:** if a channel script renders, uploads, schedules, masters audio, aligns captions, generates thumbnails or builds documentary cards, it is forbidden. That is an engine responsibility.

---

## 2. Extension points

### 2.1 Provider (external runtime)

Every subprocess and external service is behind a provider in `src/engine/providers/`:

| Provider | Capability | Used by |
|---|---|---|
| `blender` | `blender` | `universal_3d`, thumbnails, mockups |
| `remotion` | `remotion` | `universal_video` |
| `ffmpeg` | `ffmpeg` | `universal_audio`, `dark_media`, documentary mux |
| `edge_tts` | `edge_tts` | `dark_media`, narration |
| `whisper` | `whisper` | `universal_captions` (optional transcription) |
| `ai_image` | `ai_image` | image recipes |
| `prompt_export` | always available | fallback when AI image generation is unavailable |
| `stock_asset` | `network` | `universal_assets` |

Provider contract (`src/engine/providers/base.py`): `is_available()`, `info()`, `validate(spec)`, `render(spec, out_dir)`.
Rules: stateless, capability-gated, path-safe, fail-fast before subprocess/network.

### 2.2 Template (production knowledge)

- Generic templates live in `src/engine/templates_3d/<name>/{template.py, manifest.json}`.
- Channel templates live in `channels/<slug>/blender_templates/<name>/{template.py, manifest.json}`.
- A template is only executable if it is registered and (when configured) present in `channel.render.blender.template_allowlist`.
- Recipes are validated against the template manifest before any subprocess.

### 2.3 Recipe (instance)

Every deliverable is a JSON document validated by `.agents/schemas/*.schema.json`:

| Deliverable | Recipe | Engine |
|---|---|---|
| Carousel | `carousel_recipe.json` | `universal_carousel` + `carousel_builder` |
| Social post / article | `post_recipe.json`, `{platform}_recipe.json` | `universal_publisher` |
| Thumbnail | `thumbnail_recipe.json` | `universal_thumbnail` + `rule15_validator` |
| Documentary scenes | `documentary_recipe.json` | `universal_documentary` |
| Video | `video_recipe.json` | `universal_video` |
| Audio mastering / mix | `audio_recipe.json` | `universal_audio` |
| Voice | `voice_recipe.json` | `edge_tts` provider |
| 3D asset | `3d_recipe.json` | `universal_3d` + `blender` provider |
| Image | `image_recipe.json` | `ai_image` → `prompt_export` fallback |
| Public archive asset | `asset_recipe.json` | `universal_assets` |

---

## 3. Parameter cascade (mandatory)

```
1. slide_data (item override)
2. recipe.layout_parameters / recipe.<param>
3. channel.visual_identity.presets[preset]
4. channel.visual_identity.layout_parameters
5. channel.branding (legacy compatibility)
6. engine defaults (neutral, never a brand)
```

- `card_bg_alpha` is canonical; `card_alpha` is a normalized alias.
- Palette and typography follow the same order through `_resolve_palette` / `_resolve_fonts`.
- `settings.default_aspect_ratio` is read when a recipe omits `aspect_ratio`.

---

## 4. Capabilities and environment

`src/core/capabilities.py` is the single source of truth for external runtimes. Probes run at call time, never in constructors.

```bash
omnipress doctor          # human report
omnipress doctor --json   # machine report for CI/agents
```

Each capability reports: availability, version, resolved binary, env var, consumers and install hint. Missing optional capabilities degrade gracefully; required ones fail with an actionable message.

---

## 5. Statelessness and credentials

- Engines and adapters hold no request state (`self.x = ...` only in `__init__`; enforced by test).
- Channel credentials are resolved exclusively through `ChannelManager.get_credential(key, channel_slug)`:
  `channels/<slug>/.env` → `<SLUG>_<KEY>` → global `.env`.
- Channel config/env caches are keyed by `(st_mtime_ns, st_size)`.

---

## 6. Enforcement

| Invariant | Test |
|---|---|
| No channel slugs, branches or `channels/` literals in `src/` | `tests/test_architecture_invariants.py` |
| No credential env reads in adapters | idem |
| No mutable instance state outside `__init__` | idem |
| No subprocess outside `src/engine/providers/` | idem |
| Every declarative document matches its schema | `tests/test_recipe_schemas.py` |
| No `render_*` / `upload_*` / `schedule_*` under `channels/` | `tests/test_channel_layout_contract.py` |
| Version synced across 10 canonical files + changelog | `tests/test_release_invariants.py` |
| Provider path safety and capability gating | `tests/test_providers.py` |
| Rule 15 numbers enforced in production code | `tests/test_rule15_thumbnails.py` |

---

## 7. Current migration status

- `channels/dossie-historico`: **27 carousel recipes** generated from the former bespoke scripts; the 67 render/upload/schedule/publish scripts and `auto_queue_runner.py` were removed.
- **3 documentary manifests** (`ep03`, `ep03b`, `ep04`) generated in `manifest` mode from existing `episode_config.json`; the ep03/ep04 scene-generation scripts were removed.
- Remaining legacy scripts (audio assembly, caption alignment, shorts, thumbnails) are inventoried in `docs/MIGRATION_DOSSIE.md` and `docs/MIGRATION_DOCUMENTARY.md`. They must be migrated to the engines above before deletion.
