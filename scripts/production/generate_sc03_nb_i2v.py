#!/usr/bin/env python3
"""
Generate SC03 i2v clips from Hailuo NanoBanana stills — Storage Room.

Uses 6 hand-curated stills as start frames for shots 1-5 and 9.
Shots 6-8 chain from the last frame of the previous clip.

Pipeline:
  For each shot in order:
    - If a still exists for this shot, use it as start frame
    - Otherwise, extract last frame from previous clip
    - Generate i2v clip via LTX-2
  Then assemble all clips.
"""

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import requests
from lib.ffmpeg import extract_last_frame, concatenate_clips

# ─── Config ───────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).parent.parent.parent / "projects" / "pirate-romance"
SCENE_DIR = PROJECT_ROOT / "PRODUCTION" / "EP01" / "sc03"
NB_DIR = SCENE_DIR / "nb_draft"
OUTPUT_DIR = SCENE_DIR / "nb_i2v_draft"
CLIPS_DIR = OUTPUT_DIR / "clips"
ASSEMBLY_DIR = OUTPUT_DIR / "assembly"

COMFYUI_URL = "http://192.168.1.181:8100"
WORKFLOW = "ltx2-i2v"
FPS = 25
TIMEOUT = 900

NEGATIVE_PROMPT = (
    "blur, distort, low quality, cartoon, anime, deformed, extra limbs, "
    "text, watermark, modern clothing, contemporary architecture"
)

# ─── Still-to-Shot Mapping ────────────────────────────────────────────
# Maps shot ID to the Hailuo still filename in nb_draft/
STILL_MAP = {
    1: "Hailuo_Image_Change the character in the sc_478485133425500162.jpg",
    2: "Hailuo_Image_Recreate the scene to match he_478488462192910345.jpg",
    3: "Hailuo_Image_Recreate the scene to match he_478488045618778113.jpg",
    4: "Hailuo_Image_Recreate the scene to match he_478488533483442183.jpg",
    5: "Hailuo_Image_Change the character in image _478463673050927105.jpg",
    # 6, 7, 8: chain from last frame of previous clip
    9: "Hailuo_Image_Remove the grating_bars frame _478490020276133892.jpg",
}

# ─── Character + Setting Constants ────────────────────────────────────

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

SETTING = (
    "cluttered naval storage room interior at night, 18th century Caribbean colonial compound. "
    "Wooden crates stacked high, coiled rope, naval supplies. A single small window high "
    "on the far wall, wrong-blue moonlight streaming through, dust motes in the light beam"
)

# ─── Shot Definitions (video prompts only — frames come from stills) ──

SHOTS = [
    {
        "id": 1,
        "name": "Entrance and the Ledger",
        "duration": 8,
        "prompt": (
            "Cinematic medium shot, " + SETTING + ". "
            + MARS_DESC + " is pressed against a heavy wooden door, gasping for breath, "
            "chest heaving, wild eyes scanning the room. She clutches an ancient leather-bound "
            "book tight to her chest with both hands. The book has a faint wrong-blue glow "
            "pulsing from within its pages. She looks down at it and hisses: "
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


def safe_name(name):
    return name.lower().replace(" ", "_").replace("'", "").replace(":", "")


def generate_i2v(start_frame, prompt, frame_count, seed=None):
    """Generate a single i2v clip via ComfyUI LTX-2."""
    url = f"{COMFYUI_URL}/workflows/{WORKFLOW}"
    data = {
        "prompt": prompt,
        "negative_prompt": NEGATIVE_PROMPT,
        "frame_count": str(frame_count),
    }
    if seed is not None:
        data["seed"] = str(seed)

    with open(start_frame, "rb") as img_file:
        files = {"image": (Path(start_frame).name, img_file, "image/png")}
        response = requests.post(url, data=data, files=files, timeout=TIMEOUT)

    if response.status_code == 200 and len(response.content) > 10000:
        return response.content
    else:
        print(f"  ERROR: HTTP {response.status_code}, {len(response.content)} bytes")
        if response.status_code != 200:
            print(f"  {response.text[:300]}")
        return None


def main():
    CLIPS_DIR.mkdir(parents=True, exist_ok=True)
    ASSEMBLY_DIR.mkdir(parents=True, exist_ok=True)

    # Verify stills exist
    print("Checking stills...")
    for shot_id, filename in STILL_MAP.items():
        path = NB_DIR / filename
        status = "OK" if path.exists() else "MISSING"
        print(f"  Shot {shot_id}: {status} — {filename[:60]}...")
    print()

    total = len(SHOTS)
    total_duration = sum(s["duration"] for s in SHOTS)
    results = {}
    clip_paths = {}  # shot_id -> clip path (for last-frame extraction)
    start_time = time.time()

    print(f"SC03 NB Stills→i2v — Storage Room")
    print(f"{'='*60}")
    print(f"Shots: {total}, Target duration: {total_duration}s")
    print(f"Stills: {len(STILL_MAP)} provided, {total - len(STILL_MAP)} will chain from last frames")
    print(f"Output: {OUTPUT_DIR}")
    print(f"Backend: ComfyUI {WORKFLOW} ({FPS}fps)")
    print()

    for i, shot in enumerate(SHOTS):
        shot_id = shot["id"]
        name = shot["name"]
        duration = shot["duration"]
        prompt = shot["prompt"]
        frame_count = duration_to_frame_count(duration)
        sname = safe_name(name)
        output_name = f"clip{shot_id:02d}_{sname}"

        # Determine start frame source
        if shot_id in STILL_MAP:
            start_frame = NB_DIR / STILL_MAP[shot_id]
            frame_source = f"still: {start_frame.name[:50]}..."
        else:
            # Extract last frame from previous clip
            prev_id = shot_id - 1
            if prev_id not in clip_paths:
                print(f"  ERROR: No previous clip for shot {shot_id} — skipping")
                results[shot_id] = "SKIPPED (no prev clip)"
                continue

            prev_clip = clip_paths[prev_id]
            last_frame_path = CLIPS_DIR / f"lastframe_{prev_id:02d}.png"
            extracted = extract_last_frame(prev_clip, last_frame_path)
            if not extracted:
                print(f"  ERROR: Could not extract last frame from clip {prev_id} — skipping")
                results[shot_id] = "SKIPPED (extract failed)"
                continue

            start_frame = last_frame_path
            frame_source = f"last frame of clip {prev_id:02d}"

        if not Path(start_frame).exists():
            print(f"  ERROR: Start frame not found: {start_frame}")
            results[shot_id] = "SKIPPED (missing frame)"
            continue

        print(f"{'='*60}")
        print(f"--- {output_name} ({duration}s, {frame_count} frames) [{i+1}/{total}] ---")
        print(f"{'='*60}")
        print(f"  Frame: {frame_source}")
        print(f"  Prompt ({len(prompt)} chars):")
        print(f"  {prompt[:200]}...")
        print()

        t0 = time.time()
        video_bytes = generate_i2v(
            start_frame=start_frame,
            prompt=prompt,
            frame_count=frame_count,
        )
        elapsed = time.time() - t0

        if video_bytes:
            out_path = CLIPS_DIR / f"{output_name}.mp4"
            with open(out_path, "wb") as f:
                f.write(video_bytes)
            clip_paths[shot_id] = out_path

            meta = {
                "shot_id": shot_id,
                "shot_name": name,
                "duration_s": duration,
                "frame_count": frame_count,
                "workflow": WORKFLOW,
                "fps": FPS,
                "video_prompt": prompt,
                "negative_prompt": NEGATIVE_PROMPT,
                "start_frame": str(start_frame),
                "frame_source": "still" if shot_id in STILL_MAP else f"last_frame_of_clip_{shot_id-1:02d}",
                "elapsed_s": round(elapsed, 1),
                "bytes": len(video_bytes),
                "pipeline": "nb_stills_i2v",
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

    # ─── Summary ──────────────────────────────────────────────────────
    total_elapsed = time.time() - start_time
    print(f"{'='*60}")
    print(f"GENERATION SUMMARY — {total} clips in {total_elapsed/60:.1f}m")
    print(f"{'='*60}")
    for shot in SHOTS:
        sid = shot["id"]
        status = results.get(sid, "SKIPPED")
        src = "still" if sid in STILL_MAP else "chain"
        print(f"  {shot['name']} [{src}]: {status}")

    # ─── Assembly ─────────────────────────────────────────────────────
    clips = sorted(CLIPS_DIR.glob("clip*.mp4"))
    if clips:
        output_path = ASSEMBLY_DIR / "sc03_nb_i2v_assembly.mp4"
        concatenate_clips(clips, output_path)

        if output_path.exists():
            import subprocess
            probe = subprocess.run(
                ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
                 "-of", "csv=p=0", str(output_path)],
                capture_output=True, text=True,
            )
            dur = float(probe.stdout.strip()) if probe.stdout.strip() else 0
            size_mb = output_path.stat().st_size / (1024 * 1024)
            print(f"\nAssembly: {dur:.1f}s, {size_mb:.1f}MB")
            print(f"  {output_path}")
    else:
        print("\nNo clips to assemble.")


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
