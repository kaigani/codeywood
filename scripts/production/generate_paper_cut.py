#!/usr/bin/env python3
"""
Generate a paper cut — static images with dialogue and direction narration.

A paper cut is a rough assembly for evaluating directorial decisions (shot
selection, pacing, dialogue rhythm, story flow) without video generation.

Two audio layers:
  1. Dialogue (character voices) — plays at intended timing
  2. Direction narration — describes camera motion/mood in dialogue gaps

Inputs:
  - shot_list.yaml (standard Codeywood format)
  - Existing frames in scene frames/ directory
  - Existing voiceover WAVs in scene voiceover/ directory
  - Optional: narrator voice ref for direction audio

Usage:
    python3 scripts/production/generate_paper_cut.py --scene PRODUCTION/EP01/sc01
    python3 scripts/production/generate_paper_cut.py --scene PRODUCTION/EP01/sc01 --preflight
    python3 scripts/production/generate_paper_cut.py --scene PRODUCTION/EP01/sc01 --no-direction
    python3 scripts/production/generate_paper_cut.py --scene PRODUCTION/EP01/sc01 --direction-only
"""

import argparse
import json
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

sys.path.insert(0, str(Path(__file__).parent.parent))

import yaml

from lib.config import load_config, find_project_root
from lib.ffmpeg import (
    image_to_clip, mix_audio_tracks,
    probe_audio_duration, probe_duration,
)
from lib.audio_analysis import generate_direction_audio


# ---------------------------------------------------------------------------
# Voiceover discovery
# ---------------------------------------------------------------------------

def discover_voiceover(vo_dir: Path) -> Dict[int, List[dict]]:
    """
    Discover existing voiceover WAVs and group by shot number.

    Returns:
        Dict mapping shot_id → list of {path, character, text, line_id}
    """
    by_shot: Dict[int, List[dict]] = {}

    for json_path in sorted(vo_dir.glob("vo*.json")):
        wav_path = json_path.with_suffix(".wav")
        if not wav_path.exists():
            continue

        with open(json_path) as f:
            meta = json.load(f)

        shot_id = meta.get("shot")
        if shot_id is None:
            continue

        entry = {
            "path": wav_path,
            "character": meta.get("character", "unknown"),
            "text": meta.get("text", ""),
            "line_id": meta.get("line_id", 0),
        }

        by_shot.setdefault(shot_id, []).append(entry)

    # Sort lines within each shot by line_id
    for shot_id in by_shot:
        by_shot[shot_id].sort(key=lambda x: x["line_id"])

    return by_shot


def discover_frames(frames_dir: Path) -> Dict[int, Path]:
    """
    Discover existing frames and map by shot number.

    Returns:
        Dict mapping shot_id → frame PNG path
    """
    frames = {}
    for png in sorted(frames_dir.glob("frame*.png")):
        # Extract shot number from filename: frame01_xxx.png → 1
        name = png.stem
        num_str = ""
        for ch in name[5:]:  # skip "frame"
            if ch.isdigit():
                num_str += ch
            else:
                break
        if num_str:
            frames[int(num_str)] = png
    return frames


# ---------------------------------------------------------------------------
# Direction text composition
# ---------------------------------------------------------------------------

def compose_direction_text(shot: dict) -> str:
    """
    Compose direction narration from shot definition.

    Uses the dedicated `direction` field when present (preferred — written
    specifically for camera movement/intent narration). Falls back to
    extracting movement cues from `video_prompt` via regex.

    This narration is a PROXY for what the video would show that a still
    image cannot — camera motion, transitions, timing, and blocking.

    Does NOT describe image contents (the viewer can see the frame).
    """
    # Prefer the dedicated direction field — it's written for narration
    direction_field = shot.get("direction", "").strip()
    if direction_field:
        return direction_field

    video_prompt = shot.get("video_prompt", "").strip()
    if not video_prompt:
        return ""

    import re

    parts = []

    # Extract shot type from opening (almost always the first few words)
    shot_type_match = re.match(
        r'^((?:Extreme |Static |Long lens )?(?:wide|medium|close-up|close up|'
        r'tight|establishing|overhead|low[- ]angle|high[- ]angle|two-shot|'
        r'over[- ]the[- ]shoulder|POV|tracking|handheld|dolly|crane|'
        r'dutch[- ]angle|bird\'?s[- ]eye)\s*(?:shot)?)',
        video_prompt, re.IGNORECASE
    )
    if shot_type_match:
        parts.append(shot_type_match.group(1).strip().capitalize())

    # Extract camera movement cues
    motion_patterns = [
        r'(camera\s+(?:pulls?|pushes?|tracks?|pans?|tilts?|cranes?|dollies?|'
        r'moves?|rises?|drops?|holds?|follows?|circles?|rotates?|racks?|'
        r'zooms?|drifts?)\s+[^.]*)',
        r'((?:slow|fast|steady|continuous|smooth|gradual)\s+'
        r'(?:pull(?:back)?|push[- ]in|track|pan|tilt|zoom|drift|reveal)[^.]*)',
        r'((?:pull(?:s|ing)?[- ]?back|push(?:es|ing)?[- ]?in|'
        r'rack(?:s|ing)? focus)[^.]*)',
    ]
    for pattern in motion_patterns:
        for match in re.finditer(pattern, video_prompt, re.IGNORECASE):
            parts.append(match.group(1).strip())

    # Extract pacing/timing cues
    pacing_patterns = [
        r'((?:a )?(?:long|slow|extended|brief|quick)\s*(?:silent\s+)?'
        r'(?:beat|pause|hold|moment|stillness)[^.]*)',
        r'(\d+\s+seconds?\s+of\s+[^.]*)',
        r'(hold(?:s|ing)?\s+(?:on|for|the)[^.]*)',
    ]
    for pattern in pacing_patterns:
        for match in re.finditer(pattern, video_prompt, re.IGNORECASE):
            parts.append(match.group(1).strip())

    # Extract blocking/spatial cues
    blocking_patterns = [
        r'((?:he|she|they|the (?:man|woman|figure))\s+'
        r'(?:walks?|runs?|turns?|mounts?|reaches?|steps?|emerges?|stands?|'
        r'sits?|moves?|enters?|exits?|follows?|stops?)\s+[^.]*)',
        r'(two (?:figures?|people|riders?)\s+[^.]*)',
    ]
    for pattern in blocking_patterns:
        matches = list(re.finditer(pattern, video_prompt, re.IGNORECASE))
        # Take at most 2 blocking cues to keep it concise
        for match in matches[:2]:
            parts.append(match.group(1).strip())

    # Extract transition cues
    transition_patterns = [
        r'((?:hard |soft |slow )?cut\s+(?:to|from)[^.]*)',
        r'((?:fade|dissolve|wipe)\s+(?:to|in|out)[^.]*)',
    ]
    for pattern in transition_patterns:
        for match in re.finditer(pattern, video_prompt, re.IGNORECASE):
            parts.append(match.group(1).strip())

    if not parts:
        # Fallback: just the shot name as a brief direction
        name = shot.get("name", "")
        dur = shot.get("duration", 5)
        if name:
            return f"{name}. Hold for {dur} seconds."
        return ""

    # Deduplicate while preserving order
    seen = set()
    unique = []
    for p in parts:
        normalized = p.lower().strip()
        if normalized not in seen:
            seen.add(normalized)
            unique.append(p)

    direction = ". ".join(unique)
    if direction and not direction.endswith("."):
        direction += "."

    return direction


# ---------------------------------------------------------------------------
# Timing calculations
# ---------------------------------------------------------------------------

def calculate_dialogue_timing(
    shot_duration: float,
    vo_lines: List[dict],
    vo_start_offset: float = 0.5,
    vo_gap: float = 0.3,
) -> List[dict]:
    """
    Calculate start times for voiceover lines within a shot.

    Args:
        shot_duration: Total shot duration in seconds
        vo_lines: List of voiceover entries with 'path'
        vo_start_offset: Delay before first line starts
        vo_gap: Gap between consecutive lines

    Returns:
        List of {path, start_s, volume, duration_s} for mix_audio_tracks
    """
    tracks = []
    current_time = vo_start_offset

    for line in vo_lines:
        wav_dur = probe_audio_duration(line["path"])
        if wav_dur is None:
            wav_dur = 2.0  # fallback estimate

        # Don't overflow the shot
        if current_time + wav_dur > shot_duration:
            break

        tracks.append({
            "path": line["path"],
            "start_s": current_time,
            "volume": 1.0,
            "duration_s": wav_dur,
        })

        current_time += wav_dur + vo_gap

    return tracks


def find_direction_gaps(
    shot_duration: float,
    dialogue_tracks: List[dict],
    min_gap: float = 1.5,
) -> List[Tuple[float, float]]:
    """
    Find time gaps between dialogue lines where direction narration can play.

    Returns:
        List of (start_s, end_s) gap intervals
    """
    gaps = []

    if not dialogue_tracks:
        # No dialogue — direction fills the whole shot
        return [(0.3, shot_duration - 0.3)]

    # Gap before first dialogue
    first_start = dialogue_tracks[0]["start_s"]
    if first_start >= min_gap:
        gaps.append((0.2, first_start - 0.2))

    # Gaps between dialogue lines
    for i in range(len(dialogue_tracks) - 1):
        end_of_current = dialogue_tracks[i]["start_s"] + dialogue_tracks[i]["duration_s"]
        start_of_next = dialogue_tracks[i + 1]["start_s"]
        gap_size = start_of_next - end_of_current
        if gap_size >= min_gap:
            gaps.append((end_of_current + 0.2, start_of_next - 0.2))

    # Gap after last dialogue
    last = dialogue_tracks[-1]
    end_of_last = last["start_s"] + last["duration_s"]
    remaining = shot_duration - end_of_last
    if remaining >= min_gap:
        gaps.append((end_of_last + 0.2, shot_duration - 0.2))

    return gaps


# ---------------------------------------------------------------------------
# Paper cut assembly
# ---------------------------------------------------------------------------

def generate_paper_cut(
    shot_list_path: Path,
    scene_dir: Path,
    project_root: Path,
    output_path: Path,
    include_direction: bool = True,
    direction_only: bool = False,
    narrator_voice_ref: Optional[Path] = None,
    comfyui_url: str = "http://192.168.1.181:8100",
    preflight: bool = False,
) -> Optional[Path]:
    """Generate a paper cut video from shot_list.yaml and existing assets."""

    start_time = time.time()

    # Load shot list
    with open(shot_list_path) as f:
        data = yaml.safe_load(f)
    shots = data.get("shots", [])

    # Discover existing assets
    frames_dir = scene_dir / "frames"
    vo_dir = scene_dir / "voiceover"

    frames = discover_frames(frames_dir) if frames_dir.exists() else {}
    voiceover = discover_voiceover(vo_dir) if vo_dir.exists() else {}

    print(f"\n{'='*60}")
    print(f"PAPER CUT — {len(shots)} shots")
    print(f"{'='*60}")
    print(f"  Scene: {scene_dir}")
    print(f"  Frames found: {len(frames)}/{len(shots)}")
    print(f"  Voiceover shots: {len(voiceover)}")
    if include_direction and narrator_voice_ref:
        print(f"  Narrator voice: {narrator_voice_ref.name}")
    elif include_direction:
        print(f"  Direction: text overlay (no narrator voice ref)")
    print()

    # Check for missing frames
    missing_frames = []
    for shot in shots:
        sid = shot["id"]
        if sid not in frames:
            missing_frames.append(sid)

    if missing_frames:
        print(f"  WARNING: Missing frames for shots: {missing_frames}")
        print(f"  Run frame generation first, or use --skip-missing")

    if preflight:
        total_dur = sum(shot.get("duration", 5) for shot in shots)
        print(f"\n  Total planned duration: {total_dur}s")
        print(f"  Dialogue lines: {sum(len(v) for v in voiceover.values())}")

        for shot in shots:
            sid = shot["id"]
            dur = shot.get("duration", 5)
            frame_status = "OK" if sid in frames else "MISSING"
            vo_count = len(voiceover.get(sid, []))
            direction = compose_direction_text(shot)
            dir_words = len(direction.split()) if direction else 0

            print(f"\n  Shot {sid:2d} [{frame_status}] {dur}s — {shot.get('name', '')}")
            if vo_count:
                for line in voiceover.get(sid, []):
                    print(f"    VO: {line['character']}: \"{line['text'][:60]}...\"" if len(line['text']) > 60 else f"    VO: {line['character']}: \"{line['text']}\"")
            if dir_words > 0:
                print(f"    DIR: {dir_words} words — \"{direction[:80]}...\"" if len(direction) > 80 else f"    DIR: {dir_words} words — \"{direction}\"")

        print(f"\n{'='*60}\n")
        return None

    # -----------------------------------------------------------------------
    # Build paper cut
    # -----------------------------------------------------------------------
    tmp_dir = Path(tempfile.mkdtemp(prefix="paper_cut_"))
    shot_clips = []

    for i, shot in enumerate(shots):
        sid = shot["id"]
        dur = shot.get("duration", 5)
        name = shot.get("name", f"shot_{sid}")

        print(f"\n  [{sid:2d}] {name} ({dur}s)")

        # Skip shots with missing frames
        if sid not in frames:
            print(f"    SKIP — no frame")
            continue

        frame_path = frames[sid]

        # Step 1: Create image clip
        clip_path = tmp_dir / f"shot_{sid:03d}.mp4"
        result = image_to_clip(frame_path, clip_path, duration_s=dur)
        if not result:
            print(f"    ERROR — image_to_clip failed")
            continue

        # Step 2: Collect audio tracks
        audio_tracks = []

        # Dialogue tracks
        if not direction_only:
            vo_lines = voiceover.get(sid, [])
            if vo_lines:
                dialogue_tracks = calculate_dialogue_timing(dur, vo_lines)
                audio_tracks.extend(dialogue_tracks)
                for t in dialogue_tracks:
                    char = next((l["character"] for l in vo_lines if l["path"] == t["path"]), "?")
                    print(f"    VO @ {t['start_s']:.1f}s: {char} ({t['duration_s']:.1f}s)")
            else:
                dialogue_tracks = []
        else:
            dialogue_tracks = []

        # Direction narration (in dialogue gaps)
        if include_direction and narrator_voice_ref and narrator_voice_ref.exists():
            direction_text = compose_direction_text(shot)
            if direction_text:
                gaps = find_direction_gaps(dur, dialogue_tracks)
                if gaps:
                    # Generate direction audio
                    dir_audio_path = tmp_dir / f"dir_{sid:03d}.wav"
                    dir_result = generate_direction_audio(
                        text=direction_text,
                        voice_ref=narrator_voice_ref,
                        output_path=dir_audio_path,
                        comfyui_url=comfyui_url,
                    )
                    if dir_result:
                        dir_dur = probe_audio_duration(dir_result) or 3.0
                        # Place in first gap that fits
                        placed = False
                        for gap_start, gap_end in gaps:
                            gap_size = gap_end - gap_start
                            if gap_size >= min(dir_dur, 1.5):
                                audio_tracks.append({
                                    "path": dir_result,
                                    "start_s": gap_start,
                                    "volume": 0.85,
                                })
                                print(f"    DIR @ {gap_start:.1f}s: \"{direction_text[:50]}...\"")
                                placed = True
                                break
                        if not placed:
                            print(f"    DIR: no gap large enough ({dir_dur:.1f}s needed)")

        # Step 3: Mix dialogue audio onto image clip
        # image_to_clip already includes silent audio track (44100Hz stereo AAC)
        # so mix_audio_tracks can reference [0:a] and all clips stay uniform
        if audio_tracks:
            mixed_path = tmp_dir / f"mixed_{sid:03d}.mp4"
            mix_result = mix_audio_tracks(clip_path, audio_tracks, mixed_path)
            if mix_result:
                shot_clips.append(mix_result)
            else:
                # Mix failed — use the image clip as-is (has silent audio)
                shot_clips.append(clip_path)
        else:
            # No dialogue — image clip already has silent audio track
            shot_clips.append(clip_path)

    if not shot_clips:
        print("\nERROR: No clips generated")
        return None

    # Step 4: Concatenate all shots
    # All clips have uniform audio (44100Hz stereo AAC 192k) so stream copy works
    print(f"\n  Assembling {len(shot_clips)} shots...")
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    concat_file = tmp_dir / "concat_list.txt"
    with open(concat_file, "w") as f:
        for clip in shot_clips:
            f.write(f"file '{clip}'\n")

    concat_cmd = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0",
        "-i", str(concat_file),
        "-c", "copy",
        str(output_path)
    ]
    result = subprocess.run(concat_cmd, capture_output=True, text=True)
    final = output_path if (result.returncode == 0 and output_path.exists()) else None
    if not final:
        print(f"  Assembly failed")
        if result.stderr:
            print(result.stderr[:500])

    elapsed = round(time.time() - start_time, 1)
    final_dur = probe_duration(output_path) if final else None

    print(f"\n{'='*60}")
    print(f"PAPER CUT COMPLETE in {elapsed}s")
    print(f"Output: {output_path}")
    if final_dur:
        print(f"Duration: {final_dur:.1f}s")
    print(f"{'='*60}\n")

    # Cleanup
    for f in tmp_dir.glob("*"):
        f.unlink()
    tmp_dir.rmdir()

    return output_path


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Generate a paper cut — static images with dialogue and direction narration."
    )
    parser.add_argument(
        "--scene", type=Path, required=True,
        help="Scene directory path (e.g., PRODUCTION/EP01/sc01)"
    )
    parser.add_argument(
        "--output", "-o", type=Path, default=None,
        help="Output path (default: scene_dir/paper_cut.mp4)"
    )
    parser.add_argument(
        "--narrator-voice", type=Path, default=None,
        help="Path to narrator voice reference WAV for direction narration"
    )
    parser.add_argument(
        "--no-direction", action="store_true",
        help="Skip direction narration (dialogue only)"
    )
    parser.add_argument(
        "--direction-only", action="store_true",
        help="Direction narration only (skip dialogue)"
    )
    parser.add_argument(
        "--preflight", action="store_true",
        help="Show plan without generating"
    )
    parser.add_argument(
        "--comfyui-url", type=str, default="http://192.168.1.181:8100",
        help="ComfyUI server URL"
    )

    args = parser.parse_args()

    # Find project root
    project_root = find_project_root()
    if not project_root:
        print("ERROR: Could not find project root (no PROJECT_CONFIG.yaml)")
        sys.exit(1)

    # Resolve scene directory
    scene_dir = args.scene
    if not scene_dir.is_absolute():
        scene_dir = project_root / scene_dir
    if not scene_dir.exists():
        print(f"ERROR: Scene directory not found: {scene_dir}")
        sys.exit(1)

    # Find shot list (try shot_list.yaml first, then shot_list_t2v.yaml)
    shot_list_path = scene_dir / "shot_list.yaml"
    if not shot_list_path.exists():
        shot_list_path = scene_dir / "shot_list_t2v.yaml"
    if not shot_list_path.exists():
        print(f"ERROR: No shot_list.yaml or shot_list_t2v.yaml in {scene_dir}")
        sys.exit(1)

    # Output path
    output_path = args.output or (scene_dir / "paper_cut.mp4")

    # Narrator voice ref
    narrator_voice = args.narrator_voice
    if narrator_voice and not narrator_voice.is_absolute():
        narrator_voice = project_root / narrator_voice

    generate_paper_cut(
        shot_list_path=shot_list_path,
        scene_dir=scene_dir,
        project_root=project_root,
        output_path=output_path,
        include_direction=not args.no_direction,
        direction_only=args.direction_only,
        narrator_voice_ref=narrator_voice,
        comfyui_url=args.comfyui_url,
        preflight=args.preflight,
    )


if __name__ == "__main__":
    main()
