# Character Architect Skill

## Purpose
Develop deep, psychologically coherent characters with distinct voices, trackable relationships, and image-generation-ready visual descriptions.

## Trigger
LOGLINE_LOCK.md exists and is approved.

## Inputs Required
- `CREATIVE_BRIEF.md`
- `POWER_STACK.md`
- `LOGLINE_LOCK.md`

## Outputs Produced
- `CHARACTER_SHEETS/{NAME}.md` - Individual character profiles
- `RELATIONSHIP_MAP.json` - Machine-readable relationship matrix
- `CAST_LIST.md` - Summary of all characters

## Process

### Step 1: Identify Required Characters

From CREATIVE_BRIEF.md and LOGLINE_LOCK.md, identify:

**Tier 1 - Must Have (Pilot)**:
- Protagonist
- Key relationship character (from brief)
- Primary antagonist or obstacle character

**Tier 2 - Series Regulars**:
- Supporting cast needed for series engine
- Additional relationship dynamics
- Typically 3-5 additional characters

**Tier 3 - Recurring**:
- Characters who appear in multiple episodes
- World-building characters
- Define as needed

### Step 2: Build Protagonist First

Complete the full CHARACTER_SHEET template for the protagonist.

**Critical Sections**:

#### Psychology Deep Dive
1. **Want**: What they consciously pursue
2. **Need**: What they actually require (unconscious)
3. **Lie**: The false belief that blocks them
4. **Wound**: The origin event of the lie
5. **Ghost**: How the wound manifests daily
6. **Virtue with Cost**: Their strength that also causes problems

#### Relationship Wiring
- How they attach to others
- What triggers their defenses
- What they never talk about
- How they show (not say) love

#### Voice Profile
- Sentence structure patterns
- Vocabulary level and domains
- Metaphor sources
- Sarcasm/humor patterns
- What topics they avoid
- Speech patterns under stress

### Step 3: Build Key Relationship Character

The character identified as "who they need most" in the brief.

**Special Focus**:
- Why they are uniquely suited to the protagonist
- What they provide that no one else can
- Their own want/need/lie (independent arc)
- The "bond mechanism" - what draws them together
- The "pressure mechanism" - what creates conflict

### Step 4: Build Remaining Cast

For each additional character:

1. **Role Check**: What story function do they serve?
   - Ally
   - Antagonist
   - Mentor
   - Threshold Guardian
   - Shapeshifter
   - Trickster
   - Herald

2. **Differentiation Check**: Are they distinct from existing characters in:
   - Voice
   - Visual appearance
   - Worldview
   - Relationship to protagonist

3. **Arc Potential**: What change is available to them over the season?

### Step 5: Generate Relationship Map

Create `RELATIONSHIP_MAP.json` with:

For each character pair:
- **Trust** (-5 to +5): Belief in reliability/honesty
- **Respect** (-5 to +5): Admiration for competence/character
- **Dependency** (-5 to +5): Need for the other
- **Intimacy** (-5 to +5): Emotional closeness
- **Moral Alignment** (-5 to +5): Shared values

Plus:
- **Bond Mechanism**: What connects them
- **Pressure Mechanism**: What creates conflict
- **Private Language**: Unique terms/references
- **Arc Direction**: Where the relationship is heading

### Step 6: Visual Description Optimization

For each character, ensure the visual description is:

**Prompt-Ready**:
- Specific physical features (not vague)
- Age-appropriate markers
- Distinctive silhouette elements
- Signature clothing/accessories
- Color associations

**Consistency-Focused**:
- Locked visual anchors (never change)
- Allowed variations (outfit changes, etc.)
- Negative prompts (what to avoid)

### Step 7: Voice Differentiation Test

Read sample dialogue for each character. They should be distinguishable WITHOUT dialogue tags.

Test: Write the same line ("We need to talk about what happened.") in each character's voice.

If voices are too similar:
- Adjust sentence length patterns
- Change vocabulary domains
- Modify directness levels
- Add unique verbal tics

### Step 8: Contradiction Check

Verify each character:
- [ ] Has at least one surprising trait (against type)
- [ ] Causes at least one problem in the pilot (not just reactive)
- [ ] Has one relationship they're actively failing
- [ ] Has a secret (even if never revealed)
- [ ] Wants something in every scene they're in

## Quality Gate: Gate 2

**Pass Criteria**:
- [ ] Every major character has complete want/need/lie
- [ ] Every major character causes at least one pilot problem
- [ ] Every major character has one surprising competency
- [ ] Every major character has one failing relationship
- [ ] Visual descriptions are prompt-ready
- [ ] Voices are distinguishable in blind test

**Fail Action**:
- Identify specific gaps
- Return to relevant step
- Do not proceed to story-architect until passed

## Character Sheet Sections

1. **Identity**: Name, age, role, archetype
2. **Psychology**: Want/need/lie/wound/virtue
3. **Relationships**: How they connect to others
4. **Visual**: Physical description, wardrobe, props
5. **Voice**: Speech patterns, vocabulary, quirks
6. **Arc**: Where they start, where they're going
7. **Secrets**: What they hide
8. **Casting Notes**: Actor comparisons (optional)

## Common Pitfalls

### Avoid:
- Characters who only react, never initiate
- Visual descriptions that are generic ("attractive woman")
- Voices that all sound like the writer
- Relationships without conflict potential
- Backstory that doesn't affect present behavior
- Perfect heroes or pure villains

### Ensure:
- Every character believes they're the hero of their own story
- Antagonists have understandable (not sympathetic) logic
- Supporting characters have lives beyond the protagonist
- Physical descriptions include something memorable
- Voice profiles include what they WON'T say
