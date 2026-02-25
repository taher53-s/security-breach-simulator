"""
Difficulty Presets for Security Breach Simulator
Defines easy, medium, and hard configurations for scenarios.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class DifficultyPreset:
    """Configuration for a difficulty level"""
    name: str
    display_name: str
    
    # Time multipliers (1.0 = normal, 2.0 = twice as long, etc.)
    time_multiplier: float
    
    # Hint availability
    hints_enabled: bool
    max_hints: int
    
    # Policy strictness (1.0 = strict, 0.5 = lenient)
    policy_strictness: float
    
    # Scoring modifiers
    score_multiplier: float
    
    # Automation level (0 = manual, 1 = full hints)
    auto_detect_enabled: bool
    
    # Description shown to players
    description: str


# Define difficulty presets
DIFFICULTY_EASY = DifficultyPreset(
    name="easy",
    display_name="Easy",
    time_multiplier=2.0,
    hints_enabled=True,
    max_hints=5,
    policy_strictness=0.5,
    score_multiplier=1.0,
    auto_detect_enabled=True,
    description="Plenty of time, hints available, lenient policy enforcement"
)

DIFFICULTY_MEDIUM = DifficultyPreset(
    name="medium",
    display_name="Medium",
    time_multiplier=1.0,
    hints_enabled=True,
    max_hints=2,
    policy_strictness=0.75,
    score_multiplier=1.0,
    auto_detect_enabled=False,
    description="Standard time limits, limited hints, moderate policy enforcement"
)

DIFFICULTY_HARD = DifficultyPreset(
    name="hard",
    display_name="Hard",
    time_multiplier=0.5,
    hints_enabled=False,
    max_hints=0,
    policy_strictness=1.0,
    score_multiplier=1.5,
    auto_detect_enabled=False,
    description="Half the time, no hints, strict policy enforcement, 1.5x score"
)

DIFFICULTY_EXPERT = DifficultyPreset(
    name="expert",
    display_name="Expert",
    time_multiplier=0.25,
    hints_enabled=False,
    max_hints=0,
    policy_strictness=1.5,
    score_multiplier=2.0,
    auto_detect_enabled=False,
    description="Quarter time, no hints, strictest policy, 2x score"
)


# Preset lookup
DIFFICULTY_PRESETS: dict[str, DifficultyPreset] = {
    "easy": DIFFICULTY_EASY,
    "medium": DIFFICULTY_MEDIUM,
    "hard": DIFFICULTY_HARD,
    "expert": DIFFICULTY_EXPERT,
}


def get_difficulty(name: str) -> DifficultyPreset:
    """Get difficulty preset by name, defaults to medium"""
    return DIFFICULTY_PRESETS.get(name.lower(), DIFFICULTY_MEDIUM)


def list_difficulties() -> list[dict[str, Any]]:
    """List all available difficulty presets"""
    return [
        {
            "name": preset.name,
            "display_name": preset.display_name,
            "description": preset.description,
            "score_multiplier": preset.score_multiplier,
            "time_multiplier": preset.time_multiplier,
        }
        for preset in DIFFICULTY_PRESETS.values()
    ]


def apply_difficulty(score: int, difficulty: str) -> int:
    """Apply difficulty modifier to a score"""
    preset = get_difficulty(difficulty)
    return int(score * preset.score_multiplier)


class ScenarioTimer:
    """Timer that respects difficulty settings"""
    
    def __init__(self, difficulty: str = "medium") -> None:
        self.preset = get_difficulty(difficulty)
        self.base_limit: float = 900.0  # 15 minutes base
        self._start_time: float | None = None
    
    @property
    def time_limit(self) -> float:
        """Get time limit in seconds based on difficulty"""
        return self.base_limit * self.preset.time_multiplier
    
    def start(self) -> None:
        """Start the timer"""
        import time
        self._start_time = time.time()
    
    def elapsed(self) -> float:
        """Get elapsed time"""
        import time
        if self._start_time is None:
            return 0.0
        return time.time() - self._start_time
    
    def remaining(self) -> float:
        """Get remaining time"""
        return max(0.0, self.time_limit - self.elapsed())
    
    def is_expired(self) -> bool:
        """Check if time has expired"""
        return self.elapsed() > self.time_limit


if __name__ == "__main__":
    # Demo difficulty system
    print("Available Difficulty Presets:")
    print("-" * 50)
    for diff in list_difficulties():
        print(f"\n{diff['display_name']} ({diff['name']}):")
        print(f"  {diff['description']}")
        print(f"  Score Multiplier: {diff['score_multiplier']}x")
        print(f"  Time Multiplier: {diff['time_multiplier']}x")
    
    # Demo timer
    print("\n" + "=" * 50)
    print("Timer Demo (Hard difficulty):")
    timer = ScenarioTimer("hard")
    print(f"  Time limit: {timer.time_limit} seconds")
