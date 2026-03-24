#!/usr/bin/env python3
"""
Stray Signal — Hero Refs via Qwen-Edit from Locked Anchors

Uses the approved z-image portraits as style anchors and iterates with
qwen-image-edit to produce consistent hero ref sets for both characters.

Anchors:
  - Neda: hero_shots/v3/neda_portrait_seam.png
  - Kai:  hero_shots/v3/kai_portrait_grid.png

Pipeline: ComfyUI qwen-image-edit (local, $0.00)
Output: projects/stray-signal/REFERENCES/hero_shots/v3/qwen/
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
OUTPUT_DIR = REFS / "hero_shots" / "v3" / "qwen"

# Anchor images
NEDA_ANCHOR = REFS / "hero_shots" / "v3" / "neda_portrait_seam.png"
KAI_ANCHOR = REFS / "hero_shots" / "v3" / "kai_portrait_grid.png"

# Location refs for compositing (wide shots)
LOC_GRID_STREET = REFS / "exploration_v3" / "locations" / "loc_grid_street_canyon.png"
LOC_SEAM_CORRIDOR = REFS / "exploration_v3" / "locations" / "loc_seam_corridor_wide.png"
LOC_SEAM_INTIMATE = REFS / "exploration_v3" / "locations" / "loc_seam_corridor_intimate.png"
LOC_BRIEFING = REFS / "exploration_v3" / "locations" / "loc_briefing_alcove_spartan.png"
LOC_MAINTENANCE = REFS / "exploration_v3" / "locations" / "loc_maintenance_corridor_with_glow.png"
LOC_FEN_ROOM = REFS / "exploration_v3" / "locations" / "loc_fen_room_doorway.png"
LOC_DESCENT = REFS / "exploration_v3" / "locations" / "loc_descent_upper_cold.png"

# ---------------------------------------------------------------------------
# Shot definitions
# ---------------------------------------------------------------------------
SHOTS = {
    # === NEDA — portrait variations (anchor as image, prompt transforms) ===
    "neda_portrait_grid": {
        "desc": "Neda CU — Grid appearance (cold light, steel-blue jacket)",
        "image": NEDA_ANCHOR,
        "image2": None,
        "prompt": (
            "Same character, same face, same style. Close-up portrait. "
            "She now wears an angular steel-blue geometric jacket with origami-folded collar "
            "over a grey underlayer. Cold flat fluorescent lighting from above. "
            "Brutalist concrete wall background. Steel-blue and grey palette. "
            "Expression controlled and neutral, jaw tension visible. "
            "The warm amber light is gone — replaced by cold clinical fluorescent."
        ),
    },
    "neda_three_quarter": {
        "desc": "Neda three-quarter — shows asymmetric hair from both sides",
        "image": NEDA_ANCHOR,
        "image2": None,
        "prompt": (
            "Same character, same face, same style. Three-quarter view portrait. "
            "Turned slightly to show both the shaved left side with the copper-wire braid "
            "and the longer swept hair on the right side. Angular steel-blue jacket. "
            "Brutalist concrete background. Cold fluorescent light. "
            "Expression: neutral assessment, reading someone offscreen."
        ),
    },
    "neda_jaw_tell": {
        "desc": "Neda extreme CU — jaw tighten, the signature tell",
        "image": NEDA_ANCHOR,
        "image2": None,
        "prompt": (
            "Same character, same style. Extreme close-up of her lower face and jaw only. "
            "Brown skin, angular jaw with tension visible in the masseter muscle — "
            "the jaw clenched a fraction before speaking. Lips pressed. "
            "Asymmetric black hair visible at the edge of frame. "
            "Cold fluorescent light from above, faint cyan reflection on the right side. "
            "Steel-blue geometric collar at bottom of frame."
        ),
    },
    "neda_detail_hands": {
        "desc": "Neda detail — knuckle scar on stone table",
        "image": NEDA_ANCHOR,
        "image2": None,
        "prompt": (
            "Same character, same style. Extreme close-up of her hands gripping "
            "the edge of a rough stone table. White scar tissue across the knuckles "
            "of the right hand against warm brown skin. Angular steel-blue sleeve cuff "
            "at wrist. Amber light from the left. Stone texture visible on the table surface."
        ),
    },

    # === NEDA — full body (location as image, anchor as image2) ===
    "neda_full_grid": {
        "desc": "Neda full body — Grid street canyon",
        "image": LOC_GRID_STREET,
        "image2": NEDA_ANCHOR,
        "prompt": (
            "The girl from image 2 walking through this concrete street canyon. "
            "Same face, same brown skin, same asymmetric black hair. "
            "She wears an angular steel-blue geometric jacket with origami collar, "
            "concrete grey trousers, polymer boots. Posture upright, space-claiming. "
            "She moves with purpose through the brutalist architecture. "
            "Mid-stride, centered in the corridor. Full figure visible."
        ),
    },
    "neda_full_seam": {
        "desc": "Neda full body — Seam corridor",
        "image": LOC_SEAM_CORRIDOR,
        "image2": NEDA_ANCHOR,
        "prompt": (
            "The girl from image 2 standing in this underground corridor. "
            "Same face, same brown skin, same asymmetric hair, copper braid visible. "
            "She wears a fitted dark brown jacket with visible stitching over a rust underlayer, "
            "tool harness across chest, cargo trousers, worn boots. "
            "Posture sharp and direct — no Grid performance here. "
            "Amber string lights warming her skin. Full figure visible."
        ),
    },
    "neda_briefing": {
        "desc": "Neda at briefing table — amber light, operational",
        "image": LOC_BRIEFING,
        "image2": NEDA_ANCHOR,
        "prompt": (
            "The girl from image 2 seated at this stone table in the briefing alcove. "
            "Same face, same brown skin, same asymmetric hair. "
            "Seam clothing — dark jacket, rust underlayer. Leaning forward slightly, "
            "hands on the table, one hand in a fist. Deep amber light on her face. "
            "Expression intense, focused. She is volunteering for something dangerous."
        ),
    },

    # === KAI — portrait variations (anchor as image, prompt transforms) ===
    "kai_portrait_device": {
        "desc": "Kai CU — lit by device cyan glow",
        "image": KAI_ANCHOR,
        "image2": None,
        "prompt": (
            "Same character, same face, same style. Close-up portrait. "
            "His face now lit from below by cyan wireframe glow from a device screen. "
            "The cyan light picks out his cheekbones and the shaggy hair falling "
            "across his forehead. Dark maintenance corridor behind him — "
            "no fluorescent light, just the device glow. "
            "Expression: wide-eyed curiosity, lips slightly parted. "
            "Cyan is the only color in the frame."
        ),
    },
    "kai_three_quarter": {
        "desc": "Kai three-quarter — hair falling in eyes",
        "image": KAI_ANCHOR,
        "image2": None,
        "prompt": (
            "Same character, same face, same style. Three-quarter view portrait. "
            "Turned slightly, shaggy dark hair falling across his forehead and into "
            "his eyes. One hand pushing hair back but it does not stay. "
            "Concrete grey geometric jacket with high collar. "
            "Brutalist concrete background. Cold fluorescent light. "
            "Expression: watching something with quiet intensity."
        ),
    },
    "kai_detail_hands": {
        "desc": "Kai detail — hands holding device, cyan glow",
        "image": KAI_ANCHOR,
        "image2": None,
        "prompt": (
            "Same character, same style. Extreme close-up of his hands "
            "holding a brushed-aluminum tablet device. Light brown skin, lean fingers, "
            "one thumb testing the edge of the device frame. Screen shows a small "
            "cyan wireframe cat sitting. Cyan glow on fingertips. "
            "Device is scratched, dented, warm from use. Dark corridor background."
        ),
    },

    # === KAI — full body (location as image, anchor as image2) ===
    "kai_full_grid": {
        "desc": "Kai full body — Grid corridor, folded inward",
        "image": LOC_MAINTENANCE,
        "image2": KAI_ANCHOR,
        "prompt": (
            "The boy from image 2 standing in this maintenance corridor. "
            "Same face, same light brown skin, same shaggy dark hair. "
            "Angular geometric jacket in concrete grey, high collar, "
            "fitted trousers, polymer boots, maintenance tool belt at waist. "
            "Posture folded inward, shoulders hunched. He blends into the architecture. "
            "Cold fluorescent light. Full figure visible."
        ),
    },
    "kai_full_device": {
        "desc": "Kai full body — corridor with device, cyan glow",
        "image": LOC_MAINTENANCE,
        "image2": KAI_ANCHOR,
        "prompt": (
            "The boy from image 2 standing in this corridor holding a brushed-aluminum "
            "tablet device. Same face, same shaggy dark hair. "
            "Concrete grey jacket, tool belt. The device screen casts cyan wireframe "
            "light upward onto his face and the ceiling. A small cyan wireframe cat "
            "visible on the screen. He holds it carefully — like something alive. "
            "Dark corridor, cold fluorescent strips, one point of cyan warmth. "
            "Full figure visible."
        ),
    },
    "kai_watched": {
        "desc": "Kai from distance — Neda's surveillance POV",
        "image": LOC_MAINTENANCE,
        "image2": KAI_ANCHOR,
        "prompt": (
            "The boy from image 2 seen from distance, from behind a corridor junction. "
            "He does not know he is being watched. Crouched at a wall panel, "
            "device in one hand, cyan glow on the polymer floor around him. "
            "Same shaggy dark hair, same slight build. "
            "Empty corridor, end of shift, fluorescent and cold. "
            "He is the only warm thing in the frame. Voyeuristic surveillance composition."
        ),
    },
}


# ---------------------------------------------------------------------------
# API Helper
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


def save(data, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as f:
        f.write(data)
    size = Image.open(io.BytesIO(data)).size
    print(f"    Saved: {path.name} ({size[0]}x{size[1]})")
    return path


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Generate hero refs via qwen-edit from anchors")
    parser.add_argument("--shot", choices=list(SHOTS.keys()) + ["all"],
                        default="all", help="Which shot to generate")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    targets = SHOTS if args.shot == "all" else {args.shot: SHOTS[args.shot]}

    if args.dry_run:
        print(f"Would generate {len(targets)} hero refs to {OUTPUT_DIR}")
        for name, shot in targets.items():
            img2 = Path(shot["image2"]).name if shot["image2"] else "—"
            print(f"  {name}.png — {shot['desc']}")
            print(f"    image: {Path(shot['image']).name} | image2: {img2}")
        sys.exit(0)

    # Verify anchors exist
    for p in [NEDA_ANCHOR, KAI_ANCHOR]:
        if not p.exists():
            print(f"ERROR: Anchor not found: {p}")
            sys.exit(1)

    print("=" * 70)
    print("Stray Signal — Hero Refs (Qwen-Edit from Anchors)")
    print(f"Neda anchor: {NEDA_ANCHOR.name}")
    print(f"Kai anchor:  {KAI_ANCHOR.name}")
    print(f"Output: {OUTPUT_DIR}")
    print("=" * 70)

    total = len(targets)
    for i, (name, shot) in enumerate(targets.items(), 1):
        filepath = OUTPUT_DIR / f"{name}.png"

        if filepath.exists():
            print(f"\n[{i}/{total}] SKIP (exists): {name}.png")
            continue

        print(f"\n[{i}/{total}] {name}.png")
        print(f"  {shot['desc']}")

        # Check location ref exists for composited shots
        if shot["image2"] and not Path(shot["image"]).exists():
            print(f"    SKIP — location ref not found: {shot['image']}")
            continue

        seed = 15000 + i * 100

        try:
            data = qwen_edit(
                prompt=shot["prompt"],
                image_path=shot["image"],
                image2_path=shot["image2"],
                seed=seed,
                steps=4,
            )
            save(data, filepath)
        except Exception as e:
            print(f"    ERROR: {e}")
            continue

    print(f"\n{'=' * 70}")
    print("QWEN HERO REFS COMPLETE")
    print("=" * 70)
