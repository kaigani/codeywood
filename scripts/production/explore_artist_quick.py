#!/usr/bin/env python3
"""Quick one-off artist anchor test."""

import io
import time
from pathlib import Path
from PIL import Image
import requests

COMFYUI_BASE = "http://192.168.1.181:8100"
PROJECT = Path(__file__).resolve().parents[2] / "projects" / "stray-signal"
OUTPUT_DIR = PROJECT / "REFERENCES" / "exploration_v3" / "artist_test"

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

ANCHORS = {
    "mir_korra": (
        "In the style of Studio Mir and The Legend of Korra, "
        "bold clean ink outlines, flat cel-shaded coloring, "
        "realistic proportions with angular features, "
        "cinematic composition, dark atmospheric palette, "
        "animation production frame, "
    ),
}


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


if __name__ == "__main__":
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for anchor_name, anchor_prefix in ANCHORS.items():
        for char_name, char_desc in [("neda", NEDA), ("kai", KAI)]:
            filename = f"{char_name}_{anchor_name}.png"
            print(f"\n{filename}")
            prompt = anchor_prefix + char_desc
            seed = 14000 + hash(f"{anchor_name}_{char_name}") % 10000
            data = submit_and_wait("z-image-base-t2i", {
                "prompt": prompt,
                "negative_prompt": NEGATIVE,
                "seed": str(seed),
                "steps": "25",
                "cfg": "4",
                "width": "720",
                "height": "1024",
            })
            save(data, OUTPUT_DIR / filename)
    print("\nDone.")
