"""CLI tests for build_brca_longitudinal_matching.py (offline fixture mode)."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import build_brca_longitudinal_matching as matching_cli
from src.config.load_config import brca_gdc_keys, load_longitudinal_keys

SCRIPT = ROOT / "scripts" / "build_brca_longitudinal_matching.py"
FIXTURE = ROOT / "tests" / "fixtures" / "gdc_brca_samples_mini.json"
EXPECTED_PIN = ROOT / "docs" / "data" / "smoke_expected_matching.json"


class BuildBrcaMatchingCliTests(unittest.TestCase):
    def test_fixture_writes_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "longitudinal_matching"
            proc = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--fixture",
                    str(FIXTURE),
                    "--out-dir",
                    str(out),
                ],
                cwd=str(ROOT),
                capture_output=True,
                text=True,
            )
            self.assertEqual(proc.returncode, 0, msg=proc.stderr or proc.stdout)
            for name in ("visit_sequences.json", "match_pairs.json", "summary.json"):
                self.assertTrue((out / name).is_file(), name)
            summary = json.loads((out / "summary.json").read_text(encoding="utf-8"))
            self.assertEqual(summary["schema_version"], 1)
            self.assertEqual(summary["cohort_scope"], "fixture")
            self.assertIn("sample_types_observed", summary)
            self.assertIn("Blood Derived Normal", summary["sample_types_observed"])
            self.assertGreaterEqual(summary["n_samples_dropped_unranked"], 1)
            pin = json.loads(EXPECTED_PIN.read_text(encoding="utf-8"))
            for key in pin["required_summary_keys"]:
                self.assertIn(key, summary)
            fx = pin["fixture_expectations"]
            self.assertGreaterEqual(summary["n_match_pairs"], fx["n_match_pairs_min"])

    def test_discover_filter_project_and_later_types(self) -> None:
        """Filter JSON only — no GDC network."""
        gdc_keys = brca_gdc_keys(load_longitudinal_keys())
        filters = matching_cli.discover_case_filters(gdc_keys)
        self.assertEqual(filters["op"], "and")
        clauses = filters["content"]
        project = next(c for c in clauses if c["content"]["field"] == "project.project_id")
        sample = next(c for c in clauses if c["content"]["field"] == "samples.sample_type")
        self.assertEqual(project["op"], "=")
        self.assertEqual(project["content"]["value"], gdc_keys["project_id"])
        self.assertEqual(project["content"]["value"], "TCGA-BRCA")
        self.assertEqual(sample["op"], "in")
        self.assertEqual(sample["content"]["value"], list(gdc_keys["match_pair"]["later_sample_types"]))
        self.assertEqual(sample["content"]["value"], ["Recurrent Tumor", "Metastatic"])

    def test_resolve_cohort_scope(self) -> None:
        self.assertEqual(matching_cli.resolve_cohort_scope(fixture=True, discover=False), "fixture")
        self.assertEqual(matching_cli.resolve_cohort_scope(fixture=False, discover=True), "discover")
        self.assertEqual(matching_cli.resolve_cohort_scope(fixture=False, discover=False), "smoke")


if __name__ == "__main__":
    unittest.main()
