#!/usr/bin/env python3
"""
Generate a single video clip via FAL API.

This script is an API abstraction layer - it accepts explicit parameters
and executes the API call. All logic for determining WHICH files to use
belongs in the orchestrating agent (Claude), not in this script.

Usage:
    # Simple single-prompt clip
    python generate_clip.py \
        --start-frame /path/to/frame.png \
        --prompt "Character walks through doorway" \
        --duration 5 \
        --character mars=/path/to/mars_identity.png \
        --output-dir /path/to/output \
        --output-name "sc02_clip01"

    # Multi-prompt clip with JSON config
    python generate_clip.py --config /path/to/clip_config.json

    # Dry run to preview API call
    python generate_clip.py --config clip.json --dry-run

JSON Config Format:
    {
        "start_frame": "/absolute/path/to/frame.png",
        "prompts": [
            {"prompt": "First action", "duration": 3},
            {"prompt": "Second action", "duration": 5}
        ],
        "characters": [
            {
                "id": "mars", "element": "@Element1",
                "ref": "/path/to/identity.png",
                "reference_images": ["/path/to/pose1.png", "/path/to/pose2.png"]
            }
        ],
        "location_element": {
            "frontal": "/path/to/establishing_shot.png",
            "reference_image_paths": ["/path/to/detail1.png"],
            "element_tag": "@Element3"
        },
        "scene_refs": ["/path/to/ref1.png", "/path/to/ref2.png"],
        "output_dir": "/path/to/output",
        "output_name": "sc02_clip01_exterior"
    }
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any

# Add scripts/ to path for shared lib imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.fal_api import FalGenerator


def validate_config(config: Dict[str, Any]) -> List[str]:
    """Validate configuration and return list of errors."""
    errors = []

    # Required fields
    if not config.get("start_frame"):
        errors.append("start_frame is required")
    elif not Path(config["start_frame"]).exists():
        errors.append(f"start_frame not found: {config['start_frame']}")

    if not config.get("prompts"):
        errors.append("At least one prompt is required")
    else:
        for i, p in enumerate(config["prompts"]):
            if not p.get("prompt"):
                errors.append(f"prompts[{i}].prompt is required")
            if not p.get("duration"):
                errors.append(f"prompts[{i}].duration is required")

    if not config.get("output_dir"):
        errors.append("output_dir is required")

    if not config.get("output_name"):
        errors.append("output_name is required")

    # Validate character refs exist
    for char in config.get("characters", []):
        ref_path = char.get("ref")
        if ref_path and not Path(ref_path).exists():
            errors.append(f"Character ref not found: {ref_path}")
        for ri in char.get("reference_images", []):
            if not Path(ri).exists():
                errors.append(f"Character reference_image not found: {ri}")

    # Validate location element refs exist
    loc = config.get("location_element")
    if loc:
        if loc.get("frontal") and not Path(loc["frontal"]).exists():
            errors.append(f"Location frontal not found: {loc['frontal']}")
        for ri in loc.get("reference_image_paths", []):
            if not Path(ri).exists():
                errors.append(f"Location reference not found: {ri}")

    # Validate scene refs exist
    for ref in config.get("scene_refs", []):
        if not Path(ref).exists():
            errors.append(f"Scene ref not found: {ref}")

    return errors


def build_config_from_args(args) -> Dict[str, Any]:
    """Build config dict from command line arguments."""
    config = {
        "start_frame": args.start_frame,
        "output_dir": args.output_dir,
        "output_name": args.output_name,
        "prompts": [],
        "characters": [],
        "scene_refs": args.scene_ref or [],
    }

    # Parse prompts (can be specified multiple times)
    if args.prompt and args.duration:
        # Pair up prompts and durations
        for i, prompt in enumerate(args.prompt):
            duration = args.duration[i] if i < len(args.duration) else args.duration[-1]
            config["prompts"].append({
                "prompt": prompt,
                "duration": duration,
                "cut_prefix": True,  # Default to true for multi-prompt
            })

    # Parse characters (format: id=/path/to/ref.png or id=@Element1=/path/to/ref.png)
    if args.character:
        for i, char_spec in enumerate(args.character):
            if "=" in char_spec:
                parts = char_spec.split("=", 2)
                if len(parts) == 2:
                    char_id, ref_path = parts
                    element = f"@Element{i+1}"
                else:
                    char_id, element, ref_path = parts
                config["characters"].append({
                    "id": char_id,
                    "element": element,
                    "ref": ref_path,
                })

    return config


def generate_clip(config: Dict[str, Any], dry_run: bool = False) -> Optional[Dict[str, Any]]:
    """Generate a video clip from configuration."""

    start_frame = Path(config["start_frame"])
    output_dir = Path(config["output_dir"])
    output_name = config["output_name"]
    prompts = config["prompts"]
    characters = config.get("characters", [])
    scene_refs = [Path(p) for p in config.get("scene_refs", [])]
    location_element = config.get("location_element")

    # Map reference_images -> reference_image_paths for FalGenerator
    for char in characters:
        if "reference_images" in char:
            char["reference_image_paths"] = char.pop("reference_images")

    # Calculate total duration and cost estimate
    total_duration = sum(p.get("duration", 5) for p in prompts)
    # Kling v3 Pro pricing: ~$0.336 per second
    estimated_cost = total_duration * 0.336

    print(f"\n{'='*70}")
    print("CLIP GENERATION")
    print(f"{'='*70}")
    print(f"Start frame: {start_frame}")
    print(f"Output: {output_dir / output_name}")
    print(f"Duration: {total_duration}s")
    print(f"Prompts: {len(prompts)} cuts")
    for i, p in enumerate(prompts):
        print(f"  Cut {i+1} ({p.get('duration')}s): {p.get('prompt')[:60]}...")
    print(f"Characters: {[c.get('id') for c in characters]}")
    print(f"Scene refs: {len(scene_refs)}")
    print(f"Estimated cost: ${estimated_cost:.2f}")
    print(f"{'='*70}")

    if dry_run:
        print("\n[DRY RUN] Would generate clip with above parameters")
        return {
            "status": "dry_run",
            "config": config,
            "estimated_cost": estimated_cost,
        }

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    # Initialize generator (minimal config - just needs output dir)
    minimal_config = {
        "project": {"slug": "clip"},
        "paths": {},
        "assets": {},
    }
    generator = FalGenerator(minimal_config, output_dir)

    # Generate the clip
    kwargs = {}
    if location_element:
        kwargs["location_element"] = location_element

    result_path = generator.generate_video_clip(
        start_frame=start_frame,
        prompts=prompts,
        characters=characters,
        scene_refs=scene_refs,
        output_name=output_name,
        **kwargs,
    )

    if result_path:
        # Build result metadata
        timestamp = datetime.now().isoformat()
        result = {
            "status": "success",
            "output_path": str(result_path),
            "start_frame": str(start_frame),
            "prompts": prompts,
            "characters": [{"id": c.get("id"), "element": c.get("element")} for c in characters],
            "duration": total_duration,
            "timestamp": timestamp,
        }

        # Write metadata JSON alongside video
        meta_path = result_path.with_suffix(".json")
        with open(meta_path, "w") as f:
            json.dump(result, f, indent=2)

        print(f"\n{'='*70}")
        print(f"SUCCESS: {result_path}")
        print(f"Metadata: {meta_path}")
        print(f"{'='*70}")

        return result
    else:
        return {
            "status": "error",
            "message": "Generation failed",
        }


def main():
    parser = argparse.ArgumentParser(
        description="Generate a single video clip via FAL API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    # Config file (alternative to inline args)
    parser.add_argument(
        "--config", "-c",
        help="Path to JSON config file (alternative to inline args)",
    )

    # Inline arguments
    parser.add_argument(
        "--start-frame",
        help="Path to start frame image",
    )
    parser.add_argument(
        "--prompt", "-p",
        action="append",
        help="Prompt text (can specify multiple for multi-prompt clips)",
    )
    parser.add_argument(
        "--duration", "-d",
        type=int,
        action="append",
        help="Duration in seconds (pairs with --prompt)",
    )
    parser.add_argument(
        "--character",
        action="append",
        help="Character spec: id=/path/to/ref.png or id=@Element1=/path/to/ref.png",
    )
    parser.add_argument(
        "--scene-ref",
        action="append",
        help="Scene reference image path (can specify multiple)",
    )
    parser.add_argument(
        "--output-dir", "-o",
        help="Output directory for generated clip",
    )
    parser.add_argument(
        "--output-name",
        help="Output filename (without extension)",
    )

    # Control flags
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview what would be generated without executing",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON",
    )

    args = parser.parse_args()

    # Build config from file or args
    if args.config:
        config_path = Path(args.config)
        if not config_path.exists():
            print(f"Error: Config file not found: {config_path}")
            sys.exit(1)
        with open(config_path) as f:
            config = json.load(f)
    elif args.start_frame:
        config = build_config_from_args(args)
    else:
        parser.print_help()
        print("\nProvide either --config or inline arguments (--start-frame, --prompt, etc.)")
        sys.exit(1)

    # Validate
    errors = validate_config(config)
    if errors:
        print("Configuration errors:")
        for err in errors:
            print(f"  - {err}")
        sys.exit(1)

    # Generate
    result = generate_clip(config, dry_run=args.dry_run)

    # Output
    if args.json:
        print(json.dumps(result, indent=2))

    # Exit code
    if result.get("status") == "error":
        sys.exit(1)


if __name__ == "__main__":
    main()
