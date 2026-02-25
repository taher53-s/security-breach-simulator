"""
Tests for audit logging system
"""
import unittest
import json
import tempfile
import os
from pathlib import Path


class TestAuditLogging(unittest.TestCase):
    """Test audit logging functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Create temp directory for testing
        self.temp_dir = tempfile.mkdtemp()
        # Patch the audit directory
        import src.audit_log as audit_module
        audit_module.AUDIT_DIR = Path(self.temp_dir)
    
    def tearDown(self):
        """Clean up"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_audit_logger_creation(self):
        """Test audit logger can be created"""
        from src.audit_log import AuditLogger
        
        logger = AuditLogger("test_run_001", "ransomware_attack")
        self.assertEqual(logger.run_id, "test_run_001")
        self.assertEqual(logger.scenario_id, "ransomware_attack")
        self.assertEqual(len(logger.events), 0)
    
    def test_log_scenario_start(self):
        """Test logging scenario start"""
        from src.audit_log import AuditLogger
        
        logger = AuditLogger("test_run", "ransomware_attack")
        event = logger.log_scenario_start("ransomware_attack", {"difficulty": "medium"})
        
        self.assertEqual(event.event_type, "SCENARIO_START")
        self.assertIn("started", event.message.lower())
    
    def test_log_action(self):
        """Test logging player actions"""
        from src.audit_log import AuditLogger
        
        logger = AuditLogger("test_run", "ransomware_attack")
        logger.log_action("detect", "Identified suspicious process", stage=2)
        
        self.assertEqual(len(logger.events), 1)
        self.assertEqual(logger.events[0].event_type, "ACTION_TAKEN")
        self.assertEqual(logger.events[0].stage, 2)
    
    def test_log_policy_check(self):
        """Test logging policy compliance"""
        from src.audit_log import AuditLogger
        
        logger = AuditLogger("test_run", "ransomware_attack")
        logger.log_policy_check("POL-001", True)
        logger.log_policy_check("POL-002", False)
        
        self.assertEqual(len(logger.events), 2)
        # Check events are correct type
        events_by_type = {e.event_type for e in logger.events}
        self.assertIn("POLICY_FOLLOWED", events_by_type)
        self.assertIn("POLICY_IGNORED", events_by_type)
    
    def test_audit_summary(self):
        """Test audit summary generation"""
        from src.audit_log import AuditLogger
        
        logger = AuditLogger("test_run", "ransomware_attack")
        logger.log_scenario_start("ransomware_attack")
        logger.log_action("detect", "Test detection", stage=1)
        logger.log_action("isolate", "Test isolation", stage=2)
        logger.log_scenario_end("completed")
        
        summary = logger.get_summary()
        
        self.assertEqual(summary["run_id"], "test_run")
        self.assertEqual(summary["scenario_id"], "ransomware_attack")
        self.assertEqual(summary["total_events"], 4)  # Start + 2 actions + end
        self.assertIn("events_by_type", summary)


class TestConfigManagement(unittest.TestCase):
    """Test configuration management"""
    
    def test_default_config(self):
        """Test default configuration loads"""
        from src.config import load_config
        
        config = load_config()
        self.assertEqual(config.app["name"], "Security Breach Simulator")
        self.assertEqual(config.app["version"], "0.3.0")
    
    def test_difficulty_in_config(self):
        """Test difficulty settings in config"""
        from src.config import load_config
        
        config = load_config()
        self.assertIn("default_difficulty", config.scenarios)
        self.assertEqual(config.scenarios["default_difficulty"], "medium")


class TestExceptions(unittest.TestCase):
    """Test custom exceptions"""
    
    def test_breach_simulator_error(self):
        """Test base exception"""
        from src.exceptions import BreachSimulatorError
        
        error = BreachSimulatorError("Test error", {"key": "value"})
        self.assertEqual(error.message, "Test error")
        self.assertEqual(error.details["key"], "value")
    
    def test_scenario_not_found_error(self):
        """Test scenario not found exception"""
        from src.exceptions import ScenarioNotFoundError
        
        error = ScenarioNotFoundError("Test scenario not found", {"id": "test"})
        self.assertIn("Test", error.message)
        self.assertEqual(error.details["id"], "test")
    
    def test_handle_exception(self):
        """Test exception handling"""
        from src.exceptions import handle_exception, BreachSimulatorError
        
        # Custom exception
        result = handle_exception(BreachSimulatorError("test error"))
        self.assertEqual(result["error"], "BreachSimulatorError")
        
        # Standard exception - check basic keys exist
        result = handle_exception(FileNotFoundError("test.txt"))
        self.assertEqual(result["error"], "FileNotFoundError")
        # status_code may or may not be present depending on mapping


if __name__ == "__main__":
    unittest.main()
