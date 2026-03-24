#!/usr/bin/env python3
"""
TABS style exploration — finding the right visual language for a cute
digital cat mascot with subtle wireframe geometry.

Goal: cute FIRST, wireframe SECOND. Think Tamagotchi meets hologram.
Must be in the illustrated animation style of the show, not 3D render.

Running multiple prompt variations to find the sweet spot.
"""

import io
import time
from pathlib import Path

from PIL import Image
import requests

COMFYUI_BASE = "http://192.168.1.181:8100"
PROJECT = Path(__file__).resolve().parents[2] / "projects" / "stray-signal"
OUT = PROJECT / "REFERENCES" / "object_refs" / "_tabs_exploration"


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


def z_image(prompt, neg="", seed=42, w=1024, h=1024):
    return submit_and_wait("z-image-base-t2i", {
        "prompt": prompt, "negative_prompt": neg,
        "seed": str(seed), "steps": "25", "cfg": "4",
        "width": str(w), "height": str(h),
    })


def save(data, path):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as f:
        f.write(data)
    print(f"  -> {path}")


# Style prefix that anchors to the show's animation look
STYLE = "Stylized 2D animated illustration, graphic novel style with clean lines and flat color,"

# Common negative to avoid 3D renders
NEG = "3D render, photorealistic, realistic fur, realistic cat, blurry, low quality, photograph"

VARIANTS = [
    # --- Approach 1: Digital pet / Tamagotchi language ---
    {
        "name": "01_digital_pet_mascot",
        "prompt": (
            f"{STYLE} a cute digital pet cat mascot on a dark screen. "
            "The cat is electric cyan, small and round with oversized ears "
            "and big curious dot eyes. It sits upright like a Tamagotchi character. "
            "Simple geometric shapes — circles and triangles making up a "
            "friendly cat silhouette. Faint grid lines visible on its body "
            "like a subtle digital texture. Glowing softly. Pure black background."
        ),
        "seed": 601,
    },
    # --- Approach 2: Pixel mascot with glow ---
    {
        "name": "02_pixel_mascot_glow",
        "prompt": (
            f"{STYLE} a tiny glowing cyan cat character on a dark screen. "
            "The cat is drawn with chunky pixel-inspired shapes but smooth edges. "
            "Oversized head, big round eyes, stubby legs, tiny triangle ears. "
            "It looks like a friendly app icon come to life. Soft cyan glow "
            "(#00E5FF) around its outline. Minimal geometric detail — "
            "just enough lines to suggest digital origin. Pure black background."
        ),
        "seed": 602,
    },
    # --- Approach 3: Chibi hologram ---
    {
        "name": "03_chibi_hologram",
        "prompt": (
            f"{STYLE} a chibi-proportioned holographic cat on a black screen. "
            "Electric cyan color. Big head, small body, enormous pointed ears. "
            "Round expressive eyes with a curious look. The body has a slight "
            "translucent quality with faint geometric edges visible — like a "
            "hologram projected on glass. Cute and appealing, like a digital "
            "companion. Soft glow. Pure black background."
        ),
        "seed": 603,
    },
    # --- Approach 4: Animated mascot, wireframe as skin pattern ---
    {
        "name": "04_mascot_wireframe_skin",
        "prompt": (
            f"{STYLE} a cute cartoon cat character colored in electric cyan. "
            "Sitting pose, looking at the viewer with big bright eyes and a "
            "tilted head. The cat has a friendly rounded design with pointed "
            "ears slightly too big for its head. Its surface has a subtle "
            "wireframe pattern like a digital skin texture — thin geometric "
            "lines criss-crossing its body, but the overall shape is soft "
            "and appealing. Glowing against pure black background."
        ),
        "seed": 604,
    },
    # --- Approach 5: Neon sign cat ---
    {
        "name": "05_neon_sign_cat",
        "prompt": (
            f"{STYLE} a cute cat drawn in glowing cyan neon lines on a dark "
            "background. The lines are clean and continuous like a neon sign — "
            "one stroke forming ears, head, body, tail. Big round eyes as "
            "two bright dots. The cat sits with its tail curled around its "
            "paws. Simple, iconic, immediately readable as a cute cat. "
            "Soft cyan glow around the lines. Pure black background."
        ),
        "seed": 605,
    },
    # --- Approach 6: Screen UI mascot (like a virtual assistant) ---
    {
        "name": "06_ui_assistant_cat",
        "prompt": (
            f"{STYLE} a small friendly cat character displayed on a device "
            "screen UI. The cat is electric cyan, designed like a virtual "
            "assistant mascot — round face, big eyes, small smile, pointed "
            "ears. It sits in the center of a dark screen interface. The "
            "style is flat design with subtle geometric facets on its body, "
            "like a low-poly game character but drawn in 2D with clean "
            "outlines. Cute and approachable. Dark screen background."
        ),
        "seed": 606,
    },
    # --- Approach 7: Origami-geometric cute cat ---
    {
        "name": "07_origami_geometric",
        "prompt": (
            f"{STYLE} a cute cat made of geometric shapes in glowing cyan. "
            "Like a paper-craft or origami cat — angular folds creating "
            "ears, head, body — but with a friendly face. Big triangular "
            "ears, diamond-shaped eyes with bright pupils, a small angular "
            "nose. The geometric construction is visible but the overall "
            "impression is cute and endearing, not technical. Soft cyan "
            "glow. Pure black background."
        ),
        "seed": 607,
    },
    # --- Approach 8: Digital sticker / emoji cat ---
    {
        "name": "08_digital_sticker",
        "prompt": (
            f"{STYLE} a cute cat emoji character in electric cyan on a dark "
            "screen. The cat has a simple iconic design — round head, "
            "pointed ears, two big shiny eyes, a tiny curved mouth. "
            "Sitting with its tail wrapped around. The body is solid cyan "
            "with thin lighter lines suggesting digital geometry underneath — "
            "like looking at a cute sticker through a faint grid overlay. "
            "Charming and pocket-sized. Pure black background."
        ),
        "seed": 608,
    },
]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    t0 = time.time()

    for i, v in enumerate(VARIANTS):
        print(f"\n[{i+1}/{len(VARIANTS)}] {v['name']}")
        data = z_image(v["prompt"], neg=NEG, seed=v["seed"])
        save(data, OUT / f"{v['name']}.png")

    elapsed = time.time() - t0
    print(f"\n{'=' * 60}")
    print(f"{len(VARIANTS)} variants in {elapsed:.0f}s")
    print(f"Review: {OUT}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
