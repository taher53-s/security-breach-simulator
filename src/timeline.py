"""
Timeline Visualization for Security Breach Simulator
Generates ASCII visualization of breach progression
"""
from __future__ import annotations

from typing import Any
from dataclasses import dataclass


SEVERITY_COLORS = {
    "critical": "🔴",
    "high": "🟠", 
    "medium": "🟡",
    "low": "🟢",
    "unknown": "⚪",
}

SEVERITY_LINES = {
    "critical": "=",
    "high": "-",
    "medium": "~",
    "low": "·",
    "unknown": " ",
}


@dataclass
class TimelineStage:
    """A stage in the timeline"""
    stage_num: int
    name: str
    description: str
    time_offset: str
    indicators: list[str]
    severity: str = "unknown"


class TimelineVisualizer:
    """Generates ASCII visualizations of breach timelines"""
    
    def __init__(self, scenario_id: str, seed: int | None = None) -> None:
        self.scenario_id = scenario_id
        self.seed = seed
        self.stages: list[TimelineStage] = []
        self._load_scenario()
    
    def _load_scenario(self) -> None:
        """Load scenario data"""
        from generators.sample_breach import BreachGenerator
        
        generator = BreachGenerator(seed=self.seed)
        result = generator.generate(self.scenario_id)
        
        for stage in result.get("timeline", []):
            self.stages.append(TimelineStage(
                stage_num=stage.get("stage", 1),
                name=stage.get("name", "Unknown"),
                description=stage.get("description", ""),
                time_offset=stage.get("time_offset", "+0m"),
                indicators=stage.get("indicators", [])[:3],
                severity=result["scenario"].get("severity", "unknown")
            ))
    
    def render(self) -> str:
        """Render full timeline visualization"""
        output = []
        
        # Header
        output.append(self._render_header())
        output.append("")
        
        # Timeline
        for i, stage in enumerate(self.stages):
            output.append(self._render_stage(stage, is_last=i == len(self.stages) - 1))
            output.append("")
        
        # Footer
        output.append(self._render_footer())
        
        return "\n".join(output)
    
    def _render_header(self) -> str:
        """Render the header"""
        severity = self.stages[0].severity if self.stages else "unknown"
        icon = SEVERITY_COLORS.get(severity, "⚪")
        
        lines = SEVERITY_LINES.get(severity, "=")
        
        header = [
            f"{icon} SECURITY BREACH TIMELINE",
            f"Scenario: {self.scenario_id}",
            lines * 40,
        ]
        return "\n".join(header)
    
    def _render_stage(self, stage: TimelineStage, is_last: bool) -> str:
        """Render a single stage"""
        connector = "└─ " if is_last else "├─ "
        
        lines = [
            f"STAGE {stage.stage_num}: {stage.name} [{stage.time_offset}]",
            f"{connector}{stage.description[:60]}..." if len(stage.description) > 60 else f"{connector}{stage.description}",
        ]
        
        if stage.indicators:
            lines.append("")
            lines.append(f"{connector}⚠ Indicators:")
            for ind in stage.indicators:
                ind_connector = "    └─ " if ind == stage.indicators[-1] else "    ├─ "
                lines.append(f"{ind_connector}{ind}")
        
        return "\n".join(lines)
    
    def _render_footer(self) -> str:
        """Render footer"""
        return "─" * 40 + "\n" + "🏁 BREACH COMPLETE"
    
    def render_compact(self) -> str:
        """Render compact single-line timeline"""
        parts = []
        for stage in self.stages:
            icon = SEVERITY_COLORS.get(stage.severity, "⚪")
            parts.append(f"{icon} {stage.stage_num}:{stage.name[:15]}")
        return " → ".join(parts)
    
    def render_summary(self) -> str:
        """Render summary view"""
        lines = [
            "=" * 40,
            f"📊 TIMELINE SUMMARY: {self.scenario_id}",
            "=" * 40,
            f"Total Stages: {len(self.stages)}",
            f"Severity: {self.stages[0].severity.upper() if self.stages else 'UNKNOWN'}",
            "",
            "Stages:",
        ]
        
        for stage in self.stages:
            icon = SEVERITY_COLORS.get(stage.severity, "⚪")
            lines.append(f"  {icon} [{stage.time_offset}] {stage.name}")
        
        lines.append("=" * 40)
        
        return "\n".join(lines)


def visualize(scenario_id: str, style: str = "full", seed: int | None = None) -> str:
    """Main function to visualize a scenario timeline"""
    viz = TimelineVisualizer(scenario_id, seed)
    
    if style == "compact":
        return viz.render_compact()
    elif style == "summary":
        return viz.render_summary()
    else:
        return viz.render()


if __name__ == "__main__":
    # Demo visualization
    print(visualize("ransomware_attack", seed=42))
    print("\n" + "=" * 40 + "\n")
    print(visualize("ransomware_attack", style="summary", seed=42))
