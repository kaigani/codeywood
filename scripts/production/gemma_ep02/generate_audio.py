#!/usr/bin/env python3
"""
EP02 audio pipeline:
  Step 1: dialogue lines via qwen3-tts-voiceclone (refs from LTX-extracted audio)
  Step 2: ambient beds via ffmpeg lavfi (3 locations)
  Step 3: SFX library via ffmpeg synthesis
  Step 4: per-shot mix

Usage:
    python generate_audio.py --step dialogue
    python generate_audio.py --step ambient
    python generate_audio.py --step sfx
    python generate_audio.py --step mix
    python generate_audio.py --step all
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import (
    AMBIENT_DIR, CLIP_DEFS, MIX_DIR, SAMPLE_RATE, SFX_DIR,
    VOICE_LINES, VOICE_REFS,
    health_check, probe_duration_ff, run_ffmpeg, run_workflow, save,
)

VOICECLONE_WORKFLOW = "qwen3-tts-voiceclone"


def load_shots() -> list[dict]:
    with open(CLIP_DEFS) as f:
        return yaml.safe_load(f)["shots"]


SHOT_LOCATION_AMBIENT = {
    "balcony": "balcony",
    "market": "market",
    "warehouse": "warehouse",
}

# -------- ambient beds (cyber-noir flavors) --------
AMBIENT_BEDS = {
    "balcony": {
        "desc": "Balcony — distant city traffic, faint rain, low wind",
        "filter": (
            "anoisesrc=d=30:c=brown:r=44100:a=0.010,"
            "highpass=f=40,lowpass=f=500,"
            "volume=0.30"
        ),
    },
    "market": {
        "desc": "Wet market alley — distant crowd murmur, rain on metal",
        "filter": (
            "anoisesrc=d=30:c=pink:r=44100:a=0.012,"
            "highpass=f=80,lowpass=f=2500,"
            "volume=0.30"
        ),
    },
    "warehouse": {
        "desc": "Derelict warehouse — distant industrial hum, dripping",
        "filter": (
            "anoisesrc=d=30:c=brown:r=44100:a=0.006,"
            "highpass=f=30,lowpass=f=300,"
            "volume=0.28"
        ),
    },
}

# -------- SFX library (EP02 cues) --------
SFX_LIB = {
    "distant_thunder": {
        "desc": "Low distant thunder rumble",
        "filter": (
            "anoisesrc=d=4:c=brown:r=44100:a=0.20,"
            "lowpass=f=200,"
            "afade=t=in:st=0:d=1.0,afade=t=out:st=2.5:d=1.5,"
            "volume=0.55,"
            "apad=pad_dur=3"
        ),
        "duration": 7,
    },
    "blade_shing": {
        "desc": "Metallic ring of a curved blade",
        "filter": (
            "sine=f=2400:d=0.4,"
            "tremolo=f=8:d=0.3,"
            "afade=t=in:st=0:d=0.005,afade=t=out:st=0.25:d=0.15,"
            "volume=0.45,"
            "apad=pad_dur=5"
        ),
        "duration": 5.5,
    },
    "metal_scrape": {
        "desc": "High-pitched metal scraping",
        "filter": (
            "anoisesrc=d=3:c=white:r=44100:a=0.10,"
            "highpass=f=2500,lowpass=f=8000,"
            "tremolo=f=12:d=0.3,"
            "volume=0.4,"
            "apad=pad_dur=3"
        ),
        "duration": 6,
    },
    "wet_drip": {
        "desc": "Slow wet drips of rain",
        "filter": (
            "anoisesrc=d=0.06:c=pink:r=44100:a=0.10,"
            "highpass=f=300,lowpass=f=3000,"
            "afade=t=in:st=0:d=0.005,afade=t=out:st=0.04:d=0.02,"
            "volume=0.5[d1];"
            "anoisesrc=d=0.06:c=pink:r=44100:a=0.10,"
            "highpass=f=300,lowpass=f=3000,"
            "afade=t=in:st=0:d=0.005,afade=t=out:st=0.04:d=0.02,"
            "volume=0.5[d2];"
            "anoisesrc=d=0.06:c=pink:r=44100:a=0.10,"
            "highpass=f=300,lowpass=f=3000,"
            "afade=t=in:st=0:d=0.005,afade=t=out:st=0.04:d=0.02,"
            "volume=0.5[d3];"
            "[d1][d2][d3]concat=n=3:v=0:a=1,"
            "apad=pad_dur=5"
        ),
        "duration": 5.5,
    },
    "wet_slice": {
        "desc": "Wet slice of blade on skin",
        "filter": (
            "anoisesrc=d=0.3:c=pink:r=44100:a=0.10,"
            "highpass=f=400,lowpass=f=4000,"
            "afade=t=in:st=0:d=0.02,afade=t=out:st=0.2:d=0.1,"
            "volume=0.55,"
            "apad=pad_dur=6"
        ),
        "duration": 6.5,
    },
    "gurgling_sob": {
        "desc": "Wet gurgling sob",
        "filter": (
            "anoisesrc=d=1.5:c=pink:r=44100:a=0.06,"
            "highpass=f=200,lowpass=f=1500,"
            "tremolo=f=6:d=0.5,"
            "afade=t=in:st=0:d=0.1,afade=t=out:st=1.2:d=0.3,"
            "volume=0.35,"
            "apad=pad_dur=4"
        ),
        "duration": 5.5,
    },
    "core_hum": {
        "desc": "Soft glowing core hum",
        "filter": (
            "sine=f=90:d=7,"
            "tremolo=f=1.5:d=0.4,"
            "afade=t=in:st=0:d=0.8,afade=t=out:st=6:d=1.0,"
            "volume=0.4"
        ),
        "duration": 7,
    },
    "distant_footstep": {
        "desc": "Distant metallic footstep",
        "filter": (
            "anoisesrc=d=0.15:c=pink:r=44100:a=0.07,"
            "highpass=f=300,lowpass=f=2000,"
            "afade=t=in:st=0:d=0.01,afade=t=out:st=0.1:d=0.05,"
            "volume=0.35,"
            "apad=pad_dur=5"
        ),
        "duration": 5.5,
    },
    "rhythmic_boot_steps": {
        "desc": "Slow rhythmic boot steps",
        "filter": (
            "anoisesrc=d=0.18:c=pink:r=44100:a=0.08,"
            "highpass=f=150,lowpass=f=1500,"
            "afade=t=in:st=0:d=0.01,afade=t=out:st=0.12:d=0.05,"
            "volume=0.4[b1];"
            "anoisesrc=d=0.18:c=pink:r=44100:a=0.08,"
            "highpass=f=150,lowpass=f=1500,"
            "afade=t=in:st=0:d=0.01,afade=t=out:st=0.12:d=0.05,"
            "volume=0.4[b2];"
            "anoisesrc=d=0.18:c=pink:r=44100:a=0.08,"
            "highpass=f=150,lowpass=f=1500,"
            "afade=t=in:st=0:d=0.01,afade=t=out:st=0.12:d=0.05,"
            "volume=0.4[b3];"
            "anoisesrc=d=0.18:c=pink:r=44100:a=0.08,"
            "highpass=f=150,lowpass=f=1500,"
            "afade=t=in:st=0:d=0.01,afade=t=out:st=0.12:d=0.05,"
            "volume=0.4[b4];"
            "[b1][b2][b3][b4]concat=n=4:v=0:a=1,"
            "apad=pad_dur=4"
        ),
        "duration": 6,
    },
    "distant_clang": {
        "desc": "Distant metallic clang",
        "filter": (
            "sine=f=300:d=0.3,"
            "afade=t=in:st=0:d=0.005,afade=t=out:st=0.2:d=0.1,"
            "volume=0.4,"
            "apad=pad_dur=6"
        ),
        "duration": 6.5,
    },
    "sharp_inhale": {
        "desc": "Sharp sudden inhale",
        "filter": (
            "anoisesrc=d=0.4:c=pink:r=44100:a=0.08,"
            "highpass=f=500,lowpass=f=3500,"
            "afade=t=in:st=0:d=0.02,afade=t=out:st=0.3:d=0.1,"
            "volume=0.5,"
            "apad=pad_dur=6"
        ),
        "duration": 6.5,
    },
    "blade_swish": {
        "desc": "Swish of blade arc through air",
        "filter": (
            "anoisesrc=d=0.4:c=white:r=44100:a=0.10,"
            "highpass=f=1500,lowpass=f=8000,"
            "afade=t=in:st=0:d=0.01,afade=t=out:st=0.3:d=0.1,"
            "volume=0.6,"
            "apad=pad_dur=5"
        ),
        "duration": 5.5,
    },
}


# -------- step 1: dialogue --------
def step_dialogue(force: bool, dry_run: bool):
    print("\n" + "=" * 70)
    print("STEP 1: DIALOGUE — qwen3-tts-voiceclone (LTX-derived refs)")
    print("=" * 70)
    VOICE_LINES.mkdir(parents=True, exist_ok=True)

    shots = load_shots()
    lines = [
        (s["id"], s["speaker"], s["dialogue"])
        for s in shots
        if s.get("dialogue") and s.get("speaker")
    ]

    chars_needed = {sp for _, sp, _ in lines}
    for c in chars_needed:
        ref = VOICE_REFS / f"{c}_voice_ref.wav"
        if not ref.exists():
            print(f"  ERROR: voice ref missing: {ref}")
            return False

    failed = []
    for sid, speaker, text in lines:
        out = VOICE_LINES / f"shot_{sid:02d}_{speaker}.wav"
        if out.exists() and not force:
            print(f"  Shot {sid:2d} [{speaker}]: SKIP (exists)")
            continue
        ref = VOICE_REFS / f"{speaker}_voice_ref.wav"
        print(f"  Shot {sid:2d} [{speaker}]: \"{text[:60]}{'...' if len(text)>60 else ''}\"")
        if dry_run:
            continue
        t0 = time.time()
        try:
            with open(ref, "rb") as vf:
                files = [("voice", (ref.name, vf, "audio/wav"))]
                data = {"text": text, "seed": str(80600 + sid)}
                audio = run_workflow(VOICECLONE_WORKFLOW, data, files=files, timeout=180)
            save(audio, out)
            dur = probe_duration_ff(out)
            print(f"    -> {out.name} ({dur:.1f}s, {time.time()-t0:.0f}s)")
        except Exception as e:
            print(f"    FAILED: {e}")
            failed.append(sid)

    if failed:
        print(f"\n  FAILED: {failed}")
        return False
    return True


def step_ambient():
    print("\n" + "=" * 70)
    print("STEP 2: AMBIENT BEDS")
    print("=" * 70)
    AMBIENT_DIR.mkdir(parents=True, exist_ok=True)
    for bid, bed in AMBIENT_BEDS.items():
        out = AMBIENT_DIR / f"amb_{bid}.wav"
        if out.exists():
            print(f"  {bid}: EXISTS")
            continue
        print(f"  {bid}: {bed['desc']}")
        cmd = [
            "ffmpeg", "-y",
            "-f", "lavfi", "-i", bed["filter"],
            "-ac", "1", "-ar", str(SAMPLE_RATE),
            "-t", "30",
            str(out),
        ]
        run_ffmpeg(cmd, f"-> {out.name}")
    return True


def step_sfx():
    print("\n" + "=" * 70)
    print("STEP 3: SFX")
    print("=" * 70)
    SFX_DIR.mkdir(parents=True, exist_ok=True)
    for sid, sfx in SFX_LIB.items():
        out = SFX_DIR / f"sfx_{sid}.wav"
        if out.exists():
            print(f"  {sid}: EXISTS")
            continue
        print(f"  {sid}: {sfx['desc']}")
        cmd = [
            "ffmpeg", "-y",
            "-f", "lavfi", "-i", sfx["filter"],
            "-ac", "1", "-ar", str(SAMPLE_RATE),
            "-t", str(sfx["duration"]),
            str(out),
        ]
        run_ffmpeg(cmd, f"-> {out.name}")
    return True


def step_mix(force: bool):
    print("\n" + "=" * 70)
    print("STEP 4: PER-SHOT MIX")
    print("=" * 70)
    MIX_DIR.mkdir(parents=True, exist_ok=True)

    shots = load_shots()
    PERCUSSIVE = {
        "blade_shing", "wet_slice", "blade_swish",
        "sharp_inhale", "distant_clang",
    }

    for shot in shots:
        sid = shot["id"]
        duration = shot["duration"]
        out = MIX_DIR / f"shot_{sid:02d}_mix.wav"
        if out.exists() and not force:
            print(f"  Shot {sid:2d}: SKIP (exists)")
            continue

        print(f"\n  Shot {sid:2d} ({duration}s):")
        inputs: list[str] = []
        filter_parts: list[str] = []
        idx = 0

        amb_key = SHOT_LOCATION_AMBIENT.get(shot["location"], "warehouse")
        amb_path = AMBIENT_DIR / f"amb_{amb_key}.wav"
        if amb_path.exists():
            inputs.extend(["-i", str(amb_path)])
            filter_parts.append(
                f"[{idx}]atrim=duration={duration},"
                f"aformat=sample_rates={SAMPLE_RATE}:channel_layouts=mono,"
                f"volume=0.18[amb]"
            )
            idx += 1
            print(f"    Ambient: {amb_key}")
        else:
            inputs.extend(["-f", "lavfi", "-i", f"anullsrc=r={SAMPLE_RATE}:cl=mono"])
            filter_parts.append(f"[{idx}]atrim=duration={duration}[amb]")
            idx += 1

        mix_labels = ["[amb]"]

        speaker = shot.get("speaker")
        if speaker and shot.get("dialogue"):
            vl = VOICE_LINES / f"shot_{sid:02d}_{speaker}.wav"
            if vl.exists():
                line_dur = probe_duration_ff(vl)
                delay = 300 if duration - line_dur > 0.6 else 100
                inputs.extend(["-i", str(vl)])
                filter_parts.append(
                    f"[{idx}]aformat=sample_rates={SAMPLE_RATE}:channel_layouts=mono,"
                    f"adelay={delay}|{delay},"
                    f"volume=1.1[dl]"
                )
                mix_labels.append("[dl]")
                idx += 1
                print(f"    Dialogue: {vl.name} @ {delay}ms ({line_dur:.1f}s)")
            else:
                print(f"    MISSING dialogue: {vl.name}")

        if shot.get("sfx"):
            sfx_path = SFX_DIR / f"sfx_{shot['sfx']}.wav"
            if sfx_path.exists():
                percussive = shot["sfx"] in PERCUSSIVE
                sfx_delay = int(duration * 350) if percussive else 100
                inputs.extend(["-i", str(sfx_path)])
                filter_parts.append(
                    f"[{idx}]aformat=sample_rates={SAMPLE_RATE}:channel_layouts=mono,"
                    f"adelay={sfx_delay}|{sfx_delay},"
                    f"volume=0.55[sfx]"
                )
                mix_labels.append("[sfx]")
                idx += 1
                print(f"    SFX: {shot['sfx']} @ {sfx_delay}ms")
            else:
                print(f"    MISSING SFX: {shot['sfx']}")

        n = len(mix_labels)
        mix_str = "".join(mix_labels)
        filter_parts.append(
            f"{mix_str}amix=inputs={n}:duration=longest:"
            f"dropout_transition=0:normalize=0[mixed]"
        )
        filter_parts.append(
            f"[mixed]atrim=duration={duration},"
            f"aformat=sample_rates={SAMPLE_RATE}:channel_layouts=stereo[out]"
        )

        filter_complex = ";\n".join(filter_parts)
        cmd = ["ffmpeg", "-y", *inputs,
               "-filter_complex", filter_complex,
               "-map", "[out]", str(out)]
        if run_ffmpeg(cmd, f"-> {n}-track mix"):
            mix_dur = probe_duration_ff(out)
            print(f"    -> {out.name} ({mix_dur:.1f}s)")
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--step", choices=["dialogue", "ambient", "sfx", "mix", "all"], required=True)
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if args.step in ("dialogue", "all") and not args.dry_run:
        if not health_check():
            print("ERROR: ComfyUI not reachable")
            sys.exit(1)
        print("ComfyUI: OK")

    if args.step == "all":
        ok = step_dialogue(args.force, args.dry_run)
        if not ok and not args.dry_run:
            sys.exit(1)
        step_ambient()
        step_sfx()
        step_mix(args.force)
    elif args.step == "dialogue":
        ok = step_dialogue(args.force, args.dry_run)
        if not ok and not args.dry_run:
            sys.exit(1)
    elif args.step == "ambient":
        step_ambient()
    elif args.step == "sfx":
        step_sfx()
    elif args.step == "mix":
        step_mix(args.force)

    print("\nDONE")


if __name__ == "__main__":
    main()
