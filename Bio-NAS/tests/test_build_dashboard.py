"""Tests for static multi-disease dashboard generation."""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from build_dashboard import disease_row, load_pipeline_steps, skipped_status, step_failures_for_disease


class BuildDashboardTests(unittest.TestCase):
    def test_load_pipeline_steps(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            log = Path(tmp) / "pipeline_steps.log"
            log.write_text("BRCA toy NAS|0\nEpigenetic Aging public GEO sample (GSE87571)|1\n", encoding="utf-8")
            steps = load_pipeline_steps(log)
            self.assertEqual(steps, [("BRCA toy NAS", 0), ("Epigenetic Aging public GEO sample (GSE87571)", 1)])

    def test_epigenetic_aging_skip_hides_stale_nas(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            disease_dir = Path(tmp) / "epigenetic_aging"
            disease_dir.mkdir()
            (disease_dir / ".skipped").write_text("plan1_deferred\n", encoding="utf-8")
            (disease_dir / "nas_demo_results.json").write_text(
                json.dumps({"n_samples": 8, "best_architecture": {"validation_accuracy": 1.0, "hidden_width": 32}}),
                encoding="utf-8",
            )
            row = disease_row("Epigenetic Aging", disease_dir, "GEO", [], ("Epigenetic",))
            self.assertIn("Plan-1 demo", row[2])
            self.assertNotIn("DUA", row[2])
            self.assertEqual(row[4], "N/A")
            self.assertEqual(row[6], "N/A")

    def test_skipped_status_plan1_deferred(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "epigenetic_aging"
            path.mkdir()
            (path / ".skipped").write_text("plan1_deferred", encoding="utf-8")
            self.assertIn("Plan-1 demo", skipped_status(path) or "")

    def test_partial_geo_shows_nas_results(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            disease_dir = Path(tmp) / "ra"
            disease_dir.mkdir()
            (disease_dir / "nas_demo_results.json").write_text(
                json.dumps({"n_samples": 4, "best_architecture": {"validation_accuracy": 0.5, "hidden_width": 8}}),
                encoding="utf-8",
            )
            row = disease_row("RA", disease_dir, "GEO", [], ("RA",))
            self.assertEqual(row[2], "Partial")
            self.assertIn("0.50", row[6])

    def test_epigenetic_aging_ready_row(self) -> None:
        keywords = (
            "Epigenetic Aging",
            "GSE40279",
            "GSE87571",
            "GSE280465",
            "EA smoke",
            "EA toy",
            "EA public",
        )
        with tempfile.TemporaryDirectory() as tmp:
            disease_dir = Path(tmp) / "epigenetic_aging"
            disease_dir.mkdir()
            (disease_dir / ".ready").write_text("{}\n", encoding="utf-8")
            (disease_dir / "manifest.json").write_text(
                json.dumps({"n_cases": 8, "schema_version": 2}),
                encoding="utf-8",
            )
            (disease_dir / "nas_demo_results.json").write_text(
                json.dumps(
                    {
                        "n_samples": 8,
                        "best_architecture": {
                            "validation_accuracy": 0.75,
                            "hidden_width": 16,
                            "validation_loss": 0.42,
                        },
                    }
                ),
                encoding="utf-8",
            )
            row = disease_row("Epigenetic Aging", disease_dir, "GEO", [], keywords)
            self.assertEqual(row[2], "Ready")
            self.assertEqual(row[4], "8")
            self.assertIn("Methylation", row[5])
            self.assertIn("0.75", row[6])

    def test_epigenetic_aging_failed_verify_step(self) -> None:
        keywords = (
            "Epigenetic Aging",
            "GSE87571",
            "EA smoke",
            "EA toy",
            "EA public",
        )
        with tempfile.TemporaryDirectory() as tmp:
            disease_dir = Path(tmp) / "epigenetic_aging"
            disease_dir.mkdir()
            steps = [("EA smoke verify", 1)]
            row = disease_row("Epigenetic Aging", disease_dir, "GEO", steps, keywords)
            self.assertIn("Failed", row[2])
            self.assertIn("1 step", row[2])

    def test_ea_toy_nas_failure_matches_keywords(self) -> None:
        keywords = ("EA smoke", "EA toy", "GSE87571")
        failed = step_failures_for_disease([("EA toy NAS", 1)], keywords)
        self.assertEqual(failed, ["EA toy NAS"])


if __name__ == "__main__":
    unittest.main()
