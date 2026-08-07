---
skill: story-recipe
role: writer
version: 0.2

description: |
  Anchors a project to a commercially-derived genre recipe BEFORE the room
  hires, the framework is picked, or any pitches are written. A recipe is
  the externalized engine of a subgenre — slot definition, emotional
  contract, FFAR+C cast (causally obligated), named trope vocabulary,
  WIRED beat spine (every beat declares Needs/Sets-up causal edges) with
  emotional targets, conformity/variation rules, and whole-output wiring
  tests. Recipes are extracted from 10–15 commercial exemplars per slot,
  not derived from the project being fixed.

  Why this skill exists: Codeywood projects with no slot anchor drift to
  Claude's default literary-prestige centroid regardless of which writers
  are in the room. The persona/AAA/anti-viral stack pushes outward; the
  recipe pulls inward toward a known commercial neighborhood. Together
  they bracket the work.

  Three modes:
    - **Derive** — produce a fresh v2 recipe for a named subgenre slot.
    - **Diagnose** — analyze an existing project against an existing recipe
      (including the wiring tests) and propose surgical fixes.
    - **Rewire** — migrate a v1 (typological) recipe to v2 (wired).

  Source methodology: `references/story_structure/story-recipe-methodology.md`
  Recipe library:     `references/story_structure/recipes/`

  v0.3 (2026-08-06): Mechanical validator ported from gemmawood as
  `scripts/writer/validate_recipe_wiring.py` (all 54 recipes pass).
  Run it on every new/edited recipe; the Claude self-check remains as
  a complement for dramatic judgment, not a replacement for the script.
  Adds the "typology, not script" rule for beat-spine prose (rio_v4
  finding: over-specified beat prose caused 6/6 structural collapse).

  v0.2 (2026-06-11): Methodology v2 (wired recipes). Library populated
  with 54 v2 recipes ported from the divergence/gemmawood sister
  pipeline (each passed a mechanical wiring validator there). Adds the
  wiring step (Needs/Sets-up causal edges, strict tag grammar),
  whole-output wiring tests, the three laws of the executing model,
  Rewire mode, and a Claude-performed wiring self-check (no validator
  script in this repo — Claude runs the checklist).

  v0.1 (2026-05-19): Initial scaffold. Methodology graduated from
  in-conversation work; recipes derived ad-hoc to date (Romantasy from
  Story Chef / Nerdy Novelist transcript; innocent+impossible-tech
  companion was project-specific to stray-signal and intentionally NOT
  generalized into a library recipe). Skill exists so future projects
  start with a slot anchor instead of acquiring one mid-flight.
---

# Story Recipe

## Trigger phrases

- "Derive a [genre] recipe" → DERIVE mode
- "Rewire the [genre] recipe" → REWIRE mode (v1 → v2 migration)
- "What slot does [project] live in?" → SLOT-FIT mode (lightweight DIAGNOSE)
- "Fix [project] against the [genre] recipe" → DIAGNOSE mode
- "Build a recipe library across [genres]" → DERIVE, repeated
- "Compare [project] against three adjacent recipes" → SLOT-FIT, multi-way

## Core principle

A recipe is a working AI prompt only when it externalizes craft knowledge AI cannot supply for itself. Seven mandatory elements (per methodology §"Core principle"):

1. **Functional definitions** (not descriptions) — every role is a job, every flaw is named
2. **Relational definitions** — characters defined in opposition to each other
3. **Stated emotional targets per beat** — what the audience feels, not what happens
4. **Named tropes as deployable units** — naming makes them usable
5. **Explicit conformity vs variation rules** — where to obey, where to invent
6. **Wired beats (v2)** — every beat declares what it consumes from earlier beats (`Needs:`) and what it emits for later beats (`Sets up:`). Sequence tells the model *what order*; wiring tells it *what makes each beat necessary*. Without edges, the model writes ten demonstrations of the premise; with edges, it must write consequences.
7. **Whole-output conformity tests (v2)** — causality verified as a property of the finished outline (can any episode be deleted? does the climax consume earlier choices?), never per-beat "must include X" items.

A recipe missing any of the seven degrades into a description and stops working as a prompt. Read the methodology file first if any element is unclear.

### The three laws (binding for all recipe work)

Learned empirically from the divergence pipeline's executing model; they shape everything in v2:

- **Law 1 — Checkable per-unit rules get bolt-on-gamed.** Story-level demands on the *output* must be whole-output properties ("no episode is deletable"), never element checklists. The recipe *document* is a spec, authored once and human-reviewed — it may use explicit checkable fields (Needs/Sets-up lines).
- **Law 2 — The model mirrors the input's grammar.** Beats written as cause→consequence sentences produce causal reasoning; noun-headline scene labels produce checklist reasoning.
- **Law 3 — Caveats are dead text.** Anything load-bearing goes into the beat spine, the cast table, or the conformity tests — never into a Caveats aside.

---

## When to invoke

**Always before Phase 0 of writers-room** if the project has no `STORY/RECIPE.md` yet. The recipe constrains framework selection, room hiring, and AAA charter — making it the natural first step.

**Diagnose mid-flight** when:
- A project's pitch round, story lock, or first episode has landed weaker than expected
- The project conforms to none of the obvious adjacent recipes (or violates one without intent)
- The room is producing work that scans as "literary" or "elevated" when the brief asked for commercial

**Skip the skill** when:
- The brief explicitly rejects formula (voice-driven literary slipstream, art-house, theme-driven prestige)
- The slot is genre-of-one (no 5+ commercial exemplars exist)

---

## Mode A — Derive

Produce a v2 recipe for a named subgenre slot. The 8-step procedure from `story-recipe-methodology.md`:

1. **Name the emotional contract** — 3–4 word cocktail
2. **Pick the subgenre slot** — narrow enough to find 10+ exemplars; broad enough to find 5+
3. **Pull the corpus** — 10–15 commercial exemplars, tonally diverse, NOT including the project being fixed
4. **Extract the FFAR+C cast** — Function / Flaw / Causal obligation / Arc (with turn beat) / Relational position, 5–7 roles. Every flaw is a loaded spring: name what it CAUSES and which beat consumes it. The antagonist-function role carries a HUMAN motive, not a job description.
5. **Catalog tropes** — recurring units across 3+ exemplars get a name + functional definition. Include anti-tropes. Tropes stay *unwired* — texture vocabulary; the wiring lives in the spine and cast.
6. **Map the beat spine** — sized to the genre's unit, each beat written as a **causal sentence** (a character's choice + what it irreversibly changes — Law 2) carrying an **audience-emotion** target (never a theme demonstration). **Typology, not script**: a beat cell names the *function* and the *edges*, never the specific action, agent, or scene content. If the beat prose reads like a scene the writer could transcribe, it WILL be transcribed — rio_v4 evidence (2026-06-11): six independent runs off one over-specified cyberpunk spine produced six identical causal skeletons, including the no-persona baseline. Concrete illustrations go in a clearly-labelled example the writer must vary from, not in the beat cell.
7. **Wire the spine** — append `**Needs:**` / `**Sets up:**` lines to every beat cell. Tag grammar: `E<emitting-episode>-<concrete-artifact-noun>` (emitter-prefixed, one name for the artifact's whole life). Apply the six wiring rules: no orphan beats; no unfed setups; front half carries forward obligations; final two beats consume ≥3 distinct earlier emissions (≥2 character choices); costs are paid later; flaws fire as choices.
8. **State conformity + variation rules + the fixed Wiring-tests block** — conformity rules are genre-specific; the Wiring-tests block is copied VERBATIM from the methodology template between them; variation rules note that edges are fixed but edge-content is free.

Output to `references/story_structure/recipes/{slug}.md`, using `RECIPE_TEMPLATE.md` in this directory. Add a one-line entry to `references/story_structure/recipes/README.md` under "Library."

### Mechanical validation (run before filing ANY recipe)

Run the ported gemmawood validator on every new or edited recipe:

```bash
python3 scripts/writer/validate_recipe_wiring.py references/story_structure/recipes/{slug}.md
```

It enforces tag grammar, banned contentless nouns, graph closure, orphan beats,
front-half obligations, climax preconditions, the verbatim Wiring-tests block,
and repeated-8-gram template detection. The checklist below remains as Claude's
complementary self-check (the validator can't judge whether an edge is
*dramatically* good):

- [ ] **Tag grammar** — every tag matches `E<digit(s)>-<lowercase-hyphenated-noun>`; the noun names a concrete story object. Banned contentless nouns: `consequence`, `choice`, `cost`, `constraint`, `aftermath`, `event`, `outcome`.
- [ ] **Emitter-prefixed** — every tag's `E<n>` prefix is the beat that EMITS it (appears in that beat's Sets-up line), never the consumer.
- [ ] **Graph closure (both directions)** — every `Needs:` tag points at a real earlier `Sets up:`; every `Sets up:` tag is consumed by some later beat's `Needs:`.
- [ ] **No orphan beats** — every beat except the opener has at least one Needs entry.
- [ ] **Front-half obligations** — every beat in the front half (roughly beats 1–4 of 10) emits at least one tag the back half consumes.
- [ ] **Climax preconditions** — the final two beats together consume emissions from ≥3 distinct earlier beats, ≥2 of which are character choices.
- [ ] **Wiring-tests block verbatim** — the fixed block from the methodology template appears unmodified between Conformity rules and Variation rules.
- [ ] **No template boilerplate** — no beat carries generic filler like "leaves a consequence unresolved" in place of genre content.

If any check fails, fix the wiring before filing — usually by connecting existing beats, not adding new ones.

### Corpus discipline

- **Commercial successes, currently preferred over classic.** Classics often broke the formula that later codified into the formula; readership/viewership conformity is the signal you want.
- **Tonal diversity within the slot.** *Wall-E* (warm) and *Cyberpunk: Edgerunners* (brutal) both fit innocent+companion — that's evidence the recipe is real and not a tone description.
- **Never include the project being fixed.** Deriving from your own canon produces a recipe-shaped self-description and defeats the methodology.

---

## Mode B — Diagnose

Given a project AND a recipe (existing or freshly derived), produce a surgical fix list. The 6-step procedure from methodology §"Diagnostic mode":

1. **State the project's current configuration in recipe terms** — cast, beats, tropes, register, emotional contract attempted
2. **Check slot fit first** — a project that consciously violates conformity may be in the wrong slot, not broken. If wrong, find the better slot before prescribing fixes.
3. **Map project against recipe slot by slot** — match vs deviate
4. **Run the wiring tests (v2)** — apply the delete-test episode by episode; trace the climax's preconditions; check each flaw fired as a choice; check each charged cost was paid. This catches the failure the slot-by-slot map misses: a project can match every slot and still be ten demonstrations.
5. **Identify breaks** — each one is *specific* (which recipe slot or wiring test), *named* (what's missing/displaced/violated), *diagnosed* (why it weakens the engine)
6. **Propose surgical fixes that preserve voice** — minimum-conformity moves. Most projects need 3–7 surgical installs, not a rewrite; wiring breaks are usually fixed by *connecting existing beats* (make episode 6 consume what episode 3 already shows) rather than adding new ones.

Output to `projects/{project}/STORY/RECIPE_DIAGNOSIS.md`. If fixes are accepted, log them into `PROJECT_CONFIG.yaml` under `writers_room.recipe_fixes`.

### Slot-fit sub-mode

When the question is only "what slot does this live in?" (no fix list requested), produce:
- 3 candidate slots ranked by fit
- For each: matching elements / mismatching elements / one-line verdict
- A recommendation

Output to `projects/{project}/STORY/SLOT_FIT.md` or return inline.

---

## Mode C — Rewire (v1 → v2 migration)

Given a v1 (typological, unwired) recipe, migrate it to v2 in place. Follow the **Migration procedure** in `story-recipe-methodology.md` mechanically: preserve Slot / Corpus / Emotional contract / Tropes / Variation rules verbatim; add the Causal-obligation column and turn beats to the cast table; rewrite beats as causal sentences and derive the Needs/Sets-up edges from what the v1 beats already imply; insert the fixed Wiring-tests block; promote any load-bearing caveats into the spine (Law 3). Do not add/remove/reorder beats or roles. The per-recipe migration prompt (suitable for delegation to a smaller model) is at `references/story_structure/recipes/_rewire-prompt.md`. Every migration must pass the Claude wiring self-check above before the file is written.

---

## Integration with the writers-room pipeline

This skill runs **upstream of `writers-room` Phase 0 (Framework Selection)**. The output reshapes every downstream phase:

| Phase | What the recipe contributes |
|---|---|
| Phase 0 (Framework) | Recipe slot narrows the framework candidate set. Romantasy → Snowflake or Save the Cat fit; cozy mystery → Case-of-the-Week; serialized prestige → Braided Narrative; etc. The head writer recommends framework *given the recipe*, not against the bare brief. |
| Phase 1a (AAA) | Recipe's audience-implicit (from corpus) feeds the AAA charter's "I came for" and "I will not forgive" sections in the audience's own genre-fluent language. |
| Phase 1 (Head Writer) | Head writer selection privileges writers whose mechanism aligns with the recipe's emotional contract. A prestige-literary head writer on a romantasy slot is a known misfit. |
| Phase 2 (Room Assembly) | Hire for recipe coverage. Each FFAR role implies pleasures that need a writer in the room. |
| Phase 3 (Story Lock v1) | Recipe beat spine — **including its Needs/Sets-up edges** — is the *content* of the lock and the floor of the Episode Arc; framework is the *form*. The edges seed the project's Causal Contract (writers-room v3.7): edges fixed, edge-content free. Structural-stakes checklist runs against recipe's conformity rules. |
| Phase 4 (Story Lock Review) | Premortem lanes include a recipe-conformity lane: which conformity rules did the lock break, and is the break intentional? Wiring tests run at the season level on the locked Episode Arc. |
| Phase 6 (Episode Break / Draft) | Lead writer's per-beat prompt cites the recipe beat's **wiring lines** (what this beat must consume and emit) alongside its emotional target — not just the framework's structural beat. |

**Project artifacts produced:**
- `projects/{project}/STORY/RECIPE.md` — copy of the chosen recipe from the library (or freshly derived)
- `PROJECT_CONFIG.yaml`:
  ```yaml
  writers_room:
    recipe: {slug}              # e.g. "romantasy", filename in references/story_structure/recipes/
    recipe_register: {dial}     # e.g. "commercial warmth" — the register dial sitting above the engine
  ```

**Register vs recipe (important):** Register is a separate dial from recipe. *The Iron Giant* (warm) and *Cyberpunk: Edgerunners* (brutal) hit the same beats with opposite registers. The recipe demands the engine parts; register is the dial above them. Always record the register choice alongside the recipe slug.

---

## When NOT to use this skill

Per methodology §"Caveats and limits":

- **Voice-driven or theme-driven slots** (literary fiction, slipstream, New Weird, much "elevated genre"). These yield thin recipes that don't help much. Don't force formula onto a slot that resists it.
- **Genre-of-one slots.** If you can't name 5+ commercial exemplars, the recipe describes one work and won't transfer. Drop to a recognizable parent slot or skip the skill.
- **When the project is consciously breaking formula.** Genre subversion is a legitimate move — but it requires the recipe as the thing being subverted. Run the skill anyway so the breaks are deliberate.

---

## Recipe library

Maintained at `references/story_structure/recipes/`. Each file is a v2-wired recipe in the standard template. **54 slots, all v2-wired** — ported 2026-06-11 from the gemmawood sister project, where each passed a mechanical wiring validator. See `references/story_structure/recipes/README.md` for the full index and provenance; the methodology's §"Recipes in this library" carries the acceptance bar for additions.

Project-specific recipes intentionally NOT generalized:
- **Innocent + impossible-tech companion vs hostile system** — derived for `stray-signal`. Project-specific by design. Lives inside the stray-signal project, not in the library.

---

## Honest epistemic note

Pattern extraction from training data is best-effort, not original criticism. Recipes are starter material to argue with and refine against the user's own corpus expertise — not gospel. The skill produces a working draft; the user's domain knowledge is the final filter.
