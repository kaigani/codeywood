#!/usr/bin/env python3
"""
TABS character design exploration — clean designs first, rendering later.

Two directions:
A) Chibi hologram — round, big eyes, expressive, soft proportions
B) Origami geometric — angular facets, cute face, folded-paper construction

Generate clean character designs on white/light backgrounds,
no digital effects, no glow, no wireframe. Just the character.
Then we'll apply the screen rendering style via qwen-edit.
"""

import time
from pathlib import Path

import requests

COMFYUI_BASE = "http://192.168.1.181:8100"
PROJECT = Path(__file__).resolve().parents[2] / "projects" / "stray-signal"
OUT = PROJECT / "REFERENCES" / "object_refs" / "_tabs_design"

STYLE = "Clean 2D character design sheet, illustrated animation style, solid colors, clean outlines,"

NEG = "3D render, photorealistic, glow, neon, wireframe, grid, dark background, blurry, text"


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


def z_image(prompt, neg=NEG, seed=42, w=1024, h=1024):
    return submit_and_wait("z-image-base-t2i", {
        "prompt": prompt, "negative_prompt": neg,
        "seed": str(seed), "steps": "25", "cfg": "4",
        "width": str(w), "height": str(h),
    })


def save(data, path):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as f:
        f.write(data)
    print(f"  -> {Path(path).name}")


VARIANTS = [
    # ===================================================================
    # DIRECTION A: Chibi — round, soft, expressive
    # ===================================================================
    {
        "name": "A1_chibi_sitting",
        "prompt": (
            f"{STYLE} a cute chibi cat character. Cyan colored (#00E5FF). "
            "Big round head, enormous pointed ears, large expressive eyes "
            "with bright highlights. Small compact body, stubby legs, "
            "curled tail. Sitting upright, looking at viewer with curiosity. "
            "Simple clean design, easy to reproduce consistently. "
            "Light grey background. Front view."
        ),
        "seed": 701,
    },
    {
        "name": "A2_chibi_turnaround",
        "prompt": (
            f"{STYLE} character turnaround sheet of a cute chibi cat. "
            "Cyan colored. Three views side by side: front view, three-quarter "
            "view, side profile. Big head, pointed ears too large for body, "
            "big round eyes, small triangular nose, tiny smile. Compact round "
            "body, short legs, long curled tail. Simple design with minimal "
            "detail. Light grey background."
        ),
        "seed": 702,
        "w": 1536, "h": 1024,
    },
    {
        "name": "A3_chibi_expressions",
        "prompt": (
            f"{STYLE} expression sheet for a cute chibi cyan cat character. "
            "Six expressions arranged in a grid: curious (head tilt), alert "
            "(ears forward, eyes wide), patient (eyes half-closed, serene), "
            "pointing (body oriented right, nose forward), reaching (one paw "
            "extended), settled (paws tucked under, content). Same character "
            "in all six. Light grey background."
        ),
        "seed": 703,
        "w": 1536, "h": 1024,
    },

    # ===================================================================
    # DIRECTION B: Origami — angular facets, folded construction
    # ===================================================================
    {
        "name": "B1_origami_sitting",
        "prompt": (
            f"{STYLE} a cute cat character made of angular geometric facets, "
            "like a paper-craft or low-poly design. Cyan colored (#00E5FF). "
            "The body is constructed from flat triangular and diamond shapes "
            "folded together. Big triangular ears, diamond-shaped eyes with "
            "bright pupils, small angular nose. Despite the geometric "
            "construction the overall impression is cute and friendly. "
            "Sitting upright, looking at viewer. Light grey background."
        ),
        "seed": 711,
    },
    {
        "name": "B2_origami_turnaround",
        "prompt": (
            f"{STYLE} character turnaround sheet of a cute geometric cat "
            "made of angular facets. Cyan colored. Three views side by side: "
            "front, three-quarter, side profile. The cat is constructed from "
            "flat planes and sharp folds like origami. Big triangular ears, "
            "faceted round head, angular body with visible fold lines. "
            "Cute proportions — big head, small body. The geometric "
            "construction IS the design, not a texture. Light grey background."
        ),
        "seed": 712,
        "w": 1536, "h": 1024,
    },
    {
        "name": "B3_origami_expressions",
        "prompt": (
            f"{STYLE} expression sheet for a cute geometric faceted cyan cat. "
            "Six expressions arranged in a grid: curious (head angled), alert "
            "(ears rotated forward), patient (eyes narrowed peacefully), "
            "pointing (body oriented right, angular stance), reaching (one "
            "angular paw extended forward), settled (folded compact, paws "
            "tucked). Same geometric cat in all six. Angular construction "
            "throughout. Light grey background."
        ),
        "seed": 713,
        "w": 1536, "h": 1024,
    },

    # ===================================================================
    # DIRECTION C: Hybrid — chibi proportions, subtle angular facets
    # ===================================================================
    {
        "name": "C1_hybrid_sitting",
        "prompt": (
            f"{STYLE} a cute cat character that blends rounded chibi proportions "
            "with subtle geometric facets. Cyan colored (#00E5FF). Big round "
            "head with slight angular planes on the cheeks. Enormous pointed "
            "ears with a single fold line each. Large round eyes with diamond "
            "highlights. Compact body with soft edges but visible geometric "
            "seams where shapes meet. Sitting upright, friendly and curious. "
            "Light grey background. Front view."
        ),
        "seed": 721,
    },
    {
        "name": "C2_hybrid_turnaround",
        "prompt": (
            f"{STYLE} character turnaround of a cute cyan cat with chibi "
            "proportions and subtle geometric facets. Three views: front, "
            "three-quarter, side. Big head, oversized ears with fold lines, "
            "round eyes, small angular nose. The body reads as cute first, "
            "geometric second — soft overall silhouette with visible facet "
            "seams where planes meet. Short legs, curled tail with angular "
            "segments. Light grey background."
        ),
        "seed": 722,
        "w": 1536, "h": 1024,
    },
]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    t0 = time.time()

    for i, v in enumerate(VARIANTS):
        print(f"\n[{i+1}/{len(VARIANTS)}] {v['name']}")
        w = v.get("w", 1024)
        h = v.get("h", 1024)
        data = z_image(v["prompt"], seed=v["seed"], w=w, h=h)
        save(data, OUT / f"{v['name']}.png")

    elapsed = time.time() - t0
    print(f"\n{'=' * 60}")
    print(f"{len(VARIANTS)} designs in {elapsed:.0f}s")
    print(f"Review: {OUT}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
