#!/usr/bin/env python3
"""
Kling 3.0 Pro Image-to-Video Experiment

Testing:
1. Elements feature for character consistency (Mars, Jonah)
2. Location element for scene grounding
3. Multi-prompt for multiple cuts within a clip

Endpoint: fal-ai/kling-video/v3/pro/image-to-video
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path

# Load environment
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

import fal_client

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
PIRATE_PROJECT = PROJECT_ROOT / "projects" / "pirate-romance"
EXPORTS = PIRATE_PROJECT / "EXPORTS"

# Output directory for experiments
OUTPUT_DIR = Path(__file__).parent / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)


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


def run_kling_experiment(
    start_image_url: str,
    prompt: str = None,
    multi_prompt: list = None,
    elements: list = None,
    duration: str = "5",
    aspect_ratio: str = "16:9",
    generate_audio: bool = True,
    end_image_url: str = None,
    experiment_name: str = "test"
):
    """
    Run a Kling 3.0 Pro image-to-video generation.

    Args:
        start_image_url: Starting frame image URL
        prompt: Single prompt (mutually exclusive with multi_prompt)
        multi_prompt: List of prompts for multi-shot generation
        elements: List of element dicts with character/object references
        duration: Video length "3" to "15" seconds
        aspect_ratio: "16:9", "9:16", or "1:1"
        generate_audio: Enable native audio generation
        end_image_url: Optional end frame for transitions
        experiment_name: Name for output files
    """
    print(f"\n{'='*70}")
    print(f"KLING 3.0 PRO EXPERIMENT: {experiment_name}")
    print(f"{'='*70}")

    # Build request
    request = {
        "start_image_url": start_image_url,
        "duration": duration,
        "aspect_ratio": aspect_ratio,
        "generate_audio": generate_audio,
    }

    # Prompt or multi_prompt (mutually exclusive)
    if multi_prompt:
        request["multi_prompt"] = multi_prompt
        print(f"\nMULTI-PROMPT ({len(multi_prompt)} cuts):")
        for i, p in enumerate(multi_prompt):
            print(f"  [{i+1}] {p[:80]}...")
    elif prompt:
        request["prompt"] = prompt
        print(f"\nPROMPT: {prompt[:100]}...")

    # Add elements if provided
    if elements:
        request["elements"] = elements
        print(f"\nELEMENTS: {len(elements)} character/location references")
        for i, elem in enumerate(elements):
            print(f"  @Element{i+1}: {list(elem.keys())}")

    # Add end frame if provided
    if end_image_url:
        request["end_image_url"] = end_image_url
        print(f"\nEND FRAME: Transition video enabled")

    print(f"\nSETTINGS:")
    print(f"  Duration: {duration}s")
    print(f"  Aspect Ratio: {aspect_ratio}")
    print(f"  Audio: {generate_audio}")

    # Estimate cost
    cost_per_sec = 0.336 if generate_audio else 0.224
    estimated_cost = float(duration) * cost_per_sec
    print(f"  Estimated Cost: ${estimated_cost:.2f}")

    print(f"\nGenerating...")

    try:
        def on_queue_update(update):
            status = type(update).__name__
            if hasattr(update, 'logs') and update.logs:
                for log in update.logs:
                    print(f"  [{status}] {log.get('message', '')}")
            else:
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
                output_path = OUTPUT_DIR / f"{experiment_name}_{timestamp}.mp4"

                with open(output_path, "wb") as f:
                    f.write(response.content)

                print(f"✓ Saved: {output_path}")

                # Save metadata
                metadata = {
                    "experiment": experiment_name,
                    "timestamp": datetime.now().isoformat(),
                    "request": request,
                    "video_url": video_url,
                    "result": result,
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
            print(f"Result: {result}")
            return None

    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return None


def experiment_1_basic():
    """Basic test: Single character, simple motion."""
    print("\n" + "#"*70)
    print("# EXPERIMENT 1: Basic Character Motion")
    print("#"*70)

    # Find Mars entrance shot
    mars_entrance = find_latest_image(
        EXPORTS / "hero_shots" / "mars",
        "mars_entrance_*.png"
    )

    start_url = upload_image(mars_entrance)

    return run_kling_experiment(
        start_image_url=start_url,
        prompt="Young woman with dark curly hair looks up slowly, her eyes catching the golden light, a subtle knowing smile crosses her face, cinematic slow movement",
        duration="5",
        generate_audio=False,  # Start without audio to save cost
        experiment_name="basic_mars_motion"
    )


def experiment_2_elements():
    """Test elements feature with character references."""
    print("\n" + "#"*70)
    print("# EXPERIMENT 2: Elements - Character Reference Consistency")
    print("#"*70)

    # Upload Mars reference images (multiple angles)
    print("\nUploading Mars references...")
    mars_entrance = find_latest_image(EXPORTS / "hero_shots" / "mars", "mars_entrance_*.png")
    mars_action = find_latest_image(EXPORTS / "hero_shots" / "mars", "mars_action_*.png")
    mars_quiet = find_latest_image(EXPORTS / "hero_shots" / "mars", "mars_quiet_*.png")

    mars_frontal = upload_image(mars_entrance)
    mars_refs = [upload_image(mars_action), upload_image(mars_quiet)]

    # Upload a location reference
    print("\nUploading location reference...")
    location_ref = find_latest_image(EXPORTS / "location_refs", "holding_cells_*.png")
    location_url = upload_image(location_ref)

    # Build elements
    elements = [
        {
            "frontal_image_url": mars_frontal,
            "reference_image_urls": mars_refs,
        }
    ]

    return run_kling_experiment(
        start_image_url=location_url,  # Start with location
        prompt="@Element1 emerges from shadows into a shaft of golden light, dust particles floating around her, she looks around cautiously, cinematic camera push in",
        elements=elements,
        duration="5",
        generate_audio=True,
        experiment_name="elements_mars_in_location"
    )


def experiment_3_multi_character():
    """Test with both Mars and Jonah as elements."""
    print("\n" + "#"*70)
    print("# EXPERIMENT 3: Multi-Character Elements")
    print("#"*70)

    # Upload Mars
    print("\nUploading Mars references...")
    mars_entrance = find_latest_image(EXPORTS / "hero_shots" / "mars", "mars_entrance_*.png")
    mars_action = find_latest_image(EXPORTS / "hero_shots" / "mars", "mars_action_*.png")
    mars_frontal = upload_image(mars_entrance)
    mars_refs = [upload_image(mars_action)]

    # Upload Jonah
    print("\nUploading Jonah references...")
    jonah_entrance = find_latest_image(EXPORTS / "hero_shots" / "jonah", "jonah_entrance_*.png")
    jonah_action = find_latest_image(EXPORTS / "hero_shots" / "jonah", "jonah_action_*.png")
    jonah_frontal = upload_image(jonah_entrance)
    jonah_refs = [upload_image(jonah_action)]

    # Upload location
    print("\nUploading location...")
    location_ref = find_latest_image(EXPORTS / "location_refs", "whisper_market_*.png")
    location_url = upload_image(location_ref)

    elements = [
        {
            "frontal_image_url": mars_frontal,
            "reference_image_urls": mars_refs,
        },
        {
            "frontal_image_url": jonah_frontal,
            "reference_image_urls": jonah_refs,
        }
    ]

    return run_kling_experiment(
        start_image_url=location_url,
        prompt="@Element1 and @Element2 walk through a mysterious market, exchanging a glance, @Element1 reaches out to touch @Element2's arm, intimate moment, golden hour lighting, cinematic",
        elements=elements,
        duration="5",
        generate_audio=True,
        experiment_name="multi_char_mars_jonah"
    )


def experiment_4_multi_prompt():
    """Test multi-prompt for multiple cuts."""
    print("\n" + "#"*70)
    print("# EXPERIMENT 4: Multi-Prompt (Multiple Cuts)")
    print("#"*70)

    # Upload characters
    print("\nUploading character references...")
    mars_entrance = find_latest_image(EXPORTS / "hero_shots" / "mars", "mars_entrance_*.png")
    jonah_entrance = find_latest_image(EXPORTS / "hero_shots" / "jonah", "jonah_entrance_*.png")

    mars_url = upload_image(mars_entrance)
    jonah_url = upload_image(jonah_entrance)

    # Upload location
    print("\nUploading location...")
    location_ref = find_latest_image(EXPORTS / "location_refs", "threshold_island_*.png")
    location_url = upload_image(location_ref)

    elements = [
        {"frontal_image_url": mars_url},
        {"frontal_image_url": jonah_url},
    ]

    # Multi-prompt: each prompt is a different "cut"
    multi_prompt = [
        "Wide establishing shot, mysterious island at twilight, waves crashing, cinematic drone pullback",
        "@Element1 stands at the shore looking out, wind in her dark curly hair, contemplative, medium shot",
        "@Element2 approaches from behind, stops beside her, they exchange a look, two-shot, golden hour",
    ]

    return run_kling_experiment(
        start_image_url=location_url,
        multi_prompt=multi_prompt,
        elements=elements,
        duration="10",  # Longer for multiple cuts
        generate_audio=True,
        experiment_name="multi_prompt_scene"
    )


def main():
    """Run experiments."""
    import argparse

    parser = argparse.ArgumentParser(description="Kling 3.0 Pro Experiments")
    parser.add_argument("--exp", type=int, choices=[1, 2, 3, 4],
                        help="Run specific experiment (1-4)")
    parser.add_argument("--all", action="store_true",
                        help="Run all experiments")
    args = parser.parse_args()

    # Check FAL_KEY
    if not os.getenv("FAL_KEY"):
        print("ERROR: FAL_KEY not set in environment")
        sys.exit(1)

    print(f"\n{'#'*70}")
    print("# KLING 3.0 PRO - CODEYWOOD EXPERIMENTS")
    print(f"# Project: pirate-romance")
    print(f"# Output: {OUTPUT_DIR}")
    print(f"{'#'*70}")

    experiments = {
        1: ("Basic Character Motion", experiment_1_basic),
        2: ("Elements - Character Reference", experiment_2_elements),
        3: ("Multi-Character Elements", experiment_3_multi_character),
        4: ("Multi-Prompt Scene", experiment_4_multi_prompt),
    }

    if args.all:
        for num, (name, func) in experiments.items():
            print(f"\n\n{'='*70}")
            print(f"Running Experiment {num}: {name}")
            print(f"{'='*70}")
            func()
    elif args.exp:
        name, func = experiments[args.exp]
        func()
    else:
        print("\nAvailable experiments:")
        for num, (name, _) in experiments.items():
            print(f"  {num}. {name}")
        print("\nUsage:")
        print("  python kling_v3_test.py --exp 1    # Run experiment 1")
        print("  python kling_v3_test.py --all      # Run all experiments")


if __name__ == "__main__":
    main()
