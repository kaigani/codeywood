#!/usr/bin/env python3
"""
Test the 3-stage compositing pipeline for shot continuity.

Stage 1: Repose neutral character → per-shot poses via qwen-edit
Stage 2: Crop/reframe locations → per-shot angles via qwen-edit
Stage 3: Compose character pose + location crop → final frame via qwen-edit

Test shots: EP01 clips 7 (TABS appears CU) and 9 (multi-tool down medium)
"""

import io
import sys
import time
from pathlib import Path

from PIL import Image
import requests

# Target frame dimensions — all final frames normalized to this
TARGET_WIDTH = 1280
TARGET_HEIGHT = 720

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
COMFYUI_BASE = "http://192.168.1.181:8100"

PROJECT = Path(__file__).resolve().parents[2] / "projects" / "stray-signal"
REFS = PROJECT / "REFERENCES"

# Source refs
KAI_NEUTRAL = REFS / "identity_sheets" / "kai-reference-01.png"
LOC_HOUSING = REFS / "location_refs" / "v2" / "loc_housing_unit.png"
LOC_CORRIDOR = REFS / "location_refs" / "v2" / "loc_corridor.png"

# Output dirs
POSES_DIR = REFS / "character_poses" / "kai"
CROPS_DIR = REFS / "location_crops" / "EP01"
FRAMES_DIR = PROJECT / "PRODUCTION" / "EP01_v02" / "frames"


def submit_and_wait(workflow_id, params, files=None, timeout=600, poll_interval=3):
    """Submit a ComfyUI workflow job, poll until done, return binary result."""
    url = f"{COMFYUI_BASE}/workflows/{workflow_id}"

    if files:
        resp = requests.post(url, data=params, files=files)
    else:
        resp = requests.post(url, data=params)
    resp.raise_for_status()
    job = resp.json()
    job_id = job["job_id"]
    print(f"  Job submitted: {job_id} (position: {job.get('position', '?')})")

    deadline = time.time() + timeout
    polls = 0
    while time.time() < deadline:
        status = requests.get(f"{COMFYUI_BASE}/jobs/{job_id}").json()
        polls += 1
        if status["status"] == "completed":
            elapsed = time.time() - (deadline - timeout)
            print(f"  Completed in {elapsed:.1f}s ({polls} polls)")
            result = requests.get(f"{COMFYUI_BASE}/jobs/{job_id}/result")
            return result.content
        if status["status"] == "error":
            raise RuntimeError(f"Job {job_id} failed: {status.get('error')}")
        interval = 2 if polls <= 5 else poll_interval
        time.sleep(interval)

    raise TimeoutError(f"Job {job_id} did not complete within {timeout}s")


def qwen_edit(prompt, image_path, image2_path=None, image3_path=None,
              seed=42, steps=4):
    """Run qwen-image-edit with 1-3 image inputs."""
    params = {"prompt": prompt, "seed": str(seed), "steps": str(steps)}

    file_handles = []
    files = {}
    try:
        fh1 = open(image_path, "rb")
        file_handles.append(fh1)
        files["image"] = (Path(image_path).name, fh1, "image/png")

        if image2_path:
            fh2 = open(image2_path, "rb")
            file_handles.append(fh2)
            files["image2"] = (Path(image2_path).name, fh2, "image/png")

        if image3_path:
            fh3 = open(image3_path, "rb")
            file_handles.append(fh3)
            files["image3"] = (Path(image3_path).name, fh3, "image/png")

        return submit_and_wait("qwen-image-edit", params, files=files)
    finally:
        for fh in file_handles:
            fh.close()


def z_image_t2i(prompt, negative_prompt="", width=1280, height=720,
                seed=42, steps=25, cfg=4):
    """Run z-image-base-t2i for location/character generation."""
    params = {
        "prompt": prompt,
        "negative_prompt": negative_prompt,
        "seed": str(seed),
        "steps": str(steps),
        "cfg": str(cfg),
        "width": str(width),
        "height": str(height),
    }
    return submit_and_wait("z-image-base-t2i", params)


def normalize_dimensions(png_bytes, target_w=None, target_h=None):
    """Resize qwen-edit output to target dimensions if they drifted."""
    if target_w is None or target_h is None:
        return png_bytes
    img = Image.open(io.BytesIO(png_bytes))
    if img.size == (target_w, target_h):
        return png_bytes
    print(f"  Normalizing {img.size[0]}x{img.size[1]} → {target_w}x{target_h}")
    img = img.resize((target_w, target_h), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def save(data, path, normalize=False):
    """Save binary data to file, optionally normalizing to target frame size."""
    if normalize:
        data = normalize_dimensions(data, TARGET_WIDTH, TARGET_HEIGHT)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as f:
        f.write(data)
    print(f"  Saved: {path}")
    return path


# ---------------------------------------------------------------------------
# Pipeline Steps
# ---------------------------------------------------------------------------

def stage1_repose_characters():
    """Repose neutral Kai into per-shot character variants."""
    print("\n" + "=" * 60)
    print("STAGE 1: Character Reposing")
    print("=" * 60)

    # Pose A: Close-up head and shoulders, looking slightly right
    # (for clip 7 — TABS appears, Kai illuminated by screen)
    print("\n[1a] Kai CU head/shoulders, looking right, neutral expression")
    data = qwen_edit(
        prompt=(
            "Show this character in a close-up shot, head and shoulders only. "
            "He is looking slightly to the right of camera. Neutral, watchful "
            "expression. Same character, same face, same skin tone, same short "
            "dark hair. Grey neutral background. Stylized animation style."
        ),
        image_path=KAI_NEUTRAL,
        seed=101,
        steps=4,
    )
    pose_cu = save(data, POSES_DIR / "kai_cu_look_right.png")

    # Pose B: Medium shot, seated, looking down, hands on desk
    # (for clip 9 — multi-tool down, decision just made)
    print("\n[1b] Kai medium, seated, looking down, contemplative")
    data = qwen_edit(
        prompt=(
            "Show this character in a medium shot from the waist up. He is "
            "seated, looking down at his hands. Contemplative expression — "
            "someone who just made a quiet decision. Wearing a simpler grey "
            "underlayer (no jacket, no tool belt). Same face, same skin tone, "
            "same short dark hair. Grey neutral background. Stylized animation."
        ),
        image_path=KAI_NEUTRAL,
        seed=102,
        steps=4,
    )
    pose_med = save(data, POSES_DIR / "kai_med_seated_contemplative.png")

    # Pose C: Wide full body, walking away from camera
    # (for clip 17 — he goes, corridor bookend)
    print("\n[1c] Kai full body, walking away from camera, back view")
    data = qwen_edit(
        prompt=(
            "Show this character from behind, walking away from the camera. "
            "Full body, back view. He is walking with purpose — weight forward, "
            "measured steps. Wearing the same maintenance coverall. He holds "
            "a small device in his right hand at his side. Grey neutral "
            "background. Stylized animation style."
        ),
        image_path=KAI_NEUTRAL,
        seed=103,
        steps=4,
    )
    pose_back = save(data, POSES_DIR / "kai_full_walking_away.png")

    return pose_cu, pose_med, pose_back


def stage2_location_crops():
    """Generate location angle variants from wide masters."""
    print("\n" + "=" * 60)
    print("STAGE 2: Location Crops / Angles")
    print("=" * 60)

    # Crop A: Housing unit — desk corner angle with amber lamp
    print("\n[2a] Housing unit — desk corner with amber desk lamp")
    data = qwen_edit(
        prompt=(
            "Show the interior of this room from a different angle — looking "
            "at a small desk in the corner. A warm amber desk lamp is the only "
            "light source, creating pools of golden warmth. Night time — window "
            "shows darkness. The desk has a salvaged charge cable and an empty "
            "plate pushed to the side. Compact, regulation-grey walls. Stylized "
            "sci-fi animation, brutalist dystopian housing unit."
        ),
        image_path=LOC_HOUSING,
        seed=201,
        steps=4,
    )
    crop_desk = save(data, CROPS_DIR / "housing_desk_amber.png", normalize=True)

    # Crop B: Corridor — vanishing point, deeper perspective
    print("\n[2b] Corridor — deep vanishing point for walk-away shot")
    data = qwen_edit(
        prompt=(
            "Show this corridor from a lower camera angle, emphasizing the "
            "deep vanishing point. Long perspective stretching into distance. "
            "4500K fluorescent strips overhead running to infinity. Polymer "
            "floor with subtle reflection. No people. Empty, clinical, cold. "
            "Stylized sci-fi animation, brutalist dystopian."
        ),
        image_path=LOC_CORRIDOR,
        seed=202,
        steps=4,
    )
    crop_corridor = save(data, CROPS_DIR / "corridor_vanishing_point.png", normalize=True)

    return crop_desk, crop_corridor


def stage3_compose_frames(pose_cu, pose_med, pose_back, crop_desk, crop_corridor):
    """Compose character poses + location crops into final frames."""
    print("\n" + "=" * 60)
    print("STAGE 3: Final Compositing")
    print("=" * 60)

    # Frame for Clip 7: Kai CU at desk, amber+cyan light, TABS on screen
    print("\n[3a] Clip 07 — Kai CU, desk, amber+cyan dual lighting")
    data = qwen_edit(
        prompt=(
            "Film still, stylized sci-fi animation. Close-up of the boy from "
            "image 2 sitting at the desk from this room. He is illuminated by "
            "dual light — warm amber from a desk lamp on his left, cool cyan "
            "from a device screen on his right. His expression is watchful, "
            "studying something on a screen in front of him. The cyan light "
            "reflects in his eyes. Nighttime interior, intimate lighting."
        ),
        image_path=crop_desk,
        image2_path=pose_cu,
        seed=301,
        steps=4,
    )
    save(data, FRAMES_DIR / "clip_07_tabs_appears_v1.png", normalize=True)

    # Frame for Clip 9: Kai medium at desk, just put multi-tool down
    print("\n[3b] Clip 09 — Kai medium at desk, contemplative, multi-tool on desk")
    data = qwen_edit(
        prompt=(
            "Film still, stylized sci-fi animation. Medium shot of the boy "
            "from image 2 seated at the desk from this room. He wears a grey "
            "underlayer. A multi-tool sits on the desk where he just placed it. "
            "A small device on the desk glows faint cyan. Warm amber desk lamp "
            "provides the main light. His expression is contemplative — someone "
            "who just made a decision he doesn't fully understand. His shoulders "
            "are slightly dropped. Nighttime interior."
        ),
        image_path=crop_desk,
        image2_path=pose_med,
        seed=302,
        steps=4,
    )
    save(data, FRAMES_DIR / "clip_09_multitool_down_v1.png", normalize=True)

    # Frame for Clip 17: Kai walking away down corridor
    print("\n[3c] Clip 17 — Kai walking away, corridor vanishing point")
    data = qwen_edit(
        prompt=(
            "Film still, stylized sci-fi animation. Wide anamorphic shot. "
            "The boy from image 2 walks away from camera down this long "
            "corridor toward the vanishing point. He is a figure receding "
            "into depth. 4500K fluorescent strips overhead. Polymer floor. "
            "A faint cyan glow from a small device in his right hand is "
            "the only warm accent. Clinical, cold, but he walks with purpose."
        ),
        image_path=crop_corridor,
        image2_path=pose_back,
        seed=303,
        steps=4,
    )
    save(data, FRAMES_DIR / "clip_17_he_goes_v1.png", normalize=True)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    # Verify refs exist
    for ref, name in [(KAI_NEUTRAL, "Kai neutral"), (LOC_HOUSING, "Housing unit"),
                      (LOC_CORRIDOR, "Corridor")]:
        if not ref.exists():
            print(f"ERROR: {name} not found at {ref}")
            sys.exit(1)

    # Check ComfyUI is up
    try:
        health = requests.get(f"{COMFYUI_BASE}/health", timeout=5).json()
        if not health.get("comfyui_reachable"):
            print("ERROR: ComfyUI not reachable")
            sys.exit(1)
        print(f"ComfyUI: OK")
    except Exception as e:
        print(f"ERROR: Cannot reach ComfyUI at {COMFYUI_BASE}: {e}")
        sys.exit(1)

    print(f"\nProject: {PROJECT.name}")
    print(f"Kai neutral ref: {KAI_NEUTRAL.name}")
    print(f"Locations: {LOC_HOUSING.name}, {LOC_CORRIDOR.name}")
    print(f"\nOutput dirs:")
    print(f"  Poses:  {POSES_DIR}")
    print(f"  Crops:  {CROPS_DIR}")
    print(f"  Frames: {FRAMES_DIR}")

    # Run pipeline
    t0 = time.time()

    pose_cu, pose_med, pose_back = stage1_repose_characters()
    crop_desk, crop_corridor = stage2_location_crops()
    stage3_compose_frames(pose_cu, pose_med, pose_back, crop_desk, crop_corridor)

    elapsed = time.time() - t0
    print(f"\n{'=' * 60}")
    print(f"DONE — 8 generations in {elapsed:.0f}s (~{elapsed/8:.0f}s avg)")
    print(f"Cost: $0.00 (local ComfyUI)")
    print(f"\nReview outputs:")
    print(f"  Character poses: {POSES_DIR}")
    print(f"  Location crops:  {CROPS_DIR}")
    print(f"  Final frames:    {FRAMES_DIR}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
