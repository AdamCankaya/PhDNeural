#!/usr/bin/env python3
"""Unit tests for phd_parser master-plan → task/issue shaping."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from phd_parser import build_dashboard_plan, load_tasks, parse_master_plan, parse_plan_metadata


SAMPLE_PLAN = """# Sample Plan

## Core Objective
Ship a consistent Bio-NAS timeline.

---

## Year 1: Foundations

### Q3 Fall 2026: Cohort Sourcing
**Phases:** 1 | **Goal:** Secure datasets.
#### Step 1: Data Acquisition
* Identify multi-disease datasets.
  * Deliverables: inventory table.
  * Acceptance: five diseases listed.
* Source longitudinal match points.
  * Deliverables: matching strategy note.
"""


class PhdParserTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.plan_path = Path(self.tmp.name) / "plan.md"
        self.plan_path.write_text(SAMPLE_PLAN, encoding="utf-8")

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_parses_nested_requirements_into_single_tasks(self) -> None:
        tasks = parse_master_plan(self.plan_path)
        self.assertEqual(len(tasks), 2)
        self.assertEqual(tasks[0].summary(), "Identify multi-disease datasets.")
        self.assertEqual(
            tasks[0].requirements(),
            [
                "Deliverables: inventory table.",
                "Acceptance: five diseases listed.",
            ],
        )
        self.assertEqual(tasks[0].goal, "Secure datasets.")
        self.assertIn("Fall 2026", tasks[0].quarter_label)

    def test_issue_body_includes_requirements_section(self) -> None:
        task = parse_master_plan(self.plan_path)[0]
        body = task.issue_body()
        self.assertIn("<!-- phd-sync-id:", body)
        self.assertIn("## Summary", body)
        self.assertIn("## Implementation requirements", body)
        self.assertIn("- Deliverables: inventory table.", body)
        self.assertIn("Bio-NAS/phd_bio-nas_timeline_dashboard.html", body)

    def test_dashboard_plan_exposes_requirements(self) -> None:
        tasks = parse_master_plan(self.plan_path)
        title, objective = parse_plan_metadata(self.plan_path)
        plan = build_dashboard_plan(tasks, title, objective)
        task0 = plan["years"][0]["quarters"][0]["steps"][0]["tasks"][0]
        self.assertEqual(task0["text"], "Identify multi-disease datasets.")
        self.assertEqual(len(task0["requirements"]), 2)

    def test_live_master_plan_has_twenty_nine_tasks(self) -> None:
        live = ROOT / "phd_bio-nas_master_plan.md"
        tasks = load_tasks(live)
        self.assertEqual(len(tasks), 29)
        for task in tasks:
            self.assertGreaterEqual(
                len(task.requirements()),
                1,
                msg=f"{task.task_id} missing nested requirements",
            )
            self.assertTrue(task.goal, msg=f"{task.task_id} missing goal")


if __name__ == "__main__":
    unittest.main()
