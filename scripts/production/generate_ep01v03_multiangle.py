#!/usr/bin/env python3
"""
EP01 v03 — Generate multi-angle variants of key location refs using
the qwen-multiangle endpoint.

Takes existing location panels and generates camera angle variations
(horizontal rotation, vertical tilt, zoom) to give the compositing
pipeline real perspective options.

Endpoint: qwen-multiangle
  - image: source image
  - horizontal_angle: camera rotation (-60 to 60, default 24)
  - vertical_angle: camera tilt (-30 to 30, default 0)
  - zoom: zoom level (default 10)
  - seed, steps
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
REFS_DIR = PROJECT / "PRODUCTION" / "EP01_v03" / "refs"
OUTPUT_DIR = PROJECT / "PRODUCTION" / "EP01_v03" / "location_angles"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def submit_and_wait(workflow_id, params, files=None, timeout=900):
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
        # multiangle LoRA takes ~90s, poll every 5s
        time.sleep(5)
    raise TimeoutError(f"Timeout on {job_id}")


def multiangle(image_path, horizontal=24, vertical=0, zoom=10, seed=0, steps=4, retries=2):
    for attempt in range(retries + 1):
        params = {
            "horizontal_angle": horizontal,
            "vertical_angle": vertical,
            "zoom": zoom,
            "seed": seed,
            "steps": steps,
        }
        fh = open(image_path, "rb")
        try:
            files = {"image": (Path(image_path).name, fh, "image/png")}
            return submit_and_wait("qwen-multiangle", params, files=files)
        except (RuntimeError, TimeoutError, requests.exceptions.ConnectionError) as e:
            if attempt < retries:
                print(f"    RETRY ({attempt+1}/{retries}): {e}")
                time.sleep(10)
            else:
                raise
        finally:
            fh.close()


def save(data, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as f:
        f.write(data)
    size = Image.open(io.BytesIO(data)).size
    print(f"    Saved: {path.name} ({size[0]}x{size[1]})")
    return path


# ---------------------------------------------------------------------------
# Angle sweep definitions
#
# For each source image, generate a set of angle variants useful for
# the specific clips that use this location.
# ---------------------------------------------------------------------------
# NOTE: qwen-multiangle only accepts non-negative values for all params.
# horizontal_angle: 0 = straight on, higher = more rotation right
# vertical_angle: 0 = eye level, higher = looking up
# zoom: default 10, higher = closer
ANGLE_JOBS = [
    # --- GRID CORRIDOR (clips 10, 11 — Kai walking, Neda watching) ---
    {
        "name": "grid_corridor",
        "source": PANELS_DIR / "grid_corridor_top_left.png",
        "angles": [
            {"label": "slight",   "h": 15,  "v": 0,   "z": 10},
            {"label": "strong",   "h": 40,  "v": 0,   "z": 10},
            {"label": "close",    "h": 10,  "v": 0,   "z": 20},
            {"label": "high",     "h": 20,  "v": 10,  "z": 10},
        ],
    },
    # --- GRID STREETS (clips 1, 2, 9 — cityscape, Neda on grid, return) ---
    {
        "name": "grid_streets",
        "source": PANELS_DIR / "grid_streets_top_left.png",
        "angles": [
            {"label": "slight",   "h": 15,  "v": 0,   "z": 10},
            {"label": "strong",   "h": 35,  "v": 0,   "z": 10},
            {"label": "low_up",   "h": 0,   "v": 15,  "z": 10},
            {"label": "close",    "h": 10,  "v": 5,   "z": 20},
        ],
    },
    # Junction with grate (for clip 2 drop)
    {
        "name": "grid_junction",
        "source": PANELS_DIR / "grid_streets_bottom_left.png",
        "angles": [
            {"label": "slight",   "h": 15,  "v": 0,   "z": 10},
            {"label": "strong",   "h": 30,  "v": 0,   "z": 10},
            {"label": "high",     "h": 10,  "v": 20,  "z": 10},
        ],
    },
    # --- SEAM DESCENT (clip 4) ---
    {
        "name": "seam_descent",
        "source": PANELS_DIR / "seam_descent_top_left.png",
        "angles": [
            {"label": "slight",   "h": 15,  "v": 0,   "z": 10},
            {"label": "strong",   "h": 30,  "v": 0,   "z": 10},
            {"label": "close",    "h": 10,  "v": 5,   "z": 20},
        ],
    },
    # --- SEAM INTERIOR (clip 4 background) ---
    {
        "name": "seam_interior",
        "source": PANELS_DIR / "seam_interior_top_left.png",
        "angles": [
            {"label": "slight",   "h": 15,  "v": 0,   "z": 10},
            {"label": "strong",   "h": 35,  "v": 0,   "z": 10},
            {"label": "close",    "h": 10,  "v": 0,   "z": 20},
        ],
    },
    # --- SEAM ALCOVE / BRIEFING (clips 6, 7) ---
    {
        "name": "seam_alcove",
        "source": PANELS_DIR / "seam_alcove_bottom_right.png",
        "angles": [
            {"label": "slight",      "h": 15,  "v": 0,   "z": 10},
            {"label": "strong",      "h": 30,  "v": 0,   "z": 10},
            {"label": "close_table", "h": 5,   "v": 10,  "z": 20},
        ],
    },
    # --- FEN'S ROOM (clip 5) ---
    # Doorway angle
    {
        "name": "fens_room_doorway",
        "source": PANELS_DIR / "fens_room_top_left.png",
        "angles": [
            {"label": "slight",   "h": 15,  "v": 0,   "z": 10},
            {"label": "strong",   "h": 35,  "v": 0,   "z": 10},
            {"label": "close",    "h": 5,   "v": 0,   "z": 20},
        ],
    },
    # Interior angle (looking out)
    {
        "name": "fens_room_inside",
        "source": PANELS_DIR / "fens_room_top_right.png",
        "angles": [
            {"label": "slight",   "h": 15,  "v": 0,   "z": 10},
            {"label": "strong",   "h": 35,  "v": 0,   "z": 10},
            {"label": "look_up",  "h": 0,   "v": 15,  "z": 10},
        ],
    },
    # Side angle
    {
        "name": "fens_room_side",
        "source": PANELS_DIR / "fens_room_bottom_right.png",
        "angles": [
            {"label": "slight",   "h": 15,  "v": 0,   "z": 10},
            {"label": "strong",   "h": 40,  "v": 0,   "z": 10},
        ],
    },
]


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Generate multi-angle location variants")
    parser.add_argument("--location", type=str, help="Specific location name (or 'all')", default="all")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    jobs = ANGLE_JOBS
    if args.location != "all":
        jobs = [j for j in jobs if j["name"] == args.location]
        if not jobs:
            print(f"No jobs matching '{args.location}'. Available:")
            for j in ANGLE_JOBS:
                print(f"  {j['name']}")
            sys.exit(1)

    total = sum(len(j["angles"]) for j in jobs)

    if args.dry_run:
        print(f"[DRY RUN] {total} angle variants across {len(jobs)} sources:")
        for j in jobs:
            print(f"\n  {j['name']} ({Path(j['source']).name}):")
            for a in j["angles"]:
                print(f"    {a['label']}: h={a['h']}, v={a['v']}, z={a['z']}")
        sys.exit(0)

    done = 0
    failed = []
    for job in jobs:
        name = job["name"]
        src = job["source"]
        if not src.exists():
            print(f"\nSKIP: {src} not found")
            continue

        print(f"\n{'=' * 70}")
        print(f"LOCATION: {name} (from {src.name})")
        print(f"{'=' * 70}")

        for angle in job["angles"]:
            done += 1
            label = angle["label"]
            out_path = OUTPUT_DIR / f"{name}_{label}.png"

            # Skip if already generated
            if out_path.exists():
                print(f"\n  [{done}/{total}] {name}_{label} — SKIP (exists)")
                continue

            print(f"\n  [{done}/{total}] {name}_{label} (h={angle['h']}, v={angle['v']}, z={angle['z']})")

            try:
                data = multiangle(
                    src,
                    horizontal=angle["h"],
                    vertical=angle["v"],
                    zoom=angle["z"],
                    seed=hash(f"{name}_{label}") % 10000,
                    steps=4,
                )
                save(data, out_path)
            except Exception as e:
                print(f"    FAILED: {e}")
                failed.append(f"{name}_{label}")
                continue

    if failed:
        print(f"\n  FAILED ({len(failed)}): {', '.join(failed)}")

    print(f"\n{'=' * 70}")
    print(f"DONE — {done} angle variants generated")
    print(f"{'=' * 70}")
