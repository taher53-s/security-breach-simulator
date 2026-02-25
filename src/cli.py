"""
CLI for Security Breach Simulator
Provides command-line interface for all features.
"""
from __future__ import annotations

import sys
import argparse
import json
from pathlib import Path

# Add src to path for imports
ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR / "src"))

from generators.sample_breach import BreachGenerator
from scoring import ScoringEngine, load_score, list_scores
from replay import ReplayEngine
from difficulty import list_difficulties, get_difficulty
from stats import StatsDashboard
from audit_log import AuditLogger


def cmd_list(args):
    """List all scenarios"""
    gen = BreachGenerator(seed=args.seed)
    scenarios = gen.list_scenarios(severity=args.severity, category=args.category)
    
    print(f"\n📋 Available Scenarios ({len(scenarios)})")
    print("-" * 60)
    for s in scenarios:
        severity = s.get('severity', 'N/A')
        category = s.get('category', 'N/A')
        name = s.get('name', s.get('title', 'Unknown'))
        print(f"  {s['id']:30} [{severity:8}] {category}")
    
    if args.json:
        print(json.dumps([{'id': s['id'], 'name': s.get('name', ''), 
                          'severity': s.get('severity'), 
                          'category': s.get('category')} for s in scenarios], indent=2))


def cmd_generate(args):
    """Generate a breach scenario"""
    gen = BreachGenerator(seed=args.seed)
    
    if args.scenario:
        result = gen.generate(args.scenario)
    else:
        result = gen.generate_random(severity=args.severity)
    
    scenario_name = args.scenario or result.get('scenario', {}).get('name', 'Random')
    print(f"\n🎯 Generated: {scenario_name}")
    print("-" * 60)
    print(f"Name: {scenario_name}")
    print(f"Timeline events: {len(result.get('timeline', []))}")
    print(f"Duration: {result.get('total_duration_minutes', 'N/A')} minutes")
    
    if args.verbose:
        print("\n📝 Timeline:")
        for event in result.get('timeline', [])[:5]:
            print(f"  [{event.get('stage', '?')}] {event.get('event_type', 'event')}: {event.get('description', '')[:60]}")


def cmd_score(args):
    """Show scores"""
    if args.list:
        scores = list_scores(limit=args.limit)
        print("\n🏆 Recent Scores")
        print("-" * 60)
        for s in scores:
            print(f"  {s['run_id']}: {s['total_score']} pts ({s['grade']}) - {s['scenario_id']}")
        return
    
    if args.run_id:
        score = load_score(args.run_id)
        if score:
            print(f"\n📊 Score: {score.total_score}/100 ({score.grade})")
            print("-" * 40)
            print(f"  Detection: {score.detection_score}/40")
            print(f"  Compliance: {score.compliance_score}/40")
            print(f"  Efficiency: {score.total_score - score.detection_score - score.compliance_score}/20")
            print(f"\n  Detection Time: {score.detection_time_seconds or 'N/A'}s")
            print(f"  Total Actions: {score.total_actions}")
            print(f"  Policies Followed: {score.policies_followed}/{score.policies_followed + score.policies_ignored}")
        else:
            print(f"Score not found: {args.run_id}")
    else:
        # Show last score
        scores = list_scores(limit=1)
        if scores:
            print(f"\n📊 Latest Score: {scores[0]['total_score']} pts ({scores[0]['grade']})")
            print(f"   Run: {scores[0]['run_id']} | Scenario: {scores[0]['scenario_id']}")
        else:
            print("No scores found")


def cmd_replay(args):
    """Manage replays"""
    engine = ReplayEngine()
    
    if args.list:
        runs = engine.list_runs(limit=args.limit)
        print("\n🔄 Recent Replays")
        print("-" * 60)
        for r in runs:
            print(f"  {r['run_id']}: {r['scenario_id']} (seed={r['seed']})")
        return
    
    if args.compare and len(args.compare) == 2:
        result = engine.compare_runs(args.compare[0], args.compare[1])
        if result:
            print("\n📊 Run Comparison")
            print("-" * 60)
            print(f"Run 1: {result['run1']['total_score']} pts ({result['run1']['grade']})")
            print(f"Run 2: {result['run2']['total_score']} pts ({result['run2']['grade']})")
            print(f"\nScore Diff: {result['comparison']['score_diff']}")
        else:
            print("Could not compare runs")
        return
    
    print("Use --list or --compare")


def cmd_difficulty(args):
    """Show difficulty presets"""
    difficulties = list_difficulties()
    
    print("\n⚡ Difficulty Presets")
    print("-" * 60)
    for d in difficulties:
        print(f"\n{d['display_name']} ({d['name']}):")
        print(f"  {d['description']}")
        print(f"  Score: {d['score_multiplier']}x | Time: {d['time_multiplier']}x")


def cmd_stats(args):
    """Show statistics dashboard"""
    dashboard = StatsDashboard()
    
    stats = dashboard.get_total_stats()
    print("\n📊 Statistics Dashboard")
    print("=" * 50)
    print(f"Total Runs: {stats['total_runs']}")
    print(f"Average Score: {stats['average_score']}")
    print(f"Best Score: {stats.get('best_score', 'N/A')}")
    print(f"Completion Rate: {stats.get('completion_rate', 0)}%")
    
    if args.leaderboard:
        print("\n🏆 Leaderboard")
        print("-" * 40)
        for entry in dashboard.get_leaderboard(5):
            print(f"  #{entry['rank']} {entry['scenario_id']}: {entry['score']} pts")
    
    if args.trends:
        trends = dashboard.get_trends(days=7)
        print("\n📈 Trends (Last 7 Days)")
        print("-" * 40)
        for day in trends.get('daily_data', []):
            print(f"  {day['date']}: {day['avg_score']} avg ({day['runs']} runs)")


def cmd_serve(args):
    """Start API server"""
    import uvicorn
    print(f"\n🚀 Starting API server on {args.host}:{args.port}")
    uvicorn.run("backend.api.app:app", host=args.host, port=args.port, reload=args.reload)


def main():
    parser = argparse.ArgumentParser(
        description="Security Breach Simulator CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List scenarios")
    list_parser.add_argument("--severity", choices=["critical", "high", "medium", "low"])
    list_parser.add_argument("--category")
    list_parser.add_argument("--seed", type=int)
    list_parser.add_argument("--json", action="store_true")
    list_parser.set_defaults(func=cmd_list)
    
    # Generate command
    gen_parser = subparsers.add_parser("generate", help="Generate scenario")
    gen_parser.add_argument("--scenario", help="Scenario ID")
    gen_parser.add_argument("--severity", choices=["critical", "high", "medium", "low"])
    gen_parser.add_argument("--seed", type=int)
    gen_parser.add_argument("-v", "--verbose", action="store_true")
    gen_parser.set_defaults(func=cmd_generate)
    
    # Score command
    score_parser = subparsers.add_parser("score", help="Show scores")
    score_parser.add_argument("--run-id", help="Specific run ID")
    score_parser.add_argument("--list", action="store_true", help="List recent scores")
    score_parser.add_argument("--limit", type=int, default=10)
    score_parser.add_argument("--json", action="store_true")
    score_parser.add_argument("-v", "--verbose", action="store_true")
    score_parser.set_defaults(func=cmd_score)
    
    # Replay command
    replay_parser = subparsers.add_parser("replay", help="Manage replays")
    replay_parser.add_argument("--list", action="store_true")
    replay_parser.add_argument("--compare", nargs=2, help="Compare two runs")
    replay_parser.add_argument("--limit", type=int, default=10)
    replay_parser.set_defaults(func=cmd_replay)
    
    # Difficulty command
    diff_parser = subparsers.add_parser("difficulty", help="Show difficulty presets")
    diff_parser.set_defaults(func=cmd_difficulty)
    
    # Stats command
    stats_parser = subparsers.add_parser("stats", help="Show statistics")
    stats_parser.add_argument("--leaderboard", action="store_true")
    stats_parser.add_argument("--trends", action="store_true")
    stats_parser.set_defaults(func=cmd_stats)
    
    # Serve command
    serve_parser = subparsers.add_parser("serve", help="Start API server")
    serve_parser.add_argument("--host", default="0.0.0.0")
    serve_parser.add_argument("--port", type=int, default=8000)
    serve_parser.add_argument("--reload", action="store_true")
    serve_parser.set_defaults(func=cmd_serve)
    
    args = parser.parse_args()
    
    if args.command is None:
        parser.print_help()
        return
    
    args.func(args)


if __name__ == "__main__":
    main()
