"""
Test suite for Security Breach Simulator
Covers scenarios, policies, API, and generators
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
        path = os.path.join(templates_dir, 'phishing_lateral_movement.json')
        assert os.path.exists(path), "Phishing scenario missing"
    
    def test_supply_chain_exists(self, templates_dir):
        path = os.path.join(templates_dir, 'supply_chain_compromise.json')
        assert os.path.exists(path), "Supply chain scenario missing"
    
    def test_insider_threat_exists(self, templates_dir):
        path = os.path.join(templates_dir, 'insider_threat_data_exfil.json')
        assert os.path.exists(path), "Insider threat scenario missing"
    
    def test_ransomware_exists(self, templates_dir):
        path = os.path.join(templates_dir, 'ransomware_attack.json')
        assert os.path.exists(path), "Ransomware scenario missing"
    
    def test_credential_theft_exists(self, templates_dir):
        path = os.path.join(templates_dir, 'credential_theft_attack.json')
        assert os.path.exists(path), "Credential theft scenario missing"
    
    def test_ddos_exists(self, templates_dir):
        path = os.path.join(templates_dir, 'ddos_attack.json')
        assert os.path.exists(path), "DDoS scenario missing"
    
    def test_zero_day_exists(self, templates_dir):
        path = os.path.join(templates_dir, 'zero_day_exploit.json')
        assert os.path.exists(path), "Zero-day scenario missing"
    
    def test_all_scenarios_valid_json(self, templates_dir):
        """Verify all scenarios are valid JSON with required fields"""
        for filename in os.listdir(templates_dir):
            if filename.endswith('.json'):
                path = os.path.join(templates_dir, filename)
                with open(path, 'r') as f:
                    data = json.load(f)
                    # Check required fields
                    assert 'id' in data, f"{filename} missing 'id'"
                    assert 'name' in data, f"{filename} missing 'name'"
                    assert 'severity' in data, f"{filename} missing 'severity'"
                    assert 'category' in data, f"{filename} missing 'category'"
                    assert 'stages' in data, f"{filename} missing 'stages'"
                    assert 'difficulty' in data, f"{filename} missing 'difficulty'"
    
    def test_scenario_severity_values(self, templates_dir):
        """Verify severity values are valid"""
        valid_severities = ['critical', 'high', 'medium', 'low']
        for filename in os.listdir(templates_dir):
            if filename.endswith('.json'):
                path = os.path.join(templates_dir, filename)
                with open(path, 'r') as f:
                    data = json.load(f)
                    sev = data.get('severity', '').lower()
                    assert sev in valid_severities, f"{filename} has invalid severity: {sev}"
    
    def test_scenario_stages_have_indicators(self, templates_dir):
        """Verify each stage has indicators"""
        for filename in os.listdir(templates_dir):
            if filename.endswith('.json'):
                path = os.path.join(templates_dir, filename)
                with open(path, 'r') as f:
                    data = json.load(f)
                    for stage in data.get('stages', []):
                        assert 'indicators' in stage, f"{filename} stage missing indicators"
                        assert len(stage['indicators']) > 0, f"{filename} stage has no indicators"


class TestPolicyCatalog:
    """Test policy catalog loading"""
    
    @pytest.fixture
    def policies_dir(self):
        return os.path.join(os.path.dirname(__file__), '..', 'src', 'policies')
    
    def test_catalog_exists(self, policies_dir):
        path = os.path.join(policies_dir, 'catalog.json')
        assert os.path.exists(path), "Policy catalog missing"
    
    def test_catalog_valid_json(self, policies_dir):
        path = os.path.join(policies_dir, 'catalog.json')
        with open(path, 'r') as f:
            data = json.load(f)
            # Catalog is a direct list of policies
            assert isinstance(data, list), "Catalog should be a list"
            assert len(data) > 0, "No policies in catalog"
    
    def test_policies_have_required_fields(self, policies_dir):
        path = os.path.join(policies_dir, 'catalog.json')
        with open(path, 'r') as f:
            data = json.load(f)
            # Catalog is a direct list of policies
            for policy in data:
                assert 'policy_id' in policy, "Policy missing policy_id"
                assert 'title' in policy, "Policy missing title"


class TestBreachGenerator:
    """Test breach generator functionality"""
    
    def test_generator_initialization(self):
        generator = BreachGenerator()
        assert generator is not None
    
    def test_generate_phishing_scenario(self):
        generator = BreachGenerator()
        breach = generator.generate("phishing_lateral_movement")
        assert breach is not None
        assert 'scenario' in breach
        assert 'timeline' in breach
    
    def test_generate_ransomware_scenario(self):
        generator = BreachGenerator()
        breach = generator.generate("ransomware_attack")
        assert breach is not None
        assert 'scenario' in breach
        assert len(breach['timeline']) > 0
    
    def test_generate_nonexistent_scenario(self):
        generator = BreachGenerator()
        # Should raise ValueError for unknown scenarios
        with pytest.raises(ValueError, match="Unknown scenario"):
            generator.generate("nonexistent_scenario")


class TestAPIServer:
    """Test API server configuration"""
    
    def test_api_file_exists(self):
        api_path = os.path.join(os.path.dirname(__file__), '..', 'backend', 'api', 'app.py')
        assert os.path.exists(api_path), "API app.py missing"
    
    def test_api_has_required_endpoints(self):
        api_path = os.path.join(os.path.dirname(__file__), '..', 'backend', 'api', 'app.py')
        with open(api_path, 'r') as f:
            content = f.read()
            assert '/scenarios' in content, "Missing /scenarios endpoint"
            assert '/policies' in content, "Missing /policies endpoint"
            assert '/dashboard' in content, "Missing /dashboard endpoint"


class TestScenarioValidation:
    """Enhanced scenario validation tests"""
    
    @pytest.fixture
    def templates_dir(self):
        return os.path.join(os.path.dirname(__file__), '..', 'src', 'scenarios', 'templates')
    
    def test_all_scenarios_have_valid_difficulty(self, templates_dir):
        """Verify difficulty values are valid"""
        valid_difficulties = ['beginner', 'intermediate', 'advanced', 'expert']
        for filename in os.listdir(templates_dir):
            if filename.endswith('.json'):
                path = os.path.join(templates_dir, filename)
                with open(path, 'r') as f:
                    data = json.load(f)
                    diff = data.get('difficulty', '').lower()
                    assert diff in valid_difficulties, f"{filename} has invalid difficulty: {diff}"
    
    def test_all_scenarios_have_stages(self, templates_dir):
        """Verify each scenario has at least one stage"""
        for filename in os.listdir(templates_dir):
            if filename.endswith('.json'):
                path = os.path.join(templates_dir, filename)
                with open(path, 'r') as f:
                    data = json.load(f)
                    stages = data.get('stages', [])
                    assert len(stages) > 0, f"{filename} has no stages"
    
    def test_all_stages_have_required_fields(self, templates_dir):
        """Verify each stage has required fields"""
        for filename in os.listdir(templates_dir):
            if filename.endswith('.json'):
                path = os.path.join(templates_dir, filename)
                with open(path, 'r') as f:
                    data = json.load(f)
                    for stage in data.get('stages', []):
                        assert 'stage' in stage, f"{filename} stage missing 'stage'"
                        assert 'name' in stage, f"{filename} stage missing 'name'"
                        assert 'description' in stage, f"{filename} stage missing 'description'"
    
    def test_all_scenarios_have_policies_or_links(self, templates_dir):
        """Verify scenarios have policy links"""
        for filename in os.listdir(templates_dir):
            if filename.endswith('.json'):
                path = os.path.join(templates_dir, filename)
                with open(path, 'r') as f:
                    data = json.load(f)
                    has_policies = (
                        'policy_links' in data or 
                        'policy_in_play' in data or
                        'policies' in data
                    )
                    # At least one policy field should exist
                    assert has_policies, f"{filename} missing policy references"
