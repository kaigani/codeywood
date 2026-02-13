#!/usr/bin/env python3
"""
Generate LTX-2 text-to-video clips for SC02 — Naval Infiltration.
T2V pipeline — no start frames needed.

Mars infiltrates the naval compound 3 hours after watching her father hang.
She searches his cell and discovers the Ledger hidden in the wall.
"""

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import requests

# ─── Config ───────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).parent.parent.parent / "projects" / "pirate-romance"
SCENE_DIR = PROJECT_ROOT / "PRODUCTION" / "EP01" / "sc02"
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

# Mars physical description — must appear in every shot she's visible
MARS_DESC = (
    "young woman of mixed Caribbean heritage, 16 years old, lean athletic build, "
    "thick dark curly hair tied back, sun-darkened olive skin, visible freckles "
    "across nose and cheekbones, ink-stained hands, wearing worn leather vest "
    "over linen shirt, trousers, leather map case at hip, 18th century clothing"
)

# ─── T2V Shot Definitions ────────────────────────────────────────────
# Prompts written for t2v: literal, descriptive, setting anchors every shot

SHOTS = [
    {
        "id": 1,
        "name": "Compound Exterior",
        "duration": 8,
        "prompt": (
            "Cinematic wide shot, Caribbean colonial naval compound at golden hour dusk, "
            "18th century. High weathered stone walls with iron gates, Union Jack flag "
            "flying from a pole, armed guards in bright red British colonial coats with "
            "white crossbelts standing at the entrance. A drainage pipe runs up the eastern "
            "wall near the corner. A small figure — " + MARS_DESC + " — crouches in shadow "
            "near the base of the wall, studying the compound, measuring distances. "
            "She whispers to herself: \"The holding cells are in the east wing. Third floor. "
            "The window faces the harbor.\" "
            "Massive colonial architecture dwarfs her figure. Golden hour lighting, "
            "long shadows, warm amber sunlight on weathered stone. Slow camera push in "
            "toward her crouched figure. Harbor visible in the background, tall-masted ships."
        ),
    },
    {
        "id": 2,
        "name": "Scaling the Wall",
        "duration": 8,
        "prompt": (
            "Cinematic wide shot, " + MARS_DESC + " climbs a drainage pipe on the exterior "
            "wall of a Caribbean colonial naval compound, 18th century. Her silhouette against "
            "deep amber sunset sky. Athletic determined movement upward, hands gripping iron pipe, "
            "boots finding purchase on stone. Last light of day catching her figure. "
            "She murmurs under her breath: \"He had three hours between sentencing and... after. "
            "Three hours to hide what he wanted me to find.\" "
            "Weathered stone texture, practical climbing movement. Wind blows her loose curls. "
            "Camera static, looking up at her ascent. High stone walls, colonial architecture."
        ),
    },
    {
        "id": 3,
        "name": "Prison Corridor",
        "duration": 8,
        "prompt": (
            "Cinematic wide shot, interior of a Caribbean colonial prison corridor at night, "
            "18th century. Wrong-blue teal moonlight streams through barred windows, creating "
            "sharp shadows across damp stone walls. A single oil lantern flickers amber light. "
            + MARS_DESC + " drops through a high barred window, landing silently on stone floors. "
            "She moves down the long corridor of iron cell doors, scanning rusted numbers. "
            "Dripping water echoes, distant wind through bars. Atmosphere of dread and tension. "
            "Long perspective of cell doors receding into dark misty void. Her soft footsteps "
            "on wet stone. Camera tracks her movement down the corridor."
        ),
    },
    {
        "id": 4,
        "name": "The Cell",
        "duration": 10,
        "prompt": (
            "Cinematic medium shot, " + MARS_DESC + " stands in the doorway of a small stone "
            "prison cell, 18th century Caribbean colonial. Wrong-blue teal moonlight silhouettes "
            "her figure. She pushes the iron door open with a creak and steps inside slowly. "
            "She whispers barely audible: \"This is it.\" "
            "Bare stone walls, stone floor, straw scattered, a narrow wooden cot, a bucket. "
            "Dust particles swirl in the moonlight beams. She moves deeper into the cell, "
            "scanning the walls carefully, her fingers tracing the rough stone surface. "
            "She kneels at the far wall, examining the mortar between stones. Iron door "
            "creaking, stone echoes. Camera slow push in following her movement."
        ),
    },
    {
        "id": 5,
        "name": "Hands Working Stone",
        "duration": 8,
        "prompt": (
            "Extreme close-up shot, a pair of ink-stained female hands prying at crumbling "
            "stone mortar with a small blade. 18th century prison cell wall. Stone dust and "
            "fragments scatter as she works. A faint wrong-blue teal glow begins to emanate "
            "from within a hollow space behind the loosening stone. Fingers press against "
            "rough prison stone, knuckles white with effort. Labored breathing, grunts of "
            "physical effort. The glow intensifies as more stone crumbles away. The texture "
            "of old mortar breaking apart. Camera static, tight on the hands and the growing "
            "otherworldly light seeping through the cracks."
        ),
    },
    {
        "id": 6,
        "name": "The Ledger Revealed",
        "duration": 10,
        "prompt": (
            "Cinematic medium close-up, " + MARS_DESC + " pulls an ancient book from a hollow "
            "space in a stone prison wall, 18th century Caribbean colonial cell. The book is "
            "bound in strange dark leather that seems to pulse with faint wrong-blue teal light. "
            "The supernatural glow illuminates her face from below, casting dramatic shadows. "
            "Her expression shifts from focused determination to shock to recognition — she "
            "gasps. An otherworldly hum fills the air. She holds the book carefully, staring "
            "at it. Wrong-blue light pulses rhythmically, like a heartbeat. Dust particles "
            "float in the teal glow. Camera slow push in on her face as she processes what "
            "she's found. The Ledger seems alive in her hands."
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

    print(f"Generating {total} LTX-2 t2v clips for SC02 — Naval Infiltration")
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
