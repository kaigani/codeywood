"""Codeywood Studio configuration and constants."""

from pathlib import Path

# Paths
CODEYWOOD_ROOT = Path(__file__).resolve().parent.parent.parent.parent
PROJECTS_DIR = CODEYWOOD_ROOT / "projects"
TEMPLATES_DIR = CODEYWOOD_ROOT / "templates"
SKILLS_DIR = CODEYWOOD_ROOT / "skills"
SCRIPTS_DIR = CODEYWOOD_ROOT / "scripts"
VENV_PYTHON = CODEYWOOD_ROOT / "scripts" / "venv" / "bin" / "python3"

# Pipeline steps — ordered sequence with metadata
# Each step maps to a quality gate or production phase
PIPELINE_STEPS = [
    {
        "id": "ingest",
        "name": "Material Ingestion",
        "gate": None,
        "phase": "pre-production",
        "description": "Import existing materials (scripts, notes, images, references)",
        "skill": None,
        "auto": False,
    },
    {
        "id": "intake",
        "name": "Creative Intake",
        "gate": "gate_0_intake",
        "phase": "pre-production",
        "description": "Creative interview → CREATIVE_BRIEF.md + POWER_STACK.md",
        "skill": "core/story-intake",
        "auto": False,
    },
    {
        "id": "writers_room",
        "name": "Writers Room",
        "gate": None,
        "phase": "pre-production",
        "description": "Persona-driven story development (head writer + room, 3 rounds)",
        "skill": "writer/writers-room",
        "auto": False,
    },
    {
        "id": "logline",
        "name": "Logline Lock",
        "gate": "gate_1_logline",
        "phase": "pre-production",
        "description": "Generate and lock logline via tournament selection",
        "skill": "core/logline-architect",
        "auto": False,
    },
    {
        "id": "characters",
        "name": "Character Development",
        "gate": "gate_2_characters",
        "phase": "pre-production",
        "description": "Character sheets, relationship map, cast list",
        "skill": "core/character-architect",
        "auto": False,
    },
    {
        "id": "structure",
        "name": "Story Structure",
        "gate": "gate_3_story",
        "phase": "pre-production",
        "description": "Episode beats, scene lists, season grid",
        "skill": "core/story-architect",
        "auto": False,
    },
    {
        "id": "screenplay",
        "name": "Screenplay",
        "gate": "gate_4_script",
        "phase": "pre-production",
        "description": "Full screenplay with dialogue and visual metadata",
        "skill": "core/screenplay-writer",
        "auto": False,
    },
    {
        "id": "critique",
        "name": "Story Critique",
        "gate": "gate_5_approved",
        "phase": "pre-production",
        "description": "Quality assessment — score >= 70 to pass",
        "skill": "core/story-critic",
        "auto": False,
    },
    {
        "id": "style_dna",
        "name": "Visual Style DNA",
        "gate": None,
        "phase": "visual-development",
        "description": "Explore 3-4 style directions, lock winner",
        "skill": "production/visual-style-guide",
        "auto": False,
    },
    {
        "id": "character_refs",
        "name": "Character References",
        "gate": "gate_6_references",
        "phase": "visual-development",
        "description": "Hero shots, identity sheets, expression sheets",
        "skill": "production/character-reference-generator",
        "auto": False,
    },
    {
        "id": "location_refs",
        "name": "Location References",
        "gate": "gate_6_references",
        "phase": "visual-development",
        "description": "Location reference grids (2x2 composites)",
        "skill": "production/location-reference-generator",
        "auto": False,
    },
    {
        "id": "shot_lists",
        "name": "Shot Lists",
        "gate": "gate_7_shots",
        "phase": "production",
        "description": "Directors room → shot specs + clip definitions",
        "skill": "production/directors-room",
        "auto": False,
    },
    {
        "id": "storyboards",
        "name": "Storyboards",
        "gate": "gate_7_shots",
        "phase": "production",
        "description": "3x2 shot grids per scene for visual preview",
        "skill": "production/shot-image-generator",
        "auto": False,
    },
    {
        "id": "paper_cut",
        "name": "Paper Cut",
        "gate": None,
        "phase": "production",
        "description": "Static frames + dialogue + direction narration assembly",
        "skill": "production/paper-cut",
        "auto": False,
    },
    {
        "id": "frames",
        "name": "Frame Generation",
        "gate": None,
        "phase": "production",
        "description": "Generate start frames for video clips",
        "skill": "production/shot-image-generator",
        "auto": False,
    },
    {
        "id": "video",
        "name": "Video Generation",
        "gate": None,
        "phase": "production",
        "description": "T2V / I2V clip generation (LTX-2, Kling, etc.)",
        "skill": "production/video-director",
        "auto": False,
    },
    {
        "id": "assembly",
        "name": "Scene Assembly",
        "gate": None,
        "phase": "post-production",
        "description": "EDL-driven assembly with transitions and audio",
        "skill": "editor",
        "auto": False,
    },
    {
        "id": "sound_design",
        "name": "Sound Design",
        "gate": None,
        "phase": "post-production",
        "description": "Audio layers, mixing, dialogue, L/J-cuts",
        "skill": "sound-designer",
        "auto": False,
    },
    {
        "id": "color_grade",
        "name": "Color & Visual QC",
        "gate": None,
        "phase": "post-production",
        "description": "Color consistency, visual coherence, art direction",
        "skill": "art-director",
        "auto": False,
    },
    {
        "id": "delivery",
        "name": "Final Delivery",
        "gate": None,
        "phase": "delivery",
        "description": "Export final deliverables",
        "skill": None,
        "auto": False,
    },
]

# Phase display names and colors
PHASES = {
    "pre-production": {"label": "Pre-Production", "color": "cyan"},
    "visual-development": {"label": "Visual Development", "color": "magenta"},
    "production": {"label": "Production", "color": "yellow"},
    "post-production": {"label": "Post-Production", "color": "green"},
    "delivery": {"label": "Delivery", "color": "bright_white"},
}

# Status indicators
STATUS_ICONS = {
    "pending": "○",
    "active": "◉",
    "complete": "●",
    "skipped": "⊘",
    "failed": "✗",
}

STATUS_COLORS = {
    "pending": "dim",
    "active": "bold yellow",
    "complete": "bold green",
    "skipped": "dim italic",
    "failed": "bold red",
}
