"""
Test suite for difficulty presets
"""
import unittest
from src.difficulty import (
    get_difficulty, 
    list_difficulties, 
    apply_difficulty,
    ScenarioTimer,
    DIFFICULTY_PRESETS
)


class TestDifficultyPresets(unittest.TestCase):
    """Test difficulty preset configurations"""
    
    def test_get_easy_difficulty(self):
        preset = get_difficulty("easy")
        self.assertEqual(preset.name, "easy")
        self.assertEqual(preset.time_multiplier, 2.0)
        self.assertTrue(preset.hints_enabled)
        self.assertEqual(preset.max_hints, 5)
    
    def test_get_medium_difficulty(self):
        preset = get_difficulty("medium")
        self.assertEqual(preset.name, "medium")
        self.assertEqual(preset.time_multiplier, 1.0)
        self.assertEqual(preset.max_hints, 2)
    
    def test_get_hard_difficulty(self):
        preset = get_difficulty("hard")
        self.assertEqual(preset.name, "hard")
        self.assertEqual(preset.time_multiplier, 0.5)
        self.assertFalse(preset.hints_enabled)
        self.assertEqual(preset.score_multiplier, 1.5)
    
    def test_get_expert_difficulty(self):
        preset = get_difficulty("expert")
        self.assertEqual(preset.name, "expert")
        self.assertEqual(preset.time_multiplier, 0.25)
        self.assertEqual(preset.score_multiplier, 2.0)
    
    def test_default_difficulty(self):
        preset = get_difficulty("invalid")
        self.assertEqual(preset.name, "medium")
    
    def test_list_difficulties(self):
        difficulties = list_difficulties()
        self.assertEqual(len(difficulties), 4)
        names = [d['name'] for d in difficulties]
        self.assertIn('easy', names)
        self.assertIn('medium', names)
        self.assertIn('hard', names)
        self.assertIn('expert', names)


class TestApplyDifficulty(unittest.TestCase):
    """Test score application with difficulty modifiers"""
    
    def test_easy_score(self):
        score = apply_difficulty(100, "easy")
        self.assertEqual(score, 100)
    
    def test_medium_score(self):
        score = apply_difficulty(100, "medium")
        self.assertEqual(score, 100)
    
    def test_hard_score(self):
        score = apply_difficulty(100, "hard")
        self.assertEqual(score, 150)
    
    def test_expert_score(self):
        score = apply_difficulty(100, "expert")
        self.assertEqual(score, 200)


class TestScenarioTimer(unittest.TestCase):
    """Test scenario timer with difficulty settings"""
    
    def test_easy_timer(self):
        timer = ScenarioTimer("easy")
        self.assertEqual(timer.time_limit, 1800.0)  # 15 * 2
    
    def test_medium_timer(self):
        timer = ScenarioTimer("medium")
        self.assertEqual(timer.time_limit, 900.0)  # 15 * 1
    
    def test_hard_timer(self):
        timer = ScenarioTimer("hard")
        self.assertEqual(timer.time_limit, 450.0)  # 15 * 0.5
    
    def test_expert_timer(self):
        timer = ScenarioTimer("expert")
        self.assertEqual(timer.time_limit, 225.0)  # 15 * 0.25
    
    def test_timer_elapsed(self):
        timer = ScenarioTimer("medium")
        timer.start()
        import time
        time.sleep(0.01)
        self.assertGreater(timer.elapsed(), 0)
    
    def test_timer_remaining(self):
        timer = ScenarioTimer("medium")
        timer.start()
        remaining = timer.remaining()
        self.assertLess(remaining, 900.0)


if __name__ == "__main__":
    unittest.main()
