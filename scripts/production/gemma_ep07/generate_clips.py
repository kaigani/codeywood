#!/usr/bin/env python3
"""
Generate EP07 rough-cut LTX-2.3 clips with NO references —
pure text-to-video, native audio.
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import requests
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import (
    CLIP_DEFS, CLIPS_DIR, COMFYUI_BASE, NEGATIVE, STYLE_TAG,
    health_check, save,
)

WORKFLOW = "ltx2-3"
SEED_BASE = 81300  # EP07 seed range


def load_defs() -> dict:
    with open(CLIP_DEFS) as f:
        return yaml.safe_load(f)


def build_prompt(shot: dict, location: str, chars: dict) -> str:
    char_descs = [chars[c] for c in shot["characters"] if c in chars]
    if len(char_descs) == 1:
        char_phrase = char_descs[0] + "."
    elif len(char_descs) > 1:
        char_phrase = "; ".join(char_descs) + "."
    else:
        char_phrase = ""

    parts = [
        f"{shot['shot_type']} — {shot['framing']}.",
        f"Location: {location}",
    ]
    if char_phrase:
        parts.append(f"Characters: {char_phrase}")
    parts.append(shot["action"].strip())
    if shot.get("dialogue") and shot.get("speaker"):
        speaker_name = chars.get(shot["speaker"], shot["speaker"]).split(",")[0]
        parts.append(f'{speaker_name} says: "{shot["dialogue"]}"')
    if shot.get("sfx"):
        parts.append(f"Ambient: {shot['sfx']}.")
    parts.append(STYLE_TAG)
    return " ".join(parts)


def submit(params: dict) -> str:
    url = f"{COMFYUI_BASE}/workflows/{WORKFLOW}"
    r = requests.post(url, data=params, timeout=120)
    if r.status_code not in (200, 202):
        raise RuntimeError(f"submit {r.status_code}: {r.text[:300]}")
    body = r.json()
    return body["job_id"]


def poll_jobs(jobs: dict, timeout: int = 3000) -> list[str]:
    pending = dict(jobs)
    failed = []
    while pending:
        still: dict = {}
        for name, (job_id, t0, out_path) in pending.items():
            elapsed = time.time() - t0
            if elapsed > timeout:
                print(f"  {name}: TIMEOUT after {elapsed:.0f}s")
                failed.append(name)
                continue
            try:
                status = requests.get(f"{COMFYUI_BASE}/jobs/{job_id}", timeout=10).json()
            except Exception:
                still[name] = (job_id, t0, out_path)
                continue
            st = status.get("status", "unknown")
            if st == "completed":
                r = requests.get(f"{COMFYUI_BASE}/jobs/{job_id}/result", timeout=180)
                save(r.content, out_path)
                kb = len(r.content) / 1024
                print(f"  {name}: DONE ({elapsed:.0f}s, {kb:.0f} KB)")
            elif st in ("error", "failed"):
                print(f"  {name}: FAILED — {status.get('error')}")
                failed.append(name)
            else:
                still[name] = (job_id, t0, out_path)
        pending = still
        if pending:
            time.sleep(12)
    return failed


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--shot", type=int, default=0)
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--timeout", type=int, default=3000)
    args = ap.parse_args()

    if not (args.all or args.shot):
        ap.print_help()
        sys.exit(1)

    CLIPS_DIR.mkdir(parents=True, exist_ok=True)

    if not args.dry_run and not health_check():
        print("ERROR: ComfyUI not reachable")
        sys.exit(1)

    defs = load_defs()
    shots = defs["shots"]
    location = defs["location_prose"].strip()
    chars = defs["characters"]

    if args.shot:
        shots = [s for s in shots if s["id"] == args.shot]
        if not shots:
            print(f"No shot {args.shot}")
            sys.exit(1)

    total_dur = sum(s["duration"] for s in shots)
    print("=" * 70)
    print(f"EP07 ROUGH CUT — {WORKFLOW} t2v — {len(shots)} shots — total {total_dur}s")
    print("=" * 70)

    jobs: dict = {}
    skipped = 0
    failed: list[str] = []

    for shot in shots:
        sid = shot["id"]
        name = f"clip_{sid:02d}"
        out = CLIPS_DIR / f"{name}.mp4"
        if out.exists() and not args.force:
            skipped += 1
            print(f"  Shot {sid:2d}: SKIP (exists)")
            continue

        prompt = build_prompt(shot, location, chars)
        dur = shot["duration"]

        params = {
            "prompt": prompt,
            "negative_prompt": NEGATIVE,
            "duration": str(dur),
            "width": "1920",
            "height": "1080",
            "seed": str(SEED_BASE + sid),
            "img_compression": "33",
            "static_camera": "0",
        }

        print(f"  Shot {sid:2d}: dur={dur}s")
        print(f"    Prompt[160]: {prompt[:160]}...")

        if args.dry_run:
            continue

        try:
            job_id = submit(params)
            jobs[name] = (job_id, time.time(), out)
            print(f"    -> submitted [{job_id}]")
        except Exception as e:
            print(f"    SUBMIT FAILED: {e}")
            failed.append(name)

    if skipped:
        print(f"\n({skipped} clips already exist)")

    if jobs:
        print(f"\nPolling {len(jobs)} jobs (timeout {args.timeout}s each)...")
        failed.extend(poll_jobs(jobs, timeout=args.timeout))

    print("\n" + "=" * 70)
    generated = len(shots) - len(failed) - skipped
    if failed:
        print(f"FAILED ({len(failed)}): {failed}")
    print(f"DONE — {generated} new + {skipped} existing = {generated + skipped}/{len(shots)}")
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
