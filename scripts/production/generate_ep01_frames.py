#!/usr/bin/env python3
"""
EP01 v02 — Full frame generation using 3-stage compositing pipeline.

Stage 1: Generate missing Kai poses from neutral ref
Stage 2: Generate missing location crops from wide masters
Stage 3: Compose all frames (character pose + location crop + prompt)
Stage 4: Normalize all outputs to 1280x720

Clips 5 (title card) = ffmpeg, skipped here.
Clips 7, 9, 17 = already done (v2), skipped here.
"""

import io
import sys
import time
from pathlib import Path

from PIL import Image
import requests

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
COMFYUI_BASE = "http://192.168.1.181:8100"
TARGET_W, TARGET_H = 1280, 720

PROJECT = Path(__file__).resolve().parents[2] / "projects" / "stray-signal"
REFS = PROJECT / "REFERENCES"
FRAMES_DIR = PROJECT / "PRODUCTION" / "EP01_v02" / "frames"

# Source refs
KAI_NEUTRAL = REFS / "identity_sheets" / "kai-reference-01.png"
LOC_CORRIDOR = REFS / "location_refs" / "v2" / "loc_corridor.png"
LOC_HOUSING = REFS / "location_refs" / "v2" / "loc_housing_unit.png"
LOC_MAINTENANCE = REFS / "location_refs" / "v2" / "loc_maintenance_sector.png"

# Existing character poses
KAI_POSES = REFS / "character_poses" / "kai"
# Existing location crops
LOC_CROPS = REFS / "location_crops" / "EP01"
# TABS poses
TABS_POSES = REFS / "object_refs" / "tabs_poses"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
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


def qwen_edit(prompt, image_path, image2_path=None, seed=42, steps=4):
    params = {"prompt": prompt, "seed": str(seed), "steps": str(steps)}
    fhs = []
    files = {}
    try:
        fh1 = open(image_path, "rb")
        fhs.append(fh1)
        files["image"] = (Path(image_path).name, fh1, "image/png")
        if image2_path:
            fh2 = open(image2_path, "rb")
            fhs.append(fh2)
            files["image2"] = (Path(image2_path).name, fh2, "image/png")
        return submit_and_wait("qwen-image-edit", params, files=files)
    finally:
        for fh in fhs:
            fh.close()


def normalize(png_bytes):
    img = Image.open(io.BytesIO(png_bytes))
    if img.size != (TARGET_W, TARGET_H):
        img = img.resize((TARGET_W, TARGET_H), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def save(data, path, norm=False):
    if norm:
        data = normalize(data)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as f:
        f.write(data)
    size = Image.open(io.BytesIO(data)).size
    print(f"    Saved: {path.name} ({size[0]}x{size[1]})")
    return path


# ---------------------------------------------------------------------------
# Stage 1: Missing Kai poses
# ---------------------------------------------------------------------------
def stage1_kai_poses():
    print("\n" + "=" * 70)
    print("STAGE 1: Kai Poses")
    print("=" * 70)

    poses = {}

    # Reuse existing
    poses["cu_look_right"] = KAI_POSES / "kai_cu_look_right.png"
    poses["med_seated"] = KAI_POSES / "kai_med_seated_contemplative.png"
    poses["full_walking_away"] = KAI_POSES / "kai_full_walking_away.png"

    ANCHOR = (
        "Same character, same face, same skin tone, same short dark hair. "
        "Grey neutral background. Stylized animation style."
    )

    new_poses = [
        # Clip 1: full body walking toward camera, coverall
        ("full_walking_toward", (
            f"Show this character walking toward the camera, full body. "
            f"Maintenance coverall, carrying a battered datapad in left hand. "
            f"Measured steps, head slightly tilted up. {ANCHOR}"
        ), 1001),
        # Clip 2: hands on wall close-up
        ("hands_on_wall", (
            f"Show this character's hands against a flat surface — close-up of "
            f"hands and forearms only. Light brown fingers exploring a seam. "
            f"Maintenance coverall sleeves visible. {ANCHOR}"
        ), 1002),
        # Clip 3: sitting cross-legged, multi-tool in hand
        ("sitting_crosslegged_tool", (
            f"Show this character sitting cross-legged on the ground, medium shot. "
            f"He holds a multi-tool in his right hand. A datapad sits on the floor "
            f"beside him. Maintenance coverall. Focused expression. {ANCHOR}"
        ), 1003),
        # Clip 4: hands holding device ECU
        ("hands_holding_device", (
            f"Show this character's hands holding a small device — extreme close-up "
            f"of hands only. Light brown fingers, maintenance coverall cuff. The "
            f"thumb is near the lower part of the device. {ANCHOR}"
        ), 1004),
        # Clip 6: at desk, watching, coverall removed
        ("at_desk_watching", (
            f"Show this character in a medium shot, seated at a desk. He wears "
            f"a simpler grey underlayer — no jacket, no tool belt. Hands on desk "
            f"edge. Watchful, still expression. {ANCHOR}"
        ), 1006),
        # Clip 8: same as 6/9 area — reuse med_seated for Kai fingers at bottom
        # Clip 10: at desk, turning away from device
        ("at_desk_turning_away", (
            f"Show this character in a medium shot, seated, turning to look at "
            f"something to his right. He holds a datapad. Grey underlayer, no "
            f"jacket. Expression shifting from guarded to neutral. {ANCHOR}"
        ), 1010),
        # Clip 12: CU face, recognition
        ("cu_face_recognition", (
            f"Show this character in a close-up, head and shoulders. He looks "
            f"down slightly with an expression of quiet recognition — not wonder, "
            f"not excitement. Someone seeing something they suspected confirmed. "
            f"Grey underlayer collar visible. {ANCHOR}"
        ), 1012),
        # Clip 13: asleep at desk
        ("asleep_at_desk", (
            f"Show this character asleep, head resting on his arms on a surface. "
            f"Medium shot. Grey underlayer. Face relaxed, eyes closed. One hand "
            f"loosely holding a small object. {ANCHOR}"
        ), 1013),
        # Clip 15: standing in corridor, coverall, map + device
        ("standing_corridor_ready", (
            f"Show this character standing, full body. Maintenance coverall on. "
            f"He holds a datapad in one hand and a small device in the other. "
            f"Posture slightly forward, weight on front foot. {ANCHOR}"
        ), 1015),
        # Clip 16: hands with datapad and pen CU
        ("hands_datapad_pen", (
            f"Show this character's hands holding a tablet-like datapad — close-up "
            f"of hands only. Right hand holds an uncapped pen poised over the "
            f"screen. Light brown fingers, maintenance coverall cuff. {ANCHOR}"
        ), 1016),
    ]

    for name, prompt, seed in new_poses:
        path = KAI_POSES / f"kai_{name}.png"
        if path.exists():
            print(f"\n  [skip] kai_{name} — exists")
            poses[name] = path
            continue
        print(f"\n  [gen] kai_{name}")
        data = qwen_edit(prompt, KAI_NEUTRAL, seed=seed)
        save(data, path)
        poses[name] = path

    return poses


# ---------------------------------------------------------------------------
# Stage 2: Missing location crops
# ---------------------------------------------------------------------------
def stage2_location_crops():
    print("\n" + "=" * 70)
    print("STAGE 2: Location Crops")
    print("=" * 70)

    crops = {}

    # Reuse existing
    crops["housing_desk_amber"] = LOC_CROPS / "housing_desk_amber.png"
    crops["corridor_vanishing"] = LOC_CROPS / "corridor_vanishing_point.png"

    new_crops = [
        # Corridor establishing — same wide but slightly different framing
        ("corridor_wide_establishing", LOC_CORRIDOR, (
            "This same corridor viewed from a wide establishing angle. "
            "Long vanishing-point perspective, 4500K fluorescent strips overhead, "
            "polymer floor with reflection. Empty, clinical, cold. No people. "
            "Stylized sci-fi animation, brutalist dystopian."
        ), 2001),
        # Corridor wall detail — closer to wall seam area
        ("corridor_wall_detail", LOC_MAINTENANCE, (
            "A close view of a concrete wall in this corridor. Focus on wall "
            "panels and seams where panels meet polymer. One panel is slightly "
            "off-color from surrounding material. 4500K overhead light. "
            "No people. Stylized sci-fi animation."
        ), 2002),
        # Housing unit dark — nighttime, only window light
        ("housing_dark_night", LOC_HOUSING, (
            "This same room at night with all lights off. Very dark. Only faint "
            "blue-grey light from the window. Deep shadows. The desk and bed "
            "are barely visible outlines. Darkest possible version of this room. "
            "No people. Stylized sci-fi animation."
        ), 2013),
    ]

    for name, source, prompt, seed in new_crops:
        path = LOC_CROPS / f"{name}.png"
        if path.exists():
            print(f"\n  [skip] {name} — exists")
            crops[name] = path
            continue
        print(f"\n  [gen] {name}")
        data = qwen_edit(prompt, source, seed=seed)
        save(data, path, norm=True)
        crops[name] = path

    return crops


# ---------------------------------------------------------------------------
# Stage 3: Compose all frames
# ---------------------------------------------------------------------------
def stage3_compose(poses, crops):
    print("\n" + "=" * 70)
    print("STAGE 3: Frame Compositing")
    print("=" * 70)

    # Define all 17 clips
    clips = [
        # --- COLD OPEN ---
        {
            "id": 1, "name": "corridor_establishing",
            "location": crops["corridor_wide_establishing"],
            "character": poses["full_walking_toward"],
            "prompt": (
                "Film still, stylized sci-fi animation. Wide anamorphic shot of a "
                "brutalist maintenance corridor. The boy from image 2 walks toward "
                "camera far down the corridor — a small figure. 4500K fluorescent "
                "strips overhead, polymer floor. Clinical, cold, institutional. "
                "He counts overhead strips as he walks."
            ),
            "seed": 3001,
        },
        {
            "id": 2, "name": "wall_seam_discovery",
            "location": crops["corridor_wall_detail"],
            "character": poses["hands_on_wall"],
            "prompt": (
                "Film still, stylized sci-fi animation. Close-up of the hands from "
                "image 2 against a concrete wall in this corridor. Fingertips "
                "exploring a wall seam where a panel meets surrounding polymer. "
                "The panel is slightly off-color. 4500K overhead light. Maintenance "
                "coverall sleeve visible."
            ),
            "seed": 3002,
        },
        {
            "id": 3, "name": "panel_opens_device",
            "location": crops["corridor_wall_detail"],
            "character": poses["sitting_crosslegged_tool"],
            "prompt": (
                "Film still, stylized sci-fi animation. Medium shot. The boy from "
                "image 2 sits cross-legged on the corridor floor in front of a wall "
                "panel that has swung open, revealing a dark alcove. He holds a "
                "multi-tool. Inside the alcove: a small brushed aluminum device. "
                "4500K overhead light. Maintenance coverall."
            ),
            "seed": 3003,
        },
        {
            "id": 4, "name": "device_crack_warmth",
            "location": None,  # ECU — character ref only
            "character": poses["hands_holding_device"],
            "prompt": (
                "Film still, stylized sci-fi animation. Extreme close-up of the "
                "hands from this image holding a small brushed aluminum device with "
                "a glass screen. A hairline crack runs across the lower third. "
                "The thumb rests above the crack. A faint warm amber glow emanates "
                "from inside at the crack edges. 4500K overhead light on aluminum."
            ),
            "seed": 3004,
        },
        # Clip 5 = title card (ffmpeg)
        None,
        # --- ACT ONE ---
        {
            "id": 6, "name": "housing_unit_desk",
            "location": crops["housing_desk_amber"],
            "character": poses["at_desk_watching"],
            "prompt": (
                "Film still, stylized sci-fi animation. Medium shot. The boy from "
                "image 2 sits at the desk in this room. He wears a grey underlayer. "
                "A small brushed aluminum device on the desk is connected to a "
                "charge cable with a green LED. The device screen lights up with "
                "cyan glow. Warm amber desk lamp mixes with cyan — a new color. "
                "Night through the window."
            ),
            "seed": 3006,
        },
        # Clip 7 = DONE (v2)
        None,
        {
            "id": 8, "name": "delete_sequence",
            "location": crops["housing_desk_amber"],
            "character": None,  # Screen close-up, TABS is the subject
            "prompt": (
                "Film still, stylized sci-fi animation. Tight close-up of a device "
                "screen on a desk. The screen shows a red DELETE prompt in clinical "
                "UI typography. A small glowing cyan geometric cat sits on the screen "
                "looking at the DELETE text. The cat has angular facets and diamond "
                "eyes. Amber desk lamp glow on device edges. Boy's fingers visible "
                "at bottom of frame."
            ),
            "seed": 3008,
        },
        # Clip 9 = DONE (v2)
        None,
        # --- ACT TWO ---
        {
            "id": 10, "name": "tabs_reads_maps",
            "location": crops["housing_desk_amber"],
            "character": poses["at_desk_turning_away"],
            "prompt": (
                "Film still, stylized sci-fi animation. Close-up pulling slightly "
                "wide to include both a device screen and the boy from image 2. "
                "The device screen shows a directory tree. A small glowing cyan "
                "geometric cat navigates through files. The boy watches, face lit "
                "by cyan, then turns to his own datapad. Amber desk lamp, night."
            ),
            "seed": 3010,
        },
        {
            "id": 11, "name": "tabs_points_northeast",
            "location": crops["housing_desk_amber"],
            "character": None,  # Screen close-up
            "prompt": (
                "Film still, stylized sci-fi animation. Tight close-up of a device "
                "screen. A glowing cyan geometric cat in a pointing posture — body "
                "oriented to the right, weight forward, alert. Soft cyan directional "
                "pulse radiating outward. Brushed aluminum device edges visible. "
                "Warm amber light on the edges. Dark background."
            ),
            "seed": 3011,
        },
        {
            "id": 12, "name": "thats_my_gap",
            "location": crops["housing_desk_amber"],
            "character": poses["cu_face_recognition"],
            "prompt": (
                "Film still, stylized sci-fi animation. Close-up of the boy from "
                "image 2. His face is illuminated by mixed amber and cyan light — "
                "warm gold on the left, cool cyan on the right. Expression of quiet "
                "recognition. He looks down slightly. A small device in his hands "
                "at the bottom of frame casts cyan glow reflected in his eyes. "
                "Housing unit wall behind."
            ),
            "seed": 3012,
        },
        # --- ACT THREE ---
        {
            "id": 13, "name": "kai_sleeps_device_dark",
            "location": crops["housing_dark_night"],
            "character": poses["asleep_at_desk"],
            "prompt": (
                "Film still, stylized sci-fi animation. Medium shot. The boy from "
                "image 2 is asleep at a desk, head on his arms. A small device sits "
                "dark in his hand, screen off. The room is nearly black — only faint "
                "blue-grey light from the window. Deep shadows. The darkest frame."
            ),
            "seed": 3013,
        },
        {
            "id": 14, "name": "tabs_paw_at_glass",
            "location": crops["housing_dark_night"],
            "character": None,  # TABS screen close-up
            "prompt": (
                "Film still, stylized sci-fi animation. Close-up of a device screen "
                "glowing in darkness. A glowing cyan geometric cat sits at the edge "
                "of the screen, looking outward. One angular paw extended toward "
                "the glass — reaching gently but not touching. Beyond the screen, "
                "out of focus: a sleeping boy's face lit by cyan. The glass is the "
                "boundary. Hairline crack visible."
            ),
            "seed": 3014,
        },
        {
            "id": 15, "name": "morning_corridor_return",
            "location": crops["corridor_wide_establishing"],
            "character": poses["standing_corridor_ready"],
            "prompt": (
                "Film still, stylized sci-fi animation. Wide anamorphic shot. Same "
                "corridor as the opening. The boy from image 2 stands closer to "
                "camera. Coverall on. Map in one hand, small device with faint cyan "
                "glow in the other. A glowing cyan cat on the device screen is "
                "oriented forward. His posture is fractionally more open than before, "
                "weight slightly forward. 4500K fluorescents."
            ),
            "seed": 3015,
        },
        {
            "id": 16, "name": "new_mark_on_map",
            "location": crops["corridor_wide_establishing"],
            "character": poses["hands_datapad_pen"],
            "prompt": (
                "Film still, stylized sci-fi animation. Close-up of the hands from "
                "image 2 holding a battered datapad with a hand-drawn sector map. "
                "An uncapped pen poised over the map at an unmapped section. A small "
                "device tucked under arm with faint cyan glow. 4500K corridor light."
            ),
            "seed": 3016,
        },
        # Clip 17 = DONE (v2)
        None,
    ]

    for clip in clips:
        if clip is None:
            continue

        out = FRAMES_DIR / f"clip_{clip['id']:02d}_{clip['name']}.png"
        if out.exists():
            print(f"\n  [skip] clip {clip['id']:02d} — exists")
            continue

        print(f"\n  [clip {clip['id']:02d}] {clip['name']}")

        loc = clip["location"]
        char = clip["character"]

        if loc and char:
            # Standard compose: location + character
            data = qwen_edit(clip["prompt"], loc, image2_path=char, seed=clip["seed"])
        elif loc and not char:
            # Screen close-up: location ref sets aspect, no character ref
            data = qwen_edit(clip["prompt"], loc, seed=clip["seed"])
        elif char and not loc:
            # ECU / hands only: character ref is primary
            data = qwen_edit(clip["prompt"], char, seed=clip["seed"])
        else:
            print("    ERROR: No refs for this clip")
            continue

        save(data, out, norm=True)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    # Verify core refs
    for ref, name in [
        (KAI_NEUTRAL, "Kai neutral"),
        (LOC_CORRIDOR, "Corridor"),
        (LOC_HOUSING, "Housing unit"),
        (LOC_MAINTENANCE, "Maintenance sector"),
    ]:
        if not ref.exists():
            print(f"ERROR: {name} not found: {ref}")
            sys.exit(1)

    try:
        health = requests.get(f"{COMFYUI_BASE}/health", timeout=5).json()
        if not health.get("comfyui_reachable"):
            print("ERROR: ComfyUI not reachable")
            sys.exit(1)
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)

    print("ComfyUI: OK")
    print(f"Project: stray-signal EP01 v02")
    print(f"Target: {TARGET_W}x{TARGET_H}")

    t0 = time.time()

    poses = stage1_kai_poses()
    crops = stage2_location_crops()
    stage3_compose(poses, crops)

    elapsed = time.time() - t0
    print(f"\n{'=' * 70}")
    print(f"EP01 COMPLETE — {elapsed:.0f}s total ({elapsed/60:.1f} min)")
    print(f"Cost: $0.00 (local ComfyUI)")
    print(f"Frames: {FRAMES_DIR}")
    print(f"{'=' * 70}")


if __name__ == "__main__":
    main()
