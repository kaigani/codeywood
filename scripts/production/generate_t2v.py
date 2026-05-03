#!/usr/bin/env python3
"""
Generalized LTX-2 text-to-video clip generator.

Reads shot_list_t2v.yaml (preferred) or shot_list.yaml (fallback) from a scene
directory and generates T2V clips via ComfyUI's ltx2-t2v workflow.

Usage:
    python3 scripts/production/generate_t2v.py --scene sc01
    python3 scripts/production/generate_t2v.py --scene sc01 --shot 3
    python3 scripts/production/generate_t2v.py --scene sc01 --shots 3-7
    python3 scripts/production/generate_t2v.py --scene sc01 --preflight
    python3 scripts/production/generate_t2v.py --scene sc01 --assemble
    python3 scripts/production/generate_t2v.py --scene sc01 --resume
    python3 scripts/production/generate_t2v.py --all-scenes --resume --assemble
"""

import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import requests
import yaml

from lib.config import ProjectConfig
from lib.ffmpeg import concatenate_clips

# ─── Defaults ─────────────────────────────────────────────────────────
DEFAULT_WORKFLOW = "ltx2-t2v"
DEFAULT_FPS = 25
DEFAULT_WIDTH = 1280
DEFAULT_HEIGHT = 720
DEFAULT_TIMEOUT = 900
MIN_FILE_SIZE = 10000  # 10KB — anything smaller is a failed generation

DEFAULT_NEGATIVE = (
    "blur, distort, low quality, cartoon, anime, deformed, extra limbs, "
    "text, watermark, modern clothing, contemporary architecture"
)

import re


def duration_to_frame_count(seconds, fps=25):
    """Convert duration in seconds to LTX-2 frame count."""
    raw = round(seconds * fps) + 1
    return max(25, min(raw, 501))


def natural_sort_key(s):
    """Sort key for natural ordering of scene IDs (sc1, sc2, ..., sc10, sc11)."""
    return [int(c) if c.isdigit() else c.lower() for c in re.split(r'(\d+)', s)]


def find_project_root(project_name=None):
    """Find project root by name or by walking up from cwd."""
    if project_name:
        codeywood_root = Path(__file__).parent.parent.parent
        project_root = codeywood_root / "projects" / project_name
        if not project_root.exists():
            print(f"ERROR: Project not found at {project_root}")
            sys.exit(1)
        return project_root
    # Fall back to lib.config walk-up-from-cwd approach
    from lib.config import find_project_root as _find_root
    try:
        return _find_root()
    except FileNotFoundError as e:
        print(f"ERROR: {e}")
        sys.exit(1)


def resolve_scene_dir(project_root, scene_id):
    """Resolve scene directory from a scene ID like 'sc01'."""
    scene_dir = project_root / "PRODUCTION" / "EP01" / scene_id
    if not scene_dir.exists():
        print(f"ERROR: Scene directory not found: {scene_dir}")
        sys.exit(1)
    return scene_dir


def load_shot_list(scene_dir):
    """Load shot list YAML, preferring shot_list_t2v.yaml over shot_list.yaml."""
    t2v_path = scene_dir / "shot_list_t2v.yaml"
    fallback_path = scene_dir / "shot_list.yaml"

    if t2v_path.exists():
        yaml_path = t2v_path
    elif fallback_path.exists():
        yaml_path = fallback_path
    else:
        return None, None

    with open(yaml_path) as f:
        data = yaml.safe_load(f)

    return data, yaml_path


def get_prompt(shot):
    """Extract prompt from a shot, preferring video_prompt over prompt."""
    return (shot.get("video_prompt") or shot.get("prompt") or "").strip()


def get_negative_prompt(data):
    """Get negative prompt from YAML metadata or use default."""
    meta = data.get("t2v_metadata", {})
    return meta.get("negative_prompt", DEFAULT_NEGATIVE)


def get_comfyui_url(project_root):
    """Get ComfyUI URL from project config or default."""
    try:
        config = ProjectConfig(project_root)
        backend = config.backend_config
        if isinstance(backend, dict):
            comfyui = backend.get("comfyui", {})
            if isinstance(comfyui, dict) and comfyui.get("base_url"):
                return comfyui["base_url"]
    except Exception:
        pass
    return "http://192.168.1.181:8100"


def generate_t2v(comfyui_url, prompt, negative_prompt, frame_count,
                 seed=None, width=DEFAULT_WIDTH, height=DEFAULT_HEIGHT,
                 workflow=DEFAULT_WORKFLOW, timeout=DEFAULT_TIMEOUT):
    """Send T2V request to ComfyUI and return video bytes."""
    url = f"{comfyui_url}/workflows/{workflow}"
    data = {
        "prompt": prompt,
        "negative_prompt": negative_prompt,
        "frame_count": str(frame_count),
        "width": str(width),
        "height": str(height),
    }
    if seed is not None:
        data["seed"] = str(seed)

    try:
        response = requests.post(url, data=data, timeout=timeout)
    except requests.exceptions.Timeout:
        print(f"  ERROR: Request timed out after {timeout}s")
        return None
    except requests.exceptions.ConnectionError as e:
        print(f"  ERROR: Connection error: {e}")
        return None

    # Synchronous response (legacy): 200 + video bytes
    if response.status_code == 200 and len(response.content) > MIN_FILE_SIZE:
        return response.content

    # Async response (current): 200 or 202 with {job_id, status, position}
    if response.status_code in (200, 202):
        try:
            job_data = response.json()
            job_id = job_data.get("job_id")
        except Exception:
            job_id = None

        if job_id:
            print(f"  Job queued: {job_id}, polling...")
            elapsed = 0
            poll_interval = 5
            while elapsed < timeout:
                time.sleep(poll_interval)
                elapsed += poll_interval
                try:
                    poll_resp = requests.get(f"{comfyui_url}/jobs/{job_id}", timeout=30)
                except Exception:
                    continue
                if poll_resp.status_code != 200:
                    continue
                try:
                    status_data = poll_resp.json()
                    status = status_data.get("status", "")
                except Exception:
                    ct = poll_resp.headers.get("content-type", "")
                    if "video" in ct and len(poll_resp.content) > MIN_FILE_SIZE:
                        return poll_resp.content
                    continue
                if status == "completed":
                    try:
                        result_resp = requests.get(
                            f"{comfyui_url}/jobs/{job_id}/result", timeout=120
                        )
                        if result_resp.status_code == 200 and len(result_resp.content) > MIN_FILE_SIZE:
                            return result_resp.content
                        print(f"  ERROR: Result download failed: HTTP {result_resp.status_code}")
                        return None
                    except Exception as e:
                        print(f"  ERROR: Result download error: {e}")
                        return None
                if status in ("failed", "error"):
                    err = status_data.get("error", "unknown")
                    print(f"  ERROR: Job failed: {err}")
                    return None
                if elapsed % 30 == 0:
                    pos = status_data.get("position", "?")
                    print(f"    ... waiting ({elapsed}s, status={status}, position={pos})")
            print(f"  ERROR: Job timed out after {timeout}s")
            return None

    print(f"  ERROR: HTTP {response.status_code}, {len(response.content)} bytes")
    if response.status_code != 200:
        print(f"  {response.text[:300]}")
    return None


def safe_filename(name):
    """Convert a shot name to a safe filename slug."""
    return (
        name.lower()
        .replace(" ", "_")
        .replace("—", "")
        .replace("'", "")
        .replace(":", "")
        .replace("/", "_")
        .strip("_")
    )


def preflight(scene_dir, shots, negative_prompt, yaml_path):
    """Print preflight information without making API calls."""
    total_duration = sum(s.get("duration", 8) for s in shots)
    total_frames = sum(duration_to_frame_count(s.get("duration", 8)) for s in shots)

    print(f"PREFLIGHT — {scene_dir.name}")
    print(f"Shot list: {yaml_path.name}")
    print(f"Clips: {len(shots)}")
    print(f"Total duration: {total_duration}s")
    print(f"Total frames: {total_frames}")
    print(f"Negative prompt: {negative_prompt[:80]}...")
    print()

    for shot in shots:
        shot_id = shot["id"]
        name = shot.get("name", f"shot_{shot_id}")
        duration = shot.get("duration", 8)
        prompt = get_prompt(shot)
        frame_count = duration_to_frame_count(duration)
        seed = shot.get("seed")

        print(f"  Shot {shot_id}: {name}")
        print(f"    Duration: {duration}s ({frame_count} frames)")
        print(f"    Prompt: {len(prompt)} chars")
        if seed is not None:
            print(f"    Seed: {seed}")
        if not prompt:
            print(f"    WARNING: No prompt — will be skipped")
        elif len(prompt) > 2000:
            print(f"    WARNING: Prompt exceeds 2000 chars (may degrade quality)")
        print()

    # Preflight JSON
    preflight_data = {
        "scene": scene_dir.name,
        "shot_list": yaml_path.name,
        "clip_count": len(shots),
        "total_duration_s": total_duration,
        "total_frames": total_frames,
        "negative_prompt": negative_prompt,
        "cost": "$0.00 (ComfyUI local)",
        "shots": [
            {
                "id": s["id"],
                "name": s.get("name", f"shot_{s['id']}"),
                "duration_s": s.get("duration", 8),
                "frame_count": duration_to_frame_count(s.get("duration", 8)),
                "prompt_chars": len(get_prompt(s)),
                "seed": s.get("seed"),
                "has_prompt": bool(get_prompt(s)),
            }
            for s in shots
        ],
    }

    preflight_path = scene_dir / "clips_t2v" / "preflight.json"
    preflight_path.parent.mkdir(parents=True, exist_ok=True)
    with open(preflight_path, "w") as f:
        json.dump(preflight_data, f, indent=2)
    print(f"Preflight JSON: {preflight_path}")


def generate_scene(scene_dir, comfyui_url, shots, negative_prompt,
                   resume=False, shot_filter=None):
    """Generate T2V clips for a scene. Returns list of output paths."""
    output_dir = scene_dir / "clips_t2v"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Filter shots if requested
    if shot_filter is not None:
        shots = [s for s in shots if s["id"] in shot_filter]

    total = len(shots)
    results = {}
    output_paths = []
    start_time = time.time()

    total_duration = sum(s.get("duration", 8) for s in shots)
    print(f"Generating {total} LTX-2 t2v clips for {scene_dir.name}")
    print(f"Target duration: {total_duration}s")
    print(f"Output: {output_dir}")
    print(f"Backend: ComfyUI {DEFAULT_WORKFLOW} ({DEFAULT_FPS}fps, {DEFAULT_WIDTH}x{DEFAULT_HEIGHT})")
    if resume:
        print(f"Resume mode: skipping existing clips >10KB")
    print()

    for i, shot in enumerate(shots):
        shot_id = shot["id"]
        name = shot.get("name", f"shot_{shot_id}")
        duration = shot.get("duration", 8)
        prompt = get_prompt(shot)
        frame_count = duration_to_frame_count(duration)
        seed = shot.get("seed")

        slug = safe_filename(name)
        output_name = f"clip{shot_id:02d}_{slug}"
        out_path = output_dir / f"{output_name}.mp4"

        # Resume: skip if file exists and is >10KB
        if resume and out_path.exists() and out_path.stat().st_size > MIN_FILE_SIZE:
            print(f"SKIP (exists): {output_name} ({out_path.stat().st_size / 1024:.0f}KB)")
            results[shot_id] = "SKIPPED (exists)"
            output_paths.append(out_path)
            continue

        if not prompt:
            print(f"SKIP: No prompt for shot {shot_id} ({name})")
            results[shot_id] = "SKIPPED (no prompt)"
            continue

        print(f"{'=' * 60}")
        print(f"--- {output_name} ({duration}s, {frame_count} frames) [{i + 1}/{total}] ---")
        print(f"{'=' * 60}")
        print(f"  Prompt ({len(prompt)} chars):")
        print(f"  {prompt[:200]}...")
        print()

        t0 = time.time()
        video_bytes = generate_t2v(
            comfyui_url=comfyui_url,
            prompt=prompt,
            negative_prompt=negative_prompt,
            frame_count=frame_count,
            seed=seed,
            width=DEFAULT_WIDTH,
            height=DEFAULT_HEIGHT,
        )
        elapsed = time.time() - t0

        if video_bytes:
            with open(out_path, "wb") as f:
                f.write(video_bytes)

            meta = {
                "shot_id": shot_id,
                "shot_name": name,
                "duration_s": duration,
                "frame_count": frame_count,
                "workflow": DEFAULT_WORKFLOW,
                "width": DEFAULT_WIDTH,
                "height": DEFAULT_HEIGHT,
                "video_prompt": prompt,
                "negative_prompt": negative_prompt,
                "seed": seed,
                "elapsed_s": round(elapsed, 1),
                "bytes": len(video_bytes),
                "pipeline": "t2v",
                "generated_at": datetime.now().isoformat(),
            }
            with open(out_path.with_suffix(".json"), "w") as f:
                json.dump(meta, f, indent=2)

            mb = len(video_bytes) / (1024 * 1024)
            print(f"  OK: {mb:.1f}MB, {elapsed:.1f}s")
            results[shot_id] = f"OK ({elapsed:.1f}s)"
            output_paths.append(out_path)
        else:
            print(f"  FAILED")
            results[shot_id] = "FAILED"

        if i < total - 1:
            elapsed_total = time.time() - start_time
            avg = elapsed_total / (i + 1)
            remaining = avg * (total - i - 1)
            print(f"  [{i + 1}/{total} done, ~{remaining / 60:.0f}m remaining]")
        print()

    # Summary
    total_elapsed = time.time() - start_time
    print(f"{'=' * 60}")
    print(f"SUMMARY — {scene_dir.name}: {total} clips in {total_elapsed / 60:.1f}m")
    print(f"{'=' * 60}")
    for shot in shots:
        sid = shot["id"]
        name = shot.get("name", f"shot_{sid}")
        status = results.get(sid, "SKIPPED")
        print(f"  {name}: {status}")
    print()

    return output_paths


def assemble_scene(scene_dir):
    """Assemble clips_t2v/ into assembly_t2v/."""
    clips_dir = scene_dir / "clips_t2v"
    if not clips_dir.exists():
        print(f"  No clips_t2v/ for {scene_dir.name}")
        return None

    # Collect clips sorted by filename (clip01, clip02, ...)
    clips = sorted(clips_dir.glob("clip*.mp4"))
    if not clips:
        print(f"  No clips found in {clips_dir}")
        return None

    assembly_dir = scene_dir / "assembly_t2v"
    assembly_dir.mkdir(parents=True, exist_ok=True)
    output_path = assembly_dir / f"{scene_dir.name}_t2v_assembled.mp4"

    print(f"Assembling {scene_dir.name}: {len(clips)} clips")
    result = concatenate_clips(clips, output_path)
    return result


def discover_scenes(project_root):
    """Discover all scene directories in episode order (dynamic scan)."""
    ep_dir = project_root / "PRODUCTION" / "EP01"
    if not ep_dir.exists():
        print(f"ERROR: Episode directory not found: {ep_dir}")
        sys.exit(1)
    scenes = []
    for d in sorted(ep_dir.iterdir(), key=lambda p: natural_sort_key(p.name)):
        if d.is_dir() and d.name.startswith("sc"):
            scenes.append((d.name, d))
    return scenes


def parse_shot_range(shot_arg):
    """Parse shot range like '3-7' or single shot '3' into a set of IDs."""
    if "-" in shot_arg:
        start, end = shot_arg.split("-", 1)
        return set(range(int(start), int(end) + 1))
    return {int(shot_arg)}


def main():
    parser = argparse.ArgumentParser(description="Generate LTX-2 T2V clips")
    parser.add_argument("--project", help="Project name (e.g., hellmouth-cowboy)")
    parser.add_argument("--scene", help="Scene ID (e.g., sc01)")
    parser.add_argument("--shot", help="Single shot ID to generate")
    parser.add_argument("--shots", help="Shot range to generate (e.g., 3-7)")
    parser.add_argument("--all-scenes", action="store_true",
                        help="Generate all scenes in episode order")
    parser.add_argument("--preflight", action="store_true",
                        help="Show prompts/durations without generating")
    parser.add_argument("--resume", action="store_true",
                        help="Skip clips where .mp4 already exists and >10KB")
    parser.add_argument("--assemble", action="store_true",
                        help="Assemble clips into scene video after generation")
    args = parser.parse_args()

    if not args.scene and not args.all_scenes:
        parser.error("Either --scene or --all-scenes is required")

    project_root = find_project_root(args.project)
    comfyui_url = get_comfyui_url(project_root)

    # Build shot filter
    shot_filter = None
    if args.shot:
        shot_filter = {int(args.shot)}
    elif args.shots:
        shot_filter = parse_shot_range(args.shots)

    # Determine scenes to process
    if args.all_scenes:
        scenes = discover_scenes(project_root)
    else:
        scene_dir = resolve_scene_dir(project_root, args.scene)
        scenes = [(args.scene, scene_dir)]

    # Health check (skip for preflight)
    if not args.preflight:
        try:
            r = requests.get(f"{comfyui_url}/health", timeout=5)
            if r.status_code != 200:
                print(f"ERROR: ComfyUI not healthy at {comfyui_url}: {r.text}")
                sys.exit(1)
        except Exception as e:
            print(f"ERROR: ComfyUI not reachable at {comfyui_url}: {e}")
            sys.exit(1)

    # Process each scene
    all_start = time.time()
    scene_results = {}

    for scene_id, scene_dir in scenes:
        data, yaml_path = load_shot_list(scene_dir)
        if data is None:
            print(f"SKIP: No shot list found for {scene_id}")
            print()
            continue

        shots = data.get("shots", [])
        if not shots:
            print(f"SKIP: No shots defined in {yaml_path}")
            print()
            continue

        negative_prompt = get_negative_prompt(data)

        if args.preflight:
            preflight(scene_dir, shots, negative_prompt, yaml_path)
        else:
            output_paths = generate_scene(
                scene_dir, comfyui_url, shots, negative_prompt,
                resume=args.resume, shot_filter=shot_filter,
            )
            scene_results[scene_id] = output_paths

            if args.assemble and output_paths:
                assemble_scene(scene_dir)

    # Final summary for multi-scene runs
    if args.all_scenes and not args.preflight:
        total_elapsed = time.time() - all_start
        total_clips = sum(len(v) for v in scene_results.values())
        print(f"\n{'=' * 60}")
        print(f"ALL SCENES COMPLETE — {total_clips} clips in {total_elapsed / 60:.1f}m")
        print(f"{'=' * 60}")
        for scene_id, paths in scene_results.items():
            print(f"  {scene_id}: {len(paths)} clips")


if __name__ == "__main__":
    main()
