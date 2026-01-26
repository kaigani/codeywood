# Workflow Orchestrator Skill

## Purpose
Manage the end-to-end pipeline, tracking progress through phases, managing gates, and coordinating skill execution.

## Trigger
Project initialization or continuation.

## Inputs Required
- Project configuration
- Current state of all artifacts
- Quality gate status

## Outputs Produced
- `PROJECT_STATUS.md` - Current project state
- `EXECUTION_LOG.md` - History of actions
- Gate pass/fail tracking

## Pipeline Overview

```
PHASE 1: STORY FOUNDATION (v0.1)
├── story-intake
├── logline-architect
├── character-architect
├── story-architect
├── screenplay-writer
├── dialogue-doctor
├── story-critic
└── bible-keeper (continuous)

PHASE 2a: REFERENCE LIBRARY (v0.2a)
├── canon-database-manager
├── visual-style-guide
├── character-reference-generator
├── location-reference-generator
└── prop-reference-generator

PHASE 2b: SHOT PRODUCTION (v0.2b)
├── shot-list-generator
├── shot-image-generator
├── shot-quality-validator
├── visual-continuity-validator
└── reference-library-updater

PHASE 3: SCENE GENERATION (v0.3)
└── [Future skills]
```

## State Machine

### Project States

```
INITIALIZED
    ↓
STORY_INTAKE
    ↓
STORY_DEVELOPMENT
    ↓
STORY_REVIEW
    ↓ (Gate 5 Pass)
REFERENCE_GENERATION
    ↓
SHOT_PRODUCTION
    ↓
SHOT_VALIDATION
    ↓ (Quality Pass)
EPISODE_COMPLETE
```

### Transitions

Each transition requires:
- Previous phase outputs exist
- Quality gate passed (if applicable)
- No blocking errors

## Quality Gates

### Gate 0: Intake Complete
- [ ] All 8 core questions answered
- [ ] CREATIVE_BRIEF.md exists
- [ ] POWER_STACK.md exists

### Gate 1: Logline Locked
- [ ] LOGLINE_LOCK.md exists
- [ ] Contains protagonist + flaw
- [ ] Contains relationship stake
- [ ] Contains consequence

### Gate 2: Characters Complete
- [ ] All main CHARACTER_SHEETS exist
- [ ] RELATIONSHIP_MAP.json exists
- [ ] All characters have want/need/lie
- [ ] Visual descriptions are prompt-ready

### Gate 3: Story Structured
- [ ] EP{{XX}}_BEATS.md exists
- [ ] EP{{XX}}_SCENELIST.md exists
- [ ] All scenes have GOTC

### Gate 4: Script Complete
- [ ] SCRIPT_EP{{XX}}.md exists
- [ ] Dialogue refined
- [ ] Visual metadata present

### Gate 5: Story Approved
- [ ] CRITIQUE_REPORT passes (70+)
- [ ] No critical issues
- [ ] Ready for visual production

### Gate 6: References Complete
- [ ] CANON_DB.json fully populated
- [ ] All character refs generated
- [ ] All location refs generated
- [ ] Style guide complete

### Gate 7: Shots Complete
- [ ] All shots generated
- [ ] Quality validation passed
- [ ] Continuity validation passed

## Process

### Step 1: Check Current State

Scan for existing artifacts:
```
Does CREATIVE_BRIEF.md exist? → Story intake complete
Does LOGLINE_LOCK.md exist? → Logline phase complete
Does CHARACTER_SHEETS/ have files? → Characters phase complete
...
```

### Step 2: Identify Next Action

Based on state:
- Missing artifacts → Run appropriate skill
- Gate not passed → Address failures
- All gates passed → Move to next phase

### Step 3: Execute Skill

Call appropriate skill with required inputs.
Monitor for completion and errors.

### Step 4: Validate Output

Check skill produced expected outputs.
Run any automated validation.

### Step 5: Update State

Record completion in PROJECT_STATUS.md.
Log action in EXECUTION_LOG.md.

### Step 6: Check Gate

If phase complete, evaluate gate criteria.
If passed, unlock next phase.
If failed, identify remediation.

## Status Tracking

### PROJECT_STATUS.md Format

```markdown
# Project Status: {{SHOW_TITLE}}

**Current Phase**: REFERENCE_GENERATION
**Current State**: IN_PROGRESS
**Last Update**: 2026-01-25T10:30:00Z

## Phase Progress

### Phase 1: Story Foundation
- [x] story-intake (2026-01-20)
- [x] logline-architect (2026-01-20)
- [x] character-architect (2026-01-21)
- [x] story-architect (2026-01-22)
- [x] screenplay-writer (2026-01-23)
- [x] dialogue-doctor (2026-01-23)
- [x] story-critic (2026-01-24) - PASSED 82/100

### Phase 2a: Reference Library
- [x] canon-database-manager (2026-01-24)
- [x] visual-style-guide (2026-01-24)
- [ ] character-reference-generator (IN PROGRESS)
- [ ] location-reference-generator
- [ ] prop-reference-generator

## Gate Status

| Gate | Status | Date |
|------|--------|------|
| Gate 0 | PASSED | 2026-01-20 |
| Gate 1 | PASSED | 2026-01-20 |
| Gate 2 | PASSED | 2026-01-21 |
| Gate 3 | PASSED | 2026-01-22 |
| Gate 4 | PASSED | 2026-01-23 |
| Gate 5 | PASSED | 2026-01-24 |
| Gate 6 | PENDING | |

## Blockers

None currently.

## Next Actions

1. Complete character reference generation
2. Generate location references
3. Generate prop references (if needed)
```

## Error Handling

### Skill Failure
- Log error details
- Identify cause
- Suggest remediation
- Block dependent steps

### Gate Failure
- Document what failed
- Identify required fixes
- Re-run validation after fixes

### Missing Inputs
- Identify what's missing
- Trace back to source skill
- Execute prerequisite skill

## Notes

- Orchestrator doesn't create content, only manages flow
- Human intervention may be needed at gates
- Some phases can run in parallel (refs generation)
- Log everything for debugging
- State should be recoverable from artifacts
