#!/usr/bin/env python3
"""
Design character voices using qwen3-tts-voicedesign on ComfyUI.

Creates reference voice audio per character from voice_definitions.yaml.
These voice refs are used by generate_dialogue.py for TTS cloning.

Usage:
    python design_voices.py --character mars
    python design_voices.py --character mars --seed 42
    python design_voices.py --all
    python design_voices.py --all --dry-run
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

import requests
import yaml

# Add scripts/ to path for shared lib imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.config import load_config, find_project_root


def load_voice_definitions(project_root: Path) -> dict:
    """Load voice_definitions.yaml from project root."""
    voice_path = project_root / "voice_definitions.yaml"
    if not voice_path.exists():
        raise FileNotFoundError(f"voice_definitions.yaml not found at {voice_path}")

    with open(voice_path) as f:
        data = yaml.safe_load(f)

    return data.get("characters", {})


def design_voice(
    character_id: str,
    instruct: str,
    sample_text: str,
    base_url: str,
    workflow: str,
    output_dir: Path,
    seed: int = None,
    dry_run: bool = False,
) -> Path:
    """
    Design a character voice via qwen3-tts-voicedesign endpoint.

    Args:
        character_id: Character identifier
        instruct: Voice design instruction text
        sample_text: Sample text to speak
        base_url: ComfyUI base URL
        workflow: Workflow name
        output_dir: Directory for output files
        seed: Optional seed for reproducibility
        dry_run: If True, print params but don't call API

    Returns:
        Path to generated voice ref WAV, or None on failure
    """
    print(f"\n{'='*60}")
    print(f"VOICE DESIGN: {character_id}")
    print(f"{'='*60}")
    print(f"Instruct: {instruct[:100]}...")
    print(f"Sample: \"{sample_text}\"")
    if seed is not None:
        print(f"Seed: {seed}")

    if dry_run:
        print("-> DRY RUN: skipping API call")
        return None

    output_dir.mkdir(parents=True, exist_ok=True)
    url = f"{base_url}/workflows/{workflow}"

    data = {
        "instruct": instruct.strip(),
        "text": sample_text.strip(),
    }
    if seed is not None:
        data["seed"] = str(seed)

    print(f"\nPOST {url}")
    try:
        response = requests.post(url, data=data, timeout=120)
    except requests.exceptions.ConnectionError as e:
        print(f"x Connection error: {e}")
        print(f"  Is ComfyUI running at {base_url}?")
        return None
    except requests.exceptions.Timeout:
        print(f"x Request timed out after 120s")
        return None

    if response.status_code != 200:
        print(f"x API error {response.status_code}: {response.text[:200]}")
        return None

    # Check content type
    content_type = response.headers.get("content-type", "")
    if "audio" not in content_type and "octet-stream" not in content_type:
        print(f"x Unexpected content type: {content_type}")
        print(f"  Response: {response.text[:200]}")
        return None

    # Save audio
    output_path = output_dir / f"{character_id}_voice_ref.wav"
    with open(output_path, "wb") as f:
        f.write(response.content)
    print(f"-> Saved: {output_path} ({len(response.content)} bytes)")

    # Save metadata
    metadata = {
        "character_id": character_id,
        "instruct": instruct.strip(),
        "sample_text": sample_text.strip(),
        "seed": seed,
        "workflow": workflow,
        "endpoint": url,
        "timestamp": datetime.now().isoformat(),
        "file_size_bytes": len(response.content),
    }
    metadata_path = output_path.with_suffix(".json")
    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=2)
    print(f"-> Metadata: {metadata_path}")

    return output_path


def main():
    parser = argparse.ArgumentParser(
        description="Design character voices via qwen3-tts-voicedesign",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--character", "-c",
        help="Character ID to design voice for (e.g., mars, jonah)",
    )
    parser.add_argument(
        "--all", "-a",
        action="store_true",
        help="Design voices for all characters in voice_definitions.yaml",
    )
    parser.add_argument(
        "--seed",
        type=int,
        help="Seed for reproducibility",
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

    if not args.character and not args.all:
        parser.print_help()
        print("\nSpecify --character NAME or --all")
        sys.exit(1)

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

    # Load voice definitions
    try:
        voice_defs = load_voice_definitions(project_root)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)

    # Get TTS config
    tts_config = config._config.get("tts", {})
    comfyui_config = tts_config.get("comfyui", config.backend_config.get("comfyui", {}))
    base_url = comfyui_config.get("base_url", "http://192.168.1.181:8100")
    workflow = comfyui_config.get("voicedesign_workflow", "qwen3-tts-voicedesign")

    # Output directory
    output_dir = config.references_dir / "voice_refs"

    # Determine which characters to process
    if args.all:
        characters = list(voice_defs.keys())
    else:
        if args.character not in voice_defs:
            print(f"Error: Character '{args.character}' not found in voice_definitions.yaml")
            print(f"Available: {list(voice_defs.keys())}")
            sys.exit(1)
        characters = [args.character]

    print(f"Project: {project_root.name}")
    print(f"ComfyUI: {base_url}")
    print(f"Workflow: {workflow}")
    print(f"Output: {output_dir}")
    print(f"Characters: {characters}")

    # Design voices
    results = {}
    for char_id in characters:
        char_def = voice_defs[char_id]
        instruct = char_def.get("instruct", "")
        sample_text = char_def.get("sample_text", "Hello, this is a test.")

        if not instruct:
            print(f"\nSkipping {char_id}: no instruct defined")
            continue

        result = design_voice(
            character_id=char_id,
            instruct=instruct,
            sample_text=sample_text,
            base_url=base_url,
            workflow=workflow,
            output_dir=output_dir,
            seed=args.seed,
            dry_run=args.dry_run,
        )
        results[char_id] = result

    # Summary
    print(f"\n{'='*60}")
    print("VOICE DESIGN COMPLETE")
    print(f"{'='*60}")
    for char_id, path in results.items():
        status = "OK" if path else ("DRY" if args.dry_run else "FAIL")
        print(f"  [{status}] {char_id}: {path or '(skipped)'}")

    if not args.dry_run and None in results.values():
        sys.exit(1)


if __name__ == "__main__":
    main()
