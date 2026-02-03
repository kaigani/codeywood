# CLAUDE.md - Codeywood AI Video Story Generation System

## Project Overview

Codeywood is a modular Claude Skills-based system for autonomous AI video story generation. The goal is complete 20-30 minute episodes from user requirements using a hybrid architecture:

- **Creative Layer** (Claude): Story development, quality evaluation, iteration
- **Execution Layer** (Python + n8n): API orchestration, file management, reproducible workflows

## Memory Management & Isolation
To prevent context bleed between sub-projects in this monorepo, follow these strict rules when using memory tools (e.g., `claude-mem` or `server-memory`):

- **Primary Tag Format:** Always use the prefix `[CODEYWOOD-{project-name}]` for all memory storage and retrieval. For general context use prefix `[CODEYWOOD]`.
- **Dynamic Project Detection:** Determine `{project-name}` based on the current working projects directory relative to the Codeywood root (e.g., `[CODEYWOOD-pirate-romance]` for `/projects/pirate-romance/`, `[CODEYWOOD-hellmouth-cowboy]` for `/projects/hellmouth-cowboy/`).
- **Storage Rule:** When saving a new memory (decisions, patterns, bug fixes), it MUST include the project-specific tag in the `tags` array.
- **Retrieval Rule:** When searching for past context, always include the current project-specific tag in the search filter to ignore memories from unrelated sub-projects.

## Quick Reference

### Key Commands

```bash
# Generate character hero shots (from project directory)
python3 scripts/generate/fal_generate.py --hero CHARACTER --model nano_banana

# Generate identity sheet
python3 scripts/generate/fal_generate.py --identity CHARACTER

# Generate location reference grid
python3 scripts/generate/fal_generate.py --location LOCATION

# Generate storyboard
python3 scripts/generate/fal_generate.py --storyboard SCENE

# List available models
python3 scripts/generate/fal_generate.py --list-models
```

### Available Models

| Model | Best For |
|-------|----------|
| `nano_banana` | Technical refs, identity sheets, precise control |
| `seedream` | Artistic styles, painterly, emotional shots |
| `hunyuan` | Illustration, stylized art |
| `grok` | Creative exploration, graphic styles |

## Directory Structure

```
codeywood/
├── skills/              # Claude skill definitions (role-based)
│   ├── writer/          # Story development skills
│   ├── production/      # Visual production skills
│   └── meta/            # System orchestration skills
├── scripts/generate/    # Image generation CLI tools
├── templates/           # Project scaffolding
├── projects/            # Individual productions
├── references/          # Knowledge base (prompting techniques)
├── WORKFLOWS/patterns/  # Reusable execution patterns
└── EXPORTS/             # Cross-project outputs
```

## Project Structure (Per Project)

```
projects/{name}/
├── PROJECT_CONFIG.yaml  # Human-edited: style DNA, characters, settings
├── .state.json          # Machine-managed: pipeline state, gates
├── STORY/
│   ├── CREATIVE_BRIEF.md
│   ├── LOGLINE_LOCK.md
│   ├── CHARACTER_SHEETS/*.md
│   └── SCRIPTS/*.md
└── EXPORTS/
    ├── hero_shots/
    ├── identity_sheets/
    └── location_refs/
```

## State Management

| File | Edited By | Purpose |
|------|-----------|---------|
| `PROJECT_CONFIG.yaml` | Humans | Style, characters, model preferences |
| `.state.json` | Workflows | Pipeline state, gate status |

**Never manually edit .state.json** - it's managed by workflows.

## Style DNA Components

When defining visual style, break it into four components:

1. **Medium/Era**: Animation style, time period, reference shows
2. **Line-work/Texture**: Edge rendering, surface detail
3. **Lighting/Rendering**: Shadows, contrast, atmosphere
4. **Color Palette**: Dominant tones, accents, saturation levels

## FAL API Conventions

### Parameter Formats

```python
# Use string literals for common sizes
"image_size": "square_hd"       # 1024x1024
"image_size": "landscape_16_9"  # 1536x864
"image_size": "portrait_4_3"    # 1024x1536

# Or dicts for custom sizes
"image_size": {"width": 1536, "height": 1536}

# Always include seed for reproducibility
"seed": 12345
```

### Two Nano Banana Pro Modes

**Text-to-Image** (identity sheets):
```python
arguments={
    "prompt": prompt,
    "image_size": "square_hd",
    "negative_prompt": negative_prompt,
    "num_inference_steps": 40,
    "guidance_scale": 4.5
}
```

**Multi-Image Reference** (final frames):
```python
arguments={
    "prompt": prompt,
    "image_urls": [ref1_url, ref2_url],  # Uploaded references
    "aspect_ratio": "16:9",
    "resolution": "2K"
}
```

## Quality Gates

Production passes through 8 sequential gates:

| Gate | Name | Key Check |
|------|------|-----------|
| 0 | Intake | CREATIVE_BRIEF.md complete |
| 1 | Logline | LOGLINE_LOCK.md approved |
| 2 | Characters | All CHARACTER_SHEETS complete |
| 3 | Structure | Episode beats + scene lists |
| 4 | Script | Full screenplay with metadata |
| 5 | Approved | Critique score >= 70 |
| 6 | References | All visual refs generated |
| 7 | Shots | All storyboards validated |

## Visual Production Phases

1. **Phase 0**: Modality selection (animation, live-action, hybrid)
2. **Phase 1**: Style DNA exploration (3-4 directions, lock winner)
3. **Phase 2**: Character + location references
4. **Phase 3**: Identity sheets (8-panel composites)
5. **Phase 4**: Storyboards (3x2 shot grids)
6. **Phase 5+**: Production shots

## Composite Layout Prompting

For identity sheets and reference grids, use explicit panel descriptions:

```
TOP ROW (left to right):
- Extreme close-up of eyes, heavy ink outlines
- Close-up of face profile
- Hands reference shot

MIDDLE SECTION (large):
- Full body front view with signature wardrobe
- Full body back view, silhouette quality

BOTTOM ROW (left to right):
- Portrait showing vulnerability
- Signature action pose
- Quiet moment or alternate state
```

## Common Patterns

### Character Reference Workflow

1. Read CHARACTER_SHEETS/{name}.md for visual keywords
2. Read CREATIVE_BRIEF.md for style guide keywords
3. Build prompts combining character + style
4. Generate: hero shots, expression sheet, costume ref
5. Save to EXPORTS/character_refs/

### Writers Room Pattern

Multi-agent story development with 5 personas:
- Chaos Architect (wild ideas)
- Internal Logician (structure)
- Shadow Psychologist (character depth)
- Sensory Nihilist (sensory details)
- Brutal Editor (cuts and clarity)

## Optional Integrations

### MCP Servers (Optional)

**FAL Documentation MCP** - Provides access to fal.ai API documentation:
```
mcp__fal__SearchFal - Search fal.ai docs for API info
```
Use this to verify parameter names, model capabilities, and best practices.

### Claude Memory (Optional)

**claude-mem** - Persistent memory across sessions for project context:
- Use `/claude-mem:make-plan` - Create implementation plans with documentation discovery
- Use `/claude-mem:do` - Execute plans using subagents

When using claude-mem, follow the memory isolation rules in the Memory Management section above to prevent context bleed between sub-projects.

## Key Files to Know

| File | Purpose |
|------|---------|
| `ARCHITECTURE.md` | Full system design |
| `SKILL.md` | Master production skill |
| `references/KNOWLEDGE_BASE.md` | Prompting techniques |
| `WORKFLOWS/README.md` | Workflow pattern format |
| `scripts/generate/fal_generate.py` | Main image generation tool |

## Current Active Project

**pirate-romance** - "The Cartographer's Daughter"
- Phase: Visual Development (Phase 5)
- Style: Jeweled Caribbean Fantasy (YA live-action)
- Characters: Mars (protagonist), Jonah (love interest), Silas/Voice-Taker, Hannah

## Development Notes

- Visual consistency uses reference-based approach (Nano Banana Pro)
- Dual-model workflow: SeeDream for artistic, Nano Banana for technical
- Python venv at `sandbox/fal_experiments/venv/` has all dependencies
- Always use `--seed` parameter for reproducible generation
- Optional MCP: `fal` for API documentation lookup
- Optional Plugin: `claude-mem` for persistent memory across sessions
