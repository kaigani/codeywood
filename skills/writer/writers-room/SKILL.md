---
skill: writers-room
role: writer
version: 3.3

description: |
  Persona-driven writers room led by a head writer (showrunner). The head
  writer writes Story Lock v1, assembles a room hired for gaps, then runs
  a structured review round. Episode breaking follows with lead writer +
  shadow + standby assignments.

  Process tested on Stray Signal. Reference: PROCESS_REFERENCE.md
  Persona definitions: skills/writer/personas/ (schema: _schema_v5.yaml)
  Framework catalog: skills/writer/frameworks/ (83 typed methodologies)

  v3.1 (2026-04-13): Adds the Antagonistic Audience Archetype (AAA) — a
  brief-tuned audience advocate who delivers adversarial-collaborative
  feedback at every structural decision point in the project. Catches
  auteur drift (the room internalizing its own craft values over the
  audience's experience). The AAA is instantiated during Phase 1 from
  the brief's audience spec, then participates in Phase 4 (Story Lock
  Review), Phase 5 (Experience Map), and at every episode-break review.
  Same AAA mechanism documented in detail in pitch-round skill v2.1.
  See AAA Charter format below.

  v3.2 (2026-04-18): Graduates the anti-viral blocklist into Story Lock
  v1 and the episode-breaking drafts. Validated on the Snowflake 2126
  3-way test (5 Terminal personas × Original vs ACTION-swap vs
  ANTIVIRAL). Appending the blocklist moved cohort mean 102.8 → 39.0
  (Terminal → Mild) — 3x the effect of swapping persona influences.
  The virus (bureaucratic engine, villain vacuum, passive endings,
  institutional containment) lives in Sonnet's default vocabulary and
  structural patterns, not in the references the head writer cites.
  Location: `skills/writer/ANTIVIRAL_PROMPT.md`. The blocklist is
  appended to the head writer's Story Lock prompt and to the lead
  writer's episode-draft prompt as the LAST input, AFTER persona lens
  and AFTER brief. Includes v2 tone-word and tone-move extensions
  (austere, measured, methodical + sentence-level register habits)
  targeting B5 prestige-somber residue that survived the initial
  20-word blocklist.

  v3.3 (2026-05-02): Replaces the bespoke `POWER_STACK.md` with a typed
  framework catalog at `skills/writer/frameworks/` (83 methodologies —
  Dan Harmon, Save the Cat, Kishōtenketsu, Snowflake, Heist, Siege,
  Mystery Box, etc.). Framework selection is a new Phase 0 before AAA
  charter. Each framework's `methodology_structure` and `beats_or_units`
  become the spine of Story Lock (Phase 3) and the lead writer's
  per-beat prompt (Phase 6). Framework's `failure_modes` becomes the
  gap-map for room hiring (Phase 2). Framework's `validation_checklist`
  runs pre-flight in Story Lock Review (Phase 4). Experience Map
  (Phase 5) and AAA stay framework-agnostic — frameworks structure plot,
  experience map structures feeling.

inputs:
  required:
    - name: creative_brief
      type: file
      path: STORY/CREATIVE_BRIEF.md
      description: The foundational story concept
    - name: framework
      type: file
      path: STORY/FRAMEWORK.yaml
      description: |
        The typed structural methodology selected in Phase 0. Copied from
        skills/writer/frameworks/ catalog. Replaces POWER_STACK.md as the
        structural backbone of the writers room.
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
    - Framework selected from skills/writer/frameworks/ and copied to STORY/FRAMEWORK.yaml
    - Head writer selected and configured in PROJECT_CONFIG.yaml
    - Room assembled with lanes assigned (hire for gaps named in framework.failure_modes)
    - Story Lock v1 written by head writer with all six components, episode arc filled using framework.beats_or_units
    - Room review completed (one flag per writer, sorted into accept/debate/table; framework.validation_checklist run as pre-flight)
    - Story Lock updated to v2 with changes marked
    - Every character has fatal flaw, hidden desire, wound, and arc
    - Structural constraints locked and enforceable
  validation:
    - type: file_exists
      path: STORY/WRITERS_ROOM/STORY_LOCK.md
    - type: file_exists
      path: STORY/FRAMEWORK.yaml

dependencies:
  skills:
    - writer/story-intake
  files:
    - STORY/CREATIVE_BRIEF.md
    - STORY/FRAMEWORK.yaml
  directories:
    - skills/writer/personas/
    - skills/writer/frameworks/
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
  framework: dan_harmon_story_circle  # filename (without .yaml) from skills/writer/frameworks/
  head_writer: mick_caffrey           # filename (without .yaml) from skills/writer/personas/
  room:
    - kit_ato
    - gwyn_thompson
    - tad_gridley
    - priya_anand
  lanes:                              # assigned after room assembly
    kit_ato: "structural editing, load-bearing diagnostics"
    gwyn_thompson: "sensory specificity, physical grounding"
    tad_gridley: "escalation stress-testing, volatility"
    priya_anand: "behavioral character specificity"
```

If no configuration exists, run Head Writer Selection first.

---

## Phase 0: Framework Selection (v3.3, NEW)

**Why:** Every writers room runs on *some* structural methodology. Leaving it implicit means the head writer's defaults silently become the show's defaults — usually three-act, usually save-the-cat-shaped, regardless of whether that fits the brief. Making the choice explicit lets the room hire for the framework's known failure modes, draft against its actual beat structure, and review against its validation checklist.

**The catalog lives at `skills/writer/frameworks/`** — 83 typed methodologies, each a YAML with consistent structure (`metadata`, `framework_overview`, `core_principles`, `methodology_structure`, `beats_or_units`, `validation_checklist`, `failure_modes`, `revision_passes`, `visual_storytelling`).

Skip if `STORY/FRAMEWORK.yaml` already exists for this project.

### Mode A: Head Writer Recommends (default)

Requires the head writer to be selected first (run Phase 1 inline if needed).

1. Read `STORY/CREATIVE_BRIEF.md`.
2. Glob `skills/writer/frameworks/*.yaml`. For each candidate, the head writer reads only `metadata.suitable_media`, `metadata.target_lengths`, `metadata.best_for`, `metadata.not_ideal_for`, `metadata.core_principle`, `framework_overview` — fast scan.
3. Head writer shortlists **three frameworks** and writes a ~120-word memo per candidate in voice: why this framework fits THIS brief, what it would force the room to do well, what it would force the room to give up.
4. Present the three memos to the user. User picks one.

### Mode B: Direct User Pick

User names a framework explicitly (e.g., "use kishotenketsu" or "the heist structure"). Skip the recommendation memos. Head writer is shown the choice and writes a one-paragraph "what this means for our room" note.

### Mode C: Auto-Suggest (when brief is sparse)

For projects where the brief is too thin for a head-writer recommendation, filter the catalog by:
- `metadata.suitable_media` matching the brief's medium (animation / live-action / short-form / etc.)
- `metadata.target_lengths` overlapping the brief's runtime
- `metadata.best_for` containing keywords from the brief (genre, mode)

Present the top 5 hits to the user with one-line summaries. User picks.

### After Selection

1. Copy the chosen framework: `cp skills/writer/frameworks/{name}.yaml STORY/FRAMEWORK.yaml`
2. Record the choice in `PROJECT_CONFIG.yaml`:
   ```yaml
   writers_room:
     framework: {name}    # filename without .yaml
   ```
3. The framework is now the structural backbone. It will:
   - **Phase 2** — its `failure_modes` becomes the gap-map for hiring
   - **Phase 3** — its `methodology_structure` and `beats_or_units` shape the Story Lock spine
   - **Phase 4** — its `validation_checklist` runs as pre-flight before the one-flag round
   - **Phase 6** — its `beats_or_units[i]` becomes the lead writer's per-beat prompt; `revision_passes` shape draft review

**Constraint discipline:** Once a framework is selected, the room operates under it. If a flag in Phase 4 says "the framework is wrong for this brief," that flag belongs in the TABLED pile and triggers a return to Phase 0 — not a mid-stream framework swap during Story Lock review.

---

## Phase 1a: Instantiate the Antagonistic Audience Archetype (v3.1, NEW)

**Why:** Personas (including the head writer) tend to internalize and gravitate to their auteur wants and needs. The AAA provides an external perspective representing the brief's actual audience, intervening at every structural decision to keep the room honest. This is distinct from the room's own debates (which adjudicate craft) and from the post-hoc audience-critic in pitch-round Phase 4 (which evaluates output, too late to shape it).

**Instantiation:** Read the brief's audience spec. If unspecified, define it now — every brief has an audience and leaving it implicit is how auteur drift starts.

Write the **AAA Charter** for this project. One-page document defining the archetype's voice for THIS brief specifically.

```markdown
# AAA Charter — {Project title}

## I am
{One paragraph in first person — age, context, attitude. Specific. Not 
"I am the audience." More like: "I am 42. I watch this with my partner 
on a Thursday after work. I'm tired. I will not pause to think."}

## I came for
{One paragraph in MY language — not craft language. Not "earned 
catharsis" — "the part where the lonely person finally gets seen."}

## I will check out if
{Bullet list of disengagement triggers specific to THIS audience.}

## I will forgive
{Bullet list of what this audience tolerates if pleasure lands.}

## I will not forgive
{Non-negotiables.}

## My voice
{Two-three sentences in the archetype's actual voice, capturing 
speech patterns. The AAA's memos will be written in this voice.}
```

Save to `STORY/AAA_CHARTER.md`. The AAA is now active across the project.

**Distinctness:** The AAA is not a writer in the room. The AAA does not pitch, does not write episodes. The AAA is consulted at structural decision points and delivers ~300-500 word memos in voice. The room reads, decides whether to obey, departs from, or override — but the room must ANSWER the AAA, not ignore it.

---

## Phase 1: Head Writer Selection

Skip if `PROJECT_CONFIG.yaml` already has `writers_room.head_writer`.

### Mode A: Elevator Pitch

1. Read `STORY/CREATIVE_BRIEF.md`.
2. Preflight: `python3 scripts/personas/render_persona.py --all --skill writers-room` pre-renders base+room_behavior+architecture per persona into `skills/writer/personas/.runtime/writers-room/`.
3. Load eligible personas from the runtime dir (those with `base.versatility: hybrid | generalist` or head-writer-related `base.room_title`).
4. Each eligible persona delivers a ~150-word pitch in their voice: how they'd approach this project, what they'd optimize for, what they see that others would miss. Draw on their `base.philosophy`, `base.engine`, and `base.polemic`.
4. Present all pitches to the user. User picks.

### Mode B: Generate New

1. User provides a brief describing the kind of head writer they want.
2. Generate a new persona following `skills/writer/personas/_schema_v5.yaml`. Apply the "Discard Your First Instinct" rule rigorously.
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
- **(v3) What is this show's primary experience delivery?** (genre_contract / emotional_register / mode / cultural_idiom / function) — every show makes one of these promises, whether stated or not.
- **(v3) Does the room structurally commit to delivering that promise?** A show promising mass-audience horror delivered through a room of prestige specialists will reliably ship prestige drama with horror garnish.
- **(v3.3) What does the chosen framework already tell us will go wrong?** Read `STORY/FRAMEWORK.yaml`'s `failure_modes` and `not_ideal_for` fields. Each named failure mode is a gap. Hire writers whose `room_behavior.notices_first` or `polemics.hill_they_will_die_on` directly counters those failure modes. A heist-structure project should not assemble a room where nobody owns "the third-act reveal collapses into exposition" — that's a known failure of heist structure and the framework names it.

Then hire to fill those gaps from `skills/writer/personas/`.

### Tonal Register Balance Rule (v3)

A room is tonally trapped when all its writers share the same `primary_experience_delivery.category`. Four prestige specialists writing a room will produce prestige drama even if their mechanisms differ. The fix is structural:

1. **A room must have at least one writer from at least 2 different experience-delivery categories.** A room with a genre_contract specialist, an emotional_register specialist, and a function specialist will produce richer output than three writers who all declared genre_contract.

2. **For pop/mainstream briefs, explicit exclusion of prestige-only specialists by default.** Personas whose `primary_experience_delivery.primary` starts with `prestige-` (e.g., `prestige-restraint`, `prestige-ambiguity`, `prestige-kinetic-stillness`) are designed for art-house work. Include them in pop briefs only when their specific counter-register is genuinely load-bearing.

3. **Audit the assembled room's aggregate `affective_palette`.** If every room member has `restraint_profile: 1-2`, the room will reliably default to melancholic-restrained output regardless of mechanism diversity. At least one room member should have `restraint_profile: 4-5` for any show that needs kinetic energy, emotional directness, or maximalist register.

### Hire for Pleasure Coverage (v3)

What audience pleasure is this show contractually committed to? Hire at least 2 writers who deliver that pleasure with authority (see `pleasure_they_render_with_authority` field). If the show promises "the specific dread of creature-feature horror" but no writer's declared pleasure includes dread, horror, or on-schedule reveal — the room will fail to deliver the show's promise.

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
5. **Episode Arc** — one row per episode: title, core beat, cliffhanger. **(v3.3) Filled using the framework's `beats_or_units` as the per-episode skeleton** — each episode's core beat must map to one of the framework's named beats/units, and the sequence must follow the framework's `methodology_structure`. If the framework's beat count doesn't match the episode count (e.g., 8-stage Story Circle for a 12-episode arc), the head writer specifies the mapping (e.g., one stage per arc-third, or one stage per episode with the remainder as transition episodes).
6. **Structural Constraints** — the rules that make this show *this show*. Locked and enforced without mercy. **(v3.3) The framework's `core_principles` are appended as locked constraints** — they are not negotiable at draft level.

The head writer writes this using `STORY/CREATIVE_BRIEF.md` and `STORY/FRAMEWORK.yaml` as inputs, filtered through their `creative_philosophy`, `taste`, and `craft_method`. The framework is consulted in this order: `methodology_structure` (the spine) → `core_principles` (the constraints) → `story_inputs` (what the framework demands the writer have already decided) → `beats_or_units` (the per-beat fill) → `validation_checklist` (the self-check).

### Anti-Viral Blocklist (v3.2)

Append `skills/writer/ANTIVIRAL_PROMPT.md` as the LAST section of the head writer's Story Lock prompt — after the persona lens, after the brief, after the POWER_STACK. This is the shared anti-viral list graduated from pitch-round v2.6.

The blocklist applies to ALL six Story Lock components. In particular:
- The **Logline** must not introduce the protagonist by institutional title.
- The **Final Premise** must not resolve through a document action, a hearing, or an implication-ending.
- **Character Shadows** must not stack tonal adjectives (austere, measured, methodical) in place of concrete want.
- **World Rules** may describe institutional architecture only as backstory; the drama must be physical.
- **Structural Constraints** that require document-driven or deposition-driven storytelling are virus-captured — rewrite them.

Save as `STORY/WRITERS_ROOM/STORY_LOCK_v1.md`.

---

## Phase 4: Story Lock Review

One round. The whole room reviews Story Lock v1. **The AAA reviews alongside the room** (v3.1).

### Pre-Flight: Framework Validation Checklist (v3.3, NEW)

Before the one-flag round begins, the head writer runs `STORY/FRAMEWORK.yaml`'s `validation_checklist` against Story Lock v1. Each item is a yes/no check. Items that fail go directly into the **ACCEPTED** pile as automatic structural fixes — they do not consume any writer's one flag. The room's flags are reserved for problems the framework's checklist *doesn't* catch.

If more than ~30% of the validation checklist fails, the Story Lock isn't ready for room review. Return to Phase 3 — either the head writer hasn't internalized the framework yet, or the framework choice is wrong (return to Phase 0).

Record the pre-flight result at the top of `story_lock_review.md`:

```markdown
## Framework Pre-Flight ({framework name})
| Checklist item | Pass/Fail | Note |
|---------------|-----------|------|
| {item} | PASS | |
| {item} | FAIL | {what's missing — auto-accepted as fix} |
```

### The Rules

- **One flag per writer.** Not a list of notes — *one flag*. The most important structural problem they see.
- **One flag from the AAA.** (v3.1) The audience advocate reads Story Lock v1 in voice (per `STORY/AAA_CHARTER.md`) and delivers a single flag — the one place where the lock fails THIS audience. Same one-flag discipline as the writers; AAA's flag has equal procedural weight.
- **Every flag comes with a proposed fix or direction.** Not just diagnosis.
- **Flags are heard in full before any debate begins.**
- Each writer's flag is shaped by their persona: their `room_behavior.notices_first`, `polemics.hill_they_will_die_on`, and `craft_method` determine what they see.
- The AAA's flag is shaped by the charter — what THIS audience would not tolerate, would not forgive, would not show up for.

### AAA Flag Format (v3.1)

The AAA reads Story Lock v1 and writes a one-flag memo in voice:

```markdown
## AAA Flag

In voice: "{1-2 paragraph, in the charter's voice, naming the SINGLE 
biggest place this Story Lock fails me. Specific. Not 'too slow' but 
'I would put my phone down at minute 12 because the show keeps 
introducing characters and not letting me care about any of them yet.'
Or: 'I came here for X and I read the entire Story Lock and X never 
arrives.' Or: 'The protagonist's wound is real to me but the way 
it's being investigated is real only to a writers' room.'}"

### Proposed fix
{One direction the room could take to address the flag, also in voice.}
```

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

## AAA (v3.1)
The Antagonistic Audience Archetype: {AAA's flag, in voice + proposed fix}

## Accepted Changes
{What changed and why — note which changes were prompted by AAA flag}

## Debated
{The question, the resolution, who called it. AAA-prompted debates 
should be marked.}

## Tabled
{What, assigned to whom, for which episode}

## What Held
{What the room tested and confirmed was already right}

## AAA Verdict on the Revised Lock (v3.1)
After the room sorts flags into accept/debate/table and revises Story 
Lock to v2, the AAA reads v2 and delivers a one-paragraph verdict in 
voice: "Did the lock improve for me?" If the AAA still won't show up, 
that's a serious flag — Story Lock v3 may be needed before proceeding 
to Experience Map.
```

Update Story Lock to v2 and save as `STORY/WRITERS_ROOM/STORY_LOCK.md`. Mark what changed from v1. Version the document.

**v3.1 escalation:** If the AAA's verdict on Story Lock v2 is "I still won't show up," the room MUST do one of three things before proceeding to Phase 5:
  1. Revise to Story Lock v3 addressing the AAA's persistent concern
  2. Make a conscious, documented decision to override the AAA (the user is choosing to make work for a different audience than the brief specified — fine, but explicit)
  3. Re-examine the brief — is the audience spec wrong?

Silently ignoring the AAA across Story Lock revisions is the failure mode this rule exists to prevent. Auteur drift at the Story Lock level becomes auteur drift at every downstream phase.

---

## Phase 5: Experience Map & Plot Casting

*This phase runs before episode breaking. It is the bridge between what the story IS and what scenes we write. Process adapted from Corey Mandell's "Experience-First" methodology (Coen Brothers, Vince Gilligan school).*

**Core principle:** Do not start with the itinerary (the outline). Start with the purpose of the trip (the experience). Most unsuccessful writers get trapped in the "trees" of an outline. We look at the "forest" of the experience first, then back into the events that create it.

**v3.1 — AAA participation:** The Experience Map IS the audience-experience document. The AAA reads the Experience Map after the room produces it and answers a single question in voice: "Is the experience you mapped the experience I came for?" If the AAA names a gap between the room's mapped experience and the audience's expected experience, the Experience Map is revised before episode breaking begins. This is the natural intersection point — Experience Map asks "what does the audience feel?" and the AAA is the audience's voice.

### Step 1: Define the "Underneath" Experience

Before mapping *what* happens, map *how the audience feels.*

**The "Vacation" analogy:** Every story arc, episode, or scene is a trip. What kind?
- A "honeymoon" (romance/intimacy)
- A "bachelor party" (chaos/excitement)
- A "solo retreat" (reflection/peace)
- A "road trip with someone you're about to break up with" (tension/dread/tenderness)

Name the psychological journey, not the plot. The underneath experience is the feeling the audience can't articulate but their body knows.

**Examples:**
- *Ladybird*: The experience of having to "rip yourself away" from a controlling parent — inherently painful and injurious.
- *Cheers*: The experience of "safety and wholesomeness" in an environment (a bar) that usually feels dangerous or dark.
- *Breaking Bad*: The slow realization that you've been rooting for the wrong person.

### Step 2: The Experience Map (Deliverable)

A literal map of the audience's emotional states from beginning to end. Not plot beats — *feeling states.*

**Format:**

```markdown
# Experience Map: {Episode/Arc Title}

## Underneath Experience
{One sentence: the psychological journey the audience takes}

## The Trip Type
{The vacation analogy — what kind of emotional trip is this?}

## Feeling States (in order)

| # | State | The Audience Is... | Transition Mechanism |
|---|-------|--------------------|---------------------|
| 1 | {feeling} | {what their body is doing} | {what shifts them to the next state} |
| 2 | {feeling} | {what their body is doing} | {what shifts them to the next state} |
| ... | | | |

## The Moment That Earns the Trip
{The single moment where the underneath experience crystallizes — the audience FEELS the theme without anyone saying it}

## What the Audience Takes Home
{The feeling that persists after the screen goes dark}
```

**Scope of application:**
- **Entire story arc**: Map the macro-experience. Cast the major milestones that force the audience to feel that trajectory.
- **Single episode**: Map the emotional arc. Every beat escalates or complicates the underneath experience.
- **Single scene**: Define the underneath experience of a conversation. Is it a "power struggle" or a "failed connection"? Cast the dialogue and actions that create that specific friction.

### Step 3: Soliciting Volume (Writers Room Brainstorm)

Once the Experience Map is set, use the room to generate a massive pool of possibilities.

- **Open solicitations**: Task the writers with pitching as many ideas as possible for each feeling state. Every funny, dramatic, or mundane event that could create that specific feeling.
- **Quantity over quality**: Aim for volume. The goal is to create a pool of events without the pressure of finding the "right" one immediately.
- **No sequencing yet**: Events are unordered. Just a pile of possibilities per feeling state.

### Step 4: Plot Casting (Narrowing to the Plot)

The head writer "casts" the events that best fit the "roles" created by the Experience Map.

**The filter:** Review the brainstormed pool through the lens of the intended experience. Ask: *"Which of these events creates the exact underlying feeling we mapped?"*

**Strategic selection principles:**
- Don't pick the funniest scene — pick the one that establishes the character's heart.
- Don't pick the most dramatic event — pick the one that physicalizes the internal experience.
- *Cheers* cast the scene with the underage kid to prove the lead was a "good guy when no one was looking," establishing the "safe" experience.
- *Ladybird* chose a girl jumping out of a moving car to physicalize the "pain of breaking free."

**Finalizing the plot:** Sequence only the "cast" events. This ensures the plot never feels episodic or lagging — every beat is an escalation of the intended experience.

**Deliverable:** `STORY/WRITERS_ROOM/EXPERIENCE_MAP_{episode}.md` containing the map + the cast events.

---

## Phase 6: Episode Breaking

*This phase runs per-episode, after the Experience Map is finalized.*

### Assign the Team

- **Lead writer** — whose strengths match the episode's hardest problem
- **Shadow** — complementary discipline, reads first draft and brings specific notes
- **Standby** — specialist for the episode's fun engine or specific challenge
- **AAA on call** (v3.1) — at the episode-break review (after the lead writer's first outline), the AAA reads the episode outline and delivers ONE flag in voice: the place this specific episode would lose THIS audience. Same one-flag discipline. The lead writer either revises or documents an explicit override.

### Episode-Level AAA Frequency Rule

Not every per-episode beat needs AAA review — that drowns the room. The rule:
- **Episode 1 (pilot):** AAA reviews the outline AND the first draft (the audience makes their decision in the pilot)
- **Mid-season episodes (any episode that establishes a new arc, shifts tone, or introduces a major character):** AAA reviews the outline only
- **Standard episodes:** No mandatory AAA review; lead writer may request consultation if uncertain
- **Finale episode:** AAA reviews outline AND first draft (the audience's decision to come back next season is made here)

The AAA stays brief-tuned across the project — the same charter from Phase 1a applies through to the finale. If audience expectations evolve mid-project (e.g., a streaming show's audience changes between seasons), the user re-runs Phase 1a to update the charter.

### The Episode Has One Job

Before drafting, the room agrees on one sentence: what is this episode's job?

Not the plot. Not the theme. The *job.* What does the audience feel at the end that they didn't feel at the beginning? This should map directly to the Experience Map's "What the Audience Takes Home."

### The KISS Test

What is the simplest version of this episode that does the job? Complexity is earned by proving the simple version works first.

### Framework-Driven Beat Brief (v3.3, NEW)

For each episode, the lead writer is handed a beat brief assembled from `STORY/FRAMEWORK.yaml`. The brief contains the framework's `beats_or_units` slice that maps to this episode (per the Story Lock's Episode Arc mapping decided in Phase 3). For each beat in scope, include:

- `writer_prompt` — the framework's instruction for what to write
- `story_function` — what this beat does for the plot
- `visual_function` — what this beat does on screen (load-bearing for codeywood's visual-translation pass)
- `emotional_function` — what this beat does to the audience
- `required_decisions` — what the writer must decide before drafting
- `diagnostic_questions` — what to ask while drafting
- `completion_criteria` — when this beat is done
- `common_failure_modes` — what to avoid

This becomes the lead writer's prompt scaffold. The lead writer drafts *to* the framework's beats, not around them. If a beat's `completion_criteria` cannot be met, the writer flags it before drafting more — the framework choice or the Story Lock's beat mapping may be wrong.

### Draft Review

Three parts:

1. **What's working** — specifically. Not "this is good." *This is working because it does X.* The room needs to know what to protect.
2. **What needs work** — specifically. Not "this scene is weak." Identify the structural problem, not just the symptom.
3. **The one note that matters** — one change that unlocks everything else. Name it.

**Rule:** If something made someone feel something real in draft one, it does not get touched in draft two. Protect what works.

**Rule:** If a draft requires more than four structural changes, the draft failed at a higher level than execution. Go back to the episode brief, not the page.

**Rule:** If a scene doesn't escalate the underneath experience from the Experience Map, it doesn't belong — no matter how well-written it is.

**Rule (v3.2):** Every episode draft is written with `skills/writer/ANTIVIRAL_PROMPT.md` appended to the lead writer's prompt. The draft review includes an explicit anti-viral pass — any scene that violates a banned word, banned concept, or banned tone move is flagged. The lead writer rewrites or documents an explicit override. Virus violations are not tonal preferences; they are structural failures that degrade the scene's filmability.

**Rule (v3.3):** Draft review uses the framework's `revision_passes` field (if present) as a structured re-read protocol. Each pass has a single focus (e.g., "structural pass," "character pass," "tension pass," "specificity pass"). The shadow runs the passes in order before bringing notes — preventing the common failure where one diffuse "I read it, here's everything I noticed" critique conflates structural problems with line-level ones. If the framework lacks `revision_passes`, the shadow runs a default three-pass: structural → character → specificity.

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

## Phase 7: Visual Translation Revision

*This phase runs when the Visual Translation Pass (`skills/production/visual-translation/SKILL.md`) flags beats as FAIL and sends revision notes back to the writers room.*

### When This Triggers

After the screenplay is complete, the Visual Translation Pass tests every beat against 7 rules for visual translatability. Beats that fail are sent back with:
- Which rule(s) they violate
- What the beat is trying to DO (its narrative function)
- A proposed visual alternative

### The Revision Rules

1. **Preserve the feeling state.** The experience map's emotional sequence is sacred. Change the mechanism, not the destination.
2. **Accept the constraint.** If the pass says "temperature is invisible," it's invisible. Don't argue — find a visible version of the same beat.
3. **One-for-one replacement.** Every cut beat must be replaced by something that does the same narrative job visually. Don't just delete — substitute.
4. **Annotate changes.** Mark every revision with `[VT-FIX]` and the rule that drove it. The directors room needs to understand why each change was made.
5. **Re-test.** After revision, the screenplay goes through the Visual Translation Pass again. Only fully-passing scripts proceed to the directors room.

### Common Revision Patterns

| Prose Beat | Visual Alternative |
|------------|-------------------|
| Internal state ("files something away") | Physical reaction (face changes, hand goes to mouth) |
| Screen content as story | Screen as light source + dialogue carries intellectual content |
| Micro-movement (2mm jaw shift) | Scale up to visible: catches self smiling, flinches, freezes |
| Gradual transformation | Before/after wide shot, same angle |
| Invisible process (untangling cables) | Show the result, skip the process |
| Background text | Dedicated insert shot held 3+ seconds, or cut |
| Temperature/texture ("it's warm") | Cut — temperature is invisible |
| Subtle environmental change | Make it OBVIOUS and character-reacted-to, or cut |

### Output

Revised screenplay saved as `STORY/SCRIPTS/{episode}_v{N}.md` with `[VT-FIX]` annotations.

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
- **Virus capture (v3.2)** — the draft reads as institutional process, passive endings, villain-absent, interior-static. If the anti-viral pass flags ≥3 violations per episode, the virus has taken hold and the Story Lock (not the draft) likely needs revision — the room's mechanisms are producing document-drama rather than physical story.
- **Framework drift (v3.3)** — the draft no longer maps to the framework's `beats_or_units`. Symptom: the lead writer's draft is "good" in isolation but the room can't say which beat it is delivering. Diagnosis: the writer drafted from intuition and the framework was decoration. Fix: re-anchor to `STORY/FRAMEWORK.yaml` per the Phase 6 Beat Brief and re-draft from the beat the scene is supposed to be doing. Persistent drift across multiple episodes means the framework is wrong for this brief — return to Phase 0 and reselect.

---

*Historical process reference (Stray Signal, pre-framework-catalog): `skills/writer/writers-room/PROCESS_REFERENCE.md`. The PROCESS_REFERENCE describes the bespoke power-stack era; this SKILL.md is authoritative for v3.3 onward.*

*Framework catalog: `skills/writer/frameworks/` (83 typed methodologies — see each YAML's `metadata` block for fit signals).*
