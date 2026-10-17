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

## 3. High-CTR Packaging (Thumbnail + Title Synergy)

A documentary with 100% retention achieves zero views if nobody clicks:

1. **The 3-Element Visual Rule**:
   - Limit the thumbnail to **3 visual focal points** (e.g., 1 high-contrast subject/face, 1 dramatic background/document, 1 bold badge/text element).
2. **The 120px Mobile Test**:
   - 70%+ of YouTube impressions happen on mobile. Shrink the thumbnail to 120px wide: if the core idea, emotion, or visual contrast isn't instantly clear, redesign it.
3. **Curiosity Gap vs. Clickbait**:
   - **Clickbait**: Makes a promise the video cannot fulfill (causes 10-second retention collapse).
   - **Curiosity Gap**: Opens a question only watching the video can answer (e.g., *"O Algoritmo Que Quebrou a Receita Federal"*).
4. **Zero Title-Thumbnail Redundancy**:
   - If the title says *"Como a Oracle Perdeu o Contrato Bilionário"*, the thumbnail must NOT say *"A Oracle Perdeu"*. The thumbnail should say *"ERRO DE CÓDIGO"* or show a redacted contract with a stamped *"CANCELADO"*.

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
