# Recipe Rewire Prompt — v1 → v2 migration (for GPT 5.5)

Operator instructions (for the human running this — not part of the model prompt):

1. **One recipe per conversation.** Fresh context each time; do not batch. Temperature low (≤0.4).
2. Paste, in order: (a) everything below the `=== PROMPT ===` line, (b) the full gold example `references/story_structure/recipes/ensemble_heist.md`, (c) the target recipe's CURRENT file from `references/story_structure/recipes/`.
3. The model must produce its **derivation notes first** and then the file. If it writes the file without notes, reject and re-ask — the notes are where the judgment happens.
4. Save the output file, then run the **Claude wiring self-check** from `skills/writer/story-recipe/SKILL.md` (tag grammar, emitter-prefixing, graph closure both directions, front-half obligations, climax preconditions, verbatim Wiring-tests block, no boilerplate). On FAIL, paste the error list back into the same conversation and ask for a corrected full file. Two failed correction rounds → flag the recipe for frontier-model handling.
5. The self-check covers syntax and graph closure, not dramatic judgment. After it passes, spot-read the derivation notes: if a flaw's firing beat contradicts the v1 text, or an edge feels arbitrary, reject.

=== PROMPT ===

You are migrating a TV-season story recipe from v1 (sequence-only) to v2 (causally wired). You will receive two documents after these instructions: a GOLD EXAMPLE (a finished v2 recipe — match its structure, register, and density exactly) and the TARGET RECIPE (a v1 recipe contaminated by a failed previous migration).

## Why the previous attempt failed — do not repeat it

The previous migration pass satisfied the format and failed the substance. It prepended the same boilerplate sentence to every beat ("Because the choice made during X leaves a consequence unresolved…"), generated contentless dependency tags ("E3-the-assembly-begins-consequence"), and assigned cast obligations round-robin (Planner→Beat 2, Second→Beat 3, …) instead of deriving them from the genre. That output was rejected wholesale. The entire value of this task is in the judgment the previous pass skipped: reading what the v1 text already implies about WHO causes WHAT, and making those implications explicit as edges.

## Phase 0 — Recover the v1

The TARGET RECIPE file contains the original v1 intact underneath the failed migration's additions. Strip, and do not reuse:
- In every beat cell: the leading boilerplate sentence (any sentence containing "leaves a consequence unresolved" or "irreversibly narrowing what remains possible") and the existing **Needs:** / **Sets up:** lines with their tags.
- In the cast table: the entire "Causal obligation" column content (sentences of the form "In Beat N, this flaw drives X to choose in a way that causes Y") and any "(turn: Beat N)" suffixes in the Arc column.
- The existing `## Wiring tests` section (you will re-insert it fresh).
- If "Common failure mode" bullets appear under Conformity rules, they belong to the v1 Caveats — treat them under the Caveats rules below.

What remains is the v1: Slot, Corpus, Emotional contract, cast (Function/Flaw/Arc/Relational position), Trope vocabulary, beat names + beat prose + emotional targets, Conformity rules, Variation rules, Caveats.

## Phase 1 — Derivation notes (output these BEFORE the file)

Write a short analysis, and only then the file:

1. **Flaw placement, per cast role:** quote the v1 phrase (from the Flaw, Arc, or a beat) that implies where this role's flaw fires, name the beat where it fires AS AN ON-SCREEN CHOICE the character makes, and name the later beat(s) that consume the consequence. If the v1 places a role's pressure mid-runtime, the flaw fires mid-runtime — never assign beats by position in the table.
2. **Latent edges, per beat:** what does the v1 prose already imply this beat plants or uses? (A casing implies geography someone later runs on; a public triumph implies a reputation that can be measured against a fall; a dismissal implies a warning someone pays for ignoring.)
3. **Ambiguities:** anything the v1 leaves unexplained that the wiring must decide (how does the antagonist learn X? who caused Y?) — state your resolution and which cast flaw or beat supports it.
4. **Climax inventory:** which earlier emissions the final two beats will consume, marking which are character CHOICES.

## Phase 2 — Write the complete v2 file

### Preserve verbatim from the recovered v1
Slot, Corpus, Emotional contract, Trope vocabulary (with anti-tropes), Variation rules (you may append ONE final bullet noting the wiring's edges are fixed while every edge's content varies — model it on the gold example's last variation bullet). Keep the beat COUNT, beat NAMES, beat ORDER, and every Emotional target cell unchanged. If an emotional target is theme-shaped ("reinforces the theme of X"), replace it with the audience emotion the moment produces — that is the only permitted target edit.

### Cast → `## Cast (FFAR+C)`
Columns: Role | Function | Flaw | Causal obligation | Arc (from → to, turn beat) | Relational position.
Each Causal obligation is written fresh from that role's specifics per your Phase 1 notes: the firing beat, the choice, the consuming beat(s), the cost. If the antagonist-function role's flaw reads as a job description ("believes in optimization", "maintains order"), sharpen it to a human motive consistent with the v1 text: class contempt, envy, wounded pride, a specific past humiliation, family vengeance. Derive each Arc turn beat from the v1 arc text (if the arc says "when the plan breaks," the turn is the beat where the spine breaks the plan).

### Beat spine
Rewrite each Beat cell as 2–4 causal sentences — a character's CHOICE plus what it irreversibly changes — keeping the v1 beat's content and specific imagery. The causation must BE the prose, not a clause bolted in front of unchanged v1 text. End each cell with:
**Needs:** [bare tags, or — for the opener]. **Sets up:** [tags, each with consumer pointer(s): `E4-omitted-layer (→E10)`].

**Tag grammar (strict):** `E<emitting-episode>-<concrete-artifact-noun>`. The noun names a story object: a lie, a debt, a wound, a tool, a secret, a body, a betrayal, a map, a reputation, a bargain, a humiliation. BANNED: tags whose noun is only "consequence", "choice", "cost", "constraint", "aftermath", "event", or "outcome"; tags prefixed with the consuming episode's number; the same tag emitted twice.

**Wiring rules (all seven must hold):**
1. Every beat except the opener consumes ≥1 earlier emission.
2. Every emission is consumed by some later beat's Needs line.
3. Every front-half beat (1–4) emits ≥1 thing the back half (5+) consumes.
4. The final two beats together consume emissions from ≥3 distinct earlier beats, of which ≥2 are character CHOICES (not facts or setup conditions).
5. Every charged cost (a death, a betrayal, a burned resource, a lost trust) visibly constrains a later beat.
6. Flaws fire as decisions whose consequences propagate — never as trait-displays that merely happen to a character.
7. The climax's method is something established and paid for earlier.

### Fixed block — insert verbatim between Conformity rules and Variation rules

## Wiring tests
- Delete-test: no episode can be removed without a later episode breaking.
- The climax consumes at least two character choices from distinct earlier episodes.
- Every named flaw fires as a choice whose consequence is visible in a later episode.
- Every relationship the cast table says moves shows its early state AND its changed
  state as on-screen actions.
- Every cost charged is paid: a later episode is harder in a named way because of it.

### Caveats sweep
Any v1 caveat stating a causal discipline ("plant the groundwork in beat N", "every breakage must do double duty") gets encoded into the spine's edges; it may remain in Caveats only as a parenthetical pointer ("now encoded in the wiring: …"). Human-reader notes (register dials, subvariants, genre-of-one warnings) stay as they are.

### Hard fail conditions
- Any 8+ word phrase appearing in two or more beat cells.
- Any Causal obligation cell sharing its sentence skeleton with another row.
- Any banned tag noun, consumer-prefixed tag, or dangling edge (a Sets-up nothing consumes; a Needs nothing emits).
- File length beyond the recovered v1's +15%.

### Self-check (print this before the file)
Confirm, in one line each: tag closure traced both directions; seven wiring rules; no banned nouns; beat names/order/targets match v1; preserved sections verbatim; length within budget.

Then output the complete file, fenced, ready to save as `references/story_structure/recipes/<name>.md`.
