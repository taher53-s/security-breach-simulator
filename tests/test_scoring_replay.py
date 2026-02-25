"""
Tests for scoring and replay systems
"""
import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from scoring import ScoringEngine, ScenarioScore, load_score, list_scores
from replay import ReplayEngine, create_replay_from_score


class TestScoringEngine(unittest.TestCase):
    """Test scoring functionality"""
    
    def test_engine_initialization(self):
        """Test scoring engine initializes correctly"""
        engine = ScoringEngine(seed=42)
        self.assertIsNotNone(engine.run_id)
        self.assertEqual(engine.seed, 42)
    
    def test_start_scenario(self):
        """Test scenario start"""
        engine = ScoringEngine()
        engine.start_scenario("ransomware_attack", ["POL-001"])
        self.assertEqual(engine.scenario_id, "ransomware_attack")
    
    def test_record_action(self):
        """Test action recording"""
        engine = ScoringEngine()
        engine.start_scenario("test")
        engine.record_action("detect", "Found threat", 1)
        self.assertEqual(len(engine.actions), 1)
        self.assertEqual(engine.actions[0].action_type, "detect")
    
    def test_record_policy_compliance(self):
        """Test policy compliance tracking"""
        engine = ScoringEngine()
        engine.start_scenario("test")
        engine.record_policy_compliance(True)
        engine.record_policy_compliance(True)
        engine.record_policy_compliance(False)
        self.assertEqual(engine.policies_followed, 2)
        self.assertEqual(engine.policies_ignored, 1)
    
    def test_calculate_score(self):
        """Test score calculation"""
        engine = ScoringEngine(seed=42)
        engine.start_scenario("ransomware_attack", ["POL-001"])
        engine.record_action("detect", "Found threat", 2)
        engine.record_action("respond", "Started response", 2)
        engine.record_policy_compliance(True)
        
        score = engine.calculate_score()
        self.assertIsInstance(score, ScenarioScore)
        self.assertGreater(score.total_score, 0)
        self.assertIn(score.grade, ["A", "B", "C", "D", "F"])


class TestReplayEngine(unittest.TestCase):
    """Test replay functionality"""
    
    def test_create_replay(self):
        """Test creating a replay"""
        engine = ReplayEngine()
        replay = engine.create_replay("ransomware_attack", seed=42)
        self.assertIsNotNone(replay.run_id)
        self.assertEqual(replay.scenario_id, "ransomware_attack")
        self.assertEqual(replay.seed, 42)
    
    def test_list_runs(self):
        """Test listing replays"""
        engine = ReplayEngine()
        runs = engine.list_runs(limit=5)
        self.assertIsInstance(runs, list)


if __name__ == '__main__':
    unittest.main()
