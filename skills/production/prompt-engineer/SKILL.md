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

| Model | Best Mode | Notes |
|-------|-----------|-------|
| nano_banana | Reference sheets, photorealistic | Best for precise control, technical refs |
| seedream | Concept art, artistic | Painterly quality, emotional impact |
| hunyuan | Stylized illustration | Strong line work, graphic styles |
| grok | Creative exploration | Experimental, varied outputs |

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

#### Motion Verbs (Essential)
Unlike image prompts, video prompts MUST include motion:
| Static (Bad) | Motion (Good) |
|--------------|---------------|
| woman standing | woman looks up slowly |
| man at table | man reaches for the glass |
| crowd in market | crowd parts as she walks through |

#### Camera Movement Descriptors
| Movement | Description |
|----------|-------------|
| `push in` | Camera moves toward subject |
| `pull back` / `crane movement` | Camera retreats, often rising |
| `tracking shot` | Camera follows subject laterally |
| `pan` | Camera rotates on axis |
| `static shot` | No camera movement (intentional stillness) |

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
