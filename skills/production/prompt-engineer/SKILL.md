# Prompt Engineer Skill

## Purpose
Transform story and visual concepts into optimized prompts for AI image generation services. This skill provides consistent handling of prompts across different generation modes (photorealistic, concept art, reference sheets) and services (fal.ai models).

## Trigger
When generating any visual asset that requires prompt construction.

## Inputs Required
- Visual concept or scene description
- Target output mode (photorealistic, concept, reference)
- Style DNA from PROJECT_CONFIG.yaml
- Character or location data (if applicable)

## Outputs Produced
- Optimized prompt string
- Negative prompt string
- Recommended model parameters

## Prompt Modes

### Mode 1: PHOTOREALISTIC (Production Stills)

**Goal**: Images that look like frames from an actual film shoot.

**Framework**: Frame the prompt as a "cinematographer's lookbook" or "location scout's gallery" rather than "concept art" or "illustration."

**Required Elements**:

1. **Camera & Lens Specification**
   - Specific lens: `24mm anamorphic`, `50mm f/1.4`, `85mm portrait lens`
   - Camera reference: `shot on ARRI Alexa`, `RED camera`, `Panavision`
   - Depth of field: `f/2.8 shallow depth of field`, `f/8 deep focus`

2. **Film Stock / Color Science**
   - Film stocks: `Kodak Vision3 500T`, `Fujifilm Eterna`, `35mm film grain`
   - Digital looks: `ARRI color science`, `Blackmagic RAW`

3. **Lighting as Physical Reality**
   - Practical sources: `practical light from oil lanterns`, `window key light`
   - Quality descriptors: `hard shadows`, `diffused daylight`, `bounce fill`
   - Avoid: "magical glow", "ethereal light", "supernatural illumination"

4. **Material Physics Over Vibe Words**
   - DO: `damp limestone reflecting amber lantern light`, `refractive distortions through leaded glass`
   - DON'T: `ethereal`, `mystical`, `magical`, `impossible`, `supernatural`, `otherworldly`

5. **Power Phrase**
   - Include: `practical set construction` - signals physical reality over digital painting

**Template**:
```
[SCENE DESCRIPTION]. [CAMERA/LENS]. [LIGHTING QUALITY]. [MATERIAL DETAILS].
Shot on [CAMERA], [FILM STOCK]. [f-STOP]. Practical set construction.
```

**Example**:
```
Caribbean colonial prison cells, damp stone walls with iron bars. 24mm anamorphic
lens, f/2.8. Single shaft of golden afternoon light cuts through dust particles,
illuminating condensation on limestone. Rust oxidation on iron, water stains on
mortar, practical oil lantern visible in frame. Shot on ARRI Alexa, Kodak Vision3
500T color science. Practical set construction.
```

### Mode 2: CONCEPT ART (Development Phase)

**Goal**: Evocative images for creative exploration and mood setting.

**Framework**: Painterly, illustrative quality is acceptable. Focus on emotional impact.

**Allowed Elements**:
- Atmospheric adjectives: `ethereal`, `haunting`, `luminous`
- Style references: `in the style of`, `reminiscent of`
- Art medium references: `digital painting`, `concept art`, `matte painting`

**Template**:
```
[MOOD] [SCENE DESCRIPTION]. [STYLE REFERENCE]. [COLOR PALETTE].
[ATMOSPHERE DESCRIPTORS]. Cinematic concept art, high detail.
```

### Mode 3: REFERENCE SHEETS (Character/Location Identity)

**Goal**: Consistent multi-panel layouts for production reference.

**Framework**: Technical specification document, clinical presentation.

**Required Elements**:
1. **Grid specification**: `2x2 grid`, `3x2 layout`, `8-panel composite`
2. **Background**: `neutral #2d2d2d background`, `white studio background`
3. **Panel descriptions**: Explicit description of each panel position
4. **Consistency anchors**: Age, physical attributes, signature elements

**Template**:
```
A professional [GRID] [TYPE] reference sheet for [PRODUCTION TYPE]. Subject: [NAME].

[PANEL DESCRIPTIONS - explicit position and content for each]

Style: [STYLE DNA]. Neutral background with thin dividers between panels.
```

### Mode 4: STORYBOARD (Pre-Production Sketches)

**Goal**: Black and white composition sketches for shot planning. NOT finished art.

**Framework**: Text-to-image ONLY — never use reference images for storyboards. Reference images cause detail bleed (identity sheet faces override the sketch style).

**Required Elements**:
1. **Sketch style directive**: `"black and white rough sketch, thick confident ink strokes, value blocking with simple hatching, figures as dark silhouettes, composition reference only"`
2. **Composition vocabulary**: diagonal motion, vertical framing, negative space, forward vector — describe figures as silhouettes and shapes, NOT by appearance details
3. **No cinematic style DNA**: No lens specs, no film stock references
4. **Aggressive negative prompt**: `color, detailed rendering, photorealistic, finished artwork, realistic skin/eyes/hair, identity sheet, film grain, bokeh`

**Model**: Nano Banana Pro text-to-image (`fal-ai/nano-banana-pro`), 40 steps, guidance 4.5

**Content Filter Workarounds**:
- Gallows/hanging scenes get flagged — describe as "empty gallows structure" or abstract the aftermath
- Don't depict bodies in violent contexts

**Template**:
```
[SKETCH STYLE]. [COMPOSITION TYPE]. [FIGURE SILHOUETTES WITH POSTURE].
[SPATIAL RELATIONSHIPS]. [VALUE/LIGHT BLOCKING].
```

> **Note**: Storyboards are INPUT to frame generation — generate boards first, then use them as composition reference for production frames.

---

### Action Sequence Triptych Awareness

When a prompt describes multiple sequential actions, Nano Banana Pro sometimes generates a **multi-panel triptych** instead of a single image. These triptychs are:
- **NOT good as start frames** (video models need a single image)
- **Valuable as element reference_image_urls** for action sequences — they show the motion arc across panels (start pose → mid-action → end state)

**Prevention**: Prompt must describe ONE frozen moment, not a sequence.
**If generated**: Store in REFERENCES/shot_frames/ for reuse as pose guides.

---

## Vocabulary Guide

### Photorealistic - AVOID These Words
| Category | Vibe Words to Avoid |
|----------|---------------------|
| Light | ethereal, magical, mystical, supernatural, impossible |
| Atmosphere | otherworldly, dreamlike, fantastical, enchanted |
| General | stunning, breathtaking, amazing, incredible |
| Style | concept art, illustration, digital painting, render |

### Photorealistic - USE These Words
| Category | Technical Terms to Use |
|----------|------------------------|
| Light | practical, key light, fill, bounce, hard shadow, diffused |
| Lens | anamorphic, spherical, telephoto, wide-angle, f-stop values |
| Camera | ARRI Alexa, RED, Panavision, Sony Venice, Blackmagic |
| Film | Kodak Vision3, Fujifilm Eterna, 35mm grain, color science |
| Material | oxidation, patina, weathering, condensation, reflection, refraction |
| Set | practical set construction, period-accurate props, location scout |

## Negative Prompt Templates

### Photorealistic Mode
```
digital painting, illustration, concept art, anime style, cartoon,
stylized, CGI render, video game, oversaturated, HDR, neon colors,
fantasy glow, magical effects, lens flare abuse, floating elements,
deformed anatomy, extra limbs, bad proportions, blurry, low quality
```

### Reference Sheet Mode
```
desaturated, gritty, grimdark, realistic gore, sexualized,
Halloween costume aesthetic, campy, muddy colors, floating heads,
bland lighting, generic fantasy, anime style, cartoon style,
multiple people, crowd scene, deformed, extra limbs, bad anatomy
```

## Model Selection Guide

### Cloud Models (fal.ai)

| Model | Best Mode | Notes |
|-------|-----------|-------|
| nano_banana | Reference sheets, photorealistic | Best for precise control, technical refs, highest detail density |
| seedream | Concept art, artistic | Painterly quality, emotional impact |
| hunyuan | Stylized illustration | Strong line work, graphic styles |
| grok | Creative exploration | Experimental, varied outputs |

### Local Models (ComfyUI)

| Model | Best Mode | Speed | Quality vs NBP | Notes |
|-------|-----------|-------|----------------|-------|
| flux2-klein-t2i | Drafts, iteration, storyboards | ~8-15s | ~75% | cfg 4.0, steps 20, MUST use wide aspect ratio for scenes |
| flux2-t2i (Dev) | Production frames | ~150-270s | ~85-90% | steps 20, best local option for final frames |
| flux2-klein-edit | Character likeness transfer | ~21s | ~85-90% of Dev i2i | Input image resolution determines output resolution |
| flux2-i2i (Dev) | Hero frames, final production | ~270s | ~95% | Best skin/material micro-detail locally |

**Klein vs Dev decision**: Use Klein for anything iterative (storyboards, drafts, concept exploration). Switch to Dev only for final production frames where texture and detail density matter. Klein at 20 steps matches Dev at 12 steps for composition quality, but can never match Dev's material texture rendering.

#### Klein Optimal Settings

| Param | Simple Scenes | Complex Scenes | Notes |
|-------|--------------|----------------|-------|
| cfg | 3.5 | 4.0 | 3.5 too soft for unusual subjects (skeletons, dense environments); 5.0 no improvement over 4.0 |
| steps | 10-12 | 20 | Linear ~0.4s/step. Converges by step 20 — no quality gain at 28 |

Klein warm speed: ~6s t2i, ~21s i2i (vs ~150s Dev t2i, ~270s Dev i2i) — 25x/12x faster when model cached.

#### Quality Ceiling Comparison

| Model | Quality vs NBP | Generation Time | Best For |
|-------|---------------|-----------------|----------|
| Klein | ~75% | ~6-15s | Drafts, iteration, storyboards |
| Dev | ~85-90% | ~150-270s | Production frames |
| NBP (cloud) | 100% (baseline) | varies | Final hero frames, identity sheets |

Main Klein gaps vs NBP: foreground clutter density, material micro-texture (dust grain, yellowed plastic, oxidized metal), dynamic range (deeper blacks, more vivid highlights), fine anatomical detail.

### Z-Image → Qwen Edit Pipeline

For local ($0.00) production frames with character consistency:

1. **Phase 1 — Z-Image t2i**: Generate isolated character refs (square) + location refs (wide). Best for clean individual refs with high texture quality.
2. **Phase 2 — Qwen Image Edit**: Compose refs into scene frames (character + location per shot). The killer advantage is consistency across shots, not per-frame quality.

When to use vs Klein/Dev pipeline:
- **Z-Image + Qwen**: When you need character consistency across many frames (dialogue scenes, paper cuts)
- **Klein**: When iterating on composition and don't need cross-frame consistency
- **Dev**: When final production quality matters and you can wait

See: `references/services/z-image/z-image-base.md` and `references/services/qwen/qwen-image-edit.md`

### Reference Image Ordering (Nano Banana Pro)

When using Nano Banana Pro with multiple reference images, ordering in the `image_urls` array matters:

1. **Identity sheets FIRST** — highest priority for character likeness
2. **Storyboard board SECOND** — composition reference
3. **Location ref LAST**

If identity sheets go after the storyboard, the board's character appearance can override identity, degrading likeness.

**Content filter**: Remove age references like "He is 17" from prompts — triggers policy violation.

### JSON Prompting for Multiref (Flux/ComfyUI)

When using Flux multiref workflows with 2+ reference images, JSON-structured prompts referencing images by number produce more accurate results:

```json
{
  "scene": "Two characters meet at a market stall",
  "subject_1": "The alien from image 1 stands behind the counter",
  "subject_2": "The robot from image 3 examines the merchandise"
}
```

This is more reliable than prose descriptions for complex multi-reference compositions.

## Process

### Step 1: Identify Output Mode
Determine if the request is for:
- Production stills → PHOTOREALISTIC mode
- Early development → CONCEPT ART mode
- Identity/reference → REFERENCE SHEET mode

### Step 2: Gather Source Data
- Read PROJECT_CONFIG.yaml for style DNA
- Read relevant character/location configs
- Note any specific visual keywords

### Step 3: Build Prompt Structure
Follow the template for the identified mode:
1. Assemble scene/subject description
2. Add mode-appropriate technical elements
3. Apply vocabulary corrections (replace vibe words)
4. Add style DNA elements
5. Construct negative prompt

### Step 4: Parameter Selection
Based on mode and model:
- Set aspect ratio (16:9 for locations, square for identity sheets)
- Set resolution (2K for final, 1K for exploration)
- Set inference steps (40 for quality, 25 for speed)
- Set guidance scale (4.5 standard, lower for creativity)

## Integration with fal_generate.py

The prompt engineer skill informs these functions:
- `build_identity_prompt()` - Reference sheet mode
- `build_hero_prompt()` - Photorealistic mode
- `build_location_prompt()` - Photorealistic mode with architectural focus

## Examples

### Input: "Prison cells where the ledger was hidden"

**Concept Art Mode Output**:
```
Prompt: Haunting prison cells beneath a Caribbean gallows, shafts of ethereal
golden light piercing the darkness, atmosphere of forgotten confessions and
desperation. Moody cinematic concept art, rich shadows, amber and rust palette.

Negative: cartoon, anime, bright colors, cheerful, modern elements
```

**Photorealistic Mode Output**:
```
Prompt: 18th century Caribbean colonial prison cells, damp limestone walls with
mortar deterioration visible, rust-oxidized iron bars, single shaft of afternoon
sun cutting through dust particles at 45-degree angle. Period-accurate iron
shackles, practical oil lantern mounted on wall bracket. 24mm anamorphic lens,
f/2.8, shallow depth of field on foreground bars. Shot on ARRI Alexa, Kodak
Vision3 500T. Practical set construction, location scout photograph.

Negative: digital painting, illustration, concept art, magical glow,
supernatural lighting, fantasy elements, stylized, CGI render
```

## Quality Checklist

Before finalizing any prompt:
- [ ] Mode-appropriate vocabulary used
- [ ] No conflicting style signals (photorealistic + "concept art")
- [ ] Technical specifications included for photorealistic mode
- [ ] Material physics described, not just mood
- [ ] Negative prompt addresses common failure modes
- [ ] Aspect ratio appropriate for output type

---

## Advanced Prompting Techniques (Tested 2026-02-23)

These techniques were validated through systematic A/B testing across 26+ generations.

### Technique 1: Prompt Opener Framing

The first 2-5 words of a prompt set the model's interpretation mode. This affects composition, lighting, and detail rendering significantly.

**Effectiveness ranking** (best to worst):
1. `Film still.` — Most cinematic, best composition and lighting
2. `Cinematic establishing shot from a [genre] [type].` — Strong genre-appropriate rendering
3. `Photograph of [location].` — Good photographic realism, slightly clinical
4. Raw description (no framing) — Weakest results, most generic

**Examples**:
```
✅ "Film still. Wide shot of an abandoned warehouse..."
✅ "Cinematic establishing shot from a dark sci-fi thriller. An abandoned..."
⚠️ "Photograph of an abandoned warehouse interior. Center frame:..."
❌ "Show a dusty warehouse with a skeleton sitting at a desk..."
```

### Technique 2: Spatial Layer Structure (FOREGROUND/SUBJECT/BACKGROUND)

For complex scenes with many objects, explicitly structuring the prompt into spatial layers dramatically improves object density and depth composition.

**Template**:
```
[FRAMING]. [SETTING].
FOREGROUND: [close objects, desk surface, floor clutter].
SUBJECT: [main subject with detailed physical description].
BACKGROUND: [environment stretching into depth].
OVERHEAD: [lighting source].
[Technical specs]. [Color/grade]. [Film reference].
```

**When to use**: Scenes requiring dense visual clutter, multiple object types, or strong sense of depth. Particularly effective for production-design-heavy shots (workstations, laboratories, markets, control rooms).

**When NOT to use**: Simple portraits, single-subject shots, or when the model needs creative freedom with composition.

### Technique 3: Exhaustive Physical Vocabulary for Unusual Subjects

Models default to their training distribution. For unusual subjects (skeletons, aliens, monsters, damaged objects), one-word descriptions are insufficient. You must describe the physical specifics exhaustively to override the model's default interpretation.

**Pattern**: Name the subject THEN enumerate its visible physical features:

```
❌ "A skeleton sits at a desk"
✅ "A complete human skeleton — bare white skull with empty eye sockets,
    exposed ribcage, skeletal arms and bony fingers — sits slumped at
    a dusty desk. The skeleton wears rotting work coveralls and a faded
    trucker cap on its skull."
```

**Reinforce with negative prompts** using antonyms of the desired state:
```
negative_prompt: "alive, skin, flesh, living person, muscle, tissue"
```

This applies to any subject that deviates from photographic norms: damaged buildings (describe the damage), alien creatures (describe anatomy), fantasy props (describe materials and wear).

### Technique 4: Aspect Ratio as Composition Control

Aspect ratio is not just a formatting choice — it fundamentally changes how subjects are rendered.

| Ratio | Effect | Best For |
|-------|--------|----------|
| 1:1 (1024x1024) | Compresses scenes, subjects dominate, less environment | Portraits, icons, reference sheets |
| 5:3 (1280x768) | Balanced scene + subject, good depth | Establishing shots, workstation scenes |
| 16:9 (1280x720) | Maximum environment, subject can get lost | Landscapes, wide establishing shots |

**Critical finding**: Square format can make complex subjects (skeletons, robots, damaged objects) look like normal humans/objects because there's insufficient spatial context for the model to render unusual details. Wide formats give the model room to render both subject detail AND environmental context.

### Technique 5: Negative Prompt Strategy

Effective negative prompts operate on three levels:

1. **Style exclusion**: `cartoon, anime, illustration, painting, digital art, 3D render, CGI`
2. **Quality floor**: `blurry, low quality, smooth surfaces, pristine, new, clean`
3. **Subject-specific antonyms**: `alive, skin, flesh` (for skeletons), `modern, contemporary` (for period pieces)

The subject-specific antonyms are the most impactful and most commonly overlooked.

---

## STILL IMAGE: Logical Consistency Rules

When crafting prompts for still images, avoid "logical knots" that confuse the model. Each element must work together physically and cinematically.

### Rule 1: Single Time of Day / Lighting State

**Problem**: Asking for a "transition" (e.g., "golden hour to wrong-blue moonlight") in a single still forces the model to represent change over time.

**Result**: The model may split the image awkwardly or create muddy orange-teal color casts.

**Fix**: Describe the **result** of the transition, not the transition itself. Pick the dominant look.

| Wrong | Right |
|-------|-------|
| "golden hour fading to purple dusk" | "purple dusk with faint amber warmth from lantern" |
| "sunrise to full daylight" | "harsh midday sun, high contrast shadows" |
| "night becoming dawn" | "pre-dawn blue, first pink on horizon" |

### Rule 2: Lens Logic Must Be Consistent

**Problem**: Wide-angle lenses (24mm) naturally produce deep focus. Asking for "shallow depth of field" with a wide lens contradicts optical physics.

**Cinematography Reality**:
| Lens | Natural DoF | Use For |
|------|-------------|---------|
| 24mm wide | Deep focus | Environments, establishing shots, epic scope |
| 50mm normal | Medium | General purpose, natural perspective |
| 85mm+ telephoto | Shallow focus | Portraits, close-ups, subject isolation |

**Fix**: Match lens choice to desired depth of field:

| Wrong | Right |
|-------|-------|
| "24mm anamorphic, shallow DoF" | "24mm anamorphic, deep focus" |
| "85mm, everything in focus" | "24mm wide angle, deep focus" |
| "wide angle, blurred background" | "85mm telephoto, shallow DoF, bokeh" |

### Rule 3: Describe States, Not Motion

**Problem**: Still images cannot show motion. Describing actions mid-process ("landing", "falling", "running") forces the model to freeze an unstable moment.

**Fix**: Describe the **pose** or **result** of the action:

| Motion (Bad) | State (Good) |
|--------------|--------------|
| "woman landing on floor" | "woman in mid-crouch on stone floor" |
| "man falling backward" | "man caught off-balance, arms outstretched" |
| "ship sinking into waves" | "ship listing severely, deck nearly vertical" |
| "flames spreading across building" | "building engulfed in flames, structure collapsing" |

### Rule 4: Conflicting Light Sources

**Problem**: Multiple light sources with different qualities can create muddy or impossible lighting.

**Fix**: Establish hierarchy - one KEY light, supporting FILL or ACCENT lights:

| Conflicting | Hierarchical |
|-------------|--------------|
| "sunlight and moonlight both illuminating the scene" | "moonlight primary, faint amber lantern accent on face" |
| "harsh shadows and soft diffused light" | "hard key light from left, soft fill on right" |

### Example: Before/After Optimization

**Before** (logical knots):
```
Interior of colonial prison at night, golden hour to wrong-blue transition,
young woman landing silently on stone floor having dropped through window,
24mm anamorphic lens, shallow depth of field, long perspective of cell doors
```

**After** (logically consistent):
```
Cinematic wide shot, interior Caribbean colonial prison corridor at night.
A young woman in mid-crouch on weathered stone floor beneath a high barred window.
Practical oil lantern casts flickering amber glow against damp walls.
Wrong-blue teal moonlight streams through bars, creates sharp shadows.
Long perspective of iron cell doors receding into dark misty void.
Shot on ARRI Alexa, 24mm anamorphic lens, deep focus, high contrast,
heavy texture on stone and iron.
```

**Fixes applied**:
1. Single lighting state (moonlight dominant, lantern accent)
2. Wide lens + deep focus (not shallow DoF)
3. "Mid-crouch" pose instead of "landing" action

---

## FRAME vs VIDEO PROMPTS (CRITICAL DISTINCTION)

Frame prompts and video prompts serve different purposes. Confusing them causes generation failures.

### Frame Prompts (for Nano Banana Pro / image generation)

**Purpose**: Generate a single, clean moment to use as a video start frame.

**Rules**:
- Describe STATIC states, not transitions
- No temporal language ("then", "as", "shifts to")
- Single lighting state
- Single character pose/expression

| Element | Frame Prompt Approach |
|---------|----------------------|
| Expression | "Her expression is focused determination" |
| Action | "She crouches at the wall, blade in hand" |
| Lighting | "Wrong-blue moonlight from barred window" |

### Video Prompts (for Kling / video generation)

**Purpose**: Describe motion and transitions that animate FROM the start frame.

**Rules**:
- Include motion verbs and camera movement
- Transitions are allowed ("shifts from X to Y")
- Describe what CHANGES, not what stays static
- Must be START FRAME AWARE - continue from visible state

| Element | Video Prompt Approach |
|---------|----------------------|
| Expression | "Her expression shifts from determination to horror" |
| Action | "She pries at the mortar, stone dust falling" |
| Camera | "Slow dolly-in as she discovers the book" |

### Transitional Language Placement

| Language Type | Frame Prompt | Video Prompt |
|---------------|--------------|--------------|
| "shifts from X to Y" | ❌ NEVER | ✅ Yes |
| "turns and walks" | ❌ NEVER | ✅ Yes |
| "as the sun sets" | ❌ NEVER | ✅ Yes |
| Static pose | ✅ Yes | ⚠️ Add motion |
| Single state | ✅ Yes | ⚠️ Add change |

**CRITICAL**: If transitional language appears in a frame prompt, it will cause composite images (multiple states rendered in one frame).

---

## VIDEO GENERATION: Kling 3.0 Pro

### Overview

Kling 3.0 Pro (`fal-ai/kling-video/v3/pro/image-to-video`) generates 3-15 second video clips from starting images with strong character/location consistency through its Elements system.

### API Schema Requirements

**CRITICAL**: These formats are enforced by validation - incorrect formats will fail.

#### Elements Format
Elements provide character/location consistency across the video. BOTH fields are required:
```python
elements = [
    {
        "frontal_image_url": "https://...",      # REQUIRED: Clear frontal view
        "reference_image_urls": ["https://..."]  # REQUIRED: Array of additional angles
    }
]
```
- **Wrong**: `{"frontal_image_url": "..."}` (missing reference_image_urls)
- **Right**: `{"frontal_image_url": "...", "reference_image_urls": ["..."]}`

#### Multi-Prompt Format
Multi-prompt enables multiple "cuts" within a single video. Each prompt needs its own duration:
```python
multi_prompt = [
    {"prompt": "Close-up shot...", "duration": "3"},
    {"prompt": "Medium shot...", "duration": "3"},
    {"prompt": "Wide shot...", "duration": "4"}
]
```
- **Wrong**: `["prompt 1", "prompt 2"]` (strings, not dicts)
- **Wrong**: `[{"prompt": "..."}]` (missing duration)
- **Right**: `[{"prompt": "...", "duration": "N"}]`
- **Sum Rule**: Total of all `duration` values must equal the video's total `duration`

#### Duration Values
- Always use **strings**, not integers: `"5"` not `5`
- Range: "3" to "15" seconds
- With audio (`generate_audio: true`): $0.336/second
- Without audio: $0.224/second

### Element Reference Syntax

In prompts, reference uploaded elements with `@Element1`, `@Element2`, etc:
```
"@Element1 walks through the @Element2 market, looking around curiously"
```
- @Element1 = First element in array (typically main character)
- @Element2 = Second element (typically location or secondary character)

### Video Prompting Techniques

#### Start Frame Awareness (CRITICAL)

Video prompts must describe actions that CONTINUE FROM the visible start frame state.

The model SEES the start frame. If the prompt contradicts what's visible, the model will:
- Try to reconcile the contradiction (creating awkward transitions)
- Invent intermediate actions (moving to a "new" position)
- Produce discontinuous motion

**Before writing video prompts**:
1. View/understand the start frame (generated shot frame OR extracted last frame)
2. Note the character's current position/state/expression
3. Write prompts that continue FROM that state, not TO that state

| Start Frame Shows | BAD Prompt | GOOD Prompt |
|-------------------|------------|-------------|
| Mars IN doorway | "She reaches for the door handle" | "She steps forward through the doorway" |
| Hands already working | "She notices the loose stone" | "She continues prying at the mortar" |
| Character sitting | "She walks to the chair and sits" | "She shifts in her seat, leaning forward" |

#### Motion Verbs (Essential)
Unlike image prompts, video prompts MUST include motion:
| Static (Bad) | Motion (Good) |
|--------------|---------------|
| woman standing | woman looks up slowly |
| man at table | man reaches for the glass |
| crowd in market | crowd parts as she walks through |

#### Camera Movement Descriptors

> **LTX-2 Note**: Use `dolly in` not `push in` — LTX-2 renders equipment nouns as physical objects. See `video-director/SKILL.md` for the full camera motion anti-patterns table.

| Movement | Description | LTX-2 Safe? |
|----------|-------------|-------------|
| `dolly in` / `dolly forward` | Camera moves toward subject | Yes |
| `pull back` / `crane movement` | Camera retreats, often rising | Yes |
| `tracking shot` | Camera follows subject laterally | Yes |
| `pan right` / `pan left` | Camera rotates on axis (specify direction) | Yes |
| `static shot` | No camera movement (intentional stillness) | Yes |
| ~~`push in`~~ | Unreliable on LTX-2 | Avoid |

#### Transition Language (Multi-Prompt)
When using multi-prompt, **prefix each prompt with "Cut to:"** to signal clear scene transitions. This helps the model understand each segment is a distinct shot:

- Cut 1: "Cut to: Close-up on hands examining..."
- Cut 2: "Cut to: @Element1 speaks to the merchant, expression shifts from..."
- Cut 3: "Cut to: Wide shot pulling back as @Element1 turns and walks away..."

**Note**: The "Cut to:" prefix improves transition clarity and reduces artifacts between segments.

### Multi-Cut Scene Template

For a 10-second, 3-cut scene:
```python
multi_prompt = [
    {
        "prompt": "Cut to: Close-up on [DETAIL], [MOOD], [LIGHTING], cinematic shallow depth of field",
        "duration": "3"
    },
    {
        "prompt": "Cut to: @Element1 [ACTION], [EXPRESSION CHANGE], medium close-up, [LIGHTING]",
        "duration": "3"
    },
    {
        "prompt": "Cut to: Wide shot [PULLBACK ACTION] as @Element1 [DEPARTURE ACTION] into @Element2, [ATMOSPHERE], cinematic crane movement",
        "duration": "4"
    }
]
```

### Recommended Parameters

```python
request = {
    "start_image_url": start_url,        # Required: Starting frame
    "prompt": prompt,                      # OR multi_prompt (mutually exclusive)
    "multi_prompt": multi_prompt,
    "elements": elements,                  # Character/location references
    "duration": "10",                      # Total video length
    "aspect_ratio": "16:9",               # "16:9", "9:16", or "1:1"
    "generate_audio": True,               # Native audio generation
    "negative_prompt": "blur, distort, low quality, cartoon, anime, deformed hands",
    # Optional:
    "end_image_url": end_url,             # For transition videos
}
```

### Character Element Best Practices

For maximum character consistency:
1. **Frontal**: Use identity sheet or clear frontal portrait
2. **References**: Include 2-3 additional angles (action pose, profile, etc.)
3. **Multiple characters**: Add as separate elements, reference as @Element1, @Element2

```python
# Good character element setup
elements = [
    {
        "frontal_image_url": upload(identity_sheet),
        "reference_image_urls": [
            upload(hero_shot_1),
            upload(hero_shot_2)
        ]
    }
]
```

### Location Element Best Practices

Locations can also use elements for consistency:
```python
{
    "frontal_image_url": upload(main_location_ref),
    "reference_image_urls": [upload(alternate_angle)]
}
```

Reference in prompts: `"walks through the bustling @Element2 market"`

### Video Prompt Examples

**Single Character Motion**:
```
@Element1 looks up slowly, her eyes catching the golden light, a subtle knowing
smile crosses her face, cinematic slow movement, shallow depth of field
```

**Multi-Character Interaction**:
```
@Element1 and @Element2 exchange a glance, @Element1 reaches out to touch
@Element2's arm, intimate moment, golden hour lighting, cinematic two-shot
```

**Scene Progression (3 cuts)**:
```
Cut 1: "Close-up on hands examining strange glowing bottles, curiosity, soft
        ambient light filtering through market stalls"
Cut 2: "@Element1 speaks to an unseen merchant, her expression shifts from
        curiosity to suspicion, medium close-up, warm golden market lighting"
Cut 3: "Wide shot pulling back as @Element1 turns and walks away into the
        bustling @Element2 market, atmospheric haze, golden hour light"
```

### Common Failure Modes

| Issue | Cause | Fix |
|-------|-------|-----|
| Validation error on multi_prompt | List of strings, not dicts | Use `[{"prompt": "...", "duration": "N"}]` |
| Validation error on elements | Missing reference_image_urls | Always include both frontal AND references |
| Duration mismatch | Cut durations don't sum to total | Ensure sum equals video duration |
| Character inconsistency | Only frontal image provided | Add 2-3 reference angles |
| Static video | No motion verbs in prompt | Add action verbs, camera movement |
| **"Custom Voice IDs not supported with Elements"** | Using both voice_ids AND elements | **Choose one**: voice OR elements, not both |
| **Unexpected objects/creatures appear** | Prose/narrative language interpreted literally | Use purely descriptive language (see below) |

### Video Prompts: Descriptive vs Narrative Language

**CRITICAL**: Video models interpret language literally. Prose or narrative language will be rendered visually.

| Narrative (BAD) | Descriptive (GOOD) |
|-----------------|-------------------|
| "atmosphere of lingering presence" | "empty room, dust in the air" |
| "something was here" | "bare stone walls, straw on floor" |
| "a sense of dread fills the space" | "dark shadows in corners, dim lighting" |
| "memories of the past echo" | "old scratches on the wall, faded marks" |
| "danger lurks unseen" | "she looks around cautiously" |

**Rule**: Describe only what the CAMERA SEES, not what the CHARACTER FEELS or what the STORY IMPLIES.

### LTX-2 Style Prompting (Non-Photorealistic Looks)

LTX-2 cannot change rendering medium but CAN produce striking non-photorealistic looks by describing **physical materials and production techniques** that exist in the real world.

**Prompt Architecture for Experimental Styles**:

1. **Physical frame/medium** (what the footage is playing ON or shot WITH):
   - "Footage playing on a damaged VHS tape through a CRT television"
   - "Shot on Kodak Aerochrome infrared film stock"
   - "Footage from a FLIR thermal imaging camera"

2. **Material artifacts** (physical damage, chemical processes, surface texture):
   - "Heavy analog signal corruption: horizontal tracking lines roll up the screen"
   - "Chemical burn stains blooming orange through the emulsion"
   - "UV-reactive paint smeared across surfaces — vivid green and hot pink glow"

3. **Active scene description** (avoid static words — see trigger warning below):
   - Describe people DOING things, not posing for pictures
   - Include motion verbs even for heavily stylized scenes
   - Use temporal connectors: "then", "as", "slowly"

4. **Audio layer** (ambient sound enhances temporal coherence):
   - "The VHS player hums and clicks, audio warped by tracking errors"
   - "The UV tubes emit a low-frequency electrical buzz"

**Trigger Word Warning**: The words "photograph", "photographic print", "print", "frame" (as picture frame), and "still" cause LTX-2 to produce near-static output. Always reframe static medium references as active physical phenomena. See `video-director/SKILL.md` for the full trigger word table and fixes.

**Optimal prompt length**: 500-700 characters. Shorter prompts produce fewer hallucinated elements. The screenplay format (`EXT. LOCATION – TIME` headers) improves shot adherence.

### Voice vs Elements Trade-off

**CRITICAL LIMITATION**: Kling 3.0 does not allow `voice_ids` and `elements` in the same request.

| Need | Use | Trade-off |
|------|-----|-----------|
| Character speaks with custom voice | `voice_ids` only | Rely on start frame for visual consistency |
| Character visual consistency across cuts | `elements` only | Use native audio, no custom voice |

**Workflow for dialogue scenes**:
1. Use a frame showing the character as `start_image_url`
2. Include character description in prompts (hair, clothing)
3. Use `voice_ids` with `<<<voice_N>>>` syntax
4. NO `elements` array

**Workflow for visual consistency scenes**:
1. Use `elements` with frontal + reference images
2. Use `@ElementN` syntax in prompts
3. NO `voice_ids` - use native audio generation

### Quality Checklist (Video)

Before submitting a Kling 3.0 request:
- [ ] Elements have both `frontal_image_url` AND `reference_image_urls`
- [ ] Multi-prompt uses dict format with `prompt` and `duration` keys
- [ ] Cut durations sum to total video duration
- [ ] Prompts include motion verbs and camera movement
- [ ] @ElementN references match uploaded element order
- [ ] Duration values are strings ("5" not 5)

---

## VOICE DESIGN: Character Voice Pipeline

Creating consistent character voices for video requires a multi-step pipeline using MiniMax for voice design and Kling for video integration.

### Voice Pipeline Overview

```
MiniMax voice-design → Preview Audio → Kling create-voice → Kling voice_id → Kling video
     ($1.00)              (.mp3)           ($0.035)         (numeric ID)      ($0.392/s)
```

**IMPORTANT**: MiniMax voice IDs are NOT compatible with Kling video. You must clone the MiniMax audio using Kling's create-voice endpoint to get a Kling-compatible voice_id.

### Step 1: MiniMax Voice Design

**Endpoint**: `fal-ai/minimax/voice-design`

**Cost**: $1.00 per voice + $0.03/1000 chars preview

Use the "Archetype + Modifier" formula for best results:

```python
voice_prompt = """A young female adventurer, 16 years old, with a clear and warm voice
that carries a subtle Caribbean lilt. She speaks with quick wit and easy charm,
her words winding and redirecting like someone used to talking her way out of trouble.
There's a guarded intelligence beneath the friendly surface. Slightly breathless energy,
as if she might need to run at any moment. Confident delivery that masks deeper uncertainty."""

preview_text = "You're asking what I want? That's a big question for someone who just met me."

result = fal_client.subscribe(
    "fal-ai/minimax/voice-design",
    arguments={
        "prompt": voice_prompt,
        "preview_text": preview_text,
    }
)
# Returns: {"custom_voice_id": "ttv-...", "audio": {"url": "https://..."}}
```

**Voice Description Formula**:
1. **Archetype**: Role-based character (e.g., "young adventurer", "wise mentor", "grumpy sailor")
2. **Physicality**: Vocal texture (e.g., "gravelly", "breathy", "crisp", "warm")
3. **Disposition**: Emotional baseline (e.g., "guarded", "optimistic", "cynical")
4. **Speech Pattern**: Delivery style (e.g., "quick-witted", "slow and deliberate", "winding")

### Step 2: Kling Voice Clone

**Endpoint**: `fal-ai/kling-video/create-voice`

**Cost**: $0.035 per voice

Clone the MiniMax preview audio to get a Kling-compatible voice_id:

```python
result = fal_client.subscribe(
    "fal-ai/kling-video/create-voice",
    arguments={
        "voice_url": minimax_audio_url,  # The preview audio from Step 1
    }
)
# Returns: {"voice_id": "848145936509059116"}
```

**Audio Requirements**:
- Duration: 5-30 seconds
- Clean, noise-free
- Single voice (no background speakers)
- Formats: mp3, wav, ogg, m4a, aac

### Step 3: Use Voice in Kling Video

**Cost**: $0.392/second (with voice control)

Reference the Kling voice_id using `<<<voice_1>>>` syntax directly before the dialogue:

```python
request = {
    "start_image_url": image_url,
    "prompt": "Young woman examines strange bottles, she says <<<voice_1>>> 'I've never seen bottles like these before' expression shifts to suspicion, close-up shot",
    "voice_ids": ["848145936509059116"],  # Kling voice_id from Step 2
    "duration": "5",
    "generate_audio": True,
}
```

**Voice Reference Syntax**:
- `<<<voice_1>>>` - First voice in `voice_ids` array
- `<<<voice_2>>>` - Second voice (max 2 per generation)

**IMPORTANT**: Place the voice tag directly before the quoted dialogue, not as a subject:
- **Correct**: `"She says <<<voice_1>>> 'Hello, stranger.'"`
- **Wrong**: `"<<<voice_1>>> says 'Hello, stranger.'"` (voice tag as subject)

### MiniMax Voice Prompt Examples

**The Clever Young Adventurer** (Mars):
```
A young female adventurer, 16 years old, with a clear and warm voice that carries
a subtle Caribbean lilt. She speaks with quick wit and easy charm, her words winding
and redirecting like someone used to talking her way out of trouble. Guarded intelligence
beneath the friendly surface. Confident delivery that masks deeper uncertainty.
```

**The Gruff Sea Captain**:
```
A middle-aged male with a deep, weathered voice roughened by salt air and shouted orders.
Strong Scottish accent, speaks with gruff authority and a perpetual undertone of impatience.
Words come in short, commanding bursts. Occasional warmth breaks through the harshness.
```

**The Ethereal Presence**:
```
A female voice with an otherworldly quality, clear and resonant as if speaking in a vast
empty space. Calm and measured delivery, slightly detached from emotion. Words carry
weight and significance. Neither warm nor cold, simply present.
```

**The Young Scholar**:
```
A male voice in his late teens, educated and precise in word choice but with youthful
enthusiasm breaking through. Speaks quickly when excited about ideas, slows deliberately
when explaining. Slight breathlessness from constant mental energy.
```

### MiniMax Technical Settings

When generating TTS with MiniMax (if using for non-Kling purposes):

| Setting | Range | Notes |
|---------|-------|-------|
| Pitch | -5 to +5 | Lower for villains/authority, higher for youth/energy |
| Speed | 0.8x to 1.2x | Lower for calculating, higher for frantic |
| Emotion | Auto/Happy/Sad/Angry/Fearful/Neutral | "Auto" reads punctuation cues |

### Voice Pipeline Cost Summary

| Step | Cost | Output |
|------|------|--------|
| MiniMax voice-design | $1.00 + preview | Voice profile + preview audio |
| Kling create-voice | $0.035 | Kling-compatible voice_id |
| Kling video (per second) | $0.392 | Video with character voice |

**Example 5-second video with voice**: $1.00 + $0.035 + ($0.392 × 5) = $2.995

### Quality Checklist (Voice)

Before voice pipeline:
- [ ] Character voice description uses Archetype + Modifier formula
- [ ] Preview text captures character's speech patterns
- [ ] MiniMax preview audio saved for reference
- [ ] Kling voice_id stored in project metadata
- [ ] Video prompts use `<<<voice_N>>>` syntax correctly
