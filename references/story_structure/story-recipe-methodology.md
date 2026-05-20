# Story Recipe Methodology

A framework for deriving genre-specific story recipes from commercial corpora, optimized for use as AI prompts. Includes the procedure for derivation, the recipe template, and a diagnostic mode for fixing existing projects against a recipe.

---

## When to invoke

- **"Derive a [genre] recipe"** — produces a fresh recipe for a named subgenre slot.
- **"What slot does [project] live in?"** — triangulates a project against the closest commercial neighborhood.
- **"Fix [project] against the [genre] recipe"** — runs the diagnostic mode against an existing or freshly-derived recipe.
- **"Build a recipe library across [genres]"** — derives multiple recipes and notes crossover compatibility.

---

## Core principle: why recipes work as AI prompts

Effective recipes externalize craft knowledge that is usually tacit. AI does not have implicit genre intuition — it has explicit pattern-matching. A recipe wins as a prompt when it provides all five of the following:

1. **Functional definitions, not descriptions.** Each character is a job in the cast, not a person. The protagonist's flaw is named explicitly because the flaw is the engine of behavior. "Martyr complex" generates a thousand scenes; "interesting protagonist" generates nothing.
2. **Relational definitions.** Characters are defined in opposition to each other ("the betrayer exists to contrast the love interest"). LLMs do better with constraint satisfaction than open-ended generation.
3. **Stated emotional targets per beat.** Not "Chapter 7: rescue from danger," but "Readers need to feel rooting for her before anything magical happens." The target is what the AI generates toward.
4. **Named tropes as deployable units.** "Touch her and die." "Joy episode." "Soft resurrection." Named tropes are deployable; unnamed ones produce cliché by accident.
5. **Explicit conformity vs variation rules.** Where the AI must obey the genre, and where it must invent. AI defaults to repetition; the variation rules tell it where to take risks.

Any methodology that produces all five elements will produce effective AI prompts. The procedure below is one path to all five.

---

## The methodology — 7 steps

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

### Step 4. Extract the cast — minimum viable functions
The smallest set of character roles that ALL exemplars contain. For each role, fill the **FFAR** fields:

- **Function** — what the role does in the emotional system
- **Flaw** — the named flaw that generates behavior (most outlines skip this; don't)
- **Arc** — trajectory from starting state to ending state
- **Relational position** — defined in opposition to which other role(s)

Most genres land at 5–7 roles. Romantasy: 6. Innocent+companion: 6. Heist: 5–6. Cozy mystery: 5. If you have 12 roles, you're describing one work — collapse to functions.

### Step 5. Catalog the trope vocabulary
Every recurring unit across 3+ exemplars gets a name and a functional definition. Tropes are the genre's nouns. Naming matters — once a trope is named ("Joy Episode," "soft resurrection," "touch her and die," "categorization joke"), it can be deployed or subverted deliberately.

Include **anti-tropes**: what the genre never does. Negative constraints are often more useful than positive ones for AI prompts.

### Step 6. Map the beat spine with emotional targets
The genre-specific structural spine — NOT Hero's Journey, NOT Save the Cat, NOT three-act. Each beat has three fields:

- What happens
- What changes
- What the audience feels at this moment

The emotional target column is non-negotiable. A beat without an emotional target is a plot point; the recipe needs targets to engineer the cocktail.

Format the spine to the genre's unit: chapter-by-chapter for novels, episode-by-episode for series, act-by-act for film, season-by-season for serialized prestige TV. Some recipes need multiple resolutions (a 36-chapter book has both chapter beats and act movements).

### Step 7. State conformity and variation rules
- **Conformity rules** — break these and it's not the genre anymore. These are the audience's implicit contract terms.
- **Variation rules** — where the genre demands invention. Repeating these patterns feels stale.

Both are equally important. List both.

---

## The recipe template

Deliver every recipe in this structure:

```
# [Subgenre Slot Name]

## Slot
Commercial neighborhood + one-line definition.

## Corpus
10–15 named exemplars, with brief notes on tonal range.

## Emotional contract
3–4 word cocktail + one sentence on the audience experience.

## Cast (FFAR)
Table:
Role | Function | Flaw | Arc | Relational position
5–7 roles.

## Trope vocabulary
Named units with functional definitions.
Include anti-tropes (what the genre never does).

## Beat spine
Table or list:
Position | Beat | Emotional target
Sized to genre unit (chapters / episodes / acts / seasons).

## Conformity rules
Bullet list. Break these and it's not the recipe.

## Variation rules
Bullet list. Must vary across works in this slot.

## Caveats
Honest notes on slot edge cases, register dials, common failures,
and the genre-of-one risk if relevant.
```

---

## Diagnostic mode

For fixing an existing project against a recipe:

1. **State the project's current configuration in recipe terms.** Cast, beats, tropes, register, emotional contract attempted.
2. **Check slot fit first.** Before prescribing fixes, confirm the project is in the right slot. A project consciously violating recipe conformity may be in the wrong slot, not broken. If slot is wrong, find the better slot before diagnosing.
3. **Map project against recipe slot by slot.** Where does it match? Where does it deviate?
4. **Identify breaks.** Each break is:
   - Specific (which recipe slot it's in)
   - Named (what's missing, displaced, or violated)
   - Diagnosed (why it weakens the engine)
5. **Propose surgical fixes that preserve project voice.** The fix should be the minimum recipe-conformity move that restores the engine. Most projects don't need a rewrite — they need 3–7 surgical installs.

The diagnostic mode is most useful when audience response is weaker than expected and the project conforms to none of the obvious adjacent recipes.

---

## Caveats and limits

- **Subgenre, not genre.** "Sci-fi" doesn't formula. "Cyberpunk dystopia heist" does. Slot specificity is the difference between a useful recipe and a generic one.
- **Commercial corpus, not your own work.** Recipe must come from outside the project being fixed. Self-derivation defeats the methodology.
- **Some genres formula better than others.** High-conformity genres (romantasy, cozy mystery, locked-room thriller, LitRPG, heist, slasher, romance subgenres, procedural) yield tight recipes. Voice-driven or theme-driven genres (literary fiction, slipstream, New Weird, much "elevated genre") yield thin recipes that don't help much. Don't force formula onto a slot that resists it.
- **Genre-of-one is a trap.** If you can't name 5+ commercial exemplars in the slot, you're describing one work rather than extracting a pattern. The recipe won't transfer.
- **Register is a separate dial from recipe.** *The Iron Giant* (warm) and *Cyberpunk: Edgerunners* (brutal) hit the same beats with opposite registers. The recipe demands the engine parts; register is the dial above them. Prestige restraint, commercial warmth, and pulp velocity are all register choices that can sit on top of the same recipe.
- **Recipes are floors, not ceilings.** Conformity rules are the floor. World, voice, character specifics, and the variation rules are where the work happens. The recipe does not produce the story — it ensures the engine runs.
- **Honest epistemic note.** Pattern extraction from training data is best-effort, not original criticism. Recipes are starter material to argue with and refine against the user's own corpus expertise — not gospel.

---

## Recipes in this library

*Maintained list of recipes derived using this methodology. Files live at `references/story_structure/recipes/`. Add each as it's built.*

- **Romantasy** — desire + danger + transformation. 6 archetypes, 36 chapters. (Source: Story Chef / Nerdy Novelist transcript, validated commercial canon.) *To be filed.*

## Project-specific recipes (intentionally not generalized)

Recipes that were derived to serve one project rather than seed a library slot. They live inside the project, not in the library.

- **Innocent + Impossible Tech Companion vs Hostile System (animated serialized sci-fi)** — wonder + protection + ache. 6 cast roles, 10-episode spine. Corpus: Wall-E, Iron Giant, Wild Robot, Big Hero 6, Edgerunners, Pantheon, Castle in the Sky, Treasure Planet, Astro Boy, Made in Abyss, How to Train Your Dragon, E.T. *Project: stray-signal.*

---

## Example invocations

- *"Derive a Western recipe."* → Slot it (revisionist vs classical vs acid Western vs space Western — pick one), pull corpus of 10–15, deliver full template.
- *"What slot does Stray Signal live in?"* → Triangulate project beats against known recipes, propose closest slot, note breaks if relevant.
- *"Fix [project] against the [genre] recipe."* → Derive recipe if not already in library, then run diagnostic mode with surgical fix list.
- *"Build a recipe library across cozy mystery, heist, locked-room thriller, and cosmic horror."* → Derive each, note crossover compatibility (e.g., heist + cosmic horror = a known hybrid slot).
- *"Compare the [project] against three adjacent recipes to pick the right slot."* → Slot-fit analysis before diagnostic.
