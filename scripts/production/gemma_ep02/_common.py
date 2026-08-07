"""Common config and helpers for gemma-anthology EP02 production scripts.

EP02 = "The Blood-Trail" — realistic cyber-noir style (not animation).
"""

from __future__ import annotations

import struct
import subprocess
import time
from pathlib import Path

import requests

COMFYUI_BASE = "http://192.168.1.181:8100"

PROJECT = Path(__file__).resolve().parents[3] / "projects" / "260513-gemma-anthology"
PRODUCTION = PROJECT / "PRODUCTION" / "EP02"
SHOTLIST = PROJECT / "shotlists" / "episode-02.md"
CLIP_DEFS = PRODUCTION / "clip_definitions.yaml"
VOICE_DEFS = PROJECT / "voice_definitions_ep02.yaml"

REFS_DIR = PROJECT / "REFERENCES" / "EP02"
CHAR_REFS = REFS_DIR / "character_refs"
LOC_REFS = REFS_DIR / "location_refs"
VOICE_PORTRAITS = REFS_DIR / "voice_portraits"
VOICE_VIDEO_REFS = REFS_DIR / "voice_video_refs"
VOICE_REFS = REFS_DIR / "voice_refs"

FRAMES_DIR = PRODUCTION / "frames"
CLIPS_DIR = PRODUCTION / "clips"
AUDIO_DIR = PRODUCTION / "audio"
VOICE_LINES = AUDIO_DIR / "voice_lines"
AMBIENT_DIR = AUDIO_DIR / "ambient"
SFX_DIR = AUDIO_DIR / "sfx"
MIX_DIR = AUDIO_DIR / "clip_mixes"
ASSEMBLY_DIR = PRODUCTION / "assembly"
DELIVERABLES = PROJECT / "DELIVERABLES" / "EP02"

# Realistic cyber-noir negative — keep "photograph" OUT of negative because
# we want photoreal, but block style drift toward animation/illustration.
NEGATIVE = (
    "blurry, oversaturated, pixelated, low resolution, distorted, noise, "
    "watermark, text, logo, subtitles, deformed, extra limbs, music, "
    "soundtrack, musical instruments, cartoon, anime, anime style, "
    "illustration, drawing, painting, painted, 3d render, cgi, "
    "graphic novel, comic book, stylized, smooth shading, cel shading, "
    "video game, plastic skin, doll-like, signature, bad anatomy, "
    "duplicate figures"
)

# Realistic cyber-noir style — ARRI Alexa anamorphic, film grain, teal/orange
STYLE_TAG = (
    "Cinematic live-action frame, shot on ARRI Alexa with 35mm anamorphic "
    "lens, fine 35mm film grain, naturalistic skin texture, practical "
    "lighting, shallow depth of field, cyber-noir color grade with cold "
    "teal shadows and burning orange highlights, high dynamic range. "
    "Photoreal cinematic photography, NOT animation."
)

SAMPLE_RATE = 44100


def health_check() -> bool:
    try:
        r = requests.get(f"{COMFYUI_BASE}/health", timeout=5)
        return r.status_code == 200
    except Exception:
        return False


def submit_sync_or_async(workflow: str, data: dict, files=None, timeout: int = 300):
    """POST to a workflow. Return (job_id, sync_content) — one will be None."""
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


def probe_wav_duration(wav_path: Path) -> float | None:
    with open(wav_path, "rb") as f:
        f.read(12)
        while True:
            chunk_id = f.read(4)
            if not chunk_id:
                return None
            chunk_size = struct.unpack("<I", f.read(4))[0]
            if chunk_id == b"fmt ":
                fmt_data = f.read(chunk_size)
                channels = struct.unpack("<H", fmt_data[2:4])[0]
                sample_rate = struct.unpack("<I", fmt_data[4:8])[0]
                bits_per_sample = struct.unpack("<H", fmt_data[14:16])[0]
            elif chunk_id == b"data":
                bytes_per_sample = bits_per_sample // 8
                total_samples = chunk_size // (channels * bytes_per_sample)
                return total_samples / sample_rate
            else:
                f.seek(chunk_size, 1)


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
