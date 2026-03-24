#!/usr/bin/env python3
"""
EP01 v03 "Handler" — Final Assembly

Assembles all 25 clips into final episode video:
1. Clips without VO: pass through as-is
2. Clips with VO: mix dialogue at specified offsets
3. Shot 12: freeze-extend last frame to fit 8.4s intel VO
4. Concatenate all clips in order
5. Output: EP01_v03_handler.mp4

Audio mixing:
  - Shot 12: VOICE intel (0.3s) + VOICE tabs (after intel ends)
  - Shot 13: VOICE "No." at 1.5s
  - Shot 14: VOICE "You knew..." at 3.9s
  - Shot 15: VOICE "Go." at 4.0s
"""

import subprocess
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[2] / "projects" / "stray-signal"
CLIPS_DIR = PROJECT / "PRODUCTION" / "EP01_v03" / "clips"
VO_DIR = PROJECT / "PRODUCTION" / "EP01_v03" / "voiceover"
STAGING = PROJECT / "PRODUCTION" / "EP01_v03" / "assembly"
OUTPUT = PROJECT / "PRODUCTION" / "EP01_v03" / "EP01_v03_handler.mp4"


def run(cmd, desc=""):
    """Run ffmpeg command, raise on failure."""
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  FAILED: {desc}")
        print(result.stderr[-500:] if result.stderr else "no stderr")
        raise RuntimeError(f"ffmpeg failed: {desc}")
    return result


def get_duration(path):
    """Get duration of a media file in seconds."""
    r = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
         "-of", "csv=p=0", str(path)],
        capture_output=True, text=True
    )
    return float(r.stdout.strip())


def normalize_clip(src, dst):
    """Re-encode clip to consistent format for concat."""
    run([
        "ffmpeg", "-y", "-i", str(src),
        "-c:v", "libx264", "-preset", "fast", "-crf", "18",
        "-vf", "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2",
        "-r", "25",
        "-c:a", "aac", "-b:a", "128k", "-ar", "44100", "-ac", "2",
        "-shortest",
        str(dst),
    ], f"normalize {src.name}")


def freeze_extend(src, dst, target_duration):
    """Extend a clip by freezing the last frame."""
    clip_dur = get_duration(src)
    if clip_dur >= target_duration:
        normalize_clip(src, dst)
        return

    run([
        "ffmpeg", "-y", "-i", str(src),
        "-c:v", "libx264", "-preset", "fast", "-crf", "18",
        "-vf", (
            f"scale=1920:1080:force_original_aspect_ratio=decrease,"
            f"pad=1920:1080:(ow-iw)/2:(oh-ih)/2,"
            f"tpad=stop_mode=clone:stop_duration={target_duration - clip_dur:.2f}"
        ),
        "-r", "25",
        "-c:a", "aac", "-b:a", "128k", "-ar", "44100", "-ac", "2",
        "-t", f"{target_duration:.2f}",
        str(dst),
    ], f"freeze-extend {src.name} to {target_duration:.1f}s")


def mix_vo(clip_src, vo_specs, dst):
    """Mix one or more VO files into a clip at specified offsets.

    vo_specs: list of (vo_path, offset_seconds)
    """
    # Build ffmpeg command with adelay for each VO
    inputs = ["-i", str(clip_src)]
    for vo_path, _ in vo_specs:
        inputs.extend(["-i", str(vo_path)])

    # Build filter graph
    # [0:a] is the clip's native audio
    # [1:a], [2:a], ... are the VO tracks
    filters = []
    mix_inputs = []

    # Native audio pass-through
    mix_inputs.append("[0:a]")

    for i, (vo_path, offset_ms) in enumerate(vo_specs, 1):
        delay_ms = int(offset_ms * 1000)
        # Delay VO and convert to stereo 44100Hz
        filters.append(
            f"[{i}:a]aresample=44100,aformat=sample_fmts=fltp:channel_layouts=stereo,"
            f"adelay={delay_ms}|{delay_ms}[vo{i}]"
        )
        mix_inputs.append(f"[vo{i}]")

    # Mix all audio streams
    n_inputs = len(mix_inputs)
    mix_str = "".join(mix_inputs)
    filters.append(
        f"{mix_str}amix=inputs={n_inputs}:duration=longest:dropout_transition=0[mixed]"
    )

    filter_complex = ";".join(filters)

    run([
        "ffmpeg", "-y",
        *inputs,
        "-filter_complex", filter_complex,
        "-map", "0:v",
        "-map", "[mixed]",
        "-c:v", "libx264", "-preset", "fast", "-crf", "18",
        "-vf", "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2",
        "-r", "25",
        "-c:a", "aac", "-b:a", "128k", "-ar", "44100", "-ac", "2",
        "-shortest",
        str(dst),
    ], f"mix VO into {clip_src.name}")


# ---------------------------------------------------------------------------
# Shot order and VO mapping
# ---------------------------------------------------------------------------
SHOT_ORDER = [
    "01_cityscape_dawn",
    "02_neda_on_grid",
    "03_neda_at_grate",
    "04_the_drop",
    "05_title_card",
    "06_descent_cold",
    "07_descent_transition",
    "08_descent_warm",
    "09_corridor_approach",
    "10_fens_room",
    "11_neda_walks_on",
    "12_briefing_intel",
    "13_briefing_volunteer",
    "14_briefing_argument",
    "15_briefing_silence",
    "16_return_warm",
    "17_return_transition",
    "18_return_surface",
    "19_grid_mission",
    "20_corridor_empty",
    "21_kai_approaches",
    "22_kai_glow_detail",
    "23_neda_watching",
    "24_neda_moves_forward",
    "25_black_hold",
]

# VO mixing specs: shot_name -> [(vo_file, offset_seconds)]
VO_MIX = {
    "12_briefing_intel": [
        ("vo_12_voice_intel_v2.wav", 0.3),
    ],
    "13_briefing_volunteer": [
        ("vo_13_voice_no.wav", 1.5),
    ],
    "14_briefing_argument": [
        ("vo_14_voice_knife_v2.wav", 3.9),
    ],
    "15_briefing_silence": [
        ("vo_15_voice_go.wav", 4.0),
    ],
}

# Shot 12 needs freeze-extension to fit the ~8.7s of VO
FREEZE_EXTEND = {
    "12_briefing_intel": 9.5,  # extend from 6s to 9.5s
}


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Assemble EP01 v03")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    STAGING.mkdir(parents=True, exist_ok=True)

    # Verify all source clips exist
    missing = []
    for name in SHOT_ORDER:
        clip = CLIPS_DIR / f"{name}.mp4"
        if not clip.exists():
            missing.append(name)
    if missing:
        print(f"ERROR: Missing clips: {', '.join(missing)}")
        sys.exit(1)

    # Verify all VO files exist
    for name, specs in VO_MIX.items():
        for vo_file, _ in specs:
            vo = VO_DIR / vo_file
            if not vo.exists():
                missing.append(f"{name}: {vo_file}")
    if missing:
        print(f"ERROR: Missing VO: {', '.join(missing)}")
        sys.exit(1)

    if args.dry_run:
        print("=" * 70)
        print("EP01 v03 Assembly — DRY RUN")
        print("=" * 70)
        total_dur = 0
        for name in SHOT_ORDER:
            clip = CLIPS_DIR / f"{name}.mp4"
            dur = get_duration(clip)
            ext = FREEZE_EXTEND.get(name)
            vo = VO_MIX.get(name)
            notes = []
            if ext:
                notes.append(f"freeze-extend to {ext}s")
                dur = ext
            if vo:
                vo_descs = [f"{v[0]} @ {v[1]}s" for v in vo]
                notes.append(f"VO: {', '.join(vo_descs)}")
            total_dur += dur
            note_str = f" — {'; '.join(notes)}" if notes else ""
            print(f"  {name} ({dur:.1f}s){note_str}")
        print(f"\nTotal: {total_dur:.1f}s ({total_dur/60:.1f}min)")
        print(f"Output: {OUTPUT}")
        sys.exit(0)

    print("=" * 70)
    print("EP01 v03 — Assembly")
    print("=" * 70)

    staged_clips = []

    for i, name in enumerate(SHOT_ORDER, 1):
        clip_src = CLIPS_DIR / f"{name}.mp4"
        staged = STAGING / f"{i:02d}_{name}.mp4"
        staged_clips.append(staged)

        print(f"\n[{i}/{len(SHOT_ORDER)}] {name}")

        has_extend = name in FREEZE_EXTEND
        has_vo = name in VO_MIX

        if has_extend and has_vo:
            # First freeze-extend, then mix VO
            temp = STAGING / f"{name}_extended.mp4"
            print(f"  Freeze-extend to {FREEZE_EXTEND[name]}s")
            freeze_extend(clip_src, temp, FREEZE_EXTEND[name])
            vo_specs = [(VO_DIR / vf, offset) for vf, offset in VO_MIX[name]]
            print(f"  Mix {len(vo_specs)} VO track(s)")
            mix_vo(temp, vo_specs, staged)
            temp.unlink(missing_ok=True)

        elif has_vo:
            vo_specs = [(VO_DIR / vf, offset) for vf, offset in VO_MIX[name]]
            print(f"  Mix {len(vo_specs)} VO track(s)")
            mix_vo(clip_src, vo_specs, staged)

        elif has_extend:
            print(f"  Freeze-extend to {FREEZE_EXTEND[name]}s")
            freeze_extend(clip_src, staged, FREEZE_EXTEND[name])

        else:
            print(f"  Normalize")
            normalize_clip(clip_src, staged)

    # Build concat list
    concat_list = STAGING / "concat.txt"
    with open(concat_list, "w") as f:
        for staged in staged_clips:
            f.write(f"file '{staged}'\n")

    # Final concat
    print(f"\n{'=' * 70}")
    print("Concatenating...")
    run([
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0",
        "-i", str(concat_list),
        "-c:v", "libx264", "-preset", "slow", "-crf", "18",
        "-c:a", "aac", "-b:a", "192k",
        str(OUTPUT),
    ], "final concat")

    final_dur = get_duration(OUTPUT)
    size_mb = OUTPUT.stat().st_size / (1024 * 1024)
    print(f"\nSaved: {OUTPUT.name}")
    print(f"Duration: {final_dur:.1f}s ({final_dur/60:.1f}min)")
    print(f"Size: {size_mb:.1f} MB")
    print("=" * 70)
    print("ASSEMBLY COMPLETE")
    print("=" * 70)
