"""
Configuration Management for Security Breach Simulator
Loads settings from config.yaml with environment variable overrides.
"""
from __future__ import annotations

import os
import yaml
from pathlib import Path
from typing import Any
from dataclasses import dataclass, field


# Default configuration
DEFAULT_CONFIG = {
    "app": {
        "name": "Security Breach Simulator",
        "version": "1.0.0",
        "debug": False
    },
    "server": {
        "host": "0.0.0.0",
        "port": 8000,
        "reload": False
    },
    "scenarios": {
        "default_difficulty": "medium",
        "hints_enabled": True,
        "max_hints": 3,
        "time_limit": 900
    },
    "scoring": {
        "multipliers": {
            "easy": 1.0,
            "medium": 1.0,
            "hard": 1.5,
            "expert": 2.0
        },
        "thresholds": {
            "A": 90,
            "B": 80,
            "C": 70,
            "D": 60
        }
    },
    "logging": {
        "audit_dir": ".audit",
        "scores_dir": ".scores",
        "runs_dir": ".runs",
        "level": "INFO"
    },
    "api": {
        "cors_origins": "*",
        "rate_limit": {
            "enabled": False,
            "requests_per_minute": 60
        },
        "cache_ttl": 300
    }
}


@dataclass
class Config:
    """Application configuration"""
    app: dict[str, Any] = field(default_factory=lambda: DEFAULT_CONFIG["app"])
    server: dict[str, Any] = field(default_factory=lambda: DEFAULT_CONFIG["server"])
    scenarios: dict[str, Any] = field(default_factory=lambda: DEFAULT_CONFIG["scenarios"])
    scoring: dict[str, Any] = field(default_factory=lambda: DEFAULT_CONFIG["scoring"])
    logging: dict[str, Any] = field(default_factory=lambda: DEFAULT_CONFIG["logging"])
    api: dict[str, Any] = field(default_factory=lambda: DEFAULT_CONFIG["api"])


def load_config(config_path: str | Path | None = None) -> Config:
    """Load configuration from file with env var overrides"""
    config_data = DEFAULT_CONFIG.copy()
    
    # Load from file if provided
    if config_path is None:
        config_path = os.environ.get("BREACH_CONFIG", "config.yaml")
    
    path = Path(config_path)
    if path.exists():
        with open(path) as f:
            file_config = yaml.safe_load(f)
            if file_config:
                _deep_merge(config_data, file_config)
    
    # Environment variable overrides
    _apply_env_overrides(config_data)
    
    return Config(**config_data)


def _deep_merge(base: dict, override: dict) -> None:
    """Deep merge override into base"""
    for key, value in override.items():
        if key in base and isinstance(base[key], dict) and isinstance(value, dict):
            _deep_merge(base[key], value)
        else:
            base[key] = value


def _apply_env_overrides(config: dict) -> None:
    """Apply environment variable overrides"""
    # Server settings
    if host := os.environ.get("BREACH_HOST"):
        config["server"]["host"] = host
    if port := os.environ.get("BREACH_PORT"):
        config["server"]["port"] = int(port)
    
    # Debug mode
    if debug := os.environ.get("BREACH_DEBUG"):
        config["app"]["debug"] = debug.lower() in ("true", "1", "yes")
    
    # Difficulty
    if diff := os.environ.get("BREACH_DIFFICULTY"):
        config["scenarios"]["default_difficulty"] = diff
    
    # Directories
    if audit := os.environ.get("BREACH_AUDIT_DIR"):
        config["logging"]["audit_dir"] = audit
    if scores := os.environ.get("BREACH_SCORES_DIR"):
        config["logging"]["scores_dir"] = scores


# Global config instance
_config: Config | None = None


def get_config() -> Config:
    """Get global config instance (lazy loaded)"""
    global _config
    if _config is None:
        _config = load_config()
    return _config


def reload_config() -> Config:
    """Force reload configuration"""
    global _config
    _config = load_config()
    return _config


if __name__ == "__main__":
    # Print current configuration
    import json
    config = load_config()
    print(json.dumps({
        "app": config.app,
        "server": config.server,
        "scenarios": config.scenarios,
    }, indent=2))
