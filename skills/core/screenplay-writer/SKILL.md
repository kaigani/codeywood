# Screenplay Writer Skill

## Purpose
Transform beat sheets and scene lists into industry-standard screenplay format with proper formatting, pacing, and visual storytelling.

## Trigger
EP{{XX}}_BEATS.md and EP{{XX}}_SCENELIST.md exist and pass Gate 4.

## Inputs Required
- `CREATIVE_BRIEF.md`
- `POWER_STACK.md`
- `CHARACTER_SHEETS/*.md`
- `EP{{XX}}_BEATS.md`
- `EP{{XX}}_SCENELIST.md`

## Outputs Produced
- `SCRIPTS/SCRIPT_EP{{XX}}.md` - Complete screenplay in markdown format

## Process

### Step 1: Establish Screenplay Parameters

From inputs, confirm:
- Episode length target (in pages, ~1 page = 1 minute)
- Act break formatting (### ACT BREAK or continuous)
- Scene heading style (INT./EXT. format)
- Dialogue style (character-specific patterns from sheets)

### Step 2: Format Scene Headings

Standard format:
```
### SC01 - INT. PRECINCT BULLPEN - DAY

**Time**: Early morning
**Characters**: ALICE, BOB
**Mood**: Tense anticipation
```

Include visual metadata for shot planning.

### Step 3: Write Action Lines

**Principles**:
- Present tense, active voice
- One paragraph = one shot/moment
- White space creates pacing
- Specific visual details for image generation
- Avoid camera directions (save for shot list)

**Good Action**:
```
Alice stares at the evidence board. Her finger traces the red string
connecting two photos.

Bob enters with coffee. Stops when he sees her expression.
```

**Avoid**:
```
Alice is standing in front of the evidence board and she looks at it
for a while, thinking about the case while touching some of the photos
that are connected by string.
```

### Step 4: Write Dialogue

**Format**:
```
**ALICE**
Three connections. All dead ends.

**BOB**
Maybe you're looking at it wrong.

**ALICE**
*(not turning around)*
Maybe you should get better coffee.
```

**Dialogue Principles** (from POWER_STACK):
1. **Subtext**: Characters rarely say what they mean
2. **Status**: Every exchange has a winner
3. **Voice**: Match CHARACTER_SHEET voice profiles
4. **Anti-Exposition**: Information through conflict

**Parentheticals**: Use sparingly, only when action isn't clear

### Step 5: Manage Pacing

**Scene Length Guidelines**:
- Short scenes (1/2 page): Transitional, single beat
- Standard scenes (1-2 pages): Most dialogue scenes
- Long scenes (3+ pages): Major confrontations, climaxes

**White Space**:
- Break action into short paragraphs
- New paragraph = new visual focus
- Dialogue-heavy scenes need action breaks

**Page Targets by Act** (for 1-hour drama):
| Act | Pages | Purpose |
|-----|-------|---------|
| Cold Open | 3-5 | Hook |
| Act 1 | 8-12 | Setup |
| Act 2 | 10-12 | Complication |
| Act 3 | 10-12 | Escalation |
| Act 4 | 10-12 | Crisis |
| Act 5 | 8-10 | Resolution |
| Tag | 1-2 | Button |

### Step 6: Act Breaks

Format act breaks clearly:

```
---

## ACT TWO

---
```

Ensure each act ends on its designed act-out from the beat sheet.

### Step 7: Visual Metadata

For each scene, include metadata that helps shot planning:

```
**Visual Notes**:
- Lighting: Harsh overhead fluorescent
- Weather: Visible rain through windows
- Key Props: Evidence board, coffee cups, Alice's notebook
- Suggested Shots: Wide establishing, CU on Alice's hands, OTS Bob to Alice
```

### Step 8: Dialogue Polish Pass

After first draft, verify:
- [ ] Each character sounds distinct (blind test)
- [ ] No on-the-nose exposition
- [ ] Subtext is present
- [ ] Status is clear in exchanges
- [ ] Private language used where appropriate
- [ ] Speech patterns match CHARACTER_SHEETS

### Step 9: Read-Through Simulation

Mentally perform each scene:
- Does it play? (Action is filmable)
- Does it flow? (Dialogue is speakable)
- Does it land? (Emotional beats hit)

Flag any scenes that feel flat for dialogue-doctor review.

## Quality Gate: Gate 5

**Pass Criteria**:
- [ ] Page count matches target length
- [ ] All scenes from scene list are present
- [ ] Act breaks are properly placed
- [ ] Dialogue sounds distinct per character
- [ ] Visual metadata is complete
- [ ] No camera directions in action (save for shot list)
- [ ] Subtext is evident (characters don't say what they mean)

**Fail Action**:
- Flag specific scenes/pages
- Proceed to dialogue-doctor for revision

## Screenplay Formatting Reference

### Scene Heading
```
### SC## - INT./EXT. LOCATION NAME - DAY/NIGHT
```

### Action
```
Prose description of what we see. Present tense.

New paragraph for new visual focus.
```

### Dialogue
```
**CHARACTER NAME**
Dialogue here. Natural speech patterns.

**CHARACTER NAME**
*(parenthetical only if needed)*
More dialogue.
```

### Transitions (use sparingly)
```
*CUT TO:*

*SMASH CUT:*

*DISSOLVE TO:*
```

### Simultaneous Dialogue
```
**ALICE** | **BOB**
Line here | Overlapping line
```

### Montage
```
**MONTAGE - ALICE INVESTIGATES**

- Alice at her desk, papers spread everywhere
- Alice interviewing a witness
- Alice at a coffee shop, staring at notes

**END MONTAGE**
```

### Flashback
```
**FLASHBACK - TWO YEARS AGO**

[Scene content]

**END FLASHBACK**
```

## Voice Checklist

Before completing, for each major character:

| Character | Sentence Length | Directness | Sarcasm | Metaphor Domain | ✓ |
|-----------|-----------------|------------|---------|-----------------|---|
| From CHARACTER_SHEET → verify dialogue matches

## Notes

- This is a FIRST DRAFT screenplay
- Dialogue will be refined by dialogue-doctor
- Visual metadata is for production planning
- Don't over-direct in action lines
- Trust the scene structure from beat sheet
- If a scene feels weak, note it—don't restructure
