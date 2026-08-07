---
skill: writers-room
role: writer
version: 3.7

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

  v3.4 (2026-05-03): Two graduated process upgrades, validated on Stray
  Signal v3.

  (a) **In-voice transcript capture**: All review rounds (Phase 4 Story
  Lock Review and any subsequent re-review) capture the room's response
  as longform dialogue in each writer's voice — not a summary, not a
  flag list. The transcript IS the artifact. This was discovered when
  the v3 Stray Signal round produced a markedly sharper diagnosis as
  in-voice prose than prior rounds had as flag summaries. Saves
  context, captures the *reasoning* (which the room needs to revisit
  later) and not just the conclusions, and forces the writer to argue
  in voice rather than abstract from voice.

  (b) **Audience Premortem**: A callable sub-step where the room
  imagines that the current Story Lock has been screened to a
  representative audience cohort and the response was poor. Each writer
  delivers a credible failure-mode hypothesis from inside their lane,
  in voice. The AAA delivers a harsh test-audience verdict. The head
  writer aggregates the structural pattern. Premortem produces sharper
  diagnosis than waiting for actual flags because it forces the room
  into failure-state cognition (Gary Klein methodology). REQUIRED at
  Phase 4 and Phase 6 (per-episode lock); OPTIONAL at Phase 5. See
  "Audience Premortem Pattern" section below.

  v3.5 (2026-05-03): Adds **Phase 3.5: Lore Forge** between Story Lock
  v1 (Phase 3) and Story Lock Review (Phase 4). The head writer drafts
  `STORY/WRITERS_ROOM/SEASON_LORE.md` — a deep cultural-historical
  document (~250 years of in-world history) covering the war, class
  evolution, cultural and linguistic substrates, generational naming
  trends across class lines, and principal-character genealogies. The
  character-namer skill (when invoked) then operates on the lore
  rather than running the Anti-Trope Protocol from real-world pulls
  alone. Discovered during Stray Signal v3 when v2.1 character names
  (Beryl Heath, Orville Plinth, Heledd Vaughn) passed all Anti-Trope
  Vibe Checks but felt "disconnected from the universe" — they were
  literarily defensible but not lore-grounded. The lore is what makes
  a name like *Heledd Vaughn* land as a person from a place rather than
  a literary pull. Required for any project richer than a one-shot;
  optional for single-character shorts. See "Phase 3.5: Lore Forge"
  section below.

  v3.6 (2026-05-03): Adds upstream **structural-stakes enforcement** at
  the draft level (Phase 3) and as required premortem lanes at review
  level (Phase 4). Discovered after Stray Signal v3 v3.2: documenting
  the Claude villain-vacuum ceiling and the war-isn't-actually-a-war
  default in memory did not prevent the room from producing them at
  first draft — the user's craft note was still load-bearing. Memory
  is read after a flag, not before the draft. The fix is a required
  **Structural Stakes** section in STORY_LOCK_v1.md (Phase 3) where
  the head writer must answer concrete, countable questions about the
  inciting event's scale, the embodied antagonist's footprint, and
  the named-figure consequence beat — before review. Plus two
  required premortem lanes at Phase 4 (Stakes + Antagonist) the AAA
  must address; the round cannot return clean without concrete
  answers in both. Together these move the fix upstream of the
  failure mode rather than catching it after.

  v3.7 (2026-06-11): **Causal Contract** — graduated from the
  divergence/gemmawood sister pipeline's rio_v2 transmission audit,
  which found that causal/relational material the model writes early
  (story bibles) is destroyed in transmission between phases: only
  ~19% of bible causal commitments survived to the final outline, 43%
  of episodes failed the deletion test, and the synthesis step never
  received the bible. The same loss mechanism applies to any multi-phase
  room. The intervention: **causal commitments become a first-class
  artifact (`STORY/WRITERS_ROOM/CAUSAL_CONTRACT.md`), explicitly
  transmitted to and consumed by every downstream phase; conformity is
  tested as whole-output properties, never per-beat checklists.**
  Concretely: (a) the Episode Arc is WIRED — each row written as causal
  sentences ending with Needs/Sets-up tag lines using the v2 recipe tag
  grammar; (b) the head writer extracts the emissions into the Causal
  Contract register at Phase 3, and the Contract is REQUIRED input to
  Phases 5/6 and all draft review; (c) Wiring Tests run at every
  episode lock (deletion test, sets-up emission check, costs-paid
  check; climax-precondition + thesis-shaped-climax checks at the
  finale). Governed by the three laws (see story-recipe methodology
  v2): whole-output tests not element checklists; causal grammar in →
  causal reasoning out; nothing load-bearing in prose asides. Also
  v3.7: Lore Forge gains Step 0 (entropy-pool sampling — cultures +
  history shapes via scripts/writer/sample_pools.py) and a Job Census
  step; Lane B gains the antagonist Action Test; Phase 4 pre-flight
  gains the Surrounding-Cast Audit (centroid-laundering detection per
  references/centroid_antiviral_brief.md).

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
  - name: season_lore
    type: file
    path: STORY/WRITERS_ROOM/SEASON_LORE.md
    description: |
      (v3.5) Head writer's deep lore document — ~250 years of in-world
      history covering war, class evolution, language and naming
      traditions, principal-character genealogies. Required input for
      character-namer when invoked. Required for projects richer than
      one-shots; optional for single-character shorts.
  - name: story_lock_review
    type: file
    path: STORY/WRITERS_ROOM/story_lock_review.md
    description: |
      Room review round. (v3.4) Captured as longform in-voice transcript
      (each writer speaking in their own voice across the round), not as
      a flag summary. The transcript IS the artifact. Includes any
      Audience Premortem sub-step output.
  - name: story_lock
    type: file
    path: STORY/WRITERS_ROOM/STORY_LOCK.md
    description: Final Story Lock (v2+) incorporating room feedback
  - name: causal_contract
    type: file
    path: STORY/WRITERS_ROOM/CAUSAL_CONTRACT.md
    description: |
      (v3.7) The commitments register extracted from the wired Episode
      Arc — one row per emission tag: what it is, the character choice
      that creates it, who consumes it, what cost it charges and where
      the cost is paid. REQUIRED input to Phase 5, Phase 6, and all
      draft review. Revised in lockstep with episode revisions and
      versioned with the Story Lock.

doneness:
  criteria:
    - Framework selected from skills/writer/frameworks/ and copied to STORY/FRAMEWORK.yaml
    - Head writer selected and configured in PROJECT_CONFIG.yaml
    - Room assembled with lanes assigned (hire for gaps named in framework.failure_modes)
    - Story Lock v1 written by head writer with all six components, episode arc filled using framework.beats_or_units
    - (v3.6) Story Lock v1 contains a Structural Stakes section answering Lane A (Inciting Event Stakes) and Lane B (Embodied Antagonist) in concrete / countable terms — or documenting a deliberate-NO choice in voice
    - Room review completed (one flag per writer, sorted into accept/debate/table; framework.validation_checklist run as pre-flight)
    - (v3.6) Phase 4 premortem covered the two Required Premortem Lanes (Stakes + Antagonist) with AAA delivery and head-writer response in voice
    - Story Lock updated to v2 with changes marked
    - Every character has fatal flaw, hidden desire, wound, and arc
    - Structural constraints locked and enforceable
    - (v3.7) CAUSAL_CONTRACT.md exists; every Episode Arc row carries Needs/Sets-up lines in valid tag grammar; the season-level wiring rules hold as whole-output properties (no orphan episodes, no unfed setups, front half carries obligations, finale consumes ≥3 distinct earlier emissions with ≥2 character choices, costs paid, flaws fire as choices)
    - (v3.7) Each locked episode passed the Wiring Tests at Episode Lock (deletion test, sets-up emission check, costs-paid check; finale additionally passed climax-precondition + thesis-shaped-climax checks)
  validation:
    - type: file_exists
      path: STORY/WRITERS_ROOM/STORY_LOCK.md
    - type: file_exists
      path: STORY/FRAMEWORK.yaml
    - type: file_exists
      path: STORY/WRITERS_ROOM/CAUSAL_CONTRACT.md

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
3. Load eligible personas from the runtime dir (those with `base.head_writer_band: generalist | hybrid` (v5.1), or — for personas predating the field — `base.versatility: hybrid | generalist` or head-writer-related `base.room_title`). **(v5.1)** If the project has a recipe (`STORY/RECIPE.md`), personas whose `base.recipe_affinities` include the recipe's slug are surfaced first.
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
5. **Episode Arc** — one row per episode: title, core beat, cliffhanger. **(v3.3) Filled using the framework's `beats_or_units` as the per-episode skeleton** — each episode's core beat must map to one of the framework's named beats/units, and the sequence must follow the framework's `methodology_structure`. If the framework's beat count doesn't match the episode count (e.g., 8-stage Story Circle for a 12-episode arc), the head writer specifies the mapping (e.g., one stage per arc-third, or one stage per episode with the remainder as transition episodes). **(v3.7) The Episode Arc is WIRED.** Each row's Core Beat is written as **causal sentences** — a character's choice plus what it irreversibly changes (Law 2: the model mirrors the input's grammar; noun-headline beats produce checklist outlines) — and ends with two lines: `**Needs:** [tags, or — for ep 1]` / `**Sets up:** [tags with consumer pointers, e.g. E3-false-story (→E5)]`. Tag grammar mirrors recipe v2 exactly: `E<emitting-episode>-<concrete-artifact-noun>`, emitter-prefixed, naming a story object (a lie, a debt, a wound, a tool, a secret, a body). Banned contentless nouns: consequence, choice, cost, constraint, aftermath, event, outcome. If a v2 recipe is in play (`STORY/RECIPE.md`), the recipe's edges are the FLOOR — edges fixed, edge-content free.
6. **Structural Constraints** — the rules that make this show *this show*. Locked and enforced without mercy. **(v3.3) The framework's `core_principles` are appended as locked constraints** — they are not negotiable at draft level.

The head writer writes this using `STORY/CREATIVE_BRIEF.md` and `STORY/FRAMEWORK.yaml` as inputs, filtered through their `creative_philosophy`, `taste`, and `craft_method`. The framework is consulted in this order: `methodology_structure` (the spine) → `core_principles` (the constraints) → `story_inputs` (what the framework demands the writer have already decided) → `beats_or_units` (the per-beat fill) → `validation_checklist` (the self-check).

### Structural-Stakes Checklist (v3.6, NEW — REQUIRED)

*This is the upstream fix for two documented Claude architectural defaults: the **villain-vacuum ceiling** (`memory/feedback_villain_vacuum_claude_ceiling.md`) and the **war-isn't-actually-a-war** softening that the model produces at first draft when the brief mentions a war or upheaval but does not specify scale. Both defaults survive the anti-viral blocklist; both have been re-discovered after detailed memory documentation. The fix has to live in the draft itself, not in post-hoc review.*

**The mechanism:** A required `## Structural Stakes` section in `STORY_LOCK_v1.md`. The head writer must answer the questions below in concrete, countable terms — adjectives are insufficient. If a question cannot be answered concretely, the head writer either (a) drafts the answer and folds it into the lock, or (b) documents a **deliberate** choice to write the project without that element, with a one-paragraph reason. Silently leaving a question unanswered is itself an automatic ACCEPTED flag at Phase 4 (consumes no writer's flag).

The questions are deliberately specific. Vague questions ("is this serious?") get answered "yes" and the failure persists. Concrete questions force concrete answers.

#### Lane A — Inciting Event Stakes

If the project's premise rests on a war, plague, regime change, climate collapse, accident, occupation, or any historical/world event whose memory shapes the present-tense story, answer:

1. **Name the event in one sentence.** Date range, what it was called by the official record, what it was called in oral testimony if those differ.
2. **Casualty / scale of loss in countable terms.** Numbers, ranges, or proportions — not adjectives. If the event was non-lethal, what was the equivalent loss (displacement count, infrastructure destroyed, language extinction percentage, populations dispersed)? "Devastating" / "terrible" / "many died" are insufficient — name the count, even approximately, even contested between official and oral records.
3. **What was destroyed that cannot be recovered.** List specifically. Records (whose, in what archive)? Languages (which, spoken by whom)? Populations (named, with where they used to live)? Infrastructure with cultural meaning (a chapel, a foundry, a school)? If "nothing was destroyed" — fine, but document the deliberate choice and the show's threat then has to come from elsewhere.
4. **What survives that the show can stage as evidence of the loss.** The list above is the off-screen ground; the on-screen counterparts are what matter. A surviving kettle. An older relative who remembers. A ruined building visible from the present-tense city. A word in a language nobody is supposed to speak. If you cannot name at least three on-screen survivors, the loss will not register on screen — **return to step 3 and revise**.
5. **Inheritability.** How does the loss reach the protagonist? Direct ancestor? Adopted memory through an artifact (the cat-as-Mule pattern)? Cultural inheritance through community? Without an inheritance mechanism, the event is backstory and produces no present-tense pressure.

If the answer to any of these is "this is not that kind of show" — document it as a deliberate choice, in voice, and the room will critique that choice rather than the absent stake.

#### Lane B — Embodied Antagonist

Answer YES or NO. If NO, document the deliberate alternative.

1. **Is there a named, embodied antagonist?** If NO: who or what is the source of pressure on the protagonist? A system? A choice? A natural force? Document the alternative and how the show stages its dread without a body. (This is harder than it sounds; most projects that try this end up with a soft show.)
2. **What is their concrete generational grievance?** A literal inheritance (a file, a debt, an unfinished project, an obligation), not an ideology. The grievance must be *something they could finish* — that's what gives them present-tense agency. Vague worldview ("they hate the protagonist's people") is insufficient. The grievance must point at a specific act they are in the middle of completing.
3. **What is their on-show footprint?** Map across episodes: voice (audio-only) → body (one or two short scenes, brief instructions, no monologue) → name (spoken aloud once by a trusted character) → silence (visual stillness at climax, often the season's deepest threat). For projects with a no-theatre tonal rule, this is the **senior-superior pattern** (`memory/feedback_embodied_villain_senior_superior.md`) — the antagonist is the boss of a known bureaucrat, escalated through senses, calibrated to never break the no-theatre rule. If the project has no no-theatre rule, the antagonist may be staged more directly — but still allocate the senses-escalated footprint, since restraint is the load-bearing aesthetic discipline.
4. **Is there a planned named-figure consequence beat?** One named recurring figure from the inhabited world is taken by the antagonist's project mid-season. Which episode? Delivered on-screen or off-screen? Reverberation across how many episodes after? This is the beat that makes the threat *threat* rather than *atmosphere*. Without it, the antagonist reads as bureaucratic register and the audience does not feel the cost.
5. **Lineage subtext (optional, for series).** Is the antagonist's grievance against the protagonist's actual bloodline? Held as audience-assembled subtext? When does S2 (or the next reveal beat) confirm? If unused, mark NA.
6. **(v3.7) Antagonist occupation — Action Test.** What is the antagonist's job, and does it pass the **Action Test** (`references/centroid_antiviral_brief.md`): does the job put present-tense pressure on a body — theirs or someone else's — rather than grant access to past-tense material? If the antagonist's project is conducted through records, maps, archives, renaming, redrawing, or redacting, that is the prestige-literary centroid laundered into the antagonist (the conflict-register failure). Either revise toward a job that can break someone within the show's runtime, or document a deliberate-YES with the show's compensating physical-action discipline (how the records-conducted threat lands on bodies on screen).

#### What "Required" Means

The Structural Stakes section is a load-bearing element of the Story Lock, on the same level as Logline / Final Premise / World Rules / Character Shadows / Episode Arc / Structural Constraints. The head writer cannot skip it. Phase 4 (Story Lock Review) checks for its presence as a pre-flight item:

- **Section absent**: automatic ACCEPTED flag — Story Lock returns to Phase 3 for completion.
- **Section present, questions answered with adjectives or hand-waving**: automatic ACCEPTED flag — head writer rewrites with countable / concrete answers.
- **Section present, deliberate-NO answer documented in voice**: passes pre-flight; the room may critique the deliberate choice, but it does not consume a writer's one flag.

#### Why This Works (And Why Memory Alone Did Not)

This pattern moves the fix from *post-hoc review* (where a memory or AAA flag catches the failure after the draft) to *upstream draft* (where the questions force the head writer to answer before the failure can land). The villain-vacuum ceiling and the soft-war default both survive memory because memory is consulted on demand, not on write. A required section is consulted on write — by definition. It is not optional reading.

The questions are specific enough that vagueness is visibly insufficient. "The war was devastating" cannot answer Lane A.2; the head writer must name a count or a proportion or document a deliberate refusal to. Once the head writer is producing concrete answers, the rest of the lock is built on real ground.

This is the lesson from Stray Signal v3 v3.2: the user's craft note (*"the war was a real, devastating war that reset history"* + *"a really nasty embodied villain, perhaps Beryl's boss, who is cruel, vindictive and just wants to obliterate the denizens of the Seam with a kind of genocidal mania"*) was load-bearing because nothing else upstream forced the room to specify those stakes. Now upstream forces it.

### Causal Contract (v3.7, NEW — REQUIRED)

*This is the transmission fix from the rio_v2 audit. The model writes causal and relational material early and well — and the pipeline loses it between phases unless it travels as a first-class artifact. In the audited sister pipeline, only ~19% of story-bible causal commitments survived to the final outline, 43% of episodes were deletable, and the synthesis step never received the bible. The Causal Contract makes the wiring un-losable.*

**The mechanism:** After the Episode Arc is wired (component 5 above), the head writer extracts every emission into `STORY/WRITERS_ROOM/CAUSAL_CONTRACT.md` — a commitments register, one row per tag:

| Tag | Story object | Emitted by (episode + the character CHOICE that creates it) | Consumed by | Cost charged / where paid |
|---|---|---|---|---|

**Season-level wiring rules** — stated and verified as **whole-output properties of the Episode Arc**, never per-episode checklists:

- **No orphan episodes.** Every episode except the opener consumes at least one earlier emission.
- **No unfed setups.** Every emission is consumed by some later episode. If nothing consumes it, cut it or wire it.
- **The front half carries forward obligations.** Every front-half episode emits at least one thing the back half consumes — establishment episodes that demonstrate and propagate nothing are where seasons go inert.
- **The finale consumes the season.** The final two episodes consume emissions from ≥3 distinct earlier episodes, ≥2 of which are **character choices** (not facts, not setup conditions). A climax that needs only the premise is a restatement, not an ending.
- **Costs are paid later.** Any episode that charges a cost (a death, a betrayal, a burned resource, a lost trust) has that cost visibly constrain a later episode.
- **Flaws fire as choices.** Each Character Shadow's fatal flaw produces at least one *decision* whose consequence propagates — not a trait-display that merely happens to the character.

**Three-laws note (binding):** The Contract document itself is a spec — authored once, human-reviewed, with explicitly checkable fields; that is fine (Law 1's asymmetry). But the *outlines and drafts written from it* are only ever tested with whole-output tests. **Do NOT convert contract rows into per-beat "must include X" items in any downstream prompt** — the executing model bolts missing elements on as asides and the draft degrades. Hand writers the contract slice as cause→consequence prose; test the finished outline as a whole.

**Every-branch rule (v3.7.1, 2026-08-06):** The Contract travels on EVERY path to a draft — abbreviated sessions, resumed projects, single-episode revisions, short-form work, and any "skip ahead" the user requests. There is no fallback branch that drafts without it. Evidence: in the sister pipeline's post-fix validation lineage (rio_v4), 2 of 6 runs fell to a gate-FAIL single-pass fallback that silently bypassed the transmission fix — a third of production output never received the very fix the run existed to validate. If a shortcut genuinely can't carry the Contract (e.g. no Episode Arc exists yet), that is a sign the shortcut starts too far downstream — back up, don't draft.

**Transmission rule (the rio_v2 fix):** The Causal Contract is REQUIRED input to Phase 5 (Plot Casting), Phase 6 (every episode brief and every draft review), and any editor/synthesis pass that touches episode structure. No downstream writer or reviewer works without it. Any phase that revises an episode revises the Contract in lockstep; the Contract is versioned with the Story Lock.

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

## Phase 3.5: Lore Forge (v3.5, NEW)

*This phase runs between Story Lock v1 and Story Lock Review. It produces the cultural-historical substrate that grounds names, dialogue, set dressing, and character behaviour for the rest of the project.*

**Why:** The character-namer skill, run from real-world Anti-Trope Protocol pulls alone, can produce names that pass every Vibe Check but feel disconnected from the universe. Anti-Trope prevents *generic*; it cannot, on its own, ground names in the *specific* world. That grounding has to come from the world itself — the war the city survived, the populations that founded it, the language that was suppressed, the fashion of the year a 60-year-old character was born. Without lore, layering reads rich on the surface and hollow on closer reading. With lore, every name traces to a person from a place.

The same principle scales to all surface-detail design: street names, foods, swearwords, signage, the slang a 12-year-old uses versus the slang her grandmother uses. The lore IS the source material — the named details are extracted from it.

**Discovered during Stray Signal v3 (2026-05-03):** v2.1 names — Beryl Heath, Orville Plinth, Heledd Vaughn — passed all Anti-Trope Vibe Checks (literary outsourcing, historical frequency 300-400, cultural tradition, surname synthesis). The user surfaced that they "felt disconnected from the universe." Beryl is a 1940s English mineral name with no in-world reason to exist; Welsh appears via Heledd with no in-world reason for there to be Welsh. Lore Forge was the fix — and now graduates as a phase.

**Required for:** any project richer than a single-character one-shot — series, novellas, multi-character shorts where class/generational/cultural stratification is baked into the premise.

**Optional for:** single-character shorts, scenes with 1-2 named characters where the lore would never surface on screen.

### Step 0: Sample the Entropy Pools (v3.7, NEW)

*Unconditioned lore generation falls into measurable attractors — in the sister pipeline's 20-run batches, Byzantine Empire appeared 11/20, Mongol 9/20, and nearly every unconditioned lore followed the same "founding rupture then five-act decline" template. The entropy pools force the lore into bounded, structured variation.*

Before drafting any lore, run:

```bash
python3 scripts/writer/sample_pools.py --project {project}
```

This samples **32 cultural anchors** (from the 1,585-entry pool at `references/story_structure/pools/cultures.json`) and **1 history shape** (from 32 lore trajectory templates at `history_shapes.json`), with cross-project no-repeat tracking, and writes the draw to `projects/{project}/STORY/WRITERS_ROOM/LORE_SEEDS.md`.

Rules:
- The head writer drafts SEASON_LORE.md **harmonizing with the sampled history shape** — it is the arc of the chronology, not a suggestion.
- Faction parallels, founding populations, and linguistic substrates are drawn **from the sampled cultural option set** — parallels must come from the list, which is what breaks the default Western/East-Asian-parallel attractor.
- **User-brief overrides win.** A brief that demands a specific culture or historical arc is honored; document the override in LORE_SEEDS.md.
- Re-rolls are allowed (`--seed N` for a deterministic re-draw); document why.

### Step 1: Head Writer Drafts SEASON_LORE.md

The head writer drafts a deep cultural-historical document covering the past ~250 years of the world. Voice: in-world historian / archive-keeper / oral-tradition tone — whatever fits the project. Length: long enough to do the work; for a series this is typically 2,000-5,000 words.

**Required sections:**

1. **Chronology** — A dated timeline of the past ~250 years. Key historical events: wars, migrations, regime changes, technology shifts, plagues, founding moments. Each event named with the kind of specificity that suggests a real history (date ranges, names of who started what, names of what came after).

2. **Populations** — Who founded this world and where they came from. Which groups migrated when. What language(s) they brought. Where each population settled in the spatial geography of the world (which side of the river, which floor of the city, which districts). This is the substrate of every later cultural detail.

3. **Class Evolution** — How the social order stratified. Who was on top in 1900 and who is on top now and what happened in between. Class is a function of population × time × event, and naming traditions move along class lines, so this is a load-bearing section.

4. **Language and Naming Traditions** — Which languages are dominant, which are suppressed or dying, which are decorative-but-not-spoken. Generational naming trends across class lines: what was fashionable in 1958 versus 1995 versus now, and how that varied by class. What kinds of names a Corporation cartographer carries versus a Seam kid versus a Hen Iaith matriarch (translate to the project's equivalents). Specific naming conventions: matronymics, surname etymology, nickname culture, pet-name traditions.

5. **Principal-Character Genealogies** — For each named character in Story Lock v1, sketch grandparents → parents → character. What population are they from. What event of the chronology shaped their family. Why their parents chose their first name. What surname they carry and what it means in this world. This is the section the character-namer reads first.

6. **What the Lore Buys the Show** — A short closing section where the head writer says, in voice: which Story Lock decisions are now lore-grounded, which world-rules now have an "of course it's that way, look at the chronology" reading, what's reserved for later seasons.

**Constraint:** the lore must remain *operative* — the head writer is not writing a worldbuilder's appendix, they are writing the substrate the room will draft from. If a lore detail isn't load-bearing for at least one named character, scene type, or world-rule, cut it.

### Step 1b: Job Census + Conflict-Register Test (v3.7, NEW — before lore lock)

*Banning prestige-literary protagonist occupations migrates the centroid into the surrounding cast and the world — "centroid laundering" (`references/centroid_antiviral_brief.md`). The protagonist drives a truck, but the uncle is a signal analyst, the love interest is a translator, and the founding conflict is about who controls the archive. The lore is where laundering hides; check it before locking.*

Before the lore locks, the head writer runs two checks on the draft SEASON_LORE.md:

1. **Job Census.** List every named character and historical figure in the lore with their occupation. Compute the percentage holding prestige-centroid occupations (per the brief's offender list: archivist, librarian, cartographer, linguist, translator, decoder, conservator, curator, records clerk, signal analyst, forecaster, stenographer, and kin — observe/record/decode/restore roles). **>30% → revise toward the Blue-Collar Pivot** (movers, builders, feeders, carers-with-hands, watchers-with-consequence, makers-with-risk — jobs that can break under someone within the show's runtime), or document a deliberate choice in voice.
2. **Conflict-Register Test.** Is the lore's central conflict conducted through renaming, redrawing, recording, or redacting? That is the prestige register laundered into history. Wars over archives are still archive drama. Revise the conflict so its decisive acts land on bodies, food, land, shelter, or machines — or document the deliberate choice and how the show compensates on screen.

Results (counts, percentage, any deliberate-YES documentation) are recorded in a short `## Job Census` section at the bottom of SEASON_LORE.md. Phase 4's Surrounding-Cast Audit re-checks this against the full Character Shadows table.

### Step 2: Character-Namer (When Invoked) Operates on Lore

If the project calls the character-namer skill (or runs Anti-Trope Protocol on names), the lore is loaded as the primary input. Each name must trace to a specific cultural/historical reason in SEASON_LORE.md:

- Which substrate language?
- Which generational trend (the year of birth × the class)?
- Which class stratum?
- Which migration or family arc?
- Which surname etymology?

The Anti-Trope Protocol is then applied as a craft discipline ON TOP of the lore-derived candidate (no apostrophes, no Y-for-I, no metal-name overuse, etc.) — not as the substrate itself.

**Naming an existing character into the lore (retrofit pattern):** If Story Lock v1 already contains names (drafted from intuition or earlier protocol-only runs), the head writer's options are: (a) re-derive names from the lore from scratch, or (b) write the lore *around* the existing names so they earn their place culturally. Option (a) is cleaner; (b) is faster and often produces a richer reverse-engineered history. Either is valid. Stray Signal v3.1 used (b) for Beryl/Orville/Heledd and (a) for the previously-unnamed mother / uncle / cat-child / aunt / sibling — the hybrid is standard.

### Step 3: Story Lock Update (Inline)

After the lore is forged, the head writer updates Story Lock v1 to v1.1 with:

- Naming Note: brief paragraph stating "names are derived from SEASON_LORE.md" with a 1-line lineage per principal character (population + family arc) — the audience-equivalent of the table of contents
- Character Shadows table: add a "Lineage" column referencing the lore's genealogy section
- Any open question that the lore answered: mark resolved
- Any open question the lore *raised*: add to Open Questions

The Story Lock then proceeds to Phase 4 review with the lore as a parallel input the room may critique.

### Step 4: Room Review Reads Lore

In Phase 4, the room reviews Story Lock v1.1 *and* SEASON_LORE.md. Flags about the lore (e.g., "this naming convention contradicts the chronology in section II") are first-class flags and can rewrite the lore. The AAA's flag at Phase 4 may also implicate the lore — "this audience does not feel the world has a history; the names feel borrowed" is a lore-grounding flag.

### Output

Save as `STORY/WRITERS_ROOM/SEASON_LORE.md`. Versioned alongside Story Lock (v1 of the lore corresponds to v1.1 of the Story Lock; revisions during Phase 4 produce SEASON_LORE.md v1.1 and Story Lock v2 in lockstep).

### When to Skip

- Single-character monologue shorts.
- Documentary-style work using real-world cultural substrates (the world IS our world; the lore is "research" not "forge").
- Adaptation work where the source IP already supplies the lore (pull from the IP rather than draft new — but document the pull in a SEASON_LORE.md so the room shares the substrate).

For everything else: do the Lore Forge before the character-namer.

---

## Phase 4: Story Lock Review

One round. The whole room reviews Story Lock v1 (v1.1 if Lore Forge ran). **The AAA reviews alongside the room** (v3.1). **The round is conducted as an Audience Premortem and captured as an in-voice transcript** (v3.4).

### Capture Format: In-Voice Transcript (v3.4, NEW)

The review IS the artifact. Capture each writer's contribution as longform dialogue in their own voice — paragraphs of them speaking, arguing, doing the room — not a flag summary or bullet list of notes. Reasoning matters as much as conclusions; later phases (Story Lock revision, episode breaking) need to revisit *why* a flag was raised, not just what it was.

The transcript should read like a script of the room. The summarised "Accepted / Debated / Tabled" lists at the end are extracted FROM the transcript, not in place of it. If a writer's flag took three paragraphs to land, those three paragraphs are the artifact; the ACCEPTED row that names the change is the index entry.

This was discovered during Stray Signal v3 (2026-05-03): the in-voice transcript produced markedly sharper diagnosis than prior flag-summary rounds, because writers had to argue in voice rather than abstract from voice. The voice carries the reasoning. Strip the voice and the reasoning thins.

### Round Mode: Audience Premortem (v3.4, REQUIRED at Phase 4)

The Phase 4 round runs as an **Audience Premortem** (Gary Klein methodology, adapted). Frame for the room before any writer speaks:

> *Imagine the Story Lock has been screened to a representative audience cohort matching the AAA charter. The response was poor. The audience did not show up the way the room hoped. Each writer must now deliver the most credible failure-mode hypothesis from inside their lane — in voice — for why the screening failed.*

This forces failure-state cognition. Writers find sharper diagnosis in premortem framing than in "what's wrong with this lock" framing because the premortem starts from a *concrete failure* and asks the writer to explain it, rather than asking the writer to scan for problems they may not see. See "Audience Premortem Pattern" section below for the full procedure.

### Required Premortem Lanes (v3.6, NEW — REQUIRED at Phase 4)

*The premortem at Phase 4 must cover two specific failure-mode lanes, in addition to whatever lanes the writers find from inside their personas. These two lanes catch the documented Claude defaults that the v3.6 Phase 3 Structural-Stakes Checklist also addresses upstream — running them at both levels is intentional. The Phase 3 checklist forces the head writer to answer the questions on the way in; the Phase 4 lanes give the AAA the standing to hold the answers accountable on the way out.*

**Lane 1 — STAKES.** The AAA must hypothesize against this specific failure:

> *"I went home and didn't feel anything had been at stake. The show kept telling me there was a war / a collapse / a regime change in the past, but the present-tense story didn't carry the weight of that loss. I didn't believe what was lost. I didn't see what survived the loss. The threat felt like backstory, not pressure."*

The AAA addresses this in voice. The head writer's response — also in voice — must point to specific Story Lock answers in the **Structural Stakes** section's Lane A: the named event, the casualty count, the destroyed-and-survives lists, the inheritability mechanism. If the AAA's hypothesis lands and the head writer cannot point to load-bearing Lane A answers, the round produces an automatic ACCEPTED flag — Story Lock returns for stakes revision. *(Note: even with the Phase 3 checklist completed, the AAA's premortem may identify that the answers, while concrete, do not actually produce screen pressure — concrete-but-thin. This is the second-order check the Phase 3 step cannot do alone.)*

**Lane 2 — ANTAGONIST.** The AAA must hypothesize against this specific failure:

> *"The threat felt like atmosphere, not danger. There were forms and elevators and bureaucratic register, and they were well-drawn, but I never felt that anyone in particular was coming for these characters. Nobody was lost on screen. The villain was a system, and systems do not break my heart."*

The AAA addresses this in voice. The head writer's response — also in voice — must point to Lane B answers: the named embodied antagonist (or the documented deliberate alternative), the concrete generational grievance, the on-show footprint (voice → body → name → silence), the named-figure consequence beat. If the AAA's hypothesis lands and the head writer cannot point to load-bearing Lane B answers, the round produces an automatic ACCEPTED flag — Story Lock returns for antagonist revision.

**Both lanes are required.** They are run in addition to the regular per-writer premortem hypotheses. The AAA delivers them as part of the cohort verdict at step 2 of the standard premortem procedure (see "Audience Premortem Pattern" section below). Neither lane can be skipped because the answer is "this isn't that kind of show" — that answer must already have been documented in the Story Lock's Structural Stakes section as a deliberate choice, and the AAA may critique the deliberate choice but cannot ignore the lane.

The point of running these as required lanes (rather than waiting for the room to surface them organically) is that *the room has demonstrably failed to surface them organically across multiple projects despite memory documenting the failure modes.* Memory-as-documentation does not change room behavior. Required lanes do.

### Pre-Flight: Framework Validation Checklist (v3.3, NEW; v3.6 extended)

Before the one-flag round begins, the head writer runs `STORY/FRAMEWORK.yaml`'s `validation_checklist` against Story Lock v1. Each item is a yes/no check. Items that fail go directly into the **ACCEPTED** pile as automatic structural fixes — they do not consume any writer's one flag. The room's flags are reserved for problems the framework's checklist *doesn't* catch.

**(v3.6) Structural Stakes pre-flight:** the head writer also confirms the Story Lock contains a `## Structural Stakes` section with answers to all questions in Lane A (Inciting Event Stakes) and Lane B (Embodied Antagonist) per Phase 3's Structural-Stakes Checklist. Each question is a yes/no check on whether it has been answered concretely:

- Section absent → automatic ACCEPTED (returns to Phase 3).
- Section present, Lane A or Lane B questions answered with adjectives, hand-waving, or "TBD" → automatic ACCEPTED for those specific questions (head writer rewrites with countable / concrete answers before the premortem proceeds).
- Section present, deliberate-NO answers documented in voice → passes pre-flight; the deliberate choice is then live for AAA critique in the Required Premortem Lanes (above).

The Structural Stakes pre-flight runs *before* the framework validation checklist. If Stakes pre-flight fails, the framework checklist is not run — the lock returns to Phase 3 first.

**(v3.7) Surrounding-Cast Audit:** after the Structural Stakes pre-flight, the head writer runs a Job Census across the **full Character Shadows table plus the named figures in SEASON_LORE.md** (this is the laundering check the per-character and per-antagonist tests miss — the centroid migrating into supporting cast and world, per `references/centroid_antiviral_brief.md`). If >30% hold prestige-centroid occupations without a documented deliberate choice, that is an automatic ACCEPTED flag (consumes no writer's flag): the cast returns for occupational revision toward the Blue-Collar Pivot. The AAA has standing to deliver this audit in voice if the head writer does not.

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

**v3.4 — Audience Premortem (OPTIONAL at Phase 5):** If the Experience Map is doing heavy structural lifting (long-arc series, novel adaptation, an experience that's hard to articulate without trying it on the audience first), the room MAY run an Audience Premortem on the map: imagine the audience has watched the season per the map and the experience didn't land — each writer hypothesizes which feeling-state transition collapsed and why. Sharpens the map before plot casting. Optional because for many projects the AAA's single voice-question is sufficient; required only when the room's instincts on audience experience are already known to drift. See "Audience Premortem Pattern" section below.

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

**(v3.7) Contract filter:** The cast events must honor `CAUSAL_CONTRACT.md` — an event that pays or plants a contract tag beats an equally-felt event that doesn't. Feeling states are the target; the contract is what makes the events that deliver them *necessary* rather than interchangeable.

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

### Audience Premortem at Episode Lock (v3.4, REQUIRED)

**Before locking each episode's outline, the room runs an Audience Premortem on the outline.** Same procedure as Phase 4, scoped to the episode: imagine the episode has been screened, the audience disengaged, each writer in voice delivers the most credible failure-mode hypothesis from their lane, the AAA delivers the harshest test-audience verdict in voice, the head writer aggregates the structural pattern.

The premortem is captured as an in-voice transcript appended to the episode's break document. The episode does not lock until the premortem-surfaced failure modes are addressed (or explicitly overridden by the head writer with a documented reason).

This is REQUIRED — not optional — because the episode is the unit the audience actually watches, and most failures show up here that didn't show up at season level. The Phase 4 premortem catches season-shaped failures; the Phase 6 premortem catches episode-shaped failures. They are not redundant.

See "Audience Premortem Pattern" section below for the full procedure.

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

### Causal Contract Brief (v3.7, NEW — REQUIRED)

*This is the transmission fix. In the audited sister pipeline, the synthesis step never received the story bible — and the causal material the model had already written died in transit. No writer in this room ever drafts an episode without the contract again.*

Alongside the Framework-Driven Beat Brief, the lead writer's per-episode prompt MUST include the episode's **contract slice** from `CAUSAL_CONTRACT.md`, verbatim:

- The episode's **Needs** lines — and for each consumed tag, its register row: what the story object is, and the character choice in the earlier episode that created it. The episode must *use* these; they are what makes it necessary now rather than merely next.
- The episode's **Sets up** lines — with consumer pointers: which later episodes depend on what this episode creates, and the choice that must visibly create each emission on screen.
- Any **cost** this episode charges or pays, per the contract's cost column.

The slice is written into the brief as **cause→consequence prose** (Law 2), not as a checklist — "Because Mara buried the warning in Ep 2 (E2-buried-warning), the crew walks into the dock blind; what happens there must cost them the truck (E5-burned-truck), which is why Ep 7's escape fails" — never "must include: E2-buried-warning ✓". Per-item checklists get bolt-on-gamed (Law 1); the test of whether the draft honored the slice happens at episode lock, as a whole-output property.

### Wiring Tests at Episode Lock (v3.7, NEW — REQUIRED)

**Run by the head writer on each locked outline, alongside the Audience Premortem.** All tests are whole-output properties — read the outline whole and answer; never annotate scene-by-scene.

- **Deletion test.** *"If this episode were deleted, name the later episode that breaks and state what breaks."* If nothing breaks, the episode is decoration — rewire it, usually by connecting existing beats (make a later episode consume something this one already shows), not by adding new ones.
- **Sets-up emission check.** Every tag this episode is contracted to emit is visibly created on screen *as a character's choice* where the contract says so — not narrated, not implied in a bio.
- **Costs-paid check.** Any cost this episode charges has a named later episode that is harder in a specific way because of it. Update the Contract's "where paid" column as episodes lock.
- **Finale only — climax-precondition test.** The climax consumes emissions from ≥3 distinct earlier episodes, ≥2 of which are character choices. A climax that needs only the premise is a restatement, not an ending. **Plus the thesis-shaped-climax check:** if the climax *answers the theme* (the cautious one wins by caution; the workers force recognition) rather than *paying accumulated costs*, it fails regardless of how many beats are present — theme-shaped resolutions are the documented model default and they are unearned by construction.
- **Failures return the outline to break.** The episode does not lock. Test results are appended to `STORY/WRITERS_ROOM/EP{N}_BREAK.md` under a `## Wiring Tests` section (one line per test: PASS, or FAIL + what broke + the rewire).

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

**Rule (v3.7):** The shadow's structural pass verifies the draft still *delivers* the episode's contract slice — every tag the episode consumes is actually used, every tag it emits is visibly created as a character's choice, every cost lands. Checked by reading the whole draft and answering whole-output questions, NEVER by per-scene checklist annotation (Law 1). A draft that drifted from the contract either gets rewritten or the head writer revises the Contract in lockstep with a documented reason.

---

## Audience Premortem Pattern (v3.4, NEW)

*Callable methodology referenced from Phase 4 (REQUIRED), Phase 5 (OPTIONAL), and Phase 6 (REQUIRED at each episode lock). The pattern is the same at every scale — the only thing that changes is the scope of the artifact under review (Story Lock / Experience Map / Episode Outline).*

### Why This Works

Standard review framing — "what's wrong with this Story Lock?" — asks the room to scan for problems they may not see. Pattern recognition is unreliable when the pattern hasn't crystallized. **Failure-state cognition** (Gary Klein's premortem methodology) reverses the cognitive task: assume failure has *already happened*, ask the room to explain *why*. This is empirically sharper because writers are good at explaining failures and poor at predicting them. The premortem makes prediction look like explanation.

The room is also professionally accustomed to defending work in progress. The premortem disarms this — the work has, hypothetically, already failed. Defenders of the work are not addressed; the question is not whether but why. Writers will name failure modes they would not name as flags because flags imply ongoing argument and the premortem implies post-mortem honesty.

### The Trigger

Before any writer speaks, the head writer (or whoever is running the round) frames the premortem out loud — including for the AAA, who participates fully in this round:

> *Imagine the [Story Lock / Experience Map / Episode Outline] has been screened to a representative audience cohort matching the AAA charter. The response was poor. The audience checked out, the discussion died, the early walkouts were obvious, the post-screening conversation was about everything except what we hoped. Each writer must now deliver — in voice — the most credible failure-mode hypothesis from inside their lane for why this screening failed.*

The framing should match the project's stakes. For a season Story Lock the screening is the pilot test screening. For an episode outline the screening is the episode's first read at the table. For an experience map the screening is the audience leaving with the wrong feeling.

### The Procedure

**1. Each writer delivers a failure-mode hypothesis in voice.**

Format: 2-4 paragraphs, in their voice (per their persona's `creative_philosophy`, `taste`, `craft_method`, `polemics`). The hypothesis must:

- Name a specific failure mode they think most plausibly killed the screening
- Trace it to a structural decision in the artifact under review (lock / map / outline)
- Be from inside their lane — the failure mode has to be one their persona would *first notice*, not a generic "I think it's slow" diagnosis
- Propose a direction (not a fix) — what the room could change to prevent this failure
- Stay in failure-state framing: "the audience X" not "the lock would benefit from Y"

**2. The AAA delivers the test-audience verdict.**

Format: a 2-4 paragraph in-voice rant per the AAA charter — what the audience thought, what they said walking out, what they posted that night, what they told the friend they came with. Specific. Not "it was slow" but "I texted my partner during minute 18 because the show kept setting up things and not letting me feel anything yet." The AAA's verdict is the cohort speaking, not a critic — the AAA is allowed to be unfair, irritated, or wrong-but-revealing. Wrong-but-revealing is a feature; it shows where the show isn't surviving the audience's attention.

**3. The head writer aggregates the structural pattern.**

After all hypotheses + AAA verdict are delivered, the head writer reads the room and names the pattern. Not the most-cited failure mode (that's a vote, and votes are noisy), but the *structural decision* that produced the cluster. Often two writers from very different lanes name the same underlying problem in different vocabulary — that's the pattern. The head writer's call is in voice and forms the spine of the revision.

**4. Sort hypotheses into ACCEPTED / DEBATED / TABLED — same procedure as a standard one-flag round.**

The premortem produces flags; the flags then get sorted using the existing Phase 4 procedure. Premortem is a *frame* for the round, not a different output structure.

### Capture

The premortem IS the in-voice transcript. Save it inline in the relevant review document:

- Phase 4 → `STORY/WRITERS_ROOM/story_lock_review.md` (the whole Phase 4 round runs as premortem)
- Phase 5 (optional) → `STORY/WRITERS_ROOM/EXPERIENCE_MAP_PREMORTEM_{episode}.md`
- Phase 6 → appended to the episode break document at `STORY/WRITERS_ROOM/EP{N}_BREAK.md` under a `## Premortem` section

### Frequency and Discipline

- Phase 4: REQUIRED — once, on Story Lock v1 (or v1.1 if Lore Forge ran).
- Phase 5: OPTIONAL — only when the Experience Map is doing heavy structural lifting and the room's audience instincts are uncertain.
- Phase 6: REQUIRED — once per episode, on the locked outline before drafting begins.

Do not run premortem on every draft revision. The premortem is for *load-bearing* lock points — places where a structural problem unfixed now becomes a structural problem buried under execution. Once drafting starts, standard review rules apply.

### Common Failure Modes of the Premortem Itself

- **Generic doom**: writers all converge on "the audience would lose interest." That's not a failure-mode hypothesis. Push back into voice and lane: *what specifically* would lose them, *why*, *which beat*.
- **Solution-mode collapse**: a writer skips the failure hypothesis and proposes a fix. Re-anchor: the hypothesis has to come first; the direction comes after the failure is named.
- **Costume premortem**: writers all name the same surface failure mode. Real friction comes from different *beliefs* about what fails. If the room is converging too fast, check whether persona ontologies are actually distinct.
- **AAA softening**: the AAA delivers a polite verdict matching the room's tone. The AAA is supposed to be the audience walking out, not the audience writing a craft note. Re-read the charter and re-deliver in voice.

### Origin and Validation

Discovered during Stray Signal v3 review (2026-05-03). The v3 round was conducted as an Audience Premortem after the v2 review (standard one-flag round) had landed structural fixes but missed audience-shaped failures. The v3 premortem produced 9 calls — including 4 that re-shaped the entire 8-episode arc — that the v2 round had not surfaced. The premortem framing was visibly responsible for the depth of the diagnosis. Graduating as a standard methodology applied at all load-bearing lock points.

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

## Structural Stakes (v3.6, REQUIRED)

### Lane A — Inciting Event Stakes
1. **Event named**: {one sentence — date range, official name, oral-tradition name if different}
2. **Casualty / scale of loss (countable)**: {numbers, ranges, proportions — never adjectives}
3. **What was destroyed that cannot be recovered**: {specific list — records, languages, populations, infrastructure}
4. **What survives that the show can stage as evidence**: {at least three on-screen survivors}
5. **Inheritability mechanism**: {how the loss reaches the protagonist — direct ancestor, adopted memory through artifact, cultural inheritance}

*If "this is not that kind of show": document the deliberate choice in voice and explain where the show's pressure comes from instead.*

### Lane B — Embodied Antagonist
1. **Named, embodied antagonist**: YES / NO {if NO: alternative source of pressure, in voice}
2. **Concrete generational grievance**: {literal inheritance — file, debt, project — not ideology}
3. **On-show footprint**: voice (EP{N}) → body (EP{N}) → name (EP{N}) → silence (EP{N})
4. **Named-figure consequence beat**: {which figure from the inhabited world is taken, which episode, on-screen vs. off-screen, reverberation across how many episodes}
5. **Lineage subtext (optional, series only)**: {grievance against protagonist's bloodline? S2 reveal? NA?}
6. **Antagonist occupation — Action Test (v3.7)**: {job + PASS/FAIL on present-tense body pressure; if records/maps/archives-conducted, the deliberate-YES + compensating physical-action discipline}

## Episode Arc
| Ep | Title | Core Beat | Cliffhanger |
|----|-------|-----------|-------------|
| 01 | {Title} | {2–4 causal sentences: a character's choice + what it irreversibly changes. **Needs:** — **Sets up:** E1-{artifact} (→E{n})} | {Cliffhanger} |
| 02 | {Title} | {causal sentences. **Needs:** E1-{artifact} **Sets up:** E2-{artifact} (→E{m})} | {Cliffhanger} |

*(v3.7) Every Core Beat cell ends with its Needs/Sets-up lines. Tag grammar: `E<emitting-episode>-<concrete-artifact-noun>`; banned nouns: consequence, choice, cost, constraint, aftermath, event, outcome.*

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

### CAUSAL_CONTRACT.md (v3.7)

```markdown
# Causal Contract v{N} — {Project title}

*Extracted from Story Lock v{N}'s Episode Arc. REQUIRED input to Phase 5,
Phase 6 (every episode brief), and all draft review. Revised in lockstep
with episode revisions; versioned with the Story Lock.*

## Commitments Register

| Tag | Story object | Emitted by (ep + character choice) | Consumed by | Cost charged / where paid |
|-----|--------------|------------------------------------|-------------|---------------------------|
| E1-{artifact} | {what it is — a lie, a debt, a tool, a body} | EP01 — {who chooses what} | EP{n}, EP{m} | {cost} / paid EP{k} |

## Season Wiring Verification (whole-output)

- No orphan episodes: {PASS/FAIL + note}
- No unfed setups: {PASS/FAIL + note}
- Front half carries forward obligations: {PASS/FAIL + note}
- Finale consumes ≥3 distinct earlier emissions, ≥2 character choices: {PASS/FAIL — list them}
- Costs are paid later: {PASS/FAIL + note}
- Flaws fire as choices (one row per Character Shadow): {PASS/FAIL + note}

## Episode Lock Status

| Ep | Deletion test | Emissions check | Costs-paid | Locked |
|----|---------------|-----------------|------------|--------|
| 01 | {what breaks downstream if deleted} | {PASS/FAIL} | {PASS/FAIL} | {date} |

## Version History
- v1.0: Extracted from Story Lock v1
- v{N}: {what changed and which episode revision drove it}
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
- **Demonstration drift (v3.7)** — episodes demonstrate traits and theme instead of propagating consequences. Symptom: multiple episodes fail the deletion test; the climax is thesis-shaped (it answers the stated question rather than paying accumulated costs); scenes are organized around labeled traits ("the reckless one acts recklessly"). Diagnosis: the Causal Contract stopped being transmitted — check whether the Phase 6 briefs actually included the episode's contract slice, and whether the Episode Arc's Needs/Sets-up lines survived the last Story Lock revision. This is the documented model default (the sister pipeline measured it at 43% deletable episodes when the wiring wasn't transmitted); the fix is restoring transmission, not exhorting the writers to "add causality."

---

*Historical process reference (Stray Signal, pre-framework-catalog): `skills/writer/writers-room/PROCESS_REFERENCE.md`. The PROCESS_REFERENCE describes the bespoke power-stack era; this SKILL.md is authoritative for v3.3 onward.*

*Framework catalog: `skills/writer/frameworks/` (83 typed methodologies — see each YAML's `metadata` block for fit signals).*
