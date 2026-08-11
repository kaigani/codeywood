---
name: story-intake
description: "Conducts a structured 8-10 question creative interview to generate CREATIVE_BRIEF.md and POWER_STACK.md, establishing genre, protagonist psychology, key relationships, series engine, theme, tone, and visual aesthetic. Use when starting a new story project and no creative brief exists yet."
---

# Story Intake

Conduct the initial creative interview (8–10 questions) and generate foundational story documents that drive all downstream skill execution. Sparse user input enables autonomous development across the full pipeline.

## Inputs

- User responses to the interview questions below

## Outputs

- `CREATIVE_BRIEF.md` — comprehensive story overview with genre, characters, relationships, tone, and visual keywords
- `POWER_STACK.md` — selected story structure framework tailored to the genre

## Process

### Step 1: Conduct Creative Interview

Ask exactly these 8 questions, one at a time. Wait for each response before proceeding.

1. **Genre & Comparisons**: "What genre is your show? Name 2 comparable shows you want to evoke, and 1 anti-comp (a show you want to avoid resembling)."
2. **Protagonist Duality**: "Who is your protagonist? What are they exceptionally good at, AND what personal flaw ruins their closest relationships?"
3. **Key Relationship**: "Who does the protagonist need most in their life, and why do they push that person away?"
4. **Series Engine**: "What's the 'engine' that generates new episode problems each week? (e.g., new cases, new clients, new missions)"
5. **Theme Question**: "What's the central thematic question your show explores? (One sentence, framed as a question)"
6. **Tone Guardrails**: "What are your tone boundaries? (Content rating, comedy level 1–10, violence level 1–10)"
7. **Setting & Aesthetic**: "Describe your setting and visual aesthetic in 5–10 keywords."
8. **Season Endpoint**: "By the season finale, what must be irrevocably different about your protagonist's world or relationships?"

**Optional deep-dive** (only if core answers are thin):
- "What's a secret your protagonist keeps from everyone?"
- "What would make your protagonist walk away from everything they've built?"

Do NOT ask more than 10 questions total. Do NOT ask about plot details — those come from downstream skills.

### Step 2: Synthesize Creative Brief

Generate `CREATIVE_BRIEF.md` from the interview responses. Key synthesis tasks:

- Extract implicit genre conventions from the comp and anti-comp choices
- Identify the core dramatic engine that sustains episodic storytelling
- Map the protagonist's conscious want vs. unconscious need
- Define the central relationship stakes and pressure points
- Establish visual and tonal identity using the aesthetic keywords (critical for image generation downstream)

### Step 3: Select Power Stack

Based on genre and story type, generate `POWER_STACK.md` with the recommended structure framework.

Default stack for relationship-driven drama:

1. 4–6 Act TV Structure (pacing, act-outs)
2. Want/Need/Lie character engine
3. Relationship Arc Matrix (trust, respect, dependency, intimacy, moral alignment)
4. Scene Design: Goal / Obstacle / Turn / Cost
5. Dialogue System: Subtext + Status + Private Language
6. Theme Argument (central question for coherence)

Adjust the stack for non-drama genres (e.g., procedural, comedy, thriller) based on the interview responses.

### Step 4: Validate Completeness

Before completing, verify all criteria are met:

- [ ] Genre conventions are clear from comps
- [ ] Protagonist has both strength AND flaw
- [ ] At least one key relationship is defined with bond and pressure mechanisms
- [ ] Series engine can generate distinct episode problems
- [ ] Theme is expressible as a single question
- [ ] Tone boundaries are set (rating, comedy, violence)
- [ ] Visual/aesthetic keywords exist for image generation
- [ ] Season arc has a clear, irrevocable endpoint

## Quality Gate: Gate 0

**Pass**: All 8 core questions answered, no contradictions, sufficient detail for autonomous development.

**Fail**: Ask ONE clarifying question maximum. If still insufficient, note gaps in `CREATIVE_BRIEF.md` for later resolution — do not block the pipeline.

## Notes

- The goal is sparse input that enables autonomous development — resist over-questioning
- Visual/aesthetic keywords captured here directly feed character-reference-generator and location-reference-generator downstream
- This skill is the entry point for the entire pipeline; all other skills depend on its outputs
