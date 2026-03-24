#!/usr/bin/env python3
"""
Round 2 fixes for EP01 frames — targeted re-runs on clips that still failed.

Remaining issues:
  04 — skin tone too dark, crack too shattered (edit-on-edit v2 to fix skin only)
  07 — TABS hologram again: use clip_11_v2 as screen-rendering reference
  10 — TABS hologram again: same fix as 07
  14 — paw scale wrong (giant hand); revert to original, fix only the crack
  16 — map still decorative; force B&W engineering grid language

Usage:
  python3 fix_ep01_frames_r2.py               # all
  python3 fix_ep01_frames_r2.py --clip 7      # one clip
  python3 fix_ep01_frames_r2.py --clip 7,10   # multiple
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

DEVICE_OFF   = REFS / "object_refs" / "device_off.png"
DEVICE_ON    = REFS / "object_refs" / "device_on.png"
DATAPAD      = REFS / "object_refs" / "datapad_maps.png"

TABS_DIR     = REFS / "object_refs" / "tabs_poses"
TABS_SITTING = TABS_DIR / "tabs_sitting_default.png"
TABS_READING = TABS_DIR / "tabs_reading_focused.png"
TABS_PAW     = TABS_DIR / "tabs_paw_reaching.png"

KAI_DIR       = REFS / "character_poses" / "kai"
KAI_HANDS_DEV = KAI_DIR / "kai_hands_holding_device.png"
KAI_HANDS_PAD = KAI_DIR / "kai_hands_datapad_pen.png"

CROPS     = REFS / "location_crops" / "EP01"
CROP_DESK = CROPS / "housing_desk_amber.png"

# Clip 11 v2 is our proof that TABS-on-flat-screen works — use as reference
TABS_ON_SCREEN_REF = FRAMES / "clip_11_tabs_points_northeast_v2.png"


# ─── ComfyUI helpers ──────────────────────────────────────────────────────────

def submit_and_wait(workflow_id, params, files=None, timeout=600, poll_interval=3):
    url = f"{COMFYUI_BASE}/workflows/{workflow_id}"
    resp = requests.post(url, data=params, files=files) if files else requests.post(url, data=params)
    resp.raise_for_status()
    job = resp.json()
    job_id = job["job_id"]
    print(f"    job {job_id} (queue pos {job.get('position', '?')})")
    deadline = time.time() + timeout
    polls = 0
    while time.time() < deadline:
        status = requests.get(f"{COMFYUI_BASE}/jobs/{job_id}").json()
        polls += 1
        if status["status"] == "completed":
            elapsed = time.time() - (deadline - timeout)
            print(f"    done in {elapsed:.1f}s")
            return requests.get(f"{COMFYUI_BASE}/jobs/{job_id}/result").content
        if status["status"] == "error":
            raise RuntimeError(f"Job {job_id} failed: {status.get('error')}")
        time.sleep(2 if polls <= 5 else poll_interval)
    raise TimeoutError(f"Job {job_id} timed out after {timeout}s")


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
        for fh in handles:
            fh.close()


def normalize(png_bytes, w=TARGET_W, h=TARGET_H):
    img = Image.open(io.BytesIO(png_bytes))
    if img.size != (w, h):
        print(f"    resize {img.size} → {w}x{h}")
        img = img.resize((w, h), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, "PNG")
    return buf.getvalue()


def save(data, path, norm=True):
    data = normalize(data) if norm else data
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as f:
        f.write(data)
    print(f"    saved: {path.name}")
    return path


def header(n, name):
    print(f"\n{'='*60}")
    print(f"CLIP {n:02d} R2 — {name}")
    print(f"{'='*60}")


# ─── Fixes ────────────────────────────────────────────────────────────────────

def fix_04():
    """Edit-on-edit v2: fix skin tone only, keep form factor."""
    header(4, "device_crack_warmth — fix skin tone → light brown")
    data = qwen_edit(
        prompt=(
            "In this image, the hands holding the device have skin that is too "
            "dark. Change the skin tone of the hands to light brown — medium warm "
            "tone, like the character shown in image 2. Keep the device, the "
            "crack in the glass, the warm amber glow, and everything else exactly "
            "the same. Only change: the hand skin tone."
        ),
        image=FRAMES / "clip_04_device_crack_warmth_v2.png",
        image2=KAI_HANDS_DEV,
        seed=142,
    )
    save(data, FRAMES / "clip_04_device_crack_warmth_v3.png")


def fix_07():
    """
    Anti-hologram pass: use clip_11_v2 as flat-screen reference.
    clip_11 proved TABS can render as a flat 2D screen image.
    Pass it as image2 so the model sees the correct rendering mode.
    """
    header(7, "tabs_appears_screen — anti-hologram, flat screen ref")

    print("\n  Stage 1: Compose Kai at desk (same as R1 stage 1)")
    stage1 = qwen_edit(
        prompt=(
            "Film still, stylized sci-fi animation. Close-up of the boy from "
            "image 2 sitting at the desk from this room (image 1). He is "
            "looking down at a small handheld device on the desk in front of "
            "him. The device screen glows cyan. Dual lighting: warm amber desk "
            "lamp from his left, cool cyan from the device screen on his right. "
            "His face is half warm gold, half cool cyan. Watchful expression. "
            "Nighttime interior."
        ),
        image=CROP_DESK,
        image2=KAI_HANDS_DEV,
        seed=711,
    )
    stage1_path = save(stage1, FRAMES / "clip_07_r2_stage1.png")

    print("\n  Stage 2: Add TABS on flat device screen (anti-hologram)")
    data = qwen_edit(
        prompt=(
            "In this image, the boy looks at a small handheld device on the "
            "desk. On the device screen, show the wireframe cyan cat from "
            "image 3 — displayed as a flat 2D image on the screen glass, "
            "exactly like the screen display in image 2. The cat is NOT a "
            "hologram. It is NOT projected into the room. It is a flat image "
            "viewed through the device screen glass, contained entirely within "
            "the screen rectangle. Keep the boy, desk, and room the same."
        ),
        image=stage1_path,
        image2=TABS_ON_SCREEN_REF,
        image3=TABS_SITTING,
        seed=712,
    )
    save(data, FRAMES / "clip_07_tabs_appears_v4.png")


def fix_10():
    """
    Anti-hologram pass for tabs_reads_maps. Same strategy as fix_07.
    """
    header(10, "tabs_reads_maps — anti-hologram, flat screen ref")

    print("\n  Stage 1: Compose Kai watching device at desk")
    stage1 = qwen_edit(
        prompt=(
            "Film still, stylized sci-fi animation. Medium close-up. The boy "
            "from image 2 sits at the desk in this room (image 1). He is "
            "looking at a small handheld device on the desk — the device screen "
            "glows cyan. His expression is guarded but not hostile, watching "
            "carefully. Amber desk lamp behind him. He holds a datapad in one "
            "hand. Nighttime."
        ),
        image=CROP_DESK,
        image2=KAI_HANDS_DEV,
        seed=1011,
    )
    stage1_path = save(stage1, FRAMES / "clip_10_r2_stage1.png")

    print("\n  Stage 2: Add TABS on flat device screen (anti-hologram)")
    data = qwen_edit(
        prompt=(
            "In this image, the boy watches a small handheld device on the "
            "desk. On the device screen, show the wireframe cyan cat from "
            "image 3 navigating through files — displayed as a flat 2D image "
            "on the screen glass, exactly like the screen display in image 2. "
            "The cat is NOT a hologram. It is NOT projected into the room. "
            "It is a flat image on the device screen, contained within the "
            "screen rectangle. The cat is focused and methodical, not looking "
            "up. Keep the boy, desk, and room the same."
        ),
        image=stage1_path,
        image2=TABS_ON_SCREEN_REF,
        image3=TABS_READING,
        seed=1012,
    )
    save(data, FRAMES / "clip_10_tabs_reads_maps_v3.png")


def fix_14():
    """
    Revert to original clip_14 (correct paw scale, correct composition).
    Single targeted edit: reduce shattered glass to hairline crack only.
    """
    header(14, "tabs_paw_at_glass — fix crack on original (correct paw scale)")
    data = qwen_edit(
        prompt=(
            "In this image, the crack in the device screen glass is too "
            "prominent — it appears shattered with many fracture lines. "
            "Reduce it to a single thin hairline crack running across the lower "
            "edge of the screen — subtle, barely visible, like a stress fracture. "
            "Keep everything else exactly the same: the wireframe cat, the cat's "
            "paw position, the sleeping boy visible behind the glass, the cyan "
            "lighting, the composition."
        ),
        image=FRAMES / "clip_14_tabs_paw_at_glass.png",
        seed=1411,
    )
    save(data, FRAMES / "clip_14_tabs_paw_at_glass_v3.png")


def fix_16():
    """Force B&W utilitarian engineering grid — no color, no decoration."""
    header(16, "new_mark_on_map — B&W utilitarian sector grid")
    data = qwen_edit(
        prompt=(
            "Close-up of the hands from image 2 holding the battered datapad "
            "from image 1. The datapad map must be: black ink on white or "
            "cream paper ONLY — no color whatsoever. The map is a utilitarian "
            "engineering grid: straight ruled lines dividing the surface into "
            "numbered rectangular sectors, small handwritten annotations, "
            "question marks clustered in one sector (Sector 12). It looks like "
            "a military survey map or engineer's field sketch — functional, "
            "obsessive, zero decoration. A pen is poised over Sector 12. "
            "A device with faint cyan glow is tucked under the arm at frame "
            "edge. 4500K fluorescent corridor light. Stylized animation."
        ),
        image=DATAPAD,
        image2=KAI_HANDS_PAD,
        seed=1611,
    )
    save(data, FRAMES / "clip_16_new_mark_on_map_v3.png")


# ─── Main ─────────────────────────────────────────────────────────────────────

ALL_FIXES = {4: fix_04, 7: fix_07, 10: fix_10, 14: fix_14, 16: fix_16}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--clip", help="Comma-separated clip numbers (e.g. 7,10)")
    args = parser.parse_args()

    try:
        h = requests.get(f"{COMFYUI_BASE}/health", timeout=5).json()
        if not h.get("comfyui_reachable"):
            print("ERROR: ComfyUI not reachable"); sys.exit(1)
        print("ComfyUI: OK")
    except Exception as e:
        print(f"ERROR: {e}"); sys.exit(1)

    if not TABS_ON_SCREEN_REF.exists():
        print(f"ERROR: flat-screen reference not found: {TABS_ON_SCREEN_REF}")
        sys.exit(1)

    targets = [int(x.strip()) for x in args.clip.split(",")] if args.clip else sorted(ALL_FIXES)
    invalid = [n for n in targets if n not in ALL_FIXES]
    if invalid:
        print(f"ERROR: No fix defined for clip(s): {invalid}"); sys.exit(1)

    print(f"\nFixing clips: {targets}")
    t0 = time.time()
    results = {}

    for n in targets:
        try:
            ALL_FIXES[n]()
            results[n] = "OK"
        except Exception as e:
            print(f"\nERROR clip {n}: {e}")
            results[n] = f"FAILED: {e}"

    elapsed = time.time() - t0
    print(f"\n{'='*60}")
    print(f"DONE — {len(targets)} clips in {elapsed/60:.1f}m")
    for n in targets:
        print(f"  clip {n:02d}: {results.get(n, 'SKIPPED')}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
