"""
FAL API wrapper for visual production.

Provides high-level functions for:
- Image generation (frames, storyboards)
- Video generation (clips)
- File upload/download
"""

import os
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Callable
import requests

try:
    import fal_client
except ImportError:
    fal_client = None

from .config import ProjectConfig


class FalGenerator:
    """High-level FAL API wrapper."""

    def __init__(self, config: ProjectConfig, output_dir: Path):
        if fal_client is None:
            raise ImportError("fal_client not installed. Run: pip install fal-client")

        if not os.getenv("FAL_KEY"):
            raise EnvironmentError("FAL_KEY environment variable not set")

        self.config = config
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Track uploaded URLs to avoid re-uploading
        self._upload_cache: Dict[str, str] = {}

    def upload_image(self, filepath: Path) -> str:
        """
        Upload a local image and return the FAL URL.
        Uses caching to avoid re-uploading the same file.
        """
        filepath = Path(filepath)
        cache_key = str(filepath.resolve())

        if cache_key in self._upload_cache:
            return self._upload_cache[cache_key]

        if not filepath.exists():
            raise FileNotFoundError(f"Image not found: {filepath}")

        print(f"  Uploading: {filepath.name}")
        url = fal_client.upload_file(str(filepath))
        print(f"    ✓ {url[:60]}...")

        self._upload_cache[cache_key] = url
        return url

    def upload_images(self, filepaths: List[Path]) -> List[str]:
        """Upload multiple images and return URLs."""
        urls = []
        for fp in filepaths:
            if fp and Path(fp).exists():
                urls.append(self.upload_image(fp))
        return urls

    def _on_queue_update(self, update):
        """Default queue update handler."""
        status = type(update).__name__
        if status == "Completed":
            print(f"  [{status}]")
        else:
            print(f"  [{status}]", end="\r")

    def _download_file(self, url: str, output_path: Path) -> bool:
        """Download a file from URL."""
        response = requests.get(url)
        if response.status_code == 200:
            with open(output_path, "wb") as f:
                f.write(response.content)
            return True
        return False

    def _save_metadata(self, output_path: Path, metadata: Dict[str, Any]):
        """Save generation metadata as JSON."""
        metadata_path = output_path.with_suffix(".json")
        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=2, default=str)

    def generate_frame(
        self,
        prompt: str,
        refs: List[Path] = None,
        output_name: str = "frame",
        lighting_mode: str = "night",
        negative_prompt: str = None,
        on_queue_update: Callable = None,
    ) -> Optional[Path]:
        """
        Generate a production frame using Nano Banana Pro.

        Args:
            prompt: The generation prompt (without style DNA)
            refs: List of reference image paths
            output_name: Base name for output file
            lighting_mode: One of 'day', 'night', 'supernatural'
            negative_prompt: Override negative prompt
            on_queue_update: Custom queue update callback

        Returns:
            Path to generated image, or None on failure
        """
        print(f"\n{'='*70}")
        print(f"FRAME: {output_name}")
        print(f"{'='*70}")

        # Upload references
        ref_urls = self.upload_images(refs or [])

        # Build full prompt with style DNA
        style_prompt = self.config.build_style_prompt(lighting_mode)
        full_prompt = f"{prompt}. {style_prompt}"

        print(f"\nPrompt: {prompt[:100]}...")
        print(f"References: {len(ref_urls)}")

        # Build request
        defaults = self.config.get_model_defaults("nano_banana")
        request = {
            "prompt": full_prompt,
            "aspect_ratio": defaults.get("aspect_ratio", "16:9"),
            "resolution": defaults.get("resolution", "2K"),
            "num_images": 1,
            "output_format": defaults.get("output_format", "png"),
            "negative_prompt": negative_prompt or self.config.build_negative_prompt(),
        }

        if ref_urls:
            request["image_urls"] = ref_urls

        # Get endpoint
        modality = "edit" if ref_urls else "text_to_image"
        endpoint = self.config.get_model_endpoint("nano_banana", modality)
        print(f"\nEndpoint: {endpoint}")

        try:
            result = fal_client.subscribe(
                endpoint,
                arguments=request,
                with_logs=True,
                on_queue_update=on_queue_update or self._on_queue_update,
            )

            # Extract image URL
            image_url = None
            if result and "images" in result and len(result["images"]) > 0:
                image_url = result["images"][0].get("url")

            if image_url:
                print(f"\n✓ Generated: {image_url}")

                # Download and save
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = self.output_dir / f"{output_name}_{timestamp}.png"

                if self._download_file(image_url, output_path):
                    print(f"✓ Saved: {output_path}")

                    # Save metadata
                    self._save_metadata(output_path, {
                        "prompt": prompt,
                        "full_prompt": full_prompt,
                        "references": [str(r) for r in (refs or [])],
                        "endpoint": endpoint,
                        "timestamp": datetime.now().isoformat(),
                        "image_url": image_url,
                    })

                    return output_path
                else:
                    print(f"✗ Failed to download")
                    return None
            else:
                print("✗ No image in result")
                return None

        except Exception as e:
            print(f"✗ Error: {e}")
            import traceback
            traceback.print_exc()
            return None

    def generate_video_clip(
        self,
        start_frame: Path,
        prompts: List[Dict[str, Any]],
        characters: List[Dict[str, str]],
        scene_refs: List[Path] = None,
        output_name: str = "clip",
        negative_prompt: str = None,
        on_queue_update: Callable = None,
    ) -> Optional[Path]:
        """
        Generate a video clip using Kling 3.0.

        Args:
            start_frame: Path to start frame image
            prompts: List of {"prompt": str, "duration": int} dicts
            characters: List of {"id": str, "element": str} dicts
            scene_refs: List of scene reference frame paths (establishing shots, etc.)
            output_name: Base name for output file
            negative_prompt: Override negative prompt
            on_queue_update: Custom queue update callback

        Returns:
            Path to generated video, or None on failure
        """
        print(f"\n{'='*70}")
        print(f"VIDEO CLIP: {output_name}")
        print(f"{'='*70}")

        # Upload start frame
        start_url = self.upload_image(start_frame)

        # Upload scene reference images
        scene_ref_urls = []
        if scene_refs:
            print(f"  Scene references: {len(scene_refs)}")
            for ref in scene_refs:
                if ref and ref.exists():
                    scene_ref_urls.append(self.upload_image(ref))

        # Build elements from character list
        elements = []
        for char in characters:
            char_id = char["id"]
            identity = self.config.get_identity_sheet(char_id)
            hero = self.config.get_hero_shot(char_id, "entrance")

            if identity:
                element = {
                    "frontal_image_url": self.upload_image(identity),
                }
                # Build reference_image_urls: hero shot + scene refs
                ref_urls = []
                if hero:
                    ref_urls.append(self.upload_image(hero))
                ref_urls.extend(scene_ref_urls)
                if ref_urls:
                    element["reference_image_urls"] = ref_urls
                elements.append(element)
                print(f"  Element: {char['element']} = {char_id} (refs: {len(ref_urls)})")

        # Build multi-prompt
        multi_prompt = []
        for p in prompts:
            prompt_text = p["prompt"]
            # Add "CUT to:" prefix if not present and cut_prefix is true (default)
            if p.get("cut_prefix", True) and not prompt_text.strip().lower().startswith("cut to:"):
                prompt_text = f"CUT to: {prompt_text}"
            multi_prompt.append({
                "prompt": prompt_text,
                "duration": str(p["duration"]),
            })

        total_duration = sum(int(p["duration"]) for p in prompts)

        print(f"\nStart frame: {start_frame.name}")
        print(f"Multi-prompt ({len(prompts)} cuts):")
        for i, p in enumerate(multi_prompt):
            print(f"  [{i+1}] ({p['duration']}s) {p['prompt'][:60]}...")

        # Build request
        defaults = self.config.get_model_defaults("kling")
        request = {
            "start_image_url": start_url,
            "multi_prompt": multi_prompt,
            "duration": str(total_duration),
            "aspect_ratio": defaults.get("aspect_ratio", "16:9"),
            "generate_audio": defaults.get("generate_audio", True),
            "negative_prompt": negative_prompt or self.config.build_negative_prompt(for_video=True),
        }

        if elements:
            request["elements"] = elements

        # Cost estimate
        cost_per_sec = self.config.models.get("kling", {}).get("cost_per_second", 0.336)
        estimated_cost = total_duration * cost_per_sec
        print(f"\nDuration: {total_duration}s | Estimated cost: ${estimated_cost:.2f}")

        # Get endpoint
        endpoint = self.config.get_model_endpoint("kling", "image_to_video")
        print(f"Endpoint: {endpoint}")

        try:
            result = fal_client.subscribe(
                endpoint,
                arguments=request,
                with_logs=True,
                on_queue_update=on_queue_update or self._on_queue_update,
            )

            # Extract video URL
            video_url = None
            if result and "video" in result:
                video_url = result["video"].get("url")

            if video_url:
                print(f"\n✓ Generated: {video_url}")

                # Download and save
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = self.output_dir / f"{output_name}_{timestamp}.mp4"

                if self._download_file(video_url, output_path):
                    print(f"✓ Saved: {output_path}")

                    # Save metadata
                    self._save_metadata(output_path, {
                        "start_frame": str(start_frame),
                        "prompts": prompts,
                        "characters": characters,
                        "duration": total_duration,
                        "endpoint": endpoint,
                        "timestamp": datetime.now().isoformat(),
                        "video_url": video_url,
                    })

                    return output_path
                else:
                    print(f"✗ Failed to download")
                    return None
            else:
                print("✗ No video in result")
                return None

        except Exception as e:
            print(f"✗ Error: {e}")
            import traceback
            traceback.print_exc()
            return None


def extract_last_frame(video_path: Path, output_path: Path) -> Optional[Path]:
    """
    Extract the last frame from a video using ffmpeg.

    Args:
        video_path: Path to video file
        output_path: Path for output image

    Returns:
        Path to extracted frame, or None on failure
    """
    import subprocess

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        "ffmpeg", "-y",
        "-sseof", "-1",
        "-i", str(video_path),
        "-update", "1",
        "-q:v", "2",
        str(output_path)
    ]

    print(f"\nExtracting last frame from {video_path.name}...")
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0 and output_path.exists():
        print(f"✓ Extracted: {output_path}")
        return output_path
    else:
        print(f"✗ Failed to extract frame")
        if result.stderr:
            print(result.stderr[:500])
        return None


def concatenate_clips(clips: List[Path], output_path: Path) -> Optional[Path]:
    """
    Concatenate video clips using ffmpeg.

    Args:
        clips: List of clip paths in order
        output_path: Path for output video

    Returns:
        Path to concatenated video, or None on failure
    """
    import subprocess

    if not clips:
        print("No clips to concatenate")
        return None

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Write concat file
    concat_file = output_path.parent / "concat_list.txt"
    with open(concat_file, "w") as f:
        for clip in clips:
            f.write(f"file '{clip}'\n")

    cmd = [
        "ffmpeg", "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", str(concat_file),
        "-c", "copy",
        str(output_path)
    ]

    print(f"\nConcatenating {len(clips)} clips...")
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0 and output_path.exists():
        print(f"✓ Assembled: {output_path}")
        return output_path
    else:
        print(f"✗ Assembly failed")
        if result.stderr:
            print(result.stderr[:500])
        return None
