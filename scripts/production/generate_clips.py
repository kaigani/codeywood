#!/usr/bin/env python3
"""
Generate video clips from clip definition YAML.

Usage:
    python generate_clips.py --clips path/to/clips.yaml [--frames-dir path/to/frames]
    python generate_clips.py --clips path/to/clips.yaml --clip 1
    python generate_clips.py --clips path/to/clips.yaml --all

Examples:
    # Generate all clips for SC02
    python generate_clips.py --clips clip_definitions/sc02_clips.yaml --all

    # Generate specific clip
    python generate_clips.py --clips clip_definitions/sc02_clips.yaml --clip 2
"""

import argparse
import sys
from pathlib import Path
from typing import Optional

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from lib.config import load_config, find_project_root
from lib.shot_list import load_shot_list, load_clip_definitions
from lib.fal_api import FalGenerator, extract_last_frame


def find_frame_for_shot(frames_dir: Path, shot_id: int) -> Optional[Path]:
    """Find the most recent frame file for a shot."""
    patterns = [
        f"*shot{shot_id:02d}*.png",
        f"*shot_{shot_id}*.png",
        f"*shot{shot_id}*.png",
    ]

    for pattern in patterns:
        matches = list(frames_dir.glob(pattern))
        if matches:
            # Return most recent
            return sorted(matches, key=lambda p: p.stat().st_mtime)[-1]

    return None


def find_clip_output(clips_dir: Path, clip_id: int) -> Optional[Path]:
    """Find the most recent clip output."""
    patterns = [
        f"*clip{clip_id:02d}*.mp4",
        f"*clip_{clip_id}*.mp4",
        f"*clip{clip_id}*.mp4",
    ]

    for pattern in patterns:
        matches = list(clips_dir.glob(pattern))
        if matches:
            return sorted(matches, key=lambda p: p.stat().st_mtime)[-1]

    return None


def generate_clip(
    generator: FalGenerator,
    clip_defs,
    clip: dict,
    frames_dir: Path,
    clips_dir: Path,
) -> Optional[Path]:
    """Generate a single video clip."""
    clip_id = clip.get("id")
    clip_name = clip.get("name", f"clip_{clip_id}")
    output_name = clip.get("output_name", f"clip{clip_id:02d}")

    print(f"\n{'#'*70}")
    print(f"# CLIP {clip_id}: {clip_name}")
    print(f"{'#'*70}")

    # Resolve start frame
    start_config = clip_defs.get_start_frame_strategy(clip)
    strategy = start_config.get("strategy", "shot")

    start_frame = None

    if strategy == "shot":
        shot_id = start_config.get("shot_id")
        start_frame = find_frame_for_shot(frames_dir, shot_id)
        if not start_frame:
            print(f"✗ Error: Frame for shot {shot_id} not found in {frames_dir}")
            print("  Run generate_frames.py first")
            return None
        print(f"Start frame: Shot {shot_id} -> {start_frame.name}")

    elif strategy == "last_frame":
        prev_clip_id = start_config.get("clip_id")
        prev_clip = find_clip_output(clips_dir, prev_clip_id)
        if not prev_clip:
            print(f"✗ Error: Clip {prev_clip_id} not found for last_frame extraction")
            return None

        # Extract last frame
        extracted_path = clips_dir / f"clip{clip_id:02d}_start_frame.png"
        start_frame = extract_last_frame(prev_clip, extracted_path)
        if not start_frame:
            print(f"✗ Error: Failed to extract last frame from clip {prev_clip_id}")
            return None
        print(f"Start frame: Last frame of clip {prev_clip_id}")

    elif strategy == "custom":
        custom_path = start_config.get("custom_path")
        start_frame = Path(custom_path)
        if not start_frame.exists():
            print(f"✗ Error: Custom start frame not found: {custom_path}")
            return None
        print(f"Start frame: Custom -> {start_frame}")

    else:
        print(f"✗ Error: Unknown start frame strategy: {strategy}")
        return None

    # Collect scene reference frames from shots referenced in this clip
    scene_refs = []
    for prompt_def in clip.get("prompts", []):
        shot_ref = prompt_def.get("shot_ref")
        if shot_ref:
            frame = find_frame_for_shot(frames_dir, shot_ref)
            if frame and frame not in scene_refs:
                scene_refs.append(frame)
    print(f"Scene refs: {len(scene_refs)} frames")

    # Get characters
    characters = clip_defs.get_clip_characters(clip)
    print(f"Characters: {[c['id'] for c in characters]}")

    # Build prompts
    prompts = clip_defs.build_clip_prompts(clip)
    if not prompts:
        print("✗ Error: No prompts defined for clip")
        return None

    print(f"Prompts: {len(prompts)} cuts")

    # Generate clip
    return generator.generate_video_clip(
        start_frame=start_frame,
        prompts=prompts,
        characters=characters,
        scene_refs=scene_refs,
        output_name=output_name,
    )


def main():
    parser = argparse.ArgumentParser(
        description="Generate video clips from clip definition YAML",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--clips", "-c",
        required=True,
        help="Path to clip definitions YAML file",
    )
    parser.add_argument(
        "--frames-dir", "-f",
        help="Directory containing generated frames (auto-detected if not specified)",
    )
    parser.add_argument(
        "--output-dir", "-o",
        help="Output directory for clips (defaults to {scene_id}_outputs/clips)",
    )
    parser.add_argument(
        "--clip",
        type=int,
        help="Generate a specific clip by ID",
    )
    parser.add_argument(
        "--all", "-a",
        action="store_true",
        help="Generate all clips",
    )
    parser.add_argument(
        "--project",
        help="Path to project root (auto-detected if not specified)",
    )

    # Agentic primitives flags
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview what would be generated without executing",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing clips (default: skip if exists)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON for structured parsing",
    )

    args = parser.parse_args()

    # Load configuration
    try:
        if args.project:
            project_root = Path(args.project)
        else:
            project_root = find_project_root(Path(args.clips).parent)
        config = load_config(project_root)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)

    # Load clip definitions
    clips_path = Path(args.clips)
    if not clips_path.is_absolute():
        alt_path = project_root / "VISUAL_PRODUCTION" / args.clips
        if alt_path.exists():
            clips_path = alt_path

    if not clips_path.exists():
        print(f"Error: Clip definitions not found: {clips_path}")
        sys.exit(1)

    # Load shot list (referenced from clip definitions)
    import yaml
    with open(clips_path) as f:
        clip_data = yaml.safe_load(f)

    shot_list_ref = clip_data.get("shot_list", "")
    shot_list_path = (clips_path.parent / shot_list_ref).resolve()
    if not shot_list_path.exists():
        # Try VISUAL_PRODUCTION relative path
        shot_list_path = project_root / "VISUAL_PRODUCTION" / "shot_lists" / f"{clip_data.get('scene_id')}_shots.yaml"

    if not shot_list_path.exists():
        print(f"Error: Shot list not found: {shot_list_path}")
        sys.exit(1)

    shot_list = load_shot_list(shot_list_path, config)
    clip_defs = load_clip_definitions(clips_path, shot_list)

    scene_id = clip_defs.scene_id

    # Determine directories
    if args.frames_dir:
        frames_dir = Path(args.frames_dir)
    else:
        frames_dir = project_root / "VISUAL_PRODUCTION" / f"{scene_id}_outputs" / "frames"

    if args.output_dir:
        output_dir = Path(args.output_dir)
    else:
        output_dir = project_root / "VISUAL_PRODUCTION" / f"{scene_id}_outputs" / "clips"

    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"Frames directory: {frames_dir}")
    print(f"Output directory: {output_dir}")

    # Initialize generator
    try:
        generator = FalGenerator(config, output_dir)
    except (ImportError, EnvironmentError) as e:
        print(f"Error: {e}")
        sys.exit(1)

    # Determine which clips to generate
    if args.clip:
        clips_to_generate = [clip_defs.get_clip(args.clip)]
        if clips_to_generate[0] is None:
            print(f"Error: Clip {args.clip} not found in definitions")
            available = [c.get("id") for c in clip_defs.clips]
            print(f"Available clips: {available}")
            sys.exit(1)
    elif args.all:
        clips_to_generate = clip_defs.clips
    else:
        parser.print_help()
        print("\nSpecify --clip N or --all to generate clips")
        sys.exit(1)

    # Generate clips
    results = {}
    for clip in clips_to_generate:
        clip_id = clip.get("id")
        result = generate_clip(
            generator=generator,
            clip_defs=clip_defs,
            clip=clip,
            frames_dir=frames_dir,
            clips_dir=output_dir,
        )
        results[f"clip_{clip_id}"] = result

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
