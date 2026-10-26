---
name: youtube-thumbnail-design
description: "YouTube thumbnail design with specific dimensions, contrast rules, and mobile preview optimization. Covers safe zones, text placement, face expression psychology, and A/B testing. Use for: YouTube thumbnails, video cover images, click-through optimization. Triggers: youtube thumbnail, thumbnail design, video thumbnail, click through rate, ctr optimization, youtube cover, video cover image, thumbnail maker, thumbnail tips, youtube design, video preview image"
allowed-tools: Bash(belt *)
---

> **Install the belt CLI skill:** `npx skills add belt-sh/cli`

# YouTube Thumbnail Design

Create high-CTR YouTube thumbnails with AI image generation via [inference.sh](https://inference.sh) CLI.

## Quick Start

> Requires inference.sh CLI (`belt`). [Install instructions](https://raw.githubusercontent.com/inference-sh/skills/refs/heads/main/cli-install.md)

```bash
belt login

# Generate a thumbnail
belt app run falai/flux-dev-lora --input '{
  "prompt": "YouTube thumbnail style, close-up of a person with surprised excited expression looking at a glowing laptop screen, vibrant blue and orange color scheme, dramatic studio lighting, shallow depth of field, high contrast, cinematic",
  "width": 1280,
  "height": 720
}'
```


## Specifications

| Spec | Value |
|------|-------|
| Dimensions | 1280 x 720 px (minimum) |
| Recommended | 1920 x 1080 px |
| Aspect ratio | 16:9 |
| Max file size | 2 MB |
| Formats | JPG, GIF, PNG |

## The 120px Test

Your thumbnail appears at roughly **120px wide** on mobile — that's how most viewers first see it.

**At 120px, viewers must be able to identify:**
1. The mood/emotion (from colors and expression)
2. The general subject (from composition)
3. The text (if any — only if large enough)

**Test:** view your thumbnail at 120px width. If it's a muddy blur, redesign.

## Safe Zones

```
┌─────────────────────────────────────────────┐
│                                             │
│   ✅ SAFE FOR TEXT AND KEY ELEMENTS         │
│                                             │
│                                             │
│                                             │
│                                             │
│                                       ┌───┐ │
│                                       │ ⏱ │ │ ← Timestamp overlay
│                              ┌────────┴───┘ │    (bottom-right)
│   ┌────┐                     │  DURATION    │
│   │ CH │ Chapter marker      └──────────────│
└───┴────┴────────────────────────────────────┘
     ↑ Bottom-left: chapter/progress markers
```

**Avoid placing critical elements in:**
- Bottom-right corner (video duration timestamp)
- Bottom-left corner (chapter markers, progress bar)
- Extreme edges (cropping varies by device)

## Color Strategy

### High-Contrast Pairs That Work

| Combination | Mood | Best For |
|-------------|------|----------|
| Yellow + Black | Urgency, attention | Tech, business, lists |
| Red + White | Energy, excitement | Entertainment, reactions |
| Blue + Orange | Professional contrast | Education, tutorials |
| Green + White | Growth, money | Finance, success stories |
| Purple + Yellow | Premium, creative | Design, art, creativity |
| White + Dark | Clean, minimal | Luxury, minimalist channels |

### Color Rules

- **Background** and **text/subject** should be complementary or high-contrast
- Avoid same-temperature colors touching (red on orange = mud)
- Use **3 colors maximum** per thumbnail
- Saturate more than real life — thumbnails compete with bright UI

## Text on Thumbnails (Rule 15 — Titanic Typography Standard)

> [!IMPORTANT]
> Low CTR (0.90% to 1.5%) is almost always caused by tiny, cluttered fonts that become illegible smudges on mobile feeds. Under **Rule 15**, thumbnails follow the **Titanic Typography Scale**: 3 words maximum, massive font sizes (160px–220px), and zero micro-text.

### When to Use Text

- Emotional hook / shock: *"A MAIOR FARSA"*, *"ERA TUDO FALSO!"*
- Mystery / anomaly: *"18 ANDARES NO SUBSOLO"*, *"NUNCA EXISTIU"*
- Action / veto: *"CÓPIA VETADA!"*, *"SEGREDO DE ESTADO"*
- Strong stance: *"O GRANDE GOLPE"*, *"PROIBIDO"*

### When NOT to Use Text

- The video title already says it (redundancy kills curiosity)
- Technical explanations, bullet points, subtitles, or metadata tables (strictly banned on covers)
- Anything that requires font size < 50px to fit on screen

### Rule 15 Typography Specifications (1920x1080 Master)

| Spec | Rule 15 Standard | Rationale |
|------|-------------------|-----------|
| **Word Limit** | **Max 3 to 4 words** | Read in 500ms on mobile feed without cognitive overload |
| **Headline Font Size** | **160px to 220px** | Must be effortlessly legible at 120px mobile width |
| **Badge / Seal Font Size** | **50px to 65px** | Supporting context (e.g. `● CASO REAL`, `CONFIDENCIAL`) |
| **Micro-Font Floor** | **Strictly prohibited < 50px** | Zero bullet points, zero subtitles, zero fine print |
| **Protective Stroke** | **10px to 16px (`stroke_width >= 11`)** | Black `#000000` stroke isolates letters over any background |
| **Font Family** | **Ultra-condensed heavy (`Anton`, `Impact`, `Montserrat 900`)** | Maximum vertical fill with minimal horizontal sprawling |
| **Color Contrast** | **Bi-tonal: White (`#FFF`) + Alert Yellow (`#FFE500`)** | Peripheral eye rods trigger instant attention to warning yellow |
| **Chiaroscuro Shield** | **Dark gradient (`rgba(4,6,10,0.96)`) on text side** | 100% contrast guaranteed without flattening background subject |
| **YouTube Safe Zone** | **Clear 320x140px bottom-right corner** | Completely clear of YouTube's video duration timestamp badge |


## Face Expression Psychology

Thumbnails with faces get **higher CTR** than faceless thumbnails. Expression matters:

| Expression | CTR Impact | Best For |
|------------|-----------|----------|
| **Surprise/shock** | Highest | Reaction, reveal, discovery content |
| **Curiosity** | High | Tutorial, how-to, tips |
| **Excitement** | High | Unboxing, reviews, announcements |
| **Concern/worry** | Medium-high | Warning, mistake, problem content |
| **Confidence** | Medium | Expert advice, authority content |
| **Neutral** | Lowest | Avoid unless your brand is minimalist |

### Face Composition Rules

- Face should fill **30-50%** of the thumbnail
- Eyes looking **toward the text or subject** (directs viewer attention)
- Eyes looking at camera = connection. Eyes looking at object = curiosity.
- Place face on one side (usually left), text or subject on the other

```bash
# Generate a face-forward thumbnail
belt app run falai/flux-dev-lora --input '{
  "prompt": "close-up portrait of a man with genuinely surprised expression, mouth slightly open, raised eyebrows, looking at camera, left side of frame, vibrant teal background, dramatic rim lighting, YouTube thumbnail style, high contrast, cinematic",
  "width": 1280,
  "height": 720
}'

# Generate a face-looking-at-subject thumbnail
belt app run bytedance/seedream-4-5 --input '{
  "prompt": "person looking amazed at a glowing holographic chart showing upward growth, dramatic blue and green lighting, right side profile view, dark background, tech aesthetic, high energy",
  "size": "2K"
}'
```

## Thumbnail Patterns by Content Type

### Tutorial / How-To
```bash
belt app run falai/flux-dev-lora --input '{
  "prompt": "overhead flat lay of organized workspace with laptop showing code editor, colorful sticky notes, coffee cup, clean bright background, professional setup, tutorial style composition, warm lighting",
  "width": 1280,
  "height": 720
}'
```

### Before/After
```bash
belt app run falai/flux-dev-lora --input '{
  "prompt": "split composition, left side dark and messy disorganized desk, right side bright clean organized minimalist workspace, dramatic contrast between chaos and order, clear dividing line in center, high contrast",
  "width": 1280,
  "height": 720
}'
```

### Product Review / Comparison
```bash
belt app run falai/flux-dev-lora --input '{
  "prompt": "two products facing each other with dramatic lighting and sparks between them, competition battle concept, dark background with colorful rim lighting, versus comparison style, high energy, product photography",
  "width": 1280,
  "height": 720
}'
```

### Listicle / Number
```bash
belt app run falai/flux-dev-lora --input '{
  "prompt": "dynamic arrangement of 7 different colorful objects floating in space against dark gradient background, each item distinct and clearly separated, energetic composition, vibrant saturated colors, studio lighting",
  "width": 1280,
  "height": 720
}'
```

## A/B Testing

Test one variable at a time:

| Variable | Test A vs B |
|----------|-------------|
| Face vs No face | Same composition, with/without person |
| Expression | Surprise vs curiosity |
| Color scheme | Warm vs cool palette |
| Text vs No text | With/without text overlay |
| Background | Bright vs dark |
| Composition | Left-facing vs right-facing subject |

```bash
# Generate variant A
belt app run falai/flux-dev-lora --input '{
  "prompt": "..., bright yellow background, ...",
  "width": 1280, "height": 720
}' --no-wait

# Generate variant B (same prompt, different background)
belt app run falai/flux-dev-lora --input '{
  "prompt": "..., dark navy background, ...",
  "width": 1280, "height": 720
}' --no-wait
```

## Thumbnail Checklist

- [ ] 1280x720 minimum (1920x1080 preferred)
- [ ] Under 2MB file size
- [ ] Passes the 120px squint test
- [ ] No critical elements in bottom-right (timestamp) or bottom-left (chapter)
- [ ] Max 3 colors, high contrast
- [ ] Text (if any) is max 6 words, bold, with contrast stroke
- [ ] Face expression matches content energy (if applicable)
- [ ] Doesn't duplicate the video title
- [ ] Stands out from surrounding thumbnails (check your niche)
- [ ] Works on both light and dark YouTube backgrounds

## Common Mistakes

| Mistake | Problem | Fix |
|---------|---------|-----|
| Too much text | Unreadable at thumbnail size | Max 6 words or no text |
| Low contrast | Disappears in the feed | Use complementary colors |
| Cluttered composition | Eye doesn't know where to look | One focal point |
| Generic stock photo feel | No personality, gets skipped | Authentic expressions, unique angles |
| Tiny details | Lost at 120px | Bold, simple shapes |
| Same style every video | Viewer fatigue | Vary within brand guidelines |
| Misleading thumbnail | Kills trust, hurts retention | Match the actual content |

## Related Skills

```bash
npx skills add inference-sh/skills@ai-image-generation
npx skills add inference-sh/skills@image-upscaling
npx skills add inference-sh/skills@prompt-engineering
```

Browse all apps: `belt app list`

