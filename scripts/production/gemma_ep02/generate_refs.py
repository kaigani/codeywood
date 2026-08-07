#!/usr/bin/env python3
"""
Generate character + location refs for Gemma EP02 via z-image-base-t2i.

Realistic cyber-noir style (NOT animation).

Usage:
    python generate_refs.py --all
    python generate_refs.py --characters
    python generate_refs.py --locations
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
        "id": "kane",
        "seed": 80301,
        "size": (1024, 1536),
        "prompt": (
            "Hero shot of Kane Ballum, lean ascetic male, late 30s, weathered "
            "pale skin with practical lighting catching pore detail, dark "
            "deep-set eyes, shaved head. Wearing white ritual linens stained "
            "with old dried blood at the cuffs and hem, and a polished "
            "obsidian half-mask covering the lower face from below the nose "
            "to the chin. Realistic textile texture on the linens, real "
            "obsidian surface with reflective highlight. Three-quarter "
            "portrait, full upper body in frame. Standing against neutral "
            "charcoal studio backdrop. Cinematic key light from upper left, "
            "cold teal fill on the right side, single burning-orange rim "
            "light on the obsidian mask. " + STYLE_TAG
        ),
    },
    {
        "id": "ishelle",
        "seed": 80302,
        "size": (1024, 1536),
        "prompt": (
            "Hero shot of Ishelle Zune, regal female, mid 30s, porcelain "
            "pale skin with realistic skin texture and faint freckles, "
            "sharp aristocratic features, dark hair pulled back tight. "
            "Wearing a high-collar sculptural gown of iridescent synthetic "
            "silk that catches magenta and teal light along its folds. "
            "Real fabric drape, real specular highlights on the silk. "
            "Direct cold gaze into camera. Standing against neutral "
            "charcoal studio backdrop. Three-quarter portrait, full upper "
            "body in frame. Sodium-vapor yellow key light from above, cold "
            "teal fill from below-left. " + STYLE_TAG
        ),
    },
    {
        "id": "alvin",
        "seed": 80303,
        "size": (1024, 1536),
        "prompt": (
            "Hero shot of Alvin Salim, gaunt male, late 30s, hollow "
            "cheekbones, sweat beading on forehead, dark circles under "
            "desperate eyes, scruffy stubble. Wearing a grime-streaked "
            "leather duster over a fraying grey undershirt. Real worn "
            "leather texture with scratches and wear, real stained fabric. "
            "Shaking hands held at chest level. Three-quarter portrait, "
            "full upper body in frame. Standing against neutral charcoal "
            "studio backdrop. Cinematic key light from upper left, deep "
            "blue shadow on right side of face. " + STYLE_TAG
        ),
    },
]


LOCATIONS = [
    {
        "id": "balcony",
        "seed": 80401,
        "size": (1536, 1024),
        "prompt": (
            "Wide environment plate. A rain-slicked open-air balcony "
            "overlooking a vast cyberpunk neon slum at night. Wet stone "
            "balustrade in the foreground catches sodium-vapor yellow "
            "light. Beyond the balcony, a forest of magenta and acid-green "
            "neon signs stretches into atmospheric haze. Towering brutalist "
            "buildings shrouded in greasy mist. Steam vents rising from the "
            "streets below. Real puddle reflections on wet stone. No people "
            "in frame. High contrast cinematography with cold teal shadows "
            "and burning orange highlights. " + STYLE_TAG
        ),
    },
    {
        "id": "market",
        "seed": 80402,
        "size": (1536, 1024),
        "prompt": (
            "Wide environment plate. A narrow crowded wet market alleyway "
            "in a cyberpunk slum at night. Damp concrete underfoot reflects "
            "the magenta and acid-green neon signs hung in unknown script "
            "overhead. Sodium-vapor yellow lanterns flicker. Rusted metal "
            "stall railings line both sides, draped in greasy plastic "
            "sheeting. Steam rises from food vendors. Greasy rain falls. "
            "Real wet surfaces, real fabric textures, real metal corrosion. "
            "No people in frame. Cyber-noir color grade, cold teal shadows "
            "and burning orange highlights. " + STYLE_TAG
        ),
    },
    {
        "id": "warehouse",
        "seed": 80403,
        "size": (1536, 1024),
        "prompt": (
            "Wide environment plate. The interior of a derelict abandoned "
            "industrial warehouse at night. Massive rusting machinery — "
            "old pipework, conveyor remnants, cracked steel beams — "
            "dominates the space. A single shaft of harsh white light cuts "
            "diagonally through dust from a broken skylight above. Damp "
            "concrete floor. Faint magenta neon spill leaks through a "
            "broken window on the far wall. Real rust textures, real "
            "concrete, real dust motes in the light shaft. No people in "
            "frame. Cyber-noir color grade. " + STYLE_TAG
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
        print(f"    -> {out.name} ({len(content)/1024:.0f} KB, {time.time()-t0:.0f}s)")
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
    print(f"EP02 REFS — {WORKFLOW} — realistic cyber-noir")
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
