---
name: canon-database-manager
description: "Creates and maintains CANON_DB.json, the machine-readable source of truth for all visual generation and consistency checking. Extracts characters, locations, props, visual style, factions, and canon facts from Phase 1 story artifacts. Use when all Phase 1 artifacts pass Gate 5 and the visual production pipeline needs a structured data source."
---

# Canon Database Manager

Create and maintain `CANON_DB.json` — the machine-readable source of truth that powers all visual generation, reference creation, and consistency checking across the production pipeline.

## Inputs

- `CREATIVE_BRIEF.md` — aesthetic keywords and visual style
- `CHARACTER_SHEETS/*.md` — psychology, visual descriptions, voice profiles
- `RELATIONSHIP_MAP.json` — scored relationship axes
- `EP{{XX}}_SCENELIST.md` — all episode scene lists (locations, time-of-day)
- `SCRIPTS/SCRIPT_EP{{XX}}.md` — all episode scripts (action descriptions, props)
- `SHOW_BIBLE.md` — consolidated canon facts

## Outputs

- `CANON_DB.json` — structured database with meta, characters, locations, props, visual_style, factions, canon_facts, and continuity_log sections

## Process

### Step 1: Initialize Database Structure

Create the base `CANON_DB.json`:

```json
{
  "meta": { "show_title": "", "version": "1.0.0", "last_updated": "", "knowledge_cutoff": "", "phase": "PRE_VISUAL" },
  "characters": {},
  "locations": {},
  "props": {},
  "visual_style": {},
  "factions": {},
  "canon_facts": [],
  "continuity_log": []
}
```

### Step 2: Extract Characters

For each character in `CHARACTER_SHEETS/`:

1. Create ID in `UPPERCASE_SNAKE_CASE` (e.g., `ALICE_CHEN`)
2. Extract psychology: want, need, lie, wound, virtue_with_cost
3. Extract visual data: physical description (prompt-optimized), signature outfit, color palette, signature props, negative prompts. Initialize empty `reference_images` object
4. Extract voice data: sentence length, metaphor domain, sarcasm/directness levels, linguistic fingerprints, taboo topics
5. Convert relationships from `RELATIONSHIP_MAP.json` with all axes and bond/pressure mechanisms

### Step 3: Extract Locations

Scan all `SCENELIST` files for unique locations:

1. Create ID in `UPPERCASE_SNAKE_CASE`
2. Determine type: primary / secondary / recurring / one-off
3. Extract visual data: description, time variants needed, key areas, mood. Initialize empty `reference_images` object
4. Define blocking rules where applicable (standard character positions, furniture placement)

### Step 4: Extract Props

Identify signature, functional, and environmental props from `CHARACTER_SHEETS` and scripts. Create ID, set type and owner, write description and significance, initialize empty `reference_images`.

### Step 5: Define Visual Style

Populate from `CREATIVE_BRIEF.md` aesthetic section: global_aesthetic, color_grading, lighting_style, lens_language, camera_movement, and shot_taxonomy.

### Step 6: Extract Factions, Canon Facts, and Continuity Log

- **Factions**: organizational groupings with member IDs, values, and inter-faction conflicts
- **Canon facts**: immutable timeline events, character history, world rules, relationship history
- **Continuity log**: initialized empty, grows with each update (date, change, affected_artifacts, reason)

### Step 7: Validate Completeness

- [ ] All characters from `CHARACTER_SHEETS` are present
- [ ] All locations from scene lists are present
- [ ] All relationships from `RELATIONSHIP_MAP.json` are present
- [ ] Visual descriptions are prompt-ready (no placeholders)

See `templates/CANON_DB_schema.json` for the complete JSON schema.

## Update Protocol

When updating an existing `CANON_DB.json`:

1. Read current version
2. Make targeted changes only
3. Increment `meta.version` (semver)
4. Update `meta.last_updated`
5. Add entry to `continuity_log`
6. Validate against schema

## Notes

- All IDs use `UPPERCASE_SNAKE_CASE`; character IDs follow `FIRST_LAST` format
- `CANON_DB.json` is the single source of truth — all reference generators read from it
- Visual reference paths are populated by downstream generator skills, not by this skill
- Never edit `CANON_DB.json` directly in scripts — always use this skill to maintain the continuity log
