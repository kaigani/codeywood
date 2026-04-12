"""
Backend-neutral generator for visual production.

Refactored from FalGenerator — keeps all orchestration logic
(preflight, metadata, prompt assembly, element building) but
delegates API calls to a pluggable backend.
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Callable

import requests

from .config import ProjectConfig
from .backends import (
    create_video_backend,
    create_image_backend,
    get_video_backend_name,
    get_image_backend_name,
    VideoResult,
    ImageResult,
)


class Generator:
    """High-level generation wrapper with pluggable backends."""

    def __init__(self, config, output_dir: Path, preflight: bool = False):
        self.config = config
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.preflight = preflight

        # Create backends (None in preflight mode)
        self._video_backend = create_video_backend(config, preflight=preflight)
        try:
            self._image_backend = create_image_backend(config, preflight=preflight)
        except (ImportError, EnvironmentError):
            # Image backend may not be available (e.g., video-only scripts)
            self._image_backend = None

        # Track uploaded URLs to avoid re-uploading (fal backend)
        self._upload_cache: Dict[str, str] = {}

    @property
    def video_backend_name(self) -> str:
        if self._video_backend:
            return self._video_backend.name
        return get_video_backend_name(self.config)

    @property
    def image_backend_name(self) -> str:
        if self._image_backend:
            return self._image_backend.name
        return get_image_backend_name(self.config)

    # ─── File helpers ───────────────────────────────────────────────

    def upload_image(self, filepath: Path) -> str:
        """Upload a local image and return a URL. Uses the image backend."""
        filepath = Path(filepath)
        cache_key = str(filepath.resolve())

        if cache_key in self._upload_cache:
            return self._upload_cache[cache_key]

        if not filepath.exists():
            raise FileNotFoundError(f"Image not found: {filepath}")

        # Delegate to whichever backend supports upload
        if self._image_backend:
            url = self._image_backend.upload_image(filepath)
        elif self._video_backend and hasattr(self._video_backend, 'upload_image'):
            url = self._video_backend.upload_image(filepath)
        else:
            raise RuntimeError("No backend available for image upload")

        self._upload_cache[cache_key] = url
        return url

    def upload_images(self, filepaths: List[Path]) -> List[str]:
        """Upload multiple images and return URLs."""
        urls = []
        for fp in filepaths:
            if fp and Path(fp).exists():
                urls.append(self.upload_image(fp))
        return urls

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

    def _resolve_url(self, path: Path, preflight: bool) -> str:
        """Resolve a file path to a URL. In preflight mode, returns local:// path."""
        if preflight:
            return f"local://{path}"
        return self.upload_image(path)

    def _save_video_result(self, result: VideoResult, output_path: Path) -> bool:
        """Save a VideoResult to disk, handling both bytes and URL responses."""
        if result.video_bytes:
            with open(output_path, "wb") as f:
                f.write(result.video_bytes)
            return True
        elif result.video_url:
            return self._download_file(result.video_url, output_path)
        return False

    def _save_image_result(self, result: ImageResult, output_path: Path) -> bool:
        """Save an ImageResult to disk, handling both bytes and URL responses."""
        if result.image_bytes:
            with open(output_path, "wb") as f:
                f.write(result.image_bytes)
            return True
        elif result.image_url:
            return self._download_file(result.image_url, output_path)
        return False

    # ─── Prompt helpers ─────────────────────────────────────────────

    @staticmethod
    def _strip_element_tags(text: str) -> str:
        """Remove @ElementN tags from prompt text."""
        return re.sub(r'@Element\d+', '', text).strip()

    @staticmethod
    def _simplify_multi_prompts(prompts: List[Dict[str, Any]]) -> str:
        """Concatenate multi_prompt entries into a single prompt string."""
        parts = []
        for p in prompts:
            text = p.get("prompt", "")
            # Strip "CUT to:" prefixes
            text = re.sub(r'(?i)^CUT\s+to:\s*', '', text.strip())
            if text:
                parts.append(text)
        return ". ".join(parts)

    # ─── Preflight ──────────────────────────────────────────────────

    def _write_preflight(
        self,
        request: Dict[str, Any],
        output_name: str,
        endpoint: str,
        total_duration: int,
        estimated_cost: float,
        files_info: Dict[str, Any],
        element_labels: List[str],
        prompt_max_chars: int,
        prompt_mode: str = "multi_prompt",
        backend_name: str = "fal",
    ) -> Path:
        """Write preflight inspection JSON and return its path."""
        # Annotate prompts based on mode
        if prompt_mode == "narrative":
            prompt_text = request.get("prompt", "")
            char_count = len(prompt_text)
            NARRATIVE_MAX = 2500
            any_over = char_count > NARRATIVE_MAX
            char_counts = [char_count]
        else:
            annotated_prompts = []
            char_counts = []
            any_over = False
            for p in request.get("multi_prompt", []):
                count = len(p["prompt"])
                over = count > prompt_max_chars
                if over:
                    any_over = True
                char_counts.append(count)
                annotated_prompts.append({
                    **p,
                    "char_count": count,
                    "over_limit": over,
                })

        # Annotate elements with labels
        annotated_elements = []
        for i, elem in enumerate(request.get("elements", [])):
            label = element_labels[i] if i < len(element_labels) else f"element_{i}"
            annotated_elements.append({
                "label": label,
                **elem,
                "frontal_exists": not elem["frontal_image_url"].startswith("local://") or Path(elem["frontal_image_url"].replace("local://", "")).exists(),
                "all_refs_exist": all(
                    not u.startswith("local://") or Path(u.replace("local://", "")).exists()
                    for u in elem.get("reference_image_urls", [])
                ),
            })

        api_request = {
            "endpoint": endpoint,
            "backend": backend_name,
            "start_image_url": request.get("start_image_url", request.get("start_frame")),
            "aspect_ratio": request.get("aspect_ratio"),
            "generate_audio": request.get("generate_audio"),
            "negative_prompt": request.get("negative_prompt"),
            "elements": annotated_elements,
        }

        analysis = {
            "total_duration_s": total_duration,
            "estimated_cost_usd": round(estimated_cost, 2),
            "prompt_mode": prompt_mode,
            "any_over_limit": any_over,
            "num_elements": len(annotated_elements),
            "backend": backend_name,
        }

        if prompt_mode == "narrative":
            api_request["prompt"] = request.get("prompt")
            api_request["duration"] = request.get("duration")
            analysis["prompt_char_count"] = char_counts[0]
            analysis["max_allowed_chars"] = 2500
        else:
            api_request["multi_prompt"] = annotated_prompts
            api_request["shot_type"] = request.get("shot_type")
            analysis["num_prompts"] = len(annotated_prompts)
            analysis["prompt_char_counts"] = char_counts
            analysis["max_allowed_chars"] = prompt_max_chars

        # ComfyUI-specific preflight info
        if backend_name == "comfyui":
            comfyui_settings = {}
            if hasattr(self.config, '_config'):
                comfyui_settings = self.config._config.get("backend", {}).get("comfyui", {})
            api_request["comfyui"] = {
                "workflow": comfyui_settings.get("video_workflow", "ltx2-i2v"),
                "frame_count": round(total_duration * comfyui_settings.get("fps", 25)) + 1,
                "fps": comfyui_settings.get("fps", 25),
            }
            # Strip element tags from prompt for ComfyUI preview
            if prompt_mode == "narrative" and api_request.get("prompt"):
                api_request["comfyui"]["simplified_prompt"] = self._strip_element_tags(api_request["prompt"])

        preflight_data = {
            "preflight": True,
            "output_name": output_name,
            "api_request": api_request,
            "analysis": analysis,
            "files": files_info,
        }

        output_path = self.output_dir / f"{output_name}_preflight.json"
        with open(output_path, "w") as f:
            json.dump(preflight_data, f, indent=2, default=str)

        print(f"\n-> Preflight written: {output_path}")
        return output_path

    # ─── Frame generation ───────────────────────────────────────────

    def generate_frame(
        self,
        prompt: str,
        refs: List[Path] = None,
        output_name: str = "frame",
        lighting_mode: str = "night",
        negative_prompt: str = None,
        on_queue_update: Callable = None,
    ) -> Optional[Path]:
        """Generate a production frame using the image backend."""
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

        neg = negative_prompt or self.config.build_negative_prompt()

        # Get endpoint
        modality = "edit" if ref_urls else "text_to_image"
        endpoint = self.config.get_model_endpoint("nano_banana", modality)
        print(f"\nEndpoint: {endpoint}")

        try:
            result = self._image_backend.generate_image(
                prompt=full_prompt,
                reference_urls=ref_urls if ref_urls else None,
                negative_prompt=neg,
                aspect_ratio=defaults.get("aspect_ratio", "16:9"),
                on_queue_update=on_queue_update,
                endpoint=endpoint,
                resolution=defaults.get("resolution", "2K"),
                output_format=defaults.get("output_format", "png"),
                num_inference_steps=defaults.get("num_inference_steps", 40),
                guidance_scale=defaults.get("guidance_scale", 4.5),
            )

            if result.image_url or result.image_bytes:
                print(f"\n-> Generated")
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = self.output_dir / f"{output_name}_{timestamp}.png"

                if self._save_image_result(result, output_path):
                    print(f"-> Saved: {output_path}")
                    self._save_metadata(output_path, {
                        "prompt": prompt,
                        "full_prompt": full_prompt,
                        "references": [str(r) for r in (refs or [])],
                        "endpoint": endpoint,
                        "backend": self.image_backend_name,
                        "timestamp": datetime.now().isoformat(),
                        "image_url": result.image_url,
                    })
                    return output_path
                else:
                    print(f"x Failed to save")
                    return None
            else:
                print("x No image in result")
                return None

        except Exception as e:
            print(f"x Error: {e}")
            import traceback
            traceback.print_exc()
            return None

    # ─── Video clip generation ──────────────────────────────────────

    def generate_video_clip(
        self,
        start_frame: Path,
        prompts: List[Dict[str, Any]],
        characters: List[Dict[str, str]],
        scene_refs: List[Path] = None,
        output_name: str = "clip",
        negative_prompt: str = None,
        on_queue_update: Callable = None,
        preflight: bool = False,
        prompt_mode: str = "multi_prompt",
        **kwargs,
    ) -> Optional[Path]:
        """
        Generate a video clip, adapting to backend capabilities.

        For backends that don't support elements/multi_prompt (ComfyUI),
        prompts are simplified and elements are skipped with a warning.
        """
        mode_label = "PREFLIGHT" if preflight else "VIDEO CLIP"
        backend_name = self.video_backend_name
        print(f"\n{'='*70}")
        print(f"{mode_label}: {output_name} [{backend_name}]")
        print(f"{'='*70}")

        # Track all referenced files for preflight reporting
        files_info = {
            "start_frame": str(start_frame),
            "identity_sheets": {},
            "reference_images": [],
            "scene_refs": [],
            "missing": [],
        }

        # Resolve start frame
        if not start_frame.exists():
            files_info["missing"].append(str(start_frame))
        start_url = self._resolve_url(start_frame, preflight)

        # Resolve scene reference images
        scene_ref_urls = []
        if scene_refs:
            print(f"  Scene references: {len(scene_refs)}")
            for ref in scene_refs:
                if ref:
                    ref = Path(ref)
                    files_info["scene_refs"].append(str(ref))
                    if ref.exists():
                        scene_ref_urls.append(self._resolve_url(ref, preflight))
                    elif preflight:
                        files_info["missing"].append(str(ref))
                        scene_ref_urls.append(f"local://{ref}")

        # ─── Build elements (only for backends that support them) ───
        elements = []
        element_labels = []
        video_backend = self._video_backend

        supports_elements = video_backend.supports_elements if video_backend else True  # assume True for preflight

        if supports_elements:
            elements, element_labels = self._build_elements(
                characters, scene_ref_urls, start_url, preflight, files_info, kwargs
            )
        elif characters and not preflight:
            char_ids = [c.get("id", "?") for c in characters]
            print(f"  Note: {backend_name} backend does not support elements — character identity sheets skipped")
            print(f"    Characters referenced: {char_ids}")

        # ─── Element tag remapping ──────────────────────────────────
        element_tag_remap = {}
        if supports_elements:
            for i, char in enumerate(characters):
                original_tag = char.get("element", "")
                actual_tag = f"@Element{i + 1}"
                if original_tag and original_tag != actual_tag:
                    element_tag_remap[original_tag] = actual_tag
            if kwargs.get("location_element"):
                loc = kwargs["location_element"]
                original_loc_tag = loc.get("element_tag", "")
                actual_loc_tag = f"@Element{len(characters) + 1}"
                if original_loc_tag and original_loc_tag != actual_loc_tag:
                    element_tag_remap[original_loc_tag] = actual_loc_tag

        def remap_element_tags(text: str) -> str:
            for old_tag, new_tag in element_tag_remap.items():
                text = text.replace(old_tag, new_tag)
            return text

        if element_tag_remap:
            print(f"  Element tag remap: {element_tag_remap}")
            for p in prompts:
                p["prompt"] = remap_element_tags(p["prompt"])

        # ─── Build prompts based on mode ────────────────────────────
        MULTI_PROMPT_MAX_CHARS = 500
        NARRATIVE_MAX_CHARS = 2500
        NARRATIVE_WARN_CHARS = 2000

        if prompt_mode == "narrative":
            narrative_text = prompts[0]["prompt"]
            total_duration = int(prompts[0]["duration"])
            narrative_chars = len(narrative_text)

            print(f"\nStart frame: {start_frame.name}")
            print(f"Narrative prompt ({narrative_chars} chars, {total_duration}s):")
            print(f"  {narrative_text[:120]}...")
            if narrative_chars > NARRATIVE_MAX_CHARS:
                print(f"  ERROR: Exceeds API limit of {NARRATIVE_MAX_CHARS} chars!")
                if not preflight:
                    narrative_text = narrative_text[:NARRATIVE_MAX_CHARS]
            elif narrative_chars > NARRATIVE_WARN_CHARS:
                print(f"  WARNING: Approaching limit ({narrative_chars}/{NARRATIVE_MAX_CHARS})")

            multi_prompt = None
        else:
            multi_prompt = []
            for p in prompts:
                prompt_text = p["prompt"]
                if p.get("cut_prefix", True) and not prompt_text.strip().lower().startswith("cut to:"):
                    prompt_text = f"CUT to: {prompt_text}"
                if len(prompt_text) > MULTI_PROMPT_MAX_CHARS:
                    print(f"  WARNING: Prompt exceeds {MULTI_PROMPT_MAX_CHARS} chars ({len(prompt_text)})")
                    if not preflight:
                        prompt_text = prompt_text[:MULTI_PROMPT_MAX_CHARS]
                multi_prompt.append({
                    "prompt": prompt_text,
                    "duration": str(p["duration"]),
                })

            total_duration = sum(int(p["duration"]) for p in prompts)

            print(f"\nStart frame: {start_frame.name}")
            print(f"Multi-prompt ({len(prompts)} cuts):")
            for i, p in enumerate(multi_prompt):
                chars = len(p["prompt"])
                flag = " [OVER LIMIT]" if chars > MULTI_PROMPT_MAX_CHARS else ""
                print(f"  [{i+1}] ({p['duration']}s, {chars}ch{flag}) {p['prompt'][:60]}...")

        # ─── Cost estimate & config ─────────────────────────────────
        KLING_DEFAULTS = {
            "aspect_ratio": "16:9",
            "generate_audio": True,
            "cost_per_second": 0.336,
            "endpoint": "fal-ai/kling-video/v3/pro/image-to-video",
        }
        DEFAULT_NEGATIVE = "blurry, distorted, low quality, artifacts, text, watermark, talking, dialogue"

        if hasattr(self.config, 'get_model_defaults'):
            defaults = self.config.get_model_defaults("kling") or {}
        else:
            defaults = {}

        if negative_prompt:
            neg_prompt = negative_prompt
        elif hasattr(self.config, 'build_negative_prompt'):
            neg_prompt = self.config.build_negative_prompt(for_video=True)
        else:
            neg_prompt = DEFAULT_NEGATIVE

        # Use backend's cost_per_second if available
        if video_backend:
            cost_per_sec = video_backend.cost_per_second
        elif backend_name == "comfyui":
            cost_per_sec = 0.0  # local GPU, free
        elif hasattr(self.config, 'models'):
            cost_per_sec = self.config.models.get("kling", {}).get("cost_per_second", KLING_DEFAULTS["cost_per_second"])
        else:
            cost_per_sec = KLING_DEFAULTS["cost_per_second"]

        estimated_cost = total_duration * cost_per_sec
        print(f"\nDuration: {total_duration}s | Estimated cost: ${estimated_cost:.2f}")
        print(f"Backend: {backend_name}")

        # Get endpoint
        if backend_name == "comfyui":
            endpoint = f"comfyui://{backend_name}"
        elif hasattr(self.config, 'get_model_endpoint'):
            endpoint = self.config.get_model_endpoint("kling", "image_to_video")
        else:
            endpoint = KLING_DEFAULTS["endpoint"]

        if backend_name != "comfyui":
            print(f"Endpoint: {endpoint}")

        # ─── Build the API request dict (for preflight + fal) ──────
        request = {
            "start_image_url": start_url,
            "aspect_ratio": defaults.get("aspect_ratio", KLING_DEFAULTS["aspect_ratio"]),
            "generate_audio": defaults.get("generate_audio", KLING_DEFAULTS["generate_audio"]),
            "negative_prompt": neg_prompt,
        }

        if prompt_mode == "narrative":
            request["prompt"] = narrative_text
            request["duration"] = str(total_duration)
        else:
            request["multi_prompt"] = multi_prompt
            request["shot_type"] = "customize"

        if elements:
            request["elements"] = elements

        # ─── Preflight: write JSON and return ──────────────────────
        if preflight:
            files_info["all_exist"] = len(files_info["missing"]) == 0
            return self._write_preflight(
                request=request,
                output_name=output_name,
                endpoint=endpoint,
                total_duration=total_duration,
                estimated_cost=estimated_cost,
                files_info=files_info,
                element_labels=element_labels,
                prompt_max_chars=MULTI_PROMPT_MAX_CHARS,
                prompt_mode=prompt_mode,
                backend_name=backend_name,
            )

        # ─── Live: call backend ────────────────────────────────────
        try:
            if backend_name == "comfyui":
                # ComfyUI: simplify prompt and send directly
                if prompt_mode == "narrative":
                    final_prompt = narrative_text
                else:
                    final_prompt = self._simplify_multi_prompts(prompts)

                # Strip element tags (ComfyUI doesn't understand them)
                final_prompt = self._strip_element_tags(final_prompt)

                # Pass through reference_audio if provided
                comfyui_kwargs = {}
                if kwargs.get("reference_audio"):
                    comfyui_kwargs["reference_audio"] = Path(kwargs["reference_audio"])
                if kwargs.get("last_frame"):
                    comfyui_kwargs["last_frame"] = Path(kwargs["last_frame"])
                if kwargs.get("static_camera") is not None:
                    comfyui_kwargs["static_camera"] = kwargs["static_camera"]

                result = video_backend.generate_video(
                    start_frame=start_frame,
                    prompt=final_prompt,
                    duration_seconds=float(total_duration),
                    negative_prompt=neg_prompt,
                    on_queue_update=on_queue_update,
                    **comfyui_kwargs,
                )
            else:
                # Fal: pass full request with elements, multi_prompt, etc.
                backend_kwargs = {
                    "aspect_ratio": request["aspect_ratio"],
                    "generate_audio": request["generate_audio"],
                }
                if elements:
                    backend_kwargs["elements"] = elements
                if multi_prompt:
                    backend_kwargs["multi_prompt"] = multi_prompt
                    backend_kwargs["shot_type"] = "customize"

                result = video_backend.generate_video(
                    start_frame=start_frame,
                    prompt=narrative_text if prompt_mode == "narrative" else "",
                    duration_seconds=float(total_duration),
                    negative_prompt=neg_prompt,
                    on_queue_update=on_queue_update,
                    **backend_kwargs,
                )

            # Save result
            if result.video_url or result.video_bytes:
                print(f"\n-> Generated")
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = self.output_dir / f"{output_name}_{timestamp}.mp4"

                if self._save_video_result(result, output_path):
                    print(f"-> Saved: {output_path}")

                    self._save_metadata(output_path, {
                        "start_frame": str(start_frame),
                        "prompts": prompts,
                        "characters": characters,
                        "duration": total_duration,
                        "endpoint": endpoint,
                        "backend": backend_name,
                        "timestamp": datetime.now().isoformat(),
                        "video_url": result.video_url,
                    })

                    return output_path
                else:
                    print(f"x Failed to save video")
                    return None
            else:
                print("x No video in result")
                if result.metadata.get("error"):
                    print(f"  Error: {result.metadata['error']}")
                return None

        except Exception as e:
            print(f"x Error: {e}")
            import traceback
            traceback.print_exc()
            return None

    # ─── Element building (extracted for clarity) ───────────────────

    def _build_elements(
        self,
        characters: List[Dict[str, str]],
        scene_ref_urls: List[str],
        start_url: str,
        preflight: bool,
        files_info: Dict[str, Any],
        kwargs: Dict[str, Any],
    ) -> tuple:
        """Build elements list and labels for Kling-style backends."""
        elements = []
        element_labels = []

        for char in characters:
            char_id = char["id"]

            # Prefer explicit ref path if provided (agentic mode)
            if "ref" in char:
                identity_path = Path(char["ref"]) if char["ref"] else None
            elif hasattr(self.config, 'get_identity_sheet'):
                identity_path = self.config.get_identity_sheet(char_id)
            else:
                identity_path = None

            # Hero shot: explicit or config lookup
            if "hero_ref" in char:
                hero_path = Path(char["hero_ref"]) if char["hero_ref"] else None
            elif hasattr(self.config, 'get_hero_shot'):
                hero_path = self.config.get_hero_shot(char_id, "entrance")
            else:
                hero_path = None

            if identity_path and (identity_path.exists() or preflight):
                if not identity_path.exists():
                    files_info["missing"].append(str(identity_path))
                files_info["identity_sheets"][char_id] = str(identity_path)

                identity_url = self._resolve_url(identity_path, preflight)
                element = {
                    "frontal_image_url": identity_url,
                }
                ref_urls = []
                if "reference_image_paths" in char:
                    for rp in char["reference_image_paths"]:
                        rp = Path(rp)
                        files_info["reference_images"].append(str(rp))
                        if rp.exists():
                            ref_urls.append(self._resolve_url(rp, preflight))
                        elif preflight:
                            files_info["missing"].append(str(rp))
                            ref_urls.append(f"local://{rp}")
                else:
                    if hero_path and (hero_path.exists() or preflight):
                        if not hero_path.exists():
                            files_info["missing"].append(str(hero_path))
                        ref_urls.append(self._resolve_url(hero_path, preflight))
                    ref_urls.extend(scene_ref_urls)
                if not ref_urls:
                    ref_urls.append(start_url)
                element["reference_image_urls"] = ref_urls
                elements.append(element)
                element_labels.append(f"{char_id} ({char.get('element', '?')})")
                print(f"  Element: {char.get('element', '?')} = {char_id} (refs: {len(ref_urls)})")
            elif identity_path:
                print(f"  Warning: Identity not found for {char_id}: {identity_path}")

        # Build location/scene element if provided
        if kwargs.get("location_element"):
            loc = kwargs["location_element"]
            frontal_path = Path(loc["frontal"]) if loc.get("frontal") else None
            if frontal_path and (frontal_path.exists() or preflight):
                if not frontal_path.exists():
                    files_info["missing"].append(str(frontal_path))
                loc_element = {
                    "frontal_image_url": self._resolve_url(frontal_path, preflight),
                }
                loc_ref_urls = []
                for rp in loc.get("reference_image_paths", []):
                    rp = Path(rp)
                    if rp.exists():
                        loc_ref_urls.append(self._resolve_url(rp, preflight))
                    elif preflight:
                        files_info["missing"].append(str(rp))
                        loc_ref_urls.append(f"local://{rp}")
                if not loc_ref_urls:
                    loc_ref_urls.append(start_url)
                loc_element["reference_image_urls"] = loc_ref_urls
                elements.append(loc_element)
                loc_tag = loc.get("element_tag", f"@Element{len(elements)}")
                element_labels.append(f"location ({loc_tag})")
                print(f"  Element: {loc_tag} = location (refs: {len(loc_ref_urls)})")

        return elements, element_labels
