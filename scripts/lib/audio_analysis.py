"""
Audio analysis utilities for Claude's proxy hearing.

Provides waveform visualization, silence detection, and Whisper STT
transcription via ComfyUI backend.
"""

import json
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Optional


def generate_waveform(
    audio_path: Path,
    output_path: Path,
    width: int = 1200,
    height: int = 200,
    color: str = "#4a9eff",
) -> Optional[Path]:
    """
    Generate an amplitude waveform visualization using ffmpeg.

    Args:
        audio_path: Path to audio or video file
        output_path: Path for output PNG
        width: Image width in pixels
        height: Image height in pixels
        color: Waveform color (hex)

    Returns:
        Path to waveform PNG, or None on failure
    """
    audio_path = Path(audio_path)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        "ffmpeg", "-y",
        "-i", str(audio_path),
        "-filter_complex",
        f"showwavespic=s={width}x{height}:colors={color}",
        "-frames:v", "1",
        str(output_path)
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0 and output_path.exists():
        print(f"  Waveform saved: {output_path}")
        return output_path
    else:
        if result.stderr and "does not contain any stream" in result.stderr:
            print(f"  No audio track found in {audio_path.name}")
        else:
            print(f"  Failed to generate waveform")
            if result.stderr:
                print(f"  {result.stderr[:300]}")
        return None


def detect_silence(
    audio_path: Path,
    threshold_db: float = -30.0,
    min_duration_s: float = 0.5,
) -> Optional[List[Dict]]:
    """
    Detect silence regions in an audio/video file.

    Args:
        audio_path: Path to audio or video file
        threshold_db: Silence threshold in dB (default -30)
        min_duration_s: Minimum silence duration in seconds

    Returns:
        List of dicts with start_s, end_s, duration_s for each silence region,
        or None on failure.
    """
    audio_path = Path(audio_path)

    cmd = [
        "ffmpeg", "-y",
        "-i", str(audio_path),
        "-af", f"silencedetect=noise={threshold_db}dB:d={min_duration_s}",
        "-f", "null", "-"
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        if "does not contain any stream" in (result.stderr or ""):
            print(f"  No audio track in {audio_path.name}")
        return None

    # Parse silencedetect output from stderr
    import re
    silences = []
    current_start = None

    for line in result.stderr.split("\n"):
        start_match = re.search(r"silence_start:\s*([\d.]+)", line)
        end_match = re.search(r"silence_end:\s*([\d.]+)\s*\|\s*silence_duration:\s*([\d.]+)", line)

        if start_match:
            current_start = float(start_match.group(1))
        elif end_match:
            end_time = float(end_match.group(1))
            dur = float(end_match.group(2))
            silences.append({
                "start_s": round(current_start or (end_time - dur), 2),
                "end_s": round(end_time, 2),
                "duration_s": round(dur, 2),
            })
            current_start = None

    print(f"  Detected {len(silences)} silence region(s)")
    return silences


def transcribe_audio(
    audio_path: Path,
    comfyui_url: str = "http://192.168.1.181:8100",
    model_size: str = "large",
    timeout: int = 300,
) -> Optional[Dict]:
    """
    Transcribe audio using Whisper STT via ComfyUI workflow.

    Args:
        audio_path: Path to audio or video file
        comfyui_url: ComfyUI server URL
        model_size: Whisper model size (base, small, medium, large)
        timeout: Request timeout in seconds

    Returns:
        Dict with transcript text and segments with timestamps, or None on failure.
    """
    import requests

    audio_path = Path(audio_path)
    if not audio_path.exists():
        print(f"  Audio file not found: {audio_path}")
        return None

    # First extract audio to WAV if it's a video file
    if audio_path.suffix.lower() in ('.mp4', '.mov', '.avi', '.mkv', '.webm'):
        tmp_wav = Path(tempfile.mktemp(suffix=".wav"))
        cmd = [
            "ffmpeg", "-y", "-i", str(audio_path),
            "-vn", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1",
            str(tmp_wav)
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            if "does not contain any stream" in (result.stderr or ""):
                print(f"  No audio track in {audio_path.name}")
            return None
        upload_path = tmp_wav
    else:
        upload_path = audio_path
        tmp_wav = None

    try:
        # Upload audio to ComfyUI
        api_url = f"{comfyui_url.rstrip('/')}/api"
        with open(upload_path, "rb") as f:
            upload_resp = requests.post(
                f"{api_url}/upload/audio",
                files={"file": (upload_path.name, f, "audio/wav")},
                timeout=30,
            )
        if upload_resp.status_code != 200:
            print(f"  Upload failed: {upload_resp.status_code}")
            return None

        upload_data = upload_resp.json()
        audio_filename = upload_data.get("name", upload_path.name)

        # Build Whisper STT workflow
        workflow = {
            "whisper-stt": {
                "class_type": "WhisperSTT",
                "inputs": {
                    "audio": audio_filename,
                    "model_size": model_size,
                }
            }
        }

        # Submit workflow
        prompt_resp = requests.post(
            f"{api_url}/prompt",
            json={"prompt": workflow},
            timeout=30,
        )
        if prompt_resp.status_code != 200:
            print(f"  Workflow submission failed: {prompt_resp.status_code}")
            return None

        prompt_id = prompt_resp.json().get("prompt_id")
        if not prompt_id:
            print(f"  No prompt_id returned")
            return None

        # Poll for completion
        import time
        start = time.time()
        while time.time() - start < timeout:
            history_resp = requests.get(f"{api_url}/history/{prompt_id}", timeout=10)
            if history_resp.status_code == 200:
                history = history_resp.json()
                if prompt_id in history:
                    outputs = history[prompt_id].get("outputs", {})
                    if outputs:
                        # Extract transcript from workflow output
                        for node_id, node_output in outputs.items():
                            if "text" in node_output:
                                text = node_output["text"]
                                if isinstance(text, list):
                                    text = text[0] if text else ""
                                return {
                                    "text": text,
                                    "model_size": model_size,
                                    "audio_file": str(audio_path),
                                }
                        # Try alternative output format
                        return {
                            "raw_output": outputs,
                            "model_size": model_size,
                            "audio_file": str(audio_path),
                        }
            time.sleep(2)

        print(f"  Transcription timed out after {timeout}s")
        return None

    except requests.ConnectionError:
        print(f"  ComfyUI not available at {comfyui_url}")
        return None
    except Exception as e:
        print(f"  Transcription error: {e}")
        return None
    finally:
        if tmp_wav and tmp_wav.exists():
            tmp_wav.unlink()


def generate_direction_audio(
    text: str,
    voice_ref: Path,
    output_path: Path,
    comfyui_url: str = "http://192.168.1.181:8100",
    workflow: str = "qwen3-tts-voiceclone",
    timeout: int = 120,
) -> Optional[Path]:
    """
    Generate spoken direction narration via TTS voice clone.

    Handles both sync (200 with audio) and async (202 with job_id) responses
    from the ComfyUI API.

    Args:
        text: Direction text to speak
        voice_ref: Path to narrator voice reference WAV
        output_path: Path for output audio file
        comfyui_url: ComfyUI server URL
        workflow: TTS workflow name
        timeout: Max seconds to wait for async job

    Returns:
        Path to generated audio, or None on failure
    """
    import time as _time
    import requests as _requests

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    url = f"{comfyui_url}/workflows/{workflow}"

    try:
        with open(voice_ref, "rb") as vf:
            files = {"voice": (voice_ref.name, vf, "audio/wav")}
            data = {"text": text}
            response = _requests.post(url, data=data, files=files, timeout=timeout)
    except _requests.exceptions.ConnectionError:
        print(f"  ComfyUI not available at {comfyui_url}")
        return None
    except _requests.exceptions.Timeout:
        print(f"  TTS request timed out")
        return None

    # Sync response — audio returned directly
    if response.status_code == 200:
        content_type = response.headers.get("content-type", "")
        if "audio" in content_type or "octet-stream" in content_type:
            with open(output_path, "wb") as f:
                f.write(response.content)
            return output_path

    # Async response — poll for job completion
    if response.status_code in (200, 202):
        try:
            job_data = response.json()
        except Exception:
            print(f"  TTS: unexpected response format")
            return None

        job_id = job_data.get("job_id")
        if not job_id:
            print(f"  TTS: no job_id in response")
            return None

        deadline = _time.time() + timeout
        while _time.time() < deadline:
            try:
                status_resp = _requests.get(
                    f"{comfyui_url}/jobs/{job_id}", timeout=10
                )
                status = status_resp.json()
            except Exception:
                _time.sleep(2)
                continue

            if status.get("status") == "completed":
                result_resp = _requests.get(
                    f"{comfyui_url}/jobs/{job_id}/result", timeout=30
                )
                if result_resp.status_code == 200 and len(result_resp.content) > 100:
                    with open(output_path, "wb") as f:
                        f.write(result_resp.content)
                    return output_path
                else:
                    print(f"  TTS: result fetch failed ({result_resp.status_code})")
                    return None

            if status.get("status") == "error":
                print(f"  TTS job failed: {status.get('error', 'unknown')}")
                return None

            _time.sleep(2)

        print(f"  TTS: job {job_id} timed out after {timeout}s")
        return None

    print(f"  TTS error {response.status_code}: {response.text[:200]}")
    return None
