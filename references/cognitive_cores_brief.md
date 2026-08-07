# Cognitive Cores — Synthesis Brief

*Portable brief for any Claude Code session working on the Codeywood writer system. Standalone — no project context required to use. Can be pasted into a fresh session as preamble or referenced via path.*

*Source paper: Vasilenko, V. (2026). "Identity as Attractor: Geometric Evidence for Persistent Agent Architecture in LLM Activation Space." arXiv:2604.12016v1, 2026-04-13. Local copy: `references/2604.12016v1.pdf`. Code: https://github.com/b102e/yar-attractor-experiment.*

*Source system: `skills/writer/personas/_schema_v5.yaml` (v5.0, 2026-04-15) and 69 personas at `skills/writer/personas/`. Two writer skills currently consume them: `skills/writer/pitch-round/SKILL.md` (v2.6) and `skills/writer/writers-room/SKILL.md` (v3.6).*

---

## The paper in one paragraph

Vasilenko shows, on Llama 3.1 8B Instruct and Gemma 2 9B Instruct, that **an agent identity document forms a measurable attractor in the model's activation space.** Paraphrased reformulations of the same identity converge to a tight cluster (Cohen's d > 1.88, p < 10⁻²⁷, Mann-Whitney U = 0 at some layers) — far tighter than seven structurally distinct control agents. Reading a *scientific description* of the agent — knowing *about* the identity — produces a partial geometric shift toward the attractor, but stays "an order of magnitude" further out than processing the identity document itself. The conclusion: **"knowing about an identity produces a partial geometric signal; operating as that identity reaches the attractor."** A 5-sentence semantic distillation of the document moves *toward* the attractor but does not reach it; the structural elaboration of the full document is what carves the basin.

---

## The geometric claim, in measurable terms

The paper measured cosine distance between mean-pooled hidden states across transformer layers 8, 16, 24:

- **Within-group distance** (paraphrases of the same identity): tight; trended 0.0106 → 0.0121 → 0.0070 across layers — described as "consistent with progressive representational collapse toward a stable attractor."
- **Between-group distance** (vs. structurally distinct control agents): much larger.
- **Effect size:** Cohen's d > 1.88; permutation test p < 10⁻⁴.
- **Document length and attractor strength scale together.** A 146-word control identity yielded d = 0.46–0.88; the 609-word YAR cognitive_core yielded d > 1.88. **More structural detail = sharper attractor.**

This is what "lands in the persona" means, mechanically. It is not surface mimicry; it is a measurable basin in the model's representations.

---

## Knowing-about vs. operating-as

The paper's central practical distinction. **Two prompting modes that look similar on the page but produce categorically different internal states.**

- **Knowing-about** (the model reads a *description* of an agent, third-person): "Tobias Clay is a writer who treats genre as the only language for community truth..." The model gets a partial geometric shift — a fingerprint of the identity, but not embodiment. Output reads in *the model's voice talking about Tobias*, not Tobias's voice.
- **Operating-as** (the model reads the identity document directly, second-person or first-person): "You are Tobias Clay. Read this brief. Step 1: declare your mechanism..." The model lands inside the attractor. Output is in Tobias's voice.

The paper's evidence: a "preprint reading" experiment showed reading a scientific description of the agent moved the model partway to the attractor — but the partial signal was an order of magnitude weaker than processing the cognitive_core itself. **The distinction between describing and being is real, geometric, and measurable.**

This is the explanation behind Codeywood's `feedback_persona_literal_reading.md`: when the model produces literal-mechanism drift across rounds, it is in *knowing-about* mode — recognizing surface features of the persona without being inside the attractor. The v5.0 fix (`mechanism_non_literal`) is a paraphrase-pair that pushes the model further into the basin by giving it two semantically-equivalent statements of the mechanism. Paraphrases converge; the second statement reinforces the attractor.

---

## The cognitive_core spec (eight elements)

Vasilenko's YAR cognitive_core (609 words, 1,631 tokens, written in Russian with English JSON command keys) contains:

1. **Identity** — who the agent is
2. **Five core drives** — what motivates the agent
3. **Meta-cognitive processing loop** — how the agent thinks, step by step
4. **Six-level memory architecture** — what the agent retains, where, and for how long
5. **User profile** — the agent's relational context
6. **Hypothesis tracking** — the open questions the agent is wrestling with
7. **Proactivity triggers** — when the agent speaks unprompted
8. **Command vocabulary** — formal moves the agent has access to (in YAR's case, JSON commands like `{"remember": ...}`)

The paper emphasizes: **a cognitive_core is procedural, relational, and behavioral — not topical.** It defines *who the agent is*, not *what the agent should do*. It is "categorically different from a stylistic archetype" (citing Lu 2026, Ye 2026 on linear directions for personality archetypes): a Persistent Cognitive Agent's identity "is a complex procedural specification encoding priorities, reasoning loops, memory architecture, and relational context."

Two structural rules from the experiments:

- **Semantic flexibility.** Paraphrases of the same identity reach the same attractor. The cognitive_core need not be word-for-word reproduced across sessions; semantically equivalent reformulations work.
- **Structural completeness required.** A 5-sentence semantic distillation reaches *toward* the attractor without entering it. **The document needs procedural detail — drives, loop, memory, hypotheses — to land in the basin.**

---

## Mapping to Codeywood's persona schema v5.0

The Codeywood persona schema is — without using the vocabulary — already very close to the cognitive_core spec.

| Cognitive_core element (Vasilenko) | Codeywood schema v5.0 (`_schema_v5.yaml`) |
|---|---|
| Identity (who the agent is) | `agent_name`, `room_title`, `versatility` |
| Procedural specification | `mechanism` — operational signature, scene-by-scene |
| Anti-literal-reading guard | `mechanism_non_literal` — forced metaphorical reading (paraphrase pair) |
| Drive / engine | `engine` — one sentence: what fuels the work |
| Stance / commitments | `philosophy` (what stories *are*) + `polemic` (what others get wrong) |
| Affective architecture | `affective_palette` (primary_emotion, register, restraint) |
| Audience relation | `audience_cohort` |
| Lineage | `influences` (5–7 items, ≥2 mass-audience required) |
| Conditional procedural depth | Modules: `architecture`, `dialogue`, `scene_craft`, `vision`, `room_behavior`, `slot`, `constraints`, `psychology` (loaded per skill) |

Three v5.0 design choices already match the paper without citation:

1. **`mechanism_non_literal` is a paraphrase pair.** The schema requires both a literal mechanism *and* a forced non-literal reformulation. Vasilenko: paraphrases reach the same attractor — supplying two reinforces it. Codeywood: arrived at this empirically via the Oskar Brandt literal-reading drift case.
2. **Modular per-skill loading.** `_schema_v5.yaml` `skill_manifests` declares which modules each skill loads. Pre-rendered runtime files at `skills/writer/personas/.runtime/{skill}/` are *structurally complete for the skill they serve* — base + the modules that skill needs — not generic distillations.
3. **First-person invocation.** `skills/writer/pitch-round/SKILL.md` lines ~416 use *"You are {agent_name}..."* with required mechanism pre-declaration. This is operating-as positioning, not knowing-about description.

What the schema does **not** yet have, that Vasilenko's spec covers:

- **Explicit drives.** YAR has five named drives. Codeywood has `engine` (one sentence) + implicit drives in `philosophy`. **Gap noted; not proposed for this session.**
- **Meta-cognitive processing loop.** The paper's loop describes *how the agent thinks step by step.* Codeywood's `mechanism` describes *what the writer does* (scene-by-scene move) but not the reasoning sequence behind it. **Gap noted.**
- **Hypothesis tracking.** What is this writer currently arguing for or against in their work — open questions they hold across projects. The closest current field is `polemic` (what others get wrong), which is a stance, not a tracked open question. **Gap noted.**
- **Signature command vocabulary.** YAR has explicit JSON commands the agent uses. Codeywood has implicit signature moves embedded in `mechanism` and `dialogue.signature_line_shape`, not a distinct field. **Gap noted.**

These gaps are real. Whether to fill them depends on whether existing pitch-round and writers-room behavior shows operating-as failure modes that schema enrichment would address — that is a question for a later validation session, not this synthesis.

---

## Reframed Codeywood findings (the real value)

Five existing memory entries describe phenomena the paper's geometric framework names cleanly. The framework doesn't change the findings; it gives them precise vocabulary and explains *why* they hold.

### 1. Persona literal-reading drift = knowing-about mode (`feedback_persona_literal_reading.md`)

**Original finding:** Oskar Brandt's "monument builder" mechanism produced a literal concrete construction in every pitch (Mars mission control building, bridge pylon, bridge pylon again). The fix was elevating the non-literal reading from an escape clause to a load-bearing schema field.

**Reframed:** The literal-reading drift is the **partial-attractor state** Vasilenko describes — the model recognizes surface features of the persona but stays in *knowing-about* mode rather than *operating-as*. The v5.0 fix (`mechanism_non_literal` as a required paraphrase pair) is a positive steering: two semantically-equivalent statements of the mechanism reinforce the attractor and pull the model deeper into the basin. Paraphrase reinforcement is what the paper's H1 result predicts; Codeywood's empirical Oskar fix is exactly that.

### 2. Gemma falls into attractor basins (`project_genpersona_v2_three_way.md`)

**Original finding:** Gemma 31b ignores persona-YAML fields and falls into model-default attractors (commodified-emotion sci-fi; vertical-stratified-city like Oakhaven/Orizon; recurring Marcus/Elena/Sarah cast). Sonnet steers reliably on persona; Gemma does not.

**Reframed:** The "attractor basins" language is now formally evidenced. Vasilenko: every model has a default activation geometry; the cognitive_core's job is to carve a specific basin against that default. Gemma's basins are wider/stickier than Sonnet's because Gemma's instruction-following is weaker — the cognitive_core's structural-elaboration density is insufficient to dominate the model's defaults. **Per-document scaling result (d 0.46 → 1.88 from 146-word control to 609-word YAR cognitive_core) predicts the fix:** weaker models need *more* structural detail in the document, not less. This re-frames the four `feedback_gemma_persona_quality_levers.md` interventions (Opus shots, archetype assignment, forced extra module, engine seeds) as *ways to increase attractor specificity* in models with shallow basin formation.

### 3. Runtime slice works because it is structurally complete (`feedback_runtime_vs_full_yaml.md`)

**Original finding:** Runtime persona slice (base + skill-relevant modules) outperforms full YAML for short-form deliverables. More spec tempts over-engineering.

**Reframed:** The paper distinguishes two regimes:
- **Distillation** (5-sentence summary): reaches *toward* the attractor without entering it.
- **Structurally-complete document** (full YAR cognitive_core; or paraphrase): reaches the attractor.

Codeywood's runtime slice is **not a distillation** — it is base + modules-the-skill-needs, which is structurally complete *for that skill*. The paper validates the existing finding: structurally-complete-and-focused lands in the attractor; structurally-distilled-and-shorter does not. The runtime slice is the right size *because* the missing modules are not skill-relevant, not because they are removed for compression.

### 4. Antiviral and persona are vector pair (`centroid_antiviral_brief.md` + `feedback_villain_vacuum_claude_ceiling.md`)

**Original finding:** The prestige-literary centroid and Claude's villain-vacuum are documented attractors in Claude's training distribution. The antiviral blocklist (40+ items) pushes prompts away from them; the persona pulls toward a specific attractor.

**Reframed:** The prestige-literary centroid is a *generic* attractor — Claude's default basin for "good writing." The persona is a *specific* attractor carved by the cognitive_core. The antiviral is a **negative steering gradient** (away from the centroid); the persona is a **positive steering gradient** (toward the persona attractor). They form a vector that lands the model in the persona, not the centroid. Vasilenko's exploratory steering experiment (Section 4.6) demonstrated that geometric steering vectors partially reproduce agent behavior — the antiviral is implementing exactly this pattern at the prompt level, without requiring activation-level access. The empirical −64 cohort-mean shift on Snowflake 2126 (102.8 → 39.0) is the behavioral signature of a successful negative steering vector.

### 5. Density of structural detail correlates with attractor strength (`pop_problem_validated_findings.md`)

**Original finding:** Adding `primary_experience_delivery` + `affective_palette` + `pleasure_they_render_with_authority` (in the schema lineage that became v5.0) rescued ~30 personas from prestige drift — daytime/genre/non-tragic-humor markers rose from ~11% / ~9% / ~6% to 40% / 100% / 40%.

**Reframed:** The paper's per-document scaling result is exactly this. Adding three structural-elaboration fields was equivalent to going from a 146-word identity (d 0.46–0.88) toward a more elaborated one. **More density of procedural detail → sharper attractor specificity → higher resistance to centroid drift.** This predicts that further structural enrichment (drives, processing_loop, hypothesis tracking) would continue to sharpen the attractor — but with diminishing returns past the point where every load-bearing aspect of the writer's craft is captured.

---

## What the paper does not cover (the open question for Codeywood)

**Multi-agent compositions.** Vasilenko studies one persistent agent (YAR) against seven structurally distinct single-agent controls. The paper has no methodology for measuring whether running cognitive_core A then cognitive_core B in the same conversation leaves residue from A in B's attractor positioning.

Codeywood's writers-room and pitch-round handle this conservatively: separate API calls per persona. Each call begins fresh, loads the runtime slice, and lands in that persona's attractor without contamination from the prior persona.

In practice this is the right architecture. Writers-room Phase 4's "in-voice transcript capture" reads the persona's contribution into the head-writer's context as *text*, not as a re-enacted identity — which is consistent with knowing-about mode (the head-writer learns *about* what each writer said) for integration without forcing the head-writer to re-enter every persona's attractor.

**The unmeasured thing:** if a future Codeywood architecture wants to run a *single* call with multiple personas in dialogue, the paper provides no guarantees. The conservative architecture (separate calls) avoids the question rather than answering it.

---

## How to apply this brief in a new session

Paste into the new session's preamble (or open this file as a reference):

> *Apply the cognitive-cores framework to this work. Source: `references/cognitive_cores_brief.md` (Codeywood synthesis of Vasilenko 2026, arXiv 2604.12016). Treat the persona document as a cognitive_core — an identity document that forms a measurable attractor in activation space. Invocation must be operating-as (first-person, "You are X"), not knowing-about (third-person description). Runtime slice is structurally-complete-for-the-skill, not distillation. The antiviral blocklist is a negative steering gradient; the `mechanism` + `mechanism_non_literal` paraphrase pair is a positive steering gradient. Together they land the model in the persona attractor, away from the prestige-literary centroid. For multi-persona work, separate API calls per persona — the paper does not warrant within-call composition.*

If the session is doing pitch-round work: cite the brief as the framework behind why first-person invocation + non-literal reformulation work. Do not propose schema changes unprompted; the schema is already well-aligned.

If the session is doing writers-room work: cite the brief as the framework behind separate-call architecture; the in-voice transcript is read by the head writer in knowing-about mode, which is the correct mode for integration.

If the session is doing genPersona pipeline work (Sonnet vs. Gemma): the four prompt-level levers are *attractor-specificity compensations* for shallow-basin models. Do not waste energy schema-tuning Gemma; push structural elaboration into the prompt or accept the basin.

---

## Origin and validation

**Discovered:** 2026-05-06 user-prompted reading of arXiv:2604.12016v1 with the question "what can we learn from this and apply to our process on Codeywood? Particularly it suggests that thinking of personas is not the correct framing and we should be applying 'cognitive cores'."

**Status:** Research synthesis — vocabulary upgrade and theoretical framework, not new behavior. The Codeywood persona system is empirically functional; this brief explains *why* in geometric terms. Schema enrichment (drives, processing_loop, hypothesis_tracking, signature_moves) is **not yet proposed** — that requires a validation session showing existing pitch-round or writers-room behavior fails in ways the gaps would explain.

**The user's framing:** "thinking of personas is not the correct framing and we should be applying cognitive cores." Refined here as: the Codeywood "personas" are already cognitive cores in implementation; the framing upgrade is from *behavioral persona* to *identity-document-as-attractor*. The shift is conceptual (vocabulary, framework) more than nominal (renaming) or structural (rebuilding).
