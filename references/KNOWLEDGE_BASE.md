# Codeywood Visual Generation Knowledge Base

> Practical knowledge for prompting different AI generation services across modalities.

## Architecture

This knowledge base is organized along two dimensions:

### Services (`/services/`)
Service-specific prompt vocabulary, techniques, and limitations. Each generator has its own language.

| Service | Best For | Key Techniques |
|---------|----------|----------------|
| **SeeDream v4.5** | Artistic styles, painterly, stylized | Animation vocabulary, cel-shading terms |
| **Nano Banana Pro** | Technical refs, identity sheets | Hex color grading, composite layouts |
| **Hunyuan Image 3.0** | Artistic, illustration | (Too realistic for animation) |
| **Grok Imagine** | Graphic posters, bold styles | High stylization |
| **Midjourney** | Concept art, mood exploration | Style suffixes, chaos/stylize params |
| **Runway Gen-3** | Video generation, motion | Keyframe descriptions, camera language |

### Modalities (`/modalities/`)
Different visual styles require different prompting approaches and reference types.

| Modality | Style Anchors | Reference Focus |
|----------|---------------|-----------------|
| **Animation** | Art style, line weight, color palette, shading | Model sheets, color scripts, BG paintings |
| **Live Action** | Camera, lens, film stock, color grade | Film stills, LUTs, cinematography refs |
| **Hybrid** | Blend of techniques | Mixed approach based on target |

## Usage Pattern

1. **Determine modality** - What's the visual target? (animation, live action, hybrid)
2. **Select service** - Which generator fits this task?
3. **Load service vocabulary** - Use service-specific prompt patterns
4. **Apply modality approach** - Use appropriate reference strategy

## Key Principles

### Specificity Over Abstraction
Generic prompts fail. Instead of "character turnaround", describe exactly what you want:
- Panel layout
- View types
- Lighting setup
- Background treatment

### Service-Specific Techniques
What works on one service may not work on another:
- Hex color palettes work on Nano Banana Pro, not universally
- Midjourney responds to `--stylize` and `--chaos`
- Flux prefers natural language over keyword stacking

### Reference Weight Tuning
Different tasks need different reference influence:
- Style lock-in: High weight (0.90-0.95)
- Variation within style: Medium weight (0.75-0.85)
- Exploration: Low weight (0.50-0.70)

## Best Practices

### Style DNA Exploration (Phase 1)

**DO NOT commit to a visual style without exploring 3-4 creative directions first.**

This is not about testing different models—it's about testing different artistic approaches for your project.

**Process**:
1. **Define 3-4 Style DNA Templates** - Each template deconstructs a different creative direction into:
   - Medium/Era (animation style, time period, references)
   - Line-work/Texture (how edges and surfaces render)
   - Lighting/Rendering (shadow approach, contrast, atmosphere)
   - Color Palette (dominant tones, accents, saturation)

2. **Test Each Template** - Generate 2-3 mood frames per template using different scenarios (character silhouette, environment, detail shot)

3. **Formal Comparison** - Evaluate across:
   - Visual criteria (tone match, contrast, distinctiveness)
   - Technical criteria (consistency, clarity, scalability)
   - Narrative criteria (supports story, appropriate for audience)

4. **Lock Winner** - Select ONE Style DNA, extract palette, document rationale

**Why This Matters**:
- Prevents premature commitment that leads to rework
- Reveals which direction works best for YOUR project
- Establishes visual language before expensive character/environment work
- Provides comparison data for knowledge base

**Hellmouth Cowboy Example**:
- Tested: Gothic Western, Samurai Jack Minimal, Base 90s Animated
- Winner: Gothic Western (atmospheric, supports horror-western fusion, distinctive)
- 9 images generated (3 templates × 3 scenarios)
- Decision made with evidence, not gut feeling

### Hero Shots Before Identity Sheets (Phase 2)

Generate 3-5 hero shots per character BEFORE creating technical reference sheets.

**Why**: Establishes what makes the character visually compelling, informs what to emphasize in identity sheets

**Hero shot types**: The Entrance, The Signature Action, The Quiet Moment, The Confrontation

### Composite Layout Prompting (Phase 3)

Replace generic "turnaround" prompts with explicit panel-by-panel descriptions:

```
Clean layout with multiple views on neutral beige background. Grid format:
TOP ROW: Eye close-up | Face profile | Hand reference
MIDDLE SECTION: Full body front view | Full body back view
BOTTOM ROW: Hat off portrait | Gun draw | Sitting profile
Technical: Heavy ink outlines, cel-shaded, thin black dividing lines
```

**Why**: Predictable, consistent results. AI interprets "turnaround" inconsistently.

## Generation Tools

The project-agnostic generation tools live in `scripts/generate/`:

```bash
# Setup (one time)
cd /path/to/codeywood/scripts/generate
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
export FAL_KEY="your_api_key"

# From your project directory (where PROJECT_CONFIG.yaml lives):

# Style DNA exploration
python /path/to/codeywood/scripts/generate/fal_generate.py --test style_dna

# Hero shots for a character
python /path/to/codeywood/scripts/generate/fal_generate.py --hero nameless

# Identity sheet for a character
python /path/to/codeywood/scripts/generate/fal_generate.py --identity nameless

# List available models
python /path/to/codeywood/scripts/generate/fal_generate.py --list-models
```

### Project Configuration

Each project needs a `PROJECT_CONFIG.yaml` file. Copy from `templates/PROJECT_CONFIG.yaml` and customize:

- **Project metadata** - name, slug, modality
- **Visual settings** - primary/technical models, default sizes
- **Locked Style DNA** - medium/era, linework, lighting, palette, hex colors
- **Character palettes** - per-character color schemes
- **Paths** - where to find/store files

The generation tool reads this config and uses it for all prompts.

## Directory Structure

```
/references/
├── KNOWLEDGE_BASE.md          # This file
├── services/
│   ├── nano-banana-pro/
│   │   ├── TECHNIQUES.md      # What works
│   │   ├── LIMITATIONS.md     # What doesn't
│   │   └── prompts/           # Template library
│   ├── midjourney/
│   ├── flux/
│   └── runway-gen3/
├── modalities/
│   ├── animation/
│   │   ├── APPROACH.md        # Style ref strategy
│   │   ├── VOCABULARY.md      # Prompt language
│   │   └── reference_types/   # What refs to capture
│   ├── live-action/
│   └── hybrid/
└── visual_consistency/        # Legacy (to be migrated)
```

## Contributing

When adding knowledge:
1. Test techniques across multiple generations
2. Document what works AND what fails
3. Include example prompts with results
4. Note service version/date (capabilities change)
