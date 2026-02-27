#!/usr/bin/env python3
"""
Smart assembly tool — reads an EDL (Edit Decision List) YAML and executes
a full assembly with trimming and transitions.

Usage:
    python3 scripts/editing/smart_assemble.py EDL_FILE
    python3 scripts/editing/smart_assemble.py EDL_FILE --output assembled.mp4
    python3 scripts/editing/smart_assemble.py EDL_FILE --preflight

EDL format (YAML):
    output: assembly.mp4
    clips:
      - path: clip01.mp4
        trim_in_s: 0.3          # Trim from head (optional, default 0)
        trim_out_s: 0.5         # Trim from tail (optional, default 0)
        transition_out: hard_cut  # hard_cut, crossfade, l_cut, j_cut
      - path: clip02.mp4
        trim_in_s: 0.0
        trim_out_s: 0.8
        transition_out: crossfade
        transition_duration: 0.5
      - path: clip03.mp4
        transition_out: l_cut
        audio_lead_s: 1.0
"""

import argparse
import json
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent.parent))

import yaml

from lib.ffmpeg import (
    trim_clip, crossfade_transition, l_cut, j_cut,
    concatenate_clips, probe_duration
)


def load_edl(edl_path: Path) -> dict:
    """Load and validate an EDL YAML file."""
    with open(edl_path) as f:
        edl = yaml.safe_load(f)

    if not edl or "clips" not in edl:
        print(f"ERROR: EDL must contain a 'clips' list")
        sys.exit(1)

    return edl


def resolve_clip_path(clip_entry: dict, base_dir: Path) -> Path:
    """Resolve clip path relative to EDL file location."""
    path = Path(clip_entry["path"])
    if path.is_absolute():
        return path
    return base_dir / path


def preflight(edl: dict, base_dir: Path):
    """Show what the assembly would do without executing."""
    clips = edl["clips"]
    total_input_dur = 0
    total_trim = 0
    missing = []

    print(f"\n{'='*60}")
    print(f"SMART ASSEMBLE — PREFLIGHT")
    print(f"{'='*60}")
    print(f"Clips: {len(clips)}")
    print()

    for i, entry in enumerate(clips):
        path = resolve_clip_path(entry, base_dir)
        exists = path.exists()
        dur = probe_duration(path) if exists else None

        trim_in = entry.get("trim_in_s", 0)
        trim_out = entry.get("trim_out_s", 0)
        transition = entry.get("transition_out", "hard_cut")

        status = "OK" if exists else "MISSING"
        if not exists:
            missing.append(str(path))

        dur_str = f"{dur:.2f}s" if dur else "??s"
        trimmed_dur = (dur - trim_in - trim_out) if dur else None
        trimmed_str = f"→ {trimmed_dur:.2f}s" if trimmed_dur else ""

        if dur:
            total_input_dur += dur
            total_trim += trim_in + trim_out

        print(f"  [{i+1:02d}] {path.name:<30} {dur_str:>8} {trimmed_str:>10}  [{status}]")
        if trim_in > 0 or trim_out > 0:
            print(f"       trim: -{trim_in}s head, -{trim_out}s tail")
        if i < len(clips) - 1:
            trans_detail = transition
            if transition == "crossfade":
                trans_detail += f" ({entry.get('transition_duration', 1.0)}s)"
            elif transition in ("l_cut", "j_cut"):
                lead_key = "audio_lead_s" if transition == "l_cut" else "video_lead_s"
                trans_detail += f" ({entry.get(lead_key, 1.0)}s)"
            print(f"       → {trans_detail}")

    print(f"\n  Total input: {total_input_dur:.1f}s")
    print(f"  Total trimmed: {total_trim:.1f}s")
    print(f"  Estimated output: ~{total_input_dur - total_trim:.1f}s")

    if missing:
        print(f"\n  WARNING: {len(missing)} missing clip(s):")
        for m in missing:
            print(f"    {m}")

    print(f"{'='*60}\n")


def trim_and_reencode(src: Path, dst: Path, start_s: float = 0, end_s: float = None,
                      strip_audio: bool = False) -> Optional[Path]:
    """Trim and re-encode a clip in one pass to uniform H.264 parameters."""
    cmd = ["ffmpeg", "-y"]
    if start_s > 0:
        cmd += ["-ss", str(start_s)]
    cmd += ["-i", str(src)]
    if end_s is not None:
        cmd += ["-to", str(end_s - start_s)]  # -to is relative when -ss is before -i
    cmd += [
        "-c:v", "libx264", "-preset", "fast", "-crf", "18",
        "-pix_fmt", "yuv420p",
        "-r", "25",
    ]
    if strip_audio:
        cmd += ["-an"]
    else:
        cmd += ["-c:a", "aac", "-b:a", "128k"]
    cmd.append(str(dst))
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0 and dst.exists():
        return dst
    # Retry without audio if audio encoding failed
    if not strip_audio and result.returncode != 0:
        cmd_retry = [c for c in cmd if c not in ["-c:a", "aac", "-b:a", "128k"]]
        cmd_retry.insert(-1, "-an")
        result = subprocess.run(cmd_retry, capture_output=True, text=True)
        if result.returncode == 0 and dst.exists():
            return dst
    print(f"    ffmpeg error: {result.stderr[-200:]}" if result.stderr else "    unknown error")
    return None


def smart_assemble(edl: dict, base_dir: Path, output_path: Path) -> Path:
    """
    Execute the assembly described by the EDL.

    Strategy:
    1. Trim + re-encode all clips in one pass (uniform H.264 parameters)
    2. Group segments by transition type:
       - Consecutive hard_cuts → collect for single concat pass
       - crossfade/l_cut/j_cut → apply pairwise, then join segments
    3. Final single-pass concat of all segments
    """
    clips_spec = edl["clips"]
    start_time = time.time()
    tmp_dir = Path(tempfile.mkdtemp(prefix="assembly_"))

    print(f"\n{'='*60}")
    print(f"SMART ASSEMBLE — {len(clips_spec)} clips")
    print(f"{'='*60}")

    # Step 1: Trim + re-encode all clips in one pass
    print(f"\n[Step 1] Trim + re-encode to uniform format...")
    uniform_clips = []
    for i, entry in enumerate(clips_spec):
        src = resolve_clip_path(entry, base_dir)
        if not src.exists():
            print(f"  ERROR: Missing clip: {src}")
            sys.exit(1)

        trim_in = entry.get("trim_in_s", 0)
        trim_out = entry.get("trim_out_s", 0)
        dur = probe_duration(src)
        end_s = (dur - trim_out) if dur and trim_out > 0 else None

        uniform_path = tmp_dir / f"uniform_{i:03d}.mp4"
        result = trim_and_reencode(src, uniform_path, start_s=trim_in, end_s=end_s)
        if result:
            uniform_clips.append(result)
            out_dur = probe_duration(result)
            print(f"  [{i+1:02d}] {src.name:<35} → {out_dur:.2f}s")
        else:
            print(f"  ERROR: Failed to process {src.name}")
            sys.exit(1)

    # Step 3: Build segments (handle transitions)
    print(f"\n[Step 3] Building assembly...")
    # Check if we have any non-hard-cut transitions
    has_complex_transitions = any(
        entry.get("transition_out", "hard_cut") != "hard_cut"
        for entry in clips_spec[:-1]
    )

    if not has_complex_transitions:
        # All hard cuts — single concat pass (fast path)
        print(f"  All hard cuts — single-pass concat of {len(uniform_clips)} clips")
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        final = concatenate_clips(uniform_clips, output_path)
    else:
        # Mixed transitions — group consecutive hard-cuts, apply complex transitions
        segments = []  # List of clip paths ready for final concat
        i = 0
        while i < len(uniform_clips):
            transition = clips_spec[i].get("transition_out", "hard_cut") if i < len(clips_spec) - 1 else None

            if transition in ("crossfade", "l_cut", "j_cut"):
                next_clip = uniform_clips[i + 1]
                seg_output = tmp_dir / f"seg_{len(segments):03d}.mp4"

                if transition == "crossfade":
                    dur = clips_spec[i].get("transition_duration", 1.0)
                    result = crossfade_transition(uniform_clips[i], next_clip, seg_output, duration=dur)
                elif transition == "l_cut":
                    lead = clips_spec[i].get("audio_lead_s", 1.0)
                    result = l_cut(uniform_clips[i], next_clip, seg_output, audio_lead_s=lead)
                elif transition == "j_cut":
                    lead = clips_spec[i].get("video_lead_s", 1.0)
                    result = j_cut(uniform_clips[i], next_clip, seg_output, video_lead_s=lead)

                if result:
                    segments.append(result)
                else:
                    # Fallback: add both as separate clips
                    segments.append(uniform_clips[i])
                    segments.append(next_clip)
                i += 2  # Skip both clips involved in the transition
            else:
                # hard_cut or last clip — just add to segments
                segments.append(uniform_clips[i])
                i += 1

        # Final concat of all segments
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        if len(segments) == 1:
            import shutil
            shutil.copy2(str(segments[0]), str(output_path))
            final = output_path
        else:
            final = concatenate_clips(segments, output_path)

    elapsed = round(time.time() - start_time, 1)
    final_dur = probe_duration(output_path) if final else None

    print(f"\n{'='*60}")
    print(f"ASSEMBLY COMPLETE in {elapsed}s")
    print(f"Output: {output_path}")
    if final_dur:
        print(f"Duration: {final_dur:.2f}s")
    print(f"{'='*60}\n")

    # Cleanup temp files
    for f in tmp_dir.glob("*"):
        f.unlink()
    tmp_dir.rmdir()

    return output_path


def main():
    parser = argparse.ArgumentParser(
        description="Smart assembly — reads EDL YAML, executes trimming + transitions."
    )
    parser.add_argument("edl", type=Path, help="Path to EDL YAML file")
    parser.add_argument("--output", "-o", type=Path, default=None,
                        help="Output path (default: from EDL or assembly.mp4)")
    parser.add_argument("--preflight", action="store_true",
                        help="Show what would be done without executing")

    args = parser.parse_args()

    if not args.edl.exists():
        print(f"ERROR: EDL file not found: {args.edl}")
        sys.exit(1)

    edl = load_edl(args.edl)
    base_dir = args.edl.parent

    if args.preflight:
        preflight(edl, base_dir)
        return

    if args.output is None:
        args.output = Path(edl.get("output", "assembly.mp4"))
        if not args.output.is_absolute():
            args.output = base_dir / args.output

    smart_assemble(edl, base_dir, args.output)


if __name__ == "__main__":
    main()
