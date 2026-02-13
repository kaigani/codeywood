#!/usr/bin/env python3
"""
Generate LTX-2 video clips for SC01 v2 using Klein draft frames as start frames.
"""

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.backends.comfyui_backend import ComfyUIVideoBackend

import yaml

# ─── Config ───────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).parent.parent.parent / "projects" / "pirate-romance"
SCENE_DIR = PROJECT_ROOT / "PRODUCTION" / "EP01" / "sc01"
SHOT_LIST = SCENE_DIR / "shot_list_v2.yaml"
CLIP_DEFS = SCENE_DIR / "clip_definitions_v2.yaml"
DRAFTS_DIR = SCENE_DIR / "frames" / "drafts_v2"
OUTPUT_DIR = SCENE_DIR / "clips_v2"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Backend
backend = ComfyUIVideoBackend(
    base_url="http://192.168.1.181:8100",
    workflow="ltx2-i2v",
    fps=25,
    timeout=900,
)


def find_draft_frame(shot_id, shot_name):
    """Find the Klein draft frame for a shot."""
    # Match by filename pattern
    for png in sorted(DRAFTS_DIR.glob("*.png")):
        if png.name.startswith(f"{shot_id:02d}_"):
            return png
    return None


def generate_all():
    """Generate LTX-2 video clips for all v2 shots."""
    with open(SHOT_LIST) as f:
        shot_data = yaml.safe_load(f)

    with open(CLIP_DEFS) as f:
        clip_data = yaml.safe_load(f)

    clips = clip_data.get("clips", [])
    shots = {s["id"]: s for s in shot_data.get("shots", [])}
    total = len(clips)
    results = {}
    start_time = time.time()

    print(f"Generating {total} LTX-2 video clips for SC01 v2")
    print(f"Output: {OUTPUT_DIR}")
    print(f"Backend: ComfyUI ltx2-i2v (25fps)")
    print()

    for i, clip in enumerate(clips):
        clip_id = clip["id"]
        clip_name = clip.get("name", f"clip_{clip_id}")
        output_name = clip.get("output_name", f"clip{clip_id:02d}")
        duration = clip.get("duration", 8)
        shot_ids = clip.get("shots_covered", [clip_id])

        # Get the video prompt from the shot list
        shot = shots.get(shot_ids[0])
        if not shot:
            print(f"SKIP: No shot found for clip {clip_id}")
            continue

        video_prompt = shot.get("video_prompt", "").strip()
        if not video_prompt:
            # Fall back to clip narrative prompt
            video_prompt = clip.get("narrative_prompt", "").strip()

        if not video_prompt:
            print(f"SKIP: No video prompt for clip {clip_id}")
            continue

        # Find start frame
        start_frame = find_draft_frame(clip_id, clip_name)
        if not start_frame:
            print(f"SKIP: No draft frame found for clip {clip_id}")
            continue

        print(f"\n{'='*60}")
        print(f"--- {output_name} ({duration}s) [{i+1}/{total}] ---")
        print(f"{'='*60}")

        t0 = time.time()

        result = backend.generate_video(
            start_frame=start_frame,
            prompt=video_prompt,
            duration_seconds=float(duration),
            negative_prompt="blur, distort, low quality, cartoon, anime, deformed, extra limbs, text, watermark",
        )

        elapsed = time.time() - t0

        if result.video_bytes and len(result.video_bytes) > 10000:
            out_path = OUTPUT_DIR / f"{output_name}.mp4"
            with open(out_path, "wb") as f:
                f.write(result.video_bytes)

            # Save full metadata
            meta = {
                "clip_id": clip_id,
                "clip_name": clip_name,
                "shot_ids": shot_ids,
                "duration_s": duration,
                "start_frame": str(start_frame),
                "video_prompt": video_prompt,
                "workflow": result.metadata.get("workflow", "ltx2-i2v"),
                "frame_count": result.metadata.get("frame_count"),
                "fps": result.metadata.get("fps", 25),
                "elapsed_s": round(elapsed, 1),
                "bytes": len(result.video_bytes),
            }
            with open(out_path.with_suffix(".json"), "w") as f:
                json.dump(meta, f, indent=2)

            mb = len(result.video_bytes) / (1024 * 1024)
            print(f"  OK: {mb:.1f}MB, {elapsed:.1f}s")
            results[clip_id] = f"OK ({elapsed:.1f}s)"
        else:
            print(f"  FAILED")
            results[clip_id] = "FAILED"

        if i < total - 1:
            elapsed_total = time.time() - start_time
            avg = elapsed_total / (i + 1)
            remaining = avg * (total - i - 1)
            print(f"  [{i+1}/{total} done, ~{remaining/60:.0f}m remaining]")

    # Summary
    total_elapsed = time.time() - start_time
    print(f"\n{'='*60}")
    print(f"SUMMARY — {total} clips in {total_elapsed/60:.1f}m")
    print(f"{'='*60}")
    for clip in clips:
        cid = clip["id"]
        name = clip.get("output_name", f"clip{cid:02d}")
        status = results.get(cid, "SKIPPED")
        print(f"  {name}: {status}")


if __name__ == "__main__":
    if not backend.health_check():
        print("ERROR: ComfyUI not reachable at http://192.168.1.181:8100")
        sys.exit(1)

    generate_all()
