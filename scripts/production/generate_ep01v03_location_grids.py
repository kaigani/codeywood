#!/usr/bin/env python3
"""
EP01 v03 — Multi-angle location reference grids.

Generates 2x2 reference grids showing 4 different angles/framings of each
key location. This gives the compositing pipeline flexibility — no more
pasting characters onto the same flat perspective every time.

Locations:
  1. grid_streets     — Brutalist city streets (clips 1, 2, 9)
  2. grid_corridor    — Maintenance corridor beneath education block (clips 10, 11)
  3. seam_descent     — Transition space, stone + amber (clip 4)
  4. seam_interior    — Underground community space (clip 4 background)
  5. seam_alcove      — Small briefing room, stone table (clips 6, 7)
  6. fens_room        — Grow-lamp room, doorway framing (clip 5)

Pipeline: ComfyUI qwen-image-edit (local, $0.00)
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
OUTPUT_DIR = PROJECT / "PRODUCTION" / "EP01_v03" / "location_grids"

# Source references
GRID_PLAZA = REFS / "style_inspiration" / "grid_plaza_zimage.png"
GRID_CORRIDOR_STYLE = REFS / "style_inspiration" / "grid_corridor_zimage.png"
LOC_CORRIDOR = REFS / "location_refs" / "v2" / "loc_corridor.png"
LOC_SEAM_MAIN = REFS / "location_refs" / "v2" / "loc_seam_main.png"
LOC_FEN_ROOM = REFS / "location_refs" / "loc_fen_room.png"
SEAM_INTERIOR = REFS / "style_inspiration" / "seam_interior_seedream.png"
LOC_MAINTENANCE = REFS / "location_refs" / "v2" / "loc_maintenance_sector.png"

# Style prefix
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
# Location Grids
# ---------------------------------------------------------------------------

LOCATIONS = {
    "grid_streets": {
        "ref1": GRID_PLAZA,
        "ref2": GRID_CORRIDOR_STYLE,
        "seed": 4001,
        "prompt": (
            STYLE +
            "2x2 composite reference grid on neutral dark background (#2d2d2d). "
            "Professional location reference sheet. Thin black dividing lines between panels. "
            "All panels show the SAME brutalist dystopian city street — concrete, polymer, "
            "4500K cold lighting, geometric angular architecture, no warmth, no decoration. "
            "Dawn to late afternoon light. No people in any panel.\n\n"
            "TOP LEFT: Wide establishing shot looking DOWN a long brutalist street. "
            "Vanishing point perspective. Monolithic concrete towers on both sides. "
            "Cold steel-blue dawn light. A drone small in the upper sky.\n\n"
            "TOP RIGHT: Medium street-level view from LOW ANGLE looking up at the "
            "buildings. Concrete walls rise like canyon walls. 4500K overhead lighting. "
            "Polymer pavement in foreground. Oppressive vertical scale.\n\n"
            "BOTTOM LEFT: Wide shot of a STREET JUNCTION — where two brutalist corridors "
            "meet. A ground-level maintenance grate visible in the polymer pavement. "
            "Angular geometry. Late afternoon cold light from the side.\n\n"
            "BOTTOM RIGHT: Medium shot looking ALONG a brutalist street with citizens "
            "walking at uniform spacing — geometric angular clothing, steel-blue and grey, "
            "all moving in the same direction. 4500K flat lighting. Regulation uniformity."
        ),
    },

    "grid_corridor": {
        "ref1": LOC_CORRIDOR,
        "ref2": LOC_MAINTENANCE,
        "seed": 4002,
        "prompt": (
            STYLE +
            "2x2 composite reference grid on neutral dark background (#2d2d2d). "
            "Professional location reference sheet. Thin black dividing lines between panels. "
            "All panels show the SAME maintenance corridor beneath an education block — "
            "fluorescent strip lighting, polymer floor, institutional walls, sterile. "
            "No people in any panel.\n\n"
            "TOP LEFT: Wide shot looking DOWN the corridor from one end. Long vanishing "
            "point perspective. Fluorescent strips on ceiling. Polymer floor reflecting "
            "cold light. Institutional walls. Empty. The corridor stretches ahead.\n\n"
            "TOP RIGHT: Medium shot from the MIDDLE of the corridor looking toward a "
            "T-junction at the end. Side corridors branching off. Fluorescent lighting "
            "from overhead. The perspective is shallower — we are inside, not outside.\n\n"
            "BOTTOM LEFT: Close-medium shot of the corridor WALL and FLOOR detail — "
            "polymer surface, institutional texture, a maintenance panel, cable conduit. "
            "Fluorescent light from above casts flat even illumination. Texture reference.\n\n"
            "BOTTOM RIGHT: Wide shot from a HIGH ANGLE looking down the corridor at "
            "approximately 30 degrees. The full width of the corridor visible. Fluorescent "
            "strips create even light pools. The perspective is surveillance-like — "
            "clinical, watchful. Empty corridor stretching away."
        ),
    },

    "seam_descent": {
        "ref1": SEAM_INTERIOR,
        "ref2": LOC_SEAM_MAIN,
        "seed": 4003,
        "prompt": (
            STYLE +
            "2x2 composite reference grid on neutral dark background (#2d2d2d). "
            "Professional location reference sheet. Thin black dividing lines between panels. "
            "All panels show the SAME underground transition space — where the cold Grid "
            "surface gives way to the warm Seam underground. Rough stone replacing smooth "
            "polymer. Amber LED string lights. No people.\n\n"
            "TOP LEFT: Wide shot looking DOWN stone steps descending into warm amber light. "
            "The top of the steps is cold blue-grey (Grid world). The bottom glows amber. "
            "Rough stone walls. The color temperature transition is dramatic.\n\n"
            "TOP RIGHT: Medium shot at the BOTTOM of the descent, looking back UP the "
            "stone steps toward cold light above. We are in the warm world looking toward "
            "the cold. Amber string lights on rough stone walls around us.\n\n"
            "BOTTOM LEFT: Wide shot of the transition MIDPOINT — half cold, half warm. "
            "Stone walls with amber LEDs beginning. Rough texture. A narrow passage "
            "opening into wider space below. The shift from institutional to organic.\n\n"
            "BOTTOM RIGHT: Medium shot of the FIRST VIEW of the Seam from the bottom "
            "of the steps. Looking into the main underground space — amber string lights, "
            "rough stone opening up, warm golden light ahead. The promise of community."
        ),
    },

    "seam_interior": {
        "ref1": LOC_SEAM_MAIN,
        "ref2": SEAM_INTERIOR,
        "seed": 4004,
        "prompt": (
            STYLE +
            "2x2 composite reference grid on neutral dark background (#2d2d2d). "
            "Professional location reference sheet. Thin black dividing lines between panels. "
            "All panels show the SAME underground community space (The Seam) — rough stone "
            "walls, amber LED string lights, warm golden light, salvaged furniture, art. "
            "A lived-in underground sanctuary. No people.\n\n"
            "TOP LEFT: Wide establishing shot of the main Seam space. High ceiling of rough "
            "stone. Amber string lights criss-crossing overhead. Salvaged tables, a colorful "
            "mural on one wall, plants growing under lights. Warm, messy, alive.\n\n"
            "TOP RIGHT: Medium shot of a CORRIDOR in the Seam — rough stone walls, amber "
            "string lights along the ceiling, doors or openings branching off to private "
            "rooms. Intimate, narrower than the main space. Warm amber light.\n\n"
            "BOTTOM LEFT: Medium shot of a DETAIL AREA — a salvaged table with items on it "
            "(seeds, tools, a guitar leaning against the wall). String lights close. The "
            "texture of underground life — rough, warm, personal, handmade.\n\n"
            "BOTTOM RIGHT: Wide shot of the Seam from a DIFFERENT ANGLE — looking across "
            "the main space toward the mural wall. Amber light from a different direction. "
            "Depth visible — alcoves, passages leading away. The space has layers."
        ),
    },

    "seam_alcove": {
        "ref1": LOC_SEAM_MAIN,
        "ref2": SEAM_INTERIOR,
        "seed": 4005,
        "prompt": (
            STYLE +
            "2x2 composite reference grid on neutral dark background (#2d2d2d). "
            "Professional location reference sheet. Thin black dividing lines between panels. "
            "All panels show the SAME small underground briefing alcove — a private room "
            "carved from rough stone, intimate, confined, with a stone table. Part of an "
            "underground resistance community. No people.\n\n"
            "TOP LEFT: Wide shot of the small alcove from the DOORWAY looking in. Low rough "
            "stone ceiling. A simple stone table with two seats. Amber LED string lights "
            "providing warm golden light. Stone walls close on all sides. Private, confined.\n\n"
            "TOP RIGHT: Medium shot from INSIDE the alcove looking at the table from one "
            "seat's perspective. The opposite seat visible across the stone table. Amber "
            "light from above. Rough stone wall behind the opposite seat. Close quarters.\n\n"
            "BOTTOM LEFT: Close-medium shot of the TABLE SURFACE and hands-level view — "
            "rough-hewn stone table, the texture of carved rock, amber light pooling on "
            "the surface. The kind of table where difficult decisions are made.\n\n"
            "BOTTOM RIGHT: Medium shot from the CORNER of the alcove — showing both the "
            "doorway (warmer amber corridor light beyond) and the table arrangement. Two "
            "distinct light sources: overhead amber in the room, corridor amber through door."
        ),
    },

    "fens_room": {
        "ref1": LOC_FEN_ROOM,
        "ref2": SEAM_INTERIOR,
        "seed": 4006,
        "prompt": (
            STYLE +
            "2x2 composite reference grid on neutral dark background (#2d2d2d). "
            "Professional location reference sheet. Thin black dividing lines between panels. "
            "All panels show the SAME small underground room lit by grow-lamps — green-white "
            "overhead light, different from the amber of the surrounding corridors. A room "
            "for growing plants, repurposed as a living space. Sparse. Still. No people.\n\n"
            "TOP LEFT: Wide shot from the DOORWAY looking in. The doorway frame is visible — "
            "warm amber corridor light on the door edges. Inside: green-white grow-lamps "
            "overhead. A chair or low seat in the center. Sparse furnishing. The contrast "
            "between amber doorway and green-white interior is stark.\n\n"
            "TOP RIGHT: Medium shot from INSIDE the room looking toward the doorway. "
            "Green-white grow-lamp light filling the room. The doorway shows warm amber "
            "corridor light beyond — a rectangle of warmth in a green-white room. The "
            "perspective of someone sitting inside, looking out.\n\n"
            "BOTTOM LEFT: Close-medium shot of the GROW-LAMPS themselves — overhead panels "
            "casting green-white light downward. Plant trays or growing shelves visible. "
            "The clinical quality of the light. Sterile compared to the Seam's warmth.\n\n"
            "BOTTOM RIGHT: Wide shot from a SIDE ANGLE — showing the room's depth. The "
            "chair/seat visible in profile. Grow-lamps overhead. The room is small but has "
            "vertical space. Green-white light creates long shadows on rough stone walls."
        ),
    },
}


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Generate EP01 v03 multi-angle location grids")
    parser.add_argument("--location", choices=list(LOCATIONS.keys()) + ["all"],
                        default="all", help="Which location to generate (default: all)")
    parser.add_argument("--dry-run", action="store_true", help="Print what would be generated")
    args = parser.parse_args()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Output dir: {OUTPUT_DIR}")

    targets = LOCATIONS.keys() if args.location == "all" else [args.location]

    if args.dry_run:
        print("\n[DRY RUN] Would generate:")
        for name in targets:
            loc = LOCATIONS[name]
            print(f"\n  {name}:")
            print(f"    ref1: {Path(loc['ref1']).name}")
            print(f"    ref2: {Path(loc['ref2']).name}" if loc.get('ref2') else "    ref2: none")
            print(f"    seed: {loc['seed']}")
        sys.exit(0)

    for name in targets:
        loc = LOCATIONS[name]
        print(f"\n{'=' * 70}")
        print(f"LOCATION: {name}")
        print(f"{'=' * 70}")

        ref2 = loc.get("ref2")
        print(f"  Generating from {Path(loc['ref1']).name}" +
              (f" + {Path(ref2).name}" if ref2 else "") + "...")

        data = qwen_edit(
            loc["prompt"],
            loc["ref1"],
            image2_path=ref2,
            seed=loc["seed"],
            steps=4,
        )
        save(data, OUTPUT_DIR / f"{name}_grid.png")

    print(f"\n{'=' * 70}")
    print("DONE")
    print(f"{'=' * 70}")
