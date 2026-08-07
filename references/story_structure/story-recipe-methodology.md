# Story Recipe Methodology — v2 (wired recipes)

A framework for deriving genre-specific story recipes from commercial corpora, optimized for use as AI prompts. Includes the derivation procedure, the recipe template, the **wiring layer** (new in v2), a migration procedure for rewriting v1 recipes, and a diagnostic mode for fixing existing projects against a recipe.

**What changed in v2 and why.** The rio_v2 bible-vs-outline audit (see `references/story_structure/calibration_corpus.md` for the source corpus and audit numbers) ran six full pipeline runs across five different v1 recipes (cyberpunk, urban_fantasy, ensemble_heist, tragedy, hard_sf_systems) and found a uniform failure signature regardless of genre: 43% of episodes could be deleted without breaking any later episode, causal chains only ignited in the back half, and climaxes depended on 0–3 earned character choices. The v1 recipes did their job perfectly — and their job was never causality. A v1 beat spine is **typological** (it says which scene-types occur, in what order — Propp's functions, modernized) but not **causal** (it never says what each beat must consume from earlier beats or feed to later ones). A story can hit every beat and still be ten disconnected demonstrations. v2 recipes keep everything v1 recipes did and add the **wiring**: every beat declares what it needs and what it sets up, flaws fire as choices with propagating consequences, and conformity is tested as a property of the whole outline, not per-beat presence.

---

## When to invoke

- **"Derive a [genre] recipe"** — produces a fresh v2 recipe for a named subgenre slot.
- **"Rewire the [genre] recipe"** — migrates an existing v1 recipe to v2 (see Migration procedure).
- **"What slot does [project] live in?"** — triangulates a project against the closest commercial neighborhood.
- **"Fix [project] against the [genre] recipe"** — runs the diagnostic mode against an existing or freshly-derived recipe.
- **"Build a recipe library across [genres]"** — derives multiple recipes and notes crossover compatibility.

---

## Core principle: why recipes work as AI prompts

Effective recipes externalize craft knowledge that is usually tacit. AI does not have implicit genre intuition — it has explicit pattern-matching. A recipe wins as a prompt when it provides all of the following:

1. **Functional definitions, not descriptions.** Each character is a job in the cast, not a person. The protagonist's flaw is named explicitly because the flaw is the engine of behavior. "Martyr complex" generates a thousand scenes; "interesting protagonist" generates nothing.
2. **Relational definitions.** Characters are defined in opposition to each other ("the betrayer exists to contrast the love interest"). LLMs do better with constraint satisfaction than open-ended generation.
3. **Stated emotional targets per beat.** Not "Chapter 7: rescue from danger," but "Readers need to feel rooting for her before anything magical happens." The target is what the AI generates toward.
4. **Named tropes as deployable units.** "Touch her and die." "Joy episode." "Soft resurrection." Named tropes are deployable; unnamed ones produce cliché by accident.
5. **Explicit conformity vs variation rules.** Where the AI must obey the genre, and where it must invent. AI defaults to repetition; the variation rules tell it where to take risks.
6. **Wired beats (v2).** Every beat declares what it consumes from earlier beats and what it emits for later beats to consume. Sequence tells the model *what order*; wiring tells it *what makes each beat necessary*. Without edges, the model writes ten demonstrations of the premise; with edges, it must write consequences.
7. **Whole-output conformity tests (v2).** Causality is verified as a property of the finished outline (can any episode be deleted? does the climax consume earlier choices?), never as per-beat "must include X" items.

### Three laws from the executing model

These were learned empirically from the divergence pipeline's local writer model and shape everything in v2. Treat them as binding when authoring or migrating recipes:

- **Law 1 — Checkable per-unit rules get bolt-on-gamed.** When the writing model audits its draft against a "must include X" rule, it bolts the missing element on as a parenthetical or em-dash aside, degrading the draft. So the recipe's *story-level demands* must be whole-output properties ("no episode is deletable") rather than element checklists. Note the asymmetry: the **recipe document itself** is a spec, authored once and human-reviewed — it may and should use explicit checkable fields (Needs/Sets up lines). The *outline the model writes from the recipe* is where only whole-output tests are safe.
- **Law 2 — The model mirrors the input's grammar.** A sequence-shaped input produces checklist reasoning; a causal-shaped input produces causal reasoning. Therefore v2 beats are written as cause→consequence sentences ("Because the group buried the warning in Ep 2, the killer takes one of them mid-transgression…"), not noun-headline scene labels. The grammar of the recipe is the grammar of the outline.
- **Law 3 — Caveats are dead text.** v1 recipes carried their causal discipline in the Caveats section ("every breakage must do double duty," "plant the reversal in the casing") — and the audit shows those caveats had zero effect. Anything load-bearing goes into the beat spine, the cast table, or the conformity tests. Caveats are for human readers only.

---

## The methodology — 8 steps

### Step 1. Name the emotional contract
What cocktail does this subgenre deliver? Romantasy: *desire + danger + transformation.* Cozy mystery: *puzzle + community + restoration.* Heist: *cleverness + camaraderie + reversal.* Innocent+companion sci-fi: *wonder + protection + ache.*

If you can't name the cocktail in 3–4 words, the slot is too broad. Drop to subgenre. The cocktail is the target; everything else is engineering to deliver it.

### Step 2. Pick the subgenre slot
Genres are too broad. "Sci-fi" doesn't formula. "Animated serialized sci-fi with innocent + impossible-tech companion vs hostile system" does. The right slot is where 10+ commercial exemplars share both an emotional contract AND a structural spine.

Beware genre-of-one slots — if you can't find 5+ commercial exemplars, the recipe will describe one work rather than extract a pattern.

### Step 3. Pull the corpus — 10 to 15 commercial exemplars
**Commercially successful.** Current preferred over classic — classics often broke the formula that later codified into the formula. Readership/viewership conformity is the signal you want.

Aim for tonal diversity within the slot. *Wall-E* and *Cyberpunk: Edgerunners* both fit the innocent+companion recipe with opposite registers; that's evidence the recipe is real and not a tone description.

**DO NOT include your own work in progress.** The recipe must come from the corpus, not from the project being fixed. Deriving from your own canon produces a recipe-shaped self-description and defeats the methodology.

### Step 4. Extract the cast — minimum viable functions, causally obligated
The smallest set of character roles that ALL exemplars contain. For each role, fill the **FFAR+C** fields:

- **Function** — what the role does in the emotional system
- **Flaw** — the named flaw that generates behavior (most outlines skip this; don't)
- **Causal obligation (v2)** — what the flaw must CAUSE, and which beat consumes it. A flaw is not a description; it is a loaded spring. "Gambling addiction" is incomplete; "his gambling debt is how the Authority finds the crew (fires at the Complication; its cost is still being paid at the climax)" is wired. The flaw fires as a **choice the character makes**, and the consequence propagates to at least one later beat.
- **Arc** — trajectory from starting state to ending state, **plus the beat where it turns**. The early state and the changed state must both be visible as on-screen behavior; a relationship or arc that is only described in a bio has not moved.
- **Relational position** — defined in opposition to which other role(s)

Most genres land at 5–7 roles. If you have 12 roles, you're describing one work — collapse to functions.

**Antagonist discipline.** The antagonist-function role (Mark, Killer, Rival, System's Face) must carry a HUMAN motive in its Flaw/Function fields — class hatred, envy, wounded pride, family vengeance, contempt, greed, a specific past humiliation — locatable in time and visible in beats. "Believes in optimization" and "erases mistakes" are job descriptions, not motives; the executing model defaults to them unless the recipe forbids it.

### Step 5. Catalog the trope vocabulary
Every recurring unit across 3+ exemplars gets a name and a functional definition. Tropes are the genre's nouns. Naming matters — once a trope is named ("Joy Episode," "soft resurrection," "touch her and die"), it can be deployed or subverted deliberately.

Include **anti-tropes**: what the genre never does. Negative constraints are often more useful than positive ones for AI prompts.

Tropes stay *unwired* — they are texture vocabulary, deployable anywhere. The wiring lives in the spine and cast, not the trope list.

### Step 6. Map the beat spine with emotional targets
The genre-specific structural spine — NOT Hero's Journey, NOT Save the Cat, NOT three-act. Each beat has four fields:

- What happens — **written as a causal sentence**: a character's choice + what it irreversibly changes (Law 2)
- What it consumes (see Step 7)
- What it emits (see Step 7)
- What the audience feels at this moment

The emotional target column is non-negotiable, and it must be an **audience emotion, not a theme demonstration**. "The audience pre-grieves" is a target; "the theme of community is reinforced" is not — theme-shaped targets produce theme-shaped (unearned) climaxes.

Format the spine to the genre's unit: chapter-by-chapter for novels, episode-by-episode for series, act-by-act for film. For Codeywood's pipeline the usual render target is a serialized episodic season.

### Step 7. Wire the spine (v2 — the dependency map)
This is the step v1 lacked. For every beat, append two compact lines inside the beat cell:

- **Needs:** which earlier beats' emissions this beat consumes — the thing that makes it *necessary now* rather than merely *next* ("Needs: E2-dismissed-warning").
- **Sets up:** what this beat emits that a later beat must consume — a debt, a lie, a hidden body, a fractured trust, a tool — with consumer pointer(s) ("Sets up: E3-false-story (→E5), E3-staged-body (→E6)").

**Tag grammar (strict; wiring checks are performed by Claude per the story-recipe SKILL.md self-check — tag grammar, banned contentless nouns, bidirectional graph closure, front-half obligations, climax preconditions):** every tag is `E<emitting-episode>-<concrete-artifact-noun>` — prefixed by the beat that EMITS it, never the consumer, so one artifact keeps one name for its whole life. The noun names a story object (a lie, a debt, a wound, a tool, a secret, a body, a betrayal, a map, a reputation, a bargain). Banned: tags whose noun is only "consequence", "choice", "cost", "constraint", "aftermath", "event", or "outcome" — a contentless tag is the circular-edge failure ("Needs: previous episode") in tag syntax.

Wiring rules (verify these against the finished spine before delivering the recipe):

1. **No orphan beats.** Every beat except the opening consumes at least one earlier emission.
2. **No unfed setups.** Every emission is consumed by some later beat. If nothing consumes it, cut it or wire it.
3. **The front half carries forward obligations.** Setup beats (roughly beats 1–4) are where v1 recipes went inert — assembly, casing, group-establishment beats that demonstrate and propagate nothing. In v2, every setup beat emits at least one thing the back half consumes. Recruitment is not a beat; recruitment *that plants the flaw which later breaks the plan* is a beat.
4. **The climax consumes the season.** The final two beats must consume emissions from at least three distinct earlier beats, and at least two of those must be **character choices** (not facts, not setup conditions). The climax's method must be something established and paid for earlier — a climax that needs only the premise is a restatement, not an ending.
5. **Costs are paid later.** Any beat that charges a cost (a death, a betrayal, a burned resource, a lost trust) must have that cost visibly constrain a later beat. A loss that changes nothing is decoration.
6. **Flaws fire as choices.** Where a beat exploits a cast flaw (per the Causal obligation column), the flaw produces a *decision* the character makes, whose consequence propagates — not a trait-display that merely happens to them. Genre-canonical patterns like the slasher death order are kept, but each death must change the survivors' options, knowledge, or location, and the death should be triggered by a transgression the victim chooses, not just emblematize their label.

### Step 8. State conformity and variation rules
- **Conformity rules** — break these and it's not the genre anymore. These are the audience's implicit contract terms.
- **Wiring tests (v2)** — the whole-output causal tests, stated as properties of the finished outline (see template; this block is FIXED text, identical in every recipe).
- **Variation rules** — where the genre demands invention. Repeating these patterns feels stale. Note in v2: the *edges* are fixed (the Complication must consume a planted flaw), but the *content* of every edge varies freely (which flaw, what it costs, how it surfaces). Wiring constrains shape, never material.

---

## The recipe template (v2)

Deliver every recipe in this structure:

```
# [Subgenre Slot Name]

## Slot
Commercial neighborhood + one-line definition.

## Corpus
10–15 named exemplars, with brief notes on tonal range.

## Emotional contract
3–4 word cocktail + one sentence on the audience experience.

## Cast (FFAR+C)
Table:
Role | Function | Flaw | Causal obligation | Arc (from → to, turn beat) | Relational position
5–7 roles. Antagonist-function role carries a human motive.

## Trope vocabulary
Named units with functional definitions.
Include anti-tropes (what the genre never does).

## Beat spine
Table: Position | Beat | Emotional target
Each Beat cell: 2–4 causal sentences (choice + irreversible change),
ending with two compact lines:
  **Needs:** [beat-number tags, or "—" for the opener]
  **Sets up:** [beat-number tags]
Sized to genre unit; 10-episode season for this pipeline.

## Conformity rules
Bullet list. Break these and it's not the recipe. Genre-specific.

## Wiring tests
FIXED BLOCK — copy verbatim into every recipe:
- Delete-test: no episode can be removed without a later episode breaking.
- The climax consumes at least two character choices from distinct earlier episodes.
- Every named flaw fires as a choice whose consequence is visible in a later episode.
- Every relationship the cast table says moves shows its early state AND its changed
  state as on-screen actions.
- Every cost charged is paid: a later episode is harder in a named way because of it.

## Variation rules
Bullet list. Must vary across works in this slot. Edges fixed; edge-content free.

## Caveats
Honest notes for human readers: slot edge cases, register dials, genre-of-one
risk. NOTHING load-bearing lives here (Law 3) — if a caveat states a causal
discipline, move it into the spine wiring or the wiring tests.
```

**Token budget.** Recipes are injected whole into the Story Lock and episode-breaking prompts as the FLOOR. Hold a v2 recipe to roughly the v1 length +15% (v1 average ≈ 115 lines). Pay for the wiring lines by compressing corpus notes and trope descriptions — never by cutting edges.

---

## Migration procedure — rewriting a v1 recipe to v2

This procedure is designed to be executed per-recipe by a smaller model. Follow it mechanically.

**Inputs:** one v1 recipe file from `references/story_structure/recipes/`. **Output:** the same file, rewired, same slot, same genre content.

1. **Preserve verbatim:** Slot, Corpus, Emotional contract, Trope vocabulary (including anti-tropes), Variation rules. Do not rederive, trim, or improve them. This is a rewiring pass, not a re-derivation.
2. **Cast table:** rename header to `Cast (FFAR+C)`; add the **Causal obligation** column. For each role, derive the obligation from what the v1 Flaw and Arc already imply — name what the flaw causes and which beat consumes it. Add the turn beat to the Arc column. If the antagonist-function role's Flaw/Function reads as a job description ("arrogance disguised as competence" is fine; "maintains efficiency" is not), sharpen it to a human motive consistent with the v1 text.
3. **Beat spine:** rewrite each Beat cell as causal sentences (Law 2) and append the **Needs:** / **Sets up:** lines. Derive the edges from what the v1 beats already imply — most v1 spines have latent wiring ("the audience knows the predator before the prey" implies E1 emits something E3 consumes); make it explicit. Where a beat has no derivable edge (pure hangout/establishment beats), give it a forward obligation consistent with the genre: what does this beat plant that the back half uses?
4. **Apply the seven wiring rules from Step 7.** In particular: front-half beats each emit ≥1 forward obligation; the final two beats consume ≥3 distinct earlier emissions, ≥2 of them character choices; flaw-exploiting beats fire as choices.
5. **Insert the fixed Wiring tests block** between Conformity rules and Variation rules, verbatim from the template.
6. **Sweep the Caveats** (Law 3): any caveat that states a causal discipline ("every breakage must do double duty," "plant the reversal's groundwork in the casing") gets PROMOTED — encode it as edges in the relevant beats and/or a conformity rule — then delete it from Caveats. Caveats keep only human-reader notes (register dials, edge cases, genre-of-one warnings).
7. **Do not:** add or remove beats; change the beat order; add or remove cast roles; rename tropes; change the emotional targets except to fix theme-shaped ones ("reinforces the theme of X" → the audience emotion the moment produces); exceed the +15% length budget.
8. **Self-check before writing the file:** every beat except the opener has a Needs line pointing at a real earlier Sets-up; every Sets-up is consumed somewhere; the final two beats satisfy wiring rule 4; the Causal obligation column references real beat numbers; the Wiring tests block is verbatim.

### Worked example (slasher, beats 3–4)

**v1 (before):**

> | 3 | **The First In-Group Kill.** Member of the named group is killed — usually a peripheral / reckless / cruel one. The kill is staged at full Signature Method intensity. Skeptic dismisses the disappearance as runaway / overdose / quit. | Shock. The audience knows; the group does not yet. |
> | 4 | **The Phone Dies / The Car Won't Start.** Isolation mechanism engaged. The group is now structurally trapped at the Place. Final Girl notices the wrongness before the others; her testimony is dismissed by the Skeptic. | Frustration into fear. The audience watches the corridor narrow. |

**v2 (after):**

> | 3 | **The First In-Group Kill.** Because the group laughed off what the Final Girl saw in Ep 2, one member breaks the group's one safety habit by choice — sneaking out, going back for something, taking the shortcut — and the killer takes them mid-transgression by the Signature Method. The Skeptic supplies a runaway story and the group adopts it, which means nobody searches — the body stays where the killer staged it. **Needs:** E2-dismissed-warning. **Sets up:** E3-false-story (→E5), E3-staged-body (→E6), E3-one-fewer-driver (→E4). | Shock. The audience knows; the group does not yet. |
> | 4 | **The Phone Dies / The Car Won't Start.** The group's escape options fail — and at least one failure is a cost of Ep 3, not coincidence: the missing member was the one with the car keys, the working phone, the route knowledge. The Final Girl names the wrongness; the Skeptic, now invested in the runaway story, has to dismiss her harder. The group is structurally trapped at the Place. **Needs:** E3-one-fewer-driver, E3-false-story. **Sets up:** E4-doubled-down-skeptic (→E7), E4-place-arsenal (→E10: the geography learned while trapped is what she fights with). | Frustration into fear. The audience watches the corridor narrow. |

Note what changed: the victim dies *during a choice* (not as a trait-display); the dismissal in Ep 2 now *causes* Ep 3; the death *costs* the group something Ep 4 consumes; the trap's geography is planted as the climax's weapon. Same beats, same order, same genre — wired.

---

## Diagnostic mode

For fixing an existing project against a recipe:

1. **State the project's current configuration in recipe terms.** Cast, beats, tropes, register, emotional contract attempted.
2. **Check slot fit first.** Before prescribing fixes, confirm the project is in the right slot. A project consciously violating recipe conformity may be in the wrong slot, not broken. If slot is wrong, find the better slot before diagnosing.
3. **Map project against recipe slot by slot.** Where does it match? Where does it deviate?
4. **Run the wiring tests (v2).** Apply the delete-test episode by episode; trace the climax's preconditions; check each flaw fired as a choice; check each charged cost was paid. This catches the failure the slot-by-slot map misses: a project can match every slot and still be ten demonstrations.
5. **Identify breaks.** Each break is specific (which recipe slot or wiring test), named (what's missing, displaced, or violated), diagnosed (why it weakens the engine).
6. **Propose surgical fixes that preserve project voice.** The fix should be the minimum recipe-conformity move that restores the engine. Most projects don't need a rewrite — they need 3–7 surgical installs, and wiring breaks are usually fixed by *connecting existing beats* (make episode 6 consume what episode 3 already shows) rather than adding new ones.

---

## Caveats and limits

- **Subgenre, not genre.** "Sci-fi" doesn't formula. "Cyberpunk dystopia heist" does. Slot specificity is the difference between a useful recipe and a generic one.
- **Commercial corpus, not your own work.** Recipe must come from outside the project being fixed. Self-derivation defeats the methodology.
- **Some genres formula better than others.** High-conformity genres (romantasy, cozy mystery, locked-room thriller, LitRPG, heist, slasher, romance subgenres, procedural) yield tight recipes. Voice-driven or theme-driven genres yield thin recipes that don't help much. Don't force formula onto a slot that resists it. Wiring, however, applies everywhere — even a thin recipe's few beats should carry edges.
- **Genre-of-one is a trap.** If you can't name 5+ commercial exemplars in the slot, you're describing one work rather than extracting a pattern. The recipe won't transfer.
- **Register is a separate dial from recipe.** *The Iron Giant* (warm) and *Cyberpunk: Edgerunners* (brutal) hit the same beats with opposite registers. The recipe demands the engine parts; register is the dial above them.
- **Recipes are floors, not ceilings — and wiring is necessary, not sufficient.** A wired recipe forces consequences to exist; it cannot force them to be surprising, moving, or well-chosen. The recipe ensures the engine runs; the persona, lore, and characters decide what it's carrying. Do not expect v2 wiring alone to produce a near-final treatment — it removes a structural failure mode so the creative failures become visible.
- **The wiring depends on the pipeline transmitting it.** Edges in a recipe are useless if intermediate steps strip causal connectives between draft and final outline (see the rio_v2 audit via `calibration_corpus.md`). Recipe v2 and the transmission fix (writers-room v3.7's Causal Contract — every downstream phase receives the wiring) are one intervention in two parts; evaluate them together.
- **Honest epistemic note.** Pattern extraction from training data is best-effort, not original criticism. Recipes are starter material to argue with and refine against the user's own corpus expertise — not gospel.

---

## Recipes in this library

The library lives at `references/story_structure/recipes/` — **54 slots, all v2-wired** (ported 2026-06-11 from the gemmawood sister project, where the full set passed a mechanical wiring validator: emitter-named concrete-artifact tags, bidirectional graph closure, front-half obligations, climax consuming ≥3 distinct earlier beats, no template boilerplate). Persona `recipe_affinities` fields reference these slot names.

Provenance: `ensemble_heist` is the hand-wired gold example; `cyberpunk`, `urban_fantasy`, `tragedy`, `hard_sf_systems` were hand-wired alongside it; the remaining 49 were migrated via `recipes/_rewire-prompt.md` and validated per-recipe. Substance spot-checks: slasher (full audit), comfort_rewatch_sitcom, sports_underdog_montage, talent_show_stage (soft-stakes stress sample) — edges name concrete artifacts in all sampled recipes.

**Acceptance bar for new or edited recipes:** the recipe must pass the Claude wiring self-check in `skills/writer/story-recipe/SKILL.md` (tag grammar, graph closure, front-half obligations, climax preconditions, verbatim Wiring-tests block) plus a derivation-notes review before entering the library.

---

## Example invocations

- *"Derive a Western recipe."* → Slot it (revisionist vs classical vs acid Western vs space Western — pick one), pull corpus of 10–15, deliver full v2 template.
- *"Rewire the slasher recipe."* → Run the migration procedure on `references/story_structure/recipes/slasher.md`; preserve content, add edges, promote caveats, insert wiring tests.
- *"What slot does Stray Signal live in?"* → Triangulate project beats against known recipes, propose closest slot, note breaks if relevant.
- *"Fix [project] against the [genre] recipe."* → Derive or load recipe, then run diagnostic mode including the wiring tests, with surgical fix list.
- *"Build a recipe library across cozy mystery, heist, locked-room thriller, and cosmic horror."* → Derive each, note crossover compatibility (e.g., heist + cosmic horror = a known hybrid slot).
