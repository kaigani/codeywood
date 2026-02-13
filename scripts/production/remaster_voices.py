#!/usr/bin/env python3
"""
Voice-to-voice remastering for lip-synced on-screen dialogue (Route B).

Extracts speech from video clips, remasters with designed character voice,
and remixes back onto the video. Preserves original lip-sync timing.

FUTURE: Depends on audio separation and voice-to-voice endpoints
that are not yet available on ComfyUI.

Usage:
    python remaster_voices.py --scene PRODUCTION/EP01/sc05b
    python remaster_voices.py --scene PRODUCTION/EP01/sc05b --clip 4
    python remaster_voices.py --scene PRODUCTION/EP01/sc05b --preflight
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

import yaml

# Add scripts/ to path for shared lib imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.config import load_config, find_project_root
from lib.shot_list import load_shot_list
from lib.dialogue import get_voice_to_voice_lines


def separate_audio(video_path: Path, base_url: str, workflow: str) -> bytes:
    """
    Extract speech from video using audio separation endpoint.

    PLACEHOLDER — depends on future endpoint.
    """
    raise NotImplementedError(
        "Audio separation endpoint not yet available. "
        "Check PROJECT_CONFIG.yaml tts.comfyui.audiosep_workflow"
    )


def voice_to_voice(speech_audio: Path, voice_ref: Path, base_url: str, workflow: str) -> bytes:
    """
    Remaster speech with designed character voice.

    PLACEHOLDER — depends on future endpoint.
    """
    raise NotImplementedError(
        "Voice-to-voice endpoint not yet available. "
        "Check PROJECT_CONFIG.yaml tts.comfyui.voice2voice_workflow"
    )


def main():
    parser = argparse.ArgumentParser(
        description="Voice-to-voice remastering for lip-synced dialogue (FUTURE)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--scene", "-s",
        required=True,
        help="Path to scene directory",
    )
    parser.add_argument(
        "--clip",
        type=int,
        help="Only remaster a specific clip",
    )
    parser.add_argument(
        "--preflight",
        action="store_true",
        help="Show analysis without calling API",
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

    # Check if endpoints are configured
    tts_config = config.tts_config
    comfyui_config = tts_config.get("comfyui", {})
    audiosep = comfyui_config.get("audiosep_workflow")
    v2v = comfyui_config.get("voice2voice_workflow")

    if not audiosep or audiosep == "TBD":
        print("Voice-to-voice remastering is not yet available.")
        print("Waiting for audio separation endpoint to be added to ComfyUI.")
        print()
        print("In the meantime, use generate_dialogue.py --include-onscreen")
        print("to generate text TTS as a fallback for on-screen dialogue.")
        sys.exit(0)

    # Resolve scene
    scene_path = Path(args.scene)
    if not scene_path.is_absolute():
        scene_path = project_root / args.scene

    shot_list_path = scene_path / "shot_list.yaml"
    if not shot_list_path.exists():
        print(f"Error: Shot list not found: {shot_list_path}")
        sys.exit(1)

    shot_list = load_shot_list(shot_list_path, config)
    lines = get_voice_to_voice_lines(shot_list.shots)

    if not lines:
        print("No on-screen dialogue lines found for voice-to-voice remastering.")
        sys.exit(0)

    print(f"Found {len(lines)} on-screen dialogue lines for remastering.")
    for line in lines:
        print(f"  Shot {line.shot_id}: {line.character_id} - \"{line.text[:60]}\"")

    if args.preflight:
        print("\nPreflight complete. Endpoints ready when configured.")
        sys.exit(0)

    # Would call separate_audio + voice_to_voice here
    print("\nEndpoints not yet implemented. Use --preflight for analysis.")
    sys.exit(0)


if __name__ == "__main__":
    main()
