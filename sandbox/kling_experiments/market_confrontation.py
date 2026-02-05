#!/usr/bin/env python3
"""
Kling 3.0 Pro - Market Confrontation Scene

Continuation from market_scene: Mars confronts the produce seller about
suspicious cursed objects she found in the back of his stall.

Uses:
- market_scene_end-frame.png as starting frame
- Mars identity sheet as @Element1 (character consistency)
- Native audio with dialogue embedded in prompts
- Multi-prompt for 3 cuts
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

import fal_client

# Paths
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
PIRATE_PROJECT = PROJECT_ROOT / "projects" / "pirate-romance"
EXPORTS = PIRATE_PROJECT / "EXPORTS"
OUTPUT_DIR = SCRIPT_DIR / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)

# Input images
START_FRAME = SCRIPT_DIR / "market_scene_end-frame.png"


def upload_image(filepath: Path) -> str:
    """Upload a local image and return the FAL URL."""
    print(f"  Uploading: {filepath.name}")
    url = fal_client.upload_file(str(filepath))
    print(f"    ✓ {url[:60]}...")
    return url


def find_latest_image(directory: Path, pattern: str) -> Path:
    """Find the most recent image matching pattern."""
    matches = list(directory.glob(pattern))
    if not matches:
        raise FileNotFoundError(f"No files matching {pattern} in {directory}")
    return sorted(matches, key=lambda p: p.stat().st_mtime, reverse=True)[0]


def run_market_confrontation():
    """
    Create a 3-cut scene: Mars confronts the produce seller about cursed objects.
    """
    print("\n" + "#" * 70)
    print("# MARKET CONFRONTATION: Mars accuses the seller")
    print("# 3 cuts: Accusation → Seller's reaction → Mars demands answers")
    print("#" * 70)

    # Verify start frame exists
    if not START_FRAME.exists():
        print(f"ERROR: {START_FRAME} not found")
        return None

    # Upload starting frame (end of previous scene)
    print("\nUploading starting frame...")
    start_url = upload_image(START_FRAME)

    # NOTE: Custom Voice IDs are NOT supported with Elements in Kling 3.0
    # Prioritizing character consistency via elements over custom voice
    print("\nUploading Mars character references...")
    mars_identity = find_latest_image(EXPORTS / "identity_sheets", "mars_identity_*.png")
    mars_entrance = find_latest_image(EXPORTS / "hero_shots" / "mars", "mars_entrance_*.png")

    mars_frontal = upload_image(mars_identity)
    mars_ref = upload_image(mars_entrance)

    # Build element for Mars (character consistency)
    elements = [
        {
            "frontal_image_url": mars_frontal,
            "reference_image_urls": [mars_ref],
        }
    ]

    # Multi-prompt: 3 cuts with @Element1 for character consistency
    # Dialogue is embedded directly in prompts for native audio generation
    multi_prompt = [
        {
            "prompt": "Medium shot, @Element1 steps forward confrontationally toward the produce seller, "
                      "she points accusingly at the glowing bottles on the shelves behind him and says "
                      "'What are those things in the back? I saw them glowing.' "
                      "Suspicious expression, afternoon market lighting, shallow depth of field",
            "duration": "4"
        },
        {
            "prompt": "Close-up reaction shot of the produce seller, middle-aged man's face shifts from "
                      "friendly to nervous, he stammers 'I don't know what you mean, miss.' "
                      "He glances back at his shelves, beads of sweat forming, "
                      "warm golden market lighting, cinematic tension",
            "duration": "3"
        },
        {
            "prompt": "Over-shoulder shot from behind seller, @Element1 leans in closer with narrowing eyes, "
                      "she says 'Don't lie to me. I know a curse when I see one.' "
                      "Her expression hardens with determination, confrontational body language, "
                      "dramatic lighting shift, cinematic tension builds",
            "duration": "3"
        }
    ]

    print(f"\n{'=' * 70}")
    print("KLING 3.0 PRO: Market Confrontation (with Elements)")
    print(f"{'=' * 70}")
    print(f"\nSTARTING FRAME: {START_FRAME.name}")
    print(f"\nELEMENTS:")
    print(f"  @Element1: Mars (identity sheet + hero shot)")
    print(f"\nVOICE: Native audio (no custom voice - incompatible with elements)")
    print(f"\nMULTI-PROMPT ({len(multi_prompt)} cuts):")
    for i, p in enumerate(multi_prompt):
        prompt_preview = p["prompt"][:70] + "..."
        print(f"  [{i+1}] ({p['duration']}s) {prompt_preview}")

    # Build request
    # NOTE: Using elements for character consistency, native audio (no voice_ids)
    request = {
        "start_image_url": start_url,
        "multi_prompt": multi_prompt,
        "elements": elements,
        "duration": "10",  # 4 + 3 + 3 = 10 seconds
        "aspect_ratio": "16:9",
        "generate_audio": True,
        "negative_prompt": "blur, distort, low quality, cartoon, anime, deformed hands, multiple faces",
    }

    # Estimate cost (with native audio, no voice control)
    cost_per_sec = 0.336  # with audio but no custom voice
    estimated_cost = 10 * cost_per_sec
    print(f"\nSETTINGS:")
    print(f"  Duration: 10s (4+3+3)")
    print(f"  Aspect Ratio: 16:9")
    print(f"  Audio: Native (no custom voice)")
    print(f"  Estimated Cost: ${estimated_cost:.2f}")

    print(f"\nGenerating...")

    try:
        def on_queue_update(update):
            status = type(update).__name__
            print(f"  [{status}]")

        result = fal_client.subscribe(
            "fal-ai/kling-video/v3/pro/image-to-video",
            arguments=request,
            with_logs=True,
            on_queue_update=on_queue_update
        )

        # Extract video URL
        video_url = None
        if result and "video" in result:
            video_url = result["video"].get("url")

        if video_url:
            print(f"\n✓ Generated: {video_url}")

            # Download video
            import requests
            response = requests.get(video_url)

            if response.status_code == 200:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = OUTPUT_DIR / f"market_confrontation_{timestamp}.mp4"

                with open(output_path, "wb") as f:
                    f.write(response.content)

                print(f"✓ Saved: {output_path}")

                # Save metadata
                metadata = {
                    "experiment": "market_confrontation",
                    "timestamp": datetime.now().isoformat(),
                    "start_frame": str(START_FRAME),
                    "audio_mode": "native (dialogue embedded in prompts)",
                    "multi_prompt": multi_prompt,
                    "video_url": video_url,
                }
                metadata_path = output_path.with_suffix('.json')
                with open(metadata_path, "w") as f:
                    json.dump(metadata, f, indent=2, default=str)

                return output_path
            else:
                print(f"✗ Failed to download: {response.status_code}")
                return None
        else:
            print("✗ No video in result")
            print(f"Result: {json.dumps(result, indent=2, default=str)}")
            return None

    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    if not os.getenv("FAL_KEY"):
        print("ERROR: FAL_KEY not set")
        sys.exit(1)

    result = run_market_confrontation()

    if result:
        print(f"\n{'=' * 70}")
        print(f"SUCCESS: {result}")
        print(f"{'=' * 70}")
    else:
        print(f"\n{'=' * 70}")
        print("EXPERIMENT FAILED - Check errors above")
        print(f"{'=' * 70}")
