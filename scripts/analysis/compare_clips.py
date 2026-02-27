#!/usr/bin/env python3
"""
Side-by-side comparison of reference vs. generated clips.

Produces dual filmstrips, color palette comparison, motion intensity overlay,
and a structured diff report.

Usage:
    python3 scripts/analysis/compare_clips.py REFERENCE GENERATED
    python3 scripts/analysis/compare_clips.py REFERENCE GENERATED --output comparison/
    python3 scripts/analysis/compare_clips.py REFERENCE GENERATED --quick
    python3 scripts/analysis/compare_clips.py REFERENCE GENERATED --preflight

Output:
    comparison/
      dual_filmstrip.png     # Reference (top) vs generated (bottom)
      color_comparison.png   # Side-by-side color palettes
      motion_overlay.png     # Overlaid motion intensity timelines
      diff_report.json       # Structured comparison data
"""

import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.video_analysis import (
    extract_filmstrip, probe_metadata,
    analyze_color_palette, analyze_motion
)


def build_dual_filmstrip(
    ref_filmstrip_data: dict,
    gen_filmstrip_data: dict,
    output_path: Path,
) -> Path:
    """
    Create a dual filmstrip: reference on top, generated on bottom.
    """
    from PIL import Image, ImageDraw, ImageFont

    output_path = Path(output_path)

    ref_img = Image.open(ref_filmstrip_data["filmstrip_path"])
    gen_img = Image.open(gen_filmstrip_data["filmstrip_path"])

    # Match widths
    target_w = max(ref_img.width, gen_img.width)
    if ref_img.width != target_w:
        ratio = target_w / ref_img.width
        ref_img = ref_img.resize((target_w, int(ref_img.height * ratio)), Image.LANCZOS)
    if gen_img.width != target_w:
        ratio = target_w / gen_img.width
        gen_img = gen_img.resize((target_w, int(gen_img.height * ratio)), Image.LANCZOS)

    # Build canvas
    label_h = 30
    gap = 8
    total_h = label_h + ref_img.height + gap + label_h + gen_img.height + 8

    canvas = Image.new("RGB", (target_w, total_h), (20, 20, 20))
    draw = ImageDraw.Draw(canvas)

    try:
        font = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 14)
    except (IOError, OSError):
        font = ImageFont.load_default()

    # Reference label + filmstrip
    ref_dur = ref_filmstrip_data.get("duration_s", "?")
    draw.text((8, 6), f"REFERENCE ({ref_dur}s)", fill=(100, 255, 100), font=font)
    canvas.paste(ref_img, (0, label_h))

    # Generated label + filmstrip
    gen_dur = gen_filmstrip_data.get("duration_s", "?")
    gen_y = label_h + ref_img.height + gap
    draw.text((8, gen_y + 6), f"GENERATED ({gen_dur}s)", fill=(100, 180, 255), font=font)
    canvas.paste(gen_img, (0, gen_y + label_h))

    canvas.save(output_path, "PNG")
    return output_path


def build_motion_overlay(
    ref_motion: dict,
    gen_motion: dict,
    output_path: Path,
) -> Path:
    """Create overlaid motion intensity chart for both clips."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(12, 4))

    ref_times = [s["timecode_s"] for s in ref_motion["samples"]]
    ref_energy = [s["energy"] for s in ref_motion["samples"]]
    gen_times = [s["timecode_s"] for s in gen_motion["samples"]]
    gen_energy = [s["energy"] for s in gen_motion["samples"]]

    ax.fill_between(ref_times, ref_energy, alpha=0.3, color="#69db7c", label="Reference")
    ax.plot(ref_times, ref_energy, color="#69db7c", linewidth=1.5)
    ax.fill_between(gen_times, gen_energy, alpha=0.3, color="#74c0fc", label="Generated")
    ax.plot(gen_times, gen_energy, color="#74c0fc", linewidth=1.5)

    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Motion Energy")
    ax.set_title("Motion Intensity Comparison")
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()

    fig.savefig(str(output_path), dpi=150)
    plt.close(fig)
    return output_path


def build_color_comparison(
    ref_color: dict,
    gen_color: dict,
    output_path: Path,
) -> Path:
    """Create side-by-side color palette comparison."""
    from PIL import Image, ImageDraw, ImageFont

    ref_img = Image.open(ref_color["palette_image"])
    gen_img = Image.open(gen_color["palette_image"])

    # Stack vertically with labels
    target_w = max(ref_img.width, gen_img.width)
    label_h = 26
    gap = 8
    total_h = label_h + ref_img.height + gap + label_h + gen_img.height + 8

    canvas = Image.new("RGB", (target_w, total_h), (20, 20, 20))
    draw = ImageDraw.Draw(canvas)

    try:
        font = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 12)
    except (IOError, OSError):
        font = ImageFont.load_default()

    ref_temp = ref_color.get("overall_temperature", "?")
    draw.text((8, 4), f"REFERENCE (temp: {ref_temp})", fill=(100, 255, 100), font=font)
    canvas.paste(ref_img, (0, label_h))

    gen_temp = gen_color.get("overall_temperature", "?")
    gen_y = label_h + ref_img.height + gap
    draw.text((8, gen_y + 4), f"GENERATED (temp: {gen_temp})", fill=(100, 180, 255), font=font)
    canvas.paste(gen_img, (0, gen_y + label_h))

    canvas.save(output_path, "PNG")
    return output_path


def compare_clips(
    ref_path: Path,
    gen_path: Path,
    output_dir: Path,
    frames: int = 12,
    quick: bool = False,
    preflight: bool = False,
) -> dict:
    """
    Run side-by-side comparison of reference vs. generated clip.

    Returns summary dict with all comparison artifacts.
    """
    ref_path = Path(ref_path)
    gen_path = Path(gen_path)
    output_dir = Path(output_dir)

    for p, label in [(ref_path, "Reference"), (gen_path, "Generated")]:
        if not p.exists():
            print(f"ERROR: {label} file not found: {p}")
            sys.exit(1)

    # Preflight
    if preflight:
        ref_meta = probe_metadata(ref_path)
        gen_meta = probe_metadata(gen_path)
        print(f"\n{'='*60}")
        print(f"COMPARE CLIPS — PREFLIGHT")
        print(f"{'='*60}")
        print(f"Reference: {ref_path.name} ({ref_meta['duration_s']}s, "
              f"{ref_meta['video']['width']}x{ref_meta['video']['height']})")
        print(f"Generated: {gen_path.name} ({gen_meta['duration_s']}s, "
              f"{gen_meta['video']['width']}x{gen_meta['video']['height']})")
        print(f"Duration diff: {abs(ref_meta['duration_s'] - gen_meta['duration_s']):.1f}s")
        mode = "quick (filmstrip only)" if quick else "full (filmstrip + color + motion)"
        print(f"Mode: {mode}")
        print(f"Output: {output_dir}")
        return {"preflight": True}

    output_dir.mkdir(parents=True, exist_ok=True)
    start_time = time.time()
    summary = {"artifacts": {}}

    print(f"\n{'='*60}")
    print(f"COMPARE CLIPS")
    print(f"  Reference: {ref_path.name}")
    print(f"  Generated: {gen_path.name}")
    print(f"{'='*60}")

    # Metadata
    ref_meta = probe_metadata(ref_path)
    gen_meta = probe_metadata(gen_path)
    summary["reference"] = {"file": str(ref_path), "duration_s": ref_meta["duration_s"]}
    summary["generated"] = {"file": str(gen_path), "duration_s": gen_meta["duration_s"]}
    summary["duration_diff_s"] = round(abs(ref_meta["duration_s"] - gen_meta["duration_s"]), 2)

    # Filmstrips
    print(f"\n[1] Extracting filmstrips...")
    ref_dir = output_dir / "ref"
    gen_dir = output_dir / "gen"
    ref_film = extract_filmstrip(ref_path, ref_dir, n=frames)
    gen_film = extract_filmstrip(gen_path, gen_dir, n=frames)

    if ref_film and gen_film:
        dual_path = output_dir / "dual_filmstrip.png"
        build_dual_filmstrip(ref_film, gen_film, dual_path)
        summary["artifacts"]["dual_filmstrip"] = str(dual_path)
        print(f"  Dual filmstrip: {dual_path}")

    if not quick:
        # Color palette comparison
        print(f"\n[2] Comparing color palettes...")
        ref_color = analyze_color_palette(ref_path, ref_dir)
        gen_color = analyze_color_palette(gen_path, gen_dir)
        if ref_color and gen_color:
            color_path = output_dir / "color_comparison.png"
            build_color_comparison(ref_color, gen_color, color_path)
            summary["artifacts"]["color_comparison"] = str(color_path)
            summary["color_diff"] = {
                "ref_temperature": ref_color.get("overall_temperature"),
                "gen_temperature": gen_color.get("overall_temperature"),
                "match": ref_color.get("overall_temperature") == gen_color.get("overall_temperature"),
            }

        # Motion comparison
        print(f"\n[3] Comparing motion intensity...")
        ref_motion = analyze_motion(ref_path, ref_dir)
        gen_motion = analyze_motion(gen_path, gen_dir)
        if ref_motion and gen_motion:
            motion_path = output_dir / "motion_overlay.png"
            build_motion_overlay(ref_motion, gen_motion, motion_path)
            summary["artifacts"]["motion_overlay"] = str(motion_path)
            summary["motion_diff"] = {
                "ref_mean_energy": ref_motion["stats"]["mean_energy"],
                "gen_mean_energy": gen_motion["stats"]["mean_energy"],
                "energy_ratio": round(
                    gen_motion["stats"]["mean_energy"] /
                    max(ref_motion["stats"]["mean_energy"], 0.01), 2
                ),
            }

    elapsed = round(time.time() - start_time, 1)
    summary["elapsed_s"] = elapsed

    # Save report
    report_path = output_dir / "diff_report.json"
    with open(report_path, "w") as f:
        json.dump(summary, f, indent=2)
    summary["artifacts"]["diff_report"] = str(report_path)

    print(f"\n{'='*60}")
    print(f"COMPARISON COMPLETE in {elapsed}s")
    print(f"Duration: ref={ref_meta['duration_s']}s, gen={gen_meta['duration_s']}s "
          f"(diff: {summary['duration_diff_s']}s)")
    for name, path in summary["artifacts"].items():
        print(f"  {name}: {Path(path).name}")
    print(f"{'='*60}\n")

    return summary


def main():
    parser = argparse.ArgumentParser(
        description="Side-by-side comparison of reference vs. generated clips."
    )
    parser.add_argument("reference", type=Path, help="Reference video file")
    parser.add_argument("generated", type=Path, help="Generated video file")
    parser.add_argument("--output", "-o", type=Path, default=None,
                        help="Output directory")
    parser.add_argument("--frames", "-n", type=int, default=12,
                        help="Filmstrip frames (default: 12)")
    parser.add_argument("--quick", action="store_true",
                        help="Quick mode: filmstrip comparison only")
    parser.add_argument("--preflight", action="store_true",
                        help="Show what would be done")

    args = parser.parse_args()

    if args.output is None:
        args.output = args.reference.parent / "comparison"

    compare_clips(
        ref_path=args.reference,
        gen_path=args.generated,
        output_dir=args.output,
        frames=args.frames,
        quick=args.quick,
        preflight=args.preflight,
    )


if __name__ == "__main__":
    main()
