---
name: prop-reference-generator
description: "Generates consistent reference images for signature props, plot-critical objects, and recurring items using CANON_DB.json data and style guidelines. Produces isolated, in-context, and detail close-up shots for each prop. Use when CANON_DB.json and STYLEGUIDE_VISUAL.md exist and prop references need to be created for visual production."
---

# Prop Reference Generator

Generate reference images for signature props and objects that need consistent appearance across shots. Reads prop definitions from `CANON_DB.json`, applies the show's visual style from `STYLEGUIDE_VISUAL.md`, and produces a categorized reference pack for each prop.

## Inputs

- `CANON_DB.json` — props section with type, owner, description, significance
- `STYLEGUIDE_VISUAL.md` — global aesthetic and style keywords
- `CHARACTER_SHEETS/*.md` — for signature prop ownership and interaction context

## Outputs

- `PROP_REFS/{PROP}/refs/*.png` — isolated, context, and detail reference images
- Updated `CANON_DB.json` — reference image paths added to each prop entry

## Process

### Step 1: Identify and Prioritize Props

Extract props from `CANON_DB.json` and `CHARACTER_SHEETS`. Assign priority:

| Priority | Category | Reference Scope |
|----------|----------|-----------------|
| High | Signature character props | All three reference types |
| High | Plot McGuffins | Isolated + detail |
| Medium | Frequently seen objects | Isolated + context |
| Low | Background props | Skip unless appears in close-ups |

### Step 2: Extract Prop Data

Read each prop's entry from `CANON_DB.json`:

```json
{
  "type": "signature",
  "owner": "CHARACTER_ID",
  "description": "Worn leather-bound notebook, frayed bookmark",
  "significance": "Contains all case notes, never out of sight"
}
```

### Step 3: Generate Isolated Reference

Load `prompts/isolated_prop.txt` and substitute variables. Generate a clean studio shot:

- White or neutral background
- Multiple angles where possible
- Full detail visibility, material texture clear

**Prompt template example:**
```
{{PROP_DESCRIPTION}}, product photography style, clean white background,
studio lighting, multiple angles visible, high detail,
{{MATERIAL_DESCRIPTION}}, {{STYLE_KEYWORDS}}

Negative: people, hands, cluttered background, shadows, low detail
```

Save as `refs/{prop}_isolated.png`.

### Step 4: Generate Context Shots

Show the prop in typical use — with its owner character (using character reference images for consistency) in a natural environment. Save as `refs/{prop}_context.png`.

### Step 5: Generate Detail Shots

For high-priority props, generate close-ups of distinctive features: texture, material, markings, text. Save as `refs/{prop}_detail.png`.

### Step 6: Update CANON_DB

Add generated reference paths to each prop entry:

```json
"reference_images": {
  "isolated": "PROP_REFS/ALICE_NOTEBOOK/refs/notebook_isolated.png",
  "in_hand": "PROP_REFS/ALICE_NOTEBOOK/refs/notebook_hand.png",
  "detail": "PROP_REFS/ALICE_NOTEBOOK/refs/notebook_detail.png"
}
```

## Notes

- Signature props get full treatment (all three reference types)
- Use character reference images when generating interaction shots for consistency
- Props must match the show's locked visual style — apply `STYLEGUIDE_VISUAL.md` keywords
- Background props rarely need dedicated references unless they appear in insert shots
