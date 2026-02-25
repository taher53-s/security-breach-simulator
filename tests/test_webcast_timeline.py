"""
Tests for webcast and timeline visualization
"""
import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from webcast import ScenarioWebcaster, WebcastEvent
from timeline import TimelineVisualizer, visualize


class TestWebcast(unittest.TestCase):
    """Test webcast functionality"""
    
    def test_webcaster_init(self):
        """Test webcaster initializes correctly"""
        webcaster = ScenarioWebcaster("ransomware_attack", seed=42)
        self.assertEqual(webcaster.scenario_id, "ransomware_attack")
        self.assertEqual(webcaster.seed, 42)
    
    def test_sse_event(self):
        """Test SSE event formatting"""
        event = WebcastEvent(
            event_type="stage",
            stage=1,
            timestamp=5.0,
            data={"name": "Test"}
        )
        sse = event.to_sse()
        self.assertIn("event: stage", sse)
        self.assertIn("data:", sse)


class TestTimeline(unittest.TestCase):
    """Test timeline visualization"""
    
    def test_visualizer_init(self):
        """Test visualizer loads scenario"""
        viz = TimelineVisualizer("ransomware_attack", seed=42)
        self.assertGreater(len(viz.stages), 0)
    
    def test_visualize_full(self):
        """Test full visualization renders"""
        result = visualize("ransomware_attack", style="full", seed=42)
        self.assertIn("SECURITY BREACH TIMELINE", result)
        self.assertIn("STAGE", result)
    
    def test_visualize_summary(self):
        """Test summary visualization renders"""
        result = visualize("ransomware_attack", style="summary", seed=42)
        self.assertIn("TIMELINE SUMMARY", result)
    
    def test_visualize_compact(self):
        """Test compact visualization renders"""
        result = visualize("ransomware_attack", style="compact", seed=42)
        self.assertIn("→", result)


if __name__ == '__main__':
    unittest.main()
