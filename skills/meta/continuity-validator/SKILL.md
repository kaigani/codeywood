# Continuity Validator Skill

## Purpose
Cross-check all story artifacts for contradictions, timeline inconsistencies, and canon violations before proceeding to visual production.

## Trigger
Before visual production begins (after Gate 5), and periodically during development.

## Inputs Required
- All story artifacts:
  - `CREATIVE_BRIEF.md`
  - `LOGLINE_LOCK.md`
  - `CHARACTER_SHEETS/*.md`
  - `RELATIONSHIP_MAP.json`
  - `EP{{XX}}_BEATS.md`
  - `EP{{XX}}_SCENELIST.md`
  - `SCRIPTS/SCRIPT_EP{{XX}}.md`
  - `SHOW_BIBLE.md`
  - `CANON_DB.json`

## Outputs Produced
- `CONTINUITY_REPORT.md`
- List of contradictions to resolve
- PASS/FAIL for visual production readiness

## Continuity Dimensions

### 1. Character Continuity
- Ages consistent across documents
- Physical descriptions match everywhere
- Backstory facts don't contradict
- Voice profiles match dialogue
- Relationship history consistent

### 2. Timeline Continuity
- Events ordered correctly
- Time references don't conflict
- Character ages align with history
- "X years ago" references match

### 3. World Continuity
- Rules established are followed
- Location descriptions consistent
- Technology/period consistent
- Organization structures consistent

### 4. Relationship Continuity
- Relationship history matches references
- Axis values match described dynamics
- Character knowledge is accurate
- Secret knowledge properly tracked

### 5. Visual Continuity
- Physical descriptions match across docs
- Outfit descriptions consistent
- Location descriptions match
- Prop descriptions consistent

## Process

### Step 1: Build Fact Database

Extract all stated facts from artifacts:

```
FACT: Alice is 32 years old
SOURCE: CHARACTER_SHEETS/ALICE_CHEN.md
TYPE: character_attribute

FACT: Alice's partner died 18 months before pilot
SOURCE: CANON_DB.json
TYPE: timeline_event

FACT: Alice and Bob have worked together for 9 months
SOURCE: CANON_DB.json
TYPE: relationship_history
```

### Step 2: Cross-Reference Facts

For each fact, check for:
- Direct contradictions
- Implied contradictions
- Timeline conflicts
- Logical inconsistencies

### Step 3: Check Character Facts

For each character:
- [ ] Age matches across all documents
- [ ] Physical description consistent
- [ ] Backstory facts align
- [ ] Relationship history consistent
- [ ] Knowledge states are accurate

### Step 4: Check Timeline

Build timeline from all references:
```
-18 months: Partner dies
-9 months: Alice and Bob start working together
-0: Pilot begins
```

Verify:
- [ ] Events don't conflict
- [ ] Durations add up
- [ ] Age references match

### Step 5: Check World Facts

Verify:
- [ ] Location descriptions match
- [ ] Technology/period consistent
- [ ] Organizations described consistently
- [ ] Rules are followed in story

### Step 6: Check Scripts Against Canon

For each script:
- [ ] Character dialogue matches voice profile
- [ ] Character knowledge is accurate (no revealing secrets they shouldn't know)
- [ ] Location references match descriptions
- [ ] Timeline references are accurate

### Step 7: Generate Report

```markdown
# Continuity Report

**Date**: 2026-01-25
**Scope**: All Phase 1 artifacts
**Status**: {{PASS/FAIL}}

## Summary
- Facts checked: {{COUNT}}
- Contradictions found: {{COUNT}}
- Warnings: {{COUNT}}

## Contradictions

### CRITICAL: Age Inconsistency
**Fact 1**: Alice is 32 (CHARACTER_SHEET)
**Fact 2**: "In her late twenties" (SCRIPT_EP01, SC03)
**Resolution Required**: Update script dialogue

### HIGH: Timeline Conflict
**Fact 1**: Partner died 18 months ago (CANON_DB)
**Fact 2**: "Two years since Mike died" (SCRIPT_EP01, SC08)
**Resolution Required**: Correct timeline reference

## Warnings

### Character Knowledge
**Scene**: EP01_SC05
**Issue**: Bob references case detail Alice hasn't shared
**Severity**: Medium
**Suggestion**: Add earlier reveal or adjust dialogue

## Verified Consistent

### Character Ages
- Alice: 32 ✓
- Bob: 45 ✓

### Timeline
- Partner death: -18 months ✓
- Partnership start: -9 months ✓

### Locations
- Precinct Bullpen: Consistent across 3 documents ✓
```

### Step 8: Track Resolutions

For each contradiction:
1. Document the issue
2. Identify source of truth
3. List documents to update
4. Verify resolution

## Contradiction Severity

### CRITICAL
- Breaks story logic
- Visible to audience
- Must fix before visual production

### HIGH
- Confusing to audience
- Affects character/story integrity
- Should fix before visual production

### MEDIUM
- Minor inconsistency
- Careful reader might notice
- Fix when possible

### LOW
- Very minor
- Unlikely to be noticed
- Document but don't block

## Common Contradiction Types

### Timeline Issues
- "X years ago" conflicts
- Age inconsistencies
- Event ordering problems

### Character Issues
- Description variations
- Knowledge leaks (knowing what they shouldn't)
- Voice/behavior inconsistencies

### World Issues
- Technology anachronisms
- Geography conflicts
- Rule violations

## Automated Checks

Where possible, automate:
- Age extraction and comparison
- Timeline event extraction
- Character name consistency
- Location name consistency

## Notes

- Run before major phase transitions
- Critical contradictions block progress
- Some contradictions need human judgment
- Document resolutions in BIBLE_CHANGELOG.md
- Update CANON_DB with correct facts
