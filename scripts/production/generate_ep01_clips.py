#!/usr/bin/env python3
"""
Generate EP01 video clips using LTX-2.3 Fast (ltx2-3-fast).

- i2v from approved start frames
- Audio description embedded in every prompt (environmental, no dialogue)
- Negative prompt suppresses music fill
- Clips 1-17, skipping clip 05 (title card → ffmpeg)

Usage:
  python3 generate_ep01_clips.py              # all clips
  python3 generate_ep01_clips.py --clip 1     # single clip
  python3 generate_ep01_clips.py --clip 1,3,7 # multiple
  python3 generate_ep01_clips.py --dry-run    # preview prompts only
  python3 generate_ep01_clips.py --start 6    # resume from clip N
"""

import argparse
import json
import sys
import time
from pathlib import Path

import requests

# ─── Config ───────────────────────────────────────────────────────────────────

COMFYUI_BASE = "http://192.168.1.181:8100"
WORKFLOW     = "ltx2-3-fast"

PROJECT  = Path(__file__).resolve().parents[2] / "projects" / "stray-signal"
FRAMES   = PROJECT / "PRODUCTION" / "EP01_v02" / "frames"
CLIPS_DIR = PROJECT / "PRODUCTION" / "EP01_v02" / "clips"

NEGATIVE_PROMPT = (
    "blurry, oversaturated, pixelated, low resolution, grainy, distorted, "
    "noise, compression artifacts, glitches, watermark, text overlay, "
    "music, background music, instrumental music, soundtrack, score, "
    "melody, musical, cinematic score, ambient music"
)

# ─── Clip manifest ────────────────────────────────────────────────────────────
# Each entry: id, frame filename, duration (s), visual prompt, audio prompt
# Audio prompt is appended to visual: "Sound: [description]."

CLIPS = [

    dict(
        id=1,
        frame="clip_01_corridor_establishing_v2.png",
        duration=10,
        visual=(
            "A wide anamorphic shot of a brutalist maintenance corridor. "
            "A lone boy in a maintenance coverall walks toward camera with "
            "measured, systematic steps. He tilts his head slightly upward "
            "at each overhead fluorescent strip, counting. He stops at a "
            "junction and touches the concrete wall with one hand. "
            "Boot soles echo on polymer floor. Clinical 4500K lighting."
        ),
        audio=(
            "Constant 60Hz fluorescent hum fills the corridor. "
            "Measured boot steps on hard polymer floor, steady cadence. "
            "Faint echo off concrete walls. No music."
        ),
    ),

    dict(
        id=2,
        frame="clip_02_wall_seam_discovery.png",
        duration=8,
        visual=(
            "Close-up of a boy's hands exploring a concrete wall seam. "
            "His thumb runs along the edge where a panel meets surrounding "
            "polymer. He traces the outline of an off-color panel. "
            "His hand goes still — the moment of recognition. "
            "Then he sits down cross-legged on the polymer floor. "
            "Two seconds of stillness."
        ),
        audio=(
            "Fingertips dragging slowly across rough concrete grain. "
            "The faint scrape of a thumbnail finding the panel seam. "
            "Fabric rustle as he sits down. Then stillness — "
            "only the 60Hz hum. No music."
        ),
    ),

    dict(
        id=3,
        frame="clip_03_panel_opens_device.png",
        duration=10,
        visual=(
            "A boy sits cross-legged on a corridor floor, working a wall "
            "panel with a multi-tool. The panel swings open revealing a "
            "maintenance alcove. Inside: a brushed aluminum device with "
            "a real glass screen. He reaches in and picks it up. "
            "His expression shifts subtly as he registers its warmth. "
            "He turns it in his hand. His thumbnail catches a hairline "
            "crack across the lower third of the glass."
        ),
        audio=(
            "Multi-tool scraping metal against the panel edge. "
            "A grinding hinge as the panel swings open. "
            "The specific weight of brushed aluminum lifted from a surface. "
            "Subtle intake of breath. 60Hz hum underneath. No music."
        ),
    ),

    dict(
        id=4,
        frame="clip_04_device_crack_warmth_v2.png",
        duration=6,
        visual=(
            "Extreme close-up of a brushed aluminum device held in a "
            "boy's hands. His thumbnail traces a hairline crack across "
            "the glass. A faint warm glow pulses from inside the device "
            "at the crack edges. His thumb rests on the crack. "
            "The warmth breathes slowly."
        ),
        audio=(
            "The barely audible sound of a thumbnail dragging across "
            "cracked glass — tiny and precise. "
            "A faint electrical warmth hum from inside the device, "
            "like a heartbeat. Near-silence. No music."
        ),
    ),

    # Clip 05 = title card — generated via ffmpeg, skip LTX-2
    # dict(id=5, ...),

    dict(
        id=6,
        frame="clip_06_housing_unit_desk_final.png",
        duration=8,
        visual=(
            "A boy leans over a small desk at night in a compact housing "
            "unit, both hands on a glowing device. Amber desk lamp pools "
            "warmth behind him. The device screen brightens with a loading "
            "bar. Cyan glow mixes with the amber lamp — a new color "
            "that doesn't exist anywhere in the Grid."
        ),
        audio=(
            "Faint drainage conduit sound through a closed window. "
            "The pixel-buzz of old hardware powering up. "
            "A green LED ticking on a charge cable. "
            "Loading bar tone accelerating then cutting to silence. "
            "Amber lamp hum. No music."
        ),
    ),

    dict(
        id=7,
        frame="clip_07_tabs_appears_final.png",
        duration=8,
        visual=(
            "Close-up of a boy's face illuminated from below by cool cyan "
            "light from a device screen he holds in his hands. "
            "Warm amber desk lamp from behind and left. "
            "His eyes are wide open, studying what he sees on the screen. "
            "First encounter — neither frightened nor excited, fully present. "
            "Neither moves first."
        ),
        audio=(
            "Near silence. A faint digital chirp from the device screen — "
            "high register, brief, like a greeting. "
            "The desk lamp hums. The boy's breathing is measured, controlled. "
            "No music."
        ),
    ),

    dict(
        id=8,
        frame="clip_08_delete_sequence_final.png",
        duration=10,
        visual=(
            "Tight close-up of a device screen showing a DELETE prompt "
            "in red and a wireframe cyan cat. The cat looks at the DELETE "
            "text, then looks upward toward the viewer. It walks to the "
            "corner of the screen and tucks its paws underneath, settling "
            "with deliberate patience. It stares at the opposite wall. "
            "Three seconds of nothing. Then fingers navigate to close "
            "the settings menu. The DELETE prompt disappears. "
            "The cat does not acknowledge this."
        ),
        audio=(
            "Compact government UI tones — a short sterile click sequence. "
            "Then silence. The 60Hz hum underneath during the three-second hold. "
            "Another click as the menu closes. Then only the hum. No music."
        ),
    ),

    dict(
        id=9,
        frame="clip_09_multitool_down_v1.png",
        duration=9,
        visual=(
            "A boy in a housing unit at night. He looks at the multi-tool "
            "in his hand, then looks at the device where a small wireframe "
            "cat sits in the corner ignoring him. He places the multi-tool "
            "down on the desk surface — deliberate, not dropping. "
            "His hand stays on the desk for a beat. "
            "His shoulders drop one centimeter. The first physical release."
        ),
        audio=(
            "The specific metallic sound of a multi-tool placed on a "
            "hard desk surface — controlled, deliberate. "
            "A soft exhale. Fabric shifting as shoulders drop. "
            "The device emits a faint pixel-buzz. Amber lamp hum. No music."
        ),
    ),

    dict(
        id=10,
        frame="clip_10_tabs_reads_maps_final.png",
        duration=10,
        visual=(
            "A boy at a desk watches a device screen. A wireframe cyan cat "
            "moves methodically through a directory of map files — focused, "
            "not looking up. The boy watches for five seconds, his expression "
            "shifting from guarded to the absence of resistance. "
            "Then he looks away first. He turns to his own datapad "
            "and starts making a notation. Not looking at the device. "
            "Aware of the device."
        ),
        audio=(
            "Device scrolling sounds — digital texture, soft and rapid. "
            "The cat emits brief focused chirps as it navigates files. "
            "The boy shifts his weight — fabric sound. "
            "Pen on datapad paper. Amber lamp hum underneath. No music."
        ),
    ),

    dict(
        id=11,
        frame="clip_11_tabs_points_northeast_final.png",
        duration=10,
        visual=(
            "Tight close-up of a device screen. A wireframe cyan cat "
            "holds a pointing posture — body oriented, weight forward, "
            "paw extended northeast. Warm directional pulse rings "
            "radiate outward across the screen. Hands enter frame "
            "holding a datapad map. A finger traces to an unmapped "
            "section covered in question marks. The finger stops on "
            "the gap. A thumb finds the hairline crack on the device screen."
        ),
        audio=(
            "A warm tonal pulse from the device — low and resonant, "
            "like a tuning fork, repeating with the pulse rings. "
            "It sounds like attention being paid. "
            "Pen on paper as the finger traces. "
            "Near-silence around it. No music."
        ),
    ),

    dict(
        id=12,
        frame="clip_12_thats_my_gap.png",
        duration=10,
        visual=(
            "Close-up of a boy's face illuminated by mixed amber and cyan "
            "light. He speaks — the first and only voice in the episode. "
            "Quiet, to himself: 'Sector twelve. That's my gap.' "
            "His eyes don't leave the map. His thumb is on the device crack. "
            "Hold on his face for two beats after the line."
        ),
        audio=(
            "A boy's voice, murmured quietly to himself: "
            "'Sector twelve. That's my gap.' "
            "Then complete silence. The ambient hum has been gone since "
            "he started speaking. Two beats of silence after the line. "
            "No music."
        ),
    ),

    dict(
        id=13,
        frame="clip_13_kai_sleeps_device_dark.png",
        duration=7,
        visual=(
            "A boy asleep at a desk, head on his arms. A device sits dark "
            "in his loosely curled hand. The room is nearly black — only "
            "faint blue-grey light from a window. Stillness. His breathing. "
            "Then the device screen brightens slowly. Cyan glow builds, "
            "casting light on his sleeping face and hand. "
            "The light changes the room."
        ),
        audio=(
            "The sound of slow, deep breathing — asleep. "
            "Near total silence in the room. "
            "Then a whisper-sound from the device as the screen wakes — "
            "a soft electrical presence, barely there. "
            "The faintest 60Hz tone returning. No music."
        ),
    ),

    dict(
        id=14,
        frame="clip_14_tabs_paw_at_glass_final.png",
        duration=12,
        visual=(
            "A device screen showing a single glowing cyan paw print "
            "centered on the dark glass. In the screen's reflection: "
            "a boy sleeping, his face lit by the device's glow. "
            "Hold on the paw print and the sleeping reflection. "
            "Then the screen dims slowly. Darkness returns. "
            "The last visible thing: the faintest cyan edge "
            "before the screen goes fully dark."
        ),
        audio=(
            "The faintest pixel-tick sound — like a small weight "
            "pressing against glass from the inside. "
            "Then nothing. The screen dimming produces a soft "
            "descending electrical tone. Silence. No music."
        ),
    ),

    dict(
        id=15,
        frame="clip_15_morning_corridor_return.png",
        duration=10,
        visual=(
            "Wide shot of the same brutalist corridor from the opening. "
            "A boy stands closer to camera now. He looks at a map — "
            "route to Sector 12, covered in question marks. "
            "He looks at the device in his other hand. "
            "A wireframe cyan cat on the screen is already oriented "
            "forward, already waiting. His free hand moves to his pocket. "
            "Body ahead of decision."
        ),
        audio=(
            "The 60Hz corridor hum returns — the same as the opening, "
            "but the boy's boots don't move yet. "
            "A brief warm device tone — TABS present. "
            "Then boots on polymer: purposeful, not counting. No music."
        ),
    ),

    dict(
        id=16,
        frame="clip_16_new_mark_on_map_final.png",
        duration=8,
        visual=(
            "Close-up of a boy's hands holding a battered datapad "
            "with a hand-drawn sector map. He holds a pen over the map "
            "and makes a mark he hasn't made before — not a notation, "
            "not a symbol from his system. Something new. "
            "His hand is steady. He caps the pen. Puts it away. "
            "The mark sits on the map — small, different, irreversible."
        ),
        audio=(
            "The pen uncapping — a small plastic click. "
            "Pen on paper: the specific scratch of a new mark being made, "
            "deliberate and short. The pen capping again. "
            "Corridor hum underneath. No music."
        ),
    ),

    dict(
        id=17,
        frame="clip_17_he_goes_v2.png",
        duration=7,
        visual=(
            "Wide shot of a brutalist corridor. A boy walks away from "
            "camera toward the vanishing point. Measured steps but with "
            "purpose — not counting fluorescent strips anymore. "
            "The corridor gradually absorbs him. A faint cyan glow "
            "from the device in his hand is the last warm accent "
            "as he recedes. Cut to black."
        ),
        audio=(
            "Boot steps receding down the corridor — the same polymer floor "
            "as the opening, but the cadence is different: going somewhere. "
            "60Hz hum. The faintest TABS chirp from the device. "
            "Steps get quieter. Silence. Then black. No music."
        ),
    ),
]


# ─── API helpers ──────────────────────────────────────────────────────────────

def submit_and_wait(params, files, timeout=900, poll_interval=5):
    url = f"{COMFYUI_BASE}/workflows/{WORKFLOW}"
    resp = requests.post(url, data=params, files=files)
    resp.raise_for_status()
    job = resp.json()
    job_id = job["job_id"]
    print(f"  job {job_id} (pos {job.get('position', '?')})")

    deadline = time.time() + timeout
    polls = 0
    while time.time() < deadline:
        s = requests.get(f"{COMFYUI_BASE}/jobs/{job_id}").json()
        polls += 1
        if s["status"] == "completed":
            elapsed = time.time() - (deadline - timeout)
            print(f"  done in {elapsed:.0f}s")
            return requests.get(f"{COMFYUI_BASE}/jobs/{job_id}/result").content
        if s["status"] == "error":
            raise RuntimeError(f"Job failed: {s.get('error')}")
        if polls % 6 == 0:
            elapsed = time.time() - (deadline - timeout)
            print(f"  ... {elapsed:.0f}s elapsed")
        time.sleep(2 if polls <= 5 else poll_interval)

    raise TimeoutError(f"Job {job_id} timed out after {timeout}s")


def generate_clip(clip, output_dir):
    frame_path = FRAMES / clip["frame"]
    if not frame_path.exists():
        raise FileNotFoundError(f"Frame not found: {frame_path}")

    # Combine visual + audio prompts
    full_prompt = f"{clip['visual'].strip()} {clip['audio'].strip()}"

    params = {
        "prompt": full_prompt,
        "negative_prompt": NEGATIVE_PROMPT,
        "duration": str(clip["duration"]),
        "width":  "1280",
        "height": "720",
        "seed":   str(clip["id"] * 1000 + 42),
    }

    with open(frame_path, "rb") as fh:
        files = {"first_frame": (frame_path.name, fh, "image/png")}
        data = submit_and_wait(params, files)

    out_path = output_dir / f"clip_{clip['id']:02d}_{Path(clip['frame']).stem.replace('_final','').replace('_v2','')}.mp4"
    with open(out_path, "wb") as f:
        f.write(data)

    mb = len(data) / (1024 * 1024)
    print(f"  saved: {out_path.name} ({mb:.1f}MB)")

    meta = {
        "clip_id": clip["id"],
        "frame": clip["frame"],
        "duration_s": clip["duration"],
        "prompt": full_prompt,
        "negative_prompt": NEGATIVE_PROMPT,
        "workflow": WORKFLOW,
        "bytes": len(data),
    }
    with open(out_path.with_suffix(".json"), "w") as f:
        json.dump(meta, f, indent=2)

    return out_path


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--clip",    help="Comma-separated clip IDs to generate")
    parser.add_argument("--start",   type=int, help="Resume from clip N")
    parser.add_argument("--dry-run", action="store_true", help="Print prompts only")
    args = parser.parse_args()

    # Health check
    if not args.dry_run:
        try:
            h = requests.get(f"{COMFYUI_BASE}/health", timeout=5).json()
            if not h.get("comfyui_reachable"):
                print("ERROR: ComfyUI not reachable"); sys.exit(1)
            print(f"ComfyUI: OK  ({WORKFLOW})")
        except Exception as e:
            print(f"ERROR: {e}"); sys.exit(1)

    # Select clips
    clip_map = {c["id"]: c for c in CLIPS}

    if args.clip:
        ids = [int(x.strip()) for x in args.clip.split(",")]
    elif args.start:
        ids = [c["id"] for c in CLIPS if c["id"] >= args.start]
    else:
        ids = [c["id"] for c in CLIPS]

    invalid = [i for i in ids if i not in clip_map]
    if invalid:
        print(f"ERROR: Unknown clip IDs: {invalid}"); sys.exit(1)

    targets = [clip_map[i] for i in ids]

    if args.dry_run:
        for clip in targets:
            print(f"\n{'='*60}")
            print(f"CLIP {clip['id']:02d} — {clip['frame']}  ({clip['duration']}s)")
            print(f"{'='*60}")
            print(f"VISUAL: {clip['visual']}")
            print(f"AUDIO:  {clip['audio']}")
        return

    CLIPS_DIR.mkdir(parents=True, exist_ok=True)
    print(f"\nGenerating {len(targets)} clips → {CLIPS_DIR}")
    print(f"Total duration: {sum(c['duration'] for c in targets)}s\n")

    t0 = time.time()
    results = {}

    for i, clip in enumerate(targets):
        cid = clip["id"]
        print(f"\n{'='*60}")
        print(f"CLIP {cid:02d} — {clip['duration']}s  [{i+1}/{len(targets)}]")
        print(f"{'='*60}")

        try:
            generate_clip(clip, CLIPS_DIR)
            results[cid] = "OK"
        except Exception as e:
            print(f"  ERROR: {e}")
            results[cid] = f"FAILED: {e}"

        # ETA
        elapsed = time.time() - t0
        done = i + 1
        if done < len(targets):
            avg = elapsed / done
            remaining = avg * (len(targets) - done)
            print(f"  [{done}/{len(targets)} done — ~{remaining/60:.0f}m remaining]")

    total = time.time() - t0
    print(f"\n{'='*60}")
    print(f"DONE — {len(targets)} clips in {total/60:.1f}m  ($0.00)")
    print(f"{'='*60}")
    for clip in targets:
        cid = clip["id"]
        print(f"  clip {cid:02d}: {results.get(cid, 'SKIPPED')}")


if __name__ == "__main__":
    main()
