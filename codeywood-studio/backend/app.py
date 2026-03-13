#!/usr/bin/env python3
"""Codeywood Studio — Flask API backend."""

import json
import os
import shutil
import subprocess
from pathlib import Path

from flask import Flask, jsonify, request, Response, send_from_directory, stream_with_context

from lib.config import PIPELINE_STEPS, PHASES, CODEYWOOD_ROOT
from lib.project import (
    list_projects,
    create_project,
    load_state,
    save_state,
    load_config,
    update_step_status,
    get_ingest_summary,
    assess_and_save,
)
from lib.pipeline import (
    get_steps_by_phase,
    get_step,
    get_current_step,
    build_claude_prompt,
)
from lib.personas import (
    list_personas as _list_personas,
    load_persona,
    get_room_config,
    get_eligible_head_writers,
)

# Resolve frontend dist path (for production serving)
FRONTEND_DIST = Path(__file__).resolve().parent.parent / "frontend" / "dist"

app = Flask(__name__)


# ── SPA Serving (production) ─────────────────────────────────────────────────

@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve_spa(path):
    """Serve React SPA. In dev, Vite handles this via proxy."""
    if path and path.startswith("api/"):
        return jsonify({"error": "Not found"}), 404
    if path and FRONTEND_DIST.exists() and (FRONTEND_DIST / path).exists():
        return send_from_directory(str(FRONTEND_DIST), path)
    if FRONTEND_DIST.exists() and (FRONTEND_DIST / "index.html").exists():
        return send_from_directory(str(FRONTEND_DIST), "index.html")
    return "<h1>Codeywood Studio</h1><p>Run <code>cd frontend && npm run build</code> or use Vite dev server.</p>", 200


# ── API: Projects ────────────────────────────────────────────────────────────

@app.route("/api/projects")
def api_list_projects():
    projects = list_projects()
    result = []
    for p in projects:
        state = load_state(p["path"])
        pipeline = state.get("pipeline", {})
        current = get_current_step(pipeline)

        result.append({
            "slug": p["slug"],
            "name": p["name"],
            "phase": p.get("phase", "unknown"),
            "current_step": current["id"] if current else None,
            "current_step_name": current["name"] if current else "All Complete",
            "progress": _calc_progress(pipeline),
        })
    return jsonify(result)


@app.route("/api/projects", methods=["POST"])
def api_create_project():
    data = request.json
    name = data.get("name", "").strip()
    slug = data.get("slug", "").strip()

    if not name or not slug:
        return jsonify({"error": "Name and slug required"}), 400

    try:
        path = create_project(name, slug)
        return jsonify({"slug": slug, "path": str(path)})
    except ValueError as e:
        return jsonify({"error": str(e)}), 409


# ── API: Assess ──────────────────────────────────────────────────────────────

@app.route("/api/projects/<slug>/assess", methods=["POST"])
def api_assess_project(slug):
    """Scan project files and update pipeline status."""
    project_path = CODEYWOOD_ROOT / "projects" / slug
    if not project_path.exists():
        return jsonify({"error": "Project not found"}), 404
    result = assess_and_save(project_path)
    return jsonify(result)


@app.route("/api/assess-all", methods=["POST"])
def api_assess_all():
    """Assess all projects at once."""
    projects = list_projects()
    results = {}
    for p in projects:
        result = assess_and_save(p["path"])
        results[p["slug"]] = result
    return jsonify(results)


# ── API: Pipeline ────────────────────────────────────────────────────────────

@app.route("/api/projects/<slug>/pipeline")
def api_pipeline(slug):
    project_path = CODEYWOOD_ROOT / "projects" / slug
    if not project_path.exists():
        return jsonify({"error": "Project not found"}), 404

    config = load_config(project_path)
    state = load_state(project_path)
    pipeline = state.get("pipeline", {})

    phases = []
    for phase_id, phase_info in PHASES.items():
        steps = []
        for step in PIPELINE_STEPS:
            if step["phase"] != phase_id:
                continue
            status = pipeline.get(step["id"], "pending")
            steps.append({
                "id": step["id"],
                "name": step["name"],
                "description": step["description"],
                "gate": step["gate"],
                "skill": step["skill"],
                "status": status,
            })
        if steps:
            phases.append({
                "id": phase_id,
                "label": phase_info["label"],
                "color": phase_info["color"],
                "steps": steps,
            })

    current = get_current_step(pipeline)
    return jsonify({
        "project": {
            "name": _project_name(config, slug),
            "slug": slug,
            "phase": state.get("current_phase", "unknown"),
        },
        "phases": phases,
        "current_step": current["id"] if current else None,
        "progress": _calc_progress(pipeline),
    })


@app.route("/api/projects/<slug>/steps/<step_id>/status", methods=["PUT"])
def api_update_step(slug, step_id):
    project_path = CODEYWOOD_ROOT / "projects" / slug
    if not project_path.exists():
        return jsonify({"error": "Project not found"}), 404

    data = request.json
    status = data.get("status")
    if status not in ("pending", "active", "complete", "skipped", "failed"):
        return jsonify({"error": "Invalid status"}), 400

    update_step_status(project_path, step_id, status)
    return jsonify({"ok": True})


@app.route("/api/projects/<slug>/steps/<step_id>/prompt")
def api_step_prompt(slug, step_id):
    project_path = CODEYWOOD_ROOT / "projects" / slug
    step = get_step(step_id)
    if not step:
        return jsonify({"error": "Step not found"}), 404

    context = request.args.get("context", "")
    prompt = build_claude_prompt(step, project_path, context)
    return jsonify({"prompt": prompt})


@app.route("/api/projects/<slug>/steps/<step_id>/outputs")
def api_step_outputs(slug, step_id):
    project_path = CODEYWOOD_ROOT / "projects" / slug
    if not project_path.exists():
        return jsonify({"error": "Project not found"}), 404

    output_map = {
        "ingest": ["INGEST"],
        "intake": ["STORY/CREATIVE_BRIEF.md", "STORY/POWER_STACK.md"],
        "writers_room": ["STORY/WRITERS_ROOM"],
        "logline": ["STORY/LOGLINE_LOCK.md"],
        "characters": ["STORY/CHARACTER_SHEETS", "STORY/RELATIONSHIP_MAP.json", "STORY/CAST_LIST.md"],
        "structure": ["STORY"],
        "screenplay": ["STORY/SCRIPTS"],
        "critique": ["STORY"],
        "style_dna": ["REFERENCES"],
        "character_refs": ["REFERENCES/hero_shots", "REFERENCES/identity_sheets"],
        "location_refs": ["REFERENCES/location_refs"],
        "shot_lists": ["PRODUCTION"],
        "storyboards": ["REFERENCES/storyboards"],
        "paper_cut": ["PRODUCTION"],
        "frames": ["PRODUCTION"],
        "video": ["PRODUCTION"],
        "assembly": ["PRODUCTION"],
        "sound_design": ["PRODUCTION"],
        "color_grade": ["PRODUCTION"],
        "delivery": ["DELIVERABLES"],
    }

    paths = output_map.get(step_id, [])
    outputs = []

    for rel_path in paths:
        full_path = project_path / rel_path
        if full_path.is_file():
            outputs.append({
                "path": rel_path,
                "type": "file",
                "size": full_path.stat().st_size,
            })
        elif full_path.is_dir():
            files = [f for f in full_path.rglob("*") if f.is_file() and not f.name.startswith(".")]
            if files:
                outputs.append({
                    "path": rel_path,
                    "type": "directory",
                    "count": len(files),
                    "files": [str(f.relative_to(project_path)) for f in files[:20]],
                })

    return jsonify({"outputs": outputs})


# ── API: Ingest ──────────────────────────────────────────────────────────────

@app.route("/api/projects/<slug>/ingest")
def api_ingest_list(slug):
    project_path = CODEYWOOD_ROOT / "projects" / slug
    files = get_ingest_summary(project_path)
    return jsonify({"files": files})


@app.route("/api/projects/<slug>/ingest/open", methods=["POST"])
def api_ingest_open(slug):
    project_path = CODEYWOOD_ROOT / "projects" / slug
    ingest_dir = project_path / "INGEST"
    ingest_dir.mkdir(exist_ok=True)
    subprocess.run(["open", str(ingest_dir)])
    return jsonify({"ok": True})


@app.route("/api/projects/<slug>/ingest/copy", methods=["POST"])
def api_ingest_copy(slug):
    project_path = CODEYWOOD_ROOT / "projects" / slug
    ingest_dir = project_path / "INGEST"
    ingest_dir.mkdir(exist_ok=True)

    data = request.json
    source = Path(data.get("path", "")).expanduser()

    if not source.exists():
        return jsonify({"error": f"Path not found: {source}"}), 404

    copied = 0
    if source.is_file():
        shutil.copy2(source, ingest_dir / source.name)
        copied = 1
    elif source.is_dir():
        for f in source.rglob("*"):
            if f.is_file() and not f.name.startswith("."):
                rel = f.relative_to(source)
                dest = ingest_dir / rel
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(f, dest)
                copied += 1

    return jsonify({"copied": copied})


# ── API: Run Claude ──────────────────────────────────────────────────────────

@app.route("/api/projects/<slug>/steps/<step_id>/run", methods=["POST"])
def api_run_step(slug, step_id):
    """Run a pipeline step via Claude Code, streaming output via SSE."""
    project_path = CODEYWOOD_ROOT / "projects" / slug
    step = get_step(step_id)
    if not step:
        return jsonify({"error": "Step not found"}), 404

    data = request.json or {}
    context = data.get("context", "")
    prompt = build_claude_prompt(step, project_path, context)

    update_step_status(project_path, step_id, "active")

    def generate():
        try:
            proc = subprocess.Popen(
                ["claude", "--print", "-p", prompt],
                cwd=str(CODEYWOOD_ROOT),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
            )

            for line in proc.stdout:
                yield f"data: {json.dumps({'type': 'output', 'text': line})}\n\n"

            proc.wait()
            exit_code = proc.returncode
            yield f"data: {json.dumps({'type': 'done', 'exit_code': exit_code})}\n\n"

        except FileNotFoundError:
            yield f"data: {json.dumps({'type': 'error', 'text': 'claude command not found. Is Claude Code installed?'})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'text': str(e)})}\n\n"

    return Response(
        stream_with_context(generate()),
        mimetype="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


# ── API: Personas ────────────────────────────────────────────────────────────

@app.route("/api/personas")
def api_personas():
    """List all available writer personas."""
    return jsonify(_list_personas())


@app.route("/api/personas/eligible")
def api_eligible_head_writers():
    """List personas eligible to be head writers."""
    return jsonify(get_eligible_head_writers())


@app.route("/api/personas/<name>")
def api_persona(name):
    """Get full persona by name."""
    try:
        persona = load_persona(name)
        return jsonify(persona)
    except FileNotFoundError:
        return jsonify({"error": f"Persona '{name}' not found"}), 404


@app.route("/api/projects/<slug>/writers-room")
def api_writers_room_config(slug):
    """Get writers room configuration for a project."""
    project_path = CODEYWOOD_ROOT / "projects" / slug
    if not project_path.exists():
        return jsonify({"error": "Project not found"}), 404
    config = get_room_config(project_path)
    # Enrich with persona details
    if config["head_writer"]:
        try:
            hw = load_persona(config["head_writer"])
            config["head_writer_detail"] = {
                "agent_name": hw.get("agent_name") or hw.get("name", config["head_writer"]),
                "room_title": hw.get("room_title", ""),
                "one_line_thesis": (hw.get("creative_philosophy") or {}).get("one_line_thesis", ""),
            }
        except FileNotFoundError:
            config["head_writer_detail"] = None
    room_details = []
    for member_name in config["room"]:
        try:
            m = load_persona(member_name)
            room_details.append({
                "name": member_name,
                "agent_name": m.get("agent_name") or m.get("name", member_name),
                "room_title": m.get("room_title", ""),
                "primary_function": m.get("primary_function", ""),
            })
        except FileNotFoundError:
            room_details.append({"name": member_name, "agent_name": member_name, "room_title": "Unknown", "primary_function": ""})
    config["room_details"] = room_details
    return jsonify(config)


@app.route("/api/projects/<slug>/writers-room", methods=["PUT"])
def api_set_writers_room(slug):
    """Set writers room configuration for a project."""
    project_path = CODEYWOOD_ROOT / "projects" / slug
    if not project_path.exists():
        return jsonify({"error": "Project not found"}), 404

    import yaml
    config_path = project_path / "PROJECT_CONFIG.yaml"
    config = {}
    if config_path.exists():
        with open(config_path) as f:
            config = yaml.safe_load(f) or {}

    data = request.json
    config["writers_room"] = {
        "head_writer": data.get("head_writer"),
        "room": data.get("room", []),
        "room_size": data.get("room_size", 5),
    }

    with open(config_path, "w") as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)

    return jsonify({"ok": True})


# ── Helpers ──────────────────────────────────────────────────────────────────

def _project_name(config: dict, fallback: str) -> str:
    """Safely extract project name from config (handles both dict and string formats)."""
    proj = config.get("project", {})
    if isinstance(proj, dict):
        return proj.get("name", fallback)
    if isinstance(proj, str):
        return proj
    return fallback


def _calc_progress(pipeline: dict) -> dict:
    total = len(PIPELINE_STEPS)
    complete = sum(1 for s in PIPELINE_STEPS if pipeline.get(s["id"]) == "complete")
    skipped = sum(1 for s in PIPELINE_STEPS if pipeline.get(s["id"]) == "skipped")
    return {
        "total": total,
        "complete": complete,
        "skipped": skipped,
        "percent": round((complete + skipped) / total * 100) if total else 0,
    }


if __name__ == "__main__":
    app.run(debug=True, port=5555)
