# Shot List Generator Skill

## Purpose
Convert screenplay scenes into detailed, machine-readable shot specifications that enable automated image generation.

## Trigger
All reference images generated (CHARACTER_REFS, LOCATION_REFS complete).

## Inputs Required
- `SCRIPTS/SCRIPT_EP{{XX}}.md`
- `EP{{XX}}_SCENELIST.md`
- `CANON_DB.json` (with reference paths)
- `STYLEGUIDE_VISUAL.md`

## Outputs Produced
- `SHOT_LIST_EP{{XX}}.json` - Machine-readable shot specifications

## Shot Specification Schema

Each shot contains:

```json
{
  "shot_id": "EP01_SC03_SH02",
  "scene_id": "SC03",
  "shot_number": 2,
  "shot_type": "medium",
  "duration": 4.5,

  "content": {
    "description": "Alice reviews case files while Bob paces nervously",
    "characters": ["ALICE_CHEN", "BOB_MARTINEZ"],
    "character_actions": {
      "ALICE_CHEN": "seated at desk, looking at files",
      "BOB_MARTINEZ": "standing, pacing in background"
    },
    "dialogue": "ALICE: Three connections..."
  },

  "visual": {
    "location": "PRECINCT_BULLPEN",
    "location_area": "alice_desk",
    "time_of_day": "afternoon",
    "lighting": "harsh overhead fluorescent",
    "weather": null,
    "mood": "tense"
  },

  "camera": {
    "shot_type": "medium",
    "angle": "eye_level",
    "movement": "static",
    "focus": "ALICE_CHEN",
    "depth_of_field": "shallow"
  },

  "composition": {
    "framing": "Alice screen left, Bob screen right background",
    "foreground": "case files on desk",
    "background": "evidence board visible",
    "notes": "shallow DoF on Alice, Bob slightly soft"
  },

  "references": {
    "character_refs": [
      "CHARACTER_REFS/ALICE_CHEN/refs/alice_seated_working.png",
      "CHARACTER_REFS/BOB_MARTINEZ/refs/bob_standing_concerned.png"
    ],
    "location_ref": "LOCATION_REFS/PRECINCT_BULLPEN/refs/bullpen_alice_desk.png"
  },

  "audio_cues": ["office ambience", "paper rustling", "footsteps"],

  "generation": {
    "prompt": null,
    "status": "pending",
    "attempts": 0,
    "output_path": null
  }
}
```

## Process

### Step 1: Parse Screenplay

For each scene in SCRIPT_EP{{XX}}.md:
1. Extract scene header (location, time)
2. Identify characters present
3. Break down action beats
4. Note dialogue segments

### Step 2: Determine Shot Coverage

Apply standard coverage patterns:

**Dialogue Scenes**:
- Establishing/master shot
- Medium shots of each speaking character
- Over-shoulder shots for reactions
- Close-ups for emotional beats
- Inserts for important details

**Action Scenes**:
- Wide for geography
- Medium for action clarity
- Close-ups for impact moments
- Inserts for details

**Transition Scenes**:
- Establishing shot
- Character entering/exiting

### Step 3: Create Shot Breakdown

For each scene, list shots in sequence:

1. **Establishing**: Location context
2. **Coverage**: Standard dialogue coverage
3. **Emphasis**: Key emotional/story beats
4. **Details**: Insert shots for props/reactions

### Step 4: Assign Shot Types

From STYLEGUIDE_VISUAL.md shot taxonomy:

| Type | Use Case |
|------|----------|
| establishing | Scene opening, location |
| wide | Full figures, action geography |
| medium | Standard dialogue |
| medium_close | Intimate dialogue |
| close_up | Emotion, reactions |
| extreme_cu | Detail emphasis |
| over_shoulder | Dialogue coverage |
| two_shot | Relationship framing |
| insert | Object/detail |
| pov | Subjective moment |

### Step 5: Map References

For each shot, identify required references:

**Character References**:
- Select closest pose/expression match
- Multiple characters = multiple refs

**Location References**:
- Match location + area
- Match time of day
- Match weather if applicable

### Step 6: Define Composition

For each shot, specify:
- Character positions (screen left/right)
- Foreground elements
- Background elements
- Focus point
- Depth of field

### Step 7: Estimate Durations

Based on:
- Dialogue length (words → seconds)
- Action complexity
- Emotional weight
- Pacing requirements

Typical durations:
- Establishing: 2-4 seconds
- Dialogue medium: 3-8 seconds
- Close-up reaction: 1-3 seconds
- Insert: 1-2 seconds

### Step 8: Generate Shot IDs

Format: `EP{{XX}}_SC{{XX}}_SH{{XX}}`

- EP: Episode number (2 digits)
- SC: Scene number (2 digits)
- SH: Shot number within scene (2 digits)

### Step 9: Compile Shot List

Create `SHOT_LIST_EP{{XX}}.json`:

```json
{
  "meta": {
    "episode": "EP01",
    "total_shots": 127,
    "total_duration": 2520,
    "generated": "2026-01-25T10:30:00Z"
  },
  "shots": [
    { ... },
    { ... }
  ]
}
```

### Step 10: Validate

Check:
- [ ] All scenes have coverage
- [ ] All characters have references mapped
- [ ] All locations have references mapped
- [ ] Durations sum to episode length
- [ ] Shot IDs are unique
- [ ] No orphan references

## Coverage Guidelines

### Minimum Coverage Per Scene

**2-Person Dialogue**:
- 1 establishing/master
- 2 medium singles
- 2 over-shoulders
- 2-4 close-ups

**Group Scene (3+)**:
- 1 establishing/master
- Medium of each speaker
- Select OTS for key exchanges
- Close-ups for pivotal moments

**Solo Scene**:
- 1 establishing
- 1-2 mediums
- Close-ups for internal moments
- Inserts as needed

### When to Add More Coverage

- High emotion scenes
- Plot-critical reveals
- Character transformation moments
- Action sequences

### When to Use Less Coverage

- Transitional scenes
- Simple information transfer
- Montage sequences

## Notes

- Shot list is INPUT for shot-image-generator
- Prompts are generated by shot-image-generator, not here
- References must exist before shot list can be complete
- Duration estimates guide pacing, not strict requirements
- Coverage can be adjusted during generation phase
