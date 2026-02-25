"""
Pure unittest tests for BreachGenerator - no pytest dependency
"""
import unittest
import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from generators.sample_breach import BreachGenerator


class TestGeneratorFilters(unittest.TestCase):
    """Test filtering functionality"""
    
    def setUp(self):
        self.gen = BreachGenerator()
    
    def test_list_scenarios_returns_list(self):
        """Test list_scenarios returns a list"""
        result = self.gen.list_scenarios()
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)
    
    def test_list_scenarios_filter_by_severity(self):
        """Test filtering by severity"""
        critical = self.gen.list_scenarios(severity="critical")
        self.assertTrue(all(s['severity'].lower() == 'critical' for s in critical))
    
    def test_list_scenarios_filter_by_category(self):
        """Test filtering by category"""
        malware = self.gen.list_scenarios(category="malware")
        self.assertTrue(all(s['category'].lower() == 'malware' for s in malware))
    
    def test_filter_by_category(self):
        """Test filter_by_category method"""
        result = self.gen.filter_by_category("phishing")
        self.assertIsInstance(result, list)
    
    def test_seeded_generator_is_deterministic(self):
        """Test that seeded generator produces same results"""
        gen1 = BreachGenerator(seed=42)
        gen2 = BreachGenerator(seed=42)
        
        r1 = gen1.generate_random()
        r2 = gen2.generate_random()
        
        self.assertEqual(r1['scenario']['scenario_id'], r2['scenario']['scenario_id'])


class TestGeneratorExport(unittest.TestCase):
    """Test export functionality"""
    
    def setUp(self):
        self.gen = BreachGenerator()
    
    def test_export_to_markdown_returns_string(self):
        """Test markdown export returns a string"""
        result = self.gen.export_to_markdown("ransomware_attack")
        self.assertIsInstance(result, str)
        self.assertIn("# Ransomware Attack", result)
    
    def test_export_to_markdown_contains_sections(self):
        """Test markdown has required sections"""
        result = self.gen.export_to_markdown("ransomware_attack")
        self.assertIn("## Threat Overview", result)
        self.assertIn("## Timeline of Events", result)
        self.assertIn("## Objectives", result)


class TestGeneratorScenarios(unittest.TestCase):
    """Test scenario generation"""
    
    def setUp(self):
        self.gen = BreachGenerator()
    
    def test_generate_known_scenario(self):
        """Test generating a known scenario"""
        result = self.gen.generate("ransomware_attack")
        self.assertIn("scenario", result)
        self.assertIn("timeline", result)
    
    def test_generate_random_scenario(self):
        """Test random scenario generation"""
        result = self.gen.generate_random()
        self.assertIsNotNone(result)
    
    def test_generate_random_with_severity(self):
        """Test random generation with severity filter"""
        result = self.gen.generate_random(severity="critical")
        self.assertEqual(result['scenario']['severity'].lower(), 'critical')
    
    def test_get_scenario_summary(self):
        """Test scenario summary"""
        summary = self.gen.get_scenario_summary("ransomware_attack")
        self.assertEqual(summary['id'], "ransomware_attack")
        self.assertIn("severity", summary)
        self.assertIn("stages", summary)
    
    def test_timeline_has_events(self):
        """Test timeline contains events"""
        result = self.gen.generate("ransomware_attack")
        self.assertGreater(len(result['timeline']), 0)
    
    def test_timeline_event_structure(self):
        """Test timeline event has required fields"""
        result = self.gen.generate("ransomware_attack")
        event = result['timeline'][0]
        self.assertIn("stage", event)
        self.assertIn("name", event)
        self.assertIn("indicators", event)
        self.assertIn("policies", event)


class TestGeneratorPolicies(unittest.TestCase):
    """Test policy handling"""
    
    def setUp(self):
        self.gen = BreachGenerator()
    
    def test_policies_loaded(self):
        """Test policies are loaded"""
        self.assertGreater(len(self.gen.policies), 0)
    
    def test_policy_structure(self):
        """Test policy has expected fields"""
        policy_id = list(self.gen.policies.keys())[0]
        policy = self.gen.policies[policy_id]
        self.assertIn("policy_id", policy)


if __name__ == '__main__':
    unittest.main()
