#!/usr/bin/env python3
"""
Generate TABS pose variants from the locked 08 (duo glow+line) design.

All poses needed for EP01:
- Sitting/studying (clips 7, 13) — default idle
- Settled patience, paws tucked (clip 8) — after DELETE sequence
- Looking away, corner of screen (clip 8 end, 9)
- Reading/navigating, focused (clip 10) — scanning map files
- Pointing, weight forward (clip 11) — directional pulse
- Paw reaching at glass (clip 14) — emotional climax
- Oriented forward, waiting (clip 15) — morning, already pointing
"""

import time
from pathlib import Path

import requests

COMFYUI_BASE = "http://192.168.1.181:8100"
PROJECT = Path(__file__).resolve().parents[2] / "projects" / "stray-signal"
SOURCE = PROJECT / "REFERENCES" / "object_refs" / "_tabs_screen_render" / "08_duo_glow_and_line.png"
OUT = PROJECT / "REFERENCES" / "object_refs" / "tabs_poses"


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


# Keep prompt anchored: same character, same rendering style, same glow
ANCHOR = (
    "Same glowing cyan geometric cat character with the same rendering style — "
    "soft cyan filled body with brighter geometric edge lines, diamond eyes. "
    "Dark background."
)

POSES = [
    {
        "name": "tabs_sitting_default",
        "prompt": (
            f"This cat character sitting upright, looking directly at the "
            f"viewer with curious attention. Head tilted very slightly. "
            f"Ears forward. {ANCHOR}"
        ),
        "seed": 901,
    },
    {
        "name": "tabs_settled_patience",
        "prompt": (
            f"This cat character with its paws tucked neatly underneath its "
            f"body, settled and compact. Eyes half-closed, serene, patient. "
            f"The posture of a cat that has decided to wait. {ANCHOR}"
        ),
        "seed": 902,
    },
    {
        "name": "tabs_looking_away",
        "prompt": (
            f"This cat character turned away from the viewer, looking at "
            f"the far corner. Sitting but oriented to the right side, body "
            f"angled away. Demonstratively not looking at you. {ANCHOR}"
        ),
        "seed": 903,
    },
    {
        "name": "tabs_reading_focused",
        "prompt": (
            f"This cat character looking downward with intense focus, as if "
            f"reading something below it. Head angled down, ears forward, "
            f"eyes locked on something. Methodical concentration. {ANCHOR}"
        ),
        "seed": 904,
    },
    {
        "name": "tabs_pointing",
        "prompt": (
            f"This cat character in a pointing posture — body oriented to "
            f"the right, weight forward on front paws, nose aimed to the "
            f"right. Alert, focused, like a cat that has spotted something "
            f"and wants you to look. Tail straight out. {ANCHOR}"
        ),
        "seed": 905,
    },
    {
        "name": "tabs_paw_reaching",
        "prompt": (
            f"This cat character sitting at the edge of the frame, one paw "
            f"extended forward toward the viewer — reaching out gently but "
            f"not quite touching. A tender, careful gesture. The paw hovers "
            f"in space. Eyes looking at where the paw reaches. {ANCHOR}"
        ),
        "seed": 906,
    },
    {
        "name": "tabs_oriented_forward",
        "prompt": (
            f"This cat character standing alert, body oriented forward "
            f"(toward the right of frame), already in motion posture. "
            f"Weight on front paws, ready to move. Ears forward, eyes "
            f"bright. The posture of someone who was already waiting "
            f"for you to catch up. {ANCHOR}"
        ),
        "seed": 907,
    },
]


def main():
    OUT.mkdir(parents=True, exist_ok=True)

    if not SOURCE.exists():
        print(f"ERROR: Source not found: {SOURCE}")
        return

    t0 = time.time()

    # First copy the source as the canonical sitting reference
    print(f"\nSource: {SOURCE.name}")

    for i, p in enumerate(POSES):
        print(f"\n[{i+1}/{len(POSES)}] {p['name']}")
        data = qwen_edit(p["prompt"], SOURCE, seed=p["seed"])
        save(data, OUT / f"{p['name']}.png")

    elapsed = time.time() - t0
    print(f"\n{'=' * 60}")
    print(f"{len(POSES)} poses in {elapsed:.0f}s")
    print(f"Review: {OUT}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
