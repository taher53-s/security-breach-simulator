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

    def __init__(self, seed: int | None = None) -> None:
        self._rng = random.Random(seed)
        self.scenarios = self._load_scenarios()
        self.policies = self._load_policies()

    def _load_scenarios(self) -> list[dict[str, Any]]:
        scenarios = []
        for file in sorted(SCENARIOS_DIR.glob("*.json")):
            data = json.loads(file.read_text(encoding="utf-8"))
            data["scenario_id"] = file.stem
            # Ensure consistent field names
            if "id" in data and "scenario_id" not in data:
                data["scenario_id"] = data["id"]
            if "title" in data and "name" not in data:
                data["name"] = data["title"]
            scenarios.append(data)
        return scenarios

    def _load_policies(self) -> dict[str, dict[str, Any]]:
        data = json.loads(POLICY_FILE.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            items = data.get("policies", [])
        elif isinstance(data, list):
            items = data
        else:
            items = []
        return {p["policy_id"]: p for p in items if isinstance(p, dict) and "policy_id" in p}

    def list_scenarios(self, severity: str | None = None, category: str | None = None) -> list[dict[str, Any]]:
        """List all available scenarios, optionally filtered by severity and/or category"""
        scenarios = [
            {
                "id": s.get("scenario_id") or s.get("id"),
                "name": s.get("name") or s.get("title"),
                "severity": s.get("severity", "medium"),
                "category": s.get("category", "unknown"),
                "difficulty": s.get("difficulty", "medium"),
            }
            for s in self.scenarios
        ]
        
        if severity:
            scenarios = [s for s in scenarios if s.get("severity", "").lower() == severity.lower()]
        if category:
            scenarios = [s for s in scenarios if s.get("category", "").lower() == category.lower()]
        
        return scenarios

    def filter_by_category(self, category: str) -> list[dict[str, Any]]:
        """Filter scenarios by category"""
        return self.list_scenarios(category=category)

    def generate_random(self, severity: str | None = None) -> dict[str, Any]:
        """Generate a random scenario, optionally filtered by severity."""
        candidates = self.scenarios
        if severity:
            candidates = [s for s in candidates if s.get("severity", "").lower() == severity.lower()]
        if not candidates:
            raise ValueError(f"No scenarios available for severity={severity!r}")
        selected = self._rng.choice(candidates)
        return self.generate(selected["scenario_id"])

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
            "total_duration_minutes": sum(stage.get("duration_minutes", 5) for stage in scenario.get("stages", [])),
            "generated_by": "BreachGenerator",
            "version": "0.3.0",
        }

    def _generate_timeline(self, scenario: dict[str, Any]) -> list[dict[str, Any]]:
        """Generate timeline events from scenario stages"""
        timeline = []
        current_time = 0

        # Handle both "stages" and "phases" field names
        stages = scenario.get("stages", scenario.get("phases", []))
        
        for i, stage in enumerate(stages):
            # Get policy details from multiple possible field names
            policy_ids = stage.get("policies", stage.get("policy_in_play", []))
            stage_policies = []
            for policy_id in policy_ids:
                if policy_id in self.policies:
                    stage_policies.append(self.policies[policy_id])

            # Handle both numeric and stage-based indexing
            stage_num = stage.get("stage", i + 1)
            
            event = {
                "stage": stage_num,
                "name": stage.get("name"),
                "description": stage.get("description"),
                "indicators": stage.get("indicators", stage.get("metrics", [])),
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

    def export_to_markdown(self, scenario_id: str) -> str:
        """Export scenario to markdown format for documentation"""
        result = self.generate(scenario_id)
        scenario = result["scenario"]
        timeline = result["timeline"]
        
        md = f"""# {scenario.get('name', 'Unknown Scenario')}

**Severity:** {scenario.get('severity', 'unknown').upper()} | **Category:** {scenario.get('category', 'unknown')} | **Difficulty:** {scenario.get('difficulty', 'unknown')}

{scenario.get('description', '')}

## Threat Overview

- **Threat Actor:** {scenario.get('threat_actor', 'Unknown')}
- **Entry Point:** {scenario.get('entry_point', 'Unknown')}
- **Est. Duration:** {result['total_duration_minutes']} minutes

## Objectives

"""
        for obj in scenario.get('objectives', []):
            md += f"- {obj}\n"
        
        md += "\n## Timeline of Events\n\n"
        
        for event in timeline:
            md += f"### Stage {event['stage']}: {event['name']}\n"
            md += f"**Time Offset:** {event['time_offset']}\n\n"
            md += f"{event.get('description', '')}\n\n"
            
            if event.get('indicators'):
                md += "**Indicators:**\n"
                for ind in event['indicators']:
                    md += f"- {ind}\n"
                md += "\n"
            
            if event.get('policies'):
                md += "**Recommended Policies:**\n"
                for pol in event['policies']:
                    md += f"- **{pol['title']}**: {pol['action']}\n"
                md += "\n"
            
            md += "---\n\n"
        
        md += f"\n*Generated by Security Breach Simulator v{result['version']}*\n"
        return md

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
    parser.add_argument("command", choices=["list", "generate", "summary", "export"])
    parser.add_argument("--scenario", help="Scenario ID")
    parser.add_argument("--severity", help="Severity filter for random generation")
    parser.add_argument("--category", help="Category filter for listing scenarios")
    parser.add_argument("--format", choices=["json", "markdown"], default="json", help="Output format for generate/export")
    parser.add_argument("--seed", type=int, help="Optional RNG seed for deterministic output")

    args = parser.parse_args()
    generator = BreachGenerator(seed=args.seed)

    if args.command == "list":
        scenarios = generator.list_scenarios(severity=args.severity, category=args.category)
        print("Available scenarios:\n")
        for s in scenarios:
            print(f"  {s['id']:40} [{s['severity']:8}] {s['name']}")

    elif args.command == "generate":
        result = generator.generate(args.scenario) if args.scenario else generator.generate_random(args.severity)
        if args.format == "markdown":
            print(generator.export_to_markdown(result["scenario"]["scenario_id"]))
        else:
            print(json.dumps(result, indent=2))

    elif args.command == "export":
        if not args.scenario:
            print("Error: --scenario required for export")
            return
        if args.format == "markdown":
            print(generator.export_to_markdown(args.scenario))
        else:
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
