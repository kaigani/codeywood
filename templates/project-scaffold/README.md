# Project Name

> One-line description of your project

## Quick Start

1. Copy this scaffold to `projects/your-project-name/`
2. Copy `templates/PROJECT_CONFIG.yaml` to your project and customize
3. Run style DNA exploration to lock your visual language
4. Generate hero shots and identity sheets for your characters

## Project Structure

```
your-project/
├── PROJECT_CONFIG.yaml      # Project configuration (REQUIRED)
├── README.md                # This file
│
├── STORY/                   # Story artifacts
│   ├── CREATIVE_BRIEF.md
│   ├── LOGLINE_LOCK.md
│   ├── SEASON_GRID.md
│   ├── EP01_BEATS.md
│   └── CHARACTER_SHEETS/    # Character definitions
│       ├── CHARACTER_A.md
│       └── CHARACTER_B.md
│
├── VISUAL_PRODUCTION/       # Visual production pipeline
│   ├── WORKFLOW.md          # Production workflow documentation
│   ├── STYLE_GUIDE/         # Locked style references
│   │   ├── STYLE_PROMPTS.md
│   │   └── examples/        # Style reference images
│   ├── CHARACTER_REFS/      # Per-character reference materials
│   ├── LOCATION_REFS/       # Per-location reference materials
│   ├── STORYBOARDS/         # Episode storyboards
│   └── ACTION_SEQUENCES/    # Action sequence breakdowns
│
└── EXPORTS/                 # Generated assets
    ├── style_tests/         # Style DNA exploration outputs
    ├── hero_shots/          # Per-character hero shots
    │   ├── character-a/
    │   └── character-b/
    └── identity_sheets/     # Character identity sheets
```

## Visual Production Workflow

1. **Phase 0**: Choose modality (animation, live-action, hybrid)
2. **Phase 1**: Style DNA exploration - test 3-4 directions, lock winner
3. **Phase 2**: Hero shots - establish character presence
4. **Phase 3**: Identity sheets - technical reference panels
5. **Phase 4+**: Locations, storyboards, action sequences

See `references/KNOWLEDGE_BASE.md` for detailed best practices.

## Generation Commands

```bash
# Run from this project directory

# Style DNA exploration
python /path/to/codeywood/scripts/generate/fal_generate.py --test style_dna

# Hero shots
python /path/to/codeywood/scripts/generate/fal_generate.py --hero character-slug

# Identity sheets
python /path/to/codeywood/scripts/generate/fal_generate.py --identity character-slug
```
