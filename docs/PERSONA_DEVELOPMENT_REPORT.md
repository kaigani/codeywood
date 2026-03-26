# Persona Development for Creative Writing with LLMs
## A Study in Three Tests

**System**: Codeywood AI Video Story Generation
**Date**: March 2026
**Models tested**: Claude Opus 4.6, Claude Sonnet 4.6, external models
**Persona count**: 25 writer personas (v3 schema) + deprecated v2 personas

---

## Executive Summary

Over three structured tests, we developed and refined a system of 25 writer personas for screenplay generation with large language models. The study produced four major findings:

1. **Persona design is constraint design.** The most effective personas are defined by what they reject (anti-canons) and how they build (craft method), not by comprehensive character descriptions. Three sentences of creative tension can outperform 80 fields of personality data.

2. **LLMs have architectural defaults that personas alone don't override.** Scene-level persona fields (voice, anti-canon, craft method) change HOW scenes are written but not WHAT SHAPE the story takes. A new field — `story_world` — was required to break structural convergence across personas.

3. **The writers room process categorically improves on solo writes.** Multi-persona collaboration produces richer screenplays than any individual persona, because the friction between incompatible mechanisms generates scenes no single persona could write.

4. **Personas reliably beat the bare model.** Across all three tests, every persona format except one (Audience Contract) outperformed the no-persona control. The persona system is not decorative — it materially changes creative output.

---

## Test 1: The Omelas Test — What Makes a Persona Work?

**Brief**: Adapt Ursula K. Le Guin's "The Ones Who Walk Away from Omelas" as a short film.
**Design**: 12 persona format variations + 1 no-persona control, evaluated by 3 independent reviewers.

### Purpose

Before building 25 personas, we needed to know which *components* of a persona actually drive creative differentiation. We isolated 12 format types — from a single dialogue sample to a full 80-field schema — and tested each against the same brief.

### Key Findings

**The Format Tier List:**

| Tier | Formats | Why They Work |
|------|---------|---------------|
| **1: Design into every room** | Anti-Canon, Craft Method, Dialogue Sample | Force novel choices by blocking defaults, providing process, or giving integrated voice |
| **2: Strong specialization** | Constraints Only, Psychology Only, Tension Pair | Scene-level craft, emotional grounding, minimal-viable originality |
| **3: Useful but not essential** | Ontology, Taste, Room Behavior, Full Schema | Add texture without changing structure |
| **4: Below control** | One Scene, Audience Contract | Output-focused formats don't give the model a way to make different choices |

**The meta-finding**: All three evaluators converged on the same principle:
- "The formats that work give the model *generative pressure* — a constraint, a tension, a voice."
- "A persona format is only valuable if it can push the model into a different *adaptation thesis*, not merely a different register."
- "Stop prompting for personality and start prompting for friction."

**The surprise**: A 3-sentence Tension Pair (score: 28/30) outperformed the full 80-field schema (score: 27/30). Comprehensive ≠ effective. The model has enough general capability; it needs direction, not saturation.

### Design Implications

This test produced the **v3 persona architecture**: ~80-100 lines per persona, built around voice_sample + anti_canon + craft_method + constraints + creative_tension + psychology. This replaced the v2 architecture (~200-700 lines with 80+ fields).

---

## Interlude: The Persona Roster — Mechanisms Over Moods

Between tests 1 and 2, we built 25 personas using the v3 architecture and tested them across 3 briefs (animated anthology, YA sci-fi, Scooby-Doo parody) × 25 voices = 75 outputs.

### Core Finding: Mechanisms > Moods

The strongest personas are derived from **nameable mechanisms**, not moods or genres.

- **Mechanism** = a specific structural trick in one sentence. E.g., "escalating logical chains that arrive at absurdity" (Luckfield), "the competent invisible person in someone else's story" (Jessup), "charm as simultaneous weapon and self-destruction" (Lowell).
- **Mood** = an atmospheric orientation. E.g., "visceral maximalism," "radical ambiguity."

Mechanisms produce hard constraints (anti-canons almost write themselves). Moods produce soft preferences (anti-canons feel forced or generic). Mechanisms are infinite; moods converge.

**Validation**: When two personas with mood-based definitions were redefined around mechanisms, their scores jumped dramatically:
- Still (#2): "body horror as feminist weapon" (mood) → "the body mutinies into something unauthorized" (mechanism). Score: 20→28.
- Font (#10): "high-concept thought experiments" (genre) → "the rule is old news, the edge case breaks the adaptation" (mechanism). Score: 21→27.

### Anti-Canon Design Rules

1. **Block the model's most probable completion path.** The anti-canon that produces the biggest quality gain forbids what the LLM would do by default.
2. **Cross-blocking prevents persona collision.** When two personas share adjacent territory, each must explicitly block the other's signature move.
3. **Block specific structural choices, not themes.** "I will never write violence" (thematic, weak). "I will never write a scene where violence solves the dramatic problem" (structural, strong).

### Claude's Default Convergence Patterns

Identified across 75 outputs:

| Default Pattern | Frequency | Nature |
|----------------|-----------|--------|
| Villain reframing ("they're not evil") | 17/25 on YA brief | Tonal |
| Legal/evidentiary crisis | 6/25 on Scooby brief | Structural |
| Empathy with non-consenting subjects | 6/25 | Thematic |
| Enumerated implications ("First... Second...") | 3/25 | Formal |

### Cross-Model Portability

Tested 4 personas across 3 models (Opus, Sonnet, external). **Mechanisms port cleanly.** All personas produced structurally recognizable output regardless of model. What changes is register: Opus drifts toward prestige/A24, Sonnet stays tightest to mechanism, external model is most punchline-driven. The persona files are model-agnostic; model selection is a tonal dial.

### Room Profiles

Separate files loaded only in multi-persona context. A/B test showed three improvements: voice differentiation in dialogue, quality of disagreement (mechanism vs. mechanism, not generic), and synthesis specificity (best ideas emerged from interaction dynamics, not either persona alone).

---

## Test 2: The Sleepwalker Test — Breaking Structural Convergence

**Brief**: A man in his 40s discovers his waking experience is the sleepwalking dream state of his older self. He can't write, can't read clocks. He tries to communicate with his waking self and discovers the truth could unravel spacetime.

**Design**: 3 solo personas + 1 writers room + 1 Sonnet adaptation. Then a second round with a new `story_world` field added.

### The Convergence Problem

Five different personas (Roza Vidal, Sola Jin, Nils Halden, Writers Room, Sonnet) all produced the **same story architecture**:

| Default Element | All 5 Versions |
|----------------|----------------|
| Setting | Dark house, 2-3 AM |
| Population | Solitary protagonist |
| Method | Room-by-room investigation |
| Discovery | Hidden documents in drawers |
| Other characters | Absent (traces only — coffee mug, coat, handwriting) |
| Movement | Inward (deeper into house) |
| Tone | Contemplative with dark comedy |

The personas changed pacing (Roza: 8.05, Sola: 6.35), texture, and individual scene quality — but not the story's physical architecture. An external model writing the same Roza Vidal persona produced a fundamentally different version: morning chaos, Sarah present and yelling about tax forms, the courier honking, discovery through social failure.

### Diagnosis: Scene-Level vs. Architecture-Level

The v3 persona fields operate at the **scene level**:
- `voice_sample` → how the writer sounds
- `anti_canon` → what scenes/moves they refuse
- `craft_method` → how they build individual scenes

Nothing operates at the **architecture level** — who is present, where pressure comes from, what the physical/social space looks like. The LLM fills that gap with its own defaults.

### The Fix: `story_world`

A new field added to the schema with two sub-fields:

```yaml
story_world:
  dramatic_container: >
    3-4 sentences: the physical/social reality this writer builds
    for ANY story. Who is present, where pressure comes from,
    what the space looks like. Derived from the mechanism.
  structural_anti_canon: >
    One sentence: the architectural default this writer will
    NEVER build. Must name the specific pattern that kills
    their mechanism.
```

**Design principle**: The `dramatic_container` is derived from the mechanism the same way `anti_canon` is. Roza's mechanism (colliding timelines at speed) can only be visible in a room full of people on different schedules. Nils's mechanism (partition between incompatible selves) can only be visible when the protagonist crosses between contexts.

### Validation: V1 → V2 Comparison

| Writer | V1 Architecture (no story_world) | V2 Architecture (with story_world) |
|--------|----------------------------------|-------------------------------------|
| **Roza Vidal** | Solitary, dark house, 3 AM | Morning chaos, Sarah in 5/8 scenes, discovery through social failure |
| **Sola Jin** | House as passive setting, solo investigation | House as filter architecture with room-specific physics, basement outside the rules |
| **Nils Halden** | Entire story in one house at night | 7 locations (lecture hall, faculty dining, library, campus, home, office, child's door) |

Pacing scores improved across all three: Roza +0.45, Sola +1.15, Nils +1.45.

**Signal-to-weight ratio**: ~5 lines per persona file. Best ratio of any field in the schema.

### The Deprecated v2 Persona Test

A 724-line deprecated v2 persona (Gwyn Thompson) produced genuine architectural divergence: zero dialogue, the house as sensory antagonist, somatic arc instead of narrative arc. Key v2 fields driving this (audience_model, favorite_antagonists, act_structure_approach) were absent from v3. This confirmed that `story_world` addresses spatial architecture, while v2's richness also captured temporal and modal architecture that v3 lost. However, external reviewers noted the result was "a festival darling, not a Friday-night watch" — architecturally innovative but commercially challenging.

### Pacing Diagnosis

The original complaint — screenplays read like prose — was diagnosed as three specific causes:
1. **Investigation without physical stakes** — character touring rooms, not fighting constraints
2. **Revelations through internal state** — characters thinking/speaking rather than discovering through action
3. **Evenly distributed pacing** — no dramatic shape, just steady competent rhythm

External reviewers diverged on what "good pacing" means: one valued kinetic momentum (ranked Roza #1), another valued concept originality and final-image resonance (ranked Sola #1, for the coffee-mug ending). This exposed a rubric gap — pacing assessment should include an "invention" or "parking lot" dimension.

---

## Test 3: The Echo Chamber Test — Does the Room Improve on Solo?

**Brief**: A corporate mediator trapped in an AI sensory deprivation tank discovers her internal monologue is echoed with a 3-second delay. The "technicians" monitoring her are her own fragmented personalities. She tries to glitch the simulation by thinking in contradictions.

**Design**: 3 solo personas (Sola Jin, Nils Halden, Luthor Reed) + 1 writers room (Luthor as head + Nils, Gwyn Thompson, Leonie Marsh, Gani Urs) + 1 Sonnet control. All with `story_world` active.

### Structural Divergence Confirmed

| | The tank is... | The echo is... | Reassembly means... |
|---|---|---|---|
| **Sola Jin** | Body-sized sphere with degrading physics | The gap between feeling and analysis | Losing the professional instrument |
| **Nils Halden** | Five physical rooms, each demanding a different Mara | The leak between partitioned selves | Making doors, not walls |
| **Luthor Reed** | A negotiation table | Opposing fire with 3s response time | Surrendering the weapon |
| **Writers Room** | A siege with somatic architecture | Invasion → mirror → absence-as-grief | The cost of hearing yourself clearly |
| **Sonnet** | *The Conversation* inverted | Subject becoming surveilled | The harder choice |

The `story_world` field produced genuine divergence on a completely new brief, confirming the Sleepwalker results weren't brief-specific.

### The Writers Room Verdict

**Both external reviewers ranked the room version above every solo write.** The cleanest A/B test: Luthor solo vs. Luthor-as-head-writer-with-room.

What the room added that Luthor alone couldn't:
- **Gwyn Thompson**: Body-first glitch construction (skin → proprioception → salt → visual). Luthor's solo had glitches as linguistic events.
- **Leonie Marsh**: Permanent ambiguity — the Diplomat scene readable as genuine empathy OR engineered extraction. Luthor's solo had fragments as known tactical entities.
- **Gani Urs**: Three-stage echo refrain (invasion → mirror → absence-as-grief). Luthor's solo had the echo as a tactical clock.
- **Nils Halden**: Each fragment names the partition it protects during the choice scene. Luthor's solo had the choice as strategic; the room made it personal.

The "who won which scene" map shows no single persona dominates:

| Scenes Won | Persona | Contribution |
|:---:|---------|-------------|
| 1, 4, 6, 9 | Luthor Reed | Siege architecture, tactical exchanges, the Child as breach |
| 7, 11 | Gwyn Thompson | Body-first glitches, somatic reassembly |
| 3, 5 | Leonie Marsh | Ambiguity plants, irreconcilable readings |
| 12 | Gani Urs | Refrain's third meaning — echo as absence/grief |
| 10 | Nils Halden | Each fragment mourning its own dissolution |

### External Review Scores

| Screenplay | Originality | Pacing | Appeal | Brief Interp | Production | Total /50 |
|-----------|:-:|:-:|:-:|:-:|:-:|:-:|
| **Writers Room** | 9.0 | 8.5 | 8.5 | 9.5 | 8.5 | **44.0** |
| Luthor solo | 8.5 | 9.0 | 8.0 | 9.0 | 9.0 | 43.5 |
| Sola solo | 8.0 | 8.0 | 8.0 | 8.5 | 8.5 | 41.0 |
| Nils solo | 8.5 | 7.5 | 8.0 | 8.5 | 8.0 | 40.5 |
| Sonnet control | 7.0 | 8.0 | 7.5 | 7.5 | 8.0 | 38.0 |

The Sonnet control finished last in both reviews, confirming the persona system beats raw model capability.

---

## The Persona Architecture: Final State

### Schema (v2.1)

The current persona file contains ~85-105 lines with these sections:

```yaml
# Header comment: inspiration, mechanism line, differentiation
agent_name:
room_title:

voice_sample: |    # 3 paragraphs, first-person, how they talk about craft

anti_canon:        # 5 things they refuse to write (structural, not thematic)

story_world:       # NEW — the architectural field
  dramatic_container: >    # Physical/social reality for ANY story
  structural_anti_canon: > # The shape they will NEVER build

craft_method:
  story_entry_point: >     # Where they start
  scene_construction: >    # How they build scenes
  rewrite_approach: >      # What they cut, what they protect

constraints:       # 5-6 hard rules that force novel choices

creative_tension: > # The opposing impulses in their work

psychology:
  creative_engine: >  # What drives them
  blind_spot: >       # Where they fail
  cant_write: >       # Their honest limitation
```

### What Each Section Does

| Section | Level | Function | Evidence |
|---------|-------|----------|----------|
| `voice_sample` | Scene | Integrates personality into output voice | Omelas: Dialogue Sample scored 30/30 |
| `anti_canon` | Scene | Blocks default completions, forces novel choices | Omelas: Anti-Canon scored 29/30; Persona test: mechanisms > moods |
| `story_world` | Architecture | Determines physical/social shape of story | Sleepwalker: broke convergence; Echo Chamber: confirmed on new brief |
| `craft_method` | Scene | Provides process for building scenes | Omelas: Craft Method was unanimous top tier |
| `constraints` | Scene | Hard rules that force structural choices | Omelas: Constraints scored 28/30 |
| `creative_tension` | Thematic | Opposing impulses create generative friction | Omelas: Tension Pair (3 sentences) scored 28/30 |
| `psychology` | Character | Provides creative engine and honest limitations | Omelas: Psychology scored 28/30 for world-grounding |

### What NOT to Include

| Excluded | Why | Evidence |
|----------|-----|----------|
| Audience Contract | Output-focused; doesn't help model make different choices | Omelas: scored below control |
| Taste Profile | Preferences without pressure; doesn't change structure | Omelas: Tier 3 |
| Full backstory/lore | Performativity doesn't constrain output | v2→v3 finding: 573 lines created narrator, not narration |
| Comprehensive schema (80+ fields) | Over-determines; feels thesis-driven not discovered | Omelas: Full Schema was 7th of 13 |

### Room Profiles (Loaded Only in Multi-Persona Context)

Separate file per persona (~30 lines):
- `voice_in_room` — speech patterns, rhythm
- `notices_first` — what catches attention (derived from mechanism)
- `builds_by` — how they metabolize others' ideas
- `clashes_with` — 2 personas with incompatible mechanisms
- `allies_with` — 2 personas with complementary mechanisms
- `concedes_when` — what changes their position
- `verbal_signature` — catchphrases and delivery

---

## The Writers Room Process

### When It Adds Value

The room categorically improves on solo writes when:
- The brief has **multiple load-bearing dimensions** (Echo Chamber: language + body + identity + ambiguity + temporal structure)
- The head writer has a **strong mechanism with known blind spots** (Luthor: brilliant at language, blind to somatic experience)
- Room members are **hired for gaps** with explicit lane assignments and documented friction points

### When Solo May Be Sufficient

- The brief aligns perfectly with one persona's mechanism (Sola on a sealed-system premise)
- The desired output is genre-specific with a single dominant axis (pure comedy, pure action)
- Production speed matters more than richness

### The Room's Mechanism

The room works because **the friction between incompatible mechanisms generates scenes no single persona could write**. The Diplomat scene in Echo Chamber (readable as genuine empathy OR engineered extraction) required Leonie Marsh's ambiguity engine operating inside Luthor Reed's siege architecture. Neither persona could produce that scene alone — it exists only in the negotiation between them.

---

## Conclusions

### For Persona Designers

1. **Start with the mechanism.** Define it in one sentence before writing anything else. If you can't name the mechanism, the persona will underperform.
2. **Write anti-canons that block the model's defaults**, not the persona's thematic enemies. The most valuable anti-canon is the one that, if removed, would make the output indistinguishable from the control.
3. **Add `story_world` to break architectural convergence.** Without it, the model supplies its own structural defaults regardless of persona.
4. **Keep it lean.** ~85-105 lines outperforms ~200-700 lines. Signal density matters more than information volume.
5. **Cross-block adjacent personas.** If two personas could produce similar output, add anti-canons to each that explicitly block the other's signature move.

### For Creative Writing Systems

1. **The bare model is the floor, not the ceiling.** Personas reliably beat the control across all tests. The investment in persona design pays off.
2. **Structural convergence is the real enemy**, not tonal sameness. Personas naturally produce different voices; they don't naturally produce different story shapes. Architecture-level instruction is required.
3. **Multi-persona collaboration produces categorically richer output** when the room is assembled for friction, not harmony. Hire for gaps. Document the clashes. The disagreements are the value.
4. **External reviewers disagree with each other** — and that's the signal that the personas are working. If all reviewers ranked the same way, the divergence would be superficial.

### The Hierarchy of Persona Fields (by Impact)

1. **story_world** — determines the physical shape of the story (architecture level)
2. **anti_canon** — blocks default completions, forces novel choices (scene level)
3. **craft_method** — provides the process for building scenes (scene level)
4. **voice_sample** — integrates personality into output voice (scene level)
5. **constraints** — hard rules that force structural choices (scene level)
6. **mechanism** (in header comment) — the seed from which everything else is derived
7. **creative_tension / psychology** — provides engine and limitations (character level)
8. **room_profile** — enables productive multi-persona friction (room level)

---

## Appendix: Test Materials

All test materials are preserved in the project directories:

| Test | Location | Contents |
|------|----------|----------|
| Omelas | `projects/omelas-test/` | 12 persona formats + control, 3 evaluations, synthesis |
| Sleepwalker | `projects/sleepwalker-test/` | V1 (5 screenplays), V2 (3 with story_world), deprecated Gwyn, evaluation |
| Echo Chamber | `projects/echo-chamber-test/` | 3 solos + room + Sonnet control, room process artifacts |

Persona files: `skills/writer/personas/` (25 numbered files + room_profiles/ + _deprecated/)
Schema: `skills/writer/personas/_schema.yaml` (v2.1)
