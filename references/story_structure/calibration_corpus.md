# Calibration Corpus (pointer — lives in gemmawood)

A shared corpus of complete story-pipeline outputs for calibrating any
future story-quality evaluator against human judgment. It is maintained
in the gemmawood sister project, not duplicated here:

**Location:** `/Users/kaigani/Documents/PC_SHARED/260611 gemmawood/calibration/corpus/`
**Catalog:** `MANIFEST.md` in that directory.

**Contents:** 17 entries / 46 artifacts from the divergence-test
pipeline's final runs — rio_v2 (runs 000–005; run-002 carries the
pre-bible vs. with-bible A/B pair, the primary controlled comparison
for transmission loss), stray_v5 (000–005, outlines only), pippa_v3
(baselines + 000–003). Each entry includes the final outline plus,
where the lineage produced them, the story bible, lead draft, and beat
sheet.

**Why it matters to Codeywood:** the rio_v2 audit numbers that motivate
writers-room v3.7's Causal Contract and the v2 recipe wiring (~19% of
bible causal commitments surviving to final outline; 43% of episodes
failing the deletion test; climaxes consuming 0–3 earned choices) are
derived from this corpus and documented in its MANIFEST. Any judge or
rubric proposed for Codeywood's narrative gates must be calibrated
against human ratings of this corpus before being used as an
optimization target — uncalibrated scalar gates passed 93% of outputs
that humans judged structurally broken.

Codeywood deliberately does NOT adopt the gemmawood judge rubric yet
(decision 2026-06-11): evaluation instruments stay as-is until
calibration results exist. Re-checked 2026-08-06: gemmawood is frozen
since Jun 11, the rubric is still uncalibrated — the decision stands.
Codeywood's own instrument has since matured
(`combined_evaluation_rubric.md` v0.3 + `judge_workflow.md`).

**Known gap (2026-08-06):** the corpus is entirely PRE-fix material.
The only post-fix lineage — `260503 divergence test/runs/rio_v4/`
(6 complete runs incl. a no-persona baseline, + 728KB thinking log) —
was never added or audited. A spot audit found causality improved but
all 6 runs collapsed to one causal skeleton (over-specified recipe
beat prose; see `learnings/INDEX.md`). Any judge calibrated on this
corpus has never seen an output from the architecture that actually
shipped; add rio_v4 as the post-fix arm before running calibration.
