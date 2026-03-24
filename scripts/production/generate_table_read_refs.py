#!/usr/bin/env python3
"""
Table Read — Generate visual references for Mick Caffrey + table room + character poses.

Phases 1-3 of the table read pipeline:
  Phase 1: Mick Caffrey hero portrait (z-image-base-t2i) + CU at table (qwen-edit) + angle variant (qwen-multiangle)
  Phase 2: Table read room location (z-image-base-t2i)
  Phase 3: Character table poses — Mick/Neda/Kai CU at table (qwen-edit) + wide 3-person (z-image t2i)
"""

import io
import sys
import time
from pathlib import Path

from PIL import Image
import requests

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
COMFYUI_BASE = "http://192.168.1.181:8100"

PROJECT = Path(__file__).resolve().parents[2] / "projects" / "stray-signal"
REFS = PROJECT / "REFERENCES"
TABLE_READ = PROJECT / "PRODUCTION" / "EP01_v03" / "table_read"
OUT_REFS = TABLE_READ / "refs"
OUT_FRAMES = TABLE_READ / "frames"

# Source hero shots for character poses
NEDA_PORTRAIT = REFS / "hero_shots" / "v2" / "neda_portrait.png"
KAI_PORTRAIT = REFS / "hero_shots" / "v2" / "kai_portrait.png"

STYLE = (
    "Stylized sci-fi animation, graphic novel rendering with cinematic lighting, "
    "clean character silhouettes. "
)

MICK_DESC = (
    "Late 30s man, wiry athletic build, restless energy. Dark reddish-brown hair pushed back "
    "from forehead, 3-day stubble, sharp observant eyes with crow's feet. Worn black leather "
    "jacket over faded band t-shirt, dark jeans. A battered notebook with storyboard sketches "
    "in one hand. The posture of someone about to stand up again. "
)

NEDA_DESC = (
    "17-year-old girl, brown skin with warm undertone, black hair cropped short "
    "on sides with longer top pushed back, thin copper braid behind left ear, "
    "dark assessing eyes, angular jaw. Same face, same skin tone, same character. "
)

KAI_DESC = (
    "16-year-old boy, lean build not yet grown into his frame, observant eyes, "
    "short functional dark hair. Quiet presence. "
)

TABLE_ROOM_DESC = (
    "Production room blending brutalist and underground aesthetics. Concrete walls with "
    "rough texture, warm amber work-lights overhead — LED string lights and practical spots. "
    "Large worn wooden table center frame, scripts and storyboards scattered across it. "
    "Storyboards pinned to the concrete wall behind. The room has the cold geometry of "
    "the Grid but the warm amber light of the Seam. "
)

TARGET_W, TARGET_H = 1280, 720


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def submit_and_wait(workflow_id, params, files=None, timeout=600):
    url = f"{COMFYUI_BASE}/workflows/{workflow_id}"
    if files:
        resp = requests.post(url, data=params, files=files)
    else:
        resp = requests.post(url, data=params)
    resp.raise_for_status()
    job = resp.json()
    job_id = job["job_id"]
    start = time.time()
    deadline = start + timeout
    while time.time() < deadline:
        status = requests.get(f"{COMFYUI_BASE}/jobs/{job_id}").json()
        st = status.get("status", "unknown")
        if st == "completed":
            elapsed = time.time() - start
            print(f"    Done ({elapsed:.0f}s)")
            return requests.get(f"{COMFYUI_BASE}/jobs/{job_id}/result").content
        if st in ("error", "failed"):
            raise RuntimeError(f"Job {job_id} failed: {status.get('error')}")
        time.sleep(3)
    raise TimeoutError(f"Timeout on {job_id}")


def z_image_t2i(prompt, negative_prompt="", seed=42, steps=25, cfg=4.0,
                width=1024, height=1024):
    params = {
        "prompt": prompt,
        "negative_prompt": negative_prompt,
        "seed": str(seed),
        "steps": str(steps),
        "cfg": str(cfg),
        "width": str(width),
        "height": str(height),
    }
    return submit_and_wait("z-image-base-t2i", params)


def qwen_edit(prompt, image_path, image2_path=None, seed=42, steps=4):
    params = {"prompt": prompt, "seed": str(seed), "steps": str(steps)}
    fhs = []
    files = {}
    try:
        fh1 = open(image_path, "rb")
        fhs.append(fh1)
        files["image"] = (Path(image_path).name, fh1, "image/png")
        if image2_path:
            fh2 = open(image2_path, "rb")
            fhs.append(fh2)
            files["image2"] = (Path(image2_path).name, fh2, "image/png")
        return submit_and_wait("qwen-image-edit", params, files=files)
    finally:
        for fh in fhs:
            fh.close()


def qwen_multiangle(image_path, horizontal=15, vertical=5, seed=42, steps=4):
    """Camera angle variant via LoRA. Params must be ints, not strings. All >= 0."""
    fh = open(image_path, "rb")
    try:
        files = {"image": (Path(image_path).name, fh, "image/png")}
        params = {
            "horizontal_angle": horizontal,
            "vertical_angle": vertical,
            "seed": seed,
            "steps": steps,
        }
        return submit_and_wait("qwen-multiangle", params, files=files)
    finally:
        fh.close()


def normalize(png_bytes, w=TARGET_W, h=TARGET_H):
    img = Image.open(io.BytesIO(png_bytes))
    if img.size != (w, h):
        img = img.resize((w, h), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def save(data, path, norm_size=None):
    if norm_size:
        data = normalize(data, *norm_size)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as f:
        f.write(data)
    size = Image.open(io.BytesIO(data)).size
    print(f"    Saved: {path.name} ({size[0]}x{size[1]})")
    return path


NEGATIVE = (
    "blurry, oversaturated, pixelated, low resolution, distorted, noise, "
    "watermark, text, logo, subtitles, deformed, extra limbs, photograph, "
    "photorealistic, live action, Grid citizen, coverall, geometric collar"
)

# ---------------------------------------------------------------------------
# Asset definitions
# ---------------------------------------------------------------------------
ASSETS = [
    # --- PHASE 1: Mick Caffrey ---
    {
        "name": "mick_hero_portrait",
        "phase": 1,
        "method": "z-image-t2i",
        "output_dir": "refs",
        "seed": 8001,
        "width": 1024,
        "height": 1024,
        "prompt": (
            STYLE +
            "Portrait of a showrunner/director in a sci-fi animation style. " +
            MICK_DESC +
            "Warm amber side-lighting on concrete background. Head and shoulders, "
            "looking slightly off-camera with an intense, assessing gaze. Not a character "
            "in the show — a real-world creative rendered in the animation style. "
            "No geometric collar, no coveralls, no Grid uniform."
        ),
    },
    {
        "name": "mick_cu_at_table",
        "phase": 1,
        "method": "qwen-edit",
        "output_dir": "refs",
        "depends_on": ["table_read_room", "mick_hero_portrait"],
        "image": "table_read_room",
        "image2": "mick_hero_portrait",
        "seed": 8002,
        "prompt": (
            STYLE +
            "Close-up of a director seated at a large wooden table reading a script. " +
            MICK_DESC +
            "He leans forward over scattered scripts and storyboards. Amber work-lights "
            "cast warm side-lighting. Concrete walls behind. He looks like he's about to "
            "stand up and pace. The character from image 2 seated at the table in this room."
        ),
    },
    {
        "name": "mick_angle_variant",
        "phase": 1,
        "method": "qwen-multiangle",
        "output_dir": "refs",
        "depends_on": ["mick_hero_portrait"],
        "source": "mick_hero_portrait",
        "horizontal": 15,
        "vertical": 5,
        "seed": 8003,
    },

    # --- PHASE 2: Table Read Room ---
    {
        "name": "table_read_room",
        "phase": 2,
        "method": "z-image-t2i",
        "output_dir": "refs",
        "seed": 8010,
        "width": 1280,
        "height": 720,
        "prompt": (
            STYLE + TABLE_ROOM_DESC +
            "Wide shot of the empty room. No people. The table is the focal point. "
            "Warm amber light from overhead string lights contrasts with cool concrete walls. "
            "Storyboard panels pinned to the far wall. A few coffee cups on the table. "
            "Notebooks and scripts scattered. The aesthetic bridges brutalist Grid architecture "
            "with Seam warmth. Cinematic wide composition."
        ),
    },

    # --- PHASE 3: Character Table Poses ---
    {
        "name": "mick_cu_at_table",
        "phase": 3,
        "method": "qwen-edit",
        "output_dir": "frames",
        "depends_on": ["table_read_room", "mick_hero_portrait"],
        "image": "table_read_room",
        "image2": "mick_hero_portrait",
        "seed": 8020,
        "prompt": (
            STYLE +
            "Close-up of a director seated at a large wooden table in a production room. " +
            MICK_DESC +
            "Leaning forward, one hand on a script, other gesturing. Amber work-light "
            "on his face. Concrete walls behind with pinned storyboards. Scripts scattered "
            "on the table. Restless energy, mid-sentence. "
            "The character from image 2 at the table in this room."
        ),
    },
    {
        "name": "neda_cu_at_table",
        "phase": 3,
        "method": "qwen-edit",
        "output_dir": "frames",
        "depends_on": ["table_read_room"],
        "image": "table_read_room",
        "image2_path": NEDA_PORTRAIT,
        "seed": 8021,
        "prompt": (
            STYLE +
            "Close-up of a young woman seated at a large wooden table in a production room. " +
            NEDA_DESC +
            "She sits upright, script in front of her, hands resting on the table. "
            "Expression: present, thoughtful, in character. Amber work-light on her face. "
            "Concrete walls behind with pinned storyboards. "
            "The character from image 2 seated at the table in this room."
        ),
    },
    {
        "name": "kai_cu_at_table",
        "phase": 3,
        "method": "qwen-edit",
        "output_dir": "frames",
        "depends_on": ["table_read_room"],
        "image": "table_read_room",
        "image2_path": KAI_PORTRAIT,
        "seed": 8022,
        "prompt": (
            STYLE +
            "Close-up of a young man seated at a large wooden table in a production room. " +
            KAI_DESC +
            "He sits quietly, script in front of him, listening. Slightly hunched, "
            "taking it in. Amber work-light on his face. Concrete walls behind. "
            "The character from image 2 seated at the table in this room."
        ),
    },
    {
        "name": "table_read_wide",
        "phase": 3,
        "method": "z-image-t2i",
        "output_dir": "frames",
        "seed": 8025,
        "width": 1280,
        "height": 720,
        "prompt": (
            STYLE + TABLE_ROOM_DESC +
            "Wide shot of three people seated at the table during a script reading. "
            "CENTER: A wiry man in his late 30s with dark reddish-brown hair and a "
            "black leather jacket, leaning forward with restless energy, gesturing. "
            "LEFT: A 17-year-old girl with brown skin and short black hair, sitting "
            "upright with a script in front of her, attentive. "
            "RIGHT: A 16-year-old boy with dark hair, sitting quietly, listening. "
            "Scripts and storyboards scattered across the wooden table. Amber string "
            "lights overhead, concrete walls with pinned storyboards behind. "
            "The energy of a creative session in progress."
        ),
    },
]


# ---------------------------------------------------------------------------
# Resolve dependencies and generate
# ---------------------------------------------------------------------------
def get_output_path(asset):
    if asset["output_dir"] == "refs":
        return OUT_REFS / f"{asset['name']}.png"
    return OUT_FRAMES / f"{asset['name']}.png"


def find_asset(name):
    for a in ASSETS:
        if a["name"] == name:
            return a
    return None


def resolve_image_path(ref_name):
    """Resolve a ref name to its output path."""
    asset = find_asset(ref_name)
    if asset:
        return get_output_path(asset)
    return None


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Generate table read visual references")
    parser.add_argument("--phase", type=int, help="Run specific phase (1-3, or 0 for all)", default=0)
    parser.add_argument("--asset", type=str, help="Specific asset name", default=None)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--timeout", type=int, default=600)
    args = parser.parse_args()

    OUT_REFS.mkdir(parents=True, exist_ok=True)
    OUT_FRAMES.mkdir(parents=True, exist_ok=True)

    # Filter assets
    assets = ASSETS
    if args.asset:
        assets = [a for a in ASSETS if a["name"] == args.asset]
        if not assets:
            print(f"No asset '{args.asset}'. Available:")
            for a in ASSETS:
                print(f"  Phase {a['phase']}: {a['name']} ({a['method']})")
            sys.exit(1)
    elif args.phase > 0:
        assets = [a for a in ASSETS if a["phase"] == args.phase]

    # Deduplicate by name (mick_cu_at_table appears in Phase 1 and 3 — Phase 3 is the frame)
    seen = set()
    deduped = []
    for a in reversed(assets):  # prefer later definitions
        if a["name"] not in seen:
            seen.add(a["name"])
            deduped.append(a)
    assets = list(reversed(deduped))

    # Topological sort: z-image-t2i first (no deps), then qwen-edit, then qwen-multiangle
    method_order = {"z-image-t2i": 0, "qwen-edit": 1, "qwen-multiangle": 2}
    assets.sort(key=lambda a: (method_order.get(a["method"], 9), a["phase"], a["name"]))

    if args.dry_run:
        print(f"[DRY RUN] {len(assets)} assets:")
        for a in assets:
            out = get_output_path(a)
            exists = out.exists()
            deps = a.get("depends_on", [])
            dep_str = f" (needs: {', '.join(deps)})" if deps else ""
            print(f"  Phase {a['phase']}: {a['name']} [{a['method']}] "
                  f"{'EXISTS' if exists else 'pending'}{dep_str}")
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

    total = len(assets)
    done = 0
    failed = []

    for asset in assets:
        done += 1
        name = asset["name"]
        method = asset["method"]
        out_path = get_output_path(asset)

        if out_path.exists():
            print(f"\n  [{done}/{total}] Phase {asset['phase']}: {name} — SKIP (exists)")
            continue

        print(f"\n  [{done}/{total}] Phase {asset['phase']}: {name} [{method}]")

        try:
            if method == "z-image-t2i":
                data = z_image_t2i(
                    prompt=asset["prompt"],
                    negative_prompt=NEGATIVE,
                    seed=asset["seed"],
                    steps=25,
                    cfg=4.0,
                    width=asset.get("width", 1024),
                    height=asset.get("height", 1024),
                )
                norm = None
                if asset.get("width") == 1280:
                    norm = (1280, 720)
                save(data, out_path, norm_size=norm)

            elif method == "qwen-edit":
                # Resolve image paths
                img_ref = asset.get("image")
                img2_ref = asset.get("image2")
                img_path = resolve_image_path(img_ref) if img_ref else None
                img2_path = asset.get("image2_path") or resolve_image_path(img2_ref)

                if img_path and not img_path.exists():
                    print(f"    SKIP: dependency not ready: {img_path.name}")
                    failed.append(name)
                    continue
                if img2_path and not Path(img2_path).exists():
                    print(f"    SKIP: dependency not ready: {Path(img2_path).name}")
                    failed.append(name)
                    continue

                data = qwen_edit(
                    prompt=asset["prompt"],
                    image_path=img_path,
                    image2_path=img2_path,
                    seed=asset["seed"],
                    steps=4,
                )
                save(data, out_path, norm_size=(TARGET_W, TARGET_H))

            elif method == "qwen-multiangle":
                source_ref = asset.get("source")
                source_path = resolve_image_path(source_ref)
                if not source_path or not source_path.exists():
                    print(f"    SKIP: source not ready: {source_ref}")
                    failed.append(name)
                    continue

                data = qwen_multiangle(
                    image_path=source_path,
                    horizontal=asset.get("horizontal", 15),
                    vertical=asset.get("vertical", 5),
                    seed=asset.get("seed", 42),
                    steps=4,
                )
                save(data, out_path)

        except Exception as e:
            print(f"    FAILED: {e}")
            failed.append(name)

    if failed:
        print(f"\n  FAILED ({len(failed)}): {', '.join(failed)}")

    print(f"\n{'=' * 70}")
    print(f"DONE — {done} table read assets processed")
    print(f"{'=' * 70}")
