# Combined Evaluation Rubric

**Status:** v0.3 — UNCALIBRATED (against the human corpus). v0.3 (2026-08-06)
ports the floor-discipline machinery from the screenplay-rubric workflow
(`260614 scoring rubric/workflow.md`, gen-3 "floor-disciplined" — same lineage
as this rubric's 12 criteria): burden-of-proof scoring, deterministic Cap
Rules, the evidence-quote admissibility rule, banned uplift phrases,
As-Submitted vs Potential split, and control artifacts. Full multi-judge
protocol distilled in `judge_workflow.md` (same directory). v0.2 adds the
Assumed-Competence Floor (Design principle 5): competence is a given, scored at
zero; the 1–5 scale is re-anchored to creative value above baseline; Execution &
Readability is demoted to a gate. Floor behavior validated on a slop specimen
(competent-empty → flat 1s, with discrimination preserved). Still
diagnostic/side-by-side until a human-corpus calibration run.

**Origin (2026-06-14):** Merges a 12-criterion screenplay-competition rubric
(industry-standard craft quality) with codeywood's existing evaluation
machinery (pitch-round 7-dimension rubric, dialogue-reviewer, AAA / centroid /
villain-vacuum diagnostics). Designed to be scored single-pass OR via the
dialectical-eval skill (`skills/writer/dialectical-eval/SKILL.md`).

## Design principles

1. **Two bands, kept separate.** Band A measures intrinsic craft quality
   ("is it a good story?"). Band B measures system/brief conformity ("is it
   on-brief, non-default, persona-faithful, buildable?"). Band B is reported as
   flags and gates alongside the Band A score — **never summed into it**. This
   mirrors pitch-round's Production-vs-Craft shortlist split (v2.2): collapsing
   the two into one number hides the signal that "good" and "on-brief/buildable"
   are different questions.

2. **Stage-aware.** Some criteria can't be evaluated on a 150-word pitch
   (Dialogue, Execution/Readability, fine Pacing need a script). Score only the
   criteria applicable to the artifact's stage. The aggregate is the **mean of
   applicable Band A criteria** (1-5), so stages with fewer applicable criteria
   aren't penalized.

3. **Equal weight (v0.1).** All applicable Band A criteria weighted equally. No
   weights are baked in until calibration shows which dimensions carry signal.

4. **Contestable vs checkable.** Each criterion is tagged for the
   dialectical-eval skill: contestable criteria get the for/against + blind-judge
   treatment; checkable criteria (observable facts) stay single-pass.

5. **Assumed-Competence Floor (v0.2, 2026-06-14).** All work in this pipeline is
   AI-produced or AI-proofread, so basic technical competence — clean prose,
   correct format, grammar, fluent/readable dialogue, internal coherence,
   graspability, buildability — is a **given**, not an achievement. It earns
   **zero** credit in the Band A score. Clarity, fluency, polish, consistency,
   "instantly graspable," "cleanly executed," and marketability-by-familiarity
   are table stakes; only *creative value above that baseline* is scored
   (specificity, originality, distinct voice, dramatization vs statement,
   earned vs asserted emotion, subtext, genuine stakes, a real idea). This is
   the centroid logic applied to scoring: competence IS the centroid, and the
   score rewards departure from it. Consequence: **competent-but-empty "slop"
   floors at 1, not a charity 2** (validated — see dialectical-eval findings).

## Band A — Craft Quality (the "is it good" score; 1-5 each, equal weight)

**Re-anchored scale (v0.2):** competence is assumed, so the 1–5 gradient measures
*creative value above the competence baseline*:
- **1** = cleanly executed but creatively empty / pure genre-default (the floor — competent slop lands here)
- **2** = mostly default with a faint flicker of specific merit
- **3** = real, specific creative merit, unevenly delivered
- **4** = strong and specific
- **5** = singular / exceptional

| # | Criterion | What judges evaluate | Codeywood lens absorbed | Stage | Dialectic |
|---|-----------|----------------------|-------------------------|-------|-----------|
| 1 | **Concept / Premise** | Central idea compelling, fresh, marketable, easy to grasp | Surprise; Mechanism Fidelity (partial) | Pitch + Script | Contestable |
| 2 | **Story Structure** | Clear beginning/middle/end, strong escalation and payoff | Structural Concreteness | Pitch (arc proxy) → Script | Contestable |
| 3 | **Character Development** | Characters distinct, emotionally engaging, changed by the story | Character Shadows (writers-room) | Pitch (weak) → Script | Contestable |
| 4 | **Protagonist Drive** | Clear goal, motivation, conflict, active role in plot | want→action→consequence→reframe (PR finding 17) | Pitch + Script | Contestable |
| 5 | **Conflict & Stakes** | Meaningful obstacles; stakes intensify and matter | Structural-Stakes Checklist Lane A | Pitch (proxy) → Script | Contestable |
| 6 | **Dialogue** | Natural, character-specific, purposeful, cinematic not expositional | dialogue-reviewer (12 principles) | **Script only** | Contestable |
| 7 | **Emotional Impact** | Makes the reader feel something specific (dread, laughter, catharsis…) | Pleasure Contract; Emotional critic; AAA tone-residue | Pitch (proxy) → Script | Contestable |
| 8 | **Originality / Voice** | Distinctive perspective, tone, worldview, stylistic signature | Originality critic; Centroid Busting (partial) | Pitch + Script | Contestable |
| 9 | **Pacing** | Momentum; scenes not too long, repetitive, or slow to turn | Plot Velocity test (AAA v2.4); Audience critic | Pitch (velocity proxy) → Script | Contestable |
| 10 | **Visual Storytelling** | Thinks in images, actions, behavior — not prose explanation | visual-translation skill; Producer critic (partial) | Pitch (proxy) → Storyboard/Script | Mixed* |
| 11 | **Theme / Meaning** | Something underneath the plot: a question, argument, truth, POV | — *(gap codeywood previously had no dimension for)* | Pitch (proxy) → Script | Contestable |
| 12 | **Execution & Readability** | Professionally formatted, polished, free of avoidable confusion/errors | Screenplay Viability (partial) | **Script only** | **GATE (v0.2) — not scored** |

**(v0.2) Execution & Readability is now a binary GATE, removed from the Band A
mean.** Under the Assumed-Competence Floor it is ~4 for everything and earns no
credit, so it no longer averages in. Evaluate it as a pass/fail check: *clears
basic professional competence? Y → assumed, proceed; N → flag as sub-floor.* A
"yes" is table stakes; only a "no" carries information.

\* **Visual Storytelling** splits: "does it name images/actions vs explain in
prose" is checkable; "are they genuinely *cinematic*" is contestable. Score the
checkable half single-pass and the cinematic-quality half dialectically.

**Aggregate (Band A):** mean of the applicable *scored* criteria, on the
re-anchored 1-5 scale. **Criterion 12 (Execution) is a gate, excluded from the
mean.**
- Pitch stage: criteria 1-5, 7-11 are scored (≈9); 6 is N/A; 12 is a gate.
- Script stage: criteria 1-11 are scored; 12 is a gate.
- Report the mean AND the full per-criterion vector — the vector is where the
  diagnostic value lives; the mean is for ranking. **Watch the *shape*, not just
  the mean: a dead-flat vector with no dimension ≥3 is the fingerprint of
  competent slop; real-but-flawed work shows peaks and troughs.**

## Floor Discipline & Burden of Proof (v0.3 — applies to every Band A score)

Ported from the floor-disciplined screenplay workflow; these rules are what kept
a known-slop control at its true floor after three judges independently drifted
it upward.

1. **Start at the floor.** Every criterion begins at **1** and is raised only
   when the text demonstrates the higher anchor. Clean execution, completeness,
   clear geography, a recognizable goal, visible objects, chronological
   progression, and understandable stakes can all still score 1.
2. **Burden of proof belongs to the higher score.** When evidence supports both
   N and N+1, use N.
3. **Evidence-quote admissibility** (also gemmawood `judge/RUBRIC.md`): *every
   score must quote the text that supports it — at both ends of a causal claim
   where relevant. A score without a supporting quote is inadmissible.*
4. **No invented readings.** Do not award credit for latent irony, contradiction,
   subtext, or thematic complexity unless the work actually dramatizes it. A
   reading the judge can invent is not demonstrated execution.
5. **Banned uplift phrases.** These phrases do not justify raising a score unless
   accompanied by a demonstrated, criterion-specific audience effect: *"complete
   progression," "clear stakes," "usable frame," "visible spine," "filmable
   gesture," "consistent motif," "could support."* (They are exactly what a
   generous LLM judge reaches for when it wants to raise a score without
   evidence — flag them in any rationale.)

### Cap Rules (deterministic ceilings, adapted to the 1-5 scale)

Diagnostic triggers that mechanically ceiling specific criteria. Caps are
ceilings, not target scores. Check each as a boolean BEFORE aggregating:

| Trigger | Caps (criterion ≤ score) |
|---------|--------------------------|
| Merely readable/formatted/coherent but generic | most criteria ≤ 1 (this IS the Assumed-Competence Floor) |
| On-the-nose dialogue (characters state feelings/theme directly) | Dialogue ≤ 2, Character Dev ≤ 2, Emotional Impact ≤ 3 |
| Passive protagonist (things happen TO them) | Protagonist Drive ≤ 2, Structure ≤ 3, Conflict & Stakes ≤ 3 |
| Cliché-symbol payload (rain, coffee, single tear, sad piano, airport goodbye, funeral speech, childhood photo) | Originality ≤ 2, Emotional Impact ≤ 3, Visual Storytelling ≤ 2 |
| No surprise (emotional arc predictable from the opening) | Concept ≤ 2, Structure ≤ 3, Originality ≤ 2 |

### As-Submitted vs Potential (dual score)

Score every criterion twice: **As-Submitted** (what the text demonstrates — the
official score, determines gates and rankings) and **Potential** (revision
ceiling — reported separately, never substitutes). Potential may exceed
As-Submitted only when a *specific underexploited strength already creates a
meaningful effect in the submitted text* — a familiar premise, usable frame,
clear deadline, complete structure, or object motif does not by itself justify
it. In the pipeline, Potential is the revision-priority signal fed back to the
writers room; As-Submitted is what gates.

### Control artifacts (judge-drift regression check)

Before trusting any scoring run, verify the judge against known anchors:
- **Floor control**: a deliberately competent-but-dead sample (canonical example:
  "The Last Coffee," `260614 scoring rubric/05 example/` — true score 12/120 ≈
  flat 1s here). If it starts scoring midrange, the judge has drifted and every
  gate has silently loosened.
- **Ceiling control**: a known-great professional script (Get Out and Chinatown
  runs recorded in dialectical-eval Validated findings; structural ceiling ≈3.6
  on this instrument).

## Band B — System / Brief Diagnostics (flags & gates, reported alongside — NOT summed in)

| Criterion | What it catches | Form | Stage | Dialectic |
|-----------|-----------------|------|-------|-----------|
| **Brief Compliance** | Hard constraints (format, location, prohibitions, ending req) honored | **Hard gate** — fail = must-fix before advancing | Pitch + Script | Checkable |
| **Mechanism Fidelity** | Persona being itself, not generic Claude (remove mechanism → pitch collapses) | Score 1-5, **diagnostic only** | Pitch + Script | Contestable |
| **Centroid Busting** | Silent defaults across medium / tradition / protagonist / time / tone / audience / stylization axes | Default count → `[CENTROID-CONVERGENCE]` if ≥3 | Pitch + Script | Checkable (count) |
| **Villain-Vacuum** | On-camera embodied antagonist vs faceless system | `[VILLAIN-PRESENT/ABSENT/GHOST]`; roster-level % aggregate | Pitch + Script | Checkable (3 questions) |
| **Producibility** | Can the AI pipeline actually build this? (cast size, environments, visual demands) | Producer-critic score 0-100; flag if <75 | Pitch + Script | Contestable |

**Gate behavior:**
- **Brief Compliance** is a hard gate — a non-compliant item is disqualified or
  routed to must-fix regardless of Band A score.
- **Centroid Busting / Villain-Vacuum** are diagnostics that bite at the
  *roster* level (e.g. >30% [CENTROID-CONVERGENCE] = the brief lacks constraint
  strength; <30% [VILLAIN-PRESENT] on a morally complex brief = systemic-
  antagonism default). Individual flags inform but don't auto-disqualify.
- **Mechanism Fidelity / Producibility** are reported beside the Band A score
  for production decisions but never inflate or deflate it.

## Relationship to the existing pitch-round rubric

This rubric is a **superset** of the pitch-round 7-dimension rubric. Mapping:

| Pitch-round 7-dim | Lands in |
|-------------------|----------|
| Mechanism Fidelity | Band B (Mechanism Fidelity) |
| Structural Concreteness | Band A #2 (Story Structure) |
| Brief Compliance | Band B (Brief Compliance, hard gate) |
| Surprise | Band A #1 (Concept) + #8 (Originality) |
| Screenplay Viability | Band B (Producibility) + Band A #12 (Execution) |
| Pleasure Contract Delivery | Band A #7 (Emotional Impact) |
| Centroid Busting | Band B (Centroid Busting) |

**Migration is forward-only and optional.** Existing pitch-round runs are not
retroactively re-scored. Do not rewire pitch-round's SKILL.md to use this rubric
without an explicit decision — this doc is the agreed rubric definition; wiring
it in is a separate step.

## Scoring procedure (single-pass or dialectical)

1. Determine artifact stage (pitch vs script) → fix the applicable criteria set.
2. **Competence gate (Execution & Readability):** pass/fail. A "no" flags the
   work as sub-floor; a "yes" is assumed and earns nothing.
3. **Band A:** score each applicable scored criterion on the re-anchored 1-5
   scale, giving **zero credit for competence/clarity/fluency** (Assumed-
   Competence Floor). Contestable criteria via dialectical-eval (for/against +
   holistic judge); checkable criteria single-pass. Aggregate = mean of scored
   criteria (Execution excluded).
4. **Band B:** evaluate each diagnostic; emit flags/gates. Do not add to the
   Band A mean.
5. Report: Band A mean + per-criterion vector (note its shape), Band B flags,
   and (during the pilot) the single-pass-vs-dialectical comparison.

## Scope & validity boundary (v0.2.1, 2026-06-14) — READ BEFORE USING A SCORE

This instrument judges **commercial-genre WRITING for an AI-video pipeline**. It
is NOT a universal film/screenplay quality oracle, and a low score is NOT a
verdict on a finished film. It **systematically under-rates** a specific class of
work, for four distinct reasons — only the first is intentional:

1. **By design:** the anti-prestige-centroid DNA (villain-vacuum, active
   protagonist, escalating external stakes, anti-art-house lean) deprioritizes
   the quiet/internal/passive-protagonist/ambiguous-fade mode on purpose.
2. **Blueprint, not film:** it scores a text artifact. Performance, sound design,
   editing, direction, timing of silence — where execution-dependent films live —
   are invisible to it. Directorial restraint (e.g. cutting away before a climax)
   reads on the page as "skips its climaxes."
3. **Restraint reads as absence:** the Assumed-Competence Floor rewards
   specificity / dramatization / active pursuit, so purposeful minimalism and
   hollow slop have a similar TEXT surface. The instrument separates them (slop
   floored at 1.1; a restrained art film at ~2.4) but **compresses the gap** far
   below the real quality difference.
4. **Density bias:** the dialectical method favors maximalist work that hands the
   FOR advocate more concrete choices to cite over spare, economical work.

**Evidence:** *Stutterer* (Benjamin Cleary, 2016 Academy Award, Best Live Action
Short) scored a recalibrated **~2.4** here — a great FILM grown from a modest
SCRIPT, its greatness added downstream of the page. The score is a defensible
read of the *blueprint*; it is meaningless as a judgment of the *film*.

**Rule:** never use this instrument as a film-quality oracle; never read a low
score as "weak film." It ranks commercial-genre writing within the pipeline's
mission. For spare/execution-dependent/art-house work it is out of scope. (A
"restraint/execution-aware" mode was considered and deferred — it pulls against
the anti-prestige-centroid mission this rubric exists to serve.)

## Validation plan

Earns load-bearing status only after a calibration run shows the Band A
aggregate (and especially the dialectically-scored contestable criteria) tracks
human/ground-truth verdicts better than the current single-pass rubric, with a
lower false-positive rate. Until then: diagnostic, side-by-side. See
`calibration_corpus.md` and `skills/writer/dialectical-eval/SKILL.md`.
