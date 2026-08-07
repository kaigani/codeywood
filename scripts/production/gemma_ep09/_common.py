"""Common config for gemma-anthology EP09 production scripts.

EP09 = "The Slaughter" — rough-cut tier (pure t2v, no refs). Estate
violence. Cold surgical blue + violent arterial red + obsidian black.
"""

from __future__ import annotations

import struct
import subprocess
import time
from pathlib import Path

import requests

COMFYUI_BASE = "http://192.168.1.181:8100"

PROJECT = Path(__file__).resolve().parents[3] / "projects" / "260513-gemma-anthology"
PRODUCTION = PROJECT / "PRODUCTION" / "EP09"
SHOTLIST = PROJECT / "shotlists" / "episode-09.md"
CLIP_DEFS = PRODUCTION / "clip_definitions.yaml"

CLIPS_DIR = PRODUCTION / "clips"
ASSEMBLY_DIR = PRODUCTION / "assembly"
DELIVERABLES = PROJECT / "DELIVERABLES" / "EP09"

NEGATIVE = (
    "blurry, oversaturated, pixelated, low resolution, distorted, noise, "
    "watermark, text, logo, subtitles, deformed, extra limbs, music, "
    "soundtrack, musical instruments, cartoon, anime, anime style, "
    "illustration, drawing, painting, painted, 3d render, cgi, "
    "graphic novel, comic book, stylized, smooth shading, cel shading, "
    "video game, plastic skin, doll-like, signature, bad anatomy, "
    "duplicate figures, sterile, calm, peaceful"
)

STYLE_TAG = (
    "Hyper-visceral cyberpunk live-action frame, shot on 35mm anamorphic "
    "lenses with gritty high-grain texture, high contrast lighting with "
    "deep shadows and saturated neon highlights, cold surgical blue and "
    "violent arterial red and obsidian black color palette, polished "
    "black obsidian floors reflecting violet and gold neon strips, rapid "
    "aggressive handheld camera during action, naturalistic skin texture "
    "and tactile blood. Photoreal cinematic photography, NOT animation."
)

SAMPLE_RATE = 44100


def health_check() -> bool:
    try:
        r = requests.get(f"{COMFYUI_BASE}/health", timeout=5)
        return r.status_code == 200
    except Exception:
        return False


def submit_sync_or_async(workflow: str, data: dict, files=None, timeout: int = 300):
    url = f"{COMFYUI_BASE}/workflows/{workflow}"
    resp = requests.post(url, data=data, files=files, timeout=60)
    if resp.status_code not in (200, 202):
        raise RuntimeError(f"{workflow} POST {resp.status_code}: {resp.text[:200]}")
    ct = resp.headers.get("content-type", "")
    if "audio" in ct or "image" in ct or "video" in ct or "octet-stream" in ct:
        return None, resp.content
    body = resp.json()
    job_id = body.get("job_id")
    if not job_id:
        raise RuntimeError(f"{workflow}: no job_id in response: {body}")
    return job_id, None


def poll_job(job_id: str, timeout: int = 600) -> bytes:
    start = time.time()
    polls = 0
    while time.time() - start < timeout:
        try:
            status = requests.get(f"{COMFYUI_BASE}/jobs/{job_id}", timeout=10).json()
        except Exception:
            time.sleep(3)
            continue
        st = status.get("status", "unknown")
        if st == "completed":
            r = requests.get(f"{COMFYUI_BASE}/jobs/{job_id}/result", timeout=120)
            return r.content
        if st in ("error", "failed"):
            raise RuntimeError(f"Job {job_id} failed: {status.get('error')}")
        polls += 1
        time.sleep(2 if polls <= 5 else 5)
    raise TimeoutError(f"Job {job_id} timeout after {timeout}s")


def run_workflow(workflow: str, data: dict, files=None, timeout: int = 600) -> bytes:
    job_id, sync_content = submit_sync_or_async(workflow, data, files=files)
    if sync_content is not None:
        return sync_content
    return poll_job(job_id, timeout=timeout)


def save(content: bytes, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as f:
        f.write(content)
    return path


def probe_duration_ff(path: Path) -> float:
    cmd = [
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", str(path),
    ]
    out = subprocess.run(cmd, capture_output=True, text=True)
    return float(out.stdout.strip())


def run_ffmpeg(cmd: list[str], desc: str = "") -> bool:
    if desc:
        print(f"    {desc}")
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"    FFMPEG ERROR: {r.stderr[-500:]}")
        return False
    return True
