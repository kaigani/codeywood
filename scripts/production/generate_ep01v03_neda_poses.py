#!/usr/bin/env python3
"""
EP01 v03 — Generate Neda character pose variants for compositing pipeline.

Stage 1 of the 3-stage compositing pipeline: extract character onto neutral
backgrounds in the poses needed for each clip.

Neda appears in clips 2, 4, 5, 6, 7, 8, 9 — each needs a specific pose.
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
REFS = PROJECT / "REFERENCES"
OUTPUT_DIR = REFS / "character_poses" / "neda"

# Source hero shots
NEDA_GRID = REFS / "hero_shots" / "v2" / "neda_grid.png"
NEDA_SEAM = REFS / "hero_shots" / "v2" / "neda_seam.png"
NEDA_PORTRAIT = REFS / "hero_shots" / "v2" / "neda_portrait.png"

STYLE = (
    "Stylized sci-fi animation, graphic novel rendering with cinematic lighting, "
    "clean character silhouettes. "
)

NEDA_DESC = (
    "17-year-old girl, brown skin with warm undertone, black hair cropped short "
    "on sides with longer top pushed back, thin copper braid behind left ear, "
    "dark assessing eyes, angular jaw. Same face, same skin tone, same character. "
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


def save(data, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as f:
        f.write(data)
    size = Image.open(io.BytesIO(data)).size
    print(f"    Saved: {path.name} ({size[0]}x{size[1]})")
    return path


# ---------------------------------------------------------------------------
# Pose definitions
# ---------------------------------------------------------------------------
POSES = [
    # Clip 2: Walking on Grid, medium shot, blending with crowd
    {
        "name": "neda_med_walking_grid",
        "source": NEDA_GRID,
        "seed": 5001,
        "prompt": (
            STYLE + "Show this character in a medium shot, walking forward at regulation pace. " +
            NEDA_DESC +
            "Angular steel-blue jacket with geometric collar, grey trousers, boots. "
            "Walking naturally, arms at sides, looking straight ahead. "
            "Grey neutral background. Full body visible from knees up."
        ),
    },
    # Clip 4: Descending steps, side/back view, transitioning to Seam
    {
        "name": "neda_full_descending",
        "source": NEDA_SEAM,
        "seed": 5002,
        "prompt": (
            STYLE + "Show this character from behind and slightly to the side, walking downward as if descending steps. " +
            NEDA_DESC +
            "Dark layered jacket over warm-toned shirt. Seen from behind, head slightly turned. "
            "Shoulders relaxing, posture softening. Full body. "
            "Grey neutral background."
        ),
    },
    # Clip 5: Standing in doorway, silhouette, from behind
    {
        "name": "neda_silhouette_doorway",
        "source": NEDA_SEAM,
        "seed": 5003,
        "prompt": (
            STYLE + "Show this character as a dark silhouette standing in a doorway, seen from behind. " +
            NEDA_DESC +
            "Standing still, looking into a room. Arms at sides. Slight lean of the head. "
            "The posture of someone watching something painful. Full body silhouette. "
            "Grey neutral background."
        ),
    },
    # Clip 6: CU seated, listening intently, amber light direction
    {
        "name": "neda_cu_listening",
        "source": NEDA_PORTRAIT,
        "seed": 5004,
        "prompt": (
            STYLE + "Close-up of this character seated, listening intently. " +
            NEDA_DESC +
            "Head and shoulders visible. She sits at a table, slightly leaning forward. "
            "Expression: controlled, absorbing information. Eyes focused on someone off-screen. "
            "Right hand resting on table edge. "
            "Grey neutral background."
        ),
    },
    # Clip 7: CU leaning forward, speaking with conviction
    {
        "name": "neda_cu_speaking_conviction",
        "source": NEDA_PORTRAIT,
        "seed": 5005,
        "prompt": (
            STYLE + "Close-up of this character leaning forward, speaking with intensity. " +
            NEDA_DESC +
            "Head and shoulders visible. Leaning forward toward camera. Jaw set. "
            "Expression: absolute conviction that costs something. Eyes direct, unflinching. "
            "Copper braid visible behind left ear catching light. "
            "Right hand gripping table edge, knuckles visible. "
            "Grey neutral background."
        ),
    },
    # Clip 8: Medium walking with purpose through corridor
    {
        "name": "neda_med_walking_purpose",
        "source": NEDA_SEAM,
        "seed": 5006,
        "prompt": (
            STYLE + "Show this character in a medium shot, walking with determination. " +
            NEDA_DESC +
            "Dark layered jacket, tool harness. Walking with purpose, stride longer than casual. "
            "Eyes forward, jaw set. One hand brushes past a thin braid behind her left ear. "
            "Medium shot from waist up. "
            "Grey neutral background."
        ),
    },
    # Clip 9: Full body walking on Grid, faster than crowd pace
    {
        "name": "neda_full_walking_mission",
        "source": NEDA_GRID,
        "seed": 5007,
        "prompt": (
            STYLE + "Show this character in a full body shot, walking with mission pace — faster and more direct than normal. " +
            NEDA_DESC +
            "Angular steel-blue jacket with geometric collar, grey trousers, boots. "
            "Longer stride, body leaning slightly forward. A body with coordinates. "
            "Eyes tracking something overhead without tilting her head. "
            "Grey neutral background."
        ),
    },
]


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Generate Neda character poses")
    parser.add_argument("--pose", type=str, help="Specific pose name (or 'all')", default="all")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    poses = POSES
    if args.pose != "all":
        poses = [p for p in POSES if p["name"] == args.pose]
        if not poses:
            print(f"No pose matching '{args.pose}'. Available:")
            for p in POSES:
                print(f"  {p['name']}")
            sys.exit(1)

    if args.dry_run:
        print(f"[DRY RUN] {len(poses)} poses:")
        for p in poses:
            exists = (OUTPUT_DIR / f"{p['name']}.png").exists()
            print(f"  {p['name']} (from {Path(p['source']).name}) {'EXISTS' if exists else 'pending'}")
        sys.exit(0)

    total = len(poses)
    done = 0
    failed = []

    for pose in poses:
        done += 1
        name = pose["name"]
        out_path = OUTPUT_DIR / f"{name}.png"

        if out_path.exists():
            print(f"\n  [{done}/{total}] {name} — SKIP (exists)")
            continue

        print(f"\n  [{done}/{total}] {name}")

        try:
            data = qwen_edit(
                pose["prompt"],
                pose["source"],
                seed=pose["seed"],
                steps=4,
            )
            save(data, out_path)
        except Exception as e:
            print(f"    FAILED: {e}")
            failed.append(name)

    if failed:
        print(f"\n  FAILED ({len(failed)}): {', '.join(failed)}")

    print(f"\n{'=' * 70}")
    print(f"DONE — {done} Neda poses processed")
    print(f"{'=' * 70}")
