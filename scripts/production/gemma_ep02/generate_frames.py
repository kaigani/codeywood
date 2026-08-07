#!/usr/bin/env python3
"""
Composite first frames for 12 EP02 shots via qwen-image-edit.

Each shot uses:
  - Location ref (image slot — drives aspect ratio)
  - Character ref(s) (image2/image3 slots)
  - Realistic style prompt (cyber-noir, not animation)

Usage:
    python generate_frames.py --all
    python generate_frames.py --shot 3
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import (
    CHAR_REFS, CLIP_DEFS, FRAMES_DIR, LOC_REFS, STYLE_TAG,
    health_check, run_workflow, save,
)

WORKFLOW = "qwen-image-edit"


def build_composite_prompt(shot: dict) -> str:
    chars = [c for c in shot["characters"] if c != "informant"]
    has_informant = "informant" in shot["characters"]

    char_parts = []
    for c in chars:
        char_parts.append(c.title().replace("_", " "))
    if has_informant:
        char_parts.append("a terrified informant (gaunt male in dark grimy clothes, sweat on his brow)")
    char_phrase = ", ".join(char_parts) if char_parts else ""

    if char_parts:
        char_line = f"Place {char_phrase} into the scene as described."
    else:
        char_line = "Render the scene with no people on screen."

    parts = [
        f"{shot['shot_type']} — {shot['framing']}.",
        char_line,
        shot["action"].strip(),
        f"Style: {STYLE_TAG}",
    ]
    return " ".join(parts)


def load_shots() -> list[dict]:
    with open(CLIP_DEFS) as f:
        return yaml.safe_load(f)["shots"]


def gen_frame(shot: dict, force: bool, dry_run: bool) -> bool:
    sid = shot["id"]
    name = f"shot_{sid:02d}_c{shot['clip_number']}s{shot['shot_number']}"
    out = FRAMES_DIR / f"{name}.png"
    if out.exists() and not force:
        print(f"  Shot {sid:2d}: SKIP (exists)")
        return True

    loc_id = shot["location"]
    loc_ref = LOC_REFS / f"{loc_id}_ref.png"
    if not loc_ref.exists():
        print(f"  Shot {sid:2d}: NO LOCATION REF {loc_ref}")
        return False

    # Up to 2 named-character refs (excluding informant — no ref image)
    char_refs = []
    for cid in shot["characters"]:
        if cid == "informant":
            continue
        cref = CHAR_REFS / f"{cid}_ref.png"
        if cref.exists():
            char_refs.append(cref)
        if len(char_refs) >= 2:
            break

    prompt = build_composite_prompt(shot)
    print(f"  Shot {sid:2d}: {name}")
    print(f"    Location: {loc_ref.name}")
    if char_refs:
        print(f"    Chars: {[r.name for r in char_refs]}")
    print(f"    Prompt[120]: {prompt[:120]}...")

    if dry_run:
        return True

    data = {
        "prompt": prompt,
        "seed": str(80500 + sid),
        "steps": "4",
    }

    files = [("image", (loc_ref.name, open(loc_ref, "rb"), "image/png"))]
    if len(char_refs) >= 1:
        files.append(("image2", (char_refs[0].name, open(char_refs[0], "rb"), "image/png")))
    if len(char_refs) >= 2:
        files.append(("image3", (char_refs[1].name, open(char_refs[1], "rb"), "image/png")))

    t0 = time.time()
    try:
        content = run_workflow(WORKFLOW, data, files=files, timeout=300)
        save(content, out)
        print(f"    -> {out.name} ({len(content)/1024:.0f} KB, {time.time()-t0:.0f}s)")
        return True
    except Exception as e:
        print(f"    FAILED: {e}")
        return False
    finally:
        for _, (_, fh, _) in files:
            try:
                fh.close()
            except Exception:
                pass


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--shot", type=int, default=0)
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if not (args.all or args.shot):
        ap.print_help()
        sys.exit(1)

    if not args.dry_run and not health_check():
        print("ERROR: ComfyUI not reachable")
        sys.exit(1)

    FRAMES_DIR.mkdir(parents=True, exist_ok=True)

    shots = load_shots()
    if args.shot:
        shots = [s for s in shots if s["id"] == args.shot]
        if not shots:
            print(f"No shot {args.shot}")
            sys.exit(1)

    print("=" * 70)
    print(f"EP02 FRAMES — {WORKFLOW} — {len(shots)} shots — realistic")
    print("=" * 70)

    failed = []
    for shot in shots:
        if not gen_frame(shot, args.force, args.dry_run):
            failed.append(shot["id"])

    print("\n" + "=" * 70)
    if failed:
        print(f"FAILED: {failed}")
        sys.exit(1)
    print("DONE")


if __name__ == "__main__":
    main()
