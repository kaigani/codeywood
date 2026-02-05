#!/usr/bin/env python3
"""
Kling 3.0 Pro - Market Scene Experiment

Scene: Mars at the Whisper Market examining bottles, talking to merchant, then leaving

Uses:
- detail-image.jpg as starting frame (bottles close-up)
- Mars identity sheet as @Element1 (character consistency)
- location-image.jpg as @Element2 (market location reference)
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
DETAIL_IMAGE = SCRIPT_DIR / "detail-image.jpg"
LOCATION_IMAGE = SCRIPT_DIR / "location-image.jpg"


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


def run_market_scene():
    """
    Create a 3-cut scene of Mars at the market.
    """
    print("\n" + "#"*70)
    print("# MARKET SCENE: Mars at the Whisper Market")
    print("# 3 cuts: Examining bottles → Talking to merchant → Leaving stall")
    print("#"*70)

    # Verify input images exist
    if not DETAIL_IMAGE.exists():
        print(f"ERROR: {DETAIL_IMAGE} not found")
        return None
    if not LOCATION_IMAGE.exists():
        print(f"ERROR: {LOCATION_IMAGE} not found")
        return None

    # Upload starting image (detail shot of bottles)
    print("\nUploading starting frame (detail shot)...")
    start_url = upload_image(DETAIL_IMAGE)

    # Upload Mars identity sheet + additional refs for Element1
    print("\nUploading Mars character references...")
    mars_identity = find_latest_image(EXPORTS / "identity_sheets", "mars_identity_*.png")
    mars_entrance = find_latest_image(EXPORTS / "hero_shots" / "mars", "mars_entrance_*.png")
    mars_action = find_latest_image(EXPORTS / "hero_shots" / "mars", "mars_action_*.png")

    mars_frontal = upload_image(mars_identity)
    mars_ref1 = upload_image(mars_entrance)
    mars_ref2 = upload_image(mars_action)

    # Upload location image for Element2
    print("\nUploading location reference...")
    location_url = upload_image(LOCATION_IMAGE)
    # Also get a market ref from exports for additional reference
    market_ref = find_latest_image(EXPORTS / "location_refs", "whisper_market_*.png")
    market_ref_url = upload_image(market_ref)

    # Build elements (both frontal AND reference_image_urls required)
    elements = [
        {
            "frontal_image_url": mars_frontal,
            "reference_image_urls": [mars_ref1, mars_ref2],
        },
        {
            "frontal_image_url": location_url,
            "reference_image_urls": [market_ref_url],
        }
    ]

    # Multi-prompt: each item needs "prompt" and "duration" (sum must <= total duration)
    # 3 cuts at ~3s each = 9s total (under 10s limit)
    multi_prompt = [
        {
            "prompt": "Close-up on hands examining strange glowing bottles, curiosity, soft ambient light filtering through market stalls, cinematic shallow depth of field",
            "duration": "3"
        },
        {
            "prompt": "@Element1 young woman with dark curly hair speaks to an unseen merchant, gesturing at the bottles, her expression shifts from curiosity to suspicion, medium close-up, warm golden market lighting",
            "duration": "3"
        },
        {
            "prompt": "Wide shot pulling back as @Element1 turns and walks away from the stall into the bustling @Element2 market, atmospheric haze, golden hour light filtering through fabric awnings, cinematic crane movement",
            "duration": "4"
        }
    ]

    print(f"\n{'='*70}")
    print("KLING 3.0 PRO: Market Scene")
    print(f"{'='*70}")
    print(f"\nSTARTING FRAME: {DETAIL_IMAGE.name}")
    print(f"\nELEMENTS:")
    print(f"  @Element1: Mars (identity sheet + 2 hero shots)")
    print(f"  @Element2: Market location (2 refs)")
    print(f"\nMULTI-PROMPT ({len(multi_prompt)} cuts):")
    for i, p in enumerate(multi_prompt):
        prompt_text = p.get("prompt", str(p))
        print(f"  [{i+1}] {prompt_text[:70]}...")

    # Build request
    request = {
        "start_image_url": start_url,
        "multi_prompt": multi_prompt,
        "elements": elements,
        "duration": "10",  # 10 seconds for 3 cuts
        "aspect_ratio": "16:9",
        "generate_audio": True,
        "negative_prompt": "blur, distort, low quality, cartoon, anime, deformed hands",
    }

    # Estimate cost
    cost_per_sec = 0.336  # with audio
    estimated_cost = 10 * cost_per_sec
    print(f"\nSETTINGS:")
    print(f"  Duration: 10s")
    print(f"  Aspect Ratio: 16:9")
    print(f"  Audio: True")
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
                output_path = OUTPUT_DIR / f"market_scene_{timestamp}.mp4"

                with open(output_path, "wb") as f:
                    f.write(response.content)

                print(f"✓ Saved: {output_path}")

                # Save metadata
                metadata = {
                    "experiment": "market_scene",
                    "timestamp": datetime.now().isoformat(),
                    "request": {k: v for k, v in request.items() if k != "elements"},
                    "elements_count": len(elements),
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

        # If validation error, try alternative format
        if "multi_prompt" in str(e) and "not a valid dict" in str(e):
            print("\n--- Trying alternative: single prompt with scene description ---")
            return run_market_scene_single_prompt(start_url, elements)

        return None


def run_market_scene_single_prompt(start_url: str, elements: list):
    """
    Fallback: Use single prompt describing the full scene with cuts.
    """
    print("\n" + "="*70)
    print("FALLBACK: Single prompt with scene description")
    print("="*70)

    # Single comprehensive prompt describing the scene progression
    prompt = """Cinematic scene progression:
First, close-up on hands examining strange glowing bottles with curiosity.
Then, @Element1 young woman with dark curly hair speaks to the merchant, her expression shifting from curiosity to suspicion.
Finally, wide shot as @Element1 turns and walks away into the bustling @Element2 market, golden hour light filtering through awnings.
Smooth camera movements, cinematic transitions between shots, atmospheric lighting."""

    request = {
        "start_image_url": start_url,
        "prompt": prompt,
        "elements": elements,
        "duration": "10",
        "aspect_ratio": "16:9",
        "generate_audio": True,
        "negative_prompt": "blur, distort, low quality, cartoon, anime, deformed hands",
    }

    print(f"\nPROMPT: {prompt[:200]}...")

    try:
        def on_queue_update(update):
            print(f"  [{type(update).__name__}]")

        result = fal_client.subscribe(
            "fal-ai/kling-video/v3/pro/image-to-video",
            arguments=request,
            with_logs=True,
            on_queue_update=on_queue_update
        )

        video_url = None
        if result and "video" in result:
            video_url = result["video"].get("url")

        if video_url:
            print(f"\n✓ Generated: {video_url}")

            import requests
            response = requests.get(video_url)

            if response.status_code == 200:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = OUTPUT_DIR / f"market_scene_single_{timestamp}.mp4"

                with open(output_path, "wb") as f:
                    f.write(response.content)

                print(f"✓ Saved: {output_path}")
                return output_path

        return None

    except Exception as e:
        print(f"✗ Fallback also failed: {e}")
        return None


if __name__ == "__main__":
    if not os.getenv("FAL_KEY"):
        print("ERROR: FAL_KEY not set")
        sys.exit(1)

    result = run_market_scene()

    if result:
        print(f"\n{'='*70}")
        print(f"SUCCESS: {result}")
        print(f"{'='*70}")
    else:
        print(f"\n{'='*70}")
        print("EXPERIMENT FAILED - Check errors above")
        print(f"{'='*70}")
