"""
API endpoint tests for Security Breach Simulator
Tests for pagination, filtering, and API responses
"""
import pytest
import json
import sys
import os
from unittest.mock import patch, MagicMock

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


class TestScenariosPagination:
    """Test scenarios endpoint pagination"""
    
    @pytest.fixture
    def mock_scenarios(self):
        return [
            {
                "id": "scenario_1",
                "name": "Test Scenario 1",
                "description": "Test description 1",
                "severity": "high",
                "category": "malware",
                "difficulty": "intermediate",
                "estimated_duration_minutes": 30,
                "stages": []
            },
            {
                "id": "scenario_2", 
                "name": "Test Scenario 2",
                "description": "Test description 2",
                "severity": "critical",
                "category": "phishing",
                "difficulty": "advanced",
                "estimated_duration_minutes": 45,
                "stages": []
            },
            {
                "id": "scenario_3",
                "name": "Test Scenario 3",
                "description": "Test description 3", 
                "severity": "low",
                "category": "insider",
                "difficulty": "beginner",
                "estimated_duration_minutes": 20,
                "stages": []
            },
        ]
    
    def test_scenarios_pagination_default(self, mock_scenarios):
        """Test default pagination returns all items"""
        from api.app import list_scenarios
        with patch('api.app._cached_catalog', return_value=(mock_scenarios, [])):
            result = list_scenarios()
            assert result['total'] == 3
            assert len(result['items']) == 3
            assert result['limit'] == 50
            assert result['offset'] == 0
    
    def test_scenarios_pagination_with_limit(self, mock_scenarios):
        """Test pagination with limit parameter"""
        from api.app import list_scenarios
        with patch('api.app._cached_catalog', return_value=(mock_scenarios, [])):
            result = list_scenarios(limit=2)
            assert result['total'] == 3
            assert len(result['items']) == 2
            assert result['limit'] == 2
    
    def test_scenarios_pagination_with_offset(self, mock_scenarios):
        """Test pagination with offset parameter"""
        from api.app import list_scenarios
        with patch('api.app._cached_catalog', return_value=(mock_scenarios, [])):
            result = list_scenarios(offset=2)
            assert result['total'] == 3
            assert len(result['items']) == 1
            assert result['offset'] == 2
    
    def test_scenarios_pagination_combined(self, mock_scenarios):
        """Test pagination with both limit and offset"""
        from api.app import list_scenarios
        with patch('api.app._cached_catalog', return_value=(mock_scenarios, [])):
            result = list_scenarios(limit=1, offset=1)
            assert result['total'] == 3
            assert len(result['items']) == 1
            assert result['items'][0]['id'] == 'scenario_2'


class TestScenariosFiltering:
    """Test scenarios endpoint filtering"""
    
    @pytest.fixture
    def mock_scenarios(self):
        return [
            {
                "id": "scenario_1",
                "name": "Phishing Attack",
                "description": "Email phishing scenario",
                "severity": "high",
                "category": "phishing",
                "difficulty": "intermediate",
                "estimated_duration_minutes": 30,
                "stages": []
            },
            {
                "id": "scenario_2", 
                "name": "Ransomware Outbreak",
                "description": "Crypto locker scenario",
                "severity": "critical",
                "category": "malware",
                "difficulty": "advanced",
                "estimated_duration_minutes": 45,
                "stages": []
            },
            {
                "id": "scenario_3",
                "name": "Data Exfiltration",
                "description": "Insider threat data theft", 
                "severity": "high",
                "category": "insider",
                "difficulty": "intermediate",
                "estimated_duration_minutes": 20,
                "stages": []
            },
        ]
    
    def test_filter_by_severity(self, mock_scenarios):
        """Test filtering by severity"""
        from api.app import list_scenarios
        with patch('api.app._cached_catalog', return_value=(mock_scenarios, [])):
            result = list_scenarios(severity="critical")
            assert result['total'] == 1
            assert result['items'][0]['severity'] == 'critical'
    
    def test_filter_by_category(self, mock_scenarios):
        """Test filtering by category"""
        from api.app import list_scenarios
        with patch('api.app._cached_catalog', return_value=(mock_scenarios, [])):
            result = list_scenarios(category="phishing")
            assert result['total'] == 1
            assert result['items'][0]['category'] == 'phishing'
    
    def test_filter_by_search(self, mock_scenarios):
        """Test search functionality"""
        from api.app import list_scenarios
        with patch('api.app._cached_catalog', return_value=(mock_scenarios, [])):
            result = list_scenarios(search="phishing")
            assert result['total'] == 1
            assert 'phishing' in result['items'][0]['name'].lower()
    
    def test_combined_filters(self, mock_scenarios):
        """Test combined filtering"""
        from api.app import list_scenarios
        with patch('api.app._cached_catalog', return_value=(mock_scenarios, [])):
            result = list_scenarios(severity="high", category="insider")
            assert result['total'] == 1
            assert result['items'][0]['category'] == 'insider'
            assert result['items'][0]['severity'] == 'high'


class TestPoliciesPagination:
    """Test policies endpoint pagination"""
    
    def test_policies_pagination_default(self):
        """Test default policies pagination"""
        mock_policies = [
            {"policy_id": f"policy_{i}", "title": f"Policy {i}"} 
            for i in range(10)
        ]
        from api.app import list_policies
        with patch('api.app._cached_catalog', return_value=([], mock_policies)):
            result = list_policies()
            assert result['total'] == 10
            assert result['limit'] == 50
    
    def test_policies_pagination_with_limit(self):
        """Test policies pagination with limit"""
        mock_policies = [
            {"policy_id": f"policy_{i}", "title": f"Policy {i}"} 
            for i in range(10)
        ]
        from api.app import list_policies
        with patch('api.app._cached_catalog', return_value=([], mock_policies)):
            result = list_policies(limit=5)
            assert result['total'] == 10
            assert len(result['items']) == 5
