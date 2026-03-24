#!/usr/bin/env python3
"""
Stray Signal — Locked Hero Reference Generation v3

Generates the definitive character reference set for Neda and Kai using
the locked "Concrete & Ink" style DNA and the approved character designs
from exploration_v3.

Neda: asymmetric hair (shaved left, swept right), copper braid, angular face
Kai: shaggy overgrown cut falling in eyes, softer rounder face

Pipeline: ComfyUI z-image-base-t2i (local, $0.00)
Output: projects/stray-signal/REFERENCES/hero_shots/v3/
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
OUTPUT_DIR = PROJECT / "REFERENCES" / "hero_shots" / "v3"

# ---------------------------------------------------------------------------
# LOCKED STYLE — Korra anchor (from PROJECT_CONFIG.yaml)
# ---------------------------------------------------------------------------
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
# LOCKED CHARACTER DESCRIPTIONS
# ---------------------------------------------------------------------------

NEDA_FACE = (
    "17-year-old girl, compact athletic build, brown skin with warm undertone, "
    "angular face with strong jaw and high cheekbones, sharp dark assessing eyes, "
    "black hair in an asymmetric cut — shaved close on the left side "
    "with longer hair swept across to the right falling just past the ear, "
    "thin copper-wire braid hanging from the shaved left side exposed and visible, "
    "scar across right knuckles, "
)

NEDA_GRID = (
    "angular steel-blue geometric jacket with origami-folded collar and sharp "
    "shoulder panels, grey underlayer visible at the neckline, "
    "high-waisted fitted trousers in concrete grey, polymer-soled boots, "
    "posture upright and space-claiming, expression controlled and neutral, "
    "subtle jaw tension visible, "
)

NEDA_SEAM = (
    "fitted dark brown jacket with visible hand-stitching over rust-colored underlayer, "
    "copper-wire braid catching amber light, tool harness across chest "
    "with junction access instruments, cargo pockets on worn trousers, "
    "boots with real scuffs and patina, posture sharp and direct, "
    "expression focused and operational, "
)

KAI_FACE = (
    "16-year-old boy, lean narrow-shouldered build, light brown skin, "
    "softer rounder face that makes him look younger than 16, "
    "dark hair in a shaggy overgrown regulation cut — sides growing out unevenly, "
    "top long enough to fall across his forehead and into his eyes, "
    "watchful dark eyes that track movement before faces, "
)

KAI_GRID = (
    "angular geometric jacket in concrete grey and pale steel blue "
    "with structured folded panels and high collar, "
    "fitted trousers in pale sage, polymer-soled boots, "
    "maintenance tool belt with small diagnostic instruments at waist, "
    "posture slightly folded inward, shoulders hunched, unremarkable, "
)

KAI_DEVICE = (
    "holding a brushed-aluminum tablet device slightly too large for his hands, "
    "scratched and dented, screen showing faint cyan wireframe cat form, "
    "cyan glow reflected on his face and fingers, "
)

# ---------------------------------------------------------------------------
# HERO REF SHOTS
# ---------------------------------------------------------------------------

SHOTS = {
    # === NEDA ===
    "neda_portrait_grid": {
        "desc": "Neda CU portrait — Grid appearance (primary ref)",
        "prompt": (
            STYLE + "Close-up portrait of " + NEDA_FACE + NEDA_GRID +
            "Brutalist concrete wall background with visible form-tie holes "
            "and speckle texture. Cold flat fluorescent light from above. "
            "Steel-blue and concrete grey palette. "
            "A face that is striking and specific — impossible to forget."
        ),
        "w": 720, "h": 1024, "seed": 11001,
    },
    "neda_portrait_seam": {
        "desc": "Neda CU portrait — Seam appearance",
        "prompt": (
            STYLE + "Close-up portrait of " + NEDA_FACE + NEDA_SEAM +
            "Rough stone wall background with amber LED string lights. "
            "Warm amber light casting deep bronze on brown skin. "
            "Copper braid catching golden light against the shaved side. "
            "The same angular face, now in warm underground light."
        ),
        "w": 720, "h": 1024, "seed": 11002,
    },
    "neda_full_grid": {
        "desc": "Neda full body — Grid street",
        "prompt": (
            STYLE + "Full body shot of " + NEDA_FACE + NEDA_GRID +
            "Standing in a brutalist concrete street canyon — massive walls "
            "on both sides, polymer floor, fluorescent strip lights along lower walls. "
            "Cold steel-blue overcast sky as thin strip above. "
            "She moves through the space with purpose. "
            "Full figure visible head to toe, centered in frame. "
            "The architecture dwarfs her but she takes up space through posture."
        ),
        "w": 1024, "h": 1024, "seed": 11003,
    },
    "neda_full_seam": {
        "desc": "Neda full body — Seam corridor",
        "prompt": (
            STYLE + "Full body shot of " + NEDA_FACE + NEDA_SEAM +
            "Standing in an underground stone corridor with amber string lights "
            "overhead. Rough-hewn walls, salvaged electronics mounted on surfaces. "
            "Warm amber glow on everything. She is sharp and direct here — "
            "no performance, no Grid mask. "
            "Full figure visible head to toe, centered."
        ),
        "w": 1024, "h": 1024, "seed": 11004,
    },
    "neda_detail_hands": {
        "desc": "Neda detail — knuckle scar, hands on stone table",
        "prompt": (
            STYLE + "Extreme close-up of brown-skinned hands gripping the edge "
            "of a rough stone table. White scar tissue across the knuckles of "
            "the right hand against warm brown skin. Angular geometric sleeve cuff "
            "visible at wrist — steel-blue fabric with sharp folds. "
            "Amber light from the left, cool fluorescent from the right. "
            "The hands are strong, practical, scarred from corridors and junction panels."
        ),
        "w": 1024, "h": 720, "seed": 11005,
    },
    "neda_jaw_tell": {
        "desc": "Neda detail — the jaw tighten, signature tell",
        "prompt": (
            STYLE + "Extreme close-up of a girl's lower face and jaw. Brown skin, "
            "angular jaw with tension visible in the masseter muscle — the jaw is "
            "clenched a fraction before speaking. Lips pressed. Asymmetric black hair "
            "falling across one side. Cold fluorescent light from above, "
            "faint cyan reflection from the right side of the face. "
            "Steel-blue geometric collar visible at bottom of frame. "
            "The geometry of the face is precise and specific."
        ),
        "w": 1024, "h": 720, "seed": 11006,
    },
    "neda_three_quarter": {
        "desc": "Neda three-quarter view — shows both hair sides",
        "prompt": (
            STYLE + "Three-quarter view portrait of " + NEDA_FACE + NEDA_GRID +
            "Turned slightly to show both the shaved left side with exposed "
            "copper-wire braid and the swept longer hair on the right. "
            "Brutalist concrete background. Cold flat fluorescent light. "
            "Expression: neutral assessment — she is reading someone offscreen."
        ),
        "w": 720, "h": 1024, "seed": 11007,
    },

    # === KAI ===
    "kai_portrait_grid": {
        "desc": "Kai CU portrait — Grid appearance (primary ref)",
        "prompt": (
            STYLE + "Close-up portrait of " + KAI_FACE + KAI_GRID +
            "Brutalist concrete wall background with visible form-tie holes "
            "and speckle texture. Cold flat fluorescent light from above. "
            "The face is unremarkable at first glance — the kind that disappears "
            "in a crowd. But the eyes are tracking, alive with pattern-hunger."
        ),
        "w": 720, "h": 1024, "seed": 12001,
    },
    "kai_portrait_device": {
        "desc": "Kai CU portrait — lit by device cyan glow",
        "prompt": (
            STYLE + "Close-up portrait of " + KAI_FACE +
            "His face lit from below by cyan wireframe glow from a device screen. "
            "The cyan picks out his cheekbones and the shaggy hair falling across "
            "his forehead. Dark maintenance corridor behind him — no fluorescent light, "
            "just the device glow. His expression: the first real curiosity he has "
            "ever felt. Eyes wide, lips slightly parted. "
            "The cyan is the only color in the frame."
        ),
        "w": 720, "h": 1024, "seed": 12002,
    },
    "kai_full_grid": {
        "desc": "Kai full body — Grid corridor, folded inward",
        "prompt": (
            STYLE + "Full body shot of " + KAI_FACE + KAI_GRID +
            "Standing in a brutalist maintenance corridor — concrete walls, "
            "polymer conduits, fluorescent strip lights overhead casting hard-edged "
            "light pools. He is folded inward, shoulders slightly hunched, "
            "not making eye contact. The corridor is monotone grey. He blends in "
            "perfectly. Full figure visible head to toe. The maintenance tool belt "
            "is his one visual distinction."
        ),
        "w": 1024, "h": 1024, "seed": 12003,
    },
    "kai_full_device": {
        "desc": "Kai full body — corridor with device, cyan glow",
        "prompt": (
            STYLE + "Full body shot of " + KAI_FACE + KAI_GRID + KAI_DEVICE +
            "Standing in a dim maintenance corridor. The device screen casts "
            "cyan wireframe light upward onto his face and the ceiling above him. "
            "A small cyan wireframe cat form visible on the screen. "
            "He holds the device carefully — the way you hold something alive. "
            "Dark corridor, cold fluorescent strips, one point of cyan warmth. "
            "Full figure visible head to toe."
        ),
        "w": 1024, "h": 1024, "seed": 12004,
    },
    "kai_detail_hands": {
        "desc": "Kai detail — hands holding device, cyan glow on fingers",
        "prompt": (
            STYLE + "Extreme close-up of a boy's hands holding a brushed-aluminum "
            "tablet device. Light brown skin, lean fingers, one thumb testing the "
            "edge of the device frame. The screen shows a small cyan wireframe cat "
            "sitting and blinking. Cyan glow cast on his fingertips and the polymer "
            "floor beneath. The device is scratched, dented, warm from use. "
            "Maintenance corridor background, dark with cold fluorescent strips."
        ),
        "w": 1024, "h": 720, "seed": 12005,
    },
    "kai_watched": {
        "desc": "Kai from distance — Neda's surveillance POV",
        "prompt": (
            STYLE + "Medium-wide shot of a 16-year-old boy with lean build, "
            "light brown skin, dark shaggy hair, seen from behind a corridor junction. "
            "He does not know he is being watched. Crouched at a wall panel, "
            "device in one hand, cyan glow on the polymer floor around him. "
            "Empty maintenance corridor at shift-end — fluorescent, cold, monotone. "
            "He is the only warm thing in the frame. "
            "Shot from distance. Voyeuristic surveillance composition."
        ),
        "w": 1280, "h": 720, "seed": 12006,
    },
    "kai_three_quarter": {
        "desc": "Kai three-quarter view — hair falling in eyes",
        "prompt": (
            STYLE + "Three-quarter view portrait of " + KAI_FACE + KAI_GRID +
            "Turned slightly, shaggy hair falling across his forehead and into "
            "his eyes. He pushes it back with one hand but it does not stay. "
            "Brutalist concrete background. Cold flat fluorescent light. "
            "Expression: watching something with quiet intensity — pattern-hunger."
        ),
        "w": 720, "h": 1024, "seed": 12007,
    },
}


# ---------------------------------------------------------------------------
# API Helper
# ---------------------------------------------------------------------------
def submit_and_wait(workflow_id, params, timeout=600):
    url = f"{COMFYUI_BASE}/workflows/{workflow_id}"
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
    parser = argparse.ArgumentParser(description="Generate locked hero refs v3")
    parser.add_argument("--shot", choices=list(SHOTS.keys()) + ["all"],
                        default="all", help="Which shot to generate")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    targets = SHOTS if args.shot == "all" else {args.shot: SHOTS[args.shot]}

    if args.dry_run:
        print(f"Would generate {len(targets)} hero refs to {OUTPUT_DIR}")
        for name, shot in targets.items():
            print(f"  {name}.png — {shot['desc']} ({shot['w']}x{shot['h']})")
        sys.exit(0)

    print("=" * 70)
    print("Stray Signal — Hero Refs v3 (Locked)")
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

        try:
            data = submit_and_wait("z-image-base-t2i", {
                "prompt": shot["prompt"],
                "negative_prompt": NEGATIVE,
                "seed": str(shot["seed"]),
                "steps": "25",
                "cfg": "4",
                "width": str(shot["w"]),
                "height": str(shot["h"]),
            })
            save(data, filepath)
        except Exception as e:
            print(f"    ERROR: {e}")
            continue

    print(f"\n{'=' * 70}")
    print("HERO REFS v3 COMPLETE")
    print("=" * 70)
