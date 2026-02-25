"""
Replay System for Security Breach Simulator
Allows re-running scenarios with the same parameters for comparison.
"""
from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime
from typing import Any
from dataclasses import dataclass, asdict

try:
    from .scoring import load_score, ScenarioScore
except ImportError:
    from scoring import load_score, ScenarioScore


ROOT_DIR = Path(__file__).resolve().parents[1]
RUNS_DIR = ROOT_DIR / ".runs"
RUNS_DIR.mkdir(exist_ok=True)


@dataclass
class ReplayRun:
    """Record of a scenario run that can be replayed"""
    run_id: str
    original_run_id: str | None
    scenario_id: str
    seed: int | None
    created_at: str
    config: dict[str, Any]
    results: dict[str, Any] | None = None
    
    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class ReplayEngine:
    """Manages scenario replay functionality"""
    
    def __init__(self) -> None:
        self.runs: dict[str, ReplayRun] = {}
        self._load_existing_runs()
    
    def _load_existing_runs(self) -> None:
        """Load existing replay runs from disk"""
        for f in RUNS_DIR.glob("*.json"):
            try:
                data = json.loads(f.read_text())
                run = ReplayRun(**data)
                self.runs[run.run_id] = run
            except Exception:
                pass
    
    def create_replay(
        self,
        scenario_id: str,
        seed: int | None = None,
        original_run_id: str | None = None,
        config: dict[str, Any] | None = None
    ) -> ReplayRun:
        """Create a new replay run"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        run_id = f"replay_{timestamp}"
        
        run = ReplayRun(
            run_id=run_id,
            original_run_id=original_run_id,
            scenario_id=scenario_id,
            seed=seed,
            created_at=datetime.now().isoformat(),
            config=config or {}
        )
        
        self.runs[run_id] = run
        self._save_run(run)
        
        return run
    
    def _save_run(self, run: ReplayRun) -> None:
        """Save run to disk"""
        filepath = RUNS_DIR / f"{run.run_id}.json"
        filepath.write_text(json.dumps(run.to_dict(), indent=2))
    
    def get_run(self, run_id: str) -> ReplayRun | None:
        """Get a replay run by ID"""
        return self.runs.get(run_id)
    
    def list_runs(self, limit: int = 20) -> list[dict[str, Any]]:
        """List recent replay runs"""
        runs = sorted(self.runs.values(), key=lambda r: r.created_at, reverse=True)[:limit]
        return [
            {
                "run_id": r.run_id,
                "scenario_id": r.scenario_id,
                "seed": r.seed,
                "original_run_id": r.original_run_id,
                "created_at": r.created_at,
                "has_results": r.results is not None
            }
            for r in runs
        ]
    
    def save_results(self, run_id: str, results: dict[str, Any]) -> None:
        """Save results for a replay run"""
        if run_id in self.runs:
            self.runs[run_id].results = results
            self._save_run(self.runs[run_id])
    
    def compare_runs(self, run_id1: str, run_id2: str) -> dict[str, Any] | None:
        """Compare two runs for performance analysis"""
        # Try loading from scoring system first
        score1 = load_score(run_id1)
        score2 = load_score(run_id2)
        
        if score1 and score2:
            return {
                "run1": {
                    "run_id": score1.run_id,
                    "scenario_id": score1.scenario_id,
                    "total_score": score1.total_score,
                    "grade": score1.grade,
                    "detection_time": score1.detection_time_seconds,
                    "total_actions": score1.total_actions
                },
                "run2": {
                    "run_id": score2.run_id,
                    "scenario_id": score2.scenario_id,
                    "total_score": score2.total_score,
                    "grade": score2.grade,
                    "detection_time": score2.detection_time_seconds,
                    "total_actions": score2.total_actions
                },
                "comparison": {
                    "score_diff": score1.total_score - score2.total_score,
                    "detection_diff": (
                        (score2.detection_time_seconds or 0) - 
                        (score1.detection_time_seconds or 0)
                    ),
                    "actions_diff": score1.total_actions - score2.total_actions
                }
            }
        
        return None


def create_replay_from_score(score: ScenarioScore, config: dict[str, Any] | None = None) -> ReplayRun:
    """Create a replay run from an existing score"""
    engine = ReplayEngine()
    return engine.create_replay(
        scenario_id=score.scenario_id,
        seed=score.seed,
        original_run_id=score.run_id,
        config=config
    )


if __name__ == "__main__":
    # Demo replay
    engine = ReplayEngine()
    
    # Create a replay
    replay = engine.create_replay("ransomware_attack", seed=42)
    print(f"Created replay: {replay.run_id}")
    
    # List runs
    print("\nRecent replays:")
    for run in engine.list_runs(5):
        print(f"  {run}")
