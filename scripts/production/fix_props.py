#!/usr/bin/env python3
"""Fix props via edit-on-edit."""

import time
from pathlib import Path
import requests

COMFYUI_BASE = "http://192.168.1.181:8100"
PROJECT = Path(__file__).resolve().parents[2] / "projects" / "stray-signal"
REFS = PROJECT / "REFERENCES" / "object_refs"


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


def qwen_fix(prompt, image_path, seed=42, steps=4):
    params = {"prompt": prompt, "seed": str(seed), "steps": str(steps)}
    with open(image_path, "rb") as fh:
        files = {"image": (Path(image_path).name, fh, "image/png")}
        return submit_and_wait("qwen-image-edit", params, files=files)


def save(data, path):
    with open(path, "wb") as f:
        f.write(data)
    print(f"  -> {Path(path).name}")


def main():
    # Fix 1: Device on — derive from device_off to match form factor
    print("\n[1] Device on — from device_off, turn on screen with cyan cat")
    data = qwen_fix(
        prompt=(
            "Turn on this device's screen. The screen glows electric cyan "
            "with a small geometric cat shape visible on it. The cyan light "
            "illuminates the aluminum edges. Keep the exact same device "
            "shape, same angle, same cracked glass. Just the screen is now on."
        ),
        image_path=REFS / "device_off.png",
        seed=561,
    )
    save(data, REFS / "device_on.png")

    # Fix 2: Datapad — replace Chinese text with English-style markings
    print("\n[2] Datapad — replace text with sector numbers and question marks")
    data = qwen_fix(
        prompt=(
            "Replace all text on this datapad screen with English sector "
            "labels: SEC-7, SEC-8, SEC-12 with question marks. Hand-drawn "
            "style annotations. Remove any non-English characters. Keep "
            "everything else the same — the map layout, the worn edges, "
            "the overall design."
        ),
        image_path=REFS / "datapad_maps.png",
        seed=562,
    )
    save(data, REFS / "datapad_maps.png")

    print("\nDone.")


if __name__ == "__main__":
    main()
