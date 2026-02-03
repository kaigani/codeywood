---
name: Animated Series
modality: animated-series
version: 1.0

description: |
  End-to-end production pipeline for animated episodic content.
  From initial concept through visual reference generation.

phases:
  - id: intake
    name: Story Intake
    skills:
      - writer/story-intake
    gate: gate-0
    deliverables:
      - STORY/CREATIVE_BRIEF.md
      - STORY/POWER_STACK.md

  - id: story-development
    name: Story Development
    skills:
      - writer/logline-development
      - writer/character-creation
      - writer/story-structure
    gate: gate-3
    deliverables:
      - STORY/LOGLINE_LOCK.md
      - STORY/CHARACTER_SHEETS/*.md
      - STORY/EPISODE_STRUCTURE.md

  - id: screenplay
    name: Screenplay
    skills:
      - writer/screenplay
      - writer/dialogue-polish
    gate: gate-4
    deliverables:
      - STORY/SCRIPTS/*.md

  - id: story-approval
    name: Story Approval
    skills:
      - writer/story-critique
    gate: gate-5
    deliverables:
      - STORY/CRITIQUE_REPORT.md

  - id: visual-development
    name: Visual Development
    skills:
      - art-director/style-guide
      - art-director/character-design
      - art-director/location-design
    gate: gate-6
    deliverables:
      - VISUAL_PRODUCTION/STYLE_GUIDE/
      - EXPORTS/hero_shots/
      - EXPORTS/identity_sheets/
      - EXPORTS/location_refs/

  - id: shot-production
    name: Shot Production
    skills:
      - art-director/storyboards
    gate: gate-7
    deliverables:
      - EXPORTS/storyboards/

gates:
  - id: gate-0
    name: Intake Complete
    criteria:
      - CREATIVE_BRIEF.md exists
      - POWER_STACK.md exists

  - id: gate-3
    name: Story Structured
    criteria:
      - Logline locked with protagonist, flaw, stakes
      - All main characters have sheets
      - Episode structure defined with beats

  - id: gate-4
    name: Scripts Complete
    criteria:
      - All episode scripts written
      - Dialogue polished

  - id: gate-5
    name: Story Approved
    criteria:
      - Critique score >= 70
      - Major issues addressed

  - id: gate-6
    name: References Complete
    criteria:
      - Style guide locked
      - All character refs generated
      - All location refs generated

  - id: gate-7
    name: Shots Complete
    criteria:
      - All storyboards generated
      - Visual continuity validated
---

# Animated Series Production Plan

## Overview

This plan guides production of animated episodic content from initial concept to shot-ready visual references. It's designed for serialized storytelling with consistent characters and visual style.

## When to Use This Plan

- Animated TV series (any length)
- Animated short films
- Web series with consistent visual style
- Any project requiring character consistency across episodes

## Phase Details

### Phase 1: Story Intake

**Purpose:** Capture the creator's vision and establish core story elements.

**Skills:**
- `writer/story-intake` - Guided interview to extract concept

**Deliverables:**
- `CREATIVE_BRIEF.md` - Core concept, tone, audience
- `POWER_STACK.md` - Thematic and emotional foundations

**Doneness:**
- [ ] Creative brief captures genre, tone, and target audience
- [ ] Power stack defines core themes and emotional journey
- [ ] No placeholder content

---

### Phase 2: Story Development

**Purpose:** Develop the logline, characters, and story structure.

**Skills:**
- `writer/logline-development` - Lock the logline
- `writer/character-creation` - Create character sheets
- `writer/story-structure` - Define episode beats

**Deliverables:**
- `LOGLINE_LOCK.md` - Finalized logline
- `CHARACTER_SHEETS/*.md` - One per main character
- `EPISODE_STRUCTURE.md` - Beats and scene lists

**Doneness:**
- [ ] Logline has clear protagonist, flaw, and stakes
- [ ] Each character has complete sheet (visual, psychological, arc)
- [ ] Episode structure has beginning, middle, end with clear beats

---

### Phase 3: Screenplay

**Purpose:** Write full scripts with dialogue and visual direction.

**Skills:**
- `writer/screenplay` - Write episode scripts
- `writer/dialogue-polish` - Refine dialogue quality

**Deliverables:**
- `SCRIPTS/*.md` - Episode screenplays

**Doneness:**
- [ ] Scripts have proper format (scene headers, action, dialogue)
- [ ] Visual metadata included for key moments
- [ ] Dialogue sounds natural and character-appropriate

---

### Phase 4: Story Approval

**Purpose:** Quality review before visual production begins.

**Skills:**
- `writer/story-critique` - Evaluate story quality

**Deliverables:**
- `CRITIQUE_REPORT.md` - Detailed evaluation

**Doneness:**
- [ ] Critique score >= 70
- [ ] Critical issues identified and addressed
- [ ] Ready for visual production

---

### Phase 5: Visual Development

**Purpose:** Establish visual style and generate character/location references.

**Skills:**
- `art-director/style-guide` - Lock visual style
- `art-director/character-design` - Generate character references
- `art-director/location-design` - Generate location references

**Deliverables:**
- `STYLE_GUIDE/` - Visual style documentation
- `hero_shots/` - Character hero images
- `identity_sheets/` - Character reference sheets
- `location_refs/` - Location reference grids

**Doneness:**
- [ ] Style guide locked and approved
- [ ] All main characters have hero shots and identity sheets
- [ ] All key locations have reference grids

---

### Phase 6: Shot Production

**Purpose:** Generate storyboards for each scene.

**Skills:**
- `art-director/storyboards` - Generate storyboard grids

**Deliverables:**
- `storyboards/` - Scene storyboard composites

**Doneness:**
- [ ] All scenes have storyboards
- [ ] Shot composition clear
- [ ] Visual continuity maintained

---

## Project Structure

```
{project}/
├── PROJECT_CONFIG.yaml     # Project settings
├── .state.json            # Progress tracking
├── .env                   # API keys (not committed)
│
├── STORY/
│   ├── CREATIVE_BRIEF.md
│   ├── POWER_STACK.md
│   ├── LOGLINE_LOCK.md
│   ├── EPISODE_STRUCTURE.md
│   ├── CHARACTER_SHEETS/
│   │   ├── {CHARACTER}.md
│   │   └── ...
│   └── SCRIPTS/
│       ├── EP01.md
│       └── ...
│
├── VISUAL_PRODUCTION/
│   ├── STYLE_GUIDE/
│   └── SHOT_LISTS/
│
└── EXPORTS/
    ├── style_tests/
    ├── hero_shots/
    ├── identity_sheets/
    ├── location_refs/
    └── storyboards/
```
