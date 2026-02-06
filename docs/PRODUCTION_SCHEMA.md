# Visual Production Data Schema

This document defines the YAML schemas for the visual production pipeline.
Data is separated from execution logic to enable:
- Human review of shot lists and clip definitions
- Version control of creative decisions
- Auto-generation of Markdown deliverables
- Reusable execution scripts across all scenes

## Schema Overview

```
PROJECT_CONFIG.yaml          # Project-level: style, assets, models
├── style_dna                # Visual style definition
├── assets                   # Character/location manifest
└── models                   # FAL model configurations

shot_lists/
├── {scene_id}_shots.yaml    # Per-scene shot definitions
└── {scene_id}_shots.md      # Auto-generated deliverable

clip_definitions/
├── {scene_id}_clips.yaml    # Per-scene video clip sequences
└── {scene_id}_clips.md      # Auto-generated deliverable
```

---

## 1. PROJECT_CONFIG.yaml Additions

Add these sections to the existing PROJECT_CONFIG.yaml:

```yaml
# =============================================================================
# VISUAL PRODUCTION CONFIG
# =============================================================================

style_dna:
  # Core visual identity - used in all prompts
  setting: "Caribbean colonial"
  era: "18th century golden age of piracy"

  # Lighting modes (referenced by shots)
  lighting:
    day:
      description: "Golden hour, jewel-toned saturated colors"
      keywords: "golden hour lighting, jewel-toned saturated colors, practical sunlight"
    night:
      description: "Wrong-blue moonlight with amber lantern accent"
      keywords: "wrong-blue moonlight, teal supernatural palette, amber lantern accent"
    supernatural:
      description: "Teal glow, unsettling light sources"
      keywords: "wrong-blue supernatural glow, teal light emanating from within"

  # Camera/film look
  cinematography:
    camera: "ARRI Alexa"
    film_stock: "Kodak Vision3 500T"
    default_lens: "35mm anamorphic"
    depth_of_field: "shallow"

  # Texture/material notes
  textures:
    - "weathered stone"
    - "rusted iron"
    - "salt-worn wood"
    - "practical set construction"

  # Negative prompt (what to avoid)
  negative_prompt: >
    blur, distort, low quality, cartoon, anime,
    deformed hands, extra limbs, multiple faces,
    modern elements, anachronistic objects

# =============================================================================
# ASSET MANIFEST
# =============================================================================

assets:
  # Character identity sheets and references
  characters:
    mars:
      name: "Mars Blackwood"
      description: "16, protagonist, compulsive liar, survivor"
      identity_sheet: "identity_sheets/mars_identity_nano_banana_20260203_131447.png"
      hero_shots:
        entrance: "hero_shots/mars/mars_entrance_nano_banana_20260203_120530.png"
        action: "hero_shots/mars/mars_action_nano_banana_20260203_120530.png"
      visual_keywords:
        - "ink-stained fingers"
        - "practical clothing"
        - "leather vest"
        - "map case at hip"

    jonah:
      name: "Jonah Vane"
      description: "17, truth-cursed, deliberate stillness, built to destroy"
      identity_sheet: "identity_sheets/jonah_identity_nano_banana_20260203_131551.png"
      hero_shots:
        entrance: "hero_shots/jonah/jonah_entrance_nano_banana_20260203_122140.png"
        action: "hero_shots/jonah/jonah_action_nano_banana_20260203_122140.png"
        quiet: "hero_shots/jonah/jonah_quiet_nano_banana_20260203_122140.png"
      visual_keywords:
        - "tall, broad-shouldered"
        - "throat scarring like tree rings"
        - "amber glow beneath skin when lying"
        - "heavy-lidded patient eyes"

    silas_voicetaker:
      name: "Silas / Voice-Taker"
      description: "The entity wearing Silas's face, mid-transformation"
      identity_sheet: "identity_sheets/silas_voicetaker_identity_nano_banana_20260203_193914.png"
      visual_keywords:
        - "Silas's silhouette"
        - "active darkness where face should be"
        - "wet footprints on dry ground"
        - "stands on water"

  # Location references
  locations:
    holding_cells:
      name: "Naval Compound Holding Cells"
      ref: "location_refs/holding_cells_ref_nano_banana_20260204_075649.png"
      description: "Colonial prison corridors, iron cell doors, wrong-blue moonlight"
      keywords:
        - "weathered stone walls"
        - "iron cell doors"
        - "narrow barred windows"
        - "practical oil lantern lighting"

    storage_room:
      name: "Naval Compound Storage Room"
      ref: null  # TODO: Generate dedicated ref
      fallback: "holding_cells"  # Use this ref if dedicated not available
      description: "Cluttered naval storage, crates, small high window"
      keywords:
        - "wooden crates"
        - "coiled rope"
        - "naval supplies"
        - "small high window"
        - "dust motes in moonlight"

  # Storyboards (generated)
  storyboards:
    sc02:
      ref: "storyboards/EP01/pr-sc02-naval-infiltration_storyboard_nano_banana_20260204_230152.png"
    sc03:
      ref: null  # TODO: Generate

# =============================================================================
# MODEL CONFIGURATIONS
# =============================================================================

models:
  nano_banana:
    name: "Nano Banana Pro"
    best_for: "Production stills, identity sheets, precise control"
    endpoints:
      text_to_image: "fal-ai/nano-banana-pro"
      edit: "fal-ai/nano-banana-pro/edit"
    default_params:
      aspect_ratio: "16:9"
      resolution: "2K"
      output_format: "png"

  kling:
    name: "Kling Video 3.0 Pro"
    best_for: "Video generation with character consistency"
    endpoints:
      image_to_video: "fal-ai/kling-video/v3/pro/image-to-video"
      text_to_video: "fal-ai/kling-video/v3/pro/text-to-video"
    default_params:
      aspect_ratio: "16:9"
      generate_audio: true
    cost_per_second: 0.336
```

---

## 2. Shot List Schema

File: `shot_lists/{scene_id}_shots.yaml`

```yaml
# =============================================================================
# SHOT LIST SCHEMA
# =============================================================================
# This file defines all shots for a scene.
# Used to generate: start frames, storyboards, shot list deliverable
# =============================================================================

# -----------------------------------------------------------------------------
# SCENE METADATA
# -----------------------------------------------------------------------------
scene:
  id: string              # Required. Scene identifier (e.g., "sc03")
  name: string            # Required. Human-readable name
  episode: string         # Required. Episode identifier (e.g., "ep01")

  # From screenplay
  description: string     # Required. 1-2 sentence summary
  location: string        # Required. Key from assets.locations
  time_of_day: string     # Required. One of: day | night | dawn | dusk

  # Screenplay reference
  screenplay_sections:    # Optional. References to screenplay
    - string              # e.g., "INT. NAVAL COMPOUND - STORAGE ROOM"

# -----------------------------------------------------------------------------
# VIDEO DIRECTOR METADATA
# Enforces pacing and consistency principles
# -----------------------------------------------------------------------------
director:
  # Pacing structure - shots should follow this rhythm
  pacing_structure:
    - establish           # Wide shot, set the stage
    - approach            # Character enters/moves
    - detail              # Close-up on significant element
    - action              # Key beat of scene
    - reaction            # Character processes
    - transition          # Movement to next beat

  # Dialogue handling strategy
  dialogue_strategy: string  # Required. One of:
    # - "none": Silent scene, no character speech
    # - "adr": ADR-ready footage (silent, dialogue added in post)
    # - "scripted": Specific dialogue in prompts (risky)
    # - "vocalizations": Grunts, sighs, breathing only

  # Sound design notes for the scene
  ambient_sound: string   # Overall ambient soundscape

  # Estimated total duration
  estimated_duration: string  # e.g., "45-60s"

# -----------------------------------------------------------------------------
# CHARACTERS IN SCENE
# Maps characters to Kling element IDs
# -----------------------------------------------------------------------------
characters:
  - id: string            # Required. Key from assets.characters
    element: string       # Required. Kling element ID (e.g., "@Element1")
    role: string          # Required. One of: protagonist | secondary | background

# Example:
# characters:
#   - id: mars
#     element: "@Element1"
#     role: protagonist
#   - id: jonah
#     element: "@Element2"
#     role: secondary

# -----------------------------------------------------------------------------
# SHOTS
# -----------------------------------------------------------------------------
shots:
  - id: integer           # Required. Sequential shot number
    name: string          # Required. Short descriptive name

    # -----------------------------
    # Shot classification
    # -----------------------------
    type: string          # Required. One of:
      # - establish: Wide/atmospheric, often no characters
      # - entrance: Character enters frame/space
      # - action: Key narrative beat
      # - detail: Close-up on object/element
      # - reaction: Character emotional response
      # - reveal: Dramatic reveal of character/object
      # - conversation: Dialogue scene coverage
      # - transition: Movement between beats

    shot_type: string     # Required. One of:
      # - extreme_wide: Landscape/establishing
      # - wide: Full environment + characters
      # - medium_wide: Characters in environment
      # - medium: Waist-up
      # - medium_close: Chest-up
      # - close: Face/head
      # - extreme_close: Detail (eyes, hands, object)

    # -----------------------------
    # Timing
    # -----------------------------
    duration: string      # Required. e.g., "2-3s", "4s"

    # -----------------------------
    # Characters in shot
    # -----------------------------
    characters: list      # Required. List of character IDs, or empty []

    # -----------------------------
    # VIDEO DIRECTOR FIELDS
    # These enforce explicit direction principles
    # -----------------------------

    # Sound (REQUIRED - prevents generic audio)
    sound:
      ambient: string     # Environmental sounds
      character: string   # Character sounds (breathing, footsteps)
      dramatic: string    # Tension/mood sounds

    # Dialogue control (REQUIRED - prevents invented speech)
    dialogue: string      # One of:
      # - "none": Complete silence from characters
      # - "breathing": Only breathing sounds
      # - "effort": Grunts, gasps, exertion sounds
      # - "reaction": Sharp intake, sighs, non-verbal
      # - "scripted: '[exact words]'": Specific dialogue

    # Camera (REQUIRED - explicit camera direction)
    camera:
      movement: string    # One of: static | push_in | pull_out | track | pan | tilt
      speed: string       # One of: slow | medium | fast (if moving)

    # Body language (REQUIRED for shots with characters)
    body_language: string # Specific physical direction

    # Lighting override (optional - defaults to scene.time_of_day)
    lighting: string      # Key from style_dna.lighting

    # Lens override (optional - defaults to style_dna.cinematography.default_lens)
    lens: string          # e.g., "85mm", "24mm anamorphic"

    # -----------------------------
    # References
    # Which assets to include in generation
    # -----------------------------
    refs:
      include_identity: boolean   # Include character identity sheets
      include_location: boolean   # Include location reference
      include_storyboard: boolean # Include scene storyboard
      additional: list            # Additional ref paths

    # -----------------------------
    # The prompt
    # -----------------------------
    prompt: string        # Required. Multi-line prompt text
                          # Should NOT include style DNA (added by generator)
                          # Should NOT include "no spoken dialogue" (added based on dialogue field)

    # -----------------------------
    # Generation metadata
    # -----------------------------
    output_name: string   # Output filename prefix
    priority: string      # One of: required | optional | alternate
    notes: string         # Production notes

# =============================================================================
# EXAMPLE SHOT
# =============================================================================
# shots:
#   - id: 1
#     name: "Storage Room Atmosphere"
#     type: establish
#     shot_type: wide
#     duration: "2-3s"
#     characters: []
#
#     sound:
#       ambient: "Distant dripping water, creaking wood"
#       character: null
#       dramatic: "Atmospheric tension"
#
#     dialogue: "none"
#
#     camera:
#       movement: static
#
#     body_language: null  # No characters
#
#     refs:
#       include_identity: false
#       include_location: true
#       include_storyboard: true
#
#     prompt: |
#       Wide establishing shot of cluttered naval storage room interior at night.
#       Wooden crates stacked high, coiled rope, naval supplies scattered.
#       A single small window high on the wall, wrong-blue moonlight streaming through.
#       Deep shadows in the corners, dust motes visible in the light beam.
#       Atmospheric stillness, no characters visible.
#
#     output_name: "sc03_shot01_establish"
#     priority: required
```

---

## 3. Clip Definition Schema

File: `clip_definitions/{scene_id}_clips.yaml`

```yaml
# =============================================================================
# CLIP DEFINITION SCHEMA
# =============================================================================
# Defines how shots are sequenced into video clips.
# Each clip = one Kling generation (may have multiple cuts via multi-prompt)
# =============================================================================

# -----------------------------------------------------------------------------
# METADATA
# -----------------------------------------------------------------------------
scene_id: string          # Required. Must match shot list
shot_list: string         # Required. Path to shot list YAML

# -----------------------------------------------------------------------------
# CLIPS
# -----------------------------------------------------------------------------
clips:
  - id: integer           # Required. Sequential clip number
    name: string          # Required. Descriptive name

    # -----------------------------
    # Character configuration
    # -----------------------------
    type: string          # Required. One of:
      # - single_character: One @Element
      # - two_character: Two @Elements
      # - no_character: Atmospheric/establishing only

    characters: list      # Required. Character IDs from shot list
    # Example: [mars] or [mars, jonah] or []

    # -----------------------------
    # Start frame strategy
    # -----------------------------
    start_frame:
      strategy: string    # Required. One of:
        # - shot: Use generated frame from shot list
        # - last_frame: Extract from previous clip
        # - custom: Use custom image path

      shot_id: integer    # Required if strategy=shot
      clip_id: integer    # Required if strategy=last_frame
      custom_path: string # Required if strategy=custom

    # -----------------------------
    # Multi-prompt sequence
    # Each prompt = one cut within the clip
    # -----------------------------
    prompts:
      - shot_ref: integer # Optional. Reference to shot in shot list
        duration: integer # Required. Seconds for this cut

        # Prompt can be:
        # 1. Auto-generated from shot_ref (uses shot's prompt + sound + dialogue)
        # 2. Custom override
        prompt: string    # Optional. If null, generated from shot_ref

        # Cut transition prefix
        cut_prefix: boolean  # Default true. Adds "Cut to:" prefix

    # -----------------------------
    # Total duration
    # -----------------------------
    total_duration: integer  # Required. Sum of prompt durations

    # -----------------------------
    # Output
    # -----------------------------
    output_name: string   # Output filename prefix

    # -----------------------------
    # Continuity notes
    # -----------------------------
    continuity:
      from_clip: integer  # Which clip this continues from
      notes: string       # Any continuity concerns

# =============================================================================
# EXAMPLE CLIP
# =============================================================================
# clips:
#   - id: 1
#     name: "Establish + Entrance"
#     type: single_character
#     characters: [mars]
#
#     start_frame:
#       strategy: shot
#       shot_id: 1
#
#     prompts:
#       - shot_ref: 1
#         duration: 3
#         # prompt auto-generated from shot 1
#
#       - shot_ref: 2
#         duration: 4
#         # prompt auto-generated from shot 2
#
#     total_duration: 7
#     output_name: "sc03_clip01_entrance"
#
#     continuity:
#       from_clip: null
#       notes: "First clip of scene, fresh start"
```

---

## 4. Auto-Generated Deliverables

### Shot List Markdown

Generated from `{scene_id}_shots.yaml` → `{scene_id}_shots.md`

```markdown
# SC03 Shot List - Storage Room

**Episode**: EP01 - The Binding
**Location**: Naval Compound Storage Room
**Time**: Night
**Estimated Duration**: 45-60s

## Scene Summary
Mars and Jonah's first real conversation. She escapes through the window, leaving him behind.

## Director Notes
- **Pacing**: Establish → Entrance → Reveal → Conversation → Decision → Escape → Reaction
- **Dialogue Strategy**: ADR (silent footage, dialogue added in post)
- **Ambient Sound**: Distant dripping, creaking wood, compound atmosphere

## Characters
| Character | Element | Role |
|-----------|---------|------|
| Mars | @Element1 | Protagonist |
| Jonah | @Element2 | Secondary |

---

## Shots

### Shot 1: Storage Room Atmosphere
| Attribute | Value |
|-----------|-------|
| Type | Establish |
| Shot Type | Wide |
| Duration | 2-3s |
| Characters | None |
| Camera | Static |
| Sound | Distant dripping water, creaking wood |
| Dialogue | None |

**Prompt:**
> Wide establishing shot of cluttered naval storage room interior at night...

---

### Shot 2: Mars Bursts In
| Attribute | Value |
|-----------|-------|
| Type | Entrance |
| Shot Type | Medium |
| Duration | 3-4s |
| Characters | Mars |
| Camera | Static |
| Sound | Door slam, gasping breath |
| Dialogue | None |
| Body Language | Cornered animal, survival mode |

**Prompt:**
> Medium shot, young woman bursts through wooden door...

---
[continues for all shots]
```

---

## 5. Validation Rules

The execution layer should validate:

### Shot List Validation
- [ ] All required fields present
- [ ] `type` is valid enum value
- [ ] `shot_type` is valid enum value
- [ ] `dialogue` is valid enum value
- [ ] `characters` references exist in scene.characters
- [ ] `duration` is parseable
- [ ] `sound` has at least one non-null field
- [ ] `camera.movement` is valid enum value
- [ ] `body_language` is provided if characters non-empty

### Clip Validation
- [ ] `scene_id` matches shot list
- [ ] `characters` are subset of shot list characters
- [ ] `start_frame.shot_id` exists in shot list
- [ ] `prompts[].shot_ref` exists in shot list (if provided)
- [ ] `total_duration` equals sum of prompt durations
- [ ] `continuity.from_clip` references valid clip

### Video Director Validation
- [ ] Scene has at least one `establish` type shot
- [ ] Scene has at least one `reaction` type shot (breathing room)
- [ ] No two consecutive `action` shots (needs breathing room)
- [ ] `dialogue` field present on ALL shots (prevents invented speech)
- [ ] `sound` field present on ALL shots (prevents generic audio)

---

## 6. Directory Structure

```
projects/pirate-romance/
├── PROJECT_CONFIG.yaml
│
├── VISUAL_PRODUCTION/
│   ├── SCHEMA.md                    # This file
│   │
│   ├── shot_lists/
│   │   ├── sc02_shots.yaml
│   │   ├── sc02_shots.md            # Auto-generated
│   │   ├── sc03_shots.yaml
│   │   └── sc03_shots.md            # Auto-generated
│   │
│   ├── clip_definitions/
│   │   ├── sc02_clips.yaml
│   │   ├── sc02_clips.md            # Auto-generated
│   │   ├── sc03_clips.yaml
│   │   └── sc03_clips.md            # Auto-generated
│   │
│   ├── sc02_outputs/
│   │   ├── frames/
│   │   ├── clips/
│   │   └── assembly/
│   │
│   └── sc03_outputs/
│       ├── frames/
│       ├── clips/
│       └── assembly/
│
├── EXPORTS/
│   ├── identity_sheets/
│   ├── hero_shots/
│   ├── location_refs/
│   └── storyboards/
│
└── STORY/
    └── SCRIPTS/
```

---

## 7. Usage Examples

### Generate frames for a scene
```bash
python scripts/production/generate_frames.py \
  --shot-list shot_lists/sc03_shots.yaml \
  --output-dir sc03_outputs/frames
```

### Generate specific shot
```bash
python scripts/production/generate_frames.py \
  --shot-list shot_lists/sc03_shots.yaml \
  --shot 5 \
  --output-dir sc03_outputs/frames
```

### Generate clips
```bash
python scripts/production/generate_clips.py \
  --clips clip_definitions/sc03_clips.yaml \
  --frames-dir sc03_outputs/frames \
  --output-dir sc03_outputs/clips
```

### Generate shot list deliverable
```bash
python scripts/production/generate_deliverable.py \
  --shot-list shot_lists/sc03_shots.yaml \
  --format markdown \
  --output shot_lists/sc03_shots.md
```

### Validate before generation
```bash
python scripts/production/validate.py \
  --shot-list shot_lists/sc03_shots.yaml \
  --clips clip_definitions/sc03_clips.yaml
```
