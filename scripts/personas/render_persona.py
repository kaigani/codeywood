#!/usr/bin/env python3
"""Pre-render a v5 persona for a specific skill.

Reads the persona + skill manifest, writes a runtime file containing BASE +
only the intersection of (persona has) ∩ (skill needs ∪ persona.prefer_load).

Usage:
    python3 scripts/personas/render_persona.py --persona 30_hal_sutter --skill pitch-round
    python3 scripts/personas/render_persona.py --persona 30_hal_sutter --skill pitch-round --stdout
    python3 scripts/personas/render_persona.py --all --skill pitch-round   # render full roster

Output: .runtime/{skill}/{persona}.yaml (or stdout)
"""
import argparse
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
PERSONAS = ROOT / "skills/writer/personas"
SCHEMA = PERSONAS / "_schema_v5.yaml"
RUNTIME_ROOT = PERSONAS / ".runtime"


def load_schema():
    with open(SCHEMA) as f:
        return yaml.safe_load(f)


def load_persona(name: str):
    # Accept bare id or filename
    path = PERSONAS / (name if name.endswith(".yaml") else f"{name}.yaml")
    with open(path) as f:
        return yaml.safe_load(f), path


def render(persona: dict, skill: str, schema: dict):
    manifests = schema["skill_manifests"]
    if skill not in manifests:
        raise ValueError(f"unknown skill '{skill}'; known: {sorted(manifests)}")
    needed = set(manifests[skill])

    is_v5 = (persona.get("schema_version") == 5.0) or ("base" in persona)
    if not is_v5:
        # v4 graceful degradation — emit whole persona with a note
        return {
            "_runtime_note": "v4 persona: base-only degradation; modules absent.",
            "_skill": skill,
            **persona,
        }

    base = persona.get("base", {})
    mods_declared = persona.get("modules", {}) or {}
    prefer = set(base.get("prefer_load", []) or [])

    # Intersection: skill needs (minus 'base') ∪ persona.prefer_load, all ∩ persona.has
    wanted = (needed - {"base"}) | prefer
    loaded = {k: v for k, v in mods_declared.items() if k in wanted}
    unmet = wanted - set(loaded.keys())

    out = {
        "_runtime": {
            "skill": skill,
            "schema_version": 5.0,
            "modules_loaded": sorted(loaded.keys()),
            "modules_unmet": sorted(unmet),  # skill wanted these; persona doesn't have them → centroid default
        },
        "base": base,
    }
    if loaded:
        out["modules"] = loaded
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--persona", help="persona id (e.g. 30_hal_sutter) or filename")
    ap.add_argument("--all", action="store_true", help="render every persona in the roster")
    ap.add_argument("--skill", required=True, help="skill name (must exist in schema manifests)")
    ap.add_argument("--stdout", action="store_true", help="print to stdout instead of writing")
    args = ap.parse_args()

    schema = load_schema()
    if args.skill not in schema["skill_manifests"]:
        print(f"unknown skill: {args.skill}", file=sys.stderr)
        print(f"known: {sorted(schema['skill_manifests'])}", file=sys.stderr)
        sys.exit(2)

    if args.all:
        personas = sorted(PERSONAS.glob("*.yaml"))
        personas = [p for p in personas if not p.name.startswith("_")]
    elif args.persona:
        personas = [(PERSONAS / (args.persona if args.persona.endswith(".yaml") else f"{args.persona}.yaml"))]
    else:
        ap.error("--persona or --all required")

    out_dir = RUNTIME_ROOT / args.skill
    if not args.stdout:
        out_dir.mkdir(parents=True, exist_ok=True)

    for p_path in personas:
        with open(p_path) as f:
            persona = yaml.safe_load(f)
        rendered = render(persona, args.skill, schema)
        ytext = yaml.safe_dump(rendered, sort_keys=False, allow_unicode=True, width=100)
        if args.stdout:
            print(f"# ---- {p_path.name} ----")
            print(ytext)
        else:
            out_path = out_dir / p_path.name
            out_path.write_text(ytext)
            cov = rendered.get("_runtime", {}).get("modules_loaded", [])
            print(f"  wrote {out_path.relative_to(ROOT)}  [{','.join(cov) or 'base-only'}]")


if __name__ == "__main__":
    main()
