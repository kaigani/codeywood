"""
FAL backend for video and image generation.

Wraps fal_client SDK for Kling video and Nano Banana Pro image generation.
"""

import os
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable

import requests

try:
    import fal_client
except ImportError:
    fal_client = None

from .base import VideoBackend, ImageBackend, VideoResult, ImageResult


class FalVideoBackend(VideoBackend):
    """Kling v3 Pro video generation via fal_client."""

    name = "fal"
    supports_elements = True
    supports_multi_prompt = True
    supports_audio = True
    cost_per_second = 0.336

    def __init__(self, endpoint: str = "fal-ai/kling-video/v3/pro/image-to-video"):
        if fal_client is None:
            raise ImportError("fal_client not installed. Run: pip install fal-client")
        if not os.getenv("FAL_KEY"):
            raise EnvironmentError("FAL_KEY environment variable not set")
        self.endpoint = endpoint
        self._upload_cache: Dict[str, str] = {}

    def upload_image(self, filepath: Path) -> str:
        """Upload a local image and return the FAL URL."""
        filepath = Path(filepath)
        cache_key = str(filepath.resolve())
        if cache_key in self._upload_cache:
            return self._upload_cache[cache_key]
        if not filepath.exists():
            raise FileNotFoundError(f"Image not found: {filepath}")
        print(f"  Uploading: {filepath.name}")
        url = fal_client.upload_file(str(filepath))
        print(f"    -> {url[:60]}...")
        self._upload_cache[cache_key] = url
        return url

    def _on_queue_update(self, update):
        status = type(update).__name__
        if status == "Completed":
            print(f"  [{status}]")
        else:
            print(f"  [{status}]", end="\r")

    def generate_video(
        self,
        start_frame: Path,
        prompt: str,
        duration_seconds: float,
        negative_prompt: str = "",
        seed: Optional[int] = None,
        on_queue_update: Optional[Callable] = None,
        **backend_kwargs,
    ) -> VideoResult:
        """
        Generate video via Kling API.

        Backend-specific kwargs:
            elements: List of element dicts for character/location consistency
            multi_prompt: List of {"prompt": str, "duration": str} dicts (overrides prompt)
            shot_type: Shot type string (e.g., "customize")
            aspect_ratio: Output aspect ratio
            generate_audio: Whether to generate audio
        """
        start_url = self.upload_image(start_frame)

        request = {
            "start_image_url": start_url,
            "aspect_ratio": backend_kwargs.get("aspect_ratio", "16:9"),
            "generate_audio": backend_kwargs.get("generate_audio", True),
            "negative_prompt": negative_prompt,
        }

        # Multi-prompt mode vs narrative mode
        multi_prompt = backend_kwargs.get("multi_prompt")
        if multi_prompt:
            request["multi_prompt"] = multi_prompt
            request["shot_type"] = backend_kwargs.get("shot_type", "customize")
        else:
            request["prompt"] = prompt
            request["duration"] = str(int(duration_seconds))

        # Elements (character/location identity)
        elements = backend_kwargs.get("elements")
        if elements:
            request["elements"] = elements

        result = fal_client.subscribe(
            self.endpoint,
            arguments=request,
            with_logs=True,
            on_queue_update=on_queue_update or self._on_queue_update,
        )

        video_url = None
        if result and "video" in result:
            video_url = result["video"].get("url")

        return VideoResult(
            video_url=video_url,
            metadata={"endpoint": self.endpoint, "request": request},
        )

    def health_check(self) -> bool:
        return fal_client is not None and bool(os.getenv("FAL_KEY"))


class FalImageBackend(ImageBackend):
    """Nano Banana Pro image generation via fal_client."""

    name = "fal"
    cost_per_image = 0.15

    def __init__(self):
        if fal_client is None:
            raise ImportError("fal_client not installed. Run: pip install fal-client")
        if not os.getenv("FAL_KEY"):
            raise EnvironmentError("FAL_KEY environment variable not set")
        self._upload_cache: Dict[str, str] = {}

    def upload_image(self, filepath: Path) -> str:
        filepath = Path(filepath)
        cache_key = str(filepath.resolve())
        if cache_key in self._upload_cache:
            return self._upload_cache[cache_key]
        if not filepath.exists():
            raise FileNotFoundError(f"Image not found: {filepath}")
        print(f"  Uploading: {filepath.name}")
        url = fal_client.upload_file(str(filepath))
        print(f"    -> {url[:60]}...")
        self._upload_cache[cache_key] = url
        return url

    def _on_queue_update(self, update):
        status = type(update).__name__
        if status == "Completed":
            print(f"  [{status}]")
        else:
            print(f"  [{status}]", end="\r")

    def generate_image(
        self,
        prompt: str,
        reference_urls: Optional[List[str]] = None,
        negative_prompt: str = "",
        aspect_ratio: str = "16:9",
        seed: Optional[int] = None,
        on_queue_update: Optional[Callable] = None,
        **backend_kwargs,
    ) -> ImageResult:
        """
        Generate image via Nano Banana Pro.

        Backend-specific kwargs:
            endpoint: Override endpoint (text_to_image vs edit)
            resolution: Output resolution (e.g., "2K")
            num_inference_steps: Inference steps
            guidance_scale: Guidance scale
        """
        endpoint = backend_kwargs.get("endpoint", "fal-ai/nano-banana-pro")

        # If references provided, use edit endpoint
        if reference_urls and endpoint == "fal-ai/nano-banana-pro":
            endpoint = "fal-ai/nano-banana-pro/edit"

        request = {
            "prompt": prompt,
            "num_images": 1,
            "output_format": backend_kwargs.get("output_format", "png"),
            "negative_prompt": negative_prompt,
        }

        if reference_urls:
            request["image_urls"] = reference_urls
            request["aspect_ratio"] = aspect_ratio
            request["resolution"] = backend_kwargs.get("resolution", "2K")
        else:
            # Text-to-image mode
            request["image_size"] = backend_kwargs.get("image_size", "square_hd")
            request["num_inference_steps"] = backend_kwargs.get("num_inference_steps", 40)
            request["guidance_scale"] = backend_kwargs.get("guidance_scale", 4.5)

        if seed is not None:
            request["seed"] = seed

        result = fal_client.subscribe(
            endpoint,
            arguments=request,
            with_logs=True,
            on_queue_update=on_queue_update or self._on_queue_update,
        )

        image_url = None
        if result and "images" in result and len(result["images"]) > 0:
            image_url = result["images"][0].get("url")

        return ImageResult(
            image_url=image_url,
            metadata={"endpoint": endpoint, "request": request},
        )

    def health_check(self) -> bool:
        return fal_client is not None and bool(os.getenv("FAL_KEY"))
