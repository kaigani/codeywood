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


def extract_audio(video_path: Path, output_path: Path) -> Optional[Path]:
    """
    Extract audio track from a video file.

    Args:
        video_path: Path to video file
        output_path: Path for output audio file (WAV)

    Returns:
        Path to extracted audio, or None on failure
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        "ffmpeg", "-y",
        "-i", str(video_path),
        "-vn",                  # No video
        "-acodec", "pcm_s16le", # WAV format
        "-ar", "44100",         # 44.1kHz
        "-ac", "2",             # Stereo
        str(output_path)
    ]

    print(f"\nExtracting audio from {video_path.name}...")
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0 and output_path.exists():
        print(f"  Extracted: {output_path}")
        return output_path
    else:
        print(f"  Failed to extract audio")
        if result.stderr:
            # Check for "no audio" case
            if "does not contain any stream" in result.stderr:
                print(f"  (Video has no audio track)")
            else:
                print(result.stderr[:500])
        return None


def replace_audio(video_path: Path, audio_path: Path, output_path: Path) -> Optional[Path]:
    """
    Replace a video's audio track with new audio.

    Args:
        video_path: Path to video file
        audio_path: Path to new audio file
        output_path: Path for output video

    Returns:
        Path to output video, or None on failure
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        "ffmpeg", "-y",
        "-i", str(video_path),
        "-i", str(audio_path),
        "-c:v", "copy",        # Copy video stream
        "-map", "0:v:0",       # Video from first input
        "-map", "1:a:0",       # Audio from second input
        "-shortest",
        str(output_path)
    ]

    print(f"\nReplacing audio in {video_path.name}...")
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0 and output_path.exists():
        print(f"  Saved: {output_path}")
        return output_path
    else:
        print(f"  Failed to replace audio")
        if result.stderr:
            print(result.stderr[:500])
        return None


def mix_audio_tracks(
    video_path: Path,
    audio_tracks: List[dict],
    output_path: Path,
) -> Optional[Path]:
    """
    Mix dialogue audio tracks onto a video at specified timecodes.

    Args:
        video_path: Path to base video file
        audio_tracks: List of dicts with:
            - path: Path to audio file
            - start_s: Start time in seconds (float)
            - volume: Volume multiplier (0.0-1.0, default 1.0)
        output_path: Path for output video

    Returns:
        Path to output video, or None on failure
    """
    if not audio_tracks:
        print("No audio tracks to mix")
        return None

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Build ffmpeg complex filter
    # Input 0 = video, inputs 1..N = audio tracks
    inputs = ["-i", str(video_path)]
    for track in audio_tracks:
        inputs.extend(["-i", str(track["path"])])

    # Build filter chain: delay each track, then mix all together
    filter_parts = []
    mix_inputs = []

    # Include original video audio if it has one (index [0:a])
    mix_inputs.append("[0:a]")

    for i, track in enumerate(audio_tracks):
        input_idx = i + 1
        delay_ms = int(track.get("start_s", 0) * 1000)
        volume = track.get("volume", 1.0)

        label = f"a{i}"
        # Apply delay and volume
        filter_parts.append(
            f"[{input_idx}:a]adelay={delay_ms}|{delay_ms},volume={volume}[{label}]"
        )
        mix_inputs.append(f"[{label}]")

    # Mix all audio streams
    n_inputs = len(mix_inputs)
    mix_input_str = "".join(mix_inputs)
    filter_parts.append(f"{mix_input_str}amix=inputs={n_inputs}:duration=first:dropout_transition=2[aout]")

    filter_complex = ";".join(filter_parts)

    cmd = [
        "ffmpeg", "-y",
        *inputs,
        "-filter_complex", filter_complex,
        "-map", "0:v",
        "-map", "[aout]",
        "-c:v", "copy",
        "-c:a", "aac",
        "-b:a", "192k",
        str(output_path)
    ]

    print(f"\nMixing {len(audio_tracks)} audio track(s) onto {video_path.name}...")
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0 and output_path.exists():
        print(f"  Saved: {output_path}")
        return output_path
    else:
        print(f"  Failed to mix audio")
        if result.stderr:
            # Try without original audio (video may have no audio track)
            if "does not contain any stream" in result.stderr or "Invalid" in result.stderr:
                return _mix_audio_no_original(video_path, audio_tracks, output_path)
            print(result.stderr[:500])
        return None


def _mix_audio_no_original(
    video_path: Path,
    audio_tracks: List[dict],
    output_path: Path,
) -> Optional[Path]:
    """Fallback mixer when video has no original audio track."""
    inputs = ["-i", str(video_path)]
    for track in audio_tracks:
        inputs.extend(["-i", str(track["path"])])

    filter_parts = []
    mix_inputs = []

    for i, track in enumerate(audio_tracks):
        input_idx = i + 1
        delay_ms = int(track.get("start_s", 0) * 1000)
        volume = track.get("volume", 1.0)
        label = f"a{i}"
        filter_parts.append(
            f"[{input_idx}:a]adelay={delay_ms}|{delay_ms},volume={volume}[{label}]"
        )
        mix_inputs.append(f"[{label}]")

    if len(mix_inputs) == 1:
        # Single track, no amix needed
        filter_complex = ";".join(filter_parts)
        audio_map = f"[a0]"
    else:
        mix_input_str = "".join(mix_inputs)
        filter_parts.append(
            f"{mix_input_str}amix=inputs={len(mix_inputs)}:duration=longest:dropout_transition=2[aout]"
        )
        filter_complex = ";".join(filter_parts)
        audio_map = "[aout]"

    cmd = [
        "ffmpeg", "-y",
        *inputs,
        "-filter_complex", filter_complex,
        "-map", "0:v",
        "-map", audio_map,
        "-c:v", "copy",
        "-c:a", "aac",
        "-b:a", "192k",
        str(output_path)
    ]

    print(f"  Retrying without original audio track...")
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0 and output_path.exists():
        print(f"  Saved: {output_path}")
        return output_path
    else:
        print(f"  Failed to mix audio (fallback)")
        if result.stderr:
            print(result.stderr[:500])
        return None


def probe_audio_duration(audio_path: Path) -> Optional[float]:
    """
    Get the duration of an audio file in seconds.

    Args:
        audio_path: Path to audio file

    Returns:
        Duration in seconds, or None on failure
    """
    cmd = [
        "ffprobe", "-v", "quiet",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(audio_path)
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0 and result.stdout.strip():
        try:
            return float(result.stdout.strip())
        except ValueError:
            return None
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
