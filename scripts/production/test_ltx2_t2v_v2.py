#!/usr/bin/env python3
"""
LTX-2 text-to-video test v2 — improved prompts with setting, period, and character specificity.

Changes from v1:
  - Caribbean colonial setting anchors in every shot
  - 18th century period-specific costume details
  - Literal, descriptive language (what the camera sees)
  - Character physical descriptions explicit and complete
  - Extra detail where composition might be ambiguous
"""

import json
import sys
import time
from pathlib import Path

import requests
import yaml

# ─── Config ───────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).parent.parent.parent / "projects" / "pirate-romance"
SCENE_DIR = PROJECT_ROOT / "PRODUCTION" / "EP01" / "sc01"
OUTPUT_DIR = SCENE_DIR / "t2v_test_v2"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

COMFYUI_URL = "http://192.168.1.181:8100"
WORKFLOW = "ltx2-t2v"
FPS = 25
TIMEOUT = 900

NEGATIVE_PROMPT = "blur, distort, low quality, cartoon, anime, deformed, extra limbs, text, watermark, modern clothing, contemporary architecture"


def duration_to_frame_count(seconds, fps=25):
    raw = round(seconds * fps) + 1
    return max(25, min(raw, 321))


def generate_t2v(prompt, frame_count, seed=None, width=1280, height=720):
    url = f"{COMFYUI_URL}/workflows/{WORKFLOW}"
    data = {
        "prompt": prompt,
        "negative_prompt": NEGATIVE_PROMPT,
        "frame_count": str(frame_count),
        "width": str(width),
        "height": str(height),
    }
    if seed is not None:
        data["seed"] = str(seed)

    response = requests.post(url, data=data, timeout=TIMEOUT)

    if response.status_code == 200 and len(response.content) > 10000:
        return response.content
    else:
        print(f"  ERROR: HTTP {response.status_code}, {len(response.content)} bytes")
        if response.status_code != 200:
            print(f"  {response.text[:300]}")
        return None


# ─── Improved T2V Prompts ─────────────────────────────────────────────
SHOTS = [
    {
        "id": 1,
        "name": "The Rope",
        "duration": 5,
        "prompt": (
            "Extreme close-up filling the entire frame. A thick coil of heavy braided "
            "hemp rope resting on sun-bleached timber. The rope is coiled flat on the "
            "wood surface like a sleeping snake. The wood grain is deep, cracked, and "
            "salt-weathered from decades of Caribbean sun and sea air. An iron bracket "
            "is visible at the edge of the wood. Late afternoon golden sunlight rakes "
            "across the textured surfaces at a low angle. Dust motes float slowly "
            "through the warm light. A faint vibration trembles through the heavy "
            "timber. A single loose hemp fiber stirs in the warm breeze. The wood "
            "creaks faintly. No people visible, no surroundings, just rope and wood "
            "and golden light."
        ),
    },
    {
        "id": 2,
        "name": "Gallows Square — The Reveal",
        "duration": 10,
        "prompt": (
            "Slow cinematic push forward into a Caribbean colonial port town square, "
            "18th century. Two-story and three-story stucco buildings painted in bright "
            "Caribbean colors — deep burgundy, sea-teal, coral pink, faded yellow — "
            "line every side of the cobblestone square. Wooden shutters and wrought-iron "
            "balconies on the upper floors. At the center of the square stands a raised "
            "wooden platform built from heavy sun-bleached timber, with vertical posts "
            "and a horizontal crossbar. A dense crowd of hundreds fills the square — "
            "men in linen shirts and leather vests, women in long cotton dresses and "
            "headscarves, children sitting on shoulders. Street vendors push wooden "
            "carts. The atmosphere is loud and chaotic like a festival. Golden late "
            "afternoon sunlight bathes everything in warm amber. Seabirds wheel "
            "overhead against a vivid blue Caribbean sky. Palm fronds are visible "
            "above the rooftops. The camera drifts slowly forward through the crowd "
            "toward the wooden platform."
        ),
    },
    {
        "id": 3,
        "name": "Mars in the Crowd",
        "duration": 10,
        "prompt": (
            "Static medium shot in a Caribbean colonial town square, 18th century. "
            "Pastel-colored stucco buildings are visible in the soft background blur. "
            "At center frame, a young woman of mixed Caribbean heritage in her early "
            "twenties stands perfectly frozen among a dense jostling crowd. She has "
            "thick dark curly hair partially visible beneath a dark blue-grey woven "
            "shawl draped over her head and shoulders. Sun-darkened olive skin with "
            "visible freckles across her nose and cheekbones. Sharp dark eyes fixed "
            "straight ahead, unblinking. Her jaw is clenched tight. Her fingers slowly "
            "twist the shawl fabric at her chest — the only sign she is breathing. "
            "Around her, the 18th century crowd jostles and presses — elbows, "
            "shoulders, backs bumping past her. Men in rough linen shirts, women in "
            "cotton dresses. Bodies flow around her like water around a stone. She does "
            "not flinch, does not turn her head, does not react. Golden afternoon "
            "sunlight catches her dark eyes. Shallow depth of field, crowd blurred "
            "around her sharp stillness."
        ),
    },
    {
        "id": 4,
        "name": "Silas Ascends",
        "duration": 8,
        "prompt": (
            "Static low-angle shot looking upward from below and behind. An outdoor "
            "Caribbean colonial town square, 18th century. A tall lean man in his late "
            "forties walks steadily upward on wide sun-bleached wooden steps, his back "
            "to the camera. He has salt-and-pepper hair pulled back in a loose tie, "
            "visible from behind. He wears a threadbare off-white linen shirt — a "
            "prisoner stripped of coat and possessions. His hands are bound behind his "
            "back with rough rope, ink stains visible on his fingers. Two soldiers in "
            "bright red British colonial coats with white crossbelts and black tricorn "
            "hats walk on either side of him on the steps. The man walks with unhurried "
            "steady steps, head held level, shoulders back — not defeated. Golden "
            "afternoon backlight haloes his hair from above. Vivid blue Caribbean sky "
            "overhead. The camera looks up at him from below as he ascends, one step "
            "then another."
        ),
    },
    {
        "id": 5,
        "name": "The Sentence",
        "duration": 8,
        "prompt": (
            "Static wide shot of a raised wooden platform in the center of a "
            "Caribbean colonial cobblestone town square, 18th century. The platform is "
            "built from heavy sun-bleached timber with iron bracket hardware, standing "
            "four feet above the ground. On the platform: a man in dark formal 18th "
            "century attire holds an unrolled parchment scroll and reads aloud, his "
            "voice carrying over the hushed crowd. He speaks clearly, projecting: "
            "'Silas Blackwood. For crimes of treason, smuggling, and commerce with "
            "enemies of the Crown.' Beside him stands a tall man with salt-and-pepper hair in a "
            "threadbare linen shirt, hands bound behind his back, watching the crowd "
            "with calm detachment. A thick hemp rope loop hangs from the wooden "
            "crossbar overhead to his right. Red-coated soldiers stand at the edges of "
            "the platform. Below, a dense crowd of 18th century townspeople watches in "
            "near silence. Behind the platform, two-story Caribbean stucco buildings "
            "painted in bright colors — burgundy, teal, coral — frame the scene. "
            "Golden afternoon light. Vivid blue sky. The crowd is hushed and still."
        ),
    },
    {
        "id": 6,
        "name": "The Smile",
        "duration": 12,
        "prompt": (
            "Static close-up of a man's face filling the frame. He is in his late "
            "forties with deeply weathered sun-darkened skin, prominent lines around "
            "his eyes and mouth, salt-and-pepper stubble on his jaw, and grey-streaked "
            "hair pulled back. Ink traces are faintly visible on his jawline. Strong "
            "golden afternoon key light from the right side illuminates half his face, "
            "the other half in warm shadow. A soft golden blur of a crowd fills the "
            "background. His eyes search slowly, scanning from left to right, looking "
            "past the camera into the distance. Patient, methodical. Then his eyes "
            "stop — he has found someone. The corner of his mouth lifts. A slow, "
            "genuine smile spreads across his face, deepening the lines around his "
            "eyes. His lips move, whispering barely audible words meant only for her: "
            "'Good girl.' His "
            "eyes are bright, glistening. The smile holds — warm, steady, unwavering. "
            "Wind stirs his hair. Near silence."
        ),
    },
    {
        "id": 7,
        "name": "Mars — The Weight",
        "duration": 12,
        "prompt": (
            "Static close-up of a young woman's face and upper chest. She is in her "
            "early twenties with sun-darkened olive skin and visible freckles across "
            "her nose and cheekbones. Thick dark curly hair frames her face beneath a "
            "dark blue-grey woven shawl draped over her head. Her jaw is clenched, her "
            "dark eyes wide and fixed straight ahead, watching something in front of "
            "her. Her right hand is pressed flat against her chest over her linen "
            "shirt, just below the collarbone. Behind her, blurred figures of an 18th "
            "century crowd in warm golden light. She does not cry. She does not speak. "
            "Her eyes track something that moves slowly downward. The crowd murmur "
            "fades. Her lips part slightly. A hard swallow moves her throat. Her "
            "whispered voice, barely audible: 'He told me once — the sea doesn't "
            "reward sentiment. It rewards preparation.' Silence. Her eyes track "
            "something that moves and stops. 'He was right.' The smallest nod, barely "
            "perceptible. Her eyes close for one second, then open again — the muscles "
            "around her eyes tighten. 'I don't know what that makes me.' The light "
            "shifts slowly from gold to deeper amber. She does not look away."
        ),
    },
    {
        "id": 8,
        "name": "The Drop — Crowd Surge",
        "duration": 5,
        "prompt": (
            "Static wide shot from behind and slightly above a dense crowd of hundreds "
            "of people in a Caribbean colonial cobblestone town square, 18th century. "
            "The camera sees the backs of hundreds of heads — straw hats, cloth "
            "headscarves, bare heads, tricorn hats — all packed together facing the "
            "same direction. The crowd wears 18th century Caribbean clothing: linen, "
            "cotton, leather. On both sides of the frame, two-story stucco buildings "
            "painted in bright Caribbean colors — burgundy, teal, coral pink — frame "
            "the square. Beyond the crowd in the middle distance, a raised wooden "
            "platform is visible, small in the frame. A collective gasp — the crowd "
            "surges forward as one body. Arms rise, hands go to mouths. Bodies press "
            "forward, stumbling against each other. The sound erupts — a roar of "
            "hundreds of voices. Some people turn away, some press closer. The wave "
            "of reaction moves through the dense crowd."
        ),
    },
    {
        "id": 9,
        "name": "She Remains",
        "duration": 10,
        "prompt": (
            "Static wide shot of a Caribbean colonial cobblestone town square, 18th "
            "century. Late afternoon light, golden shifting to amber, long shadows "
            "stretching across the cobblestones. Two-story pastel stucco buildings — "
            "burgundy, teal, faded yellow — line the edges of the square. The crowd "
            "is dispersing — people walking away in all directions, the event over. "
            "Men in linen shirts, women carrying children, vendors pushing carts, all "
            "moving toward the edges of the frame. At the center of the frame, one "
            "figure stands absolutely still: a young woman in a dark blue-grey shawl "
            "draped over her head and shoulders, facing toward a raised wooden platform "
            "visible in the middle distance. She is the only person not moving. Bodies "
            "stream past her on all sides without a glance. The square empties around "
            "her. Her shadow stretches long and dark across the cobblestones. The "
            "silence grows as the footsteps and voices recede."
        ),
    },
    {
        "id": 10,
        "name": "Mars Departs",
        "duration": 8,
        "prompt": (
            "Medium shot of a young woman viewed from a three-quarter angle as she "
            "walks with steady purpose down a narrow cobblestone alley between "
            "Caribbean colonial buildings, 18th century. She wears a dark blue-grey "
            "woven shawl over her head and shoulders. Thick dark curly hair is visible "
            "beneath the shawl. Sun-darkened olive skin. She is walking away from the "
            "camera at an angle, head down, pace deliberate and controlled. Not "
            "running. The nearly empty cobblestone square is visible behind her, a few "
            "stragglers walking. Ahead of her, the narrow alley is shadowed between "
            "two-story stucco buildings painted in faded Caribbean colors — teal and "
            "coral. Amber late afternoon light catches the shawl as she moves forward. "
            "She does not look back. She walks into the shadow of the alley, the "
            "golden light giving way to cool blue shadow between the buildings. Steady "
            "boot steps on cobblestone. A distant bell tolls."
        ),
    },
    {
        "id": 11,
        "name": "Final Image",
        "duration": 8,
        "prompt": (
            "Static wide shot looking straight upward at an empty wooden beam "
            "structure against a vivid blue sky. The sky fills most of the frame — "
            "intensely blue, cloudless, oversaturated. Two thick vertical wooden posts "
            "rise from the lower corners of the frame, supporting a heavy horizontal "
            "crossbar across the upper portion. The wood is sun-bleached pale and "
            "weathered, salt-cracked with visible grain. A thick hemp rope hangs from "
            "the crossbar, swaying gently in a warm breeze. Iron bracket hardware "
            "where the posts meet the crossbar. A single water droplet clings to the "
            "underside of the wood, catching the bright sunlight. The structure is "
            "empty now. Late afternoon light, everything too bright, the colors "
            "oversaturated and vivid. Wind blows. The timber creaks softly. Silence."
        ),
    },
]


def main(only_shots=None):
    shots_to_run = [s for s in SHOTS if only_shots is None or s["id"] in only_shots]
    total = len(shots_to_run)
    results = {}
    start_time = time.time()

    print(f"LTX-2 Text-to-Video Test v2 — Improved Prompts")
    print(f"Workflow: {WORKFLOW} ({FPS}fps, 1280x720)")
    print(f"Output: {OUTPUT_DIR}")
    if only_shots:
        print(f"Re-running shots: {only_shots}")
    print(f"Shots: {total}")
    print()

    for i, shot in enumerate(shots_to_run):
        shot_id = shot["id"]
        name = shot["name"]
        duration = shot["duration"]
        prompt = shot["prompt"]
        frame_count = duration_to_frame_count(duration)

        safe_name = name.lower().replace(" ", "_").replace("—", "").replace("'", "").strip("_")
        output_name = f"t2v2_{shot_id:02d}_{safe_name}"

        print(f"{'='*60}")
        print(f"--- {output_name} ({duration}s, {frame_count} frames) [{i+1}/{total}] ---")
        print(f"{'='*60}")
        print(f"  Prompt ({len(prompt)} chars):")
        print(f"  {prompt[:200]}...")
        print()

        t0 = time.time()
        video_bytes = generate_t2v(
            prompt=prompt,
            frame_count=frame_count,
            width=1280,
            height=720,
        )
        elapsed = time.time() - t0

        if video_bytes:
            out_path = OUTPUT_DIR / f"{output_name}.mp4"
            with open(out_path, "wb") as f:
                f.write(video_bytes)

            meta = {
                "shot_id": shot_id,
                "shot_name": name,
                "duration_s": duration,
                "frame_count": frame_count,
                "workflow": WORKFLOW,
                "width": 1280,
                "height": 720,
                "video_prompt": prompt,
                "negative_prompt": NEGATIVE_PROMPT,
                "elapsed_s": round(elapsed, 1),
                "bytes": len(video_bytes),
                "mode": "t2v_v2_improved",
            }
            with open(out_path.with_suffix(".json"), "w") as f:
                json.dump(meta, f, indent=2)

            mb = len(video_bytes) / (1024 * 1024)
            print(f"  OK: {mb:.1f}MB, {elapsed:.1f}s")
            results[shot_id] = f"OK ({elapsed:.1f}s)"
        else:
            print(f"  FAILED")
            results[shot_id] = "FAILED"

        if i < total - 1:
            elapsed_total = time.time() - start_time
            avg = elapsed_total / (i + 1)
            remaining = avg * (total - i - 1)
            print(f"  [{i+1}/{total} done, ~{remaining/60:.0f}m remaining]")
        print()

    # Summary
    total_elapsed = time.time() - start_time
    print(f"{'='*60}")
    print(f"SUMMARY — {total} clips in {total_elapsed/60:.1f}m")
    print(f"{'='*60}")
    for shot in shots_to_run:
        sid = shot["id"]
        name = shot["name"]
        status = results.get(sid, "SKIPPED")
        print(f"  Shot {sid} ({name}): {status}")


if __name__ == "__main__":
    try:
        r = requests.get(f"{COMFYUI_URL}/health", timeout=5)
        if r.status_code != 200:
            print(f"ERROR: ComfyUI not healthy: {r.text}")
            sys.exit(1)
    except Exception as e:
        print(f"ERROR: ComfyUI not reachable at {COMFYUI_URL}: {e}")
        sys.exit(1)

    # Parse --shots 5,6,7 flag
    only_shots = None
    for arg in sys.argv[1:]:
        if arg.startswith("--shots="):
            only_shots = [int(x) for x in arg.split("=")[1].split(",")]
        elif arg == "--shots" and sys.argv.index(arg) + 1 < len(sys.argv):
            only_shots = [int(x) for x in sys.argv[sys.argv.index(arg) + 1].split(",")]

    main(only_shots=only_shots)
