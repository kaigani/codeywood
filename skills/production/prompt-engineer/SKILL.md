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
