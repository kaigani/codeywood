# Codeywood Generation Tools

Project-agnostic image generation tools for visual production.

## Setup

```bash
# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set your FAL.ai API key
export FAL_KEY="your_api_key_here"
# Or create a .env file in your project with: FAL_KEY=your_api_key_here
```

## Usage

All commands should be run from your project directory (where `PROJECT_CONFIG.yaml` lives).

### Style DNA Exploration

Test 3-4 different visual directions before committing to a style:

```bash
python /path/to/codeywood/scripts/generate/fal_generate.py --test style_dna
```

This generates test images for each style DNA template across multiple scenarios.

### Hero Shots

Generate hero shots that establish a character's visual presence:

```bash
python /path/to/codeywood/scripts/generate/fal_generate.py --hero nameless
python /path/to/codeywood/scripts/generate/fal_generate.py --hero minnie-chance
```

Hero shots are generated using the primary model (default: SeeDream v4.5).

### Identity Sheets

Generate technical reference sheets with composite layouts:

```bash
python /path/to/codeywood/scripts/generate/fal_generate.py --identity nameless
```

Identity sheets are generated using the technical model (default: Nano Banana Pro).

### Specify Model

Override the default model:

```bash
python fal_generate.py --hero nameless --model seedream
python fal_generate.py --identity nameless --model nano_banana
```

### Available Models

```bash
python fal_generate.py --list-models
```

| Model | Best For |
|-------|----------|
| `seedream` | Artistic styles, painterly, stylized (SeeDream v4.5) |
| `hunyuan` | Artistic styles, illustration (Hunyuan Image 3.0) |
| `grok` | Artistic exploration, creative styles (Grok Imagine) |
| `nano_banana` | Precise style refs, prompt handling, technical refs (Nano Banana Pro) |

## Project Configuration

Each project needs a `PROJECT_CONFIG.yaml` file. Copy from `templates/PROJECT_CONFIG.yaml` and customize.

### Key Configuration Sections

**Visual Settings:**
```yaml
visual:
  primary_model: "seedream"        # For artistic/hero shots
  technical_model: "nano_banana"   # For identity sheets
```

**Locked Style DNA:**
```yaml
style_dna:
  name: "Gothic Western"
  locked: true
  medium_era: "Dark animated style inspired by Castlevania..."
  linework_texture: "Heavy ink outlines..."
  lighting_rendering: "Dramatic rim lighting..."
  color_palette: "Desaturated dusty palette..."
  hex_palette:
    - "#0d0d0d"
    - "#1a1a1a"
    # ... 8-12 colors
```

**Character Palettes:**
```yaml
characters:
  nameless:
    name: "Nameless"
    palette:
      - "#0d0d0d"
      - "#1a1a1a"
```

## Output Structure

Generated images are saved to your project's `EXPORTS/` directory:

```
EXPORTS/
├── style_tests/           # Style DNA exploration results
├── hero_shots/
│   ├── nameless/          # Per-character hero shots
│   ├── minnie-chance/
│   └── ...
└── identity_sheets/       # Character identity sheets
```

Each image has a corresponding `.json` metadata file with prompt, settings, and timestamp.

## Workflow

The recommended visual production workflow:

1. **Phase 1: Style DNA Exploration**
   - Create 3-4 style DNA templates in your config
   - Run `--test style_dna` for each
   - Compare results, lock winning Style DNA

2. **Phase 2: Hero Shots**
   - Run `--hero <character>` for each main character
   - Lock winning hero shots
   - Extract character-specific palettes

3. **Phase 3: Identity Sheets**
   - Run `--identity <character>` for each main character
   - Validate against hero shots

See `references/KNOWLEDGE_BASE.md` for detailed best practices.
