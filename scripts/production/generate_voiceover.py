#!/usr/bin/env python3
"""
Generate voiceover audio from ledger_voiceover.yaml using TTS voice cloning.

Reads the episode-level voiceover catalog and generates WAV files for each
line using the appropriate character voice reference.

Output: PRODUCTION/EP01/scXX/voiceover/voXX_<character>_<slug>.wav

Usage:
    python generate_voiceover.py
    python generate_voiceover.py --scene sc05b
    python generate_voiceover.py --line 14
    python generate_voiceover.py --preflight
    python generate_voiceover.py --resume
    python generate_voiceover.py --mix
"""

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

import requests
import yaml

# Add scripts/ to path for shared lib imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.config import load_config, find_project_root


def load_voiceover_catalog(episode_dir: Path) -> list:
    """Load ledger_voiceover.yaml from the episode directory."""
    catalog_path = episode_dir / "ledger_voiceover.yaml"
    if not catalog_path.exists():
        raise FileNotFoundError(f"Voiceover catalog not found: {catalog_path}")

    with open(catalog_path) as f:
        data = yaml.safe_load(f)

    return data.get("lines", [])


def make_slug(text: str, max_len: int = 40) -> str:
    """Create a filename-safe slug from text."""
    words = re.sub(r'[^a-z0-9\s]', '', text.lower()).split()
    slug = "_".join(words[:6])
    return slug[:max_len] if slug else "line"


def output_filename(line: dict) -> str:
    """Generate standard output filename for a voiceover line."""
    line_id = line["id"]
    character = line["character"]
    slug = make_slug(line["text"])
    return f"vo{line_id:02d}_{character}_{slug}.wav"


def output_dir_for_line(line: dict, production_dir: Path) -> Path:
    """Get the output directory for a line's scene."""
    scene = line["scene"]
    return production_dir / scene / "voiceover"


def generate_tts(
    line: dict,
    voice_ref_path: Path,
    base_url: str,
    workflow: str,
    out_dir: Path,
) -> Path:
    """Generate TTS audio for a single voiceover line."""
    out_dir.mkdir(parents=True, exist_ok=True)
    filename = output_filename(line)
    out_path = out_dir / filename

    url = f"{base_url}/workflows/{workflow}"
    text = line["text"]

    print(f"  Line {line['id']:2d} | {line['character']:16s} | shot {line['shot']}")
    print(f"         | \"{text}\"")
    print(f"         | Voice: {voice_ref_path.name}")

    try:
        with open(voice_ref_path, "rb") as vf:
            files = {"voice": (voice_ref_path.name, vf, "audio/wav")}
            data = {"text": text}
            response = requests.post(url, data=data, files=files, timeout=120)
    except requests.exceptions.ConnectionError as e:
        print(f"         | ERROR: Connection error: {e}")
        return None
    except requests.exceptions.Timeout:
        print(f"         | ERROR: Timed out after 120s")
        return None

    if response.status_code != 200:
        print(f"         | ERROR: API {response.status_code}: {response.text[:200]}")
        return None

    content_type = response.headers.get("content-type", "")
    if "audio" not in content_type and "octet-stream" not in content_type:
        print(f"         | ERROR: Unexpected content type: {content_type}")
        return None

    # Save audio
    with open(out_path, "wb") as f:
        f.write(response.content)
    size_kb = len(response.content) / 1024
    print(f"         | OK: {filename} ({size_kb:.1f} KB)")

    # Save metadata
    metadata = {
        "line_id": line["id"],
        "scene": line["scene"],
        "shot": line["shot"],
        "character": line["character"],
        "text": text,
        "context": line.get("context", ""),
        "voice_ref": str(voice_ref_path),
        "workflow": workflow,
        "timestamp": datetime.now().isoformat(),
        "file_size_bytes": len(response.content),
    }
    metadata_path = out_path.with_suffix(".json")
    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=2)

    return out_path


def preflight(lines: list, config, production_dir: Path):
    """Show preflight report without calling API."""
    print(f"\n{'='*60}")
    print(f"VOICEOVER PREFLIGHT — {len(lines)} lines")
    print(f"{'='*60}")

    missing_voices = set()
    scenes = {}

    for line in lines:
        scene = line["scene"]
        scenes.setdefault(scene, []).append(line)

        voice_ref = config.get_voice_ref(line["character"])
        voice_ok = "OK" if voice_ref else "MISSING"
        if not voice_ref:
            missing_voices.add(line["character"])

        out_dir = output_dir_for_line(line, production_dir)
        out_path = out_dir / output_filename(line)
        exists = "EXISTS" if out_path.exists() else ""

        print(f"\n  #{line['id']:2d} | {line['scene']} shot {line['shot']} | {line['character']:16s} | Voice: {voice_ok} {exists}")
        print(f"       | \"{line['text']}\"")
        print(f"       | {line.get('context', '')}")

    print(f"\n{'='*60}")
    print(f"SUMMARY")
    print(f"{'='*60}")
    print(f"  Total lines: {len(lines)}")
    print(f"  Scenes: {sorted(scenes.keys())}")
    for scene, scene_lines in sorted(scenes.items()):
        chars = set(l["character"] for l in scene_lines)
        print(f"    {scene}: {len(scene_lines)} lines ({', '.join(sorted(chars))})")

    if missing_voices:
        print(f"\n  WARNING: Missing voice refs for: {sorted(missing_voices)}")
        print(f"  Run: python design_voices.py --character <name>")


def main():
    parser = argparse.ArgumentParser(
        description="Generate voiceover audio from ledger_voiceover.yaml",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--scene", "-s",
        help="Only generate lines for a specific scene (e.g., sc05b)",
    )
    parser.add_argument(
        "--line", "-l",
        type=int,
        help="Only generate a specific line by ID",
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Skip lines where output WAV already exists",
    )
    parser.add_argument(
        "--preflight",
        action="store_true",
        help="Show line catalog and voice ref status without calling API",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print parameters without calling API",
    )
    parser.add_argument(
        "--project",
        help="Path to project root (auto-detected if not specified)",
    )
    args = parser.parse_args()

    # Load project config
    try:
        if args.project:
            project_root = Path(args.project)
        else:
            project_root = find_project_root()
        config = load_config(project_root)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)

    # Resolve episode dir
    production_dir = project_root / "PRODUCTION" / "EP01"
    if not production_dir.exists():
        print(f"Error: Production dir not found: {production_dir}")
        sys.exit(1)

    # Load voiceover catalog
    try:
        lines = load_voiceover_catalog(production_dir)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)

    # Filter
    if args.scene:
        lines = [l for l in lines if l["scene"] == args.scene]
        if not lines:
            print(f"No lines found for scene {args.scene}")
            sys.exit(0)

    if args.line:
        lines = [l for l in lines if l["id"] == args.line]
        if not lines:
            print(f"No line found with ID {args.line}")
            sys.exit(1)

    # Preflight mode
    if args.preflight:
        preflight(lines, config, production_dir)
        sys.exit(0)

    # Get TTS config
    tts_config = config.tts_config
    comfyui_config = tts_config.get("comfyui", config.backend_config.get("comfyui", {}))
    base_url = comfyui_config.get("base_url", "http://192.168.1.181:8100")
    workflow = comfyui_config.get("voiceclone_workflow", "qwen3-tts-voiceclone")

    print(f"Voiceover Generation — {len(lines)} lines")
    print(f"ComfyUI: {base_url}")
    print(f"Workflow: {workflow}")

    # Generate TTS for each line
    results = {}
    skipped = 0
    for line in lines:
        out_dir = output_dir_for_line(line, production_dir)
        out_path = out_dir / output_filename(line)

        # Resume: skip existing files
        if args.resume and out_path.exists() and out_path.stat().st_size > 1000:
            print(f"  Line {line['id']:2d} | SKIP (exists: {out_path.name})")
            skipped += 1
            results[line["id"]] = out_path
            continue

        # Get voice ref
        voice_ref = config.get_voice_ref(line["character"])
        if not voice_ref:
            print(f"\n  Line {line['id']:2d} | SKIP: no voice ref for '{line['character']}'")
            print(f"         | Run: python design_voices.py --character {line['character']}")
            results[line["id"]] = None
            continue

        if args.dry_run:
            print(f"\n  Line {line['id']:2d} | {line['character']:16s} | \"{line['text'][:60]}...\"")
            print(f"         | DRY RUN: would use {voice_ref.name}")
            results[line["id"]] = None
            continue

        result = generate_tts(
            line=line,
            voice_ref_path=voice_ref,
            base_url=base_url,
            workflow=workflow,
            out_dir=out_dir,
        )
        results[line["id"]] = result

    # Summary
    print(f"\n{'='*60}")
    print("VOICEOVER GENERATION COMPLETE")
    print(f"{'='*60}")
    success = sum(1 for v in results.values() if v is not None)
    failed = sum(1 for v in results.values() if v is None)
    print(f"  Generated: {success - skipped}")
    print(f"  Skipped (resume): {skipped}")
    print(f"  Failed: {failed}")

    # Group by scene
    scene_counts = {}
    for line in lines:
        scene = line["scene"]
        scene_counts.setdefault(scene, {"ok": 0, "fail": 0})
        if results.get(line["id"]):
            scene_counts[scene]["ok"] += 1
        else:
            scene_counts[scene]["fail"] += 1

    for scene, counts in sorted(scene_counts.items()):
        status = "OK" if counts["fail"] == 0 else f"{counts['fail']} FAILED"
        print(f"  {scene}: {counts['ok']} lines ({status})")

    if failed > 0 and not args.dry_run:
        sys.exit(1)


if __name__ == "__main__":
    main()
