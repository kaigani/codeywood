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
import argparse
import re
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


def load_character_sheet(project_path, character_slug):
    """Load character sheet markdown and extract visual/psychological data"""
    config = load_project_config(project_path)
    char_sheets_path = project_path / config['paths']['character_sheets']

    # Try different naming conventions
    possible_names = [
        f"{character_slug.upper()}.md",
        f"{character_slug.replace('-', '_').upper()}.md",
        f"{character_slug.title().replace('-', '_')}.md",
        f"{character_slug}.md",
    ]

    char_file = None
    for name in possible_names:
        path = char_sheets_path / name
        if path.exists():
            char_file = path
            break

    if not char_file:
        print(f"ERROR: Character sheet not found for '{character_slug}'")
        print(f"Looked in: {char_sheets_path}")
        return None

    with open(char_file, 'r') as f:
        content = f.read()

    # Extract key information
    character_data = {
        'slug': character_slug,
        'name': extract_field(content, 'Full Name') or character_slug.title(),
        'physical_description': extract_code_block(content, 'Physical Description'),
        'wardrobe': extract_code_block(content, 'Signature Outfit') or extract_code_block(content, 'Wardrobe'),
        'keywords': extract_code_block(content, 'Image Generation Keywords'),
        'negative_prompts': extract_code_block(content, 'Negative Prompts'),
        'one_line': extract_quote(content, 'One-Line Description'),
    }

    return character_data


def extract_field(content, field_name):
    """Extract a field value from markdown table or line"""
    pattern = rf'\|\s*{field_name}\s*\|\s*([^|]+)\s*\|'
    match = re.search(pattern, content)
    if match:
        return match.group(1).strip()
    return None


def extract_code_block(content, header):
    """Extract content from a code block under a header"""
    pattern = rf'(?:###?\s*{header}|{header})\s*\n```[^\n]*\n(.*?)```'
    match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return None


def extract_quote(content, header):
    """Extract a blockquote under a header"""
    pattern = rf'###?\s*{header}\s*\n>\s*(.+)'
    match = re.search(pattern, content, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return None


# ============================================================================
# MODEL DEFINITIONS
# ============================================================================

MODELS = {
    "seedream": {
        "endpoint": "fal-ai/bytedance/seedream/v4.5/text-to-image",
        "name": "SeeDream v4.5",
        "best_for": "Artistic styles, painterly, stylized",
    },
    "hunyuan": {
        "endpoint": "fal-ai/hunyuan-image/v3/instruct/text-to-image",
        "name": "Hunyuan Image 3.0",
        "best_for": "Artistic styles, illustration",
    },
    "grok": {
        "endpoint": "xai/grok-imagine-image",
        "name": "Grok Imagine",
        "best_for": "Artistic exploration, creative styles",
    },
    "nano_banana": {
        "endpoint": "fal-ai/nano-banana-pro",
        "name": "Nano Banana Pro",
        "best_for": "Precise style refs, prompt handling, technical refs",
    },
}


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
        character_data.get('physical_description', ''),
        character_data.get('wardrobe', ''),
        moment,
        style_dna['medium_era'],
        style_dna['linework_texture'],
        style_dna['lighting_rendering'],
        composition,
        mood,
        style_dna['color_palette'],
    ]
    return ". ".join(filter(None, components))


def build_identity_sheet_prompt(character_data, style_dna, hex_palette=None):
    """Build an identity sheet prompt with composite layout"""
    char_desc = character_data.get('physical_description', '')
    wardrobe = character_data.get('wardrobe', '')

    layout = f"""Clean layout with multiple character views on neutral warm beige background (#d4c4b0). Professional character reference sheet format.

TOP ROW (left to right):
- Extreme close-up of eyes, heavy ink outlines
- Close-up of face profile
- Hands reference shot

MIDDLE SECTION (large):
- Full body front view with signature wardrobe, commanding presence
- Full body back view, silhouette quality

BOTTOM ROW (left to right):
- Portrait showing vulnerability or alternate expression
- Signature action pose
- Quiet moment or alternate state

Technical: Dark animated style with heavy ink outlines, crisp silhouettes, cel-shaded shadows, high contrast. Thin black dividing lines between panels. Consistent lighting across all views"""

    components = [
        char_desc,
        wardrobe,
        layout,
    ]

    if hex_palette:
        hex_str = '", "'.join(hex_palette)
        components.append(f'Color grading: ["{hex_str}"]')

    return ". ".join(filter(None, components))


# ============================================================================
# IMAGE GENERATION
# ============================================================================

def generate_image(prompt, model_id, settings, output_path, negative_prompt=None, seed=None):
    """Generate an image using FAL.ai"""
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

    # Convert image_size dict to standard literal if possible
    image_size = settings.get('image_size', {"width": 1024, "height": 1024})
    if isinstance(image_size, dict):
        w, h = image_size.get("width", 1024), image_size.get("height", 1024)
        # Map common sizes to fal literals
        size_map = {
            (1024, 1024): "square_hd",
            (1536, 864): "landscape_16_9",
            (864, 1536): "portrait_16_9",
            (1024, 1536): "portrait_4_3",
            (1536, 1024): "landscape_4_3",
        }
        image_size = size_map.get((w, h), image_size)  # Use literal or keep dict

    # Prepare arguments
    arguments = {
        "prompt": prompt,
        "image_size": image_size,
    }

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

    print(f"Settings: {json.dumps({k: v for k, v in arguments.items() if k != 'prompt'}, indent=2)}")
    print("\nGenerating...")

    try:
        def queue_update(update):
            try:
                print(f"  Queue: {type(update).__name__}")
            except:
                pass

        result = fal_client.subscribe(
            model["endpoint"],
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

    # Load character data
    char_data = load_character_sheet(project_path, character_slug)
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

    settings = {
        "image_size": config['visual']['defaults'].get('hero_shot_size', {"width": 1024, "height": 1536}),
        "num_inference_steps": config['visual']['defaults'].get('num_inference_steps', 35),
        "guidance_scale": config['visual']['defaults'].get('guidance_scale', 4.0),
    }

    for shot in hero_shots:
        prompt = build_hero_shot_prompt(
            char_data,
            style_dna,
            shot['moment'],
            shot['composition'],
            shot['mood']
        )

        filename = f"{character_slug}_{shot['name']}_{model_id}_{timestamp}.png"
        output_path = hero_path / filename

        generate_image(prompt, model_id, settings, output_path, negative_prompt, seed=seed)


def run_identity_sheet(project_path, config, character_slug, model_id=None, seed=None):
    """Generate identity sheet for a character"""
    if model_id is None:
        model_id = config['visual'].get('technical_model', 'nano_banana')

    # Load character data
    char_data = load_character_sheet(project_path, character_slug)
    if not char_data:
        return

    # Get style DNA from config
    style_dna = config.get('style_dna', DEFAULT_STYLE_DNA_TEMPLATES['gothic_western'])
    hex_palette = style_dna.get('hex_palette', [])

    # Check for character-specific palette
    char_config = config.get('characters', {}).get(character_slug, {})
    if char_config.get('palette'):
        hex_palette = char_config['palette']

    print(f"\n{'#'*70}")
    print(f"# IDENTITY SHEET: {char_data['name']}")
    print(f"# Model: {MODELS[model_id]['name']}")
    print(f"{'#'*70}")

    prompt = build_identity_sheet_prompt(char_data, style_dna, hex_palette)

    # Get output directory
    exports_path = project_path / config['paths'].get('exports', 'EXPORTS')
    identity_path = exports_path / "identity_sheets"
    identity_path.mkdir(parents=True, exist_ok=True)

    negative_prompt = ", ".join(config.get('negative_prompts', []))
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    settings = {
        "image_size": config['visual']['defaults'].get('identity_sheet_size', {"width": 1536, "height": 1536}),
        "num_inference_steps": 40,
        "guidance_scale": 4.5,
    }

    filename = f"{character_slug}_identity_{model_id}_{timestamp}.png"
    output_path = identity_path / filename

    generate_image(prompt, model_id, settings, output_path, negative_prompt, seed=seed)


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


def run_location_ref(project_path, config, location_slug, model_id=None, seed=None):
    """Generate 2x2 location reference grid"""
    if model_id is None:
        model_id = config['visual'].get('primary_model', 'seedream')

    if location_slug not in LOCATIONS:
        print(f"ERROR: Unknown location '{location_slug}'")
        print(f"Available: {', '.join(LOCATIONS.keys())}")
        return

    loc = LOCATIONS[location_slug]

    # Get style DNA from config
    style_dna = config.get('style_dna', DEFAULT_STYLE_DNA_TEMPLATES['gothic_western'])
    hex_palette = style_dna.get('hex_palette', [])

    print(f"\n{'#'*70}")
    print(f"# LOCATION: {loc['name']}")
    print(f"# Time: {loc['time']}")
    print(f"# Model: {MODELS[model_id]['name']}")
    print(f"{'#'*70}")

    # Build prompt
    components = [
        loc['description'],
        loc['grid'],
        style_dna['medium_era'],
        style_dna['linework_texture'],
        style_dna['lighting_rendering'],
        style_dna['color_palette'],
        "Technical: Thin black dividing lines between panels. Consistent lighting approach across views. Each panel shows different angle/detail of same location.",
    ]

    if hex_palette:
        hex_str = '", "'.join(hex_palette)
        components.append(f'Color grading: ["{hex_str}"]')

    prompt = ". ".join(filter(None, components))

    # Get output directory
    exports_path = project_path / config['paths'].get('exports', 'EXPORTS')
    location_path = exports_path / "location_refs"
    location_path.mkdir(parents=True, exist_ok=True)

    negative_prompt = ", ".join(config.get('negative_prompts', []))
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    settings = {
        "image_size": {"width": 1536, "height": 1536},
        "num_inference_steps": config['visual']['defaults'].get('num_inference_steps', 35),
        "guidance_scale": config['visual']['defaults'].get('guidance_scale', 4.0),
    }

    filename = f"{location_slug}_ref_{model_id}_{timestamp}.png"
    output_path = location_path / filename

    generate_image(prompt, model_id, settings, output_path, negative_prompt, seed=seed)


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
    parser.add_argument("--list-models", action="store_true", help="List available models")

    args = parser.parse_args()

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
        print(f"GENERATING ALL LOCATION REFERENCES")
        print(f"{'='*70}\n")
        for location_slug in LOCATIONS.keys():
            run_location_ref(project_path, config, location_slug, args.model, seed=args.seed)
        print(f"\n{'='*70}")
        print(f"ALL LOCATIONS COMPLETE")
        print(f"{'='*70}")

    elif args.location:
        run_location_ref(project_path, config, args.location, args.model, seed=args.seed)

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


if __name__ == "__main__":
    main()
