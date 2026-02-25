# Security Breach Simulator - New Features Batch

Progress update (as of 2026-02-25 09:45 Asia/Calcutta):

## New Features Commits (2026-02-25)

| Hash | Summary |
|------|---------|
| 84bca93 | feat: Add scoring and replay system |
| 6d7f285 | test: Add tests for scoring and replay systems |

### Features Added:
1. **Scoring System** (src/scoring.py)
   - ScoringEngine tracks player performance
   - Detection time, steps taken, policy compliance scoring
   - Grade calculation (A-F) based on total score
   - Save/load scores to .scores directory

2. **Replay System** (src/replay.py)
   - ReplayEngine for re-running scenarios with same seed
   - Compare runs for performance analysis
   - Save replays to .runs directory

3. **CLI Commands**
   - `breach score --last` - Show last run score
   - `breach score --run-id <id>` - Show specific run
   - `breach replay` - List recent replays
   - `breach replay --run-id <id>` - Show replay details

## Previous Batches

### Morning/Night Batch v2 (earlier):
| Hash | Summary |
|------|---------|
| df8fc9d | feat: Add category filtering and markdown export to generator |
| 57474f2 | test: Add pure unittest test suite |
| 3cdc6ea | feat(api): Add markdown export endpoint |

Current status:
- ✅ Scoring system implemented
- ✅ Replay system implemented  
- ✅ CLI commands added
- ✅ Tests passing (25 total)
- All commits pushed to origin/main

Next actions:
- None - batch complete.
