#!/usr/bin/env python3
"""Re-poll specific running/pending LTX-2.3 jobs and save their results."""

from __future__ import annotations

import sys
import time
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import CLIPS_DIR, COMFYUI_BASE, save

JOBS = {
    "clip_07": "7a58b6ce285245aa85995783426e0719",
    "clip_08": "8d4aa16b7f594bafb2c188d49cf756f7",
    "clip_09": "56bf603f7fd74fe2b592abe18d721662",
    "clip_10": "84fe98d825194ebeb96f5369bd35a762",
    "clip_11": "7c58e190543043628fd898ca51e63f4a",
    "clip_12": "23bfeba4589e4b6c8a6830f89452a1a9",
}

PER_JOB_TIMEOUT = 3000  # 50 min — generous for queued tail


def main():
    pending = dict(JOBS)
    starts = {k: time.time() for k in pending}
    failed = []

    while pending:
        still = {}
        for name, job_id in pending.items():
            out = CLIPS_DIR / f"{name}.mp4"
            if out.exists():
                print(f"  {name}: SKIP (file exists)")
                continue
            try:
                status = requests.get(
                    f"{COMFYUI_BASE}/jobs/{job_id}", timeout=15
                ).json()
            except Exception as e:
                print(f"  {name}: poll error: {e}")
                still[name] = job_id
                continue
            st = status.get("status", "unknown")
            if st == "completed":
                r = requests.get(
                    f"{COMFYUI_BASE}/jobs/{job_id}/result", timeout=180
                )
                save(r.content, out)
                kb = len(r.content) / 1024
                print(f"  {name}: DONE ({kb:.0f} KB)")
            elif st in ("error", "failed"):
                print(f"  {name}: FAILED — {status.get('error')}")
                failed.append(name)
            else:
                elapsed = time.time() - starts[name]
                if elapsed > PER_JOB_TIMEOUT:
                    print(f"  {name}: TIMEOUT ({elapsed:.0f}s)")
                    failed.append(name)
                else:
                    pos = status.get("position")
                    print(f"  {name}: {st}{f' (pos {pos})' if pos is not None else ''}  [{elapsed:.0f}s]")
                    still[name] = job_id
        pending = still
        if pending:
            time.sleep(15)

    print(f"\n{'FAILED: ' + str(failed) if failed else 'ALL CLIPS DONE'}")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
