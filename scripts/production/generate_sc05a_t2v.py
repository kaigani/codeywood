#!/usr/bin/env python3
"""
Generate LTX-2 text-to-video clips for SC05a — Underwater: The Dive.
T2V pipeline — no start frames needed.
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
SCENE_DIR = PROJECT_ROOT / "PRODUCTION" / "EP01" / "sc05a"
SHOT_LIST = SCENE_DIR / "shot_list.yaml"
OUTPUT_DIR = SCENE_DIR / "clips"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

COMFYUI_URL = "http://192.168.1.181:8100"
WORKFLOW = "ltx2-t2v"
FPS = 25
TIMEOUT = 900

NEGATIVE_PROMPT = (
    "blur, distort, low quality, cartoon, anime, deformed, extra limbs, "
    "text, watermark, modern clothing, drowning, panic, struggling, distress"
)


def duration_to_frame_count(seconds, fps=25):
    raw = round(seconds * fps) + 1
    return max(25, min(raw, 321))


def generate_t2v(prompt, frame_count, seed=None, width=1280, height=720):
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
        data = yaml.safe_load(f)

    shots = data.get("shots", [])
    total = len(shots)
    results = {}
    start_time = time.time()

    print(f"Generating {total} LTX-2 t2v clips for SC05a")
    print(f"Output: {OUTPUT_DIR}")
    print(f"Backend: ComfyUI {WORKFLOW} ({FPS}fps, 1280x720)")
    print()

    for i, shot in enumerate(shots):
        shot_id = shot["id"]
        name = shot.get("name", f"shot_{shot_id}")
        duration = shot.get("duration", 8)
        video_prompt = shot.get("video_prompt", "").strip()
        frame_count = duration_to_frame_count(duration)

        if not video_prompt:
            print(f"SKIP: No video prompt for shot {shot_id}")
            continue

        safe_name = name.lower().replace(" ", "_").replace("—", "").replace("'", "").strip("_")
        output_name = f"clip{shot_id:02d}_{safe_name}"

        print(f"{'='*60}")
        print(f"--- {output_name} ({duration}s, {frame_count} frames) [{i+1}/{total}] ---")
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
                "pipeline": "t2v",
            }
            with open(out_path.with_suffix(".json"), "w") as f:
                json.dump(meta, f, indent=2)

            mb = len(video_bytes) / (1024 * 1024)
            print(f"  OK: {mb:.1f}MB, {elapsed:.1f}s")
            results[shot_id] = f"OK ({elapsed:.1f}s)"
        else:
            print(f"  FAILED")
            results[shot_id] = "FAILED"

        if i < total - 1:
            elapsed_total = time.time() - start_time
            avg = elapsed_total / (i + 1)
            remaining = avg * (total - i - 1)
            print(f"  [{i+1}/{total} done, ~{remaining/60:.0f}m remaining]")
        print()

    # Summary
    total_elapsed = time.time() - start_time
    print(f"{'='*60}")
    print(f"SUMMARY — {total} clips in {total_elapsed/60:.1f}m")
    print(f"{'='*60}")
    for shot in shots:
        sid = shot["id"]
        name = shot.get("name", f"shot_{sid}")
        status = results.get(sid, "SKIPPED")
        print(f"  {name}: {status}")


if __name__ == "__main__":
    try:
        r = requests.get(f"{COMFYUI_URL}/health", timeout=5)
        if r.status_code != 200:
            print(f"ERROR: ComfyUI not healthy: {r.text}")
            sys.exit(1)
    except Exception as e:
        print(f"ERROR: ComfyUI not reachable at {COMFYUI_URL}: {e}")
        sys.exit(1)
    main()
