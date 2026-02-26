"""
Scoring 2.0 — Security Breach Simulator
8-dimension cybersecurity skills matrix backed by SQLite.
Tracks: Detection, MITRE Coverage, Containment, Policy, Evidence,
        Communication, Recovery, Efficiency
"""
from __future__ import annotations

import json
import sqlite3
import time
from datetime import datetime
from pathlib import Path
from typing import Any
from dataclasses import dataclass, asdict, field

ROOT_DIR = Path(__file__).resolve().parents[1]
DB_PATH = ROOT_DIR / ".scores" / "breach_sim.db"
DB_PATH.parent.mkdir(exist_ok=True)

ANALYST_TIERS = [
    (0,    "Tier 1 Analyst",  "🔵"),
    (200,  "Tier 2 Analyst",  "🟢"),
    (500,  "Senior Analyst",  "🟡"),
    (1000, "SOC Lead",        "🟠"),
    (2000, "CISO",            "🔴"),
]

UNICODE_BAR_CHARS = "▏▎▍▌▋▊▉█"

def _bar(value: int, max_val: int, width: int = 20) -> str:
    filled = int((value / max_val) * width) if max_val else 0
    return "█" * filled + "░" * (width - filled)

def _get_tier(total_xp: int) -> tuple[str, str]:
    tier_name, tier_icon = ANALYST_TIERS[0][1], ANALYST_TIERS[0][2]
    for threshold, name, icon in ANALYST_TIERS:
        if total_xp >= threshold:
            tier_name, tier_icon = name, icon
    return tier_name, tier_icon


@dataclass
class DimensionScore:
    name: str
    label: str
    score: int
    max_score: int
    details: str = ""

    @property
    def pct(self) -> float:
        return (self.score / self.max_score * 100) if self.max_score else 0

    @property
    def bar(self) -> str:
        return _bar(self.score, self.max_score)


@dataclass
class ScoreCard:
    run_id: str
    scenario_id: str
    difficulty: str
    timestamp: str

    # 8 Dimensions
    detection_speed:    DimensionScore = field(default_factory=lambda: DimensionScore("detection_speed", "Detection Speed", 0, 20, ""))
    mitre_coverage:     DimensionScore = field(default_factory=lambda: DimensionScore("mitre_coverage", "MITRE Coverage", 0, 15, ""))
    containment:        DimensionScore = field(default_factory=lambda: DimensionScore("containment", "Containment", 0, 15, ""))
    policy_compliance:  DimensionScore = field(default_factory=lambda: DimensionScore("policy_compliance", "Policy Compliance", 0, 15, ""))
    evidence:           DimensionScore = field(default_factory=lambda: DimensionScore("evidence", "Evidence Preservation", 0, 10, ""))
    communication:      DimensionScore = field(default_factory=lambda: DimensionScore("communication", "Communication", 0, 10, ""))
    recovery_speed:     DimensionScore = field(default_factory=lambda: DimensionScore("recovery_speed", "Recovery Speed", 0, 10, ""))
    efficiency:         DimensionScore = field(default_factory=lambda: DimensionScore("efficiency", "Efficiency", 0, 5, ""))

    @property
    def dimensions(self) -> list[DimensionScore]:
        return [
            self.detection_speed, self.mitre_coverage, self.containment,
            self.policy_compliance, self.evidence, self.communication,
            self.recovery_speed, self.efficiency,
        ]

    @property
    def total_score(self) -> int:
        return sum(d.score for d in self.dimensions)

    @property
    def max_possible(self) -> int:
        return sum(d.max_score for d in self.dimensions)

    @property
    def grade(self) -> str:
        pct = self.total_score / self.max_possible * 100 if self.max_possible else 0
        if pct >= 90: return "A+"
        if pct >= 80: return "A"
        if pct >= 70: return "B"
        if pct >= 60: return "C"
        if pct >= 50: return "D"
        return "F"

    @property
    def radar_data(self) -> dict[str, float]:
        """Normalised 0-100 values for each axis (for radar chart)."""
        return {d.label: round(d.pct, 1) for d in self.dimensions}

    @property
    def xp_earned(self) -> int:
        multipliers = {"easy": 0.5, "medium": 1.0, "hard": 1.5, "expert": 2.0}
        return int(self.total_score * multipliers.get(self.difficulty, 1.0))

    def improvement_tips(self) -> list[str]:
        tips = []
        dims = sorted(self.dimensions, key=lambda d: d.pct)
        for d in dims[:3]:
            if d.pct < 60:
                tips.append(f"Focus on {d.label} — currently {d.pct:.0f}%. {d.details}")
        return tips or ["Great performance across all dimensions!"]

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "scenario_id": self.scenario_id,
            "difficulty": self.difficulty,
            "timestamp": self.timestamp,
            "total_score": self.total_score,
            "max_possible": self.max_possible,
            "grade": self.grade,
            "xp_earned": self.xp_earned,
            "radar_data": self.radar_data,
            "dimensions": {d.name: {"score": d.score, "max": d.max_score, "pct": round(d.pct, 1)} for d in self.dimensions},
            "tips": self.improvement_tips(),
        }

    def print_card(self) -> None:
        R="\033[91m"; Y="\033[93m"; G="\033[92m"; C="\033[96m"
        BOLD="\033[1m"; DIM="\033[2m"; RST="\033[0m"
        pct = self.total_score / self.max_possible * 100 if self.max_possible else 0
        grade_color = G if pct >= 70 else (Y if pct >= 50 else R)
        tier_name, tier_icon = _get_tier(self.xp_earned)

        print(f"\n  {BOLD}{'═'*55}{RST}")
        print(f"  {BOLD}  INCIDENT RESPONSE SCORECARD{RST}")
        print(f"  {BOLD}{'═'*55}{RST}")
        print(f"  Scenario : {self.scenario_id}")
        print(f"  Difficulty: {self.difficulty.upper()}")
        print(f"  Grade    : {grade_color}{BOLD}{self.grade}{RST}   "
              f"Score: {grade_color}{BOLD}{self.total_score}/{self.max_possible}{RST}")
        print(f"  Tier     : {tier_icon} {BOLD}{tier_name}{RST}   XP Earned: +{self.xp_earned}")
        print(f"\n  {'─'*55}")
        print(f"  {'DIMENSION':<25} {'SCORE':>7}  {'BAR':<22} {'%':>5}")
        print(f"  {'─'*55}")

        for d in self.dimensions:
            color = G if d.pct >= 70 else (Y if d.pct >= 50 else R)
            print(f"  {d.label:<25} {color}{d.score:>3}/{d.max_score:<3}{RST}  "
                  f"{color}{d.bar}{RST}  {d.pct:>4.0f}%")

        print(f"  {'─'*55}")
        print(f"\n  {BOLD}Improvement Tips:{RST}")
        for tip in self.improvement_tips():
            print(f"  {DIM}• {tip}{RST}")
        print(f"\n  {'═'*55}\n")


class ScoringEngine2:
    """
    8-dimension scoring engine backed by SQLite.
    Tracks all runs, leaderboards, personal improvement over time.
    """

    def __init__(self, scenario_id: str, difficulty: str = "medium") -> None:
        self.scenario_id = scenario_id
        self.difficulty = difficulty
        self.run_id = f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self._start_time = time.time()
        self._detection_time: float | None = None
        self._containment_before_lateral = False
        self._actions: list[dict[str, Any]] = []
        self._policies_followed = 0
        self._policies_total = 0
        self._mitre_identified: set[str] = set()
        self._mitre_total: set[str] = set()
        self._evidence_logged = 0
        self._escalated = False
        self._recovery_time: float | None = None
        self._db = self._init_db()

    def _init_db(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(DB_PATH))
        conn.execute("""
            CREATE TABLE IF NOT EXISTS runs (
                run_id TEXT PRIMARY KEY,
                scenario_id TEXT,
                difficulty TEXT,
                total_score INTEGER,
                grade TEXT,
                xp_earned INTEGER,
                scores_json TEXT,
                timestamp TEXT
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_scenario ON runs(scenario_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_score ON runs(total_score DESC)")
        conn.commit()
        return conn

    # ── Action Recording API ────────────────────────────────────────────────

    def detect_threat(self) -> None:
        if self._detection_time is None:
            self._detection_time = time.time() - self._start_time

    def contain_before_lateral(self) -> None:
        self._containment_before_lateral = True

    def log_action(self, action_type: str, description: str, stage: int = 0) -> None:
        self._actions.append({
            "type": action_type, "description": description,
            "stage": stage, "elapsed": time.time() - self._start_time,
        })

    def follow_policy(self, policy_id: str, followed: bool = True) -> None:
        self._policies_total += 1
        if followed:
            self._policies_followed += 1

    def identify_mitre(self, technique_id: str) -> None:
        self._mitre_identified.add(technique_id)

    def set_mitre_total(self, techniques: list[str]) -> None:
        self._mitre_total = set(techniques)

    def preserve_evidence(self) -> None:
        self._evidence_logged += 1

    def escalate(self) -> None:
        self._escalated = True

    def mark_recovered(self) -> None:
        if self._recovery_time is None:
            self._recovery_time = time.time() - self._start_time

    # ── Score Calculation ───────────────────────────────────────────────────

    def calculate(self) -> ScoreCard:
        card = ScoreCard(
            run_id=self.run_id,
            scenario_id=self.scenario_id,
            difficulty=self.difficulty,
            timestamp=datetime.now().isoformat(),
        )

        # 1. Detection Speed (0-20)
        dt = self._detection_time
        if dt is not None:
            if dt < 60:   pts = 20
            elif dt < 180: pts = 16
            elif dt < 300: pts = 12
            elif dt < 600: pts = 7
            else:          pts = 3
        else:
            pts = 0
        card.detection_speed = DimensionScore("detection_speed", "Detection Speed", pts, 20,
            f"Detection in {dt:.0f}s" if dt else "Threat not detected")

        # 2. MITRE Coverage (0-15)
        if self._mitre_total:
            ratio = len(self._mitre_identified) / len(self._mitre_total)
            pts = int(ratio * 15)
        else:
            pts = 8
        card.mitre_coverage = DimensionScore("mitre_coverage", "MITRE Coverage", pts, 15,
            f"{len(self._mitre_identified)}/{len(self._mitre_total)} techniques identified")

        # 3. Containment (0-15)
        pts = 15 if self._containment_before_lateral else (7 if self._detection_time else 0)
        card.containment = DimensionScore("containment", "Containment", pts, 15,
            "Isolated before lateral movement" if self._containment_before_lateral else "Late containment")

        # 4. Policy Compliance (0-15)
        if self._policies_total:
            pts = int((self._policies_followed / self._policies_total) * 15)
        else:
            pts = 0
        card.policy_compliance = DimensionScore("policy_compliance", "Policy Compliance", pts, 15,
            f"{self._policies_followed}/{self._policies_total} policies followed")

        # 5. Evidence (0-10)
        pts = min(10, self._evidence_logged * 2)
        card.evidence = DimensionScore("evidence", "Evidence Preservation", pts, 10,
            f"{self._evidence_logged} forensic actions logged")

        # 6. Communication (0-10)
        pts = 10 if self._escalated else 3
        card.communication = DimensionScore("communication", "Communication", pts, 10,
            "Escalated to management" if self._escalated else "Did not escalate")

        # 7. Recovery Speed (0-10)
        rt = self._recovery_time
        if rt:
            if rt < 300:   pts = 10
            elif rt < 600: pts = 7
            elif rt < 900: pts = 4
            else:          pts = 2
        else:
            pts = 0
        card.recovery_speed = DimensionScore("recovery_speed", "Recovery Speed", pts, 10,
            f"Recovery in {rt:.0f}s" if rt else "No recovery marked")

        # 8. Efficiency (0-5) — fewer actions = better
        n = len(self._actions)
        pts = 5 if n <= 5 else (4 if n <= 8 else (3 if n <= 12 else (1 if n <= 20 else 0)))
        card.efficiency = DimensionScore("efficiency", "Efficiency", pts, 5,
            f"{n} total actions taken")

        return card

    def save(self) -> ScoreCard:
        card = self.calculate()
        self._db.execute("""
            INSERT OR REPLACE INTO runs
            (run_id, scenario_id, difficulty, total_score, grade, xp_earned, scores_json, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            card.run_id, card.scenario_id, card.difficulty,
            card.total_score, card.grade, card.xp_earned,
            json.dumps(card.to_dict()), card.timestamp,
        ))
        self._db.commit()
        return card

    @staticmethod
    def get_leaderboard(scenario_id: str | None = None, limit: int = 10) -> list[dict[str, Any]]:
        conn = sqlite3.connect(str(DB_PATH))
        if scenario_id:
            rows = conn.execute(
                "SELECT run_id, scenario_id, difficulty, total_score, grade, xp_earned, timestamp "
                "FROM runs WHERE scenario_id=? ORDER BY total_score DESC LIMIT ?",
                (scenario_id, limit)
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT run_id, scenario_id, difficulty, total_score, grade, xp_earned, timestamp "
                "FROM runs ORDER BY total_score DESC LIMIT ?", (limit,)
            ).fetchall()
        conn.close()
        return [
            {"rank": i+1, "run_id": r[0], "scenario_id": r[1], "difficulty": r[2],
             "total_score": r[3], "grade": r[4], "xp_earned": r[5], "timestamp": r[6]}
            for i, r in enumerate(rows)
        ]

    @staticmethod
    def get_total_xp() -> int:
        try:
            conn = sqlite3.connect(str(DB_PATH))
            row = conn.execute("SELECT COALESCE(SUM(xp_earned),0) FROM runs").fetchone()
            conn.close()
            return row[0]
        except Exception:
            return 0

    @staticmethod
    def get_personal_best(scenario_id: str) -> dict[str, Any] | None:
        conn = sqlite3.connect(str(DB_PATH))
        row = conn.execute(
            "SELECT total_score, grade, timestamp FROM runs WHERE scenario_id=? ORDER BY total_score DESC LIMIT 1",
            (scenario_id,)
        ).fetchone()
        conn.close()
        return {"score": row[0], "grade": row[1], "timestamp": row[2]} if row else None


if __name__ == "__main__":
    eng = ScoringEngine2("ransomware_attack", "hard")
    eng.detect_threat()
    eng.contain_before_lateral()
    eng.log_action("isolate", "Isolated host CORP-WS-001", 2)
    eng.follow_policy("policy-identity-mfa", True)
    eng.follow_policy("policy-network-segmentation", True)
    eng.follow_policy("policy-data-loss-prevention", False)
    eng.set_mitre_total(["T1566", "T1486", "T1021"])
    eng.identify_mitre("T1566")
    eng.identify_mitre("T1486")
    eng.preserve_evidence()
    eng.preserve_evidence()
    eng.escalate()
    eng.mark_recovered()
    card = eng.save()
    card.print_card()
