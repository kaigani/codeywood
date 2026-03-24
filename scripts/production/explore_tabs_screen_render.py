#!/usr/bin/env python3
"""
Render B1 TABS design into on-screen style variants via qwen-edit.

Starting from the clean B1 origami design, apply different screen
rendering treatments to find the right look for TABS displayed
on the device screen.
"""

import time
from pathlib import Path

import requests

COMFYUI_BASE = "http://192.168.1.181:8100"
PROJECT = Path(__file__).resolve().parents[2] / "projects" / "stray-signal"
SOURCE = PROJECT / "REFERENCES" / "object_refs" / "_tabs_design" / "B1_origami_sitting.png"
OUT = PROJECT / "REFERENCES" / "object_refs" / "_tabs_screen_render"


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
    while time.time() < deadline:
        status = requests.get(f"{COMFYUI_BASE}/jobs/{job_id}").json()
        if status["status"] == "completed":
            elapsed = time.time() - (deadline - timeout)
            print(f"  Done ({elapsed:.0f}s)")
            return requests.get(f"{COMFYUI_BASE}/jobs/{job_id}/result").content
        if status["status"] == "error":
            raise RuntimeError(f"Failed: {status.get('error')}")
        time.sleep(2)
    raise TimeoutError("Timeout")


def qwen_edit(prompt, image_path, seed=42, steps=4):
    params = {"prompt": prompt, "seed": str(seed), "steps": str(steps)}
    with open(image_path, "rb") as fh:
        files = {"image": (Path(image_path).name, fh, "image/png")}
        return submit_and_wait("qwen-image-edit", params, files=files)


def save(data, path):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as f:
        f.write(data)
    print(f"  -> {Path(path).name}")


VARIANTS = [
    # --- Rendering on black screen background ---
    {
        "name": "01_cyan_glow_black",
        "prompt": (
            "Render this cat character glowing in electric cyan on a pure "
            "black background. Keep the exact same character design and pose. "
            "The cat is displayed on a device screen — it glows softly with "
            "cyan light. The faceted geometric lines on its body are visible "
            "as slightly brighter edges. Dark screen background."
        ),
        "seed": 801,
    },
    {
        "name": "02_soft_glow_minimal",
        "prompt": (
            "Show this same cat character in glowing cyan on a black screen. "
            "Soft ambient glow around the character. The geometric facets "
            "catch the light as subtle edge highlights. Keep the design "
            "exactly — same proportions, same face, same pose. It looks like "
            "a cute holographic mascot displayed on a small screen."
        ),
        "seed": 802,
    },
    {
        "name": "03_flat_cyan_screen",
        "prompt": (
            "Show this cat character as a flat cyan graphic on a dark screen. "
            "Like a retro computer program — solid cyan fill with slightly "
            "lighter lines where the geometric facets meet. No 3D shading, "
            "flat color. Same character, same pose. Simple, clean, like an "
            "icon on an old terminal display."
        ),
        "seed": 803,
    },
    {
        "name": "04_line_art_cyan",
        "prompt": (
            "Draw this cat character using only cyan lines on a black "
            "background. The lines follow the geometric facet edges of "
            "the design — the fold lines become the drawing. The eyes are "
            "filled bright cyan dots. The rest is line work only — no fill, "
            "just the structural lines of the origami cat glowing cyan."
        ),
        "seed": 804,
    },
    {
        "name": "05_screen_pixel_art",
        "prompt": (
            "Show this cat character as if displayed on a small low-resolution "
            "screen. The same design but rendered with slight pixelation at "
            "the edges — like a character on a handheld game device. Cyan "
            "colored on dark screen. The geometric facets are visible as "
            "color value shifts. Cute and readable despite the low-res feel."
        ),
        "seed": 805,
    },
    {
        "name": "06_laser_etch_style",
        "prompt": (
            "Render this cat character in the style of a laser etching or "
            "engraving. Thin precise cyan lines on black background. The "
            "geometric facet edges become fine etched lines. The eyes are "
            "bright filled shapes. A subtle glow along the lines like laser "
            "light. Precise, delicate, technical but still cute. Same "
            "character design and proportions."
        ),
        "seed": 806,
    },
    {
        "name": "07_screen_scanlines",
        "prompt": (
            "Show this cat character on a device screen with subtle horizontal "
            "scanlines. The cat glows in cyan. The geometric facets are visible "
            "as lighter edge lines. Faint CRT-style scanlines across the whole "
            "image give it a screen-display feeling. Same character, same pose. "
            "Dark screen background."
        ),
        "seed": 807,
    },
    {
        "name": "08_duo_glow_and_line",
        "prompt": (
            "This cat character displayed on a dark screen in two layers: "
            "a soft filled cyan glow for the body shape, and brighter thin "
            "lines along the geometric facet edges on top. The combination "
            "reads as a cute glowing mascot with visible geometric structure. "
            "Same design, same pose. The eyes are the brightest element."
        ),
        "seed": 808,
    },
]


def main():
    OUT.mkdir(parents=True, exist_ok=True)

    if not SOURCE.exists():
        print(f"ERROR: Source not found: {SOURCE}")
        return

    t0 = time.time()

    for i, v in enumerate(VARIANTS):
        print(f"\n[{i+1}/{len(VARIANTS)}] {v['name']}")
        data = qwen_edit(v["prompt"], SOURCE, seed=v["seed"])
        save(data, OUT / f"{v['name']}.png")

    elapsed = time.time() - t0
    print(f"\n{'=' * 60}")
    print(f"{len(VARIANTS)} renders in {elapsed:.0f}s")
    print(f"Review: {OUT}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
