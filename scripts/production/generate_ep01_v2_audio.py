#!/usr/bin/env python3
"""
EP01 "INTAKE" v2 — Full Audio Pipeline

Generates all audio for EP01 v2:
  1. Voice refs via qwen3-tts-voicedesign (if missing)
  2. Dialogue lines via qwen3-tts-voiceclone
  3. Ambient beds via ffmpeg lavfi
  4. Cat SFX via ffmpeg synthesis
  5. Per-clip audio mixes

Usage:
    python generate_ep01_v2_audio.py --step voice-refs --dry-run
    python generate_ep01_v2_audio.py --step voice-refs
    python generate_ep01_v2_audio.py --step dialogue --dry-run
    python generate_ep01_v2_audio.py --step dialogue
    python generate_ep01_v2_audio.py --step ambient
    python generate_ep01_v2_audio.py --step sfx
    python generate_ep01_v2_audio.py --step mix
    python generate_ep01_v2_audio.py --step all
"""

import argparse
import json
import struct
import subprocess
import sys
import time
from pathlib import Path

import requests
import yaml

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
COMFYUI_BASE = "http://192.168.1.181:8100"
VOICEDESIGN_WORKFLOW = "qwen3-tts-voicedesign"
VOICECLONE_WORKFLOW = "qwen3-tts-voiceclone"

PROJECT = Path(__file__).resolve().parents[2] / "projects" / "stray-signal-v2"
PRODUCTION = PROJECT / "PRODUCTION" / "EP01"
VOICE_DEFS = PROJECT / "voice_definitions.yaml"
VOICE_REFS_DIR = PROJECT / "REFERENCES" / "voice_refs"

AUDIO_DIR = PRODUCTION / "audio"
VOICE_LINES_DIR = AUDIO_DIR / "voice_lines"
AMBIENT_DIR = AUDIO_DIR / "ambient"
SFX_DIR = AUDIO_DIR / "sfx"
MIX_DIR = AUDIO_DIR / "clip_mixes"

SAMPLE_RATE = 44100

# ---------------------------------------------------------------------------
# Dialogue definitions — extracted from SCRIPT_EP01_v2.md
# ---------------------------------------------------------------------------
DIALOGUE_LINES = [
    # SC01
    {"id": "gl_01", "clip": 2, "character": "glenn", "text": "That's not supposed to do that."},

    # SC02
    {"id": "gl_02", "clip": 6, "character": "glenn", "text": "You alphabetized the packet headers."},
    {"id": "gl_03", "clip": 6, "character": "glenn", "text": "Nobody alphabetizes packet headers."},
    {"id": "gl_04", "clip": 8, "character": "glenn", "text": "You're not supposed to be here."},
    {"id": "gl_05", "clip": 9, "character": "glenn", "text": "I should file this."},

    # SC04
    {"id": "so_01", "clip": 13, "character": "sol", "text": "Glenn. You're buttoned wrong."},
    {"id": "gl_06", "clip": 13, "character": "glenn", "text": "I need to put something somewhere."},
    {"id": "so_02", "clip": 13, "character": "sol", "text": "Are you smuggling?"},
    {"id": "gl_07", "clip": 13, "character": "glenn", "text": "I'm relocating."},
    {"id": "so_03", "clip": 13, "character": "sol", "text": "Relocating what."},

    {"id": "so_04", "clip": 15, "character": "sol", "text": "Glenn. Those are Compacts."},
    {"id": "so_05", "clip": 15, "character": "sol", "text": "Untagged autonomous —"},

    {"id": "gl_08", "clip": 16, "character": "glenn",
     "text": "They're not Compacts. They're not anything. They're untagged."},
    {"id": "gl_09", "clip": 16, "character": "glenn",
     "text": "They alphabetize. Sol. They alphabetize packet headers."},

    {"id": "so_06", "clip": 17, "character": "sol", "text": "Huh."},
    {"id": "gl_10", "clip": 17, "character": "glenn", "text": "I know."},

    {"id": "so_07", "clip": 20, "character": "sol", "text": "What do they eat?"},
    {"id": "gl_11", "clip": 20, "character": "glenn", "text": "Entropy. I think. They sort it."},
    {"id": "so_08", "clip": 20, "character": "sol", "text": "So they eat my noise floor."},
    {"id": "gl_12", "clip": 20, "character": "glenn", "text": "They're very efficient."},
    {"id": "so_09", "clip": 20, "character": "sol", "text": "They can stay tonight. Back room."},
    {"id": "gl_13", "clip": 20, "character": "glenn", "text": "I can take them —"},
    {"id": "so_10", "clip": 20, "character": "sol",
     "text": "Glenn. You're a compliance analyst carrying untagged hardware through Sector 11. Sit down. Drink this."},
]

# Per-clip ambient assignments
CLIP_AMBIENT = {
    1: "bureau", 2: "bureau", 3: "bureau",
    4: "relay", 5: "relay", 6: "relay", 7: "relay", 8: "relay", 9: "relay",
    10: "street", 11: "street",
    12: "bar", 13: "bar", 14: "bar", 15: "bar", 16: "bar", 17: "bar",
    18: "bar", 19: "bar", 20: "bar", 21: "bar",
    22: "backroom", 23: "backroom",
    24: "bar_quiet", 25: "bar_quiet",
    26: "silence",
}

# Per-clip SFX assignments
CLIP_SFX = {
    5: ["tabs_chirp"],
    7: ["tabs_chirp"],  # after bolt line
    8: ["tabs_chirp_double"],
    11: ["drone_hum"],
    14: ["tabs_chirp"],  # polite intro
    18: ["cat_scatter"],  # paws on wood
    23: ["tabs_purr"],
}

# Clip durations from shot list
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
def health_check():
    """Check ComfyUI is reachable."""
    try:
        r = requests.get(f"{COMFYUI_BASE}/health", timeout=5)
        return r.status_code == 200
    except Exception:
        return False


def submit_voicedesign(instruct, text, seed=None, timeout=180):
    """Design a voice via qwen3-tts-voicedesign."""
    url = f"{COMFYUI_BASE}/workflows/{VOICEDESIGN_WORKFLOW}"
    data = {"instruct": instruct.strip(), "text": text.strip()}
    if seed is not None:
        data["seed"] = str(seed)

    resp = requests.post(url, data=data, timeout=30)
    resp.raise_for_status()

    # Sync response (direct audio)
    content_type = resp.headers.get("content-type", "")
    if "audio" in content_type or "octet-stream" in content_type:
        return resp.content

    # Async response (job_id)
    job = resp.json()
    job_id = job.get("job_id")
    if not job_id:
        raise RuntimeError(f"Unexpected response: {content_type} — {resp.text[:200]}")

    print(f"    Job: {job_id} (polling...)")
    start = time.time()
    polls = 0
    while time.time() - start < timeout:
        status = requests.get(f"{COMFYUI_BASE}/jobs/{job_id}").json()
        st = status.get("status", "unknown")
        if st == "completed":
            elapsed = time.time() - start
            print(f"    Done ({elapsed:.0f}s)")
            result = requests.get(f"{COMFYUI_BASE}/jobs/{job_id}/result")
            return result.content
        if st in ("error", "failed"):
            raise RuntimeError(f"Voicedesign job {job_id} failed: {status.get('error')}")
        polls += 1
        time.sleep(2 if polls <= 5 else 5)

    raise TimeoutError(f"Voicedesign timeout on job {job_id}")


def submit_voiceclone(text, voice_ref_path, timeout=120):
    """Clone a voice via qwen3-tts-voiceclone."""
    url = f"{COMFYUI_BASE}/workflows/{VOICECLONE_WORKFLOW}"
    with open(voice_ref_path, "rb") as vf:
        files = {"voice": (voice_ref_path.name, vf, "audio/wav")}
        data = {"text": text}
        resp = requests.post(url, data=data, files=files, timeout=30)

    # Sync response
    if resp.status_code == 200:
        ct = resp.headers.get("content-type", "")
        if "audio" in ct or "octet-stream" in ct:
            return resp.content

    # Async response
    resp.raise_for_status()
    job = resp.json()
    job_id = job.get("job_id")
    if not job_id:
        raise RuntimeError(f"No job_id in response: {resp.text[:200]}")

    start = time.time()
    polls = 0
    while time.time() - start < timeout:
        status = requests.get(f"{COMFYUI_BASE}/jobs/{job_id}").json()
        st = status.get("status", "unknown")
        if st == "completed":
            result = requests.get(f"{COMFYUI_BASE}/jobs/{job_id}/result")
            return result.content
        if st in ("error", "failed"):
            raise RuntimeError(f"TTS job {job_id} failed: {status.get('error')}")
        polls += 1
        time.sleep(2 if polls <= 5 else 5)

    raise TimeoutError(f"TTS timeout on job {job_id}")


def probe_duration(wav_path):
    """Get WAV duration in seconds via ffprobe."""
    cmd = [
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", str(wav_path)
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return float(result.stdout.strip())


def run_ffmpeg(cmd, desc=""):
    """Run ffmpeg command, return success bool."""
    if desc:
        print(f"    {desc}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"    FFMPEG ERROR: {result.stderr[:200]}")
        return False
    return True


# ---------------------------------------------------------------------------
# Step 1: Voice Refs
# ---------------------------------------------------------------------------
def step_voice_refs(dry_run=False):
    """Generate voice refs via voicedesign if missing."""
    print("\n" + "=" * 70)
    print("STEP 1: VOICE REFS (qwen3-tts-voicedesign)")
    print("=" * 70)

    with open(VOICE_DEFS) as f:
        defs = yaml.safe_load(f)
    characters = defs.get("characters", {})

    VOICE_REFS_DIR.mkdir(parents=True, exist_ok=True)

    for char_id, char_def in characters.items():
        ref_path = VOICE_REFS_DIR / f"{char_id}_voice_ref.wav"
        if ref_path.exists():
            print(f"\n  {char_id}: EXISTS — {ref_path}")
            continue

        instruct = char_def["instruct"]
        sample = char_def["sample_text"]
        seed = char_def.get("seed")

        print(f"\n  {char_id}: GENERATING")
        print(f"    Instruct: {instruct[:80]}...")
        print(f"    Sample: \"{sample[:60]}...\"")
        if seed:
            print(f"    Seed: {seed}")

        if dry_run:
            print("    -> DRY RUN: skipped")
            continue

        try:
            audio_data = submit_voicedesign(instruct, sample, seed)
            with open(ref_path, "wb") as f:
                f.write(audio_data)
            print(f"    -> Saved: {ref_path.name} ({len(audio_data) / 1024:.0f} KB)")

            # Save metadata
            meta = {
                "character_id": char_id,
                "instruct": instruct.strip(),
                "sample_text": sample.strip(),
                "seed": seed,
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
            }
            with open(ref_path.with_suffix(".json"), "w") as f:
                json.dump(meta, f, indent=2)
        except Exception as e:
            print(f"    FAILED: {e}")


# ---------------------------------------------------------------------------
# Step 2: Dialogue Lines
# ---------------------------------------------------------------------------
def step_dialogue(dry_run=False, force=False):
    """Generate all dialogue lines via voiceclone."""
    print("\n" + "=" * 70)
    print("STEP 2: DIALOGUE LINES (qwen3-tts-voiceclone)")
    print("=" * 70)

    VOICE_LINES_DIR.mkdir(parents=True, exist_ok=True)

    # Check voice refs exist
    for char in ("glenn", "sol"):
        ref = VOICE_REFS_DIR / f"{char}_voice_ref.wav"
        if not ref.exists():
            print(f"\n  ERROR: Voice ref missing: {ref}")
            print(f"  Run: --step voice-refs first")
            return
        print(f"  Voice ref: {char} -> {ref.name}")

    total = len(DIALOGUE_LINES)
    done = 0
    failed = []

    for line in DIALOGUE_LINES:
        done += 1
        line_id = line["id"]
        char = line["character"]
        text = line["text"]
        clip = line["clip"]
        out_path = VOICE_LINES_DIR / f"{line_id}_{char}.wav"

        if out_path.exists() and not force:
            print(f"\n  [{done}/{total}] {line_id}: SKIP (exists)")
            continue

        print(f"\n  [{done}/{total}] {line_id} (clip {clip}, {char})")
        print(f"    \"{text[:70]}{'...' if len(text) > 70 else ''}\"")

        if dry_run:
            print("    -> DRY RUN: skipped")
            continue

        ref_path = VOICE_REFS_DIR / f"{char}_voice_ref.wav"
        try:
            audio_data = submit_voiceclone(text, ref_path)
            with open(out_path, "wb") as f:
                f.write(audio_data)
            dur = probe_duration(out_path)
            print(f"    -> Saved: {out_path.name} ({dur:.1f}s, {len(audio_data) / 1024:.0f} KB)")
        except Exception as e:
            print(f"    FAILED: {e}")
            failed.append(line_id)

    if failed:
        print(f"\n  FAILED ({len(failed)}): {', '.join(failed)}")
    print(f"\n  Done: {done}/{total} lines processed")


# ---------------------------------------------------------------------------
# Step 3: Ambient Beds
# ---------------------------------------------------------------------------
def step_ambient():
    """Generate ambient beds per location via ffmpeg lavfi."""
    print("\n" + "=" * 70)
    print("STEP 3: AMBIENT BEDS (ffmpeg lavfi)")
    print("=" * 70)

    AMBIENT_DIR.mkdir(parents=True, exist_ok=True)

    # Each ambient is a 30s loopable bed (will be trimmed per clip during mix)
    beds = {
        "bureau": {
            "desc": "60Hz hum + soft fluorescent buzz — institutional nothing",
            "filter": (
                "anoisesrc=d=30:c=pink:r=44100:a=0.003,"
                "highpass=f=55,lowpass=f=65,"  # isolate ~60Hz band
                "volume=0.4"
            ),
        },
        "relay": {
            "desc": "Deep server hum + electrical crackle — something alive in dead infrastructure",
            "filter": (
                "anoisesrc=d=30:c=brown:r=44100:a=0.005,"
                "highpass=f=40,lowpass=f=200,"
                "volume=0.3"
            ),
        },
        "street": {
            "desc": "City hum + distant traffic — sodium-vapor evening",
            "filter": (
                "anoisesrc=d=30:c=pink:r=44100:a=0.008,"
                "highpass=f=80,lowpass=f=2000,"
                "volume=0.2"
            ),
        },
        "bar": {
            "desc": "Low bass hum + murmur — neon noise floor",
            "filter": (
                "anoisesrc=d=30:c=brown:r=44100:a=0.01,"
                "highpass=f=60,lowpass=f=500,"
                "volume=0.35"
            ),
        },
        "bar_quiet": {
            "desc": "Same bar but thinner — the noise floor has a gap",
            "filter": (
                "anoisesrc=d=30:c=brown:r=44100:a=0.005,"
                "highpass=f=80,lowpass=f=300,"
                "volume=0.15"
            ),
        },
        "backroom": {
            "desc": "Near silence — amber hum, muffled bar through a door",
            "filter": (
                "anoisesrc=d=30:c=brown:r=44100:a=0.002,"
                "highpass=f=50,lowpass=f=150,"
                "volume=0.15"
            ),
        },
        "silence": {
            "desc": "True silence — black hold",
            "filter": "anullsrc=r=44100:cl=stereo,atrim=duration=30",
        },
    }

    for bed_id, bed in beds.items():
        out_path = AMBIENT_DIR / f"amb_{bed_id}.wav"
        if out_path.exists():
            print(f"\n  {bed_id}: EXISTS")
            continue

        print(f"\n  {bed_id}: {bed['desc']}")
        cmd = [
            "ffmpeg", "-y",
            "-f", "lavfi", "-i", bed["filter"],
            "-ac", "1", "-ar", str(SAMPLE_RATE),
            "-t", "30",
            str(out_path),
        ]
        if run_ffmpeg(cmd, f"-> Generating {out_path.name}"):
            print(f"    -> Saved: {out_path.name}")


# ---------------------------------------------------------------------------
# Step 4: Cat SFX
# ---------------------------------------------------------------------------
def step_sfx():
    """Generate cat SFX via ffmpeg synthesis."""
    print("\n" + "=" * 70)
    print("STEP 4: CAT SFX (ffmpeg synthesis)")
    print("=" * 70)

    SFX_DIR.mkdir(parents=True, exist_ok=True)

    sfx_defs = {
        "tabs_chirp": {
            "desc": "Tabs chirp — rising two-tone, digital, bright",
            # Rising sine sweep 800Hz -> 1600Hz over 0.3s
            "filter": (
                "sine=f=800:d=0.15,"
                "afade=t=in:st=0:d=0.02,afade=t=out:st=0.12:d=0.03"
                "[a1];"
                "sine=f=1200:d=0.2,"
                "afade=t=in:st=0:d=0.02,afade=t=out:st=0.15:d=0.05"
                "[a2];"
                "[a1][a2]concat=n=2:v=0:a=1,"
                "volume=0.3"
            ),
            "duration": 0.5,
        },
        "tabs_chirp_double": {
            "desc": "Tabs double chirp — two quick rising tones",
            "filter": (
                "sine=f=800:d=0.12,"
                "afade=t=in:st=0:d=0.02,afade=t=out:st=0.09:d=0.03"
                "[a1];"
                "sine=f=1200:d=0.15,"
                "afade=t=in:st=0:d=0.02,afade=t=out:st=0.12:d=0.03"
                "[a2];"
                "sine=f=900:d=0.12,"
                "afade=t=in:st=0:d=0.02,afade=t=out:st=0.09:d=0.03"
                "[a3];"
                "sine=f=1400:d=0.15,"
                "afade=t=in:st=0:d=0.02,afade=t=out:st=0.12:d=0.03"
                "[a4];"
                "[a1][a2][a3][a4]concat=n=4:v=0:a=1,"
                "volume=0.3"
            ),
            "duration": 0.8,
        },
        "tabs_purr": {
            "desc": "Tabs purr — resonant data-hum, low and even",
            # Low oscillating tone
            "filter": (
                "sine=f=120:d=8,"
                "tremolo=f=4:d=0.3,"
                "afade=t=in:st=0:d=1,afade=t=out:st=6:d=2,"
                "volume=0.25"
            ),
            "duration": 8,
        },
        "drone_hum": {
            "desc": "Compliance drone — approaching and receding",
            "filter": (
                "sine=f=200:d=5,"
                "tremolo=f=8:d=0.5,"
                "afade=t=in:st=0:d=2,afade=t=out:st=3:d=2,"
                "volume=0.4"
            ),
            "duration": 5,
        },
        "cat_scatter": {
            "desc": "Quick paws on wood — cats hopping off bar",
            # Short noise bursts
            "filter": (
                "anoisesrc=d=0.8:c=white:r=44100:a=0.02,"
                "highpass=f=2000,lowpass=f=8000,"
                "afade=t=in:st=0:d=0.05,afade=t=out:st=0.6:d=0.2,"
                "volume=0.3"
            ),
            "duration": 0.8,
        },
    }

    for sfx_id, sfx in sfx_defs.items():
        out_path = SFX_DIR / f"sfx_{sfx_id}.wav"
        if out_path.exists():
            print(f"\n  {sfx_id}: EXISTS")
            continue

        print(f"\n  {sfx_id}: {sfx['desc']}")
        cmd = [
            "ffmpeg", "-y",
            "-f", "lavfi", "-i", sfx["filter"],
            "-ac", "1", "-ar", str(SAMPLE_RATE),
            "-t", str(sfx["duration"]),
            str(out_path),
        ]
        if run_ffmpeg(cmd, f"-> Generating {out_path.name}"):
            print(f"    -> Saved: {out_path.name}")


# ---------------------------------------------------------------------------
# Step 5: Per-Clip Mix
# ---------------------------------------------------------------------------
def step_mix(force=False):
    """Pre-mix audio per clip: dialogue + ambient + SFX."""
    print("\n" + "=" * 70)
    print("STEP 5: PER-CLIP AUDIO MIX")
    print("=" * 70)

    MIX_DIR.mkdir(parents=True, exist_ok=True)

    # Group dialogue lines by clip
    clip_dialogue = {}
    for line in DIALOGUE_LINES:
        clip_id = line["clip"]
        if clip_id not in clip_dialogue:
            clip_dialogue[clip_id] = []
        clip_dialogue[clip_id].append(line)

    for clip_id in sorted(CLIP_DURATIONS.keys()):
        duration = CLIP_DURATIONS[clip_id]
        out_path = MIX_DIR / f"clip_{clip_id:02d}_mix.wav"

        if out_path.exists() and not force:
            print(f"\n  Clip {clip_id:02d}: SKIP (exists)")
            continue

        print(f"\n  Clip {clip_id:02d} ({duration}s):")

        inputs = []
        filter_parts = []
        input_idx = 0

        # --- Ambient bed ---
        amb_key = CLIP_AMBIENT.get(clip_id, "silence")
        amb_path = AMBIENT_DIR / f"amb_{amb_key}.wav"
        if amb_path.exists():
            inputs.extend(["-i", str(amb_path)])
            # Trim ambient to clip duration, set low volume
            filter_parts.append(
                f"[{input_idx}]atrim=duration={duration},"
                f"aformat=sample_rates={SAMPLE_RATE}:channel_layouts=mono,"
                f"volume=0.15[amb]"
            )
            input_idx += 1
            print(f"    Ambient: {amb_key}")
        else:
            # Generate silence as ambient
            inputs.extend(["-f", "lavfi", "-i",
                          f"anullsrc=r={SAMPLE_RATE}:cl=mono"])
            filter_parts.append(
                f"[{input_idx}]atrim=duration={duration}[amb]"
            )
            input_idx += 1
            print(f"    Ambient: silence (missing {amb_key})")

        mix_inputs = ["[amb]"]

        # --- Dialogue lines ---
        lines = clip_dialogue.get(clip_id, [])
        if lines:
            # Calculate timing: space lines evenly with small gaps
            cumulative_offset_ms = 300  # start 300ms in
            for i, line in enumerate(lines):
                wav_path = VOICE_LINES_DIR / f"{line['id']}_{line['character']}.wav"
                if not wav_path.exists():
                    print(f"    MISSING: {wav_path.name} — skipping line")
                    continue

                line_dur = probe_duration(wav_path)
                delay_ms = int(cumulative_offset_ms)

                inputs.extend(["-i", str(wav_path)])
                label = f"dl{i}"
                filter_parts.append(
                    f"[{input_idx}]aformat=sample_rates={SAMPLE_RATE}:"
                    f"channel_layouts=mono,"
                    f"adelay={delay_ms}|{delay_ms},"
                    f"volume=1.0[{label}]"
                )
                mix_inputs.append(f"[{label}]")
                input_idx += 1

                # Next line starts after this one + 400ms gap
                cumulative_offset_ms += (line_dur * 1000) + 400
                print(f"    Dialogue: {line['id']} @ {delay_ms}ms ({line_dur:.1f}s) "
                      f"\"{line['text'][:40]}...\"")

        # --- SFX ---
        sfx_list = CLIP_SFX.get(clip_id, [])
        for j, sfx_id in enumerate(sfx_list):
            sfx_path = SFX_DIR / f"sfx_{sfx_id}.wav"
            if not sfx_path.exists():
                print(f"    MISSING SFX: {sfx_path.name}")
                continue

            inputs.extend(["-i", str(sfx_path)])
            label = f"sfx{j}"
            # Place SFX at 50% through the clip
            sfx_delay = int(duration * 500)  # ms
            filter_parts.append(
                f"[{input_idx}]aformat=sample_rates={SAMPLE_RATE}:"
                f"channel_layouts=mono,"
                f"adelay={sfx_delay}|{sfx_delay},"
                f"volume=0.5[{label}]"
            )
            mix_inputs.append(f"[{label}]")
            input_idx += 1
            print(f"    SFX: {sfx_id} @ {sfx_delay}ms")

        # --- Mix ---
        n_inputs = len(mix_inputs)
        mix_str = "".join(mix_inputs)
        filter_parts.append(
            f"{mix_str}amix=inputs={n_inputs}:duration=longest:"
            f"dropout_transition=0:normalize=0[mixed]"
        )

        # Final: ensure duration, convert to stereo
        filter_parts.append(
            f"[mixed]atrim=duration={duration},"
            f"aformat=sample_rates={SAMPLE_RATE}:channel_layouts=stereo[out]"
        )

        filter_complex = ";\n".join(filter_parts)

        cmd = ["ffmpeg", "-y"]
        cmd.extend(inputs)
        cmd.extend(["-filter_complex", filter_complex])
        cmd.extend(["-map", "[out]", str(out_path)])

        if run_ffmpeg(cmd, f"-> Mixing {n_inputs} tracks"):
            mix_dur = probe_duration(out_path)
            print(f"    -> Saved: {out_path.name} ({mix_dur:.1f}s)")
        else:
            print(f"    -> FAILED to mix clip {clip_id}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="EP01 v2 Full Audio Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--step",
        choices=["voice-refs", "dialogue", "ambient", "sfx", "mix", "all"],
        required=True,
        help="Pipeline step to run",
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--force", action="store_true",
                       help="Regenerate even if output exists")
    args = parser.parse_args()

    steps = {
        "voice-refs": lambda: step_voice_refs(args.dry_run),
        "dialogue": lambda: step_dialogue(args.dry_run, args.force),
        "ambient": lambda: step_ambient(),
        "sfx": lambda: step_sfx(),
        "mix": lambda: step_mix(args.force),
    }

    if args.step == "all":
        # Check ComfyUI for voice steps
        if not args.dry_run:
            if not health_check():
                print("ERROR: ComfyUI not reachable at", COMFYUI_BASE)
                sys.exit(1)
            print("ComfyUI: OK")

        for step_name in ["voice-refs", "dialogue", "ambient", "sfx", "mix"]:
            steps[step_name]()
    else:
        if args.step in ("voice-refs", "dialogue") and not args.dry_run:
            if not health_check():
                print("ERROR: ComfyUI not reachable at", COMFYUI_BASE)
                sys.exit(1)
            print("ComfyUI: OK")
        steps[args.step]()

    print("\n" + "=" * 70)
    print("AUDIO PIPELINE COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
