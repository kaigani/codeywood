#!/usr/bin/env python3
"""Validate a v5 persona YAML against _schema_v5.yaml.

Usage:
    python3 scripts/personas/validate_v5.py skills/writer/personas/30_hal_sutter.yaml
    python3 scripts/personas/validate_v5.py --all
"""
import argparse
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
PERSONAS = ROOT / "skills/writer/personas"
SCHEMA = PERSONAS / "_schema_v5.yaml"

EMOTION_VOCAB = {"wonder","delight","awe","melancholy","dread","tension","recognition",
                 "ache","grief","joy","rage","tenderness","curiosity","discomfort",
                 "catharsis","triumph","nostalgia","alarm","warmth","exhilaration"}
REGISTER_VOCAB = {"warm","cool","dry","plaintive","ecstatic","austere","wry","tender",
                  "severe","ironic","sincere","operatic","deadpan","lyrical",
                  "muscular","playful","elegiac","reverent"}

# Keywords signaling mass-audience practitioner clusters. A monoculture list is
# flagged if ALL influences match a single cluster.
MASS_AUDIENCE_HINTS = {
    "pop_film": ["spielberg","cameron","nolan","feige","marvel","pixar","miyazaki",
                 "jenkins","coogler","villeneuve","gerwig","waititi","peele"],
    "pop_tv":   ["gilligan","waller-bridge","fey","schur","feige","abbott","kohan",
                 "rhimes","chase","simon","benioff"],
    "genre":    ["carpenter","craven","king","barker","flanagan","aster","eggers",
                 "del toro","bong","park","refn"],
    "kids":     ["bird","docter","selick","miyazaki","linklater","henson"],
    "reality":  [],  # handled separately
}
PRESTIGE_CLUSTER = ["bresson","dreyer","tarkovsky","ozu","kiarostami","angelopoulos",
                    "akerman","bergman","haneke","ceylan","apichatpong","hou"]


def err(path, msg):  print(f"  ERR {path}: {msg}"); return False
def warn(path, msg): print(f"  WARN {path}: {msg}")


def check_len(val, maxlen, path, name):
    if isinstance(val, str) and len(val) > maxlen:
        err(path, f"{name} is {len(val)} chars, max {maxlen}")
        return False
    return True


def validate_base(p, path):
    ok = True
    b = p.get("base") or p  # allow either nested or flat
    required = ["agent_name","room_title","versatility","mechanism",
                "mechanism_non_literal","audience_cohort","affective_palette",
                "philosophy","engine","polemic","influences"]
    for f in required:
        if f not in b or b[f] in (None, "", []):
            err(path, f"missing BASE field: {f}"); ok = False

    if b.get("versatility") not in {"specialist","hybrid","generalist"}:
        err(path, f"versatility must be specialist|hybrid|generalist"); ok = False

    for f in ["mechanism","mechanism_non_literal","audience_cohort",
              "philosophy","engine","polemic"]:
        if f in b: ok = check_len(b[f], 200, path, f) and ok

    ap = b.get("affective_palette", {})
    if ap.get("primary_emotion") not in EMOTION_VOCAB:
        err(path, f"primary_emotion '{ap.get('primary_emotion')}' not in vocab"); ok = False
    if ap.get("register") not in REGISTER_VOCAB:
        err(path, f"register '{ap.get('register')}' not in vocab"); ok = False
    r = ap.get("restraint")
    if not (isinstance(r, int) and 1 <= r <= 5):
        err(path, f"restraint must be int 1-5, got {r}"); ok = False

    infs = b.get("influences", []) or []
    if not (5 <= len(infs) <= 7):
        err(path, f"influences count {len(infs)}, must be 5-7"); ok = False

    # Monoculture check: warn if all influences fall into the prestige cluster
    low = [str(x).lower() for x in infs]
    prestige_hits = sum(1 for n in low if any(k in n for k in PRESTIGE_CLUSTER))
    mass_hits = 0
    for cluster in MASS_AUDIENCE_HINTS.values():
        mass_hits += sum(1 for n in low if any(k in n for k in cluster))
    if mass_hits < 2:
        warn(path, f"audit rule: only {mass_hits} clearly mass-audience influences (need ≥2); verify or diversify")
    if prestige_hits >= len(infs) - 1:
        warn(path, "monoculture: influences skew all-prestige")

    # Mechanism / non_literal must differ substantively
    if b.get("mechanism") and b.get("mechanism_non_literal"):
        if b["mechanism"].strip().lower() == b["mechanism_non_literal"].strip().lower():
            err(path, "mechanism and mechanism_non_literal are identical"); ok = False
    return ok


def validate_modules(p, path):
    ok = True
    mods = p.get("modules", {}) or {}
    known = {"architecture","dialogue","scene_craft","vision",
             "room_behavior","slot","constraints","psychology"}
    for name, body in mods.items():
        if name not in known:
            err(path, f"unknown module: {name}"); ok = False
        if name == "constraints":
            fm = (body or {}).get("fail_modes", []) or []
            if len(fm) < 2:
                err(path, f"constraints.fail_modes needs ≥2 items, got {len(fm)}"); ok = False
    return ok


def module_coverage(p):
    mods = p.get("modules", {}) or {}
    return sorted(mods.keys())


def validate_file(path: Path) -> bool:
    try:
        with open(path) as f:
            p = yaml.safe_load(f)
    except Exception as e:
        print(f"  ERR {path.name}: YAML parse failed: {e}"); return False
    if not p:
        print(f"  ERR {path.name}: empty"); return False
    is_v5 = (p.get("schema_version") == 5.0) or ("base" in p)
    if not is_v5:
        print(f"  SKIP {path.name}: v4 (no schema_version:5.0 / no base:)"); return True  # not a failure
    ok = validate_base(p, path.name)
    ok = validate_modules(p, path.name) and ok
    cov = module_coverage(p)
    status = "OK " if ok else "FAIL"
    print(f"  {status} {path.name}  modules=[{','.join(cov) or 'base-only'}]")
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path", nargs="?", help="persona YAML path")
    ap.add_argument("--all", action="store_true", help="validate all personas/*.yaml")
    args = ap.parse_args()

    if args.all:
        paths = sorted(PERSONAS.glob("*.yaml"))
        paths = [p for p in paths if not p.name.startswith("_")]
    elif args.path:
        paths = [Path(args.path)]
    else:
        ap.error("provide a path or --all")

    results = [validate_file(p) for p in paths]
    fails = sum(1 for r in results if not r)
    print(f"\n{len(results)} validated, {fails} failures")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
