"""Concept-art workflow — z-image-base-t2i, pencil + watercolor style.

Builds prompts using Z-Image's official 4-layer structure:
  1. Subject & Action (objective, concrete)
  2. Composition & Visual Style (medium, camera, framing)
  3. Lighting & Environment
  4. Text Factor (verbatim quoted strings, English layout)

Z-Image Turbo rules baked in:
  - No "8K / masterpiece / photorealistic / ultra-detailed" meta-tags
  - Negative prompts are weak; describe the clean state in the positive
  - Embedded text strings kept to 1-5 words per line
"""

from __future__ import annotations

import json
import subprocess
import time
from pathlib import Path

import requests

COMFYUI_BASE = "http://192.168.1.181:8100"
WORKFLOW = "z-image-base-t2i"

# Repo root resolved relative to this file: scripts/production/concept_art/_common.py
REPO_ROOT = Path(__file__).resolve().parents[3]

# Pencil + watercolor concept art style block.
# Drops meta-tags ("8K", "masterpiece") and describes the medium concretely
# (per Z-Image's "addition not subtraction" rule).
STYLE_BLOCK = (
    "Pencil and watercolor concept art. Loose graphite linework with visible "
    "construction lines, soft watercolor washes where light catches surfaces, "
    "off-white paper grain texture, hand-drawn illustrator sketchbook "
    "aesthetic. Expressive but objective rendering, working concept sketch, "
    "no photographic detail."
)

# A weak / placeholder negative — z-image-turbo largely ignores this.
NEGATIVE = (
    "no photographic realism, no 3d render, no cgi, no plastic skin, "
    "no anime, no smooth digital painting, no neon highlights"
)


def health_check() -> bool:
    try:
        return requests.get(f"{COMFYUI_BASE}/health", timeout=5).status_code == 200
    except Exception:
        return False


def submit(data: dict, timeout: int = 60):
    """POST. Returns (job_id, sync_content) — exactly one is None."""
    resp = requests.post(f"{COMFYUI_BASE}/workflows/{WORKFLOW}", data=data, timeout=timeout)
    if resp.status_code not in (200, 202):
        raise RuntimeError(f"submit {resp.status_code}: {resp.text[:200]}")
    ct = resp.headers.get("content-type", "")
    if "image" in ct or "octet-stream" in ct:
        return None, resp.content
    body = resp.json()
    return body["job_id"], None


def poll(job_id: str, timeout: int = 300) -> bytes:
    t0 = time.time()
    polls = 0
    while time.time() - t0 < timeout:
        try:
            st = requests.get(f"{COMFYUI_BASE}/jobs/{job_id}", timeout=10).json()
        except Exception:
            time.sleep(2)
            continue
        s = st.get("status")
        if s == "completed":
            return requests.get(f"{COMFYUI_BASE}/jobs/{job_id}/result", timeout=120).content
        if s in ("failed", "error"):
            raise RuntimeError(f"job {job_id} {s}: {st.get('error')}")
        polls += 1
        time.sleep(2 if polls <= 5 else 4)
    raise TimeoutError(f"job {job_id} timed out after {timeout}s")


def run(data: dict, timeout: int = 300) -> bytes:
    job_id, sync = submit(data)
    if sync is not None:
        return sync
    return poll(job_id, timeout=timeout)


def save(content: bytes, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)
    return path


# ----- 4-layer prompt builder -----

def build_prompt(
    subject_action: str,
    composition: str,
    lighting: str,
    text_factor: str = "",
) -> str:
    """Assemble the 4 official Z-Image layers into a single prompt.

    Style block goes first because pencil-watercolor is the medium constraint.
    """
    parts = [STYLE_BLOCK, subject_action, composition, lighting]
    if text_factor:
        parts.append(text_factor)
    return " ".join(p.strip() for p in parts if p.strip())
