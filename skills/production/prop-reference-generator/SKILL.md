# Prop Reference Generator Skill

## Purpose
Generate reference images for signature props and objects that need consistent appearance across shots.

## Trigger
CANON_DB.json and STYLEGUIDE_VISUAL.md exist.

## Inputs Required
- `CANON_DB.json` (props data)
- `STYLEGUIDE_VISUAL.md`
- `CHARACTER_SHEETS/*.md` (for signature props)

## Outputs Produced
- `PROP_REFS/{PROP}/refs/*.png` - Reference images
- Updated `CANON_DB.json` (reference paths added)

## Reference Types Required

For each signature prop:

### 1. Isolated Object
- Clean background
- Multiple angles
- Detail visible

### 2. In Context
- With owner/user
- In typical usage

### 3. Detail Close-ups
- Specific important features
- Texture and material

## Process

### Step 1: Identify Required Props

From CANON_DB.json and CHARACTER_SHEETS:
- Signature props (character-associated)
- Plot-critical objects
- Recurring items

**Priority**:
- Signature character props (high)
- Plot McGuffins (high)
- Frequently seen objects (medium)
- Background props (low - may not need refs)

### Step 2: Extract Prop Data

From CANON_DB.json:
```json
{
  "type": "signature",
  "owner": "CHARACTER_ID",
  "description": "...",
  "significance": "..."
}
```

### Step 3: Generate Isolated Reference

Load prompt template:
```
prompts/isolated_prop.txt
```

Create clean object shot:
- White/neutral background
- Multiple angles if possible
- Clear detail visibility

Save as `refs/{prop}_isolated.png`

### Step 4: Generate Context Shots

Show prop in typical use:
- With character (if signature prop)
- In typical environment
- Natural interaction

Use character reference as input for consistency.

Save as `refs/{prop}_context.png`

### Step 5: Generate Detail Shots

For important props:
- Close-up of distinctive features
- Texture/material clarity
- Any text/markings

Save as `refs/{prop}_detail.png`

### Step 6: Update CANON_DB

Add reference paths:
```json
"reference_images": {
  "isolated": "PROP_REFS/ALICE_NOTEBOOK/refs/notebook_isolated.png",
  "in_hand": "PROP_REFS/ALICE_NOTEBOOK/refs/notebook_hand.png",
  ...
}
```

## Prompt Template

### prompts/isolated_prop.txt

```
{{PROP_DESCRIPTION}}, product photography style, clean white background, studio lighting, multiple angles visible, high detail, {{MATERIAL_DESCRIPTION}}, {{STYLE_KEYWORDS}}

Negative: people, hands, cluttered background, shadows, low detail
```

## Prop Categories

### SIGNATURE PROPS
Items associated with specific characters.
- Generate all reference types
- Include character interaction shots

### PLOT PROPS
Items critical to story.
- Generate isolated + detail
- Ensure distinctive features are clear

### ENVIRONMENT PROPS
Items that define locations.
- May only need establishing shot inclusion
- Generate if appears in close-ups

## Notes

- Signature props get full treatment
- Plot props need distinctive features visible
- Background props may not need dedicated references
- Use character references when generating interaction shots
- Props should match show's visual style
