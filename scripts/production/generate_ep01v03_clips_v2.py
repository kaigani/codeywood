#!/usr/bin/env python3
"""
EP01 v03 "Handler" — Video Clip Generation v2

Generates all video clips from locked production frames using LTX-2.3 Fast.
Each clip combines visual motion + ambient audio direction in a single prompt.
Dialogue is layered in post — NOT baked into generation.

Non-AI clips:
  - Shot 5 (title card): ffmpeg text overlay
  - Shot 25 (black hold): ffmpeg black frame

Workflow: ltx2-3-fast (ComfyUI, local, $0.00)
  - first_frame: production frame PNG (1280x720)
  - prompt: motion + audio cues (no music)
  - duration: seconds
  - seed: reproducibility

Pipeline: frames/ → clips/ → (post: dialogue TTS + assembly)
"""

import subprocess
import sys
import time
from pathlib import Path

import requests

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
COMFYUI_BASE = "http://192.168.1.181:8100"
WORKFLOW = "ltx2-3"

PROJECT = Path(__file__).resolve().parents[2] / "projects" / "stray-signal"
FRAMES_DIR = PROJECT / "PRODUCTION" / "EP01_v03" / "frames"
CLIPS_DIR = PROJECT / "PRODUCTION" / "EP01_v03" / "clips"

NEGATIVE = (
    "blurry, oversaturated, pixelated, low resolution, distorted, noise, "
    "watermark, text, logo, subtitles, deformed, extra limbs, photograph, "
    "photorealistic, live action, music, soundtrack, musical instruments"
)

# Shared style suffix for all prompts
STYLE_TAG = "Stylized sci-fi animation, bold ink outlines, cel-shaded coloring."


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def submit_job(params, files=None):
    """Submit a job and return the job_id immediately (non-blocking)."""
    url = f"{COMFYUI_BASE}/workflows/{WORKFLOW}"
    if files:
        resp = requests.post(url, data=params, files=files)
    else:
        resp = requests.post(url, data=params)
    resp.raise_for_status()
    return resp.json()["job_id"]


def poll_jobs(jobs, timeout=600):
    """Poll a dict of {name: (job_id, start_time, out_path)} until all complete.
    Returns list of failed names."""
    pending = dict(jobs)  # copy
    failed = []
    while pending:
        still_pending = {}
        for name, (job_id, start_time, out_path) in pending.items():
            elapsed = time.time() - start_time
            if elapsed > timeout:
                print(f"  {name}: TIMEOUT ({elapsed:.0f}s)")
                failed.append(name)
                continue
            try:
                status = requests.get(f"{COMFYUI_BASE}/jobs/{job_id}").json()
            except Exception as e:
                still_pending[name] = (job_id, start_time, out_path)
                continue
            st = status.get("status", "unknown")
            if st == "completed":
                data = requests.get(f"{COMFYUI_BASE}/jobs/{job_id}/result").content
                save(data, out_path)
                print(f"  {name}: Done ({elapsed:.0f}s)")
            elif st in ("error", "failed"):
                print(f"  {name}: FAILED — {status.get('error')}")
                failed.append(name)
            else:
                still_pending[name] = (job_id, start_time, out_path)
        pending = still_pending
        if pending:
            time.sleep(5)
    return failed


def save(data, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as f:
        f.write(data)
    kb = len(data) / 1024
    print(f"    Saved: {path.name} ({kb:.0f} KB)")
    return path


def make_title_card(out_path, duration=3):
    """Generate title card via ffmpeg — cyan wireframe text on black."""
    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", f"color=black:s=1920x1080:d={duration}:r=25",
        "-f", "lavfi", "-i", f"anullsrc=r=44100:cl=stereo:d={duration}",
        "-vf", (
            "drawtext=text='STRAY SIGNAL':fontsize=96:fontcolor=0x00CCCC:"
            "x=(w-text_w)/2:y=(h-text_h)/2:font=Courier"
        ),
        "-c:v", "libx264", "-preset", "fast", "-crf", "18",
        "-c:a", "aac", "-b:a", "128k",
        "-shortest",
        str(out_path),
    ]
    subprocess.run(cmd, capture_output=True, check=True)
    print(f"    Saved: {out_path.name} (ffmpeg title card, {duration}s)")


def make_black_hold(out_path, duration=3):
    """Generate black hold via ffmpeg — silence."""
    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", f"color=black:s=1920x1080:d={duration}:r=25",
        "-f", "lavfi", "-i", f"anullsrc=r=44100:cl=stereo:d={duration}",
        "-c:v", "libx264", "-preset", "fast", "-crf", "18",
        "-c:a", "aac", "-b:a", "128k",
        "-shortest",
        str(out_path),
    ]
    subprocess.run(cmd, capture_output=True, check=True)
    print(f"    Saved: {out_path.name} (ffmpeg black hold, {duration}s)")


# ---------------------------------------------------------------------------
# Clip definitions
#
# frame: filename in frames/ (without .png)
# prompt: motion description + audio cues. No music. Dialogue layered in post.
# ---------------------------------------------------------------------------
CLIPS = [
    # ===================================================================
    # THE GRID — Unease + Rooting (21s, 4 clips)
    # ===================================================================
    {
        "shot": 1,
        "name": "01_cityscape_dawn",
        "duration": 6,
        "seed": 30001,
        "prompt": (
            "Wide establishing shot. Camera holds steady on static tripod. "
            "Massive brutalist concrete blocks rise against cold steel-blue sky. "
            "A single small surveillance drone traces a slow lazy arc across "
            "the upper frame, left to right. Dawn light slowly brightens on "
            "concrete surfaces. No people. Wind shifts shadows on building faces. "
            "Ambient sound: deep 60Hz electrical hum building from silence, "
            "wind through concrete corridors, distant drone buzz. No music. "
            + STYLE_TAG
        ),
    },
    {
        "shot": 2,
        "name": "02_neda_on_grid",
        "duration": 5,
        "seed": 30002,
        "prompt": (
            "Medium shot. A girl in a steel-blue geometric jacket walks forward "
            "on a brutalist concrete street. One or two distant figures in grey "
            "behind her move at the same regulation pace. But her eyes are "
            "different — aware, scanning, tracking without turning her head. "
            "She swallows — dry air. She moves toward a junction ahead. "
            "Ambient sound: boot steps on polymer in uniform rhythm, 60Hz hum, "
            "dry swallow close to mic. No music. "
            + STYLE_TAG
        ),
    },
    {
        "shot": 3,
        "name": "03_neda_at_grate",
        "duration": 5,
        "seed": 30003,
        "prompt": (
            "Medium-wide shot. The girl in steel-blue jacket approaches a "
            "maintenance grate at ground level on a brutalist street. She reaches "
            "it without hesitation. One smooth efficient motion: she crouches and "
            "lifts the polymer grate cover. No checking sight lines — already "
            "checked. Ambient sound: boot steps slowing, polymer creak, "
            "grate scrape beginning. No music. "
            + STYLE_TAG
        ),
    },
    {
        "shot": 4,
        "name": "04_the_drop",
        "duration": 5,
        "seed": 30004,
        "prompt": (
            "Wide shot. A figure in steel-blue jacket crouched at an open "
            "maintenance grate in a brutalist concrete street. She drops below "
            "the surface. The grate slides back into place. The street is empty "
            "again. As if no one was ever there. Wind moves through the corridor. "
            "Ambient sound: grate scrape, brief descent — metal on stone, "
            "60Hz recedes, then silence. No music. "
            + STYLE_TAG
        ),
    },

    # ===================================================================
    # TITLE CARD (3s) — ffmpeg
    # ===================================================================
    {
        "shot": 5,
        "name": "05_title_card",
        "duration": 3,
        "seed": 0,
        "prompt": "",
        "method": "ffmpeg_title",
    },

    # ===================================================================
    # THE SEAM — Descent: Relief (17s, 3 clips)
    # ===================================================================
    {
        "shot": 6,
        "name": "06_descent_cold",
        "duration": 6,
        "seed": 30006,
        "prompt": (
            "Medium shot from behind. A girl in steel-blue jacket descends narrow "
            "polymer steps in a vertical passage. Cold fluorescent strip lights "
            "on smooth walls. She moves steadily downward. Grid-tight posture — "
            "shoulders held, controlled. Everything is cold steel-blue. "
            "Ambient sound: boot steps on polymer with growing echo, 60Hz fading, "
            "drip of condensation. No music. "
            + STYLE_TAG
        ),
    },
    {
        "shot": 7,
        "name": "07_descent_transition",
        "duration": 5,
        "seed": 30007,
        "prompt": (
            "Medium shot. A girl descends steps through a transition zone. "
            "Mixed lighting — cold fluorescent above fading, amber LED string "
            "lights growing from below. Polymer walls giving way to rough stone. "
            "Her shoulders begin to drop — a centimeter. Involuntary. "
            "The echo changes from flat to resonant. "
            "Ambient sound: fluorescent hum dying, first stone echo, "
            "faint distant guitar — someone working through chords. No music. "
            + STYLE_TAG
        ),
    },
    {
        "shot": 8,
        "name": "08_descent_warm",
        "duration": 6,
        "seed": 30008,
        "prompt": (
            "Wide shot. A girl reaches the bottom of stone steps and enters "
            "an underground space. Amber LED string lights criss-crossing overhead "
            "cast warm golden light on everything. She moves forward with the "
            "ease of someone who has been here her whole life. Her posture is "
            "different now — looser, natural. She belongs here. "
            "Ambient sound: guitar clearer, voices carrying at natural distance, "
            "stone echo, warm ambient hum. No music. "
            + STYLE_TAG
        ),
    },

    # ===================================================================
    # THE SEAM — Fen: Dread (16s, 3 clips)
    # ===================================================================
    {
        "shot": 9,
        "name": "09_corridor_approach",
        "duration": 5,
        "seed": 30009,
        "prompt": (
            "Medium shot. A girl in dark fitted jacket walks through an "
            "underground stone corridor. Amber string lights overhead on rough "
            "stone walls. A door and branching corridor visible ahead. She walks "
            "with purpose but begins to slow. Something about the door ahead. "
            "Ambient sound: footsteps on stone, warm Seam ambient, "
            "her pace changes — subtle hesitation. No music. "
            + STYLE_TAG
        ),
    },
    {
        "shot": 10,
        "name": "10_fens_room",
        "duration": 6,
        "seed": 30010,
        "prompt": (
            "Wide doorway shot. A grow-lamp room through a doorway. A figure "
            "seated in absolute stillness — silhouette against green-white light. "
            "Not resting. Sitting the way furniture sits. The figure does not move "
            "at all. In the foreground doorway, a girl stands looking in. She does "
            "not enter. She does not speak. She stands still, watching. "
            "Two distinct lighting zones — warm amber doorway, green-white room. "
            "Ambient sound: near-silence, grow-lamp buzz, faint phantom swipe — "
            "soft repetitive skin-on-nothing. No music. "
            + STYLE_TAG
        ),
    },
    {
        "shot": 11,
        "name": "11_neda_walks_on",
        "duration": 5,
        "seed": 30011,
        "prompt": (
            "Medium shot. A girl in dark jacket walks forward through a stone "
            "corridor toward the camera. Behind her, a faint green-white glow "
            "from a doorway she has passed. Amber string lights ahead. "
            "She walks forward. She does not look back. Jaw tight. "
            "Expression controlled. "
            "Ambient sound: footsteps resume, grow-lamp buzz recedes, "
            "amber ambient returns. No music. "
            + STYLE_TAG
        ),
    },

    # ===================================================================
    # THE SEAM — Briefing: Investment + Silence (22s, 4 clips)
    # Shot 12: listening only (no on-screen speech)
    # Shots 13-14: dialogue prompted for lipsync
    # Shot 15: silence (no speech)
    # ===================================================================
    {
        "shot": 12,
        "name": "12_briefing_intel",
        "duration": 6,
        "seed": 30012,
        "prompt": (
            "Close-up of a girl's face in warm amber light. An underground "
            "stone room with rough-hewn walls and amber string lights. She sits "
            "at a stone table, listening intently. Her expression is controlled, "
            "absorbing every word from someone off-screen. Her eyes track slightly "
            "as she processes information. Then her right hand moves to grip the "
            "edge of the stone table. Her eyes change — not surprise, recognition. "
            "Ambient sound: stone room acoustics, quiet ambient hum, "
            "hand gripping stone table. No music. "
            + STYLE_TAG
        ),
    },
    {
        "shot": 13,
        "name": "13_briefing_volunteer",
        "duration": 5,
        "seed": 30013,
        "prompt": (
            "Close-up of a girl leaning slightly forward at a rough stone table "
            "in an underground room lit by amber string lights. She says "
            "\"I'll go.\" with controlled intensity. Jaw set. Eyes direct, "
            "looking off-screen. Copper-wire braid behind her left ear catches "
            "the amber light. She does not flinch at refusal. "
            "Dialogue: \"I'll go.\" "
            "Ambient sound: stone room acoustics. No music. "
            + STYLE_TAG
        ),
    },
    {
        "shot": 14,
        "name": "14_briefing_argument",
        "duration": 6,
        "seed": 30014,
        "prompt": (
            "Close-up of a girl leaning further forward at a stone table. "
            "Tightest framing. Amber light on brown skin. She says "
            "\"It has to be me. I know the activation sequence. I know the "
            "fuel signs.\" with fierce conviction. Jaw tightens between phrases. "
            "Right fist grips the stone table edge. Not anger — necessity. "
            "She pauses, then says \"That's why it has to be me.\" "
            "Dialogue: \"It has to be me. I know the activation sequence. "
            "I know the fuel signs. That's why it has to be me.\" "
            "Amber light, copper braid catching light. "
            "Ambient sound: stone room acoustics. No music. "
            + STYLE_TAG
        ),
    },
    {
        "shot": 15,
        "name": "15_briefing_silence",
        "duration": 5,
        "seed": 30015,
        "prompt": (
            "Close-up of a girl's face in amber light. The stillness after "
            "conviction. She does not look away. She does not soften. Jaw held. "
            "Eyes steady. Four seconds of absolute stillness. Then — barely "
            "perceptible — the tension in her jaw releases a fraction. "
            "Amber light heavy on rough stone walls. "
            "Ambient sound: silence. Stone room. Four seconds of nothing. "
            "No voices. No music. "
            + STYLE_TAG
        ),
    },

    # ===================================================================
    # THE SEAM — Return: Commitment (15s, 3 clips)
    # ===================================================================
    {
        "shot": 16,
        "name": "16_return_warm",
        "duration": 5,
        "seed": 30016,
        "prompt": (
            "Medium shot. A girl walks with purpose through an underground "
            "stone corridor. Amber string lights on rough stone walls. Dark "
            "fitted jacket, rust underlayer. She passes a branching hallway — "
            "she does not look toward it. She moves toward stone steps ahead. "
            "Decision in every line of her body. "
            "Ambient sound: purposeful footsteps on stone, amber ambient. "
            "No music. "
            + STYLE_TAG
        ),
    },
    {
        "shot": 17,
        "name": "17_return_transition",
        "duration": 5,
        "seed": 30017,
        "prompt": (
            "Medium shot. A girl climbs narrow stone steps. Ascending. "
            "Warm amber light from below fades. Cold steel-blue grows from above. "
            "Her posture shifts — tightening. Shoulders rising. The Grid "
            "performance returning. Rough stone becoming smooth polymer. "
            "Ambient sound: stone steps, amber receding, 60Hz returning — "
            "faint at first, air goes dry. No music. "
            + STYLE_TAG
        ),
    },
    {
        "shot": 18,
        "name": "18_return_surface",
        "duration": 5,
        "seed": 30018,
        "prompt": (
            "Medium shot. A girl emerges into a cold polymer tunnel. Steel-blue "
            "jacket, geometric collar. Cold fluorescent light on her face. "
            "The warmth is gone. Grid posture restored — tight, controlled, "
            "eyes scanning. She moves forward with mission pace. "
            "Ambient sound: 60Hz hum full, polymer under boots, scrubbed air. "
            "No music. "
            + STYLE_TAG
        ),
    },

    # ===================================================================
    # THE GRID WITH PURPOSE — Curiosity + The Turn (36s, 6 clips)
    # ===================================================================
    {
        "shot": 19,
        "name": "19_grid_mission",
        "duration": 6,
        "seed": 30019,
        "prompt": (
            "Wide shot. Brutalist concrete street. A girl in steel-blue jacket "
            "moves with mission energy — faster and more direct than the opening. "
            "Late afternoon, shadows slightly longer. A surveillance drone "
            "overhead — she tracks it without breaking stride. Same world as "
            "the opening but different energy. "
            "Ambient sound: 60Hz returns, Grid ambient, drone buzz, "
            "boot steps — faster, purposeful. No music. "
            + STYLE_TAG
        ),
    },
    {
        "shot": 20,
        "name": "20_corridor_empty",
        "duration": 6,
        "seed": 30020,
        "prompt": (
            "Wide shot. Empty maintenance corridor. Fluorescent strip lighting. "
            "Polymer floor. Vanishing point perspective. End of shift. Every "
            "shadow engineered out. Sterile. Then — not empty. A small figure "
            "appears at the far end. Walking toward camera. Distant, measured. "
            "Ambient sound: 60Hz DROPS OUT completely. Fluorescent buzz only. "
            "Single distant footsteps — measured, careful. No music. "
            + STYLE_TAG
        ),
    },
    {
        "shot": 21,
        "name": "21_kai_approaches",
        "duration": 6,
        "seed": 30021,
        "prompt": (
            "Medium shot. A boy walks toward camera in a maintenance corridor. "
            "Alone. Lean build, shaggy dark hair, concrete grey jacket, tool belt. "
            "In his hand a brushed-aluminum device emits a faint cyan glow that "
            "catches his face and fingers. He is absorbed in the device, unaware "
            "anyone is watching. The cyan glow is a color that does not belong "
            "in this cold sterile world. Measured careful steps. "
            "Ambient sound: single footsteps on polymer, faint device pixel-buzz, "
            "fluorescent hum, no 60Hz. No music. "
            + STYLE_TAG
        ),
    },
    {
        "shot": 22,
        "name": "22_kai_glow_detail",
        "duration": 5,
        "seed": 30022,
        "prompt": (
            "Extreme close-up. A boy's hands holding a brushed-aluminum device. "
            "The screen shows a faint cyan wireframe form. Cyan glow pulses — "
            "faintly, alive. Light catches his fingertips and the polymer surface "
            "below. The device is scratched, dented. The cyan is the only color "
            "in the cold fluorescent frame. Something in this glow that the world "
            "doesn't own. It moves. "
            "Ambient sound: device pixel-buzz close and detailed — the sound of "
            "something alive. Silence around it. No music. "
            + STYLE_TAG
        ),
    },
    {
        "shot": 23,
        "name": "23_neda_watching",
        "duration": 5,
        "seed": 30023,
        "prompt": (
            "Close-up. A girl stands absolutely still in a cold fluorescent "
            "corridor. She watches something ahead and off-screen. A faint cyan "
            "light reflects on her face from something we cannot see. She "
            "recognizes it. Her jaw tightens slowly — the same tell. Eyes narrow "
            "with calculation, recognition, and something she is trying very hard "
            "not to feel. Three seconds of absolute stillness. "
            "Ambient sound: near-silence. 60Hz gone. Just her breathing, close "
            "to mic. No music. "
            + STYLE_TAG
        ),
    },
    {
        "shot": 24,
        "name": "24_neda_moves_forward",
        "duration": 4,
        "seed": 30024,
        "prompt": (
            "Medium shot. A girl in steel-blue jacket stands in a corridor with "
            "distant cyan glow ahead. She takes a step forward. Then another. "
            "She moves toward the cyan glow. Toward the boy who does not know "
            "she is there. Expression resolved from dread into purpose. "
            "Ambient sound: one step, two. Polymer under boots. Then silence. "
            "No music. "
            + STYLE_TAG
        ),
    },

    # ===================================================================
    # BLACK HOLD (3s) — ffmpeg
    # ===================================================================
    {
        "shot": 25,
        "name": "25_black_hold",
        "duration": 3,
        "seed": 0,
        "prompt": "",
        "method": "ffmpeg_black",
    },
]


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        description="Generate EP01 v03 video clips via LTX-2.3 Fast"
    )
    parser.add_argument(
        "--shot", type=int, default=0,
        help="Specific shot number (or 0 for all)"
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--timeout", type=int, default=600,
        help="Per-clip timeout in seconds"
    )
    args = parser.parse_args()

    CLIPS_DIR.mkdir(parents=True, exist_ok=True)

    clips = CLIPS
    if args.shot > 0:
        clips = [c for c in CLIPS if c["shot"] == args.shot]
        if not clips:
            print(f"No shot {args.shot}")
            sys.exit(1)

    if args.dry_run:
        print("=" * 70)
        print("EP01 v03 — Clip Generation (DRY RUN)")
        print(f"Output: {CLIPS_DIR}")
        total_dur = sum(c["duration"] for c in clips)
        print(f"Clips: {len(clips)} | Total duration: {total_dur}s")
        print("=" * 70)
        for c in clips:
            method = c.get("method", "ltx2")
            out = CLIPS_DIR / f"{c['name']}.mp4"
            exists = "EXISTS" if out.exists() else "pending"
            if method.startswith("ffmpeg"):
                print(f"  Shot {c['shot']:2d}: {c['name']} ({c['duration']}s) "
                      f"[{method}] {exists}")
            else:
                frame = FRAMES_DIR / f"{c['name']}.png"
                has_frame = "frame OK" if frame.exists() else "NO FRAME"
                print(f"  Shot {c['shot']:2d}: {c['name']} ({c['duration']}s) "
                      f"[{has_frame}] {exists}")
        sys.exit(0)

    # Health check for LTX clips
    ltx_clips = [c for c in clips if c.get("method", "ltx2") == "ltx2"]
    if ltx_clips:
        try:
            r = requests.get(f"{COMFYUI_BASE}/health", timeout=5)
            if r.status_code != 200:
                print(f"ERROR: ComfyUI not healthy (status {r.status_code})")
                sys.exit(1)
        except Exception as e:
            print(f"ERROR: ComfyUI not reachable: {e}")
            sys.exit(1)

    total = len(clips)
    failed = []

    print("=" * 70)
    print("EP01 v03 — Clip Generation (batch mode)")
    print(f"Output: {CLIPS_DIR}")
    total_dur = sum(c["duration"] for c in clips)
    print(f"Clips: {total} | Total duration: {total_dur}s")
    print("=" * 70)

    # --- Phase 1: ffmpeg clips (instant) ---
    for clip_def in clips:
        method = clip_def.get("method", "ltx2")
        name = clip_def["name"]
        out_path = CLIPS_DIR / f"{name}.mp4"
        if out_path.exists() or method == "ltx2":
            continue
        print(f"\n  Shot {clip_def['shot']}: {name} [{method}]")
        try:
            if method == "ffmpeg_title":
                make_title_card(out_path, duration=clip_def["duration"])
            elif method == "ffmpeg_black":
                make_black_hold(out_path, duration=clip_def["duration"])
        except Exception as e:
            print(f"    FAILED: {e}")
            failed.append(name)

    # --- Phase 2: Submit all LTX jobs ---
    ltx_jobs = {}  # name -> (job_id, start_time, out_path)
    skipped = 0

    print(f"\nSubmitting LTX-2.3 jobs...")
    for clip_def in clips:
        method = clip_def.get("method", "ltx2")
        if method != "ltx2":
            continue

        name = clip_def["name"]
        shot = clip_def["shot"]
        out_path = CLIPS_DIR / f"{name}.mp4"

        if out_path.exists():
            skipped += 1
            continue

        frame_path = FRAMES_DIR / f"{name}.png"
        if not frame_path.exists():
            print(f"  Shot {shot}: {name} — SKIP (no start frame)")
            failed.append(name)
            continue

        params = {
            "prompt": clip_def["prompt"],
            "negative_prompt": NEGATIVE,
            "duration": str(clip_def["duration"]),
            "width": "1920",
            "height": "1080",
            "seed": str(clip_def["seed"]),
            "static_camera": "0",
        }

        try:
            fh = open(frame_path, "rb")
            try:
                files = {"first_frame": (frame_path.name, fh, "image/png")}
                job_id = submit_job(params, files=files)
            finally:
                fh.close()
            ltx_jobs[name] = (job_id, time.time(), out_path)
            print(f"  Shot {shot}: {name} ({clip_def['duration']}s) — submitted [{job_id[:12]}]")
        except Exception as e:
            print(f"  Shot {shot}: {name} — SUBMIT FAILED: {e}")
            failed.append(name)

    if skipped:
        print(f"  ({skipped} clips already exist, skipped)")

    # --- Phase 3: Poll all jobs until done ---
    if ltx_jobs:
        print(f"\nPolling {len(ltx_jobs)} jobs...")
        poll_failed = poll_jobs(ltx_jobs, timeout=args.timeout)
        failed.extend(poll_failed)

    print(f"\n{'=' * 70}")
    if failed:
        print(f"FAILED ({len(failed)}): {', '.join(failed)}")
    generated = total - len(failed) - skipped
    print(f"COMPLETE — {generated} new + {skipped} existing = {total - len(failed)}/{total}")
    print(f"Total duration: {total_dur}s")
    print("=" * 70)
