#!/usr/bin/env python3
"""
Round 3 fixes — final pass on remaining failures.

  04 — crack still shattered: edit-on-edit v3, fix crack only (skin tone is now OK)
  07 — TABS hologram: FLIP ORDER — build device+TABS first, then add Kai behind
  10 — TABS hologram: same flip strategy
  16 — map still colorful: drop datapad ref as base, describe map from scratch

Key insight for 07/10: when Kai is in base image, TABS always becomes a hologram.
When device_on is the base (proven by clip_11), TABS renders flat on screen.
Strategy: device_on + TABS → flat screen → then add Kai context behind it.

Usage:
  python3 fix_ep01_frames_r3.py
  python3 fix_ep01_frames_r3.py --clip 7
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

DEVICE_ON    = REFS / "object_refs" / "device_on.png"

TABS_DIR     = REFS / "object_refs" / "tabs_poses"
TABS_SITTING = TABS_DIR / "tabs_sitting_default.png"
TABS_READING = TABS_DIR / "tabs_reading_focused.png"

KAI_DIR       = REFS / "character_poses" / "kai"
KAI_CU_RIGHT  = KAI_DIR / "kai_cu_look_right.png"
KAI_WATCHING  = KAI_DIR / "kai_at_desk_watching.png"
KAI_HANDS_PAD = KAI_DIR / "kai_hands_datapad_pen.png"

CROPS        = REFS / "location_crops" / "EP01"
CROP_DESK    = CROPS / "housing_desk_amber.png"


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


def qwen_edit(prompt, image, image2=None, image3=None, seed=42, steps=4):
    params = {"prompt": prompt, "seed": str(seed), "steps": str(steps)}
    handles, files = [], {}
    try:
        fh = open(image, "rb"); handles.append(fh)
        files["image"] = (Path(image).name, fh, "image/png")
        if image2:
            fh2 = open(image2, "rb"); handles.append(fh2)
            files["image2"] = (Path(image2).name, fh2, "image/png")
        if image3:
            fh3 = open(image3, "rb"); handles.append(fh3)
            files["image3"] = (Path(image3).name, fh3, "image/png")
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
    print(f"\n{'='*60}\nCLIP {n:02d} R3 — {name}\n{'='*60}")


# ─── Fixes ────────────────────────────────────────────────────────────────────

def fix_04():
    """One targeted edit: hairline crack only. Skin tone is now OK from v3."""
    header(4, "device_crack_warmth — hairline crack fix")
    data = qwen_edit(
        prompt=(
            "In this image, the cracks in the device screen glass are too "
            "prominent — multiple fracture lines making it look shattered. "
            "Replace all the cracks with a single hairline crack: one thin, "
            "clean line running across the lower third of the screen glass — "
            "barely visible, like a stress fracture. Keep the hands, the skin "
            "tone, the device, and everything else exactly the same."
        ),
        image=FRAMES / "clip_04_device_crack_warmth_v3.png",
        seed=141,
    )
    save(data, FRAMES / "clip_04_device_crack_warmth_v4.png")


def fix_07():
    """
    Flip order: device_on + TABS first → flat screen proven.
    Then add Kai's face behind the device in second pass.
    """
    header(7, "tabs_appears_screen — flip order (device+TABS → add Kai)")

    print("\n  Stage 1: device_on as base + TABS sitting (proven flat-screen method)")
    stage1 = qwen_edit(
        prompt=(
            "Close-up of the device screen from image 1. On the screen, show "
            "the wireframe cyan cat from image 2 sitting and looking outward — "
            "displayed as a flat 2D image on the screen glass. The cat has "
            "angular geometric facets, electric cyan color, ears slightly too "
            "large. It studies the viewer with digital curiosity. The screen "
            "glows cyan. Device is a small handheld unit, brushed aluminum "
            "frame. Warm amber light touches the device edges from off-screen."
        ),
        image=DEVICE_ON,
        image2=TABS_SITTING,
        seed=731,
    )
    stage1_path = save(stage1, FRAMES / "clip_07_r3_stage1.png")

    print("\n  Stage 2: Widen composition — add Kai's face behind/beside device")
    data = qwen_edit(
        prompt=(
            "This image shows a handheld device screen with a wireframe cyan "
            "cat displayed on it. Widen the composition to show the scene: "
            "the device is on a desk in a small housing unit at night. The "
            "boy from image 2 is visible in the background, seated at the desk, "
            "his face illuminated — warm amber desk lamp on his left, cool cyan "
            "from the device screen on his right. His expression is watchful. "
            "The device with the cat on screen remains in the foreground in "
            "sharp focus. Split-focus composition: device screen sharp, boy's "
            "face soft or equally sharp. Keep the cat on the screen exactly."
        ),
        image=stage1_path,
        image2=KAI_CU_RIGHT,
        seed=732,
    )
    save(data, FRAMES / "clip_07_tabs_appears_v5.png")


def fix_10():
    """Same flip strategy as fix_07 — device+TABS first, Kai context second."""
    header(10, "tabs_reads_maps — flip order (device+TABS → add Kai)")

    print("\n  Stage 1: device_on as base + TABS reading (proven flat-screen method)")
    stage1 = qwen_edit(
        prompt=(
            "Close-up of the device screen from image 1. On the screen, show "
            "the wireframe cyan cat from image 2 navigating through a file "
            "directory — displayed as a flat 2D image on the screen glass. "
            "The cat moves methodically through the files, focused, not looking "
            "up. The screen displays a directory tree around the cat. "
            "Device is a small handheld unit. Amber light touches device edges."
        ),
        image=DEVICE_ON,
        image2=TABS_READING,
        seed=1031,
    )
    stage1_path = save(stage1, FRAMES / "clip_10_r3_stage1.png")

    print("\n  Stage 2: Add Kai watching from behind the device")
    data = qwen_edit(
        prompt=(
            "This image shows a handheld device screen with a wireframe cyan "
            "cat navigating files on it. Widen the composition: the device "
            "is on a desk in a small housing unit at night. The boy from "
            "image 2 is visible beside and behind the device, watching the "
            "screen. His expression: guarded but not hostile. He holds a "
            "datapad in one hand. Amber desk lamp behind him. Cyan glow from "
            "the screen on his face. The cat remains on the screen exactly "
            "as shown — flat, contained within the screen."
        ),
        image=stage1_path,
        image2=KAI_WATCHING,
        seed=1032,
    )
    save(data, FRAMES / "clip_10_tabs_reads_maps_v4.png")


def fix_16():
    """Drop datapad ref as base. Use hands ref only + pure text description of map."""
    header(16, "new_mark_on_map — hands-only ref, full map description")
    data = qwen_edit(
        prompt=(
            "Close-up of the hands from image 1 holding a battered handheld "
            "datapad. The screen of the datapad shows a hand-drawn sector map "
            "in BLACK AND WHITE ONLY — black ink lines on a white background, "
            "no color at all. The map is a strict engineering grid: horizontal "
            "and vertical lines forming rectangular numbered sectors. Sector "
            "labels are small printed numbers. One sector (labeled '12') has "
            "dense question marks written over it. The map looks exactly like "
            "a pencil-and-ink field survey, military grid, or engineer's sketch. "
            "A stylus pen is poised over Sector 12. A small device is tucked "
            "under the arm with a faint cyan glow at the edge. 4500K corridor "
            "fluorescent overhead. Stylized animation."
        ),
        image=KAI_HANDS_PAD,
        seed=1631,
    )
    save(data, FRAMES / "clip_16_new_mark_on_map_v4.png")


# ─── Main ─────────────────────────────────────────────────────────────────────

ALL_FIXES = {4: fix_04, 7: fix_07, 10: fix_10, 16: fix_16}


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
    invalid = [n for n in targets if n not in ALL_FIXES]
    if invalid:
        print(f"ERROR: No fix defined for: {invalid}"); sys.exit(1)

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
