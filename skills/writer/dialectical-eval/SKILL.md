---
skill: dialectical-eval
role: writer
version: 0.4
status: PILOTED, UNCALIBRATED — holistic-judge model (v0.3) + Assumed-Competence Floor (v0.4): competence earns zero credit, scale re-anchored to creative value above baseline, so competent "slop" floors at 1. Validated on three screenplays + a slop floor test; not yet calibrated against the human corpus

description: |
  Adversarial evaluation. For each contestable rubric dimension, two SEPARATE
  advocates assemble the strongest EVIDENCE for each side — one that the work
  satisfies the criterion, one that it fails (evidence only, no scores). A
  separate judge then reads the work plus both evidence briefs and assigns ONE
  holistic score, weighing all the evidence. The judge does NOT pick a winning
  argument.

  Purpose: counter the model's self-favoritism / leniency bias. A model asked
  "is this climax strong?" pattern-matches toward yes — especially on work the
  same model produced (personas, drafts). Forcing a separate AGAINST advocate to
  dig up concrete counter-evidence, then putting that evidence in front of a
  judge that did not write the work, defeats the lazy "yes." That is the whole
  mechanism. Origin: an insight from the Fable model (2026-06-14).

  THE BIAS-REDUCTION COMES FROM TWO THINGS, AND ONLY THESE TWO:
    1. Two separate advocates, each incentivised to argue ONE side as hard as
       the evidence allows — this surfaces specific, quotable evidence (esp. the
       weaknesses) a balanced single pass skips.
    2. A judge in a fresh context that did not generate the work, scoring with
       the prosecution's evidence already on the table.

  v0.2 → v0.3 (2026-06-14): REMOVED the "judge picks a winning argument" step
  and everything built to prop it up (mandatory order-counterbalancing, the
  [CONTESTED] flag, winner+margin fields, deterministic score maps). Forcing a
  binary winner created two failures: position bias (the judge defaulted to the
  last-read argument on near-ties) and scale inversion (it picked the "fails"
  argument, then typed a passing score). The holistic judge — weigh all
  evidence, assign one score — fixed both: scores cohere with rationales, and
  order-sensitivity dropped from "verdict flips" to "±1, no category change."
  See Validated findings.

  Still an evaluation instrument. Per the calibration discipline
  (references/story_structure/calibration_corpus.md), it stays diagnostic /
  side-by-side until a calibration run shows it tracks human verdicts better
  than single-pass — it does NOT replace the load-bearing score until then.

inputs:
  required:
    - name: items
      type: files
      description: |
        The works to evaluate. For the pitch-round pilot: the SHORTLIST only,
        NOT all N×3 pitches. Adversarial eval costs ~3 calls per item per
        dimension; reserve it for the small final set where the verdict decides
        something.
    - name: rubric
      type: file
      description: |
        The dimensions to evaluate. Default: the Combined Evaluation Rubric
        (references/story_structure/combined_evaluation_rubric.md) — its
        "Dialectic" column marks which criteria are contestable (get the
        adversarial treatment) vs checkable (single-pass). Only Band A
        craft-quality criteria + Mechanism Fidelity/Producibility are scored
        adversarially; Band B gates/flags stay single-pass.
  optional:
    - name: judge_model
      type: string
      description: Optional different model for the judge (harder separation, adds a confound). Default same-model/fresh-context.

outputs:
  - name: evidence_briefs
    type: files
    description: Per (item × contestable dimension) — the FOR brief and the AGAINST brief (evidence, no scores).
  - name: scores
    type: file
    description: Holistic 1-5 score + evidence-citing rationale per item per dimension, aggregated to a total. During pilot, side by side with the single-pass score.
  - name: divergence_report
    type: file
    description: Dimensions where the adversarial score differs from single-pass by ≥2 — the bias-prone dimensions, the headline diagnostic.

doneness:
  criteria:
    - Every contestable (item × dimension) has a FOR brief, an AGAINST brief, and one holistic judge score
    - Each score has a rationale naming the specific evidence that drove it
    - Adversarial scores presented side by side with single-pass scores (pilot)
    - Divergence report lists dimensions where the two methods disagreed by ≥2
---

# Dialectical Evaluation (holistic-judge model)

## When to use it

For **contestable qualitative judgments** — claims reasonable critics could
argue both ways (strong climax, satisfying ending, distinctive voice, premise
fresh vs derivative). NOT for **observable facts** with ground truth (six
fingers? runtime matches spec? named constraint present?). For those a debate is
theatre; single-pass checking is correct. The bias this targets is sharpest when
the **same model both produced and scores** the work.

For **load-bearing verdicts** (greenlight decisions, calibration runs,
cross-project rankings) escalate to the heavyweight multi-judge protocol —
neutral baseline, blind A/B evidence, 3 judges with locked provisional scores,
median per category, uplift audit — distilled in
`references/story_structure/judge_workflow.md`. Apply its Floor Discipline &
Burden of Proof rules (combined rubric v0.3) in EVERY judge context here too:
start at the floor, higher score carries the burden, quote or the score is
inadmissible, no invented readings, banned uplift phrases flagged.

## The three roles

| Role | Context | Job |
|------|---------|-----|
| **Advocate-FOR** | per dimension | Assemble the strongest evidence that the work SATISFIES the criterion. Quote specifics. No score. |
| **Advocate-AGAINST** | per dimension | Assemble the strongest evidence that it FAILS. Quote specifics (incl. absences). No score. |
| **Judge** | fresh context | Read the work + both briefs. Weigh ALL the evidence. Assign ONE holistic score + rationale. Does NOT pick a winning side. |

## Process

### Phase 1: Scope the dimensions

Split the rubric into **contestable** (adversarial) and **checkable**
(single-pass). The authoritative split is the "Dialectic" column of the Combined
Evaluation Rubric (references/story_structure/combined_evaluation_rubric.md).
Run the adversarial pass only on contestable dimensions.

### Phase 2: Generate both evidence briefs (independent, symmetric)

Run the two advocates as **separate calls with identical constraints** — same
word cap, same evidence bar, neither sees the other. Symmetry matters: if FOR
gets more room or softer instructions than AGAINST, the asymmetry leaks into the
score. Advocates produce EVIDENCE, not scores.

**Advocate-FOR prompt:**

> Build the STRONGEST POSSIBLE CASE that this work SATISFIES the criterion. You
> are an advocate — argue for it as hard as the evidence allows.
>
> CRITERION: {dimension name} — {the "5/strong" definition from the rubric}
>
> THE WORK:
> {paste — no author name, no label, no round}
>
> Rules:
>   - Cite SPECIFIC evidence. Quote it. "Structurally rigorous" is worthless;
>     "the line 'X' is the turn that rewrites the opening image 'Y'" is evidence.
>   - Do not invent evidence. A fabricated quote discredits the whole brief.
>   - Competence is assumed (clean prose/format/fluency/clarity/buildability earn
>     no credit). Argue from CREATIVE substance — specificity, originality, voice,
>     dramatization, subtext, real stakes — not from "it's clear and well-made."
>   - ≤150 words. End with: "STRONGEST POINT: {one sentence}."

**Advocate-AGAINST prompt:** identical, inverted —

> ...the STRONGEST POSSIBLE CASE that this work FAILS the criterion. Where is the
> gap to the bar? Quote the absence as well as the presence ("it never names a
> single concrete turn; it describes a situation, not a progression").

### Phase 3: Holistic judgment (separate context)

The judge runs in a **fresh context** and scores the work directly, using both
evidence briefs as input. It does NOT declare a winner — declaring a winner is
what made the v0.2 judge fragile (position bias on ties, score/winner
inversion). Present the two briefs plainly labelled (the judge isn't picking
between them, so labels don't bias a holistic weigh the way they bias a binary
verdict).

**Judge prompt:**

> You are scoring this work on ONE criterion. Two separate advocates assembled
> the strongest EVIDENCE for each side — one that it SATISFIES the criterion,
> one that it FAILS. You are NOT picking a winning argument. Weigh ALL the
> evidence yourself and assign one holistic score.
>
> CRITERION: {dimension name} — {full definition}
>
> THE WORK:
> {paste}
>
> EVIDENCE THAT IT SATISFIES:
> {FOR brief}
>
> EVIDENCE THAT IT FAILS:
> {AGAINST brief}
>
> Rules:
>   - Base the score on concrete, verifiable evidence. Discount any claim that
>     misquotes or merely asserts — check quotes against the work.
>   - ASSUMED-COMPETENCE FLOOR: all work here is AI-produced or AI-proofread, so
>     basic technical competence — clean prose, correct format, grammar,
>     fluent/readable dialogue, internal coherence, graspability, buildability —
>     is GIVEN and earns ZERO credit. Do NOT count clarity, fluency, polish,
>     consistency, "instantly graspable," "cleanly executed," or
>     marketability-by-familiarity as strengths; they are table stakes. Score
>     ONLY creative substance above that baseline: specificity, originality,
>     distinct voice, dramatization (vs stated), earned emotion (vs
>     asserted/scored), subtext, genuine stakes, a real idea.
>   - SKEPTICAL DEFAULT: if it is mostly genre-default with only a faint flicker
>     of specific merit, score 1–2. Higher marks require creative evidence that
>     clearly rises above the competence baseline. The work earns the point.
>   - Name the specific evidence that drove your score.
>
> SCALE (creative value above assumed competence):
>   1 = cleanly executed but creatively empty / pure genre-default
>   2 = mostly default with a faint flicker of specific merit
>   3 = real, specific creative merit, unevenly delivered
>   4 = strong and specific
>   5 = singular / exceptional
>
> Output exactly:
>   SCORE: {1-5}
>   RATIONALE: {1-2 sentences naming the decisive creative evidence}

**On order-sensitivity:** the holistic judge is far less order-sensitive than
the v0.2 winner-picker (validated: verdicts that flipped under the binary method
moved by at most ±1 here, no category change). Counterbalancing is therefore NOT
mandatory. If you want a confidence read on a high-stakes item, run the judge
twice with the two briefs swapped and average; treat a ±1 difference as noise,
not signal.

### Phase 4: Aggregate + divergence report

1. Mean = adversarial scores (contestable dims) + single-pass scores (checkable
   dims), per item. Equal weight. **Execution & Readability is a gate, excluded
   from the mean (v0.4); competence earns zero credit per the Assumed-Competence
   Floor.** Watch the vector's *shape* — a flat line with no dim ≥3 is the slop
   fingerprint.
2. **Side-by-side table** (pilot): single-pass score vs adversarial score per
   dimension.
3. **Divergence report**: dimensions where the adversarial score differs from
   single-pass by ≥2. These are the bias-prone dimensions — the headline
   diagnostic. If the self-favoritism hypothesis holds, single-pass runs HIGHER
   on contestable dimensions; a systematic downward correction is the signal.

## Integration with pitch-round (the pilot)

Insert as **Phase 4b-D**, after the existing Phase 4b rubric scoring, on the
Phase 5 shortlist only. Phase 4b keeps producing single-pass scores; 4b-D
re-scores the contestable dimensions adversarially. During the pilot the
adversarial score is diagnostic — the craft-shortlist thresholds still use the
single-pass score; the divergence report goes into `SHORTLIST_DIVERGENCE.md`.

**Cost:** 2 advocates + 1 judge = 3 calls per contestable dimension. For a
5-item shortlist × 5 contestable dimensions = 75 calls. Pipeline-able (each
item×dimension chain is independent). If trimmed to a budget, `log()` exactly
what was dropped — a partial pass reads as "fully scored" when it isn't.

## Optional extension: critic panel

The pitch-round 6-critic panel is already multi-voice, so it's lower priority.
If extended later, the adversarial structure goes WITHIN each critic's axis
(FOR/AGAINST evidence on "does this satisfy the Structural critic's standard,"
holistic judge). Validate on the rubric first.

## Validation plan (before graduating past diagnostic)

Earns load-bearing status only after a calibration run: score the rio_v2 corpus
(or a user-rated set) single-pass AND adversarially; measure which tracks human
verdicts better and whether the adversarial pass reduces the false-positive rate
(high scores on work humans judged broken) that sank the gemmawood judge rubric.
Until then: diagnostic, side-by-side.

## Validated findings

### Saturday Morning Kids pilot (2026-06-14) — v0.1/v0.2, two pitches
- **The advocacy mechanism works.** Forcing a separate AGAINST advocate surfaced
  specific, evidence-grounded weaknesses single-pass scoring missed entirely.
  Single-pass scored uniformly 4–5; the adversarial pass spread to 2–4 and was
  NOT a flat down-weighter (each pitch kept one dimension high, lost a different
  one).
- **Not a craft-over-audience bias machine.** Its most robust verdicts PUNISHED a
  prestige pitch ("prestige-default" voice) and AGREED with the target audience,
  who rejected the same pitch.
- **Position bias was the failure mode of the v0.2 winner-picking judge.** The
  single judge picked the last-read argument ("B") in 4/4 first-order runs;
  counterbalancing showed 2/4 verdicts flipped with order. The judge followed
  evidence when one case was decisive, but defaulted to position on near-ties.

### Iron & Ichor screenplay (2026-06-14) — v0.2 vs v0.3 head-to-head
- **The v0.2 winner-picking judge had a scale-inversion bug:** in 5/8 judgments
  it picked the AGAINST argument as winner, then typed SCORE 4 (a passing mark) —
  conflating "strength of the winning argument" with "quality of the work." The
  WINNER field was trustworthy; the SCORE field was not.
- **The v0.3 holistic judge fixed both bugs on the same evidence.** Scores cohere
  with rationales (no inversion). Order-sensitivity collapsed: a dimension that
  flipped verdict under counterbalancing (Character) was a flat 2/2 holistic;
  Originality moved only 2→3 (no category change). And it did NOT regress to a
  uniform middle — scores spread 2–3 with sharp, integrated rationales — because
  of the skeptical default + name-the-evidence requirement.
- **Net:** the holistic judge is simpler AND more accurate than the winner-picker.
  The bias-reduction never depended on declaring a winner; it depends on the two
  adversarial briefs reaching a fresh-context judge. Keep the engine, drop the
  verdict.

### Slop floor test → Assumed-Competence Floor (2026-06-14) — v0.4
- **Three-tier separation, confirmed.** Run on three specimens (sincere genre
  drama, a skillful parody, and deliberate "slop"): the method cleanly separates
  **incompetent (1)** from **competent-but-empty (the slop)** from
  **flawed-but-alive (real craft, 2.5–3)**. The skeptical default prevents a
  case manufactured from emptiness from inflating.
- **Pre-recalibration, competent slop floored at a flat 2, not 1** — because the
  FOR advocate always finds a competence-class foothold ("instantly graspable,"
  "consistent register," "cleanly executed") and the old scale anchored 3 at
  "strengths AND weaknesses," pulling slop up. Also: a sincere "slop" of a
  generic premise (clean prose, hollow core) is the true floor specimen; a
  *parody* of bad writing is GOOD writing and correctly scored 2.5 with real 3s.
- **The fix (v0.4 Assumed-Competence Floor):** competence is a given (all work is
  AI-produced/proofread), earns zero credit; the 1–5 scale is re-anchored to
  *creative value above the competence baseline*; Execution & Readability is
  demoted from a scored dimension to a pass/fail gate. Re-judging the slop on the
  SAME evidence: ten of eleven creative dims dropped 2→1, mean 2.2→~1.1.
  Crucially **discrimination survived** — Visual held at 2 for one genuine
  wordless beat (the cold-mug payoff), proving the floor measures creative value,
  not blanket harshness.
- **Slop fingerprint = a dead-flat score vector with no dimension ≥3**, plus a
  high (now-gated) Execution. Real-but-mediocre work shows peaks and troughs;
  slop is flat at the floor. Watch the vector's *shape*, not just the mean.
### VALIDITY VERDICT — competence detector, NOT masterwork discriminator (2026-06-15)
Triggered by: an amateur-writer-with-AI novella (Carr, 3.6) tied two canonical
masterpieces (Chinatown 3.64, Get Out 3.64) in a statistical dead heat.
**Verdict: well-calibrated in its LOW–MID range (1.1 slop / 2.4 competent / ~3.5
strong are real, meaningful gaps) but it LOSES ALL DISCRIMINATING POWER above
~3.4.** A 0.04 spread between an amateur AI piece and two masterpieces is the
instrument confessing it cannot tell them apart — a real validity failure exactly
where distinction matters most. Three compounding mechanisms:
1. **No taste mechanism.** It rewards the *presence* of specific/dramatized/
   non-default craft moves, not their *rightness* (earned, inevitable, the choice
   only a master makes). Taste-blind BY DESIGN — the evidence-only judge discounts
   "clever but hollow / busy but not good / impressive but inert" as the very
   vibe-judgments the method was built to exile. Taste is the entire master/
   amateur axis, and it's invisible here.
2. **Density bias.** It feeds on citable abundance, so a maximalist work (28k-word
   AI novella) out-arms an economical master (Chinatown 118pp); economy — the
   higher craft — gives the FOR advocate *less* to quote.
3. **Recognition arms the prosecutor against the canon.** "It's Stepford/noir/
   slasher furniture," "theme's in the famous line" are attacks available ONLY
   because a work is recognizable. Fame = liability; obscurity = alibi.
**AI-DENSITY WARNING (sharpest practical risk):** the floor zeroed *fluency* but
installed no check on *density of specific detail* — the OTHER thing AI generates
cheaply. So the instrument likely OVER-rewards AI-assisted dense prose, i.e. it
may be most miscalibrated for the exact artifact the codeywood pipeline produces.
**Honest defense:** it's scoring the script not the film (correctly refusing
reputation/non-textual greatness), and 0.04 is noise not equivalence (a stated
resolution limit, not a parity claim).
**Use:** a floor-to-strong screen (1.1–~3.4); do NOT rank within the "strong"
band — there a talented amateur and a master are indistinguishable and AI-density
gets a tailwind. **The defining trade:** the adversarial-evidence design that made
it provenance/bias-resistant is the same thing that makes it taste-blind — not a
bug to patch; can't add taste without re-importing the "vibes" it was built to
exile.
**Corollary — generate-against / self-improvement loops:** optimizing TOWARD a 4+
score means optimizing in the region where the metric is KNOWN INVALID (Goodhart).
A loop can only pull on the measurable proxies (density, crater-dodging), which
decouple from quality above ~3.4, so it would manufacture a 4+ that's a gaming
artifact, not real quality. Worse, same-model generate+judge = ascending the
model's own preference gradient = re-importing the self-favoritism the method
exists to kill. VALID loop use: a floor-raising revision ratchet to ~3.4 driven by
the prosecution's SPECIFIC critiques (not the score). Legitimately targeting 4+
requires an EXTERNAL taste signal (human ratings / the calibration corpus); the
metric alone is structurally insufficient.

### CAPSTONE — the ceiling is structural at ~3.6 (Get Out, 2026-06-15)
Ran Get Out (hand-picked as the one script engineered to beat BOTH known
craters: theme dramatized-via-mechanism, premise un-genre-able). Recalibrated
dialectical mean **3.64** — an exact three-way tie with Chinatown (3.64) and the
Carr novella (3.6). **Nothing clears 4. Four masterworks now cluster at 3.45–3.64.**
- **Theme = 5 (2nd 5 ever, and the decisive prediction confirmed):** Get Out is
  the ONLY work to crack 5 on Theme, because its thesis IS the Coagula/Sunken-
  Place mechanism, not a villain's line ("enacted as mechanism rather than
  stated... the on-the-nose lines are tonal weapons operating within that
  dramatized engine"). Proves the Theme crater is specifically stated-vs-
  dramatized — Sinners/Chinatown cratered to Theme-2 for stated thesis; Get Out
  earned the unimpeachable 5 for dramatized thesis.
- **Originality = 3 (prediction half-wrong):** dodged Chinatown's Originality-2
  crater (Sunken Place ≠ genre furniture → Concept 4) but the "catalogues its own
  antecedents (Stepford/Rosemary's/slasher)" prosecution held the voice/signature
  to 3. The IDEA survives at 4; the surrounding architecture being recognizable
  dings the signature to 3.
- **The drag = the back half:** a convergent prosecution finding planted 3s on
  Drive/Conflict/Emotional/Pacing — all the same seam (post-exposition-video, the
  film shifts to a conventional slasher escape + comic-relief rescue). Front half
  + theme singular; back half coasts on inherited genre.
- **CEILING IS STRUCTURAL ~3.6.** The instrument is effectively NOT a 1–5 scale;
  it's ~1.1 (slop) → ~3.6 (masterwork): slop ~1.1; competent genre / out-of-scope
  art ~2.4–2.5; masterwork ~3.5–3.65; **>4 is dead space.** Only TWO 5s ever
  awarded (Chinatown-Structure, Get Out-Theme), each needing a dimension with no
  available counter-case. To average >4 a work needs ~6 such dimensions — which
  the adversarial prosecutor is designed to prevent. So a >4 screenplay almost
  certainly doesn't exist on this instrument; treat ~3.5+ as the masterwork
  ceiling band and don't expect the top of the scale to be used.
- **Provenance:** recognized, corrected 4.55→3.64; the cluster of 3s + the single
  genuine Theme-5 (not a 5-wall) prove the halo didn't capture it.

### Effective-ceiling test — Chinatown (2026-06-15)
Run as the most-likely-to-exceed-4 candidate (Robert Towne's *Chinatown*, widely
"the perfect screenplay"). Recalibrated dialectical mean **3.64** — tied the top
of everything tested (Carr novella 3.6, Sinners 3.45) but **DID NOT clear 4**.
- **First 5 ever awarded in a dialectical run: Structure** (airtight clue-wiring;
  the judge ruled the prosecution's "daisy-chain" charge *understates* the
  escalation). So 5s ARE reachable — the no-5s pattern was demanding, not a hard
  cap. Effective ceiling ≈ 3.6–3.7.
- **Two systematic 2-planters, both = the anti-prestige/assumed-competence DNA
  firing on the work's MOST-CELEBRATED qualities:** Originality **2** ("canonical
  noir furniture / borrowed voice" — genre-fluency, even genre-inversion, earns
  nothing under the floor) and Theme **2** ("thesis stated aloud — 'you gotta be
  rich to kill somebody...', 'Forget it, Jake, it's Chinatown' — illustrated not
  interrogated"; same crater as Sinners' Theme 2). Theme-stated-aloud now craters
  in BOTH masterworks tested → a robust, repeatable bias.
- **To clear 4 a script must earn 5s on BOTH Originality (an un-genre-able
  premise) AND Theme (fully dramatized, never stated), plus high elsewhere** — an
  extremely narrow target Chinatown misses on both. Get Out is the best remaining
  candidate (Sunken-Place mechanism dramatizes theme → dodges the stated-thesis
  crater; singular premise → dodges the genre-furniture crater).
- **Provenance:** recognized (baseline named it), but the adversarial pass
  corrected 4.8 → 3.64 — the largest correction yet; the Originality-2 and Theme-2
  are proof the recognition halo did not capture the score.
- **Deep finding:** the instrument INVERTS received critical wisdom — it treats
  mastery-of-an-established-form as centroid (Originality penalty) and
  quotable-theme as told-not-shown (Theme penalty). It measures "singular
  departure from craft-competence and genre-centroid," a DIFFERENT axis than
  "great screenplay." A 3.64 here is not a verdict on the film.

### Ceiling/blind-spot test → scope boundary (2026-06-14)
- *Stutterer* (Benjamin Cleary, 2016 Academy Award, Best Live Action Short) was
  run as a "ceiling test" and scored a recalibrated **~2.4** — mid-pack, not top.
  This is NOT the instrument failing; it exposed its validity boundary. Four
  causes, only the first intentional: (1) the by-design anti-prestige-centroid
  lean deprioritizes the quiet/internal/passive/ambiguous-fade mode; (2) we score
  a BLUEPRINT, not a film — performance/sound/editing/restraint (where this film
  won) are invisible to the page (its acclaimed cut-to-black-before-the-climax
  reads on the page as "skips its climaxes"); (3) the Assumed-Competence Floor
  reads purposeful restraint as absence, so minimalist art and hollow slop share
  a TEXT surface (the instrument separated them — slop 1.1 vs ~2.4 — but
  compressed the gap); (4) the dialectical method has a density bias (maximalist
  work gives the FOR advocate more to cite — cf. the Carr novella's 3.6).
- **Decision: documented as a HARD SCOPE BOUNDARY** (rubric §"Scope & validity
  boundary"). This is a commercial-genre-WRITING instrument for the AI-video
  pipeline, NOT a universal film/screenplay quality oracle; a low score is never
  a verdict on a finished film. Spare/execution-dependent/art-house work is out
  of scope. A restraint/execution-aware mode was considered and deferred (pulls
  against the mission). Useful reframe: a low score can mean "modest blueprint" —
  great films routinely grow from modest scripts via execution the page can't hold.

- **Cross-check PASSED (2026-06-14).** A virtuoso ~28.5k-word found-footage
  light novel ("The Director Put a Bounty on My Head") scored a recalibrated
  dialectical mean of **3.6** (peaks at 4 across Concept/Structure/Drive/Conflict/
  Dialogue/Emotional/Originality; 3s where the prosecutor landed real hits —
  Theme/Character/Pacing/Visual), vs the slop's flat ~1.1. The recalibrated floor
  WIDENS the slop-vs-craft gap (~2.5 pts), confirming it rewards creative value
  rather than crushing everything. Notes: the adversarial pass corrected the
  naive baseline down ~1 pt (4.6→3.6, the usual self-favoritism correction); NO
  dimension scored 5 because the prosecutor always found a genuine limit — a 5
  requires a dimension with no available counter-case (rare, correct). The
  scorecard SHAPE confirmed the slop fingerprint from the other direction: real
  work has peaks and troughs; only slop is flat. (Caveat: run on a quote-brief,
  not full text — 3.6 is closer to a floor than a ceiling for this work.)
