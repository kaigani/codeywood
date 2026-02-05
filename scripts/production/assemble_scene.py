#!/usr/bin/env python3
"""
Assemble video clips into a final scene.

Usage:
    python assemble_scene.py --clips path/to/clips.yaml
    python assemble_scene.py --clips-dir path/to/clips --output scene.mp4
    python assemble_scene.py --clips path/to/clips.yaml --alternate

Examples:
    # Assemble SC02 from clip definitions
    python assemble_scene.py --clips clip_definitions/sc02_clips.yaml

    # Assemble from directory (auto-detect clips)
    python assemble_scene.py --clips-dir sc02_outputs/clips --output sc02_complete.mp4
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Optional

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from lib.config import find_project_root
from lib.fal_api import concatenate_clips


def find_clips_in_order(clips_dir: Path, clip_ids: List[int]) -> List[Path]:
    """Find clip files matching the specified IDs in order."""
    found = []

    for clip_id in clip_ids:
        patterns = [
            f"*clip{clip_id:02d}*.mp4",
            f"*clip_{clip_id}*.mp4",
            f"*clip0{clip_id}*.mp4",
        ]

        clip_path = None
        for pattern in patterns:
            matches = list(clips_dir.glob(pattern))
            if matches:
                # Get most recent
                clip_path = sorted(matches, key=lambda p: p.stat().st_mtime)[-1]
                break

        if clip_path:
            found.append(clip_path)
            print(f"  Clip {clip_id}: {clip_path.name}")
        else:
            print(f"  Clip {clip_id}: NOT FOUND")

    return found


def main():
    parser = argparse.ArgumentParser(
        description="Assemble video clips into a final scene",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--clips", "-c",
        help="Path to clip definitions YAML (provides assembly order)",
    )
    parser.add_argument(
        "--clips-dir", "-d",
        help="Directory containing clip files",
    )
    parser.add_argument(
        "--output", "-o",
        help="Output file path",
    )
    parser.add_argument(
        "--alternate",
        action="store_true",
        help="Use alternate assembly order (if defined in YAML)",
    )
    parser.add_argument(
        "--project",
        help="Path to project root (auto-detected if not specified)",
    )
    args = parser.parse_args()

    # Determine project root
    try:
        if args.project:
            project_root = Path(args.project)
        elif args.clips:
            project_root = find_project_root(Path(args.clips).parent)
        elif args.clips_dir:
            project_root = find_project_root(Path(args.clips_dir))
        else:
            project_root = find_project_root()
    except FileNotFoundError:
        project_root = Path.cwd()

    # Load assembly order from YAML or auto-detect
    clip_ids = None
    scene_id = "scene"
    clips_dir = None

    if args.clips:
        import yaml
        clips_path = Path(args.clips)
        if not clips_path.is_absolute():
            alt_path = project_root / "VISUAL_PRODUCTION" / args.clips
            if alt_path.exists():
                clips_path = alt_path

        if not clips_path.exists():
            print(f"Error: Clip definitions not found: {clips_path}")
            sys.exit(1)

        with open(clips_path) as f:
            clip_data = yaml.safe_load(f)

        scene_id = clip_data.get("scene_id", "scene")
        assembly = clip_data.get("assembly", {})

        if args.alternate and "alternate" in assembly:
            clip_ids = assembly["alternate"].get("clips", [])
            output_name = assembly["alternate"].get("output_name", f"{scene_id}_alternate")
            print(f"Using alternate assembly order")
        else:
            clip_ids = assembly.get("clips", [])
            output_name = assembly.get("output_name", f"{scene_id}_complete")

        # Default clips directory
        if not args.clips_dir:
            clips_dir = project_root / "VISUAL_PRODUCTION" / f"{scene_id}_outputs" / "clips"

    if args.clips_dir:
        clips_dir = Path(args.clips_dir)

    if not clips_dir:
        print("Error: Must specify --clips YAML or --clips-dir directory")
        sys.exit(1)

    if not clips_dir.exists():
        print(f"Error: Clips directory not found: {clips_dir}")
        sys.exit(1)

    print(f"Clips directory: {clips_dir}")

    # If no clip IDs specified, auto-detect from directory
    if not clip_ids:
        # Find all clips and sort by number
        all_clips = list(clips_dir.glob("*clip*.mp4"))
        if not all_clips:
            print(f"Error: No clips found in {clips_dir}")
            sys.exit(1)

        # Sort by modification time (or name)
        all_clips = sorted(all_clips, key=lambda p: p.name)
        print(f"Auto-detected {len(all_clips)} clips:")
        for clip in all_clips:
            print(f"  - {clip.name}")

        # Use the sorted clips directly
        clips_to_assemble = all_clips
    else:
        print(f"Assembly order: {clip_ids}")
        clips_to_assemble = find_clips_in_order(clips_dir, clip_ids)

    if not clips_to_assemble:
        print("Error: No clips to assemble")
        sys.exit(1)

    if len(clips_to_assemble) < len(clip_ids or []):
        print(f"Warning: Only {len(clips_to_assemble)} of {len(clip_ids)} clips found")

    # Determine output path
    if args.output:
        output_path = Path(args.output)
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_name = f"{scene_id}_complete" if not clip_ids else output_name
        output_dir = project_root / "VISUAL_PRODUCTION" / f"{scene_id}_outputs" / "assembly"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"{output_name}_{timestamp}.mp4"

    print(f"\nAssembling {len(clips_to_assemble)} clips...")

    # Concatenate
    result = concatenate_clips(clips_to_assemble, output_path)

    if result:
        print(f"\n✓ Assembly complete: {result}")

        # Calculate total duration estimate
        total_clips = len(clips_to_assemble)
        print(f"  Clips: {total_clips}")
    else:
        print("\n✗ Assembly failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
