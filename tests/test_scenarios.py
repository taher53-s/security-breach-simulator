"""
Test suite for Security Breach Simulator
"""
import pytest
import json
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from generators.sample_breach import BreachGenerator


class TestScenarioTemplates:
    """Test scenario template loading and validation"""
    
    @pytest.fixture
    def templates_dir(self):
        return os.path.join(os.path.dirname(__file__), '..', 'src', 'scenarios', 'templates')
    
    def test_phishing_lateral_movement_exists(self, templates_dir):
        """Test that phishing scenario template exists"""
        path = os.path.join(templates_dir, 'phishing_lateral_movement.json')
        assert os.path.exists(path), "Phishing scenario template missing"
    
    def test_supply_chain_exists(self, templates_dir):
        """Test that supply chain scenario template exists"""
        path = os.path.join(templates_dir, 'supply_chain_compromise.json')
        assert os.path.exists(path), "Supply chain scenario template missing"
    
    def test_insider_threat_exists(self, templates_dir):
        """Test that insider threat scenario template exists"""
        path = os.path.join(templates_dir, 'insider_threat_data_exfil.json')
        assert os.path.exists(path), "Insider threat scenario template missing"
    
    def test_ransomware_exists(self, templates_dir):
        """Test that ransomware scenario template exists"""
        path = os.path.join(templates_dir, 'ransomware_attack.json')
        assert os.path.exists(path), "Ransomware scenario template missing"
    
    def test_all_scenarios_valid_json(self, templates_dir):
        """Test that all scenario templates are valid JSON"""
        for filename in os.listdir(templates_dir):
            if filename.endswith('.json'):
                path = os.path.join(templates_dir, filename)
                with open(path, 'r') as f:
                    data = json.load(f)
                    # Check required fields
                    assert 'id' in data, f"{filename} missing 'id'"
                    assert 'name' in data, f"{filename} missing 'name'"
                    assert 'severity' in data, f"{filename} missing 'severity'"
                    assert 'stages' in data, f"{filename} missing 'stages'"


class TestPolicyCatalog:
    """Test policy catalog loading"""
    
    @pytest.fixture
    def policies_dir(self):
        return os.path.join(os.path.dirname(__file__), '..', 'src', 'policies')
    
    def test_catalog_exists(self, policies_dir):
        """Test that policy catalog exists"""
        path = os.path.join(policies_dir, 'catalog.json')
        assert os.path.exists(path), "Policy catalog missing"
    
    def test_catalog_valid_json(self, policies_dir):
        """Test that policy catalog is valid JSON"""
        path = os.path.join(policies_dir, 'catalog.json')
        with open(path, 'r') as f:
            data = json.load(f)
            assert 'policies' in data, "Catalog missing 'policies' key"
            assert len(data['policies']) > 0, "No policies in catalog"


class TestBreachGenerator:
    """Test breach generator functionality"""
    
    def test_generator_initialization(self):
        """Test that generator can be initialized"""
        generator = BreachGenerator()
        assert generator is not None
    
    def test_generate_breach(self):
        """Test breach generation"""
        generator = BreachGenerator()
        scenario_id = "phishing_lateral_movement"
        breach = generator.generate(scenario_id)
        
        assert breach is not None
        assert 'scenario' in breach
        assert 'timeline' in breach
        assert len(breach['timeline']) > 0
