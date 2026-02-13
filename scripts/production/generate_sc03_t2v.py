#!/usr/bin/env python3
"""
Generate LTX-2 text-to-video clips for SC03 — Storage Room.
T2V pipeline — no start frames needed.

Mars and Jonah's first real conversation in a naval storage room.
She learns he can only speak truth. She escapes through the window,
leaving him behind.

Consolidated from 25 shots to 9 clips per dialogue-scene heuristic.
"""

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import requests

# ─── Config ───────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).parent.parent.parent / "projects" / "pirate-romance"
SCENE_DIR = PROJECT_ROOT / "PRODUCTION" / "EP01" / "sc03"
OUTPUT_DIR = SCENE_DIR / "t2v_draft"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

COMFYUI_URL = "http://192.168.1.181:8100"
WORKFLOW = "ltx2-t2v"
FPS = 25
TIMEOUT = 900

NEGATIVE_PROMPT = (
    "blur, distort, low quality, cartoon, anime, deformed, extra limbs, "
    "text, watermark, modern clothing, contemporary architecture"
)

# Character physical descriptions — must appear in every shot they're visible
MARS_DESC = (
    "young woman of mixed Caribbean heritage, 16 years old, lean athletic build, "
    "thick dark curly hair tied back, sun-darkened olive skin, visible freckles "
    "across nose and cheekbones, ink-stained hands, wearing worn leather vest "
    "over linen shirt, trousers, leather map case at hip, 18th century clothing"
)

JONAH_DESC = (
    "young man, 17 years old, tall and broad-shouldered, olive skin, cropped dark hair, "
    "faint scarring at his throat like old burns, heavy-lidded patient eyes, wearing "
    "simple worn linen shirt and dark trousers, 18th century clothing"
)

# Setting anchor — must appear in every shot
SETTING = (
    "cluttered naval storage room interior at night, 18th century Caribbean colonial compound. "
    "Wooden crates stacked high, coiled rope, naval supplies. A single small window high "
    "on the far wall, wrong-blue moonlight streaming through, dust motes in the light beam"
)

# ─── T2V Shot Definitions ────────────────────────────────────────────

SHOTS = [
    {
        "id": 1,
        "name": "Entrance and the Ledger",
        "duration": 8,
        "prompt": (
            "Cinematic medium shot, " + SETTING + ". "
            + MARS_DESC + " bursts through a heavy wooden door, slams it behind her, "
            "presses her back flat against the wood. She is gasping for breath, chest heaving, "
            "wild eyes scanning the room. She clutches an ancient leather-bound book tight to "
            "her chest with both hands. The book has an unsettling smooth quality, faint "
            "wrong-blue glow pulsing from within its pages. She looks down at it and hisses: "
            "\"What are you?\" She opens the book tentatively, her face illuminated from below "
            "by wrong-blue glow from the pages. Door slam echo, ragged breathing, heartbeat. "
            "Camera static, wrong-blue moonlight from the high window."
        ),
    },
    {
        "id": 2,
        "name": "Ledger Recoils",
        "duration": 8,
        "prompt": (
            "Cinematic close-up, " + MARS_DESC + " stares down at an open ancient book. "
            "Wrong-blue glow illuminates her face from below. Her expression shifts from "
            "curiosity to shock to disgust as she reads something on the pages. "
            "She slams the book shut against her chest, jaw clenched, eyes bright with "
            "fury and violation. " + SETTING + ". "
            "She whispers through gritted teeth: \"That's not— How does it know?\" "
            "The look of someone who has been exposed against their will. "
            "Supernatural hum from the book, abrupt silence when it closes. "
            "Camera slow push in on her face. Wrong-blue moonlight on one side."
        ),
    },
    {
        "id": 3,
        "name": "Jonah Revealed",
        "duration": 10,
        "prompt": (
            "Cinematic medium-wide two-shot, " + SETTING + ". "
            + MARS_DESC + " spins defensively toward the shadows, hearing a noise. "
            "Her hand reaches toward a small blade in her boot. From the deep shadows, "
            + JONAH_DESC + " steps slowly into the wrong-blue moonlight. His hands are "
            "open at his sides, non-threatening but immovable. He speaks calmly: "
            "\"It does that.\" She draws the blade from her boot, holds it low in a "
            "street-fighter grip. She says through gritted teeth: \"My father said not "
            "to trust you.\" He watches her with patient, heavy-lidded eyes. "
            "Tension between them, dust motes drifting in the moonlight. "
            "Creak of floorboard, her sharp breathing. Camera static."
        ),
    },
    {
        "id": 4,
        "name": "The Confrontation",
        "duration": 10,
        "prompt": (
            "Cinematic medium two-shot, " + SETTING + ". "
            + MARS_DESC + " faces " + JONAH_DESC + " across the moonlit room. "
            "She holds her blade lowered but ready, the ancient book clutched protectively "
            "under her other arm. About eight feet apart among crates and supplies. "
            "She says with hard, testing tone: \"Are you built to destroy him?\" "
            "He pauses, his throat works as he swallows, weighing the cost of speaking. "
            "A faint amber glow flickers beneath the skin of his scarred throat. "
            "He says simply: \"Yes.\" The honesty lands like a blow. Her expression "
            "shifts from defensive suspicion to stunned shock. She expected lies and "
            "got brutal truth. Wrong-blue moonlight between them. Camera slow push in."
        ),
    },
    {
        "id": 5,
        "name": "Truth Curse",
        "duration": 8,
        "prompt": (
            "Cinematic close-up sequence, " + SETTING + ". "
            "Close on " + JONAH_DESC + ", his face and scarred throat in dramatic "
            "wrong-blue moonlight. Old burn scars layered like tree rings on his neck. "
            "Faint amber glow beneath the skin of his throat, like fire under the surface. "
            "His expression is controlled, patient, but pain lives in his eyes. "
            "He says quietly with steady resignation: \"It hurts.\" He swallows, "
            "throat working, the physical cost of forced honesty visible in his body. "
            "The amber glow pulses faintly when he speaks. "
            "Subtle hum from the glow, settling silence. Camera static, tight on his face."
        ),
    },
    {
        "id": 6,
        "name": "The Gut Punch",
        "duration": 10,
        "prompt": (
            "Cinematic close-up then medium two-shot, " + SETTING + ". "
            "Close on " + MARS_DESC + " in wrong-blue moonlight. Her expression is raw "
            "and unguarded, the mask momentarily gone. She says quietly, almost to herself: "
            "\"What if most of you is performance?\" This is not the calculating survivor — "
            "this is the girl underneath. A flicker of vulnerability she didn't intend to show. "
            "Then wider: both " + MARS_DESC + " and " + JONAH_DESC + " stand in the storage room. "
            "Neither is moving. The aggression between them has dissolved. She has lowered "
            "her blade entirely. He watches her with heavy, patient eyes. Something has shifted — "
            "not trust, but recognition. Two damaged people in a moment of accidental honesty. "
            "Distant dripping water, creaking wood. Camera static."
        ),
    },
    {
        "id": 7,
        "name": "The Window Calculation",
        "duration": 8,
        "prompt": (
            "Cinematic medium shot, " + SETTING + ". "
            + MARS_DESC + " stands looking up at the small high window, studying it with "
            "calculating eyes, measuring distances and angles. Wrong-blue moonlight from the "
            "window illuminates her upturned face. She says with urgent matter-of-fact tone: "
            "\"We need to move.\" Her body language has shifted from emotional to tactical. "
            "A cartographer's daughter reading the geometry of escape. Her eyes move deliberately "
            "from the narrow window to " + JONAH_DESC + " standing behind her. She is measuring "
            "his broad shoulders against the narrow window opening. The realization crosses "
            "her face — she fits, he doesn't. Muffled footsteps and voices approaching outside. "
            "Camera static."
        ),
    },
    {
        "id": 8,
        "name": "The Escape",
        "duration": 10,
        "prompt": (
            "Cinematic medium shot, " + SETTING + ". "
            + MARS_DESC + " pulls herself up toward the small high window, using a wooden "
            "crate as a stepping stone. Athletic practiced movement, the leather book tucked "
            "into her shirt. She is half-through the window frame, upper body leaning out "
            "into moonlight and night air, legs still inside. " + JONAH_DESC + " stands in "
            "the room behind her, hand slightly raised. He says with quiet urgency: \"Wait.\" "
            "She pauses, turns her face back toward him. She says softly: \"I'm sorry.\" "
            "The words ring hollow. Her expression is almost guilt, almost nothing. "
            "She drops through the window and is gone. Wrong-blue moonlight illuminates "
            "her from outside. Guards' voices closer. Camera static from inside the room."
        ),
    },
    {
        "id": 9,
        "name": "Left Behind",
        "duration": 8,
        "prompt": (
            "Cinematic medium shot widening to wide, " + SETTING + ". "
            + JONAH_DESC + " stands alone in the storage room. The small window behind him "
            "is empty now — she is gone. Wrong-blue moonlight falls where she stood. "
            "He says quietly to the empty room: \"I know.\" His expression is unreadable, "
            "patient, like he expected this. He does not move to follow. He does not react "
            "with anger. His hands hang open at his sides, empty. Something heavy in his "
            "stillness — acceptance. Dust motes drift and settle in the moonlight. "
            "The room feels vast and empty despite the clutter. Distant dripping water, "
            "wind through the window. Camera slow pull back, the scene exhales."
        ),
    },
]


def duration_to_frame_count(seconds, fps=25):
    raw = round(seconds * fps) + 1
    return max(25, min(raw, 321))


def generate_t2v(prompt, frame_count, seed=None, width=1280, height=720):
    url = f"{COMFYUI_URL}/workflows/{WORKFLOW}"
    data = {
        "prompt": prompt,
        "negative_prompt": NEGATIVE_PROMPT,
        "frame_count": str(frame_count),
        "width": str(width),
        "height": str(height),
    }
    if seed is not None:
        data["seed"] = str(seed)
    response = requests.post(url, data=data, timeout=TIMEOUT)
    if response.status_code == 200 and len(response.content) > 10000:
        return response.content
    else:
        print(f"  ERROR: HTTP {response.status_code}, {len(response.content)} bytes")
        if response.status_code != 200:
            print(f"  {response.text[:300]}")
        return None


def main():
    total = len(SHOTS)
    results = {}
    start_time = time.time()

    total_duration = sum(s["duration"] for s in SHOTS)
    print(f"Generating {total} LTX-2 t2v clips for SC03 — Storage Room")
    print(f"Target duration: {total_duration}s ({total} clips)")
    print(f"Output: {OUTPUT_DIR}")
    print(f"Backend: ComfyUI {WORKFLOW} ({FPS}fps, 1280x720)")
    print()

    for i, shot in enumerate(SHOTS):
        shot_id = shot["id"]
        name = shot["name"]
        duration = shot["duration"]
        prompt = shot["prompt"]
        frame_count = duration_to_frame_count(duration)

        safe_name = name.lower().replace(" ", "_").replace("'", "")
        output_name = f"clip{shot_id:02d}_{safe_name}"

        print(f"{'='*60}")
        print(f"--- {output_name} ({duration}s, {frame_count} frames) [{i+1}/{total}] ---")
        print(f"{'='*60}")
        print(f"  Prompt ({len(prompt)} chars):")
        print(f"  {prompt[:200]}...")
        print()

        t0 = time.time()
        video_bytes = generate_t2v(
            prompt=prompt,
            frame_count=frame_count,
            width=1280,
            height=720,
        )
        elapsed = time.time() - t0

        if video_bytes:
            out_path = OUTPUT_DIR / f"{output_name}.mp4"
            with open(out_path, "wb") as f:
                f.write(video_bytes)

            meta = {
                "shot_id": shot_id,
                "shot_name": name,
                "duration_s": duration,
                "frame_count": frame_count,
                "workflow": WORKFLOW,
                "width": 1280,
                "height": 720,
                "video_prompt": prompt,
                "negative_prompt": NEGATIVE_PROMPT,
                "elapsed_s": round(elapsed, 1),
                "bytes": len(video_bytes),
                "pipeline": "t2v",
            }
            with open(out_path.with_suffix(".json"), "w") as f:
                json.dump(meta, f, indent=2)

            mb = len(video_bytes) / (1024 * 1024)
            print(f"  OK: {mb:.1f}MB, {elapsed:.1f}s")
            results[shot_id] = f"OK ({elapsed:.1f}s)"
        else:
            print(f"  FAILED")
            results[shot_id] = "FAILED"

        if i < total - 1:
            elapsed_total = time.time() - start_time
            avg = elapsed_total / (i + 1)
            remaining = avg * (total - i - 1)
            print(f"  [{i+1}/{total} done, ~{remaining/60:.0f}m remaining]")
        print()

    # Summary
    total_elapsed = time.time() - start_time
    print(f"{'='*60}")
    print(f"SUMMARY — {total} clips in {total_elapsed/60:.1f}m")
    print(f"{'='*60}")
    for shot in SHOTS:
        sid = shot["id"]
        name = shot["name"]
        status = results.get(sid, "SKIPPED")
        print(f"  {name}: {status}")


if __name__ == "__main__":
    try:
        r = requests.get(f"{COMFYUI_URL}/health", timeout=5)
        if r.status_code != 200:
            print(f"ERROR: ComfyUI not healthy: {r.text}")
            sys.exit(1)
    except Exception as e:
        print(f"ERROR: ComfyUI not reachable at {COMFYUI_URL}: {e}")
        sys.exit(1)
    main()
