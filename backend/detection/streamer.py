"""Simple detection event streamer for breach scenarios."""
from __future__ import annotations

import argparse
import json
import random
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
SCENARIO_DIR = ROOT / "src" / "scenarios" / "templates"
POLICY_FILE = ROOT / "src" / "policies" / "catalog.json"


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_scenarios() -> list[dict[str, Any]]:
    scenarios: list[dict[str, Any]] = []
    for file in sorted(SCENARIO_DIR.glob("*.json")):
        data = _load_json(file)
        data.setdefault("scenario_id", file.stem)
        scenarios.append(data)
    return scenarios


def _load_policies() -> list[dict[str, Any]]:
    data = _load_json(POLICY_FILE)
    return data if isinstance(data, list) else []


def _build_phases(scenario: dict[str, Any]) -> list[dict[str, Any]]:
    phases = []
    for phase in scenario.get("phases", []):
        phase_id = phase.get("name", "phase").lower().replace(" ", "_")
        policies = phase.get("policy_in_play", [])
        phases.append(
            {
                "phase_id": f"{scenario.get('scenario_id')}::{phase_id}",
                "scenario_id": scenario.get("scenario_id"),
                "phase_name": phase.get("name"),
                "description": phase.get("description"),
                "metrics": phase.get("metrics", []),
                "policy_ids": policies,
                "severity": random.choice(["low", "medium", "high"]),
            }
        )
    return phases


def _match_policies(policy_ids: list[str], policies: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [policy for policy in policies if policy.get("policy_id") in policy_ids]


def _stream_phases(phase_queue: list[dict[str, Any]], policies: list[dict[str, Any]], interval: float) -> None:
    print("Starting detection stream (ctrl-c to stop)...")
    while True:
        for phase in phase_queue:
            event = {
                "timestamp": time.time(),
                "phase": phase["phase_name"],
                "scenario": phase["scenario_id"],
                "severity": phase["severity"],
                "description": phase["description"],
                "matched_policies": [p["policy_id"] for p in _match_policies(phase["policy_ids"], policies)],
                "policy_rationale": [p.get("intent") for p in _match_policies(phase["policy_ids"], policies)],
            }
            print(json.dumps(event))
            time.sleep(interval)


def _default_scenario_id() -> str | None:
    scenarios = _load_scenarios()
    return scenarios[0].get("scenario_id") if scenarios else None


def main() -> None:
    parser = argparse.ArgumentParser(description="Stream detection events from scenario phases.")
    parser.add_argument("--scenario", required=False, help="Scenario ID to stream (defaults to first).")
    parser.add_argument("--interval", type=float, default=2.0, help="Seconds between phase events.")
    args = parser.parse_args()

    scenarios = _load_scenarios()
    if not scenarios:
        raise SystemExit("No scenario templates found.")

    scenario_id = args.scenario or _default_scenario_id()
    if not scenario_id:
        raise SystemExit("Unable to select a scenario.")

    scenario = next((s for s in scenarios if s.get("scenario_id") == scenario_id), None)
    if not scenario:
        raise SystemExit(f"Scenario '{scenario_id}' not found.")

    policies = _load_policies()
    phases = _build_phases(scenario)
    if not phases:
        raise SystemExit("Scenario contains no phases to stream.")

    _stream_phases(phases, policies, args.interval)


if __name__ == "__main__":
    main()
