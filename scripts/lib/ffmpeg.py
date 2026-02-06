"""
FFmpeg utilities for video production.

Extracted from fal_api.py to separate video processing from API concerns.
"""

import subprocess
from pathlib import Path
from typing import List, Optional


def extract_last_frame(video_path: Path, output_path: Path) -> Optional[Path]:
    """
    Extract the last frame from a video using ffmpeg.

    Args:
        video_path: Path to video file
        output_path: Path for output image

    Returns:
        Path to extracted frame, or None on failure
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        "ffmpeg", "-y",
        "-sseof", "-1",
        "-i", str(video_path),
        "-update", "1",
        "-q:v", "2",
        str(output_path)
    ]

    print(f"\nExtracting last frame from {video_path.name}...")
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0 and output_path.exists():
        print(f"✓ Extracted: {output_path}")
        return output_path
    else:
        print(f"✗ Failed to extract frame")
        if result.stderr:
            print(result.stderr[:500])
        return None


def concatenate_clips(clips: List[Path], output_path: Path) -> Optional[Path]:
    """
    Concatenate video clips using ffmpeg concat demuxer.

    Args:
        clips: List of clip paths in order
        output_path: Path for output video

    Returns:
        Path to concatenated video, or None on failure
    """
    if not clips:
        print("No clips to concatenate")
        return None

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Write concat file
    concat_file = output_path.parent / "concat_list.txt"
    with open(concat_file, "w") as f:
        for clip in clips:
            f.write(f"file '{clip}'\n")

    cmd = [
        "ffmpeg", "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", str(concat_file),
        "-c", "copy",
        str(output_path)
    ]

    print(f"\nConcatenating {len(clips)} clips...")
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0 and output_path.exists():
        print(f"✓ Assembled: {output_path}")
        return output_path
    else:
        print(f"✗ Assembly failed")
        if result.stderr:
            print(result.stderr[:500])
        return None


def probe_duration(video_path: Path) -> Optional[float]:
    """
    Get the duration of a video file in seconds.

    Args:
        video_path: Path to video file

    Returns:
        Duration in seconds, or None on failure
    """
    cmd = [
        "ffprobe", "-v", "quiet",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(video_path)
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0 and result.stdout.strip():
        try:
            return float(result.stdout.strip())
        except ValueError:
            return None
    return None
