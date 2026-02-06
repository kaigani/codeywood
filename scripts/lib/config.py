"""
Configuration loader for visual production.

Loads PROJECT_CONFIG.yaml and provides access to:
- Style DNA
- Asset paths (identity sheets, location refs, etc.)
- Model configurations
- Video Director defaults
"""

import os
from pathlib import Path
from typing import Optional, Dict, Any
import yaml

# Load .env file if python-dotenv is available
try:
    from dotenv import load_dotenv
    # Try multiple locations for .env
    for env_path in [
        Path.cwd() / ".env",
        Path.cwd().parent / ".env",
        Path.cwd().parent.parent / ".env",
        Path(__file__).parent.parent.parent.parent / ".env",  # codeywood root
    ]:
        if env_path.exists():
            load_dotenv(env_path)
            break
except ImportError:
    pass


class ProjectConfig:
    """Loads and provides access to project configuration."""

    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)
        # Support both new (REFERENCES/) and legacy (EXPORTS/) layouts
        refs = self.project_root / "REFERENCES"
        self.references_dir = refs if refs.exists() else self.project_root / "EXPORTS"
        self.exports_dir = self.references_dir  # backward compat alias
        self.config_path = self.project_root / "PROJECT_CONFIG.yaml"

        if not self.config_path.exists():
            raise FileNotFoundError(f"PROJECT_CONFIG.yaml not found at {self.config_path}")

        with open(self.config_path) as f:
            self._config = yaml.safe_load(f)

    @property
    def style_dna(self) -> Dict[str, Any]:
        """Get style DNA configuration."""
        return self._config.get("style_dna", {})

    @property
    def models(self) -> Dict[str, Any]:
        """Get model configurations."""
        return self._config.get("models", {})

    @property
    def assets(self) -> Dict[str, Any]:
        """Get asset manifest."""
        return self._config.get("assets", {})

    @property
    def characters(self) -> Dict[str, Any]:
        """Get character definitions."""
        return self._config.get("characters", {})

    @property
    def locations(self) -> Dict[str, Any]:
        """Get location definitions."""
        return self._config.get("locations", {})

    @property
    def video_director(self) -> Dict[str, Any]:
        """Get video director defaults."""
        return self._config.get("video_director", {})

    @property
    def negative_prompts(self) -> list:
        """Get global negative prompts."""
        return self._config.get("negative_prompts", [])

    def get_model_endpoint(self, model_id: str, modality: str) -> str:
        """Get FAL endpoint for a model and modality."""
        model = self.models.get(model_id)
        if not model:
            raise ValueError(f"Unknown model: {model_id}")

        endpoints = model.get("endpoints", {})
        # Handle both underscore and hyphen formats
        endpoint = endpoints.get(modality) or endpoints.get(modality.replace("-", "_"))
        if not endpoint:
            raise ValueError(f"Model '{model_id}' does not support modality '{modality}'")

        return endpoint

    def get_model_defaults(self, model_id: str) -> Dict[str, Any]:
        """Get default parameters for a model."""
        model = self.models.get(model_id)
        if not model:
            return {}
        return model.get("defaults", {})

    def resolve_asset_path(self, asset_type: str, asset_key: str, sub_key: str = None) -> Optional[Path]:
        """
        Resolve an asset path from the manifest.

        Args:
            asset_type: One of 'identity_sheets', 'hero_shots', 'location_refs', 'storyboards'
            asset_key: The asset key (e.g., 'mars', 'holding_cells')
            sub_key: Optional sub-key for nested assets (e.g., 'entrance' for hero_shots)

        Returns:
            Absolute path to the asset, or None if not found
        """
        assets = self.assets.get(asset_type, {})

        if sub_key:
            # Nested structure (e.g., hero_shots.mars.entrance)
            asset_group = assets.get(asset_key, {})
            relative_path = asset_group.get(sub_key)
        else:
            relative_path = assets.get(asset_key)

        if not relative_path:
            return None

        full_path = self.exports_dir / relative_path
        return full_path if full_path.exists() else None

    def get_identity_sheet(self, character_id: str) -> Optional[Path]:
        """Get identity sheet path for a character."""
        return self.resolve_asset_path("identity_sheets", character_id)

    def get_hero_shot(self, character_id: str, shot_type: str = "entrance") -> Optional[Path]:
        """Get hero shot path for a character."""
        return self.resolve_asset_path("hero_shots", character_id, shot_type)

    def get_location_ref(self, location_id: str) -> Optional[Path]:
        """Get location reference path."""
        path = self.resolve_asset_path("location_refs", location_id)
        if path:
            return path

        # Check for fallback in location definitions
        location_def = self.locations.get(location_id, {})
        fallback = location_def.get("fallback") if isinstance(location_def, dict) else None
        if fallback:
            return self.resolve_asset_path("location_refs", fallback)

        return None

    def get_storyboard(self, scene_id: str) -> Optional[Path]:
        """Get storyboard path for a scene."""
        return self.resolve_asset_path("storyboards", scene_id)

    def build_style_prompt(self, lighting_mode: str = "night") -> str:
        """
        Build style DNA prompt string.

        Args:
            lighting_mode: One of 'day', 'night', 'supernatural'

        Returns:
            Style DNA prompt string
        """
        style = self.style_dna
        parts = []

        # Add medium/era
        if style.get("medium_era"):
            parts.append(style["medium_era"])

        # Add cinematography
        if style.get("cinematography"):
            parts.append(style["cinematography"])

        # Add lighting for mode
        lighting = style.get("lighting", {}).get(lighting_mode, {})
        if lighting.get("keywords"):
            parts.append(lighting["keywords"])

        # Add textures
        textures = style.get("textures", [])
        if textures:
            parts.append(", ".join(textures))

        return ". ".join(parts)

    def build_negative_prompt(self, for_video: bool = False) -> str:
        """
        Build negative prompt string.

        Args:
            for_video: If True, include video-specific negative prompts

        Returns:
            Negative prompt string
        """
        prompts = list(self.negative_prompts)

        if for_video:
            video_negative = self.video_director.get("video_negative_prompt", "")
            if video_negative:
                prompts.extend([p.strip() for p in video_negative.split(",")])

        return ", ".join(prompts)


def find_project_root(start_path: Path = None) -> Path:
    """
    Find the project root by looking for PROJECT_CONFIG.yaml.

    Args:
        start_path: Starting directory (defaults to current working directory)

    Returns:
        Path to project root

    Raises:
        FileNotFoundError if PROJECT_CONFIG.yaml not found
    """
    if start_path is None:
        start_path = Path.cwd()

    current = Path(start_path).resolve()

    # Walk up the directory tree
    while current != current.parent:
        config_path = current / "PROJECT_CONFIG.yaml"
        if config_path.exists():
            return current
        current = current.parent

    raise FileNotFoundError(
        f"Could not find PROJECT_CONFIG.yaml starting from {start_path}"
    )


def load_config(project_path: Path = None) -> ProjectConfig:
    """
    Load project configuration.

    Args:
        project_path: Path to project root (auto-detected if not provided)

    Returns:
        ProjectConfig instance
    """
    if project_path is None:
        project_path = find_project_root()

    return ProjectConfig(project_path)
