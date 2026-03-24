#!/usr/bin/env python3
"""
Table Read v02 — Assemble all clips into final video.

- Concatenates all shot clips in order with hard cuts
- Layers V.O. audio onto PROD shots that have dialogue
- Adds 2s black hold at end
- Output: table_read/table_read_ep01_v02.mp4
"""

import subprocess
import sys
from pathlib import Path

import yaml

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
PROJECT = Path(__file__).resolve().parents[2] / "projects" / "stray-signal"
TABLE_READ = PROJECT / "PRODUCTION" / "EP01_v03" / "table_read"
SHOT_LIST = TABLE_READ / "table_read_shot_list.yaml"
CLIPS_DIR = TABLE_READ / "clips"
AUDIO_DIR = TABLE_READ / "audio"
OUTPUT = TABLE_READ / "table_read_ep01_v02.mp4"

TARGET_W, TARGET_H = 1280, 720
FPS = 25


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def probe_has_audio(clip_path):
    """Check if clip has an audio stream."""
    cmd = [
        "ffprobe", "-v", "error",
        "-select_streams", "a",
        "-show_entries", "stream=codec_type",
        "-of", "csv=p=0",
        str(clip_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return "audio" in result.stdout


def normalize_clip(clip_path, norm_path, has_audio):
    """Re-encode clip to uniform format. Add silent audio if needed."""
    if has_audio:
        cmd = [
            "ffmpeg", "-y",
            "-i", str(clip_path),
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-vf", f"scale={TARGET_W}:{TARGET_H},fps={FPS}",
            "-preset", "medium",
            "-crf", "18",
            "-c:a", "aac",
            "-ar", "44100",
            "-ac", "2",
            "-b:a", "128k",
            str(norm_path),
        ]
    else:
        cmd = [
            "ffmpeg", "-y",
            "-i", str(clip_path),
            "-f", "lavfi",
            "-i", "anullsrc=r=44100:cl=stereo",
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-vf", f"scale={TARGET_W}:{TARGET_H},fps={FPS}",
            "-preset", "medium",
            "-crf", "18",
            "-c:a", "aac",
            "-ar", "44100",
            "-ac", "2",
            "-b:a", "128k",
            "-shortest",
            str(norm_path),
        ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Normalize failed: {result.stderr[-300:]}")


def layer_vo_audio(clip_path, audio_path, output_path):
    """Mix V.O. audio onto a video clip. V.O. starts at beginning of clip."""
    cmd = [
        "ffmpeg", "-y",
        "-i", str(clip_path),
        "-i", str(audio_path),
        "-filter_complex",
        "[0:a][1:a]amix=inputs=2:duration=first:dropout_transition=2[a]",
        "-map", "0:v",
        "-map", "[a]",
        "-c:v", "copy",
        "-c:a", "aac",
        "-ar", "44100",
        "-ac", "2",
        "-b:a", "128k",
        str(output_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"V.O. layer failed: {result.stderr[-300:]}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Assemble table read v02 video")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--output", type=str, default=None, help="Override output path")
    args = parser.parse_args()

    output = Path(args.output) if args.output else OUTPUT

    with open(SHOT_LIST) as f:
        shot_list = yaml.safe_load(f)

    shots = shot_list["shots"]

    # Build clip list and identify V.O. needs
    clip_info = []
    missing = []
    total_dur = 0

    for s in shots:
        shot_num = s["shot"]
        shot_type = s["type"]
        clip_path = CLIPS_DIR / f"shot_{shot_num:02d}.mp4"
        dur = s["duration"]
        has_audio_text = bool(s.get("audio"))
        is_prod = shot_type in ("PROD_FRAME", "PROD_CLIP")

        # V.O. = PROD shot with audio text (layer at assembly, not baked in)
        needs_vo = is_prod and has_audio_text
        vo_wav = AUDIO_DIR / f"shot_{shot_num:02d}.wav" if needs_vo else None

        if clip_path.exists():
            clip_info.append({
                "shot": shot_num,
                "type": shot_type,
                "clip": clip_path,
                "duration": dur,
                "needs_vo": needs_vo,
                "vo_wav": vo_wav,
            })
            total_dur += dur
        else:
            missing.append(shot_num)

    if args.dry_run:
        vo_shots = [c for c in clip_info if c["needs_vo"]]
        vo_ready = [c for c in vo_shots if c["vo_wav"] and c["vo_wav"].exists()]
        print(f"[DRY RUN] Assembly plan:")
        print(f"  Shots: {len(shots)}")
        print(f"  Clips ready: {len(clip_info)}")
        print(f"  Missing: {len(missing)}")
        if missing:
            print(f"  Missing shots: {missing}")
        print(f"  V.O. layers needed: {len(vo_shots)} ({len(vo_ready)} WAVs ready)")
        for c in vo_shots:
            wav_ok = c["vo_wav"] and c["vo_wav"].exists()
            print(f"    Shot {c['shot']:2d}: {c['type']} {'[wav OK]' if wav_ok else '[NO WAV]'}")
        print(f"  Estimated duration: {total_dur}s ({total_dur//60}m {total_dur%60}s)")
        print(f"  + 2s black hold")
        print(f"  Output: {output}")
        sys.exit(0)

    if missing:
        print(f"WARNING: {len(missing)} clips missing: {missing}")
        print(f"Proceeding with {len(clip_info)} available clips.")

    if not clip_info:
        print("ERROR: No clips to assemble.")
        sys.exit(1)

    # Step 1: Normalize all clips + layer V.O. where needed
    print(f"\nStep 1: Normalizing {len(clip_info)} clips...")
    norm_dir = TABLE_READ / "clips_norm_v02"
    norm_dir.mkdir(parents=True, exist_ok=True)
    norm_paths = []

    for i, c in enumerate(clip_info):
        shot_num = c["shot"]
        clip = c["clip"]
        norm_path = norm_dir / clip.name

        if norm_path.exists():
            norm_paths.append(norm_path)
            continue

        has_audio = probe_has_audio(clip)

        # First normalize
        temp_norm = norm_dir / f"_temp_{clip.name}"
        try:
            normalize_clip(clip, temp_norm, has_audio)
        except RuntimeError as e:
            print(f"  WARN: Failed to normalize {clip.name}: {e}")
            continue

        # Layer V.O. if needed
        if c["needs_vo"] and c["vo_wav"] and c["vo_wav"].exists():
            try:
                layer_vo_audio(temp_norm, c["vo_wav"], norm_path)
                temp_norm.unlink(missing_ok=True)
                tag = "V.O."
            except RuntimeError as e:
                print(f"  WARN: V.O. layer failed for shot {shot_num}: {e}")
                temp_norm.rename(norm_path)
                tag = "no-vo"
        else:
            temp_norm.rename(norm_path)
            tag = "audio" if has_audio else "silent"
            if c["needs_vo"]:
                tag = "no-vo (wav missing)"

        norm_paths.append(norm_path)
        print(f"  [{i+1}/{len(clip_info)}] shot_{shot_num:02d}.mp4 [{tag}]")

    # Step 2: Generate 2s black hold
    print("\nStep 2: Generating black hold...")
    black_path = norm_dir / "black_hold.mp4"
    if not black_path.exists():
        cmd = [
            "ffmpeg", "-y",
            "-f", "lavfi",
            "-i", f"color=black:s={TARGET_W}x{TARGET_H}:r={FPS}:d=2",
            "-f", "lavfi",
            "-i", "anullsrc=r=44100:cl=stereo",
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-preset", "medium",
            "-crf", "18",
            "-c:a", "aac",
            "-ar", "44100",
            "-ac", "2",
            "-b:a", "128k",
            "-shortest",
            str(black_path),
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"  WARN: Failed to generate black hold: {result.stderr[-300:]}")
        else:
            print("  black_hold.mp4")
    norm_paths.append(black_path)

    # Step 3: Concat
    print(f"\nStep 3: Concatenating {len(norm_paths)} segments...")

    concat_file = TABLE_READ / "concat_list_v02.txt"
    with open(concat_file, "w") as f:
        for p in norm_paths:
            f.write(f"file '{p}'\n")

    output.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "ffmpeg", "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", str(concat_file),
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-preset", "medium",
        "-crf", "18",
        "-c:a", "aac",
        "-ar", "44100",
        "-ac", "2",
        "-b:a", "128k",
        str(output),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"ERROR: Concat failed: {result.stderr[-500:]}")
        sys.exit(1)

    # Get final duration
    probe_cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "csv=p=0",
        str(output),
    ]
    probe = subprocess.run(probe_cmd, capture_output=True, text=True)
    final_dur = float(probe.stdout.strip()) if probe.returncode == 0 else 0

    mb = output.stat().st_size / (1024 * 1024)
    print(f"\n{'=' * 70}")
    print(f"ASSEMBLED: {output.name}")
    print(f"  Duration: {final_dur:.1f}s ({final_dur/60:.0f}m {final_dur%60:.0f}s)")
    print(f"  Size: {mb:.1f} MB")
    print(f"  Clips: {len(norm_paths)} (including black hold)")
    print(f"  Path: {output}")
    print(f"{'=' * 70}")
