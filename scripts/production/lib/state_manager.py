"""
State Manager for execution tracking.

Records script executions, generation results, and gate status to .state.json.
Enables Claude to understand execution history and make informed decisions.

Usage:
    from lib.state_manager import StateManager

    state = StateManager(project_root)
    state.record_execution(
        command="fal_generate.py --hero mars",
        output_paths=["EXPORTS/hero_shots/mars/mars_entrance.png"],
        metadata={"model": "nano_banana", "seed": 12345}
    )
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
import uuid


class StateManager:
    """Manages project state and execution tracking."""

    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)
        self.state_path = self.project_root / ".state.json"
        self._state = self._load_state()

    def _load_state(self) -> Dict[str, Any]:
        """Load existing state or create empty state."""
        if self.state_path.exists():
            with open(self.state_path) as f:
                return json.load(f)
        else:
            return self._create_empty_state()

    def _create_empty_state(self) -> Dict[str, Any]:
        """Create an empty state structure."""
        return {
            "version": "0.5",
            "project_slug": self.project_root.name,
            "current_phase": "INITIALIZED",
            "current_state": "PENDING",
            "last_updated": None,
            "gates": {
                "gate_0_intake": {"status": "pending", "passed_at": None},
                "gate_1_logline": {"status": "pending", "passed_at": None},
                "gate_2_characters": {"status": "pending", "passed_at": None},
                "gate_3_story": {"status": "pending", "passed_at": None},
                "gate_4_script": {"status": "pending", "passed_at": None},
                "gate_5_approved": {"status": "pending", "passed_at": None},
                "gate_6_references": {"status": "pending", "passed_at": None},
                "gate_7_shots": {"status": "pending", "passed_at": None},
            },
            "skills_completed": [],
            "generations": {
                "hero_shots": {},
                "identity_sheets": {},
                "location_refs": {},
                "storyboards": {},
                "frames": {},
                "clips": {},
            },
            "executions": [],
            "errors": [],
        }

    def _save_state(self):
        """Save state to disk."""
        self._state["last_updated"] = datetime.now().isoformat()
        with open(self.state_path, "w") as f:
            json.dump(self._state, f, indent=2)

    def record_execution(
        self,
        command: str,
        output_paths: Optional[List[str]] = None,
        status: str = "success",
        metadata: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None,
    ) -> str:
        """
        Record a script execution.

        Args:
            command: The command that was executed
            output_paths: List of paths to generated files
            status: "success", "error", or "skipped"
            metadata: Additional metadata (model, seed, etc.)
            error_message: Error message if status is "error"

        Returns:
            Execution ID
        """
        execution_id = str(uuid.uuid4())[:8]
        timestamp = datetime.now().isoformat()

        execution_record = {
            "execution_id": execution_id,
            "command": command,
            "started_at": timestamp,
            "completed_at": timestamp,
            "status": status,
            "output_paths": output_paths or [],
            "metadata": metadata or {},
        }

        if error_message:
            execution_record["error"] = error_message

        self._state["executions"].append(execution_record)

        # Keep only last 100 executions
        if len(self._state["executions"]) > 100:
            self._state["executions"] = self._state["executions"][-100:]

        self._save_state()
        return execution_id

    def record_generation(
        self,
        asset_type: str,
        asset_key: str,
        path: str,
        model: str,
        seed: Optional[int] = None,
        locked: bool = False,
    ):
        """
        Record a generated asset.

        Args:
            asset_type: Type of asset (hero_shots, identity_sheets, etc.)
            asset_key: Key for the asset (character slug, location slug, etc.)
            path: Path to the generated file
            model: Model used for generation
            seed: Random seed if used
            locked: Whether this is the locked/approved version
        """
        timestamp = datetime.now().isoformat()

        record = {
            "path": str(path),
            "model": model,
            "generated_at": timestamp,
            "locked": locked,
        }
        if seed is not None:
            record["seed"] = seed

        # Ensure the asset type exists
        if asset_type not in self._state["generations"]:
            self._state["generations"][asset_type] = {}

        # For types that can have multiple assets (hero_shots), use lists
        if asset_type in ["hero_shots", "location_refs"]:
            if asset_key not in self._state["generations"][asset_type]:
                self._state["generations"][asset_type][asset_key] = []
            self._state["generations"][asset_type][asset_key].append(record)
        else:
            # For single assets (identity_sheets), just store the record
            self._state["generations"][asset_type][asset_key] = record

        self._save_state()

    def record_error(
        self,
        message: str,
        phase: Optional[str] = None,
        skill: Optional[str] = None,
    ):
        """Record an error."""
        error_record = {
            "timestamp": datetime.now().isoformat(),
            "phase": phase or self._state.get("current_phase", "UNKNOWN"),
            "skill": skill,
            "message": message,
            "resolved": False,
        }
        self._state["errors"].append(error_record)
        self._save_state()

    def update_gate(self, gate_number: int, passed: bool, details: Optional[str] = None):
        """Update gate status."""
        gate_key = f"gate_{gate_number}_{'intake' if gate_number == 0 else ['logline', 'characters', 'story', 'script', 'approved', 'references', 'shots'][gate_number - 1]}"

        if gate_key in self._state["gates"]:
            self._state["gates"][gate_key]["status"] = "passed" if passed else "failed"
            if passed:
                self._state["gates"][gate_key]["passed_at"] = datetime.now().isoformat()
            if details:
                self._state["gates"][gate_key]["details"] = details
            self._save_state()

    def update_phase(self, phase: str, state: str = "IN_PROGRESS"):
        """Update current phase and state."""
        self._state["current_phase"] = phase
        self._state["current_state"] = state
        self._save_state()

    def get_execution_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent execution history."""
        return self._state["executions"][-limit:]

    def get_generations(self, asset_type: str) -> Dict[str, Any]:
        """Get all generations of a specific type."""
        return self._state["generations"].get(asset_type, {})

    def get_gate_status(self, gate_number: int) -> Dict[str, Any]:
        """Get status of a specific gate."""
        gate_names = ["intake", "logline", "characters", "story", "script", "approved", "references", "shots"]
        gate_key = f"gate_{gate_number}_{gate_names[gate_number]}"
        return self._state["gates"].get(gate_key, {"status": "unknown"})

    @property
    def current_phase(self) -> str:
        """Get current phase."""
        return self._state.get("current_phase", "UNKNOWN")

    @property
    def current_state(self) -> str:
        """Get current state."""
        return self._state.get("current_state", "UNKNOWN")


# Convenience function for scripts
def get_state_manager(project_root: Optional[Path] = None) -> StateManager:
    """Get a StateManager instance, auto-detecting project root if not provided."""
    if project_root is None:
        # Try to find project root
        from lib.config import find_project_root
        project_root = find_project_root()

    return StateManager(project_root)
