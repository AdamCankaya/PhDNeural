"""Tests for static multi-disease dashboard generation."""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from build_dashboard import disease_row, load_pipeline_steps


class BuildDashboardTests(unittest.TestCase):
    def test_load_pipeline_steps(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            log = Path(tmp) / "pipeline_steps.log"
            log.write_text("BRCA toy NAS|0\nEpigenetic Aging public GEO sample (GSE87571)|1\n", encoding="utf-8")
            steps = load_pipeline_steps(log)
            self.assertEqual(steps, [("BRCA toy NAS", 0), ("Epigenetic Aging public GEO sample (GSE87571)", 1)])

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


if __name__ == "__main__":
    unittest.main()
