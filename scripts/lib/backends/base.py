"""
Backend protocol definitions for video and image generation.

Defines the abstract interface that all backends must implement,
plus result dataclasses for backend-neutral return values.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Any, List, Optional


@dataclass
class VideoResult:
    """Result from a video generation backend."""
    video_bytes: Optional[bytes] = None   # ComfyUI: raw bytes
    video_url: Optional[str] = None       # Fal: download URL
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ImageResult:
    """Result from an image generation backend."""
    image_bytes: Optional[bytes] = None
    image_url: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class VideoBackend(ABC):
    """Abstract interface for video generation backends."""

    name: str = "base"
    supports_elements: bool = False
    supports_multi_prompt: bool = False
    supports_audio: bool = False
    cost_per_second: float = 0.0

    @abstractmethod
    def generate_video(
        self,
        start_frame: Path,
        prompt: str,
        duration_seconds: float,
        negative_prompt: str = "",
        seed: Optional[int] = None,
        reference_audio: Optional[Path] = None,
        **backend_kwargs,
    ) -> VideoResult:
        """
        Generate a video clip from a start frame and prompt.

        Args:
            start_frame: Path to the start frame image
            prompt: The generation prompt (single string)
            duration_seconds: Desired clip duration in seconds
            negative_prompt: Negative prompt text
            seed: Random seed for reproducibility
            reference_audio: Optional path to a voice reference WAV for audio-driven generation
            **backend_kwargs: Backend-specific parameters (elements, multi_prompt, etc.)

        Returns:
            VideoResult with either video_bytes or video_url populated
        """
        ...

    def health_check(self) -> bool:
        """Check if the backend service is reachable. Returns True if healthy."""
        return True


class ImageBackend(ABC):
    """Abstract interface for image generation backends."""

    name: str = "base"
    cost_per_image: float = 0.0

    @abstractmethod
    def generate_image(
        self,
        prompt: str,
        reference_urls: Optional[List[str]] = None,
        negative_prompt: str = "",
        aspect_ratio: str = "16:9",
        seed: Optional[int] = None,
        **backend_kwargs,
    ) -> ImageResult:
        """
        Generate an image from a prompt.

        Args:
            prompt: The generation prompt
            reference_urls: Optional list of reference image URLs
            negative_prompt: Negative prompt text
            aspect_ratio: Output aspect ratio
            seed: Random seed for reproducibility
            **backend_kwargs: Backend-specific parameters

        Returns:
            ImageResult with either image_bytes or image_url populated
        """
        ...

    @abstractmethod
    def upload_image(self, filepath: Path) -> str:
        """Upload a local image and return a URL usable by this backend."""
        ...

    def health_check(self) -> bool:
        """Check if the backend service is reachable."""
        return True
