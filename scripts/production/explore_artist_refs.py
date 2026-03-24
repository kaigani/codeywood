#!/usr/bin/env python3
"""
Stray Signal — Artist Reference Style Test

Same character (Neda portrait, Grid appearance) rendered with different
artist/show anchors in the style prefix. Goal: find which reference name
z-image understands best to produce the locked "Concrete & Ink" look.

Pipeline: ComfyUI z-image-base-t2i (local, $0.00)
Output: projects/stray-signal/REFERENCES/exploration_v3/artist_test/
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
OUTPUT_DIR = PROJECT / "REFERENCES" / "exploration_v3" / "artist_test"

# ---------------------------------------------------------------------------
# Constant character description (Neda portrait, Grid)
# ---------------------------------------------------------------------------
NEDA = (
    "Close-up portrait of a 17-year-old girl, compact athletic build, "
    "brown skin with warm undertone, angular face with strong jaw and high cheekbones, "
    "sharp dark assessing eyes, black hair in an asymmetric cut — shaved close on "
    "the left side with longer hair swept across to the right, "
    "thin copper-wire braid on the shaved left side, "
    "angular steel-blue geometric jacket with origami-folded collar, "
    "grey underlayer visible at neckline, "
    "brutalist concrete wall background with speckle texture, "
    "cold flat fluorescent light, steel-blue and concrete grey palette, "
    "expression controlled and neutral, jaw tension visible. "
)

# Also test Kai to see if the anchor holds across characters
KAI = (
    "Close-up portrait of a 16-year-old boy, lean narrow-shouldered build, "
    "light brown skin, softer rounder face, dark hair in a shaggy overgrown cut "
    "falling across his forehead and into his eyes, watchful dark eyes, "
    "angular geometric jacket in concrete grey with high collar, "
    "brutalist concrete wall background with speckle texture, "
    "cold flat fluorescent light, steel-blue and concrete grey palette, "
    "expression watchful and quiet. "
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
# Artist anchors to test
# ---------------------------------------------------------------------------
ARTIST_ANCHORS = {
    "jamie_hewlett": (
        "In the style of Jamie Hewlett, bold confident ink outlines, "
        "flat color fills with subtle tone shifts, angular specific character design, "
        "graphic novel aesthetic, strong silhouette, limited palette, "
    ),
    "studio_mir": (
        "In the style of Studio Mir animation, bold ink outlines, "
        "flat cel-shaded coloring, realistic proportions, angular character design, "
        "cinematic lighting, animation production frame, "
    ),
    "hewlett_mir": (
        "In the style of Jamie Hewlett and Studio Mir, bold ink outlines, "
        "flat cel-shaded coloring with subtle tone variation, "
        "angular specific character design with realistic proportions, "
        "graphic novel meets animation production frame, limited palette, "
    ),
    "tartakovsky": (
        "In the style of Genndy Tartakovsky, bold geometric shapes, "
        "flat color with no gradients, strong angular silhouettes, "
        "minimal detail maximum impact, graphic bold outlines, "
        "animation cel aesthetic, "
    ),
    "castlevania": (
        "In the style of Netflix Castlevania by Powerhouse Animation, "
        "bold dark outlines, flat cel coloring with atmospheric lighting, "
        "realistic proportions, angular faces, dark palette, "
        "animation production frame, "
    ),
    "spiderverse": (
        "In the style of Into the Spider-Verse, graphic novel halftone texture, "
        "bold ink outlines, flat color with Ben-Day dots in shadows, "
        "comic panel aesthetic, strong graphic design, limited palette, "
        "animation frame with print texture, "
    ),
    "korra": (
        "In the style of The Legend of Korra, Studio Mir animation, "
        "clean bold outlines, flat cel-shaded coloring, "
        "realistic proportions with angular features, "
        "cinematic composition, animation production frame, "
    ),
    "boondocks": (
        "In the style of The Boondocks animated series, bold dark outlines, "
        "flat cel coloring, realistic proportions, angular specific faces, "
        "cinematic framing, limited color palette, "
        "animation production frame, "
    ),
    "hewlett_spiderverse": (
        "In the style of Jamie Hewlett meets Into the Spider-Verse, "
        "bold confident ink outlines, flat color with speckle grain texture, "
        "graphic novel aesthetic, angular specific character design, "
        "strong silhouette, limited palette, animation frame, "
    ),
    "mir_hewlett_dark": (
        "In the style of Studio Mir and Jamie Hewlett, dark palette, "
        "thick confident ink outlines, flat cel coloring with hard-edged shadows, "
        "angular character design with broad realistic features, "
        "strong silhouette readability, near-black shadows, "
        "animation production frame, graphic novel influence, "
    ),
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
    parser = argparse.ArgumentParser(description="Artist reference style test")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    total = len(ARTIST_ANCHORS) * 2  # Neda + Kai per anchor

    if args.dry_run:
        print(f"Would generate {total} images ({len(ARTIST_ANCHORS)} anchors x 2 characters)")
        for name in ARTIST_ANCHORS:
            print(f"  neda_{name}.png")
            print(f"  kai_{name}.png")
        sys.exit(0)

    print("=" * 70)
    print("Artist Reference Style Test")
    print(f"Output: {OUTPUT_DIR}")
    print(f"{len(ARTIST_ANCHORS)} anchors x 2 characters = {total} images")
    print("=" * 70)

    count = 0
    for anchor_name, anchor_prefix in ARTIST_ANCHORS.items():
        for char_name, char_desc in [("neda", NEDA), ("kai", KAI)]:
            count += 1
            filename = f"{char_name}_{anchor_name}.png"
            filepath = OUTPUT_DIR / filename

            if filepath.exists():
                print(f"\n[{count}/{total}] SKIP (exists): {filename}")
                continue

            prompt = anchor_prefix + char_desc
            seed = 13000 + hash(f"{anchor_name}_{char_name}") % 10000

            print(f"\n[{count}/{total}] {filename}")
            print(f"  Anchor: {anchor_name}")

            try:
                data = submit_and_wait("z-image-base-t2i", {
                    "prompt": prompt,
                    "negative_prompt": NEGATIVE,
                    "seed": str(seed),
                    "steps": "25",
                    "cfg": "4",
                    "width": "720",
                    "height": "1024",
                })
                save(data, filepath)
            except Exception as e:
                print(f"    ERROR: {e}")
                continue

    print(f"\n{'=' * 70}")
    print("ARTIST TEST COMPLETE")
    print("=" * 70)
