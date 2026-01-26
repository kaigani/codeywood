# Character Reference Generator Skill

## Purpose
Generate comprehensive character reference image packs that enable consistent character reproduction across all shots.

## Trigger
CANON_DB.json and STYLEGUIDE_VISUAL.md exist.

## Inputs Required
- `CANON_DB.json` (character visual data)
- `STYLEGUIDE_VISUAL.md`
- `CHARACTER_SHEETS/*.md`

## Outputs Produced
- `CHARACTER_REFS/{NAME}/VISUAL_SPEC.md` - Character visual specification
- `CHARACTER_REFS/{NAME}/refs/*.png` - Reference images
- Updated `CANON_DB.json` (reference paths added)

## Reference Types Required

For each main character, generate:

### 1. Turnaround Sheet
- Front view (neutral pose)
- 3/4 view (neutral pose)
- Profile view (neutral pose)
- Back view (neutral pose)

**Purpose**: Establish consistent proportions and features from all angles.

### 2. Expression Pack
- Neutral
- Happy/Pleased
- Sad/Disappointed
- Angry/Frustrated
- Surprised/Shocked
- Determined
- Vulnerable

**Purpose**: Establish how features change with emotion while remaining recognizable.

### 3. Outfit Variants
- Primary/Signature outfit
- 2-3 alternate outfits (based on script needs)

**Purpose**: Enable wardrobe changes while maintaining character identity.

### 4. Action Poses
- 3-5 key poses from script scenarios
- e.g., running, fighting, working, relaxed

**Purpose**: Reference for dynamic shots.

### 5. Detail Close-ups
- Face/head detail
- Hands (if signature gestures)
- Signature props with character

**Purpose**: High-detail reference for close-up shots.

## Process

### Step 1: Extract Character Data

From CANON_DB.json, retrieve:
```json
{
  "description": "...",
  "signature_outfit": "...",
  "color_palette": [...],
  "signature_prop": "...",
  "negative_prompts": [...]
}
```

### Step 2: Create Visual Specification

Generate `CHARACTER_REFS/{NAME}/VISUAL_SPEC.md`:

```markdown
# Visual Specification: {{CHARACTER_NAME}}

## Physical Description
{{FROM_CANON_DB}}

## Signature Look
- **Outfit**: {{OUTFIT}}
- **Colors**: {{PALETTE}}
- **Props**: {{PROPS}}

## Visual Anchors (LOCKED)
- {{FEATURE_1}}
- {{FEATURE_2}}
- {{FEATURE_3}}

## Allowed Variations
- {{VARIATION_1}}
- {{VARIATION_2}}

## Negative Prompts
- {{NEGATIVE_1}}
- {{NEGATIVE_2}}

## Reference Status
- [ ] Turnaround
- [ ] Expressions
- [ ] Outfits
- [ ] Poses
- [ ] Details
```

### Step 3: Generate Turnaround (SEED IMAGE)

Load prompt template:
```
prompts/turnaround.txt
```

Construct prompt:
1. Insert character description
2. Insert signature outfit
3. Add style keywords from STYLEGUIDE_VISUAL.md
4. Add negative prompts

**API Call** (fal.ai/recraft-v3):
```json
{
  "prompt": "{{CONSTRUCTED_PROMPT}}",
  "negative_prompt": "{{NEGATIVE_PROMPTS}}",
  "image_size": {"width": 1024, "height": 1024},
  "num_inference_steps": 28,
  "guidance_scale": 3.5
}
```

Save result as `refs/{name}_turnaround.png`

**CRITICAL**: This becomes the SEED reference for all subsequent images.

### Step 4: Generate Expression Pack

Use turnaround as reference input.

For each expression:
1. Load `prompts/expressions.txt`
2. Modify for specific expression
3. Include turnaround as reference image
4. Set reference_weight: 0.95

Save as `refs/{name}_expr_{emotion}.png`

### Step 5: Generate Outfit Variants

Use turnaround as reference input.

For each outfit:
1. Load `prompts/outfits.txt`
2. Modify for specific outfit description
3. Include turnaround as reference image
4. Set reference_weight: 0.90 (allow outfit variation)

Save as `refs/{name}_outfit_{variant}.png`

### Step 6: Generate Action Poses

Use turnaround as reference input.

For each pose:
1. Load `prompts/action_poses.txt`
2. Describe specific pose
3. Include turnaround as reference image
4. Set reference_weight: 0.85 (allow pose variation)

Save as `refs/{name}_pose_{action}.png`

### Step 7: Generate Details

Use turnaround and best expression as references.

1. Face close-up
2. Hands (if needed)
3. Signature prop interaction

Save as `refs/{name}_detail_{type}.png`

### Step 8: Update CANON_DB

Add reference paths to character entry:

```json
"reference_images": {
  "turnaround": "CHARACTER_REFS/ALICE_CHEN/refs/alice_turnaround.png",
  "front_neutral": "CHARACTER_REFS/ALICE_CHEN/refs/alice_front_neutral.png",
  ...
}
```

### Step 9: Quality Check

For each generated image:
- [ ] Features match turnaround
- [ ] Expression is readable
- [ ] Outfit is accurate
- [ ] Pose is natural
- [ ] Style matches STYLEGUIDE

Flag failures for regeneration.

## Prompt Templates

Located in `prompts/`:

### turnaround.txt
See template file for full prompt structure.

### expressions.txt
See template file for expression-specific prompts.

### outfits.txt
See template file for outfit variant prompts.

### action_poses.txt
See template file for dynamic pose prompts.

## API Configuration

Located in `config/fal_api_settings.json`:

```json
{
  "endpoint": "fal-ai/recraft-v3",
  "default_params": {
    "image_size": {"width": 1024, "height": 1024},
    "num_inference_steps": 28,
    "guidance_scale": 3.5,
    "safety_tolerance": "2",
    "output_format": "png"
  },
  "reference_mode_params": {
    "style_reference_weight": 0.85,
    "character_reference_weight": 0.95
  }
}
```

## Notes

- Turnaround is the SEED - all other images reference it
- Higher reference weights = more consistency, less variation
- Lower reference weights = allow for pose/outfit changes
- Always review generated images before proceeding
- Regenerate any images that break visual anchors
- Update CANON_DB after successful generation
