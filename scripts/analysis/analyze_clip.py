#!/usr/bin/env python3
"""
Unified clip analysis tool.

Runs all available analyses on a single clip, producing an analysis directory
with filmstrip, metadata, waveform, transcript, and summary.

Usage:
    python3 scripts/analysis/analyze_clip.py VIDEO_PATH
    python3 scripts/analysis/analyze_clip.py VIDEO_PATH --output analysis/my_clip/
    python3 scripts/analysis/analyze_clip.py VIDEO_PATH --quick
    python3 scripts/analysis/analyze_clip.py VIDEO_PATH --preflight
    python3 scripts/analysis/analyze_clip.py VIDEO_PATH --frames 16 --cols 4

Output structure:
    analysis/
      filmstrip.png        # N-frame grid with timecodes
      metadata.json        # Technical specs
      waveform.png         # Audio amplitude (if audio present)
      transcript.json      # Whisper STT (if --transcribe and ComfyUI available)
      color_palette.png    # Color palette visualization (unless --quick)
      color_palette.json   # Color data
      motion_chart.png     # Motion intensity timeline (unless --quick)
      motion.json          # Motion data
      summary.json         # Manifest of all artifacts
"""

import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.video_analysis import extract_filmstrip, probe_metadata, analyze_color_palette, analyze_motion
from lib.audio_analysis import generate_waveform, detect_silence, transcribe_audio


def analyze_clip(
    video_path: Path,
    output_dir: Path,
    frames: int = 12,
    cols: int = 4,
    quick: bool = False,
    transcribe: bool = False,
    comfyui_url: str = "http://127.0.0.1:8188",
    preflight: bool = False,
) -> dict:
    """
    Run all available analyses on a video clip.

    Args:
        video_path: Path to video file
        output_dir: Directory for output artifacts
        frames: Number of filmstrip frames
        cols: Filmstrip grid columns
        quick: If True, only filmstrip + metadata (skip color, motion, audio)
        transcribe: If True, run Whisper STT via ComfyUI
        comfyui_url: ComfyUI server URL for transcription
        preflight: If True, just show what would be done

    Returns:
        Summary dict with paths to all artifacts
    """
    video_path = Path(video_path)
    output_dir = Path(output_dir)

    if not video_path.exists():
        print(f"ERROR: File not found: {video_path}")
        sys.exit(1)

    print(f"\n{'='*60}")
    print(f"ANALYZE CLIP: {video_path.name}")
    print(f"Output: {output_dir}")
    print(f"{'='*60}")

    # ─── Preflight ────────────────────────────────────────────
    if preflight:
        meta = probe_metadata(video_path)
        if meta:
            print(f"\nVideo: {meta['file_name']}")
            print(f"Duration: {meta['duration_s']}s")
            if meta.get('video'):
                v = meta['video']
                print(f"Resolution: {v['width']}x{v['height']} @ {v['fps']}fps")
                print(f"Codec: {v['codec']}")
            print(f"Audio: {'Yes' if meta.get('audio') else 'No'}")
            print(f"Size: {meta['file_size_mb']}MB")

        print(f"\nAnalyses to run:")
        print(f"  [x] Filmstrip ({frames} frames, {cols} cols)")
        print(f"  [x] Metadata")
        if not quick:
            print(f"  [x] Color palette (8 samples)")
            print(f"  [x] Motion analysis (0.5s interval)")
        else:
            print(f"  [ ] Color palette (skipped: --quick)")
            print(f"  [ ] Motion analysis (skipped: --quick)")

        has_audio = meta and meta.get("audio")
        if has_audio:
            if not quick:
                print(f"  [x] Waveform")
                print(f"  [x] Silence detection")
            else:
                print(f"  [ ] Waveform (skipped: --quick)")
                print(f"  [ ] Silence detection (skipped: --quick)")
        else:
            print(f"  [ ] Waveform (no audio)")
            print(f"  [ ] Silence detection (no audio)")

        if transcribe:
            print(f"  [x] Whisper STT ({comfyui_url})")
        else:
            print(f"  [ ] Whisper STT (not requested)")

        print(f"\nOutput directory: {output_dir}")
        return {"preflight": True}

    # ─── Run analyses ─────────────────────────────────────────
    output_dir.mkdir(parents=True, exist_ok=True)
    start_time = time.time()
    summary = {
        "video": str(video_path),
        "video_name": video_path.name,
        "output_dir": str(output_dir),
        "artifacts": {},
    }

    # 1. Metadata (always)
    print(f"\n[1] Extracting metadata...")
    meta = probe_metadata(video_path)
    if meta:
        meta_path = output_dir / "metadata.json"
        with open(meta_path, "w") as f:
            json.dump(meta, f, indent=2)
        summary["metadata"] = meta
        summary["artifacts"]["metadata"] = str(meta_path)
        print(f"  Duration: {meta['duration_s']}s")
        if meta.get("video"):
            v = meta["video"]
            print(f"  Resolution: {v['width']}x{v['height']} @ {v['fps']}fps")
        print(f"  Audio: {'Yes' if meta.get('audio') else 'No'}")

    # 2. Filmstrip (always)
    print(f"\n[2] Extracting filmstrip ({frames} frames)...")
    filmstrip_data = extract_filmstrip(video_path, output_dir, n=frames, cols=cols)
    if filmstrip_data:
        summary["artifacts"]["filmstrip"] = filmstrip_data["filmstrip_path"]
        summary["filmstrip"] = filmstrip_data

    # 3. Color palette (unless --quick)
    if not quick:
        print(f"\n[3] Analyzing color palette...")
        color_data = analyze_color_palette(video_path, output_dir)
        if color_data:
            color_json_path = output_dir / "color_palette.json"
            with open(color_json_path, "w") as f:
                json.dump(color_data, f, indent=2)
            summary["artifacts"]["color_palette"] = color_data["palette_image"]
            summary["artifacts"]["color_palette_json"] = str(color_json_path)
            summary["color_palette"] = color_data

    # 4. Motion analysis (unless --quick)
    if not quick:
        print(f"\n[4] Analyzing motion intensity...")
        motion_data = analyze_motion(video_path, output_dir)
        if motion_data:
            motion_json_path = output_dir / "motion.json"
            with open(motion_json_path, "w") as f:
                json.dump(motion_data, f, indent=2)
            summary["artifacts"]["motion_chart"] = motion_data["chart_path"]
            summary["artifacts"]["motion_json"] = str(motion_json_path)
            summary["motion"] = motion_data

    # 5. Audio analyses
    has_audio = meta and meta.get("audio")
    if has_audio and not quick:
        print(f"\n[5] Generating waveform...")
        waveform_path = output_dir / "waveform.png"
        result = generate_waveform(video_path, waveform_path)
        if result:
            summary["artifacts"]["waveform"] = str(result)

        print(f"\n[6] Detecting silence regions...")
        silences = detect_silence(video_path)
        if silences is not None:
            silence_path = output_dir / "silence.json"
            with open(silence_path, "w") as f:
                json.dump(silences, f, indent=2)
            summary["artifacts"]["silence"] = str(silence_path)
            summary["silence_regions"] = silences
    elif not has_audio:
        print(f"\n[5-6] Skipping audio analysis (no audio track)")
    else:
        print(f"\n[5-6] Skipping audio analysis (--quick mode)")

    # 7. Whisper transcription (optional)
    if transcribe and has_audio:
        print(f"\n[7] Transcribing audio (Whisper STT)...")
        transcript = transcribe_audio(video_path, comfyui_url=comfyui_url)
        if transcript:
            transcript_path = output_dir / "transcript.json"
            with open(transcript_path, "w") as f:
                json.dump(transcript, f, indent=2)
            summary["artifacts"]["transcript"] = str(transcript_path)
            summary["transcript"] = transcript
    elif transcribe:
        print(f"\n[7] Skipping transcription (no audio track)")

    # ─── Summary ──────────────────────────────────────────────
    elapsed = round(time.time() - start_time, 1)
    summary["elapsed_s"] = elapsed
    summary["analysis_mode"] = "quick" if quick else "full"

    summary_path = output_dir / "summary.json"
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2, default=str)
    summary["artifacts"]["summary"] = str(summary_path)

    print(f"\n{'='*60}")
    print(f"ANALYSIS COMPLETE in {elapsed}s")
    print(f"Artifacts: {len(summary['artifacts'])} files in {output_dir}")
    for name, path in summary["artifacts"].items():
        print(f"  {name}: {Path(path).name}")
    print(f"{'='*60}\n")

    return summary


def main():
    parser = argparse.ArgumentParser(
        description="Analyze a video clip — produces filmstrip, metadata, and more."
    )
    parser.add_argument("video", type=Path, help="Path to video file")
    parser.add_argument("--output", "-o", type=Path, default=None,
                        help="Output directory (default: analysis/ next to video)")
    parser.add_argument("--frames", "-n", type=int, default=12,
                        help="Number of filmstrip frames (default: 12)")
    parser.add_argument("--cols", type=int, default=4,
                        help="Filmstrip grid columns (default: 4)")
    parser.add_argument("--quick", action="store_true",
                        help="Quick mode: filmstrip + metadata only")
    parser.add_argument("--transcribe", action="store_true",
                        help="Run Whisper STT (requires ComfyUI)")
    parser.add_argument("--comfyui-url", default="http://127.0.0.1:8188",
                        help="ComfyUI server URL")
    parser.add_argument("--preflight", action="store_true",
                        help="Show what would be done without running")

    args = parser.parse_args()

    # Default output directory: analysis/ next to the video
    if args.output is None:
        args.output = args.video.parent / "analysis" / args.video.stem

    analyze_clip(
        video_path=args.video,
        output_dir=args.output,
        frames=args.frames,
        cols=args.cols,
        quick=args.quick,
        transcribe=args.transcribe,
        comfyui_url=args.comfyui_url,
        preflight=args.preflight,
    )


if __name__ == "__main__":
    main()
