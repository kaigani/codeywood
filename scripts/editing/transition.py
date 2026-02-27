#!/usr/bin/env python3
"""
Create transitions between two video clips.

Usage:
    python3 scripts/editing/transition.py CLIP_A CLIP_B --type crossfade --duration 1.0
    python3 scripts/editing/transition.py CLIP_A CLIP_B --type l_cut --lead 1.5
    python3 scripts/editing/transition.py CLIP_A CLIP_B --type j_cut --lead 1.0
    python3 scripts/editing/transition.py CLIP_A CLIP_B --type hard_cut
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.ffmpeg import (
    crossfade_transition, l_cut, j_cut, concatenate_clips, probe_duration
)


def main():
    parser = argparse.ArgumentParser(description="Create transitions between clips.")
    parser.add_argument("clip_a", type=Path, help="First clip")
    parser.add_argument("clip_b", type=Path, help="Second clip")
    parser.add_argument("--type", "-t", choices=["crossfade", "l_cut", "j_cut", "hard_cut"],
                        default="crossfade", help="Transition type")
    parser.add_argument("--duration", "-d", type=float, default=1.0,
                        help="Crossfade duration in seconds")
    parser.add_argument("--lead", "-l", type=float, default=1.0,
                        help="Audio/video lead time for L/J cuts")
    parser.add_argument("--output", "-o", type=Path, default=None,
                        help="Output path")

    args = parser.parse_args()

    for clip in [args.clip_a, args.clip_b]:
        if not clip.exists():
            print(f"ERROR: File not found: {clip}")
            sys.exit(1)

    if args.output is None:
        args.output = args.clip_a.parent / f"transition_{args.type}.mp4"

    # Show info
    dur_a = probe_duration(args.clip_a)
    dur_b = probe_duration(args.clip_b)
    print(f"Clip A: {args.clip_a.name} ({dur_a:.2f}s)" if dur_a else f"Clip A: {args.clip_a.name}")
    print(f"Clip B: {args.clip_b.name} ({dur_b:.2f}s)" if dur_b else f"Clip B: {args.clip_b.name}")
    print(f"Transition: {args.type}")

    if args.type == "crossfade":
        result = crossfade_transition(args.clip_a, args.clip_b, args.output, duration=args.duration)
    elif args.type == "l_cut":
        result = l_cut(args.clip_a, args.clip_b, args.output, audio_lead_s=args.lead)
    elif args.type == "j_cut":
        result = j_cut(args.clip_a, args.clip_b, args.output, video_lead_s=args.lead)
    elif args.type == "hard_cut":
        result = concatenate_clips([args.clip_a, args.clip_b], args.output)

    if result:
        new_dur = probe_duration(result)
        print(f"\nOutput: {result} ({new_dur:.2f}s)" if new_dur else f"\nOutput: {result}")
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
