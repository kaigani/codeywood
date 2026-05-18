# CLAUDE.md - Codeywood AI Video Story Generation System

## Project Overview

Codeywood is a modular Claude Skills-based system for autonomous AI video story generation. The goal is complete 20-30 minute episodes from user requirements using a hybrid architecture:

- **Claude** (Orchestrator): Story development, quality evaluation, workflow orchestration, adaptive decision-making
- **Scripts** (Primitives): Generalized Python tools for API calls, file management, reproducible operations

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

# Generate location reference grid (photorealistic by default)
python3 scripts/generate/fal_generate.py --location LOCATION

# Generate location with concept art mode (for early development)
python3 scripts/generate/fal_generate.py --location LOCATION --mode concept

# Generate all locations
python3 scripts/generate/fal_generate.py --all-locations

# Generate storyboard
python3 scripts/generate/fal_generate.py --storyboard SCENE

# List available models
python3 scripts/generate/fal_generate.py --list-models
```

### Concept Art (pencil + watercolor sketches via local z-image)

Requires the project venv (`source sandbox/fal_experiments/venv/bin/activate`) — pulls in `pyyaml`, `Pillow`, `requests`.

```bash
# Define subjects: copy template to projects/{name}/CONCEPT_ART/subjects.yaml
cp scripts/production/concept_art/subjects_template.yaml \
   projects/{name}/CONCEPT_ART/subjects.yaml

# Dry-run to confirm subject list
python3 scripts/production/concept_art/generate.py --project projects/{name} --dry-run

# Generate all locations + characters + scenes
caffeinate -i python3 scripts/production/concept_art/generate.py --project projects/{name}

# One kind only / single subject / regenerate
python3 scripts/production/concept_art/generate.py --project projects/{name} --kind scenes
python3 scripts/production/concept_art/generate.py --project projects/{name} --only ep01_temple_sprint --force

# Build contact sheets (scenes_contact_sheet.png + contact_sheet.png)
python3 scripts/production/concept_art/contact_sheets.py --project projects/{name}
```

Skill: `skills/production/concept-art/SKILL.md`. Scenes use `ep##_<name>` id prefix so the contact sheet groups by episode.

### Available Models

| Model | Best For |
|-------|----------|
| `nano_banana` | Technical refs, identity sheets, precise control |
| `seedream` | Artistic styles, painterly, emotional shots |
| `hunyuan` | Illustration, stylized art |
| `grok` | Creative exploration, graphic styles |

### Video Analysis & Editing Commands

```bash
# Analyze a clip (filmstrip, metadata, color, motion, audio)
python3 scripts/analysis/analyze_clip.py VIDEO_PATH
python3 scripts/analysis/analyze_clip.py VIDEO_PATH --quick          # Filmstrip + metadata only
python3 scripts/analysis/analyze_clip.py VIDEO_PATH --preflight      # Show what would be done
python3 scripts/analysis/analyze_clip.py VIDEO_PATH --transcribe     # Include Whisper STT

# Compare reference vs. generated clip
python3 scripts/analysis/compare_clips.py REFERENCE GENERATED
python3 scripts/analysis/compare_clips.py REFERENCE GENERATED --quick

# Trim a clip
python3 scripts/editing/trim_clip.py VIDEO --start 2.5 --end 8.0

# Create transitions between clips
python3 scripts/editing/transition.py CLIP_A CLIP_B --type crossfade --duration 1.0
python3 scripts/editing/transition.py CLIP_A CLIP_B --type l_cut --lead 1.5

# Smart assembly from EDL YAML
python3 scripts/editing/smart_assemble.py EDL_FILE
python3 scripts/editing/smart_assemble.py EDL_FILE --preflight

# Paper cut (static images + dialogue + direction narration)
python3 scripts/production/generate_paper_cut.py --scene PRODUCTION/EP01/sc01
python3 scripts/production/generate_paper_cut.py --scene PRODUCTION/EP01/sc01 --preflight
python3 scripts/production/generate_paper_cut.py --scene PRODUCTION/EP01/sc01 --no-direction
python3 scripts/production/generate_paper_cut.py --scene PRODUCTION/EP01/sc01 --direction-only
```

### Post-Production Skills

| Skill | Role | Purpose |
|-------|------|---------|
| `editor` | Post-production | Film editing decisions, trim heuristics, rhythm, EDL drafting |
| `sound-designer` | Post-production | Audio layers, mixing, dialogue, L/J-cut strategy |
| `art-director` | Post-production | Visual coherence, color consistency, style DNA enforcement |
| `clip-study` | Production | Feedback loop — analyze reference → replicate → compare → learn |

## Directory Structure

```
codeywood/
├── skills/              # Claude skill definitions (role-based)
│   ├── writer/          # Story development skills
│   ├── production/      # Visual production skills
│   ├── editor/          # Film editing cognitive skill
│   ├── sound-designer/  # Sound design cognitive skill
│   ├── art-director/    # Visual coherence cognitive skill
│   └── meta/            # System orchestration skills
├── scripts/
│   ├── lib/             # Shared Python library (config, fal_api, ffmpeg, paths)
│   ├── analysis/        # Video analysis CLIs (analyze_clip, compare_clips)
│   ├── editing/         # Editing CLIs (trim_clip, smart_assemble, transition)
│   ├── reference/       # Image generation CLI tools
│   └── production/      # Video production primitives
├── templates/           # Project scaffolding
├── projects/            # Individual productions
├── references/          # Knowledge base (prompting techniques)
├── docs/                # System documentation
└── WORKFLOWS/patterns/  # Reusable execution patterns
```

## Project Structure (Per Project)

```
projects/{name}/
├── PROJECT_CONFIG.yaml  # Human-edited: style DNA, characters, settings
├── .state.json          # Machine-managed: pipeline state, gates
├── STORY/               # Narrative artifacts
│   ├── CREATIVE_BRIEF.md
│   ├── LOGLINE_LOCK.md
│   ├── CHARACTER_SHEETS/*.md
│   └── SCRIPTS/*.md
├── REFERENCES/          # Shared visual reference library (identity sheets, hero shots, etc.)
│   ├── identity_sheets/
│   ├── hero_shots/
│   ├── location_refs/
│   └── storyboards/
├── PRODUCTION/          # Per-scene video production
│   └── EP01/
│       └── sc03/        # Everything for one scene in one place
│           ├── shot_list.yaml
│           ├── clip_definitions.yaml
│           ├── frames/  # Generated start frames
│           ├── clips/   # Generated video clips
│           └── assembly/
└── DELIVERABLES/        # Final approved outputs
    └── EP01/
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

## Prompt Engineering (Production vs Concept)

The system supports two prompt modes via the prompt-engineer skill:

### Photorealistic Mode (Default)
For production stills that look like frames from an actual film. Uses:
- **Camera/Lens specs**: "24mm anamorphic lens, f/2.8"
- **Film stock refs**: "shot on ARRI Alexa, Kodak Vision3 500T"
- **Material physics**: "oxidized iron, damp limestone, condensation"
- **Power phrase**: "practical set construction"

**Avoid** vibe words: ethereal, magical, mystical, supernatural, concept art, illustration

### Concept Mode
For early development with painterly/illustrative quality. Allows:
- Atmospheric adjectives (ethereal, haunting)
- Style references ("in the style of")
- Art medium references (digital painting, matte painting)

Use `--mode concept` for development exploration, default `--mode photorealistic` for final production.

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
| `skills/production/prompt-engineer/SKILL.md` | Prompt engineering techniques |
| `scripts/lib/video_analysis.py` | Filmstrip, color palette, motion analysis |
| `scripts/lib/audio_analysis.py` | Waveform, silence detection, Whisper STT |
| `scripts/lib/scene_detect.py` | Cut detection, shot breakdown |
| `scripts/lib/ffmpeg.py` | FFmpeg utils + editing primitives (trim, crossfade, L/J-cut, speed, color grade) |
| `scripts/analysis/analyze_clip.py` | Unified clip analysis CLI |
| `scripts/analysis/compare_clips.py` | Reference vs. generated comparison CLI |
| `scripts/editing/smart_assemble.py` | EDL-driven assembly with transitions |
| `skills/editor/SKILL.md` | Film editing cognitive skill |
| `skills/sound-designer/SKILL.md` | Sound design cognitive skill |
| `skills/art-director/SKILL.md` | Visual coherence cognitive skill |
| `skills/production/clip-study/SKILL.md` | Feedback loop — study, replicate, learn |
| `skills/production/visual-translation/SKILL.md` | Prose-to-visual diagnostic — tests beats before directors room, feedback loop to writers room |
| `skills/production/concept-art/SKILL.md` | Pencil + watercolor concept sketches via local z-image (locations + characters + scenes) |
| `scripts/production/concept_art/generate.py` | Concept-art driver — reads `{project}/CONCEPT_ART/subjects.yaml` |

## Current Active Project

**pirate-romance** - "The Cartographer's Daughter"
- Phase: Visual Development (Phase 5)
- Style: Jeweled Caribbean Fantasy (YA live-action)
- Characters: Mars (protagonist), Jonah (love interest), Silas/Voice-Taker, Hannah

## Knowledge Lifecycle

New findings follow this lifecycle:
1. **DISCOVER** → Write to `memory/` (with date, source, validation status)
2. **VALIDATE** → Test across 2+ sessions or projects
3. **GRADUATE** → Move to the relevant SKILL.md or `references/` doc
4. **CLEAN** → Delete from memory after graduation

Memory is a staging area, not permanent storage. If a finding has been stable for 2+ sessions and applies broadly (not project-specific), it should graduate to its skill.

Graduation targets:
- Prompting techniques → `skills/production/prompt-engineer/SKILL.md`
- Video generation rules → `skills/production/video-director/SKILL.md`
- Editing/assembly lessons → `skills/editor/SKILL.md`
- Audio/voice findings → `skills/sound-designer/SKILL.md`
- Visual coherence rules → `skills/art-director/SKILL.md`
- QC patterns → `skills/production/image-qc/SKILL.md` or `video-qc/SKILL.md`
- Model-specific API knowledge → `references/services/{model}/`
- Project-specific state → stays in memory

## Development Notes

- Visual consistency uses reference-based approach (Nano Banana Pro)
- Dual-model workflow: SeeDream for artistic, Nano Banana for technical
- Python venv at `sandbox/fal_experiments/venv/` has all dependencies
- Always use `--seed` parameter for reproducible generation
- Optional MCP: `fal` for API documentation lookup
- Optional Plugin: `claude-mem` for persistent memory across sessions
