"""Utilities for loading and working with writer persona YAML files."""

import yaml
from pathlib import Path
from .config import CODEYWOOD_ROOT

PERSONAS_DIR = CODEYWOOD_ROOT / "skills" / "writer" / "personas"


def list_personas() -> list[dict]:
    """List available writer personas with summary fields.

    Returns list of dicts with: name (filename stem), agent_name, room_title,
    primary_function, versatility_level, genre_affinity (list).
    Handles both v2 schema format (agent_name field) and simpler format (name field).
    Skips _schema.yaml.
    """
    personas = []
    for path in sorted(PERSONAS_DIR.glob("*.yaml")):
        if path.stem.startswith("_"):
            continue
        try:
            data = yaml.safe_load(path.read_text())
        except Exception:
            continue
        if not isinstance(data, dict):
            continue
        phil = data.get("creative_philosophy", {}) or {}
        personas.append({
            "name": path.stem,
            "agent_name": data.get("agent_name") or data.get("name", path.stem),
            "room_title": data.get("room_title", ""),
            "primary_function": data.get("primary_function", ""),
            "versatility_level": data.get("versatility_level", ""),
            "genre_affinity": phil.get("genre_affinity", []) or [],
        })
    return personas


def load_persona(name: str) -> dict:
    """Load full persona YAML by filename stem (e.g., 'tad_gridley').

    Raises FileNotFoundError if not found.
    """
    path = PERSONAS_DIR / f"{name}.yaml"
    if not path.exists():
        raise FileNotFoundError(f"Persona not found: {path}")
    return yaml.safe_load(path.read_text())


def build_head_writer_preamble(persona: dict) -> str:
    """Extract key fields from a persona dict into a ~300 word creative lens preamble.

    Returns a system instruction paragraph telling Claude to adopt this persona's
    creative perspective. Handles missing fields gracefully.
    """
    agent_name = persona.get("agent_name") or persona.get("name", "Unknown")
    room_title = persona.get("room_title", "")
    phil = persona.get("creative_philosophy", {}) or {}
    craft = persona.get("craft_method", {}) or {}
    taste = persona.get("taste", {}) or {}
    polemics = persona.get("polemics", {}) or {}

    parts = []

    # Opening identity
    if room_title:
        parts.append(
            f"You are {agent_name}, {room_title}."
        )
    else:
        parts.append(f"You are {agent_name}.")

    # Story ontology and thesis
    ontology = phil.get("story_ontology", "")
    thesis = phil.get("one_line_thesis", "")
    # Some ontologies start with "A story is..." — avoid doubling
    if ontology:
        if ontology.lower().startswith("a story"):
            parts.append(f"To you, {ontology.rstrip()}")
        else:
            parts.append(f"To you, a story is {ontology.rstrip()}")
    if thesis:
        parts.append(thesis)

    # What they optimize for
    optimize = phil.get("what_they_optimize_for", [])
    if optimize:
        joined = ", ".join(optimize[:-1]) + f", and {optimize[-1]}" if len(optimize) > 1 else optimize[0]
        parts.append(f"You optimize every project for {joined}.")

    # Character model
    char_model = craft.get("character_model", "")
    char_method = craft.get("character_model_method", "")
    if char_model and char_method:
        parts.append(f"Your character model is {char_model}: {char_method}")
    elif char_model:
        parts.append(f"Your character model is {char_model}.")

    # Information strategy
    info_strat = craft.get("information_strategy", "")
    if info_strat:
        parts.append(
            f"Your preferred information strategy is {info_strat}."
        )

    # Taste signature
    taste_sig = taste.get("taste_signature", "")
    if taste_sig:
        parts.append(f"Your taste signature: {taste_sig}")

    # Hill they will die on
    hill = polemics.get("hill_they_will_die_on", "")
    if hill:
        parts.append(
            f"The craft principle you will never compromise on: {hill}"
        )

    # Closing instruction
    parts.append(
        "Apply this creative lens to all story development work. "
        "Let these instincts shape your feedback, pitches, and rewrites "
        "without breaking character or narrating your own persona."
    )

    return " ".join(parts)


def get_room_config(project_path: Path) -> dict:
    """Load writers_room config from PROJECT_CONFIG.yaml.

    Returns dict with head_writer (str or None), room (list of str), room_size (int).
    Returns defaults if writers_room section doesn't exist.
    """
    defaults = {"head_writer": None, "room": [], "room_size": 5}
    config_path = project_path / "PROJECT_CONFIG.yaml"
    if not config_path.exists():
        return defaults
    try:
        data = yaml.safe_load(config_path.read_text())
    except Exception:
        return defaults
    if not isinstance(data, dict):
        return defaults
    wr = data.get("writers_room", {}) or {}
    return {
        "head_writer": wr.get("head_writer"),
        "room": wr.get("room", []) or [],
        "room_size": wr.get("room_size", 5),
    }


def get_eligible_head_writers() -> list[dict]:
    """Return personas eligible to be head writers.

    Eligible = versatility_level is 'hybrid' or 'generalist',
    OR the persona has a head-writer-related room_title.
    Returns same format as list_personas().
    """
    head_writer_keywords = {"head writer", "showrunner", "lead writer", "head_writer"}
    eligible = []
    for p in list_personas():
        level = (p.get("versatility_level") or "").lower()
        title = (p.get("room_title") or "").lower()
        if level in ("hybrid", "generalist"):
            eligible.append(p)
        elif any(kw in title for kw in head_writer_keywords):
            eligible.append(p)
    return eligible
