#!/usr/bin/env python3
"""
Generate Final Animation Frame with Image References

Uses CORRECT Nano Banana Pro parameters with actual image reference inputs.

Usage:
    python generate_final_frame.py \
        --scene SC10 \
        --shot 6 \
        --characters nameless minnie \
        --location open-road \
        --prompt "Two figures walking away toward horizon..."

Requirements:
    pip install fal-client pyyaml python-dotenv requests
"""

import os
import sys
import json
import argparse
import requests
from datetime import datetime
from pathlib import Path

try:
    import fal_client
except ImportError:
    print("ERROR: fal-client required. Install with: pip install fal-client")
    sys.exit(1)

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML required. Install with: pip install pyyaml")
    sys.exit(1)

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


def find_latest_file(directory, pattern):
    """Find most recent file matching pattern"""
    files = list(Path(directory).glob(pattern))
    if not files:
        return None
    return sorted(files, key=lambda p: p.stat().st_mtime, reverse=True)[0]


def load_project_config(project_path):
    """Load PROJECT_CONFIG.yaml"""
    config_path = Path(project_path) / "PROJECT_CONFIG.yaml"
    if not config_path.exists():
        print(f"ERROR: PROJECT_CONFIG.yaml not found at {project_path}")
        sys.exit(1)

    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def main():
    parser = argparse.ArgumentParser(
        description="Generate final animation frame with image references",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument("--project", default=".", help="Project directory")
    parser.add_argument("--scene", required=True, help="Scene ID (e.g., SC10)")
    parser.add_argument("--shot", required=True, help="Shot number (e.g., 6)")
    parser.add_argument("--characters", nargs="+", help="Character slugs (e.g., nameless minnie)")
    parser.add_argument("--location", help="Location slug (e.g., open-road)")
    parser.add_argument("--prompt", help="Shot description prompt (or use --prompt-file)")
    parser.add_argument("--prompt-file", help="File containing prompt text")
    parser.add_argument("--aspect-ratio", default="16:9", help="Aspect ratio (default: 16:9)")
    parser.add_argument("--resolution", default="2K", help="Resolution: 2K, HD, SD (default: 2K)")
    parser.add_argument("--seed", type=int, help="Random seed for reproducibility")

    args = parser.parse_args()

    # Load project config
    project_path = Path(args.project).absolute()
    config = load_project_config(project_path)
    exports_path = project_path / config['paths'].get('exports', 'EXPORTS')

    print("\n" + "="*70)
    print("FINAL FRAME GENERATION - Nano Banana Pro with Image References")
    print("="*70)
    print(f"\nProject: {project_path}")
    print(f"Scene: {args.scene}")
    print(f"Shot: {args.shot}")
    print(f"Aspect Ratio: {args.aspect_ratio}")
    print(f"Resolution: {args.resolution}")

    # Upload character identity sheets
    image_urls = []

    if args.characters:
        print(f"\nUploading character references...")
        identity_path = exports_path / "identity_sheets"

        for char_slug in args.characters:
            identity_file = find_latest_file(identity_path, f"identity_{char_slug}_*.png")
            if identity_file:
                print(f"  {char_slug}: {identity_file.name}")
                url = fal_client.upload_file(str(identity_file))
                image_urls.append(url)
                print(f"    ✓ Uploaded: {url}")
            else:
                print(f"  WARNING: No identity sheet found for {char_slug}")

    # Upload location reference
    if args.location:
        print(f"\nUploading location reference...")
        location_path = exports_path / "location_refs"

        location_file = find_latest_file(location_path, f"{args.location}_ref_*.png")
        if location_file:
            print(f"  {args.location}: {location_file.name}")
            url = fal_client.upload_file(str(location_file))
            image_urls.append(url)
            print(f"    ✓ Uploaded: {url}")
        else:
            print(f"  WARNING: No location reference found for {args.location}")

    if not image_urls:
        print("\nERROR: No references uploaded. Specify --characters and/or --location")
        sys.exit(1)

    # Get prompt
    if args.prompt_file:
        with open(args.prompt_file, 'r') as f:
            prompt = f.read().strip()
    elif args.prompt:
        prompt = args.prompt
    else:
        print("\nERROR: Provide --prompt or --prompt-file")
        sys.exit(1)

    # Add style DNA to prompt
    style_dna = config.get('style_dna', {})
    full_prompt = f"""{prompt}

Use character and location designs from reference images.

{style_dna.get('medium_era', '')}
{style_dna.get('linework_texture', '')}
{style_dna.get('lighting_rendering', '')}
{style_dna.get('color_palette', '')}"""

    print("\n" + "="*70)
    print("GENERATING WITH NANO BANANA PRO")
    print("="*70)
    print(f"\nReferences: {len(image_urls)} images uploaded")
    print(f"Aspect Ratio: {args.aspect_ratio}")
    print(f"Resolution: {args.resolution}")
    print("\nPrompt preview (first 200 chars):")
    print(full_prompt[:200] + "...")
    print("\nGenerating...")

    # Build arguments for Nano Banana Pro with image references
    api_arguments = {
        "prompt": full_prompt,
        "image_urls": image_urls,
        "aspect_ratio": args.aspect_ratio,
        "resolution": args.resolution,
        "num_images": 1,
        "output_format": "png"
    }

    # Add seed for reproducibility if provided
    if args.seed is not None:
        api_arguments["seed"] = args.seed

    # Generate with CORRECT parameters - use /edit endpoint for image references
    result = fal_client.subscribe(
        "fal-ai/nano-banana-pro/edit",
        arguments=api_arguments,
        with_logs=True,
        on_queue_update=lambda u: print(f"  Queue: {type(u).__name__}")
    )

    # Get image URL
    image_url = result["images"][0]["url"]
    print(f"\n✓ Generated: {image_url}")

    # Download and save
    response = requests.get(image_url)
    if response.status_code == 200:
        # Create output directory
        output_dir = exports_path / "final_frames" / "EP01" / args.scene
        output_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"shot_{args.shot}_{timestamp}.png"
        output_path = output_dir / filename

        with open(output_path, "wb") as f:
            f.write(response.content)

        print(f"✓ Saved: {output_path}")

        # Save metadata
        metadata = {
            "scene": args.scene,
            "shot": args.shot,
            "characters": args.characters,
            "location": args.location,
            "aspect_ratio": args.aspect_ratio,
            "resolution": args.resolution,
            "seed": args.seed,
            "image_references": image_urls,
            "prompt": full_prompt,
            "timestamp": datetime.now().isoformat(),
            "image_url": image_url,
            "model": "fal-ai/nano-banana-pro/edit",
            "method": "CORRECT (with image_urls via /edit endpoint)"
        }

        metadata_path = output_path.with_suffix('.json')
        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=2)

        print(f"✓ Metadata: {metadata_path}")
        print("\n" + "="*70)
        print("GENERATION COMPLETE")
        print("="*70)
    else:
        print(f"\n✗ Download failed: {response.status_code}")
        sys.exit(1)


if __name__ == "__main__":
    main()
