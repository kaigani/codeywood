# Visual Style Guide Skill

## Purpose
Define the show's complete visual language, including global aesthetics, shot conventions, consistency rules, and negative prompts for image generation.

## Trigger
CANON_DB.json is initialized with story data.

## Inputs Required
- `CREATIVE_BRIEF.md` (aesthetic keywords)
- `CANON_DB.json`
- `SHOW_BIBLE.md`

## Outputs Produced
- `STYLEGUIDE_VISUAL.md` - Complete visual style reference

## Process

### Step 1: Establish Global Aesthetic

From CREATIVE_BRIEF.md aesthetic keywords, define:

**Primary Style Category**:
- Photorealistic
- Stylized/Animated
- Hybrid
- Period-specific

**Reference Artists/Films** (for AI understanding):
- Visual touchstones that inform the look
- Specific cinematographers or directors
- Art movements or periods

### Step 2: Define Color Language

**Primary Palette**:
- 3-5 core colors that define the show
- Their emotional associations
- When each is emphasized

**Color by Context**:
| Context | Dominant Colors | Mood |
|---------|-----------------|------|
| Protagonist scenes | | |
| Antagonist scenes | | |
| Intimate moments | | |
| Action/tension | | |
| Resolution/calm | | |

**Color Grading Style**:
- Overall color temperature
- Shadow color bias
- Highlight treatment
- Saturation level

### Step 3: Define Lighting Style

**Lighting Philosophy**:
- Naturalistic vs. Stylized
- Key light preferences
- Shadow density
- Motivated vs. Expressive

**Standard Lighting Setups**:
| Scenario | Setup | Notes |
|----------|-------|-------|
| Dialogue (day interior) | | |
| Dialogue (night interior) | | |
| Exterior day | | |
| Exterior night | | |
| Emotional close-up | | |
| Action/tension | | |

### Step 4: Define Shot Taxonomy

Standard shot types for this production:

| Shot Type | Description | When to Use | Framing Notes |
|-----------|-------------|-------------|---------------|
| Establishing | Wide, shows full location | Scene opening | Include context |
| Wide | Full figures in environment | Action, geography | Room to move |
| Medium | Waist up | Standard dialogue | Most common |
| Medium Close | Chest up | Intimate dialogue | Emotional focus |
| Close-up | Face only | Emotion beats | Eye-level typical |
| Extreme CU | Detail (eyes, hands) | Emphasis | Selective use |
| Over-shoulder | From behind one character | Dialogue coverage | Shows relationship |
| Two-shot | Two characters in frame | Relationship focus | Balance composition |
| Insert | Object/detail | Information | Brief duration |
| POV | Character's view | Subjective moment | Match eyeline |

### Step 5: Camera Language

**Movement Philosophy**:
- Static preference vs. motivated movement
- Handheld usage
- Dolly/tracking preferences
- Crane/high angle usage

**Standard Movements**:
| Movement | Purpose | When Used |
|----------|---------|-----------|
| Push in | Increasing tension/intimacy | Key revelations |
| Pull back | Reveal, isolation | Surprise, loneliness |
| Track | Following action | Movement sequences |
| Pan | Survey environment | Establishing |
| Static | Stability, observation | Dialogue default |

### Step 6: Composition Guidelines

**Framing Conventions**:
- Rule of thirds application
- Headroom standards
- Looking room for dialogue
- Power dynamics through height

**Visual Hierarchy**:
- How to draw attention
- Focus/blur usage
- Foreground/background relationships

### Step 7: Character Visual Rules

For each major character, define:

**Locked Visual Anchors** (must appear in every image):
- Specific physical features
- Signature colors
- Consistent accessories

**Allowed Variations**:
- Outfit changes
- Expression range
- Lighting adaptation

**Prohibited Elements**:
- Things that would break character
- Anachronistic elements
- Inconsistent features

### Step 8: Location Visual Rules

For each key location:

**Establishing Requirements**:
- What must be visible to identify location
- Time-of-day variants
- Weather variants

**Consistency Elements**:
- Fixed architectural features
- Prop placements
- Lighting characteristics

### Step 9: Global Prompt Components

**Always Include**:
```
{{GLOBAL_STYLE_KEYWORDS}}
{{QUALITY_MARKERS}}
{{ASPECT_RATIO_PREFERENCE}}
```

**Never Include**:
```
{{GLOBAL_NEGATIVE_PROMPTS}}
```

### Step 10: Quality Standards

**Technical Requirements**:
- Resolution targets
- Aspect ratio standards
- Format preferences

**Consistency Metrics**:
- Acceptable character variation
- Lighting consistency requirements
- Color accuracy tolerance

## Style Guide Format

```markdown
# Visual Style Guide: {{SHOW_TITLE}}

## 1. Overview
[Quick summary of the visual identity]

## 2. Global Aesthetic
[Style category, references, mood]

## 3. Color Language
[Palette, meanings, grading]

## 4. Lighting
[Philosophy, setups, standards]

## 5. Shot Taxonomy
[Types, usage, framing]

## 6. Camera Language
[Movement philosophy, conventions]

## 7. Composition
[Framing rules, visual hierarchy]

## 8. Character Visual Rules
[Per-character anchors and variations]

## 9. Location Visual Rules
[Per-location consistency requirements]

## 10. Prompt Components
[Global inclusions and exclusions]

## 11. Quality Standards
[Technical requirements]

## 12. Reference Images
[Key reference images for AI guidance]
```

## Notes

- This guide is reference for all visual generation skills
- Update as visual references are created
- Serves as the "visual constitution" of the show
- All image prompts should align with these rules
- When in doubt, refer to this guide
