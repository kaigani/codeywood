# Learnings — primary sources

Primary-source audits ported from the divergence/gemmawood sister projects
(2026-08-06). These are the evidence behind numbers cited in
`skills/writer/writers-room/SKILL.md` (v3.7 Causal Contract) and
`references/story_structure/story-recipe-methodology.md`.

| Doc | What it establishes |
|-----|---------------------|
| [BIBLE_OUTLINE_AUDIT_rio_v2.md](BIBLE_OUTLINE_AUDIT_rio_v2.md) | Transmission-loss ground truth: 106 bible commitments → 20 (19%) dramatized; 26/60 (43%) episodes deletable; median causal chain 4; climaxes consuming 0–3 earned choices. Two-stage loss: relational evolutions die at bible→arc, causal wiring dies at beats→final. |
| [PROJECT_STATE_REPORT.md](PROJECT_STATE_REPORT.md) | Divergence project post-mortem: solved divergence, not story. Evaluator gap (93% gate PASS on structurally broken outputs), richer-generation-reduces-diversity negative result, centroid laundering, physicalization overcorrection, 10-item challenge inventory. |

Additional un-ported evidence (read in place):

- `PC_SHARED/260503 divergence test/runs/rio_v4/` — the ONLY post-fix validation
  lineage (v2 recipe + transmission fix together). Never formally audited. Spot
  audit (2026-08-06 survey): causality improved, but **all 6 runs — including the
  no-persona baseline — collapsed to one causal skeleton** because the v2 recipe
  spine over-specified scene content. Also: 2/6 runs fell to the gate-FAIL
  single-pass fallback and silently bypassed the transmission fix.
- `runs/rio_v4/thinking-log.md` (728KB) — Gemma reasoning traces showing where
  convergence happens during seed generation.
