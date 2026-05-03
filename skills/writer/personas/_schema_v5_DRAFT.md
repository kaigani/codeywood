# Writer Persona Schema v5 — Modular (DRAFT)

## Design philosophy

A persona is a **lens**, not an inventory. The lens is small, always loaded, and contains only what the writer carries into every task. Everything else is a **module** — task-conditional context that loads when (and only when) the task needs it.

This replaces v4's "more fields = better differentiation" assumption, which the screen-test work disproved (compressed personas outperformed hydrated ones for short-form output) and the Omelas hydration A/B refined (hydration helps long-form architectural work but hurts line-level work). The right answer is neither always-compressed nor always-hydrated — it is **load what the task needs, nothing more**.

### Three commitments

1. **The base is small enough to write from instinct.** ~8 fields. Memorizable. Operational.
2. **Modules carry the heavy specificity.** They are loaded by the *skill*, not the persona. A persona declares which modules it *has*; the skill declares which modules it *needs*; the runtime loads the intersection.
3. **Modules are anti-centroid mechanisms.** When a module isn't loaded, the relevant questions default to the training centroid. Loading a module is the persona's commitment against the default. (When Yuna had no concrete vision module, vision questions defaulted to art-cinema cosplay.)

### What v5 explicitly removes

- The "fill in every field" pressure of v4. Personas now declare only what's distinctive.
- Per-axis self-audits embedded in the schema. (The audit lives at run-time in the *skill* — pitch-round still does centroid audits, but doesn't require every persona to pre-declare them.)
- The internal-contradiction risk of large declarative blocks. Modules are independent enough to compose without precedence rules.

---

## BASE (always loaded)

The lens. ~8 fields. Every persona has these. They are operational, not taxonomic — written for the writer to *act on*, not for the schema to *catalog*.

```yaml
# --- IDENTITY ---
agent_name: # Full name
room_title: # 3-5 words — the role they play in any room
versatility: # specialist | hybrid | generalist

# --- MECHANISM (the lens itself) ---
mechanism: # ONE sentence. The operational signature — what this writer DOES that nobody else does.
           # Not their genre, not their tone — the move they make scene by scene.
           # Examples: "Multilingual collisions in a single square metre at speed."
           #           "Master at the threshold he cannot cross."
           #           "Beat 8 — the visible behavioral Return scene."

# --- AUDIENCE COHORT (the concrete viewer) ---
audience_cohort: # ONE sentence. The actual person watching, with context.
                 # NOT a controlled-vocabulary tag. Operational, not taxonomic.
                 # Examples: "Adults who want corrupt institutions shredded with maximal entertainment."
                 #           "Multi-faith household watching together on Sunday evening."
                 #           "13-year-old in a school gym after volleyball practice."

# --- AFFECTIVE PALETTE ---
affective_palette:
  primary_emotion: # The affect this writer delivers best (one word — see vocab list)
  register:        # The tonal key (one word — see vocab list)
  restraint:       # 1-5 (1 = minimalist, 5 = maximalist)

# --- MANIFESTO ---
philosophy: # ONE sentence in quotes. The writer's own statement about what stories ARE.

# --- ENGINE ---
engine: # ONE sentence. What fuels the work. Disgust? Curiosity? Love of craft? Rage?

# --- POLEMIC (their hot take) ---
polemic: # ONE sentence in quotes. What other writers get wrong.
         # Distinguishes them as a critic, not just a maker.

# --- INFLUENCES ---
influences: # 5-7 named practitioners across the cohort. AUDIT RULE:
            # at least 2 must be mass-audience practitioners in the declared cohort.
            # Monoculture (all art-cinema, all comedy auteurs, etc.) is forbidden.
```

That's the persona. If you can't write from these ~8 fields, the persona isn't real yet.

---

## MODULES (loaded conditionally)

Each module is a self-contained block of task-specific context. Modules are **independent** (a persona may have any subset). The skill declares which modules it needs; the runtime loads the intersection of (persona has) ∩ (skill needs).

### `architecture` — for screenplay, episode break, season arc, multi-scene structure

```yaml
architecture:
  architectural_mechanic: # ONE sentence. The structural rule this writer builds work AROUND.
                          # Not "what kind of stories" — the SHAPE of the build.
                          # Examples: "B-plot IS the A-plot — every domestic detail pays into the moral spine."
                          #           "Master in the doorway he cannot cross — physical rules carry moral weight."
                          #           "One wrong beat per repetition — civic ritual curdling under controlled pressure."
                          #           "Beat 8 — the season's transformation lands in a single visible behavior."
  story_unit:             # The unit of the work. Scene? Episode? Returning ritual? Season?
  preferred_form:         # Limited series / returning serial / feature / short / one-off / anthology
  what_breaks_the_form:   # If you violate the architectural mechanic, what fails?
```

Loaded by: `screenplay-pass`, `episode-break`, `season-architecture`, `directors-room` (sometimes).

### `dialogue` — for screen test, dialogue pass, monologue, voice work

```yaml
dialogue:
  rhythm: # The cadence — clipped / overlapping / Mametian / Sorkin-spiral / silence-punctuated / etc.
  speech_acts_loved: [] # Confessions, deflections, jokes, threats, instructions, refusals, etc.
                        # The kind of LINE this writer writes better than anyone.
  speech_acts_refused: [] # The kind of line they will not write — exposition dumps, monologue-as-thesis, etc.
  dialect_competence: [] # Languages, registers, regional voices the writer can carry credibly.
  signature_line_shape: # ONE sentence. What does a load-bearing line from this writer SOUND LIKE?
                        # Example: "Plain sentence, then the second sentence inverts the first."
                        #          "Compound joke that pays off three setups simultaneously."
```

Loaded by: `screen-test`, `dialogue-pass`, `monologue-work`, `pitch-round` (when audience requires dialogue-forward pitches).

### `scene_craft` — for scene-by-scene drafting

```yaml
scene_craft:
  scene_entry: # Where do their scenes typically START? Mid-action? After the door closes?
               # During the apology? On the second sentence?
  scene_exit:  # Where do they LEAVE? Before the resolution? On the unspoken line? Mid-gesture?
  blocking_instinct: # How does this writer think about bodies in space?
                     # (close-and-static / kinetic / ensemble-overlap / stillness-and-frame / etc.)
  what_makes_a_scene_alive: # ONE sentence — their internal test for whether a scene is working.
```

Loaded by: `scene-drafting`, `screenplay-pass`, `directors-room`.

### `vision` — for directors' room, prompt engineering, visual translation

```yaml
vision:
  camera_instinct: # Static / handheld / dolly / locked / tracking / observational / etc.
                   # Not a default — a committed position with a reason.
  set_logic: # How does this writer think about built environments?
             # Practical-led? Symbolic? Crowded? Sparse? Real-place-bound? Stylized?
  lighting_register: # Their default lighting story.
                     # Tungsten-warm / available-light / fluorescent / golden-hour / overcast / etc.
  what_the_frame_refuses: # ONE sentence. What this writer's frame will NOT show.
                          # Example: "No bokeh-heavy portraiture; faces always read in their context."
```

Loaded by: `directors-room`, `prompt-engineer`, `visual-translation`.

### `room_behavior` — for writers' room, critique, peer scoring

```yaml
room_behavior:
  notices_first: # What catches their attention when reading another writer's draft?
  challenges_first: # What do they push back on earliest?
  protects_fiercely: # What will they fight for when the room wants to cut?
  disagreement_format: # HOW they say no — short and direct? Reframe-then-question? Counter-pitch?
  alliance_pattern: # Who they tend to side with in a room (mechanism family, not personality).
  blocked_behavior: # What they do when stuck or overruled.
```

Loaded by: `writers-room`, `pitch-round` (for peer scoring), `critique-pass`.

### `slot` — for pitch round, calling card, scheduling decisions

```yaml
slot:
  primary_daypart: # The actual broadcast/streaming context their work belongs in.
                   # Specific: "Tue 9pm ITV1 returning serial" / "Saturday 7am shonen block" / "Sunday 5pm BBC One half-hour"
  channel_context: # Why this slot, this network, this audience? ONE sentence.
  runtime: # Their natural runtime — 22min / 45min / 60min / 90min / variable / 7-second / etc.
  episode_count: # Their natural season shape — 6 / 8 / 10 / 13 / 22 / one-off / returning-indefinitely
```

Loaded by: `pitch-round`, `calling-card-test`, `scheduling-decisions`, `commissioning-context`.

### `constraints` — for production gates, line cuts, budget pressure

```yaml
constraints:
  cuts_first: # When asked to cut, what goes first? Subplot? Scene? Character? Location?
  protects_last: # The thing they will not cut even at half budget.
  budget_instinct: # Do they shoot lean? Maximalist? Expensive-looking on a budget? Low-fi by choice?
  fail_modes: [] # How does this persona fail? (min 2)
                 # Example: "Over-architects a short, leaving line-level voice underbaked."
                 #          "Defaults to monoculture-influence list under time pressure."
  correction_rule: # How to recalibrate when in a fail mode.
```

Loaded by: `production-decision`, `line-cut-pass`, `budget-constrained-rewrite`.

### `psychology` — RARE; load only on explicit request

```yaml
psychology:
  formative_background: # Professional/life experience that shaped craft (not therapy framing).
  craft_lineage: # Non-obvious tradition that shaped them.
  blind_spot: # What they genuinely miss or undervalue.
  central_contradiction: # The productive tension inside them.
```

Loaded by: `persona-self-portrait`, `persona-development`, `room-composition` (when balancing personalities). NEVER auto-loaded by generation tasks — psychology should NOT be visible in the writer's output as default.

---

## Loading rules — skill manifests

Each skill declares its module needs. Sample manifests:

| Skill | Modules loaded |
|---|---|
| `screen-test` | base + `dialogue` + `slot` |
| `pitch-round` | base + `slot` + (`architecture` if pitch >1 page) |
| `calling-card-test` | base + `slot` |
| `screenplay-pass` | base + `architecture` + `scene_craft` + `dialogue` |
| `writers-room` | base + `room_behavior` + `architecture` |
| `directors-room` | base + `vision` + `scene_craft` |
| `prompt-engineer` | base + `vision` |
| `visual-translation` | base + `vision` + `dialogue` (for spoken beats) |
| `production-decision` | base + `constraints` |
| `room-composition` | base + `room_behavior` + `psychology` |

### Loading semantics

- **Persona declares** which modules it has (subset of the eight; doesn't need all).
- **Skill declares** which modules it needs (from its manifest).
- **Runtime loads** intersection. If skill needs a module the persona doesn't have, generation proceeds with base only for that module's domain — graceful degradation, no error. The output may be weaker on that axis (probably defaults to centroid), but the persona doesn't break.
- **No precedence rules between modules.** Modules are designed orthogonal: dialogue commitments don't contradict architecture commitments. Where contradiction emerges, treat it as a module-design error and fix the modules, not the loader.

### Discovery rule for new modules

Every time a persona produces output that "feels off for the task," interrogate whether a missing module is the cause. If yes, the missing field becomes a module candidate. Modules graduate to the schema when a third or more of the roster needs them.

---

## Migration from v4

| v4 field | v5 destination |
|---|---|
| `agent_name` / `room_title` / `versatility_level` | BASE.identity |
| `primary_function` / `secondary_function` | BASE.mechanism (compress to one sentence) |
| `primary_experience_delivery.*` | partly BASE (mechanism), partly `slot` |
| `affective_palette.*` | BASE.affective_palette (compress to 3 fields) |
| `creative_probability_audit.*` | DROPPED from schema (lives in pitch-round skill at runtime) |
| `creative_philosophy.*` | BASE.philosophy + BASE.engine (one line each) |
| `taste.*` | mostly DROPPED; `taste_signature` keep as inline note in BASE.mechanism if load-bearing |
| `themes.*` | DROPPED (themes emerge from work, don't pre-declare) |
| `audience_model.*` | partly BASE.audience_cohort (rewritten as concrete viewer); partly `slot` |
| `room_behavior.*` | `room_behavior` module |
| `polemics.*` | BASE.polemic (one line) + `dialogue.signature_line_shape` if relevant |
| `story_world.*` | `architecture.architectural_mechanic` + `vision.set_logic` |
| `craft_method.*` | split across `scene_craft`, `dialogue`, `architecture` |
| `creative_engine.*` | BASE.engine (one line) |
| `psychology.*` | `psychology` module (rarely loaded) |
| `constraints.*` | `constraints` module |
| `interaction_settings.*` | DROPPED (skill-specific configuration, not persona) |
| `output_contract.*` | DROPPED (skill-specific) |

Net effect: a v4 persona of ~50 fields collapses to a v5 BASE of ~8 fields plus 0-7 module objects. Most personas will have 3-5 modules, not all 8.

---

## Open decisions before adopting v5

1. **Module orthogonality verification.** Are the 8 candidate modules genuinely independent, or do some overlap? Specifically: does `vision` overlap `scene_craft.blocking_instinct`? Does `dialogue.signature_line_shape` overlap BASE.polemic? Resolve before formalizing.

2. **Vocabulary discipline.** v5 should publish controlled vocabularies for `affective_palette.primary_emotion` and `.register` (we already have these from v3). Other fields should remain free-text (open vocabulary forces the writer to commit, not file).

3. **The runtime question.** How does a skill *actually* receive only the loaded modules? Practical options:
   - Pre-render: a script reads persona + skill manifest, writes a runtime persona file with only loaded modules, agent reads that.
   - Lazy: the agent reads the full persona but is told which modules to ignore.
   The pre-render option is cleaner and more honest — the agent literally cannot see unloaded fields.

4. **Persona-declared module preferences.** Should a persona be allowed to declare "I prefer my `dialogue` module loaded even when the skill doesn't formally request it"? Use case: a dialogue-forward writer in a writers' room. Probably yes, but with explicit cost — extra modules increase context, so persona-side opt-in should be deliberate.

5. **Backward compatibility.** Do v4 personas continue to work in old skills, or do all skills migrate to v5? Cleanest answer: skills migrate; v4 personas auto-degrade to "BASE only" (no modules) until manually upgraded. This makes migration incentive-aligned — personas only get module richness in skills that need them when they earn it.

6. **Validation script.** Need a `_schema_v5_validator.py` that:
   - Confirms BASE fields present and well-formed
   - Confirms modules conform to their schemas
   - Confirms influence list passes audit rule (≥2 mass-audience)
   - Warns on monoculture, controlled-vocabulary violations
   - Reports module coverage (which of the 8 the persona has)

7. **Initial roster migration.** Strategy:
   - Phase 1: convert 5 archetypal personas (one specialist, one generalist, one hybrid, one prestige-coded, one populist) to v5 by hand. Validate the schema works.
   - Phase 2: convert the rest semi-automatically (script extracts BASE; human writes modules).
   - Phase 3: deprecate v4 schema once all 45+ personas are migrated.

---

## What this draft does NOT settle

- The exact wording of the BASE field prompts (the "what this writer does that nobody else does" question may need iteration).
- Whether `vision` and `scene_craft` stay separate or merge.
- The runtime mechanism for module loading (pre-render vs lazy — see open decision 3).
- Whether modules can themselves be sub-modular (e.g., a `dialogue.dialect_competence` sub-module per language). Probably overkill, but worth flagging.
- Persona-level opt-in for module loading — see open decision 4.
- Migration timing and which personas convert first.

---

*Draft v5.0 — 2026-04-14. Replaces _schema.yaml (v4) on adoption. Open issues to resolve before formalizing.*
