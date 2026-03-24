#!/usr/bin/env python3
"""
EP01 v03 "Handler" — Production Frame Generation

Uses locked character anchors + curated location refs via qwen-image-edit
to generate start frames for all 23 AI-generated clips.

Character anchors:
  - Neda portrait: hero_shots/v3/neda_portrait_seam.png (CU shots)
  - Neda identity: hero_shots/v3/qwen/neda_identity.png (full body shots)
  - Kai portrait:  hero_shots/v3/kai_portrait_grid.png (CU shots)
  - Kai identity:  hero_shots/v3/qwen/kai_identity_tall_17002.png (full body shots)

Location refs: exploration_v3/locations/ (curated set)

Pipeline: ComfyUI qwen-image-edit (local, $0.00)
Output: projects/stray-signal/PRODUCTION/EP01_v03/frames/
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
OUTPUT_DIR = PROJECT / "PRODUCTION" / "EP01_v03" / "frames"

# Character anchors
NEDA_PORTRAIT = REFS / "hero_shots" / "v3" / "neda_portrait_seam.png"
NEDA_IDENTITY = REFS / "hero_shots" / "v3" / "qwen" / "neda_identity.png"
KAI_PORTRAIT = REFS / "hero_shots" / "v3" / "kai_portrait_grid.png"
KAI_IDENTITY = REFS / "hero_shots" / "v3" / "qwen" / "kai_identity_tall_17002.png"

# Location refs (curated from exploration_v3)
LOC_GRID_STREET = REFS / "exploration_v3" / "locations" / "loc_grid_street_canyon.png"
LOC_DESCENT_COLD = REFS / "exploration_v3" / "locations" / "loc_descent_upper_cold.png"
LOC_DESCENT_MID = REFS / "exploration_v3" / "locations" / "loc_descent_middle_transition.png"
LOC_SEAM_WIDE = REFS / "exploration_v3" / "locations" / "loc_seam_corridor_wide.png"
LOC_SEAM_INTIMATE = REFS / "exploration_v3" / "locations" / "loc_seam_corridor_intimate.png"
LOC_SEAM_JUNCTION = REFS / "exploration_v3" / "locations" / "loc_seam_corridor_junction.png"
LOC_FEN_ROOM = REFS / "exploration_v3" / "locations" / "loc_fen_room_doorway.png"
LOC_BRIEFING = REFS / "exploration_v3" / "locations" / "loc_briefing_alcove_spartan.png"
LOC_MAINTENANCE = REFS / "exploration_v3" / "locations" / "loc_maintenance_corridor_end_of_shift.png"
LOC_MAINT_GLOW = REFS / "exploration_v3" / "locations" / "loc_maintenance_corridor_with_glow.png"

# Style prefix for z-image-only shots (no character ref available)
STYLE = (
    "In the style of The Legend of Korra, bold clean ink outlines, "
    "flat cel-shaded coloring, realistic proportions with angular features, "
    "cinematic composition, dark atmospheric palette, "
    "animation production frame, "
)
NEGATIVE = (
    "photorealistic, 3D render, watercolor, concept art, painting, "
    "smooth digital coloring, airbrushed, soft gradients, "
    "chibi, super-deformed, big eyes, pointy chin, "
    "soft glow, bloom, lens flare, neon, cyberpunk, "
    "blurry, low quality, deformed, extra limbs, bad anatomy, "
    "text, watermark, signature, bright saturated colors"
)

# ---------------------------------------------------------------------------
# Frame definitions
# ---------------------------------------------------------------------------
# method: "qwen" (qwen-image-edit) or "zimage" (z-image-base-t2i)
# For qwen: image = first slot (sets aspect), image2 = second slot
# For zimage: prompt only, no image refs

FRAMES = {
    # === THE GRID — Unease + Rooting ===
    "01_cityscape_dawn": {
        "shot": 1,
        "desc": "Wide brutalist cityscape, dawn, no people, drone",
        "method": "qwen",
        "image": LOC_GRID_STREET,
        "image2": None,
        "prompt": (
            "Same style as this image. Wide establishing shot of a brutalist "
            "dystopian cityscape at dawn. Monolithic concrete blocks rising without "
            "ornament against cold steel-blue sky. A single small surveillance drone "
            "in the upper frame. No people. Concrete grey and steel blue palette. "
            "Vanishing point perspective. The scale is monumental and oppressive."
        ),
    },
    "02_neda_on_grid": {
        "shot": 2,
        "desc": "Neda medium shot, walking on Grid street",
        "method": "qwen",
        "image": LOC_GRID_STREET,
        "image2": NEDA_IDENTITY,
        "prompt": (
            "The girl from image 2 walking through this brutalist concrete street. "
            "Same face, same brown skin, same asymmetric black hair. "
            "Angular steel-blue geometric jacket, concrete grey trousers. "
            "Medium shot. One or two distant figures in identical grey clothing behind her. "
            "She moves at the same pace but her eyes are different — aware, scanning. "
            "4500K flat fluorescent lighting. Desaturated palette."
        ),
    },
    "03_neda_at_grate": {
        "shot": 3,
        "desc": "Neda approaching maintenance grate",
        "method": "qwen",
        "image": LOC_GRID_STREET,
        "image2": NEDA_IDENTITY,
        "prompt": (
            "The girl from image 2 in this brutalist street, approaching a "
            "maintenance grate at ground level. Same face, steel-blue jacket. "
            "Medium-wide shot. A polymer grate cover visible in the lower portion "
            "of the frame. She approaches it with purpose, no hesitation. "
            "Cold fluorescent light. Empty street. Concrete walls."
        ),
    },
    "04_the_drop": {
        "shot": 4,
        "desc": "Figure at grate edge, about to descend",
        "method": "qwen",
        "image": LOC_GRID_STREET,
        "image2": NEDA_IDENTITY,
        "prompt": (
            "The girl from image 2 crouched at an open maintenance grate in this "
            "concrete street. Wide shot. The grate is open — dark opening visible. "
            "She is at the edge, steel-blue jacket visible, about to drop below. "
            "Cold steel-blue light. Empty street around her. The moment before "
            "she disappears."
        ),
    },

    # === DESCENT — Relief gradient ===
    # NOTE: Descent locations are portrait (720x1280). Use LOC_SEAM_WIDE (landscape)
    # as image slot to set aspect, descent location as image2 for style reference.
    "06_descent_cold": {
        "shot": 6,
        "desc": "Neda descending polymer steps, cold light",
        "method": "qwen",
        "image": LOC_SEAM_WIDE,
        "image2": NEDA_IDENTITY,
        "prompt": (
            "The girl from image 2 descending narrow polymer steps in a vertical "
            "passage, seen from behind. Same steel-blue jacket. Cold fluorescent "
            "strip lights on smooth polymer walls. She moves downward steadily. "
            "Grid-tight posture — shoulders held, controlled. "
            "Cold steel-blue palette throughout. No amber light. Medium shot from behind. "
            "Narrow stairwell, not a corridor."
        ),
    },
    "07_descent_transition": {
        "shot": 7,
        "desc": "Neda in transition zone — cold above, warm below",
        "method": "qwen",
        "image": LOC_SEAM_WIDE,
        "image2": NEDA_IDENTITY,
        "prompt": (
            "The girl from image 2 descending steps through a transition zone. "
            "Same steel-blue jacket. Mixed lighting — cold fluorescent above, "
            "first amber LED string lights below. Polymer walls giving way to "
            "rough stone. She is between worlds. Medium shot. "
            "Her shoulders beginning to drop — a centimeter. "
            "Half cold blue, half warm amber in the frame."
        ),
    },
    "08_descent_warm": {
        "shot": 8,
        "desc": "Neda arriving in The Seam, full warm amber",
        "method": "qwen",
        "image": LOC_SEAM_WIDE,
        "image2": NEDA_IDENTITY,
        "prompt": (
            "The girl from image 2 entering this underground space from stone steps "
            "at the right side. Wide shot. She now wears Seam clothing — dark fitted "
            "jacket, rust underlayer. Or she is removing her Grid jacket. "
            "Amber string lights overhead. Warm golden glow on everything. "
            "Her posture is looser, natural. She belongs here."
        ),
    },

    # === FEN — Dread ===
    "09_corridor_approach": {
        "shot": 9,
        "desc": "Neda walking through Seam corridor, door ahead",
        "method": "qwen",
        "image": LOC_SEAM_INTIMATE,
        "image2": NEDA_PORTRAIT,
        "prompt": (
            "The girl from image 2 walking through this underground stone corridor. "
            "Same face, brown skin, asymmetric hair. Seam clothing — dark jacket, "
            "rust underlayer. Medium shot. A door and branching corridor visible ahead. "
            "Amber string lights. She walks with purpose but is about to slow."
        ),
    },
    "10_fens_room": {
        "shot": 10,
        "desc": "Doorway composition — Neda foreground, Fen silhouette",
        "method": "qwen",
        "image": LOC_FEN_ROOM,
        "image2": NEDA_PORTRAIT,
        "prompt": (
            "View through this doorway. The girl from image 2 stands in the "
            "doorway foreground, seen from behind — dark jacket, asymmetric hair. "
            "Looking into the room. Inside: a figure seated in silhouette, "
            "backlit by grow-lamps. Absolutely still. The posture of furniture. "
            "Two lighting zones: warm amber doorway, green-white room. "
            "Wide composition. She does not enter."
        ),
    },
    "11_neda_walks_on": {
        "shot": 11,
        "desc": "Neda walking forward in Seam corridor, green glow behind",
        "method": "qwen",
        "image": LOC_SEAM_INTIMATE,
        "image2": NEDA_PORTRAIT,
        "prompt": (
            "The girl from image 2 walking forward through this stone corridor. "
            "Same face, same brown skin, same asymmetric black hair. "
            "Seam clothing — dark fitted jacket, rust underlayer. "
            "Medium shot from the front, she walks toward camera. "
            "Behind her a faint green-white glow from a doorway she has passed. "
            "Amber string lights ahead. Jaw tight. Expression controlled. "
            "She does not look back."
        ),
    },

    # === BRIEFING — Investment + Silence ===
    # NOTE: LOC_BRIEFING (landscape) must be image slot to set aspect.
    # NEDA_PORTRAIT as image2 for character reference.
    "12_briefing_intel": {
        "shot": 12,
        "desc": "Neda CU, briefing alcove, listening",
        "method": "qwen",
        "image": LOC_BRIEFING,
        "image2": NEDA_PORTRAIT,
        "prompt": (
            "The girl from image 2 in this stone briefing alcove. Close-up. "
            "Same face, same brown skin, same asymmetric black hair. "
            "Deep amber light on her face. Dark eyes sharp, listening. "
            "Her scarred right hand on the rough stone table. "
            "Seam clothing — dark jacket, rust underlayer. "
            "Expression: absorbing information that costs something."
        ),
    },
    "13_briefing_volunteer": {
        "shot": 13,
        "desc": "Neda CU tighter, leaning forward, 'I'll go'",
        "method": "qwen",
        "image": LOC_BRIEFING,
        "image2": NEDA_PORTRAIT,
        "prompt": (
            "The girl from image 2 in this stone briefing alcove. Tighter close-up. "
            "Same face, same brown skin, same asymmetric hair. "
            "Amber light on her face. Jaw set. Eyes direct. Copper-wire braid "
            "behind left ear catches the light. Leaning forward slightly. "
            "Controlled conviction. She is volunteering."
        ),
    },
    "14_briefing_argument": {
        "shot": 14,
        "desc": "Neda CU tightest, jaw set, fist on table",
        "method": "qwen",
        "image": LOC_BRIEFING,
        "image2": NEDA_PORTRAIT,
        "prompt": (
            "The girl from image 2 in this stone briefing room. Tightest close-up. "
            "Same face, same brown skin. Leaning further forward. "
            "Amber light, copper braid. Jaw tightening visibly. "
            "Right fist gripping the stone table edge. Not anger — necessity. "
            "Conviction that costs something."
        ),
    },
    "15_briefing_silence": {
        "shot": 15,
        "desc": "Neda CU, stillness after the argument, amber",
        "method": "qwen",
        "image": LOC_BRIEFING,
        "image2": NEDA_PORTRAIT,
        "prompt": (
            "The girl from image 2 in this stone briefing room. Close-up. "
            "Same face, same brown skin. The stillness after conviction. "
            "Amber light heavy on her face. She does not look away. "
            "She does not soften. Jaw held. Eyes steady. "
            "The weight of what she said hanging in the amber light."
        ),
    },

    # === RETURN — Commitment gradient ===
    "16_return_warm": {
        "shot": 16,
        "desc": "Neda in Seam corridor, purposeful, last warmth",
        "method": "qwen",
        "image": LOC_SEAM_JUNCTION,
        "image2": NEDA_PORTRAIT,
        "prompt": (
            "The girl from image 2 walking with purpose through this underground "
            "junction. Same face, Seam clothing — dark jacket, rust underlayer. "
            "Amber string lights. A branching corridor visible — she does not look "
            "toward it. She moves toward stone steps ahead. Medium shot. "
            "Decision in every line of her body."
        ),
    },
    # NOTE: Descent locations are portrait. Use LOC_SEAM_WIDE (landscape) as image slot.
    "17_return_transition": {
        "shot": 17,
        "desc": "Neda ascending, warm below cold above",
        "method": "qwen",
        "image": LOC_SEAM_WIDE,
        "image2": NEDA_IDENTITY,
        "prompt": (
            "The girl from image 2 ascending narrow steps — moving upward. "
            "Same face. Mixed lighting: amber light from below fading, "
            "cold steel-blue growing from above. Rough stone becoming smooth "
            "polymer. She is between worlds, ascending. Her posture is tightening — "
            "shoulders rising. She is becoming Grid-Neda again. Medium shot. "
            "Half warm amber below, half cold blue above."
        ),
    },
    "18_return_surface": {
        "shot": 18,
        "desc": "Neda emerging into cold tunnel, Grid clothes restored",
        "method": "qwen",
        "image": LOC_GRID_STREET,
        "image2": NEDA_IDENTITY,
        "prompt": (
            "The girl from image 2 emerging from a maintenance grate into "
            "a cold polymer tunnel. Same face. Now wearing angular steel-blue "
            "jacket, geometric collar — Grid-Neda restored. Cold fluorescent light "
            "on her face. The warmth is gone. Medium shot. "
            "Posture tight, jaw set, eyes scanning. Brutalist concrete around her."
        ),
    },

    # === GRID WITH PURPOSE — Curiosity + The Turn ===
    "19_grid_mission": {
        "shot": 19,
        "desc": "Neda on Grid street, mission pace, drone overhead",
        "method": "qwen",
        "image": LOC_GRID_STREET,
        "image2": NEDA_IDENTITY,
        "prompt": (
            "The girl from image 2 moving through this brutalist street. "
            "Same face, steel-blue jacket. Wide shot. Late afternoon — shadows "
            "slightly longer. She moves differently now — faster, more direct. "
            "Mission pace. A drone visible overhead. Same world as the opening "
            "but different energy."
        ),
    },
    "20_corridor_empty": {
        "shot": 20,
        "desc": "Empty maintenance corridor, vanishing point",
        "method": "qwen",
        "image": LOC_MAINTENANCE,
        "image2": None,
        "prompt": (
            "Same style as this image. Empty maintenance corridor. "
            "Fluorescent strip lighting. Polymer floor. Vanishing point perspective. "
            "End of shift. Every shadow engineered out. Sterile. Cold blue-white light. "
            "No people visible. The corridor stretches to nothing."
        ),
    },
    "21_kai_approaches": {
        "shot": 21,
        "desc": "Kai walking in corridor, device with cyan glow",
        "method": "qwen",
        "image": LOC_MAINTENANCE,
        "image2": KAI_IDENTITY,
        "prompt": (
            "The boy from image 2 walking toward camera in this maintenance corridor. "
            "Same face, same shaggy dark hair, same light brown skin. "
            "Concrete grey jacket, tool belt. Medium shot. "
            "In his hand: a brushed-aluminum device with faint cyan wireframe glow. "
            "The cyan light reflects onto his face and fingers. "
            "He is absorbed in the device, unaware. Single figure, alone."
        ),
    },
    "22_kai_glow_detail": {
        "shot": 22,
        "desc": "Device CU, cyan glow on fingers",
        "method": "qwen",
        "image": LOC_MAINTENANCE,
        "image2": KAI_PORTRAIT,
        "prompt": (
            "Extreme close-up of the boy from image 2's hands holding a "
            "brushed-aluminum device. Same light brown skin, lean fingers. "
            "The screen shows a small cyan wireframe cat form. "
            "Cyan glow on his fingertips and the polymer surface below. "
            "The device is scratched, dented. Dark maintenance corridor background. "
            "The cyan is the only color."
        ),
    },
    "23_neda_watching": {
        "shot": 23,
        "desc": "Neda CU, Grid corridor, cyan reflection, jaw tightening",
        "method": "qwen",
        "image": LOC_MAINTENANCE,
        "image2": NEDA_PORTRAIT,
        "prompt": (
            "The girl from image 2 in this cold corridor. Close-up. "
            "Same face, same brown skin, same asymmetric hair. Steel-blue jacket. "
            "Cold fluorescent light. A faint cyan glow reflects on the right "
            "side of her face from something ahead. Her jaw is tightening — "
            "the signature tell. Calculation, recognition, "
            "and something she is trying very hard not to feel."
        ),
    },
    "24_neda_moves_forward": {
        "shot": 24,
        "desc": "Neda medium shot, stepping toward distant cyan",
        "method": "qwen",
        "image": LOC_MAINT_GLOW,
        "image2": NEDA_IDENTITY,
        "prompt": (
            "The girl from image 2 standing in this corridor with the distant "
            "cyan glow ahead. Same face, steel-blue jacket. Medium shot. "
            "She is about to take a step forward — toward the glow, toward "
            "the boy who does not know she is there. Expression resolved "
            "from dread into purpose. One foot slightly forward."
        ),
    },
}


# ---------------------------------------------------------------------------
# API Helpers
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


def normalize(png_bytes, target_w=1280, target_h=720):
    """Normalize qwen-edit output to production frame dimensions."""
    img = Image.open(io.BytesIO(png_bytes))
    if img.size != (target_w, target_h):
        img = img.resize((target_w, target_h), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


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
    parser = argparse.ArgumentParser(description="Generate EP01 v03 production frames")
    parser.add_argument("--shot", default="all",
                        help="Shot name or 'all' (default: all)")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    if args.shot == "all":
        targets = FRAMES
    else:
        targets = {k: v for k, v in FRAMES.items() if args.shot in k}
        if not targets:
            print(f"No shots matching '{args.shot}'")
            sys.exit(1)

    if args.dry_run:
        print(f"Would generate {len(targets)} frames to {OUTPUT_DIR}")
        for name, f in targets.items():
            img2 = Path(f["image2"]).name if f.get("image2") else "—"
            print(f"  {name}.png (shot {f['shot']}) — {f['desc']}")
            print(f"    {f['method']} | image: {Path(f['image']).name} | image2: {img2}")
        sys.exit(0)

    # Verify all refs exist
    missing = []
    for name, f in targets.items():
        if not Path(f["image"]).exists():
            missing.append(f"  {name}: {f['image']}")
        if f.get("image2") and not Path(f["image2"]).exists():
            missing.append(f"  {name}: {f['image2']}")
    if missing:
        print("ERROR: Missing reference files:")
        for m in missing:
            print(m)
        sys.exit(1)

    print("=" * 70)
    print("EP01 v03 — Production Frame Generation")
    print(f"Output: {OUTPUT_DIR}")
    print(f"Frames: {len(targets)}")
    print("=" * 70)

    total = len(targets)
    for i, (name, f) in enumerate(targets.items(), 1):
        filepath = OUTPUT_DIR / f"{name}.png"

        if filepath.exists():
            print(f"\n[{i}/{total}] SKIP (exists): {name}.png")
            continue

        print(f"\n[{i}/{total}] {name}.png (shot {f['shot']})")
        print(f"  {f['desc']}")

        seed = 20000 + f["shot"] * 100

        try:
            data = qwen_edit(
                prompt=f["prompt"],
                image_path=f["image"],
                image2_path=f.get("image2"),
                seed=seed,
                steps=4,
            )
            # Normalize all frames to 1280x720 production size
            data = normalize(data)
            save(data, filepath)
        except Exception as e:
            print(f"    ERROR: {e}")
            continue

    print(f"\n{'=' * 70}")
    print("FRAME GENERATION COMPLETE")
    print("=" * 70)
