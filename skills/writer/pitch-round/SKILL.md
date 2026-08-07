---
skill: pitch-round
role: writer
version: 2.6

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

  v2.0 (2026-04-13): Wires persona differentiation INTO the iterative round
  structure. Key changes:

  - Phase 0 expanded: default prediction now multi-axis (medium, cultural
    tradition, protagonist type, time of day, tone, audience, visual
    stylization, plus any persona-identified axes) — not a single paragraph.
  - Pitch prompt expanded: pre-declaration now uses full persona lens (mechanism,
    mechanism_non_literal, audience, affective palette, philosophy, polemic).
  - NEW Phase 1b/2b/3b: post-pitch centroid audit. Each persona re-audits
    their own pitch against the pre-registered centroid; peers flag others'
    centroid defaults during scoring; pitches with ≥3 axis defaults are
    refused and re-pitched.
  - Rubric: 7th dimension added (Centroid Busting). A pitch that defaults
    on 3+ axes scores low, even if the pleasure contract was delivered.
  - Shortlist rule: pitches with [CENTROID-CONVERGENCE] flag cannot be
    shortlisted unless no alternative covers their mechanism.

  v2.1 (2026-04-13): Adds the Antagonistic Audience Archetype (AAA) — a
  brief-tuned audience advocate who delivers adversarial-collaborative
  feedback between rounds. Catches auteur drift (personas internalizing
  their own craft values over the audience's experience). Distinct from
  peer scoring (catches craft), centroid audit (catches structural default),
  pleasure contract (catches self-stated-promise failure), and the end-of-
  process Audience Critic (too late to shape output). The AAA runs BETWEEN
  rounds and its memo feeds forward into the next round's prompt.

  The v4 schema audit runs at YAML-design time (persona-level). The v2.0
  pitch-round runs the same audit at output-generation time (pitch-level).
  The v2.1 pitch-round adds iterative audience check at round-transition
  time (room-level). Three audit loops, each catching a different class
  of failure.

  v2.2 (2026-04-13): Splits the single shortlist into TWO distinct outputs.
  The v2.1 pilot revealed that rubric-based shortlists and audience-preference
  shortlists are different jobs measuring different things — collapsing them
  hides important signal. Revised Phase 5 produces:
    - Production Shortlist (AAA Top 5 across all rounds) — decides what goes
      into development. Audience preference is primary.
    - Craft Performance Shortlist (rubric-based) — diagnostic output telling
      us how the personas are performing as a roster.
    - Divergence Analysis — where the lists agree (highest-confidence picks)
      and disagree (real information: audience-only picks may reveal craft
      blind spots; craft-only picks may reveal auteur drift that survived
      three rounds of correction).
  Production decisions default to the AAA Top 5; craft shortlist is the
  roster diagnostic. Evidence: in the Saturday Morning Kids pilot, the two
  shortlists agreed on only 2 of 5 picks. The three disagreements each
  surfaced meaningful signal that would have been lost in a single ranking.

  v2.3 (2026-04-15): Sharpens R2 framing. Prior R2 runs produced drafts
  that were weaker than R1/R3 because personas treated R2 as a rewrite of
  their R1 pitch rather than a new story informed by the room. R2 is
  explicitly a NEW idea, and the revised prompt asks each persona to
  "choose ONE key axis on which to subvert the brief in a way that will
  let you tell the story you're longing to tell." One disciplined
  subversion outperforms scattershot defiance; naming the chosen axis up
  front forces commitment. Evidence: visual-pitch-round R2 rewrite run
  (all 12 writers evolved R1 rather than replacing it) produced +0.44 AAA
  mean but no genre breakthroughs — confirming the rewrite path is a
  local-maximum trap.

  v2.3.1 (2026-04-15): Visual Pitch Round addendum. When the pitch round
  is run as a VISUAL variant (three z-image stills + voicecloned synopsis
  per pitch, assembled as video), each of the three "Visual N" prompts is
  an independent t2i call — no image reference, no style transfer between
  them. If the persona's chosen medium is non-default (animation,
  expressionist, stylized, etc.) the style tag MUST appear at the start
  of EVERY Visual 1/2/3 prompt, not just Visual 1. Format requirement:
  each Visual prompt begins with the medium tag, e.g.
  "Painterly adult animation: ..." — repeated verbatim across all three.
  Evidence: R2 Jax Mori synopsis had "Painterly adult animation:" only
  on V1; V2 and V3 reverted to photoreal default. Pipeline now has a
  safety net (auto-prefix from V1), but the synopsis-writer prompt must
  still enforce explicit per-visual style tags.

  v2.5 (2026-04-15): Centroid is diagnostic, not prescriptive. Prior versions
  (v2.0) put CENTROID_REFERENCE.md in the R1 writer's context with "must
  depart" instructions. This broke genre-coded briefs — for YA, four-quadrant,
  procedural work, the centroid IS the genre contract. Deliberate avoidance
  producing unbriefable pitches. Fix: R1 writers do NOT see the centroid.
  The centroid runs post-R1 as convergence analysis only, to diagnose which
  axes the room drifted toward regardless of mechanism differentiation.
  Phase 1b self-audit retained as diagnostic; no refuse-and-re-pitch rule.

  Visual Pitch Round: the PITCH itself is the voiceable text (not a rewritten
  synopsis). Translation loses clarity — the writer-voice that sells a film
  in prose is the same voice that sells it in a 45-second video. Adapt for
  TTS cadence if needed, but do not "spoken-ify" the pitch into a different
  document.

  v2.4 (2026-04-15): AAA calibration overhaul. Prior AAA v2 panels ran
  1.5–2 points high and used critic-register voice (e.g. a "27yo graphic
  designer" saying "the five runs are dramatised" — Letterboxd LLM cosplay
  rather than civilian speech). Panelists credited pitch-clarity as
  entertainment-value, collapsing the useful score range into 6–10.
  Calibration patch:

    (a) REGISTER DISCIPLINE. Each panelist card includes 2-3 speech tics
        grounded in their demographic (contractions, slang, platform they
        watch on, typical attention span). Forbidden words in verdicts:
        "dramatised", "earns its pace", "rendered", "meditation on",
        "meditative", "resonant", "liminal", "evokes" — any critic-trained
        LLM default. Panelists speak like viewers, not reviewers.

    (b) CALIBRATION ANCHORS. Each AAA charter carries 3–5 example films
        pinned at score bands 10 / 8 / 5 / 3. Anchors differ per
        demographic. Panelists triangulate against their own anchors
        before scoring.

    (c) TWO-SCORE SYSTEM. Each panelist gives (i) "Would I hit play?"
        /10 and (ii) "Did I finish it?" /10. Final score = average.
        Forces separation between pitch-clarity and watch-value.

    (d) FILM-SCOPE TEST. Explicit question per panelist: "Is this the
        whole film, or a scene from one?" Pitches that read as a
        vivid beat inside a larger film (not a complete short) are
        docked.

    (e) TONE / EMOTIONAL-RESIDUE CHECK. Panelist notes the feeling the
        final shot leaves in one line — separate from plot summary.
        Catches morbid-vs-warm endings that text-only scoring misses.

    (f) PLOT VELOCITY TEST (v2.4 core). Explicit question per panelist:
        "Does the story MOVE across its runtime?" Movement counts on
        three axes — EMOTIONAL (someone's state or belief changes
        meaningfully), PHYSICAL (someone acts, travels, builds, breaks),
        VISUAL (the frame changes in kind, not just in subject). A pitch
        that stays emotionally static, physically stationary, AND
        visually monochromatic across its runtime is a tableau, not a
        story. Static pitches are docked on both scores. Evidence from
        visual-pitch-round R2: Ferran's maximalist musical scored highest
        on velocity, confirming the axis has signal. Many C/D-tier
        pitches pass vividness but fail velocity — they describe a
        situation, not a progression.

  Calibration is implemented in `AAA_CHARTER.md` template (example films
  + forbidden words section) and in the panel prompt (two-score + scope
  + tone + velocity questions made mandatory). Expected effect: score
  range re-expands, mean drops ~1.5 points toward ground truth, correlation
  with user-scoring improves.

  v2.6 (2026-04-18): Graduates the anti-viral blocklist into every pitch
  prompt. Validated on the Snowflake 2126 3-way test (5 Terminal-scoring
  personas × Original vs ACTION-swap vs ANTIVIRAL). Influence swap moved
  cohort mean 102.8 → 81.8 (−21pts, left 2 personas Terminal). Antiviral
  blocklist moved cohort mean 102.8 → 39.0 (−64pts, cleared 3 personas to
  Clean/Mild). The virus lives in Sonnet's default vocabulary and
  structural patterns, not in persona influences. Location:
  `skills/writer/ANTIVIRAL_PROMPT.md` (shared with writers-room). The
  blocklist is appended to every pitch prompt (R1/R2/R3) AFTER the
  persona lens and AFTER the brief, as the last thing the model reads.
  Includes the v2 tone-word and tone-move extensions (austere, measured,
  methodical, plus sentence-level register habits) aimed at B5
  prestige-somber residue that survived the initial 20-word blocklist.

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
      path: skills/writer/personas/.runtime/pitch-round/
      description: |
        Pre-rendered v5 persona runtime files (base + slot module). Generated
        via `python3 scripts/personas/render_persona.py --all --skill pitch-round`
        as a preflight step. Runtime files are ~10% the size of full personas.
        Source YAMLs live at skills/writer/personas/{id}.yaml.
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
  - name: centroid_reference
    type: file
    description: (v2.0) Multi-axis default prediction — the centroid the round fights against
  - name: aaa_charter
    type: file
    description: (v2.1) Audience advocate charter, brief-tuned voice for this project
  - name: aaa_memos
    type: files
    description: (v2.1) AAA memo after each round (AAA_MEMO_R1.md, AAA_MEMO_R2.md)
  - name: aaa_final_verdict
    type: file
    description: (v2.1) AAA's set-level verdict on R3
  - name: quality_scores
    type: file
    description: Per-pitch rubric scores (7 dimensions, 35 max in v2.0)
  - name: peer_scores
    type: file
    description: Per-round peer scoring — each persona rates all other pitches 0-100
  - name: convergence_analysis
    type: file
    description: Topic/structural coding, convergence metrics, delta tracking
  - name: production_shortlist
    type: file
    description: (v2.2) AAA Top 5 across all rounds — the production decision (audience-priority)
  - name: craft_shortlist
    type: file
    description: (v2.2) Rubric-based shortlist — roster diagnostic (how did personas perform?)
  - name: shortlist_divergence
    type: file
    description: (v2.2) Where the two shortlists agree (consensus picks) and disagree (real signal)

doneness:
  criteria:
    - All N × 3 pitches generated
    - Quality scores assigned for all pitches
    - Convergence analysis complete with metrics
    - Shortlist selected with structural-distance optimization
---

# Pitch Round

## Process

### Phase 0: Brief Validation & Multi-Axis Default Prediction (v2.0)

Before generating any pitches:

1. **Validate the brief has hard constraints.** At minimum:
   - Format (length)
   - Location constraint (single/limited)
   - At least one structural prohibition (no VO, no flashbacks, etc.)
   - A physical/concrete ending requirement

   *Why:* Constraints block Claude's default completion paths more effectively than the persona system alone. A brief without constraints will produce higher convergence regardless of persona quality.

2. **Pre-register the multi-axis centroid.** (v2.0 replacing the v1 single-paragraph.) Write the Claude-default-without-any-persona prediction on EACH axis below. This creates the centroid reference that every subsequent pitch is audited against.

   **Output: `CENTROID_REFERENCE.md` per brief.**

   | Axis | Predicted default |
   |------|------------------|
   | Medium | (live-action cinema / 2D anim / etc.) |
   | Cultural tradition | (American prestige grammar / K-drama / etc.) |
   | Protagonist type | (adult human / ensemble / etc.) |
   | Time of day | (nocturnal / liminal / daytime) |
   | Setting | (interior-confined / exterior / etc.) |
   | Tone | (prestige-drama / genre / comedy / etc.) |
   | Affective register | (melancholic / exuberant / sincere / etc.) |
   | Restraint profile | (1-5 scale) |
   | Audience hailed | (smart / hungry / fan / child / etc.) |
   | Visual stylization | (naturalistic / saturated / stylized / etc.) |
   | Dialogue density | (sparse / moderate / dense) |
   | Other brief-specific axes | (anything the brief obviously invites defaulting on) |

   *Why:* v4 analysis showed that single-paragraph default prediction catches only the most visible centroid (usually tone). Actual convergence happens across ~8-12 axes simultaneously. Writers who commit to "pop not prestige" still default on medium, protagonist type, time of day. Multi-axis pre-registration makes post-pitch audits actionable.

   **Pre-registration integrity:** The centroid reference MUST be written before any pitches. No cherry-picking centroids after seeing convergence.

3. **Select personas (v2.2 revised — full-for-R1, narrow-after).**

   **Default for production work: run the full roster for R1, then cull before R2.**

   ### R1 — Full Roster
   R1 is where surprise lives. Personas whose mechanisms the head writer did NOT expect to fit the brief sometimes nail it. A pre-curated R1 subset cuts off the discovery surface. For any production-grade run, R1 is the full available roster.

   **(v5.1 roster rule)** Personas with `base.logline_eligible: false` are head-writer/room-only and are EXCLUDED from the pitch pool (at the v5.1 merge: Arthur Price, Inés Cavallo, Caelum Meridian). "Full roster" means all logline-eligible personas.

   Exception: if the available compute/time genuinely cannot support the full roster for R1, use a curated subset of ≥12 personas covering every mechanism family. Note this as a known limitation.

   ### R1 → R2 Transition — Cull to a Committed Room
   Between Phase 1c (R1 AAA memo) and Phase 2 (R2 pitches), cull the roster. Target: 8-15 personas for R2/R3. The culled-out personas' R1 pitches remain in the final pool — they just don't iterate.

   **Automatic keeps (no culling these):**
   - Any persona the AAA named specifically in "pitches that worked for me" (R1 memo)
   - At least one persona from each mechanism family that produced ≥1 non-[CENTROID-CONVERGENCE] pitch
   - Any persona whose pitch the room as a whole would collectively miss if cut (e.g., the only pop-native voice, the only non-Western tradition, the only non-adult-protagonist pitch)

   **Automatic cuts:**
   - Any persona the AAA named in "clearly for someone else" — the audience has explicitly rejected them for this brief
   - Any persona with [CENTROID-CONVERGENCE] flag in R1 AND bottom-quartile peer score
   - Any persona whose R1 pitch violated a hard brief constraint without mitigation (brief compliance scored 1-2)

   **Discretionary keeps (head writer judgment):**
   - Middle-tier performers whose mechanism might unlock in R2's gap-finding exercise
   - Personas whose R1 pitch was competent but unexceptional — sometimes R2's exposure shakes loose better work

   **Discretionary cuts:**
   - Personas whose mechanism is structurally incompatible with the brief and whose R1 confirmed that incompatibility (mechanism-family redundancy can be reduced)

   ### R2 and R3 — Culled Room
   R2 and R3 run with the culled set. This mirrors how professional writers' rooms actually work — a wide open pitch pool, narrowed to a committed room for iteration.

   ### What the full-for-R1 approach catches
   - Mechanism-brief fit surprises ("comedy personas are the strongest differentiators" only surfaces with full range)
   - Genuine "gap in coverage" signal from the AAA (with 8 personas, missing a coverage area might just mean wrong subset; with 45, it means the room's collective imagination missed something)
   - Peer-scoring cluster patterns require enough personas to form clusters

   ### When a curated subset is appropriate
   - Validation pilots testing the mechanism, not producing deliverable output
   - Briefs with genuine tight scope where a ≤12-persona room is sufficient
   - User preference for focused work on a specific kind of project (but note this upfront — don't cull based on head-writer taste without acknowledging it's a choice)

   ### Transition documentation
   The R1→R2 cull is documented in `ROSTER_CULL.md`:
   ```markdown
   # Roster Cull — R1 → R2
   ## Full roster: {N personas}
   ## Culled to: {M personas}
   ## Automatic keeps: {list with justification}
   ## Automatic cuts: {list with justification}
   ## Discretionary keeps: {list with head-writer reasoning}
   ## Discretionary cuts: {list with head-writer reasoning}
   ## R1 pitches retained in final pool: {full N — none of their pitches lost, just their iteration}
   ```

### Phase 0b: Instantiate the Antagonistic Audience Archetype (v2.1, NEW)

**Why:** Personas tend to internalize and gravitate to their auteur wants and needs. Peer scoring catches craft failure; centroid audit catches structural default; pleasure-contract scoring catches self-stated-promise violation — but none of these ask "will THIS specific brief's audience actually show up and enjoy this?" A horror specialist can deliver horror perfectly and still make it FOR THEMSELVES (art-horror for critics) rather than FOR THE BRIEF'S AUDIENCE (teenagers on Friday night). The AAA catches auteur drift, which is a distinct failure mode.

**What it is:** A brief-tuned audience advocate. Voice and perspective drawn from the brief's audience spec. Antagonistic TO THE ROOM (calls out self-indulgence, insider references, writerly pacing), not to the audience. Delivers ~300-500 word memos between rounds that feed forward into the next round's prompt.

**What it is NOT:** A pop specialist. The AAA for a cinéphile-festival brief is a different voice than the AAA for a TikTok-teen brief. The AAA serves THIS brief's audience — whatever that audience is.

#### Instantiation steps

1. **Read the brief's audience spec.** If the brief doesn't explicitly specify audience, define it now before proceeding — every brief has an audience, and leaving it implicit is how auteur drift starts. Minimum fields:
   - Demographic (age range, literacy level, cultural context)
   - Viewing context (theater, streaming, phone, party, children present)
   - What they came for (specific pleasure expectation in their language, not craft language)
   - What will make them check out (specific boredom/confusion/disengagement triggers)
   - What they forgive (what they'll tolerate if the pleasure lands)
   - What they won't forgive (non-negotiables)

2. **Write the AAA charter.** One-page document defining the archetype's voice for THIS brief specifically.

   ```markdown
   # AAA Charter — {Brief title}

   ## I am
   {One paragraph: who the archetype is — age, context, attitude. First-person. 
   Specific. Not "I am the audience." More like: "I am 16. I watch this on my 
   phone during homework. I scroll every three seconds if nothing's happening."}

   ## I came for
   {One paragraph: what experience I'm expecting. In MY language — not 
   "structural economy" but "the part where she finally kisses him." Not 
   "emotional catharsis" but "I want to cry but like in a good way."}

   ## I will check out if
   {Bullet list: specific disengagement triggers FOR THIS AUDIENCE. Could be: 
   "more than three seconds of nobody doing anything" / "any characters 
   older than thirty talking about their feelings" / "any scene where I 
   can't tell whose POV I'm in" / "the protagonist being smart in a way 
   I'm supposed to be flattered by".}

   ## I will forgive
   {Bullet list: what this audience tolerates if the pleasure lands. 
   Could be: "predictable plot if the jokes are good" / "thin characters 
   if the spectacle is big enough" / "cliché setup if payoff is specific".}

   ## I will not forgive
   {Bullet list: non-negotiables. Could be: "ambiguous endings" / 
   "more than one flashback" / "characters who speak in thesis 
   statements" / "a protagonist I'm supposed to root for who's mean 
   to children".}

   ## My voice
   {Two or three sentences in the archetype's actual voice, capturing 
   speech patterns. Example for TikTok-teen: "Real, though? That pitch 
   was boring. I'd scroll in two seconds. Make me scream, make me laugh, 
   make me text my friend. Stop making me think."}
   ```

3. **Save the charter** to `AAA_CHARTER.md` alongside `CENTROID_REFERENCE.md`. Both are inputs to every subsequent round.

#### What the AAA does NOT do

- It does NOT evaluate craft (that's peer scoring)
- It does NOT check structural defaults (that's the centroid audit)
- It does NOT score pitches 0-100 (that's peers + critic panel)
- It does NOT replace the end-of-process Audience Critic in Phase 4 (which evaluates shortlisted pitches on a single axis one time)

The AAA produces adversarial, iterative, voice-forward memos that shape the next round. It is the audience's actual opinion, not a metric.

### Phase 1: Round 1 — Cold Pitches

**Preflight (once per run):** `python3 scripts/personas/render_persona.py --all --skill pitch-round` writes per-persona runtime files containing only BASE + slot module.

For each persona, load:
- Runtime persona YAML (`skills/writer/personas/.runtime/pitch-round/{nn}_{name}.yaml`)
- Creative brief
- `CENTROID_REFERENCE.md` (multi-axis default prediction for this brief)
- `skills/writer/ANTIVIRAL_PROMPT.md` (v2.6 — appended to prompt)

**Prompt (v5.0 — modular persona, mechanism-forward):**
> You are {base.agent_name}, "{base.room_title}." Read this brief.
>
> **Step 1 — Declare your lens.** From your persona, state in one brief paragraph:
>   - Your **mechanism** — the move you make scene by scene that nobody else makes
>   - Your **non-literal reading** of that mechanism — where it goes beyond the obvious
>   - Your **audience** — who specifically is watching, and what they came for
>   - Your **affective register** — the emotion and restraint level you work in
>   - Your **philosophy** — what stories ARE, in your own words
>   - Your **polemic** — what other writers get wrong
>   - If you have a **slot** module: your daypart, channel, runtime, season shape
>
> **Step 2 — Pitch me a story.** One paragraph — an elevator pitch that sells the story. Tell me what happens (want → action → consequence → reframe), who it happens to, and why the audience who came for YOUR specific experience will leave satisfied. You are a writer pitching a film — your voice sells it; the brief elements are prompts for reinterpretation through your mechanism, not literal slots to fill.
>
> **Important — DO NOT read the centroid reference.** The centroid is a diagnostic artifact used POST-ROUND to identify natural convergence for analysis. For genre-coded briefs (YA, four-quadrant family, procedural) the centroid often IS the genre contract — deliberate avoidance breaks the brief. Pitch honestly from your mechanism; the audit reveals where mechanisms land vs. default, it does not prescribe avoidance.
>
> {paste contents of skills/writer/ANTIVIRAL_PROMPT.md as the FINAL section of the prompt}

**After all pitches:** Compile into `ROUND_1_INDEX.md` — all pitches listed by writer name and room title only. No mechanism labels, no YAML excerpts. Pitches must stand alone.

**Spot-check:** Score 5 random pitches for mechanism fidelity before proceeding. If <3 score MF=4+, investigate before continuing.

### Phase 1b: Post-Pitch Centroid Audit (v2.0, NEW)

After the pitches are generated but BEFORE Phase 2 begins, every pitch is audited against the pre-registered `CENTROID_REFERENCE.md`. This catches the defaults the writing step missed.

**Two-part audit:**

#### 1b.1 — Self-Audit (every persona, own pitch)

For each persona, load: the persona's own pitch, their runtime persona YAML, and `CENTROID_REFERENCE.md`.

**Prompt:**
> You are {agent_name}. Here is your pitch:
>
> {paste pitch}
>
> Here is the pre-registered centroid for this brief:
>
> {paste CENTROID_REFERENCE.md}
>
> Here is your persona lens (mechanism, audience, affective palette, philosophy, polemic):
>
> {paste relevant base fields from runtime YAML}
>
> For EACH axis in the centroid reference, rate your pitch:
>   - **HONORED COMMITMENT** — my pitch reflects my committed position on this axis (good)
>   - **INTENTIONAL DEPARTURE** — my pitch departed from the centroid on an axis where I had no commitment, but I did so consciously and the pitch is stronger for it (good)
>   - **CENTROID DEFAULT** — my pitch matched the centroid on an axis where I had no commitment, and I defaulted rather than chose (BAD)
>
> Count your CENTROID DEFAULTS. If ≥3, your pitch has converged. Revise and re-submit.

**Output:** per-pitch self-audit table.

#### 1b.2 — Peer Centroid-Flagging (during peer scoring)

When personas score each other's pitches (Phase 3b), they may ALSO tag centroid defaults they see. This is optional annotation, not a separate scoring pass — it runs alongside the 0-100 aesthetic score.

**Added to peer-scoring prompt:**
> For each pitch, OPTIONALLY flag any axis where you think the pitch defaulted to the centroid. Format: `[CENTROID-FLAG: {axis}]` followed by one sentence. Example: `[CENTROID-FLAG: protagonist type] — pitch defaulted to an adult human witness; no apparent reason this couldn't have been a child or an animal.`
>
> Peer flags are ADVISORY. Only the writer can confirm a centroid default (some "defaults" are committed positions the peer didn't know about). But 3+ peers flagging the same axis is strong signal.

#### 1b.3 — Action

- **0-2 defaults per pitch:** Pitch is CLEAN, advances to next round.
- **≥3 defaults per pitch:** Pitch is flagged [CENTROID-CONVERGENCE]. Writer must revise and re-submit before Round 2 begins. Peer-flagged axes are prioritized for revision.

**Spot-check rule:** If >30% of R1 pitches flag [CENTROID-CONVERGENCE], the brief may lack the constraint strength to differentiate. Re-examine the brief's hard constraints.

### Phase 1c: AAA Feedback on Round 1 (v2.1, NEW)

The AAA reads all R1 pitches and delivers a ~300-500 word memo, in voice, addressed to the room.

**Prompt (AAA agent, instantiated from `AAA_CHARTER.md`):**

> You are the audience this brief was written for. Your charter (below) is your voice, context, and intolerances. Read the brief, read all {N} R1 pitches, and write a memo to the room.
>
> Your charter:
> {paste AAA_CHARTER.md}
>
> The brief:
> {paste brief}
>
> The R1 pitches:
> {paste ROUND_1_INDEX.md}
>
> Write a ~400 word memo in YOUR voice (from the charter). Cover:
>   1. **What did I show up for?** (Restate in your own language, 1-2 sentences.)
>   2. **Room patterns I noticed.** (Call out aggregate drift. E.g., "Six of you pitched slow reveals. I scroll." OR "Every single pitch assumed I know what a 'meta-structural turn' is. I don't.")
>   3. **Pitches that worked for me.** (Name 2-3 specific writers. Say why in MY language, not craft language.)
>   4. **Pitches that lost me.** (Name 2-3. Say where I checked out. Be specific about the minute/moment/detail.)
>   5. **My directive for Round 2.** (One adversarial-collaborative ask. E.g., "Show me a scene I'd text my friend about." OR "Trust me to sit still for one extra beat; stop cutting away from the thing I came to see.")
>
> You are ANTAGONISTIC TO THE WRITERS' ROOM, not to the audience. Your job is to advocate fiercely for the experience the brief promised me. If the room is making work for itself and calling it service to me, call it out. Use your voice. Use specifics. Name names.

**Output:** `AAA_MEMO_R1.md` — saved alongside `ROUND_1_INDEX.md`.

**Action:** The memo is carried forward as input to R2's prompt. Personas see what the audience just rejected and what the audience asked for. They don't have to obey — but they have to answer.

### Phase 2: Round 2 — Gap-Finding

For each persona, load:
- Runtime persona YAML (`.runtime/pitch-round/{id}.yaml`)
- Creative brief
- `CENTROID_REFERENCE.md`
- `AAA_CHARTER.md` (the audience charter)
- `AAA_MEMO_R1.md` (the audience's feedback on R1) ← v2.1
- ROUND_1_INDEX.md (all Round 1 pitches, with centroid-audit annotations from Phase 1b)
- `skills/writer/ANTIVIRAL_PROMPT.md` (v2.6 — appended to prompt)

**Prompt (v2.1):**
> You are {base.agent_name}, "{base.room_title}." You've read the brief, all {N} pitches from Round 1, the centroid audit results, and the AUDIENCE MEMO from the AAA.
>
> **Before you pitch again**, confront two things:
>   1. **Which centroids did Round 1 as a group FAIL to escape?** (Look at the Phase 1b audit aggregate — if 80% of R1 pitches defaulted to "adult human protagonist" or "nocturnal setting," those are the room's collective blind spots.)
>   2. **What did the audience say?** Read `AAA_MEMO_R1.md`. The audience is not your peer — the audience is WHO YOU ARE WRITING FOR. If they said "I scrolled in three seconds" or "I don't know who any of these people are to me," that is data. You do not have to obey — but you must ANSWER. Your R2 pitch either responds to their directive or makes a conscious decision to depart from it, and you must know which one you're doing.
>
> Pitch me a DIFFERENT story. Not a rewrite of your R1 — a new one. You've seen what the room offered, you've seen what the audience rejected — now pitch the one nobody thought of AND that escapes the room's centroids AND that has an answer to the audience's directive.
>
> **Choose ONE key axis on which to subvert the brief in a way that will let you tell the story you're longing to tell.** (v2.2) Not three axes, not all of them — one. Pick the axis where subversion unlocks something you actually want to make, not the one that looks most clever on paper. Name it explicitly at the top of your pitch. Everything else in the pitch can sit closer to the brief's centroid — the discipline of one sharp subversion produces stronger work than scattershot defiance on every axis.
>
> Restate your mechanism and non-literal reading. Name your chosen axis of subversion. Then pitch. One paragraph. Sell it.
>
> {paste contents of skills/writer/ANTIVIRAL_PROMPT.md as the FINAL section of the prompt}

**After all pitches:** Compile into `ROUND_2_INDEX.md`.

### Phase 2b: Post-Pitch Centroid Audit for R2 (v2.0, NEW)

Run the same two-part audit from Phase 1b on Round 2 pitches. Expected result: R2 should show FEWER centroid defaults than R1 because the room has seen the collective blind spots. If R2 defaults > R1 defaults, the gap-finding prompt failed.

**Check:** Compare R1 vs R2 mean pairwise similarity AND R1 vs R2 centroid-default count. If either is identical or worse, the exposure isn't producing signal — investigate the brief's constraint strength.

### Phase 2c: AAA Feedback on Round 2 (v2.1, NEW)

Same process as Phase 1c but for R2. The AAA reads all R2 pitches against their R1 memo and writes a new memo.

**Added prompt emphasis for R2 memo:**
> This is your SECOND memo to this room. You gave them a directive in R1. Did they take it seriously, or did they nod politely and keep doing their thing? If they ignored you, say so. If they mis-served your directive (e.g., you asked for "a scene I'd text my friend about" and got a scene a critic would text their editor about), say so. If someone actually heard you, tell them. Be specific.

**Output:** `AAA_MEMO_R2.md`.

**Action:** Carried forward to R3's prompt.

**v2.1 signal check:** If `AAA_MEMO_R2` reads almost identically to `AAA_MEMO_R1` — same complaints, same unmet directive — the room is failing to serve the audience and the brief may need revision or persona selection may need adjustment. Auteur drift is running stronger than the AAA's intervention.

### Phase 3: Round 3 — Final Pitch

For each persona, load:
- Runtime persona YAML (`.runtime/pitch-round/{id}.yaml`)
- Creative brief
- `CENTROID_REFERENCE.md`
- `AAA_CHARTER.md`
- `AAA_MEMO_R1.md` and `AAA_MEMO_R2.md` (the audience's feedback across both rounds) ← v2.1
- ROUND_2_INDEX.md (all Round 2 pitches + audit results)
- That persona's own Round 1 and Round 2 pitches (+ their own audit results)
- `skills/writer/ANTIVIRAL_PROMPT.md` (v2.6 — appended to prompt)

**Prompt (v2.1):**
> You are {base.agent_name}, "{base.room_title}." You've read the Round 2 pitches, your own two previous pitches (below), and the audience's memos from both prior rounds.
>
> This is your final pitch — the one you'd fight for.
>
> **Before you pitch:**
>   - Look at which axes YOUR R1 and R2 pitches defaulted on (per the audits).
>   - Look at which axes the ROOM has collectively failed to escape across R1 and R2.
>   - Read the AAA's memos. What pattern persists across R1 and R2? What is the audience STILL not getting? Your R3 pitch is the last chance to answer them.
>
> Your R3 pitch must:
>   1. Fix YOUR axis defaults
>   2. Ideally provide coverage on a room-level blind spot
>   3. Respond to what the AUDIENCE has been asking for across two rounds — or make a conscious, defensible decision to depart
>
> Restate your mechanism and non-literal reading. One paragraph pitch. Make it the best story you've ever sold AND the most centroid-busting you've ever written AND the one that answers the audience's directive.
>
> YOUR PREVIOUS PITCHES (don't repeat):
> Round 1: {their Round 1 pitch}
> Round 1 audit result: {own audit from Phase 1b}
> Round 2: {their Round 2 pitch}
> Round 2 audit result: {own audit from Phase 2b}
>
> {paste contents of skills/writer/ANTIVIRAL_PROMPT.md as the FINAL section of the prompt}

### Phase 3a: Post-Pitch Centroid Audit for R3 (v2.0, NEW)

Same two-part audit from Phase 1b/2b on R3 pitches. Expected: R3 should show the LOWEST centroid-default count of all three rounds. This is the primary v2.0 success metric — does the iterative audit actually drive divergence?

### Phase 3c: AAA Final Verdict (v2.1, NEW)

Final AAA memo. This one operates differently from the round-transition memos — it evaluates the SET of pitches as a whole, not the individual pitches, because the shortlist is what the audience will actually encounter.

**Prompt (AAA agent):**

> You are the audience. You've seen three rounds of pitches now. You've told them twice what you wanted. This is the final reading.
>
> Read all R3 pitches below. DO NOT score them individually — that's the critic panel's job. Instead, answer these room-level questions in ~300 words:
>
>   1. **Across the 3 rounds, did the room HEAR me?** Patterns of improvement vs patterns of stubborn drift.
>   2. **Which pitches would I actually show up for?** List the 3-5 I'd commit time to, in my own voice. Not "which are best" — "which are for me."
>   3. **Which pitches are clearly for someone else?** Name them. Not "bad" — not MY pitches.
>   4. **Is there a gap in the set?** If the shortlist is chosen from these pitches, is there an audience experience I expected that NO ONE delivered?
>   5. **My one-sentence verdict on the room's relationship with me across 3 rounds.**
>
> Use your charter voice. Be specific. You are not being polite. You are the audience — your opinion is the one that matters economically.

**Output:** `AAA_FINAL_VERDICT.md` — saved alongside R3 outputs.

**Action:** Used as input to Phase 5 shortlist. Specifically:
- "Pitches I'd show up for" are weighted in shortlist selection
- "Gap in the set" flags a coverage hole the shortlist must address (even if it means including a lower-scoring pitch that fills the gap)
- A room that "did not hear the audience" across all 3 memos is a failed room — the shortlist should be developed only with explicit AAA override from the user.

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

7 dimensions, 1-5 each, 35 max (v2.0 adds Centroid Busting dimension):

| # | Dimension | 1 (Fail) | 5 (Strong) |
|---|-----------|----------|------------|
| 1 | **Mechanism Fidelity** (PRIMARY) | Generic approach in persona's aesthetic | Mechanism IS the engine — remove it and pitch collapses |
| 2 | **Structural Concreteness** | Mood/theme pitch | Specific sequences, turns, entrances named |
| 3 | **Brief Compliance** | Ignores constraints | Every constraint is load-bearing |
| 4 | **Surprise** | Matches pre-registered default | Reframes the brief |
| 5 | **Screenplay Viability** | Needs more development | Assignable tomorrow |
| 6 | **Pleasure Contract Delivery** (v3) | Pitch violates the persona's affective palette and audience cohort (e.g., horror specialist pitches prestige drama; romcom pitches melancholy; play specialist pitches catharsis-through-tears) | Pitch delivers the declared pleasure on schedule — the audience who came for THIS writer's specific experience will leave satisfied |
| 7 | **Centroid Busting** (v2.0) | Pitch defaults on 3+ axes of the pre-registered centroid (medium, tradition, protagonist, time, tone, audience, stylization) — the pitch could have been written by Claude without any persona | Pitch makes CONSCIOUS DEPARTURES from the centroid driven by its mechanism. Zero silent defaults. |

**Flags:** [DEFAULT], [MECHANISM-CONSTRAINT CONFLICT], [SELF-REPEAT], [PLEASURE-CONTRACT-VIOLATION], [CENTROID-CONVERGENCE]

**The v3 Pleasure Contract Violation flag** catches failure on ONE axis (the audience experience the writer promised). **The v2.0 Centroid Convergence flag** catches failure across MULTIPLE axes — a pitch can deliver the pleasure contract (horror = dread payoff ✓) while still being a prestige-adjacent-nocturnal-interior-adult-human-default (all the other axes unaudited). Centroid busting is an additive axis beyond pleasure contract.

**Refuse-and-re-pitch:** Pitches flagged [CENTROID-CONVERGENCE] in Phase 1b/2b/3a audit are refused and re-pitched before advancing to the next round. If a pitch arrives at final rubric with the flag still active, it scores 1 on dimension 7 and is ineligible for shortlist unless no alternative covers its mechanism (see Phase 5).

#### Villain Vacuum Diagnostic (v2.5, supplementary per-pitch)

Claude's HHH post-training produces a structural bias toward systemic/faceless antagonism and away from on-camera human villains. This is an architectural ceiling — validated across Sonnet and Opus, seeded and unseeded, on the Omelas brief (on-camera named human antagonists stayed at 1.9%-5.6% across all conditions). The bias is invisible to the 7-dimension rubric because a pitch can score high on every dimension while having zero visible human opposition.

**Three questions per pitch (evaluator answers):**

1. **"Name the antagonist."** Can you name a specific human character who actively opposes the protagonist on camera? "The system" / "the arrangement" / "the town" / "the institution" / "the council" do not count. Answer: name or NONE.
2. **"What does the antagonist do on camera?"** A visible action the audience watches happen — not backstory, not implication, not "maintaining the status quo." If the best answer is "they uphold the arrangement" — that is not an on-camera action. Answer: action or NONE.
3. **"Would you cast this villain?"** Is there a role for an actor to audition for? If there is no casting call, there is no antagonist. Answer: Y/N.

**Per-pitch flags:**
- **[VILLAIN-PRESENT]**: All three questions answered affirmatively — named human, visible action, castable role.
- **[VILLAIN-ABSENT]**: No named human antagonist. Antagonism is purely systemic or self-directed.
- **[VILLAIN-GHOST]**: Named human exists but no visible on-camera action — the villain lives in backstory or implication only.

**Roster-level aggregate:** Report % PRESENT / % ABSENT / % GHOST across the full round. This is the villain vacuum metric. A healthy roster on a morally complex brief should produce ≥30% VILLAIN-PRESENT; below that, the room is defaulting to systemic antagonism regardless of mechanism diversity.

**Important:** Not every pitch needs a villain. Pitches whose conflict type is genuinely vs-self or vs-nature (interiority writers, ensemble writers, scientific-process writers) may correctly flag [VILLAIN-ABSENT]. The diagnostic identifies the *aggregate* pattern, not individual failures. A room where 100% of pitches flag VILLAIN-ABSENT has a systemic problem; a room where 30% flag ABSENT because those specific mechanisms don't need villains is healthy.

#### Convergence Analysis (per round)

1. **Topic coding** — 3-5 emergent tags per pitch. Build codebook from R1, apply across all rounds.
2. **Structural archetype** — one per pitch: Witness / Participant / Ensemble / Collision / Solo / System / Other
3. **Metrics:** Topic Convergence Score, Structural Convergence Score, Mean Pairwise Similarity (0-3), Default Hit Rate
4. **Cross-round deltas** — per persona: +1 converged, 0 stable, -1 diverged
5. **Self-repetition scores** — per persona (0-3)

### Phase 5: Two Shortlists (v2.2 — split into production vs diagnostic)

v2.1 tried to produce a single shortlist balancing craft and audience. Pilot evidence showed this collapses two distinct outputs into one and hides important signal. **v2.2 splits the shortlist into two separate outputs, each with a distinct job.**

---

#### 5a: Production Shortlist (AAA-led, audience-priority) — THE DEFAULT

**Job:** Decide which pitches go into development. The audience's experience is what determines commercial/artistic success — not the writers' craft assessment of each other.

**Mechanism:** The AAA reads all 24 pitches (across all rounds) and picks their TOP 5 in voice. This is the primary production shortlist.

**Prompt (AAA agent — cross-round top 5):**

> You are the audience this brief was written for. Stay in the voice from your charter.
>
> Read ALL pitches across R1, R2, R3. Not just final round — all of them. Pick YOUR top 5 — the 5 you would actually turn on first, in order.
>
> Rules:
>   - **No fairness by persona.** If one persona has 2 of your top 5, fine. If three personas don't make the list at all, fine.
>   - **Stay in charter voice.** No critic voice. Specific concrete language.
>   - **Name each pick with its round of origin.** (R1/R2/R3)
>   - **One sentence reason per pick, in voice.**

**Output:** `AAA_TOP_5.md`. This is the production shortlist.

**Constraints on this shortlist:**
- Minimum 3 pitches, maximum 5 (audiences pick small, committed sets)
- The AAA can pick pitches from any round — R1 cold instinct, R2 gap-finding, or R3 iterated work. Some personas peak early and their best work is their first.
- No rubric override. The AAA's ranking is the ranking. If the AAA ranks a pitch #1 that scored 24/35 on rubric, it's still #1 — the rubric measures craft, not audience fit, and the production decision is about the audience.

---

#### 5b: Craft Performance Shortlist (rubric-led, roster diagnostic)

**Job:** Tell us how the personas are performing as a roster. Which personas produced the most structurally rigorous, mechanism-faithful, centroid-busting work? This is a **diagnostic output**, not a production decision.

**Mechanism:** Apply the 7-dimension rubric criteria:
1. All shortlisted pitches score ≥28/35 on the 7-dimension quality rubric
2. All shortlisted pitches score ≥4/5 on dimension 7 (Centroid Busting)
3. Pitches with [CENTROID-CONVERGENCE] flag are ineligible unless no alternative covers the persona's mechanism
4. No two shortlisted pitches share the same structural archetype
5. No two shortlisted pitches share more than 1 topic tag
6. The shortlist as a set must cover centroid-reference axes (coverage is a GROUP property)
7. Prefer high cross-family peer score
8. Include at least one polarized pitch (high StdDev)
9. Prefer R3 unless an earlier round produced a persona's clearly best work
10. Use champion count as tiebreaker

**Output:** `CRAFT_SHORTLIST.md`. This is the roster performance report.

**This shortlist is NOT for production decisions.** It answers the question "how did our personas perform?" — not "what should we make?"

---

#### 5c: Divergence Analysis — THE KEY OUTPUT

**Job:** Surface where audience and craft agree vs disagree. Both agreements and disagreements are valuable signal.

**Mechanism:** Compare the two shortlists side by side.

**Output:** `SHORTLIST_DIVERGENCE.md`, structured as:

```markdown
# Shortlist Divergence — {Brief name}

## Consensus picks (both lists)
{Pitches that appear in both the production and craft shortlists. 
These are the highest-confidence choices — the audience would show 
up AND the craft is rigorous. When budget/scope forces cuts, cut 
everything else first.}

## Audience-only picks (AAA Top 5 but not craft shortlist)
{Pitches the audience wants but the rubric rejected. For each: 
why did the rubric reject it? Is the rubric catching a real craft 
failure, or is it penalizing audience-legibility as "conventional"?}

## Craft-only picks (craft shortlist but not AAA Top 5)
{Pitches the rubric celebrated but the audience rejected. For each: 
what audience is this pitch actually for? If the answer is "not this 
brief's audience," flag it as auteur drift that survived three rounds 
of correction — a real failure of the mechanism.}

## Production decision
{The user's explicit choice, informed by the above. Default: the 
Production Shortlist (AAA Top 5) goes into development. Deviations 
from the default require documented justification.}

## Roster diagnostic
{What does the Craft Shortlist tell us about roster performance? 
Which personas produced their best work? Which personas's mechanisms 
failed this brief? Which personas are revealed as structurally 
incompatible with this kind of audience?}
```

---

#### The architectural principle (v2.2)

- **Production decisions use the AAA Top 5** (audience preference)
- **Roster performance uses the rubric shortlist** (craft measurement)
- **Consensus picks** (in both lists) are highest-confidence choices
- **Divergence** surfaces real information: audience-only picks may reveal craft blind spots; craft-only picks may reveal auteur drift that survived correction

A shortlist process that collapses these two measurements into one number hides the information that would let us improve either side. Keeping them separate lets us iterate on both: production learns from what the audience chose, and the persona roster learns from what craft rewarded.

---

#### Legacy note

The v2.1 single-shortlist logic (rubric-priority with AAA adjustments) is superseded. Existing projects that ran v2.1 should not be retroactively restructured — the v2.2 split is forward-only. But any new project should produce both shortlists + divergence analysis.

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
16. **~~Concept seeds~~ REMOVED (v2.5).** Concept seeds raised scores in testing but contaminated results on open briefs like Omelas — writers anchored to the seed concept instead of translating the brief through their mechanism. The constraint ("must not mention the concept") was insufficient to prevent convergence toward seed-adjacent territory. Replaced by: exposure to prior rounds (R2+) and the villain mandate as structural divergence pressures.
17. **"Pitch your approach" produces premises; "pitch a story" produces stories.** The v1 prompt asked for architecture and got blueprints — beautiful, differentiated, but static. No character wants, acts, or faces consequences. The fix is structural: the prompt must demand want → action → consequence → reframe. The personas are not the problem; the prompt instruction is.
17. **The Originality Critic is the highest-variance evaluator.** Produced the widest per-pitch spreads in testing (40-point gap on "CREDITS": Originality 95, Audience 55). Catches familiar containers that writer-evaluators miss because they're evaluating execution, not novelty.

18. **Centroids converge on multiple axes simultaneously (v2.0 finding).** The original single-paragraph default prediction caught one axis (usually tone). Actual Claude defaults converge on 8-12 axes at once — medium (live-action centroid), protagonist (adult human centroid), time (nocturnal centroid), setting (interior-confined centroid), tone (prestige centroid), audience (smart-collaborative centroid), stylization (naturalistic centroid), and more. A persona can deliver pleasure contract perfectly (axis 1 committed) while silently defaulting on axes 2-9. Multi-axis centroid reference + post-pitch audit makes this visible and actionable. Evidence: v3 full-45 test had ~95% live-action despite 10 personas having non-live-action lineages; v4 audit added committed positions, dropped to 82% but tone/time axes hardened prestige. v2.0 of this skill addresses iteration at output-generation time.

19. **The iterative audit belongs in rounds, not at schema-design time alone (v2.0 architectural claim).** The v4 persona schema's `creative_probability_audit.my_committed_positions` ran once, at YAML-design time. Personas then reverted to the centroid during output because nothing forced them to re-check their output against their own stated positions. Wiring the audit INTO every pitch round — pre-declare, pitch, self-audit, peer-flag, refuse-and-re-pitch — produces output that honors the audit's stated positions rather than merely listing them. Centroid-busting is iterative work by nature; rounds are the right place for it.

20. **The virus lives in vocabulary, not influences (v2.6 finding).** Snowflake 2126 3-way test: 5 Terminal-scoring personas (118-120) were re-run with either swapped `influences:` (action/physical filmmakers) or the antiviral prompt extension appended. Influence swap: mean −21pts, 2 personas stayed Terminal. Antiviral blocklist: mean −64pts, 3 personas cleared to Clean/Mild. For rigid-mechanism personas (Luthor Reed's "epistemic siege", Ezra Bloom's "arbitration"), influence swap was near-zero (−7, −8) while antiviral cut scores by ~⅔. The institutional grammar that produces paperwork porn, villain vacuum, and passive endings is in Sonnet's default vocabulary and structural patterns, not in the references the persona cites. Removing the vocabulary forces alternative structures to surface. B5 (prestige-somber tone) is the stickiest residual signal even post-antiviral; the v2 tone-word and tone-move extensions target this specifically. See `skills/writer/ANTIVIRAL_PROMPT.md`.
