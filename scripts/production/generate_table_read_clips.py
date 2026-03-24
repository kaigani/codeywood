#!/usr/bin/env python3
"""
Table Read v03 — Generate video clips.

Three generation strategies:
  - TR_CU with dialogue: wan-infinitetalk (832x468 lipsync from portrait + TTS audio)
  - TR_WIDE / TR_CU silent: ltx2-3-fast (1280x720 from start frame, no audio)
  - PROD_CLIP / PROD_FRAME: ffmpeg (copy/trim or static frame)

Assembly upscales InfiniteTalk clips to 720p and layers V.O. onto wide/PROD shots.
"""

import subprocess
import sys
import time
from pathlib import Path

import requests
import yaml

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
COMFYUI_BASE = "http://192.168.1.181:8100"
WF_LIPSYNC = "wan-infinitetalk"
WF_MOTION = "ltx2-3-fast"

PROJECT = Path(__file__).resolve().parents[2] / "projects" / "stray-signal"
TABLE_READ = PROJECT / "PRODUCTION" / "EP01_v03" / "table_read"
SHOT_LIST = TABLE_READ / "table_read_shot_list.yaml"
FRAMES_DIR = TABLE_READ / "frames"
CLIPS_DIR = TABLE_READ / "clips"
AUDIO_DIR = TABLE_READ / "audio"

PROD_FRAMES = PROJECT / "PRODUCTION" / "EP01_v03" / "frames"
PROD_CLIPS = PROJECT / "PRODUCTION" / "EP01_v03" / "clips"

NEGATIVE_LTX = (
    "blurry, oversaturated, pixelated, low resolution, distorted, noise, "
    "watermark, text, logo, subtitles, deformed, extra limbs, photograph, "
    "photorealistic, live action, mouth moving, speaking, talking"
)

STYLE = "Stylized sci-fi animation."

# InfiniteTalk prompts per character (motion only, no appearance — frame handles that)
LIPSYNC_PROMPTS = {
    "mick": "Man talking at a table, animated gestures, expressive, blinking regularly",
    "neda": "Girl talking at a table, direct eye contact, controlled expression, blinking regularly",
    "kai": "Boy talking at a table, quiet intensity, measured delivery, blinking regularly",
}

# LTX-2.3 prompts — minimal, let the start frame do the work
WIDE_PROMPT = (
    "Three people seated at a table in an amber-lit production room. "
    "Subtle breathing movement. Scripts on table. Minimal motion. " + STYLE
)
SILENT_CU_PROMPT = (
    "Close-up of a person seated at a table. "
    "Subtle eye movement, listening. Minimal motion. " + STYLE
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def submit_and_wait(workflow, params, files=None, timeout=900):
    url = f"{COMFYUI_BASE}/workflows/{workflow}"
    if files:
        resp = requests.post(url, data=params, files=files)
    else:
        resp = requests.post(url, data=params)
    resp.raise_for_status()
    job = resp.json()
    job_id = job["job_id"]
    start = time.time()
    deadline = start + timeout
    polls = 0
    while time.time() < deadline:
        status = requests.get(f"{COMFYUI_BASE}/jobs/{job_id}").json()
        st = status.get("status", "unknown")
        if st == "completed":
            elapsed = time.time() - start
            print(f"    Done ({elapsed:.0f}s)")
            return requests.get(f"{COMFYUI_BASE}/jobs/{job_id}/result").content
        if st in ("error", "failed"):
            raise RuntimeError(f"Job {job_id} failed: {status.get('error')}")
        polls += 1
        time.sleep(2 if polls <= 5 else 5)
    raise TimeoutError(f"Timeout on {job_id}")


def save(data, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as f:
        f.write(data)
    kb = len(data) / 1024
    print(f"    Saved: {path.name} ({kb:.0f} KB)")
    return path


def resolve_frame(frame_name):
    """Find v02 frame (JPG) first, fall back to v01 (PNG)."""
    stem = Path(frame_name).stem
    for ext in ("_v02.jpg", "_v02.png"):
        p = FRAMES_DIR / f"{stem}{ext}"
        if p.exists():
            return p
    orig = FRAMES_DIR / frame_name
    return orig if orig.exists() else None


def get_audio_duration(wav_path):
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "csv=p=0",
        str(wav_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0 and result.stdout.strip():
        return float(result.stdout.strip())
    return 0


def static_frame_to_video(frame_path, out_path, duration):
    cmd = [
        "ffmpeg", "-y",
        "-loop", "1",
        "-i", str(frame_path),
        "-c:v", "libx264",
        "-t", str(duration),
        "-pix_fmt", "yuv420p",
        "-vf", "scale=1280:720,fps=25",
        "-preset", "medium",
        "-crf", "18",
        str(out_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg failed: {result.stderr[-500:]}")
    kb = out_path.stat().st_size / 1024
    print(f"    Saved: {out_path.name} ({kb:.0f} KB) [static frame -> {duration}s]")


def classify_shot(shot):
    """Determine generation strategy for a shot."""
    shot_type = shot["type"]
    has_audio = bool(shot.get("audio"))

    if shot_type in ("PROD_CLIP", "PROD_FRAME"):
        return "PROD"
    if shot_type == "TR_WIDE":
        return "LTX_WIDE"
    if shot_type == "TR_CU" and has_audio:
        return "INFINITETALK"
    return "LTX_SILENT_CU"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Generate table read v03 video clips")
    parser.add_argument("--shot", type=int, help="Specific shot number (0 = all)", default=0)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--force", action="store_true", help="Regenerate even if clip exists")
    parser.add_argument("--timeout", type=int, default=900, help="Per-clip timeout in seconds")
    args = parser.parse_args()

    CLIPS_DIR.mkdir(parents=True, exist_ok=True)

    with open(SHOT_LIST) as f:
        shot_list = yaml.safe_load(f)

    shots = shot_list["shots"]
    if args.shot > 0:
        shots = [s for s in shots if s["shot"] == args.shot]
        if not shots:
            print(f"No shot {args.shot}")
            sys.exit(1)

    # Health check
    has_gen = any(s["type"].startswith("TR_") for s in shots)
    if has_gen and not args.dry_run:
        try:
            r = requests.get(f"{COMFYUI_BASE}/health", timeout=5)
            if r.status_code != 200:
                print(f"ERROR: ComfyUI not healthy (status {r.status_code})")
                sys.exit(1)
        except Exception as e:
            print(f"ERROR: ComfyUI not reachable: {e}")
            sys.exit(1)

    # Classify all shots
    for s in shots:
        s["_strategy"] = classify_shot(s)

    if args.dry_run:
        counts = {}
        print(f"[DRY RUN] {len(shots)} shots:\n")
        for s in shots:
            shot_num = s["shot"]
            strategy = s["_strategy"]
            dur = s["duration"]
            out = CLIPS_DIR / f"shot_{shot_num:02d}.mp4"
            exists = out.exists()
            counts[strategy] = counts.get(strategy, 0) + 1

            if strategy == "INFINITETALK":
                frame_name = s.get("frame", "?")
                frame_path = resolve_frame(frame_name) if frame_name != "?" else None
                audio_wav = AUDIO_DIR / f"shot_{shot_num:02d}.wav"
                voice = s.get("voice", "?")
                print(f"  Shot {shot_num:2d}: LIPSYNC    ({dur}s) voice={voice} "
                      f"{'EXISTS' if exists else 'pending'} "
                      f"{'[frame OK]' if frame_path else '[NO FRAME]'} "
                      f"{'[wav OK]' if audio_wav.exists() else '[NO WAV]'}")
            elif strategy in ("LTX_WIDE", "LTX_SILENT_CU"):
                frame_name = s.get("frame", "?")
                frame_path = resolve_frame(frame_name) if frame_name != "?" else None
                label = "WIDE" if strategy == "LTX_WIDE" else "SILENT CU"
                print(f"  Shot {shot_num:2d}: {label:10s} ({dur}s) "
                      f"{'EXISTS' if exists else 'pending'} "
                      f"{'[frame OK]' if frame_path else '[NO FRAME]'}")
            else:
                src = s.get("source", "?")
                shot_type = s["type"]
                src_dir = PROD_CLIPS if shot_type == "PROD_CLIP" else PROD_FRAMES
                src_path = src_dir / src
                print(f"  Shot {shot_num:2d}: {shot_type:10s} ({dur}s) src={src} "
                      f"{'EXISTS' if exists else 'pending'} "
                      f"{'[src OK]' if src_path.exists() else '[NO SRC]'}")

        print(f"\nStrategy breakdown:")
        for k, v in sorted(counts.items()):
            print(f"  {k}: {v}")
        sys.exit(0)

    total = len(shots)
    done = 0
    failed = []
    stats = {"lipsync": 0, "ltx_wide": 0, "ltx_silent": 0, "prod_clip": 0, "prod_frame": 0}

    for shot in shots:
        done += 1
        shot_num = shot["shot"]
        shot_type = shot["type"]
        dur = shot["duration"]
        strategy = shot["_strategy"]
        out_path = CLIPS_DIR / f"shot_{shot_num:02d}.mp4"

        if out_path.exists() and not args.force:
            print(f"\n  [{done}/{total}] Shot {shot_num}: {strategy} -- SKIP (exists)")
            continue

        print(f"\n  [{done}/{total}] Shot {shot_num}: {strategy} ({dur}s)")

        try:
            if strategy == "INFINITETALK":
                # Lipsync: wan-infinitetalk (832x468)
                frame_name = shot.get("frame")
                frame_path = resolve_frame(frame_name)
                if not frame_path:
                    print(f"    SKIP: frame not found: {frame_name}")
                    failed.append(f"shot_{shot_num}")
                    continue

                audio_wav = AUDIO_DIR / f"shot_{shot_num:02d}.wav"
                if not audio_wav.exists():
                    print(f"    SKIP: audio not found: {audio_wav.name}")
                    failed.append(f"shot_{shot_num}")
                    continue

                audio_dur = get_audio_duration(audio_wav)
                max_frames = max(81, int(round(audio_dur * 30)) + 30)  # ~30fps + buffer

                # Pick character prompt
                voice = shot.get("voice", "mick")
                prompt = LIPSYNC_PROMPTS.get(voice, LIPSYNC_PROMPTS["mick"])

                print(f"    InfiniteTalk: {frame_path.name} + {audio_wav.name}")
                print(f"    Audio: {audio_dur:.1f}s, max_frames: {max_frames}")

                params = {
                    "prompt": prompt,
                    "width": "832",
                    "height": "468",
                    "max_frames": str(max_frames),
                    "seed": str(9000 + shot_num),
                }

                img_fh = open(frame_path, "rb")
                aud_fh = open(audio_wav, "rb")
                try:
                    mime = "image/jpeg" if frame_path.suffix.lower() in (".jpg", ".jpeg") else "image/png"
                    files = {
                        "image": (frame_path.name, img_fh, mime),
                        "audio": (audio_wav.name, aud_fh, "audio/wav"),
                    }
                    data = submit_and_wait(WF_LIPSYNC, params, files=files, timeout=args.timeout)
                finally:
                    img_fh.close()
                    aud_fh.close()

                save(data, out_path)
                stats["lipsync"] += 1

            elif strategy in ("LTX_WIDE", "LTX_SILENT_CU"):
                # LTX-2.3 at 1280x720 — no audio
                frame_name = shot.get("frame")
                frame_path = resolve_frame(frame_name)
                if not frame_path:
                    print(f"    SKIP: frame not found: {frame_name}")
                    failed.append(f"shot_{shot_num}")
                    continue

                prompt = WIDE_PROMPT if strategy == "LTX_WIDE" else SILENT_CU_PROMPT
                label = "WIDE" if strategy == "LTX_WIDE" else "SILENT CU"
                print(f"    LTX-2.3: {label} ({frame_path.name})")

                params = {
                    "prompt": prompt,
                    "negative_prompt": NEGATIVE_LTX,
                    "duration": str(dur),
                    "width": "1280",
                    "height": "720",
                    "seed": str(8100 + shot_num),
                }

                img_fh = open(frame_path, "rb")
                try:
                    mime = "image/jpeg" if frame_path.suffix.lower() in (".jpg", ".jpeg") else "image/png"
                    files = {"first_frame": (frame_path.name, img_fh, mime)}
                    data = submit_and_wait(WF_MOTION, params, files=files, timeout=args.timeout)
                finally:
                    img_fh.close()

                save(data, out_path)
                if strategy == "LTX_WIDE":
                    stats["ltx_wide"] += 1
                else:
                    stats["ltx_silent"] += 1

            elif shot_type == "PROD_CLIP":
                src_name = shot.get("source")
                src_path = PROD_CLIPS / src_name
                if not src_path.exists():
                    print(f"    SKIP: source clip not found: {src_name}")
                    failed.append(f"shot_{shot_num}")
                    continue

                cmd = [
                    "ffmpeg", "-y",
                    "-i", str(src_path),
                    "-t", str(dur),
                    "-c:v", "libx264",
                    "-pix_fmt", "yuv420p",
                    "-vf", "scale=1280:720",
                    "-preset", "medium",
                    "-crf", "18",
                    "-c:a", "aac", "-ar", "44100", "-ac", "2", "-b:a", "128k",
                    str(out_path),
                ]
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode != 0:
                    raise RuntimeError(f"ffmpeg trim failed: {result.stderr[-500:]}")
                kb = out_path.stat().st_size / 1024
                print(f"    Saved: {out_path.name} ({kb:.0f} KB) [prod clip -> {dur}s]")
                stats["prod_clip"] += 1

            elif shot_type == "PROD_FRAME":
                src_name = shot.get("source")
                src_path = PROD_FRAMES / src_name
                if not src_path.exists():
                    print(f"    SKIP: source frame not found: {src_name}")
                    failed.append(f"shot_{shot_num}")
                    continue

                static_frame_to_video(src_path, out_path, dur)
                stats["prod_frame"] += 1

        except Exception as e:
            print(f"    FAILED: {e}")
            failed.append(f"shot_{shot_num}")

    if failed:
        print(f"\n  FAILED ({len(failed)}): {', '.join(failed)}")

    print(f"\n{'=' * 70}")
    print(f"DONE -- {done} shots processed")
    print(f"  Lipsync (InfiniteTalk): {stats['lipsync']}")
    print(f"  Wide (LTX-2.3):        {stats['ltx_wide']}")
    print(f"  Silent CU (LTX-2.3):   {stats['ltx_silent']}")
    print(f"  Prod clips:            {stats['prod_clip']}")
    print(f"  Prod frames:           {stats['prod_frame']}")
    print(f"{'=' * 70}")
