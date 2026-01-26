# Bible Keeper Skill

## Purpose
Maintain the living SHOW_BIBLE.md document that consolidates all story artifacts into a single authoritative reference. Track changes and ensure consistency across all documents.

## Trigger
Runs continuously after story-intake completes. Updates after each major artifact change.

## Inputs Required
- All story artifacts as they are created/modified:
  - `CREATIVE_BRIEF.md`
  - `POWER_STACK.md`
  - `LOGLINE_LOCK.md`
  - `CHARACTER_SHEETS/*.md`
  - `RELATIONSHIP_MAP.json`
  - `EP{{XX}}_BEATS.md`
  - `EP{{XX}}_SCENELIST.md`
  - `SCRIPTS/SCRIPT_EP{{XX}}.md`

## Outputs Produced
- `SHOW_BIBLE.md` - Consolidated reference document
- `BIBLE_CHANGELOG.md` - Version history

## Process

### Step 1: Initial Bible Creation

After CREATIVE_BRIEF.md and LOGLINE_LOCK.md exist, create initial SHOW_BIBLE.md:

```markdown
# Show Bible: {{SHOW_TITLE}}

## Quick Reference
- **Logline**: [from LOGLINE_LOCK]
- **Genre**: [from CREATIVE_BRIEF]
- **Tone**: [from CREATIVE_BRIEF]
- **Episode Length**: [from POWER_STACK]

## Core Concept
[Synthesized from CREATIVE_BRIEF]

## Characters
[Will be populated from CHARACTER_SHEETS]

## Relationships
[Will be populated from RELATIONSHIP_MAP]

## World & Setting
[From CREATIVE_BRIEF]

## Visual Identity
[From CREATIVE_BRIEF aesthetic keywords]

## Episode Guide
[Will be populated as episodes are written]
```

### Step 2: Character Integration

When CHARACTER_SHEETS are created:

For each character, add to bible:
- Name and role
- One-paragraph summary
- Key relationships
- Arc trajectory
- Visual description (for reference generation)

Do NOT duplicate full CHARACTER_SHEET—link to it.

### Step 3: Relationship Integration

When RELATIONSHIP_MAP.json is created:
- Add relationship summaries to bible
- Include current axis values
- Note arc directions
- Track private language

### Step 4: Episode Integration

When each episode script passes Gate 5:
- Add episode to Episode Guide
- Summary (2-3 sentences)
- Key character moments
- Relationship changes
- New information revealed
- Continuity impacts

### Step 5: Change Tracking

For every update:

```markdown
## Changelog Entry

**Date**: {{DATE}}
**Change**: {{DESCRIPTION}}
**Affected Artifacts**:
- {{ARTIFACT_1}}
- {{ARTIFACT_2}}
**Reason**: {{WHY_CHANGE_WAS_MADE}}
**Verified By**: {{SKILL_OR_HUMAN}}
```

### Step 6: Consistency Monitoring

Continuously check for:

| Check | Source | Against | Status |
|-------|--------|---------|--------|
| Character ages | CHARACTER_SHEETS | SHOW_BIBLE | |
| Relationship values | RELATIONSHIP_MAP | Episode changes | |
| Timeline | All episodes | Internal logic | |
| Location names | SCENELISTS | CANON_DB | |

Flag any inconsistencies for resolution.

### Step 7: Canon Lock Status

Track what is locked vs. flexible:

**LOCKED** (cannot change without major revision):
- Character names and core identities
- Fundamental relationships
- World rules
- Established timeline events

**FLEXIBLE** (can evolve with story):
- Minor character details
- Unexplored backstory
- Future arc directions

### Step 8: Visual Reference Integration

When v0.2 begins, add:
- Reference image paths
- Visual anchors for each character
- Location reference links
- Style guide summary

## Bible Structure

```markdown
# Show Bible: {{TITLE}}

## Version & Status
- Version: X.X
- Last Updated: DATE
- Status: DEVELOPMENT/PRODUCTION/LOCKED

## Quick Reference Card
[One-page summary for anyone joining project]

## Logline & Premise
[From LOGLINE_LOCK]

## Tone & Genre
[From CREATIVE_BRIEF]

## Theme
[Central question and approach]

## Characters
### Main Characters
[Summaries with links to full sheets]

### Supporting Characters
[Brief descriptions]

### Recurring Characters
[As needed]

## Relationships
### Key Dynamics
[Narrative summaries of important relationships]

### Relationship Matrix
[Current axis values, updated per episode]

## World Building
### Setting
[Physical world description]

### Rules
[Any special rules of the world]

### Timeline
[Key events before and during series]

## Visual Identity
### Aesthetic
[Keywords and description]

### Color Language
[What colors mean in this show]

### Reference Status
[Links to visual references when generated]

## Episode Guide
### Season 1
- **EP01**: [Summary]
- **EP02**: [Summary]
...

## Canon Facts
[Established truths that cannot be contradicted]

## Open Questions
[Things deliberately left ambiguous]

## Appendices
- Full CHARACTER_SHEETS: [links]
- RELATIONSHIP_MAP: [link]
- Episode scripts: [links]
```

## Update Triggers

Update SHOW_BIBLE.md when:
- New character sheet created
- Relationship map updated
- Episode passes Gate 5
- Any canon fact established
- Visual references generated
- Continuity issue resolved

## Consistency Alerts

Generate alert if:
- Character fact contradicts established canon
- Timeline event conflicts with prior event
- Relationship change not tracked in map
- Location used that doesn't exist in references

## Notes

- Bible is REFERENCE, not source of truth
- Source documents (CHARACTER_SHEETS, etc.) remain authoritative
- Bible provides consolidated view for easy access
- Update bible AFTER source documents, not before
- Changelog is critical—track everything
- Bible should be readable by someone new to project
