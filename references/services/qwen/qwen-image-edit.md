# Qwen Image Edit — Production Reference

Workflow: `qwen-image-edit` on ComfyUI (`http://192.168.1.181:8100/workflows/qwen-image-edit`)
Model: Qwen Image Edit 2509 (Lumina2 architecture)
Inputs: prompt (required), image (required), image2 (optional), image3 (optional), seed, steps (default 4)

> **API Change**: The workflow API is now **asynchronous**. POST returns a job ID; poll for status; fetch result when complete. See `references/services/comfyui/async-api.md` for the new submit → poll → fetch pattern and a ready-to-use Python helper.

---

## Critical Rule: `image` Slot = Output Aspect Ratio

The first image slot (`image`) determines output dimensions/aspect ratio:
- Wide location ref (1280x536) as `image` → wide cinematic output
- Portrait character ref (768x1024) as `image` → portrait output

**For cinematic frames**: ALWAYS put the wide location ref as `image`
**Exception**: Character close-ups can use portrait character ref as `image`

---

## Reference Slot Strategy by Shot Type

| Shot Type | `image` | `image2` | `image3` | Prompt Pattern |
|-----------|---------|----------|----------|----------------|
| Wide establishing (no chars) | location | — | — | Descriptive scene |
| Detail/prop shot | location | — | — | "On the counter from this image..." |
| Single char + location | location | character | — | "The man from image 2 sits at..." |
| Two-shot | location | char A | char B | "Man from image 2...woman from image 3..." |
| Character close-up | character | — | — | "Close-up of this man's face..." |
| Through-window | exterior | character | — | "The man from image 2 walks..." |

---

## Prompt Formula

Best: `Film still opener` + `style DNA (stock, grain, crop)` + `ref-aware character placement` + `emotional/atmospheric direction`

### Prompt Style Comparison
- **Ref-aware** ("the man from image 1"): Slightly more reliable for character placement and multi-character scenes
- **Descriptive** (full scene without referencing images): Works but character consistency slightly lower
- **Edit-style** ("add X to this image"): Preserves more base image structure, less cinematic freedom
- **Recommendation**: Use ref-aware for all character shots

---

## Steps Parameter

| Steps | Time | Quality | Use Case |
|-------|------|---------|----------|
| 4 | ~14-18s | Good | Default for iteration and paper cut |
| 8 | ~26s | Marginal improvement | Final production frames |
| 12 | ~28s | Diminishing returns | Not worth it |

Speed by ref count: 1 ref ~14s, 2 refs ~17s, 3 refs ~22s (all at 4 steps)

---

## Character & Environment Consistency

- WITH character ref: Strong likeness preservation across shots
- WITHOUT character ref: Generic person from text — no visual consistency
- WITH location ref: Strong environment matching (colors, layout, props, lighting)
- WITHOUT location ref: Generic environment from text — no consistency
- **Rule**: Always include BOTH refs for character-in-environment shots

---

## Quality Assessment

- Material texture: Excellent (formica, chrome, vinyl, ceramic all read correctly)
- Lighting: Outstanding (fluorescent/amber/dawn color temperature transitions)
- Film grain: Visible and appropriate when prompted
- Composition: Model follows framing directions well
- Emotional register: Achievable through prompt direction ("jaw works", "not okay but present")
- Environmental density: High (props, fixtures, reflections all present)

---

## Comparison: Qwen Edit vs Z-Image vs Klein

- **Klein (pure t2i)**: Flat, muddy, no character consistency across frames
- **Z-Image (pure t2i)**: Higher per-frame quality (texture, lighting, detail), but different character every frame
- **Qwen Edit (ref-based)**: Similar quality to Z-Image, WITH character/environment consistency across all shots

The killer advantage is consistency, not per-frame quality.

---

## Recommended Production Pipeline

1. **Z-Image t2i** → Generate hero shots (characters) + location refs (interior, exterior)
2. **Qwen Image Edit** → Compose refs into scene frames (character + location per shot)
3. For close-ups: character ref as `image`, prompt describes emotion/context
4. For wide/medium shots: location ref as `image`, character ref(s) as `image2`/`image3`

See also: `references/services/z-image/z-image-base.md`

---

## Two Modes: Compose-from-Refs vs Edit-on-Edit

### Mode 1: Compose-from-Refs (refs as input)
- **Best for**: Initial frame generation, character placement, scene composition
- **Character fidelity**: High — maintains ref likeness across shots
- **Use for**: All initial frame generation, OTS shots, any shot needing character consistency

### Mode 2: Edit-on-Edit (existing frame as input)
- **Best for**: Targeted fixes, reframing, lighting/prop changes
- **Character fidelity**: Drifts from original refs — faces change on each edit pass
- **Use for**: Object removal/addition, prop fixes, sign on/off, tighter/wider reframing

### What works in edit-on-edit:
- **Object fixes**: Turn off neon sign, remove extra mug, change prop — clean, targeted edits
- **Reframing**: Medium → medium-close, or wider — preserves character and adds/removes context
- **Lighting changes**: Color temperature shifts, time-of-day adjustments

### What DOESN'T work in edit-on-edit:
- **Spatial repositioning**: Moving a character from booth to stool fails — too dramatic
- **Angle/perspective change**: OTS from a two-shot works compositionally but character faces drift
- **Major recomposition**: Fundamentally changing the layout of a scene

---

## OTS Shot Strategy (from refs)

For over-the-shoulder shots, compose from refs — don't edit existing two-shots:
- `image` = location ref (for wide aspect ratio)
- `image2` = shoulder character ref (described as "back of head, shoulder, out of focus")
- `image3` = face character ref (described as sharp, in focus, facing camera)
- Prompt must explicitly describe foreground shoulder as soft/OOF and face as sharp/in-focus

| Shot Type | `image` | `image2` | `image3` | Notes |
|-----------|---------|----------|----------|-------|
| OTS behind A, seeing B | location | char A (shoulder) | char B (face) | Works well |
| OTS behind B, seeing A | location | char B (shoulder) | char A (face) | May confuse roles — test |

---

## Iterative Workflow

1. **Generate** initial frame from refs (compose-from-refs mode)
2. **Review** for issues (wrong props, extra objects, lighting problems)
3. **Fix** specific issues via edit-on-edit (targeted prompts)
4. **Derive** shot variations (OTS, different angles) from refs, NOT from existing frames
5. **Reframe** existing frames for tighter/wider versions via edit-on-edit

---

## Field Names

- **Qwen Edit**: `image`, `image2`, `image3`
- **Flux Dev multiref**: `image1`, `image2` (different from qwen!)

**Common mistake**: Using `image1` with qwen or `image` with Dev multiref.

---

## Known Limitations

- Output is often square — use `pad_to_16x9()` to add dark borders for cinematic aspect ratio
- Species drift: animal subjects sometimes become human (especially in expression panels)
- Character faces drift on each edit-on-edit pass — derive new angles from refs, not edits
