"""
ComfyUI backend for video and image generation via local GPU service.

Connects to a local ComfyUI service that exposes workflow endpoints.
Supports:
  - ltx2-3: LTX-2.3 22B with optional reference audio, first/last frame (recommended)
  - ltx2: LTX-2 19B consolidated (text-to-video, image-to-video, optional audio)
  - ltx2-i2v: LTX-2 19B image-to-video (deprecated, use ltx2)
  - flux2-t2i: Flux 2 Dev text-to-image
  - flux2-i2i: Flux 2 Dev image-to-image (1 reference)
  - flux2-dev-multiref: Flux 2 Dev multi-reference (1-4 references)
  - flux2-klein-t2i: Flux 2 Klein text-to-image (fast draft mode)
  - flux2-klein-edit: Flux 2 Klein image edit (fast draft, 1 reference)
  - flux2-klein-multiref: Flux 2 Klein multi-reference (fast draft, 1-4 references)
"""

import re
import time
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable

import requests

from .base import VideoBackend, ImageBackend, VideoResult, ImageResult


class ComfyUIVideoBackend(VideoBackend):
    """LTX video generation via local ComfyUI service.

    Supports multiple workflows with automatic routing:
      - ltx2-3: LTX-2.3 22B — preferred for audio-driven generation (reference_audio)
      - ltx2: LTX-2 19B consolidated — fallback for non-audio generation
      - ltx2-i2v: LTX-2 19B image-to-video (deprecated)

    When reference_audio is provided, automatically routes to ltx2-3.
    """

    name = "comfyui"
    supports_elements = False
    supports_multi_prompt = False
    supports_audio = True
    cost_per_second = 0.0

    # Frame count limits (LTX-2 at 25fps)
    MIN_FRAMES = 25    # ~1s
    MAX_FRAMES = 501   # ~20s — validated on local hardware (2026-03-02)

    # Workflows that use duration (seconds) instead of frame_count
    DURATION_WORKFLOWS = {"ltx2-3", "ltx2-3-fast"}

    # Workflow to route to when reference_audio is provided
    AUDIO_WORKFLOW = "ltx2-3"

    def __init__(
        self,
        base_url: str = "http://192.168.1.181:8100",
        workflow: str = "ltx2-3",
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
        reference_audio: Optional[Path] = None,
        on_queue_update: Optional[Callable] = None,
        **backend_kwargs,
    ) -> VideoResult:
        """
        Generate video via local ComfyUI service.

        Sends multipart form data with the start frame image and text parameters.
        Response is raw MP4 bytes (synchronous, no queue).

        When reference_audio is provided, routes to the ltx2-3 workflow which
        supports voice-cloned speech generation via the [VISUAL]/[SPEECH]/[SOUNDS]
        prompt format.

        Additional backend_kwargs for ltx2-3:
            last_frame: Path to last frame image for guidance
            static_camera: float (0-1) for camera stability
            img_compression: int for compression level
        """
        start_frame = Path(start_frame)
        if not start_frame.exists():
            raise FileNotFoundError(f"Start frame not found: {start_frame}")

        if reference_audio:
            reference_audio = Path(reference_audio)
            if not reference_audio.exists():
                raise FileNotFoundError(f"Reference audio not found: {reference_audio}")

        # Optional pre-generated speech audio (drives lip-sync and exact duration)
        driven_audio = backend_kwargs.get("audio")
        if driven_audio:
            driven_audio = Path(driven_audio)
            if not driven_audio.exists():
                raise FileNotFoundError(f"Driven audio not found: {driven_audio}")

        # Route to audio-capable workflow when audio of either kind is provided
        active_workflow = self.workflow
        if (reference_audio or driven_audio) and active_workflow not in self.DURATION_WORKFLOWS:
            active_workflow = self.AUDIO_WORKFLOW
            print(f"  Routing to {active_workflow} (audio provided)")

        uses_duration = active_workflow in self.DURATION_WORKFLOWS

        if uses_duration:
            # LTX-2.3 uses duration in seconds directly
            duration_int = max(2, min(int(duration_seconds), 20))
            print(f"  ComfyUI: {active_workflow} | {duration_int}s duration")
        else:
            # Legacy workflows use frame_count
            frame_count = self._duration_to_frame_count(duration_seconds)
            print(f"  ComfyUI: {active_workflow} | {frame_count} frames ({duration_seconds:.0f}s @ {self.fps}fps)")

        # For ltx2-3, don't simplify the prompt (it uses [VISUAL]/[SPEECH]/[SOUNDS] format)
        if uses_duration:
            clean_prompt = prompt
        else:
            clean_prompt = self.simplify_prompt(prompt)

        print(f"  Prompt: {clean_prompt[:120]}...")
        if reference_audio:
            print(f"  Reference audio: {reference_audio.name}")
        if driven_audio:
            print(f"  Driven audio: {driven_audio.name}")

        url = f"{self.base_url}/workflows/{active_workflow}"

        # Build multipart form data
        data = {"prompt": clean_prompt}

        if uses_duration:
            data["duration"] = str(duration_int)
        else:
            data["frame_count"] = str(frame_count)

        if negative_prompt:
            data["negative_prompt"] = negative_prompt
        if seed is not None:
            data["seed"] = str(seed)

        # ltx2-3 specific params
        if uses_duration:
            if "static_camera" in backend_kwargs:
                data["static_camera"] = str(backend_kwargs["static_camera"])
            if "img_compression" in backend_kwargs:
                data["img_compression"] = str(backend_kwargs["img_compression"])

        # Build files dict — open all file handles together
        file_handles = []
        files = []
        try:
            # Start frame → first_frame (ltx2-3) or image (legacy)
            img_fh = open(start_frame, "rb")
            file_handles.append(img_fh)
            if uses_duration:
                files.append(("first_frame", (start_frame.name, img_fh, "image/png")))
            else:
                files.append(("image", (start_frame.name, img_fh, "image/png")))

            # Reference audio for voice cloning (ltx2-3 only)
            if reference_audio:
                ref_fh = open(reference_audio, "rb")
                file_handles.append(ref_fh)
                ref_mime = "audio/wav" if reference_audio.suffix.lower() == ".wav" else "audio/flac"
                files.append(("reference_audio", (reference_audio.name, ref_fh, ref_mime)))

            # Driven audio (pre-generated speech) — drives video duration & lip sync
            if driven_audio:
                drv_fh = open(driven_audio, "rb")
                file_handles.append(drv_fh)
                drv_mime = "audio/wav" if driven_audio.suffix.lower() == ".wav" else "audio/flac"
                files.append(("audio", (driven_audio.name, drv_fh, drv_mime)))

            # Last frame (ltx2-3 only)
            last_frame = backend_kwargs.get("last_frame")
            if last_frame and uses_duration:
                last_frame = Path(last_frame)
                if last_frame.exists():
                    lf_fh = open(last_frame, "rb")
                    file_handles.append(lf_fh)
                    files.append(("last_frame", (last_frame.name, lf_fh, "image/png")))

            print(f"  Sending to {url} (timeout: {self.timeout}s)...")
            response = requests.post(
                url,
                data=data,
                files=files,
                timeout=self.timeout,
            )
        finally:
            for fh in file_handles:
                fh.close()

        # Build metadata for results
        metadata = {
            "workflow": active_workflow,
            "fps": self.fps,
            "prompt": clean_prompt,
            "base_url": self.base_url,
        }
        if uses_duration:
            metadata["duration"] = duration_int
        else:
            metadata["frame_count"] = frame_count
        if reference_audio:
            metadata["reference_audio"] = str(reference_audio)
        if driven_audio:
            metadata["audio"] = str(driven_audio)

        # Handle synchronous response
        if response.status_code == 200:
            content_type = response.headers.get("content-type", "")
            if "video" in content_type or len(response.content) > 10000:
                print(f"  -> {len(response.content)} bytes received")
                return VideoResult(video_bytes=response.content, metadata=metadata)

        # Handle async job (HTTP 200 with JSON or HTTP 202)
        if response.status_code in (200, 202):
            try:
                job_data = response.json()
                job_id = job_data.get("job_id")
            except Exception:
                job_id = None

            if job_id:
                print(f"  -> Job queued: {job_id}, polling...")
                return self._poll_job(job_id, metadata)

        # Unexpected response
        content_type = response.headers.get("content-type", "")
        if response.status_code == 200:
            print(f"  -> Unexpected response content-type: {content_type}")
            print(f"  -> Body: {response.text[:200]}")
            return VideoResult(metadata={**metadata, "error": "unexpected_content_type"})
        else:
            print(f"  -> HTTP {response.status_code}: {response.text[:200]}")
            return VideoResult(metadata={**metadata, "error": f"http_{response.status_code}"})

    def _poll_job(self, job_id: str, metadata: dict, poll_interval: int = 5) -> VideoResult:
        """Poll an async job until completion, then download the result."""
        elapsed = 0
        while elapsed < self.timeout:
            time.sleep(poll_interval)
            elapsed += poll_interval

            try:
                poll_resp = requests.get(
                    f"{self.base_url}/jobs/{job_id}", timeout=30
                )
            except Exception:
                continue

            if poll_resp.status_code != 200:
                continue

            try:
                status_data = poll_resp.json()
                status = status_data.get("status", "")
            except Exception:
                # Might be raw video bytes
                ct = poll_resp.headers.get("content-type", "")
                if "video" in ct and len(poll_resp.content) > 10000:
                    print(f"  -> {len(poll_resp.content)} bytes received ({elapsed}s)")
                    return VideoResult(video_bytes=poll_resp.content, metadata=metadata)
                continue

            if status == "completed":
                # Download result from /jobs/{id}/result
                try:
                    result_resp = requests.get(
                        f"{self.base_url}/jobs/{job_id}/result", timeout=120
                    )
                    if result_resp.status_code == 200 and len(result_resp.content) > 1000:
                        print(f"  -> {len(result_resp.content)} bytes received ({elapsed}s)")
                        metadata["job_id"] = job_id
                        return VideoResult(video_bytes=result_resp.content, metadata=metadata)
                    else:
                        print(f"  -> Job completed but result download failed: HTTP {result_resp.status_code}")
                        return VideoResult(metadata={**metadata, "error": "result_download_failed"})
                except Exception as e:
                    print(f"  -> Result download error: {e}")
                    return VideoResult(metadata={**metadata, "error": "result_download_error"})

            elif status in ("failed", "error"):
                error_msg = status_data.get("error", "unknown")
                print(f"  -> Job failed: {error_msg}")
                return VideoResult(metadata={**metadata, "error": f"job_failed: {error_msg}"})

            elif elapsed % 30 == 0:
                pos = status_data.get("position", "?")
                print(f"    ... waiting ({elapsed}s, status={status}, position={pos})")

        print(f"  -> Timed out after {self.timeout}s")
        return VideoResult(metadata={**metadata, "error": "timeout"})

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
