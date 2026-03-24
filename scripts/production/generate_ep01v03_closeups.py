#!/usr/bin/env python3
"""
EP01 v03 — Generate close-up variants of location panels using
PIL center-crop → qwen-image-edit upscale.

This replaces the failed zoom=20 multiangle attempts. The qwen-multiangle
endpoint doesn't support zoom > 10, so we simulate close-ups by cropping
the center 60% of each source panel and upscaling with qwen-edit.

Output goes to location_angles/ alongside the multiangle variants.
"""

import io
import sys
import time
from pathlib import Path

from PIL import Image
import requests

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
COMFYUI_BASE = "http://192.168.1.181:8100"

PROJECT = Path(__file__).resolve().parents[2] / "projects" / "stray-signal"
PANELS_DIR = PROJECT / "PRODUCTION" / "EP01_v03" / "location_panels"
OUTPUT_DIR = PROJECT / "PRODUCTION" / "EP01_v03" / "location_angles"
CROPS_DIR = OUTPUT_DIR / "closeup_crops"

STYLE = (
    "Stylized sci-fi animation, graphic novel rendering with cinematic lighting, "
    "visible texture on concrete and metal surfaces, desaturated brutalist world "
    "with selective color accents. "
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def submit_and_wait(workflow_id, params, files=None, timeout=600):
    url = f"{COMFYUI_BASE}/workflows/{workflow_id}"
    if files:
        resp = requests.post(url, data=params, files=files)
    else:
        resp = requests.post(url, data=params)
    resp.raise_for_status()
    job = resp.json()
    job_id = job["job_id"]
    start = time.time()
    deadline = start + timeout
    while time.time() < deadline:
        status = requests.get(f"{COMFYUI_BASE}/jobs/{job_id}").json()
        st = status.get("status", "unknown")
        if st == "completed":
            elapsed = time.time() - start
            print(f"    Done ({elapsed:.0f}s)")
            return requests.get(f"{COMFYUI_BASE}/jobs/{job_id}/result").content
        if st in ("error", "failed"):
            raise RuntimeError(f"Job {job_id} failed: {status.get('error')}")
        time.sleep(3)
    raise TimeoutError(f"Timeout on {job_id}")


def qwen_edit(prompt, image_path, seed=42, steps=4):
    params = {"prompt": prompt, "seed": str(seed), "steps": str(steps)}
    fh = open(image_path, "rb")
    try:
        files = {"image": (Path(image_path).name, fh, "image/png")}
        return submit_and_wait("qwen-image-edit", params, files=files)
    finally:
        fh.close()


def center_crop(image_path, ratio=0.6):
    """Crop the center portion of an image (default 60%)."""
    img = Image.open(image_path)
    w, h = img.size
    new_w = int(w * ratio)
    new_h = int(h * ratio)
    left = (w - new_w) // 2
    top = (h - new_h) // 2
    return img.crop((left, top, left + new_w, top + new_h))


def save_pil(img, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path, format="PNG")
    print(f"    Saved crop: {path.name} ({img.size[0]}x{img.size[1]})")
    return path


def save_bytes(data, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as f:
        f.write(data)
    size = Image.open(io.BytesIO(data)).size
    print(f"    Saved: {path.name} ({size[0]}x{size[1]})")
    return path


# ---------------------------------------------------------------------------
# Close-up jobs — center-crop → upscale for each failed zoom variant
# ---------------------------------------------------------------------------
CLOSEUP_JOBS = [
    {
        "name": "grid_corridor_close",
        "source": PANELS_DIR / "grid_corridor_top_left.png",
        "prompt": (
            STYLE +
            "Close-up detail of a maintenance corridor. Fluorescent strip lighting "
            "on ceiling. Polymer floor surface texture. Institutional wall panels "
            "and cable conduit visible. Flat cold light. Maintain exact composition."
        ),
    },
    {
        "name": "grid_streets_close",
        "source": PANELS_DIR / "grid_streets_top_left.png",
        "prompt": (
            STYLE +
            "Close-up detail of brutalist cityscape architecture. Concrete surface "
            "texture, angular geometric forms, cold steel-blue dawn light. Monolithic "
            "tower facades. Maintain exact composition and framing."
        ),
    },
    {
        "name": "seam_descent_close",
        "source": PANELS_DIR / "seam_descent_top_left.png",
        "prompt": (
            STYLE +
            "Close-up detail of stone steps descending into warm amber light. "
            "Rough stone wall texture, amber LED string lights beginning. The "
            "transition from cold to warm. Maintain exact composition."
        ),
    },
    {
        "name": "seam_interior_close",
        "source": PANELS_DIR / "seam_interior_top_left.png",
        "prompt": (
            STYLE +
            "Close-up detail of underground community space. Amber string lights, "
            "rough stone ceiling texture, salvaged furnishings. Warm golden light "
            "on rough surfaces. Maintain exact composition."
        ),
    },
    {
        "name": "seam_alcove_close_table",
        "source": PANELS_DIR / "seam_alcove_bottom_right.png",
        "prompt": (
            STYLE +
            "Close-up of underground briefing alcove table surface. Rough-hewn "
            "stone table, amber spotlight pooling on the surface. Stone texture "
            "detail. Warm golden light. Maintain exact composition."
        ),
    },
    {
        "name": "fens_room_doorway_close",
        "source": PANELS_DIR / "fens_room_top_left.png",
        "prompt": (
            STYLE +
            "Close-up detail of a doorway framing a grow-lamp room. Warm amber "
            "door edges, green-white grow-lamp light inside. The stark contrast "
            "between amber corridor and green-white interior. Maintain composition."
        ),
    },
]


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Generate close-up location variants")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--crop-only", action="store_true", help="PIL crop only, skip upscale")
    args = parser.parse_args()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    CROPS_DIR.mkdir(parents=True, exist_ok=True)

    if args.dry_run:
        print(f"[DRY RUN] {len(CLOSEUP_JOBS)} close-up variants:")
        for j in CLOSEUP_JOBS:
            exists = (OUTPUT_DIR / f"{j['name']}.png").exists()
            print(f"  {j['name']} ({'EXISTS' if exists else 'pending'})")
        sys.exit(0)

    total = len(CLOSEUP_JOBS)
    done = 0
    failed = []

    for job in CLOSEUP_JOBS:
        done += 1
        name = job["name"]
        src = job["source"]
        out_path = OUTPUT_DIR / f"{name}.png"

        if out_path.exists():
            print(f"\n  [{done}/{total}] {name} — SKIP (exists)")
            continue

        if not src.exists():
            print(f"\n  [{done}/{total}] {name} — SKIP (source not found: {src.name})")
            failed.append(name)
            continue

        print(f"\n  [{done}/{total}] {name}")

        # Step 1: Center crop (60%)
        crop = center_crop(src, ratio=0.6)
        crop_path = save_pil(crop, CROPS_DIR / f"{name}_crop.png")

        if args.crop_only:
            continue

        # Step 2: Upscale with qwen-edit
        try:
            seed = hash(name) % 10000 + 7000
            data = qwen_edit(job["prompt"], crop_path, seed=seed, steps=4)
            save_bytes(data, out_path)
        except Exception as e:
            print(f"    FAILED: {e}")
            failed.append(name)

    if failed:
        print(f"\n  FAILED ({len(failed)}): {', '.join(failed)}")

    print(f"\n{'=' * 70}")
    print(f"DONE — {done} close-up variants processed")
    print(f"{'=' * 70}")
