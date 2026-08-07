#!/usr/bin/env python3
"""Sample the lore entropy pools (cultures + history shapes) for a project.

Used by writers-room Phase 3.5 (Lore Forge) Step 0. Provides true
randomness with cross-project no-repeat tracking so the same cultural
anchors and lore trajectories don't recur across productions (the
"Byzantine Empire 11/20 runs" failure mode from the divergence pipeline).

State lives in references/story_structure/pools/sampling_state.json and
is committed to git so no-repeat holds across sessions.

Usage:
    python3 scripts/writer/sample_pools.py --project NAME [--cultures 32] [--shapes 1]
                                           [--seed N] [--allow-repeats] [--reset] [--dry-run]
"""

import argparse
import json
import random
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
POOLS_DIR = REPO_ROOT / "references" / "story_structure" / "pools"
STATE_PATH = POOLS_DIR / "sampling_state.json"
# With only 32 shapes, all-time exclusion exhausts fast; exclude just the recent window.
SHAPE_WINDOW = 8


def culture_id(entry):
    return f"{entry['name']}|{entry['country']}|{entry['period']}"


def load_state():
    if STATE_PATH.exists():
        return json.loads(STATE_PATH.read_text())
    return {"cultures_used": {}, "shapes_recent": []}


def save_state(state):
    STATE_PATH.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--project", required=True, help="Project name (projects/{name})")
    ap.add_argument("--cultures", type=int, default=32, help="Number of cultures to sample")
    ap.add_argument("--shapes", type=int, default=1, help="Number of history shapes to sample")
    ap.add_argument("--seed", type=int, default=None, help="Deterministic re-roll seed")
    ap.add_argument("--allow-repeats", action="store_true",
                    help="Ignore the no-repeat ledger for this draw (still records the draw)")
    ap.add_argument("--reset", action="store_true", help="Clear the sampling ledger and exit")
    ap.add_argument("--dry-run", action="store_true",
                    help="Print the draw without updating state or writing LORE_SEEDS.md")
    args = ap.parse_args()

    if args.reset:
        save_state({"cultures_used": {}, "shapes_recent": []})
        print(f"Sampling ledger reset: {STATE_PATH}")
        return

    cultures = json.loads((POOLS_DIR / "cultures.json").read_text())
    shapes = json.loads((POOLS_DIR / "history_shapes.json").read_text())
    state = load_state()
    rng = random.Random(args.seed)

    used = set() if args.allow_repeats else set(state["cultures_used"])
    available = [c for c in cultures if culture_id(c) not in used]
    if len(available) < args.cultures:
        print(f"NOTE: cultures pool exhausted at no-repeat rate "
              f"({len(available)} unused of {len(cultures)}); resetting cultures ledger.",
              file=sys.stderr)
        state["cultures_used"] = {}
        available = list(cultures)
    drawn_cultures = rng.sample(available, args.cultures)

    recent = set() if args.allow_repeats else set(state["shapes_recent"][-SHAPE_WINDOW:])
    shape_pool = [s for s in shapes if s["name"] not in recent] or list(shapes)
    drawn_shapes = rng.sample(shape_pool, min(args.shapes, len(shape_pool)))

    lines = ["# Lore Seeds (sampled entropy pools)", ""]
    lines.append(f"Project: **{args.project}**" + (f" · seed {args.seed}" if args.seed is not None else ""))
    lines.append("")
    lines.append("Sampled by `scripts/writer/sample_pools.py` for writers-room Phase 3.5")
    lines.append("(Lore Forge) Step 0. The head writer harmonizes SEASON_LORE.md with the")
    lines.append("history shape and draws faction/population parallels from the cultural")
    lines.append("option set below — parallels must come from this list (user-brief")
    lines.append("overrides win; document any override).")
    lines.append("")
    for s in drawn_shapes:
        lines.append(f"## History shape: {s['name']}")
        lines.append("")
        lines.append(s["shape"])
        lines.append("")
        if s.get("real_examples"):
            lines.append(f"Real examples: {', '.join(s['real_examples'])}")
        if s.get("fiction_examples"):
            lines.append(f"Fiction examples: {', '.join(s['fiction_examples'])}")
        lines.append("")
    lines.append(f"## Cultural option set ({len(drawn_cultures)} sampled of {len(cultures)})")
    lines.append("")
    for c in sorted(drawn_cultures, key=lambda c: (c["country"], c["name"])):
        lines.append(f"- {c['name']} ({c['country']}, {c['period']})")
    lines.append("")
    output = "\n".join(lines)
    print(output)

    if args.dry_run:
        return

    for c in drawn_cultures:
        state["cultures_used"][culture_id(c)] = args.project
    state["shapes_recent"] = (state["shapes_recent"] + [s["name"] for s in drawn_shapes])[-SHAPE_WINDOW * 2:]
    save_state(state)

    seeds_path = REPO_ROOT / "projects" / args.project / "STORY" / "WRITERS_ROOM" / "LORE_SEEDS.md"
    seeds_path.parent.mkdir(parents=True, exist_ok=True)
    seeds_path.write_text(output + "\n")
    print(f"\nWritten: {seeds_path}", file=sys.stderr)
    print(f"Ledger updated: {STATE_PATH}", file=sys.stderr)


if __name__ == "__main__":
    main()
