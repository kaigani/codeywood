#!/usr/bin/env python3
"""
Assemble EP01 final video from per-shot clips.

Steps:
  1. Normalize each clip to 1920x1080, 25fps, 44100Hz stereo AAC
  2. Concat via ffmpeg concat demuxer (re-encode, never stream-copy)

Usage:
    python assemble.py
    python assemble.py --force
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import (
    ASSEMBLY_DIR, CLIP_DEFS, CLIPS_DIR, DELIVERABLES,
    probe_duration_ff, run_ffmpeg,
)


def load_shots() -> list[dict]:
    with open(CLIP_DEFS) as f:
        return yaml.safe_load(f)["shots"]


def normalize_clip(src: Path, dst: Path) -> bool:
    cmd = [
        "ffmpeg", "-y", "-i", str(src),
        "-vf", "scale=1920:1080:force_original_aspect_ratio=decrease,"
               "pad=1920:1080:(ow-iw)/2:(oh-ih)/2:black,fps=25",
        "-c:v", "libx264", "-preset", "fast", "-crf", "18",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-ac", "2",
        "-movflags", "+faststart",
        str(dst),
    ]
    return run_ffmpeg(cmd, f"-> {dst.name}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    ASSEMBLY_DIR.mkdir(parents=True, exist_ok=True)
    DELIVERABLES.mkdir(parents=True, exist_ok=True)
    norm_dir = ASSEMBLY_DIR / "normalized"
    norm_dir.mkdir(exist_ok=True)

    shots = load_shots()

    print("=" * 70)
    print("ASSEMBLE EP01")
    print("=" * 70)

    # Phase 1: normalize
    missing = []
    norm_paths: list[Path] = []
    for shot in shots:
        sid = shot["id"]
        src = CLIPS_DIR / f"clip_{sid:02d}.mp4"
        if not src.exists():
            missing.append(sid)
            continue
        dst = norm_dir / f"clip_{sid:02d}_norm.mp4"
        if dst.exists() and not args.force:
            print(f"  Shot {sid:2d}: SKIP (normalized exists)")
        else:
            print(f"  Shot {sid:2d}: normalizing")
            if not normalize_clip(src, dst):
                print(f"    FAILED")
                missing.append(sid)
                continue
        norm_paths.append(dst)

    if missing:
        print(f"\n  MISSING/FAILED clips: {missing}")
        sys.exit(1)

    # Phase 2: concat list
    concat_list = ASSEMBLY_DIR / "concat.txt"
    with open(concat_list, "w") as f:
        for p in norm_paths:
            f.write(f"file '{p.resolve()}'\n")

    # Phase 3: concat (re-encode, never stream-copy)
    final_out = DELIVERABLES / "EP01_the_breach.mp4"
    print(f"\nConcatenating {len(norm_paths)} normalized clips...")

    cmd = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0",
        "-i", str(concat_list),
        "-c:v", "libx264", "-preset", "medium", "-crf", "18",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-ac", "2",
        "-movflags", "+faststart",
        "-shortest",
        str(final_out),
    ]
    if not run_ffmpeg(cmd, f"-> {final_out.name}"):
        print("CONCAT FAILED")
        sys.exit(1)

    dur = probe_duration_ff(final_out)
    size_mb = final_out.stat().st_size / 1024 / 1024
    print(f"\n{'=' * 70}")
    print(f"DELIVERABLE: {final_out}")
    print(f"  Duration: {dur:.1f}s")
    print(f"  Size:     {size_mb:.1f} MB")
    print("=" * 70)


if __name__ == "__main__":
    main()
