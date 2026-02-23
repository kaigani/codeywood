#!/usr/bin/env python3
"""
Assemble all per-scene T2V assemblies into a full EP01 rough cut.

Discovers scenes with assembly_t2v/ or clips_t2v/ directories,
concatenates in episode order, writes manifest JSON.

Usage:
    python3 scripts/production/assemble_episode_t2v.py
    python3 scripts/production/assemble_episode_t2v.py --assemble-scenes
"""

import argparse
import json
import re
import sys
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.ffmpeg import concatenate_clips, probe_duration


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
    from lib.config import find_project_root as _find_root
    try:
        return _find_root()
    except FileNotFoundError as e:
        print(f"ERROR: {e}")
        sys.exit(1)


def discover_scenes(ep_dir):
    """Discover all scene directories in natural sort order."""
    scenes = []
    for d in sorted(ep_dir.iterdir(), key=lambda p: natural_sort_key(p.name)):
        if d.is_dir() and d.name.startswith("sc"):
            scenes.append(d.name)
    return scenes


def get_episode_title(project_root):
    """Get episode title from PROJECT_CONFIG.yaml or default."""
    try:
        import yaml
        config_path = project_root / "PROJECT_CONFIG.yaml"
        with open(config_path) as f:
            config = yaml.safe_load(f)
        name = config.get("project", {}).get("name", "Episode")
        return f"{name} — T2V Rough Cut"
    except Exception:
        return "T2V Rough Cut"


def find_scene_assembly(scene_dir):
    """Find the assembly video for a scene, checking assembly_t2v/ first."""
    # Check for pre-assembled video
    assembly_dir = scene_dir / "assembly_t2v"
    if assembly_dir.exists():
        assemblies = sorted(assembly_dir.glob("*.mp4"))
        if assemblies:
            return assemblies[0]

    # Fall back to assembling from clips_t2v/
    clips_dir = scene_dir / "clips_t2v"
    if clips_dir.exists():
        clips = sorted(clips_dir.glob("clip*.mp4"))
        if clips:
            # Auto-assemble
            assembly_dir.mkdir(parents=True, exist_ok=True)
            output_path = assembly_dir / f"{scene_dir.name}_t2v_assembled.mp4"
            result = concatenate_clips(clips, output_path)
            return result

    return None


def main():
    parser = argparse.ArgumentParser(
        description="Assemble EP01 T2V rough cut from per-scene assemblies"
    )
    parser.add_argument("--project", help="Project name (e.g., hellmouth-cowboy)")
    parser.add_argument("--assemble-scenes", action="store_true",
                        help="Also assemble individual scenes from clips before episode assembly")
    args = parser.parse_args()

    project_root = find_project_root(args.project)
    ep_dir = project_root / "PRODUCTION" / "EP01"
    deliverables_dir = project_root / "DELIVERABLES" / "EP01"
    deliverables_dir.mkdir(parents=True, exist_ok=True)

    print("EP01 T2V Rough Cut Assembly")
    print(f"Episode dir: {ep_dir}")
    print()

    scene_order = discover_scenes(ep_dir)

    # If --assemble-scenes, first assemble each scene from clips
    if args.assemble_scenes:
        for scene_id in scene_order:
            scene_dir = ep_dir / scene_id
            clips_dir = scene_dir / "clips_t2v"
            if not clips_dir.exists():
                continue
            clips = sorted(clips_dir.glob("clip*.mp4"))
            if not clips:
                continue
            assembly_dir = scene_dir / "assembly_t2v"
            assembly_dir.mkdir(parents=True, exist_ok=True)
            output_path = assembly_dir / f"{scene_id}_t2v_assembled.mp4"
            if output_path.exists():
                print(f"  {scene_id}: assembly exists, skipping")
                continue
            print(f"  Assembling {scene_id} from {len(clips)} clips...")
            concatenate_clips(clips, output_path)
        print()

    # Discover scene assemblies
    scene_videos = []
    manifest_scenes = []

    for scene_id in scene_order:
        scene_dir = ep_dir / scene_id
        if not scene_dir.exists():
            print(f"  {scene_id}: directory not found, skipping")
            continue

        assembly = find_scene_assembly(scene_dir)
        if assembly is None:
            print(f"  {scene_id}: no T2V assembly found, skipping")
            continue

        duration = probe_duration(assembly)
        size_mb = assembly.stat().st_size / (1024 * 1024)

        print(f"  {scene_id}: {assembly.name} ({duration:.1f}s, {size_mb:.1f}MB)")
        scene_videos.append(assembly)
        manifest_scenes.append({
            "scene_id": scene_id,
            "file": str(assembly),
            "duration_s": round(duration, 1) if duration else None,
            "size_mb": round(size_mb, 1),
        })

    if not scene_videos:
        print("\nERROR: No scene assemblies found. Run generate_t2v.py first.")
        sys.exit(1)

    # Concatenate into episode rough cut
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = deliverables_dir / f"ep01_t2v_rough_cut_{timestamp}.mp4"

    print(f"\nConcatenating {len(scene_videos)} scenes into rough cut...")
    result = concatenate_clips(scene_videos, output_path)

    if result is None:
        print("ERROR: Episode assembly failed")
        sys.exit(1)

    # Get final duration
    episode_duration = probe_duration(output_path)
    episode_size = output_path.stat().st_size / (1024 * 1024)

    # Write manifest
    manifest = {
        "episode": "ep01",
        "title": get_episode_title(project_root),
        "output": str(output_path),
        "assembled_at": datetime.now().isoformat(),
        "total_duration_s": round(episode_duration, 1) if episode_duration else None,
        "total_size_mb": round(episode_size, 1),
        "scene_count": len(scene_videos),
        "cost": "$0.00 (ComfyUI local)",
        "scenes": manifest_scenes,
    }

    manifest_path = output_path.with_suffix(".json")
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)

    print(f"\nEP01 T2V Rough Cut: {output_path}")
    print(f"Duration: {episode_duration:.1f}s ({episode_duration / 60:.1f}m)")
    print(f"Size: {episode_size:.1f}MB")
    print(f"Scenes: {len(scene_videos)}")
    print(f"Manifest: {manifest_path}")


if __name__ == "__main__":
    main()
