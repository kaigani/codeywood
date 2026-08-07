# Multi-Judge Evaluation Workflow (distilled)

**Ported**: 2026-08-06 from `~/Documents/PROJECTS/DEVELOPMENT/260614 scoring rubric/workflow.md`
(gen-3 "floor-disciplined", validated 2026-06-15). Full agent prompts and output
contracts live in the source file; this is the Codeywood-facing distillation.

**Relationship to dialectical-eval**: `skills/writer/dialectical-eval/SKILL.md`
is the lightweight 2-advocates + 1-holistic-judge form (~3 calls per item per
dimension). This workflow is the heavyweight form — use it when a verdict is
load-bearing (greenlight decisions, calibration runs, cross-project rankings),
not for routine round scoring.

## Why it exists

Origin experiment ("01 roope"): the same screenplay scored **120/120** from a
positively-framed critic and **12/120** from a negatively-framed one, each argued
fluently. An LLM critic will confidently produce any score you frame it toward.
Every mechanism below removes one path by which framing, rhetoric, or generosity
moves a score away from the evidence.

## The roles (all fresh contexts)

| Agent | Job | Hard constraint |
|-------|-----|-----------------|
| Advocate Evidence Reviewer | Strongest evidence of success | **May not propose scores** |
| Adversarial Evidence Reviewer | Strongest evidence of weakness | **May not propose scores** |
| Neutral Evaluator | Independent baseline scores | Scores BEFORE seeing either brief |
| Final Judges ×3 | Source-first scoring, then evidence synthesis | **Lock provisional scores before reading the briefs**; every change from provisional must cite the source evidence satisfying the new anchor |
| Cohort Ranker | Relative ranking across entries | Must not sort mechanically by totals; must flag entries scored under a different workflow version |

## The mechanisms and what each one killed

1. **Advocates produce evidence, not scores.** Gen-1 "winner inherits the
   winning brief's score" inflated results (97→81, 91→88 after removal).
   Persuasiveness is not quality: *winning the A/B argument has no automatic
   scoring consequence.*
2. **Blind A/B evidence packaging.** Advocate/adversarial briefs are randomized
   per category as Evidence A / Evidence B (key kept private), so judges can't
   pattern-match "the positive one."
3. **Score first, lock, then read evidence.** Makes every rhetoric-driven score
   movement visible and auditable as a delta.
4. **Neutral baseline + uplift audit.** One scorer produces a blind baseline;
   every judge score above it is audited. Uplift justified only by a
   criterion-specific demonstrated effect — the banned-phrase list in
   `combined_evaluation_rubric.md` §Floor Discipline is the teeth.
5. **Median per category across 3 judges** (not mean of totals) — discards
   single-judge outliers without adjudication.
6. **Floor/ceiling controls run before trusting any batch** — see
   §Control artifacts in the combined rubric.

## Five-mechanism diagnosis of judge inflation (from the floor-control audit)

When judges drift a known-slop control upward, the causes were: (1) A/B
comparison rewarding argument quality; (2) treating "functional" as 2 when the
floor assigns it 1; (3) inferring latent sophistication not dramatized; (4)
Potential rewarding generic rewrite affordances (deadlines, motifs, bookends);
(5) no burden-of-proof rule and no audit against the baseline. Every Codeywood
scoring change should be checked against this list — it is the failure taxonomy.

## Gate 5 mapping note

The legacy quality gate "Critique score >= 70" predates this machinery. On the
120-point scale, 60–71 is "professionally readable but dramatically ordinary"
and 40–59 is the AI-slop band — a 70/120 gate passes exactly the material the
floor discipline exists to fail. When Gate 5 is next exercised, define it
against the combined rubric's re-anchored scale (e.g. Band A mean with floor
discipline + caps applied, plus Band B hard gates), not a raw percentage.
