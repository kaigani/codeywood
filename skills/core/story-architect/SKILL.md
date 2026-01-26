# Story Architect Skill

## Purpose
Design episode structure, beat sheets, and scene breakdowns that execute the story promise while maintaining TV pacing conventions.

## Trigger
CHARACTER_SHEETS and RELATIONSHIP_MAP exist and pass Gate 2.

## Inputs Required
- `CREATIVE_BRIEF.md`
- `POWER_STACK.md`
- `LOGLINE_LOCK.md`
- `CHARACTER_SHEETS/*.md`
- `RELATIONSHIP_MAP.json`

## Outputs Produced
- `EP{{XX}}_BEATS.md` - Episode beat sheet
- `EP{{XX}}_SCENELIST.md` - Detailed scene breakdown
- `SEASON_GRID.md` - Overview of season arc (if building full season)

## Process

### Step 1: Determine Episode Structure

Based on POWER_STACK.md, establish:

| Element | Selection |
|---------|-----------|
| Act Structure | {{4 / 5 / 6 / COLD_OPEN+5}} |
| Episode Length | {{30 / 45 / 60}} minutes |
| A-Story Weight | {{60-70%}} of runtime |
| B-Story Weight | {{20-30%}} of runtime |
| C-Story/Runner | {{0-10%}} of runtime |

### Step 2: Define Story Threads

**A-Story** (Main Plot):
- What is the central problem/goal of this episode?
- How does it connect to the series engine?
- What is at stake?
- How does it test the protagonist's flaw?

**B-Story** (Relationship/Character):
- Which relationship is being stressed?
- What axes are moving? (from RELATIONSHIP_MAP)
- What personal growth is possible?

**C-Story/Runner** (if applicable):
- Light subplot or comic relief
- World-building opportunity
- Setup for future episodes

### Step 3: Create Beat Sheet

Use the appropriate beat sheet template based on act structure.

**Each Beat Must Define**:
1. **What Happens**: External action/event
2. **Why It Matters**: Stakes and consequences
3. **Character State**: Emotional journey position
4. **Relationship Impact**: Which axes move

**Key Beats** (adjust for act structure):

| Beat | Timing | Purpose |
|------|--------|---------|
| Cold Open | 0-3 min | Hook, establish tone, often ends on question |
| Status Quo | Act 1 | Show normal world, plant seeds |
| Inciting Incident | End Act 1 | Force protagonist into action |
| Complication | Act 2 | Initial approach fails |
| Midpoint | ~50% | Major revelation or shift |
| Escalation | Act 3 | Stakes increase, options narrow |
| Dark Moment | End Act 3 | Lowest point, all seems lost |
| Climax | Act 4/5 | Confrontation, decision, action |
| Resolution | Final Act | New status quo, setup next episode |
| Tag | Optional | Emotional button or cliffhanger |

### Step 4: Design Act-Outs

Each act must end with a reason to return:

| Act-Out Type | Description | When to Use |
|--------------|-------------|-------------|
| Question | "What will they do?" | Early acts |
| Revelation | New information changes everything | Midpoint |
| Reversal | Situation flips | Mid-to-late acts |
| Cliffhanger | Immediate danger | Pre-climax |
| Emotional Punch | Character moment | Final act |

### Step 5: Create Scene Breakdown

Convert beats into scenes with:

**Scene Header**:
- Scene number (SC01, SC02...)
- Location ID (for reference generation)
- Time of day
- Characters present

**Scene Content**:
- Goal: What does POV character want?
- Obstacle: What prevents them?
- Turn: How does situation change?
- Cost: What's gained/lost?

**Scene Metadata**:
- Estimated duration
- Mood/tone
- Key props needed
- Visual notes (for shot planning)

### Step 6: Relationship Tracking

Verify RELATIONSHIP_MAP movements:

- [ ] At least 2 axis changes per episode
- [ ] At least 1 negative movement (conflict)
- [ ] Changes feel earned by scene content
- [ ] Arc direction is progressing

### Step 7: Location Planning

List all locations needed:

| Location ID | Scene(s) | Type | Notes |
|-------------|----------|------|-------|
| {{LOC_ID}} | SC01, SC05 | Primary/Secondary | {{VISUAL_REQUIREMENTS}} |

This feeds into reference generation (v0.2).

### Step 8: Pacing Check

Verify timing:

| Act | Page Count | % of Total | Feels Right? |
|-----|------------|------------|--------------|
| Cold Open | | | |
| Act 1 | | | |
| ... | | | |

Adjust scene lengths if pacing is off.

## Quality Gate: Gate 4

**Pass Criteria**:
- [ ] Every act ends with effective act-out
- [ ] A-story and B-story are distinct but thematically linked
- [ ] Protagonist faces want/need tension
- [ ] At least 2 relationship axis movements
- [ ] All scenes have Goal/Obstacle/Turn/Cost
- [ ] Locations are tagged for reference generation
- [ ] Pacing matches genre conventions

**Fail Action**:
- Identify weak acts or mushy scenes
- Restructure before proceeding to screenplay

## Scene Design Principles

### Every Scene Must:
1. Start as late as possible
2. End as early as possible
3. Have a clear POV character
4. Change something (information, relationship, status)
5. Connect to theme (even obliquely)

### Avoid:
- Scenes that only convey information
- Characters explaining their feelings
- Consecutive scenes with same energy level
- More than 2-3 scenes in same location consecutively

### Scene Transitions:
- Cut on action or question
- Contrast (loud→quiet, tense→comic)
- Time jumps should be clear
- Geography should be trackable

## Template: Basic Beat Sheet

```
# {{EPISODE_TITLE}} - Beat Sheet

## Cold Open (0:00-3:00)
**What**:
**Why**:
**Ends on**:

## Act 1 (3:00-12:00)
**Beat 1.1**: Status quo establishment
**Beat 1.2**: Introduction of episode problem
**Beat 1.3**: Inciting incident
**Act Out**:

## Act 2 (12:00-22:00)
**Beat 2.1**: Initial approach
**Beat 2.2**: Complication
**Beat 2.3**: B-story development
**Act Out**:

## Act 3 (22:00-32:00)
**Beat 3.1**: New plan
**Beat 3.2**: Midpoint revelation
**Beat 3.3**: Stakes escalate
**Act Out**:

## Act 4 (32:00-42:00)
**Beat 4.1**: Dark moment
**Beat 4.2**: Insight or decision
**Beat 4.3**: Prepare for confrontation
**Act Out**:

## Act 5 (42:00-52:00)
**Beat 5.1**: Climactic confrontation
**Beat 5.2**: Resolution
**Beat 5.3**: New status quo

## Tag (52:00-54:00)
**What**:
**Sets up**:
```

## Notes

- Beat sheets are STRUCTURE not CONTENT
- Scenes will be expanded by screenplay-writer
- Don't solve dialogue problems here
- Focus on "what happens" not "how it's said"
- Tag locations for visual planning
