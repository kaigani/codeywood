#!/usr/bin/env python3
"""
Test LTX-2 text-to-video (no start frame) to understand native prompt interpretation.

Sends 3 representative shots from SC01 v2:
  - Shot 1 (The Rope): texture/detail, static, no characters
  - Shot 2 (Gallows Square): crowd wide, slow push, no specific characters
  - Shot 7 (Mars — The Weight): character close-up, static, V.O.

Uses existing video_prompt fields first (baseline), then can test elaborated versions.
"""

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import requests
import yaml

# ─── Config ───────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).parent.parent.parent / "projects" / "pirate-romance"
SCENE_DIR = PROJECT_ROOT / "PRODUCTION" / "EP01" / "sc01"
SHOT_LIST = SCENE_DIR / "shot_list_v2.yaml"
OUTPUT_DIR = SCENE_DIR / "t2v_test"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

COMFYUI_URL = "http://192.168.1.181:8100"
WORKFLOW = "ltx2-t2v"
FPS = 25
TIMEOUT = 900

# Shots to test (by shot id) — pass --remaining to skip already-generated shots
TEST_SHOTS = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]

NEGATIVE_PROMPT = "blur, distort, low quality, cartoon, anime, deformed, extra limbs, text, watermark"


def duration_to_frame_count(seconds, fps=25):
    raw = round(seconds * fps) + 1
    return max(25, min(raw, 501))


def generate_t2v(prompt, frame_count, seed=None, width=1280, height=720):
    """Send a text-to-video request to ComfyUI."""
    url = f"{COMFYUI_URL}/workflows/{WORKFLOW}"
    data = {
        "prompt": prompt,
        "negative_prompt": NEGATIVE_PROMPT,
        "frame_count": str(frame_count),
        "width": str(width),
        "height": str(height),
    }
    if seed is not None:
        data["seed"] = str(seed)

    response = requests.post(url, data=data, timeout=TIMEOUT)

    if response.status_code == 200 and len(response.content) > 10000:
        return response.content
    else:
        print(f"  ERROR: HTTP {response.status_code}, {len(response.content)} bytes")
        if response.status_code != 200:
            print(f"  {response.text[:300]}")
        return None


def main():
    with open(SHOT_LIST) as f:
        shot_data = yaml.safe_load(f)

    shots = {s["id"]: s for s in shot_data.get("shots", [])}

    print(f"LTX-2 Text-to-Video Test")
    print(f"Workflow: {WORKFLOW} ({FPS}fps, {1280}x{720})")
    print(f"Output: {OUTPUT_DIR}")
    print(f"Testing shots: {TEST_SHOTS}")
    print()

    results = {}
    start_time = time.time()

    for i, shot_id in enumerate(TEST_SHOTS):
        shot = shots.get(shot_id)
        if not shot:
            print(f"SKIP: Shot {shot_id} not found")
            continue

        name = shot.get("name", f"shot_{shot_id}")
        duration = shot.get("duration", 8)
        video_prompt = shot.get("video_prompt", "").strip()
        frame_count = duration_to_frame_count(duration)

        safe_name = name.lower().replace(" ", "_").replace("—", "").replace("'", "").strip("_")
        output_name = f"t2v_{shot_id:02d}_{safe_name}"

        print(f"{'='*60}")
        print(f"--- {output_name} ({duration}s, {frame_count} frames) [{i+1}/{len(TEST_SHOTS)}] ---")
        print(f"{'='*60}")
        print(f"  Prompt ({len(video_prompt)} chars):")
        print(f"  {video_prompt[:200]}...")
        print()

        t0 = time.time()
        video_bytes = generate_t2v(
            prompt=video_prompt,
            frame_count=frame_count,
            width=1280,
            height=720,
        )
        elapsed = time.time() - t0

        if video_bytes:
            out_path = OUTPUT_DIR / f"{output_name}.mp4"
            with open(out_path, "wb") as f:
                f.write(video_bytes)

            meta = {
                "shot_id": shot_id,
                "shot_name": name,
                "duration_s": duration,
                "frame_count": frame_count,
                "workflow": WORKFLOW,
                "width": 1280,
                "height": 720,
                "video_prompt": video_prompt,
                "negative_prompt": NEGATIVE_PROMPT,
                "elapsed_s": round(elapsed, 1),
                "bytes": len(video_bytes),
                "mode": "t2v_baseline",
                "notes": "Using existing video_prompt from shot_list_v2.yaml — no start frame",
            }
            with open(out_path.with_suffix(".json"), "w") as f:
                json.dump(meta, f, indent=2)

            mb = len(video_bytes) / (1024 * 1024)
            print(f"  OK: {mb:.1f}MB, {elapsed:.1f}s")
            results[shot_id] = f"OK ({elapsed:.1f}s)"
        else:
            print(f"  FAILED")
            results[shot_id] = "FAILED"

        if i < len(TEST_SHOTS) - 1:
            elapsed_total = time.time() - start_time
            avg = elapsed_total / (i + 1)
            remaining = avg * (len(TEST_SHOTS) - i - 1)
            print(f"  [{i+1}/{len(TEST_SHOTS)} done, ~{remaining/60:.0f}m remaining]")
        print()

    # Summary
    total_elapsed = time.time() - start_time
    print(f"{'='*60}")
    print(f"SUMMARY — {len(TEST_SHOTS)} clips in {total_elapsed/60:.1f}m")
    print(f"{'='*60}")
    for shot_id in TEST_SHOTS:
        shot = shots.get(shot_id, {})
        name = shot.get("name", f"shot_{shot_id}")
        status = results.get(shot_id, "SKIPPED")
        print(f"  Shot {shot_id} ({name}): {status}")


if __name__ == "__main__":
    # Health check
    try:
        r = requests.get(f"{COMFYUI_URL}/health", timeout=5)
        if r.status_code != 200:
            print(f"ERROR: ComfyUI not healthy: {r.text}")
            sys.exit(1)
    except Exception as e:
        print(f"ERROR: ComfyUI not reachable at {COMFYUI_URL}: {e}")
        sys.exit(1)

    # Skip already-generated shots if --remaining flag is passed
    if "--remaining" in sys.argv:
        existing = set()
        for mp4 in OUTPUT_DIR.glob("t2v_*.mp4"):
            # Extract shot id from filename like t2v_01_the_rope.mp4
            parts = mp4.stem.split("_")
            if len(parts) >= 2:
                try:
                    existing.add(int(parts[1]))
                except ValueError:
                    pass
        TEST_SHOTS[:] = [s for s in TEST_SHOTS if s not in existing]
        if existing:
            print(f"Skipping already-generated shots: {sorted(existing)}")

    main()
