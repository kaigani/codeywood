# Shot Image Generator Skill

## Purpose
Generate final shot images by combining reference images with shot specifications to produce consistent, production-ready frames.

## Trigger
SHOT_LIST_EP{{XX}}.json exists and all references are complete.

## Inputs Required
- `SHOT_LIST_EP{{XX}}.json`
- `CANON_DB.json` (with all reference paths)
- `STYLEGUIDE_VISUAL.md`
- `CHARACTER_REFS/*/refs/*.png`
- `LOCATION_REFS/*/refs/*.png`
- `PROP_REFS/*/refs/*.png` (if needed)

## Outputs Produced
- `SHOTS_EP{{XX}}/{shot_id}.png` - Generated shot images
- Updated `SHOT_LIST_EP{{XX}}.json` (with generation status)
- `GENERATION_LOG_EP{{XX}}.json` - Generation attempts and results

## Process

### Step 1: Load Shot Specification

Read shot from SHOT_LIST:
```json
{
  "shot_id": "EP01_SC03_SH02",
  "description": "...",
  "characters": [...],
  "location": "...",
  "references": {
    "character_refs": [...],
    "location_ref": "..."
  },
  "camera": {...},
  "composition": {...}
}
```

### Step 2: Gather Reference Images

Load all required references:
- Character reference(s) matching pose/expression
- Location reference matching area/time
- Prop references if specified

Verify all files exist before proceeding.

### Step 3: Construct Prompt

Build prompt from shot specification:

```
{{LOCATION_DESCRIPTION}}, {{TIME_OF_DAY}} lighting,
{{CHARACTER_1_DESCRIPTION}} {{CHARACTER_1_ACTION}} in {{POSITION_1}},
{{CHARACTER_2_DESCRIPTION}} {{CHARACTER_2_ACTION}} in {{POSITION_2}},
{{CAMERA_SHOT_TYPE}}, {{COMPOSITION_NOTES}},
{{LIGHTING_DESCRIPTION}}, {{MOOD}},
{{STYLE_KEYWORDS}}
```

Add negative prompts:
- Global negatives from STYLEGUIDE
- Character-specific negatives from CANON_DB
- Shot-type specific negatives

### Step 4: Configure API Call

From `config/fal_api_settings.json`:

```json
{
  "endpoint": "fal-ai/recraft-v3",
  "params": {
    "image_size": {"width": 1920, "height": 1080},
    "num_inference_steps": 28,
    "guidance_scale": 3.5
  },
  "reference_images": [...],
  "reference_weights": {
    "character": 0.95,
    "location": 0.85
  }
}
```

### Step 5: Generate Image

Make API call with:
- Constructed prompt
- Reference images
- Appropriate weights
- Shot-specific aspect ratio

### Step 6: Save and Log

Save generated image:
```
SHOTS_EP{{XX}}/EP01_SC03_SH02.png
```

Update shot in SHOT_LIST:
```json
{
  "generation": {
    "prompt": "{{FULL_PROMPT}}",
    "status": "generated",
    "attempts": 1,
    "output_path": "SHOTS_EP01/EP01_SC03_SH02.png",
    "timestamp": "2026-01-25T10:30:00Z"
  }
}
```

Log to GENERATION_LOG:
```json
{
  "shot_id": "EP01_SC03_SH02",
  "timestamp": "...",
  "prompt": "...",
  "references_used": [...],
  "params": {...},
  "success": true,
  "notes": ""
}
```

### Step 7: Quality Check (Automated)

Basic automated checks:
- Image generated successfully
- Correct dimensions
- File size reasonable
- No obvious errors (black image, etc.)

Flag for manual review if:
- Multiple characters present
- Complex composition
- First shot of a new character/location

### Step 8: Handle Failures

If generation fails:
1. Log error
2. Retry with adjusted parameters (max 3 attempts)
3. If still failing, flag for manual intervention

Retry adjustments:
- Lower reference weight
- Simplify prompt
- Change seed
- Adjust guidance

### Step 9: Batch Processing

For efficiency, process shots in batches:

**Batch by Scene**:
- All shots in a scene share location reference
- Load location once, generate all scene shots

**Batch by Character**:
- Solo scenes with same character
- Load character refs once

**Parallel Processing**:
- Independent shots can generate simultaneously
- Respect API rate limits

## Prompt Construction Templates

### Single Character Shot
```
{{LOCATION}}, {{TIME}} lighting, {{CHARACTER}} {{ACTION}},
{{SHOT_TYPE}} shot, {{COMPOSITION}}, {{STYLE}}
```

### Two Character Shot
```
{{LOCATION}}, {{TIME}} lighting,
{{CHAR_1}} {{ACTION_1}} {{POSITION_1}},
{{CHAR_2}} {{ACTION_2}} {{POSITION_2}},
{{SHOT_TYPE}} shot, {{COMPOSITION}}, {{STYLE}}
```

### Insert/Detail Shot
```
{{OBJECT_DESCRIPTION}}, close-up detail shot,
{{CONTEXT}}, {{LIGHTING}}, {{STYLE}}
```

### Establishing Shot
```
{{LOCATION_FULL_DESCRIPTION}}, wide establishing shot,
{{TIME}} lighting, {{ATMOSPHERE}}, cinematic, {{STYLE}}
```

## Reference Weight Guidelines

| Content | Character Weight | Location Weight |
|---------|------------------|-----------------|
| Close-up single | 0.95 | 0.70 |
| Medium single | 0.90 | 0.80 |
| Two-shot | 0.85 | 0.80 |
| Wide with figures | 0.80 | 0.85 |
| Establishing (no figures) | N/A | 0.90 |
| Insert/detail | Varies | Varies |

## Error Handling

### Common Issues

**Character Drift**:
- Increase character reference weight
- Use more specific character description
- Simplify pose requirements

**Location Inconsistency**:
- Increase location reference weight
- Be more specific about camera position
- Reference specific location area

**Wrong Composition**:
- More explicit position instructions
- Simplify to fewer elements
- Generate separately and composite (advanced)

**Lighting Mismatch**:
- Explicit lighting description
- Match time of day references
- Adjust mood keywords

## Batch Generation Workflow

```
1. Load SHOT_LIST
2. Group shots by scene
3. For each scene:
   a. Load location reference
   b. Load character references for scene
   c. For each shot:
      i. Construct prompt
      ii. Generate image
      iii. Save and log
      iv. Update status
4. Generate summary report
5. Flag shots needing review
```

## Notes

- This is the most API-intensive skill
- Reference images are critical for consistency
- Start with simple shots before complex ones
- Build confidence in reference system
- Log everything for debugging
- Manual review is part of the process
- Regeneration is expected and planned for
