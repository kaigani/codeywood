# Quick Start Guide

## Getting Started with AI Video Story Generation

This guide walks you through creating your first project using the skill system.

## Prerequisites

- Claude Code CLI installed
- fal.ai API key (for image generation - Phase 2+)

## Phase 1: Story Foundation (No API Required)

### Step 1: Start with Story Intake

Read and follow:
```
skills/core/story-intake/SKILL.md
```

The skill will ask you 8-10 questions about your show concept.

**You'll create:**
- `CREATIVE_BRIEF.md`
- `POWER_STACK.md`

### Step 2: Develop Your Logline

Read and follow:
```
skills/core/logline-architect/SKILL.md
```

This generates and refines multiple logline options.

**You'll create:**
- `LOGLINE_LOCK.md`

### Step 3: Build Your Characters

Read and follow:
```
skills/core/character-architect/SKILL.md
```

Develop deep character profiles with visual descriptions.

**You'll create:**
- `CHARACTER_SHEETS/{NAME}.md` for each character
- `RELATIONSHIP_MAP.json`
- `CAST_LIST.md`

### Step 4: Structure Your Story

Read and follow:
```
skills/core/story-architect/SKILL.md
```

Create beat sheets and scene breakdowns.

**You'll create:**
- `EP01_BEATS.md`
- `EP01_SCENELIST.md`

### Step 5: Write the Screenplay

Read and follow:
```
skills/core/screenplay-writer/SKILL.md
```

Transform beats into a formatted screenplay.

**You'll create:**
- `SCRIPTS/SCRIPT_EP01.md`

### Step 6: Refine Dialogue

Read and follow:
```
skills/core/dialogue-doctor/SKILL.md
```

Polish dialogue for voice, subtext, and character.

**Updates:**
- `SCRIPTS/SCRIPT_EP01.md`

### Step 7: Story Critique

Read and follow:
```
skills/core/story-critic/SKILL.md
```

Quality gate assessment with scoring.

**You'll create:**
- `CRITIQUE_REPORT_EP01.md`

If score is 70+, proceed to Phase 2.

### Step 8: Maintain the Bible

Read and follow:
```
skills/core/bible-keeper/SKILL.md
```

Consolidate all artifacts into living reference.

**You'll create:**
- `SHOW_BIBLE.md`

---

## Phase 2: Visual Development (API Required)

### Setup

1. Get fal.ai API key
2. Configure in skill config files

### Step 9: Initialize Canon Database

Read and follow:
```
skills/production/canon-database-manager/SKILL.md
```

**You'll create:**
- `CANON_DB.json`

### Step 10: Define Visual Style

Read and follow:
```
skills/production/visual-style-guide/SKILL.md
```

**You'll create:**
- `STYLEGUIDE_VISUAL.md`

### Step 11: Generate Character References

Read and follow:
```
skills/production/character-reference-generator/SKILL.md
```

**You'll create:**
- `CHARACTER_REFS/{NAME}/VISUAL_SPEC.md`
- `CHARACTER_REFS/{NAME}/refs/*.png`

### Step 12: Generate Location References

Read and follow:
```
skills/production/location-reference-generator/SKILL.md
```

**You'll create:**
- `LOCATION_REFS/{LOCATION}/VISUAL_SPEC.md`
- `LOCATION_REFS/{LOCATION}/refs/*.png`

### Step 13: Generate Shot List

Read and follow:
```
skills/production/shot-list-generator/SKILL.md
```

**You'll create:**
- `SHOT_LIST_EP01.json`

### Step 14: Generate Shot Images

Read and follow:
```
skills/production/shot-image-generator/SKILL.md
```

**You'll create:**
- `SHOTS_EP01/{shot_id}.png`

### Step 15: Validate Quality

Read and follow:
```
skills/production/shot-quality-validator/SKILL.md
```
```
skills/production/visual-continuity-validator/SKILL.md
```

**You'll create:**
- `SHOT_QA_REPORT_EP01.md`
- `VISUAL_CONTINUITY_REPORT_EP01.md`

---

## Project Structure

After Phase 1, your project should look like:

```
your-project/
├── CREATIVE_BRIEF.md
├── POWER_STACK.md
├── LOGLINE_LOCK.md
├── CAST_LIST.md
├── RELATIONSHIP_MAP.json
├── SHOW_BIBLE.md
├── CHARACTER_SHEETS/
│   ├── CHARACTER_1.md
│   └── CHARACTER_2.md
├── EP01_BEATS.md
├── EP01_SCENELIST.md
├── SCRIPTS/
│   └── SCRIPT_EP01.md
└── CRITIQUE_REPORT_EP01.md
```

After Phase 2:

```
your-project/
├── [Phase 1 files]
├── CANON_DB.json
├── STYLEGUIDE_VISUAL.md
├── CHARACTER_REFS/
│   └── CHARACTER_1/
│       ├── VISUAL_SPEC.md
│       └── refs/
│           ├── turnaround.png
│           ├── expr_neutral.png
│           └── ...
├── LOCATION_REFS/
│   └── LOCATION_1/
│       ├── VISUAL_SPEC.md
│       └── refs/
│           └── ...
├── SHOT_LIST_EP01.json
├── SHOTS_EP01/
│   ├── EP01_SC01_SH01.png
│   └── ...
└── [QA Reports]
```

## Tips

1. **Work sequentially** - Each skill builds on the previous
2. **Read the full SKILL.md** - Don't skip sections
3. **Use templates** - They ensure consistent output
4. **Check gates** - Don't proceed until quality criteria are met
5. **Document as you go** - Future you will thank present you

## Getting Help

- Check `references/` for additional guidance
- Review example outputs in skill `examples/` directories
- Open an issue if something isn't clear

Happy storytelling!
