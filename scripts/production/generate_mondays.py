#!/usr/bin/env python3
"""
Mondays — Frame-to-Video Production Script.

Generates start frames (Flux 2 Dev i2i) from character references,
then animates them (LTX-2 i2v) for a conference-call format short film.

Handles three shot types:
  - individual: Single character webcam feed
  - group: 2x3 composite grid of all participants
  - reveal: CRT/security camera feed (Howie skeleton)

Usage:
    python3 scripts/production/generate_mondays.py --preflight
    python3 scripts/production/generate_mondays.py --frames-only
    python3 scripts/production/generate_mondays.py --video-only
    python3 scripts/production/generate_mondays.py
    python3 scripts/production/generate_mondays.py --shot 14
    python3 scripts/production/generate_mondays.py --shots 12-18
    python3 scripts/production/generate_mondays.py --assemble
    python3 scripts/production/generate_mondays.py --resume
"""

import argparse
import json
import re
import sys
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import requests
import yaml

from lib.config import ProjectConfig, find_project_root
from lib.ffmpeg import concatenate_clips

# ─── Defaults ─────────────────────────────────────────────────────────
DEFAULT_FPS = 25
VIDEO_WIDTH = 1280
VIDEO_HEIGHT = 720
FRAME_WIDTH = 1280
FRAME_HEIGHT = 720
MIN_FILE_SIZE = 10000   # 10KB
FRAME_MIN_SIZE = 5000   # 5KB
FRAME_TIMEOUT = 600     # 10 min per frame (Flux 2 Dev i2i can be slow on cold load)
VIDEO_TIMEOUT = 900     # 15 min per clip


def duration_to_frame_count(seconds, fps=25):
    """Convert duration in seconds to LTX-2 frame count."""
    raw = round(seconds * fps) + 1
    return max(25, min(raw, 501))


def safe_filename(name):
    """Convert a shot name to a safe filename slug."""
    return (
        name.lower()
        .replace(" ", "_")
        .replace("—", "")
        .replace("'", "")
        .replace(":", "")
        .replace("/", "_")
        .replace("-", "_")
        .strip("_")[:40]
    )


def load_config_and_paths(project_name=None):
    """Load project config and resolve key paths."""
    if project_name:
        codeywood_root = Path(__file__).parent.parent.parent
        project_root = codeywood_root / "projects" / project_name
    else:
        project_root = find_project_root()

    config = ProjectConfig(project_root)
    backend = config.backend_config
    comfyui = backend.get("comfyui", {})

    return {
        "project_root": project_root,
        "config": config,
        "comfyui_url": comfyui.get("base_url", "http://192.168.1.181:8100"),
        "video_workflow": comfyui.get("video_workflow", "ltx2-i2v"),
        "image_workflow": comfyui.get("image_workflow", "flux2-t2i"),
        "fps": comfyui.get("fps", DEFAULT_FPS),
    }


def resolve_character_reference(project_root, config, character_id):
    """Resolve a character's reference image path."""
    char_def = config.characters.get(character_id, {})
    ref_path = char_def.get("reference")
    if ref_path:
        full_path = project_root / ref_path
        if full_path.exists():
            return full_path
    return None


def resolve_atmosphere_reference(project_root, config, ref_key):
    """Resolve an atmosphere reference image path."""
    atmo = config._config.get("atmosphere_refs", {})
    ref_path = atmo.get(ref_key)
    if ref_path:
        full_path = project_root / ref_path
        if full_path.exists():
            return full_path
    return None


# ─── Frame Generation ─────────────────────────────────────────────────

def generate_frame_t2i(comfyui_url, workflow, prompt,
                       seed=None, width=FRAME_WIDTH, height=FRAME_HEIGHT,
                       timeout=FRAME_TIMEOUT):
    """Generate a frame via Flux 2 Dev text-to-image (no reference needed).

    Frame prompts contain full character descriptions, so t2i produces
    fresh compositions without being locked to a reference headshot.
    """
    url = f"{comfyui_url}/workflows/{workflow}"

    data = {
        "prompt": prompt,
        "steps": "20",
        "width": str(width),
        "height": str(height),
    }
    if seed is not None:
        data["seed"] = str(seed)

    print(f"  Workflow: {workflow} (t2i, {width}x{height}, 20 steps)")

    try:
        response = requests.post(url, data=data, timeout=timeout)
    except requests.exceptions.Timeout:
        print(f"  ERROR: Frame gen timed out after {timeout}s")
        return None
    except requests.exceptions.ConnectionError as e:
        print(f"  ERROR: Connection error: {e}")
        return None

    if response.status_code == 200 and len(response.content) > FRAME_MIN_SIZE:
        return response.content
    else:
        print(f"  ERROR: Frame gen HTTP {response.status_code}, {len(response.content)} bytes")
        if response.status_code != 200:
            print(f"  {response.text[:300]}")
        return None


def generate_frame_group(comfyui_url, workflow, project_root, config,
                          characters, prompt, seed=None,
                          timeout=FRAME_TIMEOUT):
    """
    Generate a group frame by compositing individual character mini-frames.

    1. Generate 6 individual frames at 640x360 (half size)
    2. Tile into a 3x2 grid -> 1920x720 -> scale to 1280x720
    """
    try:
        from PIL import Image
        import io
    except ImportError:
        print("  WARNING: PIL not available. Generating group frame as t2i instead.")
        return generate_frame_t2i(comfyui_url, workflow, prompt,
                                   seed=seed, timeout=timeout)

    mini_width, mini_height = 640, 360
    grid_cols, grid_rows = 3, 2
    frames = []

    for i, char_entry in enumerate(characters):
        char_id = char_entry.get("character", f"unknown_{i}")

        char_def = config.characters.get(char_id, {})
        visual_kw = char_def.get("visual_keywords", "person at desk")
        char_name = char_def.get("name", char_id)

        mini_prompt = (
            f"Webcam screenshot of {visual_kw}. "
            f"Seated at desk, looking directly at camera with a natural expression. "
            f"Their webcam window in a video conference call. "
            f"Soft front-facing webcam lighting, natural office background. "
            f"Photorealistic, 16:9 crop."
        )

        print(f"    Generating mini-frame for {char_id} ({char_name})...")

        # Pure t2i for all mini-frames (no i2i — we want fresh compositions)
        url = f"{comfyui_url}/workflows/{workflow}"
        data = {
            "prompt": mini_prompt,
            "steps": "12",
            "width": str(mini_width),
            "height": str(mini_height),
        }
        if seed is not None:
            data["seed"] = str(seed + i)

        try:
            resp = requests.post(url, data=data, timeout=timeout)
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
            print(f"    WARNING: Mini-frame request failed: {e}")
            placeholder = Image.new("RGB", (mini_width, mini_height), (40, 40, 40))
            frames.append(placeholder)
            continue

        if resp.status_code == 200 and len(resp.content) > 1000:
            img = Image.open(io.BytesIO(resp.content))
            img = img.resize((mini_width, mini_height), Image.LANCZOS)
            frames.append(img)
        else:
            print(f"    WARNING: Failed to generate mini-frame for {char_id}")
            # Create placeholder
            placeholder = Image.new("RGB", (mini_width, mini_height), (40, 40, 40))
            frames.append(placeholder)

    # Composite into grid
    grid_w = mini_width * grid_cols
    grid_h = mini_height * grid_rows
    grid = Image.new("RGB", (grid_w, grid_h), (30, 30, 30))

    for idx, frame in enumerate(frames[:6]):
        col = idx % grid_cols
        row = idx // grid_cols
        x = col * mini_width
        y = row * mini_height
        grid.paste(frame, (x, y))

    # Add thin grid lines
    from PIL import ImageDraw
    draw = ImageDraw.Draw(grid)
    line_color = (50, 50, 50)
    # Vertical lines
    for c in range(1, grid_cols):
        x = c * mini_width
        draw.line([(x, 0), (x, grid_h)], fill=line_color, width=2)
    # Horizontal lines
    for r in range(1, grid_rows):
        y = r * mini_height
        draw.line([(0, y), (grid_w, y)], fill=line_color, width=2)

    # Scale to output size
    grid = grid.resize((FRAME_WIDTH, FRAME_HEIGHT), Image.LANCZOS)

    # Convert to bytes
    buf = io.BytesIO()
    grid.save(buf, format="PNG")
    return buf.getvalue()


# ─── Video Generation ─────────────────────────────────────────────────

def generate_video_i2v(comfyui_url, workflow, frame_path, prompt,
                        negative_prompt, duration_seconds, seed=None,
                        fps=DEFAULT_FPS, timeout=VIDEO_TIMEOUT):
    """Generate video via LTX-2 i2v from a start frame."""
    frame_count = duration_to_frame_count(duration_seconds, fps)
    url = f"{comfyui_url}/workflows/{workflow}"

    data = {
        "prompt": prompt,
        "frame_count": str(frame_count),
    }
    if negative_prompt:
        data["negative_prompt"] = negative_prompt
    if seed is not None:
        data["seed"] = str(seed)

    with open(frame_path, "rb") as img_file:
        files = {"image": (Path(frame_path).name, img_file, "image/png")}
        try:
            response = requests.post(url, data=data, files=files, timeout=timeout)
        except requests.exceptions.Timeout:
            print(f"  ERROR: Video gen timed out after {timeout}s")
            return None
        except requests.exceptions.ConnectionError as e:
            print(f"  ERROR: Connection error: {e}")
            return None

    if response.status_code == 200 and len(response.content) > MIN_FILE_SIZE:
        return response.content
    else:
        print(f"  ERROR: Video gen HTTP {response.status_code}, {len(response.content)} bytes")
        if response.status_code != 200:
            print(f"  {response.text[:300]}")
        return None


# ─── Main Pipeline ────────────────────────────────────────────────────

def load_shot_list(scene_dir):
    """Load shot list YAML."""
    for name in ["shot_list.yaml", "shot_list_t2v.yaml"]:
        path = scene_dir / name
        if path.exists():
            with open(path) as f:
                data = yaml.safe_load(f)
            return data, path
    return None, None


def preflight(ctx, scene_dir, shots, negative_prompt, yaml_path):
    """Print preflight information without making API calls."""
    project_root = ctx["project_root"]
    config = ctx["config"]

    total_duration = sum(s.get("duration", 8) for s in shots)
    total_frames = sum(duration_to_frame_count(s.get("duration", 8)) for s in shots)

    print(f"PREFLIGHT — {scene_dir.name}")
    print(f"Shot list: {yaml_path.name}")
    print(f"Clips: {len(shots)}")
    print(f"Total duration: {total_duration}s")
    print(f"Total frames: {total_frames}")
    print(f"Image workflow: {ctx['image_workflow']}")
    print(f"Video workflow: {ctx['video_workflow']}")
    print(f"Negative prompt: {negative_prompt[:80]}...")
    print(f"Cost: $0.00 (ComfyUI local)")
    print()

    individual_count = 0
    group_count = 0
    reveal_count = 0

    for shot in shots:
        shot_id = shot["id"]
        name = shot.get("name", f"shot_{shot_id}")
        duration = shot.get("duration", 8)
        shot_type = shot.get("type", "individual")
        frame_prompt = shot.get("frame_prompt", "")
        video_prompt = shot.get("video_prompt", "")
        character = shot.get("character")
        frame_count = duration_to_frame_count(duration)

        # Count types
        if shot_type == "group":
            group_count += 1
        elif shot_type == "reveal":
            reveal_count += 1
        else:
            individual_count += 1

        # Check character reference
        ref_status = "N/A"
        if shot_type == "individual" and character:
            ref_path = resolve_character_reference(project_root, config, character)
            ref_status = "OK" if ref_path else "MISSING"
        elif shot_type == "reveal":
            ref_key = shot.get("frame_reference_key")
            if ref_key:
                ref_path = resolve_atmosphere_reference(project_root, config, ref_key)
                ref_status = "OK" if ref_path else "MISSING"

        print(f"  Shot {shot_id}: {name}")
        print(f"    Type: {shot_type} | Duration: {duration}s ({frame_count} frames)")
        print(f"    Frame prompt: {len(frame_prompt)} chars")
        print(f"    Video prompt: {len(video_prompt)} chars")
        if character:
            print(f"    Character: {character} | Ref: {ref_status}")
        if not frame_prompt:
            print(f"    WARNING: No frame_prompt")
        if not video_prompt:
            print(f"    WARNING: No video_prompt")
        print()

    print(f"Shot types: {individual_count} individual, {group_count} group, {reveal_count} reveal")
    print()

    # Write preflight JSON
    preflight_data = {
        "scene": scene_dir.name,
        "shot_list": yaml_path.name,
        "clip_count": len(shots),
        "total_duration_s": total_duration,
        "total_frames": total_frames,
        "image_workflow": ctx["image_workflow"],
        "video_workflow": ctx["video_workflow"],
        "cost": "$0.00",
        "shot_types": {
            "individual": individual_count,
            "group": group_count,
            "reveal": reveal_count,
        },
    }
    preflight_path = scene_dir / "clips" / "preflight.json"
    preflight_path.parent.mkdir(parents=True, exist_ok=True)
    with open(preflight_path, "w") as f:
        json.dump(preflight_data, f, indent=2)
    print(f"Preflight JSON: {preflight_path}")


def generate_frames(ctx, scene_dir, shots, shot_filter=None, resume=False):
    """Generate start frames for all shots. Returns dict of shot_id -> frame_path."""
    project_root = ctx["project_root"]
    config = ctx["config"]
    comfyui_url = ctx["comfyui_url"]
    image_workflow = ctx["image_workflow"]

    frames_dir = scene_dir / "frames"
    frames_dir.mkdir(parents=True, exist_ok=True)

    if shot_filter:
        shots = [s for s in shots if s["id"] in shot_filter]

    total = len(shots)
    frame_paths = {}
    start_time = time.time()

    print(f"\n{'='*60}")
    print(f"FRAME GENERATION — {scene_dir.name} ({total} frames)")
    print(f"Workflow: {image_workflow}")
    print(f"Output: {frames_dir}")
    print(f"{'='*60}\n")

    for i, shot in enumerate(shots):
        shot_id = shot["id"]
        name = shot.get("name", f"shot_{shot_id}")
        shot_type = shot.get("type", "individual")
        frame_prompt = shot.get("frame_prompt", "").strip()
        character = shot.get("character")
        seed = shot.get("seed")

        slug = safe_filename(name)
        frame_path = frames_dir / f"frame{shot_id:02d}_{slug}.png"

        # Resume: skip existing frames
        if resume and frame_path.exists() and frame_path.stat().st_size > FRAME_MIN_SIZE:
            print(f"SKIP (exists): frame{shot_id:02d}_{slug} ({frame_path.stat().st_size / 1024:.0f}KB)")
            frame_paths[shot_id] = frame_path
            continue

        if not frame_prompt:
            print(f"SKIP: No frame_prompt for shot {shot_id}")
            continue

        print(f"--- Frame {shot_id}: {name} [{i+1}/{total}] ---")
        print(f"  Type: {shot_type}")
        t0 = time.time()

        if shot_type == "group":
            # Composite grid from individual mini-frames
            characters = shot.get("frame_references", [])
            print(f"  Generating {len(characters)}-panel group composite...")
            image_bytes = generate_frame_group(
                comfyui_url, image_workflow, project_root, config,
                characters, frame_prompt, seed=seed,
            )
        else:
            # Individual character or reveal: use t2i with detailed prompt
            # (frame_prompts contain full character descriptions)
            label = character or shot_type
            print(f"  Generating t2i frame for {label}...")
            image_bytes = generate_frame_t2i(
                comfyui_url, image_workflow, frame_prompt, seed=seed,
            )

        elapsed = time.time() - t0

        if image_bytes:
            with open(frame_path, "wb") as f:
                f.write(image_bytes)

            # Save metadata
            meta = {
                "shot_id": shot_id,
                "shot_name": name,
                "type": shot_type,
                "character": character,
                "workflow": image_workflow,
                "frame_prompt": frame_prompt,
                "seed": seed,
                "elapsed_s": round(elapsed, 1),
                "bytes": len(image_bytes),
                "generated_at": datetime.now().isoformat(),
            }
            with open(frame_path.with_suffix(".json"), "w") as f:
                json.dump(meta, f, indent=2)

            kb = len(image_bytes) / 1024
            print(f"  OK: {kb:.0f}KB, {elapsed:.1f}s -> {frame_path.name}")
            frame_paths[shot_id] = frame_path
        else:
            print(f"  FAILED")

        # ETA
        if i < total - 1:
            elapsed_total = time.time() - start_time
            avg = elapsed_total / (i + 1)
            remaining = avg * (total - i - 1)
            print(f"  [{i+1}/{total} done, ~{remaining/60:.0f}m remaining]")
        print()

    total_elapsed = time.time() - start_time
    ok_count = len(frame_paths)
    print(f"Frames complete: {ok_count}/{total} in {total_elapsed/60:.1f}m\n")
    return frame_paths


def generate_videos(ctx, scene_dir, shots, frame_paths, negative_prompt,
                     shot_filter=None, resume=False):
    """Generate video clips from start frames. Returns list of output paths."""
    comfyui_url = ctx["comfyui_url"]
    video_workflow = ctx["video_workflow"]
    fps = ctx["fps"]

    clips_dir = scene_dir / "clips"
    clips_dir.mkdir(parents=True, exist_ok=True)

    if shot_filter:
        shots = [s for s in shots if s["id"] in shot_filter]

    total = len(shots)
    output_paths = []
    start_time = time.time()

    print(f"\n{'='*60}")
    print(f"VIDEO GENERATION — {scene_dir.name} ({total} clips)")
    print(f"Workflow: {video_workflow} ({fps}fps, {VIDEO_WIDTH}x{VIDEO_HEIGHT})")
    print(f"Output: {clips_dir}")
    print(f"{'='*60}\n")

    for i, shot in enumerate(shots):
        shot_id = shot["id"]
        name = shot.get("name", f"shot_{shot_id}")
        duration = shot.get("duration", 8)
        video_prompt = shot.get("video_prompt", "").strip()
        seed = shot.get("seed")
        frame_count = duration_to_frame_count(duration, fps)

        slug = safe_filename(name)
        out_path = clips_dir / f"clip{shot_id:02d}_{slug}.mp4"

        # Resume: skip existing
        if resume and out_path.exists() and out_path.stat().st_size > MIN_FILE_SIZE:
            print(f"SKIP (exists): clip{shot_id:02d}_{slug} ({out_path.stat().st_size / 1024:.0f}KB)")
            output_paths.append(out_path)
            continue

        # Check frame exists
        frame_path = frame_paths.get(shot_id)
        if not frame_path or not Path(frame_path).exists():
            print(f"SKIP: No frame for shot {shot_id} ({name})")
            continue

        if not video_prompt:
            print(f"SKIP: No video_prompt for shot {shot_id}")
            continue

        print(f"--- Clip {shot_id}: {name} ({duration}s, {frame_count} frames) [{i+1}/{total}] ---")
        print(f"  Frame: {Path(frame_path).name}")
        print(f"  Prompt ({len(video_prompt)} chars): {video_prompt[:150]}...")

        t0 = time.time()
        video_bytes = generate_video_i2v(
            comfyui_url, video_workflow, frame_path, video_prompt,
            negative_prompt, duration, seed=seed, fps=fps,
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
                "workflow": video_workflow,
                "fps": fps,
                "frame_path": str(frame_path),
                "video_prompt": video_prompt,
                "negative_prompt": negative_prompt,
                "seed": seed,
                "elapsed_s": round(elapsed, 1),
                "bytes": len(video_bytes),
                "pipeline": "i2v",
                "generated_at": datetime.now().isoformat(),
            }
            with open(out_path.with_suffix(".json"), "w") as f:
                json.dump(meta, f, indent=2)

            mb = len(video_bytes) / (1024 * 1024)
            print(f"  OK: {mb:.1f}MB, {elapsed:.1f}s")
            output_paths.append(out_path)
        else:
            print(f"  FAILED")

        if i < total - 1:
            elapsed_total = time.time() - start_time
            avg = elapsed_total / (i + 1)
            remaining = avg * (total - i - 1)
            print(f"  [{i+1}/{total} done, ~{remaining/60:.0f}m remaining]")
        print()

    total_elapsed = time.time() - start_time
    print(f"Videos complete: {len(output_paths)}/{total} in {total_elapsed/60:.1f}m\n")
    return output_paths


def assemble_scene(scene_dir):
    """Assemble clips into a scene video."""
    clips_dir = scene_dir / "clips"
    if not clips_dir.exists():
        print(f"  No clips/ for {scene_dir.name}")
        return None

    clips = sorted(clips_dir.glob("clip*.mp4"))
    if not clips:
        print(f"  No clips found in {clips_dir}")
        return None

    assembly_dir = scene_dir / "assembly"
    assembly_dir.mkdir(parents=True, exist_ok=True)
    output_path = assembly_dir / f"{scene_dir.name}_assembled.mp4"

    print(f"Assembling {scene_dir.name}: {len(clips)} clips -> {output_path.name}")
    result = concatenate_clips(clips, output_path)
    if result:
        print(f"  OK: {output_path}")
    return result


def parse_shot_range(shot_arg):
    """Parse shot range like '3-7' or single shot '3' into a set of IDs."""
    if "-" in shot_arg:
        start, end = shot_arg.split("-", 1)
        return set(range(int(start), int(end) + 1))
    return {int(shot_arg)}


def main():
    parser = argparse.ArgumentParser(description="Mondays — Frame-to-Video Production")
    parser.add_argument("--project", default="mondays", help="Project name")
    parser.add_argument("--scene", default="sc01", help="Scene ID")
    parser.add_argument("--shot", help="Single shot ID to generate")
    parser.add_argument("--shots", help="Shot range (e.g., 3-7)")
    parser.add_argument("--preflight", action="store_true",
                        help="Show plan without generating")
    parser.add_argument("--frames-only", action="store_true",
                        help="Generate start frames only (no video)")
    parser.add_argument("--video-only", action="store_true",
                        help="Generate video only (requires existing frames)")
    parser.add_argument("--resume", action="store_true",
                        help="Skip existing files")
    parser.add_argument("--assemble", action="store_true",
                        help="Assemble clips after generation")
    args = parser.parse_args()

    # Load config
    ctx = load_config_and_paths(args.project)
    project_root = ctx["project_root"]
    comfyui_url = ctx["comfyui_url"]

    # Resolve scene
    scene_dir = project_root / "PRODUCTION" / "EP01" / args.scene
    if not scene_dir.exists():
        print(f"ERROR: Scene directory not found: {scene_dir}")
        sys.exit(1)

    # Load shot list
    data, yaml_path = load_shot_list(scene_dir)
    if data is None:
        print(f"ERROR: No shot list found in {scene_dir}")
        sys.exit(1)

    shots = data.get("shots", [])
    if not shots:
        print(f"ERROR: No shots in {yaml_path}")
        sys.exit(1)

    # Negative prompt
    meta = data.get("metadata", {})
    negative_prompt = meta.get("negative_prompt",
        "blur, distort, low quality, cartoon, anime, deformed, extra limbs, "
        "text, watermark, illustration, painting"
    )

    # Shot filter
    shot_filter = None
    if args.shot:
        shot_filter = {int(args.shot)}
    elif args.shots:
        shot_filter = parse_shot_range(args.shots)

    # Preflight
    if args.preflight:
        preflight(ctx, scene_dir, shots, negative_prompt, yaml_path)
        return

    # Health check
    try:
        r = requests.get(f"{comfyui_url}/health", timeout=5)
        if r.status_code != 200:
            print(f"ERROR: ComfyUI not healthy at {comfyui_url}")
            sys.exit(1)
        print(f"ComfyUI: OK ({comfyui_url})")
    except Exception as e:
        print(f"ERROR: ComfyUI not reachable: {e}")
        sys.exit(1)

    pipeline_start = time.time()

    if args.video_only:
        # Video-only: load existing frames
        frames_dir = scene_dir / "frames"
        frame_paths = {}
        for shot in shots:
            shot_id = shot["id"]
            slug = safe_filename(shot.get("name", f"shot_{shot_id}"))
            fp = frames_dir / f"frame{shot_id:02d}_{slug}.png"
            if fp.exists():
                frame_paths[shot_id] = fp
        print(f"Found {len(frame_paths)} existing frames in {frames_dir}")
        output_paths = generate_videos(
            ctx, scene_dir, shots, frame_paths, negative_prompt,
            shot_filter=shot_filter, resume=args.resume,
        )
    elif args.frames_only:
        # Frames only
        frame_paths = generate_frames(
            ctx, scene_dir, shots,
            shot_filter=shot_filter, resume=args.resume,
        )
        output_paths = []
    else:
        # Full pipeline: frames then video
        frame_paths = generate_frames(
            ctx, scene_dir, shots,
            shot_filter=shot_filter, resume=args.resume,
        )
        output_paths = generate_videos(
            ctx, scene_dir, shots, frame_paths, negative_prompt,
            shot_filter=shot_filter, resume=args.resume,
        )

    # Assemble
    if args.assemble and output_paths:
        assemble_scene(scene_dir)

    total_elapsed = time.time() - pipeline_start
    print(f"\n{'='*60}")
    print(f"PIPELINE COMPLETE — {total_elapsed/60:.1f}m total")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
