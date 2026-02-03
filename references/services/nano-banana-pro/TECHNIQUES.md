# Nano Banana Pro (recraft-v3) Techniques

> Practical knowledge from production use. Updated 2026-01.

## Service Overview

**Endpoint:** `fal-ai/recraft-v3`
**Best For:** Character references, stylized illustration, consistent style application
**Strength:** High control over composition and color

---

## Proven Techniques

### 1. Hex Color Grading

Nano Banana Pro uniquely responds to explicit hex color palettes. Include as "Color grading" in your prompt.

**Format:**
```
Color grading: ["#060910","#0b1220","#081f39","#15406a","#174f7c","#337eb2","#4ca9d2","#56b4d9","#b1cad4","#b9bfc8","#742d4b","#fe9f58"]
```

**How to Use:**
- Extract palette from style reference images (use color picker tools)
- Order from dark to light OR by frequency
- 8-12 colors works well
- Include accent colors for visual interest

**Effect:** Constrains generation to your palette, maintains visual consistency across assets.

**Note:** This technique is specific to Nano Banana Pro. Other services ignore or misinterpret hex arrays.

---

### 2. Composite Layout Prompting

Instead of abstract concepts like "turnaround" or "character sheet", describe the exact panel layout.

**Bad (generic):**
```
Character turnaround sheet, front back side views
```

**Good (specific):**
```
Clean layout with multiple views on neutral beige/gray background. Grid format showing:

TOP ROW: Extreme close-up of eyes showing iris detail and eye shape | Close-up of natural smile showing teeth and mouth shape

LEFT SIDE: Large hero portrait shot, head and shoulders, straight-on angle, neutral expression, natural lighting, eyes looking directly at camera

MIDDLE ROW: Detailed hand reference showing natural hand gesture with fingers relaxed

BOTTOM ROW: Three portrait headshots - angry expression, slight smile, neutral expression - showing subtle facial variations and personality

RIGHT SIDE: Full body turnaround - front view and back view showing complete outfit, standing naturally with arms at sides, clean studio lighting

Technical specs: High resolution, consistent lighting across all panels, clean composite layout with thin black dividing lines between panels
```

**Why This Works:**
- Removes ambiguity about layout
- Each panel has clear purpose and framing
- Technical specs ensure consistency
- Grid format helps model organize composition

---

### 3. Reference Weight Tuning

| Use Case | Style Ref Weight | Character Ref Weight |
|----------|------------------|---------------------|
| Lock style exactly | 0.90-0.95 | — |
| Style with flexibility | 0.80-0.85 | — |
| Character consistency (same pose) | 0.85 | 0.95 |
| Character variation (new pose) | 0.80 | 0.85-0.90 |
| Expression changes only | 0.85 | 0.90 |
| Style exploration | 0.50-0.70 | — |

**Note:** Higher weights = more faithful reproduction but less creativity.

---

### 4. Background Treatment

For reference sheets, specify background explicitly:

**Neutral backgrounds that work:**
- `neutral beige/gray background`
- `clean studio backdrop`
- `soft gradient from warm gray to cool gray`

**Avoid:**
- `white background` (can blow out details)
- `transparent background` (not supported)
- Complex environments (compete with subject)

---

### 5. Lighting Descriptions

Nano Banana Pro responds well to specific lighting language:

**For Reference Sheets:**
- `clean studio lighting`
- `consistent lighting across all panels`
- `soft diffused key light`
- `natural lighting, eyes looking directly at camera`

**For Mood/Hero Shots:**
- `dramatic rim lighting`
- `golden hour warmth`
- `harsh high-contrast shadows`
- `ambient occlusion emphasizing form`

---

## API Settings

**Recommended defaults for character references:**
```json
{
  "image_size": {"width": 1536, "height": 1024},
  "num_inference_steps": 28,
  "guidance_scale": 3.5,
  "style_reference_weight": 0.85,
  "character_reference_weight": 0.90
}
```

**For hero/mood shots:**
```json
{
  "image_size": {"width": 1024, "height": 1536},
  "num_inference_steps": 35,
  "guidance_scale": 4.0
}
```

---

## Template: Character Identity Sheet

Complete prompt template for a character reference composite:

```
[CHARACTER_DESCRIPTION]

Clean layout with multiple views on neutral beige/gray background. Grid format showing:

TOP ROW: Extreme close-up of eyes showing [EYE_DETAILS] | Close-up of [MOUTH_EXPRESSION] showing teeth and mouth shape

LEFT SIDE: Large hero portrait shot, head and shoulders, straight-on angle, [EXPRESSION], natural lighting, eyes looking directly at camera

MIDDLE ROW: Detailed hand reference showing [HAND_DESCRIPTION]

BOTTOM ROW: Three portrait headshots - [EXPRESSION_1], [EXPRESSION_2], [EXPRESSION_3] - showing subtle facial variations and personality

RIGHT SIDE: Full body turnaround - front view and back view showing [OUTFIT_DESCRIPTION], standing naturally with arms at sides, clean studio lighting

Technical specs: High resolution, consistent lighting across all panels, clean composite layout with thin black dividing lines between panels

[STYLE_KEYWORDS]

Color grading: [HEX_PALETTE]
```

---

## What Doesn't Work

See [LIMITATIONS.md](./LIMITATIONS.md) for known issues and workarounds.
