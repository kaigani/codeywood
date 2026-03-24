#!/usr/bin/env python3
"""
Regenerate EP01 prop refs in the illustrated animation style.

Previous versions came out as 3D product renders. These use the same
style prefix as the character designs to stay in the show's visual language.
"""

import time
from pathlib import Path

import requests

COMFYUI_BASE = "http://192.168.1.181:8100"
PROJECT = Path(__file__).resolve().parents[2] / "projects" / "stray-signal"
OUT = PROJECT / "REFERENCES" / "object_refs"

STYLE = "Stylized 2D animated illustration, graphic novel style with clean lines and flat color, sci-fi prop design,"
NEG = "3D render, photorealistic, photograph, blurry, low quality, text, watermark"


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


PROPS = [
    {
        "name": "device_off",
        "prompt": (
            f"{STYLE} a small handheld device on a light grey background. "
            "About the size of a large phone. Brushed aluminum body with a "
            "slightly ridged surface. Real glass screen, dark and off. A thin "
            "hairline crack runs across the lower third of the glass. The device "
            "looks old but solidly made — not sleek, not plastic. It has weight. "
            "Drawn in the same illustrated animation style as the rest of the show. "
            "Centered, clean background."
        ),
        "seed": 551,
    },
    {
        "name": "device_on",
        "prompt": (
            f"{STYLE} a small handheld device on a light grey background. "
            "Same design as a brushed aluminum phone-sized device with a "
            "ridged surface and hairline crack on the glass. The screen is ON "
            "— glowing electric cyan. A small geometric cat shape is visible "
            "on the screen, simple and iconic. The cyan glow illuminates the "
            "aluminum edges. Illustrated animation style. Centered, clean background."
        ),
        "seed": 552,
    },
    {
        "name": "multi_tool",
        "prompt": (
            f"{STYLE} a maintenance worker's multi-tool on a light grey background. "
            "A compact folding hand tool — matte grey metal with orange accent marks "
            "on the grip. Worn from use but functional. Has a flat blade, a small "
            "pry edge, and a wire stripper. Utilitarian, not fancy. The tool of "
            "someone who fixes things in corridors. Illustrated animation style. "
            "Centered, clean background."
        ),
        "seed": 553,
    },
    {
        "name": "datapad_maps",
        "prompt": (
            f"{STYLE} a battered tablet datapad on a light grey background. "
            "Worn scratched edges, scuffed back. The screen shows hand-drawn "
            "sector maps over a faint digital grid — obsessive small handwriting, "
            "annotations, question marks clustered in one section. Analog markings "
            "on a digital surface. A maintenance worker's personal map collection. "
            "Illustrated animation style. Centered, clean background."
        ),
        "seed": 554,
    },
]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    t0 = time.time()

    for i, p in enumerate(PROPS):
        print(f"\n[{i+1}/{len(PROPS)}] {p['name']}")
        data = z_image(p["prompt"], seed=p["seed"])
        save(data, OUT / f"{p['name']}.png")

    elapsed = time.time() - t0
    print(f"\n{'=' * 60}")
    print(f"{len(PROPS)} props in {elapsed:.0f}s")
    print(f"Review: {OUT}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
