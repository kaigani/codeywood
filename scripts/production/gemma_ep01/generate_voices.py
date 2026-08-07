#!/usr/bin/env python3
"""
Voice design (qwen3-tts-voicedesign) for the 3 EP01 characters.

Reads voice_definitions.yaml and writes voice refs to REFERENCES/voice_refs/.

Usage:
    python generate_voices.py --dry-run
    python generate_voices.py
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
    VOICE_DEFS, VOICE_REFS,
    health_check, run_workflow, save,
)

WORKFLOW = "qwen3-tts-voicedesign"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    if not args.dry_run and not health_check():
        print("ERROR: ComfyUI not reachable")
        sys.exit(1)

    VOICE_REFS.mkdir(parents=True, exist_ok=True)

    with open(VOICE_DEFS) as f:
        defs = yaml.safe_load(f)
    characters = defs.get("characters", {})

    print("=" * 70)
    print(f"VOICE DESIGN — {WORKFLOW} — {len(characters)} characters")
    print("=" * 70)

    failed = []
    for cid, cdef in characters.items():
        out = VOICE_REFS / f"{cid}_voice_ref.wav"
        if out.exists() and not args.force:
            print(f"  {cid}: SKIP (exists)")
            continue

        instruct = cdef["instruct"].strip()
        sample_text = cdef["sample_text"].strip()
        seed = cdef.get("seed", 42)

        print(f"  {cid}: seed={seed}")
        print(f"    Instruct[80]: {instruct[:80]}...")
        print(f"    Sample[60]:   \"{sample_text[:60]}...\"")

        if args.dry_run:
            continue

        data = {
            "instruct": instruct,
            "text": sample_text,
            "seed": str(seed),
        }
        t0 = time.time()
        try:
            audio = run_workflow(WORKFLOW, data, timeout=300)
            save(audio, out)
            meta = {
                "character_id": cid,
                "instruct": instruct,
                "sample_text": sample_text,
                "seed": seed,
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
            }
            with open(out.with_suffix(".json"), "w") as f:
                json.dump(meta, f, indent=2)
            print(f"    -> Saved {out.name} ({len(audio)/1024:.0f} KB, {time.time()-t0:.0f}s)")
        except Exception as e:
            print(f"    FAILED: {e}")
            failed.append(cid)

    print("\n" + "=" * 70)
    if failed:
        print(f"FAILED: {failed}")
        sys.exit(1)
    print("DONE")


if __name__ == "__main__":
    main()
