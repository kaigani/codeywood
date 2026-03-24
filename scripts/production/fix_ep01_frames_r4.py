#!/usr/bin/env python3
"""
Round 4 — redesign clips 07 and 10 as face-only glow shots.

New shot design: device is held facing Kai (away from camera).
We see only the cyan glow washing up on his face. No screen visible.
Single-ref face shot — simplest generation approach.

  07 — Kai first sees TABS: wide eyes, cyan glow, amber behind
  10 — Kai watches TABS navigate: guarded yielding, cyan glow

Usage:
  python3 fix_ep01_frames_r4.py
  python3 fix_ep01_frames_r4.py --clip 7
"""

import argparse
import io
import sys
import time
from pathlib import Path

from PIL import Image
import requests

COMFYUI_BASE = "http://192.168.1.181:8100"
TARGET_W, TARGET_H = 1280, 720

PROJECT = Path(__file__).resolve().parents[2] / "projects" / "stray-signal"
REFS    = PROJECT / "REFERENCES"
FRAMES  = PROJECT / "PRODUCTION" / "EP01_v02" / "frames"

KAI_DIR      = REFS / "character_poses" / "kai"
KAI_CU_RIGHT = KAI_DIR / "kai_cu_look_right.png"


def submit_and_wait(workflow_id, params, files=None, timeout=600, poll_interval=3):
    url = f"{COMFYUI_BASE}/workflows/{workflow_id}"
    resp = requests.post(url, data=params, files=files) if files else requests.post(url, data=params)
    resp.raise_for_status()
    job = resp.json()
    job_id = job["job_id"]
    print(f"    job {job_id} (pos {job.get('position', '?')})")
    deadline = time.time() + timeout
    polls = 0
    while time.time() < deadline:
        s = requests.get(f"{COMFYUI_BASE}/jobs/{job_id}").json()
        polls += 1
        if s["status"] == "completed":
            print(f"    done in {time.time()-(deadline-timeout):.1f}s")
            return requests.get(f"{COMFYUI_BASE}/jobs/{job_id}/result").content
        if s["status"] == "error":
            raise RuntimeError(f"Job {job_id} failed: {s.get('error')}")
        time.sleep(2 if polls <= 5 else poll_interval)
    raise TimeoutError(f"Timed out after {timeout}s")


def qwen_edit(prompt, image, image2=None, seed=42, steps=4):
    params = {"prompt": prompt, "seed": str(seed), "steps": str(steps)}
    handles, files = [], {}
    try:
        fh = open(image, "rb"); handles.append(fh)
        files["image"] = (Path(image).name, fh, "image/png")
        if image2:
            fh2 = open(image2, "rb"); handles.append(fh2)
            files["image2"] = (Path(image2).name, fh2, "image/png")
        return submit_and_wait("qwen-image-edit", params, files=files)
    finally:
        for fh in handles: fh.close()


def normalize(png_bytes):
    img = Image.open(io.BytesIO(png_bytes))
    if img.size != (TARGET_W, TARGET_H):
        print(f"    resize {img.size} → {TARGET_W}x{TARGET_H}")
        img = img.resize((TARGET_W, TARGET_H), Image.LANCZOS)
    buf = io.BytesIO(); img.save(buf, "PNG")
    return buf.getvalue()


def save(data, path):
    data = normalize(data)
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as f: f.write(data)
    print(f"    saved: {path.name}")
    return path


def header(n, name):
    print(f"\n{'='*60}\nCLIP {n:02d} R4 — {name}\n{'='*60}")


def fix_07():
    """
    Kai's face lit by cyan glow from device held toward him.
    No screen, no TABS visible — just the glow on his face.
    First encounter: wide eyes, fully present.
    """
    header(7, "tabs_appears_screen — face shot, cyan glow only")
    data = qwen_edit(
        prompt=(
            "Film still, stylized sci-fi animation. Close-up of the boy from "
            "image 1. He is seated at a desk at night holding a device in his "
            "hands below frame, screen facing toward him. The device screen is "
            "NOT visible — only its light. Cool cyan glow emanates upward from "
            "below, washing across his face, hands, and chest. Warm amber desk "
            "lamp provides secondary light from behind and to his left. "
            "Dual lighting: amber on left cheek, cool cyan on right. "
            "His eyes are wide open, studying what he sees on the screen. "
            "Expression: first encounter — neither frightened nor excited, "
            "fully present. Housing unit interior, nighttime. No device screen "
            "visible in frame."
        ),
        image=KAI_CU_RIGHT,
        seed=741,
    )
    save(data, FRAMES / "clip_07_tabs_appears_v6.png")


def fix_10():
    """
    Kai's face lit by cyan glow — guarded watch, then yielding.
    Same glow setup, different emotional register from clip 07.
    """
    header(10, "tabs_reads_maps — face shot, cyan glow only")
    data = qwen_edit(
        prompt=(
            "Film still, stylized sci-fi animation. Close-up of the boy from "
            "image 1. He is seated at a desk at night, holding a device in "
            "his hands below frame, screen facing toward him. The device screen "
            "is NOT visible — only its cool cyan light washing upward across "
            "his face. Warm amber desk lamp behind him and to his left. "
            "Dual lighting: amber rim light behind, cyan fill from below. "
            "Expression: guarded but not hostile — someone watching carefully, "
            "the beginning of trust. His jaw is relaxed. Eyes steady on the "
            "screen. The cyan light is the only cool tone in an otherwise amber "
            "room. Housing unit interior, nighttime. No device screen visible."
        ),
        image=KAI_CU_RIGHT,
        seed=1041,
    )
    save(data, FRAMES / "clip_10_tabs_reads_maps_v5.png")


ALL_FIXES = {7: fix_07, 10: fix_10}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--clip", help="Comma-separated clip numbers")
    args = parser.parse_args()

    try:
        h = requests.get(f"{COMFYUI_BASE}/health", timeout=5).json()
        if not h.get("comfyui_reachable"):
            print("ERROR: ComfyUI not reachable"); sys.exit(1)
        print("ComfyUI: OK")
    except Exception as e:
        print(f"ERROR: {e}"); sys.exit(1)

    targets = [int(x.strip()) for x in args.clip.split(",")] if args.clip else sorted(ALL_FIXES)
    print(f"\nFixing clips: {targets}")
    t0 = time.time()
    results = {}
    for n in targets:
        try:
            ALL_FIXES[n](); results[n] = "OK"
        except Exception as e:
            print(f"\nERROR clip {n}: {e}"); results[n] = f"FAILED: {e}"

    elapsed = time.time() - t0
    print(f"\n{'='*60}\nDONE — {len(targets)} clips in {elapsed/60:.1f}m")
    for n in targets:
        print(f"  clip {n:02d}: {results.get(n, 'SKIPPED')}")
    print("="*60)


if __name__ == "__main__":
    main()
