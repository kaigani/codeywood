#!/usr/bin/env python3
"""
Incremental fixes on composited frames using qwen-edit-on-edit.

Fix targeted issues while preserving composition, lighting, and character.
"""

import sys
import time
from pathlib import Path

import requests

COMFYUI_BASE = "http://192.168.1.181:8100"

PROJECT = Path(__file__).resolve().parents[2] / "projects" / "stray-signal"
FRAMES_DIR = PROJECT / "PRODUCTION" / "EP01_v02" / "frames"


def submit_and_wait(workflow_id, params, files=None, timeout=600, poll_interval=3):
    """Submit a ComfyUI workflow job, poll until done, return binary result."""
    url = f"{COMFYUI_BASE}/workflows/{workflow_id}"
    if files:
        resp = requests.post(url, data=params, files=files)
    else:
        resp = requests.post(url, data=params)
    resp.raise_for_status()
    job = resp.json()
    job_id = job["job_id"]
    print(f"  Job submitted: {job_id}")

    deadline = time.time() + timeout
    polls = 0
    while time.time() < deadline:
        status = requests.get(f"{COMFYUI_BASE}/jobs/{job_id}").json()
        polls += 1
        if status["status"] == "completed":
            elapsed = time.time() - (deadline - timeout)
            print(f"  Completed in {elapsed:.1f}s")
            result = requests.get(f"{COMFYUI_BASE}/jobs/{job_id}/result")
            return result.content
        if status["status"] == "error":
            raise RuntimeError(f"Job {job_id} failed: {status.get('error')}")
        time.sleep(2 if polls <= 5 else poll_interval)

    raise TimeoutError(f"Job {job_id} did not complete within {timeout}s")


def qwen_fix(prompt, image_path, seed=42, steps=4):
    """Run qwen-image-edit on an existing frame (edit-on-edit mode)."""
    params = {"prompt": prompt, "seed": str(seed), "steps": str(steps)}
    with open(image_path, "rb") as fh:
        files = {"image": (Path(image_path).name, fh, "image/png")}
        return submit_and_wait("qwen-image-edit", params, files=files)


def save(data, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as f:
        f.write(data)
    print(f"  Saved: {path}")
    return path


def main():
    t0 = time.time()

    # Fix 1: Clip 07 — Replace desktop monitor with small handheld device
    print("\n[Fix 1] Clip 07 — Replace monitor with small handheld device on desk")
    src = FRAMES_DIR / "clip_07_tabs_appears_v1.png"
    if not src.exists():
        print(f"  ERROR: {src} not found")
        sys.exit(1)

    data = qwen_fix(
        prompt=(
            "Replace the computer monitor with a small handheld device lying "
            "flat on the desk. The device is brushed aluminum with a glass "
            "screen showing a small wireframe cyan cat. The device is about "
            "the size of a phone. Keep everything else the same — the boy, "
            "the desk lamp, the amber lighting, the room."
        ),
        image_path=src,
        seed=311,
    )
    save(data, FRAMES_DIR / "clip_07_tabs_appears_v2.png")

    # Fix 2: Clip 09 — Darken skin tone to match CU
    print("\n[Fix 2] Clip 09 — Adjust skin tone darker to match other shots")
    src = FRAMES_DIR / "clip_09_multitool_down_v1.png"

    data = qwen_fix(
        prompt=(
            "Make the boy's skin tone slightly darker and warmer — medium "
            "brown, matching the warm amber light. Keep everything else "
            "exactly the same — his pose, expression, clothing, the room, "
            "the desk, the lighting."
        ),
        image_path=src,
        seed=312,
    )
    save(data, FRAMES_DIR / "clip_09_multitool_down_v2.png")

    # Fix 3: Clip 17 — Make device more clearly a small handheld
    print("\n[Fix 3] Clip 17 — Refine device in hand to small aluminum device")
    src = FRAMES_DIR / "clip_17_he_goes_v1.png"

    data = qwen_fix(
        prompt=(
            "The object in his right hand should be a small brushed aluminum "
            "device with a faint cyan glow from its screen. About the size "
            "of a phone, held at his side. Keep everything else the same — "
            "the corridor, his pose, the lighting, his clothing."
        ),
        image_path=src,
        seed=313,
    )
    save(data, FRAMES_DIR / "clip_17_he_goes_v2.png")

    elapsed = time.time() - t0
    print(f"\n{'=' * 60}")
    print(f"3 fixes in {elapsed:.0f}s")
    print(f"Review v1 → v2 pairs in: {FRAMES_DIR}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
