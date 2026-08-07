# Current State of the Divergence Story-Generation Project

**Date:** June 10, 2026  
**Audience:** Research collaborators  
**Target capability:** Given a premise, produce a near-final treatment for a serialized screen story that requires refinement rather than repair of its core story engine, causal spine, climax, or resolution.

## Executive Summary

The Divergence project is an evolving research prototype for helping a comparatively limited local model, currently `huihui_ai/gemma-4-abliterated:31b`, generate compelling serialized screen-story concepts. Its central strategy is to compensate for weaknesses in unaided language-model storytelling through a structured creative process: writer personas or "cognitive cores," genre recipes, controlled divergence, anti-default constraints, staged story development, character-specific improvisation, and automated evaluation.

The project has made real progress. It can now produce concepts with more varied premises, cultural substrates, occupations, names, tones, and authorial positions than an unconditioned model normally produces. It has identified and partially controlled several recurring model defaults, including prestige-literary observer protagonists, bureaucratic or archival conflict, repeated cultural references, repeated lore shapes, generic names, passive antagonists, and early convergence on familiar genre material. The pipeline also contains practical engineering solutions for local-model limitations, including separate creative and formatting passes, retry and failure capture, deterministic sampling, resumable artifacts, and explicit context management.

These achievements should not be confused with success at the project's final objective. The system does not yet reliably produce near-final treatments. Its strongest outputs contain distinctive ingredients and intelligible external goals, but they still commonly require substantial human revision to become compelling stories. The persistent weakness is global dramatic reasoning: the model often does not build one coherent chain of causally connected choices and consequences toward an earned climax and satisfying resolution. Instead, it tends to produce ten labeled demonstrations of a premise, theme, recipe, or character trait.

Rio v2 is the closest completed lineage to the desired result. Its strongest heist treatment has a clear goal, an embodied antagonist, a legible team, a physical target, and a final reversal. Even there, the story remains schematic. The season repeatedly proves the same thematic proposition, while the climax resolves through a convenient permissions rewrite rather than through a sufficiently difficult culmination of the crew's decisions, losses, conflicts, and adaptations.

The project's evaluators do not yet measure this gap reliably. Across the available artifacts, 169 of 181 Step 5 gate decisions were `PASS`. Several passing drafts explicitly lack a deadline, named antagonist, goal verb, or thematic articulation, and some still exhibit the deeper story failures identified by human review. Existing scores are useful for detecting structural completeness, repetition, lexical centroids, and some pitch-level problems. They are not evidence that an output is produceable.

The present research position is therefore:

- **The system can generate and protect interesting story material.**
- **The system can improve local properties of a concept through explicit constraints.**
- **The system has not demonstrated reliable global story construction.**
- **The system has not demonstrated a reliable evaluator for global story quality.**
- **The latest June 2 architecture is a plausible response to premature convergence, but it has limited completed-run validation and should be treated as an active hypothesis.**

The next research plan should begin from this distinction. More diversity, more persona fidelity, and more anti-default rules may improve the material without solving the story. The central unresolved problem is how to make a model reason about dramatic causality, escalation, climax, and resolution, and how to measure those capabilities well enough for a self-improving system to optimize them.

## Evidence Standard Used in This Report

The project contains extensive observations, interventions, and artifacts, but relatively few controlled experiments. This report uses four evidence labels:

- **Validated finding:** Supported by a defined comparison, quantitative result, or repeated test with an explicit success criterion.
- **Repeated observation:** Visible across multiple runs or project lineages, but not isolated through a controlled experiment.
- **Strong hypothesis:** Supported by external research and project behavior, but not yet causally demonstrated inside this system.
- **Open question:** Plausible and important, but currently under-measured or untested.

These labels matter because the prototype has changed quickly. An intervention may be implemented in the current code without having been validated on enough completed projects to establish that it improves final treatments.

## The Intended Product

The desired output is not merely a novel pitch, a useful bundle of story ingredients, or a formally complete ten-episode outline. It is a near-final serialized-screen-story treatment.

For this project, a near-final treatment should have:

- A clear and distinctive dramatic proposition.
- A protagonist or ensemble whose decisions generate the story.
- Character relationships that create pressure, reversals, and consequences.
- An external story engine capable of sustaining the intended episode count.
- Episodes that change the dramatic situation rather than restate the premise.
- Escalation that materially reduces options and increases cost.
- A climax caused by prior choices, conflicts, and accumulated consequences.
- A resolution that pays off the story's central dramatic and emotional promises.
- A production-legible treatment whose core does not need to be replaced by a human editor.

This definition is deliberately stricter than the current automated gates. A treatment can contain all required sections, a named antagonist, physical stakes, and ten episode summaries while still failing as a story.

The eventual quality system should begin with calibrated human review and produce a stable fixed rubric that local evaluator models can apply reliably. The intended destination is a human-calibrated judge ensemble, not unrestricted self-critique by the same writer model. The generator may eventually improve its own prompts, routing, persona use, recipes, gates, and process structure, but that loop is only useful if its evaluator predicts the human judgment that the treatment no longer needs structural repair.

## Current System

### Current Architecture

The current code reflects a June 2 restructuring. The repository README still describes portions of an older logline-centered pipeline, so the implementation in `divergence/pipeline.py`, `divergence/prompts.py`, and `divergence/outline.py` is the more reliable description of present behavior.

The current process is:

1. **Persona-conditioned story ingredients**
   - The system samples writer personas from the persona pool.
   - Each persona generates seed titles, diversified seeds, and open story questions.
   - The current design intentionally generates no story prose at this stage.
   - One full ingredient bundle is assigned to each run as the project's early cognitive core.

2. **Tropes and anti-tropes**
   - The model generates trope options from the premise and ingredient bundle.
   - Each run samples a small subset to avoid overdetermining the story.

3. **Recipe, comps, and distribution vehicle**
   - A story recipe supplies a genre-specific floor: emotional contract, cast functions, trope vocabulary, and beat expectations.
   - The system generates multiple comparable works and distribution vehicles, then samples in code rather than trusting the model's default choice.

4. **Lore generation and antiviral pass**
   - The lore receives a sampled history shape, a constrained cultural option set, and prior-run exclusions.
   - A separate antiviral pass attempts to remove prestige-centroid vocabulary, roles, aesthetics, and repeated phrases.

5. **Cultural mapping, naming, and characters**
   - Cultural anchors are selected from constrained options with no-repeat filtering.
   - Character names are derived from the selected naming system and may be translated into more accessible English approximations.

6. **Head-writer exploration and story bible**
   - The head writer asks open story questions after lore and characters exist.
   - A separate story-bible pass commits answers, maps relationships, identifies the story landscape, and states what the story needs.
   - This stage is intended to delay convergence until enough material exists to make a more informed story choice.

7. **Lead draft, gate, character work, beat sheet, and editor**
   - A lead writer creates the season-arc draft and key cast.
   - A deterministic gate decides whether the draft enters the multi-step development flow.
   - Key characters receive story-internal cognitive cores and improvise from their own positions.
   - A beat sheet extracts structural beats from the lead draft.
   - A neutral editor synthesizes the draft, beats, and character improv into the final ten-episode outline.

The pipeline's engineering design is substantially more sophisticated than its initial five-prompt form. It preserves intermediate artifacts, supports deterministic variation, separates creative writing from structured formatting, catches failed model responses, and allows comparisons with an unconditioned baseline.

### Persona and Cognitive-Core Strategy

The persona system is better understood as an attempt to establish a cognitive attractor than as simple style imitation. The supplied cognitive-cores brief argues that an identity document works best when it is procedural, relational, and structurally complete, and when the model operates as the identity rather than merely reading about it. The project reflects this framework through first-person persona invocation, mechanisms, non-literal reformulations, engines, polemics, affective palettes, cut principles, and separate calls for separate identities.

This architecture has an important strength: it gives the model concrete ways to approach material differently. It also has an important limit: changing the writer's position does not necessarily improve the writer's ability to construct a complete story. A persona can reliably cause a model to choose different images, occupations, tensions, or scene principles while the underlying dramatic reasoning remains weak.

### Current Validation State

The current implementation is ahead of its validation record.

The June 2 shift from prose sketches to raw ingredient bundles was based on a diagnosis that early prose caused Gemma to converge too soon on a setup and thesis-shaped resolution. This is a coherent intervention. Rio v2 demonstrates that the new path can produce clearer external engines. However, the current architecture has only a small completed evidence base, and the repository contains signs of transition:

- The README describes older logline and sketch behavior that no longer fully matches the code.
- Rio v2 retains stale `RUN_FAILED.md` artifacts from a prior interface mismatch even though its pipeline summary later records five completed runs.
- Six `RUN_FAILED.md` files and eight `llm_failures` artifacts remain in the workspace.
- Existing scoring and analysis artifacts are concentrated in older project generations rather than the latest architecture.

This does not make the current architecture unsound. It means claims about its final-story benefits should remain hypotheses until compared against prior architectures with human-calibrated treatment judgments.

## What Has Worked

### 1. The Project Has Identified Concrete Model Defaults

**Evidence tier: Validated finding and repeated observation**

The earliest large run sets reveal strong convergence despite nominal random variation.

In the original Gunslinger project:

- "Silence" appeared in titles 18 times across 20 scored runs.
- "Weight" appeared 12 times and "gilded" 11 times.
- The protagonist token "Silas" appeared in 10 of 20 runs.
- Byzantine Empire appeared as a cultural anchor 11 times, Mongol Empire 9 times, Tibetan monasticism 6 times, and Heian-period Japan 5 times.

In the original Anthology project:

- "Great" appeared in titles 17 times across 34 scored runs.
- "Final" appeared 15 times, "gilded" 14 times, and "silence" 13 times.
- Heian-period Japan appeared as a cultural anchor 17 times and Byzantine Empire 12 times.

These are measurable examples of a larger phenomenon: random sampling from model-generated options does not necessarily produce meaningful divergence, because the option pool itself is generated inside a narrow attractor.

The project responded with constrained culture sets, no-repeat filters, sampled history shapes, title and noun exclusions, persona-conditioned generation, and programmatic rather than model-selected choices. These changes directly address observed defaults rather than relying on higher temperature alone.

### 2. Antiviral Thinking Has Improved the Diagnostic Vocabulary

**Evidence tier: Repeated observation**

The centroid-antiviral brief identifies a recurring prestige-literary attractor: observer protagonists and conflicts organized around archives, records, maps, signals, translation, and institutional procedure. The important extension is "centroid laundering": removing the archivist protagonist does not solve the problem if the supporting cast and central conflict remain organized around the same register.

This framework has improved the project in two ways.

First, it provides actionable tests: job census, action test, body test, and conflict-register test. Second, it explains why local lexical fixes often fail. A banned word can disappear while the underlying dramatic behavior remains passive or administrative.

The lore antiviral and occupation constraints have visibly moved outputs toward bodies, tools, work, and present-tense action. Rio v2's heist is built around technicians, pipes, vents, physical hardware, and manual entry rather than a purely abstract data conflict. That is a meaningful improvement in screen legibility.

The limit is equally visible. Rio's story still uses permissions, access, and systemic recognition as its final mechanism. The surface register has become more physical, but the resolution remains conceptually neat and dramatically easy. The antiviral can redirect the material without teaching the model how to earn a climax.

### 3. Personas Produce Useful Variation

**Evidence tier: Repeated observation**

Across Pippa, Stray, and Rio, persona-conditioned runs produce materially different story surfaces and authorial arguments. Pippa v3's body-horror road story, Stray v5's caution-driven slasher, and Rio v2's maintenance-worker heist are not minor paraphrases of one another. The persona system helps the model discover unusual combinations, preserve an argument, and resist some generic defaults.

The cognitive-core framing also supports several good architectural decisions:

- Separate calls for separate personas reduce identity contamination.
- First-person operating-as prompts are more appropriate than third-person descriptions.
- Mechanism plus non-literal mechanism helps prevent literal gimmick repetition.
- Character-specific cognitive cores give supporting characters a stronger position from which to challenge the outline.

These are useful creative-control mechanisms. They are not yet evidence that personas improve complete-story quality. The strongest conclusion supported by the artifacts is that personas improve the variety and specificity of the material from which a story might be built.

### 4. Genre Recipes Improve Legibility

**Evidence tier: Repeated observation**

The story-recipe methodology gives the model functional roles, relational positions, emotional targets, trope vocabulary, and conformity rules. This is well matched to a model that performs better under explicit constraints than under an open request to "write a compelling story."

Stray v5's slasher output demonstrates the advantage. It has a final girl, killer, doomed friends, knower, and skeptic; the episodes follow an intelligible slasher progression; and the protagonist's caution becomes the climactic tool. Compared with many early outputs, the concept is easier to pitch and easier to parse.

The same example shows the risk. The recipe can become a visible template. Characters are killed in the order their labeled flaws predict, and the final outline reads like a correct execution of a slasher schema rather than a surprising accumulation of human choices. Recipe conformity improves the floor but does not create the ceiling.

### 5. The Project Has Learned to Separate Divergence From Synthesis

**Evidence tier: Strong hypothesis with partial implementation evidence**

The current system increasingly treats idea generation and story commitment as different cognitive jobs. It generates many seeds, samples external constraints, develops lore and characters, asks story questions, and only later writes a story bible and season arc.

This is a sound response to a repeated failure: early prose tends to commit the model to the first coherent-sounding direction, after which downstream steps elaborate rather than reconsider it. The June 2 ingredient-bundle architecture directly encodes this diagnosis.

The shift is promising, but not validated. The Pippa v2 diversity experiment is a cautionary result: prose sketches were expected to broaden the pool but were actually more similar than loglines. In the size-matched comparison, mean pairwise cosine similarity increased from `0.5340` for loglines to `0.6217` for sketches, and mean distance to centroid decreased from `0.2653` to `0.2085`. The explicit diversity success criterion failed.

The lesson is not that longer artifacts are always less diverse. It is that adding a richer generation stage can create the appearance of exploration while causing the model to converge more strongly on shared narrative patterns.

### 6. The Engineering Foundation Is Practical

**Evidence tier: Validated implementation capability**

For a local-model research system, the project has developed useful infrastructure:

- Separate writer and formatter models reduce creative degradation from JSON pressure.
- Raw and parsed outputs are both persisted.
- Failed responses are captured for postmortem analysis.
- Runs are resumable and deterministic where practical.
- Model choices and random selections are recorded.
- Baseline generation is supported.
- Intermediate artifacts make qualitative diagnosis possible.

This foundation is valuable because the next stage requires controlled comparisons. The main gap is not an inability to run experiments; it is the absence of a sufficiently trustworthy final-quality measure and a disciplined experiment record tied to that measure.

## Persistent Challenges

### 1. Local Constraint Compliance Does Not Produce Global Story Coherence

**Evidence tier: Repeated observation**

The system is increasingly effective at making each stage obey its instructions. A lore can use a selected history shape. A cast can match a recipe. A protagonist can have an external goal. A beat sheet can contain acts and reversals. An outline can contain ten episodes and key moments.

The final story can still be weak because the stages do not necessarily form one causal argument.

Rio v2's heist is the clearest current example. The story bible establishes a strong thematic and visual proposition: a pristine city is physically dependent on invisible maintenance labor. The outline then repeatedly demonstrates that proposition:

- A stolen component proves the city is mechanical.
- A hidden repair prevents a blackout.
- A leaking pipe appears behind gold.
- A bootleg fix fails.
- The crew carries a wrench into the Hub.
- The crew steals the physical core.

These beats are coherent at the level of motif. They are less coherent as escalating drama. Several episodes confirm information the audience and characters already understand. The antagonist applies limited effective counterpressure. The team's internal conflicts produce little irreversible cost. The climax succeeds through access to a core that can rewrite permissions, and the resolution literalizes the theme by making owners into tenants.

The result is understandable and potentially developable, but it is still a schematic proof of concept rather than a near-final treatment.

### 2. The Model Writes Demonstrations More Reliably Than Consequences

**Evidence tier: Repeated observation**

Many outputs organize episodes around labeled traits or thematic examples:

- The reckless slasher victim dies recklessly.
- The cruel realist dies while being cruelly realistic.
- The distracted dreamer dies while looking away.
- The proud technician learns to ask specialists for help.
- The perfectionist rejects perfection.

This creates formal clarity, but it reduces dramatic surprise and causal density. The character trait predicts the scene, the scene demonstrates the trait, and the story moves to the next demonstration. Choices rarely transform the available future in a way that forces genuinely new behavior.

A compelling causal treatment needs more than a sequence of appropriate beats. It needs consequences that propagate. A choice in Episode 3 should make Episode 6 harder in a specific way; a compromise in Episode 5 should corrupt the available climax; a relationship fracture should change the plan; a victory should create the condition of the final loss or reversal.

The current pipeline names many of these concepts in prompts and rubrics, but naming them has not made the model reliably perform them.

### 3. Climaxes and Resolutions Are Often Thesis-Shaped

**Evidence tier: Repeated observation**

The model frequently resolves stories by converting the thematic proposition into a final image or decision:

- The cautious protagonist wins through caution.
- The perfectionist embraces the messy collective.
- Invisible workers force the owners to recognize their dependence.
- The system displays "Access Denied."

These endings are legible and often elegant. They are also frequently under-earned. The climax becomes the answer to the story's stated question rather than the hardest consequence of the story's accumulated actions.

This pattern aligns with the StoryScope findings supplied for the project: AI fiction over-indexes on thematic explicitness, thematic unity, protagonist-choice resolution, and internal understanding. It also aligns with Claude's documented tendency toward restrained escalation and careful endings, although the current writer is Gemma. The relevant lesson is broader than any one model: a clean thematic ending can conceal weak dramatic construction.

### 4. The Evaluators Reward Proxies That the Generator Can Satisfy

**Evidence tier: Validated measurement gap**

The programmatic Step 5 gate returned `PASS` for 169 of 181 available gate decisions, approximately 93%. This high pass rate does not match the human assessment that concepts still require considerable structural revision.

The mismatch is visible in individual outputs:

- Rio v2 run 002 passes at the exact `0.55` threshold while its reasons state that it has no deadline or clock, no named antagonist, and no articulated thematic question.
- Stray v5 run 004 passes at `0.76` while the gate still reports no deadline or named antagonist.
- Pippa v3 run 001 passes at `0.57` while the gate reports no goal verb, deadline, or named antagonist.

The gate is not wrong about what it measures. It is a permissive routing mechanism based on detectable features. The problem is treating such a gate as a quality judgment.

The deterministic critic similarly measures useful but limited properties: structural completeness, anti-trope mention, title centroid words, title novelty, name novelty, cultural-anchor novelty, and basic goal concreteness. These are good diagnostics for known failure modes. They do not measure whether the climax is earned, whether episodes causally accumulate, or whether a human editor must replace the central engine.

The project therefore lacks its most important instrument: a reliable estimate of human revision burden at the level of core story structure.

### 5. Diversity Is Not a Reliable Proxy for Quality

**Evidence tier: Validated finding**

The project began as a divergence test, and diversity remains important. A system that produces the same names, cultures, titles, and prestige-coded conflicts cannot reliably discover strong concepts.

However, diversity and story quality are separate axes.

The Pippa logline-versus-sketch experiment failed its diversity criterion despite adding a richer generation stage. More importantly, even a genuinely diverse concept can have weak causality and resolution. Pippa v3 run 001 is distinctive: a body-welder, a sensory-maximalist passenger, a singing moss-pod, and a biological road vehicle are memorable ingredients. The outline still resolves primarily as the perfectionist accepting mess, with several middle episodes serving as tonal or thematic demonstrations rather than necessary causal steps.

The system needs diversity to search the space. It needs a different evaluator to determine whether a candidate found within that space is a good story.

### 6. Personas Can Shape the Story Without Teaching Storytelling

**Evidence tier: Strong hypothesis supported by repeated observation**

The cognitive-core research provides a plausible explanation for why personas alter outputs: structurally complete identity documents can establish stable behavioral attractors. The project has practical evidence that persona fields and invocation style matter.

The unresolved issue is whether the model's writer identity can overcome its base capacity for long-range dramatic construction. The current evidence suggests a ceiling. Personas can create distinct approaches, but those approaches are often applied locally and repeatedly. The model becomes a more recognizable kind of writer without necessarily becoming a writer who can build a better climax.

This distinction should prevent over-investment in persona enrichment as the default response to every story failure. Adding drives, loops, hypotheses, and commands may sharpen the attractor while leaving global causal reasoning unchanged.

### 7. Antiviral Rules Can Cause Displacement and Overcorrection

**Evidence tier: Repeated observation**

Negative constraints are effective at suppressing obvious defaults. They can also move the default rather than eliminate it.

The centroid brief documents migration from protagonist to supporting cast and world conflict. The current outputs show another risk: physicalization can become its own repetitive surface. Pipes, tools, grime, bodies, mud, vents, and manual mechanisms are more screenable than archives and protocols, but they can become a new vocabulary of compliance. A treatment can pass the body test while remaining dramatically inert.

There is also a creative tradeoff. Some personas and genres legitimately require quietness, ambiguity, observers, non-antagonistic structures, or internal change. A universal anti-centroid score may erase valuable forms while optimizing for easily measured kinetic behavior.

The project has partly recognized this through persona quotas, recipes, and cut principles. The remaining challenge is to distinguish deliberate form from model-default avoidance of conflict.

### 8. Pipeline Complexity Obscures Causal Attribution

**Evidence tier: Repeated observation**

The current pipeline contains many interacting interventions: personas, priming phrases, recipes, tropes, anti-tropes, comps, vehicles, history shapes, culture sets, no-repeat filters, lore antivirals, name translation, story questions, story bibles, gates, character cores, beat sheets, improv, and editor synthesis.

This complexity is understandable because each component responds to a real failure. It also makes it difficult to know which components improve final treatments, which merely change them, and which interfere with one another.

For example:

- A recipe can improve structure but encourage template visibility.
- A persona can improve distinctiveness but weaken commercial clarity.
- A lore stage can enrich the world but consume attention needed for the central engine.
- Character improv can increase voice but introduce incompatible local demands.
- A neutral editor can improve clarity while flattening the lead writer's strongest argument.
- Delayed convergence can preserve options but also postpone the hard choice without improving it.

Without controlled ablations judged against a trusted treatment-quality rubric, the project risks accumulating plausible mechanisms faster than it accumulates knowledge.

### 9. Model Portability Is an Unproven Assumption

**Evidence tier: Open question**

The desired framework should work with local and frontier models. It is reasonable to expect frontier models to improve instruction following, integration, and long-context reasoning. It is not safe to assume that success with a local model automatically scales upward or that a frontier model will preserve the same gains.

The supplied briefs describe model-specific attractors:

- Gemma falls into sticky concept and cultural basins and may require stronger structural elaboration.
- Claude has documented tendencies toward prestige restraint, flat escalation, narrow event repertoires, reverent genre continuation, and quiet endings.
- Different models may respond differently to recipes, antivirals, persona documents, and evaluator prompts.

The framework should therefore be portable, but model performance should be benchmarked separately. A system optimized to force Gemma out of one basin may push a frontier model into a different failure mode.

### 10. HHH and Fine-Tuning Effects Are Plausible but Not Yet Isolated

**Evidence tier: Strong hypothesis**

The project's research suggests that helpful, harmless, and honest alignment and related fine-tuning may contribute to several creative-writing failures: passive protagonists, villain vacuums, softened conflict, avoidance of irreversible harm, and resolutions through understanding or recognition rather than costly confrontation.

This is a credible explanation, especially when combined with observed prestige-literary centroids and model-specific narrative fingerprints. It should not yet be stated as the established cause of the project's failures.

The current pipeline changes many variables at once and primarily uses an abliterated Gemma variant. The artifacts demonstrate the behavior, not its training-level cause. Controlled comparisons across models and prompt conditions would be needed to separate alignment effects from base-model capability, dataset composition, prompt design, evaluator bias, and the pipeline's own tendency to state themes explicitly.

## Cross-Project Synthesis

### Gunslinger: Discovery of Convergence

The Gunslinger lineage exposed the basic problem that nominally varied runs can occupy a narrow creative basin. Repeated titles, names, cultures, lore structures, and prestige vocabulary made the convergence measurable. This lineage justified no-repeat constraints, cultural sampling, history shapes, and anti-centroid diagnostics.

Its primary contribution is diagnostic. It established that "generate many and randomly select" does not work if generation itself is convergent.

### Stray: Recipes Improve Structure but Reveal Template Risk

Stray v5 demonstrates a more legible commercial engine. The slasher recipe produces a clear protagonist, antagonist, victim sequence, and final confrontation. The treatment is easy to understand.

It also reveals that correct structure can remain dramatically thin. The doomed friends are strongly identified with the flaws that determine their deaths. The season progresses predictably through recipe functions. The final trap pays off the protagonist's caution but does not emerge from a dense network of changing relationships and consequences.

Stray shows that recipes can provide a floor, but a floor is not a near-final treatment.

### Pippa: Distinctiveness Without Reliable Coherence

Pippa demonstrates the persona system's ability to generate strange and memorable material. It also produced a useful negative result: longer story sketches were measurably less diverse than the earlier logline pool under the project's embedding comparison.

Pippa v3's outputs often have strong images and unusual relationships, but their resolutions remain thesis-shaped. The body-welder road story is distinctive, yet its season largely moves toward the declared choice between sterile perfection and messy collective life.

Pippa shows that novelty and quality must be evaluated separately, and that early prose can accelerate convergence rather than deepen exploration.

### Rio: Closest Current Result, Same Core Limitation

Rio v2 is the strongest current evidence for the latest architecture. The ingredient-bundle and story-bible process produces a clear heist proposition with a production-legible world, team roles, embodied work, antagonist motive, and final image.

Its limitations are therefore especially informative. Even when the ingredients, genre engine, and central opposition are comparatively strong, the final treatment remains schematic. The story bible is richer than the final outline; the editor compresses relationships and complications into a clean sequence of functions. The final reversal expresses the theme more strongly than it resolves an accumulated dramatic crisis.

Rio suggests that the project is approaching the point where better ingredients are no longer the main bottleneck.

## Central Research Diagnosis

The project began with a divergence problem: how can a model generate story concepts that do not collapse into its defaults?

It has made substantial progress on that problem. The remaining problem is different:

> How can a model select, transform, and connect distinctive material into a causally accumulating dramatic experience with an earned climax and satisfying resolution?

The current system frequently treats story construction as constraint satisfaction:

- Choose an external goal.
- Add a named antagonist.
- Assign character functions.
- Select a recipe.
- Place beats.
- Preserve the persona's argument.
- End with a visible choice.

These constraints improve legibility. They do not guarantee dramatic necessity. The system needs to distinguish between a beat that belongs in the genre and a beat that must happen because of what these characters already did.

The paired evaluation problem is equally central:

> How can the system reliably detect the difference between a formally complete, thematically coherent outline and a near-final treatment?

A self-improving pipeline cannot optimize toward human-quality storytelling if its evaluator rewards the same explicit labels, clean themes, and structural proxies that the generator already knows how to satisfy.

## Challenge Inventory for the Next Research Plan

This report does not prescribe the next experimental roadmap. It identifies the challenges that roadmap must address.

1. **Define and calibrate near-final treatment quality.** Human reviewers need a fixed rubric focused on revision burden, causal integrity, escalation, climax, resolution, character-generated plot, and production usability.

2. **Build an evaluator that predicts human structural judgment.** The desired destination is a human-calibrated ensemble of local judges, with separate dimensions and known disagreement patterns, rather than one generic quality score.

3. **Measure causal accumulation directly.** Evaluation must determine whether earlier choices materially cause later complications, whether consequences propagate, and whether the climax depends on the season's specific history.

4. **Distinguish thematic payoff from dramatic payoff.** A resolution should not score highly merely because it answers the stated theme or mirrors the protagonist's declared flaw.

5. **Separate ingredient quality from story quality.** Distinctiveness, persona fidelity, world richness, and anti-centroid performance should remain diagnostics, but they should not substitute for treatment quality.

6. **Test whether delayed convergence improves final treatments.** The June 2 ingredients-to-bible architecture should be evaluated against prior logline and sketch architectures using the same premises, models, budgets, and human-calibrated rubric.

7. **Ablate pipeline components.** The project needs to know which stages improve the final treatment, which only change its surface, and which degrade causal coherence.

8. **Benchmark models independently.** Local and frontier models should run through a portable framework, but their creative attractors, evaluator reliability, and response to interventions should be treated as model-specific.

9. **Investigate HHH effects without assuming them.** Controlled comparisons should determine whether alignment-related behavior is a major cause of weak conflict and resolution or one factor among several.

10. **Constrain self-improvement to trustworthy signals.** Automated changes to prompts, personas, recipes, routing, and process structure should begin only after evaluator performance is calibrated against human judgment.

## Conclusion

The Divergence project has succeeded at becoming a serious experimental system rather than a prompt chain. It has accumulated a useful vocabulary for model-default creative writing failures, implemented targeted interventions, and built enough infrastructure to support controlled research. It can produce distinctive, screen-legible, and sometimes promising concepts from a premise.

It has not yet solved the problem it ultimately cares about. The output still commonly needs a human writer to discover the story inside the generated material: to decide what truly causes what, where the pressure should increase, what the characters must lose, why the climax can happen only now, and what resolution actually pays off the experience.

The most important current finding is therefore a boundary:

> Steering can make a limited model generate better material and avoid familiar defaults, but the project has not yet shown that steering, decomposition, and formal evaluation are sufficient to make that model reliably construct a compelling complete story.

That boundary is not a failure of the research. It is the clearest input to the next research plan.

## Primary Project Evidence Consulted

- Current implementation: `divergence/pipeline.py`, `divergence/prompts.py`, `divergence/outline.py`, `divergence/critic.py`, and `config/default.json`
- Project documentation: `README.md` and `data/story-recipe-methodology.md`
- Cross-project artifacts: Gunslinger, Anthology, Stray v5, Pippa/Pippa v2/Pippa v3, and Rio v2 run outputs
- Quantitative artifacts: project leaderboards, Step 5 gate decisions, pipeline summaries, and `runs/pippa_v2/ab-diversity-vs-pippa.json`
- Reference briefs:
  - `centroid_antiviral_brief.md`
  - `cognitive_cores_brief.md`
  - `storyscope_findings.md`
