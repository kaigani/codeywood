#!/usr/bin/env python3
"""
EP01 v03 — Generate video clips from start frames using LTX-2.3 Fast.

Workflow: ltx2-3-fast (GGUF quantized, async job-based)
  - first_frame: start frame PNG
  - prompt: narrative motion prompt
  - duration: seconds (integer)
  - seed: reproducibility

Clip 3 (title card) is handled by ffmpeg separately.
"""

import sys
import time
from pathlib import Path

import requests

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
COMFYUI_BASE = "http://192.168.1.181:8100"
WORKFLOW = "ltx2-3-fast"

PROJECT = Path(__file__).resolve().parents[2] / "projects" / "stray-signal"
FRAMES_DIR = PROJECT / "PRODUCTION" / "EP01_v03" / "frames"
CLIPS_DIR = PROJECT / "PRODUCTION" / "EP01_v03" / "clips"

NEGATIVE = (
    "blurry, oversaturated, pixelated, low resolution, distorted, noise, "
    "watermark, text, logo, subtitles, deformed, extra limbs, photograph, "
    "photorealistic, live action"
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def submit_and_wait(params, files=None, timeout=600):
    url = f"{COMFYUI_BASE}/workflows/{WORKFLOW}"
    if files:
        resp = requests.post(url, data=params, files=files)
    else:
        resp = requests.post(url, data=params)
    resp.raise_for_status()
    job = resp.json()
    job_id = job["job_id"]
    start = time.time()
    deadline = start + timeout
    while time.time() < deadline:
        status = requests.get(f"{COMFYUI_BASE}/jobs/{job_id}").json()
        st = status.get("status", "unknown")
        if st == "completed":
            elapsed = time.time() - start
            print(f"    Done ({elapsed:.0f}s)")
            return requests.get(f"{COMFYUI_BASE}/jobs/{job_id}/result").content
        if st in ("error", "failed"):
            raise RuntimeError(f"Job {job_id} failed: {status.get('error')}")
        time.sleep(5)
    raise TimeoutError(f"Timeout on {job_id}")


def save(data, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as f:
        f.write(data)
    kb = len(data) / 1024
    print(f"    Saved: {path.name} ({kb:.0f} KB)")
    return path


# ---------------------------------------------------------------------------
# Clip definitions — narrative motion prompts for LTX-2.3
#
# Each prompt describes what CHANGES from the start frame.
# The start frame anchors the visual; the prompt directs motion.
# ---------------------------------------------------------------------------
CLIPS = [
    {
        "clip": 1,
        "name": "clip_01_cityscape_dawn",
        "duration": 8,
        "seed": 7001,
        "prompt": (
            "A wide establishing shot of a brutalist dystopian cityscape at dawn. "
            "The camera holds steady on a static tripod shot. Massive concrete blocks "
            "rise against a cold steel-blue sky. A single surveillance drone traces a "
            "slow lazy circuit across the upper frame, moving from left to right. "
            "Dawn light slowly brightens on the concrete surfaces. No people. "
            "A faint 60Hz electrical hum. Wind moves through concrete corridors, "
            "creating subtle shadow shifts on building faces. Stylized sci-fi animation, "
            "graphic novel rendering, desaturated brutalist world."
        ),
    },
    {
        "clip": 2,
        "name": "clip_02_neda_on_the_grid",
        "duration": 12,
        "seed": 7002,
        "prompt": (
            "A girl walks forward through a brutalist city street among distant citizens "
            "in grey coveralls. She wears a steel-blue jacket with geometric collar. "
            "She moves at the same regulation pace as the others, arms at sides, but her "
            "eyes track differently — aware, scanning, reading the environment without "
            "turning her head. The crowd moves in uniform rhythm behind her. She reaches "
            "a maintenance grate at ground level, then in one smooth motion she crouches, "
            "lifts the polymer cover, and drops below the surface. The grate slides back. "
            "Cold 4500K fluorescent lighting throughout. Stylized sci-fi animation, "
            "graphic novel rendering."
        ),
    },
    # Clip 3: title card — ffmpeg, skip
    {
        "clip": 3,
        "name": "clip_03_title_card",
        "duration": 0,
        "seed": 0,
        "prompt": "",
        "skip": True,
    },
    {
        "clip": 4,
        "name": "clip_04_seam_descent",
        "duration": 12,
        "seed": 7004,
        "prompt": (
            "A girl descends rough stone steps from cold blue-grey light above into "
            "warm amber light below. She is seen from behind, moving steadily downward. "
            "Her shoulders drop and her posture softens as she descends into warmth. "
            "The cold polymer and fluorescent light above gives way to rough stone walls "
            "with amber LED string lights. The color temperature shifts dramatically from "
            "cold steel-blue to warm golden amber. Behind her below, the glow of an "
            "underground community — string lights criss-crossing, warm golden light "
            "ahead. A distant guitar sound fades in. Stone echo. Voices carrying. "
            "Stylized sci-fi animation, graphic novel rendering."
        ),
    },
    {
        "clip": 5,
        "name": "clip_05_fens_room",
        "duration": 12,
        "seed": 7005,
        "prompt": (
            "A wide shot framed through a doorway. A small room lit by green-white "
            "grow-lamps. A figure sits in the center of the room in silhouette, backlit, "
            "absolutely still. The stillness of furniture. The figure does not move at all "
            "for the entire shot. In the foreground doorway, a girl stands looking in. "
            "She stands still for five seconds, watching. Then she slowly turns away and "
            "walks out of frame to the left. The seated figure never moves, never "
            "acknowledges. The grow-lamps hum. Two distinct lighting zones — warm amber "
            "doorway, green-white room. Stylized sci-fi animation, graphic novel rendering."
        ),
    },
    {
        "clip": 6,
        "name": "clip_06_briefing_intel",
        "duration": 10,
        "seed": 7006,
        "prompt": (
            "Close-up of a girl's face in warm amber light. An underground stone room "
            "with rough-hewn walls and amber string lights. She sits at a stone table, "
            "listening intently. Her expression is controlled, absorbing every word from "
            "someone off-screen. Her eyes track slightly as she processes information. "
            "Then something lands — her right hand moves to grip the edge of the stone "
            "table. Her eyes change subtly. Not surprise. Recognition. She knows what "
            "this means. Amber light pools on her brown skin. "
            "Stylized sci-fi animation, graphic novel rendering."
        ),
    },
    {
        "clip": 7,
        "name": "clip_07_briefing_argument",
        "duration": 14,
        "seed": 7007,
        "prompt": (
            "Close-up of a girl leaning forward at a rough stone table in a small "
            "underground room lit by amber string lights. She speaks with controlled "
            "intensity, her jaw tightening before each phrase. She leans further forward "
            "as she argues. Her fist grips the table edge. A copper braid behind her left "
            "ear catches the amber light. She makes her point with absolute conviction. "
            "Then silence. Four seconds of stillness. Her conviction holds in her face. "
            "The amber light is heavy on rough stone walls. "
            "Stylized sci-fi animation, graphic novel rendering."
        ),
    },
    {
        "clip": 8,
        "name": "clip_08_neda_returns",
        "duration": 8,
        "seed": 7008,
        "prompt": (
            "Medium shot of a girl walking with determination through an underground "
            "stone corridor. Amber string lights overhead on rough stone walls. She moves "
            "with purpose, stride long and direct, passing a branching hallway without "
            "looking. She reaches stone steps ascending toward colder, bluer light above. "
            "She climbs upward. The warm amber light recedes behind her as she moves "
            "toward cold. The color temperature shifts from warm to cool. "
            "Stylized sci-fi animation, graphic novel rendering."
        ),
    },
    {
        "clip": 9,
        "name": "clip_09_grid_with_purpose",
        "duration": 10,
        "seed": 7009,
        "prompt": (
            "Wide shot of a brutalist city street. Cold steel-blue architecture. A girl "
            "walks through the frame with mission energy — faster and more direct than "
            "the regulation pace. She moves with purpose, a body with coordinates. "
            "A surveillance drone passes overhead and she tracks it without looking up, "
            "without breaking stride. She moves toward a building in the distance. "
            "The same cold world as before, but she moves through it differently now. "
            "4500K cold fluorescent lighting. Concrete and polymer. "
            "Stylized sci-fi animation, graphic novel rendering."
        ),
    },
    {
        "clip": 10,
        "name": "clip_10_kai_appears",
        "duration": 12,
        "seed": 7010,
        "prompt": (
            "A maintenance corridor with fluorescent strip lighting and polymer floor. "
            "A boy walks toward the camera from the far end of the corridor. He is alone, "
            "sixteen years old, wearing a maintenance coverall. A battered datapad in one "
            "hand. In his other hand, a small device emits a faint cyan glow that catches "
            "his face and fingers. He walks with measured, careful steps. He does not look "
            "up. The cyan glow is a color that does not belong in this cold sterile world. "
            "He is unaware anyone is watching. Fluorescent cold light, hazard tape on walls. "
            "Stylized sci-fi animation, graphic novel rendering."
        ),
    },
    {
        "clip": 11,
        "name": "clip_11_neda_watching",
        "duration": 10,
        "seed": 7011,
        "prompt": (
            "Close-up of a girl's face in a cold fluorescent corridor. She stands "
            "absolutely still, watching something ahead and off-screen. A faint cyan "
            "light reflects on her face from something we cannot see. She recognizes it. "
            "Her jaw tightens slowly. Her eyes narrow with calculation and recognition "
            "and something she is trying not to feel. Three seconds of absolute stillness. "
            "Then she takes a single step forward. Her expression resolves into purpose. "
            "Then cut to black. Cold 4500K corridor light with warm cyan accent. "
            "Stylized sci-fi animation, graphic novel rendering."
        ),
    },
]


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Generate EP01 v03 video clips via LTX-2.3 Fast")
    parser.add_argument("--clip", type=int, help="Specific clip number (or 0 for all)", default=0)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--timeout", type=int, default=600, help="Per-clip timeout in seconds")
    args = parser.parse_args()

    CLIPS_DIR.mkdir(parents=True, exist_ok=True)

    clips = CLIPS
    if args.clip > 0:
        clips = [c for c in CLIPS if c["clip"] == args.clip]
        if not clips:
            print(f"No clip {args.clip}")
            sys.exit(1)

    # Health check
    try:
        r = requests.get(f"{COMFYUI_BASE}/health", timeout=5)
        if r.status_code != 200:
            print(f"ERROR: ComfyUI not healthy (status {r.status_code})")
            sys.exit(1)
    except Exception as e:
        print(f"ERROR: ComfyUI not reachable: {e}")
        sys.exit(1)

    if args.dry_run:
        print(f"[DRY RUN] {len(clips)} clips:")
        for c in clips:
            if c.get("skip"):
                print(f"  Clip {c['clip']}: {c['name']} — SKIP (ffmpeg)")
                continue
            out = CLIPS_DIR / f"{c['name']}.mp4"
            frame = FRAMES_DIR / f"{c['name']}.png"
            exists = out.exists()
            has_frame = frame.exists()
            print(f"  Clip {c['clip']}: {c['name']} ({c['duration']}s) "
                  f"{'EXISTS' if exists else 'pending'} "
                  f"{'[frame OK]' if has_frame else '[NO FRAME]'}")
        sys.exit(0)

    total = len([c for c in clips if not c.get("skip")])
    done = 0
    failed = []

    for clip_def in clips:
        if clip_def.get("skip"):
            print(f"\n  Clip {clip_def['clip']}: {clip_def['name']} — SKIP (ffmpeg title)")
            continue

        done += 1
        clip_num = clip_def["clip"]
        name = clip_def["name"]
        out_path = CLIPS_DIR / f"{name}.mp4"

        if out_path.exists():
            print(f"\n  [{done}/{total}] Clip {clip_num}: {name} — SKIP (exists)")
            continue

        frame_path = FRAMES_DIR / f"{name}.png"
        if not frame_path.exists():
            print(f"\n  [{done}/{total}] Clip {clip_num}: {name} — SKIP (no start frame)")
            failed.append(name)
            continue

        print(f"\n  [{done}/{total}] Clip {clip_num}: {name} ({clip_def['duration']}s)")

        try:
            params = {
                "prompt": clip_def["prompt"],
                "negative_prompt": NEGATIVE,
                "duration": str(clip_def["duration"]),
                "width": "1280",
                "height": "720",
                "seed": str(clip_def["seed"]),
            }
            fh = open(frame_path, "rb")
            try:
                files = {"first_frame": (frame_path.name, fh, "image/png")}
                data = submit_and_wait(params, files=files, timeout=args.timeout)
            finally:
                fh.close()

            save(data, out_path)

        except Exception as e:
            print(f"    FAILED: {e}")
            failed.append(name)

    if failed:
        print(f"\n  FAILED ({len(failed)}): {', '.join(failed)}")

    print(f"\n{'=' * 70}")
    print(f"DONE — {done}/{total} clips processed")
    print(f"{'=' * 70}")
