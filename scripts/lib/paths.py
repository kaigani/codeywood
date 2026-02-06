"""
Centralized path resolution for Codeywood projects.

All path logic lives here. Scripts use these functions instead of
hardcoding directory names. Supports both new (REFERENCES/PRODUCTION)
and legacy (EXPORTS/VISUAL_PRODUCTION) layouts.
"""

from pathlib import Path
from typing import Optional


def find_project_root(start_path: Path = None) -> Path:
    """
    Find the project root by looking for PROJECT_CONFIG.yaml.

    Walks up the directory tree from start_path.
    """
    if start_path is None:
        start_path = Path.cwd()

    current = Path(start_path).resolve()

    while current != current.parent:
        if (current / "PROJECT_CONFIG.yaml").exists():
            return current
        current = current.parent

    raise FileNotFoundError(
        f"Could not find PROJECT_CONFIG.yaml starting from {start_path}"
    )


def find_codeywood_root(start_path: Path = None) -> Path:
    """
    Find the codeywood monorepo root by looking for CLAUDE.md.

    Walks up the directory tree from start_path.
    """
    if start_path is None:
        start_path = Path.cwd()

    current = Path(start_path).resolve()

    while current != current.parent:
        if (current / "CLAUDE.md").exists():
            return current
        current = current.parent

    raise FileNotFoundError(
        f"Could not find CLAUDE.md starting from {start_path}"
    )


def references_dir(project_root: Path) -> Path:
    """
    Get the shared references directory.

    New layout: REFERENCES/
    Legacy layout: EXPORTS/
    """
    new = project_root / "REFERENCES"
    if new.exists():
        return new
    legacy = project_root / "EXPORTS"
    if legacy.exists():
        return legacy
    raise FileNotFoundError(
        f"Neither REFERENCES/ nor EXPORTS/ found in {project_root}"
    )


def production_dir(project_root: Path) -> Path:
    """
    Get the production working directory.

    New layout: PRODUCTION/
    Legacy layout: VISUAL_PRODUCTION/
    """
    new = project_root / "PRODUCTION"
    if new.exists():
        return new
    legacy = project_root / "VISUAL_PRODUCTION"
    if legacy.exists():
        return legacy
    raise FileNotFoundError(
        f"Neither PRODUCTION/ nor VISUAL_PRODUCTION/ found in {project_root}"
    )


def scene_dir(project_root: Path, episode_id: str, scene_id: str) -> Path:
    """
    Get the per-scene production directory.

    New layout: PRODUCTION/EP01/sc03/
    Legacy layout: VISUAL_PRODUCTION/ (no per-scene consolidation)

    Returns the new-layout path, creating it if needed when PRODUCTION/ exists.
    Falls back to legacy paths if only VISUAL_PRODUCTION/ exists.
    """
    prod = production_dir(project_root)

    # New layout
    new_path = prod / episode_id / scene_id
    if new_path.exists():
        return new_path

    # If PRODUCTION/ exists but scene dir doesn't, create it
    if prod.name == "PRODUCTION":
        new_path.mkdir(parents=True, exist_ok=True)
        return new_path

    # Legacy layout — return the base production dir (caller handles sub-paths)
    return prod


def scene_frames_dir(project_root: Path, episode_id: str, scene_id: str) -> Path:
    """Get the frames directory for a scene."""
    sd = scene_dir(project_root, episode_id, scene_id)

    # New layout: frames/ in scene dir
    new_path = sd / "frames"
    if new_path.exists() or sd.parent.name == episode_id:
        new_path.mkdir(parents=True, exist_ok=True)
        return new_path

    # Legacy: EXPORTS/shot_frames/EP01/sc03/ or VISUAL_PRODUCTION/sc03_outputs/frames/
    legacy_exports = references_dir(project_root) / "shot_frames" / episode_id / scene_id
    if legacy_exports.exists():
        return legacy_exports

    legacy_vp = sd / f"{scene_id}_outputs" / "frames"
    if legacy_vp.exists():
        return legacy_vp

    # Default to new layout
    new_path.mkdir(parents=True, exist_ok=True)
    return new_path


def scene_clips_dir(project_root: Path, episode_id: str, scene_id: str) -> Path:
    """Get the clips directory for a scene."""
    sd = scene_dir(project_root, episode_id, scene_id)

    # New layout
    new_path = sd / "clips"
    if new_path.exists() or sd.parent.name == episode_id:
        new_path.mkdir(parents=True, exist_ok=True)
        return new_path

    # Legacy
    legacy = sd / f"{scene_id}_outputs" / "clips"
    if legacy.exists():
        return legacy

    new_path.mkdir(parents=True, exist_ok=True)
    return new_path


def scene_assembly_dir(project_root: Path, episode_id: str, scene_id: str) -> Path:
    """Get the assembly directory for a scene."""
    sd = scene_dir(project_root, episode_id, scene_id)

    # New layout
    new_path = sd / "assembly"
    if new_path.exists() or sd.parent.name == episode_id:
        new_path.mkdir(parents=True, exist_ok=True)
        return new_path

    # Legacy
    legacy = sd / f"{scene_id}_outputs" / "assembly"
    if legacy.exists():
        return legacy

    new_path.mkdir(parents=True, exist_ok=True)
    return new_path


def deliverables_dir(project_root: Path) -> Path:
    """Get the deliverables directory for final outputs."""
    path = project_root / "DELIVERABLES"
    path.mkdir(parents=True, exist_ok=True)
    return path


def resolve_shot_list(project_root: Path, episode_id: str, scene_id: str) -> Optional[Path]:
    """Find the shot list YAML for a scene."""
    sd = scene_dir(project_root, episode_id, scene_id)

    # New layout: shot_list.yaml in scene dir
    new_path = sd / "shot_list.yaml"
    if new_path.exists():
        return new_path

    # Legacy: VISUAL_PRODUCTION/shot_lists/sc03_shots.yaml
    prod = production_dir(project_root)
    legacy = prod / "shot_lists" / f"{scene_id}_shots.yaml"
    if legacy.exists():
        return legacy

    return None


def resolve_clip_definitions(project_root: Path, episode_id: str, scene_id: str) -> Optional[Path]:
    """Find the clip definitions YAML for a scene."""
    sd = scene_dir(project_root, episode_id, scene_id)

    # New layout
    new_path = sd / "clip_definitions.yaml"
    if new_path.exists():
        return new_path

    # Legacy
    prod = production_dir(project_root)
    legacy = prod / "clip_definitions" / f"{scene_id}_clips.yaml"
    if legacy.exists():
        return legacy

    return None
