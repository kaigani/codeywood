---
skill: visual-translation
role: production
version: 1.0

description: |
  A diagnostic pass that sits between the writers room and directors room.
  Tests every beat in a screenplay against visual translation rules before
  shot planning begins. Beats that fail are pushed back to the writers room
  with concrete revision directions. Beats that pass proceed to the directors room.

  Discovered through Stray Signal EP01 production — the bar scene collapsed
  because prose beats (subtle cat actions, internal states, unreadable screen
  content, invisible environmental changes) were assigned shots instead of
  being flagged and rewritten.

inputs:
  required:
    - name: screenplay
      type: file
      path: STORY/SCRIPTS/{episode}.md
      description: The screenplay to evaluate
  optional:
    - name: experience_map
      type: file
      path: STORY/WRITERS_ROOM/EXPERIENCE_MAP_{episode}.md
      description: Feeling states to preserve during revision
    - name: project_config
      type: file
      path: PROJECT_CONFIG.yaml
      description: Style DNA, modality, format constraints

outputs:
  - name: visual_translation_pass
    type: file
    path: PRODUCTION/{episode}/visual_translation_pass.md
    description: Beat-by-beat diagnostic with PASS/FAIL/MARGINAL ratings and revision notes
  - name: revised_screenplay
    type: file
    path: STORY/SCRIPTS/{episode}_v{N}.md
    description: Revised screenplay with VT-FIX annotations (if revisions needed)

doneness:
  criteria:
    - Every beat in every scene tested against the 4-second rule
    - Every FAIL beat has a concrete visual alternative proposed
    - Revision notes grouped by scene for writers room
    - Summary table of all beats requiring revision
    - If revisions needed, revised screenplay produced with VT-FIX annotations
    - Experience map feeling states preserved (mechanisms may change, emotions must not)
  validation:
    - type: file_exists
      path: PRODUCTION/{episode}/visual_translation_pass.md

dependencies:
  skills:
    - writer/writers-room  # receives revision notes
    - production/directors-room  # consumes passing beats
---

# Visual Translation Pass

## The Core Problem

Elegant prose describes internal states, subtle actions, and conceptual ideas that cannot be communicated in a 3-5 second animation clip. The directors room cannot fix this with better prompts or more clips — it's a writing problem that needs a writing solution.

**Without this pass:** The directors room assigns shots to untranslatable beats. Frame generation produces images that don't communicate the intent. The audience sees a person standing near a wall, not "a person discovering that something precious was taken." Production time is wasted on shots that were doomed from the script stage.

**With this pass:** Every beat is tested before shot planning. Failing beats go back to the writers room with specific revision directions. The directors room only receives beats it can actually produce.

---

## When to Run

Run the Visual Translation Pass:
- **After** the screenplay is written (writers room output)
- **Before** the directors room plans shots
- **After** any screenplay revision that introduces new beats
- **When** a directors room session flags a beat as unproducible (emergency feedback)

This is **not optional**. It is a required pipeline step between writing and shot planning.

---

## The Seven Rules

### Rule 1: The 4-Second Test

**Before assigning a shot, ask: "Can a stranger understand what's happening in this clip in 4 seconds with no dialogue?"**

If the answer is no, the beat needs to be rewritten as a visual action, not assigned a more detailed prompt.

Fails the test:
- "Mumble untangles cables behind the jukebox" (looks like a colored shape near wires)
- "Tabs displays Sol's routing table — it's already cleaner" (can't read screen data at shot scale)
- "The graffiti map has been tidied" (audience never learned what it looked like before)
- "Glenn's jaw unlocks two millimeters" (invisible micro-movement)

Passes the test:
- "The bar goes from messy to spotless" (before/after)
- "Sol's face shifts from warmth to unease" (expression on a face)
- "Glenn's coat moves — something alive inside" (physical comedy)
- "Tabs pushes bolts into a neat line with one paw" (visible action, clear result)

---

### Rule 2: Show Result, Not Process

When the script describes a gradual transformation, don't try to animate the middle. Show the BEFORE state, then cut to the AFTER state. Let the audience's brain fill in the process.

- BAD: 4 clips of individual cats doing 4 different cleaning tasks
- GOOD: 1 clip of messy bar -> 1 clip of same angle, bar is clean. Where did the mess go?

This is more cinematic AND more producible.

---

### Rule 3: Dialogue = Face

**When a character speaks, they fill the frame.** Mid-shot or close-up. Not a two-shot where both characters are small.

Use two-shots for:
- Establishing spatial relationship (once per scene)
- Reaction beats (listener's face while speaker is heard O.S.)
- Scene transitions / scene buttons

Use singles for:
- Every line of dialogue
- Key emotional beats
- Comedy timing (the pause, the look)

This is not a limitation — it's how animation works. Even Pixar cuts to singles for dialogue.

---

### Rule 4: Environmental Storytelling Must Be Obvious

If the ending or key beat depends on the audience noticing something about the environment, it must be:

1. **Established clearly** — dedicated shot, held long enough to register
2. **Changed obviously** — not "one shade cooler" but visibly, unmistakably different
3. **Reacted to by a character** — a face tells the audience how to feel about the change

If the environmental change is too subtle for a character to visibly react to, it's too subtle for the audience. Prose can say "you wouldn't notice unless you were looking." Animation cannot.

- BAD: "The neon feels slightly cooler. One shade." (invisible on screen)
- BAD: "Sol sets a glass at a wrong angle" (too subtle, reads as continuity error)
- GOOD: "The wall of papers is BARE — blank concrete where chaos used to be" (unmissable)
- GOOD: "Sol reaches up and tacks papers back on the wall, CROOKED, deliberately messy" (visible action, clear intention)

---

### Rule 5: One Visual Idea Per Clip

Each clip should communicate exactly ONE thing:
- A character enters a space
- A character says a line
- A character reacts
- An object/environment is revealed
- A transformation is shown

If a clip needs the audience to track two things simultaneously (e.g., "Sol pours a drink while watching Glenn's coat move"), split it into two clips or choose the more important beat.

---

### Rule 6: Concepts Need Characters

Abstract ideas ("entropy is being consumed," "the noise floor is thinning," "optimization destroys what it improves") cannot be shown directly. They must be translated into:

1. A character's emotional reaction (Sol's face)
2. A physical consequence (a wall stripped bare)
3. A concrete visual metaphor (a messy, alive thing becomes sterile and empty)

The script can DESCRIBE the concept. The shot list must show a PERSON experiencing the consequence.

---

### Rule 7: Earn Your Payoff Shots

If the ending depends on the audience recognizing a change, the BEFORE state must be:
- Shown in its own dedicated shot (not background detail)
- Held long enough to register (~3-4 seconds)
- Visually distinctive enough to remember

Then the AFTER shot must be:
- The same angle / same framing (so the comparison is automatic)
- Obviously different (not subtly — unmistakably)
- Followed by a character reaction that tells the audience how to feel

---

## Running the Pass

### Step 1: Scene-by-Scene Beat Extraction

For each scene, extract every beat the screenplay describes. A beat is any discrete action, dialogue, visual detail, or emotional moment.

### Step 2: Test Each Beat

For every beat, ask:
1. Can a stranger understand this in 4 seconds with no dialogue? (Rule 1)
2. Is this showing a process that should be a result? (Rule 2)
3. If dialogue, is the speaker filling the frame? (Rule 3)
4. If environmental, is it obvious and character-reacted-to? (Rule 4)
5. Is this one visual idea, not two? (Rule 5)
6. If conceptual, is it shown through a person? (Rule 6)
7. If a payoff, was the setup earned? (Rule 7)

### Step 3: Rate Each Beat

| Rating | Meaning |
|--------|---------|
| PASS | Translates directly to visual. Ready for directors room. |
| MARGINAL | Could work with careful framing. Note the risk. |
| FAIL | Cannot be communicated visually as written. Must be revised. |

### Step 4: Write Revision Notes

For every FAIL beat, provide:
- **Why it fails** — which rule(s) it violates
- **What the beat is trying to DO** — the emotional/narrative function
- **Proposed visual alternative** — a concrete direction, not "make it more visual"

Group revision notes by scene. Flag scenes that need major restructuring vs. surgical fixes.

### Step 5: Produce Output

**Visual Translation Pass document** (`visual_translation_pass.md`):
```markdown
# {Episode} — Visual Translation Pass

## SC{NN} — {Scene Name} ({time range})

| Beat | Description | 4-Second Test | Status | Notes |
|------|-------------|---------------|--------|-------|
| {beat} | {what a stranger sees} | PASS/FAIL | icon | {notes} |

**Revision notes for writers room:**
- {specific change needed}
- {specific change needed}

---

## SUMMARY: Beats Requiring Writers Room Revision

| Scene | Beat | Problem | Proposed Direction |
|-------|------|---------|-------------------|
| {scene} | {beat} | {rule violated} | {concrete alternative} |
```

**If revisions are needed**, produce a revised screenplay (`SCRIPT_{EP}_v{N}.md`) with `[VT-FIX]` annotations marking every change and which rule drove it.

---

## The Feedback Loop

```
Writers Room → Screenplay
                    ↓
            Visual Translation Pass
                    ↓
            ┌── PASS ──→ Directors Room → Shot List → Production
            │
            └── FAIL ──→ Revision Notes → Writers Room → Revised Screenplay
                                                              ↓
                                                    Visual Translation Pass (re-test)
```

When the directors room encounters a beat that fails these rules mid-session, the response is NOT:
- "Write a better prompt" (production fix for a writing problem)
- "Add more clips to explain it" (pacing death)
- "Hope the audience figures it out" (they won't)

The response IS:
- Flag the beat as visually untranslatable
- Propose a concrete visual alternative
- Push the revision back through this pass
- The writers room rewrites the beat
- THEN the directors room plans the shot

---

## Diagnostic Questions (Pre-Flight)

Before starting the pass, answer these for each scene:

1. **What is the ONE thing this scene must communicate?**
2. **What is the audience supposed to FEEL at the end of this scene?**
3. **Can every beat in this scene pass the 4-second test?**
4. **Is every piece of dialogue covered by a face?**
5. **Are there any "prose beats" masquerading as visual beats?**
6. **Does the ending land on a CHARACTER, not a CONCEPT?**

---

## Common Failure Patterns

These are the most frequent ways prose beats fail to translate visually. Watch for them:

| Pattern | Example | Fix |
|---------|---------|-----|
| **Screen content as story** | "The routing table shows cleaner data" | Screen = light source. Dialogue carries intellectual content. |
| **Internal state as action** | "Files something away behind her eyes" | Cut or replace with visible physical reaction |
| **Micro-movements** | "Jaw unlocks two millimeters" | Scale up: catches himself smiling, hand goes to face |
| **Invisible process** | "Cats untangle cables one by one" | Show BEFORE/AFTER. Skip the process. |
| **Temperature/texture** | "The napkin is warm" | Cut. Temperature is invisible. |
| **Subtle environmental shift** | "The neon feels one shade cooler" | Make it OBVIOUS or cut it. |
| **Background text** | "Wellness check scrolls on wall display" | Needs dedicated insert shot held 3+ seconds, or cut. |
| **Conceptual understanding** | "The audience should understand entropy" | Show a person experiencing a consequence, not the concept. |
| **Gradual transformation** | "Over the next minute, the bar gets cleaner" | Before/after wide shot, same angle. |
| **Prose-only comedy** | "Three centimeters to the left, corrects back" | Simplify to one clear, visible precision action. |

---

## Preserving the Experience Map

When revising beats, the **feeling states** from the experience map are SACRED. You can change the mechanism (HOW the audience arrives at a feeling) but never the destination (WHAT they feel).

Check after every revision:
- Does the experience map's feeling state sequence still hold?
- Did the revision preserve the emotional function of the beat, even if the visual mechanism changed?
- If a beat was cut, does the surrounding material still deliver the same feeling?

---

## Integration with Other Skills

| Skill | Relationship |
|-------|-------------|
| `writer/writers-room` | Receives revision notes. Produces revised screenplays. |
| `production/directors-room` | Consumes passing beats. Flags mid-session failures back to this pass. |
| `production/video-director` | Provides model constraints that inform what "translatable" means. |
| `editor` | May flag post-production issues that trace back to visual translation failures. |
