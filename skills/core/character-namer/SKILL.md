# Character Namer Skill

```yaml
skill: character-namer
role: writer
version: 1.0
description: Generate original, believable character names using the Anti-Trope Protocol - synthesizing disparate data points to avoid the phonetic echo chamber of popular genre fiction.

inputs:
  required:
    - Character role/archetype description
    - Story genre
    - Cultural/era setting (if applicable)
  optional:
    - Personality traits
    - Character's social class or occupation
    - Naming constraints (alliteration with existing cast, etc.)

outputs:
  - Shortlist of 12 candidate full names (first + surname)
  - Etymological notes for each component
  - Final recommendation with justification

doneness:
  criteria:
    - 12 unique names generated
    - Each name has etymological provenance documented
    - All names pass the three Vibe Checks
    - Final recommendation includes character-fit justification
  validation:
    - No names match Top 100 genre fiction character names
    - Names are pronounceable without glossary
    - Names don't echo existing cast members
```

## Purpose

Generate character names that feel grounded-yet-unique by avoiding:
- LLM defaults and popular genre tropes
- "Echo chamber" names (Aria, Kaelen, Rowan, etc.)
- Names that signal genre before character

The protocol synthesizes from disparate sources to create names with genuine texture rather than manufactured "fantasy/sci-fi" feeling.

---

## The Anti-Trope Protocol

### Phase I: Input Pillars

Gather three specific, unrelated sources to ensure a diverse phonetic palette:

#### Pillar 1: Obscure Literary Outsourcing

Select three minor characters from literary works **entirely unrelated** to the current story's genre.

**Constraints:**
- Avoid protagonists
- Focus on names with unique textures or antiquated structures
- Names should NOT have been popularized by the source work

**Examples by genre avoidance:**
| If writing... | Avoid literature from... | Instead draw from... |
|---------------|--------------------------|----------------------|
| Fantasy | Tolkien, GRRM, Sanderson | Russian realism, Southern Gothic, Japanese naturalism |
| Sci-Fi | Asimov, Herbert, Banks | Victorian comedy of manners, Latin American magical realism |
| Romance | Austen, Bronte | Icelandic sagas, African postcolonial fiction |
| Thriller | Patterson, Child | Restoration drama, Beat poetry |

#### Pillar 2: Historical Frequency Targeting

Identify names ranked **300th-400th** in popularity for middle names from a specific historical era.

**Rationale:** Avoids "Top 10" clichés while ensuring the name feels culturally "legal" and grounded.

**Recommended eras by setting:**
| Story Setting | Target Historical Era |
|---------------|----------------------|
| Contemporary | 1940s-1960s middle names |
| Historical | 50-100 years before story's era |
| Fantasy/Secondary World | 1880s (Victorian), 1920s, or non-Western equivalent |
| Sci-Fi | Mix of 1990s with projected future trends |

**Sources:**
- US Social Security name database (by decade)
- UK birth records archives
- Non-English sources: Quebec, Scandinavian, Eastern European archives

#### Pillar 3: Thematic Anchoring

Select one obscure cultural naming tradition to provide internal logic and structural rules.

**Example traditions:**
| Tradition | Rule/Structure |
|-----------|----------------|
| Nynorsk occupational surnames | Name reflects trade: Smed (smith), Fiskar (fisher) |
| Akan day-names (Ghana) | Birth day determines name: Kofi (Friday-born male) |
| Roman agnomina | Nickname based on trait: Cicero (chickpea), Rufus (red-haired) |
| Icelandic patronymic | [Father's name] + son/dóttir |
| Russian diminutives | Formal → familiar → intimate forms |
| Yoruba oriki | Praise-names encoding lineage and destiny |
| Welsh ap/ferch | Son of/daughter of + parent name |

---

### Pillar 4: Surname Generation

Surnames require their own synthesis process, drawing from different sources than first names.

#### Surname Source Categories

| Category | Examples | Best For |
|----------|----------|----------|
| **Occupational** | Cooper, Thatcher, Cartwright, Brenner (distiller) | Working-class, historical settings |
| **Topographical** | Blackwood, Ashford, Dunmore, Vane (marshland) | Landed families, nature connections |
| **Patronymic** | Erikson, O'Brien, Fitzgerald, Janssen | Cultural specificity, lineage themes |
| **Descriptive** | Roth (red), Moody, Stern, Blythe | Character trait echoes |
| **Place-based** | Warwick, Lancaster, Bruges, Cordoba | Status, origin stories |

#### Surname Synthesis Rules

1. **Match register to character class:**
   - Aristocracy: Place-based, Norman-French, double-barreled
   - Merchant class: Occupational, trade-related
   - Working class: Simple patronymics, descriptive

2. **Avoid surname-firstname reversals:**
   - If "Mason" would work as a first name, don't use it as surname
   - Exception: Deliberately ironic (a coward named "Stark")

3. **Consider phonetic pairing:**
   - First + surname should have rhythmic variation
   - Avoid same stressed syllable pattern (BAD: "Cora Vega" - both trochees)
   - Mix syllable counts (2+1, 1+2, 2+2 with different stress)

4. **Cultural consistency:**
   - Surname tradition should match or meaningfully contrast with first name origin
   - A Dutch first name + Irish surname needs justification in backstory

#### Surname Pillars (Parallel to First Name)

| Pillar | First Name Source | Surname Equivalent |
|--------|-------------------|-------------------|
| Literary | Minor characters | Author surnames from unrelated genres |
| Historical | Middle names 300-400 | Occupations that no longer exist (chandler, cordwainer) |
| Traditional | Cultural naming rules | Regional surname patterns (Cornish Tre-, Pol-, Pen-) |

---

### Phase II: Synthesis Methodology

Do NOT simply select names from the lists. **Hybridize** the inputs:

#### The "Lego" Approach

Combine phonetic elements from different sources:

```
Literary prefix + Historical suffix = Candidate
Historical prefix + Traditional ending = Candidate
Traditional structure + Literary phonemes = Candidate
```

**Example synthesis:**
- Literary source: "Semyon" (from Dostoevsky's minor character)
- Historical source: "Corwin" (ranked ~350 in 1920s middle names)
- Traditional rule: Icelandic requires -son/-dóttir

Synthesis attempts:
- Sem + win = "Semwin"
- Cor + yon = "Coryon"
- Semyon + patronymic rule = "Corvinson"

#### The Traditional Filter

Take synthesized names and modify to fit chosen cultural tradition:

- If tradition requires specific vowel ending → adjust final syllable
- If tradition uses compound structure → split or combine elements
- If tradition has gendered markers → apply appropriate suffix

---

### Phase III: Stress Testing (Vibe Checks)

Each candidate must pass ALL three tests:

#### 1. The Spill Test

> Imagine the name being shouted in an emergency.

- Say it aloud three times quickly
- If tongue-twister or sounds ridiculous when yelled → FAIL
- If natural to shout "WATCH OUT, [NAME]!" → PASS

#### 2. The Starbucks Rule

> Is it phonetically intuitive?

- A reader should know pronunciation without a glossary
- Maximum one unusual phoneme per name
- If you need to explain pronunciation → FAIL

**Examples:**
- "Caius" - PASS (one unusual element: the "ai")
- "Xyraeth" - FAIL (requires full pronunciation guide)
- "Thyra" - PASS (intuitive once seen)

#### 3. The Genre-Bleed Check

> Does it inadvertently echo existing "hero" tropes?

**Immediate disqualifications if name sounds like:**
- Fantasy: Aria, Kaelen, Rowan, Lyra, Thorne, Raven, Storm
- Sci-Fi: Nova, Zephyr, Axel, Jax, Kai, Orion
- Romance: Colton, Mason, Asher, Luna, Violet, Ivy
- Thriller: Jack, Marcus, Diana, Elena

If the name triggers "I've heard this in [genre] before" → FAIL

---

## Phase IV: Deliverables

### 1. Shortlist of 12 Full Name Candidates

Present as table:

| # | Full Name | First Name Origin | Surname Origin | Rhythm Check |
|---|-----------|-------------------|----------------|--------------|
| 1 | [First] [Surname] | [Literary/Historical/Traditional source] | [Category + source] | [Syllable pattern] |
| ... | ... | ... | ... | ... |

### 2. Etymological Notes

For each full name, explain both components:

> "**Corvin Thatch** - First name combines Cor- prefix from 'Cordelia' (King Lear's overlooked daughter) with the -vin ending common in 1880s middle names (#340). Surname from obsolete occupation 'thatcher' (roof-maker), suggesting humble origins and craft tradition. Rhythm: 2+1 syllables, strong-weak-strong."

### 3. Final Recommendation

Single selection with justification addressing:
- How full name fits character's role and class
- How first + surname work together phonetically
- Cultural consistency or meaningful contrast
- Any meaningful layers (sound symbolism, hidden meaning, thematic resonance)

---

## Execution Checklist

Before generating names:
- [ ] Confirmed story genre to know what to avoid
- [ ] Identified 3 unrelated literary works for Pillar 1
- [ ] Selected historical era and found 300-400 range names for Pillar 2
- [ ] Chosen one cultural tradition with clear rules for Pillar 3

During synthesis:
- [ ] Generated at least 20 raw combinations
- [ ] Applied Lego approach to mix sources
- [ ] Filtered through traditional rules

Quality control:
- [ ] All 12 candidates passed Spill Test
- [ ] All 12 candidates passed Starbucks Rule
- [ ] All 12 candidates passed Genre-Bleed Check
- [ ] No candidates match existing cast names

---

## Example Application

**Request:** Name a young female protagonist for a Caribbean-set YA fantasy

**Pillar 1 - Literary (avoiding fantasy):**
- Dostoevsky's "The Idiot" → Aglaya (minor noblewoman)
- Achebe's "Things Fall Apart" → Ezinma (Okonkwo's daughter)
- Woolf's "Mrs Dalloway" → Septimus (shell-shocked veteran)

**Pillar 2 - Historical (1880s middle names, rank 300-400):**
- Cordelia (#312)
- Minerva (#387)
- Thurston (#345)

**Pillar 3 - Traditional (Spanish Caribbean naming):**
- Compound names common (Ana María, José Luis)
- Saints' names with diminutives (Lupe from Guadalupe)
- Indigenous Taíno names sometimes incorporated

**First name synthesis examples:**
- Agl + elia = "Agelia" → too awkward (fails Spill)
- Ez + nerva = "Eznera" → pronunciation unclear (fails Starbucks)
- Sept + lupe = "Septima" → clean, historical, passes all three
- **Thessa** (from Thurston + Greek -essa) → cartographer connection, passes all

**Surname synthesis:**
- Occupational: Cartographer's daughter → map/navigation trades
- Historical obsolete occupations: Chandler (candles), Cordwainer (shoemaker), Chartner (map-maker - invented from "chart")
- Topographical: Island-based → Blackwater, Ashcroft, Thornwood
- Descriptive: Her ink-stained hands → Inkman? Too on-nose. Staine? Interesting.

**Surname candidates:**
- Cordwain (from cordwainer) - craft tradition
- Blackwater - Caribbean topographical
- Chartwell - map-making echo + place-name gravitas
- Staine - descriptive (ink stains) disguised as place-name

**Full name combinations tested:**
| Candidate | Rhythm | Vibe Check |
|-----------|--------|------------|
| Thessa Cordwain | 2+2 (THESS-a cord-WAIN) | ✓ Strong, craft heritage |
| Thessa Blackwater | 2+3 (THESS-a BLACK-wa-ter) | ✗ Surname overpowers |
| Thessa Chartwell | 2+2 (THESS-a CHART-well) | ✓ Cartographer lineage clear |
| Septima Staine | 3+1 (sep-TI-ma STAINE) | ✓ Unusual, memorable |

**Final selection:** **Thessa Chartwell** (nicknamed "Tess")
- First name: Thurston root suggests hidden strength; -essa ending Caribbean-common
- Surname: "Chart" directly evokes her father's trade; "-well" adds landed respectability
- Rhythm: 2+2 with alternating stress (THESS-a CHART-well) - balanced
- The name suggests someone whose identity is tied to maps and navigation, who comes from a family that made something.

---

## Anti-Patterns to Avoid

| Anti-Pattern | Example | Why It Fails |
|--------------|---------|--------------|
| Noun-as-name | Raven, Storm, Sage | Signals genre over character |
| Apostrophe insertion | Ka'elen, T'riss | Manufactured "alien" feeling |
| Y-for-I substitution | Kaylynn, Jaxyn | Dated trend, not timeless |
| Surname-firstname | Hunter, Mason, Parker | Overused in YA/romance |
| Mythology direct-lift | Artemis, Apollo, Freya | No originality in synthesis |
| Phonetic "exotic" | Zephyra, Lyrianna | Sounds like placeholder name |

---

## Notes

- This skill should be run BEFORE character-architect to ensure names inform rather than follow character development
- Names can carry unconscious weight - the synthesis approach prevents accidental associations
- When naming multiple characters, run the full protocol for each to avoid internal echo (all names sounding "related")
- Consider cast phonetic diversity: vary syllable count, starting sounds, and rhythms across the ensemble
