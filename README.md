# AI Video Story Generation System - Project Context

**Project Goal**: Build a modular Claude Skills-based system for autonomous AI video story generation, targeting a full 20-30 minute episode from sparse user requirements.

**Development Approach**: Incremental, community-driven development via GitHub. The system will be built in Claude Code and shared openly for iteration.

**Key Technical Decision**: Reference-based visual consistency using **Google Nano Banana Pro** for image generation (not LoRAs), with **Kling/Veo 3.1 Fast** for video animation.

---

## Milestone Targets

### v0.1 - Story Foundation ✅ TARGET
**Deliverable**: Complete pilot script + story bible from 8-10 user questions
**Skills**: story-intake, logline-architect, character-architect, story-architect, screenplay-writer, dialogue-doctor, story-critic, bible-keeper

### v0.2 - Complete Image Assets ✅ YOUR FOCUS
**Deliverable**: All reference images + shot images generated
**Skills**: Add visual-canon-keeper, character/location/prop-reference-generators, shot-list-generator, shot-image-generator, quality validators

### v0.3 - Scene Generation (Future)
**Deliverable**: 2-3 minute animated scene with audio
**Skills**: Add video-animation, audio-generation, assembly tools

### v1.0+ - Full Episode (Aspirational)
**Requires**: Breakthroughs in consistency, 6-12+ months of iteration

---

## Technical Stack

### Visual Generation
- **Image Generation**: Google Nano Banana Pro (fal.ai/recraft-v3)
  - Reference-based consistency (no LoRA training needed)
  - Reference weight: 0.85-0.95 for character/location consistency
- **Video Animation**: Kling or Veo 3.1 Fast (image-to-video)
- **Workflow**: Generate reference library → Generate shot images → Animate shots

### Audio Pipeline
- **Priority**: Medium (v0.3+)
- **Future**: Segment Audio (vocal isolation), voice-to-voice (consistency), separate SFX integration
- **Short-term**: Generated soundtracks + manual editing

### Primary Development Environment
- **Claude Code** (local development)
- **fal.ai API** for media generation
- **GitHub** for community sharing and iteration

---

## Core Architecture Philosophy

### Skills vs Agents
**Key Distinction**: Claude Skills are *instruction sets* that Claude reads and follows, not separate autonomous agents. We design for **workflows** and **artifact types**, not agent roles.

### Modular Design Principles
1. **Clear Dependencies**: Each skill declares what it needs and what it produces
2. **Testable Deliverables**: Every skill has concrete output files
3. **Quality Gates**: Validation points between phases
4. **Community-Friendly**: Skills can be improved independently

### Critical Insight: Reference-Based Pipeline
The workflow is fundamentally different from prompt-only approaches:

```
Story → Character/Location Definitions → Reference Library → Shot Images → Video
```

Each stage uses the previous stage's outputs as **reference inputs**, not just text descriptions.

---

## Skills Architecture

### Phase 1: Story Foundation (v0.1)

#### 1. `story-intake/`
- **Output**: `CREATIVE_BRIEF.md` + `POWER_STACK.md`
- **Purpose**: 8-10 question interview → autonomous story development
- **Special**: Includes visual style keywords for image generation

#### 2. `logline-architect/`
- **Output**: `LOGLINE_LOCK.md`
- **Purpose**: Generate + tournament-select loglines using verbalized sampling
- **Quality Gate**: Must include protagonist flaw + relationship stake + consequence

#### 3. `character-architect/`
- **Output**: `CHARACTER_SHEETS/*.md` + `RELATIONSHIP_MAP.json`
- **Purpose**: Deep character psychology + relationship matrix
- **Key Feature**: Relationship axes (trust, respect, dependency, intimacy, moral alignment)
- **Special**: Physical descriptions optimized for image generation

#### 4. `story-architect/`
- **Output**: `EP##_BEATS.md` + `EP##_SCENELIST.md`
- **Purpose**: Episode structure with TV pacing
- **Special**: Location tags + character presence per scene for reference planning

#### 5. `screenplay-writer/`
- **Output**: `SCRIPT_EP##.md`
- **Purpose**: Industry-standard markdown screenplay
- **Special**: Scene headers with visual metadata (time, weather, mood)

#### 6. `dialogue-doctor/`
- **Output**: Revised `SCRIPT_EP##.md`
- **Purpose**: Voice, subtext, status games
- **Key Feature**: Character linguistic fingerprints, anti-exposition

#### 7. `story-critic/`
- **Output**: `CRITIQUE_REPORT.md`
- **Purpose**: Quality gate with veto power
- **Key Feature**: Numeric rubrics, anti-cliché detection

#### 8. `bible-keeper/`
- **Output**: `SHOW_BIBLE.md` + version log
- **Purpose**: Living document consolidating all story artifacts

---

### Phase 2: Reference Library (v0.2a)

#### 9. `canon-database-manager/`
- **Output**: `CANON_DB.json`
- **Purpose**: Machine-readable source of truth
- **Contents**: Characters, locations, props, factions, visual anchors, reference registry
- **Schema**: See detailed schema below

#### 10. `visual-style-guide/`
- **Output**: `STYLEGUIDE_VISUAL.md`
- **Purpose**: Define show's visual language
- **Contents**: Global aesthetic, shot taxonomy, consistency rules, negative prompts

#### 11. `character-reference-generator/`
- **Output**: `CHARACTER_REFS/{NAME}/VISUAL_SPEC.md` + `refs/*.png`
- **Purpose**: Generate character reference pack
- **Reference Types**:
  - Turnaround: front, 3/4, profile, back (neutral)
  - Expression pack: happy, sad, angry, surprised, neutral
  - Outfit variants: primary + 2-3 alternates
  - Action poses: 3-5 key poses from script
  - Close-ups: face detail shots
- **Workflow**: Generate seed → use as reference for variants

#### 12. `location-reference-generator/`
- **Output**: `LOCATION_REFS/{LOCATION}/VISUAL_SPEC.md` + `refs/*.png`
- **Purpose**: Generate location reference pack
- **Reference Types**:
  - Establishing shot (wide)
  - Key areas (3-5 sub-locations/angles)
  - Time variants (day, night, golden hour)
  - Weather variants (if needed)
  - Empty + populated versions

#### 13. `prop-reference-generator/`
- **Output**: `PROP_REFS/{PROP}/refs/*.png`
- **Purpose**: Generate signature props/objects
- **Reference Types**: Different angles, in-hand vs on-surface, detail close-ups

---

### Phase 3: Shot Production (v0.2b)

#### 14. `shot-list-generator/`
- **Output**: `SHOT_LIST_EP##.json` (machine-readable)
- **Purpose**: Convert screenplay → detailed shot specifications
- **Contents**: shot_id, scene_id, shot_type, duration, characters, location, visual_prompt, character_refs, location_ref, camera, composition_notes, audio_cues

#### 15. `shot-image-generator/`
- **Output**: `SHOTS_EP##/{shot_id}.png`
- **Purpose**: Generate final shot images using references
- **Workflow**:
  1. Load shot spec from JSON
  2. Retrieve character + location references
  3. Construct Nano Banana Pro prompt with references
  4. Generate shot image
  5. Store with metadata

#### 16. `shot-quality-validator/`
- **Output**: `SHOT_QA_REPORT_EP##.md`
- **Purpose**: QA pass on generated shots
- **Checks**: Reference consistency, composition, lighting/style, anatomical errors
- **Action**: Flags shots for regeneration

#### 17. `visual-continuity-validator/`
- **Output**: `VISUAL_QA_REPORT.md`
- **Purpose**: Check visual consistency across all shots
- **Action**: Identifies drift, enforces visual canon

#### 18. `reference-library-updater/`
- **Output**: Updated reference images + CANON_DB updates
- **Purpose**: Improve reference library based on successful shots
- **Workflow**: Extract exceptional shots as new references, track best performers

---

### Phase 4: Quality & Iteration

#### 19. `continuity-validator/`
- **Output**: `CONTINUITY_REPORT.md`
- **Purpose**: Cross-check all artifacts for story contradictions
- **Priority**: v0.2 (before shot generation)

---

### Meta/Orchestration

#### 20. `workflow-orchestrator/`
- **Output**: Execution plan, progress tracking, gate management
- **Purpose**: Master controller for full pipeline

---

## Skill Dependencies & Workflow

```
PHASE 1 (Story Foundation - v0.1)
┌─────────────────┐
│ story-intake    │
└────────┬────────┘
         │
         ├──────────────────┬──────────────────┐
         │                  │                  │
┌────────▼────────┐  ┌─────▼──────┐  ┌────────▼────────┐
│ logline-        │  │ character- │  │ bible-keeper    │
│ architect       │  │ architect  │  │ (continuous)    │
└────────┬────────┘  └─────┬──────┘  └─────────────────┘
         │                  │
         └─────────┬────────┘
                   │
           ┌───────▼────────┐
           │ story-         │
           │ architect      │
           └───────┬────────┘
                   │
           ┌───────▼────────┐
           │ screenplay-    │
           │ writer         │
           └───────┬────────┘
                   │
           ┌───────▼────────┐
           │ dialogue-      │
           │ doctor         │
           └───────┬────────┘
                   │
           ┌───────▼────────┐
           │ story-critic   │
           └────────────────┘

PHASE 2 (Reference Library - v0.2a)
┌─────────────────────────────┐
│ All Phase 1 artifacts ready │
└──────────────┬──────────────┘
               │
      ┌────────┴────────┐
      │                 │
┌─────▼──────┐  ┌──────▼──────────┐
│ canon-     │  │ visual-style-   │
│ database-  │  │ guide           │
│ manager    │  │                 │
└─────┬──────┘  └──────┬──────────┘
      │                │
      ├────────────────┼─────────────────┐
      │                │                 │
┌─────▼────────┐ ┌────▼─────────┐ ┌────▼─────────┐
│ character-   │ │ location-    │ │ prop-        │
│ reference-   │ │ reference-   │ │ reference-   │
│ generator    │ │ generator    │ │ generator    │
└──────────────┘ └──────────────┘ └──────────────┘

PHASE 3 (Shot Production - v0.2b)
┌─────────────────────────────┐
│ All references generated    │
└──────────────┬──────────────┘
               │
       ┌───────▼────────┐
       │ shot-list-     │
       │ generator      │
       └───────┬────────┘
               │
       ┌───────▼────────┐
       │ shot-image-    │
       │ generator      │◄──────┐
       └───────┬────────┘       │
               │                │
       ┌───────▼────────┐       │
       │ shot-quality-  │       │
       │ validator      │───────┘ (regeneration loop)
       └───────┬────────┘
               │
       ┌───────▼────────┐
       │ visual-        │
       │ continuity-    │
       │ validator      │
       └────────────────┘
```

---

## Recommended File Structure

```
/ai-video-story-gen/
├── README.md
├── ARCHITECTURE.md              # This document
├── CONTRIBUTING.md
│
├── skills/
│   ├── core/                    # Story development skills
│   │   ├── story-intake/
│   │   │   ├── SKILL.md
│   │   │   ├── templates/
│   │   │   │   ├── CREATIVE_BRIEF_template.md
│   │   │   │   └── POWER_STACK_template.md
│   │   │   └── examples/
│   │   ├── logline-architect/
│   │   │   ├── SKILL.md
│   │   │   ├── templates/
│   │   │   └── examples/
│   │   ├── character-architect/
│   │   │   ├── SKILL.md
│   │   │   ├── templates/
│   │   │   │   ├── CHARACTER_SHEET_template.md
│   │   │   │   └── RELATIONSHIP_MAP_template.json
│   │   │   └── examples/
│   │   ├── story-architect/
│   │   ├── screenplay-writer/
│   │   ├── dialogue-doctor/
│   │   ├── story-critic/
│   │   └── bible-keeper/
│   │
│   ├── production/              # Visual development skills
│   │   ├── canon-database-manager/
│   │   │   ├── SKILL.md
│   │   │   ├── templates/
│   │   │   │   └── CANON_DB_schema.json
│   │   │   └── examples/
│   │   ├── visual-style-guide/
│   │   ├── character-reference-generator/
│   │   │   ├── SKILL.md
│   │   │   ├── prompts/
│   │   │   │   ├── README.md
│   │   │   │   ├── turnaround.txt
│   │   │   │   ├── expressions.txt
│   │   │   │   ├── outfits.txt
│   │   │   │   └── action_poses.txt
│   │   │   ├── templates/
│   │   │   │   └── CHARACTER_VISUAL_SPEC_template.md
│   │   │   ├── examples/
│   │   │   │   └── alice_chen_example/
│   │   │   │       ├── VISUAL_SPEC.md
│   │   │   │       └── refs/
│   │   │   └── config/
│   │   │       └── fal_api_settings.json
│   │   ├── location-reference-generator/
│   │   │   ├── SKILL.md
│   │   │   ├── prompts/
│   │   │   │   ├── establishing_shot.txt
│   │   │   │   ├── key_areas.txt
│   │   │   │   └── time_variants.txt
│   │   │   └── ...
│   │   ├── prop-reference-generator/
│   │   ├── shot-list-generator/
│   │   ├── shot-image-generator/
│   │   ├── shot-quality-validator/
│   │   ├── visual-continuity-validator/
│   │   └── reference-library-updater/
│   │
│   └── meta/                    # System management skills
│       ├── workflow-orchestrator/
│       └── continuity-validator/
│
├── references/                  # Cross-skill reference materials
│   ├── visual_consistency/
│   │   ├── nano_banana_pro_best_practices.md
│   │   ├── reference_based_generation.md
│   │   └── common_pitfalls.md
│   ├── story_structure/
│   │   ├── tv_pacing_rules.md
│   │   ├── relationship_arc_patterns.md
│   │   └── beat_sheet_examples.md
│   └── style_guides/
│       ├── cinematography_reference.md
│       └── color_theory_for_ai.md
│
├── scripts/                     # Helper utilities
│   ├── batch_generation.py
│   ├── reference_validator.py
│   └── fal_api_wrapper.py
│
├── tests/
│   ├── test_character_consistency/
│   └── test_canon_validation/
│
└── examples/                    # Complete worked examples
    └── sample-project/
        ├── SHOW_BIBLE.md
        ├── CANON_DB.json
        ├── CREATIVE_BRIEF.md
        ├── CHARACTER_SHEETS/
        ├── SCRIPTS/
        ├── CHARACTER_REFS/
        ├── LOCATION_REFS/
        ├── SHOT_LIST_EP01.json
        └── SHOTS_EP01/
```

---

## CANON_DB.json Schema (Detailed)

This is the machine-readable source of truth optimized for Claude retrieval:

```json
{
  "meta": {
    "show_title": "Project Chimera",
    "version": "1.2.3",
    "last_updated": "2026-01-25T10:30:00Z",
    "knowledge_cutoff": "EP01_SHOT_GENERATION"
  },
  
  "characters": {
    "ALICE_CHEN": {
      "full_name": "Alice Chen",
      "role": "protagonist",
      "age": 32,
      "archetype": "brilliant_but_damaged",
      
      "psychology": {
        "want": "to solve the impossible case",
        "need": "to trust others again",
        "lie": "emotions make you weak",
        "wound": "partner's death",
        "virtue_with_cost": "obsessive attention to detail"
      },
      
      "visual": {
        "locked": true,
        "description": "Asian woman, athletic build, 5'7\", short black hair with one silver streak, sharp cheekbones, tired dark eyes, small scar on left eyebrow",
        "signature_outfit": "charcoal blazer, white shirt, dark jeans, black boots",
        "color_palette": ["charcoal", "steel_blue", "deep_red"],
        "signature_prop": "worn leather notebook",
        "negative_prompts": ["smiling easily", "casual posture", "bright colors"],
        
        "reference_images": {
          "front_neutral": "CHARACTER_REFS/ALICE_CHEN/refs/alice_front_neutral.png",
          "34_neutral": "CHARACTER_REFS/ALICE_CHEN/refs/alice_34_neutral.png",
          "profile_neutral": "CHARACTER_REFS/ALICE_CHEN/refs/alice_profile_neutral.png",
          "expression_determined": "CHARACTER_REFS/ALICE_CHEN/refs/alice_determined.png",
          "expression_vulnerable": "CHARACTER_REFS/ALICE_CHEN/refs/alice_vulnerable.png",
          "outfit_primary": "CHARACTER_REFS/ALICE_CHEN/refs/alice_outfit_primary.png"
        }
      },
      
      "voice": {
        "sentence_length": "medium_short",
        "metaphor_domain": "chess_strategy",
        "sarcasm_level": 7,
        "directness": 9,
        "taboo_topics": ["her partner's death", "romantic relationships"],
        "linguistic_fingerprints": [
          "uses precise technical language",
          "deflects with dark humor",
          "rarely uses contractions when emotional"
        ]
      },
      
      "relationships": {
        "BOB_MARTINEZ": {
          "axes": {
            "trust": -2,
            "respect": 4,
            "dependency": 1,
            "intimacy": -3,
            "moral_alignment": 3
          },
          "bond_mechanism": "shared obsession with truth",
          "pressure_mechanism": "Alice's refusal to open up",
          "private_language": ["the board", "ghost hunting"],
          "arc_direction": "trust +3 over season, intimacy +4"
        }
      }
    }
  },
  
  "locations": {
    "PRECINCT_BULLPEN": {
      "type": "recurring",
      "description": "Large open office with rows of desks, harsh fluorescent lighting, evidence boards on walls, coffee station in corner, large windows with city view",
      "mood": "gritty_functional",
      "locked": true,
      
      "visual": {
        "time_variants": ["morning_golden", "afternoon_harsh", "night_fluorescent"],
        "key_areas": [
          "Alice's desk - corner, covered in files",
          "Evidence board - main wall, red string",
          "Coffee station - battered machine, stained mugs",
          "Captain's office - glass walls, visible from bullpen"
        ],
        "color_palette": ["industrial_gray", "institutional_beige", "fluorescent_white"],
        "lighting_signature": "overhead harsh + desk lamps",
        "negative_prompts": ["modern tech", "clean surfaces", "warm lighting"],
        
        "reference_images": {
          "establishing_wide_day": "LOCATION_REFS/PRECINCT_BULLPEN/refs/bullpen_wide_day.png",
          "alice_desk_closeup": "LOCATION_REFS/PRECINCT_BULLPEN/refs/alice_desk.png",
          "evidence_board": "LOCATION_REFS/PRECINCT_BULLPEN/refs/evidence_board.png",
          "coffee_station": "LOCATION_REFS/PRECINCT_BULLPEN/refs/coffee_station.png"
        }
      },
      
      "blocking_rules": [
        "Alice's desk is always back-left corner",
        "Evidence board dominates main wall",
        "Natural traffic flow leaves space for two-shots at Alice's desk"
      ]
    }
  },
  
  "props": {
    "ALICE_NOTEBOOK": {
      "type": "signature",
      "owner": "ALICE_CHEN",
      "description": "Worn leather-bound notebook, pages filled with precise handwriting and sketches, frayed bookmark",
      "significance": "Contains all her case notes, never lets it out of sight",
      
      "visual": {
        "locked": true,
        "reference_images": {
          "closed": "PROP_REFS/ALICE_NOTEBOOK/refs/notebook_closed.png",
          "open_writing": "PROP_REFS/ALICE_NOTEBOOK/refs/notebook_open.png",
          "in_hand": "PROP_REFS/ALICE_NOTEBOOK/refs/notebook_hand.png"
        }
      }
    }
  },
  
  "visual_style": {
    "global_aesthetic": "neo_noir_procedural",
    "color_grading": "desaturated_with_blue_shadows",
    "lighting_style": "naturalistic_motivated",
    "lens_language": "cinema_35mm_shallow_dof",
    "camera_movement": "mostly_static_deliberate_movement",
    
    "shot_taxonomy": {
      "establishing": "wide shot showing location context",
      "medium": "waist-up, primary dialogue framing",
      "close_up": "face/emotion emphasis",
      "insert": "object/detail focus",
      "over_shoulder": "conversation dynamics",
      "two_shot": "relationship framing"
    }
  },
  
  "factions": {
    "PRECINCT_72": {
      "description": "Understaffed, underfunded precinct in the industrial district",
      "members": ["ALICE_CHEN", "BOB_MARTINEZ", "CAPT_REYES"],
      "values": ["results_over_protocol", "loyalty_to_squad"],
      "conflict_with": ["INTERNAL_AFFAIRS", "CITY_HALL"]
    }
  },
  
  "canon_facts": [
    "Alice's partner died 18 months before pilot",
    "Bob has a daughter in college",
    "The precinct is scheduled for closure in 6 months",
    "Alice and Bob have worked together for 9 months"
  ],
  
  "continuity_log": [
    {
      "date": "2026-01-20",
      "change": "Added Bob's daughter detail",
      "affected_artifacts": ["CHARACTER_SHEETS/BOB_MARTINEZ.md", "SCRIPT_EP01.md"],
      "reason": "Adds personal stakes to precinct closure"
    }
  ]
}
```

---

## Shot Specification Format

From `SHOT_LIST_EP##.json`:

```json
{
  "shot_id": "EP01_SC03_SH02",
  "scene_id": "SC03",
  "shot_type": "medium",
  "duration": 4.5,
  "characters": ["ALICE", "BOB"],
  "location": "PRECINCT_BULLPEN",
  "time_of_day": "afternoon",
  "description": "Alice reviews case files while Bob paces nervously",
  "visual_prompt": "{detailed prompt constructed by shot-image-generator}",
  "character_refs": [
    "CHARACTER_REFS/ALICE/refs/ALICE_front_neutral.png",
    "CHARACTER_REFS/BOB/refs/BOB_34_concerned.png"
  ],
  "location_ref": "LOCATION_REFS/PRECINCT_BULLPEN/refs/bullpen_wide_day.png",
  "camera": "medium_shot",
  "composition_notes": "Alice screen left, Bob screen right, depth of field on Alice",
  "audio_cues": ["office ambience", "paper rustling", "footsteps"]
}
```

---

## Prompt Template Structure

Example from `character-reference-generator/prompts/turnaround.txt`:

```
# CHARACTER TURNAROUND - NEUTRAL POSE
# Use for: Initial reference generation (no prior images)
# Model: Nano Banana Pro / recraft-v3
# Tested: 2026-01-25

## BASE PROMPT TEMPLATE

{{CHARACTER_DESCRIPTION}}, character design reference sheet, turnaround view showing front view, 3/4 view, side profile, and back view, {{OUTFIT_DESCRIPTION}}, neutral standing pose, neutral expression, clean white background, professional character sheet layout, even lighting, {{STYLE_KEYWORDS}}

## NEGATIVE PROMPT

multiple characters, dynamic pose, smiling, dramatic expression, props in hand, shadows, colored background, photography, realistic photo, {{CHARACTER_NEGATIVE_PROMPTS}}

## RECOMMENDED SETTINGS

- Aspect ratio: 16:9 (for 4-panel layout)
- Steps: 28
- Guidance: 3.5
- Safety tolerance: 2

## SUBSTITUTION VARIABLES

- {{CHARACTER_DESCRIPTION}}: From CHARACTER_SHEETS/{NAME}.md → visual.description
- {{OUTFIT_DESCRIPTION}}: From CHARACTER_SHEETS/{NAME}.md → visual.signature_outfit
- {{STYLE_KEYWORDS}}: From STYLEGUIDE_VISUAL.md → global_aesthetic
- {{CHARACTER_NEGATIVE_PROMPTS}}: From CHARACTER_SHEETS/{NAME}.md → visual.negative_prompts
```

---

## How Skills Reference Prompts

In the SKILL.md file:

```markdown
## Step 3: Generate Turnaround Images

Load the proven prompt template:
```
view /mnt/skills/user/character-reference-generator/prompts/turnaround.txt
```

Customize the template by inserting:
- Character physical description from `CHARACTER_SHEETS/{NAME}.md`
- Visual anchors from `CANON_DB.json`
- Global style keywords from `STYLEGUIDE_VISUAL.md`

Call fal.ai with customized prompt using settings from `config/fal_api_settings.json`
```

---

## fal.ai Configuration

Example from `config/fal_api_settings.json`:

```json
{
  "nano_banana_pro": {
    "endpoint": "fal-ai/recraft-v3",
    "default_params": {
      "image_size": {
        "width": 1024,
        "height": 1024
      },
      "num_inference_steps": 28,
      "guidance_scale": 3.5,
      "num_images": 1,
      "safety_tolerance": "2",
      "output_format": "png"
    },
    "reference_mode_params": {
      "style_reference_weight": 0.85,
      "character_reference_weight": 0.95
    }
  },
  "kling": {
    "endpoint": "fal-ai/kling-video/v1/standard/image-to-video",
    "default_params": {
      "duration": "5",
      "aspect_ratio": "16:9"
    }
  }
}
```

---

## Power Stack (Story Structure Framework)

Default for relationship-focused stories:

1. **4–6 Act TV Structure** - pacing, act-outs
2. **Want/Need/Lie** - internal character engine
3. **Relationship Arc Matrix** - tracked over episodes (axes: trust, respect, dependency, intimacy, moral alignment)
4. **Scene Design: Goal / Obstacle / Turn / Cost** - prevents mushy scenes
5. **Dialogue System: Subtext + Status + Private Language** - anti-cliché
6. **Theme Argument** - central question for coherence

---

## Minimal Intake Questions (8-10 Only)

When ready, the system asks exactly these and then stops:

1. Genre + 2 comps + 1 anti-comp
2. Protagonist: what are they great at / what ruins their relationships?
3. Who do they need most, and why do they push them away?
4. Series engine: what creates a new episode problem each week?
5. Central theme question (one sentence)
6. Tone guardrails (rating, comedy level, violence level)
7. Setting & aesthetic keywords (5–10)
8. Season endpoint: what must be irrevocably different by finale?

---

## Quality Gates

### Gate 0 (Intake)
- No more user questions unless contradictions exist

### Gate 1 (Logline)
- Must include: protagonist + flaw, relationship stake, irreversible consequence

### Gate 2 (Characters)
- Every major character must:
  - Cause at least one problem in the pilot
  - Have one surprising competency
  - Have one relationship they're actively failing

### Gate 3 (Visual Bible)
- "Consistency Contract":
  - Fixed descriptors that must appear in every prompt
  - Banned descriptors that cause drift
  - ID tags for characters/locations for prompt reuse

### Gate 4 (Episode Structure)
- Relationship evolution must be visible:
  - At least 2 relationship "ticks" on axes per episode

### Gate 5 (Screenplay)
- Table read simulation (agent):
  - Summarize what viewer thinks each character wants after each act
  - If unclear → rewrite scenes, not notes

### Gate 6 (Season Grid)
- Each episode must:
  - Stress a different relationship pair
  - Advance at least one season-long mystery/pressure
  - Deliver a "promise of premise" set piece

---

## Critical Missing Pieces (Future Development)

### Audio Pipeline (v0.3+)
- `audio-design/` skill - music cues, SFX, ambience
- `dialogue-casting/` skill - voice matching, ElevenLabs integration

### Advanced Visual Consistency (v0.3+)
- `reference-pipeline/` skill - img2img workflows
- `lora-training-prep/` skill - dataset prep for character LoRAs (if needed)

### Editing & Assembly (v0.3+)
- `edit-list-generator/` skill - timing, cuts, transitions
- `assembly-integration/` skill - FFmpeg commands, DaVinci Resolve XML

### Iteration Framework (v0.2+)
- `shot-regeneration/` skill - targeted fixes
- `continuity-fix/` skill - repair canon violations

---

## Implementation Priority

### Weeks 1-2: Phase 1 Skills (v0.1 milestone)
Build and test:
1. story-intake
2. logline-architect
3. character-architect
4. story-architect
5. screenplay-writer
6. bible-keeper

**Deliverable**: Complete pilot script + bible from 8-10 questions

### Weeks 3-4: Phase 2a Skills (v0.2a partial)
7. visual-canon-keeper
8. character-reference-generator
9. location-reference-generator
10. shot-list-generator

**Deliverable**: Complete visual reference pack + shot list

### Weeks 5-6: Phase 2b Skills (v0.2 COMPLETE)
11. shot-image-generator
12. reference-pipeline (img2img)
13. shot-quality-validator
14. visual-continuity-validator

**Deliverable**: All shot images generated with references

### Weeks 7-8: Quality Layer (v0.2 refinement)
15. dialogue-doctor
16. story-critic
17. continuity-validator
18. reference-library-updater

**Deliverable**: High-quality, consistent shot library ready for animation

---

## Next Steps for Claude Code Development

### Immediate Actions:

1. **Create directory structure** following the layout above
2. **Start with story-intake/SKILL.md** - this is the entry point
3. **Build and test incrementally** - don't try to create all skills at once
4. **Use real examples** - create a sample project as you build
5. **Document as you go** - capture what works and what doesn't

### First Skill to Build: `story-intake/`

This should:
- Ask the 8-10 minimal questions
- Generate CREATIVE_BRIEF.md
- Generate POWER_STACK.md
- Include visual style keywords for later image generation
- Have clear examples

### Testing Strategy:

- Create `/examples/test-project-noir/` as first test case
- Run through story-intake with a simple noir detective show
- Verify outputs match templates
- Use this to validate the skill works before building next skill

### Community Sharing:

- Push to GitHub after each working skill
- Include clear README with:
  - What works
  - What doesn't
  - How to test
  - Known limitations
- Encourage community to test and provide feedback

---

## Key Design Decisions Summary

1. **Reference-based over prompt-only** - Nano Banana Pro with reference images
2. **Incremental milestones** - v0.1 (script), v0.2 (images), v0.3 (scene)
3. **Skills not agents** - Claude reads instructions, doesn't orchestrate separate LLMs
4. **Quality gates** - Explicit validation between phases
5. **Community-driven** - Open source, GitHub, iterative improvement
6. **Realistic scope** - Full episode is aspirational, focus on achievable steps

---

## Technical Constraints & Realities

### What Works Now:
- Story generation (strong)
- Character/world building (strong)
- Reference image generation (good with iteration)
- Single shot generation (achievable)

### What Needs Iteration:
- Visual consistency across shots (challenging)
- Shot-to-shot continuity (requires refinement)
- Character expression consistency (needs good references)

### What's Aspirational:
- Full 20-30 min episode automation (6-12+ months)
- Perfect visual consistency (requires tech breakthroughs)
- Audio integration at scale (needs better tools)

---

## Success Metrics

### v0.1 Success:
- Can generate complete, coherent pilot script
- Characters have depth and contradictions
- Dialogue sounds natural and distinct
- Story structure follows TV conventions
- All in < 30 minutes from intake

### v0.2 Success:
- Reference library maintains character identity
- Shot images reference library effectively
- Visual consistency > 80% acceptable on first pass
- Can generate all shots for pilot in < 2 hours
- Regeneration workflow improves quality

### v1.0 Success (Future):
- Can generate 10-12 minute coherent sequence
- Visual continuity requires < 10% manual fixes
- Audio integration is semi-automated
- Community has contributed improvements
- System is used by others successfully

---

## Resources & References

### Technical Documentation:
- fal.ai API docs: https://fal.ai/docs
- Nano Banana Pro (recraft-v3): fal.ai/models/recraft-v3
- Kling video: fal.ai/models/kling-video
- Veo 3.1: (endpoint TBD)

### Story Structure:
- Save the Cat methodology
- TV writing beat sheets
- Relationship arc systems

### Visual Consistency:
- Reference-based generation techniques
- IP adapter methodologies
- Shot matching approaches

---

## Contact & Contribution

- **Primary Developer**: Kaigani
- **Platform**: GitHub (repo URL TBD)
- **Development Environment**: Claude Code
- **Community**: Open for contributions after v0.1 release

---

## Document Version

- **Version**: 1.0
- **Date**: 2026-01-25
- **Status**: Initial architecture specification
- **Next Review**: After v0.1 milestone completion

---

This document captures the complete architecture and technical decisions from the planning conversation. Use this as the foundation for building the Claude Skills system in Claude Code.
