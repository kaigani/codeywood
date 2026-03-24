#!/usr/bin/env python3
"""
Final frame selects for EP01_v02.

User selects:
  clip_04_device_crack_warmth_v2   → keep as-is
  clip_07_r2_stage1                → master for all Kai-looking-at-screen shots
  clip_09_multitool_down_v1        → keep as-is
  clip_11_tabs_points_northeast_v2 → concept drives all screen-content shots

Work to do:
  1. Generate clean z-image screen base at 1280x720 (clip_11 concept, native 16:9)
  2. Edit clip_07_r2_stage1 → clip_07 final (first encounter expression)
  3. Edit clip_07_r2_stage1 → clip_10 final (watching/guarded expression)
  4. Edit z-image screen base → clip_08 (DELETE prompt + TABS settled)
  5. z-image screen base IS clip_11 final (TABS pointing)
  6. Edit z-image screen base → clip_14 (TABS paw at screen edge)

Screen shots show only what's on the screen — tight on screen content,
device bezel at edges for context, screen filling the frame.
"""

import io
import sys
import time
from pathlib import Path

from PIL import Image
import requests

COMFYUI_BASE = "http://192.168.1.181:8100"
TARGET_W, TARGET_H = 1280, 720

PROJECT = Path(__file__).resolve().parents[2] / "projects" / "stray-signal"
REFS    = PROJECT / "REFERENCES"
FRAMES  = PROJECT / "PRODUCTION" / "EP01_v02" / "frames"

TABS_DIR     = REFS / "object_refs" / "tabs_poses"
TABS_SETTLED = TABS_DIR / "tabs_settled_patience.png"
TABS_PAW     = TABS_DIR / "tabs_paw_reaching.png"

KAI_DIR      = REFS / "character_poses" / "kai"
KAI_CU_RIGHT = KAI_DIR / "kai_cu_look_right.png"
KAI_WATCHING = KAI_DIR / "kai_at_desk_watching.png"

# User-selected masters
MASTER_KAI_SCREEN = FRAMES / "clip_07_r2_stage1.png"   # Kai looking at device


# ─── ComfyUI helpers ──────────────────────────────────────────────────────────

def submit_and_wait(workflow_id, params, files=None, timeout=600, poll_interval=3):
    url = f"{COMFYUI_BASE}/workflows/{workflow_id}"
    resp = requests.post(url, data=params, files=files) if files else requests.post(url, data=params)
    resp.raise_for_status()
    job = resp.json()
    job_id = job["job_id"]
    print(f"    job {job_id} (pos {job.get('position', '?')})")
    deadline = time.time() + timeout
    polls = 0
    while time.time() < deadline:
        s = requests.get(f"{COMFYUI_BASE}/jobs/{job_id}").json()
        polls += 1
        if s["status"] == "completed":
            print(f"    done in {time.time()-(deadline-timeout):.1f}s")
            return requests.get(f"{COMFYUI_BASE}/jobs/{job_id}/result").content
        if s["status"] == "error":
            raise RuntimeError(f"Job {job_id} failed: {s.get('error')}")
        time.sleep(2 if polls <= 5 else poll_interval)
    raise TimeoutError(f"Timed out after {timeout}s")


def z_image_t2i(prompt, seed=42, steps=25, cfg=4):
    """Generate at native 1280x720 — no resize drift."""
    params = {
        "prompt": prompt,
        "negative_prompt": "hologram, 3D projection, floating, glowing orb, bloom, lens flare, photorealistic, photograph",
        "seed": str(seed),
        "steps": str(steps),
        "cfg": str(cfg),
        "width": str(TARGET_W),
        "height": str(TARGET_H),
    }
    return submit_and_wait("z-image-base-t2i", params)


def qwen_edit(prompt, image, image2=None, seed=42, steps=4):
    params = {"prompt": prompt, "seed": str(seed), "steps": str(steps)}
    handles, files = [], {}
    try:
        fh = open(image, "rb"); handles.append(fh)
        files["image"] = (Path(image).name, fh, "image/png")
        if image2:
            fh2 = open(image2, "rb"); handles.append(fh2)
            files["image2"] = (Path(image2).name, fh2, "image/png")
        return submit_and_wait("qwen-image-edit", params, files=files)
    finally:
        for fh in handles: fh.close()


def save_raw(data, path):
    """Save without normalizing — z-image output is already 1280x720."""
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as f: f.write(data)
    size = Image.open(io.BytesIO(data)).size
    print(f"    saved: {path.name} ({size[0]}x{size[1]})")
    return path


def save_norm(data, path):
    """Normalize qwen-edit output to 1280x720 (handles dimension drift)."""
    img = Image.open(io.BytesIO(data))
    if img.size != (TARGET_W, TARGET_H):
        print(f"    resize {img.size} → {TARGET_W}x{TARGET_H}")
        img = img.resize((TARGET_W, TARGET_H), Image.LANCZOS)
    buf = io.BytesIO(); img.save(buf, "PNG")
    data = buf.getvalue()
    return save_raw(data, path)


def header(label):
    print(f"\n{'='*60}\n{label}\n{'='*60}")


# ─── Steps ────────────────────────────────────────────────────────────────────

def step1_screen_base():
    """
    Generate clean z-image screen base at native 1280x720.
    TABS pointing on device screen. Screen fills frame. No hologram.
    This becomes clip_11 final AND the edit base for clips 08 and 14.
    """
    header("STEP 1 — z-image screen base (TABS pointing, native 16:9)")
    data = z_image_t2i(
        prompt=(
            "Stylized sci-fi animation, graphic novel rendering. "
            "POV close-up of a rugged handheld device screen filling the frame. "
            "The screen is dark — nearly black background. On the screen: "
            "a wireframe geometric cat in electric cyan, angular polygon facets, "
            "visible geometric planes, ears slightly too large. "
            "The cat is in a pointing posture — seated, body oriented, weight "
            "forward, one forepaw extended to the right pointing outward. "
            "Concentric cyan pulse rings radiate outward from the cat across "
            "the black screen. The device frame — brushed aluminum, industrial "
            "rivets, thick bezel — is visible at the very edges of the frame. "
            "Hairline crack across the lower portion of the screen glass. "
            "The cat and pulse rings are the only light source on the screen. "
            "Screen fills 85 percent of the frame. Flat 2D screen display, "
            "not a hologram, not projected. Animation style, clean linework."
        ),
        seed=1101,
    )
    path = save_raw(data, FRAMES / "clip_11_screen_base.png")
    return path


def step2_clip11_final(screen_base):
    """clip_11 is the screen base itself — copy to final name."""
    header("STEP 2 — clip_11 final (screen base is the final frame)")
    import shutil
    out = FRAMES / "clip_11_tabs_points_northeast_final.png"
    shutil.copy2(screen_base, out)
    print(f"    copied: {out.name}")
    return out


def step3_clip08(screen_base):
    """
    Edit screen base: replace TABS pointing with TABS settled,
    add DELETE prompt in institutional red.
    """
    header("STEP 3 — clip_08 (DELETE prompt + TABS settled)")
    data = qwen_edit(
        prompt=(
            "In this device screen image, make two changes: "
            "1) The wireframe cat is now in a settled patience pose — paws "
            "tucked underneath its body, sitting in the corner of the screen, "
            "looking away deliberately to one side. Not pointing. Settled. "
            "2) In the upper area of the screen, add a text prompt that reads "
            "'DELETE' in a plain institutional red — clean sans-serif characters, "
            "like a government or military UI system. No decorative styling. "
            "Keep the dark screen, the device frame at edges, and the hairline "
            "crack exactly the same."
        ),
        image=screen_base,
        image2=TABS_SETTLED,
        seed=801,
    )
    return save_norm(data, FRAMES / "clip_08_delete_sequence_final.png")


def step4_clip14(screen_base):
    """
    Edit screen base: TABS at left edge of screen, one paw reaching
    toward the screen boundary. Tight on screen content.
    """
    header("STEP 4 — clip_14 (TABS paw at screen edge)")
    data = qwen_edit(
        prompt=(
            "In this device screen image, reposition the wireframe cat: "
            "it is now at the left edge of the screen, facing outward toward "
            "the screen boundary. One paw is extended toward the screen edge — "
            "reaching, hovering at the glass boundary, not quite touching. "
            "The cat looks out beyond the screen. The cat's pose comes from "
            "image 2. The pulse rings are gone — only the cat and the dark "
            "screen. Keep the device frame at edges, hairline crack. "
            "The reaching paw is a small cat paw — not enlarged."
        ),
        image=screen_base,
        image2=TABS_PAW,
        seed=1401,
    )
    return save_norm(data, FRAMES / "clip_14_tabs_paw_at_glass_final.png")


def step5_clip07():
    """
    Edit clip_07_r2_stage1: first encounter expression.
    Kai's eyes wider, slightly more open — the moment TABS first appears.
    """
    header("STEP 5 — clip_07 (first encounter, from Kai master)")
    data = qwen_edit(
        prompt=(
            "In this image, adjust the boy's expression: his eyes are slightly "
            "wider — the first moment of genuine surprise, not fear. Mouth "
            "closed, jaw relaxed. He leans forward a centimeter more toward "
            "the device. The dual lighting (amber lamp left, cyan glow right) "
            "remains exactly the same. Keep the room, the desk, the lamp, "
            "and everything else exactly the same."
        ),
        image=MASTER_KAI_SCREEN,
        seed=701,
    )
    return save_norm(data, FRAMES / "clip_07_tabs_appears_final.png")


def step6_clip10():
    """
    Edit clip_07_r2_stage1: guarded watching expression.
    Same composition, different emotional register from clip_07.
    """
    header("STEP 6 — clip_10 (guarded watching, from Kai master)")
    data = qwen_edit(
        prompt=(
            "In this image, adjust the boy's expression: his brow is slightly "
            "furrowed — guarded but not hostile, watchful. He is watching "
            "something carefully, deciding whether to trust it. His eyes are "
            "narrowed just slightly, lips pressed together. More closed than "
            "clip 7. The dual lighting (amber lamp left, cyan glow right) "
            "remains exactly the same. Keep the room, the desk, the lamp, "
            "and everything else exactly the same."
        ),
        image=MASTER_KAI_SCREEN,
        seed=1001,
    )
    return save_norm(data, FRAMES / "clip_10_tabs_reads_maps_final.png")


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    try:
        h = requests.get(f"{COMFYUI_BASE}/health", timeout=5).json()
        if not h.get("comfyui_reachable"):
            print("ERROR: ComfyUI not reachable"); sys.exit(1)
        print("ComfyUI: OK")
    except Exception as e:
        print(f"ERROR: {e}"); sys.exit(1)

    if not MASTER_KAI_SCREEN.exists():
        print(f"ERROR: Kai master not found: {MASTER_KAI_SCREEN}"); sys.exit(1)

    print(f"\nKai master: {MASTER_KAI_SCREEN.name}")
    print(f"Output: {FRAMES}")

    t0 = time.time()

    screen_base = step1_screen_base()
    step2_clip11_final(screen_base)
    step3_clip08(screen_base)
    step4_clip14(screen_base)
    step5_clip07()
    step6_clip10()

    elapsed = time.time() - t0
    print(f"\n{'='*60}")
    print(f"DONE — 6 steps in {elapsed/60:.1f}m  ($0.00)")
    print(f"\nFinal frames:")
    print(f"  clip_07 → clip_07_tabs_appears_final.png")
    print(f"  clip_08 → clip_08_delete_sequence_final.png")
    print(f"  clip_10 → clip_10_tabs_reads_maps_final.png")
    print(f"  clip_11 → clip_11_tabs_points_northeast_final.png")
    print(f"  clip_14 → clip_14_tabs_paw_at_glass_final.png")
    print("="*60)


if __name__ == "__main__":
    main()
