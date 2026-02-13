"""
Backend factory for video and image generation.

Usage:
    from lib.backends import create_video_backend, create_image_backend

    video_backend = create_video_backend(config)  # reads PROJECT_CONFIG.yaml
    image_backend = create_image_backend(config)
"""

import os
from typing import Optional

from .base import VideoBackend, ImageBackend, VideoResult, ImageResult


def get_video_backend_name(config=None) -> str:
    """
    Determine which video backend to use.

    Priority: CODEYWOOD_VIDEO_BACKEND env var > PROJECT_CONFIG.yaml > default ("fal")
    """
    env = os.getenv("CODEYWOOD_VIDEO_BACKEND")
    if env:
        return env.lower()

    if config is not None:
        backend_config = _get_backend_config(config)
        return backend_config.get("video", "fal")

    return "fal"


def get_image_backend_name(config=None) -> str:
    """
    Determine which image backend to use.

    Priority: CODEYWOOD_IMAGE_BACKEND env var > PROJECT_CONFIG.yaml > default ("fal")
    """
    env = os.getenv("CODEYWOOD_IMAGE_BACKEND")
    if env:
        return env.lower()

    if config is not None:
        backend_config = _get_backend_config(config)
        return backend_config.get("image", "fal")

    return "fal"


def _get_backend_config(config) -> dict:
    """Extract backend config dict from ProjectConfig."""
    if hasattr(config, '_config'):
        return config._config.get("backend", {})
    return {}


def _get_comfyui_settings(config) -> dict:
    """Extract ComfyUI-specific settings from config."""
    backend_config = _get_backend_config(config)
    return backend_config.get("comfyui", {})


def create_video_backend(config=None, preflight: bool = False) -> Optional[VideoBackend]:
    """
    Create and return a video generation backend.

    Args:
        config: ProjectConfig instance (optional, for reading backend settings)
        preflight: If True, skip authentication checks

    Returns:
        VideoBackend instance, or None if preflight mode (no backend needed)
    """
    if preflight:
        return None

    name = get_video_backend_name(config)

    if name == "comfyui":
        from .comfyui_backend import ComfyUIVideoBackend
        settings = _get_comfyui_settings(config) if config else {}
        return ComfyUIVideoBackend(
            base_url=settings.get("base_url", "http://192.168.1.181:8100"),
            workflow=settings.get("video_workflow", "ltx2-i2v"),
            fps=settings.get("fps", 25),
        )
    elif name == "fal":
        from .fal_backend import FalVideoBackend
        # Get endpoint from config if available
        endpoint = "fal-ai/kling-video/v3/pro/image-to-video"
        if config and hasattr(config, 'get_model_endpoint'):
            try:
                endpoint = config.get_model_endpoint("kling", "image_to_video")
            except (ValueError, KeyError):
                pass
        return FalVideoBackend(endpoint=endpoint)
    else:
        raise ValueError(f"Unknown video backend: {name}. Supported: fal, comfyui")


def create_image_backend(config=None, preflight: bool = False) -> Optional[ImageBackend]:
    """
    Create and return an image generation backend.

    Args:
        config: ProjectConfig instance
        preflight: If True, skip authentication checks

    Returns:
        ImageBackend instance, or None if preflight mode
    """
    if preflight:
        return None

    name = get_image_backend_name(config)

    if name == "comfyui":
        from .comfyui_backend import ComfyUIImageBackend
        settings = _get_comfyui_settings(config) if config else {}
        return ComfyUIImageBackend(
            base_url=settings.get("base_url", "http://192.168.1.181:8100"),
            workflow=settings.get("image_workflow", "flux2-klein-t2i"),
        )
    elif name == "fal":
        from .fal_backend import FalImageBackend
        return FalImageBackend()
    else:
        raise ValueError(f"Unknown image backend: {name}. Supported: fal, comfyui")


__all__ = [
    "VideoBackend",
    "ImageBackend",
    "VideoResult",
    "ImageResult",
    "create_video_backend",
    "create_image_backend",
    "get_video_backend_name",
    "get_image_backend_name",
]
