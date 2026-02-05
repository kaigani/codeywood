#!/usr/bin/env python3
"""
Codeywood FAL.ai Generation Tool

A project-agnostic image generation tool that reads configuration from
PROJECT_CONFIG.yaml and character sheets to generate:
- Style DNA exploration tests
- Character hero shots
- Character identity sheets
- Location reference grids
- Storyboard scene grids

Usage:
    # From project directory:
    python /path/to/codeywood/scripts/generate/fal_generate.py --test style_dna
    python /path/to/codeywood/scripts/generate/fal_generate.py --hero nameless
    python /path/to/codeywood/scripts/generate/fal_generate.py --identity nameless
    python /path/to/codeywood/scripts/generate/fal_generate.py --location dead-town
    python /path/to/codeywood/scripts/generate/fal_generate.py --all-locations
    python /path/to/codeywood/scripts/generate/fal_generate.py --storyboard sc01-cold-open
    python /path/to/codeywood/scripts/generate/fal_generate.py --all-storyboards

    # Or specify project path:
    python fal_generate.py --project /path/to/project --test style_dna
"""

import os
import sys
import json
import re
import argparse
from datetime import datetime
from pathlib import Path

# Try to load YAML support
try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False
    print("Warning: PyYAML not installed. Install with: pip install pyyaml")

# Load environment variables from .env if present
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# FAL.ai client
try:
    import fal_client
except ImportError:
    print("ERROR: fal_client not installed. Run: pip install fal-client")
    sys.exit(1)


# ============================================================================
# CONFIGURATION LOADING
# ============================================================================

def find_project_root(start_path=None):
    """Find project root by looking for PROJECT_CONFIG.yaml"""
    if start_path is None:
        start_path = Path.cwd()
    else:
        start_path = Path(start_path)

    current = start_path
    while current != current.parent:
        if (current / "PROJECT_CONFIG.yaml").exists():
            return current
        current = current.parent

    return None


def load_project_config(project_path):
    """Load project configuration from PROJECT_CONFIG.yaml"""
    config_path = project_path / "PROJECT_CONFIG.yaml"

    if not config_path.exists():
        print(f"ERROR: PROJECT_CONFIG.yaml not found in {project_path}")
        print("Create one from the template: templates/PROJECT_CONFIG.yaml")
        sys.exit(1)

    if not HAS_YAML:
        print("ERROR: PyYAML required to load project config")
        sys.exit(1)

    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def load_character_from_config(config, character_slug):
    """Load character visual data from PROJECT_CONFIG.yaml"""
    characters = config.get('characters', {})

    if character_slug not in characters:
        print(f"ERROR: Character '{character_slug}' not found in PROJECT_CONFIG.yaml")
        print(f"Available characters: {', '.join(characters.keys())}")
        return None

    char_config = characters[character_slug]

    return {
        'slug': character_slug,
        'name': char_config.get('name', character_slug.title()),
        'visual_keywords': char_config.get('visual_keywords', ''),
        'wardrobe': char_config.get('wardrobe', ''),
        'palette': char_config.get('palette', []),
        'role': char_config.get('role', ''),
    }


# ============================================================================
# MODEL DEFINITIONS
# ============================================================================
# Structure: model_id -> {name, best_for, endpoints: {modality -> endpoint}}
# Modalities: text-to-image, edit (with image refs), image-to-video, text-to-video

MODELS = {
    "seedream": {
        "name": "SeeDream v4.5",
        "best_for": "Artistic styles, painterly, stylized",
        "endpoints": {
            "text-to-image": "fal-ai/bytedance/seedream/v4.5/text-to-image",
        },
    },
    "hunyuan": {
        "name": "Hunyuan Image 3.0",
        "best_for": "Artistic styles, illustration",
        "endpoints": {
            "text-to-image": "fal-ai/hunyuan-image/v3/instruct/text-to-image",
        },
    },
    "grok": {
        "name": "Grok Imagine",
        "best_for": "Artistic exploration, creative styles",
        "endpoints": {
            "text-to-image": "xai/grok-imagine-image",
        },
    },
    "nano_banana": {
        "name": "Nano Banana Pro",
        "best_for": "Precise style refs, prompt handling, technical refs",
        "endpoints": {
            "text-to-image": "fal-ai/nano-banana-pro",
            "edit": "fal-ai/nano-banana-pro/edit",  # with image references
        },
    },
    "kling": {
        "name": "Kling Video 3.0 Pro",
        "best_for": "Video generation with character consistency",
        "endpoints": {
            "image-to-video": "fal-ai/kling-video/v3/pro/image-to-video",
            "text-to-video": "fal-ai/kling-video/v3/pro/text-to-video",
        },
    },
}


# =============================================================================
# AGENTIC PRIMITIVES SUPPORT
# =============================================================================

# Global flags set by CLI arguments
AGENTIC_FLAGS = {
    "dry_run": False,
    "force": False,
    "json_output": False,
}

# Collect results for JSON output
GENERATION_RESULTS = []


def check_output_exists(output_path: Path, force: bool = None) -> tuple[bool, str]:
    """Check if output already exists and decide whether to skip.

    Args:
        output_path: Path where output would be saved
        force: Override force flag (uses AGENTIC_FLAGS if None)

    Returns:
        (should_skip, reason) tuple
    """
    if force is None:
        force = AGENTIC_FLAGS["force"]

    if output_path.exists():
        if force:
            return False, "exists but --force specified, will overwrite"
        else:
            return True, f"already exists (use --force to overwrite)"
    return False, None


def log_generation_result(action: str, output_path: Path, status: str, metadata: dict = None):
    """Log a generation result for JSON output."""
    result = {
        "action": action,
        "output_path": str(output_path) if output_path else None,
        "status": status,
        "timestamp": datetime.now().isoformat(),
    }
    if metadata:
        result["metadata"] = metadata
    GENERATION_RESULTS.append(result)


def print_dry_run(action: str, output_path: Path, details: str = None):
    """Print dry-run preview of what would happen."""
    print(f"[DRY-RUN] Would {action}")
    print(f"          Output: {output_path}")
    if details:
        print(f"          {details}")


def update_state_file(project_path: Path, command: str, output_paths: list, status: str = "success", metadata: dict = None):
    """Update .state.json with execution record.

    This is a lightweight state update for the generation script.
    For full state management, use the StateManager class.
    """
    import uuid

    state_path = project_path / ".state.json"

    # Load existing state or create new
    if state_path.exists():
        with open(state_path) as f:
            state = json.load(f)
    else:
        state = {
            "version": "0.5",
            "project_slug": project_path.name,
            "current_phase": "REFERENCE_GENERATION",
            "executions": [],
            "generations": {},
        }

    # Ensure executions list exists
    if "executions" not in state:
        state["executions"] = []

    # Add execution record
    execution = {
        "execution_id": str(uuid.uuid4())[:8],
        "command": command,
        "completed_at": datetime.now().isoformat(),
        "status": status,
        "output_paths": [str(p) for p in output_paths],
    }
    if metadata:
        execution["metadata"] = metadata

    state["executions"].append(execution)

    # Keep only last 100 executions
    if len(state["executions"]) > 100:
        state["executions"] = state["executions"][-100:]

    # Update timestamp
    state["last_updated"] = datetime.now().isoformat()

    # Save
    with open(state_path, "w") as f:
        json.dump(state, f, indent=2)


def output_json_results():
    """Output all results as JSON."""
    print(json.dumps({
        "status": "complete",
        "results": GENERATION_RESULTS,
        "timestamp": datetime.now().isoformat(),
    }, indent=2))


def get_endpoint(model_id: str, modality: str = None, has_image_refs: bool = False) -> str:
    """Get the appropriate endpoint for a model based on modality.

    Args:
        model_id: The model identifier (e.g., 'nano_banana', 'kling')
        modality: Explicit modality ('text-to-image', 'edit', 'image-to-video', etc.)
        has_image_refs: If True and modality not specified, auto-selects 'edit' for supported models

    Returns:
        The FAL endpoint string
    """
    model = MODELS.get(model_id)
    if not model:
        raise ValueError(f"Unknown model: {model_id}")

    endpoints = model.get("endpoints", {})

    # If modality explicitly specified, use it
    if modality:
        if modality in endpoints:
            return endpoints[modality]
        raise ValueError(f"Model '{model_id}' does not support modality '{modality}'. Available: {list(endpoints.keys())}")

    # Auto-select based on context
    if has_image_refs and "edit" in endpoints:
        return endpoints["edit"]

    # Default to text-to-image for image models
    if "text-to-image" in endpoints:
        return endpoints["text-to-image"]

    # For video models, require explicit modality
    raise ValueError(f"Model '{model_id}' requires explicit modality. Available: {list(endpoints.keys())}")


# ============================================================================
# STYLE DNA TEMPLATES (Defaults - can be overridden by project config)
# ============================================================================

DEFAULT_STYLE_DNA_TEMPLATES = {
    "gothic_western": {
        "name": "Gothic Western",
        "medium_era": "Dark animated style inspired by Castlevania gothic horror meets Sergio Leone spaghetti western cinematography",
        "linework_texture": "Heavy ink outlines with weight variation, crisp silhouettes, slight paper grain texture",
        "lighting_rendering": "Dramatic rim lighting, deep cel-shaded shadows, volumetric dust and atmosphere, high contrast",
        "color_palette": "Desaturated dusty palette with deep blacks and blood-red punctuation",
    },
    "samurai_jack_minimal": {
        "name": "Samurai Jack Minimal",
        "medium_era": "2D animated style, Samurai Jack meets western noir",
        "linework_texture": "Clean vector shapes, thick consistent outlines, flat graphic forms, minimal detail lines",
        "lighting_rendering": "Stark silhouettes, two-tone shading, dramatic negative space, pure blacks",
        "color_palette": "Extremely limited palette, mostly blacks and grays with single accent color",
    },
    "base_90s": {
        "name": "Base 90s Animated",
        "medium_era": "1990s dark animated series, hand-drawn cel animation with modern digital compositing",
        "linework_texture": "Clean vector lines with varied weight, thicker on silhouette edges, sharp ink outlines",
        "lighting_rendering": "Cel-shaded with deep shadows, harsh directional lighting, minimal mid-tones, notan high-contrast principle",
        "color_palette": "Limited palette of desaturated earth tones with blood-red accents",
    },
}


# ============================================================================
# PROMPT ENGINEERING UTILITIES
# ============================================================================

# Photorealistic mode - words to avoid (trigger concept art / illustration look)
VIBE_WORDS_TO_AVOID = [
    "ethereal", "magical", "mystical", "supernatural", "impossible",
    "otherworldly", "dreamlike", "fantastical", "enchanted", "stunning",
    "breathtaking", "amazing", "incredible", "concept art", "illustration",
    "digital painting", "render", "fantasy glow", "YA fantasy",
]

# Photorealistic mode - technical replacements
CAMERA_SPECS = [
    "24mm anamorphic lens",
    "shot on ARRI Alexa",
    "Kodak Vision3 500T color science",
    "f/2.8 shallow depth of field",
    "practical set construction",
]

# Negative prompts by mode
NEGATIVE_PROMPTS = {
    "photorealistic": [
        "digital painting", "illustration", "concept art", "anime style", "cartoon",
        "stylized", "CGI render", "video game", "oversaturated", "HDR", "neon colors",
        "fantasy glow", "magical effects", "lens flare abuse", "floating elements",
        "deformed anatomy", "extra limbs", "bad proportions", "blurry", "low quality",
        "matte painting", "painted look", "brush strokes visible"
    ],
    "reference_sheet": [
        "desaturated", "gritty", "grimdark", "realistic gore", "sexualized",
        "Halloween costume aesthetic", "campy", "muddy colors", "floating heads",
        "bland lighting", "generic fantasy", "anime style", "cartoon style",
        "multiple people", "crowd scene", "deformed", "extra limbs", "bad anatomy"
    ],
}

def apply_photorealistic_mode(prompt, include_camera=True):
    """Transform a prompt to photorealistic mode by:
    1. Stripping vibe words that trigger concept art look
    2. Adding camera/lens technical specifications
    3. Adding practical set construction phrase
    """
    # Strip vibe words (case insensitive)
    cleaned = prompt
    for word in VIBE_WORDS_TO_AVOID:
        cleaned = re.sub(rf'\b{re.escape(word)}\b', '', cleaned, flags=re.IGNORECASE)

    # Clean up double spaces and trailing commas
    cleaned = re.sub(r'\s+', ' ', cleaned)
    cleaned = re.sub(r',\s*,', ',', cleaned)
    cleaned = re.sub(r',\s*\.', '.', cleaned)

    # Add camera specs if requested
    if include_camera:
        camera_line = ". ".join(CAMERA_SPECS[:3])  # Use first 3 specs
        cleaned = f"{cleaned.rstrip('.')}. {camera_line}."

    return cleaned.strip()


# ============================================================================
# PROMPT BUILDING
# ============================================================================

def build_style_dna_prompt(style_dna, subject, composition, mood):
    """Build a style DNA test prompt"""
    components = [
        subject,
        style_dna['medium_era'],
        style_dna['linework_texture'],
        style_dna['lighting_rendering'],
        composition,
        mood,
        style_dna['color_palette'],
    ]
    return ". ".join(filter(None, components))


def build_hero_shot_prompt(character_data, style_dna, moment, composition, mood):
    """Build a hero shot prompt from character data and style DNA"""
    components = [
        # Character specifics first
        character_data.get('visual_keywords', ''),
        character_data.get('wardrobe', ''),
        # Shot context
        moment,
        composition,
        mood,
        # Cinematography and style DNA
        style_dna.get('cinematography', ''),
        style_dna.get('medium_era', ''),
        style_dna.get('linework_texture', ''),
        style_dna.get('lighting_rendering', ''),
        style_dna.get('color_palette', ''),
    ]
    return ". ".join(filter(None, components))


def build_identity_sheet_prompt(character_data, style_dna, hex_palette=None):
    """Build an identity sheet prompt with structured format:
    Type, Character description, Style DNA, Panel layout, Technical specs, Style reference
    """
    visual_keywords = character_data.get('visual_keywords', '')
    wardrobe = character_data.get('wardrobe', '')
    char_name = character_data.get('name', 'character')

    # Build structured prompt following the template
    prompt_parts = []

    # 1. TYPE
    prompt_parts.append(f"A cinematic editorial contact sheet of {char_name}, character design reference sheet, turnaround view")

    # 2. CHARACTER DESCRIPTION
    prompt_parts.append(visual_keywords)

    # 3. WARDROBE
    prompt_parts.append(wardrobe)

    # 4. STYLE DNA
    style_components = [
        style_dna.get('medium_era', ''),
        style_dna.get('cinematography', ''),
        style_dna.get('lighting_rendering', ''),
        style_dna.get('color_palette', ''),
    ]
    prompt_parts.append(", ".join(filter(None, style_components)))

    # 5. PANEL BY PANEL LAYOUT
    layout = """Clean layout with multiple views on neutral warm beige background (#d4c4b0). Grid format showing:

TOP ROW: Extreme close-up of eyes showing iris detail and expression | Close-up of natural expression showing mouth and facial structure

LEFT SIDE: Large hero portrait shot, head and shoulders, straight-on angle, natural lighting, eyes looking directly at camera

MIDDLE ROW: Detailed hand reference showing natural hand gesture with character-specific details

BOTTOM ROW: Three portrait headshots showing range of expression - intense/serious, slight smile, neutral/watchful - showing personality through subtle facial variations

RIGHT SIDE: Full body turnaround - front view and back view showing complete outfit, standing naturally, clean lighting"""
    prompt_parts.append(layout)

    # 6. TECHNICAL SPECS
    tech_specs = "Technical specs: High resolution, consistent lighting across all panels, clean composite layout with thin black dividing lines between panels, single character only, maintain exact likeness throughout"
    prompt_parts.append(tech_specs)

    # 7. STYLE REFERENCE
    prompt_parts.append("Style reference: Match character likeness and style from provided reference images")

    return ". ".join(filter(None, prompt_parts))


# ============================================================================
# IMAGE GENERATION
# ============================================================================

def generate_image(prompt, model_id, settings, output_path, negative_prompt=None, seed=None, image_urls=None):
    """Generate an image using FAL.ai, optionally with reference images"""
    model = MODELS[model_id]

    print(f"\n{'='*70}")
    print(f"MODEL: {model['name']} ({model_id})")
    print(f"{'='*70}")
    print(f"\nPROMPT:\n{prompt[:500]}{'...' if len(prompt) > 500 else ''}\n")

    # Check for API key
    fal_key = os.getenv("FAL_KEY")
    if not fal_key:
        print("ERROR: FAL_KEY not found in environment")
        print("Set FAL_KEY environment variable or add to .env file")
        return None

    os.environ["FAL_KEY"] = fal_key

    # Prepare arguments
    arguments = {
        "prompt": prompt,
    }

    # Handle image sizing - nano_banana uses aspect_ratio + resolution
    if model_id == "nano_banana":
        if "aspect_ratio" in settings:
            arguments["aspect_ratio"] = settings["aspect_ratio"]
        if "resolution" in settings:
            arguments["resolution"] = settings["resolution"]
    else:
        # Other models use image_size
        image_size = settings.get('image_size', {"width": 1024, "height": 1024})
        if isinstance(image_size, dict):
            w, h = image_size.get("width", 1024), image_size.get("height", 1024)
            size_map = {
                (1024, 1024): "square_hd",
                (1536, 864): "landscape_16_9",
                (864, 1536): "portrait_16_9",
                (1024, 1536): "portrait_4_3",
                (1536, 1024): "landscape_4_3",
            }
            image_size = size_map.get((w, h), image_size)
        arguments["image_size"] = image_size

    # Add reference images if provided
    if image_urls:
        arguments["image_urls"] = image_urls
        print(f"Reference images: {len(image_urls)}")

    # Add seed for reproducibility
    if seed is not None:
        arguments["seed"] = seed

    # Add model-specific settings
    if model_id == "nano_banana" and negative_prompt:
        arguments["negative_prompt"] = negative_prompt

    if "num_inference_steps" in settings:
        arguments["num_inference_steps"] = settings["num_inference_steps"]
    if "guidance_scale" in settings:
        arguments["guidance_scale"] = settings["guidance_scale"]

    # Select endpoint based on model and whether we have image references
    has_refs = bool(image_urls)
    endpoint = get_endpoint(model_id, modality=None, has_image_refs=has_refs)
    print(f"Endpoint: {endpoint}")

    print(f"Settings: {json.dumps({k: v for k, v in arguments.items() if k not in ['prompt', 'image_urls']}, indent=2)}")
    print("\nGenerating...")

    try:
        def queue_update(update):
            try:
                print(f"  Queue: {type(update).__name__}")
            except:
                pass

        result = fal_client.subscribe(
            endpoint,
            arguments=arguments,
            with_logs=True,
            on_queue_update=queue_update
        )

        # Get image URL
        image_url = None
        if result and "images" in result and len(result["images"]) > 0:
            image_url = result["images"][0]["url"]
        elif result and "image" in result:
            image_url = result["image"]["url"]

        if image_url:
            print(f"\n✓ Generated: {image_url}")

            # Download image
            import requests
            response = requests.get(image_url)

            if response.status_code == 200:
                output_path.parent.mkdir(parents=True, exist_ok=True)

                with open(output_path, "wb") as f:
                    f.write(response.content)

                print(f"✓ Saved: {output_path}")

                # Save metadata
                metadata = {
                    "model_id": model_id,
                    "model_name": model["name"],
                    "timestamp": datetime.now().isoformat(),
                    "prompt": prompt,
                    "seed": arguments.get("seed"),
                    "settings": {k: v for k, v in arguments.items() if k != 'prompt'},
                    "image_url": image_url,
                    "filepath": str(output_path),
                }

                metadata_path = output_path.with_suffix('.json')
                with open(metadata_path, "w") as f:
                    json.dump(metadata, f, indent=2)

                return output_path
            else:
                print(f"✗ Failed to download: {response.status_code}")
                return None
        else:
            print("✗ No image in result")
            return None

    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return None


# ============================================================================
# TEST COMMANDS
# ============================================================================

def run_style_dna_tests(project_path, config, model_id="seedream", seed=None):
    """Run style DNA exploration tests"""
    print(f"\n{'#'*70}")
    print(f"# STYLE DNA EXPLORATION")
    print(f"# Project: {config['project']['name']}")
    print(f"{'#'*70}")

    # Get style DNA templates
    templates = DEFAULT_STYLE_DNA_TEMPLATES

    # Test scenarios
    scenarios = [
        {
            "name": "Lone Figure",
            "subject": "A lone figure silhouetted against a corrupted crimson sky at dusk, standing at the edge of a dead frontier town",
            "composition": "Wide shot, low angle, figure small but dominating composition through stark silhouette",
            "mood": "Ominous arrival, something dark approaching",
            "size": {"width": 1536, "height": 864},
        },
        {
            "name": "Town Aftermath",
            "subject": "Abandoned town at twilight, buildings as geometric shapes, something wrong in the shadows",
            "composition": "Extreme wide shot, symmetrical framing, street receding to vanishing point",
            "mood": "Silent, emptied, violence has already passed through",
            "size": {"width": 1536, "height": 864},
        },
        {
            "name": "Detail Shot",
            "subject": "Smoking revolvers laying in dust, blood splatter on weathered wood, aftermath of violence",
            "composition": "Close shot, dutch angle, objects scattered across frame",
            "mood": "Quiet after the storm, the cost visible in small details",
            "size": {"width": 1024, "height": 1024},
        },
    ]

    # Get output directory
    exports_path = project_path / config['paths'].get('exports', 'EXPORTS')
    style_tests_path = exports_path / "style_tests"
    style_tests_path.mkdir(parents=True, exist_ok=True)

    negative_prompt = ", ".join(config.get('negative_prompts', []))

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    for template_id, template in templates.items():
        print(f"\n{'='*70}")
        print(f"STYLE DNA: {template['name']}")
        print(f"{'='*70}")

        for scenario in scenarios:
            prompt = build_style_dna_prompt(
                template,
                scenario['subject'],
                scenario['composition'],
                scenario['mood']
            )

            settings = {
                "image_size": scenario['size'],
                "num_inference_steps": config['visual']['defaults'].get('num_inference_steps', 35),
                "guidance_scale": config['visual']['defaults'].get('guidance_scale', 4.0),
            }

            filename = f"style_{template_id}_{scenario['name'].lower().replace(' ', '_')}_{model_id}_{timestamp}.png"
            output_path = style_tests_path / filename

            generate_image(prompt, model_id, settings, output_path, negative_prompt, seed=seed)


def run_hero_shots(project_path, config, character_slug, model_id=None, seed=None):
    """Generate hero shots for a character"""
    if model_id is None:
        model_id = config['visual'].get('primary_model', 'seedream')

    # Load character data from config (not markdown parsing)
    char_data = load_character_from_config(config, character_slug)
    if not char_data:
        return

    # Get style DNA from config or use default
    if config['style_dna'].get('locked') and config['style_dna'].get('medium_era'):
        style_dna = config['style_dna']
    else:
        print("Warning: Style DNA not locked in config, using Gothic Western default")
        style_dna = DEFAULT_STYLE_DNA_TEMPLATES['gothic_western']

    print(f"\n{'#'*70}")
    print(f"# HERO SHOTS: {char_data['name']}")
    print(f"# Style DNA: {style_dna.get('name', 'Custom')}")
    print(f"{'#'*70}")

    # Hero shot templates
    hero_shots = [
        {
            "name": "entrance",
            "moment": "Emerging from dust and distance, first appearance, establishing presence",
            "composition": "Medium wide shot, low angle, figure dominating through presence",
            "mood": "Arrival, what they represent made visible",
        },
        {
            "name": "action",
            "moment": "Signature action, the thing they do that defines them",
            "composition": "Dynamic medium shot, capturing motion and intent",
            "mood": "Competence, purpose, who they are when challenged",
        },
        {
            "name": "quiet",
            "moment": "Alone, unguarded, the person beneath the role",
            "composition": "Close medium shot, intimate framing, space around them",
            "mood": "Vulnerability, weight, who they are when no one watches",
        },
    ]

    # Get output directory
    exports_path = project_path / config['paths'].get('exports', 'EXPORTS')
    hero_path = exports_path / "hero_shots" / character_slug
    hero_path.mkdir(parents=True, exist_ok=True)

    negative_prompt = ", ".join(config.get('negative_prompts', []))
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Nano Banana Pro uses aspect_ratio + resolution
    if model_id == "nano_banana":
        settings = {
            "aspect_ratio": "4:3",  # Portrait orientation for hero shots
            "resolution": "2K",
            "num_inference_steps": config['visual']['defaults'].get('num_inference_steps', 40),
            "guidance_scale": config['visual']['defaults'].get('guidance_scale', 4.5),
        }
    else:
        settings = {
            "image_size": config['visual']['defaults'].get('hero_shot_size', {"width": 1024, "height": 1536}),
            "num_inference_steps": config['visual']['defaults'].get('num_inference_steps', 35),
            "guidance_scale": config['visual']['defaults'].get('guidance_scale', 4.0),
        }

    for shot in hero_shots:
        # Check for existing outputs (idempotency)
        # For hero shots, check if ANY file matching the pattern exists
        existing = list(hero_path.glob(f"{character_slug}_{shot['name']}_{model_id}_*.png"))
        if existing:
            should_skip, reason = check_output_exists(existing[0])
            if should_skip:
                print(f"  Skipping {shot['name']}: {reason}")
                log_generation_result(
                    f"hero_shot_{shot['name']}",
                    existing[0],
                    "skipped",
                    {"reason": reason}
                )
                continue

        prompt = build_hero_shot_prompt(
            char_data,
            style_dna,
            shot['moment'],
            shot['composition'],
            shot['mood']
        )

        filename = f"{character_slug}_{shot['name']}_{model_id}_{timestamp}.png"
        output_path = hero_path / filename

        # Dry-run mode
        if AGENTIC_FLAGS["dry_run"]:
            print_dry_run(
                f"generate hero shot '{shot['name']}' for {character_slug}",
                output_path,
                f"Model: {model_id}, Seed: {seed}"
            )
            log_generation_result(
                f"hero_shot_{shot['name']}",
                output_path,
                "dry_run",
                {"model": model_id, "seed": seed}
            )
            continue

        generate_image(prompt, model_id, settings, output_path, negative_prompt, seed=seed)
        log_generation_result(
            f"hero_shot_{shot['name']}",
            output_path,
            "generated",
            {"model": model_id, "seed": seed}
        )


def run_identity_sheet(project_path, config, character_slug, model_id=None, seed=None):
    """Generate identity sheet for a character using hero shots as reference"""
    if model_id is None:
        model_id = config['visual'].get('technical_model', 'nano_banana')

    # Load character data from config (not markdown parsing)
    char_data = load_character_from_config(config, character_slug)
    if not char_data:
        return

    # Get style DNA from config
    style_dna = config.get('style_dna', DEFAULT_STYLE_DNA_TEMPLATES['gothic_western'])
    hex_palette = style_dna.get('hex_palette', [])

    # Check for character-specific palette
    char_config = config.get('characters', {}).get(character_slug, {})
    if char_config.get('palette'):
        hex_palette = char_config['palette']

    # Find and upload hero shots as reference images
    exports_path = project_path / config['paths'].get('exports', 'EXPORTS')
    hero_path = exports_path / "hero_shots" / character_slug

    image_urls = []
    if hero_path.exists():
        hero_files = sorted(hero_path.glob("*.png"), key=lambda p: p.stat().st_mtime, reverse=True)
        # Get the 3 most recent hero shots
        hero_files = hero_files[:3]

        if hero_files:
            print(f"\nUploading {len(hero_files)} hero shots as reference images...")
            for hero_file in hero_files:
                print(f"  Uploading: {hero_file.name}")
                url = fal_client.upload_file(str(hero_file))
                image_urls.append(url)
                print(f"    ✓ {url[:60]}...")

    if not image_urls:
        print("\nWARNING: No hero shots found. Generate hero shots first for best results.")
        print(f"  Run: --hero {character_slug}")

    print(f"\n{'#'*70}")
    print(f"# IDENTITY SHEET: {char_data['name']}")
    print(f"# Model: {MODELS[model_id]['name']}")
    print(f"# Reference images: {len(image_urls)}")
    print(f"{'#'*70}")

    prompt = build_identity_sheet_prompt(char_data, style_dna, hex_palette)

    # Get output directory
    identity_path = exports_path / "identity_sheets"
    identity_path.mkdir(parents=True, exist_ok=True)

    # Check for existing identity sheet (idempotency)
    existing = list(identity_path.glob(f"{character_slug}_identity_{model_id}_*.png"))
    if existing:
        should_skip, reason = check_output_exists(existing[0])
        if should_skip:
            print(f"  Identity sheet: {reason}")
            log_generation_result(
                "identity_sheet",
                existing[0],
                "skipped",
                {"reason": reason}
            )
            return

    negative_prompt = ", ".join(config.get('negative_prompts', []))
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Nano Banana Pro uses resolution + aspect_ratio, not image_size
    settings = {
        "aspect_ratio": "5:4",
        "resolution": "2K",
        "num_inference_steps": 40,
        "guidance_scale": 4.5,
    }

    filename = f"{character_slug}_identity_{model_id}_{timestamp}.png"
    output_path = identity_path / filename

    # Dry-run mode
    if AGENTIC_FLAGS["dry_run"]:
        print_dry_run(
            f"generate identity sheet for {character_slug}",
            output_path,
            f"Model: {model_id}, References: {len(image_urls)}"
        )
        log_generation_result(
            "identity_sheet",
            output_path,
            "dry_run",
            {"model": model_id, "seed": seed, "reference_count": len(image_urls)}
        )
        return

    generate_image(prompt, model_id, settings, output_path, negative_prompt, seed=seed, image_urls=image_urls)
    log_generation_result(
        "identity_sheet",
        output_path,
        "generated",
        {"model": model_id, "seed": seed, "reference_count": len(image_urls)}
    )


# ============================================================================
# STORYBOARDS & LOCATIONS
# ============================================================================

# Storyboard definitions (shared constant)
STORYBOARDS = {
    "sc01-cold-open": {
        "scene": "SC01 - The Clearing (Cold Open)",
        "location": "Abandoned Building Interior",
        "time": "Night - moonlight through cracks",
        "characters": "Nameless, Zombies",
        "purpose": "Establish visual style, introduce protagonist",
        "grid": """3×2 storyboard composite grid on light gray background (#e0e0e0). Professional animation storyboard format. Black and white sketch style, simple line art blocking.

TOP ROW (left to right):
SHOT 1: Black screen with title text "Silver Creek, Colorado - Night" in simple lettering, minimal composition
SHOT 2: Door bursting open, tall figure silhouette in doorway, simple shapes blocking, dramatic entrance angle
SHOT 3: Interior scene with muzzle flash indicated by radiating lines, zombie figure mid-attack simple sketch, action staging

BOTTOM ROW (left to right):
SHOT 4: Multiple figure silhouettes in chaos, motion lines indicating gunfire and action, simple blocking sketch
SHOT 5: Single figure walking through fallen shapes, smoke indicated by loose sketchy lines, relentless walk cycle
SHOT 6: Close-up on figure's face in simple line art, moonlight shaft indicated by hatching, weathered features minimal detail""",
    },
    "sc08-the-nest": {
        "scene": "SC08 - The Nest (Climax)",
        "location": "Nest Cavern Boss Arena",
        "time": "Midday underground - unnatural light",
        "characters": "Nameless, Minnie, Boss Creature",
        "purpose": "Action climax, reveal immortality, partnership moment",
        "grid": """3×2 storyboard composite grid on light gray background (#e0e0e0). Professional animation storyboard format. Black and white sketch style, simple line art blocking.

TOP ROW (left to right):
SHOT 1: Wide cavern sketch, large organic mass on ceiling blocked in with simple shapes, tiny figure below for scale
SHOT 2: Large creature figure looming, twisted body shape blocked in simple lines, threatening pose and scale
SHOT 3: Two figures in combat, motion lines showing impact, simple action staging with dramatic angle

BOTTOM ROW (left to right):
SHOT 4: Figure standing with sketch lines showing body recovering, second smaller figure watching, simple staging for reveal moment
SHOT 5: Small figure throwing object, fire indicated by radiating sketch lines spreading to nest, action trajectory clear
SHOT 6: Nest mass breaking apart with debris lines, two figure silhouettes standing in foreground, aftermath composition""",
    },
    "sc10-the-names": {
        "scene": "SC10 - The Names (Iconic Ending)",
        "location": "Open Prairie",
        "time": "Dusk - golden hour to twilight",
        "characters": "Nameless, Minnie",
        "purpose": "Establish series dynamic, iconic closing image",
        "grid": """3×2 storyboard composite grid on light gray background (#e0e0e0). Professional animation storyboard format. Black and white sketch style, simple line art blocking.

TOP ROW (left to right):
SHOT 1: Wide prairie sketch with simple horizon line, two tiny figures on horse, vast empty space composition
SHOT 2: Medium shot simple blocking, two figures on horse, basic shapes and positioning, moving forward
SHOT 3: Close-up on face in simple line art, minimal detail, expression sketch with speech indication

BOTTOM ROW (left to right):
SHOT 4: Medium on second figure, simple facial expression sketch, dialogue moment composition
SHOT 5: Two figures on horse, simple sketch with internal struggle indicated subtly, keeps riding forward
SHOT 6: WIDE composition - two silhouettes walking toward horizon line, simple shapes against sky, minimal detail iconic framing""",
    },
    # -------------------------------------------------------------------------
    # PIRATE-ROMANCE: The Cartographer's Daughter
    # -------------------------------------------------------------------------
    "pr-sc02-naval-infiltration": {
        "scene": "SC02 - Naval Infiltration (Ledger Discovery)",
        "location": "Naval Compound Exterior → Holding Cells Interior → Silas's Cell",
        "time": "Dusk to Night - wrong-blue moonlight",
        "characters": "Mars",
        "purpose": "Mars infiltrates compound, discovers the Ledger, first supernatural contact",
        "grid": """3×2 storyboard composite grid on light gray background (#e0e0e0). Professional animation storyboard format. Black and white sketch style, simple line art blocking.

TOP ROW (left to right):
SHOT 1: Wide establishing of naval compound walls at dusk, high stone walls with iron gates, tiny figure of Mars in shadow at eastern wall, scale composition showing massive colonial architecture against small determined figure
SHOT 2: Mars climbing drainage pipe on compound wall, figure silhouette against amber dusk sky, motion lines indicating upward movement, last light catching her shape
SHOT 3: Interior cell corridor, Mars dropping through window, wrong-blue moonlight through barred windows indicated by hatching, long perspective of iron doors stretching into darkness

BOTTOM ROW (left to right):
SHOT 4: Mars standing in doorway of cell, silhouetted by teal-tinged light from corridor behind, small empty cell interior with cot and bucket, something lingers in the air indicated by loose sketch lines
SHOT 5: Close-up on hands working at mortar with small blade, stone dust falling indicated by small particles, ink-stained fingers against rough stone, tactile tension composition
SHOT 6: Mars holding the Ledger, wrong-blue glow illuminating her face from below, book pulsing indicated by radiating lines, her expression a mix of horror and recognition""",
    },
}

# Location definitions (shared constant)
LOCATIONS = {
    "dead-town": {
        "name": "Silver Creek Main Street",
        "description": "Abandoned frontier town main street. Buildings weathered and boarded. Dark organic corruption spreading from mine. Wanted posters flutter. Wrong, emptied, violence already passed through",
        "grid": """2×2 composite reference grid on neutral dark background (#2d2d2d). Professional location reference sheet format.

TOP LEFT: Wide establishing of main street from center, symmetrical framing, town receding to vanishing point, massive negative space in sky
TOP RIGHT: Mid-shot down street showing corruption thickening toward mine, buildings decay, organic growths on wood
BOTTOM LEFT: Boarded building detail, weathered wood, broken windows, dark stains, frontier architecture
BOTTOM RIGHT: Wanted poster detail, fluttering paper on wall, corruption spreading across surface, frontier typography""",
        "time": "Dawn - harsh flat light revealing decay",
    },
    "building-int": {
        "name": "Abandoned Building Interior",
        "description": "Interior of abandoned building. Broken furniture, debris, confined space. Moonlight cutting through gaps. High contrast for gunfire effect",
        "grid": """2×2 composite reference grid on neutral dark background (#2d2d2d). Professional location reference sheet format.

TOP LEFT: Doorway angle, silhouette frame, darkness beyond, iconic entrance composition
TOP RIGHT: Interior from door, moonlight cutting through cracks in walls, debris scattered, shadows dominant
BOTTOM LEFT: Corner shadows, confined space, broken furniture, staging area for close combat
BOTTOM RIGHT: Window detail, moonlight shaft through broken boards, volumetric light cutting darkness""",
        "time": "Night - moonlight through cracks, high contrast",
    },
    "mine-int": {
        "name": "Corrupted Mine Interior",
        "description": "Old mining tunnels corrupted by supernatural infestation. Wooden support beams rotting. Dark organic matter on walls. Descent into corruption and darkness",
        "grid": """2×2 composite reference grid on neutral dark background (#2d2d2d). Professional location reference sheet format.

TOP LEFT: Mine entrance from outside, darkness within, corruption visible at threshold, wooden frame rotting
TOP RIGHT: Upper tunnel perspective, wood support beams, corruption on walls, lantern light fading into darkness
BOTTOM LEFT: Junction area where three tunnels branch, darkness in each direction, decision point
BOTTOM RIGHT: Passage detail close-up of corruption, organic growths on stone and wood, wrongness made visible""",
        "time": "Morning - progressive darkness from entrance to deep",
    },
    "nest-cavern": {
        "name": "Nest Cavern Boss Arena",
        "description": "Large underground cavern at end of mine. Nest visible above - organic mass, eggs, corruption at its source. Arena-like open space. High ceiling. Heart of the infestation",
        "grid": """2×2 composite reference grid on neutral dark background (#2d2d2d). Professional location reference sheet format.

TOP LEFT: Wide cavern establishing, nest visible above on ceiling, scale of space, high ceiling, arena floor
TOP RIGHT: Arena floor view looking up at nest, organic mass hanging, eggs visible, threatening presence
BOTTOM LEFT: Ceiling and nest detail, eggs, corruption dripping downward, organic horror
BOTTOM RIGHT: Exit tunnel angle, escape route visible, light from passage back, contrast with cavern darkness""",
        "time": "Midday but dark - dim light from shaft above",
    },
    "open-road": {
        "name": "Open Prairie Frontier",
        "description": "Endless open prairie. Dirt road cutting through. Vast empty sky. Isolation and scale. The frontier that goes on forever toward the hellmouth",
        "grid": """2×2 composite reference grid on neutral dark background (#2d2d2d). Professional location reference sheet format.

TOP LEFT: Wide prairie establishing, vast empty sky dominating, dirt road cutting through scrub, massive scale
TOP RIGHT: Road perspective with vanishing point, dirt and scrub on either side, emptiness stretching ahead
BOTTOM LEFT: Horizon line at dusk, sky transition, scale reference showing figure would be tiny
BOTTOM RIGHT: Dusk atmosphere detail, corrupted crimson sky, volumetric dust, blood-red punctuation in clouds""",
        "time": "Dusk - golden hour transitioning to twilight",
    },
}


def build_location_prompt(loc_config, style_dna, hex_palette, mode="photorealistic"):
    """Build a well-structured location reference prompt using prompt-engineer skill techniques.

    Modes:
    - photorealistic: Production stills look (default) - cinematographer's lookbook
    - concept: Concept art style - allows painterly/ethereal language

    Photorealistic mode uses:
    - Camera/lens specifications
    - Film stock references
    - Material physics over vibe words
    - "Practical set construction" power phrase
    """
    name = loc_config.get('name', 'Unknown Location')
    visual_keywords = loc_config.get('visual_keywords', '')
    palette = loc_config.get('palette', hex_palette[:6])

    # Format hex palette for prompt
    palette_str = ', '.join(palette) if palette else ', '.join(hex_palette[:6])

    if mode == "photorealistic":
        # PHOTOREALISTIC MODE: Frame as cinematographer's lookbook / location scout gallery
        # Uses technical camera language, material physics, practical set construction

        prompt = f"""Location scout reference gallery for a period film production. Setting: {name}.

Physical Description: {visual_keywords}

The Grid Layout (Neutral #2d2d2d background, thin dividers):

Top Left (Wide Establishing): Golden hour exterior, 24mm anamorphic lens, f/4 deep focus. Atmospheric perspective showing full environment scale. Shot on ARRI Alexa, Kodak Vision3 500T.

Top Right (Interior/Detail): Key architectural feature, practical light sources visible in frame. Hard shadows from directional light, dust particles catching light beams. 35mm spherical lens, f/2.8.

Bottom Left (Texture Close-up): Macro detail of material surfaces - weathered wood grain, oxidized metal, damp stone, condensation, salt deposits. Tangible material physics, environmental storytelling through wear patterns.

Bottom Right (Alt Lighting): Same location under different lighting - moonlight through windows, oil lantern practicals, firelight. Shows how the space transforms. Natural color temperature shifts.

Technical: Period-accurate 1720s Caribbean colonial architecture. Practical set construction, location scout photograph. High production value, 8k resolution.

Color Palette: [{palette_str}]"""

    else:
        # CONCEPT MODE: Allows painterly/ethereal language for early development
        prompt = f"""Cinematic concept art location reference for a YA historical fantasy film. Setting: {name}.

Visual Narrative: {visual_keywords}

The Grid Layout (Neutral #2d2d2d background, thin black dividers):

Top Left (Wide): Establishing shot at golden hour. Atmospheric perspective, soaring scale.
Top Right (Medium): Interior or key architectural detail. Dramatic light beams cutting through atmosphere.
Bottom Left (Close-up): Macro detail of textures - weathered surfaces, environmental storytelling.
Bottom Right (Alt Angle): Alternative lighting condition - moonlight, or supernatural coloring.

Style: Cinematic concept art, high detail, painterly finish.

Color Palette: [{palette_str}]"""

    return prompt


def run_location_ref(project_path, config, location_slug, model_id=None, seed=None, mode="photorealistic"):
    """Generate 2x2 location reference grid in 16:9 aspect ratio.

    Modes:
    - photorealistic: Cinematographer's lookbook style (default)
    - concept: Painterly concept art style
    """
    if model_id is None:
        model_id = config['visual'].get('primary_model', 'seedream')

    # Check config locations first, fall back to hardcoded LOCATIONS
    config_locations = config.get('locations', {})
    if location_slug in config_locations:
        loc_config = config_locations[location_slug]
    elif location_slug in LOCATIONS:
        # Convert old format to new format
        old_loc = LOCATIONS[location_slug]
        loc_config = {
            'name': old_loc.get('name', location_slug),
            'visual_keywords': old_loc.get('description', ''),
            'episode': 'N/A',
        }
    else:
        available = list(config_locations.keys()) + list(LOCATIONS.keys())
        print(f"ERROR: Unknown location '{location_slug}'")
        print(f"Available: {', '.join(available)}")
        return

    # Get style DNA from config
    style_dna = config.get('style_dna', DEFAULT_STYLE_DNA_TEMPLATES['gothic_western'])
    hex_palette = style_dna.get('hex_palette', [])

    print(f"\n{'#'*70}")
    print(f"# LOCATION: {loc_config.get('name', location_slug)}")
    print(f"# Episode: {loc_config.get('episode', 'N/A')}")
    print(f"# Model: {MODELS[model_id]['name']}")
    print(f"{'#'*70}")

    # Build well-structured prompt using specified mode
    prompt = build_location_prompt(loc_config, style_dna, hex_palette, mode=mode)

    # Get output directory
    exports_path = project_path / config['paths'].get('exports', 'EXPORTS')
    location_path = exports_path / "location_refs"
    location_path.mkdir(parents=True, exist_ok=True)

    # Check for existing location ref (idempotency)
    existing = list(location_path.glob(f"{location_slug}_ref_{model_id}_*.png"))
    if existing:
        should_skip, reason = check_output_exists(existing[0])
        if should_skip:
            print(f"  Location ref: {reason}")
            log_generation_result(
                "location_ref",
                existing[0],
                "skipped",
                {"reason": reason, "location": location_slug}
            )
            return

    # Use mode-appropriate negative prompt
    base_negative = config.get('negative_prompts', [])
    if mode == "photorealistic":
        mode_negative = NEGATIVE_PROMPTS.get('photorealistic', [])
    else:
        mode_negative = []  # Concept mode uses base negative only
    negative_prompt = ", ".join(base_negative + mode_negative)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Use 16:9 aspect ratio for cinematic location refs
    settings = {
        "aspect_ratio": "16:9",
        "resolution": "2K",
        "num_inference_steps": config['visual']['defaults'].get('num_inference_steps', 40),
        "guidance_scale": config['visual']['defaults'].get('guidance_scale', 4.5),
    }

    filename = f"{location_slug}_ref_{model_id}_{timestamp}.png"
    output_path = location_path / filename

    # Dry-run mode
    if AGENTIC_FLAGS["dry_run"]:
        print_dry_run(
            f"generate location ref for {location_slug}",
            output_path,
            f"Model: {model_id}, Mode: {mode}"
        )
        log_generation_result(
            "location_ref",
            output_path,
            "dry_run",
            {"model": model_id, "seed": seed, "location": location_slug, "mode": mode}
        )
        return

    generate_image(prompt, model_id, settings, output_path, negative_prompt, seed=seed)
    log_generation_result(
        "location_ref",
        output_path,
        "generated",
        {"model": model_id, "seed": seed, "location": location_slug, "mode": mode}
    )


def run_storyboard(project_path, config, storyboard_slug, model_id=None, seed=None):
    """Generate 3x2 storyboard grid for a scene"""
    if model_id is None:
        model_id = config['visual'].get('technical_model', 'nano_banana')

    if storyboard_slug not in STORYBOARDS:
        print(f"ERROR: Unknown storyboard '{storyboard_slug}'")
        print(f"Available: {', '.join(STORYBOARDS.keys())}")
        return

    story = STORYBOARDS[storyboard_slug]

    print(f"\n{'#'*70}")
    print(f"# STORYBOARD: {story['scene']}")
    print(f"# Location: {story['location']}")
    print(f"# Time: {story['time']}")
    print(f"# Characters: {story['characters']}")
    print(f"# Style: Black & white sketch blocking")
    print(f"# Model: {MODELS[model_id]['name']}")
    print(f"{'#'*70}")

    # Build prompt - SKETCH STYLE for storyboards
    components = [
        story['grid'],
        f"Scene: {story['scene']}. {story['purpose']}",
        f"Characters: {story['characters']}",
        f"Location: {story['location']}",
        f"Time: {story['time']}",
        "Simple black and white sketch style, animation storyboard blocking. Clean line art with minimal detail.",
        "Focus on composition, camera angle, character staging, and action flow.",
        "Simple shapes and silhouettes. Value blocking with hatching for shadows.",
        "NOT fully rendered - compositional reference only for applying final style and character designs later.",
        "Technical: Thin black dividing lines between panels. Cinematic 16:9 framing within each panel. Each shot shows clear staging and composition for animation keyframes. Shot numbers and brief descriptions below each panel.",
    ]

    prompt = ". ".join(filter(None, components))

    # Get output directory
    exports_path = project_path / config['paths'].get('exports', 'EXPORTS')
    storyboard_path = exports_path / "storyboards" / "EP01"
    storyboard_path.mkdir(parents=True, exist_ok=True)

    # Storyboard-specific negative prompts (avoid full rendering)
    base_negative = config.get('negative_prompts', [])
    storyboard_negative = base_negative + [
        "full color",
        "detailed rendering",
        "painted style",
        "photorealistic",
        "finished artwork",
        "detailed textures",
        "shading",
        "cel shading",
        "digital painting",
        "concept art"
    ]
    negative_prompt = ", ".join(storyboard_negative)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    settings = {
        "image_size": {"width": 1536, "height": 1024},  # Landscape for 3x2 grid
        "num_inference_steps": 40,
        "guidance_scale": 4.5,
    }

    filename = f"{storyboard_slug}_storyboard_{model_id}_{timestamp}.png"
    output_path = storyboard_path / filename

    generate_image(prompt, model_id, settings, output_path, negative_prompt, seed=seed)


def run_final_frame(project_path, config, scene_slug, shot_number, character_slugs=None):
    """Generate final production frame with image references (CORRECT Nano Banana Pro usage)"""

    print(f"\n{'#'*70}")
    print(f"# FINAL FRAME: {scene_slug} Shot {shot_number}")
    print(f"# Using TRUE image references (CORRECTED method)")
    print(f"# Model: Nano Banana Pro (fal-ai/nano-banana-pro)")
    print(f"{'#'*70}")

    # Get style DNA
    style_dna = config.get('style_dna', DEFAULT_STYLE_DNA_TEMPLATES['gothic_western'])

    # Prepare to upload references
    try:
        import fal_client
    except ImportError:
        print("ERROR: fal_client required. Install with: pip install fal-client")
        return

    # Upload character identity sheets
    exports_path = project_path / config['paths'].get('exports', 'EXPORTS')
    identity_path = exports_path / "identity_sheets"

    image_urls = []

    # If specific characters provided, upload their identity sheets
    if character_slugs:
        for char_slug in character_slugs:
            # Find most recent identity sheet for this character
            identity_files = list(identity_path.glob(f"identity_{char_slug}_*.png"))
            if identity_files:
                latest = sorted(identity_files, key=lambda p: p.stat().st_mtime, reverse=True)[0]
                print(f"Uploading {char_slug} identity sheet: {latest.name}")
                url = fal_client.upload_file(str(latest))
                image_urls.append(url)
                print(f"  ✓ {url}")
            else:
                print(f"WARNING: No identity sheet found for {char_slug}")

    # Upload location reference if available
    # TODO: Add logic to determine which location based on scene

    print(f"\n{'='*70}")
    print("⚠️  MANUAL PROMPT REQUIRED")
    print("This function requires manual prompt composition.")
    print("See ANIMATION_PIPELINE_CORRECTED.md for usage.")
    print(f"{'='*70}\n")

    print("Example usage in Python:")
    print("""
import fal_client

# Upload references
nameless_ref = fal_client.upload_file("EXPORTS/identity_sheets/identity_nameless_nano_banana_[timestamp].png")
minnie_ref = fal_client.upload_file("EXPORTS/identity_sheets/identity_minnie_nano_banana_[timestamp].png")
location_ref = fal_client.upload_file("EXPORTS/location_refs/open-road_ref_seedream_[timestamp].png")

# Compose prompt
prompt = '''[Shot composition description]

Use character designs from reference images.
Use location atmosphere from reference.

[Style DNA]'''

# Generate with CORRECT parameters
result = fal_client.subscribe(
    "fal-ai/nano-banana-pro",
    arguments={
        "prompt": prompt,
        "image_urls": [nameless_ref, minnie_ref, location_ref],
        "aspect_ratio": "16:9",
        "resolution": "2K",
        "num_images": 1,
        "output_format": "png"
    }
)

# Save result
image_url = result["images"][0]["url"]
    """)


def main():
    parser = argparse.ArgumentParser(
        description="Codeywood FAL.ai Generation Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Run style DNA exploration tests
    python fal_generate.py --test style_dna

    # Generate hero shots for a character
    python fal_generate.py --hero nameless

    # Generate identity sheet for a character
    python fal_generate.py --identity minnie-chance

    # Generate single location reference grid
    python fal_generate.py --location dead-town

    # Generate all location reference grids (batch)
    python fal_generate.py --all-locations

    # Generate single storyboard scene
    python fal_generate.py --storyboard sc01-cold-open

    # Generate all storyboards (batch)
    python fal_generate.py --all-storyboards

    # Specify model explicitly
    python fal_generate.py --hero nameless --model seedream

    # Run from different directory
    python fal_generate.py --project /path/to/project --test style_dna
        """
    )

    parser.add_argument("--project", help="Path to project directory (default: current directory)")
    parser.add_argument("--test", choices=["style_dna"], help="Run test type")
    parser.add_argument("--hero", metavar="CHARACTER", help="Generate hero shots for character")
    parser.add_argument("--identity", metavar="CHARACTER", help="Generate identity sheet for character")
    parser.add_argument("--location", metavar="LOCATION", help="Generate location reference grid")
    parser.add_argument("--all-locations", action="store_true", help="Generate all location reference grids")
    parser.add_argument("--storyboard", metavar="SCENE", help="Generate storyboard for scene")
    parser.add_argument("--all-storyboards", action="store_true", help="Generate all storyboard scenes")
    parser.add_argument("--model", choices=list(MODELS.keys()), help="Model to use")
    parser.add_argument("--seed", type=int, help="Random seed for reproducibility")
    parser.add_argument("--mode", choices=["photorealistic", "concept"], default="photorealistic",
                        help="Prompt mode: photorealistic (production stills) or concept (painterly art)")
    parser.add_argument("--list-models", action="store_true", help="List available models")

    # Agentic primitives flags
    parser.add_argument("--dry-run", action="store_true",
                        help="Preview what would be generated without executing")
    parser.add_argument("--force", action="store_true",
                        help="Overwrite existing outputs (default: skip if exists)")
    parser.add_argument("--json", action="store_true",
                        help="Output results as JSON for structured parsing")

    args = parser.parse_args()

    # Set agentic flags
    AGENTIC_FLAGS["dry_run"] = args.dry_run
    AGENTIC_FLAGS["force"] = args.force
    AGENTIC_FLAGS["json_output"] = args.json

    if args.dry_run and not args.json:
        print("\n" + "=" * 70)
        print("DRY-RUN MODE: No actual generation will occur")
        print("=" * 70)

    if args.list_models:
        print("\nAvailable Models:")
        print("=" * 60)
        for model_id, model in MODELS.items():
            print(f"\n{model_id:15s} - {model['name']}")
            print(f"{'':15s}   {model['best_for']}")
        return

    # Find project
    if args.project:
        project_path = Path(args.project)
    else:
        project_path = find_project_root()

    if not project_path:
        print("ERROR: Could not find project (no PROJECT_CONFIG.yaml found)")
        print("Either run from a project directory or specify --project")
        sys.exit(1)

    print(f"Project: {project_path}")

    # Load config
    config = load_project_config(project_path)

    # Run requested command
    if args.test == "style_dna":
        model = args.model or config['visual'].get('primary_model', 'seedream')
        run_style_dna_tests(project_path, config, model, seed=args.seed)

    elif args.hero:
        run_hero_shots(project_path, config, args.hero, args.model, seed=args.seed)

    elif args.identity:
        run_identity_sheet(project_path, config, args.identity, args.model, seed=args.seed)

    elif args.all_locations:
        print(f"\n{'='*70}")
        print(f"GENERATING ALL LOCATION REFERENCES (mode: {args.mode})")
        print(f"{'='*70}\n")
        # Use config locations if available, otherwise fall back to hardcoded
        config_locations = config.get('locations', {})
        location_slugs = list(config_locations.keys()) if config_locations else list(LOCATIONS.keys())
        for location_slug in location_slugs:
            run_location_ref(project_path, config, location_slug, args.model, seed=args.seed, mode=args.mode)
        print(f"\n{'='*70}")
        print(f"ALL LOCATIONS COMPLETE")
        print(f"{'='*70}")

    elif args.location:
        run_location_ref(project_path, config, args.location, args.model, seed=args.seed, mode=args.mode)

    elif args.all_storyboards:
        print(f"\n{'='*70}")
        print(f"GENERATING ALL STORYBOARDS (EP01 PRIORITY SCENES)")
        print(f"{'='*70}\n")
        for storyboard_slug in STORYBOARDS.keys():
            run_storyboard(project_path, config, storyboard_slug, args.model, seed=args.seed)
        print(f"\n{'='*70}")
        print(f"ALL STORYBOARDS COMPLETE")
        print(f"{'='*70}")

    elif args.storyboard:
        run_storyboard(project_path, config, args.storyboard, args.model, seed=args.seed)

    else:
        parser.print_help()
        return

    # Update state file with execution results (unless dry-run)
    if not AGENTIC_FLAGS["dry_run"] and GENERATION_RESULTS:
        # Build command string
        cmd_parts = ["fal_generate.py"]
        if args.hero:
            cmd_parts.extend(["--hero", args.hero])
        if args.identity:
            cmd_parts.extend(["--identity", args.identity])
        if args.location:
            cmd_parts.extend(["--location", args.location])
        if args.all_locations:
            cmd_parts.append("--all-locations")
        if args.storyboard:
            cmd_parts.extend(["--storyboard", args.storyboard])
        if args.all_storyboards:
            cmd_parts.append("--all-storyboards")
        if args.model:
            cmd_parts.extend(["--model", args.model])
        if args.seed:
            cmd_parts.extend(["--seed", str(args.seed)])

        # Collect output paths from successful generations
        output_paths = [r["output_path"] for r in GENERATION_RESULTS if r.get("status") == "generated"]

        if output_paths:
            update_state_file(
                project_path,
                command=" ".join(cmd_parts),
                output_paths=output_paths,
                status="success",
                metadata={"model": args.model or "default", "seed": args.seed}
            )

    # Output JSON results if requested
    if AGENTIC_FLAGS["json_output"]:
        output_json_results()


if __name__ == "__main__":
    main()
