"""
Security Breach Simulator
A tool to practice handling cyber attacks through realistic breach scenarios.

Quick Start:
    breach list                    # List all scenarios
    breach generate --scenario ransomware_attack  # Generate a scenario
    breach serve                   # Start API server
    breach stats                   # Show statistics

For more commands:
    breach --help
"""
from __future__ import annotations

__version__ = "0.3.0"
__author__ = "Security Team"

# Core exports
from .scoring import ScoringEngine, load_score, list_scores
from .replay import ReplayEngine, create_replay_from_score
from .difficulty import get_difficulty, list_difficulties, ScenarioTimer
from .stats import StatsDashboard
from .audit_log import AuditLogger
from .config import load_config, get_config
from .exceptions import (
    BreachSimulatorError,
    ScenarioNotFoundError,
    InvalidScenarioError,
    PolicyNotFoundError,
    ConfigurationError,
)

__all__ = [
    # Version
    "__version__",
    
    # Core
    "ScoringEngine",
    "ReplayEngine",
    "AuditLogger",
    "StatsDashboard",
    "ScenarioTimer",
    
    # Config
    "load_config",
    "get_config",
    
    # Utilities
    "load_score",
    "list_scores",
    "get_difficulty",
    "list_difficulties",
    "create_replay_from_score",
    
    # Exceptions
    "BreachSimulatorError",
    "ScenarioNotFoundError",
    "InvalidScenarioError",
    "PolicyNotFoundError",
    "ConfigurationError",
]
