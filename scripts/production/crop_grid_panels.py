#!/usr/bin/env python3
"""
Panel extraction from 2x2 location grids.

Pipeline: PIL crop → Qwen-Edit upscale (preserves composition at full res).

Usage:
    # Extract all panels from all grids
    python crop_grid_panels.py --all

    # Extract specific panel from specific grid
    python crop_grid_panels.py --grid seam_descent --panel tl

    # Just PIL crop (no upscale)
    python crop_grid_panels.py --all --no-upscale
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
TARGET_W, TARGET_H = 1280, 720

PROJECT = Path(__file__).resolve().parents[2] / "projects" / "stray-signal"
GRIDS_DIR = PROJECT / "PRODUCTION" / "EP01_v03" / "location_grids"
OUTPUT_DIR = PROJECT / "PRODUCTION" / "EP01_v03" / "location_panels"

STYLE = (
    "Stylized sci-fi animation, graphic novel rendering with cinematic lighting, "
    "visible texture on concrete and metal surfaces, desaturated brutalist world "
    "with selective color accents. "
)

# Panel descriptions for upscale prompts — what each quadrant contains
PANEL_DESCRIPTIONS = {
    "grid_streets": {
        "tl": "Wide establishing shot of a brutalist dystopian cityscape at dawn. Monolithic concrete towers, cold steel-blue sky, a small drone overhead. Vanishing point perspective down a long street. No people.",
        "tr": "Low angle street-level view looking up at brutalist concrete buildings. 4500K fluorescent overhead lighting. Polymer pavement. Oppressive vertical scale. Cold sterile atmosphere.",
        "bl": "Wide shot of a brutalist street junction with a ground-level maintenance grate in the polymer pavement. Angular geometric architecture. Late afternoon cold light.",
        "br": "Medium shot of a brutalist street with citizens walking at uniform spacing in geometric steel-blue clothing. 4500K flat lighting. Regulation uniformity.",
    },
    "grid_corridor": {
        "tl": "Wide shot looking down a long maintenance corridor. Fluorescent strip lighting on ceiling. Polymer floor. Institutional walls. Empty. Vanishing point perspective.",
        "tr": "Medium shot from the middle of a maintenance corridor looking toward a junction. Fluorescent lighting overhead. Institutional walls. Shallower perspective.",
        "bl": "Close-medium shot of corridor wall and floor detail. Polymer surface, maintenance panels, cable conduit. Flat fluorescent light from above.",
        "br": "High-angle wide shot looking down a maintenance corridor at 30 degrees. Surveillance perspective. Fluorescent light pools on polymer floor.",
    },
    "seam_descent": {
        "tl": "Wide shot of stone steps descending from cold blue-grey light above into warm amber light below. Underground transition space. Rough stone walls with amber LED string lights beginning.",
        "tr": "Warm underground community space with amber string lights on rough stone walls. Plants, tables, warm atmosphere. People visible in the amber glow.",
        "bl": "Underground space with rough stone walls, amber string lights, a mural, plants growing. Detail and texture of underground life. Warm golden light.",
        "br": "Dramatic amber archway or tunnel opening in rough stone. A silhouette figure in the glowing passage. Golden amber light radiating from the opening.",
    },
    "seam_interior": {
        "tl": "Wide establishing shot of an underground community space. High rough stone ceiling. Amber string lights criss-crossing. Salvaged tables, colorful mural, plants.",
        "tr": "Medium shot of an underground corridor with rough stone walls and amber string lights. Doors or openings branching off. Intimate warm amber light.",
        "bl": "Medium detail shot of underground life — salvaged table, items, plants, string lights close. Rough warm textures. Handmade aesthetic.",
        "br": "Wide shot of underground community space from alternate angle. Alcoves, passages, depth. Amber light from a different direction. Layered space.",
    },
    "seam_alcove": {
        "tl": "Underground community space with rough stone walls, amber string lights, green plant lights. Open area with tables and furnishings.",
        "tr": "Underground alcove or small room. Amber string lights, rough stone, intimate space. Green grow-lights visible. Confined warm atmosphere.",
        "bl": "Underground stone floor and table detail. Amber spotlight on rough stone surface. Texture of carved rock. Warm golden pool of light.",
        "br": "Small underground briefing alcove with a table and chair. Amber light. Rough stone walls. Intimate private space. A doorway with corridor light beyond.",
    },
    "fens_room": {
        "tl": "Wide shot from a doorway looking into a small grow-lamp room. Warm amber doorway edges. Green-white grow-lamp light inside. A small seated figure silhouette. Stark contrast.",
        "tr": "Interior of a green-white grow-lamp room looking toward the doorway. Warm amber corridor light visible through the door. Clinical green-white fill light.",
        "bl": "Grow-lamp room from another angle. Green-white overhead light panels. Plant growing area. The amber and green-white contrast on rough stone walls.",
        "br": "Side angle of grow-lamp room showing depth. Chair or seat visible. Grow-lamps overhead casting green-white light and long shadows on stone walls.",
    },
}


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
    deadline = time.time() + timeout
    polls = 0
    while time.time() < deadline:
        status = requests.get(f"{COMFYUI_BASE}/jobs/{job_id}").json()
        polls += 1
        if status["status"] == "completed":
            elapsed = time.time() - (deadline - timeout)
            print(f"    Done ({elapsed:.0f}s)")
            return requests.get(f"{COMFYUI_BASE}/jobs/{job_id}/result").content
        if status["status"] == "error":
            raise RuntimeError(f"Job {job_id} failed: {status.get('error')}")
        time.sleep(2 if polls <= 5 else 3)
    raise TimeoutError(f"Timeout on {job_id}")


def qwen_edit(prompt, image_path, seed=42, steps=4):
    params = {"prompt": prompt, "seed": str(seed), "steps": str(steps)}
    fhs = []
    files = {}
    try:
        fh1 = open(image_path, "rb")
        fhs.append(fh1)
        files["image"] = (Path(image_path).name, fh1, "image/png")
        return submit_and_wait("qwen-image-edit", params, files=files)
    finally:
        for fh in fhs:
            fh.close()


def pil_crop(image_path, quadrant):
    """Mechanical crop. quadrant: 'tl', 'tr', 'bl', 'br'"""
    img = Image.open(image_path)
    w, h = img.size
    mid_x, mid_y = w // 2, h // 2
    # Trim 2px from edges to avoid grid divider lines
    margin = 2
    boxes = {
        "tl": (margin, margin, mid_x - margin, mid_y - margin),
        "tr": (mid_x + margin, margin, w - margin, mid_y - margin),
        "bl": (margin, mid_y + margin, mid_x - margin, h - margin),
        "br": (mid_x + margin, mid_y + margin, w - margin, h - margin),
    }
    return img.crop(boxes[quadrant])


def save_pil(img, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path, format="PNG")
    print(f"    Saved: {path.name} ({img.size[0]}x{img.size[1]})")
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
# Pipeline
# ---------------------------------------------------------------------------
def extract_panel(grid_name, quadrant, upscale=True):
    """Extract one panel: PIL crop → optional Qwen upscale."""
    grid_path = GRIDS_DIR / f"{grid_name}_grid.png"
    if not grid_path.exists():
        print(f"  SKIP: {grid_path.name} not found")
        return

    panel_names = {"tl": "top_left", "tr": "top_right", "bl": "bottom_left", "br": "bottom_right"}
    panel_label = panel_names[quadrant]

    # Step 1: PIL crop
    crop = pil_crop(grid_path, quadrant)
    crop_path = save_pil(crop, OUTPUT_DIR / "crops" / f"{grid_name}_{panel_label}_crop.png")

    if not upscale:
        return crop_path

    # Step 2: Qwen upscale from crop
    desc = PANEL_DESCRIPTIONS.get(grid_name, {}).get(quadrant, "")
    if not desc:
        print(f"  WARN: No description for {grid_name}/{quadrant}, skipping upscale")
        return crop_path

    prompt = (
        STYLE +
        f"Upscale and enhance this image to full resolution. Maintain the exact same "
        f"composition, framing, and content. Add detail and clarity. "
        f"Scene: {desc}"
    )

    seed = hash(f"{grid_name}_{quadrant}") % 10000 + 6000
    data = qwen_edit(prompt, crop_path, seed=seed, steps=4)
    save_bytes(data, OUTPUT_DIR / f"{grid_name}_{panel_label}.png")


def extract_all(grids=None, upscale=True):
    """Extract all panels from all (or specified) grids."""
    if grids is None:
        grids = list(PANEL_DESCRIPTIONS.keys())

    quadrants = ["tl", "tr", "bl", "br"]
    total = len(grids) * len(quadrants)
    done = 0

    for grid_name in grids:
        print(f"\n{'=' * 70}")
        print(f"GRID: {grid_name}")
        print(f"{'=' * 70}")

        for q in quadrants:
            done += 1
            print(f"\n  [{done}/{total}] {grid_name} / {q}")
            extract_panel(grid_name, q, upscale=upscale)

    print(f"\n{'=' * 70}")
    print(f"DONE — {done} panels extracted")
    print(f"{'=' * 70}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Extract panels from 2x2 location grids")
    parser.add_argument("--all", action="store_true", help="Extract all panels from all grids")
    parser.add_argument("--grid", type=str, help="Specific grid name")
    parser.add_argument("--panel", choices=["tl", "tr", "bl", "br"], help="Specific panel")
    parser.add_argument("--no-upscale", action="store_true", help="PIL crop only, skip Qwen upscale")
    parser.add_argument("--dry-run", action="store_true", help="Print what would be generated")
    args = parser.parse_args()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "crops").mkdir(parents=True, exist_ok=True)

    if args.dry_run:
        grids = list(PANEL_DESCRIPTIONS.keys()) if args.all or not args.grid else [args.grid]
        panels = ["tl", "tr", "bl", "br"] if not args.panel else [args.panel]
        print("[DRY RUN]")
        for g in grids:
            for p in panels:
                print(f"  {g} / {p}")
        print(f"Total: {len(grids) * len(panels)} panels")
        sys.exit(0)

    if args.all:
        extract_all(upscale=not args.no_upscale)
    elif args.grid and args.panel:
        extract_panel(args.grid, args.panel, upscale=not args.no_upscale)
    elif args.grid:
        extract_all(grids=[args.grid], upscale=not args.no_upscale)
    else:
        print("Usage: --all, or --grid NAME [--panel tl/tr/bl/br]")
        sys.exit(1)
