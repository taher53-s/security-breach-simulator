# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-02-25

### Added
- **7 Scenario Types**: Ransomware, Phishing, DDoS, Insider Threat, Credential Theft, Supply Chain, Zero-Day
- **Comprehensive Scoring System**: Detection time (40pts), policy compliance (40pts), efficiency (20pts)
- **Grade System**: A-F grading based on performance (90+/80+/70+/60+)
- **Replay System**: Re-run scenarios with same parameters, compare runs
- **4 Difficulty Presets**: Easy (2x time, hints), Medium (default), Hard (0.5x time, 1.5x score), Expert (0.25x time, 2x score)
- **Full Audit Logging**: JSONL format for compliance tracking
- **Stats Dashboard**: Overall performance, trends, leaderboard
- **Complete CLI**: `list`, `generate`, `score`, `replay`, `stats`, `difficulty`, `serve`
- **FastAPI REST Server**: Health check, metrics, scenarios, policies, export endpoints
- **Docker Support**: Dockerfile and docker-compose.yml
- **GitHub Actions CI/CD**: Automated testing and linting
- **Configuration Management**: YAML config with env var overrides
- **Custom Exceptions**: Full error handling throughout
- **Professional Documentation**: Complete README, PROJECT_PLAN.md

### Changed
- Upgraded from 0.3.0 to 1.0.0
- Improved test coverage (44 tests passing)
- Better import handling for package usage

### Fixed
- Scenario field standardization (id, name, stages)
- Difficulty value validation (beginner/intermediate/expert)
- API Query object handling for direct function calls
- Test expectations updated for actual data structures

## [0.3.0] - 2026-02-24

### Added
- Category filtering
- Markdown export
- Initial test suite

### Fixed
- Policy catalog loading
- Streamer stage support

## [0.2.0] - 2026-02-23

### Added
- Basic scenario generation
- Seeded random generation

## [0.1.0] - 2026-02-21

### Added
- Initial release
- Basic scenario templates
- Simple CLI
