#!/usr/bin/env python3
"""
Screen-test clip generator using ComfyUI workflow `ltx2-3`.

Differs from generate_t2v.py:
- Uses ltx2-3 workflow (supports audio generation from prompt + static_camera)
- Input: `duration` (int seconds) instead of `frame_count`
- Passes `static_camera` float (default 1.0 for locked-off screen tests)
- Output dir: clips_screen_test

Usage:
    python3 scripts/production/generate_screen_test.py --scene sc01 [--resume]
"""

import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import requests
import yaml

DEFAULT_WORKFLOW = "ltx2-3"
DEFAULT_WIDTH = 1280
DEFAULT_HEIGHT = 720
DEFAULT_DURATION = 7
DEFAULT_STATIC = 1.0
DEFAULT_TIMEOUT = 1200
MIN_FILE_SIZE = 10000

DEFAULT_NEGATIVE = (
    "blurry, low resolution, garbled mess, compression artifacts, glitch, "
    "stop motion, still image, pixelated, robotic voice, oversaturated, "
    "watermark, subtitles, text overlay, mockumentary, documentary interview, fleabag"
)


def safe_filename(name):
    return (name.lower().replace(" ", "_").replace("—", "").replace("'", "")
            .replace(":", "").replace("/", "_").strip("_"))


def find_project_root():
    cwd = Path.cwd()
    for p in [cwd] + list(cwd.parents):
        if (p / "PROJECT_CONFIG.yaml").exists():
            return p
    raise FileNotFoundError("Could not find PROJECT_CONFIG.yaml")


def submit_and_poll(comfyui_url, prompt, negative_prompt, duration, seed,
                    width, height, static_camera, timeout):
    url = f"{comfyui_url}/workflows/{DEFAULT_WORKFLOW}"
    data = {
        "prompt": prompt,
        "negative_prompt": negative_prompt,
        "duration": str(duration),
        "width": str(width),
        "height": str(height),
        "static_camera": str(static_camera),
    }
    if seed is not None:
        data["seed"] = str(seed)

    try:
        response = requests.post(url, data=data, timeout=timeout)
    except Exception as e:
        print(f"  ERROR: submit failed: {e}")
        return None

    if response.status_code not in (200, 202):
        print(f"  ERROR: HTTP {response.status_code}: {response.text[:200]}")
        return None

    if response.status_code == 200 and len(response.content) > MIN_FILE_SIZE \
            and "video" in response.headers.get("content-type", ""):
        return response.content

    try:
        job_id = response.json().get("job_id")
    except Exception:
        print(f"  ERROR: no job_id in response: {response.text[:200]}")
        return None

    if not job_id:
        print(f"  ERROR: no job_id returned")
        return None

    print(f"  Job queued: {job_id}, polling...")
    elapsed = 0
    poll_interval = 5
    while elapsed < timeout:
        time.sleep(poll_interval)
        elapsed += poll_interval
        try:
            poll = requests.get(f"{comfyui_url}/jobs/{job_id}", timeout=30)
        except Exception:
            continue
        if poll.status_code != 200:
            continue
        try:
            sd = poll.json()
            status = sd.get("status", "")
        except Exception:
            ct = poll.headers.get("content-type", "")
            if "video" in ct and len(poll.content) > MIN_FILE_SIZE:
                return poll.content
            continue
        if status == "completed":
            r = requests.get(f"{comfyui_url}/jobs/{job_id}/result", timeout=120)
            if r.status_code == 200 and len(r.content) > MIN_FILE_SIZE:
                return r.content
            print(f"  ERROR: result fetch failed HTTP {r.status_code}")
            return None
        if status in ("failed", "error"):
            print(f"  ERROR: job failed: {sd.get('error', 'unknown')}")
            return None
        if elapsed % 30 == 0:
            pos = sd.get("position", "?")
            print(f"    ... waiting ({elapsed}s, status={status}, position={pos})")

    print(f"  ERROR: timed out after {timeout}s")
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scene", required=True, help="Scene ID (e.g., sc01)")
    ap.add_argument("--resume", action="store_true", help="Skip existing clips")
    ap.add_argument("--shots", help="Comma-separated shot IDs to run (e.g., 1,2,5)")
    ap.add_argument("--preflight", action="store_true", help="Preflight only")
    ap.add_argument("--comfyui-url", default="http://192.168.1.181:8100")
    args = ap.parse_args()

    project_root = find_project_root()
    scene_dir = project_root / "PRODUCTION" / "EP01" / args.scene
    yaml_path = scene_dir / "shot_list_t2v.yaml"
    if not yaml_path.exists():
        print(f"ERROR: {yaml_path} not found")
        sys.exit(1)

    with open(yaml_path) as f:
        data = yaml.safe_load(f)
    shots = data.get("shots", [])
    meta = data.get("t2v_metadata", {})
    negative = meta.get("negative_prompt", DEFAULT_NEGATIVE)
    width = meta.get("default_width", DEFAULT_WIDTH)
    height = meta.get("default_height", DEFAULT_HEIGHT)
    default_duration = meta.get("default_duration", DEFAULT_DURATION)
    static_camera = meta.get("default_static_camera", DEFAULT_STATIC)

    shot_filter = None
    if args.shots:
        shot_filter = set(int(x) for x in args.shots.split(","))
        shots = [s for s in shots if s["id"] in shot_filter]

    output_dir = scene_dir / "clips_screen_test"
    output_dir.mkdir(parents=True, exist_ok=True)

    if args.preflight:
        print(f"PREFLIGHT — {args.scene}")
        print(f"Shots: {len(shots)}, workflow: {DEFAULT_WORKFLOW}")
        print(f"Default duration: {default_duration}s, static_camera: {static_camera}")
        print(f"Resolution: {width}x{height}")
        for s in shots[:3]:
            print(f"  {s['id']}: {s.get('name')} ({len(s.get('video_prompt') or s.get('prompt', ''))} chars)")
        print(f"  ... ({len(shots)} total)")
        sys.exit(0)

    total = len(shots)
    results = {}
    start = time.time()

    print(f"Generating {total} screen-test clips via ComfyUI {DEFAULT_WORKFLOW}")
    print(f"Output: {output_dir}")
    print()

    for i, shot in enumerate(shots):
        sid = shot["id"]
        name = shot.get("name", f"shot_{sid}")
        duration = shot.get("duration", default_duration)
        prompt = (shot.get("video_prompt") or shot.get("prompt") or "").strip()
        seed = shot.get("seed")
        sc = shot.get("static_camera", static_camera)

        slug = safe_filename(name)
        output_name = f"clip{sid:02d}_{slug}"
        out_path = output_dir / f"{output_name}.mp4"

        if args.resume and out_path.exists() and out_path.stat().st_size > MIN_FILE_SIZE:
            print(f"SKIP (exists): {output_name}")
            results[sid] = "SKIPPED"
            continue

        if not prompt:
            print(f"SKIP (no prompt): {output_name}")
            results[sid] = "SKIPPED (no prompt)"
            continue

        print(f"{'=' * 60}")
        print(f"--- {output_name} ({duration}s) [{i + 1}/{total}] ---")
        print(f"{'=' * 60}")
        print(f"  Prompt ({len(prompt)} chars): {prompt[:160]}...")

        t0 = time.time()
        vb = submit_and_poll(args.comfyui_url, prompt, negative, duration, seed,
                             width, height, sc, DEFAULT_TIMEOUT)
        elapsed = time.time() - t0

        if vb:
            with open(out_path, "wb") as f:
                f.write(vb)
            with open(out_path.with_suffix(".json"), "w") as f:
                json.dump({
                    "shot_id": sid, "shot_name": name, "duration_s": duration,
                    "workflow": DEFAULT_WORKFLOW, "width": width, "height": height,
                    "static_camera": sc, "video_prompt": prompt,
                    "negative_prompt": negative, "seed": seed,
                    "elapsed_s": round(elapsed, 1), "bytes": len(vb),
                    "generated_at": datetime.now().isoformat(),
                }, f, indent=2)
            print(f"  OK: {len(vb)/1024/1024:.1f}MB, {elapsed:.1f}s")
            results[sid] = "OK"
        else:
            print(f"  FAILED after {elapsed:.1f}s")
            results[sid] = "FAILED"

    total_elapsed = time.time() - start
    print()
    print("=" * 60)
    print(f"SUMMARY — {args.scene}: {total} clips in {total_elapsed/60:.1f}m")
    print("=" * 60)
    for sid, status in sorted(results.items()):
        name = next((s.get("name") for s in shots if s["id"] == sid), f"shot_{sid}")
        print(f"  {sid:02d} {name}: {status}")


if __name__ == "__main__":
    main()
