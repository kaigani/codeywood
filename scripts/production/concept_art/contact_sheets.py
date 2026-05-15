#!/usr/bin/env python3
"""Build concept-art contact sheets for a project.

Reads the project's CONCEPT_ART/ directory and writes two review sheets:
  scenes_contact_sheet.png  — scenes grouped by EP##_ prefix
  contact_sheet.png         — locations (wide) + characters (portrait)

Usage:
    python3 contact_sheets.py --project projects/260513-gemma-anthology
"""

from __future__ import annotations

import argparse
import sys
from collections import defaultdict
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

REPO_ROOT = Path(__file__).resolve().parents[3]

BG = (250, 246, 235)
INK = (40, 32, 24)
PAD = 28

try:
    F_LABEL = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 22)
    F_HEADER = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 34)
except Exception:
    F_LABEL = ImageFont.load_default()
    F_HEADER = ImageFont.load_default()


def thumb(p: Path, w: int, h: int) -> Image.Image:
    im = Image.open(p).convert("RGB")
    im.thumbnail((w, h), Image.LANCZOS)
    canvas = Image.new("RGB", (w, h), BG)
    canvas.paste(im, ((w - im.width) // 2, (h - im.height) // 2))
    return canvas


def build_scenes_sheet(concept_dir: Path, project_label: str) -> Path | None:
    scenes_dir = concept_dir / "scenes"
    pngs = sorted(scenes_dir.glob("*.png")) if scenes_dir.exists() else []
    if not pngs:
        return None

    # Group by EP## prefix if present; otherwise one ungrouped bucket.
    eps: dict[str, list[Path]] = defaultdict(list)
    for p in pngs:
        prefix = p.stem.split("_", 1)[0].upper()
        bucket = prefix if prefix.startswith("EP") and prefix[2:].isdigit() else "SCENES"
        eps[bucket].append(p)
    ep_keys = sorted(eps.keys())

    cols = 3
    tw, th = 480, 320
    label_h = 30
    row_h = th + label_h + PAD
    ep_header_h = 50

    def rows_for(n: int, c: int = cols) -> int:
        return (n + c - 1) // c

    width = cols * tw + (cols + 1) * PAD
    height = sum(ep_header_h + rows_for(len(eps[k])) * row_h for k in ep_keys) + PAD + 40

    out = Image.new("RGB", (width, height), BG)
    draw = ImageDraw.Draw(out)
    draw.text(
        (PAD, PAD // 2),
        f"{project_label.upper()} — SCENE SKETCHES",
        fill=INK,
        font=F_HEADER,
    )

    y = ep_header_h + 30
    for ep in ep_keys:
        draw.text((PAD, y - 8), ep, fill=INK, font=F_HEADER)
        y += 8
        for i, p in enumerate(eps[ep]):
            col = i % cols
            row = i // cols
            x = PAD + col * (tw + PAD)
            yy = y + row * row_h
            out.paste(thumb(p, tw, th), (x, yy))
            label = p.stem.split("_", 1)[1] if "_" in p.stem else p.stem
            draw.text((x + 4, yy + th + 2), label, fill=INK, font=F_LABEL)
        y += rows_for(len(eps[ep])) * row_h

    target = concept_dir / "scenes_contact_sheet.png"
    out.save(target, "PNG", optimize=True)
    return target


def build_master_sheet(concept_dir: Path) -> Path | None:
    locs = sorted((concept_dir / "locations").glob("*.png"))
    chars = sorted((concept_dir / "characters").glob("*.png"))
    if not locs and not chars:
        return None

    tw, th = 480, 320
    cols = 4
    label_h = 30
    row_h = th + label_h + PAD
    section_h = 50

    ptw, pth = 240, 360
    pcols = 6
    prow_h = pth + label_h + PAD

    def rows_for(n: int, c: int) -> int:
        return (n + c - 1) // c if n else 0

    width = cols * tw + (cols + 1) * PAD
    height = (
        (section_h + rows_for(len(locs), cols) * row_h if locs else 0)
        + (section_h + rows_for(len(chars), pcols) * prow_h if chars else 0)
        + PAD
    )

    out = Image.new("RGB", (width, height), BG)
    draw = ImageDraw.Draw(out)

    y = 0
    if locs:
        draw.text((PAD, PAD // 2), "LOCATIONS", fill=INK, font=F_HEADER)
        y = section_h
        for i, p in enumerate(locs):
            col = i % cols
            row = i // cols
            x = PAD + col * (tw + PAD)
            yy = y + row * row_h
            out.paste(thumb(p, tw, th), (x, yy))
            draw.text((x + 4, yy + th + 2), p.stem, fill=INK, font=F_LABEL)
        y = section_h + rows_for(len(locs), cols) * row_h

    if chars:
        draw.text((PAD, y - 8), "CHARACTERS", fill=INK, font=F_HEADER)
        y += section_h - 30
        for i, p in enumerate(chars):
            col = i % pcols
            row = i // pcols
            x = PAD + col * (ptw + PAD)
            yy = y + row * prow_h
            out.paste(thumb(p, ptw, pth), (x, yy))
            draw.text((x + 4, yy + pth + 2), p.stem, fill=INK, font=F_LABEL)

    target = concept_dir / "contact_sheet.png"
    out.save(target, "PNG", optimize=True)
    return target


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", required=True, help="path to project root")
    args = ap.parse_args()

    proj = (REPO_ROOT / args.project).resolve()
    concept_dir = proj / "CONCEPT_ART"
    if not concept_dir.exists():
        print(f"ERROR: missing {concept_dir}")
        sys.exit(1)

    label = proj.name
    if "-" in label and label.split("-", 1)[0].isdigit():
        label = label.split("-", 1)[1]
    label = label.replace("-", " ")

    s = build_scenes_sheet(concept_dir, label)
    if s:
        print(f"  scenes -> {s.relative_to(REPO_ROOT)} ({s.stat().st_size // 1024} KB)")
    m = build_master_sheet(concept_dir)
    if m:
        print(f"  master -> {m.relative_to(REPO_ROOT)} ({m.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
