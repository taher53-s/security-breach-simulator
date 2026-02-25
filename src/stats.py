"""
Stats Dashboard for Security Breach Simulator
Provides player statistics and performance history.
"""
from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Any
from collections import defaultdict


ROOT_DIR = Path(__file__).resolve().parents[1]
SCORES_DIR = ROOT_DIR / ".scores"
RUNS_DIR = ROOT_DIR / ".runs"
AUDIT_DIR = ROOT_DIR / ".audit"


class StatsDashboard:
    """Generate player statistics and performance insights"""
    
    def __init__(self) -> None:
        self.scores = self._load_scores()
        self.runs = self._load_runs()
    
    def _load_scores(self) -> list[dict]:
        scores = []
        if SCORES_DIR.exists():
            for f in SCORES_DIR.glob("*.json"):
                try:
                    scores.append(json.loads(f.read_text()))
                except Exception:
                    pass
        return scores
    
    def _load_runs(self) -> list[dict]:
        runs = []
        if RUNS_DIR.exists():
            for f in RUNS_DIR.glob("*.json"):
                try:
                    runs.append(json.loads(f.read_text()))
                except Exception:
                    pass
        return runs
    
    def get_total_stats(self) -> dict[str, Any]:
        """Get overall statistics"""
        if not self.scores:
            return {
                "total_runs": 0,
                "total_scenarios": 0,
                "average_score": 0,
                "average_grade": "N/A"
            }
        
        total_score = sum(s.get("total_score", 0) for s in self.scores)
        grades = [s.get("grade", "F") for s in self.scores]
        
        # Calculate grade distribution
        grade_counts = defaultdict(int)
        for g in grades:
            grade_counts[g] += 1
        
        return {
            "total_runs": len(self.scores),
            "total_scenarios": len(set(s.get("scenario_id") for s in self.scores)),
            "average_score": round(total_score / len(self.scores), 1),
            "best_score": max(s.get("total_score", 0) for s in self.scores),
            "worst_score": min(s.get("total_score", 0) for s in self.scores),
            "grade_distribution": dict(grade_counts),
            "completion_rate": round(len(self.scores) / max(len(self.scores) + len(self.runs), 1) * 100, 1)
        }
    
    def get_scenario_stats(self, scenario_id: str) -> dict[str, Any]:
        """Get statistics for a specific scenario"""
        scenario_scores = [s for s in self.scores if s.get("scenario_id") == scenario_id]
        
        if not scenario_scores:
            return {"error": f"No runs for scenario: {scenario_id}"}
        
        total_score = sum(s.get("total_score", 0) for s in scenario_scores)
        avg_detection = sum(
            s.get("detection_time_seconds", 0) or 0 
            for s in scenario_scores
        ) / len(scenario_scores)
        
        return {
            "scenario_id": scenario_id,
            "total_runs": len(scenario_scores),
            "average_score": round(total_score / len(scenario_scores), 1),
            "best_score": max(s.get("total_score", 0) for s in scenario_scores),
            "average_detection_time": round(avg_detection, 1),
            "average_actions": sum(s.get("total_actions", 0) for s in scenario_scores) / len(scenario_scores)
        }
    
    def get_trends(self, days: int = 7) -> dict[str, Any]:
        """Get performance trends over time"""
        cutoff = datetime.now() - timedelta(days=days)
        
        recent_scores = []
        for s in self.scores:
            try:
                completed = datetime.fromisoformat(s.get("completed_at", ""))
                if completed >= cutoff:
                    recent_scores.append(s)
            except Exception:
                pass
        
        if not recent_scores:
            return {"message": f"No data in last {days} days"}
        
        # Group by date
        by_date = defaultdict(list)
        for s in recent_scores:
            try:
                date = datetime.fromisoformat(s.get("completed_at", "")).date()
                by_date[date].append(s.get("total_score", 0))
            except Exception:
                pass
        
        trend_data = []
        for date in sorted(by_date.keys()):
            scores = by_date[date]
            trend_data.append({
                "date": str(date),
                "runs": len(scores),
                "avg_score": round(sum(scores) / len(scores), 1)
            })
        
        return {
            "period_days": days,
            "total_runs": len(recent_scores),
            "daily_data": trend_data
        }
    
    def get_leaderboard(self, limit: int = 10) -> list[dict[str, Any]]:
        """Get top performing runs"""
        sorted_scores = sorted(
            self.scores, 
            key=lambda s: s.get("total_score", 0), 
            reverse=True
        )[:limit]
        
        return [
            {
                "rank": i + 1,
                "run_id": s.get("run_id"),
                "scenario_id": s.get("scenario_id"),
                "score": s.get("total_score"),
                "grade": s.get("grade"),
                "completed_at": s.get("completed_at")
            }
            for i, s in enumerate(sorted_scores)
        ]
    
    def get_policy_compliance_stats(self) -> dict[str, Any]:
        """Get policy compliance statistics"""
        total_followed = sum(s.get("policies_followed", 0) for s in self.scores)
        total_ignored = sum(s.get("policies_ignored", 0) for s in self.scores)
        total = total_followed + total_ignored
        
        if total == 0:
            return {"compliance_rate": 0, "total_checks": 0}
        
        return {
            "compliance_rate": round(total_followed / total * 100, 1),
            "total_checks": total,
            "policies_followed": total_followed,
            "policies_ignored": total_ignored
        }


def print_dashboard():
    """Print formatted dashboard to console"""
    dashboard = StatsDashboard()
    
    print("=" * 60)
    print("  SECURITY BREACH SIMULATOR - STATS DASHBOARD")
    print("=" * 60)
    
    # Overall stats
    stats = dashboard.get_total_stats()
    print("\n📊 OVERALL STATISTICS")
    print("-" * 40)
    print(f"  Total Runs:       {stats['total_runs']}")
    print(f"  Unique Scenarios: {stats['total_scenarios']}")
    print(f"  Average Score:    {stats['average_score']}")
    print(f"  Best Score:       {stats.get('best_score', 'N/A')}")
    print(f"  Completion Rate:  {stats.get('completion_rate', 0)}%")
    
    # Grade distribution
    if stats.get('grade_distribution'):
        print("\n📈 GRADE DISTRIBUTION")
        print("-" * 40)
        for grade in ['A', 'B', 'C', 'D', 'F']:
            count = stats['grade_distribution'].get(grade, 0)
            bar = "█" * count
            print(f"  {grade}: {bar} ({count})")
    
    # Policy compliance
    compliance = dashboard.get_policy_compliance_stats()
    print("\n✅ POLICY COMPLIANCE")
    print("-" * 40)
    print(f"  Compliance Rate: {compliance.get('compliance_rate', 0)}%")
    print(f"  Total Checks:   {compliance.get('total_checks', 0)}")
    
    # Leaderboard
    leaderboard = dashboard.get_leaderboard(5)
    if leaderboard:
        print("\n🏆 TOP PERFORMERS")
        print("-" * 40)
        for entry in leaderboard:
            print(f"  #{entry['rank']} {entry['scenario_id']}: {entry['score']} pts ({entry['grade']})")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    print_dashboard()
