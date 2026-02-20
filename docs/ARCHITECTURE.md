# Architecture Plan: Live Security Breach Simulator with Policy AI

## Intent
This project sits at the intersection of tabletop red teaming and automated policy compliance. It allows security teams to craft incident scenarios, correlate them with documented governance, and generate actionable breach narratives for training, automation, or executive review.

## High-Level Layers

1. **Scenario Templates** – Structured JSON templates describe attack patterns, critical assets, detection mechanisms, and success conditions. They should be portable, human-readable, and extendable for new attack paths.
2. **Policy Catalog** – A registry of policies, each with intents, severity, automation hints, and human remediation steps. Policy AI agents rely on this catalog to translate scenarios into compliance/detection insights.
3. **Breach Generator** – A lightweight orchestrator that merges scenario contexts with policy guidance. It narrates the breach, highlights controls that engage/evade, and surfaces policy gaps for follow-up.

## Current Status (Feb 21, 2026)

### Completed
- ✅ Scenario templates (4 scenarios)
- ✅ Policy catalog with ~15 policies
- ✅ Breach generator (Python CLI)
- ✅ FastAPI backend (v0.2.0)
- ✅ Detection streamer
- ✅ Test scaffolding

### In Progress
- 🔄 Dashboard integration
- 🔄 More scenario templates

### Planned
- ⏳ Policy AI scoring layer
- ⏳ Web UI / Dashboard
- ⏳ Automated response suggestions

## Data Flow
```
Scenario Templates (JSON) → Breach Generator → Narrated Timeline
                           ↓
                    Policy Catalog → Policy Annotations
                           ↓
                    API Backend → Dashboard/CLI
```

## API Endpoints (v0.2.0)

### Scenarios
- `GET /scenarios` - List all scenarios (with filters)
- `GET /scenarios/{id}` - Get scenario details
- `GET /scenarios/{id}/timeline` - Get timeline view

### Policies
- `GET /policies` - List all policies
- `GET /policies/{id}` - Get policy details

### Dashboard
- `GET /dashboard/stats` - Overview statistics
- `GET /health` - Health check

## Directory Structure
```
├── backend/
│   ├── api/
│   │   ├── app.py          # FastAPI application
│   │   └── requirements.txt
│   └── detection/
│       └── streamer.py     # SIEM event stream simulator
├── src/
│   ├── generators/
│   │   └── sample_breach.py
│   ├── policies/
│   │   └── catalog.json
│   └── scenarios/
│       └── templates/      # JSON scenario blueprints
├── tests/
│   ├── test_scenarios.py
│   └── requirements.txt
└── docs/
    └── ARCHITECTURE.md
```

## Scenario Templates

| ID | Name | Severity | Category |
|----|------|----------|----------|
| phishing_lateral_movement | Phishing Lateral Movement | High | phishing |
| supply_chain_compromise | Supply Chain Compromise | Critical | supply_chain |
| insider_threat_data_exfil | Insider Threat - Data Exfiltration | Critical | insider_threat |
| ransomware_attack | Ransomware Attack - Lateral Spread | Critical | malware |

## Testing
Run tests with:
```bash
cd tests
pip install -r requirements.txt
pytest
```

## Running

### API Server
```bash
cd backend/api
pip install -r requirements.txt
uvicorn app:app --reload
```

### Generator
```bash
python src/generators/sample_breach.py
```

### Detection Streamer
```bash
python backend/detection/streamer.py --scenario phishing_lateral_movement --interval 1.5
```

## Next Steps
1. Expand scenario templates (target: 10 scenarios)
2. Add policy scoring algorithms
3. Build web dashboard
4. Integrate AI for policy recommendations
