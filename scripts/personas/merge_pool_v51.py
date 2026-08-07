#!/usr/bin/env python3
"""One-off merge: divergence/gemmawood persona_pool.json → Codeywood v5.1 YAMLs.

Kept for provenance. Run 2026-06-11 against the gemmawood pool (post-Peele-pass,
407 cumulative edits). Matches pool entries to persona files by base.agent_name.

What it does per persona:
  - Overwrites base text fields with the pool's Peele-pass versions:
    mechanism, mechanism_non_literal, philosophy, engine, polemic,
    audience_cohort. (NOT influences — the pool trims to 4 for token budget;
    the YAML's 5-7 entry list stays canonical. Mismatches are reported.)
  - Parses the pool's flattened affective_palette string and updates the
    structured object where values differ.
  - Adds the v5.1 fields: cut_principle, recipe_affinities, head_writer_band
    (+ rationale), logline_eligible, archetype, signature_line_shape.
  - Sets schema_version: 5.1.

Requires ruamel.yaml (round-trip mode) in scripts/venv to preserve formatting.

Usage:
    python3 scripts/personas/merge_pool_v51.py [--pool PATH] [--dry-run]
"""
import argparse
import json
import re
import sys
from pathlib import Path

from ruamel.yaml import YAML
from ruamel.yaml.scalarstring import LiteralScalarString

ROOT = Path(__file__).resolve().parents[2]
PERSONAS = ROOT / "skills/writer/personas"
DEFAULT_POOL = Path(
    "/Users/kaigani/Documents/PC_SHARED/260611 gemmawood/data/personas/persona_pool.json"
)

TEXT_FIELDS = ["mechanism", "mechanism_non_literal", "philosophy", "engine",
               "polemic", "audience_cohort"]
NEW_FIELDS = ["cut_principle", "recipe_affinities", "head_writer_band",
              "head_writer_band_rationale", "logline_eligible", "archetype",
              "signature_line_shape"]


def norm(s):
    return re.sub(r"\s+", " ", (s or "")).strip()


def parse_palette(flat):
    """'primary emotion: X; register: Y; restraint: N' -> dict"""
    out = {}
    for part in flat.split(";"):
        if ":" not in part:
            continue
        k, v = part.split(":", 1)
        k = k.strip().lower().replace(" ", "_")
        v = v.strip()
        if k == "primary_emotion" or k == "register":
            out[k] = v
        elif k == "restraint":
            out[k] = int(v)
    return out


def as_scalar(text):
    """Long strings as literal blocks for readability; short ones plain."""
    text = norm(text)
    if len(text) > 90:
        # wrap to ~92 cols for the literal block
        words, lines, cur = text.split(), [], ""
        for w in words:
            if len(cur) + len(w) + 1 > 92:
                lines.append(cur)
                cur = w
            else:
                cur = f"{cur} {w}".strip()
        lines.append(cur)
        return LiteralScalarString("\n".join(lines) + "\n")
    return text


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pool", type=Path, default=DEFAULT_POOL)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    pool = {e["name"]: e for e in json.loads(args.pool.read_text())}
    yaml = YAML(typ="rt")
    yaml.preserve_quotes = True
    yaml.width = 4096

    files = sorted(p for p in PERSONAS.glob("*.yaml") if not p.name.startswith("_"))
    matched, unmatched_files, changed_total = 0, [], 0
    used_names = set()

    for path in files:
        data = yaml.load(path.read_text())
        base = data.get("base", {})
        name = norm(base.get("agent_name", ""))
        entry = pool.get(name)
        if entry is None:
            unmatched_files.append(f"{path.name} (agent_name={name!r})")
            continue
        matched += 1
        used_names.add(name)
        changes = []

        for f in TEXT_FIELDS:
            old = norm(str(base.get(f, "")))
            new = norm(entry.get(f, ""))
            if new and old != new:
                base[f] = as_scalar(new)
                changes.append(f)

        # Palette: pool values are free-form; only adopt vocab-valid ones
        # (the schema's enum stays authoritative — out-of-vocab pool values
        # keep the existing YAML value).
        EMOTIONS = {"wonder","delight","awe","melancholy","dread","tension",
                    "recognition","ache","grief","joy","rage","tenderness",
                    "curiosity","discomfort","catharsis","triumph","nostalgia",
                    "alarm","warmth","exhilaration"}
        REGISTERS = {"warm","cool","dry","plaintive","ecstatic","austere","wry",
                     "tender","severe","ironic","sincere","operatic","deadpan",
                     "lyrical","muscular","playful","elegiac","reverent"}
        pal = parse_palette(entry.get("affective_palette", ""))
        cur = base.get("affective_palette", {}) or {}
        for k, v in pal.items():
            valid = (k == "restraint" or
                     (k == "primary_emotion" and v in EMOTIONS) or
                     (k == "register" and v in REGISTERS))
            if valid and cur.get(k) != v:
                cur[k] = v
                changes.append(f"affective_palette.{k}")
            elif not valid:
                print(f"  note {path.name}: pool palette {k}={v!r} out of vocab — kept existing {cur.get(k)!r}")
        base["affective_palette"] = cur

        # influences: report-only
        pool_inf = [norm(i.split("/")[0]) for i in entry.get("influences", [])]
        yaml_inf = [norm(str(i).split("—")[0]) for i in (base.get("influences") or [])]
        missing = [i for i in pool_inf if not any(i[:25] in y or y[:25] in i for y in yaml_inf)]
        inf_note = f" [pool-influence not in yaml: {missing}]" if missing else ""

        base["cut_principle"] = as_scalar(entry["cut_principle"])
        base["recipe_affinities"] = list(entry["recipe_affinities"])
        base["head_writer_band"] = entry["head_writer_band"]
        if entry.get("head_writer_band_rationale"):
            base["head_writer_band_rationale"] = norm(entry["head_writer_band_rationale"])
        base["logline_eligible"] = bool(entry.get("logline_eligible", True))
        if entry.get("archetype"):
            base["archetype"] = norm(entry["archetype"])
        if entry.get("signature_line_shape"):
            base["signature_line_shape"] = as_scalar(entry["signature_line_shape"])
        changes.extend(NEW_FIELDS)

        data["schema_version"] = 5.1
        changed_total += 1
        print(f"{path.name}: {len(changes)} fields updated "
              f"({', '.join(c for c in changes if not c.startswith('cut_'))[:120]}…){inf_note}")

        if not args.dry_run:
            with open(path, "w") as fh:
                yaml.dump(data, fh)

    print(f"\nMatched {matched}/{len(files)} persona files; updated {changed_total}.")
    if unmatched_files:
        print("UNMATCHED FILES:", *unmatched_files, sep="\n  ")
    unused = set(pool) - used_names
    if unused:
        print("POOL ENTRIES WITH NO FILE:", sorted(unused))
    if args.dry_run:
        print("(dry run — no files written)")


if __name__ == "__main__":
    main()
