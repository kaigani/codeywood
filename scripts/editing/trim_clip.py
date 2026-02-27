#!/usr/bin/env python3
"""
Trim a video clip at specified timecodes.

Usage:
    python3 scripts/editing/trim_clip.py INPUT --start 2.5 --end 8.0
    python3 scripts/editing/trim_clip.py INPUT --start 0.3 --output trimmed.mp4
    python3 scripts/editing/trim_clip.py INPUT --end 5.0
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.ffmpeg import trim_clip, probe_duration


def main():
    parser = argparse.ArgumentParser(description="Trim a video clip at timecodes.")
    parser.add_argument("input", type=Path, help="Input video file")
    parser.add_argument("--start", "-s", type=float, default=0.0,
                        help="Start time in seconds (default: 0)")
    parser.add_argument("--end", "-e", type=float, default=None,
                        help="End time in seconds (default: end of clip)")
    parser.add_argument("--output", "-o", type=Path, default=None,
                        help="Output path (default: {name}_trimmed.mp4)")

    args = parser.parse_args()

    if not args.input.exists():
        print(f"ERROR: File not found: {args.input}")
        sys.exit(1)

    if args.output is None:
        stem = args.input.stem
        suffix = args.input.suffix
        args.output = args.input.parent / f"{stem}_trimmed{suffix}"

    # Show info
    dur = probe_duration(args.input)
    if dur:
        print(f"Input: {args.input.name} ({dur:.2f}s)")
    print(f"Trim: [{args.start}s → {args.end or 'end'}s]")

    result = trim_clip(args.input, args.output, start_s=args.start, end_s=args.end)
    if result:
        new_dur = probe_duration(result)
        print(f"\nOutput: {result} ({new_dur:.2f}s)" if new_dur else f"\nOutput: {result}")
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
