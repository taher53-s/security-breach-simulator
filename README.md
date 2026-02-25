# Security Breach Simulator

<p align="center">
  <img src="https://img.shields.io/badge/version-1.0.0-blue" alt="Version">
  <img src="https://img.shields.io/badge/python-3.11%2B-green" alt="Python">
  <img src="https://img.shields.io/badge/license-MIT-orange" alt="License">
  <img src="https://img.shields.io/badge/status-production--ready-green" alt="Status">
</p>

A professional-grade security training tool for practicing incident response through realistic cyber breach scenarios.

## Features

### Core Features
- **7 Scenario Types**: Ransomware, Phishing, DDoS, Insider Threat, Credential Theft, Supply Chain, Zero-Day
- **Category Filtering**: Filter scenarios by type (network, social, physical, etc.)
- **Seeded Generation**: Reproducible scenarios with deterministic seeds
- **Markdown Export**: Export scenarios for documentation

### Scoring & Analytics
- **Comprehensive Scoring**: Detection time, action efficiency, policy compliance
- **Grade System**: A-F grading based on performance
- **Stats Dashboard**: Track progress over time
- **Leaderboard**: Compare performance across runs
- **Trend Analysis**: View performance over 7-day periods

### Difficulty & Audit
- **4 Difficulty Levels**: Easy, Medium, Hard, Expert
- **Time Limits**: Adjust based on difficulty
- **Score Multipliers**: Up to 2x on Expert
- **Full Audit Logging**: JSONL format for compliance

### Professional Grade
- **Docker Support**: Containerized deployment
- **REST API**: FastAPI backend
- **CI/CD**: GitHub Actions workflow
- **Type Hints**: Full Python type annotations
- **Error Handling**: Custom exceptions throughout

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/taher53-s/security-breach-simulator.git
cd security-breach-simulator

# Install dependencies
pip install -e .

# Or install with dev dependencies
pip install -e ".[dev]"
```

### CLI Usage

```bash
# List all scenarios
breach list

# Generate a specific scenario
breach generate --scenario ransomware_attack

# Generate random scenario
breach generate --severity high

# Show scores
breach score --list

# Show statistics
breach stats --leaderboard

# Show difficulty presets
breach difficulty

# Start API server
breach serve --port 8000
```

### API Server

```bash
# Start the API server
uvicorn backend.api.app:app --reload

# Or use Docker
docker-compose up
```

### API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /health` | Health check |
| `GET /metrics` | Basic metrics |
| `GET /scenarios` | List scenarios |
| `GET /scenarios/{id}` | Get scenario details |
| `GET /scenarios/{id}/export?format=markdown` | Export scenario |
| `GET /policies` | List policies |
| `GET /dashboard/stats` | Dashboard statistics |

## Configuration

Copy `config.example.yaml` to `config.yaml` and customize:

```yaml
app:
  name: "Security Breach Simulator"
  version: "0.3.0"
  debug: false

scenarios:
  default_difficulty: "medium"
  hints_enabled: true
  max_hints: 3

server:
  host: "0.0.0.0"
  port: 8000
```

Or use environment variables:

```bash
export BREACH_DIFFICULTY=hard
export BREACH_PORT=8080
export BREACH_DEBUG=true
```

## Development

```bash
# Run tests
python -m unittest discover tests

# Run specific test
python -m unittest tests.test_smoke_unittest -v

# Run with pytest (with coverage)
pytest tests/ --cov=src --cov-report=html

# Lint code
ruff check src/ tests/
```

## Docker

```bash
# Build image
docker build -t security-breach-simulator .

# Run container
docker run -p 8000:8000 security-breach-simulator

# Or use docker-compose
docker-compose up
```

## Project Structure

```
security-breach-simulator/
├── src/                    # Source code
│   ├── __init__.py         # Package exports
│   ├── cli.py              # CLI interface
│   ├── config.py           # Configuration
│   ├── difficulty.py       # Difficulty presets
│   ├── scoring.py          # Scoring system
│   ├── replay.py           # Replay system
│   ├── stats.py            # Statistics
│   ├── audit_log.py        # Audit logging
│   ├── exceptions.py       # Custom exceptions
│   └── generators/         # Scenario generators
├── backend/
│   └── api/
│       └── app.py          # FastAPI application
├── tests/                  # Test suite
├── docs/                   # Documentation
├── .github/
│   └── workflows/          # CI/CD
├── Dockerfile
├── docker-compose.yml
├── config.example.yaml
└── setup.py
```

## Scoring System

| Component | Max Points | Criteria |
|-----------|-------------|----------|
| Detection | 40 | Speed of threat detection |
| Compliance | 40 | Following security policies |
| Efficiency | 20 | Minimal actions to resolve |

### Grades
- **A**: 90-100 points
- **B**: 80-89 points  
- **C**: 70-79 points
- **D**: 60-69 points
- **F**: Below 60 points

## Difficulty Presets

| Level | Time | Hints | Score Multiplier |
|-------|------|-------|------------------|
| Easy | 2x | 5 | 1.0x |
| Medium | 1x | 2 | 1.0x |
| Hard | 0.5x | 0 | 1.5x |
| Expert | 0.25x | 0 | 2.0x |

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Ensure all tests pass
5. Submit a pull request

## License

MIT License - See LICENSE file for details

## Support

- Report bugs: GitHub Issues
- Source code: GitHub Repository
- Documentation: Project Wiki
