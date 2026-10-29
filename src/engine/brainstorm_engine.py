"""Universal brainstorm and script-pack engine.

Editorial content (channel names, hooks, pillars, scene prompts) belongs to the
channel, never to `src/`. This engine loads a declarative pack from
`channels/<slug>/niches/` and renders it with the requested topic/tone. When no
pack exists it produces a structural, language-neutral skeleton.

Packs:
- `channels/<slug>/niches/<niche>.json`   -> brainstorm concepts/pillars/topics
- `channels/<slug>/niches/script_pack.json` -> script/scene/metadata templates
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.core.channel_manager import ChannelManager, slugify_channel


def _slug(value: str) -> str:
    return slugify_channel(value) or "default"


def _render(value: Any, context: Dict[str, str]) -> Any:
    """Recursively renders `{placeholder}` templates in strings, lists and dicts."""
    if isinstance(value, str):
        rendered = value
        for key, replacement in context.items():
            rendered = rendered.replace(f"{{{key}}}", replacement)
        return rendered
    if isinstance(value, list):
        return [_render(item, context) for item in value]
    if isinstance(value, dict):
        return {key: _render(item, context) for key, item in value.items()}
    return value


class BrainstormEngine:
    """Loaded from channel packs; deterministic generic fallback otherwise."""

    def __init__(self, channel_manager: Optional[ChannelManager] = None):
        self.channel_manager = channel_manager or ChannelManager()

    # ------------------------------------------------------------------
    # Pack loading
    # ------------------------------------------------------------------
    def niches_dir(self, channel_slug: Optional[str] = None) -> Path:
        slug = channel_slug or self.channel_manager.get_active_channel_slug()
        return self.channel_manager.get_channel_dir(slug) / "niches"

    def load_pack(self, niche: str, channel_slug: Optional[str] = None) -> Optional[Dict[str, Any]]:
        directory = self.niches_dir(channel_slug)
        candidates: List[Path] = []
        if niche:
            candidates.append(directory / f"{_slug(niche)}.json")
        candidates.append(directory / "_default.json")

        for candidate in candidates:
            if candidate.is_file():
                try:
                    return json.loads(candidate.read_text(encoding="utf-8"))
                except json.JSONDecodeError:
                    return None
        return None

    def load_script_pack(self, channel_slug: Optional[str] = None) -> Optional[Dict[str, Any]]:
        candidate = self.niches_dir(channel_slug) / "script_pack.json"
        if not candidate.is_file():
            return None
        try:
            return json.loads(candidate.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return None

    # ------------------------------------------------------------------
    # Brainstorm
    # ------------------------------------------------------------------
    def run(
        self,
        niche: str = "",
        tone: str = "",
        target_audience: str = "",
        language: str = "",
        channel_slug: Optional[str] = None,
    ) -> Dict[str, Any]:
        context = {
            "niche": niche,
            "tone": tone,
            "target_audience": target_audience,
            "language": language,
            "niche_title": niche.title() if niche else "",
        }

        pack = self.load_pack(niche, channel_slug) if niche else self.load_pack("", channel_slug)
        if pack:
            bundle = _render(pack, context)
            bundle["source"] = "channel_pack"
        else:
            bundle = self._generic_bundle(context)
            bundle["source"] = "generic_fallback"

        bundle.setdefault("niche", niche)
        bundle.setdefault("tone", tone)
        bundle.setdefault("targetAudience", target_audience)
        bundle.setdefault("language", language)
        return bundle

    @staticmethod
    def _generic_bundle(context: Dict[str, str]) -> Dict[str, Any]:
        niche = context["niche"] or "your niche"
        title = context["niche_title"] or "Untitled Channel"
        slugs = _slug(niche)

        concepts = [
            {
                "name": f"{title} Explained",
                "handle": f"@{slugs}.explained",
                "tagline": f"What most people miss about {niche}.",
                "ctrAngle": "Curiosity gap built on a documented anomaly.",
                "visualPalette": ["#0F172A", "#3B82F6", "#F8FAFC"],
            },
            {
                "name": f"{title} Files",
                "handle": f"@{slugs}.files",
                "tagline": f"Primary sources around {niche}, one case at a time.",
                "ctrAngle": "Evidence-first authority with archival visuals.",
                "visualPalette": ["#0B1220", "#E2E8F0", "#93C5FD"],
            },
            {
                "name": f"{title} Unfiltered",
                "handle": f"@{slugs}.unfiltered",
                "tagline": f"The practical side of {niche}, without the noise.",
                "ctrAngle": "Contrarian clarity for a broad audience.",
                "visualPalette": ["#111827", "#F59E0B", "#F9FAFB"],
            },
        ]
        pillars = [
            {"pillar": "1. Core Explanations", "description": f"Fundamentals and mental models of {niche}."},
            {"pillar": "2. Case Studies", "description": f"Documented examples and primary sources about {niche}."},
            {"pillar": "3. Practical Playbook", "description": f"Actionable steps the audience can apply to {niche}."},
        ]
        topics = [
            {
                "id": i + 1,
                "title": template.format(niche=niche),
                "hook_0_3s": hook.format(niche=niche),
                "curiosityLoop": loop.format(niche=niche),
                "format": "Shorts / Reels (9:16)",
            }
            for i, (template, hook, loop) in enumerate(
                [
                    ("The most misunderstood rule of {niche}", "Almost everyone gets this wrong about {niche}...", "The exception changes the whole picture."),
                    ("A case that changed how we see {niche}", "One documented case rewrote the standard playbook.", "Three overlooked details explain why."),
                    ("Before you start with {niche}", "Do not begin until you understand this constraint.", "It saves months of wasted effort."),
                    ("The trade-off nobody mentions", "Every shortcut in {niche} has a hidden cost.", "Here is the ledger, item by item."),
                    ("What the data actually shows", "The headline says one thing; the dataset says another.", "A simple comparison settles it."),
                ]
            )
        ]
        return {
            "channelConcepts": concepts,
            "contentPillars": pillars,
            "viralTopicsBacklog": topics,
            "productionSpecs": {
                "audioVoice": "",
                "audioBgm": "",
                "visualAiPrompts": "",
                "recommendedPacing": "",
            },
        }

    # ------------------------------------------------------------------
    # Script pack
    # ------------------------------------------------------------------
    def prepare_script(
        self,
        topic: str,
        tone: str = "",
        target_audience: str = "",
        language: str = "",
        voice: str = "",
        channel_slug: Optional[str] = None,
    ) -> Dict[str, Any]:
        context = {
            "topic": topic,
            "tone": tone,
            "target_audience": target_audience,
            "language": language,
            "voice": voice,
        }
        pack = self.load_script_pack(channel_slug)
        if pack:
            bundle = _render(pack, context)
            bundle["source"] = "channel_pack"
        else:
            bundle = self._generic_script_pack(context)
            bundle["source"] = "generic_fallback"

        bundle["topic"] = topic
        bundle["tone"] = tone
        bundle["targetAudience"] = target_audience
        bundle["language"] = language
        bundle.setdefault("audioDirection", {})
        bundle["audioDirection"]["voice"] = voice or bundle["audioDirection"].get("voice", "")
        return bundle

    @staticmethod
    def _generic_script_pack(context: Dict[str, str]) -> Dict[str, Any]:
        topic = context["topic"]
        return {
            "audioDirection": {"voice": "", "bgm": "", "pacing": ""},
            "shortScript": {
                "durationSeconds": 55,
                "hook_0_3s": f"Most people never check this about {topic}.",
                "retention_3_15s": f"Here is the detail that changes the standard explanation of {topic}.",
                "development_15_45s": f"Three documented facts about {topic} are usually left out. Each one is verifiable in a primary source.",
                "climax_45_50s": "The question is not whether the evidence exists, but who benefits from ignoring it.",
                "cta_50_55s": "Save this and tell me which point you want expanded next.",
            },
            "visualScenePrompts": [
                {
                    "scene": i + 1,
                    "timecode": timecode,
                    "aiPrompt": f"Cinematic documentary still about {topic}, archival texture, dramatic lighting, 9:16 aspect ratio, ultra-detailed",
                }
                for i, timecode in enumerate(
                    ["00:00 - 00:03", "00:03 - 00:15", "00:15 - 00:30", "00:30 - 00:45", "00:45 - 00:55"]
                )
            ],
            "instagramCarousel": {
                "slide1_cover": f"What is usually missed about {topic}?",
                "slide2_context": "The standard version is incomplete. The primary sources show a different picture.",
                "slide7_cta": "Save this and follow for the next breakdown.",
            },
            "youtubeMetadata": {
                "title": topic,
                "description": f"A structured breakdown of {topic}, from primary sources to practical conclusions.",
                "tags": [],
            },
        }
