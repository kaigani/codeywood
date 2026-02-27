"""
Scene/cut detection for video analysis.

Detects hard cuts in video by analyzing frame-to-frame differences,
produces shot breakdowns with timecodes and first-frame thumbnails.
"""

import json
import subprocess
from pathlib import Path
from typing import Dict, List, Optional


def detect_cuts(
    video_path: Path,
    threshold: float = 0.3,
) -> Optional[List[Dict]]:
    """
    Detect hard cuts in a video using ffmpeg's scene detection filter.

    Args:
        video_path: Path to video file
        threshold: Scene change threshold (0.0-1.0, lower = more sensitive)

    Returns:
        List of dicts with cut_timecode_s, shot_number, shot_duration_s,
        or None on failure.
    """
    video_path = Path(video_path)
    if not video_path.exists():
        print(f"File not found: {video_path}")
        return None

    # Get duration first
    from scripts.lib.video_analysis import probe_metadata
    meta = probe_metadata(video_path)
    if not meta:
        return None
    duration = meta["duration_s"]

    # Use ffmpeg scene detection
    cmd = [
        "ffmpeg", "-i", str(video_path),
        "-vf", f"select='gt(scene,{threshold})',showinfo",
        "-f", "null", "-"
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    # Parse cut points from showinfo output in stderr
    import re
    cuts = [0.0]  # First shot always starts at 0

    for line in result.stderr.split("\n"):
        # Look for pts_time in showinfo output
        match = re.search(r"pts_time:\s*([\d.]+)", line)
        if match:
            t = float(match.group(1))
            # Avoid duplicate/very-close cuts
            if t - cuts[-1] > 0.2:
                cuts.append(t)

    # Build shot list
    shots = []
    for i in range(len(cuts)):
        start = cuts[i]
        end = cuts[i + 1] if i + 1 < len(cuts) else duration

        shots.append({
            "shot_number": i + 1,
            "start_s": round(start, 3),
            "end_s": round(end, 3),
            "duration_s": round(end - start, 3),
        })

    # Classify pacing
    if shots:
        avg_dur = sum(s["duration_s"] for s in shots) / len(shots)
        for s in shots:
            if s["duration_s"] < avg_dur * 0.5:
                s["pacing"] = "fast"
            elif s["duration_s"] > avg_dur * 1.5:
                s["pacing"] = "slow"
            else:
                s["pacing"] = "normal"

    print(f"  Detected {len(cuts)} cuts → {len(shots)} shots")
    return shots


def shot_breakdown(
    video_path: Path,
    output_dir: Path,
    threshold: float = 0.3,
    thumb_width: int = 320,
) -> Optional[Dict]:
    """
    Full shot breakdown: detect cuts, extract first frame of each shot,
    produce annotated filmstrip and structured data.

    Args:
        video_path: Path to video file
        output_dir: Directory for output files
        threshold: Scene detection threshold
        thumb_width: Width of thumbnails

    Returns:
        Dict with breakdown data and artifact paths, or None on failure.
    """
    from PIL import Image, ImageDraw, ImageFont
    from scripts.lib.video_analysis import extract_frame_at, probe_metadata, _format_timecode

    video_path = Path(video_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Detect cuts
    shots = detect_cuts(video_path, threshold=threshold)
    if not shots:
        return None

    meta = probe_metadata(video_path)
    if not meta:
        return None

    # Extract first frame of each shot
    frames_dir = output_dir / "shot_frames"
    frames_dir.mkdir(exist_ok=True)

    frame_images = []
    for shot in shots:
        # Extract slightly after cut to avoid transition artifacts
        ts = shot["start_s"] + 0.1
        frame_path = frames_dir / f"shot_{shot['shot_number']:03d}.png"
        result = extract_frame_at(video_path, ts, frame_path)
        if result:
            img = Image.open(frame_path)
            frame_images.append((img, shot))
            shot["frame_path"] = str(frame_path)

    # Build annotated filmstrip
    if frame_images:
        cols = min(4, len(frame_images))
        orig_w, orig_h = frame_images[0][0].size
        thumb_height = int(thumb_width * orig_h / orig_w)
        label_height = 36
        padding = 4
        rows = (len(frame_images) + cols - 1) // cols

        grid_w = cols * (thumb_width + padding) + padding
        grid_h = rows * (thumb_height + label_height + padding) + padding

        canvas = Image.new("RGB", (grid_w, grid_h), (20, 20, 20))
        draw = ImageDraw.Draw(canvas)

        try:
            font = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 11)
        except (IOError, OSError):
            font = ImageFont.load_default()

        for i, (img, shot) in enumerate(frame_images):
            row = i // cols
            col = i % cols
            x = padding + col * (thumb_width + padding)
            y = padding + row * (thumb_height + label_height + padding)

            thumb = img.resize((thumb_width, thumb_height), Image.LANCZOS)
            canvas.paste(thumb, (x, y))

            # Label with shot number, timecode, duration
            tc = _format_timecode(shot["start_s"])
            label = f"Shot {shot['shot_number']} | {tc} | {shot['duration_s']:.1f}s"
            draw.rectangle(
                [x, y + thumb_height, x + thumb_width, y + thumb_height + label_height],
                fill=(40, 40, 40)
            )
            draw.text((x + 4, y + thumb_height + 4), label, fill=(200, 200, 200), font=font)

            # Color-code pacing
            pacing_colors = {"fast": "#ff6b6b", "normal": "#69db7c", "slow": "#74c0fc"}
            pace_color = pacing_colors.get(shot.get("pacing", "normal"), "#69db7c")
            draw.rectangle(
                [x + thumb_width - 8, y, x + thumb_width, y + 8],
                fill=pace_color
            )

        filmstrip_path = output_dir / "shot_breakdown.png"
        canvas.save(filmstrip_path, "PNG")
        print(f"  Shot breakdown filmstrip: {filmstrip_path}")

    # Save breakdown data
    breakdown = {
        "video": str(video_path),
        "duration_s": meta["duration_s"],
        "total_shots": len(shots),
        "avg_shot_duration_s": round(
            sum(s["duration_s"] for s in shots) / len(shots), 2
        ) if shots else 0,
        "shots": shots,
        "filmstrip_path": str(output_dir / "shot_breakdown.png"),
    }

    breakdown_path = output_dir / "breakdown.json"
    with open(breakdown_path, "w") as f:
        json.dump(breakdown, f, indent=2)

    print(f"  Breakdown data: {breakdown_path}")
    print(f"  {len(shots)} shots, avg {breakdown['avg_shot_duration_s']}s/shot")

    return breakdown
