# Z-Image Base — Production Reference

Workflow: `z-image-base-t2i` on ComfyUI (`http://192.168.1.181:8100/workflows/z-image-base-t2i`)

---

## API Change

The workflow API is now **asynchronous**. POST returns a job ID; poll for status; fetch result when complete. See `references/services/comfyui/async-api.md` for the new submit → poll → fetch pattern and a ready-to-use Python helper.

---

## Overview

Z-Image Base is a text-to-image model best suited for generating isolated character and background references. It produces high per-frame quality (texture, lighting, detail) but has no reference image input — each generation is independent with no cross-frame consistency.

---

## Parameters

| Parameter | Default | Notes |
|-----------|---------|-------|
| `prompt` | (required) | Text prompt |
| `negative_prompt` | (required) | Negative prompt |
| `seed` | (required) | For reproducibility |
| `steps` | 25 | Standard quality |
| `cfg` | 4.0 | Classifier-free guidance |
| `width` | varies | 1024 for square refs, 1280 for wide scenes |
| `height` | varies | 1024 for square refs, 720 for wide scenes |

---

## Best Use Cases

- **Isolated character refs** (1024x1024 square, clean/neutral background)
- **Empty background/location refs** (1280x720 wide, no characters)
- **Hero shots** for individual characters
- **Style exploration** before committing to full production pipeline

---

## Prompt Patterns

### Style Prefix Convention

For stop-motion/puppet projects:
```
"High-end stop-motion animation puppet, Laika Studios quality,
handcrafted miniature figure, polymer clay sculpted face,
wire armature, hand-sewn fabric clothing with visible stitching,
miniature practical set, warm storybook lighting,
shallow depth of field macro photography of miniature scene,"
```

For background-only refs, add "NO people, NO characters" explicitly.

### Character Ref Prompt Structure
1. Style prefix
2. Shot type (full body, close-up, etc.)
3. Exhaustive physical description (face, clothing, props)
4. Background directive ("clean neutral studio background")
5. Framing ("full figure visible head to toe, centered in frame")

### Background Ref Prompt Structure
1. Style prefix (background variant)
2. Shot type ("wide establishing shot")
3. Set description (materials, props, lighting)
4. Atmosphere
5. Exclusion ("NO people, NO characters, NO animals")

---

## Output Sizes

| Use Case | Width | Height | Aspect |
|----------|-------|--------|--------|
| Character ref (isolated) | 1024 | 1024 | 1:1 square |
| Character pose (sleeping, action) | 1280 | 720 | 16:9 wide |
| Background/location ref | 1280 | 720 | 16:9 wide |
| Close-up portrait | 720 | 1280 | 9:16 portrait |

---

## Known Biases & Limitations

- **Model bias on headwear**: When generating monkey characters wearing caps, z-image defaults to berets/round hats instead of flat caps. Requires very explicit cap descriptions ("flat cap with stiff short brim in front, also called driving cap, ivy cap, scally cap") and aggressive negative prompt ("beret, round beret, tam, fez, top hat")
- **No reference input**: Every generation is independent — no character consistency across frames. Use downstream compositing (qwen-image-edit or Flux Dev multiref) for consistency
- **No character consistency**: Different face/body every generation. Z-image refs are building blocks for downstream compositing, not final frames

---

## Quality Comparison

| Model | Per-Frame Quality | Consistency | Speed | Cost |
|-------|------------------|-------------|-------|------|
| Z-Image Base | High (texture, lighting, detail) | None (independent) | ~15-25s | $0.00 |
| Klein t2i | Medium (flat, simpler) | None (independent) | ~6-15s | $0.00 |
| Qwen Edit | High (similar to z-image) | High (ref-based) | ~14-22s | $0.00 |
| Flux Dev | Very high (best texture) | None/ref-based | ~150-270s | $0.00 |

---

## Integration with Qwen Edit Pipeline

Z-Image + Qwen Edit is the preferred local pipeline for production frames:

1. **Z-Image t2i** → Generate isolated character refs (square) + location refs (wide)
2. **Review & approve** each ref (QC for likeness, style, anatomy)
3. **Qwen Image Edit** → Compose approved refs into scene frames
4. For close-ups: character ref as `image`, prompt describes emotion/context
5. For wide/medium: location ref as `image`, character ref(s) as `image2`/`image3`

See: `references/services/qwen/qwen-image-edit.md` for compositing details.

---

## API Call Example

```python
from comfyui_helper import submit_and_wait  # see references/services/comfyui/async-api.md

png_bytes = submit_and_wait("z-image-base-t2i", {
    "prompt": "...",
    "negative_prompt": "...",
    "seed": "42",
    "steps": "25",
    "cfg": "4",
    "width": "1024",
    "height": "1024",
})
```
