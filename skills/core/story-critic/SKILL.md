# Story Critic Skill

## Purpose
Provide rigorous quality assessment with veto power. Identify weaknesses, clichés, and gaps before proceeding to visual development.

## Trigger
SCRIPT_EP{{XX}}.md has been refined by dialogue-doctor.

## Inputs Required
- All story artifacts:
  - `CREATIVE_BRIEF.md`
  - `LOGLINE_LOCK.md`
  - `CHARACTER_SHEETS/*.md`
  - `EP{{XX}}_BEATS.md`
  - `SCRIPTS/SCRIPT_EP{{XX}}.md`

## Outputs Produced
- `CRITIQUE_REPORT_EP{{XX}}.md`
- **PASS/FAIL** decision for Gate 5

## Process

### Step 1: Promise vs. Delivery Check

Compare LOGLINE_LOCK.md promises to script delivery:

| Promise | Delivered? | Where? | Notes |
|---------|------------|--------|-------|
| Genre | | | |
| Protagonist flaw tested | | | |
| Relationship stakes | | | |
| Tone matched | | | |

### Step 2: Character Consistency Audit

For each major character, verify:

| Check | ALICE | BOB | ... |
|-------|-------|-----|-----|
| Want pursued in script? | | | |
| Lie challenged? | | | |
| Voice consistent? | | | |
| Causes problem(s)? | | | |
| Has surprising moment? | | | |
| Relationship failing shown? | | | |

### Step 3: Structure Analysis

**Pacing Score** (1-10):

| Element | Score | Notes |
|---------|-------|-------|
| Cold open hook | | |
| Act 1 setup efficiency | | |
| Midpoint impact | | |
| Act 3 escalation | | |
| Climax payoff | | |
| Resolution satisfaction | | |

**Act-Out Strength** (1-10):

| Act | Strength | Why |
|-----|----------|-----|
| 1 | | |
| 2 | | |
| 3 | | |
| 4 | | |

### Step 4: Cliché Detection

Scan for and flag:

**Dialogue Clichés**:
- "We need to talk"
- "It's not what it looks like"
- "You don't understand"
- "I can explain"
- Character says their own theme

**Plot Clichés**:
- Ticking clock appears in final act (if not earned)
- Villain explains plan
- Last-minute save by new information
- Character "just happens" to overhear
- It was all a dream/simulation

**Character Clichés**:
- Detective with drinking problem (unless subverted)
- Mentor dies
- Villain was friend all along (unless planted)
- Character has dead spouse/child motivation

**Score**: {{COUNT}} clichés detected

### Step 5: Theme Integration Assessment

| Element | Theme Present? | How Expressed? |
|---------|----------------|----------------|
| A-Story | | |
| B-Story | | |
| Protagonist arc | | |
| Key dialogue moments | | |
| Visual motifs noted | | |

**Theme Score** (1-10): Is theme present without being preachy?

### Step 6: Relationship Arc Verification

Cross-reference RELATIONSHIP_MAP with script:

| Pair | Axis | Change Planned | Change Shown | Earned? |
|------|------|----------------|--------------|---------|
| | | | | |

**Minimum requirement**: 2 axis changes, 1 negative

### Step 7: Visual Storytelling Assessment

Does the script:
- Show rather than tell?
- Include meaningful visual details?
- Have filmable action (not just dialogue)?
- Create memorable images?
- Support later shot generation?

**Visual Score** (1-10):

### Step 8: Anti-Pattern Check

**Mushy Scenes** (no clear GOTC):
- Scene {{XX}}: {{PROBLEM}}

**Static Scenes** (no change):
- Scene {{XX}}: {{PROBLEM}}

**Exposition Dumps**:
- Scene {{XX}}: {{PROBLEM}}

**Talking Heads** (no action/movement):
- Scene {{XX}}: {{PROBLEM}}

### Step 9: Rubric Scoring

| Category | Weight | Score (1-10) | Weighted |
|----------|--------|--------------|----------|
| Logline Promise Delivery | 15% | | |
| Character Consistency | 15% | | |
| Structure & Pacing | 20% | | |
| Dialogue Quality | 15% | | |
| Theme Integration | 10% | | |
| Visual Storytelling | 10% | | |
| Originality (anti-cliché) | 10% | | |
| Relationship Arcs | 5% | | |
| **TOTAL** | 100% | | |

**Pass Threshold**: 70/100
**Current Score**: {{SCORE}}/100

### Step 10: Verdict

**☐ PASS** - Proceed to visual development
**☐ CONDITIONAL PASS** - Proceed with noted fixes
**☐ FAIL** - Return to {{SKILL}} for revision

## Critique Report Format

```markdown
# Critique Report: EP{{XX}}

## Verdict: {{PASS/CONDITIONAL/FAIL}}
## Score: {{XX}}/100

### Strengths
1. {{STRENGTH}}
2. {{STRENGTH}}
3. {{STRENGTH}}

### Critical Issues (Must Fix)
1. {{ISSUE}} - {{SOLUTION}}
2. {{ISSUE}} - {{SOLUTION}}

### Recommended Improvements (Should Fix)
1. {{IMPROVEMENT}}
2. {{IMPROVEMENT}}

### Minor Notes (Could Fix)
1. {{NOTE}}

### Clichés Detected
- {{CLICHÉ}} at {{LOCATION}} - {{SUGGESTED_FIX}}

### Scene-by-Scene Notes
- SC{{XX}}: {{NOTE}}

### Return To
{{WHICH_SKILL_FOR_REVISION_IF_ANY}}
```

## Veto Conditions

Automatic FAIL if:
- Protagonist flaw is not tested
- No relationship stakes present
- Climax doesn't address central conflict
- More than 5 unaddressed clichés
- Theme is absent or preachy
- Characters are indistinguishable in dialogue

## Notes

- Be rigorous but constructive
- Every criticism needs a suggested path forward
- Celebrate what works—don't only find problems
- Remember the goal is IMPROVEMENT, not perfection
- First draft rarely passes—that's normal
- Trust the process: critique → revision → critique
