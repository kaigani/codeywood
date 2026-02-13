"""Shared types for the prompt template library."""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class CharacterDesc:
    """A character's visual description for prompt composition."""
    id: str                            # "mars", "jonah"
    description: str                   # Full physical description (~100-150 chars)
    element_tag: Optional[str] = None  # "@Element1" (Kling only)


@dataclass
class SettingAnchor:
    """Setting/location description anchoring every prompt."""
    description: str                   # Full setting text (~100-200 chars)
    time_of_day: str = ""
    period: str = ""


@dataclass
class PromptInputs:
    """All possible inputs for prompt composition."""
    setting: SettingAnchor
    action: str                        # What happens in this shot
    characters: List[CharacterDesc] = field(default_factory=list)
    shot_type: str = ""                # "Cinematic medium shot"
    dialogue: Optional[str] = None     # Quoted speech as narrative
    camera: Optional[str] = None       # "Camera static", "slow push in"
    sound: Optional[str] = None        # "Dripping water, creaking wood"
    body_language: Optional[str] = None
    lighting: Optional[str] = None
    frozen_moment: Optional[str] = None  # Frame-only: single moment desc


@dataclass
class PromptResult:
    """Output from a compose() function."""
    prompt: str
    char_count: int
    warnings: List[str] = field(default_factory=list)
    negative_prompt: str = ""
