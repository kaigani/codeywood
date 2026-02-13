#!/usr/bin/env python3
"""
Generate Klein draft frames for SC01 v2 shot list.
One-off script — reads shot_list_v2.yaml directly.
"""

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.backends.comfyui_backend import ComfyUIImageBackend

import yaml

# ─── Config ───────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).parent.parent.parent / "projects" / "pirate-romance"
SCENE_DIR = PROJECT_ROOT / "PRODUCTION" / "EP01" / "sc01"
SHOT_LIST = SCENE_DIR / "shot_list_v2.yaml"
OUTPUT_DIR = SCENE_DIR / "frames" / "drafts_v2"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Identity sheets
MARS_ID = PROJECT_ROOT / "REFERENCES" / "identity_sheets" / "mars_identity_nano_banana_20260203_131447.png"
SILAS_ID = PROJECT_ROOT / "REFERENCES" / "identity_sheets" / "silas_human_identity_nano_banana_20260203_132208.png"

# Storyboards
BOARD_A = SCENE_DIR / "storyboards" / "sc01_board_A_the_execution_20260206_205125.png"
BOARD_B = SCENE_DIR / "storyboards" / "sc01_board_B_aftermath_20260206_205513.png"

# Backend
backend = ComfyUIImageBackend(
    base_url="http://192.168.1.181:8100",
    workflow="flux2-klein-t2i",  # Klein draft mode
    timeout=120,
)


def get_refs(shot):
    """Resolve reference images for a shot."""
    chars = shot.get("characters", [])
    shot_id = shot["id"]

    refs = []

    # Identity sheets first (highest priority)
    for char in chars:
        if char == "mars" and MARS_ID.exists():
            refs.append(MARS_ID)
        elif char == "silas" and SILAS_ID.exists():
            refs.append(SILAS_ID)

    # Storyboard second
    if shot_id <= 6 and BOARD_A.exists():
        refs.append(BOARD_A)
    elif shot_id > 6 and BOARD_B.exists():
        refs.append(BOARD_B)
    else:
        # No storyboard for non-character shots
        pass

    # Only return refs for character shots (t2i for no-character shots)
    if not chars:
        return []

    return refs


def generate_all():
    """Generate Klein draft frames for all v2 shots."""
    with open(SHOT_LIST) as f:
        data = yaml.safe_load(f)

    shots = data.get("shots", [])
    total = len(shots)
    results = {}
    start_time = time.time()

    print(f"Generating {total} Klein draft frames for SC01 v2")
    print(f"Output: {OUTPUT_DIR}")
    print(f"Backend: Klein (flux2-klein-t2i / flux2-klein-multiref)")
    print()

    for i, shot in enumerate(shots):
        shot_id = shot["id"]
        shot_name = shot.get("name", f"shot_{shot_id}")
        prompt = shot.get("frame_prompt", "").strip()

        if not prompt:
            print(f"SKIP: Shot {shot_id} has no frame_prompt")
            continue

        refs = get_refs(shot)
        ref_strs = [str(r) for r in refs]
        mode = f"Klein multiref, {len(refs)} refs" if refs else "Klein t2i"

        print(f"\n{'='*60}")
        print(f"--- {shot_id:02d}_{shot_name.lower().replace(' ', '_').replace('—', '')} ({mode}) [{i+1}/{total}] ---")
        print(f"{'='*60}")

        t0 = time.time()
        json_prompt = None  # set if multiref

        # For multiref, use JSON prompting if 2+ refs
        if len(refs) >= 2:
            # Build JSON-structured prompt for better subject attribution
            chars = shot.get("characters", [])
            json_prompt = _build_json_prompt(prompt, chars, refs)
            result = backend.generate_image(
                prompt=json_prompt,
                reference_urls=ref_strs,
                negative_prompt="cartoon, anime, illustration, painting, sketch, multiple panels, triptych, split image, text overlay, watermark",
                aspect_ratio="16:9",
                steps=12,
                cfg=3.5,
            )
        elif len(refs) == 1:
            result = backend.generate_image(
                prompt=prompt,
                reference_urls=ref_strs,
                negative_prompt="cartoon, anime, illustration, painting, sketch, multiple panels, triptych, split image, text overlay, watermark",
                aspect_ratio="16:9",
                steps=12,
                cfg=3.5,
            )
        else:
            result = backend.generate_image(
                prompt=prompt,
                negative_prompt="cartoon, anime, illustration, painting, sketch, multiple panels, triptych, split image, text overlay, watermark",
                aspect_ratio="16:9",
                steps=12,
                cfg=3.5,
            )

        elapsed = time.time() - t0

        if result.image_bytes and len(result.image_bytes) > 5000:
            out_path = OUTPUT_DIR / f"{shot_id:02d}_{shot_name.lower().replace(' ', '_').replace('—', '').replace(':', '')}.png"
            with open(out_path, "wb") as f:
                f.write(result.image_bytes)

            # Save metadata (full prompt, no truncation)
            actual_prompt = json_prompt if len(refs) >= 2 else prompt
            meta = {
                "prompt": actual_prompt,
                "frame_prompt": prompt,
                "workflow": result.metadata.get("workflow", "unknown"),
                "seed": result.metadata.get("seed"),
                "steps": result.metadata.get("steps", 12),
                "cfg": result.metadata.get("cfg"),
                "elapsed_s": round(elapsed, 1),
                "refs": len(refs),
                "ref_paths": ref_strs if refs else [],
            }
            with open(out_path.with_suffix(".json"), "w") as f:
                json.dump(meta, f, indent=2)

            print(f"  OK: {len(result.image_bytes)} bytes, {elapsed:.1f}s")
            results[shot_id] = f"OK ({elapsed:.1f}s)"
        else:
            print(f"  FAILED: No image data returned")
            results[shot_id] = "FAILED"

        if i < total - 1:
            elapsed_total = time.time() - start_time
            avg = elapsed_total / (i + 1)
            remaining = avg * (total - i - 1)
            print(f"  [{i+1}/{total} done, ~{remaining/60:.0f}m remaining]")

    # Summary
    total_elapsed = time.time() - start_time
    print(f"\n{'='*60}")
    print(f"SUMMARY — {total} frames in {total_elapsed/60:.1f}m")
    print(f"{'='*60}")
    for shot_id, status in results.items():
        shot = next(s for s in shots if s["id"] == shot_id)
        print(f"  {shot_id:02d}_{shot.get('name', '?')}: {status}")


def _build_json_prompt(prompt, chars, refs):
    """Build JSON-structured prompt for multiref shots."""
    # For shots with identity sheet + storyboard, use JSON format
    # to help Flux attribute subjects correctly
    parts = {"scene": prompt}

    ref_idx = 1
    for char in chars:
        if char == "mars":
            parts[f"subject_from_image_{ref_idx}"] = (
                "The young woman from image {}: dark curly hair, sun-darkened skin, "
                "freckles, dark borrowed shawl over head and shoulders".format(ref_idx)
            )
            ref_idx += 1
        elif char == "silas":
            parts[f"subject_from_image_{ref_idx}"] = (
                "The weathered man from image {}: salt-and-pepper hair, deep sun lines, "
                "late forties, ink-stained hands bound behind back".format(ref_idx)
            )
            ref_idx += 1

    # Storyboard is the last ref
    if ref_idx <= len(refs):
        parts[f"composition_from_image_{ref_idx}"] = (
            "Use the composition and framing from image {} as a rough guide".format(ref_idx)
        )

    return json.dumps(parts)


if __name__ == "__main__":
    # Check backend health
    if not backend.health_check():
        print("ERROR: ComfyUI service not reachable at http://192.168.1.181:8100")
        sys.exit(1)

    # Check identity sheets
    for name, path in [("Mars ID", MARS_ID), ("Silas ID", SILAS_ID)]:
        if not path.exists():
            print(f"WARNING: {name} not found at {path}")

    generate_all()
