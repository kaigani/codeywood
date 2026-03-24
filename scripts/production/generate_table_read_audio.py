#!/usr/bin/env python3
"""
Table Read v02 — Generate TTS audio for all dialogue lines.

Uses qwen3-tts-voiceclone with voice reference WAVs.
Reads shot list, generates one WAV per shot that has audio text.

Voice refs expected in table_read/audio/:
  mick_voice.wav   (required — most lines)
  neda_voice.wav   (optional — falls back to mick)
  kai_voice.wav    (optional — falls back to mick)
"""

import struct
import sys
import time
from pathlib import Path

import requests
import yaml

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
COMFYUI_BASE = "http://192.168.1.181:8100"
WORKFLOW = "qwen3-tts-voiceclone"

PROJECT = Path(__file__).resolve().parents[2] / "projects" / "stray-signal"
TABLE_READ = PROJECT / "PRODUCTION" / "EP01_v03" / "table_read"
SHOT_LIST = TABLE_READ / "table_read_shot_list.yaml"
AUDIO_DIR = TABLE_READ / "audio"

# Voice ref files per character
VOICE_REFS = {
    "mick": AUDIO_DIR / "mick_voice.wav",
    "neda": AUDIO_DIR / "neda_voice.wav",
    "kai": AUDIO_DIR / "kai_voice.wav",
}
DEFAULT_VOICE = "mick"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def get_voice_ref(character):
    """Get voice ref path, falling back to default."""
    ref = VOICE_REFS.get(character)
    if ref and ref.exists():
        return ref, character
    fallback = VOICE_REFS[DEFAULT_VOICE]
    return fallback, DEFAULT_VOICE


def strip_direction(text):
    """Strip parenthetical direction from start of audio text.

    '(energetic, rapid) Alright.' → 'Alright.'
    The direction is for LTX-2 prompting, not TTS.
    """
    if text.startswith("("):
        close = text.find(")")
        if close != -1:
            return text[close + 1:].strip()
    return text


def submit_tts(text, voice_ref_path, timeout=120):
    """Submit TTS job and wait for result."""
    url = f"{COMFYUI_BASE}/workflows/{WORKFLOW}"
    with open(voice_ref_path, "rb") as vf:
        files = {"voice": (voice_ref_path.name, vf, "audio/wav")}
        data = {"text": text}
        resp = requests.post(url, data=data, files=files, timeout=30)

    # Sync response (small text)
    if resp.status_code == 200 and resp.headers.get("content-type", "").startswith("audio"):
        return resp.content

    # Async response
    resp.raise_for_status()
    job = resp.json()
    job_id = job["job_id"]
    start = time.time()
    deadline = start + timeout
    polls = 0
    while time.time() < deadline:
        status = requests.get(f"{COMFYUI_BASE}/jobs/{job_id}").json()
        st = status.get("status", "unknown")
        if st == "completed":
            elapsed = time.time() - start
            print(f"    TTS done ({elapsed:.0f}s)")
            return requests.get(f"{COMFYUI_BASE}/jobs/{job_id}/result").content
        if st in ("error", "failed"):
            raise RuntimeError(f"TTS job {job_id} failed: {status.get('error')}")
        polls += 1
        time.sleep(2 if polls <= 5 else 5)
    raise TimeoutError(f"TTS timeout on {job_id}")


def create_silent_wav(output_path, duration_s, sample_rate=44100):
    """Create a silent WAV file of the given duration."""
    num_samples = int(duration_s * sample_rate)
    num_channels = 1
    bits_per_sample = 16
    byte_rate = sample_rate * num_channels * bits_per_sample // 8
    block_align = num_channels * bits_per_sample // 8
    data_size = num_samples * block_align

    with open(output_path, "wb") as f:
        # RIFF header
        f.write(b"RIFF")
        f.write(struct.pack("<I", 36 + data_size))
        f.write(b"WAVE")
        # fmt chunk
        f.write(b"fmt ")
        f.write(struct.pack("<I", 16))
        f.write(struct.pack("<H", 1))  # PCM
        f.write(struct.pack("<H", num_channels))
        f.write(struct.pack("<I", sample_rate))
        f.write(struct.pack("<I", byte_rate))
        f.write(struct.pack("<H", block_align))
        f.write(struct.pack("<H", bits_per_sample))
        # data chunk
        f.write(b"data")
        f.write(struct.pack("<I", data_size))
        f.write(b"\x00" * data_size)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Generate TTS audio for table read")
    parser.add_argument("--shot", type=int, default=0, help="Specific shot (0 = all)")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--force", action="store_true", help="Regenerate even if WAV exists")
    args = parser.parse_args()

    AUDIO_DIR.mkdir(parents=True, exist_ok=True)

    with open(SHOT_LIST) as f:
        shot_list = yaml.safe_load(f)

    shots = shot_list["shots"]
    if args.shot > 0:
        shots = [s for s in shots if s["shot"] == args.shot]
        if not shots:
            print(f"No shot {args.shot}")
            sys.exit(1)

    # Filter to shots with audio text
    audio_shots = [s for s in shots if s.get("audio")]

    if args.dry_run:
        print(f"[DRY RUN] {len(audio_shots)} dialogue lines to generate:\n")
        for s in audio_shots:
            shot_num = s["shot"]
            voice = s.get("voice", DEFAULT_VOICE)
            ref_path, actual_voice = get_voice_ref(voice)
            out = AUDIO_DIR / f"shot_{shot_num:02d}.wav"
            text = strip_direction(s["audio"])
            fallback = f" [FALLBACK→{actual_voice}]" if actual_voice != voice else ""
            exists = "EXISTS" if out.exists() else "pending"
            ref_ok = "ref OK" if ref_path.exists() else "NO REF"
            print(f"  Shot {shot_num:2d}: voice={voice}{fallback} [{ref_ok}] {exists}")
            print(f"           \"{text[:80]}{'...' if len(text) > 80 else ''}\"")
        print(f"\nTotal: {len(audio_shots)} lines")
        sys.exit(0)

    # Health check
    try:
        r = requests.get(f"{COMFYUI_BASE}/health", timeout=5)
        if r.status_code != 200:
            print(f"ERROR: ComfyUI not healthy (status {r.status_code})")
            sys.exit(1)
    except Exception as e:
        print(f"ERROR: ComfyUI not reachable: {e}")
        sys.exit(1)

    # Check default voice ref exists
    default_ref = VOICE_REFS[DEFAULT_VOICE]
    if not default_ref.exists():
        print(f"ERROR: Default voice ref not found: {default_ref}")
        sys.exit(1)

    total = len(audio_shots)
    done = 0
    failed = []

    for s in audio_shots:
        done += 1
        shot_num = s["shot"]
        voice = s.get("voice", DEFAULT_VOICE)
        ref_path, actual_voice = get_voice_ref(voice)
        out_path = AUDIO_DIR / f"shot_{shot_num:02d}.wav"

        if out_path.exists() and not args.force:
            print(f"\n  [{done}/{total}] Shot {shot_num}: SKIP (exists)")
            continue

        text = strip_direction(s["audio"])
        fallback = f" [using {actual_voice} voice]" if actual_voice != voice else ""
        print(f"\n  [{done}/{total}] Shot {shot_num}: {voice}{fallback}")
        print(f"    \"{text[:60]}{'...' if len(text) > 60 else ''}\"")

        try:
            data = submit_tts(text, ref_path)
            out_path.parent.mkdir(parents=True, exist_ok=True)
            with open(out_path, "wb") as f:
                f.write(data)
            kb = len(data) / 1024
            print(f"    Saved: {out_path.name} ({kb:.0f} KB)")
        except Exception as e:
            print(f"    FAILED: {e}")
            failed.append(f"shot_{shot_num}")

    if failed:
        print(f"\n  FAILED ({len(failed)}): {', '.join(failed)}")

    print(f"\n{'=' * 70}")
    print(f"DONE — {done} TTS lines processed")
    print(f"{'=' * 70}")
