# Location Reference Generator Skill

## Purpose
Generate comprehensive location reference image packs that enable consistent environment reproduction across all shots.

## Trigger
CANON_DB.json and STYLEGUIDE_VISUAL.md exist.

## Inputs Required
- `CANON_DB.json` (location data)
- `STYLEGUIDE_VISUAL.md`
- `EP{{XX}}_SCENELIST.md` (for location requirements)

## Outputs Produced
- `LOCATION_REFS/{LOCATION}/VISUAL_SPEC.md` - Location visual specification
- `LOCATION_REFS/{LOCATION}/refs/*.png` - Reference images
- Updated `CANON_DB.json` (reference paths added)

## Reference Types Required

For each key location, generate:

### 1. Establishing Shot (Wide)
- Full view of location
- Shows context and surroundings
- Defines spatial relationships

### 2. Key Areas (3-5 per location)
- Specific zones within location
- Places where action commonly occurs
- Different angles of important features

### 3. Time Variants
- Day version
- Night version
- Golden hour (if applicable)
- Specific times from script

### 4. Weather Variants (if needed)
- Clear/default
- Rain (if script requires)
- Other weather as needed

### 5. Empty vs. Populated
- Empty reference (for consistency)
- With characters (for scale/blocking)

## Process

### Step 1: Identify Required Locations

From CANON_DB.json and SCENELISTs:
- List all unique locations
- Categorize: primary / secondary / recurring / one-off
- Prioritize by scene count

### Step 2: Extract Location Data

From CANON_DB.json, retrieve:
```json
{
  "description": "...",
  "mood": "...",
  "visual": {
    "time_variants": [...],
    "key_areas": [...],
    "color_palette": [...],
    "lighting_signature": "...",
    "negative_prompts": [...]
  },
  "blocking_rules": [...]
}
```

### Step 3: Create Visual Specification

Generate `LOCATION_REFS/{LOCATION}/VISUAL_SPEC.md`:

```markdown
# Location Visual Specification: {{LOCATION_NAME}}

## Description
{{FROM_CANON_DB}}

## Key Features
- {{FEATURE_1}}
- {{FEATURE_2}}

## Color Palette
{{COLORS}}

## Lighting
{{LIGHTING_SIGNATURE}}

## Key Areas
1. {{AREA_1}}
2. {{AREA_2}}
3. {{AREA_3}}

## Blocking Rules
{{RULES}}

## Negative Prompts
{{NEGATIVES}}

## Reference Status
- [ ] Establishing wide
- [ ] Key areas
- [ ] Time variants
- [ ] Weather variants
```

### Step 4: Generate Establishing Shot (SEED)

Load prompt template:
```
prompts/establishing_shot.txt
```

Construct prompt:
1. Insert location description
2. Add key features
3. Add style keywords from STYLEGUIDE
4. Add negative prompts

**API Call**:
Generate wide shot that becomes the SEED reference.

Save as `refs/{location}_establishing_wide.png`

### Step 5: Generate Key Areas

Use establishing shot as reference.

For each key area:
1. Load `prompts/key_areas.txt`
2. Describe specific area
3. Include establishing as reference
4. Set reference_weight: 0.85

Save as `refs/{location}_{area_name}.png`

### Step 6: Generate Time Variants

Use establishing shot as reference.

For each time variant:
1. Load `prompts/time_variants.txt`
2. Modify lighting description
3. Include establishing as reference
4. Set reference_weight: 0.80 (allow lighting change)

Save as `refs/{location}_{time}.png`

### Step 7: Generate Weather Variants

Use establishing shot as reference.

For required weather conditions:
1. Modify for weather effects
2. Include establishing as reference
3. Set reference_weight: 0.75 (allow significant change)

Save as `refs/{location}_{weather}.png`

### Step 8: Update CANON_DB

Add reference paths to location entry:

```json
"reference_images": {
  "establishing_wide": "LOCATION_REFS/PRECINCT_BULLPEN/refs/bullpen_wide.png",
  "alice_desk": "LOCATION_REFS/PRECINCT_BULLPEN/refs/bullpen_alice_desk.png",
  ...
}
```

### Step 9: Quality Check

For each generated image:
- [ ] Matches description
- [ ] Key features present
- [ ] Lighting consistent with style
- [ ] Mood is appropriate
- [ ] Scale is correct

## Prompt Templates

Located in `prompts/`:

### establishing_shot.txt
Wide establishing shots of locations.

### key_areas.txt
Specific zones within locations.

### time_variants.txt
Same location at different times.

## Location Priority Tiers

**Tier 1 - Generate All Reference Types**:
- Primary recurring locations
- Most scenes take place here

**Tier 2 - Generate Establishing + Key Areas**:
- Secondary locations
- Multiple scenes but not primary

**Tier 3 - Generate Establishing Only**:
- One-off locations
- Background settings

## Notes

- Establishing shot is the SEED for all variants
- Maintain architectural consistency across variants
- Lighting changes are the main differentiator for time variants
- Keep key features visible in all angles
- Update CANON_DB after successful generation
