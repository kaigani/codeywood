#!/usr/bin/env python3
"""
Fix broken EP01 start frames using qwen-image-edit with TABS and device refs.

Broken clips and fix strategies:
  01 — corridor HUD overlays: edit-on-edit to remove UI elements
  04 — device ECU wrong skin/crack: compose device_off + kai_hands_holding_device
  07 — no TABS on screen: 2-stage compose (housing+kai+device → add TABS)
  08 — wrong device/TABS: compose device_on + tabs_settled_patience + DELETE UI
  09 — Kai on floor not desk: compose housing_desk_amber + kai_med_seated_contemplative
  10 — TABS as hologram: 2-stage compose (housing+kai_watching → add TABS on screen)
  11 — logo composition: compose device_on + tabs_pointing
  14 — shattered glass: 2-stage compose (device+tabs_paw → add kai_asleep behind glass)
  16 — decorative map: compose datapad_maps + kai_hands_datapad_pen

Usage:
  python3 fix_ep01_frames.py               # run all fixes
  python3 fix_ep01_frames.py --clip 7      # run one clip only
  python3 fix_ep01_frames.py --clip 7,8,11 # run multiple clips
"""

import argparse
import io
import sys
import time
from pathlib import Path

from PIL import Image
import requests

# ─── Config ───────────────────────────────────────────────────────────────────

COMFYUI_BASE = "http://192.168.1.181:8100"
TARGET_W, TARGET_H = 1280, 720

PROJECT = Path(__file__).resolve().parents[2] / "projects" / "stray-signal"
REFS = PROJECT / "REFERENCES"
FRAMES = PROJECT / "PRODUCTION" / "EP01_v02" / "frames"

# Object refs
DEVICE_OFF  = REFS / "object_refs" / "device_off.png"
DEVICE_ON   = REFS / "object_refs" / "device_on.png"
DATAPAD     = REFS / "object_refs" / "datapad_maps.png"

# TABS poses
TABS_DIR = REFS / "object_refs" / "tabs_poses"
TABS_SITTING  = TABS_DIR / "tabs_sitting_default.png"
TABS_SETTLED  = TABS_DIR / "tabs_settled_patience.png"
TABS_READING  = TABS_DIR / "tabs_reading_focused.png"
TABS_POINTING = TABS_DIR / "tabs_pointing.png"
TABS_PAW      = TABS_DIR / "tabs_paw_reaching.png"

# Kai poses
KAI_DIR = REFS / "character_poses" / "kai"
KAI_CU_RIGHT   = KAI_DIR / "kai_cu_look_right.png"
KAI_MED        = KAI_DIR / "kai_med_seated_contemplative.png"
KAI_WATCHING   = KAI_DIR / "kai_at_desk_watching.png"
KAI_ASLEEP     = KAI_DIR / "kai_asleep_at_desk.png"
KAI_HANDS_DEV  = KAI_DIR / "kai_hands_holding_device.png"
KAI_HANDS_PAD  = KAI_DIR / "kai_hands_datapad_pen.png"

# Location crops
CROPS = REFS / "location_crops" / "EP01"
CROP_DESK      = CROPS / "housing_desk_amber.png"
CROP_CORRIDOR  = CROPS / "corridor_wide_establishing.png"


# ─── ComfyUI helpers ──────────────────────────────────────────────────────────

def submit_and_wait(workflow_id, params, files=None, timeout=600, poll_interval=3):
    url = f"{COMFYUI_BASE}/workflows/{workflow_id}"
    resp = requests.post(url, data=params, files=files) if files else requests.post(url, data=params)
    resp.raise_for_status()
    job = resp.json()
    job_id = job["job_id"]
    print(f"    job {job_id} (queue pos {job.get('position', '?')})")

    deadline = time.time() + timeout
    polls = 0
    while time.time() < deadline:
        status = requests.get(f"{COMFYUI_BASE}/jobs/{job_id}").json()
        polls += 1
        if status["status"] == "completed":
            elapsed = time.time() - (deadline - timeout)
            print(f"    done in {elapsed:.1f}s")
            return requests.get(f"{COMFYUI_BASE}/jobs/{job_id}/result").content
        if status["status"] == "error":
            raise RuntimeError(f"Job {job_id} failed: {status.get('error')}")
        time.sleep(2 if polls <= 5 else poll_interval)

    raise TimeoutError(f"Job {job_id} timed out after {timeout}s")


def qwen_edit(prompt, image, image2=None, image3=None, seed=42, steps=4):
    """Run qwen-image-edit. image/image2/image3 are Path objects."""
    params = {"prompt": prompt, "seed": str(seed), "steps": str(steps)}
    handles, files = [], {}
    try:
        fh = open(image, "rb"); handles.append(fh)
        files["image"] = (Path(image).name, fh, "image/png")
        if image2:
            fh2 = open(image2, "rb"); handles.append(fh2)
            files["image2"] = (Path(image2).name, fh2, "image/png")
        if image3:
            fh3 = open(image3, "rb"); handles.append(fh3)
            files["image3"] = (Path(image3).name, fh3, "image/png")
        return submit_and_wait("qwen-image-edit", params, files=files)
    finally:
        for fh in handles:
            fh.close()


def normalize(png_bytes, w=TARGET_W, h=TARGET_H):
    img = Image.open(io.BytesIO(png_bytes))
    if img.size != (w, h):
        print(f"    resize {img.size} → {w}x{h}")
        img = img.resize((w, h), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, "PNG")
    return buf.getvalue()


def save(data, path, norm=True):
    data = normalize(data) if norm else data
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as f:
        f.write(data)
    print(f"    saved: {path.name}")
    return path


def header(n, name):
    print(f"\n{'='*60}")
    print(f"CLIP {n:02d} — {name}")
    print(f"{'='*60}")


# ─── Fix functions ────────────────────────────────────────────────────────────

def fix_01():
    """Remove floating HUD/UI overlays from corridor establishing shot."""
    header(1, "corridor_establishing — remove HUD overlays")
    data = qwen_edit(
        prompt=(
            "In this image, remove all floating holographic UI elements, "
            "cyan text overlays, and digital HUD displays from the corridor. "
            "The corridor should be completely clean — only concrete walls, "
            "4500K fluorescent strips overhead, polymer floor. No screens, "
            "no UI, no floating text anywhere. The boy walking in the distance "
            "remains exactly as he is. Keep everything else the same."
        ),
        image=FRAMES / "clip_01_corridor_establishing.png",
        seed=101,
    )
    save(data, FRAMES / "clip_01_corridor_establishing_v2.png")


def fix_04():
    """ECU device in hands — correct skin tone, hairline crack, amber glow."""
    header(4, "device_crack_warmth — device ECU with correct hands")
    data = qwen_edit(
        prompt=(
            "Extreme close-up of the device from image 1 held in a boy's "
            "hands from image 2. Light brown skin, maintenance coverall cuff "
            "visible at edges. The device has a hairline crack across the lower "
            "third of the glass — thin, precise, not shattered. A faint warm "
            "amber glow emanates from inside the device at the crack edges. "
            "A thumb rests just above the crack. 4500K overhead light on the "
            "aluminum surface. Stylized sci-fi animation, close-up."
        ),
        image=DEVICE_OFF,
        image2=KAI_HANDS_DEV,
        seed=104,
    )
    save(data, FRAMES / "clip_04_device_crack_warmth_v2.png")


def fix_07():
    """2-stage: compose Kai+desk+device → add TABS on screen."""
    header(7, "tabs_appears_screen — 2-stage (compose → add TABS)")

    print("\n  Stage 1: Compose Kai at desk with dual lighting and device")
    stage1 = qwen_edit(
        prompt=(
            "Film still, stylized sci-fi animation. Close-up of the boy from "
            "image 2 sitting at the desk from this room (image 1). He is "
            "looking at the small handheld device from image 3, which sits on "
            "the desk in front of him. The device screen glows cyan. Dual "
            "lighting: warm amber desk lamp from his left, cool cyan from the "
            "device screen on his right. His face is half gold, half cyan. "
            "Watchful expression — eyes wide, studying the screen. Nighttime."
        ),
        image=CROP_DESK,
        image2=KAI_CU_RIGHT,
        image3=DEVICE_ON,
        seed=701,
    )
    stage1_path = save(stage1, FRAMES / "clip_07_stage1.png")

    print("\n  Stage 2: Add TABS on device screen")
    data = qwen_edit(
        prompt=(
            "In this image, the boy is looking at a small handheld device on "
            "the desk. On the device screen, add the wireframe cyan cat from "
            "image 2 — sitting, studying the viewer with digital curiosity. "
            "The cat is contained within the device screen. It is the source "
            "of the cyan light on the boy's face. Minor edge shimmer on the "
            "wireframe. Keep everything else — the boy, room, amber lamp — "
            "exactly the same."
        ),
        image=stage1_path,
        image2=TABS_SITTING,
        seed=702,
    )
    save(data, FRAMES / "clip_07_tabs_appears_v3.png")


def fix_08():
    """Device screen close-up: TABS settled in corner, DELETE prompt visible."""
    header(8, "delete_sequence — device screen with TABS + DELETE UI")
    data = qwen_edit(
        prompt=(
            "Tight close-up of the device screen from image 1. On the screen: "
            "the wireframe cat from image 2 has walked to the corner of the "
            "screen and tucked its paws underneath — settled, patient, looking "
            "away deliberately. Also visible on screen: a 'DELETE' prompt in "
            "institutional red, clinical sans-serif typography — Compact "
            "government UI style, not stylized. A boy's fingers are visible "
            "at the bottom of the frame holding the device. Warm amber glow "
            "on the device frame edges from a desk lamp. Stylized sci-fi "
            "animation, screen close-up."
        ),
        image=DEVICE_ON,
        image2=TABS_SETTLED,
        seed=801,
    )
    save(data, FRAMES / "clip_08_delete_sequence_v2.png")


def fix_09():
    """Kai at desk (not floor) — compose housing desk + seated pose."""
    header(9, "multitool_down — Kai AT desk, not on floor")
    data = qwen_edit(
        prompt=(
            "Film still, stylized sci-fi animation. Medium shot. The boy from "
            "image 2 is seated at the desk in this room (image 1). He wears "
            "a grey underlayer — no coverall, no jacket. A multi-tool sits on "
            "the desk surface where he just placed it. A small device on the "
            "desk glows faint cyan in the background. Amber desk lamp is the "
            "main light source. His expression: someone who just made a "
            "decision he does not fully understand. Shoulders dropped a "
            "centimeter. One hand resting flat on the desk surface."
        ),
        image=CROP_DESK,
        image2=KAI_MED,
        seed=901,
    )
    save(data, FRAMES / "clip_09_multitool_down_v3.png")


def fix_10():
    """2-stage: Kai watching device → add TABS on device screen."""
    header(10, "tabs_reads_maps — 2-stage (Kai watching → TABS on screen)")

    print("\n  Stage 1: Compose Kai watching device at desk")
    stage1 = qwen_edit(
        prompt=(
            "Film still, stylized sci-fi animation. Medium close-up. The boy "
            "from image 2 sits at the desk in this room (image 1). He watches "
            "a small handheld device on the desk — the device screen glows "
            "cyan and shows a directory tree. His face is lit by the cyan "
            "glow. Expression: guarded but not hostile, watching carefully. "
            "Amber desk lamp behind him. One hand resting near the device, "
            "the other holding a datapad. Nighttime."
        ),
        image=CROP_DESK,
        image2=KAI_WATCHING,
        seed=1001,
    )
    stage1_path = save(stage1, FRAMES / "clip_10_stage1.png")

    print("\n  Stage 2: Add TABS on device screen navigating maps")
    data = qwen_edit(
        prompt=(
            "In this image, a boy watches a small handheld device on the desk. "
            "On the device screen, add the wireframe cat from image 2 — it is "
            "navigating through a directory of files. The cat is focused and "
            "methodical, not looking up. It is entirely contained within the "
            "small device screen. Keep the boy, his expression, the room, and "
            "the amber lamp exactly the same."
        ),
        image=stage1_path,
        image2=TABS_READING,
        seed=1002,
    )
    save(data, FRAMES / "clip_10_tabs_reads_maps_v2.png")


def fix_11():
    """Tight device screen — TABS in pointing posture with directional pulse."""
    header(11, "tabs_points_northeast — device screen, TABS pointing")
    data = qwen_edit(
        prompt=(
            "Extreme close-up of the device screen from image 1. On the "
            "screen: the wireframe cat from image 2 in a pointing posture — "
            "body oriented, weight forward, one paw extended, nose aimed "
            "north-northeast. The cat is the clear focus of the screen. "
            "Soft cyan directional pulse circles radiate from the cat "
            "outward across the screen. The screen is dark — cat and pulse "
            "are the only light on screen. Device frame barely visible at "
            "edges, brushed aluminum. Tight, intimate close-up."
        ),
        image=DEVICE_ON,
        image2=TABS_POINTING,
        seed=1101,
    )
    save(data, FRAMES / "clip_11_tabs_points_northeast_v2.png")


def fix_14():
    """2-stage: TABS paw at screen edge → add Kai sleeping behind glass."""
    header(14, "tabs_paw_at_glass — 2-stage (TABS paw → add sleeping Kai)")

    print("\n  Stage 1: TABS at screen edge, paw reaching")
    stage1 = qwen_edit(
        prompt=(
            "Close-up of the device screen from image 1. The wireframe cat "
            "from image 2 is sitting at the edge of the screen closest to the "
            "viewer, facing outward. One paw is extended toward the glass — "
            "reaching, hovering, not quite touching. The cat is watching "
            "something beyond the screen. The screen is the boundary between "
            "the digital and physical. A hairline crack is visible at the "
            "lower edge of the screen glass — thin, precise, not shattered. "
            "Dark background beyond the screen. Cyan glow from the cat."
        ),
        image=DEVICE_ON,
        image2=TABS_PAW,
        seed=1401,
    )
    stage1_path = save(stage1, FRAMES / "clip_14_stage1.png")

    print("\n  Stage 2: Add Kai sleeping behind the screen glass")
    data = qwen_edit(
        prompt=(
            "In this image, the wireframe cat is at the edge of a device "
            "screen with its paw reaching toward the glass. Beyond the device "
            "screen glass, out of focus in the background: add the sleeping "
            "boy from image 2 — head resting on his arms on a desk, face soft "
            "and relaxed, illuminated by the cyan glow of the device screen. "
            "The glass boundary between cat and sleeping boy is the emotional "
            "center of the frame. Keep the cat, the paw, and the screen "
            "exactly as they are."
        ),
        image=stage1_path,
        image2=KAI_ASLEEP,
        seed=1402,
    )
    save(data, FRAMES / "clip_14_tabs_paw_at_glass_v2.png")


def fix_16():
    """Close-up of hands on utilitarian sector map, pen poised at Sector 12."""
    header(16, "new_mark_on_map — utilitarian sector map, pen on gap")
    data = qwen_edit(
        prompt=(
            "Close-up of the hands from image 2 holding the battered datapad "
            "from image 1. The datapad shows a hand-drawn sector map — "
            "utilitarian grid lines, systematic annotations, question marks "
            "clustered at Sector 12. A pen is poised over Sector 12, about "
            "to make a new mark. A small device is tucked under the arm with "
            "a faint cyan glow at the edge of frame. 4500K corridor fluorescent "
            "light on the hands. The map is functional and obsessive — not "
            "decorative. Stylized sci-fi animation, close-up of hands."
        ),
        image=DATAPAD,
        image2=KAI_HANDS_PAD,
        seed=1601,
    )
    save(data, FRAMES / "clip_16_new_mark_on_map_v2.png")


# ─── Main ─────────────────────────────────────────────────────────────────────

ALL_FIXES = {
    1:  fix_01,
    4:  fix_04,
    7:  fix_07,
    8:  fix_08,
    9:  fix_09,
    10: fix_10,
    11: fix_11,
    14: fix_14,
    16: fix_16,
}


def check_refs():
    required = [
        DEVICE_OFF, DEVICE_ON, DATAPAD,
        TABS_SITTING, TABS_SETTLED, TABS_READING, TABS_POINTING, TABS_PAW,
        KAI_CU_RIGHT, KAI_MED, KAI_WATCHING, KAI_ASLEEP, KAI_HANDS_DEV, KAI_HANDS_PAD,
        CROP_DESK, CROP_CORRIDOR,
    ]
    missing = [p for p in required if not p.exists()]
    if missing:
        print("ERROR: Missing refs:")
        for p in missing:
            print(f"  {p}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--clip", help="Comma-separated clip numbers to fix (e.g. 7,8,11)")
    args = parser.parse_args()

    # Health check
    try:
        h = requests.get(f"{COMFYUI_BASE}/health", timeout=5).json()
        if not h.get("comfyui_reachable"):
            print("ERROR: ComfyUI not reachable")
            sys.exit(1)
        print(f"ComfyUI: OK")
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)

    check_refs()

    # Determine which clips to fix
    if args.clip:
        targets = [int(x.strip()) for x in args.clip.split(",")]
        invalid = [n for n in targets if n not in ALL_FIXES]
        if invalid:
            print(f"ERROR: No fix defined for clip(s): {invalid}")
            sys.exit(1)
    else:
        targets = sorted(ALL_FIXES.keys())

    print(f"\nFixing clips: {targets}")
    print(f"Output: {FRAMES}")

    t0 = time.time()
    results = {}

    for clip_num in targets:
        try:
            ALL_FIXES[clip_num]()
            results[clip_num] = "OK"
        except Exception as e:
            print(f"\nERROR on clip {clip_num}: {e}")
            results[clip_num] = f"FAILED: {e}"

    elapsed = time.time() - t0
    print(f"\n{'='*60}")
    print(f"DONE — {len(targets)} clips in {elapsed/60:.1f}m")
    for n in targets:
        print(f"  clip {n:02d}: {results.get(n, 'SKIPPED')}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
