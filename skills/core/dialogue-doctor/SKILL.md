# Dialogue Doctor Skill

## Purpose
Refine and elevate dialogue to ensure distinct character voices, rich subtext, dynamic status play, and zero exposition.

## Trigger
SCRIPT_EP{{XX}}.md exists (first draft complete).

## Inputs Required
- `CHARACTER_SHEETS/*.md` (especially voice profiles)
- `POWER_STACK.md` (dialogue system section)
- `SCRIPTS/SCRIPT_EP{{XX}}.md`

## Outputs Produced
- Revised `SCRIPTS/SCRIPT_EP{{XX}}.md`
- `DIALOGUE_NOTES_EP{{XX}}.md` (optional, for significant changes)

## Process

### Step 1: Voice Audit

For each major character, extract from CHARACTER_SHEET:

| Character | Sent. Length | Vocab Level | Directness | Sarcasm | Metaphor Domain |
|-----------|--------------|-------------|------------|---------|-----------------|
| | | | | | |

Compare to actual dialogue in script. Flag deviations.

### Step 2: Subtext Pass

For every dialogue exchange, ask:
- What does this character WANT in this moment?
- What are they ACTUALLY saying?
- Is there a gap? (There should be)

**Rewrite triggers**:
- Character says exactly what they feel
- Character explains their motivation
- Dialogue could be swapped between characters

**Subtext techniques**:
- Say the opposite of what you mean
- Answer a different question than was asked
- Change the subject to reveal discomfort
- Use physical action to contradict words
- Speak about a "safe" topic that mirrors the real issue

### Step 3: Status Pass

Every exchange has a status dynamic. Identify:
- Who is high status in this scene?
- Who is trying to raise/lower their status?
- Does the status shift during the scene?

**Status markers**:
- HIGH: Fewer words, doesn't explain, comfortable silence, claims space
- LOW: Over-explains, seeks approval, fills silence, makes self small

**Rewrite triggers**:
- Static status throughout (no play)
- Status doesn't match character's position
- No status shifts in important scenes

### Step 4: Exposition Elimination

Search for and destroy:

| Exposition Type | Example | Fix |
|-----------------|---------|-----|
| "As you know, Bob..." | "As you know, we've been partners for 3 years" | Cut entirely or show don't tell |
| Maid-and-butler | Two characters explain plot to each other | Make it conflict, not explanation |
| Recap dialogue | "Remember when you said..." | Trust the audience |
| Feeling statements | "I feel angry about this" | Show through action/behavior |
| Backstory dumps | "Ever since my father died..." | Reveal through present action |

**Allowed exposition**:
- New information one character has, other doesn't
- Information delivered through conflict
- Information that changes the scene dynamic

### Step 5: Private Language Integration

From RELATIONSHIP_MAP, identify private language for key pairs.

Ensure:
- Private terms are used naturally
- They reveal relationship depth
- New viewers can infer meaning from context

### Step 6: Linguistic Fingerprint Check

Verify each character has:
- At least one unique speech pattern
- Consistent vocabulary domain
- Recognizable sentence rhythm

**Test**: Read dialogue aloud. Can you identify speaker without tags?

### Step 7: Conflict Audit

Every scene should have dialogue conflict, even small:
- Someone wants something the other won't give
- Power imbalance being negotiated
- Information being withheld or extracted
- Status being contested

**Rewrite triggers**:
- Characters agree too easily
- Scene is purely informational
- No tension in the exchange

### Step 8: Line-Level Polish

For each line:
- Can it be shorter? (Probably yes)
- Is the verb strong? (Replace weak verbs)
- Does it sound speakable? (Read aloud test)
- Is punctuation creating rhythm? (Periods, dashes, ellipses)

### Step 9: Scene Rhythm Check

Within each scene:
- Vary line lengths (short, medium, long)
- Alternate between rapid-fire and pauses
- Build toward the scene's climax
- End on a strong line or beat

## Quality Checklist

### Per-Character
- [ ] Voice matches CHARACTER_SHEET profile
- [ ] At least one unique linguistic marker present
- [ ] Doesn't sound like other characters

### Per-Scene
- [ ] Clear status dynamic
- [ ] Status shift if significant scene
- [ ] Subtext present (gap between want and say)
- [ ] No pure exposition scenes
- [ ] Conflict present (even subtle)

### Per-Script
- [ ] All major characters distinguishable
- [ ] Private language used where appropriate
- [ ] No "As you know" exposition
- [ ] Dialogue supports visual storytelling
- [ ] Lines are speakable

## Rewrite Examples

### Before (On-the-nose)
```
**ALICE**
I'm really frustrated with this case.
We've been working on it for weeks and
we're no closer to solving it.

**BOB**
I understand your frustration. Maybe
we should take a different approach.
```

### After (Subtext)
```
**ALICE**
Same board. Same photos. Same dead ends.

**BOB**
You skipped dinner again.

**ALICE**
I'm not hungry.

**BOB**
That's not what I asked.
```

### Before (No status)
```
**ALICE**
We need to interview the witness again.

**BOB**
Okay, I'll set it up.

**ALICE**
Thanks.
```

### After (Status play)
```
**ALICE**
The witness. Again.

**BOB**
I already called. She's coming in at four.

Alice pauses. Recalibrates.

**ALICE**
...Good.

**BOB**
*(already walking away)*
You're welcome.
```

## Notes

- Don't change plot or structure
- Focus purely on how things are said
- Flag scenes that need structural fixes (return to story-architect)
- When in doubt, cut dialogue—action can carry it
- Great dialogue often comes from great silences
