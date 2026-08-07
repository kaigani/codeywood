#!/usr/bin/env python3
"""
Voice ref pipeline via LTX-2.3:
  1. z-image-base-t2i — generate speaker portrait (MCU to camera) per character
  2. LTX-2.3 — generate clip of character speaking sample_text with vocal cues
  3. ffmpeg — extract audio from the clip into a clean WAV voice ref
  4. (informant) qwen3-tts-voicedesign for the single-line NPC

Usage:
    python generate_voice_refs_ltx.py --dry-run
    python generate_voice_refs_ltx.py --all
    python generate_voice_refs_ltx.py --char kane
    python generate_voice_refs_ltx.py --force
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import (
    NEGATIVE, STYLE_TAG, VOICE_DEFS,
    VOICE_PORTRAITS, VOICE_VIDEO_REFS, VOICE_REFS,
    health_check, run_ffmpeg, run_workflow, save,
)

T2I_WORKFLOW = "z-image-base-t2i"
LTX_WORKFLOW = "ltx2-3"
VOICEDESIGN_WORKFLOW = "qwen3-tts-voicedesign"

# LTX duration must cover the sample audio comfortably. Sample texts are
# ~12-18 words → ~6-8s. Pad to 9s for headroom.
LTX_DURATION = 9


def step_portrait(cid: str, cdef: dict, force: bool, dry_run: bool) -> Path | None:
    out = VOICE_PORTRAITS / f"{cid}_speaker.png"
    if out.exists() and not force:
        print(f"    portrait: SKIP (exists)")
        return out
    prompt = cdef["portrait_prompt"].strip() + " " + STYLE_TAG
    seed = cdef.get("portrait_seed", 80100)
    print(f"    portrait: t2i seed={seed}")
    if dry_run:
        return out
    data = {
        "prompt": prompt,
        "negative_prompt": NEGATIVE,
        "seed": str(seed),
        "width": "1024",
        "height": "1536",
        "steps": "25",
        "cfg": "4",
    }
    t0 = time.time()
    try:
        content = run_workflow(T2I_WORKFLOW, data, timeout=300)
        save(content, out)
        print(f"      -> {out.name} ({len(content)/1024:.0f} KB, {time.time()-t0:.0f}s)")
        return out
    except Exception as e:
        print(f"      FAILED: {e}")
        return None


def step_ltx_clip(cid: str, cdef: dict, portrait: Path,
                  force: bool, dry_run: bool) -> Path | None:
    out = VOICE_VIDEO_REFS / f"{cid}_speaker.mp4"
    if out.exists() and not force:
        print(f"    ltx clip: SKIP (exists)")
        return out
    sample = cdef["sample_text"].strip()
    vocal = cdef["vocal_direction"].strip()
    name = cdef.get("name", cid.title())
    # Build LTX prompt: framing + vocal direction + dialogue + style
    prompt = (
        f"Medium close-up cinematic portrait of {name} speaking directly to "
        f"camera. Vocal direction: {vocal} "
        f"{name} says: \"{sample}\" "
        f"Natural lip-sync. Subtle head and shoulder movement. "
        f"Lighting holds. " + STYLE_TAG
    )
    seed = cdef.get("seed", 80200)
    print(f"    ltx clip: {LTX_DURATION}s, seed={seed}")
    print(f"      vocal: {vocal[:80]}...")
    print(f"      line: \"{sample[:60]}{'...' if len(sample)>60 else ''}\"")
    if dry_run:
        return out
    data = {
        "prompt": prompt,
        "negative_prompt": NEGATIVE,
        "duration": str(LTX_DURATION),
        "width": "1024",
        "height": "1536",
        "seed": str(seed),
        "img_compression": "33",
        "static_camera": "0",
    }
    t0 = time.time()
    try:
        with open(portrait, "rb") as fh:
            files = [("first_frame", (portrait.name, fh, "image/png"))]
            content = run_workflow(LTX_WORKFLOW, data, files=files, timeout=1800)
        save(content, out)
        print(f"      -> {out.name} ({len(content)/1024:.0f} KB, {time.time()-t0:.0f}s)")
        return out
    except Exception as e:
        print(f"      FAILED: {e}")
        return None


def step_extract_audio(cid: str, clip: Path, force: bool, dry_run: bool) -> Path | None:
    out = VOICE_REFS / f"{cid}_voice_ref.wav"
    if out.exists() and not force:
        print(f"    extract: SKIP (exists)")
        return out
    print(f"    extract: ffmpeg")
    if dry_run:
        return out
    out.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "ffmpeg", "-y", "-i", str(clip),
        "-vn", "-acodec", "pcm_s16le",
        "-ar", "44100", "-ac", "1",
        str(out),
    ]
    if run_ffmpeg(cmd, f"-> {out.name}"):
        meta = {
            "character_id": cid,
            "source_clip": str(clip.relative_to(clip.parents[2])),
            "pipeline": "ltx2-3 -> ffmpeg extract",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        }
        with open(out.with_suffix(".json"), "w") as f:
            json.dump(meta, f, indent=2)
        return out
    return None


def voicedesign_for_informant(cdef: dict, force: bool, dry_run: bool) -> Path | None:
    cid = "informant"
    out = VOICE_REFS / f"{cid}_voice_ref.wav"
    if out.exists() and not force:
        print(f"    informant: SKIP (exists)")
        return out
    print(f"    informant: qwen3-tts-voicedesign")
    instruct = cdef["instruct"].strip()
    sample = cdef["sample_text"].strip()
    seed = cdef.get("seed", 80204)
    if dry_run:
        return out
    out.parent.mkdir(parents=True, exist_ok=True)
    data = {"instruct": instruct, "text": sample, "seed": str(seed)}
    t0 = time.time()
    try:
        audio = run_workflow(VOICEDESIGN_WORKFLOW, data, timeout=300)
        save(audio, out)
        meta = {
            "character_id": cid,
            "instruct": instruct,
            "sample_text": sample,
            "seed": seed,
            "pipeline": "qwen3-tts-voicedesign (NPC single-line)",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        }
        with open(out.with_suffix(".json"), "w") as f:
            json.dump(meta, f, indent=2)
        print(f"      -> {out.name} ({len(audio)/1024:.0f} KB, {time.time()-t0:.0f}s)")
        return out
    except Exception as e:
        print(f"      FAILED: {e}")
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--char", default="", help="single character id")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if not (args.all or args.char):
        ap.print_help()
        sys.exit(1)

    if not args.dry_run and not health_check():
        print("ERROR: ComfyUI not reachable")
        sys.exit(1)

    VOICE_PORTRAITS.mkdir(parents=True, exist_ok=True)
    VOICE_VIDEO_REFS.mkdir(parents=True, exist_ok=True)
    VOICE_REFS.mkdir(parents=True, exist_ok=True)

    with open(VOICE_DEFS) as f:
        defs = yaml.safe_load(f)["characters"]

    if args.char:
        if args.char not in defs:
            print(f"ERROR: unknown character {args.char}")
            sys.exit(1)
        defs = {args.char: defs[args.char]}

    print("=" * 70)
    print(f"EP02 VOICE REFS — LTX-2.3 -> audio extract")
    print("=" * 70)

    failed = []
    for cid, cdef in defs.items():
        print(f"\n[{cid}] {cdef.get('name', cid)}")
        if cdef.get("voicedesign_only"):
            r = voicedesign_for_informant(cdef, args.force, args.dry_run)
            if not r and not args.dry_run:
                failed.append(cid)
            continue

        portrait = step_portrait(cid, cdef, args.force, args.dry_run)
        if not portrait or (not portrait.exists() and not args.dry_run):
            failed.append(cid)
            continue
        clip = step_ltx_clip(cid, cdef, portrait, args.force, args.dry_run)
        if not clip or (not clip.exists() and not args.dry_run):
            failed.append(cid)
            continue
        wav = step_extract_audio(cid, clip, args.force, args.dry_run)
        if not wav or (not wav.exists() and not args.dry_run):
            failed.append(cid)
            continue

    print("\n" + "=" * 70)
    if failed:
        print(f"FAILED: {failed}")
        sys.exit(1)
    print("DONE — voice refs ready for qwen3-tts-voiceclone")


if __name__ == "__main__":
    main()
