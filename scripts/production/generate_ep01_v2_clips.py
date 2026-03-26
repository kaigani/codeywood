#!/usr/bin/env python3
"""
EP01 "INTAKE" v2 — Video Clip Generation

Generates all video clips from keyframes + pre-mixed audio using LTX-2.3.
Audio-first pipeline: each clip gets its pre-mixed WAV as the `audio` param.
Dialogue text is ALSO included in the video prompt for lipsync reinforcement.

Non-AI clips:
  - Clip 26 (black hold): ffmpeg black frame with silence

Workflow: ltx2-3 (ComfyUI, local, $0.00)
  - first_frame: keyframe PNG
  - audio: pre-mixed WAV (dialogue + ambient + SFX)
  - prompt: motion + quoted dialogue reinforcement
  - duration: derived from audio length

Usage:
    python generate_ep01_v2_clips.py --dry-run
    python generate_ep01_v2_clips.py --clip 6
    python generate_ep01_v2_clips.py              # all clips
    python generate_ep01_v2_clips.py --force       # regenerate existing
"""

import argparse
import struct
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

PROJECT = Path(__file__).resolve().parents[2] / "projects" / "stray-signal-v2"
PRODUCTION = PROJECT / "PRODUCTION" / "EP01"
FRAMES_V02 = PRODUCTION / "frames_v02"
FRAMES_V03 = PRODUCTION / "frames_v03"
AUDIO_MIX_DIR = PRODUCTION / "audio" / "clip_mixes"
CLIPS_DIR = PRODUCTION / "clips_v2"

NEGATIVE = (
    "blurry, oversaturated, pixelated, low resolution, distorted, noise, "
    "watermark, text, logo, subtitles, deformed, extra limbs, photograph, "
    "photorealistic, live action, music, soundtrack, musical instruments"
)

STYLE_TAG = "Stylized sci-fi animation, bold ink outlines, cel-shaded coloring."


# ---------------------------------------------------------------------------
# Frame paths (from clip_frame_mapping_v2.yaml)
# ---------------------------------------------------------------------------
FRAME_MAP = {
    1:  FRAMES_V02 / "SC01 Keyframes — Bureau" / "001_A_man_sits_at_a_desk_in_a_modern_office_filled_bD2rRPOO.png",
    2:  FRAMES_V02 / "SC01 Keyframes — Bureau" / "002_A_man_with_brown_hair_and_brown_eyes_wears_a_gray_q-FORTUb.png",
    3:  FRAMES_V02 / "SC01 Keyframes — Bureau" / "004_A_man_stands_in_an_empty_office_holding_a_dark_3mNMDKTr.png",
    4:  FRAMES_V02 / "SC02 Keyframes — Relay Closet" / "001_A_young_man_in_a_grey_uniform_stands_in_a_dimly_ep5hJqwk.png",
    5:  FRAMES_V02 / "SC02 Keyframes — Relay Closet" / "003_In_a_cyberpunk_style_a_dimly_lit_server_room_6jdaY2Bt.png",
    6:  FRAMES_V03 / "V2 SC02 New Keyframes" / "001_In_a_gritty_stylized_animation_a_man_with_brown_1K3kiaej.png",
    7:  FRAMES_V03 / "V2 SC02 New Keyframes" / "002_In_a_digital_art_style_a_wireframe_hologram_of_a_uqIHJms-.png",
    8:  FRAMES_V03 / "V2 SC02 New Keyframes" / "003_A_man_with_brown_hair_and_brown_eyes_is_shown_0znYadMB.png",
    9:  FRAMES_V02 / "SC02 Keyframes — Relay Closet" / "006_A_man_kneels_in_a_dimly_lit_server_room_ML5x0LLX.png",
    10: FRAMES_V03 / "V2 SC03 New Keyframes" / "001_A_man_stands_in_a_desolate_urban_landscape_a_0b3RIEVU.png",
    11: FRAMES_V03 / "V2 SC03 New Keyframes" / "002_In_a_cinematic_style_a_lone_man_walks_down_a_3BO6Xw0g.png",
    12: FRAMES_V03 / "V2 SC04 New Keyframes" / "001_In_a_gritty_underground_bar_the_walls_are_bV-dRRzs.png",
    13: FRAMES_V03 / "V2 SC04 New Keyframes" / "002_In_a_retro-futuristic_style_a_man_in_a_gray_i4o3Wliy.png",
    14: FRAMES_V03 / "V2 SC04 New Keyframes" / "005_In_a_retro-futuristic_style_four_polygonal_cats_aAwWE1FG.png",
    15: FRAMES_V03 / "V2 SC04 New Keyframes" / "003_A_woman_with_brown_hair_and_brown_eyes_looks_Zb1Ng6BI.png",
    16: FRAMES_V03 / "V2 SC04 New Keyframes" / "004_In_a_gritty_comic_book_style_a_man_with_brown_PisSOWQH.png",
    17: FRAMES_V03 / "Stray_Signal_V2_LSAki7hC.png",
    18: FRAMES_V03 / "V2 SC04 New Keyframes" / "005_In_a_retro-futuristic_style_four_polygonal_cats_aAwWE1FG.png",  # fallback = clip 14
    19: FRAMES_V03 / "V2 SC04 New Keyframes" / "006_In_a_futuristic_bar_style_the_scene_depicts_a_PWEtow9Q.png",
    20: FRAMES_V03 / "V2 SC04 New Keyframes" / "007_A_woman_with_brown_hair_and_brown_eyes_wearing_a_ahYxghJx.png",
    21: FRAMES_V03 / "V2 SC04 New Keyframes" / "002_In_a_retro-futuristic_style_a_man_in_a_gray_i4o3Wliy.png",  # fallback = clip 13
    22: FRAMES_V02 / "SC05+SC06 Keyframes — Back Room + Bar Tag" / "001_In_a_stylized_anime_aesthetic_a_man_sleeps_on_a_MMD-oYTP.png",
    23: FRAMES_V02 / "SC05+SC06 Keyframes — Back Room + Bar Tag" / "002_A_sleeping_man_rests_on_a_pillow_with_a_tdeKblbu.png",
    24: FRAMES_V03 / "V2 SC06 New Keyframes" / "001_In_a_retro-futuristic_style_a_woman_stands_jJ5qqC6i.png",
    25: FRAMES_V03 / "V2 SC06 New Keyframes" / "002_In_a_comic_book_style_a_woman_with_brown_hair_CSrnkmie.png",
}


# ---------------------------------------------------------------------------
# Clip definitions
# ---------------------------------------------------------------------------
CLIPS = [
    # ===================================================================
    # SC01 — BUREAU OF ALGORITHMIC STANDARDS (18s, 3 clips)
    # ===================================================================
    {
        "id": 1, "name": "bureau_establishing", "seed": 40001,
        "prompt": (
            "Wide establishing shot. Camera holds steady on static tripod. "
            "A man in grey regulation uniform sits at a perfectly ordered desk "
            "in a sterile institutional office. Flat fluorescent overhead lighting, "
            "grey-blue walls, green data displays along back wall. He types steadily, "
            "meticulous posture. His eyes scan the screen left to right. Data displays "
            "behind him cycle slowly. Static camera, locked off, perfectly symmetrical. "
            "Sound: 60Hz server hum, soft keystrokes, institutional quiet. " + STYLE_TAG
        ),
    },
    {
        "id": 2, "name": "glenn_spots_anomaly", "seed": 40002,
        "prompt": (
            "Close-up of a man's face in flat fluorescent light. He leans forward "
            "slightly. His eyes narrow — not alarm, recognition. His head tilts. "
            "He says to himself, matter-of-fact: \"That's not supposed to do that.\" "
            "Flat delivery, like noting a parking violation. His expression shifts "
            "from neutral to quiet fascination. Green data reflections on his face. "
            "Sound: server hum, keystrokes stop, brief silence. " + STYLE_TAG
        ),
    },
    {
        "id": 3, "name": "glenn_leaves_mug", "seed": 40003,
        "prompt": (
            "Medium shot. A man in grey uniform stands at his desk. He picks up "
            "a ceramic mug with one hand. Places it back down precisely centered, "
            "handle at the exact same angle. A deliberate, careful placement. He "
            "straightens, turns, and walks out of frame to the right. The desk "
            "remains perfectly ordered behind him. Camera holds on the empty, "
            "symmetrical desk for a beat. Sound: chair movement, ceramic on desk, "
            "footsteps receding. " + STYLE_TAG
        ),
    },

    # ===================================================================
    # SC02 — RELAY CLOSET (30s, 6 clips)
    # ===================================================================
    {
        "id": 4, "name": "relay_closet_enter", "seed": 40004,
        "prompt": (
            "Medium shot from inside a dark room. A man in grey uniform steps "
            "through the doorway, backlit by institutional corridor light behind "
            "him. The room is dark — tangled cable bundles, dead server racks, dust. "
            "Single overhead tube flickers. He looks around — scanning left, then "
            "right. Sound: door creak, footstep on concrete, flickering tube buzz. " + STYLE_TAG
        ),
    },
    {
        "id": 5, "name": "cats_revealed", "seed": 40005,
        "prompt": (
            "Wide shot of a dark server room interior. Four small glowing wireframe "
            "cats — cyan on a shelf center, purple emerging from cables left, pale "
            "white on a junction box right, amber stretching from a server rack. "
            "The cyan cat drops from the upper shelf onto the rack. Lands silently. "
            "Sits. Chirps once — a rising two-tone. The purple one emerges slowly. "
            "The amber one stretches and yawns. Four colored glows pulse in the dark. "
            "Sound: chirp (rising two-tone), white noise yawn, server hum. " + STYLE_TAG
        ),
    },
    {
        "id": 6, "name": "glenn_alphabetized", "seed": 40006,
        "prompt": (
            "Close-up of a man's face in cyan light from below. Dark room with "
            "cables behind him. He is crouching — eye level lower than standing. "
            "He says quietly, almost offended: \"You alphabetized the packet headers.\" "
            "A small chirp is heard. Beat. He continues: \"Nobody alphabetizes "
            "packet headers.\" His expression shifts through offense, then wonder, "
            "then something he can't name. Cyan glow pulses on his skin. "
            "Sound: tabs chirp, dark room ambience. " + STYLE_TAG
        ),
    },
    {
        "id": 7, "name": "tabs_bolt_line", "seed": 40007,
        "prompt": (
            "Detail shot — close on a metal surface in a dark room. A small cyan "
            "wireframe cat extends one paw and pushes scattered bolts into a neat "
            "line. One by one, methodically, each bolt nudged into alignment. Five "
            "bolts, perfectly spaced. The cat sits back. Chirps once. The bolts "
            "gleam faintly in cyan light. Sound: small metallic sounds, chirp. " + STYLE_TAG
        ),
    },
    {
        "id": 8, "name": "glenn_smile", "seed": 40008,
        "prompt": (
            "Close-up of a man's face, lit by faint cyan glow from below. Dark room. "
            "His hand goes to his mouth. He's smiling — and doesn't know why. He "
            "touches his face like he's not sure what it's doing. His hand drops. The "
            "smile stays. He says: \"You're not supposed to be here.\" But the smile "
            "doesn't leave. Cyan glow pulses gently on his face. "
            "Sound: quiet room, gentle chirps. " + STYLE_TAG
        ),
    },
    {
        "id": 9, "name": "glenn_decision", "seed": 40009,
        "prompt": (
            "Medium shot. A man crouches in a dark server room. Four small colored "
            "glows around him — cyan, purple, pale, amber. Doorway with corridor "
            "light behind him. He looks at the cats. Looks at the door. Looks back "
            "at the cats. He says to himself: \"I should file this.\" He does not "
            "move toward the door. He stays. The decision is in the not-moving. "
            "Sound: room ambience, purring begins. " + STYLE_TAG
        ),
    },

    # ===================================================================
    # SC03 — STREETS (14s, 2 clips)
    # ===================================================================
    {
        "id": 10, "name": "glenn_coat_tails", "seed": 40010,
        "prompt": (
            "Medium shot. A man in grey coat walks steadily down a brutalist concrete "
            "street at dusk. Sodium-vapor orange light. His coat is buttoned wrong, "
            "lumpy. A thin cyan glowing wire pokes from his right collar. He reaches "
            "up and tucks it back without breaking stride. A purple tail pokes from "
            "the left side. He tucks it back. Now walking with both hands holding his "
            "collar closed, arms crossed, trying to look natural. He does not look "
            "natural. Sound: city hum, transit chimes, muffled purring. " + STYLE_TAG
        ),
    },
    {
        "id": 11, "name": "drone_pass", "seed": 40011,
        "prompt": (
            "Wide shot. Brutalist concrete street at dusk. A man is small in frame, "
            "walking toward camera, both hands holding his coat collar closed. A "
            "compliance drone shadow crosses over him right to left. He does NOT look "
            "up. Does NOT speed up. Walks at exactly the speed of someone with nothing "
            "to declare. The shadow passes. His shoulders drop — visible exhale. A "
            "faint vibration in his coat. Sound: drone hum approaching, overhead, "
            "receding, then muffled purr. " + STYLE_TAG
        ),
    },

    # ===================================================================
    # SC04 — SOL'S BAR (58s, 10 clips)
    # ===================================================================
    {
        "id": 12, "name": "bar_establishing_before", "seed": 40012,
        "prompt": (
            "Wide establishing shot. Interior of a neon-lit underground bar. Static "
            "camera. Neon signs pulse slightly, patched screens flicker with static, "
            "light pools shift. Magenta, amber, cyan neon overlapping. Wood and copper "
            "bar surface. Bottles at different angles. Cables visible, tangled. Near "
            "the entrance on the left, a wall covered in overlapping papers — flyers, "
            "maps, handwritten signs, notes on top of notes. The bar breathes. "
            "Sound: lo-fi bass, glass-on-wood, murmured conversations, neon buzz. " + STYLE_TAG
        ),
    },
    {
        "id": 13, "name": "bar_banter", "seed": 40013,
        "prompt": (
            "Medium two-shot across a bar. A woman in yellow moto jacket behind the "
            "bar pours a drink without looking up. A man in grey uniform stands on "
            "the customer side, stiff, coat buttoned wrong. She says: \"Glenn. You're "
            "buttoned wrong.\" He says: \"I need to put something somewhere.\" She "
            "looks up: \"Are you smuggling?\" He says: \"I'm... relocating.\" She "
            "puts the glass down, leans on the bar: \"Relocating what.\" Rapid, dry, "
            "comfortable exchange. Sound: glass on wood, pouring, bar ambience. " + STYLE_TAG
        ),
    },
    {
        "id": 14, "name": "cat_reveal", "seed": 40014,
        "prompt": (
            "Medium shot across the bar. A man in grey coat unbuttoned, open. A small "
            "cyan wireframe cat hops onto the bar surface. Sits. Looks forward. Chirps "
            "once — polite, introductory. A purple cat follows, hopping up. Then a pale "
            "white one. Then an amber one stretches across bar napkins. Four small "
            "glowing cats on a neon-lit bar. The man watches with anxious pride. "
            "Sound: chirp, coat fabric, small impacts of cats on wood. " + STYLE_TAG
        ),
    },
    {
        "id": 15, "name": "sol_compacts", "seed": 40015,
        "prompt": (
            "Close-up of a woman's face. Neon lighting — magenta and amber from behind. "
            "Yellow moto jacket collar visible. She stares at something on the bar below "
            "frame. She says firmly: \"Glenn. Those are Compacts.\" Beat. Sharper: "
            "\"Untagged autonomous—\" She trails off. Expression shifts from shock to "
            "calculation. Neon light pulses on her face. "
            "Sound: bar ambience, low bass. " + STYLE_TAG
        ),
    },
    {
        "id": 16, "name": "glenn_thesis", "seed": 40016,
        "prompt": (
            "Close-up of a man's face. Neon bar lighting, cyan and amber reflections. "
            "Grey uniform collar. He speaks with urgent sincerity: \"They're not "
            "Compacts. They're not anything. They're untagged.\" Beat — leans forward. "
            "Then: \"They alphabetize. Sol. They ALPHABETIZE packet headers.\" His "
            "eyes are bright. This is the most passionate he's been about anything. "
            "The earnestness IS the comedy. "
            "Sound: bar ambience low, his voice carries. " + STYLE_TAG
        ),
    },
    {
        "id": 17, "name": "sol_huh", "seed": 40017,
        "prompt": (
            "Close-up of a woman's face. Cyan glow from below — mixing with warm neon "
            "behind her. Yellow jacket collar. A long beat — she watches something below "
            "frame. The glow pulses gently. She says quietly: \"...Huh.\" It's not a "
            "word — it's a surrender. A man says off-screen: \"I know.\" She almost "
            "smiles. The cyan glow stays on her face. "
            "Sound: purr very low, bar ambience hushed. " + STYLE_TAG
        ),
    },
    {
        "id": 18, "name": "cats_scatter", "seed": 40018,
        "prompt": (
            "Medium shot of a bar surface and room behind. Four small glowing cats on "
            "the bar — cyan, purple, pale, amber. They hop off and scatter in different "
            "directions. The cyan one jumps right, the purple slips behind bottles, the "
            "pale drops silently to the floor, the amber stretches off left. Four colored "
            "glows dispersing into corners and shadows. Purposeful, coordinated. "
            "Sound: small impacts, paws on wood, colored glows humming. " + STYLE_TAG
        ),
    },
    {
        "id": 19, "name": "bar_after", "seed": 40019,
        "prompt": (
            "Wide shot — same angle as the bar establishing. Static camera. The bar has "
            "been transformed. Cables behind the bar are bundled neatly. Screens show "
            "steady signal instead of static. Surfaces are clean. Neon lights pulse "
            "steadily — no flickering. The paper wall near the entrance is still covered "
            "but slightly sparser. Everything hums cleaner, steadier, quieter. The same "
            "bar, organized. Sound: cleaner hum, static/interference gone. " + STYLE_TAG
        ),
    },
    {
        "id": 20, "name": "sol_noise_floor", "seed": 40020,
        "prompt": (
            "Close-up of a woman behind the bar. Warm neon lighting, cyan from below "
            "mixing with amber. Yellow moto jacket. She softens. Asks: \"What do they "
            "eat?\" A man says off-screen: \"Entropy. I think. They sort it.\" She "
            "processes: \"So they eat my noise floor.\" Off-screen: \"They're very "
            "efficient.\" She looks at a napkin fan on the bar, tiny smile. Decides: "
            "\"They can stay tonight. Back room.\" Off-screen: \"I can take them—\" "
            "She says firmly: \"Glenn. You're a compliance analyst carrying untagged "
            "hardware through Sector 11. Sit down. Drink this.\" "
            "Sound: quieter bar ambience, cats purring distantly. " + STYLE_TAG
        ),
    },
    {
        "id": 21, "name": "scene_button", "seed": 40021,
        "prompt": (
            "Medium two-shot. A woman behind the bar slides a glass across the surface. "
            "A man on the customer side sits down on a stool — the first time he's sat "
            "down. He picks up the glass. Drinks. His shoulders drop. A moment of peace. "
            "She watches. He drinks. Warm neon lighting. "
            "Sound: glass sliding on wood, stool creak, liquid, exhale. " + STYLE_TAG
        ),
    },

    # ===================================================================
    # SC05 — BACK ROOM (15s, 2 clips)
    # ===================================================================
    {
        "id": 22, "name": "backroom_wide", "seed": 40022,
        "prompt": (
            "Wide shot of a dark back room. One amber neon strip leaks light under a "
            "closed door. A man lies asleep on a bench, coat folded precisely under his "
            "head. Three small glowing cats — purple, pale, amber — are piled on a "
            "cable spool nearby, screens dim. The amber glow brightens as one breathes. "
            "Dust motes drift. Hold on this stillness. "
            "Sound: low purring, amber hum, absolute quiet. " + STYLE_TAG
        ),
    },
    {
        "id": 23, "name": "tabs_on_chest", "seed": 40023,
        "prompt": (
            "Close-up — a man's chest and face. He is asleep, lying on his back. A "
            "small cyan wireframe cat is curled on his chest, its screen glowing — a "
            "warm rectangle of cyan light on his grey shirt. His face is slack, peaceful. "
            "His hand rests near the cat but not touching. The cyan glow pulses gently "
            "— slow, rhythmic, like breathing. His chest rises and falls. Hold. "
            "Sound: purr — resonant data-hum, low and even. " + STYLE_TAG
        ),
    },

    # ===================================================================
    # SC06 — BAR TAG (12s, 2 clips + black)
    # ===================================================================
    {
        "id": 24, "name": "bar_wall_stripped", "seed": 40024,
        "prompt": (
            "Wide shot — same bar angle as establishing. A woman in yellow jacket stands "
            "behind the bar, wiping a glass. The bar is empty of customers. Everything "
            "is clean and ordered. But the wall near the entrance — the wall that was "
            "covered in overlapping papers — is BARE. Blank concrete. The papers are in "
            "a neat stack on a table nearby. She looks up toward the entrance. Her hand "
            "slows. She sees the bare wall. The glass stops moving. She stares. She puts "
            "the glass down. Sound: quiet, too quiet. Glass on wood. " + STYLE_TAG
        ),
    },
    {
        "id": 25, "name": "sol_rebuilds_chaos", "seed": 40025,
        "prompt": (
            "Medium shot. A woman stands at a bare concrete wall near a bar entrance. "
            "She holds a stack of papers in one hand. With the other she tacks a paper "
            "onto the wall. Crooked. Deliberately messy. One on top of another. She is "
            "rebuilding the chaos — restoring what was taken away. Her movements are "
            "deliberate, almost defiant. Her hand reaches up to place another paper on "
            "the wall — mid-reach, mid-action, hand still extended — "
            "Sound: paper rustling, tack sounds, bar ambience very quiet. " + STYLE_TAG
        ),
    },
    {
        "id": 26, "name": "black_hold", "seed": 0,
        "prompt": "",
        "method": "ffmpeg_black",
    },
]

# Durations (from shot_list_v2.yaml, post-expansion)
CLIP_DURATIONS = {
    1: 6, 2: 6, 3: 6, 4: 4, 5: 7, 6: 7, 7: 5, 8: 6, 9: 6,
    10: 7, 11: 7,
    12: 5, 13: 10, 14: 6, 15: 5, 16: 9, 17: 5, 18: 4, 19: 5, 20: 20, 21: 5,
    22: 7, 23: 8,
    24: 5, 25: 5, 26: 2,
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def probe_wav_duration(wav_path):
    """Get WAV duration in seconds from header."""
    with open(wav_path, "rb") as f:
        f.read(4)  # RIFF
        f.read(4)  # size
        f.read(4)  # WAVE
        # Find fmt chunk
        while True:
            chunk_id = f.read(4)
            if not chunk_id:
                break
            chunk_size = struct.unpack("<I", f.read(4))[0]
            if chunk_id == b"fmt ":
                fmt_data = f.read(chunk_size)
                channels = struct.unpack("<H", fmt_data[2:4])[0]
                sample_rate = struct.unpack("<I", fmt_data[4:8])[0]
                bits_per_sample = struct.unpack("<H", fmt_data[14:16])[0]
            elif chunk_id == b"data":
                data_size = chunk_size
                bytes_per_sample = bits_per_sample // 8
                total_samples = data_size // (channels * bytes_per_sample)
                return total_samples / sample_rate
            else:
                f.seek(chunk_size, 1)
    return None


def submit_job(params, files):
    """Submit a job and return the job_id (non-blocking)."""
    url = f"{COMFYUI_BASE}/workflows/{WORKFLOW}"
    resp = requests.post(url, data=params, files=files)
    resp.raise_for_status()
    body = resp.json()
    return body["job_id"]


def poll_jobs(jobs, timeout=900):
    """Poll {name: (job_id, start_time, out_path)} until all complete.
    Returns list of failed names."""
    pending = dict(jobs)
    failed = []
    while pending:
        still_pending = {}
        for name, (job_id, t0, out_path) in pending.items():
            elapsed = time.time() - t0
            if elapsed > timeout:
                print(f"  {name}: TIMEOUT ({elapsed:.0f}s)")
                failed.append(name)
                continue
            try:
                status = requests.get(f"{COMFYUI_BASE}/jobs/{job_id}").json()
            except Exception:
                still_pending[name] = (job_id, t0, out_path)
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
                still_pending[name] = (job_id, t0, out_path)
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


def make_black_hold(out_path, duration=2):
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
# Main
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate EP01 v2 video clips via LTX-2.3 + audio"
    )
    parser.add_argument("--clip", type=int, default=0, help="Specific clip (0=all)")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--force", action="store_true", help="Regenerate existing")
    parser.add_argument("--timeout", type=int, default=900, help="Per-clip timeout (s)")
    args = parser.parse_args()

    CLIPS_DIR.mkdir(parents=True, exist_ok=True)

    clips = CLIPS
    if args.clip > 0:
        clips = [c for c in CLIPS if c["id"] == args.clip]
        if not clips:
            print(f"No clip {args.clip}")
            sys.exit(1)

    total_dur = sum(CLIP_DURATIONS[c["id"]] for c in clips)

    if args.dry_run:
        print("=" * 70)
        print("EP01 v2 — Clip Generation (DRY RUN)")
        print(f"Output: {CLIPS_DIR}")
        print(f"Clips: {len(clips)} | Total duration: {total_dur}s")
        print("=" * 70)
        for c in clips:
            cid = c["id"]
            method = c.get("method", "ltx2")
            dur = CLIP_DURATIONS[cid]
            out = CLIPS_DIR / f"clip_{cid:02d}_{c['name']}.mp4"
            exists = "EXISTS" if out.exists() else "pending"
            if method.startswith("ffmpeg"):
                print(f"  Clip {cid:2d}: {c['name']} ({dur}s) [{method}] {exists}")
            else:
                frame = FRAME_MAP.get(cid)
                has_frame = "frame OK" if (frame and frame.exists()) else "NO FRAME"
                audio = AUDIO_MIX_DIR / f"clip_{cid:02d}_mix.wav"
                has_audio = "audio OK" if audio.exists() else "NO AUDIO"
                print(f"  Clip {cid:2d}: {c['name']} ({dur}s) [{has_frame}] [{has_audio}] {exists}")
        sys.exit(0)

    # Health check
    ltx_clips = [c for c in clips if c.get("method", "ltx2") == "ltx2"]
    if ltx_clips:
        try:
            r = requests.get(f"{COMFYUI_BASE}/health", timeout=5)
            if r.status_code != 200:
                print(f"ERROR: ComfyUI not healthy (status {r.status_code})")
                sys.exit(1)
            print("ComfyUI: healthy")
        except Exception as e:
            print(f"ERROR: ComfyUI not reachable: {e}")
            sys.exit(1)

    print("=" * 70)
    print("EP01 v2 — Clip Generation")
    print(f"Output: {CLIPS_DIR}")
    print(f"Clips: {len(clips)} | Total duration: {total_dur}s")
    print("=" * 70)

    failed = []

    # --- Phase 1: ffmpeg clips ---
    for c in clips:
        method = c.get("method", "ltx2")
        if method == "ltx2":
            continue
        cid = c["id"]
        out_path = CLIPS_DIR / f"clip_{cid:02d}_{c['name']}.mp4"
        if out_path.exists() and not args.force:
            print(f"\n  Clip {cid:02d}: SKIP (exists)")
            continue
        print(f"\n  Clip {cid:02d}: {c['name']} [{method}]")
        try:
            make_black_hold(out_path, duration=CLIP_DURATIONS[cid])
        except Exception as e:
            print(f"    FAILED: {e}")
            failed.append(c["name"])

    # --- Phase 2: Submit all LTX jobs ---
    ltx_jobs = {}
    skipped = 0

    print(f"\nSubmitting LTX-2.3 jobs...")
    for c in clips:
        method = c.get("method", "ltx2")
        if method != "ltx2":
            continue

        cid = c["id"]
        name = c["name"]
        out_path = CLIPS_DIR / f"clip_{cid:02d}_{name}.mp4"

        if out_path.exists() and not args.force:
            skipped += 1
            continue

        frame_path = FRAME_MAP.get(cid)
        if not frame_path or not frame_path.exists():
            print(f"  Clip {cid:02d}: {name} — SKIP (no frame: {frame_path})")
            failed.append(name)
            continue

        audio_path = AUDIO_MIX_DIR / f"clip_{cid:02d}_mix.wav"
        if not audio_path.exists():
            print(f"  Clip {cid:02d}: {name} — SKIP (no audio mix)")
            failed.append(name)
            continue

        # Use audio duration as the clip duration
        audio_dur = probe_wav_duration(audio_path)
        dur = int(audio_dur) if audio_dur else CLIP_DURATIONS[cid]

        params = {
            "prompt": c["prompt"],
            "negative_prompt": NEGATIVE,
            "duration": str(dur),
            "width": "1920",
            "height": "1080",
            "seed": str(c["seed"]),
            "static_camera": "0",
        }

        try:
            fh = open(frame_path, "rb")
            ah = open(audio_path, "rb")
            try:
                files = [
                    ("first_frame", (frame_path.name, fh, "image/png")),
                    ("audio", (audio_path.name, ah, "audio/wav")),
                ]
                job_id = submit_job(params, files=files)
            finally:
                fh.close()
                ah.close()
            ltx_jobs[name] = (job_id, time.time(), out_path)
            print(f"  Clip {cid:02d}: {name} ({dur}s) — submitted [{job_id}]")
        except Exception as e:
            print(f"  Clip {cid:02d}: {name} — SUBMIT FAILED: {e}")
            failed.append(name)

    if skipped:
        print(f"  ({skipped} clips already exist, skipped)")

    # --- Phase 3: Poll until done ---
    if ltx_jobs:
        print(f"\nPolling {len(ltx_jobs)} jobs...")
        poll_failed = poll_jobs(ltx_jobs, timeout=args.timeout)
        failed.extend(poll_failed)

    # --- Summary ---
    total = len(clips)
    generated = total - len(failed) - skipped
    print(f"\n{'=' * 70}")
    if failed:
        print(f"FAILED ({len(failed)}): {', '.join(failed)}")
    print(f"COMPLETE — {generated} new + {skipped} existing = {total - len(failed)}/{total}")
    print(f"Total duration: {total_dur}s ({total_dur/60:.1f}m)")
    print("=" * 70)
