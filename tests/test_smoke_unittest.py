"""Basic smoke tests runnable with stdlib unittest (no pytest dependency)."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import unittest

ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, os.path.join(ROOT, "src"))

from generators.sample_breach import BreachGenerator


class GeneratorSmokeTests(unittest.TestCase):
    def test_generate_known_scenario(self) -> None:
        generator = BreachGenerator(seed=7)
        result = generator.generate("ransomware_attack")
        self.assertIn("timeline", result)
        self.assertGreater(len(result["timeline"]), 0)
        self.assertIn("total_duration_minutes", result)

    def test_seeded_random_is_deterministic(self) -> None:
        g1 = BreachGenerator(seed=42)
        g2 = BreachGenerator(seed=42)
        first = g1.generate_random()
        second = g2.generate_random()
        self.assertEqual(first["scenario"]["scenario_id"], second["scenario"]["scenario_id"])


class StreamerSmokeTests(unittest.TestCase):
    def test_streamer_cycles_emits_json_lines(self) -> None:
        cmd = [
            sys.executable,
            "backend/detection/streamer.py",
            "--scenario",
            "ransomware_attack",
            "--interval",
            "0",
            "--cycles",
            "2",
        ]
        proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, check=True)
        lines = [ln for ln in proc.stdout.splitlines() if ln.startswith("{")]
        self.assertEqual(len(lines), 2)
        payload = json.loads(lines[0])
        self.assertIn("scenario", payload)
        self.assertIn("matched_policies", payload)


if __name__ == "__main__":
    unittest.main()
