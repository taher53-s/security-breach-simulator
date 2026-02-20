"""
Test CLI functionality
"""
import pytest
import subprocess
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from generators.sample_breach import BreachGenerator


class TestCLI:
    """Test command-line interface"""
    
    def test_generator_list_command(self):
        """Test list command shows scenarios"""
        from generators.sample_breach import BreachGenerator
        gen = BreachGenerator()
        scenarios = gen.list_scenarios()
        assert len(scenarios) >= 7, "Should have at least 7 scenarios"
    
    def test_generator_summary(self):
        """Test scenario summary"""
        from generators.sample_breach import BreachGenerator
        gen = BreachGenerator()
        summary = gen.get_scenario_summary("ransomware_attack")
        assert summary["id"] == "ransomware_attack"
        assert "severity" in summary
        assert "stages" in summary
    
    def test_generator_all_scenarios(self):
        """Test generating all scenarios"""
        from generators.sample_breach import BreachGenerator
        gen = BreachGenerator()
        
        scenario_ids = [
            "phishing_lateral_movement",
            "supply_chain_compromise", 
            "insider_threat_data_exfil",
            "ransomware_attack",
            "credential_theft_attack",
            "ddos_attack",
            "zero_day_exploit",
        ]
        
        for sid in scenario_ids:
            result = gen.generate(sid)
            assert result is not None
            assert "scenario" in result
            assert "timeline" in result
    
    def test_timeline_generation(self):
        """Test timeline has correct structure"""
        from generators.sample_breach import BreachGenerator
        gen = BreachGenerator()
        
        result = gen.generate("ransomware_attack")
        timeline = result["timeline"]
        
        assert len(timeline) > 0, "Timeline should have events"
        
        # Check first event structure
        event = timeline[0]
        assert "stage" in event
        assert "name" in event
        assert "indicators" in event
        assert "policies" in event
    
    def test_policy_annotations(self):
        """Test policies are linked to stages"""
        from generators.sample_breach import BreachGenerator
        gen = BreachGenerator()
        
        result = gen.generate("phishing_lateral_movement")
        
        # At least one event should have policies
        has_policies = any(len(e.get("policies", [])) > 0 for e in result["timeline"])
        assert has_policies, "Should have policies in timeline"
