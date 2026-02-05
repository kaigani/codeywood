#!/usr/bin/env python3
"""
Generate production frames from a shot list YAML.

Usage:
    python generate_frames.py --shot-list path/to/shots.yaml [--output-dir path/to/output]
    python generate_frames.py --shot-list path/to/shots.yaml --shot 1
    python generate_frames.py --shot-list path/to/shots.yaml --all

Examples:
    # Generate all required frames for SC02
    python generate_frames.py --shot-list shot_lists/sc02_shots.yaml --all

    # Generate specific shot
    python generate_frames.py --shot-list shot_lists/sc02_shots.yaml --shot 3
"""

import argparse
import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from lib.config import load_config, find_project_root
from lib.shot_list import load_shot_list
from lib.fal_api import FalGenerator


def generate_shot_frame(
    generator: FalGenerator,
    shot_list,
    shot: dict,
) -> Path:
    """Generate a single frame for a shot."""
    shot_id = shot.get("id")
    shot_name = shot.get("name", f"shot_{shot_id}")
    output_name = shot.get("output_name", f"shot{shot_id:02d}")

    print(f"\n{'#'*70}")
    print(f"# SHOT {shot_id}: {shot_name}")
    print(f"{'#'*70}")

    # Resolve references
    refs = shot_list.resolve_shot_refs(shot)
    print(f"References: {len(refs)}")
    for ref in refs:
        print(f"  - {ref.name}")

    # Build prompt
    prompt = shot_list.build_shot_prompt(shot)

    # Determine lighting mode from shot or scene
    lighting = shot.get("lighting", shot_list.get_lighting_mode())

    # Generate frame
    return generator.generate_frame(
        prompt=prompt,
        refs=refs,
        output_name=output_name,
        lighting_mode=lighting,
    )


def main():
    parser = argparse.ArgumentParser(
        description="Generate production frames from shot list YAML",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--shot-list", "-s",
        required=True,
        help="Path to shot list YAML file",
    )
    parser.add_argument(
        "--output-dir", "-o",
        help="Output directory (defaults to {scene_id}_outputs/frames)",
    )
    parser.add_argument(
        "--shot",
        type=int,
        help="Generate a specific shot by ID",
    )
    parser.add_argument(
        "--all", "-a",
        action="store_true",
        help="Generate all required shots",
    )
    parser.add_argument(
        "--project",
        help="Path to project root (auto-detected if not specified)",
    )
    args = parser.parse_args()

    # Load configuration
    try:
        if args.project:
            project_root = Path(args.project)
        else:
            project_root = find_project_root(Path(args.shot_list).parent)
        config = load_config(project_root)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)

    # Load shot list
    shot_list_path = Path(args.shot_list)
    if not shot_list_path.is_absolute():
        # Try relative to project VISUAL_PRODUCTION
        alt_path = project_root / "VISUAL_PRODUCTION" / args.shot_list
        if alt_path.exists():
            shot_list_path = alt_path

    try:
        shot_list = load_shot_list(shot_list_path, config)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)

    # Determine output directory
    if args.output_dir:
        output_dir = Path(args.output_dir)
    else:
        output_dir = project_root / "VISUAL_PRODUCTION" / f"{shot_list.scene_id}_outputs" / "frames"

    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"Output directory: {output_dir}")

    # Initialize generator
    try:
        generator = FalGenerator(config, output_dir)
    except (ImportError, EnvironmentError) as e:
        print(f"Error: {e}")
        sys.exit(1)

    # Determine which shots to generate
    if args.shot:
        shots_to_generate = [shot_list.get_shot(args.shot)]
        if shots_to_generate[0] is None:
            print(f"Error: Shot {args.shot} not found in shot list")
            available = [s.get("id") for s in shot_list.shots]
            print(f"Available shots: {available}")
            sys.exit(1)
    elif args.all:
        shots_to_generate = shot_list.get_required_frames()
    else:
        parser.print_help()
        print("\nSpecify --shot N or --all to generate frames")
        sys.exit(1)

    # Generate frames
    results = {}
    for shot in shots_to_generate:
        shot_id = shot.get("id")
        result = generate_shot_frame(generator, shot_list, shot)
        results[f"shot_{shot_id}"] = result

    # Summary
    print("\n" + "="*70)
    print("GENERATION COMPLETE")
    print("="*70)
    for name, path in results.items():
        status = "✓" if path else "✗"
        print(f"  {status} {name}: {path}")

    # Return non-zero if any failed
    if None in results.values():
        sys.exit(1)


if __name__ == "__main__":
    main()
