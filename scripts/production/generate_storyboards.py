#!/usr/bin/env python3
"""
Storyboard Generation — Black & White Block-In Sketches
Generates storyboard grids from YAML board definitions using Nano Banana Pro text-to-image.

Usage:
    python scripts/production/generate_storyboards.py --scene PRODUCTION/EP01/sc01
    python scripts/production/generate_storyboards.py --scene PRODUCTION/EP01/sc01 --board A
    python scripts/production/generate_storyboards.py --all-scenes
    python scripts/production/generate_storyboards.py --all-scenes --dry-run
"""

import os
import sys
import json
import argparse
from datetime import datetime
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

import yaml
import fal_client
import requests

# Style constants — shared across all scenes
SKETCH_STYLE = """Black and white rough sketch on light gray background.
Simple silhouettes and shapes. Thick confident ink strokes.
Value blocking with simple hatching for shadow areas only.
Figures as dark silhouettes with minimal facial detail.
Composition reference only — NOT finished artwork.
Thin black dividing lines between panels. Shot labels below each panel."""

NEGATIVE = (
    "color, full color, colored, painted, digital painting, concept art, "
    "photorealistic, photograph, detailed rendering, detailed faces, "
    "detailed textures, shading, cel shading, anime, manga, "
    "finished artwork, polished, refined, smooth rendering, "
    "film grain, lens flare, bokeh, depth of field, "
    "realistic skin, realistic eyes, realistic hair, "
    "identity sheet, character sheet, model sheet"
)

COST_PER_BOARD = 0.15  # Nano Banana Pro ~$0.15/image


def find_project_root():
    """Walk up from cwd to find the project root (contains PRODUCTION/)."""
    current = Path.cwd()
    while current != current.parent:
        if (current / "PRODUCTION").is_dir():
            return current
        current = current.parent
    return Path.cwd()


def load_board_definitions(scene_dir: Path) -> dict:
    """Load storyboard_definitions.yaml from a scene directory."""
    yaml_path = scene_dir / "storyboard_definitions.yaml"
    if not yaml_path.exists():
        print(f"  ERROR: {yaml_path} not found")
        return None
    with open(yaml_path) as f:
        return yaml.safe_load(f)


def find_all_scenes(project_root: Path) -> list:
    """Find all scene directories with storyboard_definitions.yaml."""
    production_dir = project_root / "PRODUCTION"
    scenes = []
    for episode_dir in sorted(production_dir.iterdir()):
        if not episode_dir.is_dir():
            continue
        for scene_dir in sorted(episode_dir.iterdir()):
            if not scene_dir.is_dir():
                continue
            if (scene_dir / "storyboard_definitions.yaml").exists():
                rel = scene_dir.relative_to(project_root)
                scenes.append(str(rel))
    return scenes


def generate_board(board_id: str, board_data: dict, scene_id: str, output_dir: Path) -> Path:
    """Generate a single storyboard board via text-to-image."""
    print(f"\n{'='*60}")
    print(f"BOARD {board_id}: {board_data['name']} (Shots {board_data['shots']})")
    print(f"{'='*60}")

    prompt = board_data["prompt"]
    print(f"  Prompt length: {len(prompt)} chars")
    print(f"  Mode: text-to-image (NO reference images)")

    request = {
        "prompt": prompt,
        "aspect_ratio": "16:9",
        "resolution": "2K",
        "num_images": 1,
        "output_format": "png",
        "negative_prompt": NEGATIVE,
        "num_inference_steps": 40,
        "guidance_scale": 4.5,
    }

    try:
        def on_queue_update(update):
            status = type(update).__name__
            if status == "InProgress":
                logs = getattr(update, 'logs', [])
                if logs:
                    print(f"  [{status}] {logs[-1].get('message', '')[:60]}")
                else:
                    print(f"  [{status}]")
            elif status == "Completed":
                print(f"  [{status}]")

        result = fal_client.subscribe(
            "fal-ai/nano-banana-pro",
            arguments=request,
            with_logs=True,
            on_queue_update=on_queue_update,
        )

        image_url = None
        if result and "images" in result:
            image_url = result["images"][0].get("url")

        if image_url:
            response = requests.get(image_url)
            if response.status_code == 200:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                safe_name = board_data["name"].lower().replace(" ", "_").replace("&", "and")
                filename = f"{scene_id}_board_{board_id}_{safe_name}_{timestamp}.png"
                output_path = output_dir / filename

                with open(output_path, "wb") as f:
                    f.write(response.content)

                meta = {
                    "board": board_id,
                    "name": board_data["name"],
                    "shots": board_data["shots"],
                    "grid": board_data.get("grid", "unknown"),
                    "prompt": prompt,
                    "negative_prompt": NEGATIVE,
                    "endpoint": "fal-ai/nano-banana-pro",
                    "mode": "text-to-image",
                    "image_url": image_url,
                    "output_path": str(output_path),
                    "timestamp": timestamp,
                }
                meta_path = output_path.with_suffix(".json")
                with open(meta_path, "w") as f:
                    json.dump(meta, f, indent=2)

                print(f"  SAVED: {output_path.name}")
                return output_path
            else:
                print(f"  DOWNLOAD FAILED: {response.status_code}")
                return None
        else:
            print("  NO IMAGE IN RESULT")
            return None

    except Exception as e:
        print(f"  ERROR: {e}")
        import traceback
        traceback.print_exc()
        return None


def process_scene(scene_path: str, board_filter: str = None, dry_run: bool = False, project_root: Path = None):
    """Process a single scene's storyboard definitions."""
    if project_root is None:
        project_root = find_project_root()

    scene_dir = project_root / scene_path
    if not scene_dir.is_dir():
        print(f"ERROR: Scene directory not found: {scene_dir}")
        return {}

    defs = load_board_definitions(scene_dir)
    if not defs:
        return {}

    scene_id = defs.get("scene_id", scene_dir.name)
    scene_name = defs.get("scene_name", "Unknown")
    boards = defs.get("boards", {})

    print(f"\n{'#'*60}")
    print(f"SCENE: {scene_id} — {scene_name}")
    print(f"Boards: {', '.join(boards.keys())}")
    print(f"{'#'*60}")

    output_dir = scene_dir / "storyboards"
    output_dir.mkdir(parents=True, exist_ok=True)

    if board_filter:
        board_filter = board_filter.upper()
        if board_filter not in boards:
            print(f"  ERROR: Board {board_filter} not found. Available: {', '.join(boards.keys())}")
            return {}
        boards = {board_filter: boards[board_filter]}

    if dry_run:
        total_cost = len(boards) * COST_PER_BOARD
        print(f"\n  DRY RUN — {len(boards)} boards, est. ${total_cost:.2f}")
        for bid, bdata in boards.items():
            print(f"    Board {bid}: {bdata['name']} ({bdata.get('grid', '?')}) — {len(bdata['prompt'])} chars")
        return {bid: "dry_run" for bid in boards}

    results = {}
    for bid, bdata in boards.items():
        result = generate_board(bid, bdata, scene_id, output_dir)
        results[bid] = result

    return results


def main():
    parser = argparse.ArgumentParser(description="Generate storyboard sketches from YAML definitions")
    parser.add_argument("--scene", help="Scene path relative to project root (e.g., PRODUCTION/EP01/sc01)")
    parser.add_argument("--board", help="Generate only a specific board (e.g., A, B, EXTRA)")
    parser.add_argument("--all-scenes", action="store_true", help="Generate storyboards for all scenes with definitions")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be generated without calling API")
    args = parser.parse_args()

    if not args.scene and not args.all_scenes:
        parser.print_help()
        sys.exit(1)

    if not args.dry_run and not os.getenv("FAL_KEY"):
        print("ERROR: FAL_KEY not set")
        sys.exit(1)

    project_root = find_project_root()
    print(f"Project root: {project_root}")

    all_results = {}

    if args.all_scenes:
        scenes = find_all_scenes(project_root)
        if not scenes:
            print("No scenes with storyboard_definitions.yaml found")
            sys.exit(1)

        total_boards = 0
        for scene_path in scenes:
            defs = load_board_definitions(project_root / scene_path)
            if defs:
                total_boards += len(defs.get("boards", {}))

        total_cost = total_boards * COST_PER_BOARD
        print(f"\nBATCH MODE: {len(scenes)} scenes, {total_boards} boards, est. ${total_cost:.2f}")
        print(f"Scenes: {', '.join(scenes)}")

        for scene_path in scenes:
            results = process_scene(scene_path, dry_run=args.dry_run, project_root=project_root)
            all_results[scene_path] = results
    else:
        results = process_scene(args.scene, board_filter=args.board, dry_run=args.dry_run, project_root=project_root)
        all_results[args.scene] = results

    # Summary
    print(f"\n{'='*60}")
    print("GENERATION SUMMARY")
    print(f"{'='*60}")
    total_ok = 0
    total_fail = 0
    for scene_path, results in all_results.items():
        for bid, result in results.items():
            if result and result != "dry_run":
                status = "OK"
                total_ok += 1
                name = result.name if hasattr(result, 'name') else str(result)
            elif result == "dry_run":
                status = "DRY"
                name = "-"
            else:
                status = "FAIL"
                total_fail += 1
                name = "-"
            print(f"  {scene_path} Board {bid}: [{status}] {name}")

    if not args.dry_run:
        print(f"\n  {total_ok} OK, {total_fail} FAILED")


if __name__ == "__main__":
    main()
