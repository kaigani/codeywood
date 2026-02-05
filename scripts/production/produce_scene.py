#!/usr/bin/env python3
"""
Master production script for a scene.

Runs the full pipeline: validate → frames → clips → assemble

Usage:
    python produce_scene.py sc02 --validate
    python produce_scene.py sc02 --frames
    python produce_scene.py sc02 --clips
    python produce_scene.py sc02 --assemble
    python produce_scene.py sc02 --all

Examples:
    # Full pipeline for SC02
    python produce_scene.py sc02 --all

    # Just generate clips (assumes frames exist)
    python produce_scene.py sc02 --clips

    # Validate first, then run all
    python produce_scene.py sc02 --validate --all
"""

import argparse
import subprocess
import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from lib.config import find_project_root


def run_script(script_name: str, args: list) -> bool:
    """Run a production script and return success status."""
    script_path = Path(__file__).parent / script_name
    cmd = [sys.executable, str(script_path)] + args

    print(f"\n{'='*70}")
    print(f"Running: {script_name}")
    print(f"Args: {' '.join(args)}")
    print(f"{'='*70}\n")

    result = subprocess.run(cmd)
    return result.returncode == 0


def main():
    parser = argparse.ArgumentParser(
        description="Master production script for a scene",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "scene_id",
        help="Scene identifier (e.g., 'sc02', 'sc03')",
    )
    parser.add_argument(
        "--validate", "-v",
        action="store_true",
        help="Validate YAML files",
    )
    parser.add_argument(
        "--frames", "-f",
        action="store_true",
        help="Generate start frames",
    )
    parser.add_argument(
        "--clips", "-c",
        action="store_true",
        help="Generate video clips",
    )
    parser.add_argument(
        "--assemble", "-a",
        action="store_true",
        help="Assemble final scene",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Run full pipeline (frames → clips → assemble)",
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
        else:
            project_root = find_project_root()
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)

    scene_id = args.scene_id
    visual_prod = project_root / "VISUAL_PRODUCTION"

    # Determine file paths
    shot_list = visual_prod / "shot_lists" / f"{scene_id}_shots.yaml"
    clip_defs = visual_prod / "clip_definitions" / f"{scene_id}_clips.yaml"

    # Check files exist
    if not shot_list.exists():
        print(f"Error: Shot list not found: {shot_list}")
        sys.exit(1)

    if not clip_defs.exists():
        print(f"Error: Clip definitions not found: {clip_defs}")
        sys.exit(1)

    print(f"Scene: {scene_id}")
    print(f"Project: {project_root}")
    print(f"Shot list: {shot_list}")
    print(f"Clip definitions: {clip_defs}")

    # Determine what to run
    run_validate = args.validate
    run_frames = args.frames or args.all
    run_clips = args.clips or args.all
    run_assemble = args.assemble or args.all

    if not any([run_validate, run_frames, run_clips, run_assemble]):
        parser.print_help()
        print("\nSpecify --validate, --frames, --clips, --assemble, or --all")
        sys.exit(1)

    success = True

    # Step 1: Validate
    if run_validate:
        ok = run_script("validate.py", [
            "--shot-list", str(shot_list),
            "--clips", str(clip_defs),
        ])
        if not ok:
            print("\n✗ Validation failed. Fix errors before proceeding.")
            sys.exit(1)

    # Step 2: Generate frames
    if run_frames:
        ok = run_script("generate_frames.py", [
            "--shot-list", str(shot_list),
            "--all",
        ])
        if not ok:
            print("\n✗ Frame generation failed.")
            success = False
            if args.all:
                print("Stopping pipeline.")
                sys.exit(1)

    # Step 3: Generate clips
    if run_clips:
        ok = run_script("generate_clips.py", [
            "--clips", str(clip_defs),
            "--all",
        ])
        if not ok:
            print("\n✗ Clip generation failed.")
            success = False
            if args.all:
                print("Stopping pipeline.")
                sys.exit(1)

    # Step 4: Assemble
    if run_assemble:
        ok = run_script("assemble_scene.py", [
            "--clips", str(clip_defs),
        ])
        if not ok:
            print("\n✗ Assembly failed.")
            success = False

    # Final summary
    print("\n" + "#"*70)
    print("# PRODUCTION COMPLETE" if success else "# PRODUCTION FAILED")
    print("#"*70)

    if success:
        output_dir = visual_prod / f"{scene_id}_outputs"
        print(f"\nOutputs in: {output_dir}")
        print("  /frames    - Start frame images")
        print("  /clips     - Video clips")
        print("  /assembly  - Final assembled scene")

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
