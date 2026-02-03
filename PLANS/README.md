# PLANS

Plans are high-level production pipelines tailored to specific use cases. Each plan defines the end-to-end process from initial concept to final deliverables.

## Plan Structure

Each plan directory contains:

```
{plan-name}/
├── PLAN.md           # Master plan definition
├── gates.yaml        # Quality gates and progression criteria
└── examples/         # Example projects using this plan
```

## PLAN.md Format

```yaml
---
name: Plan Name
modality: animated-series | vertical-microdrama | live-action | kids-narrative
description: One paragraph describing the use case

phases:
  - id: phase-1
    name: Phase Name
    skills:
      - writer/story-intake
      - writer/logline-development
    gate: gate-1
    deliverables:
      - CREATIVE_BRIEF.md
      - LOGLINE_LOCK.md

gates:
  - id: gate-1
    name: Gate Name
    criteria:
      - File exists: STORY/CREATIVE_BRIEF.md
      - File exists: STORY/LOGLINE_LOCK.md
---

# {Plan Name}

## Overview
{Detailed description of this production pipeline}

## When to Use This Plan
- Use case 1
- Use case 2

## Phase Details

### Phase 1: {Name}
{Description of what happens in this phase}

**Skills Invoked:**
- `writer/story-intake` - Initial creative interview
- `writer/logline-development` - Lock the logline

**Deliverables:**
- CREATIVE_BRIEF.md
- LOGLINE_LOCK.md

**Gate Criteria:**
- [ ] Creative brief captures core concept
- [ ] Logline has protagonist, flaw, and stakes
```

## Available Plans

| Plan | Modality | Status |
|------|----------|--------|
| [animated-series](./animated-series/) | Animated episodic content | Active |
| [vertical-microdrama](./vertical-microdrama/) | Short-form vertical video | Planned |
