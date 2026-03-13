"""Project management — create, load, list, and manage project state."""

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

import yaml

from .config import PIPELINE_STEPS, PROJECTS_DIR, TEMPLATES_DIR


def list_projects() -> list[dict]:
    """Return list of projects with basic metadata."""
    projects = []
    if not PROJECTS_DIR.exists():
        return projects

    for p in sorted(PROJECTS_DIR.iterdir()):
        if not p.is_dir() or p.name.startswith("."):
            continue

        info = {"slug": p.name, "path": p, "name": p.name, "phase": "unknown"}

        # Read config for display name
        config_path = p / "PROJECT_CONFIG.yaml"
        if config_path.exists():
            try:
                with open(config_path) as f:
                    cfg = yaml.safe_load(f)
                proj = cfg.get("project", {})
                if isinstance(proj, dict):
                    info["name"] = proj.get("name", p.name)
                elif isinstance(proj, str):
                    info["name"] = proj
            except Exception:
                pass

        # Read state for phase
        state_path = p / ".state.json"
        if state_path.exists():
            try:
                with open(state_path) as f:
                    state = json.load(f)
                info["phase"] = state.get("current_phase", "unknown")
                info["gates_passed"] = state.get("gates_passed", [])
            except Exception:
                pass

        projects.append(info)

    return projects


def create_project(name: str, slug: str) -> Path:
    """Create a new project from templates. Returns project path."""
    project_path = PROJECTS_DIR / slug

    if project_path.exists():
        raise ValueError(f"Project '{slug}' already exists at {project_path}")

    # Create directory structure
    dirs = [
        "STORY/CHARACTER_SHEETS",
        "STORY/SCRIPTS",
        "STORY/WRITERS_ROOM",
        "REFERENCES/identity_sheets",
        "REFERENCES/hero_shots",
        "REFERENCES/location_refs",
        "REFERENCES/storyboards",
        "REFERENCES/voice_refs",
        "PRODUCTION",
        "DELIVERABLES",
        "INGEST",
    ]

    for d in dirs:
        (project_path / d).mkdir(parents=True, exist_ok=True)

    # Copy and customize PROJECT_CONFIG.yaml
    config_template = TEMPLATES_DIR / "PROJECT_CONFIG.yaml"
    if config_template.exists():
        with open(config_template) as f:
            config_text = f.read()
        config_text = config_text.replace('"My Project"', f'"{name}"')
        config_text = config_text.replace('"my-project"', f'"{slug}"')
        with open(project_path / "PROJECT_CONFIG.yaml", "w") as f:
            f.write(config_text)

    # Create initial .state.json
    state = {
        "version": "1.0",
        "project_slug": slug,
        "current_phase": "initialized",
        "current_state": "pending",
        "last_updated": datetime.now(timezone.utc).isoformat(),
        "gates_passed": [],
        "gates": {
            "gate_0_intake": {"status": "pending", "passed_at": None, "details": None},
            "gate_1_logline": {"status": "pending", "passed_at": None, "details": None},
            "gate_2_characters": {"status": "pending", "passed_at": None, "details": None},
            "gate_3_story": {"status": "pending", "passed_at": None, "details": None},
            "gate_4_script": {"status": "pending", "passed_at": None, "details": None},
            "gate_5_approved": {"status": "pending", "passed_at": None, "details": None},
            "gate_6_references": {"status": "pending", "passed_at": None, "details": None},
            "gate_7_shots": {"status": "pending", "passed_at": None, "details": None},
        },
        "skills_completed": [],
        "pipeline": {step["id"]: "pending" for step in PIPELINE_STEPS},
    }

    with open(project_path / ".state.json", "w") as f:
        json.dump(state, f, indent=2)

    return project_path


def load_state(project_path: Path) -> dict:
    """Load project state, creating pipeline tracking if missing."""
    state_path = project_path / ".state.json"
    if not state_path.exists():
        return {"pipeline": {step["id"]: "pending" for step in PIPELINE_STEPS}}

    with open(state_path) as f:
        state = json.load(f)

    # Ensure pipeline tracking exists (for older projects)
    if "pipeline" not in state:
        state["pipeline"] = {}
    for step in PIPELINE_STEPS:
        if step["id"] not in state["pipeline"]:
            # Infer status from gates_passed
            if step["gate"] and step["gate"].replace("gate_", "gate-").replace("_", "-") in state.get("gates_passed", []):
                state["pipeline"][step["id"]] = "complete"
            else:
                state["pipeline"][step["id"]] = "pending"

    return state


def save_state(project_path: Path, state: dict):
    """Save project state."""
    state["last_updated"] = datetime.now(timezone.utc).isoformat()
    with open(project_path / ".state.json", "w") as f:
        json.dump(state, f, indent=2)


def update_step_status(project_path: Path, step_id: str, status: str):
    """Update a single pipeline step status."""
    state = load_state(project_path)
    state["pipeline"][step_id] = status
    save_state(project_path, state)


def load_config(project_path: Path) -> dict:
    """Load PROJECT_CONFIG.yaml."""
    config_path = project_path / "PROJECT_CONFIG.yaml"
    if not config_path.exists():
        return {}
    with open(config_path) as f:
        return yaml.safe_load(f) or {}


def assess_project(project_path: Path) -> dict[str, str]:
    """Scan project files to infer pipeline step statuses.

    Returns a dict of step_id -> status based on what files exist.
    """
    p = project_path
    pipeline = {}

    def _has_files(rel_path: str, ext: str = "") -> bool:
        d = p / rel_path
        if not d.exists():
            return False
        if d.is_file():
            return True
        for f in d.rglob(f"*{ext}" if ext else "*"):
            if f.is_file() and not f.name.startswith("."):
                return True
        return False

    def _has_any(*paths: str) -> bool:
        return any(_has_files(path) for path in paths)

    def _file_exists(*paths: str) -> bool:
        return any((p / path).is_file() for path in paths)

    # -- Ingest
    pipeline["ingest"] = "complete" if _has_files("INGEST") else "pending"

    # -- Intake: CREATIVE_BRIEF.md exists
    pipeline["intake"] = "complete" if _file_exists(
        "STORY/CREATIVE_BRIEF.md"
    ) else "pending"

    # -- Writers Room: STORY_LOCK.md (v2+) means complete, v1 or review means active
    pipeline["writers_room"] = "complete" if _file_exists(
        "STORY/WRITERS_ROOM/STORY_LOCK.md"
    ) else ("active" if _has_files("STORY/WRITERS_ROOM") else "pending")

    # -- Logline: LOGLINE_LOCK.md
    pipeline["logline"] = "complete" if _file_exists(
        "STORY/LOGLINE_LOCK.md"
    ) else "pending"

    # -- Characters: CHARACTER_SHEETS has files
    pipeline["characters"] = "complete" if _has_files(
        "STORY/CHARACTER_SHEETS"
    ) else "pending"

    # -- Structure: episode beats or scene lists or episode structure
    has_structure = _file_exists("STORY/EPISODE_STRUCTURE.md")
    if not has_structure:
        story_dir = p / "STORY"
        if story_dir.exists():
            has_structure = any(
                f.name.endswith("_BEATS.md") or f.name.endswith("_SCENELIST.md") or f.name == "SEASON_GRID.md"
                for f in story_dir.iterdir() if f.is_file()
            )
    pipeline["structure"] = "complete" if has_structure else "pending"

    # -- Screenplay: SCRIPTS/ has .md files
    pipeline["screenplay"] = "complete" if _has_files(
        "STORY/SCRIPTS", ".md"
    ) else "pending"

    # -- Critique: CRITIQUE_REPORT exists (many projects skip this)
    has_critique = False
    story_dir = p / "STORY"
    if story_dir.exists():
        has_critique = any(f.name.startswith("CRITIQUE_REPORT") for f in story_dir.iterdir() if f.is_file())
    pipeline["critique"] = "complete" if has_critique else "skipped"

    # -- Style DNA: style guide file or locked style_dna in config
    has_style = _file_exists(
        "REFERENCES/VISUAL_STYLE_GUIDE.md",
        "VISUAL_PRODUCTION/STYLE_GUIDE/STYLEGUIDE_VISUAL.md",
    ) or _has_files("VISUAL_PRODUCTION/STYLE_GUIDE")
    if not has_style:
        config = load_config(project_path)
        style_dna = config.get("style_dna", {})
        if isinstance(style_dna, dict) and style_dna.get("locked"):
            has_style = True
    pipeline["style_dna"] = "complete" if has_style else "pending"

    # -- Character refs: hero_shots or identity_sheets have images
    pipeline["character_refs"] = "complete" if _has_any(
        "REFERENCES/hero_shots", "REFERENCES/identity_sheets",
        "REFERENCES/character_refs",
        "VISUAL_PRODUCTION/CHARACTER_REFS",
    ) else "pending"

    # -- Location refs
    pipeline["location_refs"] = "complete" if _has_any(
        "REFERENCES/location_refs",
        "VISUAL_PRODUCTION/LOCATION_REFS",
    ) else "pending"

    # -- Shot lists: any shot_list*.yaml in PRODUCTION
    has_shots = False
    prod_dir = p / "PRODUCTION"
    if prod_dir.exists():
        has_shots = any(prod_dir.rglob("shot_list*.yaml"))
    pipeline["shot_lists"] = "complete" if has_shots else "pending"

    # -- Storyboards
    pipeline["storyboards"] = "complete" if _has_any(
        "REFERENCES/storyboards",
        "VISUAL_PRODUCTION/STORYBOARDS",
    ) else "pending"

    # -- Paper cut: any paper_cut*.mp4 or paper-cut*.mp4
    has_papercut = False
    if prod_dir.exists():
        has_papercut = any(
            f.name.startswith("paper") and f.suffix == ".mp4"
            for f in prod_dir.rglob("*.mp4")
        )
    pipeline["paper_cut"] = "complete" if has_papercut else "pending"

    # -- Frames: frames/ dirs with images
    has_frames = False
    if prod_dir.exists():
        has_frames = any(prod_dir.rglob("frames/*.png")) or any(prod_dir.rglob("frames/*.jpg"))
    pipeline["frames"] = "complete" if has_frames else "pending"

    # -- Video: clips/ dirs with mp4s
    has_clips = False
    if prod_dir.exists():
        has_clips = any(prod_dir.rglob("clips/*.mp4"))
    pipeline["video"] = "complete" if has_clips else "pending"

    # -- Assembly: assembly/ dirs with mp4s
    has_assembly = False
    if prod_dir.exists():
        has_assembly = any(prod_dir.rglob("assembly/*.mp4"))
    pipeline["assembly"] = "complete" if has_assembly else "pending"

    # -- Sound design & color grade: hard to detect, leave pending unless delivered
    pipeline["sound_design"] = "pending"
    pipeline["color_grade"] = "pending"

    # -- Delivery
    pipeline["delivery"] = "complete" if _has_files(
        "DELIVERABLES", ".mp4"
    ) else "pending"

    # If we have delivery, mark sound/color as complete too (they happened)
    if pipeline["delivery"] == "complete":
        if pipeline["assembly"] == "complete":
            pipeline["sound_design"] = "complete"
            pipeline["color_grade"] = "complete"

    # Backfill: if a later step is complete, skip all earlier pending steps.
    # Walk the pipeline in order; track the last complete step index.
    step_ids = [s["id"] for s in PIPELINE_STEPS]
    last_complete_idx = -1
    for i, sid in enumerate(step_ids):
        if pipeline.get(sid) == "complete":
            last_complete_idx = i

    if last_complete_idx > 0:
        for i in range(last_complete_idx):
            sid = step_ids[i]
            if pipeline.get(sid) == "pending":
                pipeline[sid] = "skipped"

    # Infer current phase
    phase = "initialized"
    if pipeline["intake"] == "complete":
        phase = "pre-production"
    if pipeline["character_refs"] == "complete" or pipeline["style_dna"] == "complete":
        phase = "visual-development"
    if pipeline["shot_lists"] == "complete" or pipeline["frames"] == "complete":
        phase = "production"
    if pipeline["assembly"] == "complete":
        phase = "post-production"
    if pipeline["delivery"] == "complete":
        phase = "delivered"

    return {"pipeline": pipeline, "phase": phase}


def assess_and_save(project_path: Path) -> dict:
    """Assess project state from files and save to .state.json."""
    assessment = assess_project(project_path)
    state = load_state(project_path)
    state["pipeline"] = assessment["pipeline"]
    state["current_phase"] = assessment["phase"]
    save_state(project_path, state)
    return assessment


def get_ingest_summary(project_path: Path) -> list[str]:
    """List files in the INGEST directory."""
    ingest_dir = project_path / "INGEST"
    if not ingest_dir.exists():
        return []
    files = []
    for f in sorted(ingest_dir.rglob("*")):
        if f.is_file() and not f.name.startswith("."):
            files.append(str(f.relative_to(ingest_dir)))
    return files
