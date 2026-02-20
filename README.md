# Security Breach Simulator

A tool to practice handling cyber attacks through realistic breach scenarios.

## Installation

```bash
pip install -e .
```

## Usage

### List scenarios
```bash
breach list
```

### Generate breach
```bash
breach generate ransomware_attack
```

### Get summary
```bash
breach summary phishing_lateral_movement
```

## API Server

```bash
cd backend/api
pip install -r requirements.txt
uvicorn app:app --reload
```

## Development

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=src tests/
```

## Scenarios

- phishing_lateral_movement
- supply_chain_compromise
- insider_threat_data_exfil
- ransomware_attack
- credential_theft_attack
- ddos_attack
- zero_day_exploit
