"""Sample breach generator for Live Security Breach Simulator."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable


def load_scenario_templates() -> dict[str, dict]:
    templates_dir = Path(__file__).resolve().parents[1] / "scenarios" / "templates"
    scenarios: dict[str, dict] = {}
    for path in sorted(templates_dir.glob("*.json")):
        content = json.loads(path.read_text())
        scenario_id = content.get("scenario_id") or path.stem
        scenarios[scenario_id] = content
    return scenarios


def load_policy_catalog() -> list[dict]:
    catalog_path = Path(__file__).resolve().parents[1] / "policies" / "catalog.json"
    return json.loads(catalog_path.read_text())


def match_policies(scenario: dict, policies: Iterable[dict]) -> list[dict]:
    scenario_tags = set(scenario.get("tags", []))
    matched = []
    for policy in policies:
        policy_tags = set(policy.get("tags", []))
        if scenario_tags & policy_tags:
            matched.append(policy)
    return matched


def compose_timeline(scenario: dict) -> list[str]:
    lines = []
    phases = scenario.get("phases", [])
    if not phases:
        return ["No phases defined."]
    for idx, phase in enumerate(phases, start=1):
        title = phase.get("name", f"phase-{idx}")
        description = phase.get("description", "No description")
        metrics = phase.get("metrics", [])
        lines.append(f"{idx}. {title}: {description}")
        if metrics:
            lines.append("   Metrics/Indicators:")
            for metric in metrics:
                lines.append(f"     – {metric}")
    return lines


def compose_policy_summary(policies: list[dict]) -> list[str]:
    if not policies:
        return ["No policies matched the scenario tags."]
    summary: list[str] = []
    for policy in policies:
        title = policy.get("title", "Unnamed Policy")
        severity = policy.get("severity", "unknown")
        intent = policy.get("intent", "No intent provided.")
        summary.append(f"• {title} (severity: {severity}) – {intent}")
    return summary


def render_report(scenario: dict, matched_policies: list[dict]) -> str:
    lines = ["Sample Breach Narrative", "========================"]
    lines.append(f"Scenario ID: {scenario.get('scenario_id')}")
    lines.append(f"Title: {scenario.get('title')}")
    lines.append("")
    description = scenario.get("description")
    if description:
        lines.append(f"Description: {description}")
    objectives = scenario.get("objectives", [])
    if objectives:
        lines.append("Objectives:")
        for objective in objectives:
            lines.append(f" – {objective}")
    assets = scenario.get("assets", [])
    if assets:
        lines.append("Assets of interest:")
        for asset in assets:
            lines.append(f" – {asset}")
    lines.append("")
    lines.append("Timeline")
    lines.extend(compose_timeline(scenario))
    lines.append("")
    detection_cues = scenario.get("detection_cues", [])
    if detection_cues:
        lines.append("Detection cues:")
        for cue in detection_cues:
            lines.append(f" – {cue}")
    lines.append("")
    lines.append("Policy guidance")
    lines.extend(compose_policy_summary(matched_policies))
    lines.append("")
    impact = scenario.get("impact", {})
    if impact:
        lines.append("Impact notes:")
        for k, v in impact.items():
            lines.append(f" – {k.capitalize()}: {v}")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a sample breach narrative.")
    parser.add_argument("--scenario", "-s", help="Scenario ID to render")
    parser.add_argument("--list", action="store_true", help="List available scenario IDs")
    args = parser.parse_args()

    scenarios = load_scenario_templates()
    if args.list:
        for scenario_id in sorted(scenarios):
            print(scenario_id)
        return

    if not scenarios:
        print("No scenario templates found.")
        return

    scenario_id = args.scenario or sorted(scenarios)[0]
    scenario = scenarios.get(scenario_id)
    if not scenario:
        print(f"Scenario '{scenario_id}' not found.")
        return

    policies = load_policy_catalog()
    matched = match_policies(scenario, policies)
    report = render_report(scenario, matched)
    print(report)


if __name__ == "__main__":
    main()
