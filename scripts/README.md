# SCRIPTS

Direct CLI tools for generation, editing, and utilities. These implement the execution logic defined in WORKFLOWS/patterns.

## Directory Structure

```
scripts/
├── generate/           # Asset generation tools
│   ├── fal_generate.py     # FAL.ai image generation
│   └── requirements.txt
├── edit/               # Video/audio editing tools
│   ├── assemble_shots.sh
│   └── add_audio.sh
├── util/               # Utility scripts
│   └── scaffold_project.py
└── README.md
```

## Available Scripts

### Generation (`generate/`)

| Script | Purpose | Usage |
|--------|---------|-------|
| `fal_generate.py` | Generate images via FAL.ai | See below |

#### fal_generate.py

Full-featured image generation tool that reads from PROJECT_CONFIG.yaml.

```bash
# Run from project directory or specify --project path

# Style exploration
python scripts/generate/fal_generate.py --test style_dna

# Character generation
python scripts/generate/fal_generate.py --hero CHARACTER_SLUG
python scripts/generate/fal_generate.py --identity CHARACTER_SLUG

# Location references
python scripts/generate/fal_generate.py --location LOCATION_SLUG
python scripts/generate/fal_generate.py --all-locations

# Storyboards
python scripts/generate/fal_generate.py --storyboard SCENE_SLUG
python scripts/generate/fal_generate.py --all-storyboards

# Specify model
python scripts/generate/fal_generate.py --hero mars --model nano_banana

# List available models
python scripts/generate/fal_generate.py --list-models
```

**Available Models:**
| Model ID | Name | Best For |
|----------|------|----------|
| `seedream` | SeeDream v4.5 | Artistic, painterly |
| `hunyuan` | Hunyuan Image 3.0 | Illustration |
| `grok` | Grok Imagine | Creative exploration |
| `nano_banana` | Nano Banana Pro | Precise refs, technical |

### Editing (`edit/`)

| Script | Purpose | Usage |
|--------|---------|-------|
| `assemble_shots.sh` | Combine shots into sequence | `./assemble_shots.sh scene01` |
| `add_audio.sh` | Add soundtrack to video | `./add_audio.sh video.mp4 audio.mp3` |

### Utilities (`util/`)

| Script | Purpose | Usage |
|--------|---------|-------|
| `scaffold_project.py` | Create new project structure | `python scaffold_project.py "Project Name"` |

## Environment Variables

Scripts read from `.env` in project root or codeywood root:

```bash
FAL_KEY=<fal-api-key>
```

## Dependencies

Install Python dependencies:
```bash
pip install -r scripts/generate/requirements.txt
```

Required packages:
- `fal-client` - FAL.ai API client
- `pyyaml` - YAML parsing
- `python-dotenv` - Environment loading
- `requests` - HTTP downloads

## Adding New Scripts

1. Place script in appropriate subdirectory
2. Add entry to this README
3. Include usage documentation in script header
4. Add dependencies to relevant `requirements.txt`
5. If implementing a workflow pattern, reference it in the script docstring
