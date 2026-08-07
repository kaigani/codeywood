#!/usr/bin/env python3
"""
Composite first frames for each of 12 EP01 shots via qwen-image-edit.

Each shot uses:
  - Location ref (image slot — drives aspect ratio)
  - Character ref(s) (image2/image3 slots)
  - Compositing prompt derived from clip_definitions.yaml

Usage:
    python generate_frames.py --dry-run
    python generate_frames.py --shot 3
    python generate_frames.py --all
    python generate_frames.py --force
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
    """Compose a qwen-image-edit instruction prompt for one shot."""
    chars = shot["characters"]
    char_phrase = ", ".join(c.title() for c in chars) if chars else ""

    if chars:
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
        data = yaml.safe_load(f)
    return data["shots"]


def gen_frame(shot: dict, force: bool, dry_run: bool) -> bool:
    sid = shot["id"]
    name = f"shot_{sid:02d}_c{shot['clip_number']}s{shot['shot_number']}"
    out = FRAMES_DIR / f"{name}.png"
    if out.exists() and not force:
        print(f"  Shot {sid:2d}: SKIP (exists)")
        return True

    # Location ref drives aspect ratio
    loc_id = shot["location"]
    if loc_id == "transition":
        loc_id = "slums"  # threshold scene tips into slum entrance
    loc_ref = LOC_REFS / f"{loc_id}_ref.png"
    if not loc_ref.exists():
        print(f"  Shot {sid:2d}: NO LOCATION REF {loc_ref}")
        return False

    # Character refs (up to 2; image2 and image3)
    char_refs = []
    for cid in shot["characters"][:2]:
        cref = CHAR_REFS / f"{cid}_ref.png"
        if cref.exists():
            char_refs.append(cref)
        else:
            print(f"  Shot {sid:2d}: missing char ref {cref}")

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
        "seed": str(60000 + sid),
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
        print(f"    -> Saved {out.name} ({len(content)/1024:.0f} KB, {time.time()-t0:.0f}s)")
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
    ap.add_argument("--shot", type=int, default=0, help="single shot id (0 = all)")
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
    print(f"COMPOSITE FRAMES — {WORKFLOW} — {len(shots)} shots")
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
