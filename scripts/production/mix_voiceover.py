#!/usr/bin/env python3
"""
Mix voiceover audio into T2V clips and reassemble scenes + episode.

Reads ledger_voiceover.yaml, finds corresponding T2V clips, overlays VO
audio at calculated timings, and produces new clips in clips_t2v_vo/.
Clips without VO are copied through unchanged.

Then reassembles each scene and the full episode.

Usage:
    python mix_voiceover.py
    python mix_voiceover.py --scene sc05b
    python mix_voiceover.py --preflight
    python mix_voiceover.py --assemble-only
"""

import argparse
import json
import shutil
import subprocess
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

import yaml

# Add scripts/ to path for shared lib imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.config import load_config, find_project_root
from lib.ffmpeg import (
    probe_audio_duration,
    probe_duration,
    concatenate_clips,
)


# Gap between sequential VO lines within the same shot (seconds)
VO_GAP = 0.8
# Offset from clip start before first VO line (seconds)
VO_START_OFFSET = 0.5


def load_voiceover_catalog(episode_dir: Path) -> list:
    """Load ledger_voiceover.yaml."""
    catalog_path = episode_dir / "ledger_voiceover.yaml"
    if not catalog_path.exists():
        raise FileNotFoundError(f"Voiceover catalog not found: {catalog_path}")
    with open(catalog_path) as f:
        data = yaml.safe_load(f)
    return data.get("lines", [])


def group_by_scene_shot(lines: list) -> dict:
    """Group VO lines by (scene, shot) → list of lines in order."""
    groups = defaultdict(list)
    for line in lines:
        key = (line["scene"], line["shot"])
        groups[key].append(line)
    return dict(groups)


def find_clip_for_shot(scene_dir: Path, shot_id: int) -> Path:
    """Find the T2V clip file for a given shot ID."""
    clips_dir = scene_dir / "clips_t2v"
    if not clips_dir.exists():
        return None
    pattern = f"clip{shot_id:02d}_*.mp4"
    matches = sorted(clips_dir.glob(pattern))
    return matches[0] if matches else None


def vo_filename(line: dict) -> str:
    """Get the expected VO WAV filename for a line."""
    import re
    line_id = line["id"]
    character = line["character"]
    words = re.sub(r'[^a-z0-9\s]', '', line["text"].lower()).split()
    slug = "_".join(words[:6])[:40]
    return f"vo{line_id:02d}_{character}_{slug}.wav"


def find_vo_file(line: dict, scene_dir: Path) -> Path:
    """Find the generated VO WAV file for a line."""
    vo_dir = scene_dir / "voiceover"
    filename = vo_filename(line)
    path = vo_dir / filename
    return path if path.exists() else None


def calculate_timings(vo_files: list, clip_duration: float) -> tuple:
    """
    Calculate start times for sequential VO lines within a clip.

    Places lines sequentially with VO_GAP between them, starting at
    VO_START_OFFSET. If total VO exceeds clip duration, compresses gaps
    but preserves all lines (the clip will be extended).

    Args:
        vo_files: List of (line_dict, wav_path) tuples
        clip_duration: Duration of the video clip in seconds

    Returns:
        (timings, required_duration) where:
        - timings: List of (wav_path, start_s) tuples
        - required_duration: Total duration needed (may exceed clip_duration)
    """
    if not vo_files:
        return [], 0.0

    # Get durations of each VO file
    durations = []
    for line, wav_path in vo_files:
        dur = probe_audio_duration(wav_path)
        if dur is None:
            dur = 2.0  # fallback estimate
        durations.append(dur)

    total_vo_time = sum(durations)
    n_gaps = len(durations) - 1
    total_gaps = n_gaps * VO_GAP
    total_needed = VO_START_OFFSET + total_vo_time + total_gaps

    # If VO fits within clip, use standard spacing
    if total_needed <= clip_duration:
        offset = VO_START_OFFSET
        gap = VO_GAP
    else:
        # Compress gaps but keep all lines — clip will be extended
        offset = 0.3
        gap = 0.0  # pack tight when overflowing

    # Calculate start times
    result = []
    current_time = offset
    for i, (line, wav_path) in enumerate(vo_files):
        result.append((wav_path, current_time))
        current_time += durations[i] + gap

    required_duration = current_time + 0.5  # small tail padding
    return result, required_duration


def _has_audio_track(video_path: Path) -> bool:
    """Check if a video file has an audio stream."""
    cmd = [
        "ffprobe", "-v", "quiet",
        "-select_streams", "a",
        "-show_entries", "stream=codec_type",
        "-of", "csv=p=0",
        str(video_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return bool(result.stdout.strip())


def mix_vo_onto_clip(
    clip_path: Path,
    audio_tracks: list,
    output_path: Path,
    extend_duration: float = None,
) -> Path:
    """
    Mix VO audio tracks onto a video clip, preserving original audio.

    The original audio from the video is preserved at full volume. VO tracks
    are overlaid on top using the overlay filter (no amix normalization).

    If extend_duration exceeds the clip duration, the clip's last frame is
    frozen (tpad) and original audio is padded with silence.

    Args:
        clip_path: Path to source video clip
        audio_tracks: List of dicts with path, start_s, volume
        output_path: Path for output video
        extend_duration: Total required duration (None = don't extend)

    Returns:
        Path to output video, or None on failure
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    clip_dur = probe_duration(clip_path) or 10.0
    needs_extension = extend_duration and extend_duration > clip_dur + 0.5
    has_audio = _has_audio_track(clip_path)

    # Build input list: video first, then VO tracks
    inputs = ["-i", str(clip_path)]
    for track in audio_tracks:
        inputs.extend(["-i", str(track["path"])])

    filter_parts = []

    # --- VIDEO ---
    if needs_extension:
        extra = extend_duration - clip_dur
        filter_parts.append(
            f"[0:v]tpad=stop_mode=clone:stop_duration={extra:.1f}[vout]"
        )
        video_map = "[vout]"
        video_codec = ["-c:v", "libx264", "-crf", "18", "-preset", "fast"]
    else:
        video_map = "0:v"
        video_codec = ["-c:v", "copy"]

    # --- AUDIO ---
    # Prepare each VO track with delay
    vo_labels = []
    for i, track in enumerate(audio_tracks):
        input_idx = i + 1
        delay_ms = int(track.get("start_s", 0) * 1000)
        volume = track.get("volume", 1.0)
        label = f"vo{i}"
        filter_parts.append(
            f"[{input_idx}:a]adelay={delay_ms}|{delay_ms},volume={volume}[{label}]"
        )
        vo_labels.append(f"[{label}]")

    # Mix all VO tracks into one combined VO stream
    if len(vo_labels) == 1:
        vo_combined = vo_labels[0]
    else:
        vo_input_str = "".join(vo_labels)
        filter_parts.append(
            f"{vo_input_str}amix=inputs={len(vo_labels)}:normalize=0:duration=longest[vo_mix]"
        )
        vo_combined = "[vo_mix]"

    if has_audio:
        # Preserve original audio at full volume, overlay VO on top
        if needs_extension:
            # Pad original audio with silence to match extended video
            pad_dur = extend_duration
            filter_parts.append(
                f"[0:a]apad=whole_dur={pad_dur:.1f}[orig_pad]"
            )
            orig_label = "[orig_pad]"
        else:
            orig_label = "[0:a]"

        # Overlay: original + VO combined, normalize=0 preserves volumes
        filter_parts.append(
            f"{orig_label}{vo_combined}amix=inputs=2:normalize=0:duration=longest[aout]"
        )
        audio_label = "[aout]"
    else:
        # No original audio — VO is the only audio
        audio_label = vo_combined

    filter_complex = ";".join(filter_parts)

    cmd = [
        "ffmpeg", "-y",
        *inputs,
        "-filter_complex", filter_complex,
        "-map", video_map,
        "-map", audio_label,
        *video_codec,
        "-c:a", "aac",
        "-b:a", "192k",
        str(output_path),
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0 and output_path.exists():
        return output_path
    else:
        if result.stderr:
            # If original audio caused issues, retry without it
            if has_audio and ("Invalid" in result.stderr or "does not contain" in result.stderr):
                print(f"    Retrying without original audio...")
                return mix_vo_onto_clip(clip_path, audio_tracks, output_path, extend_duration)
            print(f"    ffmpeg error: {result.stderr[:400]}")
        return None


def mix_scene(
    scene_id: str,
    scene_dir: Path,
    scene_lines: dict,
    output_base: Path,
    dry_run: bool = False,
) -> dict:
    """
    Mix VO into all clips for a scene.

    Args:
        scene_id: Scene identifier (e.g., "sc02")
        scene_dir: Path to scene directory
        scene_lines: Dict of {shot_id: [lines]} for this scene
        output_base: Base output directory for mixed clips
        dry_run: If True, print plan but don't execute

    Returns:
        Dict with stats
    """
    clips_dir = scene_dir / "clips_t2v"
    output_dir = output_base / "clips_t2v_vo"
    output_dir.mkdir(parents=True, exist_ok=True)

    if not clips_dir.exists():
        print(f"  WARNING: No clips_t2v/ directory in {scene_dir}")
        return {"mixed": 0, "copied": 0, "failed": 0}

    # Get all clips in order
    all_clips = sorted(clips_dir.glob("clip*.mp4"))
    if not all_clips:
        print(f"  WARNING: No clips found in {clips_dir}")
        return {"mixed": 0, "copied": 0, "failed": 0}

    stats = {"mixed": 0, "copied": 0, "failed": 0}

    for clip_path in all_clips:
        # Extract shot ID from filename (clip06_the_ledger_revealed.mp4 → 6)
        clip_name = clip_path.stem
        try:
            shot_id = int(clip_name.split("_")[0].replace("clip", ""))
        except (ValueError, IndexError):
            print(f"  WARNING: Can't parse shot ID from {clip_name}")
            continue

        output_path = output_dir / clip_path.name

        if shot_id in scene_lines:
            # This clip has VO lines to mix
            lines = scene_lines[shot_id]

            # Find VO files
            vo_files = []
            for line in lines:
                vo_path = find_vo_file(line, scene_dir)
                if vo_path:
                    vo_files.append((line, vo_path))
                else:
                    print(f"  WARNING: VO file not found for line {line['id']}")

            if not vo_files:
                # No VO files found, copy through
                if not dry_run:
                    shutil.copy2(clip_path, output_path)
                print(f"  {clip_name}: COPY (VO files missing)")
                stats["copied"] += 1
                continue

            # Get clip duration for timing calculation
            clip_dur = probe_duration(clip_path) or 10.0

            # Calculate timings
            timings, required_dur = calculate_timings(vo_files, clip_dur)
            extends = required_dur > clip_dur + 0.5

            # Build audio tracks
            audio_tracks = []
            for wav_path, start_s in timings:
                audio_tracks.append({
                    "path": wav_path,
                    "start_s": start_s,
                    "volume": 1.0,
                })

            # Log
            n_lines = len(vo_files)
            chars = set(l["character"] for l, _ in vo_files)
            extend_note = f" [EXTEND {clip_dur:.0f}s → {required_dur:.0f}s]" if extends else ""
            print(f"  {clip_name}: MIX {n_lines} VO line(s) ({', '.join(sorted(chars))}){extend_note}")
            for wav_path, start_s in timings:
                dur = probe_audio_duration(wav_path) or 0
                print(f"    {start_s:.1f}s: {wav_path.name} ({dur:.1f}s)")

            if dry_run:
                stats["mixed"] += 1
                continue

            # Mix VO onto clip (with optional video extension)
            result = mix_vo_onto_clip(
                clip_path=clip_path,
                audio_tracks=audio_tracks,
                output_path=output_path,
                extend_duration=required_dur if extends else None,
            )
            if result:
                stats["mixed"] += 1
            else:
                # Fallback: copy original
                shutil.copy2(clip_path, output_path)
                stats["failed"] += 1
                print(f"    FAILED — copied original instead")
        else:
            # No VO for this shot — copy clip through unchanged
            if not dry_run:
                shutil.copy2(clip_path, output_path)
            stats["copied"] += 1

    return stats


def assemble_scene(scene_dir: Path, scene_id: str) -> Path:
    """Assemble clips_t2v_vo/ into a scene assembly."""
    clips_dir = scene_dir / "clips_t2v_vo"
    assembly_dir = scene_dir / "assembly_t2v_vo"
    assembly_dir.mkdir(parents=True, exist_ok=True)

    clips = sorted(clips_dir.glob("clip*.mp4"))
    if not clips:
        print(f"  No clips to assemble for {scene_id}")
        return None

    output_path = assembly_dir / f"{scene_id}_t2v_vo_assembled.mp4"
    return concatenate_clips(clips, output_path)


def assemble_episode(production_dir: Path, scene_order: list) -> Path:
    """Concatenate all scene assemblies into episode rough cut."""
    deliverables_dir = production_dir.parent.parent / "DELIVERABLES" / "EP01"
    deliverables_dir.mkdir(parents=True, exist_ok=True)

    scene_assemblies = []
    for scene_id in scene_order:
        scene_dir = production_dir / scene_id

        # Prefer VO assembly, fall back to plain T2V assembly
        vo_assembly_dir = scene_dir / "assembly_t2v_vo"
        t2v_assembly_dir = scene_dir / "assembly_t2v"

        assembly = None
        if vo_assembly_dir.exists():
            matches = sorted(vo_assembly_dir.glob("*_assembled.mp4"))
            if matches:
                assembly = matches[0]

        if not assembly and t2v_assembly_dir.exists():
            matches = sorted(t2v_assembly_dir.glob("*_assembled.mp4"))
            if matches:
                assembly = matches[0]

        if assembly:
            dur = probe_duration(assembly) or 0
            size_mb = assembly.stat().st_size / (1024 * 1024)
            print(f"  {scene_id}: {assembly.parent.name}/{assembly.name} ({dur:.1f}s, {size_mb:.1f}MB)")
            scene_assemblies.append(assembly)
        else:
            print(f"  {scene_id}: WARNING — no assembly found, skipping")

    if not scene_assemblies:
        print("No scene assemblies found")
        return None

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = deliverables_dir / f"ep01_t2v_vo_rough_cut_{timestamp}.mp4"

    print(f"\nConcatenating {len(scene_assemblies)} scenes into rough cut...")
    result = concatenate_clips(scene_assemblies, output_path)

    if result:
        dur = probe_duration(result) or 0
        size_mb = result.stat().st_size / (1024 * 1024)
        print(f"\nEP01 T2V+VO Rough Cut: {result}")
        print(f"Duration: {dur:.1f}s ({dur/60:.1f}m)")
        print(f"Size: {size_mb:.1f}MB")
        print(f"Scenes: {len(scene_assemblies)}")

        # Write manifest
        manifest = {
            "timestamp": timestamp,
            "scenes": [],
            "total_duration_s": dur,
        }
        for assembly in scene_assemblies:
            scene_id = assembly.parent.parent.name
            scene_dur = probe_duration(assembly) or 0
            has_vo = "vo" in assembly.parent.name
            manifest["scenes"].append({
                "scene": scene_id,
                "file": str(assembly),
                "duration_s": scene_dur,
                "has_voiceover": has_vo,
            })
        manifest_path = result.with_suffix(".json")
        with open(manifest_path, "w") as f:
            json.dump(manifest, f, indent=2)
        print(f"Manifest: {manifest_path}")

    return result


# Scene order for EP01
SCENE_ORDER = [
    "sc01", "sc02", "sc02b", "sc03", "sc04",
    "sc05a", "sc05b", "sc06", "sc07", "sc08", "sc09", "sc10",
]


def main():
    parser = argparse.ArgumentParser(
        description="Mix voiceover into T2V clips and reassemble",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--scene", "-s",
        help="Only process a specific scene (e.g., sc05b)",
    )
    parser.add_argument(
        "--preflight",
        action="store_true",
        help="Show mixing plan without executing",
    )
    parser.add_argument(
        "--assemble-only",
        action="store_true",
        help="Skip mixing, just reassemble from existing clips_t2v_vo/",
    )
    parser.add_argument(
        "--no-assemble",
        action="store_true",
        help="Mix clips but skip scene/episode assembly",
    )
    parser.add_argument(
        "--project",
        help="Path to project root (auto-detected if not specified)",
    )
    args = parser.parse_args()

    # Load project config
    try:
        if args.project:
            project_root = Path(args.project)
        else:
            project_root = find_project_root()
        config = load_config(project_root)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)

    production_dir = project_root / "PRODUCTION" / "EP01"
    if not production_dir.exists():
        print(f"Error: Production dir not found: {production_dir}")
        sys.exit(1)

    # Load VO catalog
    try:
        all_lines = load_voiceover_catalog(production_dir)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)

    # Filter by scene
    if args.scene:
        all_lines = [l for l in all_lines if l["scene"] == args.scene]

    # Group by scene, then by shot within scene
    scene_groups = defaultdict(lambda: defaultdict(list))
    for line in all_lines:
        scene_groups[line["scene"]][line["shot"]].append(line)

    # Determine which scenes to process
    if args.scene:
        scenes_to_process = [args.scene]
    else:
        # All scenes that have clips_t2v/
        scenes_to_process = []
        for scene_id in SCENE_ORDER:
            scene_dir = production_dir / scene_id
            if (scene_dir / "clips_t2v").exists():
                scenes_to_process.append(scene_id)

    print(f"EP01 Voiceover Mix")
    print(f"Scenes: {scenes_to_process}")
    print(f"VO lines: {len(all_lines)} across {len(scene_groups)} scenes")
    print(f"{'='*60}")

    if not args.assemble_only:
        # Mix VO into clips
        total_stats = {"mixed": 0, "copied": 0, "failed": 0}

        for scene_id in scenes_to_process:
            scene_dir = production_dir / scene_id
            shot_lines = dict(scene_groups.get(scene_id, {}))

            vo_count = sum(len(v) for v in shot_lines.values())
            print(f"\n--- {scene_id} ({vo_count} VO lines across {len(shot_lines)} shots) ---")

            stats = mix_scene(
                scene_id=scene_id,
                scene_dir=scene_dir,
                scene_lines=shot_lines,
                output_base=scene_dir,
                dry_run=args.preflight,
            )

            for k in total_stats:
                total_stats[k] += stats[k]

        print(f"\n{'='*60}")
        print(f"MIX COMPLETE")
        print(f"  Mixed: {total_stats['mixed']} clips")
        print(f"  Copied (no VO): {total_stats['copied']} clips")
        print(f"  Failed: {total_stats['failed']} clips")

        if args.preflight:
            print("\n(Preflight mode — no files written)")
            sys.exit(0)

    # Assemble scenes and episode
    if not args.no_assemble:
        print(f"\n{'='*60}")
        print("ASSEMBLY")
        print(f"{'='*60}")

        for scene_id in scenes_to_process:
            scene_dir = production_dir / scene_id
            # Only assemble if clips_t2v_vo/ exists
            vo_clips_dir = scene_dir / "clips_t2v_vo"
            if vo_clips_dir.exists() and any(vo_clips_dir.glob("clip*.mp4")):
                print(f"\n--- {scene_id} ---")
                assemble_scene(scene_dir, scene_id)
            else:
                print(f"\n--- {scene_id}: using existing assembly_t2v/ ---")

        # Episode assembly
        print(f"\n{'='*60}")
        print("EPISODE ASSEMBLY")
        print(f"{'='*60}")
        assemble_episode(production_dir, SCENE_ORDER)


if __name__ == "__main__":
    main()
