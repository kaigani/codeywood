#!/usr/bin/env python3
"""
Concept-art workflow runner.

Reads a subjects.yaml from a project's CONCEPT_ART/ directory, generates
pencil + watercolor concept sketches via z-image-base-t2i.

Usage:
    python3 generate.py --project projects/260513-gemma-anthology
    python3 generate.py --project ... --kind locations
    python3 generate.py --project ... --kind characters
    python3 generate.py --project ... --kind scenes
    python3 generate.py --project ... --dry-run
    python3 generate.py --project ... --force
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import (
    NEGATIVE, REPO_ROOT, build_prompt, health_check, run, save,
)


SIZE_BY_KIND = {
    "locations": (1536, 1024),  # wide environment plates
    "characters": (1024, 1536),  # full-body / portrait
    "scenes":    (1536, 1024),  # widescreen scene sketches
}


def render_subject(s: dict, kind: str) -> str:
    """Compose the 4-layer prompt for a subject defined in subjects.yaml.

    Each subject entry has:
      - subject_action: required
      - composition:    required
      - lighting:       required
      - text_factor:    optional (Z-Image renders verbatim quoted text)
    """
    return build_prompt(
        subject_action=s["subject_action"].strip(),
        composition=s["composition"].strip(),
        lighting=s["lighting"].strip(),
        text_factor=s.get("text_factor", "").strip(),
    )


def gen_one(s: dict, kind: str, out_dir: Path, force: bool, dry_run: bool) -> bool:
    out = out_dir / f"{s['id']}.png"
    if out.exists() and not force:
        print(f"  {s['id']}: SKIP (exists)")
        return True

    w, h = SIZE_BY_KIND[kind]
    prompt = render_subject(s, kind)

    print(f"  {s['id']}: {w}x{h} seed={s['seed']}")
    print(f"    prompt[180]: {prompt[:180]}...")

    if dry_run:
        return True

    data = {
        "prompt": prompt,
        "negative_prompt": NEGATIVE,
        "seed": str(s["seed"]),
        "width": str(w),
        "height": str(h),
        "steps": "25",
        "cfg": "4",
    }

    t0 = time.time()
    try:
        content = run(data, timeout=300)
        save(content, out)
        print(f"    -> {out.name}  ({len(content)/1024:.0f} KB, {time.time()-t0:.0f}s)")
        return True
    except Exception as e:
        print(f"    FAILED: {e}")
        return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", required=True, help="path to project root")
    ap.add_argument("--kind", choices=["all", "locations", "characters", "scenes"], default="all")
    ap.add_argument("--only", help="single subject id (across all kinds)")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    proj = (REPO_ROOT / args.project).resolve()
    concept_dir = proj / "CONCEPT_ART"
    subjects_file = concept_dir / "subjects.yaml"
    if not subjects_file.exists():
        print(f"ERROR: missing {subjects_file}")
        sys.exit(1)

    with open(subjects_file) as f:
        subjects = yaml.safe_load(f)

    if not args.dry_run and not health_check():
        print("ERROR: ComfyUI not reachable")
        sys.exit(1)

    kinds = ["locations", "characters", "scenes"] if args.kind == "all" else [args.kind]

    print("=" * 70)
    print(f"CONCEPT ART — z-image-base-t2i — {proj.name}")
    print("=" * 70)

    failed: list[str] = []
    total = 0
    for kind in kinds:
        items = subjects.get(kind, []) or []
        if args.only:
            items = [s for s in items if s["id"] == args.only]
        if not items:
            continue
        out_dir = concept_dir / kind
        print(f"\n{kind.upper()}:")
        for s in items:
            total += 1
            if not gen_one(s, kind, out_dir, args.force, args.dry_run):
                failed.append(f"{kind}/{s['id']}")

    print("\n" + "=" * 70)
    print(f"DONE — {total - len(failed)}/{total} generated")
    if failed:
        print(f"FAILED: {failed}")
        sys.exit(1)


if __name__ == "__main__":
    main()
