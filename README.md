# Live Security Breach Simulator with Policy AI

**Live Security Breach Simulator** is a security-focused scenario engine that blends scripted breach narratives with policy-aware guidance. Each simulated incident pairs scenario templates with a policy catalog that articulates guardrails, response playbooks, and automated policy AI recommendations.

## Key Components

- `src/scenarios/templates/` – Declarative scenario blueprints describing threat actors, attack patterns, objectives, and measurement points.
- `src/policies/catalog.json` – A living policy register capturing control objectives, tolerance levels, and human-readable remediations.
- `src/generators/sample_breach.py` – A lightweight generator that stitches scenario data and policy guidance into a coherent breach narrative for training, tabletop exercises, or automation hops.
- `docs/ARCHITECTURE.md` – Architectural intent and how each module interacts in early development iterations.

## Getting Started

1. Install Python 3.11+ if not already installed.
2. Run the sample breach generator:

   ```bash
   python src/generators/sample_breach.py
   ```

   The script loads scenario and policy samples, then produces a narrated breach timeline with policy tags.

## Directory Layout

```
├── docs/ARCHITECTURE.md
├── src/
│   ├── generators/sample_breach.py
│   ├── policies/catalog.json
│   └── scenarios/templates/
└── README.md
```

## Next Steps

- Expand scenario templates with branching playbooks.
- Build a policy AI evaluation layer that scores policy adherence.
- Wire a web UI / CLI for crafting custom scenario suites and triggering policy simulations.

## API Backend

The new FastAPI service sits under `backend/api` and exposes scenario + policy data for the simulator or a future dashboard.

```bash
cd backend/api
pip install -r requirements.txt
uvicorn app:app --reload
```

Visit `http://127.0.0.1:8000/docs` after starting the server to explore the endpoints.

