"""
Scoring System for Security Breach Simulator
Tracks player performance including detection time, steps taken, and policy compliance.
"""
from __future__ import annotations

import json
import time
from pathlib import Path
from datetime import datetime
from typing import Any
from dataclasses import dataclass, asdict, field


ROOT_DIR = Path(__file__).resolve().parents[1]
SCORES_DIR = ROOT_DIR / ".scores"
SCORES_DIR.mkdir(exist_ok=True)


@dataclass
class BreachAction:
    """Record of a single action taken during a scenario"""
    timestamp: float
    action_type: str  # "detect", "respond", "isolate", "escalate", "remediate"
    description: str
    stage: int
    elapsed_seconds: float


@dataclass
class ScenarioScore:
    """Score record for a completed scenario run"""
    run_id: str
    scenario_id: str
    seed: int | None
    started_at: str
    completed_at: str
    duration_seconds: float
    
    # Detection metrics
    detection_time_seconds: float | None = None
    detection_stage: int | None = None
    detection_score: int = 0
    
    # Response metrics
    total_actions: int = 0
    actions: list[dict] = field(default_factory=list)
    
    # Policy compliance
    policies_followed: int = 0
    policies_ignored: int = 0
    compliance_score: int = 0
    
    # Overall score
    total_score: int = 0
    grade: str = "F"
    
    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class ScoringEngine:
    """Tracks and calculates scores for scenario runs"""
    
    def __init__(self, run_id: str | None = None, seed: int | None = None) -> None:
        self.run_id = run_id or self._generate_run_id()
        self.seed = seed
        self.scenario_id: str | None = None
        self.started_at = time.time()
        self.completed_at: float | None = None
        self.actions: list[BreachAction] = []
        
        # Detection tracking
        self.detection_time: float | None = None
        self.detection_stage: int | None = None
        
        # Policy tracking
        self.policies_followed: int = 0
        self.policies_ignored: int = 0
        
        # Expected policies from scenario
        self.expected_policies: set[str] = set()
    
    def _generate_run_id(self) -> str:
        return f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    def start_scenario(self, scenario_id: str, expected_policies: list[str] | None = None) -> None:
        """Initialize scoring for a new scenario"""
        self.scenario_id = scenario_id
        self.started_at = time.time()
        if expected_policies:
            self.expected_policies = set(expected_policies)
    
    def record_action(self, action_type: str, description: str, stage: int) -> None:
        """Record an action taken by the player"""
        elapsed = time.time() - self.started_at
        action = BreachAction(
            timestamp=time.time(),
            action_type=action_type,
            description=description,
            stage=stage,
            elapsed_seconds=elapsed
        )
        self.actions.append(action)
        
        # Check if this is a detection
        if action_type == "detect" and self.detection_time is None:
            self.detection_time = elapsed
            self.detection_stage = stage
    
    def record_policy_compliance(self, followed: bool) -> None:
        """Record policy compliance"""
        if followed:
            self.policies_followed += 1
        else:
            self.policies_ignored += 1
    
    def calculate_score(self) -> ScenarioScore:
        """Calculate final score for the run"""
        if self.completed_at is None:
            self.completed_at = time.time()
        
        duration = self.completed_at - self.started_at
        
        # Detection score (0-40 points)
        detection_score = 0
        if self.detection_time is not None:
            if self.detection_time < 60:  # Under 1 minute
                detection_score = 40
            elif self.detection_time < 300:  # Under 5 minutes
                detection_score = 30
            elif self.detection_time < 600:  # Under 10 minutes
                detection_score = 20
            elif self.detection_time < 900:  # Under 15 minutes
                detection_score = 10
        
        # Compliance score (0-40 points)
        total_policies = self.policies_followed + self.policies_ignored
        compliance_score = 0
        if total_policies > 0:
            compliance_ratio = self.policies_followed / total_policies
            compliance_score = int(compliance_ratio * 40)
        
        # Response efficiency score (0-20 points)
        # Fewer actions = higher score (efficiency)
        efficiency_score = 20
        if len(self.actions) > 10:
            efficiency_score = max(0, 20 - (len(self.actions) - 10))
        
        total_score = detection_score + compliance_score + efficiency_score
        
        # Calculate grade
        if total_score >= 90:
            grade = "A"
        elif total_score >= 80:
            grade = "B"
        elif total_score >= 70:
            grade = "C"
        elif total_score >= 60:
            grade = "D"
        else:
            grade = "F"
        
        return ScenarioScore(
            run_id=self.run_id,
            scenario_id=self.scenario_id or "unknown",
            seed=self.seed,
            started_at=datetime.fromtimestamp(self.started_at).isoformat(),
            completed_at=datetime.fromtimestamp(self.completed_at).isoformat(),
            duration_seconds=duration,
            detection_time_seconds=self.detection_time,
            detection_stage=self.detection_stage,
            detection_score=detection_score,
            total_actions=len(self.actions),
            actions=[{
                "type": a.action_type,
                "description": a.description,
                "stage": a.stage,
                "elapsed_seconds": a.elapsed_seconds
            } for a in self.actions],
            policies_followed=self.policies_followed,
            policies_ignored=self.policies_ignored,
            compliance_score=compliance_score,
            total_score=total_score,
            grade=grade
        )
    
    def save_score(self) -> Path:
        """Save score to file"""
        score = self.calculate_score()
        filepath = SCORES_DIR / f"{self.run_id}.json"
        filepath.write_text(json.dumps(score.to_dict(), indent=2))
        return filepath
    
    def get_score_summary(self) -> dict[str, Any]:
        """Get quick summary without saving"""
        score = self.calculate_score()
        return {
            "run_id": self.run_id,
            "scenario_id": self.scenario_id,
            "total_score": score.total_score,
            "grade": score.grade,
            "detection_time": score.detection_time_seconds,
            "total_actions": score.total_actions,
            "policies_followed": score.policies_followed
        }


def load_score(run_id: str) -> ScenarioScore | None:
    """Load a saved score by run_id"""
    filepath = SCORES_DIR / f"{run_id}.json"
    if not filepath.exists():
        return None
    data = json.loads(filepath.read_text())
    return ScenarioScore(**data)


def list_scores(limit: int = 10) -> list[dict[str, Any]]:
    """List recent scores"""
    scores = []
    for f in sorted(SCORES_DIR.glob("*.json"), reverse=True)[:limit]:
        data = json.loads(f.read_text())
        scores.append({
            "run_id": data["run_id"],
            "scenario_id": data["scenario_id"],
            "total_score": data["total_score"],
            "grade": data["grade"],
            "completed_at": data["completed_at"]
        })
    return scores


if __name__ == "__main__":
    # Demo scoring
    engine = ScoringEngine(seed=42)
    engine.start_scenario("ransomware_attack", ["POL-001", "POL-002"])
    
    engine.record_action("detect", "Identified suspicious process", 2)
    engine.record_action("respond", "Initiated incident response", 2)
    engine.record_action("isolate", "Isolated affected systems", 3)
    engine.record_policy_compliance(True)
    engine.record_policy_compliance(True)
    engine.record_policy_compliance(False)
    
    summary = engine.get_score_summary()
    print(json.dumps(summary, indent=2))
    
    # Save and reload
    path = engine.save_score()
    print(f"\nSaved to: {path}")
