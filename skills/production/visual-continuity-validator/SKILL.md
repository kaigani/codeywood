---
name: visual-continuity-validator
description: "Validates visual consistency across all shots in an episode by analyzing character, location, scene, and style continuity threads. Detects progressive, sudden, and pattern drift and generates a prioritized correction report. Use when shot quality validation is complete for an episode and cross-shot consistency needs verification."
---

# Visual Continuity Validator

Check visual consistency across all shots in an episode, identifying drift patterns and enforcing visual canon. Produces a prioritized report with regeneration recommendations.

## Inputs

- `SHOTS_EP{{XX}}/*.png` — all generated episode shots
- `SHOT_LIST_EP{{XX}}.json` — shot specifications with character/location references
- `SHOT_QA_REPORT_EP{{XX}}.md` — individual shot QA results
- `CANON_DB.json` — visual canon (locked descriptions, negative prompts)
- `CHARACTER_REFS/*/refs/*.png` — character reference images

## Outputs

- `VISUAL_CONTINUITY_REPORT_EP{{XX}}.md` — scored report with drift alerts and correction recommendations

## Process

### Step 1: Group Shots into Threads

Organize all episode shots into three analysis threads:

- **Scene thread**: shots sharing location + continuous time
- **Character thread**: all appearances of each character across the episode
- **Location thread**: all shots at each location regardless of scene

### Step 2: Character Thread Analysis

For each character, collect all shots and compare sequentially:

| Check | Within Scene | Across Scenes (Same Day) | Across Episode |
|-------|-------------|-------------------------|----------------|
| Face features | Identical | Consistent | Recognizable |
| Hair | Identical | Consistent | Consistent |
| Outfit | Identical | Can change if justified | Flexible |
| Body proportions | Identical | Consistent | Consistent |

Flag inconsistencies as drift events with shot IDs and severity.

### Step 3: Scene Thread Analysis

For each scene, verify internal cohesion:

- Lighting angle and color temperature stay consistent between shots
- Props and furniture maintain position (no unexplained movement)
- Character spatial positions follow logical blocking
- Background elements remain stable

### Step 4: Location Thread Analysis

For each location appearing in multiple scenes, compare architectural elements, key features (windows, furniture), and wall/surface colors across all shots. Verify time-of-day rendering matches the shot list specifications.

### Step 5: Drift Detection

Classify detected issues into three drift types:

- **Progressive drift**: character or location slowly changes over the episode (compare first vs. last appearance)
- **Sudden drift**: abrupt change between adjacent shots (sequential comparison)
- **Pattern drift**: consistent error across multiple shots (compare against locked reference images)

### Step 6: Generate Report

Write `VISUAL_CONTINUITY_REPORT_EP{{XX}}.md` with:

- **Summary scores** (0–100) for overall continuity, characters, locations, scenes, and style
- **Critical issues** with affected shot IDs, description, and recommended action (regenerate, update refs)
- **Drift patterns** showing each character/location's consistency timeline
- **Prioritized corrections**: Critical (breaks story clarity) → High (noticeable distraction) → Medium (visible but not distracting) → Low (acceptable variance)

### Step 7: Flag Reference Updates

If generated shots are consistently better than references, flag those improvements for the reference-library-updater skill to incorporate.

## End-of-Clip Continuity (Video Production)

When validating video clips (not just still shots), continuity must also be checked BETWEEN clips:

1. Extract last frame: `ffmpeg -sseof -1 -i clip.mp4 -update 1 -q:v 2 last_frame.png`
2. Review the extracted frame for character position, state, and expression
3. Decide: **Continue** (flows naturally) → **Bridge clip** (gap needs transitional video) → **New start frame** (new location or major change)

Bridge clips use the extracted last frame as their start frame and prompt a transition TO the next clip's expected state.

## Notes

- Perfect continuity is impossible with current AI generation — focus on character recognition and scene-level cohesion
- Progressive drift is harder to catch than sudden drift; always compare first vs. last appearance
- Scene boundaries naturally hide more variance than within-scene cuts
- Strict continuity rules apply within scenes; flexibility increases across scenes and across the episode
