"""
Incident Report Generator — Security Breach Simulator
Generates professional HTML incident reports with inline CSS.
Output: .reports/INC-YYYY-MMDD-{run_id}.html
"""
from __future__ import annotations

import json
import time
import webbrowser
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT_DIR = Path(__file__).resolve().parents[1]
REPORTS_DIR = ROOT_DIR / ".reports"
REPORTS_DIR.mkdir(exist_ok=True)

_UNICODE_BARS = {
    100: "████████████████████",
    90:  "██████████████████░░",
    80:  "████████████████░░░░",
    70:  "██████████████░░░░░░",
    60:  "████████████░░░░░░░░",
    50:  "██████████░░░░░░░░░░",
    40:  "████████░░░░░░░░░░░░",
    30:  "██████░░░░░░░░░░░░░░",
    20:  "████░░░░░░░░░░░░░░░░",
    10:  "██░░░░░░░░░░░░░░░░░░",
    0:   "░░░░░░░░░░░░░░░░░░░░",
}

def _bar_for_pct(pct: float) -> str:
    rounded = round(pct / 10) * 10
    return _UNICODE_BARS.get(min(100, max(0, rounded)), "░░░░░░░░░░░░░░░░░░░░")

def _grade_color(grade: str) -> str:
    return {"A+":"#00c853","A":"#00c853","B":"#64dd17","C":"#ffd600",
            "D":"#ff6d00","F":"#d50000"}.get(grade, "#9e9e9e")

def _severity_color(sev: str) -> str:
    return {"critical":"#d50000","high":"#ff6d00","medium":"#ffd600","low":"#00c853"}.get(sev.lower(),"#9e9e9e")


class ReportGenerator:
    """Generates professional HTML incident reports."""

    def __init__(self, analyst_name: str = "SOC Analyst") -> None:
        self.analyst_name = analyst_name

    def generate(
        self,
        scenario: dict[str, Any],
        scorecard: dict[str, Any],
        actions: list[dict[str, Any]],
        ai_analysis: str = "",
        run_id: str | None = None,
    ) -> Path:
        run_id = run_id or scorecard.get("run_id", f"run_{int(time.time())}")
        date_str = datetime.now().strftime("%Y-%m-%d")
        incident_id = f"INC-{datetime.now().strftime('%Y-%m%d')}-{run_id[-6:].upper()}"
        filename = REPORTS_DIR / f"{incident_id}.html"

        html = self._build_html(scenario, scorecard, actions, ai_analysis, incident_id, date_str)
        filename.write_text(html, encoding="utf-8")
        return filename

    def _build_html(
        self, scenario: dict, scorecard: dict, actions: list[dict],
        ai_analysis: str, incident_id: str, date_str: str,
    ) -> str:
        grade = scorecard.get("grade", "F")
        total = scorecard.get("total_score", 0)
        max_s = scorecard.get("max_possible", 100)
        pct = total / max_s * 100 if max_s else 0
        sev = scenario.get("severity", "unknown")
        radar = scorecard.get("radar_data", {})
        dims = scorecard.get("dimensions", {})

        dim_rows = "".join(
            f"""<tr>
              <td>{name.replace('_',' ').title()}</td>
              <td style="color:{('#00c853' if v['pct']>=70 else ('#ffd600' if v['pct']>=50 else '#d50000'))};font-family:monospace">
                {_bar_for_pct(v['pct'])} {v['score']}/{v['max']}
              </td>
              <td style="color:{('#00c853' if v['pct']>=70 else ('#ffd600' if v['pct']>=50 else '#d50000'))};font-weight:600">{v['pct']:.0f}%</td>
            </tr>"""
            for name, v in dims.items()
        )

        action_rows = "".join(
            f"""<tr>
              <td style="font-family:monospace;font-size:0.8em;color:#888">+{a.get('elapsed',0):.0f}s</td>
              <td><span style="background:#1e3a5f;color:#64b5f6;padding:2px 8px;border-radius:4px;font-size:0.8em">{a.get('type','action').upper()}</span></td>
              <td>{a.get('description','')}</td>
              <td style="color:#aaa">Stage {a.get('stage',0)}</td>
            </tr>"""
            for a in (actions or [])
        )

        radar_points = self._radar_svg(radar)
        ai_html = ai_analysis.replace("\n", "<br>").replace("**", "") if ai_analysis else (
            "<p style='color:#888'>AI analysis not available. Set ANTHROPIC_API_KEY to enable.</p>"
        )

        tips = scorecard.get("tips", [])
        tips_html = "".join(f"<li>{t}</li>" for t in tips)
        mitre_techniques = scenario.get("mitre_attack_techniques", scenario.get("attack_patterns", []))
        mitre_html = "".join(
            f'<span style="background:#1a237e;color:#90caf9;padding:4px 10px;border-radius:4px;margin:3px;display:inline-block;font-family:monospace;font-size:0.85em">{t}</span>'
            for t in mitre_techniques
        )
        stages = scenario.get("stages", [])
        timeline_html = "".join(
            f"""<div style="display:flex;gap:16px;margin-bottom:16px;padding:12px;background:#111;border-radius:8px;border-left:3px solid #1565c0">
              <div style="color:#1565c0;font-family:monospace;white-space:nowrap;font-size:0.85em">+{stage.get('duration_minutes',0)*i}m</div>
              <div><strong style="color:#e0e0e0">Stage {stage.get('stage',i+1)}: {stage.get('name','')}</strong>
                <div style="color:#aaa;font-size:0.9em;margin-top:4px">{stage.get('description','')}</div></div>
            </div>"""
            for i, stage in enumerate(stages)
        )
        objectives_html = "".join(f"<li>{o}</li>" for o in scenario.get("objectives", []))

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{incident_id} — Incident Response Report</title>
  <style>
    * {{ margin:0; padding:0; box-sizing:border-box; }}
    body {{ font-family:'Segoe UI',system-ui,sans-serif; background:#0a0a0f; color:#e0e0e0; line-height:1.6; }}
    .page {{ max-width:960px; margin:0 auto; padding:2rem; }}
    .header {{ background:linear-gradient(135deg,#0d1b2a 0%,#1a237e 100%); padding:2.5rem; border-radius:12px; margin-bottom:2rem; position:relative; overflow:hidden; }}
    .header::before {{ content:''; position:absolute; top:-50%; right:-10%; width:300px; height:300px; background:radial-gradient(circle,rgba(100,181,246,0.1),transparent 70%); }}
    .classified {{ display:inline-block; border:1px solid #d50000; color:#d50000; padding:3px 12px; font-family:monospace; font-size:0.75em; letter-spacing:2px; margin-bottom:1rem; }}
    h1 {{ font-size:1.8rem; font-weight:300; letter-spacing:2px; color:#fff; margin-bottom:0.5rem; }}
    .meta {{ display:flex; gap:2rem; flex-wrap:wrap; margin-top:1rem; }}
    .meta-item {{ font-size:0.85em; color:#90caf9; }}
    .meta-item strong {{ color:#fff; display:block; font-size:1em; }}
    .section {{ background:#12121a; border:1px solid #1a1a2a; border-radius:12px; padding:1.5rem; margin-bottom:1.5rem; }}
    .section-title {{ font-size:0.75em; text-transform:uppercase; letter-spacing:3px; color:#64b5f6; margin-bottom:1rem; padding-bottom:0.5rem; border-bottom:1px solid #1a1a2a; }}
    table {{ width:100%; border-collapse:collapse; }}
    th {{ text-align:left; font-size:0.75em; text-transform:uppercase; letter-spacing:1px; color:#888; padding:8px 0; border-bottom:1px solid #1a1a2a; }}
    td {{ padding:10px 0; border-bottom:1px solid #0d0d18; font-size:0.9em; vertical-align:middle; }}
    tr:last-child td {{ border-bottom:none; }}
    .grade-badge {{ display:inline-flex; align-items:center; justify-content:center; width:72px; height:72px; border-radius:50%; font-size:1.8rem; font-weight:700; border:3px solid {_grade_color(grade)}; color:{_grade_color(grade)}; }}
    .score-row {{ display:flex; align-items:center; gap:2rem; }}
    .score-num {{ font-size:2.5rem; font-weight:700; color:{_grade_color(grade)}; font-family:monospace; }}
    .sev-badge {{ background:{_severity_color(sev)}22; color:{_severity_color(sev)}; border:1px solid {_severity_color(sev)}; padding:4px 14px; border-radius:20px; font-size:0.8em; font-weight:600; text-transform:uppercase; letter-spacing:1px; }}
    .tip {{ background:#0d1b0d; border-left:3px solid #00c853; padding:10px 14px; margin:6px 0; border-radius:0 6px 6px 0; font-size:0.9em; }}
    .ai-section {{ background:#0d1218; border:1px solid #1a2a3a; border-radius:12px; padding:1.5rem; margin-bottom:1.5rem; }}
    .footer {{ text-align:center; padding:2rem; color:#444; font-size:0.8em; border-top:1px solid #1a1a2a; margin-top:2rem; }}
    @media print {{ body {{ background:#fff; color:#000; }} .header {{ background:#1a237e !important; }} }}
  </style>
</head>
<body>
<div class="page">

  <div class="header">
    <div class="classified">⚠ CONFIDENTIAL — FOR INTERNAL USE ONLY</div>
    <h1>📋 INCIDENT RESPONSE REPORT</h1>
    <div class="meta">
      <div class="meta-item"><strong>{incident_id}</strong>Incident ID</div>
      <div class="meta-item"><strong>{date_str}</strong>Report Date</div>
      <div class="meta-item"><strong>{self.analyst_name}</strong>Lead Analyst</div>
      <div class="meta-item"><strong>{scorecard.get('difficulty','medium').upper()}</strong>Difficulty</div>
      <div class="meta-item"><span class="sev-badge">{sev}</span> Severity</div>
    </div>
  </div>

  <!-- Score Summary -->
  <div class="section">
    <div class="section-title">Performance Summary</div>
    <div class="score-row">
      <div class="grade-badge">{grade}</div>
      <div>
        <div class="score-num">{total} <span style="font-size:1rem;color:#888">/ {max_s}</span></div>
        <div style="color:#888;font-size:0.9em">Overall Score — {pct:.0f}th percentile</div>
        <div style="color:#64b5f6;font-size:0.85em;margin-top:4px">+{scorecard.get('xp_earned',0)} XP earned this run</div>
      </div>
      <div style="flex:1">
        {radar_points}
      </div>
    </div>
  </div>

  <!-- Scenario Info -->
  <div class="section">
    <div class="section-title">Incident Overview</div>
    <table>
      <tr><th style="width:200px">Field</th><th>Details</th></tr>
      <tr><td style="color:#90caf9">Scenario</td><td>{scenario.get('name','Unknown')}</td></tr>
      <tr><td style="color:#90caf9">Category</td><td>{scenario.get('category','unknown').replace('_',' ').title()}</td></tr>
      <tr><td style="color:#90caf9">Description</td><td style="color:#aaa">{scenario.get('description','')}</td></tr>
      <tr><td style="color:#90caf9">Estimated Duration</td><td>{scenario.get('estimated_duration_minutes',0)} minutes</td></tr>
    </table>
    <div style="margin-top:1rem"><strong style="font-size:0.85em;color:#888">MITRE ATT&CK TECHNIQUES:</strong><br><div style="margin-top:6px">{mitre_html or '<span style="color:#555">None mapped</span>'}</div></div>
  </div>

  <!-- Skills Matrix -->
  <div class="section">
    <div class="section-title">8-Dimension Skills Matrix</div>
    <table>
      <tr><th>Dimension</th><th>Score</th><th>Percentage</th></tr>
      {dim_rows}
    </table>
  </div>

  <!-- Attack Timeline -->
  <div class="section">
    <div class="section-title">Attack Chain Timeline</div>
    {timeline_html or '<p style="color:#555">No stage data available.</p>'}
  </div>

  <!-- Actions Taken -->
  <div class="section">
    <div class="section-title">Analyst Actions Log</div>
    {'<table><tr><th>Time</th><th>Type</th><th>Action</th><th>Stage</th></tr>' + action_rows + '</table>' if actions else '<p style="color:#555">No actions recorded.</p>'}
  </div>

  <!-- Objectives -->
  <div class="section">
    <div class="section-title">Scenario Objectives</div>
    <ul style="list-style:none;padding:0">{objectives_html}</ul>
  </div>

  <!-- AI Analysis -->
  <div class="ai-section">
    <div class="section-title" style="color:#ff9800">🤖 AI Post-Incident Analysis (Claude)</div>
    <div style="font-size:0.9em;color:#ccc;line-height:1.8">{ai_html}</div>
  </div>

  <!-- Improvement Tips -->
  <div class="section">
    <div class="section-title">Recommendations</div>
    <ul style="list-style:none;padding:0">
      {''.join(f'<div class="tip">💡 {t}</div>' for t in (tips or ['Keep up the good work!']))}
    </ul>
  </div>

  <div class="footer">
    Generated by Security Breach Simulator v1.0.0 &nbsp;|&nbsp;
    {incident_id} &nbsp;|&nbsp; {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}
  </div>

</div>
</body>
</html>"""

    def _radar_svg(self, radar: dict[str, float]) -> str:
        """Generate a simple inline SVG radar chart."""
        if not radar:
            return ""
        import math
        labels = list(radar.keys())
        values = list(radar.values())
        n = len(labels)
        cx, cy, r = 90, 90, 70
        points_outer, points_data = [], []
        for i in range(n):
            angle = math.pi / 2 - 2 * math.pi * i / n
            ox = cx + r * math.cos(angle)
            oy = cy - r * math.sin(angle)
            points_outer.append((ox, oy))
            dr = r * (values[i] / 100)
            dx = cx + dr * math.cos(angle)
            dy = cy - dr * math.sin(angle)
            points_data.append((dx, dy))

        outer_poly = " ".join(f"{x:.1f},{y:.1f}" for x, y in points_outer)
        data_poly = " ".join(f"{x:.1f},{y:.1f}" for x, y in points_data)

        spokes = "".join(
            f'<line x1="{cx}" y1="{cy}" x2="{x:.1f}" y2="{y:.1f}" stroke="#1a1a3a" stroke-width="1"/>'
            for x, y in points_outer
        )
        return (
            f'<svg width="180" height="180" viewBox="0 0 180 180" style="overflow:visible">'
            f'<polygon points="{outer_poly}" fill="none" stroke="#1a1a3a" stroke-width="1"/>'
            f'{spokes}'
            f'<polygon points="{data_poly}" fill="rgba(100,181,246,0.2)" stroke="#64b5f6" stroke-width="2"/>'
            f'</svg>'
        )


def generate_report(
    scenario: dict[str, Any],
    scorecard: dict[str, Any],
    actions: list[dict[str, Any]] | None = None,
    ai_analysis: str = "",
    analyst_name: str = "SOC Analyst",
    open_browser: bool = False,
) -> Path:
    gen = ReportGenerator(analyst_name=analyst_name)
    path = gen.generate(scenario, scorecard, actions or [], ai_analysis)
    if open_browser:
        webbrowser.open(f"file://{path}")
    return path


if __name__ == "__main__":
    # Demo
    scenario = {
        "name": "Ransomware Attack - Lateral Spread", "severity": "critical",
        "category": "malware", "description": "Demo scenario",
        "attack_patterns": ["T1566","T1486","T1021"],
        "estimated_duration_minutes": 60,
        "objectives": ["Isolate systems","Identify patient zero","Restore from backup"],
        "stages": [{"stage":1,"name":"Initial Access","description":"Phishing email","duration_minutes":10},
                   {"stage":2,"name":"Encryption","description":"Files encrypted","duration_minutes":20}],
    }
    scorecard = {
        "run_id":"demo_001","grade":"B","total_score":72,"max_possible":100,
        "xp_earned":72,"difficulty":"medium",
        "radar_data":{"Detection Speed":65,"MITRE Coverage":80,"Containment":50,
                      "Policy Compliance":90,"Evidence Preservation":60,
                      "Communication":70,"Recovery Speed":55,"Efficiency":80},
        "dimensions":{
            "detection_speed":{"score":13,"max":20,"pct":65},
            "mitre_coverage":{"score":12,"max":15,"pct":80},
            "containment":{"score":8,"max":15,"pct":53},
            "policy_compliance":{"score":13,"max":15,"pct":87},
            "evidence":{"score":6,"max":10,"pct":60},
            "communication":{"score":7,"max":10,"pct":70},
            "recovery_speed":{"score":6,"max":10,"pct":60},
            "efficiency":{"score":4,"max":5,"pct":80},
        },
        "tips":["Improve detection speed — aim for under 60s","Practice containment before lateral movement"],
    }
    path = generate_report(scenario, scorecard, open_browser=True)
    print(f"Report generated: {path}")
