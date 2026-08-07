# StoryScope — Narrative-Fingerprint Findings

*Portable brief for any Claude Code writing session. Standalone — no project context required to use. Can be pasted into a fresh session as preamble or referenced via path.*

*Source paper: Russell, J., Rajendhran, R., Pham, C.M., Iyyer, M., Wieting, J. (2026). "StoryScope: Investigating idiosyncrasies in AI fiction." Preprint under review, arXiv:2604.03136v4. Local copy: `references/2604.03136v4.pdf`. University of Maryland + Google DeepMind. Dataset: 61,608 stories (~5,000 words each), 304 narrative features, 10,272 prompts, six sources (Claude Sonnet 4.6, GPT 5.4, Gemini 3 Flash, DeepSeek V3.2, Kimi K2.5, and human).*

*Companion briefs: `references/cognitive_cores_brief.md` (Vasilenko attractor framework — geometric why), `references/centroid_antiviral_brief.md` (prestige-literary centroid — protagonist-level antiviral).*

---

## The paper in one paragraph

StoryScope extracts 304 interpretable, discourse-level narrative features from each story (NarraBench-grounded: Agent, Social Network, Event, Plot, Structure, Setting, Time, Revelation, Perspective, Style) and trains XGBoost classifiers on them. **Narrative features alone — no style cues — separate human from AI at 93.2% macro-F1, retaining 97% of the performance of the model that includes style.** Six-way authorship attribution reaches 68.4%. Crucially, 30 *core* features carry most of the human-AI signal, and surface stylistic rewriting (LAMP, the Chakrabarty span-level artifact remover) barely moves the needle — narrative structure is **orthogonal to style and more durable than vocabulary**. The five AI models cluster in a tight, shared region of narrative feature space; the human stories occupy a rarer, more dispersed region (Cohen's d = 0.83 in per-story rarity). Each model also has a measurable *narrative fingerprint* — a small set of features where it diverges from the other AI sources.

---

## The empirical claim, in measurable terms

| Cut | Macro-F1 |
|---|---|
| Narrative features only (257) | 93.2% |
| Narrative + Style (304) | 96.0% |
| Style only (39) | 85.8% |
| Core narrative only (30) | 84.8% |
| Core + Fingerprint (101) | 91.1% |
| Narrative features on LAMP-edited Gemini stories | 93.9% |

The narrative signal is **not** an artifact of length: human stories average 6,400 words, AI averages 4,500, but on a length-matched subset the Narrative model still scores 93.2%. The signal is also not memorization: dropping likely-memorized prompts shifts results by ≤ 0.3 points.

**Geometric corroboration of `cognitive_cores_brief.md`.** Mean human-AI centroid distance is 1.6× the mean AI-AI distance in z-scored feature space (6.6 vs 4.3). The closest human-AI centroid pair is farther apart than the most distant AI-AI pair. Per-story rarity (mean distance to 25 nearest neighbors): humans 0.71 vs AI 0.49 percentile, Cohen's d = 0.83. **AI models converge to a shared attractor in narrative space**; this is the Vasilenko basin framework with prose fiction as the substrate instead of activation vectors.

---

## The 30 core features — what to do MORE of, what to do LESS of

The paper's Table 15 groups the 30 core features by what they reveal. AI column = average across all five models. Gap = Human − AI; negative gaps are AI-elevated.

### AI-elevated: Thematic over-determination *(do less of these)*

| Feature | Human | AI | Gap |
|---|---|---|---|
| Thematic Explicitness & Moralizing (1–5) | 3.28 | 3.94 | −0.65 |
| Moral / Philosophical Weighting (1–5) | 3.26 | 3.68 | −0.42 |
| Thematic Unity (1–5) | 4.41 | 4.74 | −0.33 |
| Narrator explicitly comments on themes | 52% | 77% | −25 |
| Dialogue serves philosophical debate | 34% | 59% | −25 |
| Intertextual references are vague allusions | 50% | 72% | −22 |

The narrator-states-the-moral move alone is a 25-point human-AI separator. AI "spells out meaning rather than trusting the reader to infer it" (paper §4.1).

### AI-elevated: Sensory & embodied over-rendering *(do less of these)*

| Feature | Human | AI | Gap |
|---|---|---|---|
| Emotion conveyed via embodied metaphors | 38% | 81% | −42 |
| Setting as psychological mirror (1–5) | 3.58 | 4.07 | −0.49 |
| Environmental / ecological emphasis (1–5) | 2.83 | 3.21 | −0.38 |
| Sensory modality: olfactory | 57% | 82% | −26 |
| Sensory density (1–5) | 3.66 | 3.93 | −0.26 |
| Depth of interior access (1–5) | 3.67 | 3.93 | −0.26 |

The 42-point gap on embodied-metaphor emotion is the largest single AI fingerprint in the dataset. "Where a human author might write that a character *felt afraid*, AI renders fear as a tightening chest, cold sweat, and dimming lamplight."

### AI-elevated: Structural streamlining *(do less of these)*

| Feature | Human | AI | Gap |
|---|---|---|---|
| Causal chain continuity (1–5) | 3.92 | 4.20 | −0.28 |
| Spatial granularity (ord) | 2.27 | 2.53 | −0.26 |
| Resolution driven by protagonist choice | 46% | 69% | −23 |
| Character introduction via external description | 30% | 52% | −22 |
| No subplots at all | 57% | 79% | −22 |
| Resolution mode = internal understanding | 27% | 47% | −21 |
| Opening spatial grounding (ord) | 2.12 | 2.33 | −0.20 |
| Pre-threat character investment (1–5) | 2.76 | 2.99 | −0.23 |

AI stories arrive on a clean causal track, the protagonist solves things from inside, and there are no loose threads. Human stories are messier.

### Human-elevated: Intertextual richness *(do more of these)*

| Feature | Human | AI | Gap |
|---|---|---|---|
| Explicit named intertextual reference | 47% | 24% | +23 |
| Reference explicitness = balanced mix | 37% | 16% | +21 |

Humans name specific texts, authors, brands, places, songs. AI hedges with vague allusions.

### Human-elevated: Reader engagement *(do more of these)*

| Feature | Human | AI | Gap |
|---|---|---|---|
| Fourth-wall permeability (0–3) | 0.67 | 0.39 | +0.28 |
| Direct reader address (0+) | 0.28 | 0.07 | +0.21 |

Humans address the reader, break the fourth wall, treat audience as co-participant. AI writes as though no one is watching.

### Human-elevated: Temporal complexity *(do more of these)*

| Feature | Human | AI | Gap |
|---|---|---|---|
| Depth of recontextualization after surprise (1–5) | 3.28 | 2.95 | +0.34 |
| Chronological discontinuity (1–5) | 2.40 | 2.12 | +0.28 |
| Nonlinear framing for delayed disclosure (1–5) | 1.96 | 1.68 | +0.28 |
| Anachrony intensity (1–5) | 2.58 | 2.31 | +0.27 |

Humans use flashbacks, flash-forwards, time jumps, and revelations that force re-reading of earlier scenes. AI tells the story chronologically from first clue to grand reveal.

### Human-elevated: Narrative diversity *(do more of these)*

| Feature | Human | AI | Gap |
|---|---|---|---|
| Location variety scope (ord) | 1.34 | 1.08 | +0.26 |
| Dialogue-to-narration proportion (1–5) | 2.95 | 2.70 | +0.24 |
| Subplot integration = thematically parallel | 42% | 21% | +22 |
| Moral polarity toward protagonist = ambivalent | 59% | 38% | +21 |
| Emotion conveyed via explicit labels | 29% | 8% | +21 |

The morally ambivalent protagonist (59% vs 38%) is structurally adjacent to the prestige-literary centroid problem in `centroid_antiviral_brief.md` — but the StoryScope finding is the opposite axis. The centroid antiviral pushes away from *observer protagonists*; the StoryScope finding pushes toward *morally compromised protagonists*. They are independent: a courier who breaks the law for a defensible reason satisfies both.

---

## Claude's specific narrative fingerprint (Table 16)

These are the features where Claude's SHAP importance is concentrated in *Claude* relative to the other four AI models — not the human-vs-AI axis, but the what-makes-Claude-Claude axis. Higher uniqueness ratio = more specifically a Claude tell.

| Rank | Feature | Dim | Uniqueness | Direction |
|---|---|---|---|---|
| 1 | **Strength of event escalation** | EVT | 22.4× | Low — events don't escalate |
| 2 | **Event-type diversity** | EVT | 10.7× | Low — narrow event repertoire |
| 3 | Ending temporal scope = epilogue / flashforward | TMP | 8.9× | High — likes epilogues |
| 4 | Dreams / visions as temporal distortion = **no** | TMP | 7.7× | High — avoids dream sequences |
| 5 | Setting mood = uncanny / haunted | SET | 4.6× | High — over-indexes on this mood |
| + 21 more | (event density, conflict modality, relationship trajectory, heteroglossia, closure, …) | | | |

Plus a feature called out in §5 of the paper: **"reverent / continuist approach to literary tradition" 62% of Claude stories** (vs 39–56% for other models). Claude honors and extends storytelling conventions rather than subverting or challenging them.

The paper's summary: *"Claude keeps it cool. Its stories are defined by its restraint: event intensity escalates less than in any other source, and narrative voice is the most uniform. ... It favors epilogues and avoids dream sequences, producing careful, consistent stories that favor quiet endings over 'avalanche' endings."*

**This is directly relevant to two existing Codeywood findings.** (1) The flat-escalation default is the Sonnet trap behind the *villain-vacuum* finding (`feedback_villain_vacuum_claude_ceiling.md`) — a story where events don't escalate has no need for an embodied antagonist. (2) The "reverent / continuist" default is the trap behind the *literal-reading drift* finding (`feedback_persona_literal_reading.md`) and the *Anti-Trope Protocol* in `story-recipe`: Claude's instinct is to extend the canonical version of the form rather than subvert it. The new `story-recipe` skill, which works *from* commercial exemplars, sits closest to this trap — it must defend against Claude's reverent-continuist default explicitly.

For reference, the other models' top fingerprints:

- **GPT 5.4** — gossip / rumor as plot mechanism (64% vs 44–55%), distant retrospective narration, subverts expectations more (41% vs 27–36%), partial / ambiguous reconciliations.
- **Gemini 3 Flash** — protagonist's social trajectory expands, primarily-direct speech, "siege / ordeal" global narrative schema, frequent flashbacks, **bleakest settings (88% tagged bleak / oppressive)**, tidiest endings.
- **DeepSeek V3.2** — front-loads context, emotional expression via behavioral cues, evenly-interleaved backstory, embedded storytelling scenes.
- **Kimi K2.5** — in-action-event character introductions, in-medias-res entry, no explicit trait labeling. Lowest F1, "generic center of the AI distribution."

---

## What this brief does *not* yet do

This brief records findings. It does not yet wire them into Codeywood skills. The next moves, when chosen, would be:

1. **A "Lane C: Structural Anti-Fingerprint"** in writers-room v3.6 Phase 4, alongside Lane A (stakes) and Lane B (embodied antagonist). Required draft-time declarations on time-jumps / anachrony, subplot integration, moral polarity of protagonist, ending mode, and intertextual specificity.
2. **A Claude-Trap audit** as a Phase 6/7 pass: explicit check for the five fingerprint features (flat escalation, low event-type diversity, epilogue ending, absence of dreams/visions, uncanny/haunted overuse) + the "reverent / continuist" default.
3. **A pitch-round structural-score upgrade** — 5–6 measurable structural scores appended to existing pitch evaluation. Pairs with the existing concept-seed + antiviral-blocklist machinery.
4. **Story-recipe ↔ StoryScope integration** — when `skills/writer/story-recipe/` extracts a recipe from exemplars, also extract their structural fingerprint, so the writer knows the *AI default vs the genre default vs the exemplar's actual structure* and can deviate intentionally.

The features that translate cleanly from prose to screenplay: theme over-determination, sensory over-rendering, single-track plots, protagonist-driven resolution, weak intertextuality, ending mode, moral polarity, anachrony. The features that don't translate (dialogue-to-narration ratio, narrator address mode, fourth-wall permeability) should be **dropped from the screenplay variant, not awkwardly forced**.

---

## How to apply this brief in a new session

Paste into the new session's preamble (or open this file as a reference):

> *Apply the StoryScope narrative-fingerprint findings to this work. Source: `references/storyscope_findings.md` (Codeywood synthesis of Russell et al. 2026, arXiv:2604.03136). The 30 core features in Table 15 measure how AI fiction structurally differs from human fiction — independent of style. The Claude fingerprint (Table 16) names the specific defaults Sonnet falls into: flat event escalation, narrow event-type diversity, epilogue endings, no dream sequences, uncanny/haunted setting mood, reverent/continuist genre stance. Use these as deliberate counter-pressure during drafting and review. The findings are orthogonal to surface style — paraphrasing won't fix a story that pattern-matches the AI cluster on these features.*

If the session is doing **pitch-round** work: cite the brief as a structural-evaluation layer that complements the existing antiviral blocklist and the centroid antiviral. The blocklist is lexical / occupational; this brief is structural.

If the session is doing **writers-room** work: cite the brief at Phase 3 (Structural Stakes Checklist) and Phase 4 (Required Premortem Lanes) as the source of a future Lane C. For now use it as a manual checklist at Story Lock.

If the session is doing **story-recipe** work: the Claude fingerprint is the trap closest to this skill — *reverent / continuist* genre stance is Claude's default when working from exemplars. Treat exemplar conformity as a deliberate choice, not a default.

If the session is doing **video / screenplay** work: ignore dialogue-to-narration, narrator-address, and fourth-wall features. Keep theme over-determination, sensory over-rendering, single-track plot, protagonist-driven resolution, moral polarity, anachrony, intertextual specificity. The flat-escalation finding is doubly important on screen because escalation in video is also a pacing problem.

---

## Cross-references inside Codeywood

- `references/cognitive_cores_brief.md` — Vasilenko's attractor framework predicts what StoryScope measures. The AI cluster in narrative space is the basin; the persona document is the steering vector that lands the model elsewhere. StoryScope is empirical corroboration of the geometric claim, with prose fiction as substrate.
- `references/centroid_antiviral_brief.md` — protagonist / cast / world-level antiviral against the prestige-literary centroid. Operates at the occupation and conflict-register axis. StoryScope operates at the discourse-structure axis. The two are independent and additive; both should run.
- `skills/writer/ANTIVIRAL_PROMPT.md` — 40+ item lexical and tone blocklist. Surface-level. StoryScope explicitly shows that style-level edits (LAMP) barely move the narrative classifier — the blocklist alone is insufficient.
- `feedback_villain_vacuum_claude_ceiling.md` — the structural correlate of Claude's #1 fingerprint (flat event escalation).
- `feedback_persona_literal_reading.md` — the structural correlate of Claude's "reverent / continuist" default.
- `skills/writer/story-recipe/SKILL.md` — the skill most exposed to the Claude reverent-continuist trap; needs an explicit anti-fingerprint check before it can ship as a Phase 0 dependency.

---

## Origin and validation

**Discovered:** 2026-05-27, user-prompted reading of arXiv:2604.03136v4 with the question "how can we incorporate insights from this paper?"

**Status:** Findings recorded. **Not yet operationalized** in any skill. Treat as a hypothesis-rich reference until at least one of the four operational moves above (Lane C, Claude-Trap audit, pitch-round score, story-recipe integration) has been built and tested on a real project. The paper's empirical work is on prose fiction with five frontier LLMs in November 2026 — the *direction* of the findings is robust (replicated across length-matched subsets, BISAC topic categories, and surface-edited stories), but the *magnitudes* may not transfer 1:1 to the Codeywood screenplay-then-video pipeline.

The most defensible immediate use of this brief: **as a checklist for human review** at Story Lock and at completed-draft milestones. Operational tooling can follow once the checklist proves itself on two or three projects.
