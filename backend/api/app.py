"""
Security Breach Simulator API
FastAPI backend for scenario and policy management
"""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any
from datetime import datetime

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

ROOT_DIR = Path(__file__).resolve().parents[3]
SCENARIOS_DIR = ROOT_DIR / "src" / "scenarios" / "templates"
POLICY_FILE = ROOT_DIR / "src" / "policies" / "catalog.json"

app = FastAPI(
    title="Security Breach Simulator API",
    description="Serves scenario templates and policy catalog data for the simulator and dashboard.",
    version="0.2.0",
)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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


# ==================== SCENARIOS ====================

@app.get("/scenarios")
def list_scenarios(
    severity: str | None = Query(None, description="Filter by severity"),
    category: str | None = Query(None, description="Filter by category"),
    search: str | None = Query(None, description="Search in name/description"),
    limit: int = Query(50, ge=1, le=100, description="Max items to return"),
    offset: int = Query(0, ge=0, description="Number of items to skip"),
) -> dict[str, Any]:
    """List all available scenarios with optional filters and pagination"""
    scenarios, _ = _cached_catalog()
    
    # Apply filters
    if severity:
        scenarios = [s for s in scenarios if s.get("severity", "").lower() == severity.lower()]
    if category:
        scenarios = [s for s in scenarios if s.get("category", "").lower() == category.lower()]
    if search:
        search = search.lower()
        scenarios = [
            s for s in scenarios
            if search in s.get("name", "").lower() or search in s.get("description", "").lower()
        ]
    
    total = len(scenarios)
    paginated = scenarios[offset:offset + limit]
    
    return {
        "items": [
            {
                "id": scenario.get("scenario_id"),
                "name": scenario.get("name"),
                "description": scenario.get("description"),
                "severity": scenario.get("severity"),
                "category": scenario.get("category"),
                "difficulty": scenario.get("difficulty"),
                "estimated_duration_minutes": scenario.get("estimated_duration_minutes"),
            }
            for scenario in paginated
        ],
        "total": total,
        "limit": limit,
        "offset": offset
    }


@app.get("/scenarios/{scenario_id}")
def get_scenario(scenario_id: str) -> dict[str, Any]:
    """Get detailed scenario by ID"""
    scenario = _find_scenario_by_id(scenario_id)
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    
    # Get linked policies
    policy_ids = scenario.get("policy_links", scenario.get("policy_in_play", []))
    policies = _match_policies(policy_ids)
    
    return {
        "scenario": scenario,
        "policies": policies,
        "generated_at": datetime.utcnow().isoformat()
    }


@app.get("/scenarios/{scenario_id}/timeline")
def get_scenario_timeline(scenario_id: str) -> dict[str, Any]:
    """Get scenario as timeline of events"""
    scenario = _find_scenario_by_id(scenario_id)
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    
    stages = scenario.get("stages", [])
    timeline = []
    
    for i, stage in enumerate(stages):
        timeline.append({
            "stage": stage.get("stage"),
            "name": stage.get("name"),
            "description": stage.get("description"),
            "indicators": stage.get("indicators", []),
            "policies": stage.get("policies", []),
            "duration_minutes": stage.get("duration_minutes", 0),
            "relative_time": f"T+{sum(s.get('duration_minutes', 0) for s in stages[:i])}m"
        })
    
    return {
        "scenario_id": scenario_id,
        "scenario_name": scenario.get("name"),
        "timeline": timeline,
        "total_duration": sum(s.get("duration_minutes", 0) for s in stages)
    }


# ==================== POLICIES ====================

@app.get("/policies")
def list_policies(
    domain: str | None = Query(None, description="Filter by domain"),
    severity: str | None = Query(None, description="Filter by severity"),
    limit: int = Query(50, ge=1, le=100, description="Max items to return"),
    offset: int = Query(0, ge=0, description="Number of items to skip"),
) -> dict[str, Any]:
    """List all policies with optional filters and pagination"""
    _, policies = _cached_catalog()
    
    if domain:
        policies = [p for p in policies if p.get("domain", "").lower() == domain.lower()]
    if severity:
        policies = [p for p in policies if p.get("severity", "").lower() == severity.lower()]
    
    total = len(policies)
    paginated = policies[offset:offset + limit]
    
    return {
        "items": paginated,
        "total": total,
        "limit": limit,
        "offset": offset
    }


@app.get("/policies/{policy_id}")
def get_policy(policy_id: str) -> dict[str, Any]:
    """Get policy by ID"""
    _, policies = _cached_catalog()
    for policy in policies:
        if policy.get("policy_id") == policy_id:
            return {"policy": policy}
    raise HTTPException(status_code=404, detail="Policy not found")


# ==================== DASHBOARD ====================

@app.get("/dashboard/stats")
def get_dashboard_stats() -> dict[str, Any]:
    """Get overview statistics for dashboard"""
    scenarios, policies = _cached_catalog()
    
    # Count by severity
    severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    category_counts = {}
    
    for scenario in scenarios:
        sev = scenario.get("severity", "medium").lower()
        if sev in severity_counts:
            severity_counts[sev] += 1
        
        cat = scenario.get("category", "unknown")
        category_counts[cat] = category_counts.get(cat, 0) + 1
    
    # Count policies by domain
    domain_counts = {}
    for policy in policies:
        domain = policy.get("domain", "unknown")
        domain_counts[domain] = domain_counts.get(domain, 0) + 1
    
    return {
        "scenarios": {
            "total": len(scenarios),
            "by_severity": severity_counts,
            "by_category": category_counts
        },
        "policies": {
            "total": len(policies),
            "by_domain": domain_counts
        },
        "generated_at": datetime.utcnow().isoformat()
    }


@app.get("/health")
def health_check() -> dict[str, Any]:
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "0.2.0",
        "timestamp": datetime.utcnow().isoformat()
    }
