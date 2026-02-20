"""
Sample breach generator - creates narrated breach timelines
"""
from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Any


ROOT_DIR = Path(__file__).resolve().parents[2]
SCENARIOS_DIR = ROOT_DIR / "src" / "scenarios" / "templates"
POLICY_FILE = ROOT_DIR / "src" / "policies" / "catalog.json"


class BreachGenerator:
    """Generates breach narratives from scenario templates"""
    
    def __init__(self) -> None:
        self.scenarios = self._load_scenarios()
        self.policies = self._load_policies()
    
    def _load_scenarios(self) -> list[dict[str, Any]]:
        scenarios = []
        for file in sorted(SCENARIOS_DIR.glob("*.json")):
            data = json.loads(file.read_text(encoding="utf-8"))
            data["scenario_id"] = file.stem
            scenarios.append(data)
        return scenarios
    
    def _load_policies(self) -> dict[str, dict[str, Any]]:
        data = json.loads(POLICY_FILE.read_text(encoding="utf-8"))
        return {p["policy_id"]: p for p in data.get("policies", [])}
    
    def list_scenarios(self) -> list[dict[str, Any]]:
        """List all available scenarios"""
        return [
            {
                "id": s["scenario_id"],
                "name": s["name"],
                "severity": s.get("severity", "medium"),
                "category": s.get("category", "unknown"),
                "difficulty": s.get("difficulty", "medium"),
            }
            for s in self.scenarios
        ]
    
    def generate(self, scenario_id: str) -> dict[str, Any]:
        """Generate a breach narrative for the given scenario"""
        scenario = None
        for s in self.scenarios:
            if s["scenario_id"] == scenario_id:
                scenario = s
                break
        
        if not scenario:
            raise ValueError(f"Unknown scenario: {scenario_id}")
        
        timeline = self._generate_timeline(scenario)
        
        return {
            "scenario": scenario,
            "timeline": timeline,
            "generated_by": "BreachGenerator",
            "version": "0.3.0",
        }
    
    def _generate_timeline(self, scenario: dict[str, Any]) -> list[dict[str, Any]]:
        """Generate timeline events from scenario stages"""
        timeline = []
        current_time = 0
        
        for stage in scenario.get("stages", []):
            # Get policy details
            stage_policies = []
            for policy_id in stage.get("policies", []):
                if policy_id in self.policies:
                    stage_policies.append(self.policies[policy_id])
            
            event = {
                "stage": stage.get("stage"),
                "name": stage.get("name"),
                "description": stage.get("description"),
                "indicators": stage.get("indicators", []),
                "time_offset": f"+{current_time}m",
                "policies": [
                    {
                        "id": p["policy_id"],
                        "title": p["title"],
                        "action": self._recommend_action(p),
                    }
                    for p in stage_policies
                ],
                "narrative": self._generate_narrative(stage),
            }
            
            timeline.append(event)
            current_time += stage.get("duration_minutes", 5)
        
        return timeline
    
    def _recommend_action(self, policy: dict[str, Any]) -> str:
        """Generate recommended action from policy"""
        severity = policy.get("severity", "medium").lower()
        
        if severity == "critical":
            return "Immediate action required - isolate affected systems"
        elif severity == "high":
            return "Priority investigation within 1 hour"
        else:
            return "Review and remediate within 24 hours"
    
    def _generate_narrative(self, stage: dict[str, Any]) -> str:
        """Generate human-readable narrative for stage"""
        name = stage.get("name", "Unknown")
        indicators = stage.get("indicators", [])
        
        narrative = f"**{name}**\n\n"
        
        if indicators:
            narrative += "Key indicators detected:\n"
            for indicator in indicators[:3]:
                narrative += f"- {indicator}\n"
        
        return narrative
    
    def get_scenario_summary(self, scenario_id: str) -> dict[str, Any]:
        """Get quick summary of scenario"""
        scenario = None
        for s in self.scenarios:
            if s["scenario_id"] == scenario_id:
                scenario = s
                break
        
        if not scenario:
            raise ValueError(f"Unknown scenario: {scenario_id}")
        
        return {
            "id": scenario["scenario_id"],
            "name": scenario["name"],
            "severity": scenario.get("severity"),
            "difficulty": scenario.get("difficulty"),
            "stages": len(scenario.get("stages", [])),
            "estimated_duration": scenario.get("estimated_duration_minutes"),
        }


def main():
    """CLI entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Security Breach Simulator")
    parser.add_argument("command", choices=["list", "generate", "summary"])
    parser.add_argument("--scenario", help="Scenario ID")
    
    args = parser.parse_args()
    generator = BreachGenerator()
    
    if args.command == "list":
        print("Available scenarios:\n")
        for s in generator.list_scenarios():
            print(f"  {s['id']:40} [{s['severity']:8}] {s['name']}")
    
    elif args.command == "generate":
        if not args.scenario:
            print("Error: --scenario required")
            return
        
        result = generator.generate(args.scenario)
        print(json.dumps(result, indent=2))
    
    elif args.command == "summary":
        if not args.scenario:
            print("Error: --scenario required")
            return
        
        summary = generator.get_scenario_summary(args.scenario)
        print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
