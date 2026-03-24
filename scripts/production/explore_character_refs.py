#!/usr/bin/env python3
"""
Stray Signal — Character & Location Reference Exploration

Creative divergence before convergence. Generate many variants across
different style interpretations to find the distinctive look for Neda
and Kai, plus key EP01 locations.

Pipeline: ComfyUI z-image-base-t2i (local, $0.00)
Output: projects/stray-signal/REFERENCES/exploration/

Usage:
  python3 scripts/production/explore_character_refs.py --target neda
  python3 scripts/production/explore_character_refs.py --target kai
  python3 scripts/production/explore_character_refs.py --target locations
  python3 scripts/production/explore_character_refs.py --target all
  python3 scripts/production/explore_character_refs.py --target all --dry-run
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
OUTPUT_BASE = PROJECT / "REFERENCES" / "exploration"

# ---------------------------------------------------------------------------
# Style DNA variants — the core creative divergence axis
# ---------------------------------------------------------------------------
# Each style is a distinct visual interpretation of "Concrete & Neon" DNA.
# We push AWAY from generic Western animation toward specific, graphic looks.

STYLES = {
    "graphic_flat": (
        "Stylized graphic illustration with bold flat color planes, hard cel-shaded edges, "
        "minimal gradients, geometric shapes defining form, limited color palette, "
        "strong silhouette readability, inspired by Into the Spider-Verse's graphic novel frames, "
        "halftone dot texture in shadows, Ben-Day dots, comic panel aesthetic, "
    ),
    "brutalist_render": (
        "Cinematic digital painting, brutalist architectural rendering style, "
        "monolithic concrete textures with visible form-marks, harsh directional lighting "
        "with deep shadows, volumetric atmosphere, muted desaturated palette with "
        "selective saturated accents, cinematic anamorphic lens distortion at edges, "
        "inspired by Blade Runner 2049 concept art, heavy atmosphere, "
    ),
    "woodblock_angular": (
        "Japanese woodblock print meets sci-fi, ukiyo-e inspired flat perspective, "
        "strong black outlines with angular geometric fills, limited ink-wash palette, "
        "paper texture visible through color, architectural precision in clothing folds, "
        "negative space as compositional element, bold graphic contrast, "
    ),
    "pixel_noir": (
        "High-contrast noir illustration with digital interference patterns, "
        "deep shadows with glitch-texture edges, scanline artifacts in light areas, "
        "CRT phosphor glow on highlights, brutalist geometry with pixel-grid overlay, "
        "monochromatic base with single color accent, surveillance-camera aesthetic, "
    ),
    "collage_cutout": (
        "Mixed-media collage illustration, cut-paper layered aesthetic with visible edges, "
        "textured paper backgrounds, screen-printed color overlays, risograph grain, "
        "geometric shapes built from overlapping cut forms, handmade quality with "
        "precise geometric structure, zine aesthetic meets architectural rendering, "
    ),
    "line_ink": (
        "Architectural ink illustration with precise technical linework, "
        "crosshatching for shadow, clean geometric construction lines visible, "
        "blueprint aesthetic with selective color washes, sharp angular perspective, "
        "pen-and-ink character rendering with geometric costume detail, "
        "isometric precision meets expressive character drawing, "
    ),
}

# ---------------------------------------------------------------------------
# Negative prompt (shared)
# ---------------------------------------------------------------------------
NEGATIVE = (
    "photorealistic, 3D render, smooth plastic skin, generic anime, "
    "chibi, cute cartoon, soft lighting, bloom, lens flare, "
    "multiple characters, crowd, blurry, low quality, deformed, "
    "extra limbs, bad anatomy, text, watermark, signature, "
    "cyberpunk neon excess, holographic UI, floating interfaces"
)

# ---------------------------------------------------------------------------
# Character prompt components
# ---------------------------------------------------------------------------

NEDA_BASE = (
    "17-year-old girl, compact athletic build, brown skin with warm undertone, "
    "black hair cropped short on sides with longer top pushed back, "
    "thin copper-wire braid behind left ear, sharp dark assessing eyes, "
    "scar across right knuckles of right hand, "
)

NEDA_GRID_OUTFIT = (
    "angular geometric jacket in steel blue with origami-folded collar and sharp "
    "shoulder panels, high-waisted fitted trousers in concrete grey, "
    "polymer-soled boots, posture upright and space-claiming, "
    "expression controlled and neutral, jaw tension visible, "
)

NEDA_SEAM_OUTFIT = (
    "fitted dark jacket with visible hand-stitching over rust-colored underlayer, "
    "cargo pockets with junction tools, worn boots with real scuffs, "
    "copper-wire braid catching amber light, posture sharp and direct, "
    "tool harness across chest, expression focused and operational, "
)

KAI_BASE = (
    "16-year-old boy, lean narrow-shouldered build, light brown skin, "
    "dark short hair slightly longer on top, watchful dark eyes that track "
    "movement before faces, hands always occupied with a small object, "
)

KAI_GRID_OUTFIT = (
    "angular geometric clothing in concrete grey and steel blue, "
    "structured origami-like jacket with sharp folded panels and high collar, "
    "fitted trousers in pale sage, polymer-soled boots, "
    "maintenance tool belt with small diagnostic instruments, "
    "posture slightly folded inward, unremarkable, designed to not be noticed, "
)

KAI_DEVICE = (
    "holding a brushed-aluminum tablet device slightly too large for his hands, "
    "scratched and dented, screen showing faint cyan wireframe cat form, "
    "cyan glow reflected on his face and fingers, "
)

# ---------------------------------------------------------------------------
# Neda exploration matrix
# ---------------------------------------------------------------------------

NEDA_VARIANTS = {
    # Shot type variations
    "portrait_grid": {
        "desc": "Close-up portrait, Grid appearance",
        "prompt": (
            "{style}"
            "Close-up portrait of " + NEDA_BASE + NEDA_GRID_OUTFIT +
            "Brutalist concrete wall background, 4500K flat fluorescent lighting, "
            "desaturated steel-blue palette. The face is specific, memorable, angular — "
            "not conventionally pretty, not generic. A face you'd recognize in a crowd."
        ),
        "w": 720, "h": 1024,
    },
    "portrait_seam": {
        "desc": "Close-up portrait, Seam appearance",
        "prompt": (
            "{style}"
            "Close-up portrait of " + NEDA_BASE + NEDA_SEAM_OUTFIT +
            "Rough stone wall background with amber LED string lights, "
            "warm amber lighting casting deep bronze on brown skin. "
            "The same angular memorable face, now in warm underground light. "
            "Copper braid catching golden light."
        ),
        "w": 720, "h": 1024,
    },
    "full_grid": {
        "desc": "Full body, Grid street",
        "prompt": (
            "{style}"
            "Full body shot of " + NEDA_BASE + NEDA_GRID_OUTFIT +
            "Standing in a wide brutalist concrete plaza with geometric architecture "
            "stretching behind her. Massive monolithic buildings with no ornament. "
            "Cold steel-blue overcast sky. She is moving through the space with purpose — "
            "not hurrying, not lingering. Full figure visible head to toe, centered in frame. "
            "The architecture dwarfs her but she takes up space through posture."
        ),
        "w": 1024, "h": 1024,
    },
    "full_seam": {
        "desc": "Full body, Seam corridor",
        "prompt": (
            "{style}"
            "Full body shot of " + NEDA_BASE + NEDA_SEAM_OUTFIT +
            "Standing in an underground stone corridor with amber string lights overhead. "
            "Rough-hewn walls, salvaged electronics mounted on surfaces, warm amber glow "
            "on everything. She's in her element — sharp, direct, operational. "
            "Full figure visible head to toe, centered. The warm environment contrasts "
            "with her controlled intensity."
        ),
        "w": 1024, "h": 1024,
    },
    "detail_hands": {
        "desc": "Detail — hands with knuckle scar",
        "prompt": (
            "{style}"
            "Extreme close-up of a brown-skinned hand, feminine but strong, "
            "white scar tissue across the knuckles against warm brown skin. "
            "The hand is gripping the edge of a rough stone table. Amber light "
            "from the left, cool fluorescent from the right. The knuckle scar "
            "is prominent. Angular geometric sleeve cuff visible at wrist. "
            "The hand tells a story of corridors and junction panels."
        ),
        "w": 1024, "h": 720,
    },
    "jaw_tell": {
        "desc": "The jaw tighten — signature tell",
        "prompt": (
            "{style}"
            "Extreme close-up of a girl's lower face and jaw. Brown skin, "
            "angular jaw, tension visible in the masseter muscle — the jaw is "
            "clenched a fraction before speaking. Lips pressed. Cold fluorescent "
            "light from above, faint cyan reflection from the right side. "
            "The geometry of the face is precise and specific. This is the moment "
            "before a lie. Steel-blue geometric collar visible at bottom of frame."
        ),
        "w": 1024, "h": 720,
    },
}

# ---------------------------------------------------------------------------
# Kai exploration matrix
# ---------------------------------------------------------------------------

KAI_VARIANTS = {
    "portrait_grid": {
        "desc": "Close-up portrait, Grid appearance",
        "prompt": (
            "{style}"
            "Close-up portrait of " + KAI_BASE + KAI_GRID_OUTFIT +
            "Brutalist concrete wall background, 4500K flat fluorescent lighting. "
            "The face is unremarkable at first glance — the kind LEDGER flags as nominal. "
            "But the eyes are tracking, calculating, alive with pattern-hunger. "
            "A face that disappears in a crowd but becomes specific the moment you look closely."
        ),
        "w": 720, "h": 1024,
    },
    "portrait_device": {
        "desc": "Close-up with device glow on face",
        "prompt": (
            "{style}"
            "Close-up portrait of " + KAI_BASE +
            "Dark maintenance corridor background. His face lit from below by "
            "a cyan wireframe glow from a device screen he's holding. "
            "The cyan light picks out his cheekbones and the longer hair on top. "
            "His eyes are wide with the first real curiosity he's ever felt. "
            "Dark around him, cyan on his face. The device light is the first "
            "color that belongs to him."
        ),
        "w": 720, "h": 1024,
    },
    "full_grid": {
        "desc": "Full body, Grid corridor",
        "prompt": (
            "{style}"
            "Full body shot of " + KAI_BASE + KAI_GRID_OUTFIT +
            "Standing in a brutalist maintenance corridor — concrete walls, "
            "exposed polymer conduits, fluorescent strip lighting overhead. "
            "He is folded inward, shoulders slightly hunched, not making eye contact. "
            "The corridor is monotone grey. He blends in perfectly. "
            "Full figure visible head to toe. The maintenance tool belt is his "
            "one visual distinction."
        ),
        "w": 1024, "h": 1024,
    },
    "full_device": {
        "desc": "Full body with device, corridor",
        "prompt": (
            "{style}"
            "Full body shot of " + KAI_BASE + KAI_GRID_OUTFIT + KAI_DEVICE +
            "Standing in a dim maintenance corridor. The device screen casts "
            "cyan wireframe light upward onto his face and the ceiling above him. "
            "A small cyan wireframe cat form is visible on the screen. "
            "He holds the device carefully — the way you hold something alive. "
            "Dark corridor, cold fluorescent strips, one point of cyan warmth. "
            "Full figure visible head to toe."
        ),
        "w": 1024, "h": 1024,
    },
    "detail_hands_device": {
        "desc": "Detail — hands holding device",
        "prompt": (
            "{style}"
            "Extreme close-up of a boy's hands holding a brushed-aluminum tablet device. "
            "Light brown skin, lean fingers, always active — one thumb testing the edge "
            "of the device frame. The screen shows a small cyan wireframe cat sitting, "
            "blinking. The glow casts cyan light on his fingertips. The device is "
            "scratched, dented, warm from use. The hands are a maintenance worker's "
            "hands — precise, quick, comfortable with objects. Background dark."
        ),
        "w": 1024, "h": 720,
    },
    "watching": {
        "desc": "Kai observed from distance — Neda's POV",
        "prompt": (
            "{style}"
            "Medium shot of " + KAI_BASE +
            "seen from behind a corridor junction. He doesn't know he's being watched. "
            "He's crouched at a wall panel, device in one hand, the screen casting "
            "cyan glow on the polymer floor. A maintenance corridor at shift-end — "
            "empty, fluorescent, cold. He's the only warm thing in the frame. "
            "The cyan glow is the only color. Shot from distance, voyeuristic, "
            "the composition of surveillance."
        ),
        "w": 1280, "h": 720,
    },
}

# ---------------------------------------------------------------------------
# Location exploration matrix (EP01 key environments)
# ---------------------------------------------------------------------------

LOCATION_VARIANTS = {
    "grid_plaza_dawn": {
        "desc": "Grid plaza establishing — dawn, no people",
        "prompt": (
            "{style}"
            "Wide establishing shot of a brutalist dystopian cityscape at dawn. "
            "Massive monolithic concrete blocks rising without ornament against a cold "
            "steel-blue sky. No curves, no decoration, no warmth. Geometric angular "
            "architecture stretching to vanishing point. A single small surveillance drone "
            "traces a circuit in the upper frame. No people visible anywhere. "
            "Concrete grey (#8C8C8C) and steel blue (#4A5568) palette. "
            "Overcast diffused light, no shadows. The scale is monumental and oppressive. "
            "NO people, NO characters, NO animals."
        ),
        "w": 1280, "h": 720,
    },
    "grid_street": {
        "desc": "Grid street level — pedestrian view",
        "prompt": (
            "{style}"
            "Street-level view of a brutalist dystopian city. Massive concrete walls "
            "on both sides creating a canyon. Smooth polished polymer floor. People-shaped "
            "gaps in the architecture — walkways sized for single-file. Overhead: a thin "
            "strip of cold grey sky between buildings. Fluorescent strip lights along "
            "the lower walls. Clinical, uniform, no signage, no decoration. "
            "The architecture is designed to move people, not welcome them. "
            "Steel blue and concrete grey palette. NO people, NO characters."
        ),
        "w": 1280, "h": 720,
    },
    "descent_cold": {
        "desc": "Descent — cold upper section, polymer steps",
        "prompt": (
            "{style}"
            "A narrow vertical passage leading downward. Polymer steps descending into "
            "dimness. Cold fluorescent strip lights on the walls, steel blue tone. "
            "The walls are smooth processed concrete transitioning to rougher texture "
            "as you look deeper down. The passage is tight — one person wide. "
            "Clinical and sterile. The same cold Grid palette but going underground. "
            "No warmth yet. The light gets dimmer with depth. "
            "NO people, NO characters."
        ),
        "w": 720, "h": 1280,
    },
    "descent_warm": {
        "desc": "Descent — warm lower section, stone steps",
        "prompt": (
            "{style}"
            "Underground stone steps leading down into warm amber light. "
            "Rough-hewn stone walls with hand-chipped texture. Amber LED string lights "
            "strung along the walls, casting golden pools. The steps are worn from use. "
            "At the bottom: a hint of warm amber space — The Seam opening up. "
            "The transition from cold concrete above to warm stone below is complete. "
            "Warm amber (#F59E0B) palette, intimate lighting, underground sanctuary feel. "
            "NO people, NO characters."
        ),
        "w": 720, "h": 1280,
    },
    "seam_corridor": {
        "desc": "Seam main corridor — branching warm underground",
        "prompt": (
            "{style}"
            "Wide shot of an underground corridor carved from rough stone. "
            "Amber LED string lights overhead casting warm golden light on every surface. "
            "Branching passages leading in multiple directions. Salvaged electronics "
            "mounted on walls — old circuit boards, repurposed screens showing data. "
            "Growing plants in wall-mounted containers. Worn floor from generations of use. "
            "The architecture is organic, adapted, human — the opposite of the Grid. "
            "Warm amber palette with moss green (#065F46) accents from plants. "
            "NO people, NO characters."
        ),
        "w": 1280, "h": 720,
    },
    "fen_room": {
        "desc": "Fen's room — grow-lamps, clinical within warm",
        "prompt": (
            "{style}"
            "View through a doorway into a small underground room. The room is lit by "
            "overhead grow-lamps casting harsh green-white light downward. A single chair "
            "in the center. The walls are rough stone but the light makes them clinical. "
            "Small plants growing under the lamps — the room's purpose was agricultural "
            "before it became a care room. The doorway frame is in warm amber light from "
            "the corridor behind us. Two distinct lighting zones: warm amber doorway, "
            "green-white clinical room. NO people, NO characters."
        ),
        "w": 1280, "h": 720,
    },
    "briefing_alcove": {
        "desc": "Briefing alcove — small, amber, intimate",
        "prompt": (
            "{style}"
            "A small underground room carved from rough stone. Close stone walls creating "
            "an intimate confined space. Warm amber LED lights casting deep golden light. "
            "A simple rough-hewn stone table in the center. Low ceiling pressing down. "
            "The amber light sits heavy on every surface. Storyboards and maps pinned "
            "to the stone wall behind the table. Salvaged electronics and a dim screen. "
            "A briefing room for two — private, hidden, warm. "
            "NO people, NO characters."
        ),
        "w": 1280, "h": 720,
    },
    "maintenance_corridor": {
        "desc": "Maintenance corridor — where Kai finds device",
        "prompt": (
            "{style}"
            "A long straight maintenance corridor in a brutalist underground facility. "
            "Cold fluorescent strip lights overhead casting flat shadowless light. "
            "Polymer conduits running along the walls. Access panels at regular intervals. "
            "The corridor stretches to a vanishing point — geometric, repetitive, empty. "
            "This is infrastructure, not living space. Cold fluorescent palette with "
            "no warmth. The kind of space only maintenance workers see. "
            "NO people, NO characters."
        ),
        "w": 1280, "h": 720,
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


def z_image_t2i(prompt, negative, seed, width, height, steps=25, cfg=4.0):
    params = {
        "prompt": prompt,
        "negative_prompt": negative,
        "seed": str(seed),
        "steps": str(steps),
        "cfg": str(cfg),
        "width": str(width),
        "height": str(height),
    }
    return submit_and_wait("z-image-base-t2i", params)


def save(data, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as f:
        f.write(data)
    size = Image.open(io.BytesIO(data)).size
    print(f"    Saved: {path} ({size[0]}x{size[1]})")
    return path


# ---------------------------------------------------------------------------
# Generation logic
# ---------------------------------------------------------------------------

def generate_character_exploration(name, variants, base_seed=5000):
    """Generate all style x variant combinations for a character."""
    out_dir = OUTPUT_BASE / name
    out_dir.mkdir(parents=True, exist_ok=True)

    total = len(STYLES) * len(variants)
    count = 0

    for style_name, style_prefix in STYLES.items():
        for var_name, var in variants.items():
            count += 1
            filename = f"{name}_{style_name}_{var_name}.png"
            filepath = out_dir / filename

            # Skip if already generated
            if filepath.exists():
                print(f"[{count}/{total}] SKIP (exists): {filename}")
                continue

            prompt = var["prompt"].format(style=style_prefix)
            seed = base_seed + hash(f"{style_name}_{var_name}") % 10000

            print(f"\n[{count}/{total}] {filename}")
            print(f"  Style: {style_name} | Variant: {var_name} ({var['desc']})")

            try:
                data = z_image_t2i(
                    prompt=prompt,
                    negative=NEGATIVE,
                    seed=seed,
                    width=var["w"],
                    height=var["h"],
                )
                save(data, filepath)
            except Exception as e:
                print(f"    ERROR: {e}")
                continue


def generate_location_exploration(base_seed=7000):
    """Generate all style x location combinations."""
    out_dir = OUTPUT_BASE / "locations"
    out_dir.mkdir(parents=True, exist_ok=True)

    total = len(STYLES) * len(LOCATION_VARIANTS)
    count = 0

    for style_name, style_prefix in STYLES.items():
        for loc_name, loc in LOCATION_VARIANTS.items():
            count += 1
            filename = f"loc_{style_name}_{loc_name}.png"
            filepath = out_dir / filename

            if filepath.exists():
                print(f"[{count}/{total}] SKIP (exists): {filename}")
                continue

            prompt = loc["prompt"].format(style=style_prefix)
            seed = base_seed + hash(f"{style_name}_{loc_name}") % 10000

            print(f"\n[{count}/{total}] {filename}")
            print(f"  Style: {style_name} | Location: {loc_name} ({loc['desc']})")

            try:
                data = z_image_t2i(
                    prompt=prompt,
                    negative=NEGATIVE,
                    seed=seed,
                    width=loc["w"],
                    height=loc["h"],
                )
                save(data, filepath)
            except Exception as e:
                print(f"    ERROR: {e}")
                continue


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Character & location reference exploration")
    parser.add_argument("--target", choices=["neda", "kai", "locations", "all"],
                        default="all", help="What to explore (default: all)")
    parser.add_argument("--style", choices=list(STYLES.keys()) + ["all"],
                        default="all", help="Limit to one style (default: all)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print what would be generated without generating")
    args = parser.parse_args()

    # Filter styles if requested
    if args.style != "all":
        active_styles = {args.style: STYLES[args.style]}
        original_styles = dict(STYLES)
        STYLES.clear()
        STYLES.update(active_styles)

    if args.dry_run:
        print("=" * 70)
        print("DRY RUN — Exploration Matrix")
        print("=" * 70)

        if args.target in ("neda", "all"):
            n = len(STYLES) * len(NEDA_VARIANTS)
            print(f"\nNEDA: {len(STYLES)} styles x {len(NEDA_VARIANTS)} variants = {n} images")
            for s in STYLES:
                for v, d in NEDA_VARIANTS.items():
                    print(f"  neda_{s}_{v}.png — {d['desc']} ({d['w']}x{d['h']})")

        if args.target in ("kai", "all"):
            n = len(STYLES) * len(KAI_VARIANTS)
            print(f"\nKAI: {len(STYLES)} styles x {len(KAI_VARIANTS)} variants = {n} images")
            for s in STYLES:
                for v, d in KAI_VARIANTS.items():
                    print(f"  kai_{s}_{v}.png — {d['desc']} ({d['w']}x{d['h']})")

        if args.target in ("locations", "all"):
            n = len(STYLES) * len(LOCATION_VARIANTS)
            print(f"\nLOCATIONS: {len(STYLES)} styles x {len(LOCATION_VARIANTS)} variants = {n} images")
            for s in STYLES:
                for v, d in LOCATION_VARIANTS.items():
                    print(f"  loc_{s}_{v}.png — {d['desc']} ({d['w']}x{d['h']})")

        total = 0
        if args.target in ("neda", "all"):
            total += len(STYLES) * len(NEDA_VARIANTS)
        if args.target in ("kai", "all"):
            total += len(STYLES) * len(KAI_VARIANTS)
        if args.target in ("locations", "all"):
            total += len(STYLES) * len(LOCATION_VARIANTS)

        print(f"\nTOTAL: {total} images")
        est_time = total * 20  # ~20s per z-image generation
        print(f"Estimated time: ~{est_time // 60}m {est_time % 60}s")
        sys.exit(0)

    # Generate
    print("=" * 70)
    print("Stray Signal — Character & Location Exploration")
    print(f"Output: {OUTPUT_BASE}")
    print("=" * 70)

    if args.target in ("neda", "all"):
        print("\n" + "=" * 70)
        print("NEDA THELL — Exploration")
        print("=" * 70)
        generate_character_exploration("neda", NEDA_VARIANTS, base_seed=5000)

    if args.target in ("kai", "all"):
        print("\n" + "=" * 70)
        print("KAI — Exploration")
        print("=" * 70)
        generate_character_exploration("kai", KAI_VARIANTS, base_seed=6000)

    if args.target in ("locations", "all"):
        print("\n" + "=" * 70)
        print("LOCATIONS — Exploration")
        print("=" * 70)
        generate_location_exploration(base_seed=7000)

    print("\n" + "=" * 70)
    print("EXPLORATION COMPLETE")
    print(f"Review results in: {OUTPUT_BASE}")
    print("=" * 70)
