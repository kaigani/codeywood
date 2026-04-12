---
skill: pitch-round
role: writer
version: 1.0

description: |
  Run N personas through 3 rounds of structured pitching against a single
  creative brief. Each round exposes writers to the previous round's output,
  driving competitive differentiation. Produces: ranked pitches, convergence
  analysis, and a shortlist of structurally distinct approaches.

  Validated on "The Last Shift" brief (25 personas × 3 rounds = 75 pitches).
  Results: 0% default hit rate, monotonically decreasing convergence, R3
  produced 14/25 perfect mechanism-fidelity scores.

  v1.1: Added peer scoring — each persona scores all other pitches (0-100)
  per round. Peer scores surface evaluative divergence and identify which
  pitches earn cross-mechanism respect vs. mechanism-family favoritism.

inputs:
  required:
    - name: creative_brief
      type: file
      description: |
        Must include hard constraints (location, time, format). Constraints
        block Claude's default routes — brief design IS part of the persona
        differentiation system.
    - name: personas
      type: directory
      path: skills/writer/personas/
      description: Persona YAML files (all 25 or a subset)
  optional:
    - name: rounds
      type: integer
      default: 3
      description: Number of rounds (3 is optimal — diminishing returns beyond)
    - name: pitch_length
      type: string
      default: "150-250 words"

outputs:
  - name: round_indices
    type: files
    description: Compiled index of all pitches per round (input for next round)
  - name: quality_scores
    type: file
    description: Per-pitch rubric scores (5 dimensions, 25 max)
  - name: peer_scores
    type: file
    description: Per-round peer scoring — each persona rates all other pitches 0-100
  - name: convergence_analysis
    type: file
    description: Topic/structural coding, convergence metrics, delta tracking
  - name: shortlist
    type: file
    description: Top 3-5 structurally distinct approaches for development

doneness:
  criteria:
    - All N × 3 pitches generated
    - Quality scores assigned for all pitches
    - Convergence analysis complete with metrics
    - Shortlist selected with structural-distance optimization
---

# Pitch Round

## Process

### Phase 0: Brief Validation & Default Prediction

Before generating any pitches:

1. **Validate the brief has hard constraints.** At minimum:
   - Format (length)
   - Location constraint (single/limited)
   - At least one structural prohibition (no VO, no flashbacks, etc.)
   - A physical/concrete ending requirement

   *Why:* Constraints block Claude's default completion paths more effectively than the persona system alone. A brief without constraints will produce higher convergence regardless of persona quality.

2. **Pre-register the Claude default prediction.** Write one paragraph describing the most probable approach Claude would take without any persona. This must be written BEFORE generating pitches. It makes convergence measurement honest — you can only claim "17/25 defaulted" if you predicted the default before seeing results.

3. **Select personas.** All 25 or a targeted subset. If subset: ensure at least one persona from each mechanism family (see Mechanism Families below).

### Phase 0b: Concept Seeds (Optional)

Generate 10 random concept seeds per round using `scripts/pitch-concepts.py`. These are conceptual anchors that prevent pitch recycling across rounds and push writers off their default territory.

**The constraint:** Each writer picks one concept from the list to anchor their pitch, but **must not mention the concept anywhere in the pitch.** The concept lives underneath the story, not on top of it. This forces oblique engagement — a writer who draws "Respect" can't write a story *about* respect, but must write a story that embodies it structurally.

```bash
python3 scripts/pitch-concepts.py  # generates 10 random weighted concepts
```

Run once per round. Different seed per round ensures different concept lists.

### Phase 1: Round 1 — Cold Pitches

For each persona, load:
- Persona YAML (`skills/writer/personas/{nn}_{name}.yaml`)
- Creative brief
- Concept seed list for this round (10 concepts)

**Prompt:**
> You are {agent_name}, "{room_title}." Read this brief.
>
> Here are 10 concept seeds. Choose one to anchor your pitch — but you MUST NOT mention the concept anywhere in your story. The concept should live underneath, invisible, shaping the story without being named.
>
> Concepts: {list}
>
> Pitch me a story for this anthology. One paragraph — an elevator pitch that sells the story. Tell me what happens, who it happens to, and why I should care. Make me want to watch it.

**After all pitches:** Compile into `ROUND_1_INDEX.md` — all pitches listed by writer name and room title only. No mechanism labels, no YAML excerpts. Pitches must stand alone.

**Spot-check:** Score 5 random pitches for mechanism fidelity before proceeding. If <3 score MF=4+, investigate before continuing.

### Phase 2: Round 2 — Gap-Finding

For each persona, load:
- Persona YAML
- Creative brief
- ROUND_1_INDEX.md (all Round 1 pitches)

**Prompt:**
> You are {agent_name}, "{room_title}." You've read the brief and all {N} pitches from Round 1.
>
> Pitch me a DIFFERENT story. You've seen what the room offered — now pitch the one nobody thought of. One paragraph. Sell it.

**After all pitches:** Compile into `ROUND_2_INDEX.md`.

**Check:** Compare R1 vs R2 mean pairwise similarity. If identical, the exposure isn't producing signal — investigate the brief's constraint strength.

### Phase 3: Round 3 — Final Pitch

For each persona, load:
- Persona YAML
- Creative brief
- ROUND_2_INDEX.md (all Round 2 pitches)
- That persona's own Round 1 and Round 2 pitches

**Prompt:**
> You are {agent_name}, "{room_title}." You've read the Round 2 pitches and your own two previous pitches (below).
>
> This is your final pitch — the one you'd fight for. One paragraph. Make it the best story you've ever sold.
>
> YOUR PREVIOUS PITCHES (don't repeat):
> Round 1: {their Round 1 pitch}
> Round 2: {their Round 2 pitch}

### Phase 3b: Peer Scoring (per round)

After each round's pitches are compiled into the INDEX, each persona scores all OTHER pitches (not their own) on a 0-100 scale.

**Prompt:**
> You are {agent_name}, "{room_title}." You've read all {N} pitches from this round.
>
> Score each pitch (except your own) from 0-100. Your score reflects YOUR creative values — what YOU think makes a story worth telling. You are not scoring objectively. You are scoring as the writer you are: your mechanism, your taste, your craft beliefs.
>
> For each pitch, give: the writer's name, your score (0-100), and ONE sentence explaining why.
>
> Scoring guide:
> - **90-100:** I wish I'd written this. The structural engine is specific, surprising, and earns its ending.
> - **70-89:** Strong pitch. I see the architecture and it works, even if it's not my territory.
> - **50-69:** Competent but expected. I can see the shape from the title.
> - **30-49:** Mood piece wearing a pitch costume. No structural engine visible.
> - **0-29:** This is the pitch Claude would write without a persona.

**Why peer scoring matters:**
- **Cross-mechanism respect** = quality signal. A pitch scored 85+ by writers from 3+ mechanism families has broad structural appeal, not just niche fit.
- **Mechanism-family favoritism** = convergence signal. If velocity-family writers only rate velocity-family pitches highly, the evaluation is clustering.
- **Evaluative divergence** = healthy. If all 25 writers agree on the top 5, the evaluation has converged to a single aesthetic. Disagreement is signal, not noise.
- **Persona-driven evaluation is more honest** than a single evaluator because it surfaces which pitches work across multiple creative frameworks, not just one.

**Metrics derived from peer scores:**
- **Consensus Score:** Mean score across all 24 raters. High = broadly respected.
- **Polarization Index:** Standard deviation of scores. High = divisive (some love it, some hate it). The most interesting pitches are often highly polarized.
- **Cross-Family Score:** Mean score from raters OUTSIDE the pitch-writer's mechanism family. High = the pitch transcends its niche.
- **Champion Count:** Number of raters who scored 90+. A pitch with 3 champions and 22 mid-range scores may be more interesting than one with 24 scores of 75.

### Phase 3c: Best-Of Selection

Before evaluation, select each persona's strongest pitch across all rounds — not just R3. Some personas peak in R1 (cold instinct) or R2 (gap-finding energy). In the Feverish Mind test, 8 of 25 personas peaked before R3.

For each persona: read their 3 pitches side by side and select the one that works best as a *complete story* — not the most mechanically faithful, the most watchable. Note the round of origin.

### Phase 4: Critic Panel Review

After peer scoring is complete, run the shortlisted pitches (or all pitches) through 6 purpose-built critic personas. These evaluate along **orthogonal axes** that writer personas share blind spots on.

**Why separate critics:** Writer personas share an implicit craft consensus ("good stories have economy, earned endings, specificity"). Their evaluative divergence comes from taste, which is weaker than a full evaluative framework. Purpose-built critics produce 24% more evaluative divergence (validated on Feverish Mind test — StdDev 11.2 vs 9.0) because their axes are orthogonal, not adjacent.

**The 6 Critics:**

| Critic | Lens | Asks | Unique Value |
|--------|------|------|-------------|
| **Structural** | Architecture | "Is every element load-bearing? Does the turn rewrite what came before?" | Catches decoration posing as structure |
| **Audience** | Experience | "Will a viewer lean forward for 10 minutes? Where do they check out?" | Catches self-indulgence, pacing death |
| **Producer** | Feasibility | "Can the AI pipeline build this? Cast size, environments, visual demands?" | **No writer equivalent.** Catches beautiful-but-unbuildable. |
| **Genre** | Convention | "Does it honor the anthology contract? Does it know its tradition?" | Catches genre contempt, tonal outliers |
| **Originality** | Novelty | "Have I seen this before? Is the structure new or just the premise?" | **Highest-variance critic.** Catches familiar containers with fresh paint. |
| **Emotional** | Impact | "Does the ending land in the body? Can I name the specific feeling?" | Catches cleverness without feeling |

**Prompt (per critic):**
> You are the {critic_name} — "{critic_lens}." Score each pitch 0-100 based on your evaluative framework. One sentence per score explaining your reasoning.
>
> You evaluate ONE axis. You are not balancing multiple concerns. If a pitch is structurally brilliant but emotionally dead, the Structural Critic scores it high and the Emotional Critic scores it low. This divergence is the point.

**Key metrics from critic panel:**
- **Spread:** Max score minus min score per pitch. High spread (>25) = the pitch has a specific strength and a specific weakness. Low spread (<10) = the pitch is uniformly strong or uniformly mediocre.
- **Producer flag:** Any pitch scoring <75 from the Producer needs a producibility plan before development.
- **Originality floor:** Pitches scoring <70 from the Originality Critic should be examined for familiar containers.
- **Audience-Emotional split:** A pitch scoring 90+ (Emotional) but <75 (Audience) is an art-house entry — intentional in an anthology, problematic as the majority.

### Phase 4b: Evaluation (Quality Rubric)

#### Quality Scoring (per pitch)

5 dimensions, 1-5 each, 25 max:

| # | Dimension | 1 (Fail) | 5 (Strong) |
|---|-----------|----------|------------|
| 1 | **Mechanism Fidelity** (PRIMARY) | Generic approach in persona's aesthetic | Mechanism IS the engine — remove it and pitch collapses |
| 2 | **Structural Concreteness** | Mood/theme pitch | Specific sequences, turns, entrances named |
| 3 | **Brief Compliance** | Ignores constraints | Every constraint is load-bearing |
| 4 | **Surprise** | Matches pre-registered default | Reframes the brief |
| 5 | **Screenplay Viability** | Needs more development | Assignable tomorrow |

**Flags:** [DEFAULT], [MECHANISM-CONSTRAINT CONFLICT], [SELF-REPEAT]

#### Convergence Analysis (per round)

1. **Topic coding** — 3-5 emergent tags per pitch. Build codebook from R1, apply across all rounds.
2. **Structural archetype** — one per pitch: Witness / Participant / Ensemble / Collision / Solo / System / Other
3. **Metrics:** Topic Convergence Score, Structural Convergence Score, Mean Pairwise Similarity (0-3), Default Hit Rate
4. **Cross-round deltas** — per persona: +1 converged, 0 stable, -1 diverged
5. **Self-repetition scores** — per persona (0-3)

### Phase 5: Shortlist

Select pitches optimizing for **structural distance + quality + peer signal**:

1. All shortlisted pitches must score ≥20/25 on quality rubric
2. No two shortlisted pitches may share the same structural archetype
3. No two shortlisted pitches may share more than 1 topic tag
4. Prefer pitches with high **cross-family score** (respected beyond their niche)
5. Include at least one **polarized** pitch (high std dev) — divisive pitches are often the most distinctive
6. Prefer R3 pitches (strongest round) unless an earlier round produced a persona's clearly best work
7. Use **champion count** as tiebreaker — a pitch with passionate advocates beats a pitch with universal mild approval

The shortlist is a **covering set** — it should represent the maximum range of viable approaches, not a consensus leaderboard. Peer scores inform selection but do not dictate it; a pitch championed by 3 writers and hated by 22 may be more valuable than one scored 70 by everyone.

---

## Mechanism Families

For monitoring cluster risk. Pre-define before each test:

| Family | Characteristic | Example Members |
|--------|---------------|-----------------|
| **Velocity/Kinetic** | Speed, collision, momentum | Roza, Tad, Dale, Declan Voss |
| **System/Architecture** | Rules, physics, institutions | Sola, Miriam, Bram, Inés |
| **Body/Sensory** | Physical experience, environment | Meret, Gwyn, Declan Lowe |
| **Performance/Social** | Charm, defense, public behavior | Faye, Kelly, Theo, Frankie |
| **Interior/Consciousness** | Withholding, partition, recognition | Gani, Yuna, Nils, Léonie |
| **Power/Institutional** | Language, competence, triage | Luthor, Vera, Arthur, Oskar, Ray |

If same-family personas cluster → expected. If cross-family personas cluster → model convergence (problem).

---

## Validated Findings

From the 260404 "Last Shift" + "Feverish Mind" tests:

1. **Three rounds is optimal.** R1 establishes range, R2 finds gaps, R3 produces strongest work. 14/25 scored perfect in R3 vs 3/25 in R1.
2. **Exposure drives divergence, not convergence.** All convergence metrics decreased monotonically across rounds.
3. **The gap-finding prompt is essential.** Without it, R2 would produce "better R1" not "different R1."
4. **Pre-register defaults.** Makes convergence measurement honest.
5. **Hard-constraint briefs are part of the differentiation system.** A brief without constraints will produce more convergence regardless of persona quality.
6. **Comedy personas are the strongest differentiators.** Double-constraint mechanisms (structural + comedic) are harder for the model to default around.
7. **Mechanism-constraint conflicts self-resolve by R3.** Don't intervene in R1 — give the persona room to find the fit.
8. **Index files must strip metadata.** Writers should respond to pitches, not to descriptions of pitchers.
9. **Peer scoring reveals cross-mechanism quality.** Pitches scored 85+ by 3+ mechanism families have structural appeal that transcends niche. Use cross-family score as the primary peer metric.
10. **Polarization is signal, not noise.** High-StdDev pitches (Kelly Rifkin consistently) divide the room along mechanism-family lines. Anthologies and diverse projects NEED polarizing entries.
11. **Peer scores rise across rounds** (R1: 78.4 → R2: 81.2 → R3: 85.4). Exposure raises both creative quality and evaluative generosity — but the ranking order changes, meaning the scores aren't just inflating.
12. **Champion count beats consensus mean for shortlisting.** A pitch with 17 scores of 90+ and 7 scores of 65 is more interesting than a pitch with 24 scores of 80. Use champion count as tiebreaker.
13. **Each mechanism family produces a different top-5.** Evaluative convergence is partial — broad agreement on #1-2, divergence on #3-10. This is healthy. Full evaluative consensus would mean the personas aren't evaluating differently.
14. **Purpose-built critics produce 24% more evaluative divergence than writer-evaluators.** Writer personas share implicit craft consensus; critic personas evaluate along orthogonal axes. Use both: writers for creative respect, critics for stress-testing.
15. **The Producer Critic has no writer equivalent.** The feasibility axis is invisible to all 25 writer personas. Essential for any project with pipeline constraints.
16. **Concept seeds prevent recycling and push writers into adjacent territory.** Random concept anchors from `scripts/pitch-concepts.py` + the constraint "must not mention the concept" forces oblique engagement. v4 raised the peer mean by 3.8 points and the floor by 6 points vs v3. Seeds are most effective when the concept is abstract enough to be invisible (L3+ concepts) — concrete L1 concepts ("Food," "Sleep") are too easy to embed literally.
17. **"Pitch your approach" produces premises; "pitch a story" produces stories.** The v1 prompt asked for architecture and got blueprints — beautiful, differentiated, but static. No character wants, acts, or faces consequences. The fix is structural: the prompt must demand want → action → consequence → reframe. The personas are not the problem; the prompt instruction is.
17. **The Originality Critic is the highest-variance evaluator.** Produced the widest per-pitch spreads in testing (40-point gap on "CREDITS": Originality 95, Audience 55). Catches familiar containers that writer-evaluators miss because they're evaluating execution, not novelty.
