#!/usr/bin/env python3
"""
Generate dialogue audio using qwen3-tts-voiceclone on ComfyUI.

Reads shot_list.yaml, extracts dialogue lines, and generates TTS audio
using designed character voice references.

Default: generates only V.O./off-screen lines (Route A: text TTS).
Use --include-onscreen to also generate on-screen dialogue as TTS fallback.

Usage:
    python generate_dialogue.py --scene PRODUCTION/EP01/sc05b
    python generate_dialogue.py --scene PRODUCTION/EP01/sc05b --shot 4
    python generate_dialogue.py --scene PRODUCTION/EP01/sc05b --include-onscreen
    python generate_dialogue.py --scene PRODUCTION/EP01/sc05b --preflight
    python generate_dialogue.py --scene PRODUCTION/EP01/sc05b --validate
    python generate_dialogue.py --scene PRODUCTION/EP01/sc05b --validate --validate-clips
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
from lib.shot_list import load_shot_list
from lib.ffmpeg import extract_audio, probe_audio_duration
from lib.dialogue import (
    parse_scene_dialogue,
    get_text_tts_lines,
    get_speakable_lines,
    DialogueLine,
)


def generate_tts_line(
    line: DialogueLine,
    voice_ref_path: Path,
    base_url: str,
    workflow: str,
    output_dir: Path,
    dry_run: bool = False,
) -> Path:
    """
    Generate TTS audio for a single dialogue line.

    Args:
        line: Parsed dialogue line
        voice_ref_path: Path to character's voice reference WAV
        base_url: ComfyUI base URL
        workflow: Workflow name for voice cloning
        output_dir: Directory for output files
        dry_run: If True, print params but don't call API

    Returns:
        Path to generated WAV, or None on failure
    """
    print(f"\n  Shot {line.shot_id} | {line.character_id} ({line.delivery})")
    print(f"  Text: \"{line.text}\"")
    print(f"  TTS: \"{line.tts_text}\"")
    print(f"  Voice ref: {voice_ref_path.name}")

    if dry_run:
        print("  -> DRY RUN: skipping API call")
        return None

    output_dir.mkdir(parents=True, exist_ok=True)
    url = f"{base_url}/workflows/{workflow}"

    try:
        with open(voice_ref_path, "rb") as vf:
            files = {"voice": (voice_ref_path.name, vf, "audio/wav")}
            data = {"text": line.tts_text}
            response = requests.post(url, data=data, files=files, timeout=120)
    except requests.exceptions.ConnectionError as e:
        print(f"  x Connection error: {e}")
        return None
    except requests.exceptions.Timeout:
        print(f"  x Request timed out after 120s")
        return None

    if response.status_code != 200:
        print(f"  x API error {response.status_code}: {response.text[:200]}")
        return None

    content_type = response.headers.get("content-type", "")
    if "audio" not in content_type and "octet-stream" not in content_type:
        print(f"  x Unexpected content type: {content_type}")
        print(f"    Response: {response.text[:200]}")
        return None

    # Save audio
    output_path = output_dir / line.output_filename
    with open(output_path, "wb") as f:
        f.write(response.content)
    print(f"  -> Saved: {output_path.name} ({len(response.content)} bytes)")

    # Save metadata
    metadata = {
        "character_id": line.character_id,
        "text": line.text,
        "tts_text": line.tts_text,
        "delivery": line.delivery,
        "route": line.route,
        "shot_id": line.shot_id,
        "line_index": line.line_index,
        "voice_ref": str(voice_ref_path),
        "workflow": workflow,
        "timestamp": datetime.now().isoformat(),
        "file_size_bytes": len(response.content),
    }
    metadata_path = output_path.with_suffix(".json")
    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=2)

    return output_path


def transcribe_audio(audio_path: Path, base_url: str, language: str = "en") -> str:
    """Transcribe an audio file using Whisper STT. Returns text or empty string."""
    try:
        with open(audio_path, "rb") as af:
            resp = requests.post(
                f"{base_url}/workflows/whisper-stt",
                files={"audio": (audio_path.name, af, "audio/wav")},
                data={"language": language, "model_size": "large"},
                timeout=120,
            )
        if resp.status_code == 200:
            return resp.json().get("text", "").strip()
    except Exception as e:
        print(f"    Transcription error: {e}")
    return ""


def _normalize_for_compare(text: str) -> str:
    """Normalize text for fuzzy comparison — lowercase, strip punctuation."""
    import re
    text = text.lower().strip()
    text = re.sub(r'[^\w\s]', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text


def validate_generated_dialogue(output_dir: Path, lines: list, base_url: str):
    """Validate generated TTS audio by transcribing back and comparing."""
    print(f"\n{'='*60}")
    print(f"VALIDATE: Generated Dialogue")
    print(f"{'='*60}")

    issues = []
    for line in lines:
        wav_path = output_dir / line.output_filename
        if not wav_path.exists():
            print(f"\n  Shot {line.shot_id} | {line.character_id}: FILE MISSING")
            issues.append(("missing", line))
            continue

        print(f"\n  Shot {line.shot_id} | {line.character_id}")
        print(f"    Expected: \"{line.text}\"")

        transcribed = transcribe_audio(wav_path, base_url)
        print(f"    Got:      \"{transcribed}\"")

        expected_norm = _normalize_for_compare(line.text)
        got_norm = _normalize_for_compare(transcribed)

        if expected_norm == got_norm:
            print(f"    MATCH")
        elif got_norm in expected_norm or expected_norm in got_norm:
            print(f"    PARTIAL MATCH (close enough)")
        else:
            print(f"    MISMATCH")
            issues.append(("mismatch", line, transcribed))

    if issues:
        print(f"\n  {len(issues)} issue(s) found")
    else:
        print(f"\n  All lines validated OK")


def validate_clips(scene_path: Path, base_url: str):
    """Transcribe all video clips in a scene to detect existing speech."""
    import tempfile

    clips_dirs = []
    for d in ["clips_v2", "clips"]:
        candidate = scene_path / d
        if candidate.exists():
            clips_dirs.append(candidate)
            break

    if not clips_dirs:
        print("  No clips directory found")
        return

    clips_dir = clips_dirs[0]
    clips = sorted(clips_dir.glob("clip*.mp4"))

    print(f"\n{'='*60}")
    print(f"VALIDATE: Video Clips ({clips_dir.name}/)")
    print(f"{'='*60}")

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp = Path(tmp_dir)
        for clip in clips:
            audio_path = tmp / f"{clip.stem}.wav"
            result = extract_audio(clip, audio_path)
            if not result:
                print(f"  {clip.name}: NO AUDIO TRACK")
                continue

            transcribed = transcribe_audio(audio_path, base_url)
            if transcribed and len(transcribed) > 2:
                print(f"  {clip.name}: SPEECH DETECTED")
                print(f"    \"{transcribed[:120]}\"")
            else:
                print(f"  {clip.name}: (no speech)")


def preflight_report(lines, config, output_dir):
    """Print preflight report without calling API."""
    print(f"\n{'='*60}")
    print(f"PREFLIGHT: {len(lines)} dialogue lines")
    print(f"{'='*60}")

    missing_voices = set()
    for line in lines:
        voice_ref = config.get_voice_ref(line.character_id)
        voice_status = "OK" if voice_ref else "MISSING"
        if not voice_ref:
            missing_voices.add(line.character_id)

        print(f"\n  Shot {line.shot_id:2d} | {line.character_id:16s} | {line.delivery:14s} | {line.route}")
        print(f"         | \"{line.text}\"")
        print(f"         | Voice ref: {voice_status}")
        print(f"         | Output: {line.output_filename}")

    # Summary
    characters_used = set(l.character_id for l in lines)
    tts_count = sum(1 for l in lines if l.route == "text_tts")
    v2v_count = sum(1 for l in lines if l.route == "voice_to_voice")

    print(f"\n{'='*60}")
    print(f"SUMMARY")
    print(f"{'='*60}")
    print(f"  Total lines: {len(lines)}")
    print(f"  Text TTS (Route A): {tts_count}")
    print(f"  Voice-to-Voice (Route B): {v2v_count}")
    print(f"  Characters: {sorted(characters_used)}")
    print(f"  Output dir: {output_dir}")

    if missing_voices:
        print(f"\n  WARNING: Missing voice refs for: {sorted(missing_voices)}")
        print(f"  Run: python design_voices.py --character <name>")

    # Write preflight JSON
    preflight_path = output_dir / "dialogue_preflight.json"
    output_dir.mkdir(parents=True, exist_ok=True)
    preflight_data = {
        "preflight": True,
        "total_lines": len(lines),
        "text_tts_lines": tts_count,
        "voice_to_voice_lines": v2v_count,
        "characters": sorted(characters_used),
        "missing_voice_refs": sorted(missing_voices),
        "lines": [
            {
                "shot_id": l.shot_id,
                "character_id": l.character_id,
                "text": l.text,
                "delivery": l.delivery,
                "route": l.route,
                "output_filename": l.output_filename,
            }
            for l in lines
        ],
    }
    with open(preflight_path, "w") as f:
        json.dump(preflight_data, f, indent=2)
    print(f"\n  Preflight JSON: {preflight_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate dialogue audio via qwen3-tts-voiceclone",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--scene", "-s",
        required=True,
        help="Path to scene directory (e.g., PRODUCTION/EP01/sc05b)",
    )
    parser.add_argument(
        "--shot",
        type=int,
        help="Only generate dialogue for a specific shot ID",
    )
    parser.add_argument(
        "--include-onscreen",
        action="store_true",
        help="Also generate TTS for on-screen dialogue (fallback when voice-to-voice unavailable)",
    )
    parser.add_argument(
        "--preflight",
        action="store_true",
        help="Show dialogue analysis without calling API",
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Transcribe generated dialogue back via Whisper and check accuracy",
    )
    parser.add_argument(
        "--validate-clips",
        action="store_true",
        help="Transcribe video clips to detect existing speech (use with --validate)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print parameters without calling API (still parses everything)",
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

    # Resolve scene path
    scene_path = Path(args.scene)
    if not scene_path.is_absolute():
        scene_path = project_root / args.scene

    shot_list_path = scene_path / "shot_list.yaml"
    if not shot_list_path.exists():
        print(f"Error: Shot list not found: {shot_list_path}")
        sys.exit(1)

    # Load shot list
    shot_list = load_shot_list(shot_list_path, config)
    shots = shot_list.shots

    # Filter to specific shot if requested
    if args.shot:
        shots = [s for s in shots if s.get("id") == args.shot]
        if not shots:
            print(f"Error: Shot {args.shot} not found")
            sys.exit(1)

    # Parse dialogue lines
    if args.include_onscreen:
        lines = get_speakable_lines(shots)
    else:
        lines = get_text_tts_lines(shots)

    if not lines:
        print("No dialogue lines found for the selected route(s).")
        if not args.include_onscreen:
            # Check if there are on-screen lines they might want
            all_lines = get_speakable_lines(shots)
            onscreen = [l for l in all_lines if l.route == "voice_to_voice"]
            if onscreen:
                print(f"  ({len(onscreen)} on-screen lines available with --include-onscreen)")
        sys.exit(0)

    # Output directory
    output_dir = scene_path / "dialogue"

    # Preflight mode
    if args.preflight:
        preflight_report(lines, config, output_dir)
        sys.exit(0)

    # Get TTS config (needed for both generate and validate)
    tts_config = config.tts_config
    comfyui_config = tts_config.get("comfyui", config.backend_config.get("comfyui", {}))
    base_url = comfyui_config.get("base_url", "http://192.168.1.181:8100")

    # Validate mode
    if args.validate:
        all_lines = get_speakable_lines(shots) if args.include_onscreen else get_text_tts_lines(shots)
        validate_generated_dialogue(output_dir, all_lines, base_url)
        if args.validate_clips:
            validate_clips(scene_path, base_url)
        sys.exit(0)

    workflow = comfyui_config.get("voiceclone_workflow", "qwen3-tts-voiceclone")

    print(f"Scene: {scene_path.name}")
    print(f"ComfyUI: {base_url}")
    print(f"Workflow: {workflow}")
    print(f"Lines to generate: {len(lines)}")
    print(f"Output: {output_dir}")

    # Generate TTS for each line
    results = {}
    for line in lines:
        voice_ref = config.get_voice_ref(line.character_id)
        if not voice_ref:
            print(f"\n  SKIP Shot {line.shot_id} | {line.character_id}: no voice ref")
            print(f"  Run: python design_voices.py --character {line.character_id}")
            results[line.output_filename] = None
            continue

        result = generate_tts_line(
            line=line,
            voice_ref_path=voice_ref,
            base_url=base_url,
            workflow=workflow,
            output_dir=output_dir,
            dry_run=args.dry_run,
        )
        results[line.output_filename] = result

    # Summary
    print(f"\n{'='*60}")
    print("DIALOGUE GENERATION COMPLETE")
    print(f"{'='*60}")
    success = sum(1 for v in results.values() if v is not None)
    total = len(results)
    print(f"  {success}/{total} lines generated")
    for filename, path in results.items():
        status = "OK" if path else ("DRY" if args.dry_run else "FAIL")
        print(f"  [{status}] {filename}")

    if not args.dry_run and None in results.values():
        sys.exit(1)


if __name__ == "__main__":
    main()
