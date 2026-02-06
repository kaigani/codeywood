#!/usr/bin/env python3
"""
Validate shot list and clip definition YAML files.

Usage:
    python validate.py --scene PRODUCTION/EP01/sc03
    python validate.py --shot-list path/to/shots.yaml
    python validate.py --clips path/to/clips.yaml

Examples:
    # Validate all SC03 files (new layout)
    python validate.py --scene PRODUCTION/EP01/sc03

    # Validate specific files (legacy)
    python validate.py --shot-list shot_lists/sc02_shots.yaml --clips clip_definitions/sc02_clips.yaml
"""

import argparse
import sys
from pathlib import Path
from typing import List, Tuple

import yaml

# Add scripts/ to path for shared lib imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.config import load_config, find_project_root


class ValidationError:
    """Represents a validation error."""

    def __init__(self, level: str, path: str, message: str):
        self.level = level  # "error" or "warning"
        self.path = path
        self.message = message

    def __str__(self):
        icon = "✗" if self.level == "error" else "⚠"
        return f"  {icon} [{self.path}] {self.message}"


class Validator:
    """YAML schema validator."""

    VALID_SHOT_TYPES = [
        "establish", "entrance", "approach", "action", "detail",
        "reaction", "reveal", "conversation", "transition"
    ]

    VALID_SHOT_FRAMES = [
        "extreme_wide", "wide", "medium_wide", "medium",
        "medium_close", "close", "extreme_close"
    ]

    VALID_DIALOGUE = ["none", "breathing", "effort", "reaction", "scripted", "adr"]

    VALID_CAMERA_MOVEMENTS = ["static", "push_in", "pull_out", "track", "pan", "tilt"]

    VALID_START_STRATEGIES = ["shot", "last_frame", "custom"]

    def __init__(self):
        self.errors: List[ValidationError] = []

    def error(self, path: str, message: str):
        """Add an error."""
        self.errors.append(ValidationError("error", path, message))

    def warning(self, path: str, message: str):
        """Add a warning."""
        self.errors.append(ValidationError("warning", path, message))

    def validate_shot_list(self, data: dict, config=None) -> bool:
        """Validate a shot list YAML."""
        print("\nValidating shot list...")

        # Required top-level fields
        if "scene" not in data:
            self.error("scene", "Missing required 'scene' section")
        else:
            scene = data["scene"]
            for field in ["id", "name", "episode", "location", "time_of_day"]:
                if field not in scene:
                    self.error(f"scene.{field}", f"Missing required field")

        if "director" not in data:
            self.error("director", "Missing required 'director' section")
        else:
            director = data["director"]
            if "dialogue_strategy" not in director:
                self.error("director.dialogue_strategy", "Missing required field")
            elif director["dialogue_strategy"] not in self.VALID_DIALOGUE:
                self.warning("director.dialogue_strategy",
                           f"Unknown value '{director['dialogue_strategy']}'. "
                           f"Expected one of: {self.VALID_DIALOGUE}")

        if "characters" not in data:
            self.error("characters", "Missing required 'characters' section")
        else:
            for i, char in enumerate(data.get("characters", [])):
                if "id" not in char:
                    self.error(f"characters[{i}].id", "Missing required field")
                if "element" not in char:
                    self.error(f"characters[{i}].element", "Missing required field")

        if "shots" not in data:
            self.error("shots", "Missing required 'shots' section")
        else:
            self._validate_shots(data["shots"], data.get("characters", []))

        return len([e for e in self.errors if e.level == "error"]) == 0

    def _validate_shots(self, shots: list, characters: list):
        """Validate shots array."""
        char_ids = [c.get("id") for c in characters]
        has_establish = False
        has_reaction = False
        prev_type = None

        for i, shot in enumerate(shots):
            path = f"shots[{i}]"
            shot_id = shot.get("id", i)

            # Required fields
            for field in ["id", "name", "type", "shot_type", "duration"]:
                if field not in shot:
                    self.error(f"{path}.{field}", "Missing required field")

            # Validate type
            shot_type = shot.get("type")
            if shot_type:
                if shot_type not in self.VALID_SHOT_TYPES:
                    self.warning(f"{path}.type",
                               f"Unknown type '{shot_type}'. Expected: {self.VALID_SHOT_TYPES}")
                if shot_type == "establish":
                    has_establish = True
                if shot_type == "reaction":
                    has_reaction = True

            # Validate shot_type (framing)
            framing = shot.get("shot_type")
            if framing and framing not in self.VALID_SHOT_FRAMES:
                self.warning(f"{path}.shot_type",
                           f"Unknown framing '{framing}'. Expected: {self.VALID_SHOT_FRAMES}")

            # Video Director required fields
            if "sound" not in shot:
                self.warning(f"{path}.sound", "Missing sound direction (Video Director principle)")

            if "dialogue" not in shot:
                self.warning(f"{path}.dialogue", "Missing dialogue control (Video Director principle)")
            elif shot.get("dialogue") not in self.VALID_DIALOGUE:
                self.warning(f"{path}.dialogue",
                           f"Unknown dialogue value '{shot.get('dialogue')}'")

            # Body language required if characters present
            shot_chars = shot.get("characters", [])
            if shot_chars and "body_language" not in shot:
                self.warning(f"{path}.body_language",
                           "Missing body language (required when characters present)")

            # Validate character references
            for char in shot_chars:
                if char not in char_ids:
                    self.error(f"{path}.characters", f"Unknown character '{char}'")

            # Camera validation
            camera = shot.get("camera", {})
            if camera:
                movement = camera.get("movement")
                if movement and movement not in self.VALID_CAMERA_MOVEMENTS:
                    self.warning(f"{path}.camera.movement",
                               f"Unknown movement '{movement}'")

            # Prompt required
            if "prompt" not in shot or not shot.get("prompt", "").strip():
                self.error(f"{path}.prompt", "Missing or empty prompt")

            # Check for consecutive action shots
            if shot_type == "action" and prev_type == "action":
                self.warning(f"{path}",
                           "Two consecutive 'action' shots - consider adding breathing room")

            prev_type = shot_type

        # Video Director checks
        if not has_establish:
            self.warning("shots", "No establishing shot found (Video Director principle)")

        if not has_reaction:
            self.warning("shots", "No reaction/breathing room shot found (Video Director principle)")

    def validate_clip_definitions(self, data: dict, shot_data: dict = None) -> bool:
        """Validate clip definitions YAML."""
        print("\nValidating clip definitions...")

        # Required fields
        if "scene_id" not in data:
            self.error("scene_id", "Missing required field")

        if "clips" not in data:
            self.error("clips", "Missing required 'clips' section")
        else:
            shot_ids = []
            if shot_data:
                shot_ids = [s.get("id") for s in shot_data.get("shots", [])]

            self._validate_clips(data["clips"], shot_ids)

        if "assembly" not in data:
            self.warning("assembly", "Missing assembly configuration")
        else:
            assembly = data["assembly"]
            if "clips" not in assembly:
                self.warning("assembly.clips", "Missing clip order")

        return len([e for e in self.errors if e.level == "error"]) == 0

    def _validate_clips(self, clips: list, shot_ids: list):
        """Validate clips array."""
        clip_ids = []

        for i, clip in enumerate(clips):
            path = f"clips[{i}]"
            clip_id = clip.get("id")
            clip_ids.append(clip_id)

            # Required fields
            for field in ["id", "name", "type", "characters", "total_duration"]:
                if field not in clip:
                    self.error(f"{path}.{field}", "Missing required field")

            # Start frame validation
            start = clip.get("start_frame", {})
            strategy = start.get("strategy", "shot")

            if strategy not in self.VALID_START_STRATEGIES:
                self.error(f"{path}.start_frame.strategy",
                         f"Unknown strategy '{strategy}'")

            if strategy == "shot" and "shot_id" not in start:
                self.error(f"{path}.start_frame.shot_id",
                         "Required when strategy is 'shot'")
            elif strategy == "shot" and shot_ids:
                if start.get("shot_id") not in shot_ids:
                    self.warning(f"{path}.start_frame.shot_id",
                               f"Shot {start.get('shot_id')} not found in shot list")

            if strategy == "last_frame" and "clip_id" not in start:
                self.error(f"{path}.start_frame.clip_id",
                         "Required when strategy is 'last_frame'")
            elif strategy == "last_frame":
                ref_id = start.get("clip_id")
                if ref_id not in clip_ids:
                    self.warning(f"{path}.start_frame.clip_id",
                               f"Clip {ref_id} not defined before this clip")

            if strategy == "custom" and "custom_path" not in start:
                self.error(f"{path}.start_frame.custom_path",
                         "Required when strategy is 'custom'")

            # Prompts validation
            prompts = clip.get("prompts", [])
            if not prompts:
                self.error(f"{path}.prompts", "No prompts defined")

            total = 0
            for j, prompt in enumerate(prompts):
                duration = prompt.get("duration", 0)
                total += duration

                if "prompt" not in prompt and "shot_ref" not in prompt:
                    self.error(f"{path}.prompts[{j}]",
                             "Must have either 'prompt' or 'shot_ref'")

                if "shot_ref" in prompt and shot_ids:
                    if prompt["shot_ref"] not in shot_ids:
                        self.warning(f"{path}.prompts[{j}].shot_ref",
                                   f"Shot {prompt['shot_ref']} not found in shot list")

            # Verify total duration
            declared = clip.get("total_duration", 0)
            if total != declared:
                self.warning(f"{path}.total_duration",
                           f"Declared {declared}s but prompts sum to {total}s")


def main():
    parser = argparse.ArgumentParser(
        description="Validate shot list and clip definition YAML files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--scene",
        help="Path to scene directory (e.g., PRODUCTION/EP01/sc03). Auto-finds shot_list.yaml, clip_definitions.yaml within.",
    )
    parser.add_argument(
        "--shot-list", "-s",
        help="Path to shot list YAML file (legacy, use --scene instead)",
    )
    parser.add_argument(
        "--clips", "-c",
        help="Path to clip definitions YAML file (legacy, use --scene instead)",
    )
    parser.add_argument(
        "--project",
        help="Path to project root (auto-detected if not specified)",
    )
    args = parser.parse_args()

    if not args.scene and not args.shot_list and not args.clips:
        parser.print_help()
        print("\nSpecify --scene, --shot-list, and/or --clips to validate")
        sys.exit(1)

    # Determine project root
    try:
        if args.project:
            project_root = Path(args.project)
        elif args.scene:
            project_root = find_project_root(Path(args.scene).parent)
        elif args.shot_list:
            project_root = find_project_root(Path(args.shot_list).parent)
        elif args.clips:
            project_root = find_project_root(Path(args.clips).parent)
        else:
            project_root = find_project_root()
    except FileNotFoundError:
        project_root = None

    # Resolve paths from --scene if provided
    shot_list_arg = args.shot_list
    clips_arg = args.clips

    if args.scene:
        scene_path = Path(args.scene)
        if not scene_path.is_absolute() and project_root:
            scene_path = project_root / args.scene
        if not shot_list_arg:
            candidate = scene_path / "shot_list.yaml"
            if candidate.exists():
                shot_list_arg = str(candidate)
        if not clips_arg:
            candidate = scene_path / "clip_definitions.yaml"
            if candidate.exists():
                clips_arg = str(candidate)

    validator = Validator()
    shot_data = None

    # Validate shot list
    if shot_list_arg:
        shot_path = Path(shot_list_arg)
        if not shot_path.is_absolute() and project_root:
            for alt_base in ["PRODUCTION", "VISUAL_PRODUCTION"]:
                alt_path = project_root / alt_base / shot_list_arg
                if alt_path.exists():
                    shot_path = alt_path
                    break

        if not shot_path.exists():
            print(f"Error: Shot list not found: {shot_path}")
            sys.exit(1)

        print(f"Shot list: {shot_path}")
        with open(shot_path) as f:
            shot_data = yaml.safe_load(f)

        validator.validate_shot_list(shot_data)

    # Validate clip definitions
    if clips_arg:
        clips_path = Path(clips_arg)
        if not clips_path.is_absolute() and project_root:
            for alt_base in ["PRODUCTION", "VISUAL_PRODUCTION"]:
                alt_path = project_root / alt_base / clips_arg
                if alt_path.exists():
                    clips_path = alt_path
                    break

        if not clips_path.exists():
            print(f"Error: Clip definitions not found: {clips_path}")
            sys.exit(1)

        print(f"Clip definitions: {clips_path}")
        with open(clips_path) as f:
            clip_data = yaml.safe_load(f)

        validator.validate_clip_definitions(clip_data, shot_data)

    # Report results
    print("\n" + "="*70)
    print("VALIDATION RESULTS")
    print("="*70)

    errors = [e for e in validator.errors if e.level == "error"]
    warnings = [e for e in validator.errors if e.level == "warning"]

    if errors:
        print(f"\n{len(errors)} Error(s):")
        for e in errors:
            print(e)

    if warnings:
        print(f"\n{len(warnings)} Warning(s):")
        for e in warnings:
            print(e)

    if not errors and not warnings:
        print("\n✓ All validations passed!")

    # Summary
    print(f"\nSummary: {len(errors)} errors, {len(warnings)} warnings")

    if errors:
        sys.exit(1)


if __name__ == "__main__":
    main()
