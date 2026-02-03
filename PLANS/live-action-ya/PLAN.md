---
name: Live Action YA
modality: live-action-ya
version: 1.0

description: |
  Production pipeline for live-action young adult content.
  Features a 5-agent Writers Room for structured creative friction
  that produces original, non-cliché storytelling.

phases:
  - id: intake
    name: Story Intake
    skills:
      - writer/story-intake
    gate: gate-0
    deliverables:
      - STORY/CREATIVE_BRIEF.md
      - STORY/POWER_STACK.md

  - id: writers-room
    name: Writers Room
    skills:
      - writer/writers-room
    gate: gate-1
    deliverables:
      - STORY/WRITERS_ROOM/round_1.md
      - STORY/WRITERS_ROOM/round_2.md
      - STORY/WRITERS_ROOM/round_3.md
      - STORY/WRITERS_ROOM/STORY_LOCK.md

  - id: story-development
    name: Story Development
    skills:
      - writer/logline-development
      - writer/character-creation
      - writer/story-structure
    gate: gate-2
    deliverables:
      - STORY/LOGLINE_LOCK.md
      - STORY/CHARACTER_SHEETS/*.md
      - STORY/EPISODE_STRUCTURE.md

  - id: screenplay
    name: Screenplay
    skills:
      - writer/screenplay
      - writer/dialogue-polish
    gate: gate-3
    deliverables:
      - STORY/SCRIPTS/*.md

  - id: visual-development
    name: Visual Development
    skills:
      - art-director/style-guide
      - art-director/character-design
      - art-director/location-design
    gate: gate-4
    deliverables:
      - VISUAL_PRODUCTION/STYLE_GUIDE/
      - EXPORTS/character_refs/
      - EXPORTS/location_refs/

gates:
  - id: gate-0
    name: Intake Complete
    criteria:
      - CREATIVE_BRIEF.md exists with genre, tone, audience
      - POWER_STACK.md exists with structural framework

  - id: gate-1
    name: Story Locked
    criteria:
      - 3 complete round-robin cycles completed
      - All 5 agents contributed each round
      - STORY_LOCK.md synthesizes final premise
      - No unresolved logical contradictions

  - id: gate-2
    name: Story Structured
    criteria:
      - Logline locked with protagonist, flaw, stakes
      - All main characters have sheets with fatal flaws
      - Episode/act structure defined with beats

  - id: gate-3
    name: Scripts Complete
    criteria:
      - All episode/scene scripts written
      - Dialogue polished and character-voice distinct

  - id: gate-4
    name: Visual References Complete
    criteria:
      - Style guide locked
      - All character refs generated
      - All location refs generated
---

# Live Action YA Production Plan

## Overview

This plan guides production of live-action young adult content using a unique **Writers Room** methodology designed to produce original, non-cliché storytelling through structured creative friction.

## When to Use This Plan

- Live-action TV series for YA audiences
- Live-action feature films for YA audiences
- Projects requiring high originality and emotional depth
- Romance, adventure, fantasy, or drama genres

## The Writers Room Philosophy

In 2026, the secret to originality from AI isn't better prose—it's **structured friction**. When agents agree too much, they default to "AI Average": a predictable blend of tropes and polite resolutions.

The Writers Room uses 5 specialized agents that actively challenge each other's contributions across 3 complete rounds.

---

## Phase 1: Story Intake

Standard creative interview to establish genre, tone, and foundational elements.

**Deliverables:**
- `CREATIVE_BRIEF.md`
- `POWER_STACK.md`

---

## Phase 2: Writers Room (The Core Innovation)

### The 5 Agents

| Agent | Role | Mission | Constraint |
|-------|------|---------|------------|
| **Chaos Architect** | Disruptor | Break clichés, introduce Black Swan events | No happy endings mid-story; must end on difficult choice |
| **Sensory Nihilist** | Stylist | Ground in visceral, sensory detail | Forbidden from abstract emotions (sad, angry, scared) |
| **Internal Logician** | Lore-Keeper | Track consistency, punish rule-breaking | Must add logical consequences for broken rules |
| **Shadow Psychologist** | Empath | Add hidden desires and fatal flaws | Every character must actively sabotage the plot |
| **Brutal Editor** | Sieve | Cut 20%, enforce structure | Must maintain non-linear or constrained structure |

### Round-Robin Workflow

Each round follows this sequence:

```
1. Chaos Architect    → Seeds/disrupts the premise
2. Internal Logician  → Builds rigid world rules
3. Shadow Psychologist → Adds character depth/shadows
4. Sensory Nihilist   → Grounds in texture/sensation
5. Brutal Editor      → Cuts 20%, enforces structure
```

### Three Rounds

- **Round 1**: Establish the bizarre premise, world rules, character shadows
- **Round 2**: Complicate everything, deepen contradictions, add texture
- **Round 3**: Refine, resolve structural issues, lock the story

**Deliverables:**
- `WRITERS_ROOM/round_1.md` - First pass
- `WRITERS_ROOM/round_2.md` - Complications
- `WRITERS_ROOM/round_3.md` - Refinement
- `WRITERS_ROOM/STORY_LOCK.md` - Final synthesis

---

## Phase 3: Story Development

Using the locked story from the Writers Room, develop formal story documents.

**Skills:**
- `writer/logline-development`
- `writer/character-creation`
- `writer/story-structure`

**Deliverables:**
- `LOGLINE_LOCK.md`
- `CHARACTER_SHEETS/*.md`
- `EPISODE_STRUCTURE.md`

---

## Phase 4: Screenplay

Full script development with dialogue polish.

**Deliverables:**
- `SCRIPTS/*.md`

---

## Phase 5: Visual Development

Character and location reference generation for production.

**Deliverables:**
- `STYLE_GUIDE/`
- `character_refs/`
- `location_refs/`

---

## Project Structure

```
{project}/
├── PROJECT_CONFIG.yaml
├── .state.json
├── .env
│
├── STORY/
│   ├── CREATIVE_BRIEF.md
│   ├── POWER_STACK.md
│   ├── WRITERS_ROOM/
│   │   ├── round_1.md
│   │   ├── round_2.md
│   │   ├── round_3.md
│   │   └── STORY_LOCK.md
│   ├── LOGLINE_LOCK.md
│   ├── EPISODE_STRUCTURE.md
│   ├── CHARACTER_SHEETS/
│   └── SCRIPTS/
│
├── VISUAL_PRODUCTION/
│   └── STYLE_GUIDE/
│
└── EXPORTS/
    ├── character_refs/
    └── location_refs/
```
