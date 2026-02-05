# Visual Continuity Validator Skill

## Purpose
Check visual consistency across all shots in an episode, identifying drift patterns and enforcing visual canon.

## Trigger
Shot quality validation complete for episode.

## Inputs Required
- `SHOTS_EP{{XX}}/*.png` - All episode shots
- `SHOT_LIST_EP{{XX}}.json` - Shot specifications
- `SHOT_QA_REPORT_EP{{XX}}.md` - Individual shot QA
- `CANON_DB.json` - Visual canon
- `CHARACTER_REFS/*/refs/*.png` - Reference images

## Outputs Produced
- `VISUAL_CONTINUITY_REPORT_EP{{XX}}.md`
- Drift alerts and correction recommendations

## Continuity Dimensions

### 1. Character Continuity
- Same character looks consistent across all appearances
- Outfit consistency within scenes
- Expression/pose progression makes sense

### 2. Location Continuity
- Same location looks consistent across all shots
- Time-of-day matches within scenes
- Props/furniture don't move unexpectedly

### 3. Scene Continuity
- Shots within a scene are visually cohesive
- Lighting consistent within scene
- Color grading consistent

### 4. Style Continuity
- Overall aesthetic maintained
- Color palette consistent
- Mood appropriate throughout

## Process

### Step 1: Group Shots

Organize shots by:
- Scene (same location, continuous time)
- Character (all appearances of each character)
- Location (all shots at each location)

### Step 2: Character Thread Analysis

For each character:
1. Collect all shots featuring character
2. Compare character appearance across shots
3. Identify drift patterns
4. Flag significant inconsistencies

**Check Points**:
- Face consistency
- Hair consistency
- Outfit consistency (within same scene)
- Body proportions
- Age appearance

### Step 3: Scene Thread Analysis

For each scene:
1. Collect all shots in scene
2. Verify temporal continuity
3. Check spatial consistency
4. Validate lighting continuity

**Check Points**:
- Lighting angle doesn't jump
- Props don't move unexpectedly
- Character positions make sense
- Background consistent

### Step 4: Location Thread Analysis

For each location:
1. Collect all shots at location
2. Compare architectural elements
3. Verify key features present
4. Check time-of-day consistency

**Check Points**:
- Key architectural features
- Furniture/prop placement
- Window positions
- Color of walls/surfaces

### Step 5: Drift Detection

Calculate drift metrics:

**Progressive Drift**:
- Character slowly changes over episode
- Detected by comparing first vs. last appearance

**Sudden Drift**:
- Abrupt change between adjacent shots
- Detected by sequential comparison

**Pattern Drift**:
- Consistent error across multiple shots
- Detected by comparing against reference

### Step 6: Generate Report

```markdown
# Visual Continuity Report: EP{{XX}}

## Summary
- Overall Continuity Score: {{0-100}}
- Characters: {{SCORE}}
- Locations: {{SCORE}}
- Scenes: {{SCORE}}
- Style: {{SCORE}}

## Critical Issues

### Character Drift: {{CHARACTER}}
- First appearance: SC01_SH03
- Drift detected: SC05_SH02 onward
- Issue: Hair color shifted darker
- Action: Regenerate SC05+ with corrected refs

## Scene Continuity Issues

### Scene 03
- Shots affected: SH04, SH06
- Issue: Lighting angle inconsistent
- Action: Regenerate with matched lighting

## Drift Patterns

### {{CHARACTER}} Over Episode
[Visual timeline or scores showing consistency]

### {{LOCATION}} Across Scenes
[Visual timeline or scores]

## Recommendations

### High Priority
1. Regenerate shots: [list]
2. Update references: [if refs are causing drift]

### Medium Priority
1. Review and potentially regenerate: [list]

### Acceptable Variance
[List of minor issues that don't require action]
```

### Step 7: Prioritize Corrections

Rank issues by:
1. **Critical**: Breaks story clarity
2. **High**: Noticeable distraction
3. **Medium**: Visible but not distracting
4. **Low**: Minor, acceptable variance

### Step 8: Update Canon if Needed

If generated shots are consistently better than references:
- Flag for reference-library-updater
- Document what works better

## Continuity Rules

### Within Scene (STRICT)
- Characters must look identical
- Outfits cannot change
- Props cannot move
- Lighting must match

### Across Scenes, Same Day (MODERATE)
- Characters should look consistent
- Outfits can change if justified
- Minor lighting variation acceptable

### Across Episode (FLEXIBLE)
- Characters recognizable
- Style consistent
- Overall aesthetic maintained

## Common Continuity Errors

### Character Issues
- Face features drifting
- Hair changing
- Age appearing different
- Outfit changing mid-scene

### Location Issues
- Architecture changing
- Props moving
- Lighting direction flipping
- Color of surfaces changing

### Scene Issues
- Shot-to-shot jumps
- Lighting inconsistency
- Color grading shifts

## End-of-Clip Continuity Review (Video Production)

When generating video clips, continuity must be validated BETWEEN clips, not just within shots.

### Workflow

```
Generate Clip N → Extract Last Frame → Claude Reviews → Decision:
    ├─ Continue to Clip N+1 (if continuity is good)
    ├─ Generate Bridge Clip (if gap needs bridging)
    └─ Generate New Frame(s) → New Bridge Clip (for exceptional continuity)
```

### Review Process

After each clip is generated:

1. **Extract last frame** using ffmpeg:
   ```bash
   ffmpeg -sseof -1 -i clip.mp4 -update 1 -q:v 2 last_frame.png
   ```

2. **Claude reviews** the extracted frame:
   - What is the character's position/state/expression?
   - Does this flow naturally into the next clip's requirements?
   - Are there any continuity breaks?

3. **Decision**:
   - **Continue**: Last frame flows naturally into next clip's start frame
   - **Bridge needed**: Gap exists but can be bridged with additional video
   - **New frames needed**: Generate supporting frame(s) using Nano Banana Pro

### Bridge Clip Strategy

When a bridge clip is needed:

1. Use extracted last frame as start frame (strategy: `last_frame`)
2. Write prompts that transition FROM the current state TO the next clip's expected state
3. Keep prompts START FRAME AWARE - describe continuation, not contradiction

### Continuity Decision Criteria

| Scenario | Decision |
|----------|----------|
| Character in same position, same framing | Continue |
| Character in similar position, different framing | Continue (cut handles it) |
| Character needs to move to new position | Bridge clip |
| Significant time/action gap | Bridge clip |
| New location | New generated start frame |

## Notes

- Perfect continuity is impossible with current tech
- Focus on maintaining character recognition
- Location minor drift is less noticeable
- Scene boundaries can hide more variance
- Some drift is acceptable if not distracting
- Progressive drift is harder to catch than sudden
- **End-of-clip review is essential for video production**
