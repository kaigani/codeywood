#!/usr/bin/env python3
"""
Generate isolated object references for consistent prop rendering.

Objects are generated on neutral backgrounds via qwen-edit from existing
hero shots / frames that contain them. These refs are used as VISUAL ANCHORS
for prompt writing and edit-on-edit fixes — NOT as additional qwen-edit
image slots (keep compositing to max 2 refs: location + character).

EP01 key objects:
- The Device (brushed aluminum, hairline crack, glass screen)
- Multi-tool (maintenance tool)
- Datapad (battered, hand-drawn maps)
- TABS on screen (wireframe cyan cat, different poses)
"""

import io
import sys
import time
from pathlib import Path

from PIL import Image
import requests

COMFYUI_BASE = "http://192.168.1.181:8100"
PROJECT = Path(__file__).resolve().parents[2] / "projects" / "stray-signal"
REFS = PROJECT / "REFERENCES"
OBJECTS_DIR = REFS / "object_refs"


def submit_and_wait(workflow_id, params, files=None, timeout=600):
    url = f"{COMFYUI_BASE}/workflows/{workflow_id}"
    if files:
        resp = requests.post(url, data=params, files=files)
    else:
        resp = requests.post(url, data=params)
    resp.raise_for_status()
    job = resp.json()
    job_id = job["job_id"]
    print(f"  Job: {job_id}")

    deadline = time.time() + timeout
    while time.time() < deadline:
        status = requests.get(f"{COMFYUI_BASE}/jobs/{job_id}").json()
        if status["status"] == "completed":
            elapsed = time.time() - (deadline - timeout)
            print(f"  Done in {elapsed:.1f}s")
            return requests.get(f"{COMFYUI_BASE}/jobs/{job_id}/result").content
        if status["status"] == "error":
            raise RuntimeError(f"Job {job_id} failed: {status.get('error')}")
        time.sleep(2)
    raise TimeoutError("Timeout")


def qwen_edit(prompt, image_path, seed=42, steps=4):
    params = {"prompt": prompt, "seed": str(seed), "steps": str(steps)}
    with open(image_path, "rb") as fh:
        files = {"image": (Path(image_path).name, fh, "image/png")}
        return submit_and_wait("qwen-image-edit", params, files=files)


def z_image(prompt, negative_prompt="", width=1024, height=1024, seed=42):
    return submit_and_wait("z-image-base-t2i", {
        "prompt": prompt,
        "negative_prompt": negative_prompt,
        "seed": str(seed), "steps": "25", "cfg": "4",
        "width": str(width), "height": str(height),
    })


def save(data, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as f:
        f.write(data)
    print(f"  Saved: {path}")
    return path


def main():
    OBJECTS_DIR.mkdir(parents=True, exist_ok=True)

    # Source: Kai hero shot that shows the device
    kai_device = REFS / "hero_shots" / "v2" / "kai_device.png"
    kai_neutral = REFS / "identity_sheets" / "kai-reference-01.png"

    t0 = time.time()

    # -----------------------------------------------------------------------
    # 1. THE DEVICE — brushed aluminum, hairline crack, glass screen
    # -----------------------------------------------------------------------
    print("\n[1] The Device — isolated on neutral background")
    # Use z-image for a clean object ref since we want precise control
    data = z_image(
        prompt=(
            "Stylized sci-fi animation, product shot on neutral grey background. "
            "A small handheld device, about the size of a large phone. Brushed "
            "aluminum body with micro-ridged surface texture. Real glass screen, "
            "dark/off. A hairline crack runs across the lower third of the glass. "
            "The device looks old but well-made — real materials, no plastic. "
            "Centered in frame, slightly angled. Clean studio lighting."
        ),
        negative_prompt="people, hands, characters, blurry, text, watermark",
        width=1024, height=1024, seed=501,
    )
    save(data, OBJECTS_DIR / "device_off.png")

    # Device with TABS on screen (cyan glow)
    print("\n[2] The Device — screen on, TABS visible, cyan glow")
    data = z_image(
        prompt=(
            "Stylized sci-fi animation, product shot on neutral grey background. "
            "A small handheld device, brushed aluminum with micro-ridged surface. "
            "The glass screen is ON, glowing with electric cyan light (#00E5FF). "
            "On the screen: a small wireframe cat shape, simple geometry, angular "
            "joints, ears slightly too large. The cyan glow illuminates the "
            "aluminum body. Hairline crack across lower third of glass. "
            "Centered in frame, clean studio lighting."
        ),
        negative_prompt="people, hands, characters, blurry, text, realistic photo",
        width=1024, height=1024, seed=502,
    )
    save(data, OBJECTS_DIR / "device_tabs_on.png")

    # -----------------------------------------------------------------------
    # 2. MULTI-TOOL — maintenance tool
    # -----------------------------------------------------------------------
    print("\n[3] Multi-tool — isolated on neutral background")
    data = z_image(
        prompt=(
            "Stylized sci-fi animation, product shot on neutral grey background. "
            "A maintenance multi-tool — a compact hand tool with multiple folding "
            "implements. Worn metal handle, matte grey with orange accent marks. "
            "The tool of a maintenance worker. Utilitarian, not fancy. "
            "Centered in frame, clean studio lighting."
        ),
        negative_prompt="people, hands, characters, blurry, text, watermark",
        width=1024, height=1024, seed=503,
    )
    save(data, OBJECTS_DIR / "multi_tool.png")

    # -----------------------------------------------------------------------
    # 3. DATAPAD — battered, hand-drawn maps
    # -----------------------------------------------------------------------
    print("\n[4] Datapad — battered with hand-drawn maps")
    data = z_image(
        prompt=(
            "Stylized sci-fi animation, product shot on neutral grey background. "
            "A battered datapad — a worn tablet-like device with a scratched screen "
            "showing hand-drawn sector maps. Obsessive notation in small handwriting, "
            "question marks scattered across one section. The maps are hand-drawn "
            "over a digital grid — analog markings on a digital surface. "
            "Worn edges, scratched back. A maintenance worker's personal tool. "
            "Centered in frame, clean studio lighting."
        ),
        negative_prompt="people, hands, characters, blurry, watermark, realistic",
        width=1024, height=1024, seed=504,
    )
    save(data, OBJECTS_DIR / "datapad_maps.png")

    # -----------------------------------------------------------------------
    # 4. TABS — wireframe cat in different poses (for screen compositing)
    # -----------------------------------------------------------------------
    print("\n[5] TABS — sitting, studying viewer")
    data = z_image(
        prompt=(
            "Stylized sci-fi animation on pure black background. A wireframe "
            "digital cat rendered in electric cyan (#00E5FF). Low-resolution, "
            "visible geometry, angular joints, ears slightly too large for its "
            "head. The cat is sitting upright, studying the viewer with digital "
            "curiosity. Minor edge shimmer on the wireframe lines. Simple, "
            "geometric, like a low-poly hologram. Pure black background."
        ),
        negative_prompt="realistic cat, fur, photorealistic, blurry, grey background",
        width=1024, height=1024, seed=505,
    )
    save(data, OBJECTS_DIR / "tabs_sitting.png")

    print("\n[6] TABS — pointing posture, weight forward")
    data = z_image(
        prompt=(
            "Stylized sci-fi animation on pure black background. A wireframe "
            "digital cat in electric cyan (#00E5FF). Low-resolution, visible "
            "geometry, angular joints. The cat is in a pointing posture — body "
            "oriented to the right, weight forward, nose aimed forward like "
            "it has spotted something. Alert, focused. Soft cyan glow around "
            "the wireframe. Pure black background."
        ),
        negative_prompt="realistic cat, fur, photorealistic, blurry, grey background",
        width=1024, height=1024, seed=506,
    )
    save(data, OBJECTS_DIR / "tabs_pointing.png")

    print("\n[7] TABS — paw extended at glass boundary")
    data = z_image(
        prompt=(
            "Stylized sci-fi animation on pure black background. A wireframe "
            "digital cat in electric cyan (#00E5FF). Low-resolution, angular "
            "geometry. The cat sits at the edge of the frame, one paw extended "
            "forward — reaching toward the viewer but not quite touching. "
            "A gesture of tenderness from a digital creature. Minor edge "
            "shimmer. Pure black background."
        ),
        negative_prompt="realistic cat, fur, photorealistic, blurry, grey background",
        width=1024, height=1024, seed=507,
    )
    save(data, OBJECTS_DIR / "tabs_paw_reaching.png")

    elapsed = time.time() - t0
    print(f"\n{'=' * 60}")
    print(f"7 object refs in {elapsed:.0f}s")
    print(f"Cost: $0.00")
    print(f"Output: {OBJECTS_DIR}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
