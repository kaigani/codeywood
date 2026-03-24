#!/usr/bin/env python3
"""
EP01 v03 — Generate start frames for all 11 clips.

Stage 3 of the compositing pipeline:
  - Clips 1, 11: use existing composition refs directly (no compositing needed)
  - Clip 3: ffmpeg title card (handled separately)
  - Clips 2, 4, 5, 6, 7, 8, 9, 10: qwen-edit compositing (location + character)

Each composited frame uses:
  - image: location ref (from panels, angles, or composition refs)
  - image2: character pose (from character_poses/)
  - prompt: scene-specific composition instructions
"""

import io
import shutil
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
PROD = PROJECT / "PRODUCTION" / "EP01_v03"
FRAMES_DIR = PROD / "frames"

# Character poses
NEDA_POSES = REFS / "character_poses" / "neda"
KAI_POSES = REFS / "character_poses" / "kai"

# Location refs
PANELS = PROD / "location_panels"
ANGLES = PROD / "location_angles"
COMP_REFS = PROD / "refs"

STYLE = (
    "Stylized sci-fi animation frame, graphic novel rendering with cinematic lighting, "
    "visible texture on concrete and metal surfaces, clean character silhouettes, "
    "exaggerated scale between figures and architecture, desaturated brutalist world "
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
    """Normalize to target dimensions."""
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


def copy_and_normalize(src, dst):
    """Copy an existing ref and normalize to target size."""
    img = Image.open(src)
    if img.size != (TARGET_W, TARGET_H):
        img = img.resize((TARGET_W, TARGET_H), Image.LANCZOS)
    dst = Path(dst)
    dst.parent.mkdir(parents=True, exist_ok=True)
    img.save(dst, format="PNG")
    print(f"    Saved: {dst.name} ({TARGET_W}x{TARGET_H}) [copied from ref]")
    return dst


# ---------------------------------------------------------------------------
# Frame definitions — one per clip
# ---------------------------------------------------------------------------
FRAMES = [
    # --- CLIP 1: Cityscape Dawn (no compositing — use ref directly) ---
    {
        "clip": 1,
        "name": "clip_01_cityscape_dawn",
        "strategy": "copy_ref",
        "source": COMP_REFS / "grid_cityscape_wide.png",
    },

    # --- CLIP 2: Neda on the Grid ---
    {
        "clip": 2,
        "name": "clip_02_neda_on_the_grid",
        "strategy": "compose",
        "location": ANGLES / "grid_streets_slight.png",
        "character": NEDA_POSES / "neda_med_walking_grid.png",
        "seed": 6002,
        "prompt": (
            STYLE +
            "Film still. Medium shot of a girl walking through a brutalist city street "
            "among a sparse crowd of uniformly-dressed citizens. She wears the same angular "
            "steel-blue jacket and grey clothing as everyone else. Same pace, same spacing. "
            "But her eyes are different — aware, tracking, reading the environment. She blends "
            "in perfectly while being completely different. Cold steel-blue 4500K lighting. "
            "Concrete walls and polymer pavement. The girl from image 2 walking on the street "
            "from this image."
        ),
    },

    # --- CLIP 3: Title Card (ffmpeg — skip here) ---
    {
        "clip": 3,
        "name": "clip_03_title_card",
        "strategy": "skip",
    },

    # --- CLIP 4: Seam Descent ---
    {
        "clip": 4,
        "name": "clip_04_seam_descent",
        "strategy": "compose",
        "location": PANELS / "seam_descent_top_left.png",
        "character": NEDA_POSES / "neda_full_descending.png",
        "seed": 6004,
        "prompt": (
            STYLE +
            "Film still. Wide shot of a girl descending rough stone steps from cold blue-grey "
            "light above into warm amber light below. She is seen from behind, moving downward. "
            "The transition is dramatic — cold polymer and fluorescent light giving way to rough "
            "stone, amber LED string lights, warmth. Her shoulders drop as she descends. Behind "
            "her below: the glow of an underground community — string lights, warm golden light "
            "ahead. The girl from image 2 descending the steps in this image."
        ),
    },

    # --- CLIP 5: Fen's Room ---
    {
        "clip": 5,
        "name": "clip_05_fens_room",
        "strategy": "compose",
        "location": COMP_REFS / "fen_silhouette_doorway.png",
        "character": NEDA_POSES / "neda_silhouette_doorway.png",
        "seed": 6005,
        "prompt": (
            STYLE +
            "Film still. Wide shot framed through a doorway. A small room lit by green-white "
            "grow-lamps. In the center of the room, a figure sits in complete silhouette — "
            "backlit by grow-lamps, absolutely still. The posture of someone who has been sitting "
            "for a very long time. In the foreground doorway, a girl stands in silhouette, looking "
            "in. Warm amber corridor light on the doorway edges. Two distinct lighting zones: "
            "amber doorway foreground, green-white room background. The contrast is stark. "
            "The standing figure from image 2 in the doorway of this room."
        ),
    },

    # --- CLIP 6: Briefing Intel ---
    {
        "clip": 6,
        "name": "clip_06_briefing_intel",
        "strategy": "compose",
        "location": COMP_REFS / "seam_briefing_alcove.png",
        "character": NEDA_POSES / "neda_cu_listening.png",
        "seed": 6006,
        "prompt": (
            STYLE +
            "Film still. Close-up of a girl seated at a rough stone table in a small "
            "underground room. Warm amber LED string lights cast golden light on rough stone "
            "walls. She sits with controlled attention, listening. Her right hand rests on the "
            "table edge. Her expression: absorbing every word, controlled, assessing. Brown "
            "skin, warm undertone, black hair cropped short with copper braid behind left ear. "
            "Amber light on her face. The character from image 2 seated in this room."
        ),
    },

    # --- CLIP 7: Briefing Argument ---
    {
        "clip": 7,
        "name": "clip_07_briefing_argument",
        "strategy": "compose",
        "location": ANGLES / "seam_alcove_slight.png",
        "character": NEDA_POSES / "neda_cu_speaking_conviction.png",
        "seed": 6007,
        "prompt": (
            STYLE +
            "Film still. Close-up of a girl leaning forward at a rough stone table in a "
            "small underground room, speaking with intensity. Different angle from the previous "
            "shot — slightly to the side, tighter framing. Amber light catches her copper braid "
            "behind her left ear. Her jaw is set. Her fist grips the table edge. Expression: "
            "absolute conviction that costs something. Not anger — necessity. Brown skin, dark "
            "assessing eyes. The character from image 2 in this underground alcove."
        ),
    },

    # --- CLIP 8: Neda Returns to Surface ---
    {
        "clip": 8,
        "name": "clip_08_neda_returns",
        "strategy": "compose",
        "location": ANGLES / "seam_interior_slight.png",
        "character": NEDA_POSES / "neda_med_walking_purpose.png",
        "seed": 6008,
        "prompt": (
            STYLE +
            "Film still. Medium shot of a girl walking with determination through an underground "
            "corridor. Rough stone walls, amber string lights overhead. She moves past branching "
            "hallways without looking. Dark layered jacket, tool harness. Her stride is long and "
            "purposeful. Ahead, stone steps ascend toward colder light — the way back to the "
            "surface. The amber light on her back as she moves toward cold. "
            "The character from image 2 walking through this corridor."
        ),
    },

    # --- CLIP 9: Grid With Purpose ---
    {
        "clip": 9,
        "name": "clip_09_grid_with_purpose",
        "strategy": "compose",
        "location": ANGLES / "grid_streets_strong.png",
        "character": NEDA_POSES / "neda_full_walking_mission.png",
        "seed": 6009,
        "prompt": (
            STYLE +
            "Film still. Wide shot of a brutalist city street. Same cold architecture, same "
            "steel-blue lighting. But a girl moves through the frame with different energy — "
            "faster, more direct, a body with coordinates. She wears an angular steel-blue "
            "jacket blending with the Grid, but her stride is longer, her posture more forward. "
            "A surveillance drone overhead. She tracks it without looking up. "
            "The character from image 2 on this Grid street."
        ),
    },

    # --- CLIP 10: Kai Appears ---
    {
        "clip": 10,
        "name": "clip_10_kai_appears",
        "strategy": "compose",
        "location": ANGLES / "grid_corridor_slight.png",
        "character": KAI_POSES / "kai_full_walking_toward.png",
        "seed": 6010,
        "prompt": (
            STYLE +
            "Film still. Wide-to-medium shot of a maintenance corridor. Fluorescent strip "
            "lighting, polymer floor, institutional walls. A boy walks toward the camera from "
            "the far end. 16 years old, maintenance coverall, a battered datapad in one hand. "
            "In his other hand, a small device emitting a faint cyan glow that catches his face "
            "and fingers. The cyan light is a color that doesn't belong in this cold sterile "
            "world. He walks with measured steps, alone, unaware anyone is watching. "
            "The character from image 2 walking in this corridor."
        ),
    },

    # --- CLIP 11: Neda Watching (use ref directly) ---
    {
        "clip": 11,
        "name": "clip_11_neda_watching",
        "strategy": "copy_ref",
        "source": COMP_REFS / "neda_watching_distance.png",
    },
]


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Generate EP01 v03 start frames")
    parser.add_argument("--clip", type=int, help="Specific clip number (or 0 for all)", default=0)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    FRAMES_DIR.mkdir(parents=True, exist_ok=True)

    frames = FRAMES
    if args.clip > 0:
        frames = [f for f in FRAMES if f["clip"] == args.clip]
        if not frames:
            print(f"No frame for clip {args.clip}")
            sys.exit(1)

    if args.dry_run:
        print(f"[DRY RUN] {len(frames)} frames:")
        for f in frames:
            out = FRAMES_DIR / f"{f['name']}.png"
            exists = out.exists()
            if f["strategy"] == "skip":
                print(f"  Clip {f['clip']}: {f['name']} — SKIP (ffmpeg title)")
            elif f["strategy"] == "copy_ref":
                print(f"  Clip {f['clip']}: {f['name']} — copy ref {'EXISTS' if exists else 'pending'}")
            else:
                print(f"  Clip {f['clip']}: {f['name']} — compose {'EXISTS' if exists else 'pending'}")
        sys.exit(0)

    total = len(frames)
    done = 0
    failed = []

    for frame in frames:
        done += 1
        clip = frame["clip"]
        name = frame["name"]
        out_path = FRAMES_DIR / f"{name}.png"
        strategy = frame["strategy"]

        if strategy == "skip":
            print(f"\n  [{done}/{total}] Clip {clip}: {name} — SKIP (ffmpeg title card)")
            continue

        if out_path.exists():
            print(f"\n  [{done}/{total}] Clip {clip}: {name} — SKIP (exists)")
            continue

        print(f"\n  [{done}/{total}] Clip {clip}: {name} ({strategy})")

        try:
            if strategy == "copy_ref":
                src = frame["source"]
                if not src.exists():
                    print(f"    SKIP: source not found: {src.name}")
                    failed.append(name)
                    continue
                copy_and_normalize(src, out_path)

            elif strategy == "compose":
                loc = frame["location"]
                char = frame["character"]
                if not loc.exists():
                    print(f"    SKIP: location ref not found: {loc}")
                    failed.append(name)
                    continue
                if not char.exists():
                    print(f"    SKIP: character pose not found: {char}")
                    failed.append(name)
                    continue

                data = qwen_edit(
                    frame["prompt"],
                    loc,
                    image2_path=char,
                    seed=frame["seed"],
                    steps=4,
                )
                save(data, out_path, norm=True)

        except Exception as e:
            print(f"    FAILED: {e}")
            failed.append(name)

    if failed:
        print(f"\n  FAILED ({len(failed)}): {', '.join(failed)}")

    print(f"\n{'=' * 70}")
    print(f"DONE — {done} frames processed")
    print(f"{'=' * 70}")
