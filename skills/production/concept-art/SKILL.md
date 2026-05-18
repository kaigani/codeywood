# Concept Art Skill

## Purpose
Generate a project-wide concept-art pack — pencil + watercolor sketches of all key locations, characters, and 2-3 key scenes per episode — for early visual development, pitch decks, and director reference. Uses the local ComfyUI `z-image-base-t2i` workflow.

This is **not** a storyboard. It's a sketchbook pass: loose, expressive, atmospheric, suitable for blocking out the look before committing to photorealistic refs or storyboards.

## Trigger
- New project entering Phase 1 (visual development) or earlier
- Need a single-image style sketch of a place, character, or pivotal moment
- Pitch deck or director hand-off requires loose visual reference

## Inputs Required
- `projects/{name}/CONCEPT_ART/subjects.yaml` — defines all subjects (start from `scripts/production/concept_art/subjects_template.yaml`)
- Local ComfyUI reachable at `http://192.168.1.181:8100` with the `z-image-base-t2i` workflow loaded
- Project venv activated: `source scripts/venv/bin/activate` (supplies `pyyaml`, `Pillow`, `requests`)

## Outputs Produced
- `projects/{name}/CONCEPT_ART/locations/{id}.png` — 1536×1024 environment plates
- `projects/{name}/CONCEPT_ART/characters/{id}.png` — 1024×1536 full-body sheets
- `projects/{name}/CONCEPT_ART/scenes/ep##_{name}.png` — 1536×1024 scene moments
- `projects/{name}/CONCEPT_ART/scenes_contact_sheet.png` — episode-grouped review grid
- `projects/{name}/CONCEPT_ART/contact_sheet.png` — locations + characters review grid

## How It Works

### 1. Style block (locked, in `scripts/production/concept_art/_common.py`)
Every prompt is prefixed with the pencil+watercolor `STYLE_BLOCK`. This is the medium constraint — do not override per subject.

### 2. Z-Image 4-layer prompt structure
Each `subjects.yaml` entry must supply:
- **subject_action** — what's in the frame (objective, concrete; no "mystical / ethereal" vibe words)
- **composition** — shot type, angle, line + wash treatment
- **lighting** — color palette + atmosphere (this is where the mood lives)
- **text_factor** — verbatim quoted margin caption (1-5 words)

### 3. Subject categories and sizing
| Category | Size | Use |
|---|---|---|
| `locations` | 1536×1024 wide | One per key environment |
| `characters` | 1024×1536 portrait | One per named character |
| `scenes` | 1536×1024 wide | 2-3 per episode |

### 4. Scene naming convention
Scenes must use `ep##_<name>` IDs (e.g. `ep01_temple_sprint`). The contact sheet groups by the `ep##` prefix automatically.

## Process

### Step 1 — Author subjects.yaml
```bash
source scripts/venv/bin/activate
mkdir -p projects/{name}/CONCEPT_ART
cp scripts/production/concept_art/subjects_template.yaml \
   projects/{name}/CONCEPT_ART/subjects.yaml
```
Fill in 5-12 locations, all named characters, and 2-3 scenes per episode. Use the existing `projects/260513-gemma-anthology/CONCEPT_ART/subjects.yaml` as a reference for tone and detail level.

### Step 2 — Dry-run
```bash
python3 scripts/production/concept_art/generate.py \
  --project projects/{name} --dry-run
```
Confirms subject count and seed assignments without hitting the workflow.

### Step 3 — Generate
```bash
caffeinate -i python3 scripts/production/concept_art/generate.py \
  --project projects/{name}
```
Run in foreground if small (<20 subjects, ~10 min), background if larger:
```bash
caffeinate -i bash -c "python3 scripts/production/concept_art/generate.py \
  --project projects/{name} 2>&1 | tee projects/{name}/CONCEPT_ART/generate.log" &
```

Throughput: ~25-30s per image on the local ComfyUI; 28 subjects ≈ 13 min.

Optional flags:
- `--kind locations|characters|scenes` — generate one section
- `--only <id>` — single subject
- `--force` — regenerate existing files

### Step 4 — Build contact sheets
```bash
python3 scripts/production/concept_art/contact_sheets.py \
  --project projects/{name}
```
Produces `scenes_contact_sheet.png` (episode-grouped) and `contact_sheet.png` (locations + characters).

### Step 5 — Iterate
If the style misses, adjust `STYLE_BLOCK` in `scripts/production/concept_art/_common.py` and regenerate with `--force`. If a subject misses, edit just that entry and run with `--only <id> --force`.

## Z-Image Operational Rules (baked into the prompt builder)

- **No meta-tags.** Do not write "8K, masterpiece, photorealistic, ultra-detailed" — Z-Image was trained to ignore these. Describe the medium concretely (already done in `STYLE_BLOCK`).
- **Negatives are weak.** CFG is effectively 0; the `NEGATIVE` field is a placeholder. Push the clean state into the positive prompt.
- **Text strings ≤ 5 words.** Z-Image renders quoted strings verbatim with English glyphs. Keep margin captions short.
- **Addition not subtraction.** Describe what you want, not what you don't want.

## Common Failures and Fixes

| Failure | Cause | Fix |
|---|---|---|
| Photorealistic output instead of sketch | Subject prose includes "photograph", "render", "cinematic" | Strip those words; STYLE_BLOCK does the heavy lifting |
| Wrong palette | `lighting` field too generic | Name specific colors (magenta neon, sodium-amber, bile-green) |
| Missing margin caption | `text_factor` too long or unquoted | Cap at 5 words, wrap in `"..."` |
| Scenes ungrouped on contact sheet | Scene `id` not prefixed `ep##_` | Rename in YAML + on disk |
| All 15+ jobs fail to connect | ComfyUI engine on port 8000 crashed | Check `/health`; user must restart ComfyUI |

## Status Logging Conventions

When narrating progress to the user during a generation run:
- `[health]` ComfyUI reachable / degraded
- `[dry-run]` subject count and IDs by kind
- `[gen]` running subject count `(n/total, kind)`
- `[contact]` contact-sheet sizes after build

## Reference

- Workflow: `z-image-base-t2i` (local ComfyUI, port 8100)
- Driver: `scripts/production/concept_art/generate.py`
- Shared helpers: `scripts/production/concept_art/_common.py`
- Contact sheets: `scripts/production/concept_art/contact_sheets.py`
- Template: `scripts/production/concept_art/subjects_template.yaml`
- Worked example: `projects/260513-gemma-anthology/CONCEPT_ART/subjects.yaml` (7 locations, 6 characters, 28 scenes across 10 episodes)
