#!/usr/bin/env python3
"""
FAL.ai Generation Sandbox
Hellmouth Cowboy - Style Exploration & Hero Shots

Usage:
    python generate.py --test style_dna_1 --model seedream
    python generate.py --test all_style --model all
"""

import os
import sys
import json
import argparse
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# FAL.ai client
try:
    import fal_client
except ImportError:
    print("ERROR: fal_client not installed. Run: pip install fal-client")
    sys.exit(1)

# Configuration
FAL_KEY = os.getenv("FAL_KEY")
if not FAL_KEY:
    print("ERROR: FAL_KEY not found in .env file")
    print("Copy .env.example to .env and add your API key")
    sys.exit(1)

os.environ["FAL_KEY"] = FAL_KEY

# Paths
SANDBOX_DIR = Path(__file__).parent
RESULTS_DIR = SANDBOX_DIR / "results"
RESULTS_DIR.mkdir(exist_ok=True)

# Model configurations
MODELS = {
    "seedream": {
        "endpoint": "fal-ai/bytedance/seedream/v4.5/text-to-image",
        "name": "SeeDream v4.5",
        "best_for": "Artistic styles, painterly, stylized",
        "default_size": {"width": 1024, "height": 1024},
    },
    "hunyuan": {
        "endpoint": "fal-ai/hunyuan-image/v3/instruct/text-to-image",
        "name": "Hunyuan Image 3.0",
        "best_for": "Artistic styles, illustration",
        "default_size": {"width": 1024, "height": 1024},
    },
    "grok": {
        "endpoint": "xai/grok-imagine-image",
        "name": "Grok Imagine",
        "best_for": "Artistic exploration, creative styles",
        "default_size": {"width": 1024, "height": 1024},
    },
    "nano_banana": {
        "endpoint": "fal-ai/nano-banana-pro",
        "name": "Nano Banana Pro",
        "best_for": "Precise style refs, prompt handling, technical refs",
        "default_size": {"width": 1536, "height": 1024},
    },
}

# Hellmouth Cowboy Style DNA Templates
STYLE_DNA_TEMPLATES = {
    "base": {
        "medium_era": "1990s dark animated series, hand-drawn cel animation with modern digital compositing",
        "linework_texture": "clean vector lines with varied weight, thicker on silhouette edges, sharp ink outlines",
        "lighting_rendering": "cel-shaded with deep shadows, harsh directional lighting, minimal mid-tones, notan high-contrast principle",
        "color_palette": "limited palette of desaturated earth tones with blood-red accents",
    },
    "gothic_western": {
        "medium_era": "Dark animated style inspired by Castlevania gothic horror meets Sergio Leone spaghetti western cinematography",
        "linework_texture": "Heavy ink outlines with weight variation, crisp silhouettes, slight paper grain texture",
        "lighting_rendering": "Dramatic rim lighting, deep cel-shaded shadows, volumetric dust and atmosphere, high contrast",
        "color_palette": "Desaturated dusty palette with deep blacks and blood-red punctuation",
    },
    "samurai_jack_minimal": {
        "medium_era": "2D animated style, Samurai Jack meets western noir",
        "linework_texture": "Clean vector shapes, thick consistent outlines, flat graphic forms, minimal detail lines",
        "lighting_rendering": "Stark silhouettes, two-tone shading, dramatic negative space, pure blacks",
        "color_palette": "Extremely limited palette, mostly blacks and grays with single accent color",
    },
}

# Test prompts for style exploration
STYLE_TESTS = {
    "style_dna_1": {
        "name": "Gothic Western DNA - Lone Figure",
        "style_dna": "gothic_western",
        "subject": "A lone gunslinger silhouetted against a corrupted crimson sky at dusk, standing at the edge of a dead frontier town",
        "composition": "Wide shot, low angle, figure small but dominating composition through stark silhouette, empty prairie stretching behind",
        "mood": "Ominous arrival, biblical plague energy, the violence to come already written in the air",
        "settings": {
            "image_size": {"width": 1536, "height": 864},
            "num_inference_steps": 35,
            "guidance_scale": 4.0,
        }
    },
    "style_dna_2": {
        "name": "Minimal Noir - Town Aftermath",
        "style_dna": "samurai_jack_minimal",
        "subject": "Abandoned western town at twilight, buildings as pure geometric shapes, something wrong in the shadows between structures",
        "composition": "Extreme wide shot, symmetrical framing, town street receding to vanishing point, massive negative space in sky",
        "mood": "Silent, emptied, violence has already passed through",
        "settings": {
            "image_size": {"width": 1536, "height": 864},
            "num_inference_steps": 35,
            "guidance_scale": 4.0,
        }
    },
    "style_dna_3": {
        "name": "Base DNA - Gunfight Aftermath",
        "style_dna": "base",
        "subject": "Smoking revolvers laying in dust, blood splatter on weathered wood, empty whiskey bottle, aftermath of violence",
        "composition": "Close shot, dutch angle, objects scattered across frame, shallow depth of field with background blur",
        "mood": "Quiet after the storm, the cost visible in small details",
        "settings": {
            "image_size": {"width": 1024, "height": 1024},
            "num_inference_steps": 35,
            "guidance_scale": 4.0,
        }
    },
}

# Hero shot prompts for Nameless
HERO_SHOTS = {
    "hero_nameless_entrance": {
        "name": "Nameless - The Entrance",
        "style_dna": "gothic_western",
        "character": "A cursed gunslinger, appears late 30s but eyes show centuries of death. Tall and gaunt, predator's build. Weathered leather face stretched over sharp bones. Long duster coat nearly black with trail dust, wide-brimmed hat pulled low, twin revolvers on worn gun belt",
        "moment": "He emerges from heat-shimmer on a dead horizon, leading his horse by the reins. Black silhouette becoming visible through dust and light",
        "composition": "Wide shot, low angle, figure small against vast corrupted sky but dominating through sheer presence. Empty frontier behind",
        "mood": "Ominous arrival, walking plague, death on two legs",
        "settings": {
            "image_size": {"width": 1024, "height": 1536},
            "num_inference_steps": 35,
            "guidance_scale": 4.0,
        }
    },
    "hero_nameless_draw": {
        "name": "Nameless - The Signature Action",
        "style_dna": "gothic_western",
        "character": "Cursed gunslinger mid-draw, hands blurred with supernatural speed. Weathered face utterly calm despite violence happening. Twin revolvers clearing leather, muzzle flash beginning",
        "moment": "Dynamic medium shot capturing economy of lethal motion. Background blurred, all focus on the hands and dead eyes above them",
        "composition": "Slightly low angle, dramatic perspective on the draw, motion lines suggesting impossible speed",
        "mood": "Cold efficiency. No anger, no satisfaction. Just work that never ends",
        "settings": {
            "image_size": {"width": 1024, "height": 1536},
            "num_inference_steps": 35,
            "guidance_scale": 4.0,
        }
    },
    "hero_nameless_quiet": {
        "name": "Nameless - The Quiet Moment",
        "style_dna": "gothic_western",
        "character": "Cursed gunslinger sits alone at cold campfire, hat off revealing gray hair longer than expected. Face exposed without shadow of brim - looks older, tired beyond measure",
        "moment": "Staring into dead embers, slumped shoulders carrying century of killing. This is who he is when no one is dying",
        "composition": "Close medium shot, firelight from below casting upward shadows. Space around him empty and isolating",
        "mood": "Weight of immortality crushing. Vulnerability beneath the legend",
        "settings": {
            "image_size": {"width": 1024, "height": 1536},
            "num_inference_steps": 35,
            "guidance_scale": 4.0,
        }
    },
    "hero_minnie_survivor": {
        "name": "Minnie Chance - The Survivor",
        "style_dna": "gothic_western",
        "character": "A Black woman survivor, 31, lean and weathered from frontier hardship. Medium height, dark brown skin, natural hair wrapped back practically. Sharp intelligent dark eyes, strong-featured face. Split riding skirt dusty from travel, leather vest with pockets, simple blouse sleeves rolled up, gun belt worn but ready. Stands amid ruins of destroyed town",
        "moment": "She surveys the devastation with coiled readiness, not panicking. Practical assessment of the situation. One hand rests near her revolver, the other clutches a worn satchel. She's survived worse. She'll survive this",
        "composition": "Medium wide shot, low angle showing her standing against destroyed buildings. Smoke and dust in background, foreground debris. Figure small but resolute",
        "mood": "Unbreakable practicality. Not soft - the frontier has hardened her. Suppressed grief beneath iron determination",
        "settings": {
            "image_size": {"width": 1024, "height": 1536},
            "num_inference_steps": 35,
            "guidance_scale": 4.0,
        }
    },
    "hero_minnie_draw": {
        "name": "Minnie Chance - The Quick Draw",
        "style_dna": "gothic_western",
        "character": "Black frontier woman, early 30s, dark brown skin, natural hair tied back. Sharp intelligent eyes now cold and focused. Leather vest, split riding skirt, gun belt. Weathered capable hands",
        "moment": "Drawing her revolver with learned competence - not a natural gunfighter but trained well. Medium shot capturing the draw. Face utterly calm, teacher managing a crisis. She's been taught by the best",
        "composition": "Medium shot, slightly low angle, focus on hands and determined face. Background slightly blurred, dust particles catching light",
        "mood": "Learned competence, not bravado. Calm under pressure. Teacher turned survivor. She does what she must",
        "settings": {
            "image_size": {"width": 1024, "height": 1536},
            "num_inference_steps": 35,
            "guidance_scale": 4.0,
        }
    },
    "hero_minnie_grief": {
        "name": "Minnie Chance - The Weight",
        "style_dna": "gothic_western",
        "character": "Black woman, 31, dark brown skin, natural hair loose for once. Sharp eyes now distant, haunted. Simple blouse, worn wedding ring visible on her hand. Face showing the grief she usually suppresses",
        "moment": "Alone at dusk, sitting on abandoned porch steps. Staring at something in her hands - small keepsake from her satchel. The practical mask has slipped. This is the tidal wave of grief she keeps dammed up",
        "composition": "Close medium shot, golden hour side lighting. Empty space around her emphasizing isolation. Silhouette partially in shadow",
        "mood": "The dam cracking. Suppressed grief surfacing. Survivor's guilt. The sound of her daughter calling. Weight of what she's lost",
        "settings": {
            "image_size": {"width": 1024, "height": 1536},
            "num_inference_steps": 35,
            "guidance_scale": 4.0,
        }
    },
    "hero_deacon_arrival": {
        "name": "Deacon Hart - The Arrival",
        "style_dna": "gothic_western",
        "character": "Weathered Black man, mid-50s, tall broad-shouldered but lean from the road. Close-cropped gray hair, short gray beard neatly kept. Deep-set eyes with unsettling warmth, dark brown almost black. Face lined with experience. Black broadcloth preacher's coat worn but maintained, white collarless shirt, broad-brimmed black hat. Carries worn Bible. Quiet authority",
        "moment": "He emerges from dust and heat shimmer on the road, Bible in hand. Not threatening, but commanding presence. A man of God walking into darkness. Slight otherworldly quality - too still, something uncanny beneath the humble dignity",
        "composition": "Medium wide shot, low angle, figure silhouetted against corrupted sky. Empty road behind, vast frontier. Small but dominating through spiritual presence",
        "mood": "Unshakeable faith walking into horror. Fire and brimstone preacher. The guide who knows more than he should. Grace offered to the damned",
        "settings": {
            "image_size": {"width": 1024, "height": 1536},
            "num_inference_steps": 35,
            "guidance_scale": 4.0,
        }
    },
    "hero_deacon_sermon": {
        "name": "Deacon Hart - The Word",
        "style_dna": "gothic_western",
        "character": "Black frontier preacher, mid-50s, gray beard, deep-set intense eyes. Black preacher's coat, white shirt. Weathered dignified face showing passion and conviction. Bible open in his hands",
        "moment": "Preaching with fire-and-brimstone intensity. Medium shot capturing the passion of his sermon, Bible held open. Face lit from below as if by campfire. Eyes burning with conviction. This is a man who has seen Hell and still believes in Heaven",
        "composition": "Medium shot, low angle emphasizing authority. Dramatic lighting from below, casting upward shadows. Background dark, focus entirely on his face and the Word",
        "mood": "Fire and brimstone. Spiritual authority. The voice that speaks truth to the damned. Grace and judgment intertwined",
        "settings": {
            "image_size": {"width": 1024, "height": 1536},
            "num_inference_steps": 35,
            "guidance_scale": 4.0,
        }
    },
    "hero_deacon_ghost": {
        "name": "Deacon Hart - The Truth",
        "style_dna": "gothic_western",
        "character": "Black preacher, mid-50s, gray hair and beard. Deep sorrowful eyes showing centuries of patience. Black coat, white shirt. Face showing both forgiveness and profound sadness. Slightly translucent quality, otherworldly",
        "moment": "Standing alone at dusk, looking toward distant horizon where hellmouth waits. Slight translucent quality revealing his ghost nature. One hand rests on Bible, the other open in gesture of offering. The weight of impossible forgiveness visible on his face",
        "composition": "Medium shot, golden hour side lighting making him partially translucent. Silhouette soft-edged unlike living characters. Empty space emphasizing his liminal state between worlds",
        "mood": "The ghost who chose grace. Bound by curse but offering redemption. Profound sadness of the forgiving dead. The guide leading his murderer home",
        "settings": {
            "image_size": {"width": 1024, "height": 1536},
            "num_inference_steps": 35,
            "guidance_scale": 4.0,
        }
    },
}

# Identity Sheet Tests (using Nano Banana Pro with composite layouts)
IDENTITY_SHEETS = {
    "identity_nameless": {
        "name": "Nameless - Identity Sheet",
        "style_dna": "gothic_western",
        "character_details": "Cursed gunslinger who appears late 30s but eyes show centuries of death. Weathered leather face stretched over sharp bones with skeleton visible beneath. Gray hair longer than expected. Twin revolvers on worn gun belt. Long duster coat nearly black with trail dust. Wide-brimmed hat pulled low",
        "layout": """Clean layout with multiple character views on neutral warm beige background (#d4c4b0). Professional character reference sheet format.

TOP ROW (left to right):
- Extreme close-up of dead eyes showing centuries of killing, heavy ink outlines
- Close-up of weathered face profile showing skeleton beneath skin, sharp bones
- Hands holding twin revolvers, worn grips visible, dramatic perspective

MIDDLE SECTION (large):
- Full body front view: Tall gaunt figure, long duster coat, wide-brimmed hat, twin revolvers on gun belt, dramatic pose
- Full body back view: Coat flowing, weathered texture visible, hat brim, holsters

BOTTOM ROW (left to right):
- Hat off revealing gray hair, tired expression, vulnerability showing
- Gun draw action shot, hands blurred with motion, cold efficiency
- Sitting alone profile, slumped shoulders, weight of immortality

Technical: Dark animated style with heavy ink outlines, crisp silhouettes, cel-shaded shadows, high contrast. Thin black dividing lines between panels. Consistent lighting across all views""",
        "hex_palette": ["#0d0d0d", "#1a1a1a", "#2d2d2d", "#8b6f5e", "#6b5a4d", "#e8d4c0", "#8b1a1a", "#a82020", "#c42428", "#4a3d32"],
        "settings": {
            "image_size": {"width": 1536, "height": 1536},
            "num_inference_steps": 40,
            "guidance_scale": 4.5,
        }
    },
    "identity_minnie": {
        "name": "Minnie Chance - Identity Sheet",
        "style_dna": "gothic_western",
        "character_details": "Black frontier woman, 31, dark brown skin, natural hair wrapped back practically. Sharp intelligent eyes, strong-featured face weathered by frontier. Split riding skirt, leather vest with pockets, simple blouse, gun belt with revolver. Practical survivor, former teacher, capable weathered hands. Wedding ring visible",
        "layout": """Clean layout with multiple character views on neutral warm beige background (#d4c4b0). Professional character reference sheet format.

TOP ROW (left to right):
- Extreme close-up of sharp intelligent eyes, teacher's gaze, heavy ink outlines
- Close-up of strong-featured face profile, dark brown skin, natural hair detail visible
- Hands holding revolver with learned competence, wedding ring visible, capable weathered hands

MIDDLE SECTION (large):
- Full body front view: Medium height figure, split riding skirt, leather vest with pockets, blouse sleeves rolled up, gun belt, satchel, coiled readiness
- Full body back view: Hair wrapped back, vest texture, skirt flow, holster placement, practical silhouette

BOTTOM ROW (left to right):
- Hair loose portrait showing vulnerability, tired expression, grief visible
- Gun draw action, calm determined face, learned competence not bravado
- Sitting profile clutching satchel, suppressed grief, survivor's weight

Technical: Dark animated style with heavy ink outlines, crisp silhouettes, cel-shaded shadows, high contrast. Thin black dividing lines between panels. Consistent lighting across all views""",
        "hex_palette": ["#3d2b1f", "#5a4332", "#6b5544", "#d4c8b0", "#b8a890", "#5a3825", "#6b4530", "#7d5236", "#8b1a1a", "#a82020"],
        "settings": {
            "image_size": {"width": 1536, "height": 1536},
            "num_inference_steps": 40,
            "guidance_scale": 4.5,
        }
    },
    "identity_deacon": {
        "name": "Deacon Hart - Identity Sheet",
        "style_dna": "gothic_western",
        "character_details": "Weathered Black man, mid-50s, tall broad-shouldered but lean. Close-cropped gray hair, short gray beard neatly kept. Deep-set eyes with unsettling warmth, dark brown almost black. Face lined with experience. Black broadcloth preacher's coat worn but maintained, white collarless shirt with clerical collar, broad-brimmed black hat. Carries worn Bible. Quiet authority, slight otherworldly quality",
        "layout": """Clean layout with multiple character views on neutral warm beige background (#d4c4b0). Professional character reference sheet format.

TOP ROW (left to right):
- Extreme close-up of deep-set eyes showing unsettling warmth, heavy ink outlines
- Close-up of weathered dignified face profile, gray beard detail, spiritual authority visible
- Hands holding worn Bible with reverence, weathered capable hands, no weapons

MIDDLE SECTION (large):
- Full body front view: Tall broad-shouldered figure, black preacher's coat, white shirt with collar, broad-brimmed hat, Bible in hand, commanding presence
- Full body back view: Coat silhouette, hat brim, no gun belt (conspicuous absence), dignified posture

BOTTOM ROW (left to right):
- Hat off portrait showing gray hair close-cropped, kind but intense expression
- Preaching with passion, Bible open, fire-and-brimstone intensity, eyes burning
- Translucent ghostly quality, sorrowful expression, hand gesture of offering, liminal state

Technical: Dark animated style with heavy ink outlines, crisp silhouettes, cel-shaded shadows, high contrast. Thin black dividing lines between panels. Consistent lighting across all views. Subtle translucent quality in ghost panel""",
        "hex_palette": ["#0d0d0d", "#1a1a1a", "#2d2d2d", "#e8e4dc", "#d4d0c8", "#4a3428", "#5a443a", "#6b5448", "#8a8a8a", "#5a4332"],
        "settings": {
            "image_size": {"width": 1536, "height": 1536},
            "num_inference_steps": 40,
            "guidance_scale": 4.5,
        }
    },
}


def build_prompt(test_config):
    """Build full prompt from test configuration using Style DNA template"""
    # Identity sheet has different structure
    if "layout" in test_config:
        components = []

        # Character details
        if "character_details" in test_config:
            components.append(test_config["character_details"])

        # Layout description
        components.append(test_config["layout"])

        # Hex color grading (Nano Banana Pro specific)
        if "hex_palette" in test_config:
            hex_colors = '", "'.join(test_config["hex_palette"])
            components.append(f'Color grading: ["{hex_colors}"]')

        prompt = ". ".join(components)
        return prompt

    # Standard hero shot / style test structure
    style_dna = STYLE_DNA_TEMPLATES[test_config["style_dna"]]

    # Build prompt components
    components = []

    # Subject/character
    if "character" in test_config:
        components.append(test_config["character"])
    elif "subject" in test_config:
        components.append(test_config["subject"])

    # Moment/action (for hero shots)
    if "moment" in test_config:
        components.append(test_config["moment"])

    # Medium & Era
    components.append(style_dna["medium_era"])

    # Line-work & Texture
    components.append(style_dna["linework_texture"])

    # Lighting & Rendering
    components.append(style_dna["lighting_rendering"])

    # Composition
    if "composition" in test_config:
        components.append(test_config["composition"])

    # Mood
    if "mood" in test_config:
        components.append(test_config["mood"])

    # Color Palette
    components.append(style_dna["color_palette"])

    prompt = ". ".join(components)

    return prompt


def generate_image(test_id, test_config, model_id, seed=None):
    """Generate image using specified FAL.ai model"""
    model = MODELS[model_id]

    print(f"\n{'='*70}")
    print(f"TEST: {test_config['name']}")
    print(f"MODEL: {model['name']} ({model_id})")
    print(f"{'='*70}")

    # Build prompt
    prompt = build_prompt(test_config)
    print(f"\nPROMPT:\n{prompt}\n")

    # Negative prompt
    negative_prompt = "multiple characters, multiple people, crowd, duplicate figures, photography, realistic photo, photorealistic, blurry, low quality, deformed, extra limbs, missing limbs, bad anatomy"

    # Convert image_size dict to standard literal if possible
    if "image_size" in test_config["settings"]:
        image_size = test_config["settings"]["image_size"]
    else:
        image_size = model["default_size"]

    if isinstance(image_size, dict):
        w, h = image_size.get("width", 1024), image_size.get("height", 1024)
        # Map common sizes to fal literals
        size_map = {
            (1024, 1024): "square_hd",
            (1536, 864): "landscape_16_9",
            (864, 1536): "portrait_16_9",
            (1024, 1536): "portrait_4_3",
            (1536, 1024): "landscape_4_3",
            (1536, 1536): "square_hd",  # Large square - use square_hd
        }
        image_size = size_map.get((w, h), image_size)  # Use literal or keep dict

    # Prepare arguments based on model
    arguments = {
        "prompt": prompt,
        "image_size": image_size,
    }

    # Add seed for reproducibility
    if seed is not None:
        arguments["seed"] = seed

    # Add model-specific settings
    if model_id == "nano_banana":
        arguments["negative_prompt"] = negative_prompt
        if "num_inference_steps" in test_config["settings"]:
            arguments["num_inference_steps"] = test_config["settings"]["num_inference_steps"]
        if "guidance_scale" in test_config["settings"]:
            arguments["guidance_scale"] = test_config["settings"]["guidance_scale"]
    elif model_id in ["seedream", "hunyuan", "grok"]:
        # Add parameters that these models support
        if "num_inference_steps" in test_config["settings"]:
            arguments["num_inference_steps"] = test_config["settings"]["num_inference_steps"]
        if "guidance_scale" in test_config["settings"]:
            arguments["guidance_scale"] = test_config["settings"]["guidance_scale"]

    print(f"Settings: {json.dumps(arguments, indent=2)}")
    print("\nGenerating...")

    try:
        # Call FAL.ai API
        def queue_update(update):
            try:
                print(f"  Queue update: {type(update).__name__}")
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
                # Save with timestamp and model
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{test_id}_{model_id}_{timestamp}.png"
                filepath = RESULTS_DIR / filename

                with open(filepath, "wb") as f:
                    f.write(response.content)

                print(f"✓ Saved: {filepath}")

                # Save metadata
                metadata = {
                    "test_id": test_id,
                    "model_id": model_id,
                    "model_name": model["name"],
                    "name": test_config["name"],
                    "timestamp": timestamp,
                    "prompt": prompt,
                    "seed": arguments.get("seed"),
                    "negative_prompt": negative_prompt if model_id == "nano_banana" else "N/A",
                    "settings": arguments,
                    "image_url": image_url,
                    "filepath": str(filepath),
                }

                metadata_file = RESULTS_DIR / f"{test_id}_{model_id}_{timestamp}.json"
                with open(metadata_file, "w") as f:
                    json.dump(metadata, f, indent=2)

                return filepath
            else:
                print(f"✗ Failed to download image: {response.status_code}")
                return None
        else:
            print("✗ No image in result")
            print(json.dumps(result, indent=2))
            return None

    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    parser = argparse.ArgumentParser(description="FAL.ai Generation Sandbox")
    parser.add_argument("--test", help="Test ID to run (or 'all_style', 'all_hero', 'all_identity')")
    parser.add_argument("--model", default="all", help="Model to use: seedream, hunyuan, grok, nano_banana, or 'all'")
    parser.add_argument("--seed", type=int, help="Random seed for reproducibility")
    parser.add_argument("--list", action="store_true", help="List available tests and models")

    args = parser.parse_args()

    if args.list:
        print("\n" + "="*70)
        print("AVAILABLE MODELS")
        print("="*70)
        for model_id, config in MODELS.items():
            print(f"\n{model_id:15s} - {config['name']}")
            print(f"{'':15s}   {config['best_for']}")

        print("\n" + "="*70)
        print("STYLE EXPLORATION TESTS")
        print("="*70)
        for test_id, config in STYLE_TESTS.items():
            print(f"{test_id:30s} - {config['name']}")

        print("\n" + "="*70)
        print("HERO SHOT TESTS")
        print("="*70)
        for test_id, config in HERO_SHOTS.items():
            print(f"{test_id:30s} - {config['name']}")

        print("\n" + "="*70)
        print("IDENTITY SHEET TESTS")
        print("="*70)
        for test_id, config in IDENTITY_SHEETS.items():
            print(f"{test_id:30s} - {config['name']}")

        print("\n" + "="*70)
        print("SPECIAL COMMANDS")
        print("="*70)
        print(f"{'all_style':30s} - Run all style tests")
        print(f"{'all_hero':30s} - Run all hero shot tests")
        print(f"{'all_identity':30s} - Run all identity sheet tests (Nano Banana Pro)")
        print(f"\n{'--model all':30s} - Test across all artistic models")
        return

    if not args.test:
        parser.print_help()
        print("\nUse --list to see available tests")
        return

    # Determine which models to use
    if args.model == "all":
        # For style exploration, use artistic models
        models_to_test = ["seedream", "hunyuan", "grok"]
    else:
        models_to_test = [args.model]

    # Run tests
    if args.test == "all_style":
        for model_id in models_to_test:
            print(f"\n{'#'*70}")
            print(f"# RUNNING ALL STYLE TESTS WITH {MODELS[model_id]['name']}")
            print(f"{'#'*70}")
            for test_id, config in STYLE_TESTS.items():
                generate_image(test_id, config, model_id, seed=args.seed)
    elif args.test == "all_hero":
        for model_id in models_to_test:
            print(f"\n{'#'*70}")
            print(f"# RUNNING ALL HERO TESTS WITH {MODELS[model_id]['name']}")
            print(f"{'#'*70}")
            for test_id, config in HERO_SHOTS.items():
                generate_image(test_id, config, model_id, seed=args.seed)
    elif args.test == "all_identity":
        # Identity sheets always use Nano Banana Pro
        print(f"\n{'#'*70}")
        print(f"# RUNNING ALL IDENTITY SHEET TESTS WITH Nano Banana Pro")
        print(f"{'#'*70}")
        for test_id, config in IDENTITY_SHEETS.items():
            generate_image(test_id, config, "nano_banana", seed=args.seed)
    elif args.test in STYLE_TESTS:
        for model_id in models_to_test:
            generate_image(args.test, STYLE_TESTS[args.test], model_id, seed=args.seed)
    elif args.test in HERO_SHOTS:
        for model_id in models_to_test:
            generate_image(args.test, HERO_SHOTS[args.test], model_id, seed=args.seed)
    elif args.test in IDENTITY_SHEETS:
        # Identity sheets always use Nano Banana Pro
        generate_image(args.test, IDENTITY_SHEETS[args.test], "nano_banana", seed=args.seed)
    else:
        print(f"Unknown test: {args.test}")
        print("Use --list to see available tests")


if __name__ == "__main__":
    main()
