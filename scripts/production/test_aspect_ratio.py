#!/usr/bin/env python3
"""
Test qwen-edit aspect ratio behavior.

Questions:
1. Does qwen-edit preserve exact input dimensions?
2. If we feed 1280x720 (16:9), do we get 1280x720 out?
3. What about 1008x576 (ComfyUI's native 16:9)?
"""

import time
from pathlib import Path
from PIL import Image
import io

import requests

COMFYUI_BASE = "http://192.168.1.181:8100"
PROJECT = Path(__file__).resolve().parents[2] / "projects" / "stray-signal"
OUT = PROJECT / "PRODUCTION" / "EP01_v02" / "frames" / "_aspect_tests"


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
            result = requests.get(f"{COMFYUI_BASE}/jobs/{job_id}/result")
            return result.content
        if status["status"] == "error":
            raise RuntimeError(f"Job {job_id} failed: {status.get('error')}")
        time.sleep(2)
    raise TimeoutError(f"Timeout")


def get_dims(png_bytes):
    img = Image.open(io.BytesIO(png_bytes))
    return img.size  # (width, height)


def main():
    OUT.mkdir(parents=True, exist_ok=True)

    loc = PROJECT / "REFERENCES" / "location_refs" / "v2" / "loc_housing_unit.png"
    kai = PROJECT / "REFERENCES" / "identity_sheets" / "kai-reference-01.png"

    print("Source dimensions:")
    print(f"  Location: {Image.open(loc).size}")
    print(f"  Character: {Image.open(kai).size}")

    # Test 1: qwen-edit with 1280x720 location as image (1 ref)
    print("\n[Test 1] qwen-edit, 1 ref (1280x720 location)")
    with open(loc, "rb") as f:
        data = submit_and_wait("qwen-image-edit", {
            "prompt": "This same room but from a slightly different angle, looking at the desk corner. Keep the same style.",
            "seed": "999", "steps": "4",
        }, files={"image": (loc.name, f, "image/png")})
    dims = get_dims(data)
    print(f"  Output: {dims[0]}x{dims[1]}")
    with open(OUT / "test1_1ref_location.png", "wb") as f:
        f.write(data)

    # Test 2: qwen-edit with 1280x720 location + 1024x1024 character (2 refs)
    print("\n[Test 2] qwen-edit, 2 refs (1280x720 location + 1024x1024 character)")
    with open(loc, "rb") as f1, open(kai, "rb") as f2:
        data = submit_and_wait("qwen-image-edit", {
            "prompt": "The boy from image 2 sits at a desk in this room. Amber desk lamp lighting.",
            "seed": "999", "steps": "4",
        }, files={
            "image": (loc.name, f1, "image/png"),
            "image2": (kai.name, f2, "image/png"),
        })
    dims = get_dims(data)
    print(f"  Output: {dims[0]}x{dims[1]}")
    with open(OUT / "test2_2ref_loc_char.png", "wb") as f:
        f.write(data)

    # Test 3: z-image at different sizes to see what it actually outputs
    for w, h, label in [(1280, 720, "1280x720"), (1008, 576, "1008x576"), (1920, 1080, "1920x1080")]:
        print(f"\n[Test 3] z-image-base-t2i at {label}")
        data = submit_and_wait("z-image-base-t2i", {
            "prompt": "Brutalist sci-fi corridor, vanishing point perspective, 4500K fluorescent strips, polymer floor, no people",
            "negative_prompt": "people, characters, animals, blurry, low quality",
            "seed": "42", "steps": "25", "cfg": "4",
            "width": str(w), "height": str(h),
        })
        dims = get_dims(data)
        print(f"  Requested: {w}x{h} → Output: {dims[0]}x{dims[1]}")
        with open(OUT / f"test3_zimage_{w}x{h}.png", "wb") as f:
            f.write(data)

    print("\nDone. Check outputs in:", OUT)


if __name__ == "__main__":
    main()
