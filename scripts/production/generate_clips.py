#!/usr/bin/env python3
"""
Generate video clips from clip definition YAML.

Usage:
    python generate_clips.py --scene PRODUCTION/EP01/sc03 --clip 1
    python generate_clips.py --scene PRODUCTION/EP01/sc03 --all
    python generate_clips.py --clips path/to/clips.yaml --clip 1  # legacy

Examples:
    # Generate specific clip (new layout)
    python generate_clips.py --scene PRODUCTION/EP01/sc03 --clip 2

    # Generate all clips (legacy layout)
    python generate_clips.py --clips clip_definitions/sc02_clips.yaml --all
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Optional

# Add scripts/ to path for shared lib imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.config import load_config, find_project_root
from lib.shot_list import load_shot_list, load_clip_definitions
from lib.generator import Generator
from lib.ffmpeg import extract_last_frame


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


def find_clip_output(clips_dir: Path, clip_id: int, output_name: Optional[str] = None) -> Optional[Path]:
    """Find the most recent clip output.

    Args:
        clips_dir: Directory containing clip outputs
        clip_id: The clip ID to search for
        output_name: Optional output_name from clip definition (preferred search method)
    """
    patterns = []

    # Prefer output_name if provided (most reliable)
    if output_name:
        patterns.append(f"*{output_name}*.mp4")

    # Fallback to ID-based patterns
    patterns.extend([
        f"*clip{clip_id:02d}*.mp4",
        f"*clip_{clip_id}*.mp4",
        f"*clip{clip_id}*.mp4",
    ])

    for pattern in patterns:
        matches = list(clips_dir.glob(pattern))
        if matches:
            return sorted(matches, key=lambda p: p.stat().st_mtime)[-1]

    return None


def generate_clip(
    generator: Generator,
    clip_defs,
    clip: dict,
    frames_dir: Path,
    clips_dir: Path,
    project_root: Path = None,
    preflight: bool = False,
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
            if preflight:
                # Use placeholder path in preflight mode
                start_frame = frames_dir / f"shot{shot_id:02d}_PENDING.png"
                print(f"Start frame: Shot {shot_id} -> [NOT YET GENERATED]")
            else:
                print(f"✗ Error: Frame for shot {shot_id} not found in {frames_dir}")
                print("  Run generate_frames.py first")
                return None
        else:
            print(f"Start frame: Shot {shot_id} -> {start_frame.name}")

    elif strategy == "last_frame":
        prev_clip_id = start_config.get("clip_id")
        # Look up the referenced clip to get its output_name for reliable matching
        prev_clip_def = clip_defs.get_clip(prev_clip_id)
        prev_output_name = prev_clip_def.get("output_name") if prev_clip_def else None
        prev_clip = find_clip_output(clips_dir, prev_clip_id, prev_output_name)
        if not prev_clip:
            if preflight:
                # Use placeholder path in preflight mode
                start_frame = clips_dir / f"clip{prev_clip_id:02d}_last_frame_PENDING.png"
                print(f"Start frame: Last frame of clip {prev_clip_id} -> [NOT YET GENERATED]")
            else:
                print(f"✗ Error: Clip {prev_clip_id} not found for last_frame extraction")
                if prev_output_name:
                    print(f"  Searched for output_name: {prev_output_name}")
                return None
        else:
            # Extract last frame
            extracted_path = clips_dir / f"clip{clip_id:02d}_start_frame.png"
            start_frame = extract_last_frame(prev_clip, extracted_path)
            if not start_frame:
                print(f"✗ Error: Failed to extract last frame from clip {prev_clip_id}")
                return None
            print(f"Start frame: Last frame of clip {prev_clip_id} ({prev_clip.name})")

    elif strategy == "custom":
        custom_path = start_config.get("custom_path")
        start_frame = Path(custom_path)
        if not start_frame.exists():
            if preflight:
                print(f"Start frame: Custom -> {start_frame} [NOT YET GENERATED]")
            else:
                print(f"✗ Error: Custom start frame not found: {custom_path}")
                return None
        else:
            print(f"Start frame: Custom -> {start_frame}")

    else:
        print(f"✗ Error: Unknown start frame strategy: {strategy}")
        return None

    # Collect scene reference frames
    prompt_mode = clip_defs.get_prompt_mode(clip)
    scene_refs = []
    if prompt_mode == "narrative":
        # Narrative mode: use shots_covered for scene refs
        for shot_id in clip.get("shots_covered", []):
            frame = find_frame_for_shot(frames_dir, shot_id)
            if frame and frame not in scene_refs:
                scene_refs.append(frame)
    else:
        # Multi-prompt mode: use shot_ref from prompts array
        for prompt_def in clip.get("prompts", []):
            shot_ref = prompt_def.get("shot_ref")
            if shot_ref:
                frame = find_frame_for_shot(frames_dir, shot_ref)
                if frame and frame not in scene_refs:
                    scene_refs.append(frame)
    print(f"Scene refs: {len(scene_refs)} frames")

    # Get characters
    characters = clip_defs.get_clip_characters(clip)

    # Resolve per-clip element_refs to file paths (multi-shot mode)
    element_refs = clip.get("element_refs", {})
    for char in characters:
        char_id = char["id"]
        if char_id in element_refs:
            ref_shots = element_refs[char_id].get("reference_shots", [])
            ref_paths = []
            for shot_id in ref_shots:
                frame = find_frame_for_shot(frames_dir, shot_id)
                if frame:
                    ref_paths.append(str(frame))
            if ref_paths:
                char["reference_image_paths"] = ref_paths

    print(f"Characters: {[c['id'] for c in characters]}")
    for c in characters:
        if "reference_image_paths" in c:
            print(f"  {c['id']}: {len(c['reference_image_paths'])} pose refs")

    # Build location element if defined at scene level
    kwargs = {}
    loc_def = clip_defs.raw_data.get("location_element")
    if loc_def:
        # Resolve relative paths from REFERENCES/ or EXPORTS/
        refs_dir = frames_dir  # fallback
        if project_root:
            for candidate in ["REFERENCES", "EXPORTS"]:
                candidate_dir = project_root / candidate
                if candidate_dir.exists():
                    refs_dir = candidate_dir
                    break
        else:
            # Walk up from frames_dir as fallback
            walk = frames_dir
            while walk.name not in ("REFERENCES", "EXPORTS") and walk.parent != walk:
                walk = walk.parent
            if walk.name in ("REFERENCES", "EXPORTS"):
                refs_dir = walk
        exports_dir = refs_dir
        loc_element = {
            "frontal": str(exports_dir / loc_def["frontal"]) if not Path(loc_def["frontal"]).is_absolute() else loc_def["frontal"],
            "element_tag": loc_def.get("element_tag", "@Element3"),
        }
        ref_paths = []
        for rp in loc_def.get("reference_shots", []):
            frame = find_frame_for_shot(frames_dir, rp)
            if frame:
                ref_paths.append(str(frame))
        loc_element["reference_image_paths"] = ref_paths
        kwargs["location_element"] = loc_element
        print(f"Location element: {loc_element['element_tag']} ({len(ref_paths)} refs)")

    # Build prompts
    prompts = clip_defs.build_clip_prompts(clip)
    if not prompts:
        print("✗ Error: No prompts defined for clip")
        return None

    if prompt_mode == "narrative":
        print(f"Prompt mode: narrative ({len(prompts[0]['prompt'])} chars)")
    else:
        print(f"Prompts: {len(prompts)} cuts")

    # Generate clip (or preflight)
    return generator.generate_video_clip(
        start_frame=start_frame,
        prompts=prompts,
        characters=characters,
        scene_refs=scene_refs,
        output_name=output_name,
        preflight=preflight,
        prompt_mode=prompt_mode,
        **kwargs,
    )


def main():
    parser = argparse.ArgumentParser(
        description="Generate video clips from clip definition YAML",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--scene", "-s",
        help="Path to scene directory (e.g., PRODUCTION/EP01/sc03). Auto-finds clip_definitions.yaml, frames/, clips/ within.",
    )
    parser.add_argument(
        "--clips", "-c",
        help="Path to clip definitions YAML file (legacy, use --scene instead)",
    )
    parser.add_argument(
        "--frames-dir", "-f",
        help="Directory containing generated frames (auto-detected from --scene)",
    )
    parser.add_argument(
        "--output-dir", "-o",
        help="Output directory for clips (auto-detected from --scene)",
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
        "--preflight", "--dry-run",
        action="store_true",
        help="Write preflight inspection JSON instead of calling FAL API",
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

    if not args.scene and not args.clips:
        parser.print_help()
        print("\nSpecify --scene or --clips")
        sys.exit(1)

    # Load configuration
    try:
        if args.project:
            project_root = Path(args.project)
        else:
            search_start = Path(args.scene or args.clips).parent if (args.scene or args.clips) else Path.cwd()
            project_root = find_project_root(search_start)
        config = load_config(project_root)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)

    # Resolve scene directory and clip definitions
    if args.scene:
        # New layout: --scene points to scene dir containing clip_definitions.yaml
        scene_path = Path(args.scene)
        if not scene_path.is_absolute():
            scene_path = project_root / args.scene
        clips_path = scene_path / "clip_definitions.yaml"
    else:
        # Legacy: --clips points directly to YAML
        clips_path = Path(args.clips)
        if not clips_path.is_absolute():
            # Try multiple locations
            for alt in [
                project_root / args.clips,
                project_root / "PRODUCTION" / args.clips,
                project_root / "VISUAL_PRODUCTION" / args.clips,
            ]:
                if alt.exists():
                    clips_path = alt
                    break
        scene_path = clips_path.parent

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
        # Try legacy paths
        scene_id_raw = clip_data.get("scene_id", "")
        for alt in [
            project_root / "VISUAL_PRODUCTION" / "shot_lists" / f"{scene_id_raw}_shots.yaml",
            project_root / "PRODUCTION" / "shot_lists" / f"{scene_id_raw}_shots.yaml",
        ]:
            if alt.exists():
                shot_list_path = alt
                break

    if not shot_list_path.exists():
        print(f"Error: Shot list not found: {shot_list_path}")
        sys.exit(1)

    shot_list = load_shot_list(shot_list_path, config)
    clip_defs = load_clip_definitions(clips_path, shot_list)

    scene_id = clip_defs.scene_id

    # Determine directories (prefer explicit args, then --scene layout, then legacy)
    if args.frames_dir:
        frames_dir = Path(args.frames_dir)
    elif args.scene:
        frames_dir = scene_path / "frames"
    else:
        frames_dir = project_root / "VISUAL_PRODUCTION" / f"{scene_id}_outputs" / "frames"

    if args.output_dir:
        output_dir = Path(args.output_dir)
    elif args.scene:
        output_dir = scene_path / "clips"
    else:
        output_dir = project_root / "VISUAL_PRODUCTION" / f"{scene_id}_outputs" / "clips"

    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"Frames directory: {frames_dir}")
    print(f"Output directory: {output_dir}")

    # Initialize generator
    try:
        generator = Generator(config, output_dir, preflight=args.preflight)
    except (ImportError, EnvironmentError) as e:
        print(f"Error: {e}")
        sys.exit(1)

    if args.preflight:
        print("\n*** PREFLIGHT MODE — no API calls will be made ***\n")

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
            project_root=project_root,
            preflight=args.preflight,
        )
        results[f"clip_{clip_id}"] = result

    # Summary
    mode_label = "PREFLIGHT COMPLETE" if args.preflight else "GENERATION COMPLETE"
    print("\n" + "="*70)
    print(mode_label)
    print("="*70)
    for name, path in results.items():
        status = "✓" if path else "✗"
        print(f"  {status} {name}: {path}")

    # Preflight: write scene-level summary and print cost totals
    if args.preflight:
        clip_summaries = []
        total_cost = 0.0
        total_duration = 0
        warnings = []

        for name, path in results.items():
            if path and Path(path).exists():
                with open(path) as f:
                    pf = json.load(f)
                analysis = pf.get("analysis", {})
                clip_summary = {
                    "clip": name,
                    "output_name": pf.get("output_name"),
                    "duration_s": analysis.get("total_duration_s", 0),
                    "cost_usd": analysis.get("estimated_cost_usd", 0),
                    "prompt_mode": analysis.get("prompt_mode", "multi_prompt"),
                    "any_over_limit": analysis.get("any_over_limit", False),
                }
                if analysis.get("prompt_mode") == "narrative":
                    clip_summary["prompt_chars"] = analysis.get("prompt_char_count", 0)
                else:
                    clip_summary["num_prompts"] = analysis.get("num_prompts", 0)
                clip_summaries.append(clip_summary)
                total_cost += analysis.get("estimated_cost_usd", 0)
                total_duration += analysis.get("total_duration_s", 0)
                if analysis.get("any_over_limit"):
                    warnings.append(f"{name}: prompt over char limit")
                files = pf.get("files", {})
                if not files.get("all_exist", True):
                    warnings.append(f"{name}: missing files: {files.get('missing', [])}")

        summary = {
            "scene_id": scene_id,
            "total_clips": len(clip_summaries),
            "total_duration_s": total_duration,
            "total_estimated_cost_usd": round(total_cost, 2),
            "clips": clip_summaries,
            "warnings": warnings,
        }

        summary_path = output_dir / f"{scene_id}_preflight_summary.json"
        with open(summary_path, "w") as f:
            json.dump(summary, f, indent=2)

        print(f"\n  Total duration: {total_duration}s")
        print(f"  Total estimated cost: ${total_cost:.2f}")
        if warnings:
            print(f"  Warnings: {len(warnings)}")
            for w in warnings:
                print(f"    - {w}")
        print(f"\n  Summary: {summary_path}")

    # Return non-zero if any failed
    if None in results.values():
        sys.exit(1)


if __name__ == "__main__":
    main()
