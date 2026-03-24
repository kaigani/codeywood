#!/usr/bin/env python3
"""
EP01 v03 — Generate 4 HIGH-priority reference images for the revised shot list.

Refs needed:
  1. grid_cityscape_wide     — Wide brutalist cityscape, dawn, no people, drone (clip 1)
  2. fen_silhouette_doorway   — Fen seated silhouette, grow-lamp, doorway framing (clip 5)
  3. seam_briefing_alcove     — Small stone room, amber light, table (clips 6-7)
  4. neda_watching_distance   — Neda CU, Grid corridor, cyan reflection, jaw tension (clip 11)

Pipeline: ComfyUI qwen-image-edit (local, $0.00)
  - Refs 1: qwen-edit from grid_plaza_zimage (establishing shot repose)
  - Refs 2: qwen-edit from loc_fen_room (reframe as doorway composition)
  - Refs 3: qwen-edit from loc_seam_main (zoom to small alcove)
  - Refs 4: qwen-edit from neda_grid + neda_portrait (character expression edit)
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
REFS = PROJECT / "REFERENCES"
OUTPUT_DIR = PROJECT / "PRODUCTION" / "EP01_v03" / "refs"

# Source references
GRID_PLAZA = REFS / "style_inspiration" / "grid_plaza_zimage.png"
GRID_CORRIDOR = REFS / "style_inspiration" / "grid_corridor_zimage.png"
LOC_FEN_ROOM = REFS / "location_refs" / "loc_fen_room.png"
LOC_SEAM_MAIN = REFS / "location_refs" / "v2" / "loc_seam_main.png"
SEAM_INTERIOR = REFS / "style_inspiration" / "seam_interior_seedream.png"
NEDA_GRID = REFS / "hero_shots" / "v2" / "neda_grid.png"
NEDA_PORTRAIT = REFS / "hero_shots" / "v2" / "neda_portrait.png"

# Style prefix for all prompts
STYLE = (
    "Stylized sci-fi animation frame, graphic novel rendering with cinematic lighting, "
    "visible texture on concrete and metal surfaces, clean character silhouettes, "
    "exaggerated scale between figures and architecture, desaturated brutalist world "
    "with selective color accents. "
)


# ---------------------------------------------------------------------------
# Helpers (same pattern as generate_ep01_frames.py)
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


def qwen_edit(prompt, image_path, image2_path=None, seed=42, steps=4):
    params = {"prompt": prompt, "seed": str(seed), "steps": str(steps)}
    fhs = []
    files = {}
    try:
        fh1 = open(image_path, "rb")
        fhs.append(fh1)
        files["image"] = (Path(image_path).name, fh1, "image/png")
        if image2_path:
            fh2 = open(image2_path, "rb")
            fhs.append(fh2)
            files["image2"] = (Path(image2_path).name, fh2, "image/png")
        return submit_and_wait("qwen-image-edit", params, files=files)
    finally:
        for fh in fhs:
            fh.close()


def normalize(png_bytes):
    img = Image.open(io.BytesIO(png_bytes))
    if img.size != (TARGET_W, TARGET_H):
        img = img.resize((TARGET_W, TARGET_H), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def save(data, path, norm=True):
    if norm:
        data = normalize(data)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as f:
        f.write(data)
    size = Image.open(io.BytesIO(data)).size
    print(f"    Saved: {path.name} ({size[0]}x{size[1]})")
    return path


# ---------------------------------------------------------------------------
# Reference Generation
# ---------------------------------------------------------------------------

def gen_grid_cityscape_wide():
    """Ref 1: Wide brutalist cityscape establishing shot, dawn, no people."""
    print("\n" + "=" * 70)
    print("REF 1: grid_cityscape_wide")
    print("=" * 70)

    prompt = (
        STYLE +
        "Wide anamorphic establishing shot of a brutalist dystopian cityscape at dawn. "
        "Massive monolithic concrete blocks rising without ornament or decoration against "
        "a cold steel-blue sky. No curves, no color, no warmth. Geometric angular "
        "architecture stretching to the horizon. A single small surveillance drone traces "
        "a lazy circuit in the upper portion of the frame. No people visible anywhere. "
        "Dawn light casting long steel-blue shadows. Concrete grey and cold blue palette. "
        "The scale is monumental and oppressive. Vanishing point perspective."
    )

    print("  Generating from grid_plaza_zimage + grid_corridor_zimage...")
    data = qwen_edit(prompt, GRID_PLAZA, image2_path=GRID_CORRIDOR, seed=3001, steps=4)
    save(data, OUTPUT_DIR / "grid_cityscape_wide.png")


def gen_fen_silhouette_doorway():
    """Ref 2: Fen seated in silhouette, grow-lamp backlighting, doorway frame."""
    print("\n" + "=" * 70)
    print("REF 2: fen_silhouette_doorway")
    print("=" * 70)

    prompt = (
        STYLE +
        "Wide shot framed through a doorway looking into a small room. The room is lit "
        "by overhead grow-lamps casting green-white light from above. In the center of "
        "the room, a figure sits in complete silhouette — backlit by the grow-lamps, "
        "facing away. Absolutely still. The posture of someone who has been sitting for "
        "a very long time. Not waiting. Not resting. Sitting the way furniture sits. "
        "The doorway frame is in warm amber light from the corridor behind us. Two "
        "distinct lighting zones: warm amber doorway foreground, green-white grow-lamp "
        "room background. The contrast is stark. No face detail on the seated figure — "
        "pure silhouette."
    )

    print("  Generating from loc_fen_room...")
    data = qwen_edit(prompt, LOC_FEN_ROOM, seed=3002, steps=4)
    save(data, OUTPUT_DIR / "fen_silhouette_doorway.png")


def gen_seam_briefing_alcove():
    """Ref 3: Small underground stone room, amber light, rough table."""
    print("\n" + "=" * 70)
    print("REF 3: seam_briefing_alcove")
    print("=" * 70)

    prompt = (
        STYLE +
        "A small underground room carved from rough stone. Close stone walls. Warm amber "
        "LED string lights cast golden light on the rough surfaces. A simple rough-hewn "
        "stone table in the center with two seats facing each other. The room is intimate "
        "and confined — a private briefing space. Amber light sits heavy on every surface. "
        "No windows. The ceiling is low. One side of the table is in slightly deeper shadow. "
        "The warmth of the amber light contrasts with the raw stone texture. Underground "
        "resistance aesthetic — functional, hidden, warm."
    )

    print("  Generating from loc_seam_main + seam_interior...")
    data = qwen_edit(prompt, LOC_SEAM_MAIN, image2_path=SEAM_INTERIOR, seed=3003, steps=4)
    save(data, OUTPUT_DIR / "seam_briefing_alcove.png")


def gen_neda_watching_distance():
    """Ref 4: Neda CU in Grid corridor, calculating expression, cyan reflection."""
    print("\n" + "=" * 70)
    print("REF 4: neda_watching_distance")
    print("=" * 70)

    prompt = (
        STYLE +
        "Close-up of a 17-year-old girl in a cold, sterile corridor. Same character, "
        "same face, same skin tone — brown skin, warm undertone, black hair cropped short "
        "on sides with longer top pushed back. Dark assessing eyes. She wears an angular "
        "steel-blue jacket with geometric collar. 4500K flat fluorescent lighting. She "
        "stands absolutely still, watching something ahead and off-screen. A faint cyan "
        "glow reflects on the right side of her face — the only warm color in the frame. "
        "Her jaw is tight. Her expression: calculation, recognition, and something she is "
        "trying very hard not to feel. The Grid corridor stretches behind her in cold "
        "blue-grey vanishing point perspective."
    )

    print("  Generating from neda_grid + neda_portrait...")
    data = qwen_edit(prompt, NEDA_GRID, image2_path=NEDA_PORTRAIT, seed=3004, steps=4)
    save(data, OUTPUT_DIR / "neda_watching_distance.png")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Generate EP01 v03 reference images")
    parser.add_argument("--ref", choices=["cityscape", "fen", "briefing", "neda", "all"],
                        default="all", help="Which ref to generate (default: all)")
    parser.add_argument("--dry-run", action="store_true", help="Print prompts without generating")
    args = parser.parse_args()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Output dir: {OUTPUT_DIR}")

    generators = {
        "cityscape": gen_grid_cityscape_wide,
        "fen": gen_fen_silhouette_doorway,
        "briefing": gen_seam_briefing_alcove,
        "neda": gen_neda_watching_distance,
    }

    if args.dry_run:
        print("\n[DRY RUN] Would generate:")
        targets = generators.keys() if args.ref == "all" else [args.ref]
        for name in targets:
            print(f"  - {name}")
        sys.exit(0)

    if args.ref == "all":
        for name, fn in generators.items():
            fn()
    else:
        generators[args.ref]()

    print("\n" + "=" * 70)
    print("DONE")
    print("=" * 70)
