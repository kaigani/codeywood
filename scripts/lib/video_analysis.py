"""
Video analysis utilities for Claude's proxy vision.

Transforms black-box video files into visual artifacts (filmstrips, color palettes,
motion charts) and structured data (JSON) that Claude can read and reason about.
"""

import json
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple


def probe_metadata(video_path: Path) -> Optional[Dict]:
    """
    Extract comprehensive metadata from a video file using ffprobe.

    Returns dict with: duration, fps, resolution, codecs, file_size, audio info.
    """
    video_path = Path(video_path)
    if not video_path.exists():
        print(f"File not found: {video_path}")
        return None

    cmd = [
        "ffprobe", "-v", "quiet",
        "-print_format", "json",
        "-show_format", "-show_streams",
        str(video_path)
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"ffprobe failed: {result.stderr[:300]}")
        return None

    probe = json.loads(result.stdout)
    fmt = probe.get("format", {})
    streams = probe.get("streams", [])

    # Find video and audio streams
    video_stream = next((s for s in streams if s.get("codec_type") == "video"), None)
    audio_stream = next((s for s in streams if s.get("codec_type") == "audio"), None)

    metadata = {
        "file": str(video_path),
        "file_name": video_path.name,
        "file_size_bytes": int(fmt.get("size", 0)),
        "file_size_mb": round(int(fmt.get("size", 0)) / (1024 * 1024), 2),
        "duration_s": round(float(fmt.get("duration", 0)), 2),
        "format": fmt.get("format_long_name", "unknown"),
        "bit_rate_kbps": round(int(fmt.get("bit_rate", 0)) / 1000),
    }

    if video_stream:
        # Parse fps from r_frame_rate (e.g., "24000/1001" or "25/1")
        fps_str = video_stream.get("r_frame_rate", "0/1")
        try:
            num, den = fps_str.split("/")
            fps = round(int(num) / int(den), 2)
        except (ValueError, ZeroDivisionError):
            fps = 0

        metadata["video"] = {
            "codec": video_stream.get("codec_name", "unknown"),
            "width": int(video_stream.get("width", 0)),
            "height": int(video_stream.get("height", 0)),
            "fps": fps,
            "total_frames": int(video_stream.get("nb_frames", 0)),
            "pix_fmt": video_stream.get("pix_fmt", "unknown"),
        }

    if audio_stream:
        metadata["audio"] = {
            "codec": audio_stream.get("codec_name", "unknown"),
            "sample_rate": int(audio_stream.get("sample_rate", 0)),
            "channels": int(audio_stream.get("channels", 0)),
            "channel_layout": audio_stream.get("channel_layout", "unknown"),
        }
    else:
        metadata["audio"] = None

    return metadata


def extract_frame_at(video_path: Path, timecode_s: float, output_path: Path) -> Optional[Path]:
    """
    Extract a single frame at a specific timecode.

    Args:
        video_path: Path to video file
        timecode_s: Time in seconds
        output_path: Path for output PNG

    Returns:
        Path to extracted frame, or None on failure
    """
    video_path = Path(video_path)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        "ffmpeg", "-y",
        "-ss", str(timecode_s),
        "-i", str(video_path),
        "-frames:v", "1",
        "-q:v", "2",
        str(output_path)
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0 and output_path.exists():
        return output_path
    return None


def extract_filmstrip(
    video_path: Path,
    output_dir: Path,
    n: int = 12,
    cols: int = 4,
    thumb_width: int = 320,
) -> Optional[Dict]:
    """
    Extract N evenly-spaced frames from a video and composite into an annotated grid.

    The filmstrip is the keystone perception tool — it transforms a video into
    an image Claude can read and reason about.

    Args:
        video_path: Path to video file
        output_dir: Directory for output files
        n: Number of frames to extract (default 12)
        cols: Number of columns in the grid (default 4)
        thumb_width: Width of each thumbnail in pixels

    Returns:
        Dict with 'filmstrip_path' (PNG) and 'frames' (list of frame metadata),
        or None on failure.
    """
    from PIL import Image, ImageDraw, ImageFont

    video_path = Path(video_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Get video metadata for duration and resolution
    meta = probe_metadata(video_path)
    if not meta or meta["duration_s"] <= 0:
        print(f"Cannot extract filmstrip: invalid video or zero duration")
        return None

    duration = meta["duration_s"]
    # Space frames evenly, avoiding the very first and last moments
    margin = min(0.2, duration * 0.02)
    timestamps = [
        margin + (duration - 2 * margin) * i / max(n - 1, 1)
        for i in range(n)
    ]

    # Extract individual frames
    frames_info = []
    frame_images = []
    tmp_dir = output_dir / "_frames_tmp"
    tmp_dir.mkdir(exist_ok=True)

    for i, ts in enumerate(timestamps):
        frame_path = tmp_dir / f"frame_{i:03d}.png"
        result = extract_frame_at(video_path, ts, frame_path)
        if result and frame_path.exists():
            img = Image.open(frame_path)
            frame_images.append(img)
            frames_info.append({
                "index": i,
                "timecode_s": round(ts, 2),
                "timecode_fmt": _format_timecode(ts),
                "path": str(frame_path),
            })
        else:
            print(f"  Warning: failed to extract frame at {ts:.2f}s")

    if not frame_images:
        print("No frames extracted")
        return None

    # Calculate thumbnail size maintaining aspect ratio
    orig_w, orig_h = frame_images[0].size
    thumb_height = int(thumb_width * orig_h / orig_w)

    # Build the grid
    rows = (len(frame_images) + cols - 1) // cols
    label_height = 24
    padding = 4
    grid_width = cols * (thumb_width + padding) + padding
    grid_height = rows * (thumb_height + label_height + padding) + padding

    canvas = Image.new("RGB", (grid_width, grid_height), (20, 20, 20))
    draw = ImageDraw.Draw(canvas)

    # Try to load a monospace font, fall back to default
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 13)
    except (IOError, OSError):
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 13)
        except (IOError, OSError):
            font = ImageFont.load_default()

    for i, (img, info) in enumerate(zip(frame_images, frames_info)):
        row = i // cols
        col = i % cols
        x = padding + col * (thumb_width + padding)
        y = padding + row * (thumb_height + label_height + padding)

        # Resize and paste frame
        thumb = img.resize((thumb_width, thumb_height), Image.LANCZOS)
        canvas.paste(thumb, (x, y))

        # Draw timecode label below frame
        label = f"[{i+1:02d}] {info['timecode_fmt']}"
        draw.rectangle(
            [x, y + thumb_height, x + thumb_width, y + thumb_height + label_height],
            fill=(40, 40, 40)
        )
        draw.text((x + 6, y + thumb_height + 4), label, fill=(200, 200, 200), font=font)

    # Save filmstrip
    filmstrip_path = output_dir / "filmstrip.png"
    canvas.save(filmstrip_path, "PNG")
    print(f"  Filmstrip saved: {filmstrip_path} ({len(frame_images)} frames)")

    # Clean up temp frames
    for f in tmp_dir.glob("*.png"):
        f.unlink()
    tmp_dir.rmdir()

    # Save frame metadata
    result_data = {
        "video": str(video_path),
        "duration_s": duration,
        "frame_count": len(frame_images),
        "grid": {"rows": rows, "cols": cols},
        "filmstrip_path": str(filmstrip_path),
        "frames": frames_info,
    }

    return result_data


def analyze_color_palette(
    video_path: Path,
    output_dir: Path,
    samples: int = 8,
    colors_per_sample: int = 5,
) -> Optional[Dict]:
    """
    Extract dominant color palettes from sampled frames across the video.

    Produces a PNG showing frame thumbnails with their dominant color swatches
    and a JSON with hex values, temperature classification, and contrast metrics.

    Args:
        video_path: Path to video file
        output_dir: Directory for output files
        samples: Number of frames to sample
        colors_per_sample: Dominant colors per frame

    Returns:
        Dict with palette data and path to visualization PNG, or None on failure.
    """
    from PIL import Image, ImageDraw, ImageFont
    import numpy as np

    video_path = Path(video_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    meta = probe_metadata(video_path)
    if not meta or meta["duration_s"] <= 0:
        return None

    duration = meta["duration_s"]
    margin = min(0.2, duration * 0.02)
    timestamps = [
        margin + (duration - 2 * margin) * i / max(samples - 1, 1)
        for i in range(samples)
    ]

    # Extract and analyze frames
    sample_data = []
    frame_images = []
    tmp_dir = output_dir / "_color_tmp"
    tmp_dir.mkdir(exist_ok=True)

    for i, ts in enumerate(timestamps):
        frame_path = tmp_dir / f"color_frame_{i:03d}.png"
        result = extract_frame_at(video_path, ts, frame_path)
        if not result:
            continue

        img = Image.open(frame_path).convert("RGB")
        frame_images.append((img, ts))

        # Quantize to find dominant colors
        small = img.resize((64, 64), Image.LANCZOS)
        pixels = np.array(small).reshape(-1, 3)
        colors = _kmeans_colors(pixels, k=colors_per_sample)

        hex_colors = [_rgb_to_hex(c) for c in colors]
        avg_rgb = pixels.mean(axis=0)
        temperature = _classify_temperature(avg_rgb)

        sample_data.append({
            "timecode_s": round(ts, 2),
            "timecode_fmt": _format_timecode(ts),
            "dominant_colors": hex_colors,
            "avg_rgb": [int(x) for x in avg_rgb],
            "temperature": temperature,
        })

    if not sample_data:
        return None

    # Build visualization: thumbnails with color swatches
    thumb_w, thumb_h = 200, 120
    swatch_h = 30
    row_h = thumb_h + swatch_h + 28
    cols = min(4, len(sample_data))
    rows = (len(sample_data) + cols - 1) // cols

    canvas_w = cols * (thumb_w + 8) + 8
    canvas_h = rows * (row_h + 8) + 8
    canvas = Image.new("RGB", (canvas_w, canvas_h), (20, 20, 20))
    draw = ImageDraw.Draw(canvas)

    try:
        font = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 11)
    except (IOError, OSError):
        font = ImageFont.load_default()

    for i, ((img, ts), data) in enumerate(zip(frame_images, sample_data)):
        row = i // cols
        col = i % cols
        x = 8 + col * (thumb_w + 8)
        y = 8 + row * (row_h + 8)

        # Thumbnail
        thumb = img.resize((thumb_w, thumb_h), Image.LANCZOS)
        canvas.paste(thumb, (x, y))

        # Color swatches
        swatch_w = thumb_w // colors_per_sample
        for j, hex_color in enumerate(data["dominant_colors"]):
            r, g, b = _hex_to_rgb(hex_color)
            sx = x + j * swatch_w
            draw.rectangle([sx, y + thumb_h, sx + swatch_w, y + thumb_h + swatch_h], fill=(r, g, b))

        # Label
        label = f"{data['timecode_fmt']} ({data['temperature']})"
        draw.text((x + 4, y + thumb_h + swatch_h + 4), label, fill=(180, 180, 180), font=font)

    palette_path = output_dir / "color_palette.png"
    canvas.save(palette_path, "PNG")

    # Cleanup
    for f in tmp_dir.glob("*.png"):
        f.unlink()
    tmp_dir.rmdir()

    # Compute overall stats
    all_temps = [s["temperature"] for s in sample_data]
    dominant_temp = max(set(all_temps), key=all_temps.count)

    result = {
        "video": str(video_path),
        "samples": sample_data,
        "overall_temperature": dominant_temp,
        "palette_image": str(palette_path),
    }

    print(f"  Color palette saved: {palette_path} ({len(sample_data)} samples)")
    return result


def analyze_motion(
    video_path: Path,
    output_dir: Path,
    interval_s: float = 0.5,
) -> Optional[Dict]:
    """
    Analyze motion intensity across a video by computing frame-to-frame differences.

    Produces a PNG timeline chart and JSON with per-sample energy values.

    Args:
        video_path: Path to video file
        output_dir: Directory for output files
        interval_s: Sampling interval in seconds

    Returns:
        Dict with motion data and chart path, or None on failure.
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np
    from PIL import Image

    video_path = Path(video_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    meta = probe_metadata(video_path)
    if not meta or meta["duration_s"] <= 0:
        return None

    duration = meta["duration_s"]
    n_samples = max(2, int(duration / interval_s))
    timestamps = [i * interval_s for i in range(n_samples) if i * interval_s < duration]

    # Extract frames at intervals
    tmp_dir = output_dir / "_motion_tmp"
    tmp_dir.mkdir(exist_ok=True)

    frames = []
    for i, ts in enumerate(timestamps):
        fp = tmp_dir / f"motion_{i:04d}.png"
        result = extract_frame_at(video_path, ts, fp)
        if result:
            img = Image.open(fp).convert("L").resize((160, 90), Image.LANCZOS)
            frames.append((ts, np.array(img, dtype=np.float32)))

    if len(frames) < 2:
        return None

    # Compute frame-to-frame differences
    motion_data = []
    for i in range(1, len(frames)):
        ts = frames[i][0]
        diff = np.abs(frames[i][1] - frames[i-1][1])
        energy = float(diff.mean())
        motion_data.append({
            "timecode_s": round(ts, 2),
            "energy": round(energy, 2),
        })

    # Classify segments
    energies = [m["energy"] for m in motion_data]
    energy_arr = np.array(energies)
    median_e = np.median(energy_arr)
    for m in motion_data:
        if m["energy"] < median_e * 0.3:
            m["classification"] = "static"
        elif m["energy"] < median_e * 1.5:
            m["classification"] = "moderate"
        else:
            m["classification"] = "high_motion"

    # Plot motion timeline
    fig, ax = plt.subplots(figsize=(12, 3))
    times = [m["timecode_s"] for m in motion_data]
    ax.fill_between(times, energies, alpha=0.4, color="#4a9eff")
    ax.plot(times, energies, color="#4a9eff", linewidth=1.5)
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Motion Energy")
    ax.set_title(f"Motion Intensity — {Path(video_path).name}")
    ax.set_xlim(0, duration)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()

    chart_path = output_dir / "motion_chart.png"
    fig.savefig(chart_path, dpi=150)
    plt.close(fig)

    # Cleanup
    for f in tmp_dir.glob("*.png"):
        f.unlink()
    tmp_dir.rmdir()

    result = {
        "video": str(video_path),
        "interval_s": interval_s,
        "samples": motion_data,
        "stats": {
            "mean_energy": round(float(energy_arr.mean()), 2),
            "max_energy": round(float(energy_arr.max()), 2),
            "min_energy": round(float(energy_arr.min()), 2),
            "std_energy": round(float(energy_arr.std()), 2),
        },
        "chart_path": str(chart_path),
    }

    print(f"  Motion chart saved: {chart_path} ({len(motion_data)} samples)")
    return result


# ─── Helpers ──────────────────────────────────────────────────────────

def _format_timecode(seconds: float) -> str:
    """Format seconds as MM:SS.f"""
    m, s = divmod(seconds, 60)
    return f"{int(m):02d}:{s:05.2f}"


def _kmeans_colors(pixels: 'np.ndarray', k: int = 5, iterations: int = 10) -> List[Tuple[int, int, int]]:
    """Simple k-means color quantization without sklearn dependency."""
    import numpy as np

    n = len(pixels)
    if n == 0:
        return [(0, 0, 0)] * k

    # Initialize centroids randomly
    rng = np.random.RandomState(42)
    indices = rng.choice(n, size=min(k, n), replace=False)
    centroids = pixels[indices].astype(np.float64)

    for _ in range(iterations):
        # Assign pixels to nearest centroid
        dists = np.linalg.norm(pixels[:, None] - centroids[None, :], axis=2)
        labels = np.argmin(dists, axis=1)
        # Update centroids
        new_centroids = np.array([
            pixels[labels == j].mean(axis=0) if (labels == j).any() else centroids[j]
            for j in range(len(centroids))
        ])
        centroids = new_centroids

    # Sort by frequency (largest cluster first)
    _, counts = np.unique(np.argmin(
        np.linalg.norm(pixels[:, None] - centroids[None, :], axis=2), axis=1
    ), return_counts=True)
    order = np.argsort(-counts)
    centroids = centroids[order]

    return [(int(c[0]), int(c[1]), int(c[2])) for c in centroids]


def _rgb_to_hex(rgb: Tuple[int, int, int]) -> str:
    return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"


def _hex_to_rgb(hex_str: str) -> Tuple[int, int, int]:
    hex_str = hex_str.lstrip("#")
    return (int(hex_str[0:2], 16), int(hex_str[2:4], 16), int(hex_str[4:6], 16))


def _classify_temperature(avg_rgb) -> str:
    """Classify color temperature as warm/neutral/cool based on average RGB."""
    r, g, b = float(avg_rgb[0]), float(avg_rgb[1]), float(avg_rgb[2])
    warmth = (r - b) / max(r + g + b, 1) * 100
    if warmth > 8:
        return "warm"
    elif warmth < -8:
        return "cool"
    return "neutral"
