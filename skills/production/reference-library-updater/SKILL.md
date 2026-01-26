# Reference Library Updater Skill

## Purpose
Improve the reference library based on successful shot generation, extracting high-quality generated images to serve as improved references.

## Trigger
After visual continuity validation and manual review of episode.

## Inputs Required
- `SHOTS_EP{{XX}}/*.png` - Generated shots
- `SHOT_QA_REPORT_EP{{XX}}.md` - Quality scores
- `VISUAL_CONTINUITY_REPORT_EP{{XX}}.md`
- `CHARACTER_REFS/*/refs/*.png` - Current references
- `LOCATION_REFS/*/refs/*.png` - Current references
- `CANON_DB.json`

## Outputs Produced
- Updated reference images (if improvements found)
- `REFERENCE_UPDATE_LOG.md`
- Updated `CANON_DB.json` (new reference paths)

## Process

### Step 1: Identify High-Quality Shots

From QA reports, find shots that:
- Scored highly on consistency (0.90+)
- Passed all quality checks
- Received positive manual review

### Step 2: Evaluate for Reference Potential

A shot is a good reference candidate if:
- Character is clearly visible
- Pose/expression is useful for future generation
- Lighting is representative
- No distracting elements

**Best Candidates**:
- Clean single-character shots
- Clear facial expressions
- New poses not in current references
- Better quality than existing references

### Step 3: Compare to Existing References

For each candidate:
1. Identify which reference it could replace/supplement
2. Compare quality objectively
3. Determine if it adds value to library

**Replacement Criteria**:
- Clearly better consistency scores when used
- Better detail/quality
- More representative of character

**Supplement Criteria**:
- New pose not currently covered
- New expression not currently covered
- Different context useful for future shots

### Step 4: Extract and Process

For approved candidates:
1. Crop to appropriate framing
2. Ensure consistent dimensions
3. Apply any necessary color correction
4. Save to appropriate reference directory

**Naming Convention**:
`{character}_{type}_{variant}_gen.png`

The `_gen` suffix indicates generated (not hand-crafted) reference.

### Step 5: Test New References

Before committing:
1. Use new reference to regenerate a known shot
2. Compare quality to original generation
3. Verify improvement

### Step 6: Update Reference Library

If tests pass:
1. Add new reference to appropriate directory
2. Update CANON_DB.json with new path
3. Keep old reference as backup

```json
"reference_images": {
  "front_neutral": "CHARACTER_REFS/ALICE/refs/alice_front_neutral.png",
  "front_neutral_gen": "CHARACTER_REFS/ALICE/refs/alice_front_neutral_gen.png",
  "action_running": "CHARACTER_REFS/ALICE/refs/alice_running_gen.png"
}
```

### Step 7: Document Changes

Log all updates:

```markdown
# Reference Library Update Log

## Update: 2026-01-25

### ALICE_CHEN

**Added**:
- `alice_determined_gen.png`
  - Source: EP01_SC08_SH03
  - Reason: Better determined expression than original
  - Quality: 0.94

**Considered but Rejected**:
- EP01_SC05_SH02
  - Reason: Lighting too specific to scene

### PRECINCT_BULLPEN

**Added**:
- `bullpen_night_gen.png`
  - Source: EP01_SC12_SH01
  - Reason: Night variant not previously covered
```

## Reference Quality Hierarchy

### Tier 1: Seed References (Original)
- Hand-crafted turnarounds
- Expression packs
- Core poses
- **Never replace, only supplement**

### Tier 2: Generated References (High Quality)
- Extracted from successful shots
- High consistency scores
- Tested and validated
- **Can supplement Tier 1**

### Tier 3: Context References
- Scene-specific variations
- Lower priority
- Used for specific shot types
- **Use when Tier 1/2 not suitable**

## When NOT to Update

- Don't replace seed references
- Don't add marginal improvements
- Don't bloat library with redundant refs
- Don't add scene-specific refs as general refs

## Feedback Loop

The update cycle improves generation over time:

```
Generate Shots → Quality Check → Find High Performers
      ↑                                    ↓
      └──── Update References ← Extract Best ←
```

## Notes

- Be conservative about updates
- Quality over quantity in reference library
- Seed references remain authoritative
- Generated refs supplement, don't replace
- Track performance of new refs
- Roll back if new refs cause problems
