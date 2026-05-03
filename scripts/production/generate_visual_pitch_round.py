#!/usr/bin/env python3
"""
Visual pitch round orchestrator.

Per writer (yaml_id matches skills/writer/personas/{yaml_id}.yaml + media/{yaml_id}/):
  Phase 1 (--phase stills): parse SYNOPSES/{id}.md → generate 3 z-image STILLS/{id}_N.jpg
  Phase 2 (--phase tts):    qwen3-tts-voiceclone(synopsis, ref=media/{id}/voice.wav) → VOICE/{id}.wav
  Phase 3 (--phase assemble): 3 stills × (audio_dur/3) + audio → PITCH_CLIPS/{id}.mp4
                              then intro.mp4 + PITCH_CLIPS/{id}.mp4 → FINAL/{id}.mp4
                              via filtergraph concat with libx264+aac re-encode

Phases are split so z-image and LTX stay cache-hot per phase (lesson from writer-intros).
Use --phase all to run all three per writer (slower).
"""
import argparse
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import requests

# ─── Config ──────────────────────────────────────────────────────────────────

COMFYUI_BASE = "http://192.168.1.181:8100"
TIMEOUT_IMAGE = 120
TIMEOUT_TTS = 180

WIDTH, HEIGHT = 1280, 720
IMAGE_WORKFLOW = "z-image-base-t2i"  # overridden by --image-model
TTS_WORKFLOW = "qwen3-tts-voiceclone"

IMAGE_NEG = (
    "blurry, low quality, watermark, text overlay, subtitles, "
    "cartoon, animation, 3D render, overexposed, underexposed, "
    "disfigured, extra limbs, bad anatomy"
)

ROOT = Path("/Users/kaigani/Documents/PROJECTS/DEVELOPMENT/260125 codeywood")
PROJECT = ROOT / "projects/260414-visual-pitch-round"  # default; overridden by --project
PERSONAS = ROOT / "skills/writer/personas"
MEDIA = PERSONAS / "media"


def set_subdir(subdir: str | None):
    """Point all output dirs at an optional subdir (e.g. R2)."""
    global SYN_DIR, STILLS_DIR, VOICE_DIR, PITCH_DIR, FINAL_DIR
    base = PROJECT / subdir if subdir else PROJECT
    SYN_DIR = base / "SYNOPSES"
    STILLS_DIR = base / "STILLS"
    VOICE_DIR = base / "VOICE"
    PITCH_DIR = base / "PITCH_CLIPS"
    FINAL_DIR = base / "FINAL"
    for d in (STILLS_DIR, VOICE_DIR, PITCH_DIR, FINAL_DIR):
        d.mkdir(parents=True, exist_ok=True)


set_subdir(None)

# ─── Helpers ──────────────────────────────────────────────────────────────────

def health():
    try:
        return requests.get(f"{COMFYUI_BASE}/health", timeout=5).status_code == 200
    except Exception:
        return False


def submit_and_wait(workflow, data, files=None, timeout=300):
    url = f"{COMFYUI_BASE}/workflows/{workflow}"
    resp = requests.post(url, data=data, files=files, timeout=30)
    ct = resp.headers.get("content-type", "")
    if resp.status_code == 200 and ("image" in ct or "audio" in ct or "video" in ct or "octet-stream" in ct):
        if len(resp.content) > 100:
            return resp.content
    if resp.status_code not in (200, 202):
        raise RuntimeError(f"HTTP {resp.status_code}: {resp.text[:300]}")
    job_id = resp.json().get("job_id")
    if not job_id:
        raise RuntimeError(f"No job_id: {resp.text[:200]}")
    start = time.time()
    while time.time() - start < timeout:
        time.sleep(3)
        try:
            status = requests.get(f"{COMFYUI_BASE}/jobs/{job_id}", timeout=15).json()
        except Exception:
            continue
        st = status.get("status", "unknown")
        if st == "completed":
            return requests.get(f"{COMFYUI_BASE}/jobs/{job_id}/result", timeout=60).content
        if st in ("error", "failed"):
            raise RuntimeError(f"Job {job_id} failed: {status.get('error')}")
    raise TimeoutError(f"Timeout on job {job_id}")


def parse_synopsis(md_path: Path) -> dict:
    text = md_path.read_text()
    sections = {}
    current = None
    buf = []
    for line in text.splitlines():
        m = re.match(r'^##\s+(.+)', line)
        if m:
            if current is not None:
                sections[current] = "\n".join(buf).strip()
                buf = []
            current = m.group(1).strip()
        else:
            if current is not None:
                buf.append(line)
    if current is not None:
        sections[current] = "\n".join(buf).strip()
    v1 = sections.get("Visual 1", "").strip()
    v2 = sections.get("Visual 2", "").strip()
    v3 = sections.get("Visual 3", "").strip()
    # Extract style/medium prefix from V1 (text before first colon if short and stylistic)
    style_prefix = ""
    if ":" in v1:
        head = v1.split(":", 1)[0].strip()
        kw = ("animation", "animated", "painterly", "illustration", "watercolor",
              "stop-motion", "stop motion", "cel-shaded", "anime", "expressionist",
              "live-action", "documentary", "photoreal", "film still", "stylized")
        if len(head) < 120 and any(k in head.lower() for k in kw):
            style_prefix = head + ". "
    return {
        "matrix": sections.get("Matrix choices", ""),
        "synopsis": sections.get("Synopsis (spoken — will be voicecloned)", sections.get("Synopsis", "")).strip(),
        "v1": v1,
        "v2": (style_prefix + v2) if style_prefix and not any(k in v2.lower()[:120] for k in ("animation", "animated", "painterly", "expressionist", "stylized")) else v2,
        "v3": (style_prefix + v3) if style_prefix and not any(k in v3.lower()[:120] for k in ("animation", "animated", "painterly", "expressionist", "stylized")) else v3,
        "style_prefix": style_prefix,
    }


def probe_duration(path: Path) -> float:
    cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration",
           "-of", "default=noprint_wrappers=1:nokey=1", str(path)]
    return float(subprocess.run(cmd, capture_output=True, text=True).stdout.strip())


def run(cmd, desc=""):
    print(f"    {desc}" if desc else f"    $ {' '.join(str(c) for c in cmd[:6])}...")
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"    FFMPEG ERR: {r.stderr[-400:]}")
        return False
    return True


# ─── Phase 1: Stills ──────────────────────────────────────────────────────────

def gen_still(prompt: str, seed: int, out_path: Path) -> bool:
    steps, cfg = ("25", "4") if IMAGE_WORKFLOW.startswith("z-image") else ("20", "4.0")
    data = {
        "prompt": prompt, "negative_prompt": IMAGE_NEG,
        "seed": str(seed), "steps": steps, "cfg": cfg,
        "width": str(WIDTH), "height": str(HEIGHT),
    }
    try:
        img = submit_and_wait(IMAGE_WORKFLOW, data, timeout=TIMEOUT_IMAGE)
    except Exception as e:
        print(f"    still ERR: {e}")
        return False
    if len(img) < 10_000:
        print(f"    still too small: {len(img)}")
        return False
    out_path.write_bytes(img)
    return True


def phase_stills(writer_ids, resume=True):
    for wid in writer_ids:
        md = SYN_DIR / f"{wid}.md"
        if not md.exists():
            print(f"  SKIP (no synopsis): {wid}")
            continue
        syn = parse_synopsis(md)
        seed_match = re.match(r'^T?(\d+)', wid)
        base_seed = int(seed_match.group(1)) * 97 + 9000 if seed_match else 9000
        print(f"\n[STILLS] {wid}")
        for i, key in enumerate(("v1", "v2", "v3"), start=1):
            prompt = syn[key]
            if not prompt:
                print(f"  v{i}: no prompt")
                continue
            out = STILLS_DIR / f"{wid}_{i}.jpg"
            if resume and out.exists() and out.stat().st_size > 10_000:
                print(f"  v{i}: exists, skip")
                continue
            print(f"  v{i}: {prompt[:70]}...")
            if gen_still(prompt, seed=base_seed + i, out_path=out):
                print(f"       OK {out.stat().st_size//1024}KB")


# ─── Phase 2: TTS voiceclone ──────────────────────────────────────────────────

def gen_voice(synopsis: str, voice_ref: Path, out_path: Path) -> bool:
    try:
        with open(voice_ref, "rb") as vf:
            files = {"voice": (voice_ref.name, vf, "audio/wav")}
            data = {"text": synopsis}
            audio = submit_and_wait(TTS_WORKFLOW, data, files=files, timeout=TIMEOUT_TTS)
    except Exception as e:
        print(f"    voice ERR: {e}")
        return False
    if len(audio) < 1_000:
        print(f"    voice too small: {len(audio)}")
        return False
    out_path.write_bytes(audio)
    return True


def phase_tts(writer_ids, resume=True):
    for wid in writer_ids:
        md = SYN_DIR / f"{wid}.md"
        if not md.exists():
            continue
        syn = parse_synopsis(md)
        if not syn["synopsis"]:
            print(f"  SKIP (no synopsis text): {wid}")
            continue
        voice_ref = MEDIA / wid / "voice.wav"
        if not voice_ref.exists():
            print(f"  SKIP (no voice ref): {wid}")
            continue
        out = VOICE_DIR / f"{wid}.wav"
        if resume and out.exists() and out.stat().st_size > 1_000:
            print(f"[TTS] {wid}: exists, skip")
            continue
        print(f"[TTS] {wid}: {syn['synopsis'][:60]}...")
        if gen_voice(syn["synopsis"], voice_ref, out):
            print(f"      OK {out.stat().st_size//1024}KB")


# ─── Phase 3: Assembly ────────────────────────────────────────────────────────

def build_pitch_clip(wid: str, out_path: Path) -> bool:
    """3 stills × (audio_dur/3) + synopsis audio."""
    stills = [STILLS_DIR / f"{wid}_{i}.jpg" for i in (1, 2, 3)]
    audio = VOICE_DIR / f"{wid}.wav"
    if not all(s.exists() for s in stills) or not audio.exists():
        print(f"    missing assets for {wid}")
        return False
    dur = probe_duration(audio)
    seg = dur / 3.0
    # One filtergraph: loop each still for seg seconds, concat as video, map audio
    cmd = [
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-loop", "1", "-t", f"{seg:.3f}", "-i", str(stills[0]),
        "-loop", "1", "-t", f"{seg:.3f}", "-i", str(stills[1]),
        "-loop", "1", "-t", f"{seg:.3f}", "-i", str(stills[2]),
        "-i", str(audio),
        "-filter_complex",
        "[0:v]scale=1280:720,fps=24,format=yuv420p[v0];"
        "[1:v]scale=1280:720,fps=24,format=yuv420p[v1];"
        "[2:v]scale=1280:720,fps=24,format=yuv420p[v2];"
        "[v0][v1][v2]concat=n=3:v=1:a=0[v]",
        "-map", "[v]", "-map", "3:a",
        "-c:v", "libx264", "-preset", "medium", "-crf", "20",
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
        "-shortest", "-movflags", "+faststart",
        str(out_path),
    ]
    return run(cmd, desc=f"pitch clip ({dur:.1f}s)")


def build_final(wid: str, pitch: Path, out_path: Path) -> bool:
    """intro.mp4 + pitch.mp4 via filtergraph concat with full re-encode."""
    intro = MEDIA / wid / "intro.mp4"
    if not intro.exists():
        print(f"    no intro for {wid}")
        return False
    cmd = [
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-i", str(intro),
        "-i", str(pitch),
        "-filter_complex",
        "[0:v]scale=1280:720,fps=24,setsar=1,format=yuv420p[v0];"
        "[1:v]scale=1280:720,fps=24,setsar=1,format=yuv420p[v1];"
        "[0:a]aresample=48000,aformat=sample_fmts=fltp:channel_layouts=stereo[a0];"
        "[1:a]aresample=48000,aformat=sample_fmts=fltp:channel_layouts=stereo[a1];"
        "[v0][a0][v1][a1]concat=n=2:v=1:a=1[v][a]",
        "-map", "[v]", "-map", "[a]",
        "-c:v", "libx264", "-preset", "medium", "-crf", "20",
        "-c:a", "aac", "-b:a", "192k",
        "-movflags", "+faststart",
        str(out_path),
    ]
    return run(cmd, desc="final (intro + pitch)")


def phase_assemble(writer_ids, resume=True):
    for wid in writer_ids:
        pitch = PITCH_DIR / f"{wid}.mp4"
        final = FINAL_DIR / f"{wid}.mp4"

        if resume and pitch.exists() and pitch.stat().st_size > 50_000:
            print(f"[PITCH] {wid}: exists, skip")
        else:
            print(f"[PITCH] {wid}")
            if not build_pitch_clip(wid, pitch):
                print(f"  FAILED pitch clip")
                continue

        if resume and final.exists() and final.stat().st_size > 50_000:
            print(f"[FINAL] {wid}: exists, skip")
            continue
        print(f"[FINAL] {wid}")
        build_final(wid, pitch, final)


# ─── Main ─────────────────────────────────────────────────────────────────────

def list_writers():
    """Active roster = all yaml_ids with a SYNOPSES/ file."""
    avail_syn = {f.stem for f in SYN_DIR.glob("*.md")} if SYN_DIR.exists() else set()
    return sorted(avail_syn)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", choices=["stills", "tts", "assemble", "all"], required=True)
    ap.add_argument("--writer", help="Single yaml_id")
    ap.add_argument("--project", help="Project directory path (default: projects/260414-visual-pitch-round)")
    ap.add_argument("--subdir", help="Output subdirectory under project (e.g. R2)")
    ap.add_argument("--image-model", choices=["z-image", "flux2-klein"], default="z-image")
    ap.add_argument("--no-resume", action="store_true")
    args = ap.parse_args()

    global PROJECT, IMAGE_WORKFLOW
    if args.project:
        PROJECT = Path(args.project) if Path(args.project).is_absolute() else ROOT / args.project
    IMAGE_WORKFLOW = {"z-image": "z-image-base-t2i", "flux2-klein": "flux2-klein-t2i"}[args.image_model]
    print(f"Image:   {IMAGE_WORKFLOW}")
    print(f"Project: {PROJECT}")

    set_subdir(args.subdir)

    if args.writer:
        writer_ids = [args.writer]
    else:
        writer_ids = list_writers()
    print(f"Writers: {len(writer_ids)}")
    print(f"Phase:   {args.phase}")

    resume = not args.no_resume

    if args.phase in ("stills", "all"):
        if not health():
            print("ComfyUI unreachable"); sys.exit(1)
        phase_stills(writer_ids, resume=resume)
    if args.phase in ("tts", "all"):
        if not health():
            print("ComfyUI unreachable"); sys.exit(1)
        phase_tts(writer_ids, resume=resume)
    if args.phase in ("assemble", "all"):
        phase_assemble(writer_ids, resume=resume)

    print("\nDone.")


if __name__ == "__main__":
    main()
