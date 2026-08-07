#!/usr/bin/env python3
"""Mechanical validator for v2 (wired) story recipes.

Usage:
    python3 scripts/writer/validate_recipe_wiring.py references/story_structure/recipes/ensemble_heist.md [...]
    python3 scripts/writer/validate_recipe_wiring.py references/story_structure/recipes/*.md

Ported from gemmawood (2026-08-06). Checks the wiring layer added by the v2
methodology (references/story_structure/story-recipe-methodology.md):
tag syntax and closure, template boilerplate, front-half obligations, climax
preconditions, and the fixed Wiring tests block. It cannot judge whether an edge
is *dramatically* good — that stays a human/frontier-model job — but it catches
every failure mode observed in the first (botched) migration.
"""

from __future__ import annotations

import re
import sys
from collections import Counter
from pathlib import Path

TAG_RE = re.compile(r"\bE(\d+)-([a-z][a-z0-9-]*)")
BANNED_NOUNS = {
    "consequence", "choice", "cost", "constraint", "aftermath", "event", "outcome",
}
TEMPLATE_PHRASES = [
    "leaves a consequence unresolved",
    "to choose in a way that causes",
    "irreversibly narrowing what remains possible",
]
WIRING_TESTS_LINES = [
    "- Delete-test: no episode can be removed without a later episode breaking.",
    "- The climax consumes at least two character choices from distinct earlier episodes.",
    "- Every named flaw fires as a choice whose consequence is visible in a later episode.",
    "- Every cost charged is paid: a later episode is harder in a named way because of it.",
]


def beat_rows(text: str) -> list[tuple[int, str]]:
    """(episode_number, full_cell_text) for each beat-spine table row."""
    rows = []
    in_spine = False
    for line in text.splitlines():
        if line.startswith("## Beat spine"):
            in_spine = True
            continue
        if in_spine and line.startswith("## "):
            break
        m = re.match(r"\|\s*(\d+)\s*\|(.*)\|[^|]*\|\s*$", line)
        if in_spine and m:
            rows.append((int(m.group(1)), m.group(2)))
    return rows


def ngrams(text: str, n: int = 8) -> set[tuple[str, ...]]:
    words = re.findall(r"[a-z']+", text.lower())
    return {tuple(words[i : i + n]) for i in range(len(words) - n + 1)}


def validate(path: Path) -> list[str]:
    errors: list[str] = []
    text = path.read_text(encoding="utf-8")

    for phrase in TEMPLATE_PHRASES:
        if phrase in text:
            errors.append(f"template boilerplate present: '{phrase}'")

    if "## Wiring tests" not in text:
        errors.append("missing '## Wiring tests' section")
    else:
        for line in WIRING_TESTS_LINES:
            if line not in text:
                errors.append(f"Wiring tests block not verbatim (missing: '{line[:50]}...')")

    rows = beat_rows(text)
    if not rows:
        errors.append("no beat-spine table rows found")
        return errors

    emits: dict[str, int] = {}        # tag -> emitting episode
    needs: list[tuple[int, str]] = []  # (episode, tag)
    declared_consumers: list[tuple[str, int, int]] = []  # (tag, emitter, pointed-at ep)

    for ep, cell in rows:
        if "**Needs:**" not in cell or "**Sets up:**" not in cell:
            errors.append(f"E{ep}: missing Needs/Sets-up lines")
            continue
        needs_part = cell.split("**Needs:**", 1)[1].split("**Sets up:**", 1)[0]
        sets_part = cell.split("**Sets up:**", 1)[1]

        for m in TAG_RE.finditer(needs_part):
            needs.append((ep, m.group(0)))
        # Sets-up tags: strip consumer pointers first, collect them separately
        for tag_m in TAG_RE.finditer(re.sub(r"\(→[^)]*\)", "", sets_part)):
            tag, src = tag_m.group(0), int(tag_m.group(1))
            if src != ep:
                errors.append(f"E{ep}: emitted tag '{tag}' not prefixed with its emitting episode")
            if tag in emits:
                errors.append(f"E{ep}: tag '{tag}' emitted twice (also E{emits[tag]})")
            emits[tag] = ep
            noun = tag.split("-", 1)[1]
            if noun in BANNED_NOUNS:
                errors.append(f"E{ep}: tag '{tag}' uses a banned contentless noun")
        for ptr in re.finditer(r"(E\d+-[a-z][a-z0-9-]*)\s*\(→([^)]*)\)", sets_part):
            for cons in re.findall(r"E(\d+)", ptr.group(2)):
                declared_consumers.append((ptr.group(1), ep, int(cons)))

    needed_tags = {t for _, t in needs}
    for tag, ep in emits.items():
        if tag not in needed_tags:
            errors.append(f"unfed setup: '{tag}' (E{ep}) is never consumed by any Needs line")
    for ep, tag in needs:
        if tag not in emits:
            errors.append(f"E{ep}: needs '{tag}' but no beat emits it")
        elif emits[tag] >= ep:
            errors.append(f"E{ep}: needs '{tag}' emitted in E{emits[tag]} (not earlier)")
    for tag, emitter, cons_ep in declared_consumers:
        if cons_ep <= emitter:
            errors.append(f"'{tag}': consumer pointer →E{cons_ep} not after emitter E{emitter}")
        elif (cons_ep, tag) not in needs:
            errors.append(f"'{tag}': declares consumer E{cons_ep} but E{cons_ep}'s Needs lacks it")

    # orphan beats (every beat after the first consumes something)
    eps_with_needs = {ep for ep, _ in needs}
    for ep, _ in rows[1:]:
        if ep not in eps_with_needs:
            errors.append(f"E{ep}: orphan beat — consumes nothing")

    # front-half obligation: beats 1-4 each emit >=1 tag consumed at 5+
    for ep, _ in rows:
        if ep <= 4:
            tags = [t for t, e in emits.items() if e == ep]
            if not any(any(ne >= 5 and nt == t for ne, nt in needs) for t in tags):
                errors.append(f"E{ep}: front-half beat emits nothing the back half (E5+) consumes")

    # climax preconditions: final two beats consume from >=3 distinct emitters
    last_two = {rows[-1][0], rows[-2][0]}
    climax_sources = {emits[t] for ep, t in needs if ep in last_two and t in emits}
    if len(climax_sources) < 3:
        errors.append(
            f"climax (E{sorted(last_two)}) consumes from only {len(climax_sources)} distinct earlier beats (need >=3)"
        )

    # repeated 8-grams across beat cells (template detection)
    gram_count: Counter = Counter()
    for _, cell in rows:
        body = cell.split("**Needs:**", 1)[0]
        for g in ngrams(body):
            gram_count[g] += 1
    repeated = [g for g, c in gram_count.items() if c >= 2]
    if repeated:
        sample = " ".join(repeated[0])
        errors.append(f"{len(repeated)} repeated 8-gram(s) across beat cells (e.g. '{sample}')")

    return errors


def main() -> int:
    paths = [Path(p) for p in sys.argv[1:]]
    if not paths:
        print(__doc__)
        return 2
    failed = 0
    for path in paths:
        errors = validate(path)
        if errors:
            failed += 1
            print(f"FAIL {path.name} ({len(errors)} error{'s' if len(errors) != 1 else ''})")
            for e in errors:
                print(f"  - {e}")
        else:
            print(f"PASS {path.name}")
    print(f"\n{len(paths) - failed}/{len(paths)} passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
