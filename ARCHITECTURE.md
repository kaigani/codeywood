# Codeywood Architecture

> A modular framework for AI-assisted visual storytelling

## First Principle: Agentic-First

**The entire system is designed for agentic orchestration by Claude.**

This is not a pipeline system where Claude follows rigid workflows. It is an adaptive
system where Claude:

1. **Retrieves data** - Reads configs, state, and generated assets
2. **Structures decisions** - Plans next steps based on current state
3. **Executes scripts** - Calls generalized Python tools via Bash
4. **Reviews outputs** - Evaluates results (images, video frames, clips)
5. **Adapts** - Adjusts subsequent steps based on what actually happened

```
┌─────────────────────────────────────────────────────────────────────┐
│                    CLAUDE (Orchestrator)                            │
│                                                                     │
│  1. Read state: PROJECT_CONFIG.yaml, .state.json, generated assets  │
│  2. Decide: What needs to happen next?                              │
│  3. Execute: Call script via Bash                                   │
│  4. Review: Read/view output, assess quality                        │
│  5. Adapt: Adjust plan based on actual results                      │
│  6. Loop: Repeat until goal achieved                                │
│                                                                     │
└────────────────────────┬────────────────────────────────────────────┘
                         │ Bash (direct script invocation)
                         ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    SCRIPTS (Generalized Primitives)                 │
│                                                                     │
│  Scripts are TOOLS, not workflows. They:                            │
│  • Accept parameters via CLI (no hardcoded values)                  │
│  • Execute a single, well-defined operation                         │
│  • Return structured results (file paths, JSON metadata)            │
│  • Don't encode workflow logic (Claude decides what to call)        │
│  • Codify best practices for API calls and data validation          │
│                                                                     │
│  Examples:                                                          │
│  • fal_generate.py --hero mars          # Generate hero shot        │
│  • generate_clips.py --clip 1           # Generate single clip      │
│  • validate.py --scene sc02             # Validate scene assets     │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Why Agentic-First?

**Non-deterministic outputs require adaptive decisions.**

AI generation models (image, video) produce non-deterministic results. A pre-planned
pipeline cannot anticipate what the model will actually generate. The system must:

- Review each output before proceeding
- Adjust subsequent prompts based on actual results
- Insert bridge content when continuity gaps appear
- Re-generate when quality is insufficient

Only an agentic approach can make these real-time decisions.

### What This Means in Practice

| Aspect | Old Approach (Pipeline) | Agentic-First |
|--------|-------------------------|---------------|
| Workflow | Predefined sequence | Claude decides next step |
| Scripts | Workflow-specific | Generalized primitives |
| State | Updated by automation | Updated by scripts, read by Claude |
| Quality gates | Automated pass/fail | Claude reviews and decides |
| Adaptation | Manual intervention | Built into the loop |
| Error handling | Stop and alert | Claude diagnoses and adjusts |

## Overview

Codeywood uses a **layered architecture**:

1. **Claude** (Orchestrator) - Reads state, makes decisions, executes scripts, reviews outputs
2. **Scripts** (Primitives) - Generalized tools that execute single operations
3. **Framework** - Reusable knowledge, skills documentation, and templates (this repo root)
4. **Projects** - Individual productions using the framework (`projects/`)

## State Management

Projects use two complementary files:

| File | Edited By | Read By | Purpose |
|------|-----------|---------|---------|
| `PROJECT_CONFIG.yaml` | Humans | Claude, Scripts | Style DNA, characters, model preferences, asset manifest |
| `.state.json` | Scripts | Claude | Execution history, gate status, generation records |

### PROJECT_CONFIG.yaml (Human-Managed)

Contains all creative decisions and asset paths:

```yaml
project: my-project
style_dna:
  name: "Style Name"
  locked: true
  # ... style components

characters:
  protagonist:
    name: "Character Name"
    visual_keywords: "..."

# Asset manifest (updated by scripts after generation)
assets:
  identity_sheets:
    protagonist: "EXPORTS/identity_sheets/protagonist_20260205.png"
  hero_shots:
    protagonist:
      entrance: "EXPORTS/hero_shots/protagonist_entrance_20260205.png"
```

### .state.json (Script-Managed)

Contains execution history and state that Claude reads to understand progress:

```json
{
  "current_phase": "visual-development",
  "gates_passed": ["gate-0", "gate-1", "gate-2"],
  "execution_log": [
    {
      "timestamp": "2026-02-05T10:30:00Z",
      "command": "fal_generate.py --hero protagonist",
      "result": "success",
      "output": "EXPORTS/hero_shots/protagonist_entrance_20260205.png",
      "metadata": {"model": "nano_banana", "seed": 12345}
    }
  ]
}
```

### State Flow

```
Claude reads state → Decides next action → Calls script →
Script executes → Script updates state → Claude reads updated state → Loop
```

## Script Design Principles

Scripts are **generalized primitives** that Claude composes into workflows. They must be:

### 1. Parameterized (No Hardcoded Values)

```bash
# Good: All values come from CLI or config
python fal_generate.py --hero mars --model nano_banana --seed 12345

# Bad: Hardcoded character or style in script
```

### 2. Single-Purpose (One Operation)

Each script does ONE thing well:
- `fal_generate.py` - Generate images via FAL.ai
- `generate_clips.py` - Generate video clips via Kling
- `assemble_scene.py` - Concatenate clips into scene

### 3. Structured Output

Scripts return structured results that Claude can parse:
- File paths to generated assets
- JSON metadata alongside each asset
- Exit codes for success/failure
- Stdout messages Claude can read

### 4. Idempotent (Safe to Re-run)

```bash
# Check if output exists, skip if so
python fal_generate.py --hero mars
# Output: "Skipping: mars_entrance already exists. Use --force to overwrite."

# Force regeneration when needed
python fal_generate.py --hero mars --force
```

### 5. Dry-Run Capable

```bash
# Preview what would happen without executing
python generate_clips.py --clip 1 --dry-run
# Output: Would generate clip01 using shot01 as start frame, 7s duration, $2.35 cost
```

### 6. State-Updating

After successful execution, scripts update `.state.json`:
```python
# At end of successful generation:
state_manager.record_execution(
    command="fal_generate.py --hero mars",
    output="EXPORTS/hero_shots/mars_entrance_20260205.png",
    metadata={"model": "nano_banana", "seed": 12345}
)
```

### 7. Config-Driven

Scripts read `PROJECT_CONFIG.yaml` for:
- Style DNA (prompts, negative prompts)
- Character definitions (visual keywords, palettes)
- Model preferences (which model to use by default)
- Output paths (where to save assets)

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

- **v0.5** (2026-02-05): **Agentic-First Architecture**
  - Established agentic orchestration as core design principle
  - Claude orchestrates all workflows (removed n8n dependency)
  - Scripts redesigned as generalized primitives
  - Added Script Design Principles (parameterized, single-purpose, idempotent, etc.)
  - State management updated: scripts update .state.json, Claude reads and decides
  - Video production validated with agentic clip generation loop (SC02)
- **v0.4** (2026-01-31): Added location reference generation, autonomous batch generation (--all-locations flag)
- **v0.3** (2026-01-29): Refactored architecture, project-agnostic generation tools
- **v0.2** (2026-01-28): Visual production pipeline, Hellmouth Cowboy validation
- **v0.1** (2026-01-26): Initial story skills and structure
