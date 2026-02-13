"""
ComfyUI backend for video and image generation via local GPU service.

Connects to a local ComfyUI service that exposes workflow endpoints.
Supports:
  - ltx2-i2v: LTX-2 19B image-to-video
  - flux2-t2i: Flux 2 Dev text-to-image
  - flux2-i2i: Flux 2 Dev image-to-image (1 reference)
  - flux2-dev-multiref: Flux 2 Dev multi-reference (1-4 references)
  - flux2-klein-t2i: Flux 2 Klein text-to-image (fast draft mode)
  - flux2-klein-edit: Flux 2 Klein image edit (fast draft, 1 reference)
  - flux2-klein-multiref: Flux 2 Klein multi-reference (fast draft, 1-4 references)
"""

import re
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable

import requests

from .base import VideoBackend, ImageBackend, VideoResult, ImageResult


class ComfyUIVideoBackend(VideoBackend):
    """LTX-2 video generation via local ComfyUI service."""

    name = "comfyui"
    supports_elements = False
    supports_multi_prompt = False
    supports_audio = False
    cost_per_second = 0.0

    # Frame count limits (LTX-2 memory constraints)
    MIN_FRAMES = 25    # ~1s at 25fps
    MAX_FRAMES = 321   # ~12.8s at 25fps

    def __init__(
        self,
        base_url: str = "http://192.168.1.181:8100",
        workflow: str = "ltx2-i2v",
        fps: int = 25,
        timeout: int = 600,
    ):
        self.base_url = base_url.rstrip("/")
        self.workflow = workflow
        self.fps = fps
        self.timeout = timeout

    def _duration_to_frame_count(self, duration_seconds: float) -> int:
        """Convert duration in seconds to frame_count for LTX-2."""
        raw = round(duration_seconds * self.fps) + 1
        return max(self.MIN_FRAMES, min(raw, self.MAX_FRAMES))

    @staticmethod
    def simplify_prompt(prompt: str) -> str:
        """
        Simplify a Kling-style prompt for LTX-2.

        - Strips @ElementN tags
        - Removes "CUT to:" prefixes
        - Strips timecode markers like [0:00-0:03]
        """
        # Strip @ElementN references
        text = re.sub(r'@Element\d+', '', prompt)
        # Strip timecode markers [0:00-0:03]
        text = re.sub(r'\[\d+:\d+[-–]\d+:\d+\]', '', text)
        # Strip "CUT to:" prefixes
        text = re.sub(r'(?i)CUT\s+to:\s*', '', text)
        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        return text

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
        Generate video via local ComfyUI service.

        Sends multipart form data with the start frame image and text parameters.
        Response is raw MP4 bytes (synchronous, no queue).

        Unsupported Kling features (elements, multi_prompt, generate_audio,
        shot_type) are silently ignored — the Generator logs warnings.
        """
        start_frame = Path(start_frame)
        if not start_frame.exists():
            raise FileNotFoundError(f"Start frame not found: {start_frame}")

        # Simplify prompt for LTX-2
        clean_prompt = self.simplify_prompt(prompt)
        frame_count = self._duration_to_frame_count(duration_seconds)

        print(f"  ComfyUI: {self.workflow} | {frame_count} frames ({duration_seconds:.0f}s @ {self.fps}fps)")
        print(f"  Prompt: {clean_prompt[:100]}...")

        url = f"{self.base_url}/workflows/{self.workflow}"

        # Build multipart form data
        data = {
            "prompt": clean_prompt,
            "frame_count": str(frame_count),
        }
        if negative_prompt:
            data["negative_prompt"] = negative_prompt
        if seed is not None:
            data["seed"] = str(seed)

        with open(start_frame, "rb") as img_file:
            files = {"image": (start_frame.name, img_file, "image/png")}

            print(f"  Sending to {url} (timeout: {self.timeout}s)...")
            response = requests.post(
                url,
                data=data,
                files=files,
                timeout=self.timeout,
            )

        if response.status_code == 200:
            content_type = response.headers.get("content-type", "")
            if "video" in content_type or len(response.content) > 10000:
                print(f"  -> {len(response.content)} bytes received")
                return VideoResult(
                    video_bytes=response.content,
                    metadata={
                        "workflow": self.workflow,
                        "frame_count": frame_count,
                        "fps": self.fps,
                        "prompt": clean_prompt,
                        "base_url": self.base_url,
                    },
                )
            else:
                print(f"  -> Unexpected response content-type: {content_type}")
                print(f"  -> Body: {response.text[:200]}")
                return VideoResult(metadata={"error": "unexpected_content_type"})
        else:
            print(f"  -> HTTP {response.status_code}: {response.text[:200]}")
            return VideoResult(metadata={"error": f"http_{response.status_code}"})

    def health_check(self) -> bool:
        """Check if the ComfyUI service is reachable."""
        try:
            response = requests.get(f"{self.base_url}/workflows", timeout=5)
            return response.status_code < 500
        except requests.ConnectionError:
            return False
        except requests.Timeout:
            return False


class ComfyUIImageBackend(ImageBackend):
    """Flux 2 image generation via local ComfyUI service.

    Supports seven workflows with automatic routing:
      - flux2-t2i: Flux 2 Dev text-to-image (0 refs)
      - flux2-i2i: Flux 2 Dev image-to-image (1 ref)
      - flux2-dev-multiref: Flux 2 Dev multi-reference (2-4 refs)
      - flux2-klein-t2i: Flux 2 Klein text-to-image (0 refs, fast draft)
      - flux2-klein-edit: Flux 2 Klein image edit (1 ref, fast draft)
      - flux2-klein-multiref: Flux 2 Klein multi-reference (2-4 refs, fast draft)

    Automatic workflow routing based on reference count:
      0 refs → t2i, 1 ref → i2i/edit, 2-4 refs → multiref
    """

    name = "comfyui"
    cost_per_image = 0.0

    # Aspect ratio presets -> (width, height)
    ASPECT_RATIOS = {
        "16:9": (1008, 576),
        "9:16": (576, 1008),
        "4:3": (1008, 768),
        "3:4": (768, 1008),
        "1:1": (1024, 1024),
        "square_hd": (1024, 1024),
        "landscape_16_9": (1008, 576),
        "portrait_4_3": (768, 1008),
    }

    # Map t2i workflow -> matching i2i workflow (1 reference)
    I2I_WORKFLOW_MAP = {
        "flux2-t2i": "flux2-i2i",
        "flux2-klein-t2i": "flux2-klein-edit",
    }

    # Map t2i workflow -> matching multiref workflow (2-4 references)
    MULTIREF_WORKFLOW_MAP = {
        "flux2-t2i": "flux2-dev-multiref",
        "flux2-klein-t2i": "flux2-klein-multiref",
    }

    # Workflows that support negative_prompt and cfg
    KLEIN_WORKFLOWS = {"flux2-klein-t2i", "flux2-klein-edit", "flux2-klein-multiref"}

    # Workflows that support guidance (Dev multiref only)
    GUIDANCE_WORKFLOWS = {"flux2-dev-multiref"}

    def __init__(
        self,
        base_url: str = "http://192.168.1.181:8100",
        workflow: str = "flux2-klein-t2i",
        timeout: int = 300,
    ):
        self.base_url = base_url.rstrip("/")
        self.workflow = workflow
        self.timeout = timeout

    def _resolve_size(self, aspect_ratio: str, width: int = None, height: int = None) -> tuple:
        """Resolve aspect ratio string to (width, height) tuple."""
        if width and height:
            return (width, height)
        return self.ASPECT_RATIOS.get(aspect_ratio, (1008, 1024))

    def _is_klein(self, workflow: str) -> bool:
        """Check if a workflow is a Klein (fast) variant."""
        return workflow in self.KLEIN_WORKFLOWS

    def _get_i2i_workflow(self) -> Optional[str]:
        """Get the image-to-image workflow matching the current t2i workflow."""
        return self.I2I_WORKFLOW_MAP.get(self.workflow)

    def _get_multiref_workflow(self) -> Optional[str]:
        """Get the multi-reference workflow matching the current t2i workflow."""
        return self.MULTIREF_WORKFLOW_MAP.get(self.workflow)

    def upload_image(self, filepath: Path) -> str:
        """ComfyUI doesn't need URL-based uploads — return local path as-is."""
        filepath = Path(filepath)
        if not filepath.exists():
            raise FileNotFoundError(f"Image not found: {filepath}")
        return str(filepath)

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
        Generate image via Flux 2 on local ComfyUI.

        Automatically selects the best workflow based on reference count:
        - 0 references → t2i (flux2-t2i or flux2-klein-t2i)
        - 1 reference  → i2i (flux2-i2i or flux2-klein-edit)
        - 2-4 refs     → multiref (flux2-dev-multiref or flux2-klein-multiref)

        Backend-specific kwargs:
            width: Override width in pixels
            height: Override height in pixels
            steps: Number of inference steps (default 20, Klein default 12)
            cfg: Guidance scale (Klein only, default 3.5)
            guidance: Guidance scale (Dev multiref only, default 4.0)
        """
        # Validate and collect reference paths
        ref_paths = []
        if reference_urls:
            for ref_url in reference_urls[:4]:  # Max 4 references
                p = Path(ref_url)
                if p.exists():
                    ref_paths.append(p)
                else:
                    print(f"  Warning: Reference image not found ({p}), skipping")
            if len(reference_urls) > 4:
                print(f"  Note: Max 4 references supported — {len(reference_urls) - 4} extra refs ignored")

        # Route: 0 refs → t2i, 1 ref → i2i, 2+ refs → multiref
        mode = "t2i"
        active_workflow = self.workflow

        if len(ref_paths) >= 2:
            multiref_workflow = self._get_multiref_workflow()
            if multiref_workflow:
                mode = "multiref"
                active_workflow = multiref_workflow
            else:
                # Fallback: use i2i with first ref if no multiref available
                i2i_workflow = self._get_i2i_workflow()
                if i2i_workflow:
                    mode = "i2i"
                    active_workflow = i2i_workflow
                    print(f"  Note: No multiref workflow for {self.workflow} — using i2i with first ref only")
                else:
                    print(f"  Note: No i2i/multiref workflows for {self.workflow} — {len(ref_paths)} refs ignored")
        elif len(ref_paths) == 1:
            i2i_workflow = self._get_i2i_workflow()
            if i2i_workflow:
                mode = "i2i"
                active_workflow = i2i_workflow
            else:
                print(f"  Note: No i2i workflow for {self.workflow} — 1 ref ignored")

        is_klein = self._is_klein(active_workflow)
        uses_guidance = active_workflow in self.GUIDANCE_WORKFLOWS

        width, height = self._resolve_size(
            aspect_ratio,
            backend_kwargs.get("width"),
            backend_kwargs.get("height"),
        )
        default_steps = 12 if is_klein else 20
        steps = backend_kwargs.get("steps", default_steps)
        cfg = backend_kwargs.get("cfg", 3.5) if is_klein else None
        guidance = backend_kwargs.get("guidance", 4.0) if uses_guidance else None

        mode_label = "Klein" if is_klein else "Dev"
        ref_label = f" ({mode}, {len(ref_paths)} refs)" if mode != "t2i" else ""
        print(f"  ComfyUI: {active_workflow} [Flux-2 {mode_label}{ref_label}] | {width}x{height} | {steps} steps")
        print(f"  Prompt: {prompt[:120]}...")

        url = f"{self.base_url}/workflows/{active_workflow}"

        # Build form data
        data = {"prompt": prompt, "steps": str(steps)}
        if seed is not None:
            data["seed"] = str(seed)

        # t2i workflows need width/height; i2i/multiref infer from input images
        if mode == "t2i":
            data["width"] = str(width)
            data["height"] = str(height)

        # Klein-specific params (cfg, negative_prompt)
        if is_klein:
            if negative_prompt:
                data["negative_prompt"] = negative_prompt
            if cfg is not None:
                data["cfg"] = str(cfg)

        # Dev multiref guidance param
        if guidance is not None:
            data["guidance"] = str(guidance)

        # Send request based on mode
        print(f"  Sending to {url}...")
        if mode == "multiref":
            # Open all reference images as image1, image2, ...
            file_handles = []
            files = []
            try:
                for i, rp in enumerate(ref_paths, start=1):
                    fh = open(rp, "rb")
                    file_handles.append(fh)
                    files.append((f"image{i}", (rp.name, fh, "image/png")))
                response = requests.post(url, data=data, files=files, timeout=self.timeout)
            finally:
                for fh in file_handles:
                    fh.close()
        elif mode == "i2i":
            with open(ref_paths[0], "rb") as img_file:
                files = {"image": (ref_paths[0].name, img_file, "image/png")}
                response = requests.post(url, data=data, files=files, timeout=self.timeout)
        else:
            response = requests.post(url, data=data, timeout=self.timeout)

        if response.status_code == 200:
            content_type = response.headers.get("content-type", "")
            if "image" in content_type or len(response.content) > 5000:
                print(f"  -> {len(response.content)} bytes received")
                metadata = {
                    "workflow": active_workflow,
                    "mode": "klein" if is_klein else "dev",
                    "ref_mode": mode,
                    "width": width,
                    "height": height,
                    "steps": steps,
                    "seed": seed,
                    "prompt": prompt,
                    "base_url": self.base_url,
                }
                if ref_paths:
                    metadata["reference_images"] = [str(p) for p in ref_paths]
                if cfg is not None:
                    metadata["cfg"] = cfg
                if guidance is not None:
                    metadata["guidance"] = guidance
                if negative_prompt:
                    metadata["negative_prompt"] = negative_prompt
                return ImageResult(image_bytes=response.content, metadata=metadata)
            else:
                print(f"  -> Unexpected response: {content_type}")
                print(f"  -> Body: {response.text[:200]}")
                return ImageResult(metadata={"error": "unexpected_content_type"})
        else:
            print(f"  -> HTTP {response.status_code}: {response.text[:200]}")
            return ImageResult(metadata={"error": f"http_{response.status_code}"})

    def health_check(self) -> bool:
        try:
            response = requests.get(f"{self.base_url}/workflows", timeout=5)
            return response.status_code < 500
        except (requests.ConnectionError, requests.Timeout):
            return False
