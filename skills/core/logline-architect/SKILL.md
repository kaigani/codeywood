# Logline Architect Skill

## Purpose
Generate and refine a compelling logline using verbalized sampling (tournament selection) to find the strongest possible hook.

## Trigger
CREATIVE_BRIEF.md exists and is complete.

## Inputs Required
- `CREATIVE_BRIEF.md`
- `POWER_STACK.md`

## Outputs Produced
- `LOGLINE_LOCK.md` - Final approved logline with rationale

## Process

### Step 1: Extract Logline Components

From CREATIVE_BRIEF.md, identify:

| Component | Source Field | Value |
|-----------|--------------|-------|
| Protagonist | protagonist.role | |
| Flaw | protagonist.fatal_flaw | |
| Inciting Incident | series_engine | |
| Goal | protagonist.want | |
| Stakes | key_relationship | |
| Obstacle | theme + antagonist | |

### Step 2: Generate Logline Candidates

Create **5 distinct loglines** using different structural approaches:

#### Approach A: Character-First
> A [FLAWED PROTAGONIST] must [ACTION] when [INCITING INCIDENT], but [INTERNAL OBSTACLE] threatens [WHAT THEY'LL LOSE].

#### Approach B: Situation-First
> When [INCITING INCIDENT], a [PROTAGONIST DESCRIPTION] discovers [REVELATION] that forces them to [IMPOSSIBLE CHOICE].

#### Approach C: Relationship-First
> [PROTAGONIST] and [KEY RELATIONSHIP] must [GOAL] while [THEIR CONFLICT] threatens to [CONSEQUENCE].

#### Approach D: Question-First
> What happens when [PREMISE]? [PROTAGONIST] finds out when [INCITING INCIDENT].

#### Approach E: Stakes-First
> With [STAKES] on the line, [PROTAGONIST] must [ACTION]—but first they'll have to [OVERCOME FLAW].

### Step 3: Tournament Selection

**Round 1: Evaluate Each Candidate**

For each logline, score (1-10):
- **Hook**: Does it create immediate curiosity?
- **Clarity**: Can you picture the show?
- **Conflict**: Is the central tension obvious?
- **Character**: Does the protagonist feel specific?
- **Stakes**: Do we understand what's at risk?

**Round 2: Top 3 Face-Off**

Select top 3 by total score. For each, ask:
1. Would you watch the pilot based on this alone?
2. Does it promise the right genre/tone?
3. Does it differentiate from comps?

**Round 3: Final Selection**

Choose winner. If tie, prefer:
1. Stronger character specificity
2. Clearer stakes
3. More distinctive hook

### Step 4: Refine Winner

Polish the winning logline:
- Remove unnecessary words
- Strengthen verbs
- Ensure protagonist flaw is implicit or explicit
- Verify relationship stake is present
- Confirm consequence is irreversible

### Step 5: Create Variations

Generate 3 versions of the final logline:
1. **Short** (under 25 words) - for pitches
2. **Standard** (25-40 words) - for documents
3. **Extended** (40-60 words) - includes theme hint

### Step 6: Lock and Document

Create `LOGLINE_LOCK.md` with:
- Final logline (all versions)
- Why this version won
- What it promises to the audience
- What it commits the writers to deliver

## Quality Gate: Gate 1

**Pass Criteria**:
- [ ] Logline includes protagonist with identifiable flaw
- [ ] Relationship stake is present
- [ ] Consequence is irreversible (can't just walk away)
- [ ] Genre is clear from word choice
- [ ] Fits in one breath when spoken

**Fail Action**:
- Return to Step 2 with specific gap to address
- Maximum 2 additional tournament rounds

## Logline Principles

### DO:
- Use active verbs
- Make the protagonist's flaw relevant to the plot
- Include emotional stakes (not just physical)
- Hint at the show's unique angle
- Create an impossible situation

### DON'T:
- Use character names (use role/archetype instead)
- Include more than 2 characters
- Reveal the ending
- Use vague language ("must confront their past")
- Describe theme directly

## Example Tournament

**Input Brief**: Detective with trust issues, partner's unsolved murder, noir procedural

**Candidates**:
1. "A detective who trusts no one must partner with the prime suspect in her partner's murder—or let the case go cold forever."
2. "When her partner's murder reopens, a brilliant but isolated detective discovers the only witness is someone she swore never to trust again."
3. "Two years after her partner's death, Detective Chen gets a new lead—but solving it means working with the one person she believes got him killed."
4. "A detective's obsessive hunt for her partner's killer forces her to choose: catch the murderer, or protect the fragile new partnership that's keeping her alive."
5. "What if the only person who can help you solve your partner's murder is the reason you stopped trusting anyone?"

**Round 1 Scores**:
| Candidate | Hook | Clarity | Conflict | Character | Stakes | Total |
|-----------|------|---------|----------|-----------|--------|-------|
| 1 | 8 | 9 | 8 | 7 | 8 | 40 |
| 2 | 7 | 7 | 7 | 8 | 6 | 35 |
| 3 | 9 | 8 | 8 | 8 | 7 | 40 |
| 4 | 6 | 6 | 8 | 7 | 9 | 36 |
| 5 | 8 | 5 | 7 | 6 | 6 | 32 |

**Top 3**: 1, 3, 4

**Winner**: Candidate 3 (most specific, best hook, clearest setup)

**Refined**:
> "Two years after her partner's death, Detective Chen finally gets a new lead—but following it means trusting the one person she believes got him killed."
