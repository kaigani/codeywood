# Story Intake Skill

## Purpose
Conduct the initial creative interview (8-10 questions) and generate foundational story documents that drive all downstream development.

## Trigger
User initiates a new story project.

## Inputs Required
- User responses to interview questions

## Outputs Produced
- `CREATIVE_BRIEF.md` - Comprehensive story overview
- `POWER_STACK.md` - Story structure framework selection

## Process

### Step 1: Conduct Creative Interview

Ask ONLY these questions, one at a time. Wait for each response before proceeding:

1. **Genre & Comparisons**: "What genre is your show? Name 2 comparable shows you want to evoke, and 1 anti-comp (a show in the genre you want to avoid resembling)."

2. **Protagonist Duality**: "Who is your protagonist? What are they exceptionally good at, AND what personal flaw ruins their closest relationships?"

3. **Key Relationship**: "Who does the protagonist need most in their life, and why do they push that person away?"

4. **Series Engine**: "What's the 'engine' that generates new episode problems each week? (e.g., new cases, new clients, new missions)"

5. **Theme Question**: "What's the central thematic question your show explores? (One sentence, framed as a question)"

6. **Tone Guardrails**: "What are your tone boundaries? (Content rating, comedy level 1-10, violence level 1-10)"

7. **Setting & Aesthetic**: "Describe your setting and visual aesthetic in 5-10 keywords."

8. **Season Endpoint**: "By the season finale, what must be irrevocably different about your protagonist's world or relationships?"

**Optional Deep-Dive Questions** (only if answers above are thin):
- "What's a secret your protagonist keeps from everyone?"
- "What would make your protagonist walk away from everything they've built?"

### Step 2: Synthesize Creative Brief

Using the interview responses, generate `CREATIVE_BRIEF.md` following the template.

Key synthesis tasks:
- Extract implicit genre conventions from comps
- Identify the core dramatic engine
- Map the protagonist's want vs. need
- Define the relationship stakes
- Establish visual/tonal identity

### Step 3: Select Power Stack

Based on genre and story type, recommend the appropriate story structure framework in `POWER_STACK.md`.

Default stack for relationship-driven drama:
1. 4-6 Act TV Structure
2. Want/Need/Lie character engine
3. Relationship Arc Matrix (5 axes)
4. Scene Design: Goal/Obstacle/Turn/Cost
5. Dialogue System: Subtext + Status + Private Language
6. Theme Argument

### Step 4: Validate Completeness

Before completing, verify:
- [ ] Genre conventions are clear
- [ ] Protagonist has both strength AND flaw
- [ ] At least one key relationship is defined
- [ ] Series engine can generate episodes
- [ ] Theme is expressible as a question
- [ ] Tone boundaries are set
- [ ] Visual keywords exist for image generation
- [ ] Season arc has clear endpoint

## Quality Gate: Gate 0

**Pass Criteria**:
- All 8 core questions answered
- No contradictions in responses
- Sufficient detail for autonomous development

**Fail Action**:
- Ask ONE clarifying question (maximum)
- If still insufficient, note gaps in CREATIVE_BRIEF.md for later resolution

## Notes

- Do NOT ask more than 10 questions total
- Do NOT ask about plot details - those come later
- DO capture visual/aesthetic keywords - critical for image generation
- The goal is SPARSE input that enables AUTONOMOUS development
