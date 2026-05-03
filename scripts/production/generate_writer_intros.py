#!/usr/bin/env python3
"""
Generate writer introduction stills + clips.

Pipeline per writer:
  1. z-image-base-t2i (1280x720) → STILLS/{id}_{slug}.jpg
  2. qwen3-tts-voicedesign → dialogue audio (WAV, temp)
  3. ltx2-i2v-audio (image + audio, 2s, 1280x720, 25fps) → CLIPS/{id}_{slug}.mp4

Input: INTROS/{id}_{slug}.md with sections:
  ## Appearance
  ## Natural setting
  ## Dialogue
  ## z-image prompt

Usage:
    python3 scripts/production/generate_writer_intros.py --writer 05_oskar-brandt
    python3 scripts/production/generate_writer_intros.py --all
    python3 scripts/production/generate_writer_intros.py --all --resume
"""

import argparse
import json
import re
import sys
import tempfile
import time
from datetime import datetime
from pathlib import Path

import requests

# ─── Config ──────────────────────────────────────────────────────────────────

COMFYUI_BASE = "http://192.168.1.181:8100"
TIMEOUT_IMAGE = 360
TIMEOUT_AUDIO = 360
TIMEOUT_VIDEO = 900

FPS = 25
DURATION_S = 5
FRAME_COUNT = FPS * DURATION_S + 1
WIDTH = 1280
HEIGHT = 720

IMAGE_WORKFLOW = "z-image-base-t2i"
AUDIO_WORKFLOW = "qwen3-tts-voicedesign"
VIDEO_WORKFLOW = "ltx2-3"

IMAGE_NEG = (
    "blurry, low quality, watermark, text overlay, subtitles, "
    "cartoon, animation, 3D render, overexposed, underexposed, "
    "disfigured, extra limbs, bad anatomy"
)
VIDEO_NEG = (
    "blurry, low resolution, ugly, garbled mess, compression artifacts, "
    "glitch, stop motion, still image, pixelated, robotic voice, oversaturated"
)

MIN_IMAGE_BYTES = 10_000
MIN_VIDEO_BYTES = 50_000
MIN_AUDIO_BYTES = 1_000

# ─── ComfyUI helpers ─────────────────────────────────────────────────────────

def health_check():
    try:
        r = requests.get(f"{COMFYUI_BASE}/health", timeout=5)
        return r.status_code == 200
    except Exception:
        return False


def submit_and_wait(workflow_id, data, files=None, timeout=300):
    """Submit a job and poll until complete. Returns raw bytes or raises."""
    url = f"{COMFYUI_BASE}/workflows/{workflow_id}"
    try:
        if files:
            resp = requests.post(url, data=data, files=files, timeout=30)
        else:
            resp = requests.post(url, data=data, timeout=30)
    except Exception as e:
        raise RuntimeError(f"Submit failed: {e}")

    # Sync response (direct content)
    ct = resp.headers.get("content-type", "")
    if resp.status_code == 200 and ("image" in ct or "video" in ct or "audio" in ct or "octet-stream" in ct):
        if len(resp.content) > 100:
            return resp.content

    if resp.status_code not in (200, 202):
        raise RuntimeError(f"HTTP {resp.status_code}: {resp.text[:300]}")

    try:
        job_id = resp.json().get("job_id")
    except Exception:
        raise RuntimeError(f"No job_id in response: {resp.text[:200]}")

    if not job_id:
        raise RuntimeError(f"No job_id returned")

    print(f"    Job: {job_id} (polling...)")
    start = time.time()
    poll_interval = 3
    while time.time() - start < timeout:
        time.sleep(poll_interval)
        poll_interval = min(poll_interval + 1, 8)
        try:
            status = requests.get(f"{COMFYUI_BASE}/jobs/{job_id}", timeout=15).json()
        except Exception:
            continue
        st = status.get("status", "unknown")
        if st == "completed":
            elapsed = time.time() - start
            result = requests.get(f"{COMFYUI_BASE}/jobs/{job_id}/result", timeout=60)
            print(f"    Done ({elapsed:.0f}s)")
            return result.content
        if st in ("error", "failed"):
            raise RuntimeError(f"Job {job_id} failed: {status.get('error', 'unknown')}")
        pos = status.get("position")
        elapsed = time.time() - start
        if int(elapsed) % 20 == 0:
            print(f"    ... {elapsed:.0f}s elapsed, status={st}, pos={pos}")
    raise TimeoutError(f"Timeout after {timeout}s on job {job_id}")

# ─── Parse INTROS .md ─────────────────────────────────────────────────────────

def parse_intro_md(path: Path) -> dict:
    """Parse an INTROS .md file into a dict with keys: appearance, setting, dialogue, z_prompt."""
    text = path.read_text()
    sections = {}
    current = None
    buf = []
    for line in text.splitlines():
        m = re.match(r'^##\s+(.+)', line)
        if m:
            if current is not None:
                sections[current] = "\n".join(buf).strip()
                buf = []
            current = m.group(1).strip()
        else:
            if current is not None:
                buf.append(line)
    if current is not None:
        sections[current] = "\n".join(buf).strip()

    return {
        "appearance": sections.get("Appearance", ""),
        "setting": sections.get("Natural setting", ""),
        "dialogue": sections.get("Dialogue", "").strip().strip('"'),
        "z_prompt": sections.get("z-image prompt", ""),
        "genre": sections.get("Genre", "").strip(),
        "medium": sections.get("Medium", "").strip(),
    }

# ─── Step 1: z-image still ───────────────────────────────────────────────────

def generate_still(writer_id: str, intro: dict, out_path: Path, seed: int = 42) -> bool:
    """Generate portrait still via z-image-base-t2i. Returns True on success."""
    prompt = intro["z_prompt"]
    if not prompt:
        print(f"  ERROR: No z-image prompt found")
        return False

    print(f"  [1/3] z-image still: {prompt[:80]}...")
    try:
        data = {
            "prompt": prompt,
            "negative_prompt": IMAGE_NEG,
            "seed": str(seed),
            "steps": "25",
            "cfg": "4",
            "width": str(WIDTH),
            "height": str(HEIGHT),
        }
        img_bytes = submit_and_wait(IMAGE_WORKFLOW, data, timeout=TIMEOUT_IMAGE)
    except Exception as e:
        print(f"  ERROR (still): {e}")
        return False

    if len(img_bytes) < MIN_IMAGE_BYTES:
        print(f"  ERROR: still too small ({len(img_bytes)} bytes)")
        return False

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_bytes(img_bytes)
    print(f"  Still OK: {len(img_bytes)/1024:.0f}KB → {out_path.name}")
    return True

# ─── Step 2: TTS voice design ─────────────────────────────────────────────────

def build_voice_instruct(intro: dict) -> str:
    """Build a voice design instruction from the writer's appearance/setting."""
    appearance = intro["appearance"]
    # Extract age and key traits from first sentence of appearance
    first_sentence = appearance.split(".")[0] if "." in appearance else appearance[:120]
    return (
        f"A realistic human voice. {first_sentence}. "
        "Natural, unhurried delivery. Not theatrical. The voice of someone "
        "accustomed to being listened to, but not performing. Minimal reverb, "
        "recorded in a quiet indoor space. Clear diction."
    )


def generate_audio(writer_id: str, intro: dict, seed: int = 42) -> bytes | None:
    """Generate TTS audio for the dialogue. Returns WAV bytes or None."""
    dialogue = intro["dialogue"]
    if not dialogue:
        print(f"  ERROR: No dialogue found")
        return None

    instruct = build_voice_instruct(intro)
    print(f"  [2/3] TTS: \"{dialogue}\"")
    print(f"    Voice: {instruct[:80]}...")

    try:
        data = {
            "instruct": instruct,
            "text": dialogue,
            "seed": str(seed),
        }
        audio_bytes = submit_and_wait(AUDIO_WORKFLOW, data, timeout=TIMEOUT_AUDIO)
    except Exception as e:
        print(f"  ERROR (audio): {e}")
        return None

    if len(audio_bytes) < MIN_AUDIO_BYTES:
        print(f"  ERROR: audio too small ({len(audio_bytes)} bytes)")
        return None

    print(f"  Audio OK: {len(audio_bytes)/1024:.0f}KB")
    return audio_bytes

# ─── Step 3: LTX-2.3 i2v clip ────────────────────────────────────────────────

def build_video_prompt(intro: dict) -> str:
    """Minimal LTX-2.3 prompt: dialogue + genre + medium. first_frame carries the visuals."""
    dialogue = intro["dialogue"]
    genre = intro.get("genre") or "Drama"
    medium = intro.get("medium") or "35mm Feature Film (Anamorphic)"
    return (
        f"Dialogue\n"
        f"\"{dialogue}\"\n\n"
        f"Genre + Medium Signaled\n"
        f"Genre: {genre}\n\n"
        f"Medium: {medium}"
    )


def generate_clip(writer_id: str, intro: dict, still_path: Path,
                  out_path: Path, seed: int = 42) -> bool:
    """Generate i2v clip via ltx2-3 with NATIVE audio from prompt. Returns True on success."""
    prompt = build_video_prompt(intro)
    print(f"  [2/2] LTX-2.3 i2v (native audio): {DURATION_S}s")
    print(f"    Prompt: {prompt[:80]}...")

    try:
        data = {
            "prompt": prompt,
            "negative_prompt": VIDEO_NEG,
            "seed": str(seed),
            "duration": str(max(2, DURATION_S)),
        }
        with open(still_path, "rb") as img_fh:
            files = {
                "first_frame": (still_path.name, img_fh, "image/jpeg"),
            }
            video_bytes = submit_and_wait(VIDEO_WORKFLOW, data, files=files, timeout=TIMEOUT_VIDEO)
    except Exception as e:
        print(f"  ERROR (clip): {e}")
        return False

    if len(video_bytes) < MIN_VIDEO_BYTES:
        print(f"  ERROR: clip too small ({len(video_bytes)} bytes)")
        return False

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_bytes(video_bytes)
    print(f"  Clip OK: {len(video_bytes)/1024:.0f}KB → {out_path.name}")
    return True

# ─── Writer pipeline ──────────────────────────────────────────────────────────

def process_writer(writer_id: str, intros_dir: Path, stills_dir: Path,
                   clips_dir: Path, resume: bool = False,
                   stills_only: bool = False, clips_only: bool = False) -> str:
    """Run full pipeline for one writer. Returns 'ok', 'skipped', or 'failed'."""
    md_path = intros_dir / f"{writer_id}.md"
    if not md_path.exists():
        print(f"ERROR: {md_path} not found")
        return "failed"

    still_path = stills_dir / f"{writer_id}.jpg"
    clip_path = clips_dir / f"{writer_id}.mp4"

    if resume and still_path.exists() and clip_path.exists():
        if still_path.stat().st_size > MIN_IMAGE_BYTES and clip_path.stat().st_size > MIN_VIDEO_BYTES:
            print(f"SKIP (exists): {writer_id}")
            return "skipped"

    print(f"\n{'='*60}")
    print(f"WRITER: {writer_id}")
    print(f"{'='*60}")

    intro = parse_intro_md(md_path)

    # Seed from writer id number (first digits)
    seed_match = re.match(r'^(\d+)', writer_id)
    seed = int(seed_match.group(1)) * 137 + 42 if seed_match else 42

    t0 = time.time()

    # Step 1: Still
    if not clips_only:
        if resume and still_path.exists() and still_path.stat().st_size > MIN_IMAGE_BYTES:
            print(f"  [1/2] Still exists, reusing.")
        else:
            if not generate_still(writer_id, intro, still_path, seed=seed):
                return "failed"
        if stills_only:
            return "ok"

    # Step 2: Clip (LTX-2.3 native audio from prompt)
    if clips_only:
        if not still_path.exists() or still_path.stat().st_size < MIN_IMAGE_BYTES:
            print(f"  ERROR: still missing for {writer_id}")
            return "failed"
        if resume and clip_path.exists() and clip_path.stat().st_size > MIN_VIDEO_BYTES:
            print(f"  [2/2] Clip exists, skipping.")
            return "skipped"
    if not generate_clip(writer_id, intro, still_path, clip_path, seed=seed):
        return "failed"

    elapsed = time.time() - t0
    print(f"\n  DONE: {writer_id} in {elapsed:.0f}s")
    print(f"    Still:  {still_path} ({still_path.stat().st_size/1024:.0f}KB)")
    print(f"    Clip:   {clip_path} ({clip_path.stat().st_size/1024:.0f}KB)")
    return "ok"

# ─── Main ─────────────────────────────────────────────────────────────────────

def find_project_root():
    """Find the 260414-writer-introductions project root."""
    # Check current dir and parents for this specific project
    cwd = Path.cwd()
    for p in [cwd] + list(cwd.parents):
        candidate = p / "projects" / "260414-writer-introductions"
        if candidate.exists():
            return candidate
        # Also check if we're already inside the project
        if (p / "INTROS").exists() and (p / "BRIEF.md").exists():
            return p
    raise FileNotFoundError(
        "Could not find 260414-writer-introductions project. "
        "Run from codeywood root or the project directory."
    )


def main():
    ap = argparse.ArgumentParser(description="Generate writer intro stills + clips")
    group = ap.add_mutually_exclusive_group(required=True)
    group.add_argument("--writer", metavar="ID_SLUG",
                       help="Run single writer (e.g. 05_oskar-brandt)")
    group.add_argument("--all", action="store_true",
                       help="Run all writers in INTROS/")
    ap.add_argument("--resume", action="store_true",
                    help="Skip writers where both STILL and CLIP already exist")
    ap.add_argument("--preflight", action="store_true",
                    help="Show what would be done without making API calls")
    ap.add_argument("--stills-only", action="store_true", help="Generate z-image stills only")
    ap.add_argument("--clips-only", action="store_true", help="Generate LTX-2.3 clips only")
    args = ap.parse_args()

    project_root = find_project_root()
    intros_dir = project_root / "INTROS"
    stills_dir = project_root / "STILLS"
    clips_dir = project_root / "CLIPS"

    print(f"Project: {project_root}")
    print(f"INTROS:  {intros_dir}")
    print(f"STILLS:  {stills_dir}")
    print(f"CLIPS:   {clips_dir}")

    # Gather writer list
    if args.writer:
        writer_ids = [args.writer]
    else:
        md_files = sorted(intros_dir.glob("*.md"))
        writer_ids = [f.stem for f in md_files]

    print(f"Writers: {len(writer_ids)}")
    print()

    if args.preflight:
        print("PREFLIGHT — would process:")
        for wid in writer_ids:
            md = intros_dir / f"{wid}.md"
            exists = "EXISTS" if (stills_dir / f"{wid}.jpg").exists() else "missing"
            print(f"  {wid:40s}  still={exists}")
        sys.exit(0)

    # Health check
    if not health_check():
        print(f"ERROR: ComfyUI not reachable at {COMFYUI_BASE}")
        sys.exit(1)
    print(f"ComfyUI OK at {COMFYUI_BASE}\n")

    stills_dir.mkdir(parents=True, exist_ok=True)
    clips_dir.mkdir(parents=True, exist_ok=True)

    results = {}
    overall_start = time.time()

    for wid in writer_ids:
        status = process_writer(wid, intros_dir, stills_dir, clips_dir, resume=args.resume,
                                stills_only=args.stills_only, clips_only=args.clips_only)
        results[wid] = status

    total_elapsed = time.time() - overall_start
    ok = sum(1 for s in results.values() if s == "ok")
    skipped = sum(1 for s in results.values() if s == "skipped")
    failed = sum(1 for s in results.values() if s == "failed")

    print(f"\n{'='*60}")
    print(f"SUMMARY — {len(writer_ids)} writers in {total_elapsed/60:.1f}m")
    print(f"  OK: {ok}  Skipped: {skipped}  Failed: {failed}")
    print(f"{'='*60}")
    for wid, status in results.items():
        print(f"  {status.upper():8s}  {wid}")

    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
