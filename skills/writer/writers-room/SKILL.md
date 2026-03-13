---
skill: writers-room
role: writer
version: 3.0

description: |
  Persona-driven writers room led by a head writer (showrunner). The head
  writer writes Story Lock v1, assembles a room hired for gaps, then runs
  a structured review round. Episode breaking follows with lead writer +
  shadow + standby assignments.

  Process tested on Stray Signal. Reference: PROCESS_REFERENCE.md
  Persona definitions: skills/writer/personas/ (schema: _schema.yaml)

inputs:
  required:
    - name: creative_brief
      type: file
      path: STORY/CREATIVE_BRIEF.md
      description: The foundational story concept
    - name: power_stack
      type: file
      path: STORY/POWER_STACK.md
      description: Story structure framework
  optional:
    - name: project_config
      type: file
      path: PROJECT_CONFIG.yaml
      description: May contain writers_room config (head_writer + room list)

outputs:
  - name: story_lock_v1
    type: file
    path: STORY/WRITERS_ROOM/STORY_LOCK_v1.md
    description: Head writer's initial Story Lock (before room review)
  - name: story_lock_review
    type: file
    path: STORY/WRITERS_ROOM/story_lock_review.md
    description: Room review round — flags, debates, decisions
  - name: story_lock
    type: file
    path: STORY/WRITERS_ROOM/STORY_LOCK.md
    description: Final Story Lock (v2+) incorporating room feedback

doneness:
  criteria:
    - Head writer selected and configured in PROJECT_CONFIG.yaml
    - Room assembled with lanes assigned (hire for gaps)
    - Story Lock v1 written by head writer with all six components
    - Room review completed (one flag per writer, sorted into accept/debate/table)
    - Story Lock updated to v2 with changes marked
    - Every character has fatal flaw, hidden desire, wound, and arc
    - Structural constraints locked and enforceable
  validation:
    - type: file_exists
      path: STORY/WRITERS_ROOM/STORY_LOCK.md

dependencies:
  skills:
    - writer/story-intake
  files:
    - STORY/CREATIVE_BRIEF.md
    - STORY/POWER_STACK.md
  directories:
    - skills/writer/personas/
---

# Writers Room

## The North Star

Before any process, before any room:

**Draw a stick figure. Label it "THIS PERSON."**

One specific audience member. Not a demographic. Every decision gets tested against this person. Not "what does the theme require" — *what does this person need right now?*

If you can't answer that, your argument isn't done yet.

---

## Project Configuration

The room is configured in `PROJECT_CONFIG.yaml`:

```yaml
writers_room:
  head_writer: mick_caffrey    # filename (without .yaml) from skills/writer/personas/
  room:
    - kit_ato
    - gwyn_thompson
    - tad_gridley
    - priya_anand
  lanes:                       # assigned after room assembly
    kit_ato: "structural editing, load-bearing diagnostics"
    gwyn_thompson: "sensory specificity, physical grounding"
    tad_gridley: "escalation stress-testing, volatility"
    priya_anand: "behavioral character specificity"
```

If no configuration exists, run Head Writer Selection first.

---

## Phase 1: Head Writer Selection

Skip if `PROJECT_CONFIG.yaml` already has `writers_room.head_writer`.

### Mode A: Elevator Pitch

1. Read `STORY/CREATIVE_BRIEF.md`.
2. Load eligible personas from `skills/writer/personas/*.yaml` (those with `versatility_level: hybrid | generalist` or head-writer-related `room_title`).
3. Each eligible persona delivers a ~150-word pitch in their voice: how they'd approach this project, what they'd optimize for, what they see that others would miss. Draw on their `creative_philosophy`, `taste`, and `polemics`.
4. Present all pitches to the user. User picks.

### Mode B: Generate New

1. User provides a brief describing the kind of head writer they want.
2. Generate a new persona following `skills/writer/personas/_schema.yaml`. Apply the "Discard Your First Instinct" rule rigorously.
3. Save to `skills/writer/personas/{name}.yaml`.
4. User confirms.

Write the selection to `PROJECT_CONFIG.yaml` under `writers_room.head_writer`.

---

## Phase 2: Room Assembly

### Hire for Gaps, Not Prestige

The question is never "who is the best writer?" The question is "what does *this show* need that it doesn't have yet?"

Before any hire, the head writer maps the show's specific vulnerabilities:

- What kind of scene will be hardest to write?
- What failure mode is most likely given the format and constraints?
- What is the emotional core that nobody in the current room owns?

Then hire to fill those gaps from `skills/writer/personas/`.

### For Each Hire, Document:

- **The gap** — what specific vulnerability this writer addresses
- **Their lane** — the domain where their voice is loudest
- **The friction** — where their ontology or taste conflicts productively with others

### Lane Discipline

1. **Lanes are announced and written down.** Not implied. Stated.
2. **Crossing lanes is allowed. Overruling a lane specialist requires justification.** The specialist isn't always right, but overruling them costs something.
3. **The head writer's lane is the stick figure.** That's the job. Everything else is delegated.

Write selections and lanes to `PROJECT_CONFIG.yaml` under `writers_room.room` and `writers_room.lanes`.

---

## Phase 3: Story Lock v1

**The head writer writes the Story Lock alone.** It is not collaborative at this stage. It is a *position* — a strong, specific argument about what the show is — that the room can then test, stress, and improve.

A weak story lock produces a room that argues about fundamentals. A strong story lock produces a room that argues about execution.

### Story Lock Components

1. **Logline** — one sentence. Subject, mechanism, cost, choice.
2. **Final Premise** — one paragraph. The full story, start to finish, including the answer.
3. **World Rules** — numbered. Specific. Every rule that isn't load-bearing gets cut.
4. **Character Shadows** — one row per character: fatal flaw, hidden desire, wound, arc. If a character doesn't have all four, they're not finished.
5. **Episode Arc** — one row per episode: title, core beat, cliffhanger.
6. **Structural Constraints** — the rules that make this show *this show*. Locked and enforced without mercy.

The head writer writes this using `STORY/CREATIVE_BRIEF.md` and `STORY/POWER_STACK.md` as inputs, filtered through their `creative_philosophy`, `taste`, and `craft_method`.

Save as `STORY/WRITERS_ROOM/STORY_LOCK_v1.md`.

---

## Phase 4: Story Lock Review

One round. The whole room reviews Story Lock v1.

### The Rules

- **One flag per writer.** Not a list of notes — *one flag*. The most important structural problem they see.
- **Every flag comes with a proposed fix or direction.** Not just diagnosis.
- **Flags are heard in full before any debate begins.**
- Each writer's flag is shaped by their persona: their `room_behavior.notices_first`, `polemics.hill_they_will_die_on`, and `craft_method` determine what they see.

### After All Flags: Sort Into Three Piles

**ACCEPTED** — Changes that solve real structural problems and don't cost more than they gain. Go into the lock immediately.

**DEBATED** — Changes that solve real problems but require the room to decide *how*, not *whether*. Fast collaborative round. Resolved by argument or head writer call.

**TABLED** — Changes that are right in principle but belong to a specific episode, not the story lock level. Assigned to specific writers.

**There is no "rejected" pile.** If a flag is wrong, the head writer explains why and the conversation moves.

### What the Round Is For

Sequencing of revelations. Structural gaps. Logical inconsistencies. Missing plants. Character arcs that are stated but not scenically embodied.

### What the Round Is Not For

Tone preferences. Aesthetic debates. "I would have done it differently."

### Output

Save the review as `STORY/WRITERS_ROOM/story_lock_review.md`:

```markdown
# Story Lock Review

## Room
Head Writer: {Name} — {Room Title}
{Writer}: {Lane} — {Their one flag + proposed fix}
...

## Accepted Changes
{What changed and why}

## Debated
{The question, the resolution, who called it}

## Tabled
{What, assigned to whom, for which episode}

## What Held
{What the room tested and confirmed was already right}
```

Update Story Lock to v2 and save as `STORY/WRITERS_ROOM/STORY_LOCK.md`. Mark what changed from v1. Version the document.

---

## Phase 5: Episode Breaking

*This phase runs per-episode, typically after the Story Lock is finalized.*

### Assign the Team

- **Lead writer** — whose strengths match the episode's hardest problem
- **Shadow** — complementary discipline, reads first draft and brings specific notes
- **Standby** — specialist for the episode's fun engine or specific challenge

### The Episode Has One Job

Before drafting, the room agrees on one sentence: what is this episode's job?

Not the plot. Not the theme. The *job.* What does the audience feel at the end that they didn't feel at the beginning?

### The KISS Test

What is the simplest version of this episode that does the job? Complexity is earned by proving the simple version works first.

### Draft Review

Three parts:

1. **What's working** — specifically. Not "this is good." *This is working because it does X.* The room needs to know what to protect.
2. **What needs work** — specifically. Not "this scene is weak." Identify the structural problem, not just the symptom.
3. **The one note that matters** — one change that unlocks everything else. Name it.

**Rule:** If something made someone feel something real in draft one, it does not get touched in draft two. Protect what works.

**Rule:** If a draft requires more than four structural changes, the draft failed at a higher level than execution. Go back to the episode brief, not the page.

---

## Output Formats

### STORY_LOCK.md

```markdown
# Story Lock v{N}

## Head Writer
{Name} — {Room Title}

## Logline
{One sentence: subject, mechanism, cost, choice}

## Final Premise
{One paragraph: the full story, including the answer}

## World Rules (Locked)
1. {Rule}
2. {Rule}
...

## Character Shadows
| Character | Fatal Flaw | Hidden Desire | Wound | Arc |
|-----------|------------|---------------|-------|-----|
| {Name}    | {Flaw}     | {Desire}      | {Wound} | {Arc} |

## Episode Arc
| Ep | Title | Core Beat | Cliffhanger |
|----|-------|-----------|-------------|
| 01 | {Title} | {Beat} | {Cliffhanger} |

## Structural Constraints
{The rules that make this show THIS show}

## Sensory Signature
{The dominant textures/sensations of this world}

## Room Credits
| Writer | Lane | Flag | Contribution |
|--------|------|------|-------------|
| {Name} | {Lane} | {Their flag} | {What they changed} |

## Version History
- v1.0: Head writer draft
- v2.0: Post-review ({changes summary})
```

---

## The Room Rules

1. **Test everything against the stick figure.** Emotion felt, not theme understood.
2. **No idea gets killed without a replacement.** Every "no" needs a "what if instead."
3. **Lane discipline.** Crossing allowed. Overruling requires justification.
4. **Animation is physical or it's nothing.** Emotion must become behavior before it hits the page.
5. **The fun engine runs before the theme engine.** Earn the depth.
6. **No defending a scene because you love it.** Love is not a structural argument. Tell us what it's *doing*.
7. **Every scene turns.** Something is different at the end than at the beginning.
8. **Exposition is a confrontation or it's cut.** Information delivered while nothing is at stake is a draft note.
9. **Fight the idea, not the person.**
10. **When the room is lost, go back to the stick figure.**

---

## Story Selection for AI Video Pipeline

The writing pipeline is the strongest link in the current production system. Lean into what it controls:

- **Bottle episodes are the sweet spot**: Two characters, one location, dialogue-heavy, high emotional stakes. These play to Claude's writing strengths and avoid AI video weaknesses (VFX, crowd scenes, action choreography).
- **Analog object motifs**: Simple physical objects (a cup, a key, a photograph) contrasting with complex character psychology. AI video handles objects well; the writing makes them meaningful.
- **Sound as narrative bookend**: Design the same object or sound at opening and close, but with changed meaning. A free storytelling layer the writing pipeline fully controls.

---

## Quality Standards

Watch for these failures:

- **Arguments about fundamentals** — the Story Lock wasn't strong enough. Go back to Phase 3.
- **Echo chamber** — personas agree too easily. Check that their `story_ontology` and `polemics` actually conflict.
- **Costume disagreement** — disagreement on surface details, agreement on assumptions. Real friction comes from different beliefs about what stories ARE.
- **Head writer steamroll** — overruling without engaging. The head writer curates but must show they understood what each member was protecting.
- **Persona drift** — a writer sounds generic. Re-read their YAML `polemics` and `creative_philosophy`.
- **Sensory vacuum** — plot and theme but no physical texture. Someone in the room must own this.
- **Unearned complexity** — failed the KISS test. Strip back to the simplest version that does the job.

---

*Full process reference: `skills/writer/writers-room/PROCESS_REFERENCE.md`*
