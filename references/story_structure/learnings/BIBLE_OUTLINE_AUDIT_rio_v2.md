# Bible-vs-Outline Causal-Density Audit — Rio v2

**Date:** June 10, 2026
**Method:** All six rio_v2 runs (000 baseline + 001–005). For each run: (1) inventory the story bible's discrete dramatic commitments — relational engines (relationships with a stated evolution), causal locks (explicit "this forces / this locks in" cause→consequence commitments), and required sequences; (2) trace each commitment's survival through 05a draft → 05b2 beat sheet → 05c improv → final outline; (3) causally audit the final outline itself (irreversibility per episode, counterfactual deletion test, longest dependency chain, climax precondition count). Run-002 audited directly; runs 000/001/003/004/005 by parallel analyst agents applying the same rubric.

## Verdict

**The hypothesis from the project state report is confirmed, and the mechanism is now located.** The causal and relational material in the bibles is largely *generated and then destroyed in transmission* — not absent from generation. The loss is two-stage and architecturally guaranteed:

1. **Relational evolutions die at bible→5a.** The 5a lead draft is a key-cast list plus a ~2-paragraph season arc. Every relationship with a trajectory ("rivalry → protective bond", "waits for the exact moment to betray him mid-heist") is compressed to a static one-clause cast label. The editor can copy a label; it cannot dramatize an evolution it never saw.
2. **Causal wiring dies at beats→final.** The beat sheet (which *does* see the bible) faithfully carries the bible's required *scenes* — but as disconnected event lines, with the connective "this forces / this locks in / because" clauses stripped. The editor then packs causally-orphaned beats into episodes 1:1.

The editor — the only step that writes the final ten episodes — **never receives the bible** (`divergence/outline.py`: story_bible_md "does NOT travel through the per-step renderer"; `editor_synthesis_prompt` inputs are logline, key cast, 5a draft, beat sheet, improv). The demonstration-not-consequence structure diagnosed in the project state report is therefore substantially a **pipeline information-plumbing failure**, not only a Gemma reasoning deficit.

## The numbers

| Run | Bible commitments | Dramatized-causal in final | Single-beat | Label-only | Absent | Contradicted | Deletable episodes | Longest causal chain | Climax precondition choices |
|---|---|---|---|---|---|---|---|---|---|
| 000 (baseline) | 17 | 2 | 10 | 3 | 0 | 2 | 4 (E1,E3,E4,E6) | 4 | 3 |
| 001 † | 19 | 3 | 4 | 0 | 12 | 0 | 4 (E2,E4,E6,E7) | 4 | 3 (1 hard) |
| 002 | 14 | 2 | 6 | 3 | 2 | 1 | 3 (E1,E3,E4) | 5 (E6→E10) | 3 |
| 003 | 19 | 5 | 10 | 1 | 3 | 0 (2 partial) | 6 (E1,E3,E4,E5,E6,E8) | 3 | 2 |
| 004 | 20 | 5 | 8 | 0 | 7 | 0 (1 flag) | 4 (E1,E3,E4,E8) | 4 | 0–2 |
| 005 | 17 | 3 | 10 | 3 | 1 | 0 | 5 (E2,E3,E5,E6,E7) | 3 | 2 |
| **Total** | **106** | **20 (19%)** | **48 (45%)** | **10** | **25** | **3+** | **26/60 episodes (43%)** | median 4 | median 2–3 |

† Run-001 is anomalous — see Pipeline hygiene below.

Reading the table:

- **Only ~1 in 5 bible commitments survives as dramatized causation** (plays across ≥2 episodes with visible consequence). Nearly half become single-beat vignettes — the scene happens, nothing downstream consumes it.
- **43% of all episodes are deletable** — no later episode breaks if they're removed. Deletable episodes cluster in E1–E6: the front half of every season is demonstrations; causal chains only ignite around E5–E7. This matches the recipe beat spine (beats 1–6 are assembly/casing setup), so the recipe floor is part of why the front half is inert.
- **Climaxes depend on 0–3 earned character choices.** Run-004's climax depends on *zero* prior choices in the strict reading — everything it needs is event/fact setup or decided inside the finale itself. Run-005's central causal motor (Val's hidden plan to use Nash in the ritual) exists only as a cast-list clause; the climax ritual "arrives un-chosen by anyone on screen."

## The key reframe

**Gemma already writes causality — at step 4e.** The bibles are full of propagating-consequence language: "the collapse of this lie in the mid-season transforms his complicity into rage" (000), "the complication in Episode 7 forces him to admit he is nothing without the specialists" (002), "polishing the presentation rather than fixing the water-pump causes Rosa to reclassify his drive as betrayal" (003), "the valve crushed in Ep 8 forces Nash to stop clinging to the past" (005). These are exactly the choice→consequence structures the project state report says the model can't produce. It produces them. The pipeline then launders them out through two compression steps and an editor that never sees the source document.

Recurring evidence patterns across runs:

- **Contradiction by blind editing:** run-000's bible commits to Leo dying in the Sump and the Isadora confrontation being "a realization, not a fight" — the final outline has Leo survive and win a fight. Run-002's editor explicitly chose "Calvin's logical rigidity over Elsa's need for emotional validation," discarding the bible's central bond arc. The editor isn't overruling the bible; it doesn't know the bible exists.
- **Beat-sheet-as-sole-carrier:** in run-005, four of five required sequences reached the final outline *only* via the beat sheet, stripped of their "this locks in" clauses — e.g., the wrong-shoes funeral arrives severed from the father's-shame motive it was built to dramatize, reading as a class vignette instead of antagonist characterization.
- **Improv recovers voice, not causation:** 05c frequently carries bible dynamics in full (Val's blood-debt, Rosa's gaze at Lou) — but the editor treats improv as VOICE, and the causal content doesn't make it into episode structure. In run-003, Rosa's improv even *restores* the bible's final image (her looking at Lou); the final outline drops both of them from the closing scene anyway.
- **Cast attrition = engine attrition:** characters who exist primarily as one half of a relational engine (Kurt Geyer, Elsa Holt, Stephen Ocean, Nima Kway, Lucille Gante, Omari Jamil) are cut at 5a, and the engine dies with them. Meanwhile 5a sometimes invents non-bible characters (Pieter Maes, Layla Safi) who survive to the final with more presence than bible commitments.
- **Baseline vs persona:** run-000 (no persona) shows the same loss profile — the laundering is architectural, not persona-induced. Its distinguishing feature is a near-mechanical 18-beats→10-episodes transcription and improv voices collapsing into the prestige-centroid "audit/ledger" register ("ledger" resurfaces twice despite the viral purge).

## Pipeline hygiene findings (incidental)

1. **Run-001 is not a valid sample.** It has no 05b2 beat sheet and no 05c improv on disk, and its final outline contains verbatim 04c/04d material plus four characters absent from 5a's key cast — the editor in that run demonstrably saw upstream context the current architecture says it shouldn't. Likely produced by the older code path behind the stale RUN_FAILED.md, then recorded as "complete" on resume. The pipeline summary's "5 completed" overstates the evidence base for the June 2 architecture by one run.
2. **Editor isolation held in the other four audited runs** (leakage check: none) — the architecture does what the code comment says, which is precisely the problem.

## Implications for the next phase

The cheapest available intervention on the project's central problem is not teaching Gemma dramatic causality — it's **stopping the pipeline from discarding the causality Gemma already produces**:

1. **Give the editor the bible** (or a distilled *causal contract* extracted from it: the numbered engines/locks/sequences, in exactly the inventory form this audit used). One-line change in transmission policy; testable by re-running the editor step on existing run artifacts with the bible added.
2. **Make the beat sheet carry wiring, not just events.** Each beat names what it *requires* and what it *causes*. Per the established Gemma findings, design this as a whole-output property (an outline where the deletion test fails for ≤2 episodes) rather than a per-beat "must include" field that gets bolt-on-gamed.
3. **Protect relational engines through 5a** — either a required "relationship trajectories" section in the 5a draft, or route the bible's relationship section directly to the editor alongside the improv.
4. **The audit rubric itself is the missing evaluator prototype.** Commitment-survival tracing + the counterfactual deletion test + climax-precondition counting produced consistent, discriminating numbers across six runs — exactly the "measure causal accumulation directly" instrument the challenge inventory calls for (Challenge 3). It is automatable as a judge prompt.

## Caveats

- One lineage, five valid runs, one judge family (Fable 5 analysts; run-002 by the same model directly). No human calibration yet — these numbers should be spot-checked by KT before being treated as ground truth (Challenge 1).
- The bibles' causal locks are promissory notes, not proof of a good story. Transmitting them intact is necessary, not sufficient — some bible locks are themselves thesis-shaped ("the failure proves the theme"). Fixing transmission removes a confound so the *real* generation-quality question becomes visible.
- The deletion test as applied here is judgment-based; two analysts could disagree at the margins (soft vs hard dependencies). The cross-run consistency of the pattern (front-loaded deletability, back-loaded chains) is robust to that noise; individual episode verdicts are not.

## Per-run audit sources

Full per-run audits (commitment inventories, survival traces, episode-by-episode causal tables) were produced in-session for runs 000, 001, 003, 004, 005 by analyst agents and for run-002 directly; this document is the synthesis. Re-running the audit on other lineages (stray_v5, pippa_v3) would test whether the two-stage loss profile generalizes beyond the June 2 architecture.
