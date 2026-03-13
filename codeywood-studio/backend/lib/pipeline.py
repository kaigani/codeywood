"""Pipeline step logic — determine available actions for each step."""

from pathlib import Path

from .config import PIPELINE_STEPS, PHASES
from .personas import get_room_config, load_persona, build_head_writer_preamble, PERSONAS_DIR
from .project import load_config


def get_steps_by_phase() -> dict[str, list[dict]]:
    """Group pipeline steps by phase."""
    grouped = {}
    for step in PIPELINE_STEPS:
        phase = step["phase"]
        if phase not in grouped:
            grouped[phase] = []
        grouped[phase].append(step)
    return grouped


def get_step(step_id: str) -> dict | None:
    """Get a pipeline step by ID."""
    for step in PIPELINE_STEPS:
        if step["id"] == step_id:
            return step
    return None


def get_current_step(pipeline_state: dict) -> dict | None:
    """Find the first non-complete, non-skipped step."""
    for step in PIPELINE_STEPS:
        status = pipeline_state.get(step["id"], "pending")
        if status in ("pending", "active", "failed"):
            return step
    return None


def get_step_actions(step: dict, status: str) -> list[str]:
    """Return available actions for a step given its status."""
    actions = []
    if status == "pending":
        actions.extend(["start", "skip"])
    elif status == "active":
        actions.extend(["complete", "restart", "skip"])
    elif status == "complete":
        actions.extend(["restart", "view"])
    elif status == "skipped":
        actions.extend(["unskip", "start"])
    elif status == "failed":
        actions.extend(["restart", "skip"])
    return actions


def _head_writer_preamble(project_path: Path) -> str:
    """Load head writer persona and build preamble for prompt injection."""
    config = load_config(project_path)
    wr = config.get("writers_room", {})
    if not isinstance(wr, dict):
        return ""
    hw_name = wr.get("head_writer")
    if not hw_name:
        return ""
    try:
        persona = load_persona(hw_name)
        preamble = build_head_writer_preamble(persona)
        return f"\n\nCREATIVE LENS — HEAD WRITER:\n{preamble}\n"
    except FileNotFoundError:
        return ""


# Steps where the head writer's creative lens applies
CREATIVE_STEPS = {"writers_room", "logline", "characters", "structure", "screenplay", "critique"}


def build_claude_prompt(step: dict, project_path: Path, context: str = "") -> str:
    """Build a prompt string for Claude Code to execute a pipeline step."""
    project_name = project_path.name
    skill = step.get("skill", "")
    hw_preamble = _head_writer_preamble(project_path) if step["id"] in CREATIVE_STEPS else ""

    prompts = {
        "ingest": f"""Review the materials in {project_path}/INGEST/ directory.
Catalog what's there (scripts, notes, images, references, etc.).
Summarize the materials and suggest how they map to the Codeywood pipeline.
{context}""",

        "intake": f"""Run the story-intake skill for project '{project_name}'.
Working directory: {project_path}
Conduct the creative interview and generate CREATIVE_BRIEF.md and POWER_STACK.md in STORY/.
Read the skill at skills/core/story-intake/SKILL.md for full instructions.
{context}""",

        "writers_room": f"""Run the writers-room skill for project '{project_name}'.
Working directory: {project_path}
Read skills/writer/writers-room/SKILL.md for the full process.
Persona files are in skills/writer/personas/ (schema: skills/writer/personas/_schema.yaml).
Check PROJECT_CONFIG.yaml for writers_room config (head_writer + room members + lanes).
If no head writer is configured, run Head Writer Selection first (SKILL.md Phase 1).
If no room is assembled, run Room Assembly (SKILL.md Phase 2).
Use STORY/CREATIVE_BRIEF.md and STORY/POWER_STACK.md as inputs.
Process: Head writer writes Story Lock v1 → Room reviews (one flag per writer, sort into accept/debate/table) → Update to Story Lock v2.
{hw_preamble}{context}""",

        "logline": f"""Run the logline-architect skill for project '{project_name}'.
Working directory: {project_path}
Read skills/core/logline-architect/SKILL.md for tournament selection process.
Generate STORY/LOGLINE_LOCK.md.
{hw_preamble}{context}""",

        "characters": f"""Run the character-architect skill for project '{project_name}'.
Working directory: {project_path}
Read skills/core/character-architect/SKILL.md for full instructions.
Generate CHARACTER_SHEETS, RELATIONSHIP_MAP.json, CAST_LIST.md in STORY/.
{hw_preamble}{context}""",

        "structure": f"""Run the story-architect skill for project '{project_name}'.
Working directory: {project_path}
Read skills/core/story-architect/SKILL.md.
Generate episode beats, scene lists, and season grid in STORY/.
{hw_preamble}{context}""",

        "screenplay": f"""Run the screenplay-writer skill for project '{project_name}'.
Working directory: {project_path}
Read skills/core/screenplay-writer/SKILL.md.
Generate full screenplay in STORY/SCRIPTS/.
{hw_preamble}{context}""",

        "critique": f"""Run the story-critic skill for project '{project_name}'.
Working directory: {project_path}
Read skills/core/story-critic/SKILL.md.
Evaluate the screenplay and produce CRITIQUE_REPORT. Score >= 70 passes Gate 5.
{hw_preamble}{context}""",

        "style_dna": f"""Run visual style DNA exploration for project '{project_name}'.
Working directory: {project_path}
Read skills/production/visual-style-guide/SKILL.md.
Explore 3-4 style directions and lock the winner in PROJECT_CONFIG.yaml.
{context}""",

        "character_refs": f"""Generate character references for project '{project_name}'.
Working directory: {project_path}
Read skills/production/character-reference-generator/SKILL.md.
Generate hero shots and identity sheets for all characters.
{context}""",

        "location_refs": f"""Generate location references for project '{project_name}'.
Working directory: {project_path}
Read skills/production/location-reference-generator/SKILL.md.
Generate location reference grids for all locations.
{context}""",

        "shot_lists": f"""Run the directors-room skill for project '{project_name}'.
Working directory: {project_path}
Read skills/production/directors-room/SKILL.md.
Generate shot lists and clip definitions for each scene.
{context}""",

        "storyboards": f"""Generate storyboards for project '{project_name}'.
Working directory: {project_path}
Generate 3x2 shot grids for each scene.
{context}""",

        "paper_cut": f"""Generate paper cuts for project '{project_name}'.
Working directory: {project_path}
Read skills/production/paper-cut/SKILL.md.
Generate static frame + dialogue assemblies for review.
{context}""",

        "frames": f"""Generate start frames for video clips for project '{project_name}'.
Working directory: {project_path}
Use the appropriate image generation pipeline based on PROJECT_CONFIG.yaml.
{context}""",

        "video": f"""Generate video clips for project '{project_name}'.
Working directory: {project_path}
Read skills/production/video-director/SKILL.md for T2V/I2V best practices.
{context}""",

        "assembly": f"""Assemble scenes for project '{project_name}'.
Working directory: {project_path}
Read skills/editor/SKILL.md for editing best practices.
Use smart_assemble.py with EDL files for transition-aware assembly.
{context}""",

        "sound_design": f"""Run sound design pass for project '{project_name}'.
Working directory: {project_path}
Read skills/sound-designer/SKILL.md for audio layering and mixing.
{context}""",

        "color_grade": f"""Run visual QC and color grading for project '{project_name}'.
Working directory: {project_path}
Read skills/art-director/SKILL.md for visual coherence checks.
{context}""",

        "delivery": f"""Prepare final deliverables for project '{project_name}'.
Working directory: {project_path}
Export assembled episodes to DELIVERABLES/.
{context}""",
    }

    return prompts.get(step["id"], f"Execute step '{step['name']}' for project at {project_path}. {context}")
