"""
AI Threat Analysis Engine — Security Breach Simulator
Powered by Anthropic Claude. Generates dynamic threat dossiers,
adaptive hints, and post-incident red team reports.
"""
from __future__ import annotations

import json
import hashlib
import time
from pathlib import Path
from typing import Any, Generator

ROOT_DIR = Path(__file__).resolve().parents[1]
CACHE_DIR = ROOT_DIR / ".ai_cache"
CACHE_DIR.mkdir(exist_ok=True)


def _cache_key(payload: dict[str, Any]) -> str:
    raw = json.dumps(payload, sort_keys=True)
    return hashlib.md5(raw.encode()).hexdigest()


def _load_cache(key: str) -> dict[str, Any] | None:
    path = CACHE_DIR / f"{key}.json"
    if path.exists():
        return json.loads(path.read_text())
    return None


def _save_cache(key: str, data: dict[str, Any]) -> None:
    path = CACHE_DIR / f"{key}.json"
    path.write_text(json.dumps(data, indent=2))


def _call_claude(system: str, user: str, stream: bool = False) -> str | Generator[str, None, None]:
    """Call Claude API. Falls back to rich mock data if no API key."""
    try:
        import anthropic  # type: ignore[import]
        client = anthropic.Anthropic()

        if stream:
            def _stream_gen() -> Generator[str, None, None]:
                with client.messages.stream(
                    model="claude-sonnet-4-20250514",
                    max_tokens=1024,
                    system=system,
                    messages=[{"role": "user", "content": user}],
                ) as s:
                    for text in s.text_stream:
                        yield text
            return _stream_gen()
        else:
            resp = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1024,
                system=system,
                messages=[{"role": "user", "content": user}],
            )
            return resp.content[0].text

    except Exception:
        # Rich fallback so the app always works
        return _mock_response(user)


def _mock_response(prompt: str) -> str:
    """Return realistic mock AI response when API unavailable."""
    if "dossier" in prompt.lower():
        return (
            "**THREAT ACTOR DOSSIER**\n\n"
            "**Classification:** Advanced Persistent Threat (APT)\n"
            "**Motivation:** Financial gain / espionage\n"
            "**Origin:** Eastern Europe (high confidence)\n"
            "**TTPs:** Spear-phishing → credential harvesting → lateral movement via SMB\n"
            "**Known Aliases:** UNC2452, COZY BEAR variant\n"
            "**Infrastructure:** Bulletproof hosting in AS49877, Tor exit nodes\n"
            "**Weaponisation:** Custom .NET loader, Cobalt Strike beacon (modified)\n"
            "**MITRE Groups:** G0016, G0032\n\n"
            "**Assessment:** This actor demonstrates patience and precision. "
            "Expect multi-stage intrusion with 2-4 week dwell time before exfil."
        )
    if "hint" in prompt.lower():
        return (
            "💡 **Adaptive Hint**\n\n"
            "Check your SIEM for event ID 4625 (failed logon) clusters — "
            "more than 10 failures from one source in 60 seconds is a credential-stuffing indicator. "
            "Correlate with 4624 (success) events that follow to find the compromised account."
        )
    if "report" in prompt.lower() or "missed" in prompt.lower():
        return (
            "**POST-INCIDENT ANALYSIS**\n\n"
            "**What You Missed:**\n"
            "- Stage 2 lateral movement via WMI was not flagged (event ID 4688 + wmic.exe)\n"
            "- No network isolation triggered within the 5-minute SLA window\n"
            "- Evidence not preserved before system reimage\n\n"
            "**Optimal Playbook Deviation:** 34% — significant gaps in containment phase\n\n"
            "**Recommendations:**\n"
            "1. Create alert rule: wmic.exe spawned by non-admin process\n"
            "2. Automate host isolation via EDR API on Tier-1 ransomware detection\n"
            "3. Implement forensic snapshot before any remediation action"
        )
    return "**AI Analysis**\n\nAnalysis complete. Review the scenario timeline for IOCs."


class AIEngine:
    """Central AI analysis engine for scenario intelligence."""

    def __init__(self) -> None:
        self._system_prompt = (
            "You are an expert cybersecurity analyst and red team operator with 15 years of experience. "
            "You write precise, technical, actionable threat intelligence. "
            "Use MITRE ATT&CK framework terminology. Be concise and structured."
        )

    def get_threat_dossier(self, scenario: dict[str, Any], use_cache: bool = True) -> str:
        """Generate a threat actor dossier for a scenario."""
        key = _cache_key({"type": "dossier", "id": scenario.get("id", scenario.get("scenario_id"))})
        if use_cache:
            cached = _load_cache(key)
            if cached:
                return cached["content"]

        prompt = (
            f"Generate a detailed threat actor dossier for this cyber attack scenario:\n"
            f"Name: {scenario.get('name', 'Unknown')}\n"
            f"Category: {scenario.get('category', 'unknown')}\n"
            f"Severity: {scenario.get('severity', 'unknown')}\n"
            f"Attack patterns: {scenario.get('attack_patterns', [])}\n\n"
            f"Include: threat actor classification, motivation, geographic origin, "
            f"TTPs, infrastructure details, and analyst assessment. Use markdown formatting."
        )

        result = _call_claude(self._system_prompt, prompt)
        if isinstance(result, Generator):
            result = "".join(result)

        _save_cache(key, {"content": result, "generated_at": time.time()})
        return result

    def get_adaptive_hint(self, scenario: dict[str, Any], stage: int, actions_taken: list[str]) -> str:
        """Get a contextual hint based on current stage and actions."""
        prompt = (
            f"A cybersecurity student is practicing incident response on '{scenario.get('name')}'. "
            f"They are at stage {stage}. Actions taken so far: {actions_taken}. "
            f"Give ONE specific, technical hint about what to look for or do next. "
            f"Do not give away the answer directly. Use SIEM/log terminology."
        )
        result = _call_claude(self._system_prompt, prompt)
        return result if isinstance(result, str) else "".join(result)

    def get_post_incident_report(
        self,
        scenario: dict[str, Any],
        actions_taken: list[dict[str, Any]],
        score: dict[str, Any],
    ) -> str:
        """Generate AI-powered post-incident analysis."""
        prompt = (
            f"Analyze this incident response performance:\n"
            f"Scenario: {scenario.get('name')}\n"
            f"Final Score: {score.get('total_score')}/100 (Grade: {score.get('grade')})\n"
            f"Actions Taken: {json.dumps(actions_taken[:10], indent=2)}\n\n"
            f"Provide: (1) What they did well, (2) Critical gaps, "
            f"(3) What the real attacker would have done while they were delayed, "
            f"(4) Three specific detection rules to write to catch this in future. "
            f"Be direct and technical."
        )
        result = _call_claude(self._system_prompt, prompt)
        return result if isinstance(result, str) else "".join(result)

    def stream_analysis(self, scenario: dict[str, Any]) -> Generator[str, None, None]:
        """Stream AI analysis token by token for CLI display."""
        prompt = (
            f"Provide a comprehensive threat analysis for: {scenario.get('name')}. "
            f"Cover: attack vector, affected systems, detection opportunities at each stage, "
            f"and top 3 preventive controls. Use headers and bullet points."
        )
        result = _call_claude(self._system_prompt, prompt, stream=True)
        if isinstance(result, str):
            for char in result:
                yield char
        else:
            yield from result


# Module-level singleton
_engine: AIEngine | None = None


def get_engine() -> AIEngine:
    global _engine
    if _engine is None:
        _engine = AIEngine()
    return _engine


if __name__ == "__main__":
    engine = get_engine()
    scenario = {"name": "Ransomware Attack", "category": "malware", "severity": "critical"}
    print(engine.get_threat_dossier(scenario))
