# Codeywood Architecture

> A modular framework for AI-assisted visual storytelling

## Overview

Codeywood uses a **hybrid architecture** that separates:

1. **Creative Work** (Claude) - Story development, quality evaluation, iteration suggestions
2. **Deterministic Execution** (n8n) - API calls, file management, pipeline orchestration
3. **Framework** - Reusable tools, knowledge, and skills (this repo root)
4. **Projects** - Individual productions using the framework (`projects/`)

```
┌─────────────────────────────────────────────────────────────┐
│                    CLAUDE (Creative)                        │
│  • Reads SKILL.md for production guidance                   │
│  • Generates plans, scripts, prompts                        │
│  • Evaluates quality and suggests iterations                │
└─────────────────────┬───────────────────────────────────────┘
                      │ n8n_run_workflow (via MCP)
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                    N8N (Deterministic)                      │
│  • Executes FAL.ai, Kling, Veo3 API calls                   │
│  • Manages file I/O and asset storage                       │
│  • Enforces quality gates                                   │
│  • Updates .state.json with execution results               │
└─────────────────────────────────────────────────────────────┘
```

This separation allows:
- **Inspectable workflows** - Open n8n, see exactly where you are
- **Manual intervention** - Pause, adjust parameters, resume
- **Reproducible execution** - Same inputs produce same outputs
- **Easy iteration** - Claude suggests, n8n executes, repeat

## State Management

Projects use two complementary files:

| File | Edited By | Purpose |
|------|-----------|---------|
| `PROJECT_CONFIG.yaml` | Humans | Style DNA, character definitions, model preferences |
| `.state.json` | n8n workflows | Pipeline state, gate status, execution history |

This separation ensures:
- Configuration is human-readable and git-friendly
- State is machine-managed and always accurate
- No merge conflicts between creative and operational data

See `schemas/state.schema.json` for the complete state schema.

## Directory Structure

```
codeywood/
├── README.md                      # Project overview
├── ARCHITECTURE.md                # This file
├── CONTRIBUTING.md                # Contribution guidelines
├── QUICKSTART.md                  # Getting started
│
├── scripts/                       # CLI tools (project-agnostic)
│   └── generate/
│       ├── fal_generate.py        # FAL.ai generation tool
│       ├── requirements.txt       # Python dependencies
│       └── README.md              # Tool documentation
│
├── references/                    # Cross-project knowledge base
│   ├── KNOWLEDGE_BASE.md          # Master knowledge file
│   ├── services/                  # Service-specific techniques
│   │   ├── nano-banana-pro/
│   │   ├── midjourney/
│   │   └── runway-gen3/
│   ├── modalities/                # Modality approaches
│   │   ├── animation/
│   │   ├── live-action/
│   │   └── hybrid/
│   └── story_structure/           # Story/narrative references
│
├── skills/                        # Claude skill definitions
│   ├── core/                      # Story development skills
│   ├── production/                # Visual production skills
│   └── meta/                      # System management skills
│
├── templates/                     # Project scaffolding
│   ├── PROJECT_CONFIG.yaml        # Configuration template
│   └── project-scaffold/          # Full project template
│
├── projects/                      # Individual productions
│   └── hellmouth-cowboy/          # Example: Hellmouth Cowboy
│       ├── PROJECT_CONFIG.yaml    # Project configuration
│       ├── STORY/                 # Story artifacts
│       ├── VISUAL_PRODUCTION/     # Visual production
│       └── EXPORTS/               # Generated assets
│
├── examples/                      # Learning examples
├── docs/                          # Documentation site
└── tests/                         # Testing infrastructure
```

## Key Concepts

### Project Configuration

Each project has a `PROJECT_CONFIG.yaml` that defines:
- Project metadata (name, modality)
- Visual settings (models, sizes)
- Locked Style DNA (medium, linework, lighting, palette)
- Character configurations (names, palettes)
- File paths

The generation tools read this config and produce consistent results across all characters/assets.

### Style DNA

A Style DNA template deconstructs a visual style into components:
- **Medium/Era**: Animation style, time period, references
- **Line-work/Texture**: How edges and surfaces render
- **Lighting/Rendering**: Shadow approach, contrast, atmosphere
- **Color Palette**: Dominant tones, accents, saturation

This allows precise style control without referencing copyrighted IPs.

### Dual-Model Workflow

Validated workflow for visual production:
- **SeeDream v4.5**: Primary for artistic/hero shots (emotion, atmosphere)
- **Nano Banana Pro**: Technical for identity sheets (layout control, precision)

### Visual Production Phases

1. **Phase 0**: Modality Selection
2. **Phase 1**: Style DNA Exploration (3-4 directions → lock winner)
3. **Phase 2**: Hero Shots (3 per character → establish presence)
4. **Phase 3**: Identity Sheets (8-panel composite layouts)
5. **Phase 4**: Supplementary Refs (optional)
6. **Phase 5**: Location Refs (2×2 composite grids)
7. **Phase 6**: Storyboards (3×2 shot grids for key scenes)
8. **Phase 7**: Action Sequences (optional, for detailed choreography)

### Composite Layout Prompting

Instead of generic "turnaround" requests, use explicit panel descriptions:
```
TOP ROW: Eye close-up | Face profile | Hand reference
MIDDLE SECTION: Full body front | Full body back
BOTTOM ROW: Portrait | Action pose | Quiet moment
```

This produces predictable, consistent results.

## Generation Tools

### Setup

```bash
cd scripts/generate
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
export FAL_KEY="your_api_key"
```

### Usage

From your project directory:

```bash
# Style DNA exploration
python /path/to/codeywood/scripts/generate/fal_generate.py --test style_dna

# Hero shots
python /path/to/codeywood/scripts/generate/fal_generate.py --hero character-slug

# Identity sheets
python /path/to/codeywood/scripts/generate/fal_generate.py --identity character-slug

# Location references (single)
python /path/to/codeywood/scripts/generate/fal_generate.py --location location-slug

# All locations (batch)
python /path/to/codeywood/scripts/generate/fal_generate.py --all-locations

# Storyboard scenes (single)
python /path/to/codeywood/scripts/generate/fal_generate.py --storyboard sc01-cold-open

# All storyboards (batch)
python /path/to/codeywood/scripts/generate/fal_generate.py --all-storyboards
```

## Creating a New Project

1. Copy `templates/project-scaffold/` to `projects/your-project/`
2. Copy `templates/PROJECT_CONFIG.yaml` to your project
3. Create character sheets in `STORY/CHARACTER_SHEETS/`
4. Run style DNA exploration
5. Lock winning Style DNA in config
6. Generate hero shots and identity sheets

## Validated Results

The framework has been validated with Hellmouth Cowboy:
- 15 style test images (3 templates × 3 scenarios + Nano Banana tests)
- 9 hero shots (3 characters × 3 shots each)
- 3 identity sheets (one per character)
- 5 location reference grids (2×2 composite layouts)
- 3 storyboard scenes (3×2 composite grids for EP01 priority scenes)
- 1 character-in-location test composition
- All locked in PROJECT_CONFIG.yaml with extracted palettes
- Autonomous batch generation validated for locations and storyboards

## Contributing

See `CONTRIBUTING.md` for guidelines.

When adding to the knowledge base:
1. Test techniques across multiple generations
2. Document what works AND what fails
3. Include example prompts with results
4. Note service version/date

## Version History

- **v0.4** (2026-01-31): Added location reference generation, autonomous batch generation (--all-locations flag)
- **v0.3** (2026-01-29): Refactored architecture, project-agnostic generation tools
- **v0.2** (2026-01-28): Visual production pipeline, Hellmouth Cowboy validation
- **v0.1** (2026-01-26): Initial story skills and structure
