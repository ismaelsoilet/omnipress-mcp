---
name: omnipress-youtube-documentary
description: "Master runbook for high-retention, investigative, historical, and technical YouTube long-form documentaries (8 to 30+ minutes) and docu-series. Orchestrates 5-act narrative arcs, retention curve optimization, pattern interrupts every 45-60s, visual pacing (B-roll/motion every 3-5s), chapter cliffhangers, packaging (high-CTR thumbnails and curiosity titles), studio broadcast mastering (-14 LUFS), and programmatic Remotion rendering."
---

# OmniPress — YouTube Long-Form Documentary Runbook

> **Master Guide**: This skill governs the production of high-retention, authoritative, and cinematic long-form YouTube documentaries (8 to 30+ minutes) for technical, historical, investigative, tax, and civic topics within the OmniPress ecosystem.

---

## 1. The 5-Act Documentary Narrative Arc

Long-form YouTube videos survive or die based on narrative structure. Never present facts as a linear encyclopedia; structure them as an investigative inquiry:

```
[ ACT 1: THE ANOMALY & THE PROMISE ] (0:00 - 1:30)
  ├── 0:00 - 0:15: Cold Open / Inciting Incident (The Hook)
  ├── 0:15 - 0:45: The Central Question ("Why did nobody notice until now?")
  └── 0:45 - 1:30: The Stakes & The Roadmap (What the viewer will uncover)

[ ACT 2: THE FOUNDATION / DOSSIER ] (1:30 - 5:00)
  ├── Archival evidence, historical context, initial data points
  ├── Pattern Interrupt at ~3:00 (Sudden tempo change or unexpected metric)
  └── Establish the "official story" before dissecting it

[ ACT 3: THE COMPLICATION / THE TURN ] (5:00 - 12:00)
  ├── The flaw in the system / The hidden mechanism
  ├── Escalating tension: evidence that contradicts the consensus
  └── Cliffhanger before Chapter break (~8:00)

[ ACT 4: THE CLIMAX / THE SMOKING GUN ] (12:00 - 20:00)
  ├── The forensic breakthrough / Complete audit / System collapse
  └── The undeniable proof (code, document, transaction ledger, court ruling)

[ ACT 5: THE AFTERMATH & THE LINGERING QUESTION ] (20:00 - End)
  ├── Real-world consequences, policy impact, systemic takeaway
  └── Final thought: A question that reframes how the viewer sees reality
```

---

## 2. Retention Curve Optimization & YouTube Mechanics

YouTube's recommendation algorithm rewards **Average Percentage Viewed (APV > 45-50% on 15m+ videos)** and **Absolute Watch Time**:

### A. The Critical 0–30s Window (Preventing the Drop-Off Cliff)
- **Zero Fluff**: Never begin with a channel intro animation, greeting ("Hey guys, welcome back"), or generic logos.
- **Immediate Payoff**: The first sentence must validate the thumbnail and title within 5 seconds.
- **Visual Motion from Frame 0**: Use dynamic camera moves ([`KenBurnsImage`](../src/video/components/KenBurnsImage.tsx)), soundscape tension, and bold kinetic typography.

### B. The 45–60 Second Retention Reset (Pattern Interrupts)
Audiences tune out if the visual or auditory rhythm remains uniform for >60 seconds:
- **Audio Shift**: Drop the background music completely for 2 seconds to highlight a critical sentence, then drop back in with a heavier bassline.
- **Visual Rhythm**: Switch visual styles: from archival document scan -> to animated map (`remotion-maps`) -> to full-screen motion chart -> to tactical code view.
- **B-Roll Cadence**: Change visual elements every **3 to 5 seconds**. A static image must always have Ken Burns zoom/pan or ambient particle grain.

### C. Chaptering & Micro-Cliffhangers
- Place chapter markers every 2 to 4 minutes.
- **Never end a chapter with closure**: Always end a chapter by introducing a new complication or puzzle before transitioning to the next topic.

---

## 3. High-CTR Packaging & Titanic Typography (Rule 15)

A documentary with 100% retention achieves zero views if nobody clicks. If CTR is between **0.90% and 1.5%**, the packaging is failing. Every documentary thumbnail must strictly follow **Rule 15** ([`15_high_ctr_thumbnail_typography_and_packaging_standards.md`](../../rules/15_high_ctr_thumbnail_typography_and_packaging_standards.md)):

1. **The 3-Word Limit (Max 4 Words)**:
   - Limit text to **3 to 4 power words** maximum (e.g., *"A MAIOR FARSA"*, *"18 ANDARES NO SUBSOLO"*, *"CÓPIA VETADA"*).
   - Never place bullet points, subtitles, paragraph excerpts, or metadata tables on thumbnail covers.
2. **Titanic Typography Scale (160px – 220px)**:
   - Master resolution: 1920x1080 (16:9).
   - Headlines must be **160px to 220px** in heavy ultra-condensed font (`Anton`, `Impact`, `Montserrat 900`).
   - Badges/seals must be **50px to 65px**. Any text below **50px** is strictly prohibited.
   - Letters must carry a protective black stroke of **10px to 16px** (`stroke_width >= 11`) and sit over a dark Chiaroscuro gradient shield on the left.
3. **High-Luminance Contrast Palette**:
   - Bi-tonal combo: Pure White (`#FFFFFF`) on Line 1 + Alert Yellow (`#FFE500` / `#FFD700`) on the shock word.
4. **YouTube Duration Shield (Safe Zone)**:
   - The bottom-right corner (**320x140px**) is the YouTube Duration Badge Death Zone. Zero text or key details in this zone. Main text must be anchored on the left 50-55%.
5. **The 3-Element Visual Rule**:
   - Exactly 3 focal points: 1 dramatic visual/subject on the right, 1 titanic typography block on the left, and 1 contextual seal/badge.
6. **The 120px Mobile Squint Test**:
   - 75%+ of impressions occur on mobile. Export a 120px wide preview: if the power words cannot be read effortlessly in under 1 second, the thumbnail is automatically rejected.
7. **Curiosity Gap vs. Redundancy**:
   - The thumbnail text must NEVER repeat the video title. The thumbnail provides the emotional shock; the title provides the search context.


---

## 4. Broadcast Soundscape & Audio Hierarchy (Rule 10)

Documentaries rely more on sound design than visuals for emotional retention:

1. **Voiceover Gate (-14.0 LUFS)**:
   - Must pass through the Broadcast Mastering Chain: `adeclick` -> `highpass=80` -> `afftdn` -> 4-band surgical EQ -> `acompressor` -> EBU R128 (-14.0 LUFS).
2. **Dynamic Music Ducking**:
   - Voice active: **0.12 to 0.18 (-20dB relative to voice)**. NEVER exceed 0.20 while narrator speaks.
   - Dramatic pauses (>1.5s): Music swells to **0.35–0.40**.
3. **Tactile Foley SFX**:
   - Document reveals: Paper rustle, ink stamp impact.
   - Data highlights: Subtle typewriter mechanical clicks, soft digital ping.
   - Chapter transitions: Deep cinematic sub-bass braam / whoosh.

---

## 5. Remotion Documentary Engine Integration

Combine OmniPress Remotion components for documentary production:

- **16:9 Widescreen Master**: `DocumentaryEpisode-16x9` (1920x1080 @ 30fps).
- **Overlays**:
  - [`TacticalGrid`](../src/video/components/TacticalGrid.tsx) & [`FilmGrain`](../src/video/components/FilmGrain.tsx) for dossier aesthetic.
  - [`SynchronizedCaptions`](../src/video/components/SynchronizedCaptions.tsx) for critical dialogue and quotes.
  - [`KenBurnsImage`](../src/video/components/KenBurnsImage.tsx) for archival photographs and technical diagrams.
- **Programmatic Thumbnail Generation**:
  - `ThumbnailEpisode` rendered via `npm run remotion:render` at 1920x1080 with high-contrast badge styling.

---

## 6. Execution Checklist for AI Agents

When tasked with creating a YouTube documentary:
1. [ ] **Thesis & Evidence Map**: Establish source log (`claim_id`, source URL, confidence) before writing script.
2. [ ] **Two-Column Script**: Visual / B-Roll / SFX in Column 1, Narration in Column 2.
3. [ ] **30s Hook Verification**: First 30s contains zero fluff, establishes premise, and promises payoff.
4. [ ] **Pattern Interrupt Check**: Ensure visual or acoustic shift occurs at least every 60 seconds.
5. [ ] **Voiceover Mastering**: Process raw audio via ffmpeg broadcast chain to -14.0 LUFS.
6. [ ] **Thumbnail & Title Package**: Draft 3 thumbnail concepts + 3 title pairings with zero text redundancy.
7. [ ] **Render & QA**: Render via Remotion, verify audio levels, check mobile legibility, and publish with chapter timestamps in description.
