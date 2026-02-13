from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException

ROOT_DIR = Path(__file__).resolve().parents[3]
SCENARIOS_DIR = ROOT_DIR / "src" / "scenarios" / "templates"
POLICY_FILE = ROOT_DIR / "src" / "policies" / "catalog.json"

app = FastAPI(
    title="Security Breach Simulator API",
    description="Serves scenario templates and policy catalog data for the simulator and dashboard.",
    version="0.1.0",
)


def _load_json(path: Path) -> Any:
    if not path.exists():
        raise FileNotFoundError(f"Missing data file: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _load_scenarios() -> list[dict[str, Any]]:
    scenarios = []
    for file in sorted(SCENARIOS_DIR.glob("*.json")):
        data = _load_json(file)
        data.setdefault("scenario_id", file.stem)
        data["_source_file"] = file.name
        scenarios.append(data)
    return scenarios


def _load_policies() -> list[dict[str, Any]]:
    data = _load_json(POLICY_FILE)
    if isinstance(data, list):
        return data
    return []


def _get_catalog() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    return _load_scenarios(), _load_policies()


@lru_cache(maxsize=1)
def _cached_catalog() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    return _get_catalog()


def _find_scenario_by_id(scenario_id: str) -> dict[str, Any] | None:
    scenarios, _ = _cached_catalog()
    for scenario in scenarios:
        if scenario.get("scenario_id") == scenario_id:
            return scenario
    return None


def _match_policies(policy_ids: list[str]) -> list[dict[str, Any]]:
    _, policies = _cached_catalog()
    return [policy for policy in policies if policy.get("policy_id") in policy_ids]


@app.get("/scenarios")
def list_scenarios() -> dict[str, Any]:
    scenarios, _ = _cached_catalog()
    return {
        "items": [
            {
                "id": scenario.get("scenario_id"),
                "title": scenario.get("title"),
                "description": scenario.get("description"),
                "tags": scenario.get("tags", []),
                "entry_point": scenario.get("entry_point"),
            }
            for scenario in scenarios
        ]
    }


@app.get("/scenarios/{scenario_id}")
def get_scenario(scenario_id: str) -> dict[str, Any]:
    scenario = _find_scenario_by_id(scenario_id)
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    policy_links = scenario.get("policy_links", scenario.get("policy_in_play", []))
    policies = _match_policies(policy_links)
    return {
        "scenario": scenario,
        "policies": policies,
    }


@app.get("/policies")
def list_policies() -> dict[str, Any]:
    _, policies = _cached_catalog()
    return {
        "items": [
            {
                "id": policy.get("policy_id"),
                "title": policy.get("title"),
                "domain": policy.get("domain"),
                "severity": policy.get("severity"),
                "tags": policy.get("tags", []),
            }
            for policy in policies
        ]
    }
