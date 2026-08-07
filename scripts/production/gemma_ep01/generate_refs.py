#!/usr/bin/env python3
"""
Generate character + location refs for Gemma Anthology EP01 via z-image-base-t2i.

Usage:
    python generate_refs.py --dry-run
    python generate_refs.py --characters
    python generate_refs.py --locations
    python generate_refs.py --all
    python generate_refs.py --force
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import (
    CHAR_REFS, LOC_REFS, NEGATIVE, STYLE_TAG,
    health_check, run_workflow, save,
)


WORKFLOW = "z-image-base-t2i"


CHARACTERS = [
    {
        "id": "alvin",
        "seed": 70101,
        "size": (1024, 1536),
        "prompt": (
            "Hero shot of Alvin Salim, late 30s gaunt man with hollow cheekbones, "
            "pale grey skin peeling in thin strips along forearms and shoulder, "
            "raw pink dermis showing beneath. Wearing a stained synthetic linen "
            "tunic, off-white with rust-colored stains. Dark sunken eyes, sweat "
            "on the brow, mouth set in determined desperation. Standing against "
            "neutral charcoal background. Three-quarter portrait, full upper "
            "body in frame. Cinematic key light from upper left, deep shadow on "
            "right side of face. " + STYLE_TAG
        ),
    },
    {
        "id": "omar",
        "seed": 70102,
        "size": (1024, 1536),
        "prompt": (
            "Hero shot of Omar Gaul, mid 40s massive-framed man, broad shoulders, "
            "thick neck. Heavy leather plating armor on torso, oxidized brass "
            "buckles. Visible cybernetic hip-grafts where leather meets pants, "
            "metal plates inset into flesh, viscous yellow fluid welling at the "
            "seams. Stubbled jaw, eyes hooded from pain, dark hair shaved short. "
            "Standing against neutral charcoal background. Three-quarter portrait, "
            "full upper body in frame. Cinematic key light from upper left, deep "
            "shadow on right side of face. " + STYLE_TAG
        ),
    },
    {
        "id": "baze",
        "seed": 70103,
        "size": (1024, 1536),
        "prompt": (
            "Hero shot of Baze Bey, early 30s lean figure with symmetrical "
            "features, polished obsidian optical implants where eyes should be — "
            "two black spheres that reflect ambient light. Sleek matte-black "
            "bodysuit, high-collar, no visible seams. Skin clean, almost too "
            "smooth. Expression neutral, clinical. Standing against neutral "
            "charcoal background. Three-quarter portrait, full upper body in "
            "frame. Cinematic key light from upper left catches the obsidian "
            "optics with a sharp specular highlight. " + STYLE_TAG
        ),
    },
]


LOCATIONS = [
    {
        "id": "temple",
        "seed": 70201,
        "size": (1536, 1024),
        "prompt": (
            "Wide environment plate. Interior of a vast pleasure cult temple — "
            "cavernous chamber with polished white marble floors and walls, "
            "tall fluted columns, gold filament threads strung between vaulted "
            "arches like an enormous suspended net. Humid incense smoke drifts "
            "at floor level. A central altar in the distance glows faintly "
            "gold. High-key pearlescent lighting from concealed sources. The "
            "atmosphere is sterile reverence, beautiful and oppressive. "
            "Symmetrical composition. No people in frame. " + STYLE_TAG
        ),
    },
    {
        "id": "slums",
        "seed": 70202,
        "size": (1536, 1024),
        "prompt": (
            "Wide environment plate. Narrow alleyway in neon-slick cyberpunk "
            "slums at night. Damp concrete walls hem in the lane. Flickering "
            "magenta and acid green neon signs in unknown script overhead. "
            "Puddles of iridescent oil on the wet pavement reflect the neon as "
            "fragmented color. Tangled cables drape between buildings. Steam "
            "vents in the middle distance. Towering decaying skyscrapers loom "
            "above the alley mouth. No people in frame. Low-key high-contrast "
            "lighting, deep shadows, saturated neon highlights. " + STYLE_TAG
        ),
    },
]


def gen(item: dict, output_dir: Path, force: bool, dry_run: bool) -> bool:
    out = output_dir / f"{item['id']}_ref.png"
    if out.exists() and not force:
        print(f"  {item['id']}: SKIP (exists)")
        return True
    w, h = item["size"]
    print(f"  {item['id']}: {w}x{h} seed={item['seed']}")
    print(f"    \"{item['prompt'][:90]}...\"")
    if dry_run:
        return True
    data = {
        "prompt": item["prompt"],
        "negative_prompt": NEGATIVE,
        "seed": str(item["seed"]),
        "width": str(w),
        "height": str(h),
        "steps": "25",
        "cfg": "4",
    }
    t0 = time.time()
    try:
        content = run_workflow(WORKFLOW, data, timeout=300)
        save(content, out)
        print(f"    -> Saved {out.name} ({len(content)/1024:.0f} KB, {time.time()-t0:.0f}s)")
        return True
    except Exception as e:
        print(f"    FAILED: {e}")
        return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--characters", action="store_true")
    ap.add_argument("--locations", action="store_true")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    do_chars = args.characters or args.all
    do_locs = args.locations or args.all
    if not (do_chars or do_locs):
        ap.print_help()
        sys.exit(1)

    if not args.dry_run and not health_check():
        print("ERROR: ComfyUI not reachable")
        sys.exit(1)

    CHAR_REFS.mkdir(parents=True, exist_ok=True)
    LOC_REFS.mkdir(parents=True, exist_ok=True)

    print("=" * 70)
    print(f"GENERATE REFS — {WORKFLOW}")
    print("=" * 70)

    failed = []
    if do_chars:
        print("\nCHARACTERS:")
        for c in CHARACTERS:
            if not gen(c, CHAR_REFS, args.force, args.dry_run):
                failed.append(c["id"])

    if do_locs:
        print("\nLOCATIONS:")
        for loc in LOCATIONS:
            if not gen(loc, LOC_REFS, args.force, args.dry_run):
                failed.append(loc["id"])

    print("\n" + "=" * 70)
    if failed:
        print(f"FAILED: {failed}")
        sys.exit(1)
    print("DONE")


if __name__ == "__main__":
    main()
