---
skill: story-recipe
role: writer
version: 0.1

description: |
  Anchors a project to a commercially-derived genre recipe BEFORE the room
  hires, the framework is picked, or any pitches are written. A recipe is
  the externalized engine of a subgenre — slot definition, emotional
  contract, FFAR cast, named trope vocabulary, beat spine with emotional
  targets, and conformity/variation rules. Recipes are extracted from
  10–15 commercial exemplars per slot, not derived from the project being
  fixed.

  Why this skill exists: Codeywood projects with no slot anchor drift to
  Claude's default literary-prestige centroid regardless of which writers
  are in the room. The persona/AAA/anti-viral stack pushes outward; the
  recipe pulls inward toward a known commercial neighborhood. Together
  they bracket the work.

  Two modes:
    - **Derive** — produce a fresh recipe for a named subgenre slot.
    - **Diagnose** — analyze an existing project against an existing recipe
      and propose surgical fixes.

  Source methodology: `references/story_structure/story-recipe-methodology.md`
  Recipe library:     `references/story_structure/recipes/`

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
- "What slot does [project] live in?" → SLOT-FIT mode (lightweight DIAGNOSE)
- "Fix [project] against the [genre] recipe" → DIAGNOSE mode
- "Build a recipe library across [genres]" → DERIVE, repeated
- "Compare [project] against three adjacent recipes" → SLOT-FIT, multi-way

## Core principle

A recipe is a working AI prompt only when it externalizes craft knowledge AI cannot supply for itself. Five mandatory elements (per methodology §"Core principle"):

1. **Functional definitions** (not descriptions) — every role is a job, every flaw is named
2. **Relational definitions** — characters defined in opposition to each other
3. **Stated emotional targets per beat** — what the audience feels, not what happens
4. **Named tropes as deployable units** — naming makes them usable
5. **Explicit conformity vs variation rules** — where to obey, where to invent

A recipe missing any of the five degrades into a description and stops working as a prompt. Read the methodology file first if any element is unclear.

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

Produce a recipe for a named subgenre slot. The 7-step procedure from `story-recipe-methodology.md`:

1. **Name the emotional contract** — 3–4 word cocktail
2. **Pick the subgenre slot** — narrow enough to find 10+ exemplars; broad enough to find 5+
3. **Pull the corpus** — 10–15 commercial exemplars, tonally diverse, NOT including the project being fixed
4. **Extract the FFAR cast** — Function / Flaw / Arc / Relational position, 5–7 roles
5. **Catalog tropes** — recurring units across 3+ exemplars get a name + functional definition. Include anti-tropes.
6. **Map the beat spine** — sized to the genre's unit (chapters / episodes / acts / seasons), each beat carries an emotional target
7. **State conformity + variation rules** — both, equally important

Output to `references/story_structure/recipes/{slug}.md`, using `RECIPE_TEMPLATE.md` in this directory. Add a one-line entry to `references/story_structure/story-recipe-methodology.md` under "Recipes in this library."

### Corpus discipline

- **Commercial successes, currently preferred over classic.** Classics often broke the formula that later codified into the formula; readership/viewership conformity is the signal you want.
- **Tonal diversity within the slot.** *Wall-E* (warm) and *Cyberpunk: Edgerunners* (brutal) both fit innocent+companion — that's evidence the recipe is real and not a tone description.
- **Never include the project being fixed.** Deriving from your own canon produces a recipe-shaped self-description and defeats the methodology.

---

## Mode B — Diagnose

Given a project AND a recipe (existing or freshly derived), produce a surgical fix list. The 5-step procedure from methodology §"Diagnostic mode":

1. **State the project's current configuration in recipe terms** — cast, beats, tropes, register, emotional contract attempted
2. **Check slot fit first** — a project that consciously violates conformity may be in the wrong slot, not broken. If wrong, find the better slot before prescribing fixes.
3. **Map project against recipe slot by slot** — match vs deviate
4. **Identify breaks** — each one is *specific* (which recipe slot), *named* (what's missing/displaced/violated), *diagnosed* (why it weakens the engine)
5. **Propose surgical fixes that preserve voice** — minimum-conformity moves. Most projects need 3–7 surgical installs, not a rewrite.

Output to `projects/{project}/STORY/RECIPE_DIAGNOSIS.md`. If fixes are accepted, log them into `PROJECT_CONFIG.yaml` under `writers_room.recipe_fixes`.

### Slot-fit sub-mode

When the question is only "what slot does this live in?" (no fix list requested), produce:
- 3 candidate slots ranked by fit
- For each: matching elements / mismatching elements / one-line verdict
- A recommendation

Output to `projects/{project}/STORY/SLOT_FIT.md` or return inline.

---

## Integration with the writers-room pipeline

This skill runs **upstream of `writers-room` Phase 0 (Framework Selection)**. The output reshapes every downstream phase:

| Phase | What the recipe contributes |
|---|---|
| Phase 0 (Framework) | Recipe slot narrows the framework candidate set. Romantasy → Snowflake or Save the Cat fit; cozy mystery → Case-of-the-Week; serialized prestige → Braided Narrative; etc. The head writer recommends framework *given the recipe*, not against the bare brief. |
| Phase 1a (AAA) | Recipe's audience-implicit (from corpus) feeds the AAA charter's "I came for" and "I will not forgive" sections in the audience's own genre-fluent language. |
| Phase 1 (Head Writer) | Head writer selection privileges writers whose mechanism aligns with the recipe's emotional contract. A prestige-literary head writer on a romantasy slot is a known misfit. |
| Phase 2 (Room Assembly) | Hire for recipe coverage. Each FFAR role implies pleasures that need a writer in the room. |
| Phase 3 (Story Lock v1) | Recipe beat spine is the *content* of the lock; framework is the *form*. Structural-stakes checklist runs against recipe's conformity rules. |
| Phase 4 (Story Lock Review) | Premortem lanes include a recipe-conformity lane: which conformity rules did the lock break, and is the break intentional? |
| Phase 6 (Episode Break / Draft) | Lead writer's per-beat prompt cites the recipe's emotional target at that position, not just the framework's structural beat. |

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

Maintained at `references/story_structure/recipes/`. Each file is a recipe in the standard template. The library's index lives at the bottom of `references/story_structure/story-recipe-methodology.md`.

Current entries:
- **Romantasy** — desire + danger + transformation. 6 archetypes, 36 chapters. (Source: Story Chef / Nerdy Novelist transcript, validated commercial canon.)

Project-specific recipes intentionally NOT generalized:
- **Innocent + impossible-tech companion vs hostile system** — derived for `stray-signal`. Project-specific by design. Lives inside the stray-signal project, not in the library.

---

## Honest epistemic note

Pattern extraction from training data is best-effort, not original criticism. Recipes are starter material to argue with and refine against the user's own corpus expertise — not gospel. The skill produces a working draft; the user's domain knowledge is the final filter.
