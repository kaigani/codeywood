---
name: character-architect
description: "Develops psychologically coherent characters with want/need/lie profiles, distinct voice fingerprints, a scored relationship matrix, and image-generation-ready visual descriptions. Produces CHARACTER_SHEETS, RELATIONSHIP_MAP.json, and CAST_LIST.md. Use when LOGLINE_LOCK.md is approved and characters need to be developed before story structure."
---

# Character Architect

Develop deep, psychologically coherent characters with distinct voices, trackable relationships, and image-generation-ready visual descriptions. Each character drives conflict through their psychology, not just their plot function.

## Inputs

- `CREATIVE_BRIEF.md` — genre, protagonist, key relationship, aesthetic keywords
- `POWER_STACK.md` — story structure framework
- `LOGLINE_LOCK.md` — approved logline with protagonist flaw and stakes

## Outputs

- `CHARACTER_SHEETS/{NAME}.md` — individual character profiles (identity, psychology, visual, voice, arc)
- `RELATIONSHIP_MAP.json` — machine-readable relationship matrix with 5 axes per pair
- `CAST_LIST.md` — summary of all characters with roles and tiers

## Process

### Step 1: Identify Required Characters

Extract character requirements from `CREATIVE_BRIEF.md` and `LOGLINE_LOCK.md`:

| Tier | Scope | Characters |
|------|-------|------------|
| 1 — Must Have (Pilot) | Protagonist, key relationship character, primary antagonist/obstacle | 3 |
| 2 — Series Regulars | Supporting cast for series engine + relationship dynamics | 3–5 |
| 3 — Recurring | World-building, multi-episode characters | As needed |

### Step 2: Build Protagonist

Complete the full CHARACTER_SHEET template with these critical sections:

**Psychology Deep Dive:**
1. **Want** — what they consciously pursue
2. **Need** — what they actually require (unconscious)
3. **Lie** — the false belief that blocks them
4. **Wound** — the origin event of the lie
5. **Ghost** — how the wound manifests daily
6. **Virtue with Cost** — their strength that also causes problems

**Relationship Wiring:** How they attach, what triggers defenses, what they never discuss, how they show (not say) love.

**Voice Profile:** Sentence length patterns, vocabulary domains, metaphor sources, sarcasm/humor levels, taboo topics, stress speech patterns.

### Step 3: Build Key Relationship Character

The person identified as "who they need most" in the brief. Define their independent want/need/lie arc, plus the **bond mechanism** (what draws them together) and **pressure mechanism** (what creates conflict).

### Step 4: Build Remaining Cast

For each additional character, verify:

1. **Role check** — story function (ally, antagonist, mentor, threshold guardian, shapeshifter, trickster, herald)
2. **Differentiation check** — distinct from existing characters in voice, visual, worldview, and relationship to protagonist
3. **Arc potential** — what change is available to them over the season

### Step 5: Generate Relationship Map

Create `RELATIONSHIP_MAP.json` with scored axes for every character pair:

- **Trust** (−5 to +5), **Respect** (−5 to +5), **Dependency** (−5 to +5), **Intimacy** (−5 to +5), **Moral Alignment** (−5 to +5)
- Plus: bond mechanism, pressure mechanism, private language, arc direction

### Step 6: Visual Description Optimization

Ensure each character's visual description is prompt-ready for image generation:

- Specific physical features (not vague — avoid "attractive woman")
- Distinctive silhouette elements, signature clothing/accessories, color associations
- Locked visual anchors that never change + allowed variations
- Negative prompts (what to avoid generating)

### Step 7: Voice Differentiation Test

Test: write the same line ("We need to talk about what happened.") in each character's voice. Characters must be distinguishable WITHOUT dialogue tags. If voices overlap, adjust sentence length, vocabulary domain, directness level, or add verbal tics.

### Step 8: Contradiction Check

Verify each major character:

- [ ] Has at least one surprising trait (against type)
- [ ] Causes at least one problem in the pilot (not just reactive)
- [ ] Has one relationship they're actively failing
- [ ] Has a secret (even if never revealed)
- [ ] Wants something in every scene they appear in

## Quality Gate: Gate 2

**Pass**: Every major character has complete want/need/lie, causes a pilot problem, has a surprising competency, has a failing relationship, has prompt-ready visuals, and passes voice differentiation.

**Fail**: Identify specific gaps, return to the relevant step. Do not proceed to story-architect until this gate passes.

## Notes

- Every character believes they are the hero of their own story — antagonists have understandable logic
- Supporting characters have lives beyond the protagonist
- Voice profiles must include what the character WON'T say, not just what they will
- Visual descriptions feed directly into character-reference-generator — specificity here saves regeneration cycles later
