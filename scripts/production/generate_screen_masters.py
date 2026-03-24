#!/usr/bin/env python3
"""
Generate final screen content shots from a blank device screen master.

Step 1: z-image — blank device screen, no cat, native 1280x720
Step 2: qwen-edit blank screen + TABS pose ref → clip_11 (pointing)
Step 3: qwen-edit blank screen + TABS pose ref → clip_08 (settled + DELETE)
Step 4: qwen-edit blank screen, text-only → clip_14 (paw at edge)
Step 5: z-image — clip_16 (hands + datapad with sector map)

"Correct reference cat" = tabs_poses/ refs used as image2 in each edit.
"""

import io
import sys
import time
import shutil
from pathlib import Path

from PIL import Image
import requests

COMFYUI_BASE = "http://192.168.1.181:8100"
TARGET_W, TARGET_H = 1280, 720

PROJECT = Path(__file__).resolve().parents[2] / "projects" / "stray-signal"
REFS    = PROJECT / "REFERENCES"
FRAMES  = PROJECT / "PRODUCTION" / "EP01_v02" / "frames"

TABS_DIR     = REFS / "object_refs" / "tabs_poses"
TABS_SITTING = TABS_DIR / "tabs_sitting_default.png"
TABS_SETTLED = TABS_DIR / "tabs_settled_patience.png"
TABS_POINTING = TABS_DIR / "tabs_pointing.png"
TABS_PAW     = TABS_DIR / "tabs_paw_reaching.png"

KAI_HANDS_PAD = REFS / "character_poses" / "kai" / "kai_hands_datapad_pen.png"


def submit_and_wait(workflow_id, params, files=None, timeout=600, poll_interval=3):
    url = f"{COMFYUI_BASE}/workflows/{workflow_id}"
    resp = requests.post(url, data=params, files=files) if files else requests.post(url, data=params)
    resp.raise_for_status()
    job_id = resp.json()["job_id"]
    print(f"    job {job_id}")
    deadline = time.time() + timeout
    polls = 0
    while time.time() < deadline:
        s = requests.get(f"{COMFYUI_BASE}/jobs/{job_id}").json()
        polls += 1
        if s["status"] == "completed":
            print(f"    done in {time.time()-(deadline-timeout):.1f}s")
            return requests.get(f"{COMFYUI_BASE}/jobs/{job_id}/result").content
        if s["status"] == "error":
            raise RuntimeError(s.get("error"))
        time.sleep(2 if polls <= 5 else poll_interval)
    raise TimeoutError("Timed out")


def z_image(prompt, seed=42, steps=25, cfg=4):
    params = {
        "prompt": prompt,
        "negative_prompt": "hologram, 3D projection, floating, photorealistic, photograph, text, watermark",
        "seed": str(seed), "steps": str(steps), "cfg": str(cfg),
        "width": str(TARGET_W), "height": str(TARGET_H),
    }
    return submit_and_wait("z-image-base-t2i", params)


def qwen_edit(prompt, image, image2=None, seed=42, steps=4):
    params = {"prompt": prompt, "seed": str(seed), "steps": str(steps)}
    handles, files = [], {}
    try:
        fh = open(image, "rb"); handles.append(fh)
        files["image"] = (Path(image).name, fh, "image/png")
        if image2:
            fh2 = open(image2, "rb"); handles.append(fh2)
            files["image2"] = (Path(image2).name, fh2, "image/png")
        return submit_and_wait("qwen-image-edit", params, files=files)
    finally:
        for fh in handles: fh.close()


def save(data, path, label=None):
    img = Image.open(io.BytesIO(data))
    if img.size != (TARGET_W, TARGET_H):
        print(f"    resize {img.size} → {TARGET_W}x{TARGET_H}")
        img = img.resize((TARGET_W, TARGET_H), Image.LANCZOS)
        buf = io.BytesIO(); img.save(buf, "PNG"); data = buf.getvalue()
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as f: f.write(data)
    size = Image.open(io.BytesIO(data)).size
    print(f"    saved: {path.name} ({size[0]}x{size[1]})")
    return path


def header(label):
    print(f"\n{'='*60}\n{label}\n{'='*60}")


def main():
    try:
        h = requests.get(f"{COMFYUI_BASE}/health", timeout=5).json()
        if not h.get("comfyui_reachable"):
            print("ERROR: ComfyUI not reachable"); sys.exit(1)
        print("ComfyUI: OK\n")
    except Exception as e:
        print(f"ERROR: {e}"); sys.exit(1)

    t0 = time.time()

    # ── Step 1: Blank device screen master ───────────────────────────────────
    header("STEP 1 — blank device screen master (z-image, no cat)")
    blank_data = z_image(
        prompt=(
            "Stylized sci-fi animation, graphic novel rendering. "
            "POV close-up of a rugged handheld device, screen facing camera. "
            "The screen fills 85 percent of the frame and is completely blank "
            "and dark — pure black, no content, no icons, no light on screen. "
            "A single hairline crack runs across the lower portion of the "
            "screen glass — one thin line, barely visible. "
            "The device body: brushed industrial aluminum casing, thick bezel "
            "with rivet bolts at corners, two small round control buttons on "
            "the right side, ventilation ridges on the bottom edge. "
            "The device frame sits at the very edges of the image. "
            "Neutral dark background behind device. "
            "Flat 2D animation style, clean linework, no glow, no light."
        ),
        seed=5001,
    )
    blank_path = save(blank_data, FRAMES / "_screen_master_blank.png")

    # ── Step 2: clip_11 — TABS pointing ──────────────────────────────────────
    header("STEP 2 — clip_11 (TABS pointing on blank screen)")
    data = qwen_edit(
        prompt=(
            "On the blank device screen in this image, display the wireframe "
            "geometric cat from image 2. The cat is in a pointing posture — "
            "seated, body oriented forward, one front paw extended and pointing "
            "to the right. The cat is rendered in electric cyan (#00E5FF), "
            "with visible polygon facets and angular geometric planes. "
            "The cat sits on the dark screen as a flat 2D display. "
            "Add soft concentric cyan pulse rings radiating outward from the "
            "cat across the black screen surface. "
            "The device frame and hairline crack remain exactly as they are. "
            "No hologram. No 3D projection. Flat screen display only."
        ),
        image=blank_path,
        image2=TABS_POINTING,
        seed=1101,
    )
    save(data, FRAMES / "clip_11_tabs_points_northeast_final.png")

    # ── Step 3: clip_08 — TABS settled + DELETE ───────────────────────────────
    header("STEP 3 — clip_08 (TABS settled + DELETE on blank screen)")
    data = qwen_edit(
        prompt=(
            "On the blank device screen in this image, add two elements: "
            "1) The wireframe geometric cat from image 2, now in a settled "
            "patience pose — sitting in the bottom-right corner of the screen, "
            "paws tucked neatly underneath its body, looking away to the left. "
            "The cat is rendered in electric cyan, visible polygon facets. "
            "Flat 2D display on the dark screen, not a hologram. "
            "2) In the upper-left area of the screen, plain institutional text "
            "reading 'DELETE' in solid red — clean sans-serif, government UI "
            "style, no decoration, no glow, just plain red text. "
            "The device frame and hairline crack remain exactly as they are."
        ),
        image=blank_path,
        image2=TABS_SETTLED,
        seed=801,
    )
    save(data, FRAMES / "clip_08_delete_sequence_final.png")

    # ── Step 4: clip_14 — TABS paw at screen edge ─────────────────────────────
    header("STEP 4 — clip_14 (TABS paw reaching toward screen edge)")
    data = qwen_edit(
        prompt=(
            "On the blank device screen in this image, display the wireframe "
            "geometric cat from image 2, repositioned to the left edge of the "
            "screen. The cat sits near the left boundary, body turned slightly "
            "to face left. Its left front paw is gently raised and extended "
            "toward the left edge of the screen glass — a small cat paw "
            "reaching toward the screen boundary, not quite touching it. "
            "The cat looks beyond the screen edge. "
            "The cat is rendered in electric cyan, visible polygon facets, "
            "flat 2D display on the dark screen. "
            "No pulse rings. No hologram. "
            "The device frame and hairline crack remain exactly as they are. "
            "The paw is small and proportional to the cat body — not enlarged."
        ),
        image=blank_path,
        image2=TABS_SITTING,
        seed=1401,
    )
    save(data, FRAMES / "clip_14_tabs_paw_at_glass_final.png")

    # ── Step 5: clip_16 — hands + datapad with sector map ────────────────────
    header("STEP 5 — clip_16 (z-image: hands + datapad sector map)")
    data = z_image(
        prompt=(
            "Stylized sci-fi animation, graphic novel rendering, cinematic. "
            "Close-up of a teenage boy's hands holding a battered handheld "
            "datapad, writing on it with a stylus pen. "
            "The boy has light brown skin, wearing a maintenance coverall. "
            "The datapad screen shows a hand-drawn sector map: black ink grid "
            "lines on a white background dividing the surface into rectangular "
            "numbered sectors. Sector labels visible. One sector area is densely "
            "covered in handwritten question marks — this is Sector 12. "
            "The stylus pen is mid-stroke, making a new mark at Sector 12. "
            "At the lower-right edge of frame, a small rugged device with a "
            "faint cyan glow is visible clipped to the boy's arm or pocket. "
            "4500K fluorescent overhead light. Cinematic composition, "
            "slightly elevated angle looking down at the datapad. "
            "Clean animation linework."
        ),
        seed=1601,
    )
    save(data, FRAMES / "clip_16_new_mark_on_map_final.png")

    elapsed = time.time() - t0
    print(f"\n{'='*60}")
    print(f"DONE — 5 steps in {elapsed/60:.1f}m")
    print(f"\nNew finals:")
    print(f"  clip_08 → clip_08_delete_sequence_final.png")
    print(f"  clip_11 → clip_11_tabs_points_northeast_final.png")
    print(f"  clip_14 → clip_14_tabs_paw_at_glass_final.png")
    print(f"  clip_16 → clip_16_new_mark_on_map_final.png")
    print(f"  master  → _screen_master_blank.png")
    print("="*60)


if __name__ == "__main__":
    main()
