# Architecture Plan: Live Security Breach Simulator with Policy AI

## Intent
This project sits at the intersection of tabletop red teaming and automated policy compliance. It should allow security teams (and policy AI agents) to craft incident scenarios, correlate them with documented governance, and generate actionable breach narratives for training, automation, or executive review.

## High-Level Layers

1. **Scenario Templates** – Structured JSON templates describe attack patterns, critical assets, detection mechanisms, and success conditions. They should be portable, human-readable, and extendable for new attack paths.
2. **Policy Catalog** – A registry of policies, each with intents, severity, automation hints, and human remediation steps. Policy AI agents rely on this catalog to translate scenarios into compliance/detection insights.
3. **Breach Generator** – A lightweight orchestrator that merges scenario contexts with policy guidance. It narrates the breach, highlights controls that engage/evade, and surfaces policy gaps for follow-up.

## Data Flow
- The generator loads scenario templates from `src/scenarios/templates/` and policy entries from `src/policies/catalog.json`.
- Policies contain tags that map back to scenarios (e.g., endpoint, identity, data exfiltration). When a scenario references a tag, the generator annotates the timeline with the relevant policy.
- Future iterations will swap the generator for a policy AI assistant that can score incidents, recommend novel controls, and auto-propose mitigations.

## Incremental Steps
1. Build foundational templates to prove out the schema.
2. Populate a policy catalog with enforcement levers and risk signals.
3. Create a prototype breach generator to validate the narrative pipeline.
4. Extend with Policy AI: scoring models, linting, and automated response suggestions.
