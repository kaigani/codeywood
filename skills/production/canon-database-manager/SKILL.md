# Canon Database Manager Skill

## Purpose
Create and maintain CANON_DB.json - the machine-readable source of truth that powers all visual generation and consistency checking.

## Trigger
All Phase 1 (story foundation) artifacts pass Gate 5.

## Inputs Required
- `CREATIVE_BRIEF.md`
- `CHARACTER_SHEETS/*.md`
- `RELATIONSHIP_MAP.json`
- `EP{{XX}}_SCENELIST.md` (all episodes)
- `SCRIPTS/SCRIPT_EP{{XX}}.md` (all episodes)
- `SHOW_BIBLE.md`

## Outputs Produced
- `CANON_DB.json` - Machine-readable canon database

## Process

### Step 1: Initialize Database Structure

Create the base CANON_DB.json with all required sections:

```json
{
  "meta": {},
  "characters": {},
  "locations": {},
  "props": {},
  "visual_style": {},
  "factions": {},
  "canon_facts": [],
  "continuity_log": []
}
```

### Step 2: Populate Meta Section

```json
"meta": {
  "show_title": "",
  "version": "1.0.0",
  "last_updated": "",
  "knowledge_cutoff": "",
  "phase": "PRE_VISUAL"
}
```

### Step 3: Extract Characters

For each character in CHARACTER_SHEETS:

1. **Create character ID**: UPPERCASE_SNAKE_CASE (e.g., "ALICE_CHEN")

2. **Extract psychology**:
   - want, need, lie, wound from character sheet
   - virtue_with_cost

3. **Extract visual data**:
   - Physical description (prompt-optimized)
   - Signature outfit
   - Color palette
   - Signature props
   - Negative prompts
   - Initialize empty reference_images object

4. **Extract voice data**:
   - Sentence length pattern
   - Metaphor domain
   - Sarcasm/directness levels
   - Linguistic fingerprints
   - Taboo topics

5. **Extract relationships**:
   - Convert from RELATIONSHIP_MAP.json
   - Include all axes, bond/pressure mechanisms

### Step 4: Extract Locations

Scan all SCENELIST files for unique locations:

1. **Create location ID**: UPPERCASE_SNAKE_CASE

2. **Determine type**: primary / secondary / recurring / one-off

3. **Extract visual data**:
   - Description from scene headers
   - Time variants needed (from scenes)
   - Key areas (from action descriptions)
   - Mood associations
   - Initialize empty reference_images object

4. **Define blocking rules** (if applicable):
   - Standard character positions
   - Key furniture/feature placement

### Step 5: Extract Props

Identify signature props from CHARACTER_SHEETS and scripts:

1. **Create prop ID**: UPPERCASE_SNAKE_CASE

2. **Define properties**:
   - type: signature / functional / environmental
   - owner (if character-specific)
   - description
   - significance
   - Initialize empty reference_images object

### Step 6: Define Visual Style

From CREATIVE_BRIEF.md aesthetic section:

```json
"visual_style": {
  "global_aesthetic": "",
  "color_grading": "",
  "lighting_style": "",
  "lens_language": "",
  "camera_movement": "",
  "shot_taxonomy": {}
}
```

### Step 7: Extract Factions/Groups

If applicable, identify organizational groupings:

- Members list (character IDs)
- Values
- Conflicts with other factions

### Step 8: Compile Canon Facts

List all established facts that cannot be contradicted:

- Timeline events
- Character history facts
- World rules
- Relationship history

### Step 9: Initialize Continuity Log

Empty array ready for tracking changes:

```json
"continuity_log": [
  {
    "date": "",
    "change": "",
    "affected_artifacts": [],
    "reason": ""
  }
]
```

### Step 10: Validate Completeness

Check that:
- [ ] All characters from CHARACTER_SHEETS are present
- [ ] All locations from SCENELISTs are present
- [ ] All relationships from RELATIONSHIP_MAP are present
- [ ] Visual descriptions are prompt-ready
- [ ] No placeholder text remains

## Schema Reference

See `templates/CANON_DB_schema.json` for complete JSON schema.

## Key Design Principles

### IDs
- All IDs are UPPERCASE_SNAKE_CASE
- Character IDs match first_last format
- Location IDs are descriptive but concise

### Visual Descriptions
- Optimized for image generation prompts
- Include specific, concrete details
- Include negative prompts (what to avoid)
- Reference images start empty, populated by generators

### Relationships
- Bidirectional (A→B stored under A, includes B reference)
- Axes use -5 to +5 scale
- Arc directions describe season trajectory

### Extensibility
- New fields can be added
- Reference_images objects expand as images are generated
- Continuity_log grows with each update

## Update Protocol

When updating CANON_DB.json:

1. Read current version
2. Make targeted changes only
3. Update meta.version (semver)
4. Update meta.last_updated
5. Add entry to continuity_log
6. Validate against schema

## Notes

- CANON_DB.json is the single source of truth for visual generation
- All reference generators read from this database
- Updates must be logged in continuity_log
- Never edit directly in scripts—use this skill
- Visual reference paths are added by generators, not this skill
