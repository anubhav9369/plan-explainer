"""Tests for the plan explainer (stdlib unittest, no third-party deps)."""

import json
import subprocess
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from explainer import explain_plan, review_checklist

DAY38 = Path(__file__).resolve().parent.parent
EXAMPLE = json.loads((DAY38 / "examples" / "summarise-paper-plan.json").read_text())


class TestExplainPlan(unittest.TestCase):
    def test_explanation_states_the_goal(self):
        self.assertIn(EXAMPLE["goal"], explain_plan(EXAMPLE))

    def test_permission_steps_are_flagged(self):
        out = explain_plan(EXAMPLE)
        self.assertIn("needs your permission", out)
        self.assertIn("2 step(s) need your explicit permission", out)

    def test_every_failure_point_appears(self):
        out = explain_plan(EXAMPLE)
        for step in EXAMPLE["steps"]:
            for failure in step["failure_points"]:
                self.assertIn(failure, out)

    def test_assumptions_constraints_and_risks_listed(self):
        out = explain_plan(EXAMPLE)
        for key in ("assumptions", "constraints", "risks"):
            for item in EXAMPLE[key]:
                self.assertIn(item, out)

    def test_decision_status_shown(self):
        self.assertIn("pending", explain_plan(EXAMPLE))

    def test_empty_plan_does_not_crash(self):
        out = explain_plan({})
        self.assertIn("(no goal stated)", out)
        self.assertIn("(none stated)", out)

    def test_checklist_asks_about_each_gated_step(self):
        questions = review_checklist(EXAMPLE)
        gated = [s for s in EXAMPLE["steps"] if s["needs_permission"]]
        self.assertEqual(
            sum("Allow step" in q for q in questions), len(gated)
        )

    def test_checklist_questions_assumptions_and_risks(self):
        questions = review_checklist(EXAMPLE)
        self.assertTrue(any("assumption" in q for q in questions))
        self.assertTrue(any("Accept this risk" in q for q in questions))

    def test_cli_renders_example_and_exits_zero(self):
        proc = subprocess.run(
            [sys.executable, str(DAY38 / "explainer.py"),
             str(DAY38 / "examples" / "summarise-paper-plan.json")],
            capture_output=True, text=True, check=False,
        )
        self.assertEqual(proc.returncode, 0)
        self.assertIn(EXAMPLE["goal"], proc.stdout)


if __name__ == "__main__":
    unittest.main()
