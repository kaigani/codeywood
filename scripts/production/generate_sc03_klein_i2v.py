#!/usr/bin/env python3
"""
Generate SC03 Klein→i2v clips — Storage Room.

Two-phase pipeline:
  Phase 1: Multiref start frames (identity sheets + location ref, JSON prompting)
  Phase 2: LTX-2 i2v clips (rich video prompts, start frames from Phase 1)

Supports Klein (fast draft) or Dev (high fidelity) frame generation via --dev flag.

Usage:
    python generate_sc03_klein_i2v.py               # Both phases (Klein frames)
    python generate_sc03_klein_i2v.py --dev          # Both phases (Dev frames)
    python generate_sc03_klein_i2v.py --frames-only  # Phase 1 only
    python generate_sc03_klein_i2v.py --dev --frames-only --shot 3  # Single Dev frame test
    python generate_sc03_klein_i2v.py --clips-only   # Phase 2 only (frames must exist)
    python generate_sc03_klein_i2v.py --shot 3       # Single shot test
"""

import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import requests
from lib.backends.comfyui_backend import ComfyUIImageBackend

# ─── Config ───────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).parent.parent.parent / "projects" / "pirate-romance"
SCENE_DIR = PROJECT_ROOT / "PRODUCTION" / "EP01" / "sc03"

COMFYUI_URL = "http://192.168.1.181:8100"
VIDEO_WORKFLOW = "ltx2-i2v"
FPS = 25
VIDEO_TIMEOUT = 900

NEGATIVE_PROMPT = (
    "blur, distort, low quality, cartoon, anime, deformed, extra limbs, "
    "text, watermark, modern clothing, contemporary architecture"
)

FRAME_NEGATIVE = (
    "cartoon, anime, illustration, painting, sketch, multiple panels, "
    "triptych, split image, text overlay, watermark"
)

# ─── Reference Images (identity sheets + location establishing shot) ──
MARS_ID = PROJECT_ROOT / "REFERENCES" / "identity_sheets" / "mars_identity_nano_banana_20260203_131447.png"
JONAH_ID = PROJECT_ROOT / "REFERENCES" / "identity_sheets" / "jonah_identity_nano_banana_20260203_131551.png"
LOCATION_REF = SCENE_DIR / "frames" / "sc03_shot01_establish_20260205_172910.png"

# ─── Character + Setting Constants ────────────────────────────────────
# Identical to generate_sc03_t2v.py for fair comparison

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

# ─── Dual-Prompt Shot Definitions ─────────────────────────────────────
# Each shot has:
#   frame_prompt: frozen moment for Klein t2i (no motion/sound/camera)
#   video_prompt: rich motion prompt for i2v (nearly identical to t2v prompts)

SHOTS = [
    {
        "id": 1,
        "name": "Entrance and the Ledger",
        "duration": 8,
        "frame_prompt": (
            "Cinematic medium shot, " + SETTING + ". "
            + MARS_DESC + " stands pressed flat against a heavy wooden door, "
            "both hands clutching an ancient leather-bound book tight to her chest. "
            "The book has a faint wrong-blue glow pulsing from within its pages. "
            "Her chest is heaving, eyes wide and scanning the room. "
            "Wrong-blue moonlight from the high window illuminates her face."
        ),
        "video_prompt": (
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
        "frame_prompt": (
            "Cinematic close-up, " + MARS_DESC + " stares down at an open ancient book "
            "in her hands. Wrong-blue glow illuminates her face from below. Her expression "
            "shows shock and disgust, jaw tight, eyes bright with fury. " + SETTING + ". "
            "Wrong-blue moonlight on one side of her face."
        ),
        "video_prompt": (
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
        "frame_prompt": (
            "Cinematic medium-wide two-shot, " + SETTING + ". "
            + MARS_DESC + " stands in a defensive stance, one hand reaching toward "
            "a small blade in her boot. " + JONAH_DESC + " stands half-emerged from "
            "deep shadows into wrong-blue moonlight, hands open at his sides, "
            "non-threatening. Dust motes drift between them in the moonlight."
        ),
        "video_prompt": (
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
        "frame_prompt": (
            "Cinematic medium two-shot, " + SETTING + ". "
            + MARS_DESC + " faces " + JONAH_DESC + " across the moonlit room. "
            "She holds a blade lowered but ready, the ancient book clutched protectively "
            "under her other arm. About eight feet apart among crates and supplies. "
            "Wrong-blue moonlight falls between them."
        ),
        "video_prompt": (
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
        "frame_prompt": (
            "Cinematic close-up, " + SETTING + ". "
            "Close on " + JONAH_DESC + ", his face and scarred throat in dramatic "
            "wrong-blue moonlight. Old burn scars layered like tree rings on his neck. "
            "Faint amber glow beneath the skin of his throat. His expression is controlled "
            "and patient, but pain lives in his eyes."
        ),
        "video_prompt": (
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
        "frame_prompt": (
            "Cinematic close-up, " + SETTING + ". "
            "Close on " + MARS_DESC + " in wrong-blue moonlight. Her expression is raw "
            "and unguarded, the mask momentarily gone. A flicker of vulnerability she didn't "
            "intend to show. This is not the calculating survivor — this is the girl underneath."
        ),
        "video_prompt": (
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
        "frame_prompt": (
            "Cinematic medium shot, " + SETTING + ". "
            + MARS_DESC + " stands looking up at the small high window, studying it with "
            "calculating eyes. Wrong-blue moonlight from the window illuminates her upturned "
            "face. A cartographer's daughter reading the geometry of escape. "
            + JONAH_DESC + " stands behind her, his broad shoulders visible."
        ),
        "video_prompt": (
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
        "frame_prompt": (
            "Cinematic medium shot, " + SETTING + ". "
            + MARS_DESC + " is halfway up on a wooden crate, reaching toward the small high "
            "window. Athletic build visible, the leather book tucked into her shirt. "
            + JONAH_DESC + " stands in the room behind her, hand slightly raised. "
            "Wrong-blue moonlight illuminates her from the window above."
        ),
        "video_prompt": (
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
        "frame_prompt": (
            "Cinematic medium shot, " + SETTING + ". "
            + JONAH_DESC + " stands alone in the storage room. The small window behind him "
            "is empty — she is gone. Wrong-blue moonlight falls where she stood. "
            "His hands hang open at his sides, empty. His expression is unreadable, patient. "
            "Dust motes drift in the moonlight. The room feels vast despite the clutter."
        ),
        "video_prompt": (
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
    """Convert duration in seconds to LTX-2 frame count."""
    raw = round(seconds * fps) + 1
    return max(25, min(raw, 321))


def safe_name(name):
    """Convert shot name to filesystem-safe string."""
    return name.lower().replace(" ", "_").replace("'", "").replace(":", "")


# Which characters appear in each shot (for reference image selection)
SHOT_CHARACTERS = {
    1: ["mars"],
    2: ["mars"],
    3: ["mars", "jonah"],
    4: ["mars", "jonah"],
    5: ["jonah"],
    6: ["mars", "jonah"],
    7: ["mars", "jonah"],
    8: ["mars", "jonah"],
    9: ["jonah"],
}


def get_refs(shot_id):
    """Get reference images for a shot: identity sheets first, location last.

    Ordering matters — identity sheets get highest priority for character likeness.
    Returns (ref_paths, char_list) tuple.
    """
    chars = SHOT_CHARACTERS.get(shot_id, [])
    refs = []

    # Identity sheets FIRST (highest priority)
    for char in chars:
        if char == "mars" and MARS_ID.exists():
            refs.append(MARS_ID)
        elif char == "jonah" and JONAH_ID.exists():
            refs.append(JONAH_ID)

    # Location establishing shot LAST
    if LOCATION_REF.exists():
        refs.append(LOCATION_REF)

    return refs, chars


def _build_json_prompt(frame_prompt, chars, refs):
    """Build JSON-structured prompt for Flux multiref.

    JSON prompting helps Flux attribute subjects correctly when multiple
    reference images are provided. References images by number (1-indexed).
    """
    parts = {"scene": frame_prompt}

    ref_idx = 1
    for char in chars:
        if char == "mars":
            parts[f"subject_from_image_{ref_idx}"] = (
                f"The young woman from image {ref_idx}: dark curly hair tied back, "
                "sun-darkened olive skin, freckles across nose and cheekbones, "
                "worn leather vest over linen shirt, ink-stained hands"
            )
            ref_idx += 1
        elif char == "jonah":
            parts[f"subject_from_image_{ref_idx}"] = (
                f"The young man from image {ref_idx}: tall, broad-shouldered, "
                "olive skin, cropped dark hair, faint burn scars at throat, "
                "heavy-lidded patient eyes, simple worn linen shirt"
            )
            ref_idx += 1

    # Location ref is the last image
    if ref_idx <= len(refs):
        parts[f"setting_from_image_{ref_idx}"] = (
            f"Use the storage room environment from image {ref_idx} as the location: "
            "stone walls, wooden crates, coiled rope, barrels, wrong-blue moonlight "
            "from high barred window, oil lantern warm glow"
        )

    return json.dumps(parts)


# ─── Phase 1: Start Frames ────────────────────────────────────────────

def generate_frames(shots, backend, frames_dir, steps=12, use_dev=False):
    """Generate multiref start frames using identity sheets + location ref."""
    frames_dir.mkdir(parents=True, exist_ok=True)
    total = len(shots)
    results = {}
    start_time = time.time()

    model_label = "Dev" if use_dev else "Klein"

    # Check reference images
    for name, path in [("Mars ID", MARS_ID), ("Jonah ID", JONAH_ID), ("Location", LOCATION_REF)]:
        status = "OK" if path.exists() else "MISSING"
        print(f"  {name}: {status} — {path.name}")

    print(f"\nPhase 1: Generating {total} {model_label} multiref start frames")
    print(f"Output: {frames_dir}")
    if use_dev:
        print(f"Backend: Dev multiref ({steps} steps, guidance 4.0, JSON prompting)")
    else:
        print(f"Backend: Klein multiref ({steps} steps, cfg 3.5, JSON prompting)")
    print()

    for i, shot in enumerate(shots):
        shot_id = shot["id"]
        name = shot["name"]
        frame_prompt = shot["frame_prompt"]
        fname = f"frame{shot_id:02d}_{safe_name(name)}"

        # Get reference images for this shot
        refs, chars = get_refs(shot_id)
        ref_strs = [str(r) for r in refs]

        # Build JSON prompt for multiref, or use raw prompt for t2i
        if len(refs) >= 2:
            actual_prompt = _build_json_prompt(frame_prompt, chars, refs)
            mode = f"multiref, {len(refs)} refs ({', '.join(chars)}+loc)"
        elif len(refs) == 1:
            actual_prompt = frame_prompt
            mode = "i2i, 1 ref"
        else:
            actual_prompt = frame_prompt
            mode = "t2i, 0 refs"

        print(f"{'='*60}")
        print(f"--- {fname} ({mode}) [{i+1}/{total}] ---")
        print(f"{'='*60}")
        print(f"  Frame prompt ({len(frame_prompt)} chars):")
        print(f"  {frame_prompt[:150]}...")
        if len(refs) >= 2:
            print(f"  JSON prompt ({len(actual_prompt)} chars)")
        print(f"  Refs: {[r.name for r in refs]}")
        print()

        t0 = time.time()
        gen_kwargs = {
            "prompt": actual_prompt,
            "reference_urls": ref_strs if refs else None,
            "negative_prompt": FRAME_NEGATIVE,
            "aspect_ratio": "16:9",
            "steps": steps,
        }
        if not use_dev:
            gen_kwargs["cfg"] = 3.5
        result = backend.generate_image(**gen_kwargs)
        elapsed = time.time() - t0

        if result.image_bytes and len(result.image_bytes) > 5000:
            out_path = frames_dir / f"{fname}.png"
            with open(out_path, "wb") as f:
                f.write(result.image_bytes)

            meta = {
                "shot_id": shot_id,
                "shot_name": name,
                "frame_prompt": frame_prompt,
                "json_prompt": actual_prompt if len(refs) >= 2 else None,
                "negative_prompt": FRAME_NEGATIVE,
                "workflow": result.metadata.get("workflow", "unknown"),
                "model": model_label.lower(),
                "ref_mode": "multiref" if len(refs) >= 2 else ("i2i" if len(refs) == 1 else "t2i"),
                "characters": chars,
                "refs": len(refs),
                "ref_paths": ref_strs,
                "steps": steps,
                "guidance": result.metadata.get("guidance") if use_dev else None,
                "cfg": result.metadata.get("cfg") if not use_dev else None,
                "width": result.metadata.get("width", 1008),
                "height": result.metadata.get("height", 576),
                "seed": result.metadata.get("seed"),
                "elapsed_s": round(elapsed, 1),
                "bytes": len(result.image_bytes),
                "pipeline": f"{model_label.lower()}_multiref",
            }
            with open(out_path.with_suffix(".json"), "w") as f:
                json.dump(meta, f, indent=2)

            kb = len(result.image_bytes) / 1024
            print(f"  OK: {kb:.0f}KB, {elapsed:.1f}s")
            results[shot_id] = f"OK ({elapsed:.1f}s)"
        else:
            print(f"  FAILED: No image data returned")
            results[shot_id] = "FAILED"

        if i < total - 1:
            elapsed_total = time.time() - start_time
            avg = elapsed_total / (i + 1)
            remaining = avg * (total - i - 1)
            print(f"  [{i+1}/{total} done, ~{remaining/60:.0f}m remaining]")
        print()

    total_elapsed = time.time() - start_time
    print(f"{'='*60}")
    print(f"Phase 1 SUMMARY — {total} frames in {total_elapsed/60:.1f}m")
    print(f"{'='*60}")
    for shot in shots:
        sid = shot["id"]
        status = results.get(sid, "SKIPPED")
        print(f"  {shot['name']}: {status}")
    print()
    return results


# ─── Phase 2: LTX-2 i2v Clips ────────────────────────────────────────

def generate_i2v(start_frame, prompt, frame_count, seed=None):
    """Generate a single i2v clip via ComfyUI LTX-2."""
    url = f"{COMFYUI_URL}/workflows/{VIDEO_WORKFLOW}"
    data = {
        "prompt": prompt,
        "negative_prompt": NEGATIVE_PROMPT,
        "frame_count": str(frame_count),
    }
    if seed is not None:
        data["seed"] = str(seed)

    with open(start_frame, "rb") as img_file:
        files = {"image": (start_frame.name, img_file, "image/png")}
        response = requests.post(url, data=data, files=files, timeout=VIDEO_TIMEOUT)

    if response.status_code == 200 and len(response.content) > 10000:
        return response.content
    else:
        print(f"  ERROR: HTTP {response.status_code}, {len(response.content)} bytes")
        if response.status_code != 200:
            print(f"  {response.text[:300]}")
        return None


def generate_clips(shots, frames_dir, clips_dir, pipeline_label="i2v"):
    """Generate LTX-2 i2v clips using start frames."""
    clips_dir.mkdir(parents=True, exist_ok=True)
    total = len(shots)
    results = {}
    start_time = time.time()

    # Verify all frames exist
    missing = []
    for shot in shots:
        fname = f"frame{shot['id']:02d}_{safe_name(shot['name'])}.png"
        frame_path = frames_dir / fname
        if not frame_path.exists():
            missing.append(fname)
    if missing:
        print(f"ERROR: Missing start frames ({len(missing)}):")
        for m in missing:
            print(f"  {m}")
        print("Run --frames-only first to generate start frames.")
        return {}

    total_duration = sum(s["duration"] for s in shots)
    print(f"Phase 2: Generating {total} LTX-2 i2v clips")
    print(f"Target duration: {total_duration}s ({total} clips)")
    print(f"Output: {clips_dir}")
    print(f"Backend: ComfyUI {VIDEO_WORKFLOW} ({FPS}fps)")
    print()

    for i, shot in enumerate(shots):
        shot_id = shot["id"]
        name = shot["name"]
        duration = shot["duration"]
        video_prompt = shot["video_prompt"]
        frame_count = duration_to_frame_count(duration)
        sname = safe_name(name)

        frame_path = frames_dir / f"frame{shot_id:02d}_{sname}.png"
        output_name = f"clip{shot_id:02d}_{sname}"

        print(f"{'='*60}")
        print(f"--- {output_name} ({duration}s, {frame_count} frames) [{i+1}/{total}] ---")
        print(f"{'='*60}")
        print(f"  Frame: {frame_path.name}")
        print(f"  Video prompt ({len(video_prompt)} chars):")
        print(f"  {video_prompt[:200]}...")
        print()

        t0 = time.time()
        video_bytes = generate_i2v(
            start_frame=frame_path,
            prompt=video_prompt,
            frame_count=frame_count,
        )
        elapsed = time.time() - t0

        if video_bytes:
            out_path = clips_dir / f"{output_name}.mp4"
            with open(out_path, "wb") as f:
                f.write(video_bytes)

            meta = {
                "shot_id": shot_id,
                "shot_name": name,
                "duration_s": duration,
                "frame_count": frame_count,
                "workflow": VIDEO_WORKFLOW,
                "fps": FPS,
                "video_prompt": video_prompt,
                "frame_prompt": shot["frame_prompt"],
                "negative_prompt": NEGATIVE_PROMPT,
                "start_frame": str(frame_path),
                "elapsed_s": round(elapsed, 1),
                "bytes": len(video_bytes),
                "pipeline": pipeline_label,
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

    total_elapsed = time.time() - start_time
    print(f"{'='*60}")
    print(f"Phase 2 SUMMARY — {total} clips in {total_elapsed/60:.1f}m")
    print(f"{'='*60}")
    for shot in shots:
        sid = shot["id"]
        status = results.get(sid, "SKIPPED")
        print(f"  {shot['name']}: {status}")
    print()
    return results


# ─── CLI ──────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="SC03 i2v test pipeline")
    parser.add_argument("--dev", action="store_true", help="Use Flux 2 Dev (high fidelity) instead of Klein (fast draft)")
    parser.add_argument("--frames-only", action="store_true", help="Phase 1 only: generate start frames")
    parser.add_argument("--clips-only", action="store_true", help="Phase 2 only: generate i2v clips (frames must exist)")
    parser.add_argument("--shot", type=int, help="Generate a single shot by ID")
    args = parser.parse_args()

    # Select model config based on --dev flag
    if args.dev:
        draft_name = "dev_i2v_draft"
        workflow = "flux2-t2i"       # Auto-routes to flux2-dev-multiref
        steps = 20
        frame_timeout = 300          # Dev is ~150s warm, can spike to 270s cold
        model_label = "Dev"
    else:
        draft_name = "klein_i2v_draft"
        workflow = "flux2-klein-t2i"  # Auto-routes to flux2-klein-multiref
        steps = 12
        frame_timeout = 120
        model_label = "Klein"

    output_dir = SCENE_DIR / draft_name
    frames_dir = output_dir / "frames"
    clips_dir = output_dir / "clips"
    pipeline_label = f"{model_label.lower()}_i2v"

    # Filter shots if --shot specified
    shots = SHOTS
    if args.shot:
        shots = [s for s in SHOTS if s["id"] == args.shot]
        if not shots:
            print(f"ERROR: Shot {args.shot} not found (valid: 1-{len(SHOTS)})")
            sys.exit(1)
        print(f"Single shot mode: shot {args.shot}")

    # Health check
    try:
        r = requests.get(f"{COMFYUI_URL}/health", timeout=5)
        if r.status_code != 200:
            print(f"ERROR: ComfyUI not healthy: {r.text}")
            sys.exit(1)
    except Exception as e:
        print(f"ERROR: ComfyUI not reachable at {COMFYUI_URL}: {e}")
        sys.exit(1)

    print(f"SC03 {model_label}→i2v Test — Storage Room")
    print(f"{'='*60}")
    total_duration = sum(s["duration"] for s in shots)
    print(f"Shots: {len(shots)}, Target duration: {total_duration}s")
    print(f"Model: Flux 2 {model_label} ({steps} steps)")
    print(f"Output: {output_dir}")
    print()

    output_dir.mkdir(parents=True, exist_ok=True)

    if args.clips_only:
        # Phase 2 only
        generate_clips(shots, frames_dir, clips_dir, pipeline_label)
    elif args.frames_only:
        # Phase 1 only
        backend = ComfyUIImageBackend(
            base_url=COMFYUI_URL,
            workflow=workflow,
            timeout=frame_timeout,
        )
        generate_frames(shots, backend, frames_dir, steps=steps, use_dev=args.dev)
    else:
        # Both phases
        backend = ComfyUIImageBackend(
            base_url=COMFYUI_URL,
            workflow=workflow,
            timeout=frame_timeout,
        )
        frame_results = generate_frames(shots, backend, frames_dir, steps=steps, use_dev=args.dev)

        # Check if any frames failed
        failed = [k for k, v in frame_results.items() if "FAILED" in v]
        if failed:
            print(f"WARNING: {len(failed)} frames failed — skipping those clips")
            shots = [s for s in shots if s["id"] not in failed]

        if shots:
            generate_clips(shots, frames_dir, clips_dir, pipeline_label)
        else:
            print("No successful frames — skipping Phase 2")


if __name__ == "__main__":
    main()
