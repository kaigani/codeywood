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
    base_volume: float = 1.0,
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
        base_volume: Volume multiplier for the base video's audio (0.0-1.0, default 1.0)

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
    if base_volume < 1.0:
        filter_parts.append(f"[0:a]volume={base_volume}[base]")
        mix_inputs.append("[base]")
    else:
        mix_inputs.append("[0:a]")

    for i, track in enumerate(audio_tracks):
        input_idx = i + 1
        delay_ms = int(track.get("start_s", 0) * 1000)
        volume = track.get("volume", 1.0)
        normalize = track.get("normalize", False)

        label = f"a{i}"
        # Build filter chain: normalize → delay → volume
        filters = []
        if normalize:
            filters.append(f"loudnorm=I=-16:TP=-1.5:LRA=11")
        filters.append(f"adelay={delay_ms}|{delay_ms}")
        if volume != 1.0:
            filters.append(f"volume={volume}")
        filter_chain = ",".join(filters)
        filter_parts.append(f"[{input_idx}:a]{filter_chain}[{label}]")
        mix_inputs.append(f"[{label}]")

    # Mix all audio streams
    n_inputs = len(mix_inputs)
    mix_input_str = "".join(mix_inputs)
    filter_parts.append(f"{mix_input_str}amix=inputs={n_inputs}:duration=first:dropout_transition=2:normalize=0[aout]")

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
        "-ar", "44100", "-ac", "2",
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
            f"{mix_input_str}amix=inputs={len(mix_inputs)}:duration=longest:dropout_transition=2:normalize=0[aout]"
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
        "-ar", "44100", "-ac", "2",
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


# ─── Editing Primitives ──────────────────────────────────────────────


def trim_clip(
    video_path: Path,
    output_path: Path,
    start_s: float = 0.0,
    end_s: Optional[float] = None,
) -> Optional[Path]:
    """
    Trim a video clip at specified timecodes.

    Uses stream copy for speed; falls back to re-encode if copy fails
    (e.g., when cutting on non-keyframes causes artifacts).

    Args:
        video_path: Path to input video
        output_path: Path for trimmed output
        start_s: Start time in seconds
        end_s: End time in seconds (None = to end of clip)

    Returns:
        Path to trimmed video, or None on failure
    """
    video_path = Path(video_path)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Build command — try copy mode first
    cmd = ["ffmpeg", "-y", "-i", str(video_path)]
    if start_s > 0:
        cmd.extend(["-ss", str(start_s)])
    if end_s is not None:
        duration = end_s - start_s
        cmd.extend(["-t", str(duration)])
    cmd.extend(["-c", "copy", str(output_path)])

    print(f"\nTrimming {video_path.name} [{start_s}s → {end_s or 'end'}s]...")
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0 and output_path.exists():
        print(f"  Trimmed (copy): {output_path}")
        return output_path

    # Fallback: re-encode
    print(f"  Copy mode failed, re-encoding...")
    cmd = ["ffmpeg", "-y", "-i", str(video_path)]
    if start_s > 0:
        cmd.extend(["-ss", str(start_s)])
    if end_s is not None:
        duration = end_s - start_s
        cmd.extend(["-t", str(duration)])
    cmd.extend([
        "-c:v", "libx264", "-preset", "fast", "-crf", "18",
        "-c:a", "aac", "-b:a", "192k",
        str(output_path)
    ])

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0 and output_path.exists():
        print(f"  Trimmed (re-encoded): {output_path}")
        return output_path

    print(f"  Trim failed")
    if result.stderr:
        print(result.stderr[:500])
    return None


def crossfade_transition(
    clip_a: Path,
    clip_b: Path,
    output_path: Path,
    duration: float = 1.0,
) -> Optional[Path]:
    """
    Create a crossfade transition between two clips using ffmpeg xfade filter.

    Args:
        clip_a: First clip
        clip_b: Second clip
        output_path: Path for output
        duration: Crossfade duration in seconds

    Returns:
        Path to output video, or None on failure
    """
    clip_a, clip_b = Path(clip_a), Path(clip_b)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Get duration of first clip to calculate offset
    dur_a = probe_duration(clip_a)
    if not dur_a:
        print(f"  Cannot determine duration of {clip_a.name}")
        return None

    offset = max(0, dur_a - duration)

    # Video crossfade
    vfilter = f"[0:v][1:v]xfade=transition=fade:duration={duration}:offset={offset}[vout]"
    # Audio crossfade
    afilter = f"[0:a][1:a]acrossfade=d={duration}[aout]"

    cmd = [
        "ffmpeg", "-y",
        "-i", str(clip_a),
        "-i", str(clip_b),
        "-filter_complex", f"{vfilter};{afilter}",
        "-map", "[vout]", "-map", "[aout]",
        "-c:v", "libx264", "-preset", "fast", "-crf", "18",
        "-c:a", "aac", "-b:a", "192k",
        str(output_path)
    ]

    print(f"\nCrossfade: {clip_a.name} → {clip_b.name} ({duration}s)...")
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0 and output_path.exists():
        print(f"  Crossfade saved: {output_path}")
        return output_path

    # Retry without audio crossfade (one or both clips may lack audio)
    cmd = [
        "ffmpeg", "-y",
        "-i", str(clip_a),
        "-i", str(clip_b),
        "-filter_complex", f"{vfilter}",
        "-map", "[vout]",
        "-c:v", "libx264", "-preset", "fast", "-crf", "18",
        "-an",
        str(output_path)
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0 and output_path.exists():
        print(f"  Crossfade saved (no audio): {output_path}")
        return output_path

    print(f"  Crossfade failed")
    if result.stderr:
        print(result.stderr[:500])
    return None


def l_cut(
    clip_a: Path,
    clip_b: Path,
    output_path: Path,
    audio_lead_s: float = 1.0,
) -> Optional[Path]:
    """
    L-cut: Audio from clip_b starts before the visual cut.

    The audience hears clip_b's audio while still seeing clip_a's video,
    then both video and audio switch to clip_b.

    Args:
        clip_a: First clip (video extends past audio cut point)
        clip_b: Second clip (audio starts early)
        output_path: Path for output
        audio_lead_s: How many seconds clip_b's audio leads the video cut

    Returns:
        Path to output video, or None on failure
    """
    clip_a, clip_b = Path(clip_a), Path(clip_b)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    dur_a = probe_duration(clip_a)
    if not dur_a:
        return None

    audio_cut_point = max(0, dur_a - audio_lead_s)

    # Complex filter: video concat, audio crossfade at cut point
    filter_complex = (
        f"[0:a]afade=t=out:st={audio_cut_point}:d={audio_lead_s}[a0];"
        f"[1:a]adelay={int(audio_cut_point * 1000)}|{int(audio_cut_point * 1000)}[a1];"
        f"[a0][a1]amix=inputs=2:duration=first:dropout_transition=2[aout];"
        f"[0:v][1:v]concat=n=2:v=1:a=0[vout]"
    )

    cmd = [
        "ffmpeg", "-y",
        "-i", str(clip_a),
        "-i", str(clip_b),
        "-filter_complex", filter_complex,
        "-map", "[vout]", "-map", "[aout]",
        "-c:v", "libx264", "-preset", "fast", "-crf", "18",
        "-c:a", "aac", "-b:a", "192k",
        str(output_path)
    ]

    print(f"\nL-cut: {clip_a.name} → {clip_b.name} (audio leads {audio_lead_s}s)...")
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0 and output_path.exists():
        print(f"  L-cut saved: {output_path}")
        return output_path

    print(f"  L-cut failed — falling back to hard cut")
    return concatenate_clips([clip_a, clip_b], output_path)


def j_cut(
    clip_a: Path,
    clip_b: Path,
    output_path: Path,
    video_lead_s: float = 1.0,
) -> Optional[Path]:
    """
    J-cut: Video from clip_b starts before the audio cut.

    The audience sees clip_b's video while still hearing clip_a's audio,
    then both switch to clip_b.

    Args:
        clip_a: First clip (audio extends past video cut point)
        clip_b: Second clip (video starts early)
        output_path: Path for output
        video_lead_s: How many seconds clip_b's video leads the audio cut

    Returns:
        Path to output video, or None on failure
    """
    clip_a, clip_b = Path(clip_a), Path(clip_b)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    dur_a = probe_duration(clip_a)
    if not dur_a:
        return None

    video_cut_point = max(0, dur_a - video_lead_s)

    filter_complex = (
        f"[0:v]trim=0:{video_cut_point},setpts=PTS-STARTPTS[v0];"
        f"[1:v]setpts=PTS-STARTPTS[v1];"
        f"[v0][v1]concat=n=2:v=1:a=0[vout];"
        f"[0:a]afade=t=out:st={video_cut_point}:d={video_lead_s}[a0];"
        f"[1:a]adelay={int(video_cut_point * 1000)}|{int(video_cut_point * 1000)}[a1];"
        f"[a0][a1]amix=inputs=2:duration=first:dropout_transition=2[aout]"
    )

    cmd = [
        "ffmpeg", "-y",
        "-i", str(clip_a),
        "-i", str(clip_b),
        "-filter_complex", filter_complex,
        "-map", "[vout]", "-map", "[aout]",
        "-c:v", "libx264", "-preset", "fast", "-crf", "18",
        "-c:a", "aac", "-b:a", "192k",
        str(output_path)
    ]

    print(f"\nJ-cut: {clip_a.name} → {clip_b.name} (video leads {video_lead_s}s)...")
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0 and output_path.exists():
        print(f"  J-cut saved: {output_path}")
        return output_path

    print(f"  J-cut failed — falling back to hard cut")
    return concatenate_clips([clip_a, clip_b], output_path)


def speed_ramp(
    video_path: Path,
    output_path: Path,
    factor: float = 2.0,
) -> Optional[Path]:
    """
    Apply uniform speed change to a video.

    Args:
        video_path: Path to input video
        output_path: Path for output
        factor: Speed multiplier (2.0 = 2x faster, 0.5 = 2x slower)

    Returns:
        Path to output video, or None on failure
    """
    video_path = Path(video_path)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    video_filter = f"setpts=PTS/{factor}"

    # Audio: atempo supports 0.5-2.0 range, chain for larger ranges
    audio_filters = []
    remaining = factor
    while remaining > 2.0:
        audio_filters.append("atempo=2.0")
        remaining /= 2.0
    while remaining < 0.5:
        audio_filters.append("atempo=0.5")
        remaining /= 0.5
    audio_filters.append(f"atempo={remaining:.4f}")
    audio_filter = ",".join(audio_filters)

    cmd = [
        "ffmpeg", "-y",
        "-i", str(video_path),
        "-filter:v", video_filter,
        "-filter:a", audio_filter,
        "-c:v", "libx264", "-preset", "fast", "-crf", "18",
        "-c:a", "aac", "-b:a", "192k",
        str(output_path)
    ]

    direction = "faster" if factor > 1 else "slower"
    print(f"\nSpeed ramp: {video_path.name} ({factor}x {direction})...")
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0 and output_path.exists():
        print(f"  Speed ramp saved: {output_path}")
        return output_path

    # Retry without audio
    cmd = [
        "ffmpeg", "-y",
        "-i", str(video_path),
        "-filter:v", video_filter,
        "-an",
        "-c:v", "libx264", "-preset", "fast", "-crf", "18",
        str(output_path)
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0 and output_path.exists():
        print(f"  Speed ramp saved (no audio): {output_path}")
        return output_path

    print(f"  Speed ramp failed")
    if result.stderr:
        print(result.stderr[:500])
    return None


def add_text_overlay(
    video_path: Path,
    output_path: Path,
    text: str,
    position: str = "bottom_center",
    start_s: float = 0.0,
    duration_s: Optional[float] = None,
    fontsize: int = 36,
    fontcolor: str = "white",
    bg_opacity: float = 0.5,
) -> Optional[Path]:
    """
    Add text overlay to a video using drawtext filter.

    Args:
        video_path: Path to input video
        output_path: Path for output
        text: Text to display
        position: Preset position (bottom_center, top_center, center, lower_third)
        start_s: When overlay appears (seconds)
        duration_s: How long overlay stays (None = to end)
        fontsize: Font size
        fontcolor: Font color
        bg_opacity: Background box opacity (0-1)

    Returns:
        Path to output video, or None on failure
    """
    video_path = Path(video_path)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    positions = {
        "bottom_center": "x=(w-text_w)/2:y=h-th-40",
        "top_center": "x=(w-text_w)/2:y=40",
        "center": "x=(w-text_w)/2:y=(h-text_h)/2",
        "lower_third": "x=60:y=h*3/4",
    }
    pos = positions.get(position, positions["bottom_center"])

    escaped = text.replace("'", "'\\''").replace(":", "\\:")

    if duration_s:
        enable = f"between(t,{start_s},{start_s + duration_s})"
    else:
        enable = f"gte(t,{start_s})"

    bg_alpha = int(bg_opacity * 255)
    drawtext = (
        f"drawtext=text='{escaped}'"
        f":fontsize={fontsize}:fontcolor={fontcolor}"
        f":{pos}"
        f":box=1:boxcolor=black@0x{bg_alpha:02x}:boxborderw=8"
        f":enable='{enable}'"
    )

    cmd = [
        "ffmpeg", "-y",
        "-i", str(video_path),
        "-vf", drawtext,
        "-c:v", "libx264", "-preset", "fast", "-crf", "18",
        "-c:a", "copy",
        str(output_path)
    ]

    print(f"\nText overlay: \"{text[:40]}\" on {video_path.name}...")
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0 and output_path.exists():
        print(f"  Overlay saved: {output_path}")
        return output_path

    print(f"  Text overlay failed")
    if result.stderr:
        print(result.stderr[:500])
    return None


def apply_color_grade(
    video_path: Path,
    output_path: Path,
    preset: str = "warm_golden",
) -> Optional[Path]:
    """
    Apply a color grading preset to a video.

    Presets:
        warm_golden:   Sunset warmth, golden tones
        cool_blue:     Cold, steely blue tones
        high_contrast: Crushed blacks, bright highlights
        bleach_bypass: Desaturated, high contrast, silver look

    Args:
        video_path: Path to input video
        output_path: Path for output
        preset: Color grade preset name

    Returns:
        Path to output video, or None on failure
    """
    video_path = Path(video_path)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    presets = {
        "warm_golden": (
            "curves=r='0/0 0.25/0.3 0.5/0.56 0.75/0.78 1/1'"
            ":g='0/0 0.25/0.26 0.5/0.51 0.75/0.76 1/0.98'"
            ":b='0/0 0.25/0.2 0.5/0.44 0.75/0.7 1/0.9',"
            "eq=saturation=1.15:brightness=0.02"
        ),
        "cool_blue": (
            "curves=r='0/0 0.25/0.22 0.5/0.46 0.75/0.72 1/0.92'"
            ":g='0/0 0.25/0.24 0.5/0.48 0.75/0.74 1/0.96'"
            ":b='0/0 0.25/0.28 0.5/0.54 0.75/0.8 1/1',"
            "eq=saturation=0.9:brightness=-0.02"
        ),
        "high_contrast": (
            "curves=master='0/0 0.15/0.05 0.5/0.5 0.85/0.95 1/1',"
            "eq=contrast=1.3:saturation=1.1"
        ),
        "bleach_bypass": (
            "eq=saturation=0.5:contrast=1.4:brightness=-0.03,"
            "curves=master='0/0 0.1/0.02 0.5/0.5 0.9/0.98 1/1'"
        ),
    }

    if preset not in presets:
        print(f"  Unknown preset '{preset}'. Available: {', '.join(presets.keys())}")
        return None

    vfilter = presets[preset]

    cmd = [
        "ffmpeg", "-y",
        "-i", str(video_path),
        "-vf", vfilter,
        "-c:v", "libx264", "-preset", "fast", "-crf", "18",
        "-c:a", "copy",
        str(output_path)
    ]

    print(f"\nColor grade: {video_path.name} [{preset}]...")
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0 and output_path.exists():
        print(f"  Graded: {output_path}")
        return output_path

    print(f"  Color grade failed")
    if result.stderr:
        print(result.stderr[:500])
    return None


def add_silent_audio(video_path: Path, output_path: Path) -> Optional[Path]:
    """
    Add a silent audio track to a video-only file.

    Needed for concat demuxer compatibility when mixing clips with
    and without audio.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        "ffmpeg", "-y",
        "-i", str(video_path),
        "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
        "-c:v", "copy",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest",
        str(output_path)
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0 and output_path.exists():
        return output_path
    return None


def image_to_clip(image_path: Path, output_path: Path,
                  duration_s: float, fps: int = 25) -> Optional[Path]:
    """
    Create a video clip from a static image held for a target duration.

    Includes a silent audio track (44100Hz stereo AAC) so clips are
    ready for audio mixing and concat without stream mismatch issues.

    Args:
        image_path: Path to source image (PNG/JPG)
        output_path: Path for output video
        duration_s: Duration in seconds
        fps: Frame rate (default 25)

    Returns:
        Path to video clip, or None on failure
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        "ffmpeg", "-y",
        "-loop", "1",
        "-i", str(image_path),
        "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
        "-c:v", "libx264",
        "-t", str(duration_s),
        "-pix_fmt", "yuv420p",
        "-r", str(fps),
        "-g", str(fps),          # keyframe every 1 second (not stillimage tune)
        "-keyint_min", str(fps),  # minimum keyframe interval
        "-c:a", "aac", "-b:a", "192k",
        "-shortest",
        str(output_path)
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0 and output_path.exists():
        return output_path

    print(f"  image_to_clip failed for {image_path.name}")
    if result.stderr:
        print(result.stderr[:500])
    return None
