#!/usr/bin/env python3
"""
MiniMax Voice Design Test - Mars Character Voice

Creates a custom voice for Mars using the MiniMax voice-design API,
then tests it in a Kling 3.0 video with voice reference.
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

# Output directory
SCRIPT_DIR = Path(__file__).parent
OUTPUT_DIR = SCRIPT_DIR / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)


def design_mars_voice():
    """
    Design a custom voice for Mars using MiniMax voice-design.

    Voice Design Strategy (Archetype + Modifier Formula):
    - Archetype: Clever young adventurer, resourceful storyteller
    - Physicality: Clear, warm, with slight Caribbean lilt
    - Disposition: Guarded but charming, quick-witted, always deflecting
    """
    print("\n" + "=" * 70)
    print("MINIMAX VOICE DESIGN: Mars (Marlowe Blackwood)")
    print("=" * 70)

    # Voice description following MiniMax best practices
    voice_prompt = """A young female adventurer, 16 years old, with a clear and warm voice
that carries a subtle Caribbean lilt. She speaks with quick wit and easy charm,
her words winding and redirecting like someone used to talking her way out of trouble.
There's a guarded intelligence beneath the friendly surface—she's always thinking
three moves ahead. Slightly breathless energy, as if she might need to run at any moment.
Confident delivery that masks deeper uncertainty."""

    # Preview text - using one of Mars's sample dialogue lines
    preview_text = """You're asking what I want? That's a big question for someone
who just met me. Let's start smaller. What do you want? I'm curious."""

    print(f"\nVOICE PROMPT:")
    print(f"  {voice_prompt[:100]}...")
    print(f"\nPREVIEW TEXT:")
    print(f"  {preview_text[:80]}...")

    # Estimate cost
    print(f"\nESTIMATED COST:")
    print(f"  Voice creation: $1.00")
    print(f"  Preview ({len(preview_text)} chars): ${len(preview_text) * 0.03 / 1000:.4f}")

    print(f"\nGenerating voice...")

    try:
        def on_queue_update(update):
            status = type(update).__name__
            print(f"  [{status}]")

        result = fal_client.subscribe(
            "fal-ai/minimax/voice-design",
            arguments={
                "prompt": voice_prompt,
                "preview_text": preview_text,
            },
            with_logs=True,
            on_queue_update=on_queue_update
        )

        voice_id = result.get("custom_voice_id")
        audio_url = result.get("audio", {}).get("url") if isinstance(result.get("audio"), dict) else result.get("audio")

        if voice_id:
            print(f"\n✓ Voice created!")
            print(f"  Voice ID: {voice_id}")
            print(f"  Preview Audio: {audio_url}")

            # Download preview audio
            if audio_url:
                import requests
                response = requests.get(audio_url)
                if response.status_code == 200:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    audio_path = OUTPUT_DIR / f"mars_voice_preview_{timestamp}.mp3"
                    with open(audio_path, "wb") as f:
                        f.write(response.content)
                    print(f"  Saved preview: {audio_path}")

            # Save voice metadata
            metadata = {
                "character": "mars",
                "voice_id": voice_id,
                "prompt": voice_prompt,
                "preview_text": preview_text,
                "preview_audio_url": audio_url,
                "timestamp": datetime.now().isoformat(),
            }
            metadata_path = OUTPUT_DIR / f"mars_voice_{timestamp}.json"
            with open(metadata_path, "w") as f:
                json.dump(metadata, f, indent=2)
            print(f"  Saved metadata: {metadata_path}")

            return voice_id
        else:
            print("✗ No voice_id in result")
            print(f"Result: {json.dumps(result, indent=2, default=str)}")
            return None

    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return None


def clone_voice_for_kling(audio_url: str):
    """
    Clone a voice using Kling's create-voice endpoint.
    MiniMax voice IDs are NOT compatible with Kling - we need to clone
    from the audio file to get a Kling-compatible voice_id.

    Args:
        audio_url: URL of audio file (5-30 seconds, clean single voice)

    Returns:
        Kling-compatible voice_id
    """
    print("\n" + "=" * 70)
    print("KLING CREATE-VOICE: Cloning from MiniMax audio")
    print("=" * 70)

    print(f"\nAudio URL: {audio_url[:60]}...")
    print(f"Cost: $0.035")

    print(f"\nCloning voice for Kling...")

    try:
        def on_queue_update(update):
            print(f"  [{type(update).__name__}]")

        result = fal_client.subscribe(
            "fal-ai/kling-video/create-voice",
            arguments={
                "voice_url": audio_url,
            },
            with_logs=True,
            on_queue_update=on_queue_update
        )

        voice_id = result.get("voice_id")

        if voice_id:
            print(f"\n✓ Kling voice created!")
            print(f"  Voice ID: {voice_id}")

            # Save to metadata
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            metadata = {
                "character": "mars",
                "kling_voice_id": voice_id,
                "source_audio_url": audio_url,
                "timestamp": datetime.now().isoformat(),
            }
            metadata_path = OUTPUT_DIR / f"mars_kling_voice_{timestamp}.json"
            with open(metadata_path, "w") as f:
                json.dump(metadata, f, indent=2)
            print(f"  Saved metadata: {metadata_path}")

            return voice_id
        else:
            print("✗ No voice_id in result")
            print(f"Result: {json.dumps(result, indent=2, default=str)}")
            return None

    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_voice_in_kling(voice_id: str):
    """
    Test the generated voice in a Kling 3.0 video.
    Uses Mars identity sheet as starting image.
    """
    print("\n" + "=" * 70)
    print("KLING 3.0 VIDEO WITH VOICE: Mars Speaking")
    print("=" * 70)

    # Find Mars identity sheet
    PROJECT_ROOT = SCRIPT_DIR.parent.parent
    PIRATE_PROJECT = PROJECT_ROOT / "projects" / "pirate-romance"
    EXPORTS = PIRATE_PROJECT / "EXPORTS"

    # Find latest Mars identity sheet
    identity_sheets = list((EXPORTS / "identity_sheets").glob("mars_identity_*.png"))
    if not identity_sheets:
        print("ERROR: No Mars identity sheet found")
        return None

    mars_identity = sorted(identity_sheets, key=lambda p: p.stat().st_mtime, reverse=True)[0]
    print(f"\nUsing identity sheet: {mars_identity.name}")

    # Upload image
    print("Uploading image...")
    start_url = fal_client.upload_file(str(mars_identity))
    print(f"  ✓ {start_url[:60]}...")

    # Dialogue for Mars to speak
    dialogue = "I've never seen bottles like these before. Where did they come from?"

    # Build request with voice reference
    # Note: <<<voice_N>>> tag should appear directly before the quoted dialogue
    prompt = f"Young woman examines strange glowing bottles, she says <<<voice_1>>> '{dialogue}' " \
             f"expression shifts from curiosity to suspicion, close-up shot, " \
             f"warm golden market lighting, cinematic shallow depth of field"

    request = {
        "start_image_url": start_url,
        "prompt": prompt,
        "voice_ids": [voice_id],
        "duration": "5",
        "aspect_ratio": "16:9",
        "generate_audio": True,
        "negative_prompt": "blur, distort, low quality, cartoon, anime, deformed",
    }

    print(f"\nPROMPT: {prompt[:100]}...")
    print(f"VOICE_ID: {voice_id}")
    print(f"\nESTIMATED COST: ${5 * 0.392:.2f} (5s with voice control)")

    print(f"\nGenerating video with voice...")

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
                output_path = OUTPUT_DIR / f"mars_voice_test_{timestamp}.mp4"

                with open(output_path, "wb") as f:
                    f.write(response.content)

                print(f"✓ Saved: {output_path}")

                # Save metadata
                metadata = {
                    "experiment": "mars_voice_test",
                    "voice_id": voice_id,
                    "prompt": prompt,
                    "dialogue": dialogue,
                    "timestamp": datetime.now().isoformat(),
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


def main():
    """
    Run full voice design pipeline:
    1. MiniMax voice-design → preview audio
    2. Kling create-voice → clone from audio → Kling voice_id
    3. Kling video → use voice_id for speech
    """
    import argparse

    parser = argparse.ArgumentParser(description="MiniMax Voice Design + Kling Test")
    parser.add_argument("--voice-only", action="store_true",
                        help="Only create voice, don't generate video")
    parser.add_argument("--kling-voice-id", type=str,
                        help="Use existing Kling voice ID instead of creating new")
    parser.add_argument("--audio-url", type=str,
                        help="Use existing audio URL to clone voice (skip MiniMax)")
    args = parser.parse_args()

    # Check FAL_KEY
    if not os.getenv("FAL_KEY"):
        print("ERROR: FAL_KEY not set in environment")
        sys.exit(1)

    print("\n" + "#" * 70)
    print("# VOICE DESIGN PIPELINE: Mars (Marlowe Blackwood)")
    print("# Step 1: MiniMax voice-design → preview audio")
    print("# Step 2: Kling create-voice → Kling-compatible voice_id")
    print("# Step 3: Kling video → video with character voice")
    print("#" * 70)

    # Step 1: Get audio (from MiniMax or existing URL)
    if args.kling_voice_id:
        # Skip to video generation with existing Kling voice
        kling_voice_id = args.kling_voice_id
        print(f"\nUsing existing Kling voice ID: {kling_voice_id}")
    elif args.audio_url:
        # Skip MiniMax, go straight to Kling clone
        audio_url = args.audio_url
        print(f"\nUsing existing audio URL for Kling clone")

        kling_voice_id = clone_voice_for_kling(audio_url)
        if not kling_voice_id:
            print("\n✗ Kling voice cloning failed")
            sys.exit(1)
    else:
        # Full pipeline: MiniMax → Kling clone
        minimax_voice_id = design_mars_voice()
        if not minimax_voice_id:
            print("\n✗ MiniMax voice creation failed")
            sys.exit(1)

        # Get the preview audio URL from the most recent metadata file
        metadata_files = sorted(OUTPUT_DIR.glob("mars_voice_*.json"),
                               key=lambda p: p.stat().st_mtime, reverse=True)
        if not metadata_files:
            print("\n✗ No voice metadata found")
            sys.exit(1)

        with open(metadata_files[0]) as f:
            metadata = json.load(f)
        audio_url = metadata.get("preview_audio_url")

        if not audio_url:
            print("\n✗ No preview audio URL in metadata")
            sys.exit(1)

        print(f"\nMiniMax voice created with preview: {audio_url[:50]}...")

        # Step 2: Clone for Kling
        kling_voice_id = clone_voice_for_kling(audio_url)
        if not kling_voice_id:
            print("\n✗ Kling voice cloning failed")
            sys.exit(1)

    # Step 3: Test in Kling video (unless voice-only)
    if not args.voice_only:
        video_path = test_voice_in_kling(kling_voice_id)

        if video_path:
            print(f"\n{'=' * 70}")
            print(f"SUCCESS!")
            print(f"  Kling Voice ID: {kling_voice_id}")
            print(f"  Video: {video_path}")
            print(f"{'=' * 70}")
        else:
            print(f"\n{'=' * 70}")
            print("Video generation failed - voice was created successfully")
            print(f"  Kling Voice ID: {kling_voice_id}")
            print("  Use --kling-voice-id to retry video with this voice")
            print(f"{'=' * 70}")
    else:
        print(f"\n{'=' * 70}")
        print(f"Voice pipeline complete!")
        print(f"  Kling Voice ID: {kling_voice_id}")
        print(f"  Run without --voice-only to test in video")
        print(f"{'=' * 70}")


if __name__ == "__main__":
    main()
