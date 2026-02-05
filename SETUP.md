# Codeywood Setup Guide

This guide walks through setting up the Codeywood framework with the agentic-first architecture where Claude orchestrates Python scripts directly.

## Prerequisites

- Python 3.10+
- Claude Code CLI
- FAL.ai API key

## Quick Start (5 minutes)

### 1. Clone and Install Python Dependencies

```bash
cd /path/to/codeywood

# Set up main generation scripts
cd scripts/generate
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Set up production scripts (if doing video production)
cd ../production
pip install -r requirements.txt
```

### 2. Set Environment Variables

Add to your shell profile (`~/.zshrc` or `~/.bashrc`):

```bash
# Required for FAL.ai API access
export FAL_KEY="your-fal-api-key"

# Optional: Set default Codeywood root
export CODEYWOOD_ROOT="/path/to/codeywood"
```

Then reload: `source ~/.zshrc`

### 3. Verify Setup

```bash
# Test the generation script
cd /path/to/codeywood
source scripts/generate/venv/bin/activate

# List available models
python3 scripts/generate/fal_generate.py --list-models

# Should output:
# Available models:
# - nano_banana: Nano Banana Pro - Best for: Precise style refs, technical refs
# - seedream: SeeDream v4.5 - Best for: Artistic styles, painterly, stylized
# ...
```

## Creating Your First Project

### 1. Scaffold Project Structure

```bash
cp -r templates/project-scaffold projects/my-project
cp templates/PROJECT_CONFIG.yaml projects/my-project/
```

### 2. Edit PROJECT_CONFIG.yaml

```yaml
project: my-project
title: "My Project"
modality: animation  # or live-action-ya, hybrid

# Leave style_dna empty for now - will be locked after exploration
style_dna:
  locked: false

characters:
  protagonist:
    name: "Character Name"
    visual_keywords: "physical description..."
```

### 3. Start Production with Claude

In Claude Code, from your project directory:

```
You: Let's start story development for this project

Claude: [Reads PROJECT_CONFIG.yaml]
I'll help you develop the story. Let me start by asking some questions
about your vision for this project...
```

## Directory Structure

```
codeywood/
├── SKILL.md                      # Master skill for Claude
├── ARCHITECTURE.md               # System design
├── SETUP.md                      # This file
├── CLAUDE.md                     # Per-project instructions
│
├── scripts/
│   ├── generate/                 # Image generation tools
│   │   ├── fal_generate.py       # Main generation script
│   │   ├── requirements.txt
│   │   └── venv/                 # Python virtual environment
│   └── production/               # Video production tools
│       ├── generate_frames.py
│       ├── generate_clips.py
│       ├── assemble_scene.py
│       └── lib/
│
├── skills/                       # Claude skill definitions
│   ├── core/                     # Story development skills
│   ├── production/               # Visual production skills
│   └── meta/                     # System management skills
│
├── references/                   # Knowledge base
│   ├── KNOWLEDGE_BASE.md
│   └── services/                 # Service-specific guides
│
├── templates/                    # Project scaffolding
│   ├── PROJECT_CONFIG.yaml
│   └── project-scaffold/
│
└── projects/                     # Your productions
    └── my-project/
        ├── PROJECT_CONFIG.yaml
        ├── .state.json
        ├── STORY/
        ├── VISUAL_PRODUCTION/
        └── EXPORTS/
```

## How It Works

### Agentic Architecture

Claude orchestrates the entire workflow:

1. **Claude reads** PROJECT_CONFIG.yaml and .state.json to understand project state
2. **Claude decides** what needs to happen next based on quality gates
3. **Claude executes** Python scripts via Bash to perform generation
4. **Claude reviews** the generated outputs
5. **Claude adapts** the plan based on results
6. **Repeat** until complete

### Script Invocation

Claude calls scripts directly:

```bash
# Generate character references
python3 scripts/generate/fal_generate.py --hero protagonist --model nano_banana

# Generate location references
python3 scripts/generate/fal_generate.py --location office --mode photorealistic

# Generate video frames
python3 scripts/production/generate_frames.py --shots shot_lists/sc01_shots.yaml

# Generate video clips (one at a time for review)
python3 scripts/production/generate_clips.py --clips clip_definitions/sc01_clips.yaml --clip 1
```

## Troubleshooting

### "FAL_KEY not set"
- Verify environment variable is exported: `echo $FAL_KEY`
- Ensure your shell profile was reloaded: `source ~/.zshrc`

### "ModuleNotFoundError: No module named 'fal_client'"
- Activate the virtual environment: `source scripts/generate/venv/bin/activate`
- Or install dependencies: `pip install -r scripts/generate/requirements.txt`

### "Character/Location not found"
- Check PROJECT_CONFIG.yaml has the character/location defined
- Verify the slug matches exactly (case-sensitive)

### "Style DNA not locked"
- Run style exploration first: `python3 scripts/generate/fal_generate.py --test style_dna`
- Lock the winning style in PROJECT_CONFIG.yaml: `style_dna: locked: true`

## Extending the System

### Adding New Scripts

Scripts should follow these principles:
- Accept all parameters via CLI (no hardcoded values)
- Read configuration from PROJECT_CONFIG.yaml
- Return structured results (file paths, JSON metadata)
- Update .state.json after successful execution

### Adding New Skills

Create a new directory in `skills/` with a SKILL.md file containing:
- Purpose
- Inputs required
- Outputs produced
- Process steps
- Doneness criteria

Skills are reference documents that inform Claude's decisions.

## Support

- Documentation: `docs/` directory
- Knowledge base: `references/KNOWLEDGE_BASE.md`
