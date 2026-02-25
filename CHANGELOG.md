# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-02-25

### Added
- **Complete CLI**: `list`, `generate`, `score`, `replay`, `stats`, `difficulty`, `serve`
- **Full Exception Handling**: Custom exceptions throughout
- **Complete Package Structure**: Proper __init__.py exports
- **Final Documentation**: Complete README, PROJECT_PLAN.md

### Changed
- Version bumped to 1.0.0

## [0.9.0] - 2026-02-25

### Added
- Pre-release fixes and final updates

## [0.8.0] - 2026-02-25

### Added
- **Docker Support**: Dockerfile and docker-compose.yml
- **GitHub Actions CI/CD**: Automated testing and linting
- **Difficulty Tests**: Comprehensive test coverage

## [0.7.0] - 2026-02-25

### Added
- **Complete CLI**: Full command-line interface
- **Custom Exceptions**: Full error handling
- **Package Structure**: Proper imports and exports

## [0.6.0] - 2026-02-25

### Added
- **Configuration Management**: YAML config with env var overrides
- **Config Tests**: Configuration testing

## [0.5.0] - 2026-02-25

### Added
- **4 Difficulty Presets**: Easy, Medium, Hard, Expert
- **Timer System**: Respects difficulty settings
- **Audit Logging**: Full JSONL format for compliance

## [0.4.0] - 2026-02-25

### Added
- **Scoring System**: Detection (40pts), compliance (40pts), efficiency (20pts)
- **Grade System**: A-F grading
- **Replay System**: Re-run scenarios, compare runs

## [0.3.0] - 2026-02-24

### Added
- **Category Filtering**: Filter scenarios by type
- **Markdown Export**: Export scenarios for documentation
- **Pure unittest Tests**: No pytest dependency

### Fixed
- Scenario field standardization

## [0.2.0] - 2026-02-23

### Added
- **API v0.2.0**: New endpoints
- **Pagination Support**: Scenarios and policies
- **Enhanced Validation**: Scenario tests

## [0.1.0] - 2026-02-21

### Added
- Initial release
- 7 Scenario types
- Basic CLI
- REST API
- Detection streamer
