"""
Audit Logging System for Security Breach Simulator
Logs all player actions with timestamps for compliance and review.
"""
from __future__ import annotations

import json
import time
from pathlib import Path
from datetime import datetime
from typing import Any
from dataclasses import dataclass, asdict, field
from enum import Enum
from collections import deque


ROOT_DIR = Path(__file__).resolve().parents[1]
AUDIT_DIR = ROOT_DIR / ".audit"
AUDIT_DIR.mkdir(exist_ok=True)


class AuditLevel(Enum):
    """Audit event severity levels"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class AuditEventType(Enum):
    """Types of audit events"""
    # Scenario lifecycle
    SCENARIO_START = "SCENARIO_START"
    SCENARIO_END = "SCENARIO_END"
    SCENARIO_ABORT = "SCENARIO_ABORT"
    
    # Player actions
    ACTION_TAKEN = "ACTION_TAKEN"
    DETECTION = "DETECTION"
    RESPONSE = "RESPONSE"
    ISOLATION = "ISOLATION"
    ESCALATION = "ESCALATION"
    REMEDIATION = "REMEDIATION"
    
    # Policy events
    POLICY_CHECK = "POLICY_CHECK"
    POLICY_FOLLOWED = "POLICY_FOLLOWED"
    POLICY_IGNORED = "POLICY_IGNORED"
    
    # System events
    HINT_REQUESTED = "HINT_REQUESTED"
    TIMEOUT = "TIMEOUT"
    ERROR = "ERROR"


@dataclass
class AuditEvent:
    """Single audit event record"""
    timestamp: str
    event_type: str
    level: str
    run_id: str
    scenario_id: str | None
    stage: int | None
    
    # Event details
    message: str
    details: dict[str, Any] = field(default_factory=dict)
    
    # Context
    elapsed_seconds: float | None = None
    user_id: str | None = None
    
    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class AuditLogger:
    """Manages audit logging for scenario runs"""
    
    def __init__(self, run_id: str, scenario_id: str | None = None) -> None:
        self.run_id = run_id
        self.scenario_id = scenario_id
        self.start_time = time.time()
        self.events: list[AuditEvent] = []
        self._current_stage: int = 0
        
        # In-memory buffer for quick access
        self._buffer: deque[AuditEvent] = deque(maxlen=1000)
    
    def _now_iso(self) -> str:
        return datetime.now().isoformat()
    
    def _elapsed(self) -> float:
        return time.time() - self.start_time
    
    def set_stage(self, stage: int) -> None:
        """Update current stage"""
        self._current_stage = stage
    
    def log(
        self,
        event_type: AuditEventType,
        message: str,
        level: AuditLevel = AuditLevel.INFO,
        details: dict[str, Any] | None = None,
        stage: int | None = None
    ) -> AuditEvent:
        """Log an audit event"""
        event = AuditEvent(
            timestamp=self._now_iso(),
            event_type=event_type.value,
            level=level.value,
            run_id=self.run_id,
            scenario_id=self.scenario_id,
            stage=stage or self._current_stage,
            message=message,
            details=details or {},
            elapsed_seconds=self._elapsed()
        )
        
        self.events.append(event)
        self._buffer.append(event)
        
        return event
    
    # Convenience methods for common events
    def log_scenario_start(self, scenario_id: str, config: dict[str, Any] | None = None) -> AuditEvent:
        """Log scenario start"""
        self.scenario_id = scenario_id
        return self.log(
            AuditEventType.SCENARIO_START,
            f"Scenario '{scenario_id}' started",
            details={"config": config or {}}
        )
    
    def log_scenario_end(self, outcome: str = "completed") -> AuditEvent:
        """Log scenario end"""
        return self.log(
            AuditEventType.SCENARIO_END,
            f"Scenario ended: {outcome}",
            details={"total_events": len(self.events)}
        )
    
    def log_action(
        self,
        action_type: str,
        description: str,
        stage: int | None = None
    ) -> AuditEvent:
        """Log a player action"""
        return self.log(
            AuditEventType.ACTION_TAKEN,
            f"Action: {action_type} - {description}",
            details={"action_type": action_type},
            stage=stage
        )
    
    def log_detection(
        self,
        description: str,
        detection_method: str,
        stage: int | None = None
    ) -> AuditEvent:
        """Log a threat detection"""
        return self.log(
            AuditEventType.DETECTION,
            f"Threat detected: {description}",
            level=AuditLevel.WARNING,
            details={"method": detection_method},
            stage=stage
        )
    
    def log_policy_check(
        self,
        policy_id: str,
        followed: bool,
        reason: str | None = None
    ) -> AuditEvent:
        """Log a policy compliance check"""
        event_type = AuditEventType.POLICY_FOLLOWED if followed else AuditEventType.POLICY_IGNORED
        return self.log(
            event_type,
            f"Policy {policy_id}: {'followed' if followed else 'ignored'}",
            details={"policy_id": policy_id, "reason": reason}
        )
    
    def log_error(self, error: str, details: dict[str, Any] | None = None) -> AuditEvent:
        """Log an error"""
        return self.log(
            AuditEventType.ERROR,
            error,
            level=AuditLevel.ERROR,
            details=details
        )
    
    def save(self) -> Path:
        """Save audit log to file"""
        filepath = AUDIT_DIR / f"{self.run_id}.jsonl"
        with open(filepath, 'w') as f:
            for event in self.events:
                f.write(json.dumps(event.to_dict()) + '\n')
        return filepath
    
    def get_summary(self) -> dict[str, Any]:
        """Get audit summary"""
        events_by_type: dict[str, int] = {}
        events_by_level: dict[str, int] = {}
        
        for event in self.events:
            events_by_type[event.event_type] = events_by_type.get(event.event_type, 0) + 1
            events_by_level[event.level] = events_by_level.get(event.level, 0) + 1
        
        return {
            "run_id": self.run_id,
            "scenario_id": self.scenario_id,
            "total_events": len(self.events),
            "duration_seconds": self._elapsed(),
            "events_by_type": events_by_type,
            "events_by_level": events_by_level
        }


def load_audit_log(run_id: str) -> list[AuditEvent] | None:
    """Load audit log from file"""
    filepath = AUDIT_DIR / f"{run_id}.jsonl"
    if not filepath.exists():
        return None
    
    events = []
    with open(filepath) as f:
        for line in f:
            if line.strip():
                events.append(AuditEvent(**json.loads(line)))
    return events


def list_audit_logs(limit: int = 20) -> list[dict[str, Any]]:
    """List recent audit logs"""
    logs = []
    for f in sorted(AUDIT_DIR.glob("*.jsonl"), reverse=True)[:limit]:
        run_id = f.stem
        # Get quick stats
        try:
            with open(f) as fp:
                lines = fp.readlines()
                event_count = len(lines)
        except Exception:
            event_count = 0
        
        logs.append({
            "run_id": run_id,
            "event_count": event_count,
            "file": f.name
        })
    return logs


if __name__ == "__main__":
    # Demo audit logging
    logger = AuditLogger("demo_run_001", "ransomware_attack")
    
    logger.log_scenario_start("ransomware_attack", {"difficulty": "medium"})
    logger.log_action("detect", "Identified suspicious file encryption", stage=2)
    logger.log_detection("Ransomware detected", "file_signature", stage=2)
    logger.log_action("isolate", "Isolated affected systems", stage=3)
    logger.log_policy_check("POL-001", True, "Followed isolation protocol")
    logger.log_policy_check("POL-002", False, "Skipped notification")
    logger.log_scenario_end("completed")
    
    # Print summary
    print("Audit Log Summary:")
    print(json.dumps(logger.get_summary(), indent=2))
    
    # Save to file
    path = logger.save()
    print(f"\nSaved to: {path}")
