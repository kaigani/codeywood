"""
Shot list and clip definition loaders.

Reads YAML files and provides structured access to:
- Shot definitions
- Clip sequences
- Reference resolution
"""

from pathlib import Path
from typing import List, Dict, Any, Optional
import yaml

from .config import ProjectConfig


class ShotList:
    """Loads and provides access to a scene's shot list."""

    def __init__(self, yaml_path: Path, config: ProjectConfig):
        self.yaml_path = Path(yaml_path)
        self.config = config

        if not self.yaml_path.exists():
            raise FileNotFoundError(f"Shot list not found: {self.yaml_path}")

        with open(self.yaml_path) as f:
            self._data = yaml.safe_load(f)

    @property
    def scene(self) -> Dict[str, Any]:
        """Get scene metadata."""
        return self._data.get("scene", {})

    @property
    def scene_id(self) -> str:
        """Get scene ID."""
        return self.scene.get("id", "unknown")

    @property
    def director(self) -> Dict[str, Any]:
        """Get director metadata."""
        return self._data.get("director", {})

    @property
    def dialogue_strategy(self) -> str:
        """Get dialogue strategy."""
        return self.director.get("dialogue_strategy", "none")

    @property
    def characters(self) -> List[Dict[str, Any]]:
        """Get character list."""
        return self._data.get("characters", [])

    @property
    def shots(self) -> List[Dict[str, Any]]:
        """Get all shots."""
        return self._data.get("shots", [])

    def get_shot(self, shot_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific shot by ID."""
        for shot in self.shots:
            if shot.get("id") == shot_id:
                return shot
        return None

    def get_character_element(self, char_id: str) -> Optional[str]:
        """Get the element ID for a character."""
        for char in self.characters:
            if char.get("id") == char_id:
                return char.get("element")
        return None

    def get_location(self) -> str:
        """Get the scene's location key."""
        return self.scene.get("location", "")

    def get_lighting_mode(self) -> str:
        """Get the scene's lighting mode based on time_of_day."""
        time = self.scene.get("time_of_day", "night")
        if time in ["day", "dusk", "dawn"]:
            return "day"
        return "night"

    def resolve_shot_refs(self, shot: Dict[str, Any]) -> List[Path]:
        """
        Resolve reference paths for a shot.

        Uses per-shot refs config if present, otherwise falls back to
        scene-level default_refs config. If neither exists, auto-includes
        identity sheets for any characters in the shot.

        Args:
            shot: Shot definition dict

        Returns:
            List of resolved reference paths
        """
        refs = []
        ref_config = shot.get("refs", self._data.get("default_refs", {}))

        # If no refs config at all, default to including identity sheets
        include_identity = ref_config.get("include_identity", not ref_config)
        include_location = ref_config.get("include_location", False)

        # Character identity sheets
        if include_identity:
            for char in shot.get("characters", []):
                identity = self.config.get_identity_sheet(char)
                if identity:
                    refs.append(identity)

        # Location reference
        if include_location:
            location = self.get_location()
            loc_ref = self.config.get_location_ref(location)
            if loc_ref:
                refs.append(loc_ref)

        # Storyboard — check scene-level mapping first, then config
        storyboard_mapping = self._data.get("storyboard_mapping", {})
        shot_id = shot.get("id")
        storyboard_path = None
        if storyboard_mapping and shot_id is not None:
            for board_file, shot_ids in storyboard_mapping.items():
                if shot_id in shot_ids:
                    # Resolve relative to shot_list.yaml directory
                    storyboard_path = self.yaml_path.parent / board_file
                    break
        if storyboard_path and storyboard_path.exists():
            refs.append(storyboard_path)
        elif ref_config.get("include_storyboard", False):
            storyboard = self.config.get_storyboard(self.scene_id)
            if storyboard:
                refs.append(storyboard)

        # Additional refs — try scene-relative first, then exports-relative
        for additional in ref_config.get("additional", []):
            path = self.yaml_path.parent / additional
            if not path.exists():
                path = self.config.exports_dir / additional
            if path.exists():
                refs.append(path)

        return refs

    def build_shot_prompt(
        self,
        shot: Dict[str, Any],
        include_dialogue_control: bool = True,
        include_sfx: bool = True,
    ) -> str:
        """
        Build the full prompt for a shot.

        Args:
            shot: Shot definition dict
            include_dialogue_control: Whether to append dialogue control text
            include_sfx: Whether to append SFX/sound text (False for frame gen)

        Returns:
            Complete prompt string
        """
        prompt = shot.get("prompt", "").strip()

        # Add dialogue control based on strategy
        # Skip if prompt already contains silence directives to avoid redundancy
        prompt_lower = prompt.lower()
        has_silence = "no talking" in prompt_lower or "characters are silent" in prompt_lower
        if include_dialogue_control and not has_silence:
            dialogue = shot.get("dialogue", self.dialogue_strategy)
            if dialogue == "none":
                prompt += ", no spoken dialogue"
            elif dialogue == "breathing":
                prompt += ", only breathing sounds, no spoken dialogue"
            elif dialogue == "effort":
                prompt += ", wordless grunts and effort sounds, no spoken dialogue"
            elif dialogue == "reaction":
                prompt += ", non-verbal reactions only, no spoken dialogue"
            # "scripted" would have specific dialogue in the prompt already

        # Build SFX line from shot sound data (skip for frame generation)
        if not include_sfx:
            return prompt
        sound = shot.get("sound", {})
        if isinstance(sound, str):
            # Flat string format: "SFX: Boots on wet slate, wind rush"
            sfx_text = sound.strip()
            if sfx_text.upper().startswith("SFX:"):
                sfx_text = sfx_text[4:].strip()
            if sfx_text:
                prompt += f". SFX: We hear {sfx_text.lower()}"
        elif isinstance(sound, dict):
            sfx_parts = []
            if sound.get("ambient"):
                sfx_parts.append(sound["ambient"].strip())
            if sound.get("character"):
                sfx_parts.append(sound["character"].strip())
            if sfx_parts:
                prompt += f". SFX: We hear {', '.join(sfx_parts).lower()}"

        return prompt

    def get_required_frames(self) -> List[Dict[str, Any]]:
        """Get shots that need frames generated.

        Returns shots with priority 'required', or all shots if no
        priority field is set on any shot.
        """
        required = [s for s in self.shots if s.get("priority") == "required"]
        if required:
            return required
        # No priority fields set — return all shots
        return list(self.shots)


class ClipDefinitions:
    """Loads and provides access to clip definitions."""

    def __init__(self, yaml_path: Path, shot_list: ShotList):
        self.yaml_path = Path(yaml_path)
        self.shot_list = shot_list

        if not self.yaml_path.exists():
            raise FileNotFoundError(f"Clip definitions not found: {self.yaml_path}")

        with open(self.yaml_path) as f:
            self._data = yaml.safe_load(f)

    @property
    def raw_data(self) -> Dict[str, Any]:
        """Get raw YAML data for direct access to scene-level config."""
        return self._data

    @property
    def scene_id(self) -> str:
        """Get scene ID."""
        return self._data.get("scene_id", "unknown")

    @property
    def clips(self) -> List[Dict[str, Any]]:
        """Get all clips."""
        return self._data.get("clips", [])

    @property
    def assembly(self) -> Dict[str, Any]:
        """Get assembly configuration."""
        return self._data.get("assembly", {})

    def get_clip(self, clip_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific clip by ID."""
        for clip in self.clips:
            if clip.get("id") == clip_id:
                return clip
        return None

    def get_prompt_mode(self, clip: Dict[str, Any]) -> str:
        """Get prompt mode for a clip: 'narrative' or 'multi_prompt' (default)."""
        return clip.get("prompt_mode", "multi_prompt")

    def get_clip_characters(self, clip: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        Get character definitions for a clip.

        Returns:
            List of {"id": str, "element": str} dicts
        """
        char_ids = clip.get("characters", [])
        result = []

        for char_id in char_ids:
            element = self.shot_list.get_character_element(char_id)
            if element:
                result.append({"id": char_id, "element": element})

        return result

    def build_clip_prompts(self, clip: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Build prompts for a clip.

        In narrative mode: returns single-item list with the full narrative prompt.
        In multi_prompt mode: resolves shot_refs to individual prompts.

        Returns:
            List of {"prompt": str, "duration": int, "cut_prefix": bool} dicts
        """
        prompt_mode = self.get_prompt_mode(clip)

        if prompt_mode == "narrative":
            narrative_text = clip.get("narrative_prompt", "")
            if not narrative_text:
                print(f"  WARNING: Clip in narrative mode but no narrative_prompt defined")
                return []
            total_duration = clip.get("duration", 10)
            return [{
                "prompt": narrative_text.strip(),
                "duration": total_duration,
                "cut_prefix": False,
            }]

        # Multi-prompt mode: existing behavior
        prompts = []

        for prompt_def in clip.get("prompts", []):
            shot_ref = prompt_def.get("shot_ref")
            custom_prompt = prompt_def.get("prompt")
            duration = prompt_def.get("duration", 3)
            cut_prefix = prompt_def.get("cut_prefix", True)

            if custom_prompt:
                # Use custom prompt directly
                prompt_text = custom_prompt.strip()
            elif shot_ref:
                # Build prompt from shot reference
                shot = self.shot_list.get_shot(shot_ref)
                if shot:
                    prompt_text = self.shot_list.build_shot_prompt(shot)
                else:
                    print(f"  WARNING: Shot {shot_ref} not found")
                    continue
            else:
                print(f"  WARNING: No prompt or shot_ref in prompt definition")
                continue

            prompts.append({
                "prompt": prompt_text,
                "duration": duration,
                "cut_prefix": cut_prefix,
            })

        return prompts

    def get_start_frame_strategy(self, clip: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get start frame strategy for a clip.

        Returns:
            Dict with "strategy" and relevant keys (shot_id, clip_id, or custom_path)
        """
        return clip.get("start_frame", {"strategy": "shot", "shot_id": 1})

    def get_assembly_order(self) -> List[int]:
        """Get the clip assembly order."""
        return self.assembly.get("clips", [])


def load_shot_list(yaml_path: Path, config: ProjectConfig) -> ShotList:
    """Load a shot list from YAML."""
    return ShotList(yaml_path, config)


def load_clip_definitions(yaml_path: Path, shot_list: ShotList) -> ClipDefinitions:
    """Load clip definitions from YAML."""
    return ClipDefinitions(yaml_path, shot_list)
